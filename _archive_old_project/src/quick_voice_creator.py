#!/usr/bin/env python3
"""
Quick Voice Creator - MVP Integration
Combines voice pattern extraction with dynamic prompt generation
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from voice_pattern_extractor import VoicePatternExtractor
from dynamic_prompt_generator import DynamicPromptGenerator

def create_voice_profile(data_path: str, output_file: str = "my_voice_profile.txt"):
    """Quick MVP: Extract voice patterns and generate personal prompt"""

    print(f"🎤 Analyzing your writing from: {data_path}")

    # Step 1: Extract voice patterns
    extractor = VoicePatternExtractor()
    voice_profile = extractor.extract_from_directory(data_path)

    print(f"✅ Voice patterns extracted!")
    print(f"   - Communication style: {voice_profile.characteristics.communication_style}")
    print(f"   - Key phrases: {len(voice_profile.characteristics.key_phrases)} found")

    # Step 2: Generate personalized prompt
    generator = DynamicPromptGenerator()
    personalized_prompt = generator.generate_prompt(voice_profile, target_model="claude")

    # Step 3: Save the result
    with open(output_file, 'w') as f:
        f.write(personalized_prompt)

    print(f"🎉 Your personalized AI voice prompt is ready!")
    print(f"📁 Saved to: {output_file}")
    print(f"💡 Use this with Claude to sound like yourself!")

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 quick_voice_creator.py /path/to/your/writing/samples")
        sys.exit(1)

    data_path = sys.argv[1]
    create_voice_profile(data_path)
