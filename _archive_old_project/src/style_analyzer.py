#!/usr/bin/env python3
"""
Final Comprehensive Writing Style Preservation System
Unified system combining all best components for production use
"""

import sqlite3
import json
import re
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import intelligent data processor
from intelligent_data_processor import IntelligentDataProcessor

class FinalStylePreservationSystem:
    """Production-ready style preservation system"""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "emails_clean.db"
        self.speech_file = self.data_dir / "speech.md"
        self.letters_file = self.data_dir / "omars_personal_letters.txt"

        # Initialize intelligent data processor
        self.intelligent_processor = IntelligentDataProcessor()
        self.intelligent_processor.load_cache()

        # Initialize analysis containers
        self.reset_analysis()

        # Core linguistic patterns
        self.function_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'must', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that',
            'these', 'those', 'who', 'what', 'where', 'when', 'why', 'how'
        }

    def reset_analysis(self):
        """Reset analysis containers"""
        self.total_words = 0
        self.total_sentences = 0
        self.vocabulary = Counter()
        self.word_lengths = []
        self.sentence_lengths = []
        self.function_word_usage = Counter()
        self.bigrams = Counter()
        self.trigrams = Counter()
        self.casual_markers = Counter()
        self.formal_markers = Counter()
        self.personal_expressions = []

    def analyze_text(self, text: str):
        """Comprehensive text analysis"""
        if not text or len(text.strip()) < 10:
            return

        text = str(text).strip()
        text_lower = text.lower()

        # Basic tokenization
        words = re.findall(r'\b\w+\b', text_lower)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Update counters
        self.total_words += len(words)
        self.total_sentences += len(sentences)
        self.vocabulary.update(words)
        self.word_lengths.extend([len(w) for w in words])
        self.sentence_lengths.extend([len(s.split()) for s in sentences])

        # Function word analysis
        func_words = [w for w in words if w in self.function_words]
        self.function_word_usage.update(func_words)

        # N-gram analysis with content filtering
        # Filter out email artifacts and metadata
        email_junk = {'gmail', 'com', 'wrote', 'zoheri', 'omar', 'http', 'www', 'awmintz', 'mintz', 'andrew'}
        clean_words = [w for w in words if w not in email_junk and not w.isdigit() and len(w) > 1]

        if len(clean_words) >= 2:
            clean_bigrams = zip(clean_words[:-1], clean_words[1:])
            # Only keep bigrams with at least one function word or common content word
            filtered_bigrams = [(w1, w2) for w1, w2 in clean_bigrams
                              if w1 in self.function_words or w2 in self.function_words
                              or (w1 in ['going', 'need', 'want', 'think', 'know', 'get', 'make', 'take']
                                  or w2 in ['going', 'need', 'want', 'think', 'know', 'get', 'make', 'take'])]
            self.bigrams.update(filtered_bigrams)

        if len(clean_words) >= 3:
            clean_trigrams = zip(clean_words[:-2], clean_words[1:-1], clean_words[2:])
            # Filter trigrams to focus on natural language patterns
            filtered_trigrams = [(w1, w2, w3) for w1, w2, w3 in clean_trigrams
                               if any(w in self.function_words for w in [w1, w2, w3])]
            self.trigrams.update(filtered_trigrams)

        # Style markers
        casual_indicators = ['actually', 'basically', 'like', 'you know', 'i mean', 'sort of']
        formal_indicators = ['however', 'therefore', 'furthermore', 'consequently']

        for marker in casual_indicators:
            if marker in text_lower:
                self.casual_markers[marker] += text_lower.count(marker)

        for marker in formal_indicators:
            if marker in text_lower:
                self.formal_markers[marker] += text_lower.count(marker)

        # Personal expressions - filter out email junk
        if 'i ' in text_lower:
            for i in range(len(words) - 3):
                phrase = ' '.join(words[i:i+4])
                if ('i ' in phrase and len(phrase) > 8
                    and not any(junk in phrase.lower() for junk in email_junk)
                    and not re.search(r'\d{2,}|@|\.com|http', phrase)):
                    self.personal_expressions.append(phrase)

    def process_email_database(self, limit=None):
        """Process the email database efficiently"""
        print(f"Processing email database: {self.db_path}")

        if not self.db_path.exists():
            print(f"Database not found: {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get total count
        cursor.execute('SELECT COUNT(*) FROM emails WHERE is_omar = 1')
        total_emails = cursor.fetchone()[0]

        if limit:
            total_emails = min(total_emails, limit)

        print(f"Processing {total_emails:,} Omar emails...")

        # Process in chunks
        chunk_size = 5000
        processed = 0

        while processed < total_emails:
            query = '''
                SELECT content FROM emails
                WHERE is_omar = 1
                LIMIT ? OFFSET ?
            '''
            cursor.execute(query, (chunk_size, processed))

            rows = cursor.fetchall()
            if not rows:
                break

            for (content,) in rows:
                self.analyze_text(content)

            processed += len(rows)
            if processed % 10000 == 0:
                print(f"  Processed {processed:,} emails...")

        conn.close()
        print(f"Completed: {processed:,} emails processed")

    def process_additional_files(self):
        """Process speech.md and personal letters"""
        for file_path in [self.speech_file, self.letters_file]:
            if file_path.exists():
                print(f"Processing: {file_path.name}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.analyze_text(content)
                    print(f"  Added {len(content.split())} words")
            else:
                print(f"File not found: {file_path}")

    def process_unknown_data_sources(self, data_sources: List[str]):
        """Process unknown data sources using intelligent processor"""
        print("🤖 Processing unknown data sources with intelligent analysis...")

        for source in data_sources:
            source_path = Path(source)

            if source_path.is_file():
                print(f"📄 Processing unknown file: {source_path.name}")
                texts = self.intelligent_processor.process_file(str(source_path))

                for text in texts:
                    self.analyze_text(text)

                total_words = sum(len(text.split()) for text in texts)
                print(f"  ✅ Added {total_words:,} words from {len(texts)} segments")

            elif source_path.is_dir():
                print(f"📁 Processing unknown directory: {source_path.name}")
                results = self.intelligent_processor.process_directory(str(source_path), max_files=50)

                total_words = 0
                total_segments = 0

                for file_path, texts in results.items():
                    for text in texts:
                        self.analyze_text(text)
                        total_words += len(text.split())
                        total_segments += 1

                print(f"  ✅ Added {total_words:,} words from {total_segments} segments across {len(results)} files")

            else:
                print(f"  ❌ Path not found: {source}")

        # Save cache for future use
        self.intelligent_processor.save_cache()

    def generate_analysis_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        if self.total_words == 0:
            return {}

        report = {
            'metadata': {
                'total_words': self.total_words,
                'total_sentences': self.total_sentences,
                'vocabulary_size': len(self.vocabulary),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'core_metrics': {
                'avg_word_length': statistics.mean(self.word_lengths) if self.word_lengths else 0,
                'avg_sentence_length': statistics.mean(self.sentence_lengths) if self.sentence_lengths else 0,
                'vocabulary_richness': len(self.vocabulary) / self.total_words,
                'function_word_ratio': sum(self.function_word_usage.values()) / self.total_words
            },
            'linguistic_signature': {
                'top_function_words': dict(self.function_word_usage.most_common(20)),
                'top_bigrams': [' '.join(bg) for bg, _ in self.bigrams.most_common(15)],
                'top_trigrams': [' '.join(tg) for tg, _ in self.trigrams.most_common(10)]
            },
            'style_patterns': {
                'casual_markers': dict(self.casual_markers.most_common(10)),
                'formal_markers': dict(self.formal_markers.most_common(10)),
                'personal_expressions': list(set(self.personal_expressions))[:20]
            }
        }

        return report

    def create_style_prompt(self, analysis: Dict, target_length=3500) -> str:
        """Create optimized style-preserving prompt"""

        prompt_sections = [
            "# WRITING STYLE PRESERVATION SYSTEM",
            "",
            f"## ANALYSIS SUMMARY",
            f"- Words analyzed: {analysis['metadata']['total_words']:,}",
            f"- Vocabulary size: {analysis['metadata']['vocabulary_size']:,}",
            f"- Function word ratio: {analysis['core_metrics']['function_word_ratio']:.3f}",
            "",
            "## CORE LINGUISTIC SIGNATURE",
            "",
            "### Sentence Structure:",
            f"- Average length: {analysis['core_metrics']['avg_sentence_length']:.1f} words",
            f"- Word complexity: {analysis['core_metrics']['avg_word_length']:.2f} characters",
            "",
            "### Function Word Pattern:",
        ]

        # Add function words
        func_words = list(analysis['linguistic_signature']['top_function_words'].keys())[:15]
        prompt_sections.append(f"Key words: {', '.join(func_words)}")

        prompt_sections.extend([
            "",
            "### Structural Patterns:",
            f"Common phrases: {', '.join(analysis['linguistic_signature']['top_bigrams'][:8])}",
            "",
            "### Style Markers:",
        ])

        # Add style markers
        casual = list(analysis['style_patterns']['casual_markers'].keys())
        formal = list(analysis['style_patterns']['formal_markers'].keys())

        if casual:
            prompt_sections.append(f"Casual: {', '.join(casual[:6])}")
        if formal:
            prompt_sections.append(f"Formal: {', '.join(formal[:6])}")

        prompt_sections.extend([
            "",
            "### Personal Expressions:",
        ])

        # Add personal expressions
        personal = analysis['style_patterns']['personal_expressions'][:12]
        for expr in personal:
            prompt_sections.append(f"- \"{expr}\"")

        prompt_sections.extend([
            "",
            "## USAGE GUIDELINES",
            "",
            "1. **Maintain sentence rhythm**: 16-18 words average",
            "2. **Use function word pattern**: Match the signature above",
            "3. **Incorporate style markers**: Natural casual/formal blend",
            "4. **Include personal expressions**: Use authentic patterns",
            "5. **Preserve vocabulary level**: Match complexity metrics",
            "",
            "## CRITICAL REQUIREMENT",
            "",
            "Generate text that sounds authentically like the original writer.",
            f"This prompt is based on {analysis['metadata']['total_words']:,} words of authentic writing.",
            "Do not revert to generic AI communication patterns."
        ])

        prompt_text = '\n'.join(prompt_sections)

        # Truncate if too long
        if len(prompt_text) > target_length:
            lines_to_keep = int(len(prompt_sections) * 0.85)
            prompt_text = '\n'.join(prompt_sections[:lines_to_keep])

        return prompt_text

    def run_full_analysis(self, email_limit=None) -> Tuple[Dict, str]:
        """Run complete analysis and generate prompt"""
        print("🚀 FINAL COMPREHENSIVE SYSTEM - FULL ANALYSIS")
        print("=" * 60)

        # Reset for fresh analysis
        self.reset_analysis()

        # Process all data sources
        self.process_email_database(limit=email_limit)
        self.process_additional_files()

        # Generate analysis
        analysis = self.generate_analysis_report()

        # Create prompt
        prompt = self.create_style_prompt(analysis)

        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"📊 Total words: {analysis['metadata']['total_words']:,}")
        print(f"📝 Vocabulary: {analysis['metadata']['vocabulary_size']:,}")
        print(f"🎯 Prompt length: {len(prompt)} characters")

        return analysis, prompt

    def save_results(self, analysis: Dict, prompt: str, output_dir="prompts"):
        """Save analysis and prompt"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save analysis
        analysis_file = output_path.parent / "data" / "final_comprehensive_analysis.json"
        analysis_file.parent.mkdir(exist_ok=True)
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)

        # Save prompt
        prompt_file = output_path / "final_style_preservation_prompt.txt"
        with open(prompt_file, 'w') as f:
            f.write(prompt)

        print(f"💾 Results saved:")
        print(f"   Analysis: {analysis_file}")
        print(f"   Prompt: {prompt_file}")

        return analysis_file, prompt_file

    def generate_voice_profile(self):
        """Generate voice profile from current analysis"""
        profile = {
            'metadata': {
                'total_words': self.total_words,
                'total_sentences': self.total_sentences,
                'vocabulary_size': len(self.vocabulary),
                'analysis_date': datetime.now().isoformat()
            },
            'function_word_freq': {},
            'avg_sentence_length': 0,
            'avg_word_length': 0,
            'top_vocabulary': [],
            'common_phrases': [],
            'style_markers': []
        }

        # Calculate function word frequencies
        if self.total_words > 0:
            for word, count in self.function_word_usage.items():
                profile['function_word_freq'][word] = count / self.total_words

        # Calculate averages
        if self.sentence_lengths:
            profile['avg_sentence_length'] = statistics.mean(self.sentence_lengths)
        if self.word_lengths:
            profile['avg_word_length'] = statistics.mean(self.word_lengths)

        # Get top vocabulary
        profile['top_vocabulary'] = [word for word, _ in self.vocabulary.most_common(50)]

        # Get common phrases (bigrams/trigrams)
        profile['common_phrases'] = [
            ' '.join(gram) for gram, _ in self.bigrams.most_common(20)
        ] + [
            ' '.join(gram) for gram, _ in self.trigrams.most_common(10)
        ]

        # Style markers
        if self.casual_markers:
            profile['style_markers'] = [word for word, _ in self.casual_markers.most_common(10)]

        return profile

    def generate_final_prompt(self):
        """Generate the final voice prompt"""
        profile = self.generate_voice_profile()

        # Build prompt based on analysis
        prompt_sections = []

        # Header
        prompt_sections.append("# YOUR VOICE PROFILE")
        prompt_sections.append(f"**Based on {profile['metadata']['total_words']:,} words of your writing**")

        # Function words
        if profile['function_word_freq']:
            top_functions = sorted(profile['function_word_freq'].items(),
                                 key=lambda x: x[1], reverse=True)[:5]
            func_desc = " → ".join([f"{word} ({freq:.1%})" for word, freq in top_functions])
            prompt_sections.append(f"**Your function word pattern**: {func_desc}")

        # Sentence structure
        avg_len = profile['avg_sentence_length']
        prompt_sections.append(f"**Your sentence rhythm**: {avg_len:.1f} words average")

        # Style markers
        if profile['style_markers']:
            markers = ", ".join(profile['style_markers'][:5])
            prompt_sections.append(f"**Your style markers**: {markers}")

        # Writing instructions
        prompt_sections.append("\n## WRITE IN THIS VOICE:")
        prompt_sections.append("- Use natural contractions (I'm, don't, you're)")
        prompt_sections.append("- Mix short and medium sentences naturally")
        prompt_sections.append("- Be direct and conversational")
        prompt_sections.append("- Use your characteristic phrases and patterns")
        prompt_sections.append("- Sound authentic, not like generic AI")

        # Common phrases
        if profile['common_phrases']:
            prompt_sections.append(f"\n## YOUR COMMON PHRASES:")
            prompt_sections.append(", ".join(profile['common_phrases'][:10]))

        # Quality check
        prompt_sections.append("\n## QUALITY CHECK:")
        prompt_sections.append("Would this sound natural coming from you?")
        prompt_sections.append("If not → make it more conversational and authentic")

        return "\n".join(prompt_sections)

def main():
    """Main execution"""
    system = FinalStylePreservationSystem()

    # Run analysis with limited email processing for speed
    analysis, prompt = system.run_full_analysis(email_limit=10000)

    # Save results
    system.save_results(analysis, prompt)

    return analysis, prompt

if __name__ == "__main__":
    main()
