#!/usr/bin/env python3
"""
Rich Corpus Sampler - Access to Full Email Dataset
Samples from 8.7M character corpus while removing sensitive information
"""

import pandas as pd
import random
import re
from pathlib import Path
from typing import List, Dict
import hashlib

class RichCorpusSampler:
    """Samples from the full email corpus with privacy filtering"""

    def __init__(self):
        self.email_path = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"
        self.text_files = [
            '/Users/khamel83/dev/atlas-voice/data/omars_personal_letters.txt',
            '/Users/khamel83/dev/atlas-voice/data/speech.md'
        ]
        self.status_path = "/Users/khamel83/Library/CloudStorage/GoogleDrive-zoheri@gmail.com/My Drive/Dev/Atlas/inputs/saved_emails/email_status.json"

    def get_diverse_real_samples(self, num_samples: int = 6) -> List[str]:
        """Get diverse samples from the full corpus"""
        print(f"🔍 Sampling {num_samples} diverse examples from full 8.7M character corpus...")

        samples = []

        # Get samples from email corpus (majority of content)
        email_samples = self._sample_from_emails(num_samples - 2)
        samples.extend(email_samples)

        # Get some samples from text files for variety
        text_samples = self._sample_from_text_files(2)
        samples.extend(text_samples)

        # Shuffle for randomness
        random.shuffle(samples)

        print(f"✅ Retrieved {len(samples)} diverse samples from corpus")
        return samples

    def _sample_from_emails(self, num_samples: int) -> List[str]:
        """Sample from the massive email dataset"""
        samples = []

        try:
            print(f"📧 Loading email dataset from CSV...")

            # Load status information if available
            status_map = {}
            try:
                import json
                with open(self.status_path, 'r') as f:
                    status_data = json.load(f)
                    status_map = {int(k): v for k, v in status_data.items()}
                print(f"📊 Loaded status for {len(status_map):,} emails")
            except:
                print("⚠️  No status data available, sampling from all emails")

            # Read CSV in chunks to handle large file
            chunk_size = 10000
            email_chunks = []

            for chunk in pd.read_csv(self.email_path, chunksize=chunk_size):
                # Filter for human emails by Omar if we have status
                if status_map:
                    human_emails = chunk[
                        (chunk['email_id'].isin(status_map.keys())) &
                        (chunk['email_id'].map(lambda x: status_map.get(x) == 'human'))
                    ]
                else:
                    # Fallback: filter by from field containing reasonable patterns
                    human_emails = chunk[
                        chunk['from'].str.contains(r'@(gmail|yahoo|hotmail|outlook)', case=False, na=False) |
                        chunk['from'].str.contains('omar', case=False, na=False)
                    ]

                if len(human_emails) > 0:
                    email_chunks.append(human_emails)

                # Stop if we have enough chunks for sampling
                if len(email_chunks) >= 20:
                    break

            if not email_chunks:
                print("❌ No human emails found")
                return []

            # Combine chunks
            all_emails = pd.concat(email_chunks, ignore_index=True)
            print(f"📊 Found {len(all_emails):,} human emails to sample from")

            # Random sample from emails
            if len(all_emails) > num_samples:
                sampled_emails = all_emails.sample(n=num_samples)
            else:
                sampled_emails = all_emails

            # Extract and clean email content
            for _, email in sampled_emails.iterrows():
                content = self._clean_email_content(email.get('body', ''))
                if len(content) >= 150:  # Minimum length filter
                    samples.append(content)

                # Stop if we have enough samples
                if len(samples) >= num_samples:
                    break

        except Exception as e:
            print(f"❌ Error sampling from emails: {e}")

        return samples

    def _sample_from_text_files(self, num_samples: int) -> List[str]:
        """Sample from text files for variety"""
        samples = []

        for file_path in self.text_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                segments = self._extract_clean_segments(content)

                # Random sample from this file
                if segments and num_samples > 0:
                    file_sample = random.choice(segments)
                    samples.append(file_sample)
                    num_samples -= 1

            except Exception as e:
                print(f"⚠️  Could not sample from {file_path}: {e}")

        return samples

    def _clean_email_content(self, content: str) -> str:
        """Clean email content while preserving authentic voice"""
        if not content or pd.isna(content):
            return ""

        # Convert to string and basic cleaning
        content = str(content).strip()

        # Remove email addresses but keep the writing style
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[email]', content)

        # Remove URLs
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[url]', content)

        # Remove phone numbers
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[phone]', content)

        # Remove long forwarding headers
        content = re.sub(r'From:.*?Subject:.*?\n', '', content, flags=re.DOTALL)
        content = re.sub(r'-----Original Message-----.*', '', content, flags=re.DOTALL)

        # Remove common email signatures and footers
        content = re.sub(r'\n\s*Best regards.*', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'\n\s*Sent from.*', '', content, flags=re.DOTALL | re.IGNORECASE)

        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content).strip()

        # Remove overly short or long content
        if len(content) < 50 or len(content) > 1000:
            return ""

        return content

    def _extract_clean_segments(self, content: str) -> List[str]:
        """Extract clean segments from text content"""
        segments = []

        # Split by paragraphs
        paragraphs = re.split(r'\n\s*\n', content)

        for para in paragraphs:
            # Clean paragraph
            clean_para = re.sub(r'\s+', ' ', para.strip())

            # Remove timestamps and obvious markers
            clean_para = re.sub(r'\d{1,2}:\d{2}\s*(AM|PM)?', '', clean_para)
            clean_para = re.sub(r'^\w+:', '', clean_para)  # Remove speaker tags

            clean_para = clean_para.strip()

            if 150 <= len(clean_para) <= 500:  # Good length range
                segments.append(clean_para)

        return segments

if __name__ == "__main__":
    sampler = RichCorpusSampler()

    print("🎲 SAMPLING FROM FULL 8.7M CHARACTER CORPUS")
    print("=" * 60)

    samples = sampler.get_diverse_real_samples(6)

    for i, sample in enumerate(samples, 1):
        print(f"\n{i}. Length: {len(sample)} characters")
        print(f"Content: {sample[:150]}...")
        print("-" * 40)
