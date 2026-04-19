#!/usr/bin/env python3
"""
Generate Final 4000-Token Style-Preserving Prompt
Process ALL available data and create the ultimate prompt
"""

import sys
from pathlib import Path

# Add the core directory to path
sys.path.append(str(Path(__file__).parent / "core"))

from final_comprehensive_system import FinalStylePreservationSystem

def generate_ultimate_prompt():
    """Generate the final 4000-token prompt with ALL data"""

    print("🚀 GENERATING FINAL 4000-TOKEN STYLE-PRESERVING PROMPT")
    print("=" * 70)
    print("Processing ALL available data sources...")

    # Initialize system
    system = FinalStylePreservationSystem()

    # Process known data sources
    print("\n📊 PROCESSING KNOWN DATA SOURCES:")
    system.process_email_database(limit=None)  # Process ALL emails
    system.process_additional_files()

    # Process unknown/additional data sources with intelligent processor
    print("\n🤖 PROCESSING UNKNOWN DATA SOURCES:")
    unknown_sources = [
        "/Users/khamel83/Library/CloudStorage/GoogleDrive-zoheri@gmail.com/My Drive/Dev/Atlas/processed/emails",
        "/Users/khamel83/Library/CloudStorage/GoogleDrive-zoheri@gmail.com/My Drive/text/chats_extract",
    ]

    system.process_unknown_data_sources(unknown_sources)

    # Generate comprehensive analysis
    print("\n📈 GENERATING COMPREHENSIVE ANALYSIS...")
    analysis = system.generate_analysis_report()

    # Create the final 4000-token prompt
    print("\n✍️ CREATING FINAL 4000-TOKEN PROMPT...")
    prompt = system.create_style_prompt(analysis, target_length=4000)

    # Save results
    final_prompt_path = "/Users/khamel83/dev/atlas-voice/FINAL_4000_TOKEN_PROMPT.txt"
    final_analysis_path = "/Users/khamel83/dev/atlas-voice/FINAL_COMPLETE_ANALYSIS.json"

    with open(final_prompt_path, 'w') as f:
        f.write(prompt)

    with open(final_analysis_path, 'w') as f:
        import json
        json.dump(analysis, f, indent=2)

    # Print results
    print("\n🎉 FINAL PROMPT GENERATION COMPLETE!")
    print("=" * 70)
    print(f"📊 **MASSIVE SCALE ACHIEVED**:")
    print(f"   • Total words processed: {analysis['metadata']['total_words']:,}")
    print(f"   • Vocabulary size: {analysis['metadata']['vocabulary_size']:,}")
    print(f"   • Prompt length: {len(prompt)} characters")
    print(f"   • Word count: {len(prompt.split())} words")
    print(f"\n📄 **FILES GENERATED**:")
    print(f"   • Final Prompt: {final_prompt_path}")
    print(f"   • Complete Analysis: {final_analysis_path}")

    # Show prompt preview
    print(f"\n📝 **FINAL PROMPT PREVIEW:**")
    print("=" * 50)
    print(prompt[:500] + "...")
    print("=" * 50)

    return prompt, analysis

if __name__ == "__main__":
    generate_ultimate_prompt()
