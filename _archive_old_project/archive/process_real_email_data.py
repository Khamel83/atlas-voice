#!/usr/bin/env python3
"""
Process Real Email Data for Speech Analysis

This script processes your 7,638 email files to extract your authentic writing patterns.
Handles chunking, overlapping, and context preservation for large-scale analysis.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Generator
import email
from email import policy
from email.parser import BytesParser
import hashlib

class EmailProcessor:
    """Process large email datasets with chunking and overlap"""

    def __init__(self, chunk_size=50000, overlap=5000):
        self.chunk_size = chunk_size  # words per chunk
        self.overlap = overlap  # words overlap between chunks

    def extract_email_content(self, email_path: Path) -> str:
        """Extract text content from .eml file"""
        try:
            with open(email_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)

            # Extract text from email body
            text_content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        text_content += part.get_content()
            else:
                text_content = msg.get_content()

            # Clean email headers and quoted text
            text_content = re.sub(r'^On.*wrote:.*$', '', text_content, flags=re.MULTILINE)
            text_content = re.sub(r'^>.*$', '', text_content, flags=re.MULTILINE)
            text_content = re.sub(r'^From:.*$', '', text_content, flags=re.MULTILINE)
            text_content = re.sub(r'^Subject:.*$', '', text_content, flags=re.MULTILINE)
            text_content = re.sub(r'^Date:.*$', '', text_content, flags=re.MULTILINE)

            return text_content.strip()

        except Exception as e:
            print(f"⚠ Error processing {email_path}: {e}")
            return ""

    def create_overlapping_chunks(self, text: str) -> List[str]:
        """Create overlapping chunks to preserve context"""
        words = text.split()
        chunks = []

        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunk = ' '.join(words[start:end])
            if chunk.strip():
                chunks.append(chunk)
            start = end - self.overlap  # Overlap chunks

        return chunks

    def process_email_directory(self, email_dir: Path) -> Generator[Dict, None, None]:
        """Process all emails in directory with metadata"""
        email_files = list(email_dir.glob("*.eml"))
        print(f"📧 Found {len(email_files)} email files")

        for i, email_path in enumerate(email_files):
            if i % 100 == 0:
                print(f"🔄 Processing email {i+1}/{len(email_files)}")

            content = self.extract_email_content(email_path)
            if not content or len(content.split()) < 50:  # Skip very short emails
                continue

            # Create overlapping chunks
            chunks = self.create_overlapping_chunks(content)

            for chunk_idx, chunk in enumerate(chunks):
                yield {
                    'source_file': str(email_path.name),
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks),
                    'word_count': len(chunk.split()),
                    'content_type': 'email',
                    'text': chunk,
                    'metadata': {
                        'email_file': email_path.name,
                        'chunk_position': f"{chunk_idx+1}/{len(chunks)}",
                        'estimated_date': self._extract_date_from_filename(email_path.name)
                    }
                }

    def _extract_date_from_filename(self, filename: str) -> str:
        """Extract date from email filename"""
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if date_match:
            return date_match.group(1)
        return "unknown"

    def process_to_chunks_file(self, email_dir: Path, output_file: Path):
        """Process all emails and save as structured chunks"""
        chunks = []
        word_count = 0

        for chunk_data in self.process_email_directory(email_dir):
            chunks.append(chunk_data)
            word_count += chunk_data['word_count']

            if len(chunks) % 100 == 0:
                print(f"📊 Processed {len(chunks)} chunks, {word_count:,} words")

        # Save structured data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_chunks': len(chunks),
                'total_words': word_count,
                'chunk_size': self.chunk_size,
                'overlap': self.overlap,
                'chunks': chunks
            }, f, indent=2)

        print(f"✅ Saved {len(chunks)} chunks ({word_count:,} words) to {output_file}")
        return chunks

if __name__ == "__main__":
    # Process your real email data
    email_dir = Path("/Users/khamel83/Library/CloudStorage/GoogleDrive-zoheri@gmail.com/My Drive/Dev/Atlas/processed/emails")
    output_file = Path("email_chunks_processed.json")

    if not email_dir.exists():
        print(f"❌ Email directory not found: {email_dir}")
    else:
        processor = EmailProcessor(chunk_size=50000, overlap=5000)
        processor.process_to_chunks_file(email_dir, output_file)
