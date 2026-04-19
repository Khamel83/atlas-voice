#!/usr/bin/env python3
"""
Massive Email Dataset Processor
Handles 6.8M email records with comprehensive linguistic analysis
"""

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import sys

class MassiveEmailProcessor:
    def __init__(self):
        self.total_words = 0
        self.total_sentences = 0
        self.word_lengths = []
        self.sentence_lengths = []
        self.vocabulary = Counter()
        self.bigrams = Counter()
        self.trigrams = Counter()
        self.function_words = Counter()
        self.pos_patterns = Counter()
        self.casual_markers = Counter()
        self.formal_markers = Counter()
        self.personal_expressions = []

        # Function words for analysis
        self.function_word_list = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'must', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that',
            'these', 'those', 'who', 'what', 'where', 'when', 'why', 'how'
        }

        self.casual_indicators = {
            'actually', 'basically', 'literally', 'totally', 'really', 'super',
            'kinda', 'sorta', 'gonna', 'wanna', 'like', 'you know', 'i mean',
            'sort of', 'kind of', 'pretty much', 'a lot', 'tons of'
        }

        self.formal_indicators = {
            'furthermore', 'moreover', 'however', 'nevertheless', 'therefore',
            'consequently', 'subsequently', 'accordingly', 'nonetheless',
            'utilize', 'implement', 'demonstrate', 'facilitate', 'optimize',
            'establish', 'maintain', 'develop', 'ensure', 'provide'
        }

    def process_text_sample(self, text: str, max_chars=10000):
        """Process a text sample with comprehensive linguistic analysis"""
        if not text or len(text.strip()) < 10:
            return

        # Truncate very long texts for performance
        if len(text) > max_chars:
            text = text[:max_chars]

        text_lower = text.lower()

        # Word analysis
        words = re.findall(r'\b\w+\b', text_lower)
        self.total_words += len(words)
        self.word_lengths.extend([len(w) for w in words])
        self.vocabulary.update(words)

        # Function word analysis
        function_words_found = [w for w in words if w in self.function_word_list]
        self.function_words.update(function_words_found)

        # N-gram analysis
        if len(words) >= 2:
            self.bigrams.update(zip(words[:-1], words[1:]))
        if len(words) >= 3:
            self.trigrams.update(zip(words[:-2], words[1:-1], words[2:]))

        # Sentence analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        self.total_sentences += len(sentences)
        self.sentence_lengths.extend([len(s.split()) for s in sentences])

        # Style marker analysis
        for marker in self.casual_indicators:
            if marker in text_lower:
                self.casual_markers[marker] += text_lower.count(marker)

        for marker in self.formal_indicators:
            if marker in text_lower:
                self.formal_markers[marker] += text_lower.count(marker)

        # Personal expression extraction
        if any(personal in text_lower for personal in ['i ', 'my ', 'me ', 'myself']):
            # Extract phrases containing personal pronouns
            for i in range(len(words)-2):
                phrase = ' '.join(words[i:i+3])
                if any(personal in phrase for personal in ['i', 'my', 'me']):
                    self.personal_expressions.append(phrase)

    def process_csv_chunk(self, file_path: str, chunk_size=10000, max_chunks=100):
        """Process CSV file in chunks"""
        print(f"Processing {file_path} in chunks...")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Increase field size limit
                csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
                reader = csv.DictReader(f)

                chunk_count = 0
                row_count = 0

                for row in reader:
                    row_count += 1

                    # Extract email content (adjust column names as needed)
                    content = ""
                    for col in ['content', 'body', 'text', 'message', 'email_content']:
                        if col in row and row[col]:
                            content = row[col]
                            break

                    if content and len(content.strip()) > 20:
                        self.process_text_sample(content)

                    # Process in chunks to avoid memory issues
                    if row_count % chunk_size == 0:
                        chunk_count += 1
                        print(f"  Processed chunk {chunk_count} ({row_count:,} rows)")

                        if chunk_count >= max_chunks:
                            print(f"  Reached max chunks limit ({max_chunks})")
                            break

                print(f"  Completed: {row_count:,} rows processed")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False

        return True

    def generate_comprehensive_analysis(self) -> dict:
        """Generate comprehensive linguistic analysis"""
        if self.total_words == 0:
            return {}

        analysis = {
            'total_words': self.total_words,
            'total_sentences': self.total_sentences,
            'avg_word_length': sum(self.word_lengths) / len(self.word_lengths) if self.word_lengths else 0,
            'avg_sentence_length': sum(self.sentence_lengths) / len(self.sentence_lengths) if self.sentence_lengths else 0,
            'vocabulary_size': len(self.vocabulary),
            'vocabulary_richness': len(self.vocabulary) / self.total_words if self.total_words > 0 else 0,

            # Function word patterns (key linguistic signature)
            'top_function_words': dict(self.function_words.most_common(20)),
            'function_word_ratio': sum(self.function_words.values()) / self.total_words if self.total_words > 0 else 0,

            # N-gram patterns
            'top_bigrams': [' '.join(bg) for bg, count in self.bigrams.most_common(10)],
            'top_trigrams': [' '.join(tg) for tg, count in self.trigrams.most_common(10)],

            # Style markers
            'casual_markers': dict(self.casual_markers.most_common(10)),
            'formal_markers': dict(self.formal_markers.most_common(10)),

            # Personal expressions
            'personal_expressions': list(set(self.personal_expressions))[:20],

            # Vocabulary complexity
            'vocabulary_complexity': len([w for w in self.vocabulary if len(w) > 6]) / len(self.vocabulary) if self.vocabulary else 0
        }

        return analysis

def main():
    processor = MassiveEmailProcessor()

    # Process the massive email dataset
    email_file = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"
    print(f"Processing massive email dataset: {email_file}")

    if processor.process_csv_chunk(email_file, chunk_size=50000, max_chunks=50):
        print("Email processing completed successfully")
    else:
        print("Email processing failed")

    # Generate analysis
    analysis = processor.generate_comprehensive_analysis()

    # Save analysis
    output_file = "/Users/khamel83/dev/Speech/massive_email_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\n=== MASSIVE EMAIL ANALYSIS ===")
    print(f"Total words processed: {analysis['total_words']:,}")
    print(f"Total sentences: {analysis['total_sentences']:,}")
    print(f"Vocabulary size: {analysis['vocabulary_size']:,}")
    print(f"Average word length: {analysis['avg_word_length']:.2f}")
    print(f"Average sentence length: {analysis['avg_sentence_length']:.1f}")
    print(f"Vocabulary richness: {analysis['vocabulary_richness']:.3f}")
    print(f"Function word ratio: {analysis['function_word_ratio']:.3f}")
    print(f"\nTop casual markers: {list(analysis['casual_markers'].keys())[:5]}")
    print(f"Top formal markers: {list(analysis['formal_markers'].keys())[:5]}")
    print(f"\nAnalysis saved to: {output_file}")

if __name__ == "__main__":
    main()
