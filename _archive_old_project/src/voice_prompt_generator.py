#!/usr/bin/env python3
"""
Voice Prompt Generator - Bridge between Nuclear Safe Room and Final Voice Prompt
Converts processed linguistic patterns into usable AI voice prompts
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics

class VoicePromptGenerator:
    """
    Generates voice prompts from nuclear safe room data
    """

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.room_two_dir = self.base_dir / "room_two_database"
        self.db_path = self.room_two_dir / "speech_patterns.db"

    def load_patterns_from_room_two(self, batch_id: str = None) -> Dict:
        """Load processed patterns from Room Two database"""

        if not self.db_path.exists():
            return {}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        patterns = {
            'metadata': {
                'total_words': 0,
                'total_files': 0,
                'batch_count': 0,
                'analysis_date': datetime.now().isoformat()
            },
            'function_words': {},
            'structural_patterns': {
                'bigrams': [],
                'trigrams': []
            },
            'vocabulary_metrics': {},
            'style_markers': {
                'casual': {},
                'formal': {}
            }
        }

        # Get basic stats
        if batch_id:
            cursor.execute('''
                SELECT SUM(total_words_processed), SUM(total_files_processed)
                FROM processing_batches
                WHERE batch_id = ? AND processing_status = 'complete'
            ''', (batch_id,))
        else:
            cursor.execute('''
                SELECT SUM(total_words_processed), SUM(total_files_processed)
                FROM processing_batches
                WHERE processing_status = 'complete'
            ''')

        words, files = cursor.fetchone()
        patterns['metadata']['total_words'] = words or 0
        patterns['metadata']['total_files'] = files or 0

        # Load function words
        if batch_id:
            cursor.execute('''
                SELECT word, frequency, relative_frequency
                FROM function_words
                WHERE source_batch_id = ?
                ORDER BY frequency DESC
                LIMIT 50
            ''', (batch_id,))
        else:
            cursor.execute('''
                SELECT word, frequency, relative_frequency
                FROM function_words
                ORDER BY frequency DESC
                LIMIT 50
            ''')

        for word, freq, rel_freq in cursor.fetchall():
            patterns['function_words'][word] = freq

        # Load structural patterns
        if batch_id:
            cursor.execute('''
                SELECT pattern_value, frequency
                FROM structural_patterns
                WHERE source_batch_id = ? AND pattern_type = 'bigrams'
                ORDER BY frequency DESC
                LIMIT 20
            ''', (batch_id,))
        else:
            cursor.execute('''
                SELECT pattern_value, frequency
                FROM structural_patterns
                WHERE pattern_type = 'bigrams'
                ORDER BY frequency DESC
                LIMIT 20
            ''')

        patterns['structural_patterns']['bigrams'] = [row[0] for row in cursor.fetchall()]

        if batch_id:
            cursor.execute('''
                SELECT pattern_value, frequency
                FROM structural_patterns
                WHERE source_batch_id = ? AND pattern_type = 'trigrams'
                ORDER BY frequency DESC
                LIMIT 10
            ''', (batch_id,))
        else:
            cursor.execute('''
                SELECT pattern_value, frequency
                FROM structural_patterns
                WHERE pattern_type = 'trigrams'
                ORDER BY frequency DESC
                LIMIT 10
            ''')

        patterns['structural_patterns']['trigrams'] = [row[0] for row in cursor.fetchall()]

        # Load vocabulary metrics
        if batch_id:
            cursor.execute('''
                SELECT metric_type, metric_value
                FROM vocabulary_metrics
                WHERE source_batch_id = ?
            ''', (batch_id,))
        else:
            cursor.execute('''
                SELECT metric_type, AVG(metric_value)
                FROM vocabulary_metrics
                GROUP BY metric_type
            ''')

        for metric_type, metric_value in cursor.fetchall():
            patterns['vocabulary_metrics'][metric_type] = metric_value

        # Load style markers
        if batch_id:
            cursor.execute('''
                SELECT marker_type, marker_value, frequency
                FROM style_markers
                WHERE source_batch_id = ?
            ''', (batch_id,))
        else:
            cursor.execute('''
                SELECT marker_type, marker_value, frequency
                FROM style_markers
            ''')

        for marker_type, marker_value, frequency in cursor.fetchall():
            if marker_type not in patterns['style_markers']:
                patterns['style_markers'][marker_type] = {}
            patterns['style_markers'][marker_type][marker_value] = frequency

        conn.close()

        return patterns

    def generate_voice_prompt(self, patterns: Dict, target_length: int = 3500) -> str:
        """Generate the final voice prompt from patterns"""

        if not patterns or patterns['metadata']['total_words'] == 0:
            return "# No Data Available\n\nNo voice patterns found. Please process some data first."

        prompt_sections = [
            "# YOUR VOICE PROFILE",
            "",
            f"**Based on analysis of {patterns['metadata']['total_words']:,} words from {patterns['metadata']['total_files']} files**",
            ""
        ]

        # Function words section
        if patterns['function_words']:
            top_functions = list(patterns['function_words'].keys())[:15]
            prompt_sections.extend([
                "## Your Language Patterns",
                "",
                "**Most frequent words:**",
                f"{', '.join(top_functions)}",
                ""
            ])

        # Vocabulary metrics
        if patterns['vocabulary_metrics']:
            avg_word_len = patterns['vocabulary_metrics'].get('avg_word_length', 0)
            avg_sent_len = patterns['vocabulary_metrics'].get('avg_sentence_length', 0)
            vocab_richness = patterns['vocabulary_metrics'].get('vocabulary_richness', 0)

            prompt_sections.extend([
                "## Your Writing Style",
                "",
                f"- **Average word length:** {avg_word_len:.1f} characters",
                f"- **Average sentence length:** {avg_sent_len:.1f} words",
                f"- **Vocabulary richness:** {vocab_richness:.3f}",
                ""
            ])

        # Structural patterns
        if patterns['structural_patterns']['bigrams']:
            prompt_sections.extend([
                "## Your Common Phrases",
                "",
                "Frequently used combinations:",
                f"{', '.join(patterns['structural_patterns']['bigrams'][:10])}",
                ""
            ])

        # Style markers
        casual_markers = patterns['style_markers'].get('casual', {})
        formal_markers = patterns['style_markers'].get('formal', {})

        if casual_markers or formal_markers:
            prompt_sections.extend([
                "## Your Style Tendencies",
                ""
            ])

            if casual_markers:
                top_casual = sorted(casual_markers.items(), key=lambda x: x[1], reverse=True)[:5]
                casual_list = [f"'{marker}' ({count} times)" for marker, count in top_casual]
                prompt_sections.append(f"**Casual patterns:** {', '.join(casual_list)}")

            if formal_markers:
                top_formal = sorted(formal_markers.items(), key=lambda x: x[1], reverse=True)[:5]
                formal_list = [f"'{marker}' ({count} times)" for marker, count in top_formal]
                prompt_sections.append(f"**Formal patterns:** {', '.join(formal_list)}")

            prompt_sections.append("")

        # Writing guidelines
        prompt_sections.extend([
            "## Writing Guidelines",
            "",
            "When writing in your voice:",
            f"- Use sentences averaging {patterns['vocabulary_metrics'].get('avg_sentence_length', 15):.0f} words",
            f"- Maintain vocabulary complexity at level {patterns['vocabulary_metrics'].get('avg_word_length', 4):.1f} characters",
            "- Incorporate your common phrases naturally",
            "- Balance casual and formal tendencies as shown above",
            "",
            "## Quality Check",
            "",
            "Before finalizing any text:",
            "- Does it sound naturally like you?",
            "- Does it use your characteristic phrases?",
            "- Is the sentence rhythm consistent with your patterns?",
            "- Would you be comfortable saying this out loud?",
            "",
            "---",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            f"*Based on {patterns['metadata']['total_words']:,} words of authentic writing*"
        ])

        prompt_text = "\n".join(prompt_sections)

        # Trim to target length if needed
        if len(prompt_text) > target_length:
            # Remove less critical sections first
            if len(prompt_text) > target_length:
                prompt_sections = prompt_sections[:-2]  # Remove generation timestamp
                prompt_text = "\n".join(prompt_sections)

        return prompt_text

    def create_complete_voice_profile(self, batch_id: str = None, output_dir: str = "profiles") -> Tuple[str, str]:
        """
        Create complete voice profile (JSON + prompt)
        Returns (profile_path, prompt_path)
        """

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # Load patterns
        patterns = self.load_patterns_from_room_two(batch_id)

        if not patterns:
            raise ValueError("No patterns found in Room Two database")

        # Generate profile ID
        profile_id = f"voice_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if batch_id:
            profile_id = f"voice_profile_{batch_id}"

        # Generate voice prompt
        prompt = self.generate_voice_prompt(patterns)

        # Create profile data
        profile_data = {
            'profile_id': profile_id,
            'batch_id': batch_id,
            'created_at': datetime.now().isoformat(),
            'metadata': patterns['metadata'],
            'patterns': patterns,
            'prompt_stats': {
                'prompt_length': len(prompt),
                'word_count': len(prompt.split()),
                'target_length': 3500
            }
        }

        # Save profile
        profile_path = output_dir / f"{profile_id}.json"
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f, indent=2)

        # Save prompt
        prompt_path = output_dir / f"{profile_id}.txt"
        with open(prompt_path, 'w') as f:
            f.write(prompt)

        print(f"✅ Voice profile created:")
        print(f"   Profile: {profile_path}")
        print(f"   Prompt: {prompt_path}")
        print(f"   Based on {patterns['metadata']['total_words']:,} words")

        return str(profile_path), str(prompt_path)

    def get_available_profiles(self, profiles_dir: str = "profiles") -> List[Dict]:
        """Get list of available voice profiles"""
        profiles_dir = Path(profiles_dir)
        profiles = []

        if profiles_dir.exists():
            for profile_file in profiles_dir.glob("*.json"):
                try:
                    with open(profile_file, 'r') as f:
                        profile_data = json.load(f)
                        profiles.append({
                            'profile_id': profile_data.get('profile_id', profile_file.stem),
                            'batch_id': profile_data.get('batch_id'),
                            'created_at': profile_data.get('created_at'),
                            'total_words': profile_data.get('metadata', {}).get('total_words', 0),
                            'file_path': str(profile_file),
                            'has_prompt': (profiles_dir / f"{profile_file.stem}.txt").exists()
                        })
                except:
                    pass

        # Sort by creation date (newest first)
        profiles.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return profiles

def main():
    """Test voice prompt generator"""
    print("🎤 VOICE PROMPT GENERATOR")
    print("=" * 40)

    generator = VoicePromptGenerator()

    # Check Room Two data
    print("📊 Checking Room Two data...")
    patterns = generator.load_patterns_from_room_two()

    if patterns['metadata']['total_words'] > 0:
        print(f"✅ Found {patterns['metadata']['total_words']:,} words of processed data")
        print(f"   From {patterns['metadata']['total_files']} files")

        # Generate prompt
        prompt = generator.generate_voice_prompt(patterns)
        print(f"\n📝 Generated voice prompt ({len(prompt)} characters):")
        print("=" * 50)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("=" * 50)

        # Create complete profile
        create_profile = input("\n💾 Create complete profile? (y/N): ").lower()
        if create_profile == 'y':
            profile_path, prompt_path = generator.create_complete_voice_profile()
            print(f"✅ Profile saved!")
    else:
        print("❌ No data found in Room Two")
        print("💡 Process some data first:")
        print("   python3 src/main.py nuclear-process /path/to/data")

if __name__ == "__main__":
    main()
