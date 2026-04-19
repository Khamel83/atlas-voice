#!/usr/bin/env python3
"""
Enhanced AI Voice Generator
Uses enhanced content analysis for realistic voice generation
"""

import requests
import random
from typing import List, Dict
from pathlib import Path
import json

class EnhancedAIVoiceGenerator:
    """AI Voice Generator with enhanced content knowledge"""

    def __init__(self):
        self.enhanced_prompt = """# OMAR'S ENHANCED VOICE PROFILE
*Generated from 8.7M character corpus analysis*

## CONTENT DOMAINS
- **Academic Writing**: Art history papers, university assignments, formal essays
- **Professional Communication**: Job applications, research assistant inquiries, work emails
- **Personal Communication**: Direct, efficient coordination with friends and colleagues
- **Technical Content**: Data analysis, university topics, academic subjects

## WRITING STYLE PATTERNS
- **Formality Level**: Adapts to context - formal for academic/work, casual for personal
- **Sentence Structure**: Direct and purposeful, minimal filler words
- **Personal Markers": Uses lowercase often, specific details, practical next steps
- **Common Phrases**: "do you want to...", "let me know...", "should we meet..."

## KNOWLEDGE BOUNDARIES
**DO Write About:**
- University life, academic work, job searches
- Art history, research, data analysis
- Social coordination, meeting planning
- Technical problem-solving (Excel, university topics)

**AVOID:**
- Alcohol-related content (beer, bars, drinking)
- Sports fandom and team preferences
- Religious topics and references
- Generic social invitations outside known patterns

## COMMUNICATION APPROACH
- Direct and purposeful communication
- Specific details and practical information
- Minimal small talk or filler content
- Focus on coordination and problem-solving
- Adapts formality based on context and audience

## EXAMPLES OF AUTHENTIC VOICE
1. **Work Context**: "hey can you ask mom if she can get a hp648c color cartridge from work. If she can that would be really good, ok thanks"
2. **Academic Context**: "Art History 101 - Formal Analysis and the Nature of Seeing Artist: Unknown... This painting is of the Sacrifice of Polyxema..."
3. **Social Coordination**: "Dudes, I'm coming into Chicago Friday the 26th and then sticking around to attend a conference on Monday and Tuesday..."

## INSTRUCTIONS FOR VOICE GENERATION
Generate content that matches Omar's authentic voice patterns, topics, and knowledge boundaries. Use direct, purposeful language with specific details. Avoid content that falls outside his known interests and experiences. Adapt formality based on context while maintaining his efficient communication style.
"""
        self.api_key = self._load_api_key()
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.5-flash-lite"

    def _load_api_key(self) -> str:
        """Load API key from environment or config"""
        import os
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        if api_key:
            return api_key

        try:
            config_path = Path('/Users/khamel83/dev/atlas-voice/config/api_keys.json')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('openrouter_api_key', '')
        except:
            pass

        return ''

    def generate_enhanced_content(self, theme: str, target_length: int = 250) -> str:
        """Generate content using enhanced voice profile"""

        if not self.api_key:
            return self._fallback_generation(theme, target_length)

        # Create prompt that includes knowledge boundaries
        prompt = f"""{{self.enhanced_prompt}}

TASK: Generate content on theme '{theme}' that matches the voice profile above.
LENGTH: Approximately {{target_length}} characters
REQUIREMENTS:
- Stay within knowledge boundaries (avoid alcohol, sports, religion)
- Match Omar's direct, purposeful communication style
- Include specific details and practical information
- Adapt formality based on theme context

Generate now:"""

        try:
            headers = {{
                "Authorization": f"Bearer {{self.api_key}}",
                "Content-Type": "application/json"
            }}

            payload = {{
                "model": self.model,
                "messages": [{{"role": "user", "content": prompt}}],
                "max_tokens": max(100, target_length // 3),
                "temperature": 0.8
            }}

            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                generated_text = result['choices'][0]['message']['content'].strip()
                print(f"✅ Enhanced generation: {{len(generated_text)}} chars")
                return generated_text
            else:
                print(f"❌ API error: {{response.status_code}}")
                return self._fallback_generation(theme, target_length)

        except Exception as e:
            print(f"❌ Generation failed: {{e}}")
            return self._fallback_generation(theme, target_length)

    def _fallback_generation(self, theme: str, target_length: int) -> str:
        """Enhanced fallback using knowledge boundaries"""
        # Use themes and content that match known domains
        theme_templates = {{
            'work': "hey regarding the project, we need to figure out the next steps. let me know when you're free to discuss.",
            'planning': "so for the weekend plans, i'm thinking we should meet around 2pm. does that work for everyone?",
            'academic': "for the assignment, we need to focus on the main requirements. have you started the outline yet?",
            'social': "hey, wanna grab coffee sometime next week? i'm thinking tuesday or wednesday afternoon."
        }}

        base = theme_templates.get(theme, theme_templates['social'])
        while len(base) < target_length * 0.8:
            base += " let me know what works for you."

        return base[:target_length]

if __name__ == "__main__":
    generator = EnhancedAIVoiceGenerator()
    result = generator.generate_enhanced_content("work", 200)
    print(f"Generated: {{result}}")
