#!/usr/bin/env python3
"""
Intelligent Data Processor
Uses LLM calls to automatically handle unknown data formats
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import openai
import tempfile
import shutil

class IntelligentDataProcessor:
    """Automatically processes unknown data formats using LLM assistance"""

    def __init__(self):
        # Known processors for common formats
        self.known_processors = {
            '.txt': self.process_text_file,
            '.md': self.process_text_file,
            '.csv': self.process_csv_file,
            '.json': self.process_json_file,
        }

        # Unknown format cache to avoid repeated LLM calls
        self.format_cache = {}

        # OpenRouter client
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

    def analyze_unknown_format(self, file_path: str, sample_content: str) -> Dict:
        """Use LLM to analyze unknown file format and generate processing code"""

        file_ext = Path(file_path).suffix.lower()

        # Check cache first
        if file_ext in self.format_cache:
            print(f"  📋 Using cached processor for {file_ext} files")
            return self.format_cache[file_ext]

        print(f"  🤖 Analyzing unknown format: {file_ext}")
        print(f"  🔍 Asking LLM how to process this data...")

        analysis_prompt = f"""
You are a data processing expert. I have a file with extension '{file_ext}' and need to extract text content for writing style analysis.

Here's a sample of the file content:
```
{sample_content[:2000]}...
```

Please analyze this format and provide:

1. **Format Identification**: What type of file is this?
2. **Processing Strategy**: How should I extract text content?
3. **Python Code**: Write a Python function to extract text content.

Requirements:
- Function should be named `process_{file_ext.replace('.', '')}_file`
- Take file_path as parameter
- Return list of text strings (content to analyze)
- Handle errors gracefully
- Extract only human-readable text content
- Skip metadata, headers, technical data

Return your response as JSON:
{{
    "format_type": "description of format",
    "strategy": "brief processing strategy",
    "python_code": "complete Python function code",
    "imports_needed": ["list", "of", "imports"],
    "confidence": 0.95
}}

Be practical and focus on text extraction for writing analysis.
"""

        try:
            response = self.client.chat.completions.create(
                model="google/gemini-2.5-flash-lite",
                messages=[
                    {"role": "system", "content": "You are a data processing expert who writes clean, working Python code for text extraction."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent code
            )

            response_text = response.choices[0].message.content.strip()

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())

                # Cache the result
                self.format_cache[file_ext] = analysis

                print(f"  ✅ LLM identified format: {analysis.get('format_type', 'Unknown')}")
                print(f"  📝 Strategy: {analysis.get('strategy', 'Default processing')}")

                return analysis
            else:
                print(f"  ❌ Failed to parse LLM response")
                return None

        except Exception as e:
            print(f"  ❌ LLM analysis failed: {e}")
            return None

    def create_dynamic_processor(self, analysis: Dict) -> callable:
        """Create a dynamic processor function from LLM-generated code"""

        try:
            # Get the generated code
            python_code = analysis.get('python_code', '')
            imports_needed = analysis.get('imports_needed', [])

            # Create a safe execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                'os': os,
                'json': json,
                're': re,
                'Path': Path,
            }

            # Add required imports
            for import_name in imports_needed:
                try:
                    if '.' in import_name:
                        module_name, attr_name = import_name.rsplit('.', 1)
                        module = __import__(module_name, fromlist=[attr_name])
                        exec_globals[attr_name] = getattr(module, attr_name)
                    else:
                        exec_globals[import_name] = __import__(import_name)
                except ImportError:
                    print(f"  ⚠️ Could not import {import_name}")

            # Execute the generated code
            exec(python_code, exec_globals)

            # Find the processor function
            for name, obj in exec_globals.items():
                if callable(obj) and name.startswith('process_') and name.endswith('_file'):
                    print(f"  ✅ Created dynamic processor: {name}")
                    return obj

            print(f"  ❌ No processor function found in generated code")
            return None

        except Exception as e:
            print(f"  ❌ Failed to create dynamic processor: {e}")
            return None

    def process_text_file(self, file_path: str) -> List[str]:
        """Process standard text files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                return [content] if content else []
        except Exception as e:
            print(f"  ❌ Error processing text file: {e}")
            return []

    def process_csv_file(self, file_path: str) -> List[str]:
        """Process CSV files"""
        try:
            import csv
            import sys

            # Handle large CSV files
            maxInt = sys.maxsize
            while True:
                try:
                    csv.field_size_limit(maxInt)
                    break
                except OverflowError:
                    maxInt = int(maxInt/10)

            texts = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Extract text from likely content columns
                    for col_name in ['content', 'body', 'text', 'message', 'email_content', 'description']:
                        if col_name in row and row[col_name]:
                            text = str(row[col_name]).strip()
                            if len(text) > 20:  # Meaningful content only
                                texts.append(text)
                            break

                    # Limit processing for performance
                    if len(texts) > 1000:
                        break

            return texts

        except Exception as e:
            print(f"  ❌ Error processing CSV file: {e}")
            return []

    def process_json_file(self, file_path: str) -> List[str]:
        """Process JSON files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            texts = []

            def extract_text_from_json(obj, depth=0):
                if depth > 5:  # Prevent infinite recursion
                    return

                if isinstance(obj, str) and len(obj.strip()) > 20:
                    texts.append(obj.strip())
                elif isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.lower() in ['content', 'text', 'message', 'body', 'description']:
                            extract_text_from_json(value, depth + 1)
                elif isinstance(obj, list):
                    for item in obj[:100]:  # Limit list processing
                        extract_text_from_json(item, depth + 1)

            extract_text_from_json(data)
            return texts

        except Exception as e:
            print(f"  ❌ Error processing JSON file: {e}")
            return []

    def get_file_sample(self, file_path: str, max_bytes: int = 5000) -> str:
        """Get a sample of file content for analysis"""
        try:
            # Try reading as text first
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_bytes)
        except:
            try:
                # Try reading as binary and converting
                with open(file_path, 'rb') as f:
                    content = f.read(max_bytes)
                    return content.decode('utf-8', errors='ignore')
            except:
                return "Binary file - content not readable as text"

    def process_file(self, file_path: str) -> List[str]:
        """Main entry point - process any file intelligently"""

        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()

        print(f"📄 Processing: {file_path.name}")

        # Check if we have a known processor
        if file_ext in self.known_processors:
            print(f"  ✅ Using known processor for {file_ext}")
            return self.known_processors[file_ext](str(file_path))

        # Unknown format - use LLM to figure it out
        print(f"  ❓ Unknown format: {file_ext}")

        # Get file sample
        sample_content = self.get_file_sample(str(file_path))

        if not sample_content.strip():
            print(f"  ❌ File appears to be empty or binary")
            return []

        # Analyze format with LLM
        analysis = self.analyze_unknown_format(str(file_path), sample_content)

        if not analysis:
            print(f"  ❌ Could not analyze format, skipping file")
            return []

        # Create dynamic processor
        processor = self.create_dynamic_processor(analysis)

        if not processor:
            print(f"  ❌ Could not create processor, falling back to text extraction")
            return [sample_content]

        # Use the dynamic processor
        try:
            result = processor(str(file_path))
            print(f"  ✅ Processed {len(result)} text segments")
            return result
        except Exception as e:
            print(f"  ❌ Dynamic processor failed: {e}")
            print(f"  📝 Falling back to sample content")
            return [sample_content]

    def process_directory(self, directory_path: str, max_files: int = 100) -> Dict[str, List[str]]:
        """Process all files in a directory intelligently"""

        directory_path = Path(directory_path)
        results = {}
        processed_count = 0

        print(f"📁 Processing directory: {directory_path}")

        # Get all files
        all_files = []
        for file_path in directory_path.rglob('*'):
            if file_path.is_file():
                all_files.append(file_path)

        print(f"  📊 Found {len(all_files)} files")

        # Process files up to limit
        for file_path in all_files[:max_files]:
            try:
                texts = self.process_file(str(file_path))
                if texts:
                    results[str(file_path)] = texts
                    processed_count += 1

            except Exception as e:
                print(f"  ❌ Failed to process {file_path.name}: {e}")

        print(f"  ✅ Successfully processed {processed_count} files")
        return results

    def save_cache(self, cache_file: str = "data/format_cache.json"):
        """Save format cache for reuse"""
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.format_cache, f, indent=2)
            print(f"💾 Saved format cache to {cache_file}")
        except Exception as e:
            print(f"❌ Failed to save cache: {e}")

    def load_cache(self, cache_file: str = "data/format_cache.json"):
        """Load format cache from previous runs"""
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    self.format_cache = json.load(f)
                print(f"📋 Loaded format cache with {len(self.format_cache)} formats")
        except Exception as e:
            print(f"⚠️ Could not load cache: {e}")

def main():
    """Demo of intelligent data processor"""
    processor = IntelligentDataProcessor()
    processor.load_cache()

    # Test with a directory
    test_dir = "data"
    results = processor.process_directory(test_dir, max_files=5)

    print(f"\n📊 PROCESSING RESULTS:")
    for file_path, texts in results.items():
        print(f"  {Path(file_path).name}: {len(texts)} text segments")

    processor.save_cache()

if __name__ == "__main__":
    main()
