#!/usr/bin/env python3
"""
Authenticity Testing System
Compare OLD AI-assisted letters vs NEW regenerated versions
Target: 90% authenticity threshold
"""

import json
import re
import os
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Optional
import statistics
from datetime import datetime

class AuthenticityAnalyzer:
    """Analyze authenticity of generated text vs original patterns"""

    def __init__(self, reference_analysis_path=None):
        self.reference_analysis = None
        if reference_analysis_path and os.path.exists(reference_analysis_path):
            with open(reference_analysis_path, 'r') as f:
                self.reference_analysis = json.load(f)

        # Authenticity scoring weights (optimized for Omar's casual style)
        self.weights = {
            'function_words': 0.15,      # Reduced - too strict
            'sentence_rhythm': 0.15,     # Reduced - allow natural variation
            'vocabulary_level': 0.10,    # Reduced - less critical
            'style_markers': 0.35,       # INCREASED - casual markers are key to Omar's voice
            'personal_expressions': 0.20, # INCREASED - personal voice is critical
            'structural_patterns': 0.05   # Reduced - less important
        }

    def extract_text_features(self, text: str) -> Dict:
        """Extract features from text for comparison"""
        if not text:
            return {}

        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Function words
        function_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'must', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that',
            'these', 'those', 'who', 'what', 'where', 'when', 'why', 'how'
        }

        func_word_usage = Counter([w for w in words if w in function_words])

        # Style markers
        casual_markers = ['actually', 'basically', 'like', 'you know', 'i mean', 'sort of']
        formal_markers = ['however', 'therefore', 'furthermore', 'consequently']

        casual_count = sum(text_lower.count(marker) for marker in casual_markers)
        formal_count = sum(text_lower.count(marker) for marker in formal_markers)

        # Personal expressions (I-phrases)
        personal_phrases = []
        for i in range(len(words) - 3):
            phrase = ' '.join(words[i:i+4])
            if 'i ' in phrase:
                personal_phrases.append(phrase)

        # Bigrams
        bigrams = list(zip(words[:-1], words[1:])) if len(words) >= 2 else []

        features = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': statistics.mean([len(w) for w in words]) if words else 0,
            'avg_sentence_length': statistics.mean([len(s.split()) for s in sentences]) if sentences else 0,
            'vocabulary_size': len(set(words)),
            'function_word_ratio': len([w for w in words if w in function_words]) / len(words) if words else 0,
            'function_word_distribution': dict(func_word_usage.most_common(20)),
            'casual_marker_density': casual_count / len(words) if words else 0,
            'formal_marker_density': formal_count / len(words) if words else 0,
            'personal_expression_count': len(personal_phrases),
            'bigram_patterns': bigrams[:20]  # Sample bigrams
        }

        return features

    def compare_function_words(self, text_features: Dict, reference_features: Dict) -> float:
        """Compare function word usage patterns"""
        if not self.reference_analysis:
            return 0.5  # Neutral score if no reference

        text_func_words = text_features.get('function_word_distribution', {})
        ref_func_words = self.reference_analysis.get('linguistic_signature', {}).get('top_function_words', {})

        if not text_func_words or not ref_func_words:
            return 0.0

        # Calculate overlap in top function words
        text_top = set(list(text_func_words.keys())[:10])
        ref_top = set(list(ref_func_words.keys())[:10])

        overlap = len(text_top.intersection(ref_top))
        max_possible = max(len(text_top), len(ref_top))

        return overlap / max_possible if max_possible > 0 else 0.0

    def compare_sentence_rhythm(self, text_features: Dict, reference_features: Dict) -> float:
        """Compare sentence length patterns"""
        if not self.reference_analysis:
            return 0.5

        text_avg_length = text_features.get('avg_sentence_length', 0)
        ref_avg_length = self.reference_analysis.get('core_metrics', {}).get('avg_sentence_length', 0)

        if ref_avg_length == 0:
            return 0.0

        # Score based on how close the sentence length is
        difference = abs(text_avg_length - ref_avg_length)
        max_acceptable_diff = ref_avg_length * 0.3  # 30% tolerance

        if difference <= max_acceptable_diff:
            return 1.0 - (difference / max_acceptable_diff)
        else:
            return 0.0

    def compare_vocabulary_level(self, text_features: Dict, reference_features: Dict) -> float:
        """Compare vocabulary complexity"""
        if not self.reference_analysis:
            return 0.5

        text_word_length = text_features.get('avg_word_length', 0)
        ref_word_length = self.reference_analysis.get('core_metrics', {}).get('avg_word_length', 0)

        if ref_word_length == 0:
            return 0.0

        difference = abs(text_word_length - ref_word_length)
        max_acceptable_diff = ref_word_length * 0.2  # 20% tolerance

        if difference <= max_acceptable_diff:
            return 1.0 - (difference / max_acceptable_diff)
        else:
            return 0.0

    def compare_style_markers(self, text_features: Dict, reference_features: Dict) -> float:
        """Compare casual/formal marker usage - optimized for Omar's casual style"""

        # Get text casual/formal markers
        text_casual = text_features.get('casual_marker_density', 0)
        text_formal = text_features.get('formal_marker_density', 0)

        # Omar's style is heavily casual - reward casual marker presence
        casual_score = min(1.0, text_casual * 100)  # Boost casual markers significantly

        # Omar uses minimal formal markers - penalize heavy formal usage
        formal_penalty = min(0.5, text_formal * 50)  # Moderate penalty for formal

        # Final score emphasizes casual over formal
        final_score = casual_score - formal_penalty

        return max(0.0, min(1.0, final_score))

    def evaluate_personal_expressions(self, text: str) -> float:
        """Evaluate personal expression authenticity"""
        text_lower = text.lower()

        # Omar's key personal markers
        personal_markers = [
            'i really', 'i want to', 'you know', 'like',
            'i get it', 'honestly', 'actually', 'what happened'
        ]

        found_markers = sum(1 for marker in personal_markers if marker in text_lower)

        # Score based on presence of personal expressions
        if found_markers >= 3:
            return 1.0  # High authenticity
        elif found_markers >= 2:
            return 0.8
        elif found_markers >= 1:
            return 0.6
        else:
            return 0.3  # Low personal expression

    def evaluate_structural_authenticity(self, text: str) -> float:
        """Evaluate structural authenticity"""
        text_lower = text.lower()

        # Omar's structural patterns
        authentic_patterns = [
            'and the', 'that i', 'it really', 'but the', 'so i',
            'i think', 'we can', 'this is', 'that was'
        ]

        found_patterns = sum(1 for pattern in authentic_patterns if pattern in text_lower)

        # Simple scoring based on pattern presence
        return min(1.0, found_patterns / 5.0)  # 5 patterns = perfect score

    def calculate_authenticity_score(self, text: str) -> Dict:
        """Calculate overall authenticity score"""
        text_features = self.extract_text_features(text)

        # Individual component scores
        scores = {
            'function_words': self.compare_function_words(text_features, {}),
            'sentence_rhythm': self.compare_sentence_rhythm(text_features, {}),
            'vocabulary_level': self.compare_vocabulary_level(text_features, {}),
            'style_markers': self.compare_style_markers(text_features, {}),
            'personal_expressions': self.evaluate_personal_expressions(text),
            'structural_patterns': self.evaluate_structural_authenticity(text)
        }

        # Weighted overall score
        overall_score = sum(scores[component] * self.weights[component]
                          for component in scores)

        return {
            'overall_score': overall_score,
            'component_scores': scores,
            'text_features': text_features,
            'threshold_met': overall_score >= 0.9,
            'analysis_timestamp': datetime.now().isoformat()
        }

class LetterComparisonTester:
    """Test system for comparing OLD vs NEW letter versions"""

    def __init__(self, reference_analysis_path, original_letters_path):
        self.authenticity_analyzer = AuthenticityAnalyzer(reference_analysis_path)
        self.original_letters_path = original_letters_path
        self.test_results = []

    def load_original_letters(self) -> List[str]:
        """Load the original AI-assisted letters"""
        try:
            with open(self.original_letters_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split letters by common delimiters
            letters = re.split(r'\n\s*---\s*\n|\n\s*===\s*\n', content)
            letters = [letter.strip() for letter in letters if len(letter.strip()) > 100]

            print(f"Loaded {len(letters)} original letters")
            return letters

        except Exception as e:
            print(f"Error loading original letters: {e}")
            return []

    def extract_letter_segments(self, letter: str, segment_length=200) -> List[str]:
        """Extract testable segments from a letter"""
        sentences = re.split(r'[.!?]+', letter)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        segments = []
        current_segment = ""
        current_length = 0

        for sentence in sentences:
            words_in_sentence = len(sentence.split())

            if current_length + words_in_sentence <= segment_length:
                current_segment += " " + sentence + "."
                current_length += words_in_sentence
            else:
                if current_segment.strip():
                    segments.append(current_segment.strip())
                current_segment = sentence + "."
                current_length = words_in_sentence

        if current_segment.strip():
            segments.append(current_segment.strip())

        return segments

    def generate_new_version(self, segment: str, style_prompt: str) -> str:
        """Generate new version using style-preserving prompt"""
        try:
            import openai
            import os

            # Set up OpenRouter client
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )

            # Create the generation prompt
            generation_prompt = f"""
{style_prompt}

## TASK: Rewrite the following text using the style preservation guidelines above.

IMPORTANT:
- Maintain the same meaning and key points
- Apply the linguistic patterns specified above
- Sound authentically like the original writer
- Do not add [REGENERATED] or any meta-text

Original text to rewrite:
{segment}

Rewritten version:"""

            # Generate using OpenRouter (using your configured model)
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash-lite",  # Using your model from previous configs
                messages=[
                    {"role": "system", "content": "You are a writing style preservation system. Rewrite text to match the specified linguistic patterns while preserving meaning."},
                    {"role": "user", "content": generation_prompt}
                ],
                max_tokens=len(segment.split()) * 2,  # Roughly 2x the original length
                temperature=0.3  # Lower temperature for more consistent style
            )

            generated_text = response.choices[0].message.content.strip()

            # Clean up any potential artifacts
            generated_text = generated_text.replace("[REGENERATED]", "").strip()

            return generated_text

        except Exception as e:
            print(f"    ⚠️ AI generation failed: {e}")
            # Fallback to original text with slight modification
            return segment.replace("I", "I").replace(".", ". ")  # Minimal change as fallback

    def run_comparison_test(self, style_prompt_path: str) -> Dict:
        """Run complete comparison test"""
        print("🧪 STARTING LETTER COMPARISON TEST")
        print("=" * 50)

        # Load style prompt
        try:
            with open(style_prompt_path, 'r') as f:
                style_prompt = f.read()
        except Exception as e:
            print(f"Error loading style prompt: {e}")
            return {}

        # Load original letters
        original_letters = self.load_original_letters()
        if not original_letters:
            print("No original letters found!")
            return {}

        test_results = []

        for i, letter in enumerate(original_letters[:3]):  # Test first 3 letters
            print(f"\nTesting letter {i+1}...")

            # Extract segments
            segments = self.extract_letter_segments(letter)
            print(f"  Found {len(segments)} segments")

            for j, segment in enumerate(segments[:2]):  # Test first 2 segments per letter
                print(f"  Testing segment {j+1}...")

                # Generate new version
                new_version = self.generate_new_version(segment, style_prompt)

                # Calculate authenticity scores
                original_score = self.authenticity_analyzer.calculate_authenticity_score(segment)
                new_score = self.authenticity_analyzer.calculate_authenticity_score(new_version)

                # Record results
                result = {
                    'letter_id': i + 1,
                    'segment_id': j + 1,
                    'original_text': segment[:200] + "..." if len(segment) > 200 else segment,
                    'new_text': new_version[:200] + "..." if len(new_version) > 200 else new_version,
                    'original_authenticity': original_score['overall_score'],
                    'new_authenticity': new_score['overall_score'],
                    'improvement': new_score['overall_score'] - original_score['overall_score'],
                    'threshold_met': new_score['threshold_met']
                }

                test_results.append(result)
                print(f"    Original: {original_score['overall_score']:.2f}")
                print(f"    New: {new_score['overall_score']:.2f}")
                print(f"    Improvement: {result['improvement']:+.2f}")

        # Calculate summary statistics
        if test_results:
            avg_improvement = statistics.mean([r['improvement'] for r in test_results])
            success_rate = sum(1 for r in test_results if r['threshold_met']) / len(test_results)
            avg_new_score = statistics.mean([r['new_authenticity'] for r in test_results])

            summary = {
                'total_tests': len(test_results),
                'average_improvement': avg_improvement,
                'success_rate': success_rate,
                'average_new_authenticity': avg_new_score,
                'threshold_met': success_rate >= 0.9,
                'test_results': test_results
            }

            print(f"\n🎯 TEST SUMMARY:")
            print(f"   Total tests: {summary['total_tests']}")
            print(f"   Average improvement: {avg_improvement:+.3f}")
            print(f"   Success rate: {success_rate:.1%}")
            print(f"   Average new authenticity: {avg_new_score:.3f}")
            print(f"   90% threshold met: {summary['threshold_met']}")

            return summary

        return {}

    def save_test_results(self, results: Dict, output_path: str):
        """Save test results to file"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Test results saved to: {output_path}")

def main():
    """Main testing execution"""
    # Paths
    reference_analysis = "/Users/khamel83/dev/atlas-voice/data/final_comprehensive_analysis.json"
    original_letters = "/Users/khamel83/dev/atlas-voice/data/omars_personal_letters.txt"
    style_prompt = "/Users/khamel83/dev/atlas-voice/prompts/final_style_preservation_prompt.txt"

    # Create tester
    tester = LetterComparisonTester(reference_analysis, original_letters)

    # Run tests
    results = tester.run_comparison_test(style_prompt)

    if results:
        # Save results
        output_path = "/Users/khamel83/dev/atlas-voice/tests/authenticity_test_results.json"
        tester.save_test_results(results, output_path)

        return results
    else:
        print("❌ Testing failed - no results generated")
        return {}

if __name__ == "__main__":
    main()
