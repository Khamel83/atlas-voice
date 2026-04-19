"""Import service for loading writing samples."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class ImportService:
    """Handles importing text data from various file formats."""

    def __init__(self, temp_dir: str = "data/imports"):
        """Initialize import service."""
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def import_file(self, file_path: str, file_type: Optional[str] = None) -> List[str]:
        """
        Import a file and return a list of text samples.

        Args:
            file_path: Path to file to import
            file_type: Optional file type hint ('email', 'text', 'json')

        Returns:
            List of text strings
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect file type if not specified
        if file_type is None:
            file_type = self._detect_file_type(path)

        if file_type == "email":
            return self._import_email_csv(path)
        elif file_type == "text":
            return self._import_text(path)
        elif file_type == "json":
            return self._import_json(path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def import_directory(self, dir_path: str, file_type: Optional[str] = None) -> List[str]:
        """
        Import all compatible files from a directory.

        Args:
            dir_path: Path to directory
            file_type: Optional file type hint

        Returns:
            Combined list of text strings
        """
        path = Path(dir_path)

        if not path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")

        all_texts = []
        for file_path in path.iterdir():
            if file_path.is_file():
                try:
                    texts = self.import_file(str(file_path), file_type)
                    all_texts.extend(texts)
                except Exception:
                    # Skip files that can't be imported
                    continue

        return all_texts

    def _detect_file_type(self, path: Path) -> str:
        """Detect file type from extension."""
        suffix = path.suffix.lower()

        if suffix == ".csv":
            return "email"
        elif suffix in [".txt", ".md"]:
            return "text"
        elif suffix == ".json":
            return "json"
        else:
            # Default to text
            return "text"

    def _import_email_csv(self, path: Path) -> List[str]:
        """
        Import emails from CSV file.

        Expects columns like:
        - 'body' or 'content' or 'text': email content
        - 'from' or 'sender': sender email (optional, for filtering)
        """
        try:
            # Try pandas for large files (more efficient)
            df = pd.read_csv(path)

            # Find content column
            content_col = None
            for col in ['body', 'content', 'text', 'message']:
                if col in df.columns:
                    content_col = col
                    break

            if content_col is None:
                # Fall back to first column
                content_col = df.columns[0]

            # Extract text, drop NaN values
            texts = df[content_col].dropna().astype(str).tolist()

            # Filter out empty strings
            texts = [t.strip() for t in texts if t and t.strip()]

            return texts

        except Exception:
            # Fall back to CSV reader for simpler files
            texts = []
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Try to find content field
                    content = (
                        row.get('body') or
                        row.get('content') or
                        row.get('text') or
                        row.get('message') or
                        list(row.values())[0]  # First value
                    )
                    if content and content.strip():
                        texts.append(content.strip())

            return texts

    def _import_text(self, path: Path) -> List[str]:
        """
        Import plain text file.

        Treats each paragraph (double newline) as a separate sample.
        """
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Split on double newlines (paragraphs)
        texts = [p.strip() for p in content.split('\n\n') if p.strip()]

        # If no paragraphs, treat whole file as one sample
        if not texts:
            texts = [content.strip()]

        return texts

    def _import_json(self, path: Path) -> List[str]:
        """
        Import JSON file.

        Expects either:
        - Array of strings: ["text1", "text2", ...]
        - Array of objects with 'text' or 'content' field: [{"text": "..."}, ...]
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array")

        texts = []
        for item in data:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                content = item.get('text') or item.get('content') or item.get('body')
                if content:
                    texts.append(str(content))

        return texts

    def clear_temp_files(self) -> None:
        """Clear all temporary import files."""
        for file_path in self.temp_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
