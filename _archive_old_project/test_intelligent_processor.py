#!/usr/bin/env python3
"""
Test the intelligent data processor with unknown formats
"""

import sys
import os
from pathlib import Path

# Add the core directory to path
sys.path.append(str(Path(__file__).parent / "core"))

from intelligent_data_processor import IntelligentDataProcessor

def test_unknown_format_processing():
    """Test processing unknown formats"""

    processor = IntelligentDataProcessor()
    processor.load_cache()

    print("🧪 TESTING INTELLIGENT DATA PROCESSOR")
    print("=" * 50)

    # Test with EML files from your system
    test_paths = [
        "/Users/khamel83/Library/CloudStorage/GoogleDrive-zoheri@gmail.com/My Drive/Dev/Atlas/processed/emails",
        # Add any other unknown format directories you want to test
    ]

    for test_path in test_paths:
        if os.path.exists(test_path):
            print(f"\n📁 Testing directory: {test_path}")

            # Get a sample file to test individual processing
            sample_files = list(Path(test_path).glob("*.eml"))[:3]

            for sample_file in sample_files:
                print(f"\n📄 Testing individual file: {sample_file.name}")
                texts = processor.process_file(str(sample_file))

                if texts:
                    print(f"  ✅ Extracted {len(texts)} text segments")
                    print(f"  📊 Total words: {sum(len(text.split()) for text in texts)}")

                    # Show sample of extracted text
                    if texts and len(texts[0]) > 100:
                        print(f"  📝 Sample: {texts[0][:200]}...")
                else:
                    print(f"  ❌ No text extracted")

                # Break after first successful test
                if texts:
                    break

            # Test directory processing
            print(f"\n📁 Testing directory processing (max 5 files)...")
            results = processor.process_directory(test_path, max_files=5)

            total_files = len(results)
            total_segments = sum(len(segments) for segments in results.values())
            total_words = sum(sum(len(text.split()) for text in segments) for segments in results.values())

            print(f"  📊 DIRECTORY RESULTS:")
            print(f"     Files processed: {total_files}")
            print(f"     Text segments: {total_segments}")
            print(f"     Total words: {total_words:,}")

        else:
            print(f"⚠️  Test path not found: {test_path}")

    # Save cache
    processor.save_cache()
    print(f"\n💾 Format cache saved with {len(processor.format_cache)} learned formats")

    # Show what formats were learned
    if processor.format_cache:
        print(f"\n📋 LEARNED FORMATS:")
        for ext, analysis in processor.format_cache.items():
            print(f"  {ext}: {analysis.get('format_type', 'Unknown')}")

if __name__ == "__main__":
    test_unknown_format_processing()
