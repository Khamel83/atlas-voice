#!/usr/bin/env python3
"""
AI Voice Generator using Google Flash 2.5 Lite
Generates fake content in Omar's voice for authenticity testing
"""

import json
import random
import openai
from pathlib import Path
from typing import List, Dict, Tuple
import os

class AIVoiceGenerator:
    """Generates AI content in Omar's voice using OpenRouter API"""

    def __init__(self):
        # Load voice profile
        with open('/Users/khamel83/dev/atlas-voice/prompts/OMARS_ULTIMATE_VOICE_PROFILE_COMPLETE.txt', 'r') as f:
            self.voice_profile = f.read()

        # Set up OpenRouter for Google Flash 2.5 Lite
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            default_headers={
                "HTTP-Referer": "https://github.com/omar/speech-project",
                "X-Title": "Omar's Voice Analysis Project"
            }
        )

        self.model = "google/gemini-2.5-flash-lite"

    def generate_fake_content(self, topic: str, length_hint: int = 250) -> str:
        """Generate fake content in Omar's voice on a given topic"""
        system_prompt = f"""You are Omar. You must write exactly like Omar based on this comprehensive voice profile:

{self.voice_profile}

WRITING REQUIREMENTS:
- Write directly from "I" perspective
- Use sentences averaging 13-15 words
- Be analytical and systematic
- Use personal pronouns frequently ("I", "you")
- Sound thoughtful and deliberate
- Be conversational but educated
- Write about {length_hint} characters total
- Make it sound authentic to Omar's communication style
- Do not mention you are an AI or that this is generated
- Write as if you're naturally communicating about the topic

TOPIC: {topic}

Generate your response now, writing exactly as Omar would:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Write a natural response about {topic} in your authentic voice."}
                ],
                temperature=0.7,
                max_tokens=400
            )

            fake_content = response.choices[0].message.content.strip()
            return fake_content

        except Exception as e:
            print(f"⚠️  AI generation failed: {e}")
            return self._fallback_generation(topic, length_hint)

    def _fallback_generation(self, topic: str, length_hint: int) -> str:
        """Fallback generation if API fails"""
        # Use patterns from voice profile to generate content
        omar_patterns = [
            f"I think that {topic} is really interesting because it shows how we approach problems systematically.",
            f"The way that I see it, {topic} requires us to think about the underlying patterns and structures.",
            f"What we need to do with {topic} is break it down into manageable components and analyze each part.",
            f"I've been thinking about {topic} lately, and I believe there's a more efficient way to approach this.",
            f"You know, when it comes to {topic}, I find that the most important thing is to understand the core principles."
        ]

        return random.choice(omar_patterns)

    def generate_test_content(self, real_samples: List[str]) -> Dict:
        """Generate fake content to pair with real samples for testing"""
        print(f"🤖 Generating AI content in Omar's voice...")

        test_content = []

        for i, real_sample in enumerate(real_samples):
            # Extract a theme from the real sample to generate related fake content
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
        """Extract a theme/topic from text for AI generation"""
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

    generator = AIVoiceGenerator()
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
