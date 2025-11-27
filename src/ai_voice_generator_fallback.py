#!/usr/bin/env python3
"""
AI Voice Generator (Fallback Version)
Generates fake content in Omar's voice using pattern-based generation
"""

import json
import random
from pathlib import Path
from typing import List, Dict

class AIVoiceGeneratorFallback:
    """Generates AI content in Omar's voice using pattern-based generation"""

    def __init__(self):
        # Load voice profile
        with open('/Users/khamel83/dev/atlas-voice/prompts/OMARS_ULTIMATE_VOICE_PROFILE_COMPLETE.txt', 'r') as f:
            self.voice_profile = f.read()

        # Omar's linguistic patterns extracted from analysis
        self.omar_patterns = {
            'sentence_starters': [
                "I think that", "The way that I see it", "What we need to do is",
                "I've been thinking about", "You know what I mean", "From my perspective",
                "The thing is", "What I'm trying to say is", "I believe that",
                "Let me think about this", "I want to make sure", "The point is"
            ],
            'connective_phrases': [
                "and then", "so that", "because of", "which means", "and that",
                "so we can", "to make sure", "and I think", "and you know",
                "and then we", "and that's", "and we need", "and I want"
            ],
            'analytical_markers': [
                "systematically", "analytical", "break down", "understand the",
                "figure out", "look at", "approach this", "think about",
                "examine", "consider", "evaluate", "assess"
            ],
            'personal_markers': ["I", "I'm", "I've", "my", "me", "you", "your", "we", "our"],
            'collaborative_markers': ["we should", "let us", "we need", "our goal", "together"],
            'solution_focus': ["can we", "how to", "what if", "let me", "we could", "should we"]
        }

        # Common topics based on email analysis
        self.topics = {
            'technology': ['app', 'software', 'device', 'computer', 'system', 'digital'],
            'daily_life': ['today', 'tonight', 'yesterday', 'morning', 'day', 'weekend'],
            'social': ['friend', 'people', 'meet', 'talk', 'call', 'message'],
            'work': ['project', 'work', 'meeting', 'task', 'deadline', 'team'],
            'planning': ['plan', 'going', 'will', 'should', 'need to', 'let us'],
            'opinions': ['think', 'believe', 'feel', 'opinion', 'view', 'perspective']
        }

    def generate_fake_content(self, theme: str, target_length: int = 250) -> str:
        """Generate fake content in Omar's voice using pattern-based approach"""
        # Choose sentence patterns
        num_sentences = random.randint(3, 6)
        sentences = []

        for i in range(num_sentences):
            if i == 0:
                # Start with a personal opener
                starter = random.choice(self.omar_patterns['sentence_starters'])
                sentence = f"{starter} "
            else:
                # Continue with connective phrase
                connector = random.choice(self.omar_patterns['connective_phrases'])
                sentence = f"{connector} "

            # Add analytical/evaluative content
            if random.random() > 0.5:
                analytical = random.choice(self.omar_patterns['analytical_markers'])
                sentence += f"{analytical} the {theme} "

            # Add personal perspective
            personal = random.choice(self.omar_patterns['personal_markers'])
            sentence += f"{personal} "

            # Add solution focus
            if random.random() > 0.6:
                solution = random.choice(self.omar_patterns['solution_focus'])
                sentence += f"{solution} "

            # Add topic-specific content
            topic_words = self.topics.get(theme, ['thing', 'stuff', 'aspect'])
            topic_word = random.choice(topic_words)
            sentence += f"the {topic_word}"

            # Ensure proper ending
            if not sentence.endswith(('.', '!', '?')):
                sentence += '.'

            sentences.append(sentence)

        # Combine sentences
        fake_content = ' '.join(sentences)

        # Adjust length to match target
        while len(fake_content) < target_length * 0.8:
            # Add another sentence
            additional = f" I think we should {random.choice(['consider', 'look at', 'think about'])} this {random.choice(topic_words)}."
            fake_content += additional

        while len(fake_content) > target_length * 1.5:
            # Trim from the end
            fake_content = fake_content[:int(target_length * 1.2)]
            if not fake_content.endswith(('.', '!', '?')):
                fake_content += '.'

        return fake_content.strip()

    def generate_test_content(self, real_samples: List[str]) -> Dict:
        """Generate fake content to pair with real samples for testing"""
        print(f"🤖 Generating AI content in Omar's voice (pattern-based)...")

        test_content = []

        for i, real_sample in enumerate(real_samples):
            # Extract a theme from the real sample
            theme = self._extract_theme(real_sample)

            print(f"📝 Test {i+1}: Generating content about '{theme}'")

            # Generate fake content
            fake_content = self.generate_fake_content(theme, len(real_sample))

            # Ensure minimum length
            while len(fake_content) < 200:
                fake_content = self.generate_fake_content(theme, len(real_sample))

            test_content.append({
                'test_number': i + 1,
                'real_content': real_sample,
                'fake_content': fake_content,
                'theme': theme,
                'real_length': len(real_sample),
                'fake_length': len(fake_content)
            })

        return test_content

    def _extract_theme(self, text: str) -> str:
        """Extract a theme/topic from text for generation"""
        # Simple keyword-based theme extraction
        themes = {
            'technology': ['tech', 'computer', 'software', 'app', 'digital', 'device'],
            'social': ['friend', 'people', 'party', 'meet', 'talk', 'social'],
            'work': ['work', 'project', 'job', 'meeting', 'deadline', 'task'],
            'daily life': ['today', 'tonight', 'yesterday', 'morning', 'day', 'time'],
            'opinions': ['think', 'believe', 'feel', 'opinion', 'view', 'perspective'],
            'planning': ['plan', 'going', 'will', 'should', 'need to', 'let us'],
            'communication': ['email', 'message', 'call', 'text', 'write', 'send'],
            'analysis': ['analyze', 'understand', 'figure out', 'break down', 'examine']
        }

        text_lower = text.lower()
        theme_scores = {}

        for theme, keywords in themes.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            theme_scores[theme] = score

        # Return theme with highest score, or default
        best_theme = max(theme_scores, key=theme_scores.get)
        return best_theme if theme_scores[best_theme] > 0 else 'daily life'

    def save_test_data(self, test_content: List[Dict]) -> None:
        """Save test data for administration"""
        with open('/Users/khamel83/dev/atlas-voice/data/generated_test_content.json', 'w') as f:
            json.dump(test_content, f, indent=2)

        print(f"💾 Generated test content saved to: data/generated_test_content.json")


def main():
    """Test the AI voice generator"""
    # Load real samples
    with open('/Users/khamel83/dev/atlas-voice/data/test_samples.json', 'r') as f:
        test_data = json.load(f)

    real_samples = test_data['real_samples'][:3]  # Use first 3 for testing

    generator = AIVoiceGeneratorFallback()
    test_content = generator.generate_test_content(real_samples)
    generator.save_test_data(test_content)

    print(f"\n🧪 GENERATED TEST CONTENT:")
    print("=" * 50)
    for test in test_content:
        print(f"\nTest {test['test_number']}:")
        print(f"Theme: {test['theme']}")
        print(f"Real ({test['real_length']} chars): {test['real_content'][:100]}...")
        print(f"Fake ({test['fake_length']} chars): {test['fake_content'][:100]}...")


if __name__ == "__main__":
    main()
