#!/usr/bin/env python3
"""
Email-Only Corpus Sampler
Samples only from email corpus, avoiding personal/voice data
"""

import pandas as pd
import random
import re
from typing import List

class EmailOnlyCorpusSampler:
    """Samples only from email corpus with content filtering"""

    def __init__(self):
        self.email_path = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"

    def get_casual_business_samples(self, num_samples: int = 6) -> List[str]:
        """Get casual business/work-related email samples"""
        print(f"📧 Sampling {num_samples} casual business emails from corpus...")

        samples = []

        try:
            # Read email data in chunks
            chunk_size = 10000
            collected_samples = []

            for chunk in pd.read_csv(self.email_path, chunksize=chunk_size):
                # Filter for business/casual emails (avoid deeply personal content)
                business_emails = chunk[
                    (chunk['subject'].str.contains(r'project|meeting|work|schedule|plan|update|question|help|thanks', case=False, na=False)) |
                    (chunk['content'].str.contains(r'project|meeting|work|schedule|plan|update|question|help|thanks', case=False, na=False))
                ]

                # Avoid overly personal emails
                business_emails = business_emails[
                    ~business_emails['content'].str.contains(r'love|relationship|sorry|hurt|feel|personal|private', case=False, na=True)
                ]

                if len(business_emails) > 0:
                    # Sample from this chunk
                    chunk_samples = business_emails.sample(n=min(20, len(business_emails)))

                    for _, email in chunk_samples.iterrows():
                        content = self._clean_business_email(email.get('content', ''))
                        if content and 150 <= len(content) <= 400:
                            collected_samples.append(content)

                # Stop when we have enough samples
                if len(collected_samples) >= num_samples * 3:
                    break

            # Random sample from collected
            if len(collected_samples) >= num_samples:
                samples = random.sample(collected_samples, num_samples)
            else:
                samples = collected_samples

            print(f"✅ Found {len(samples)} casual business email samples")

        except Exception as e:
            print(f"❌ Error sampling emails: {e}")

        return samples

    def _clean_business_email(self, content: str) -> str:
        """Clean business email content"""
        if not content or pd.isna(content):
            return ""

        content = str(content).strip()

        # Remove email addresses and signatures
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[email]', content)
        content = re.sub(r'http[s]?://\S+', '[url]', content)
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[phone]', content)

        # Remove email headers and footers
        content = re.sub(r'From:.*?Subject:.*?\n', '', content, flags=re.DOTALL)
        content = re.sub(r'-----Original Message-----.*', '', content, flags=re.DOTALL)
        content = re.sub(r'\n\s*Best.*', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'\n\s*Sent from.*', '', content, flags=re.DOTALL | re.IGNORECASE)

        # Clean whitespace
        content = re.sub(r'\s+', ' ', content).strip()

        # Filter out overly personal content
        personal_indicators = [
            'i love you', 'relationship', 'feeling', 'hurt', 'sorry for',
            'personal', 'private', 'intimate', 'heartfelt'
        ]

        content_lower = content.lower()
        for indicator in personal_indicators:
            if indicator in content_lower:
                return ""  # Skip personal content

        return content

if __name__ == "__main__":
    sampler = EmailOnlyCorpusSampler()

    print("📧 SAMPLING CASUAL BUSINESS EMAILS ONLY")
    print("=" * 50)

    samples = sampler.get_casual_business_samples(6)

    for i, sample in enumerate(samples, 1):
        print(f"\n{i}. Length: {len(sample)} characters")
        print(f"Content: {sample[:120]}...")
        print("-" * 40)
