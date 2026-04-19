#!/usr/bin/env python3
"""
Sample code for testing code style analysis
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

class SampleProcessor:
    """A sample class demonstrating coding style patterns"""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.processed_files = []
        self.total_words = 0

    def process_files(self, file_extensions: List[str] = None) -> Dict[str, int]:
        """
        Process files in the specified directory
        Returns statistics about processing
        """
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.py']

        stats = {
            'files_processed': 0,
            'total_chars': 0,
            'errors_encountered': 0
        }

        for file_path in self.data_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in file_extensions:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    word_count = len(content.split())
                    self.total_words += word_count

                    stats['files_processed'] += 1
                    stats['total_chars'] += len(content)
                    self.processed_files.append(str(file_path))

                    print(f"Processed: {file_path.name} ({word_count} words)")

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    stats['errors_encountered'] += 1

        return stats

    def get_summary(self) -> str:
        """Get a summary of processing results"""
        if not self.processed_files:
            return "No files were processed."

        return f"""
        Processing Summary:
        - Files processed: {len(self.processed_files)}
        - Total words: {self.total_words:,}
        - Average words per file: {self.total_words // len(self.processed_files)}
        """

# This is a sample comment demonstrating comment style
# The function below shows typical naming conventions
def calculate_metrics(data: List[str]) -> Dict[str, float]:
    """
    Calculate various metrics from the input data
    This function demonstrates docstring style
    """
    if not data:
        return {'average': 0.0, 'max_length': 0, 'min_length': 0}

    lengths = [len(item) for item in data]
    return {
        'average': sum(lengths) / len(lengths),
        'max_length': max(lengths),
        'min_length': min(lengths)
    }

if __name__ == "__main__":
    # Example usage
    processor = SampleProcessor("/path/to/data")
    stats = processor.process_files()
    print(processor.get_summary())
