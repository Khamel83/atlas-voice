#!/usr/bin/env python3
"""
AI Voice Generator (API Version)
Generates fake content in Omar's voice using Google Flash 2.5 Lite via OpenRouter
"""

import json
import requests
import random
from pathlib import Path
from typing import List, Dict

class AIVoiceGeneratorAPI:
    """Generates AI content in Omar's voice using LLM API"""

    def __init__(self):
        # Load voice profile
        with open('/Users/khamel83/dev/atlas-voice/prompts/OMARS_ULTIMATE_VOICE_PROFILE_COMPLETE.txt', 'r') as f:
            self.voice_profile = f.read()

        # OpenRouter API configuration
        self.api_key = self._load_api_key()
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.5-flash-lite"

    def _load_api_key(self) -> str:
        """Load API key from environment or config"""
        import os

        # Try environment variable first
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            return api_key

        # Try config file
        config_path = Path('/Users/khamel83/dev/atlas-voice/config/api_keys.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('openrouter_api_key', '')

        return ''

    def generate_fake_content(self, theme: str, target_length: int = 250) -> str:
        """Generate fake content in Omar's voice using LLM API"""

        if not self.api_key:
            print("⚠️  No API key found, falling back to pattern-based generation")
            return self._fallback_generation(theme, target_length)

        # Create improved prompt focusing on direct communication
        prompt = f"""You are Omar. Write text that sounds EXACTLY like Omar's authentic voice from his real emails.

REAL examples of Omar's actual email writing style:

"do you want to play basketball tomorrow (thursday) after your pape class. we are going to work out till like 1 and then want to play basketball after that. tell me what you are gonna do. omar"

"shippensburg, PA is no longer part of sarah palin's real america. It was already off the list because of the suspicious suffix to the city's name."

"don't take forever to watch it, don't slow down the netflix stealing machine. hamlet starts at 730. should we meet at the theater right before or do you think you can get off work early enough to catch dinner."

"with sam. im not sure what you told him (its not important anymore) but it seems as though my explanation was 'possibly the most obnoxious email ive ever received' - direct quote."

"Dudes, I'm coming into Chicago Friday the 26th and then sticking around to attend a conference on Monday and Tuesday. I have my sleeping situation figured out as well as a ticket to cubs/sox on saturday, but no other plans."

OMAR'S REAL PATTERNS:
- Direct and purposeful communication
- Casual but efficient - gets to the point
- Uses lowercase often, minimal punctuation
- Specific details and references
- Sometimes blunt or frank
- NOT filled with "like, you know, so like" verbal filler
- Questions are direct: "do you want to..." "should we..."
- Often ends with practical next steps

THEME: {theme}
LENGTH: approximately {target_length} characters

Write as Omar would actually write an email - direct, casual, purposeful. NO excessive filler words.

Write now:"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max(100, target_length // 3),
                "temperature": 0.8
            }

            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                generated_text = result['choices'][0]['message']['content'].strip()

                # Clean up any meta-commentary
                lines = generated_text.split('\n')
                clean_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(('Here', 'This', 'I am', 'As Omar')):
                        clean_lines.append(line)

                final_text = ' '.join(clean_lines)

                # Ensure reasonable length
                if len(final_text) > target_length * 1.5:
                    final_text = final_text[:target_length + 50]
                    # Cut at last complete sentence
                    last_period = final_text.rfind('.')
                    if last_period > target_length * 0.7:
                        final_text = final_text[:last_period + 1]

                print(f"✅ Generated {len(final_text)} characters via API")
                return final_text

            else:
                print(f"❌ API error {response.status_code}: {response.text}")
                return self._fallback_generation(theme, target_length)

        except Exception as e:
            print(f"❌ API request failed: {e}")
            return self._fallback_generation(theme, target_length)

    def _fallback_generation(self, theme: str, target_length: int) -> str:
        """Fallback to simple but coherent generation"""

        # Use actual phrases from Omar's voice profile
        common_starters = [
            "I think that",
            "The way I see it",
            "You know what",
            "I've been thinking about",
            "The thing is",
            "From my perspective"
        ]

        common_continuations = [
            "we need to figure out",
            "it's important to understand",
            "we should probably",
            "I want to make sure",
            "we can definitely",
            "it makes sense to"
        ]

        # Create a more coherent sentence
        starter = random.choice(common_starters)
        continuation = random.choice(common_continuations)

        # Add theme-specific content
        theme_contexts = {
            'planning': "how we're going to approach this project",
            'technology': "the best way to implement this system",
            'daily_life': "what we're doing this weekend",
            'work': "how to get this task completed efficiently"
        }

        context = theme_contexts.get(theme, "what we need to focus on")

        fake_content = f"{starter} {continuation} {context}. I mean, we've talked about this before and I think the approach should be straightforward. Let's just make sure we're all on the same page here."

        # Adjust length
        while len(fake_content) < target_length * 0.8:
            fake_content += " And honestly, that's probably the best way to handle it going forward."

        if len(fake_content) > target_length * 1.2:
            fake_content = fake_content[:target_length]
            last_period = fake_content.rfind('.')
            if last_period > target_length * 0.7:
                fake_content = fake_content[:last_period + 1]

        return fake_content

    def generate_multiple_fake_contents(self, themes: List[str], target_length: int = 250) -> List[Dict]:
        """Generate multiple fake content pieces"""
        results = []

        for i, theme in enumerate(themes):
            print(f"🎭 Generating fake content {i+1}/{len(themes)} (theme: {theme})")
            fake_content = self.generate_fake_content(theme, target_length)

            results.append({
                'theme': theme,
                'content': fake_content,
                'length': len(fake_content)
            })

        return results

if __name__ == "__main__":
    generator = AIVoiceGeneratorAPI()

    # Test generation
    themes = ['planning', 'technology', 'daily_life']
    results = generator.generate_multiple_fake_contents(themes)

    for result in results:
        print(f"\n📝 Theme: {result['theme']}")
        print(f"📊 Length: {result['length']}")
        print(f"📄 Content: {result['content']}")
        print("-" * 80)
