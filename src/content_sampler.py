#!/usr/bin/env python3
"""
Content Sampler for Authenticity Testing
Extracts real 200+ character contiguous segments from Omar's data
"""

import random
import re
from pathlib import Path
from typing import List, Tuple
import json

class ContentSampler:
    """Extracts real content segments for authenticity testing"""

    def __init__(self):
        self.data_sources = [
            '/Users/khamel83/dev/atlas-voice/data/omars_personal_letters.txt',
            '/Users/khamel83/dev/atlas-voice/data/speech.md'
        ]
        self.email_processor = None

    def load_all_content(self) -> List[str]:
        """Load all content from data sources"""
        all_content = []

        # Load text files
        for file_path in self.data_sources:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    all_content.append(content)
                    print(f"📄 Loaded {len(content.split()):,} words from {Path(file_path).name}")
            except Exception as e:
                print(f"⚠️  Could not load {file_path}: {e}")

        # Load email content
        try:
            from email_processor import EmailProcessor
            self.email_processor = EmailProcessor(
                '/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/status_tracking.csv',
                '/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv'
            )

            email_texts, email_stats = self.email_processor.process_emails_for_voice_analysis()
            all_content.extend(email_texts)
            print(f"📧 Loaded {len(email_texts)} email samples ({email_stats['total_words']:,} words)")
        except Exception as e:
            print(f"⚠️  Could not load email data: {e}")

        return all_content

    def extract_valid_segments(self, content: str, min_length: int = 200) -> List[str]:
        """Extract valid content segments meeting criteria"""
        segments = []

        # Split by sentences to get natural breaks
        sentences = re.split(r'[.!?]+', content)

        # Build segments by combining sentences until we reach minimum length
        current_segment = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Clean up the sentence
            sentence = self._clean_text(sentence)

            if len(sentence) < 10:  # Skip very short sentences
                continue

            current_segment.append(sentence)
            current_length += len(sentence)

            # Check if we've reached minimum length
            if current_length >= min_length:
                full_segment = ' '.join(current_segment)

                # Validate the segment
                if self._is_valid_segment(full_segment):
                    segments.append(full_segment)

                # Reset for next segment
                current_segment = []
                current_length = 0

        return segments

    def _clean_text(self, text: str) -> str:
        """Clean text for analysis"""
        # Remove email headers/signatures
        text = re.sub(r'^On.*wrote:.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^-+.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^Sent from.*$', '', text, flags=re.MULTILINE)

        # Remove quoted text
        text = re.sub(r'>.*$', '', text, flags=re.MULTILINE)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        return text

    def _is_valid_segment(self, segment: str) -> bool:
        """Check if segment meets quality criteria"""
        # Minimum length
        if len(segment) < 200:
            return False

        # Maximum length (keep it reasonable)
        if len(segment) > 500:
            return False

        # Must contain alphabetic characters
        if not re.search(r'[a-zA-Z]', segment):
            return False

        # Should not be mostly special characters
        alpha_ratio = len(re.findall(r'[a-zA-Z]', segment)) / len(segment)
        if alpha_ratio < 0.7:
            return False

        # Should not contain email addresses
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', segment):
            return False

        # Should not contain phone numbers
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', segment):
            return False

        # Should not be mostly numbers
        digit_ratio = len(re.findall(r'\d', segment)) / len(segment)
        if digit_ratio > 0.3:
            return False

        return True

    def get_random_segments(self, num_segments: int = 10) -> List[str]:
        """Get random valid segments from all content"""
        print("🔍 Loading and sampling content...")

        all_content = self.load_all_content()
        all_segments = []

        for content in all_content:
            if content.strip():
                segments = self.extract_valid_segments(content)
                all_segments.extend(segments)

        print(f"📊 Found {len(all_segments)} valid segments")

        if len(all_segments) < num_segments:
            print(f"⚠️  Only {len(all_segments)} segments available (requested {num_segments})")
            num_segments = len(all_segments)

        # Randomly select segments
        selected_segments = random.sample(all_segments, min(num_segments, len(all_segments)))

        print(f"✅ Selected {len(selected_segments)} random segments for testing")
        return selected_segments

    def generate_test_samples(self) -> Tuple[List[str], List[str]]:
        """Generate real samples and save metadata for fake generation"""
        real_samples = self.get_random_segments(6)  # Get 6 for 3 tests

        # Save samples with metadata for AI generation
        test_data = {
            'real_samples': real_samples,
            'generation_metadata': {
                'total_samples': len(real_samples),
                'avg_length': sum(len(s) for s in real_samples) / len(real_samples),
                'min_length': min(len(s) for s in real_samples),
                'max_length': max(len(s) for s in real_samples),
                'voice_profile_path': '/Users/khamel83/dev/atlas-voice/prompts/OMARS_ULTIMATE_VOICE_PROFILE_COMPLETE.txt'
            }
        }

        with open('/Users/khamel83/dev/atlas-voice/data/test_samples.json', 'w') as f:
            json.dump(test_data, f, indent=2)

        print(f"💾 Saved test data to: data/test_samples.json")

        # Group into pairs for the three tests
        test_pairs = []
        for i in range(0, len(real_samples), 2):
            if i + 1 < len(real_samples):
                test_pairs.append((real_samples[i], real_samples[i + 1]))

        return test_pairs[:3], real_samples  # Return 3 pairs and all samples


def main():
    """Test the content sampler"""
    sampler = ContentSampler()
    test_pairs, all_samples = sampler.generate_test_samples()

    print(f"\n🧪 TEST SAMPLES PREPARED:")
    print("=" * 50)
    for i, (sample1, sample2) in enumerate(test_pairs, 1):
        print(f"\nTEST {i}:")
        print(f"Sample 1 ({len(sample1)} chars): {sample1[:100]}...")
        print(f"Sample 2 ({len(sample2)} chars): {sample2[:100]}...")


if __name__ == "__main__":
    main()
