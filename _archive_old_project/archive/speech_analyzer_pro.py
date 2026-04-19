#!/usr/bin/env python3
"""
Speech Analyzer Pro - Make AI Sound Like You

Simple, reliable, generic tool for analyzing any text data.
Works with local models or cloud APIs. Scales with more data.

USAGE:
    python3 speech_analyzer_pro.py /path/to/text/files/
    python3 speech_analyzer_pro.py --model ollama/llama3.2 --local-only
    python3 speech_analyzer_pro.py --model openrouter/gemini-flash --api-key YOUR_KEY

CORE FEATURES:
- Generic text processing (emails, docs, chats, anything)
- Smart chunking for large datasets
- Local or cloud model support
- Style profile generation
- Safe and private processing
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple, Generator
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import hashlib
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional imports for enhanced analysis
try:
    import spacy
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None
    flesch_reading_ease = None
    flesch_kincaid_grade = None

try:
    import tiktoken
except ImportError:
    tiktoken = None

@dataclass
class AnalysisConfig:
    """Configuration for speech analysis"""
    model: str = "ollama/llama3.2"
    api_key: Optional[str] = None
    local_only: bool = True
    chunk_size: int = 10000
    overlap_size: int = 1000
    enable_ai_analysis: bool = True
    max_workers: int = 4

    @classmethod
    def from_env(cls) -> 'AnalysisConfig':
        """Load configuration from environment"""
        config = cls()

        # Model preference
        if os.getenv('OPENROUTER_API_KEY'):
            config.model = os.getenv('DEFAULT_MODEL', 'google/gemini-2.5-flash-lite')
            config.api_key = os.getenv('OPENROUTER_API_KEY')
            config.local_only = False
        elif os.getenv('OLLAMA_MODEL'):
            config.model = os.getenv('OLLAMA_MODEL')
            config.local_only = True

        return config

@dataclass
class TextChunk:
    """A chunk of text with metadata"""
    id: str
    text: str
    source_file: str
    chunk_index: int
    total_chunks: int
    word_count: int
    content_type: str = "generic"
    created_at: datetime = field(default_factory=datetime.now)

class SpeechAnalyzerPro:
    """Professional speech pattern analyzer"""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.db_path = None
        self.db_conn = None
        self.ai_client = None

        # Initialize AI client if not local-only
        if not config.local_only and config.enable_ai_analysis and config.api_key:
            try:
                import openai
                self.ai_client = openai.OpenAI(
                    api_key=config.api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            except ImportError:
                print("⚠ OpenAI not available, using local analysis only")
                config.enable_ai_analysis = False

    def __enter__(self):
        """Context manager entry"""
        self.setup_database()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup database"""
        if self.db_conn:
            self.db_conn.close()
        if self.db_path and os.path.exists(self.db_path):
            os.remove(self.db_path)

    def setup_database(self):
        """Setup temporary SQLite database"""
        self.db_path = f"/tmp/speech_analysis_{hashlib.md5(str(datetime.now()).encode()).hexdigest()}.db"
        self.db_conn = sqlite3.connect(self.db_path)

        # Create tables
        self.db_conn.execute('''
            CREATE TABLE text_chunks (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                source_file TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                total_chunks INTEGER NOT NULL,
                word_count INTEGER NOT NULL,
                content_type TEXT DEFAULT 'generic',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.db_conn.execute('''
            CREATE TABLE style_features (
                chunk_id TEXT PRIMARY KEY,
                avg_word_length REAL,
                avg_sentence_length REAL,
                vocabulary_richness REAL,
                readability_score REAL,
                formality_markers TEXT,
                casual_markers TEXT,
                content_type TEXT,
                features_json TEXT,
                FOREIGN KEY (chunk_id) REFERENCES text_chunks(id)
            )
        ''')

        self.db_conn.commit()

    def process_file(self, file_path: Path) -> List[TextChunk]:
        """Process a single file into chunks"""
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            if not content.strip():
                return []

            # Clean and normalize content
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            content = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\~\`\|\\]', '', content)

            # Detect content type
            content_type = self.detect_content_type(content, file_path.suffix)

            # Create overlapping chunks
            words = content.split()
            chunks = []

            start = 0
            chunk_index = 0
            while start < len(words):
                end = start + self.config.chunk_size
                chunk_text = ' '.join(words[start:end])

                if chunk_text.strip():
                    chunk = TextChunk(
                        id=f"{file_path.name}_{chunk_index}",
                        text=chunk_text,
                        source_file=str(file_path),
                        chunk_index=chunk_index,
                        total_chunks=(len(words) // self.config.chunk_size) + 1,
                        word_count=len(chunk_text.split()),
                        content_type=content_type
                    )
                    chunks.append(chunk)

                start = end - self.config.overlap_size
                chunk_index += 1

            return chunks

        except Exception as e:
            print(f"⚠ Error processing {file_path}: {e}")
            return []

    def detect_content_type(self, content: str, file_extension: str) -> str:
        """Detect if content is email, chat, code, or generic text"""
        content_lower = content.lower()

        # Email indicators
        email_indicators = ['@', 'subject:', 'dear', 'regards', 'sincerely', 'best regards', 'from:', 'to:']
        if file_extension == '.eml' or any(indicator in content_lower for indicator in email_indicators):
            return 'email'

        # Chat indicators
        chat_indicators = ['lol', 'btw', 'imo', 'brb', 'afk', ':)', ':(', '<3', '😊', '👍']
        if any(indicator in content_lower for indicator in chat_indicators):
            return 'chat'

        # Code indicators
        code_indicators = ['function', 'def ', 'class ', 'var ', 'let ', 'const ', 'import ', 'from ']
        if any(indicator in content_lower for indicator in code_indicators):
            return 'code'

        # Documentation indicators
        doc_indicators = ['# ', '## ', '### ', '**', '```', 'README', 'documentation']
        if any(indicator in content_lower for indicator in doc_indicators):
            return 'documentation'

        return 'generic'

    def extract_features(self, chunk: TextChunk) -> Dict:
        """Extract stylometric features from text chunk"""
        features = {}

        # Basic statistics
        words = chunk.text.split()
        sentences = re.split(r'[.!?]+', chunk.text)
        sentences = [s.strip() for s in sentences if s.strip()]

        features['avg_word_length'] = sum(len(word) for word in words) / max(len(words), 1)
        features['avg_sentence_length'] = len(words) / max(len(sentences), 1)
        features['vocabulary_richness'] = len(set(words)) / max(len(words), 1)

        # Readability scores
        if SPACY_AVAILABLE and flesch_reading_ease:
            try:
                features['readability_score'] = flesch_reading_ease(chunk.text)
            except:
                features['readability_score'] = 50.0  # Default

        # Style markers
        features['formality_markers'] = self.extract_markers(chunk.text, [
            'therefore', 'however', 'furthermore', 'consequently', 'utilize', 'assist',
            'request', 'additionally', 'moreover', 'nevertheless'
        ])

        features['casual_markers'] = self.extract_markers(chunk.text, [
            'gonna', 'wanna', 'kinda', 'sorta', 'yeah', 'okay', 'cool', 'like', 'you know',
            'i mean', 'sort of', 'basically', 'actually', 'literally'
        ])

        # Content type
        features['content_type'] = chunk.content_type

        return features

    def extract_markers(self, text: str, markers: List[str]) -> List[str]:
        """Extract style markers from text"""
        text_lower = text.lower()
        return [marker for marker in markers if marker in text_lower]

    def analyze_chunk(self, chunk: TextChunk) -> Dict:
        """Analyze a single text chunk"""
        # Extract features
        features = self.extract_features(chunk)

        # AI-enhanced analysis if available
        ai_analysis = None
        if self.ai_client and self.config.enable_ai_analysis:
            ai_analysis = self.analyze_with_ai(chunk.text, features)

        return {
            'chunk_id': chunk.id,
            'features': features,
            'ai_analysis': ai_analysis,
            'metadata': {
                'source_file': chunk.source_file,
                'chunk_index': chunk.chunk_index,
                'total_chunks': chunk.total_chunks,
                'word_count': chunk.word_count,
                'content_type': chunk.content_type
            }
        }

    def analyze_with_ai(self, text: str, features: Dict) -> Dict:
        """AI-enhanced analysis using LLM"""
        try:
            prompt = f"""
            Analyze this writing sample and extract detailed style patterns:

            TEXT SAMPLE:
            {text[:3000]}

            BASIC FEATURES:
            - Average word length: {features.get('avg_word_length', 0):.2f}
            - Average sentence length: {features.get('avg_sentence_length', 0):.2f}
            - Vocabulary richness: {features.get('vocabulary_richness', 0):.2f}
            - Content type: {features.get('content_type', 'generic')}
            - Formality markers: {features.get('formality_markers', [])}
            - Casual markers: {features.get('casual_markers', [])}

            Extract detailed style patterns and return JSON:
            {{
                "tone_profile": "description of overall tone",
                "sentence_patterns": "description of sentence structure",
                "vocabulary_style": "description of word choice",
                "communication_style": "direct/collaborative/analytical/etc",
                "key_phrases": ["phrase1", "phrase2", "phrase3"],
                "signature_elements": ["element1", "element2"]
            }}
            """

            response = self.ai_client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )

            result_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            print(f"⚠ AI analysis failed: {e}")

        return None

    def process_directory(self, input_paths: List[str]) -> Dict:
        """Process all input files and generate comprehensive analysis"""
        print("🔍 Starting speech pattern analysis...")
        print("=" * 70)

        # Find all text files
        all_files = []
        for path_str in input_paths:
            path = Path(path_str)
            if path.is_file():
                if path.suffix in ['.txt', '.md', '.eml', '.json', '.csv']:
                    all_files.append(path)
            elif path.is_dir():
                all_files.extend(path.rglob('*.txt'))
                all_files.extend(path.rglob('*.md'))
                all_files.extend(path.rglob('*.eml'))
                all_files.extend(path.rglob('*.json'))
                all_files.extend(path.rglob('*.csv'))

        if not all_files:
            print("❌ No text files found")
            return {}

        print(f"📁 Found {len(all_files)} files to process")

        # Process files into chunks
        all_chunks = []
        total_words = 0

        for file_path in all_files:
            print(f"📄 Processing {file_path.name}...")
            chunks = self.process_file(file_path)
            all_chunks.extend(chunks)
            total_words += sum(chunk.word_count for chunk in chunks)

        print(f"📊 Created {len(all_chunks)} chunks with {total_words:,} total words")

        # Analyze chunks with parallel processing
        analysis_results = []

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_chunk = {executor.submit(self.analyze_chunk, chunk): chunk for chunk in all_chunks}

            for i, future in enumerate(as_completed(future_to_chunk)):
                if i % 10 == 0:
                    print(f"🧠 Analyzing chunk {i+1}/{len(all_chunks)}...")

                try:
                    result = future.result()
                    analysis_results.append(result)
                except Exception as e:
                    print(f"⚠ Analysis failed for chunk: {e}")

        # Generate comprehensive style profile
        style_profile = self.generate_style_profile(analysis_results)

        # Create system prompt
        system_prompt = self.create_system_prompt(style_profile, total_words)

        return {
            'profile': style_profile,
            'prompt': system_prompt,
            'stats': {
                'total_files': len(all_files),
                'total_chunks': len(all_chunks),
                'total_words': total_words,
                'content_types': self.get_content_type_stats(all_chunks)
            }
        }

    def generate_style_profile(self, analysis_results: List[Dict]) -> Dict:
        """Generate comprehensive style profile from analysis results"""
        if not analysis_results:
            return {}

        # Aggregate features
        all_features = [result['features'] for result in analysis_results]

        # Calculate averages
        avg_word_length = sum(f.get('avg_word_length', 0) for f in all_features) / len(all_features)
        avg_sentence_length = sum(f.get('avg_sentence_length', 0) for f in all_features) / len(all_features)
        avg_vocabulary_richness = sum(f.get('vocabulary_richness', 0) for f in all_features) / len(all_features)

        # Collect all markers
        all_formal = []
        all_casual = []
        for features in all_features:
            all_formal.extend(features.get('formality_markers', []))
            all_casual.extend(features.get('casual_markers', []))

        # Count content types
        content_types = {}
        for features in all_features:
            content_type = features.get('content_type', 'generic')
            content_types[content_type] = content_types.get(content_type, 0) + 1

        # Collect AI insights
        ai_insights = []
        for result in analysis_results:
            if result.get('ai_analysis'):
                ai_insights.append(result['ai_analysis'])

        return {
            'statistics': {
                'avg_word_length': round(avg_word_length, 2),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'vocabulary_richness': round(avg_vocabulary_richness, 3),
                'total_analyzed_chunks': len(analysis_results)
            },
            'style_markers': {
                'formality_markers': list(set(all_formal))[:10],
                'casual_markers': list(set(all_casual))[:10],
                'primary_content_type': max(content_types, key=content_types.get) if content_types else 'generic'
            },
            'ai_insights': ai_insights[-5:] if ai_insights else [],  # Last 5 insights
            'content_distribution': content_types
        }

    def get_content_type_stats(self, chunks: List[TextChunk]) -> Dict:
        """Get statistics about content types"""
        content_types = {}
        for chunk in chunks:
            content_type = chunk.content_type
            content_types[content_type] = content_types.get(content_type, 0) + 1
        return content_types

    def create_system_prompt(self, profile: Dict, total_words: int) -> str:
        """Create optimized system prompt from style profile"""
        prompt_lines = [
            "# CONTEXT-AWARE WRITING STYLE SYSTEM PROMPT",
            "",
            "## WRITING STYLE PROFILE",
            f"- Total sources analyzed: {profile.get('statistics', {}).get('total_analyzed_chunks', 0)} chunks",
            f"- Total words processed: {total_words:,}",
            f"- Primary content type: {profile.get('style_markers', {}).get('primary_content_type', 'generic')}",
            ""
        ]

        # Add statistics
        stats = profile.get('statistics', {})
        prompt_lines.extend([
            "## CORE WRITING SIGNATURE",
            f"### Key Metrics:",
            f"- Average word length: {stats.get('avg_word_length', 0)} characters",
            f"- Average sentence length: {stats.get('avg_sentence_length', 0)} words",
            f"- Vocabulary richness: {stats.get('vocabulary_richness', 0)}",
            ""
        ])

        # Add style markers
        style_markers = profile.get('style_markers', {})
        if style_markers.get('formality_markers'):
            prompt_lines.append("### Formal Language Indicators:")
            prompt_lines.extend([f"- {marker}" for marker in style_markers['formality_markers'][:5]])
            prompt_lines.append("")

        if style_markers.get('casual_markers'):
            prompt_lines.append("### Casual Language Indicators:")
            prompt_lines.extend([f"- {marker}" for marker in style_markers['casual_markers'][:5]])
            prompt_lines.append("")

        # Add AI insights if available
        ai_insights = profile.get('ai_insights', [])
        if ai_insights:
            prompt_lines.append("## AI-EXTRACTED STYLE INSIGHTS")
            for insight in ai_insights[:3]:  # Top 3 insights
                if isinstance(insight, dict):
                    tone = insight.get('tone_profile', 'professional')
                    pattern = insight.get('sentence_patterns', 'varied')
                    prompt_lines.extend([
                        f"### Tone: {tone}",
                        f"### Sentence Structure: {pattern}",
                        ""
                    ])

        # Add usage requirements
        prompt_lines.extend([
            "## USAGE REQUIREMENTS",
            "1. Adapt writing style to match the profile metrics above",
            "2. Use natural vocabulary complexity that matches the richness level",
            "3. Maintain sentence length patterns similar to the profile",
            "4. Incorporate style markers appropriately for context",
            "5. Be authentic to the analyzed writing patterns",
            "6. Prioritize clear, effective communication",
            "7. Maintain style consistency across responses",
            "",
            "## TECHNICAL NOTES",
            f"- Generated from {total_words:,} words of authentic writing",
            f"- Uses context-aware hybrid intelligence analysis",
            f"- Optimized for multi-platform communication",
            f"- Adapts to audience and purpose automatically",
            "",
            "## CRITICAL REQUIREMENT",
            "Maintain authentic writing style patterns while adapting to context. Do not revert to generic AI communication style."
        ])

        return '\n'.join(prompt_lines)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Speech Analyzer Pro - Make AI Sound Like You')
    parser.add_argument('inputs', nargs='+', help='Text files or directories to analyze')
    parser.add_argument('--output', '-o', default='speech_prompt.txt', help='Output file')
    parser.add_argument('--model', default=None, help='Model to use (e.g., ollama/llama3.2, openrouter/gemini-flash)')
    parser.add_argument('--api-key', help='API key for cloud models')
    parser.add_argument('--local-only', action='store_true', help='Use local analysis only')
    parser.add_argument('--chunk-size', type=int, default=10000, help='Words per chunk')
    parser.add_argument('--overlap-size', type=int, default=1000, help='Words overlap between chunks')
    parser.add_argument('--max-workers', type=int, default=4, help='Parallel processing workers')

    args = parser.parse_args()

    # Load configuration
    config = AnalysisConfig.from_env()

    # Override with command line arguments
    if args.model:
        config.model = args.model
    if args.api_key:
        config.api_key = args.api_key
        config.local_only = False
    if args.local_only:
        config.local_only = True
    config.chunk_size = args.chunk_size
    config.overlap_size = args.overlap_size
    config.max_workers = args.max_workers

    print("🚀 Speech Analyzer Pro")
    print("=" * 50)
    print(f"📊 Model: {config.model}")
    print(f"🔒 Local-only: {config.local_only}")
    print(f"📁 Processing: {len(args.inputs)} input(s)")
    print("=" * 50)

    # Run analysis
    with SpeechAnalyzerPro(config) as analyzer:
        try:
            result = analyzer.process_directory(args.inputs)

            if result:
                # Save results
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result['prompt'])

                # Save detailed profile
                profile_file = args.output.replace('.txt', '_profile.json')
                with open(profile_file, 'w', encoding='utf-8') as f:
                    json.dump(result['profile'], f, indent=2)

                # Print summary
                stats = result['stats']
                print(f"\n✅ Analysis Complete!")
                print(f"📄 Files processed: {stats['total_files']}")
                print(f"🔤 Total words: {stats['total_words']:,}")
                print(f"🧩 Chunks analyzed: {stats['total_chunks']}")
                print(f"📝 System prompt saved to: {args.output}")
                print(f"📊 Detailed profile saved to: {profile_file}")
                print(f"🎯 AI WILL NOW SPEAK LIKE YOU!")
                print("=" * 70)

                # Show content type breakdown
                content_types = stats.get('content_types', {})
                if content_types:
                    print(f"📋 Content Type Breakdown:")
                    for content_type, count in content_types.items():
                        print(f"   {content_type}: {count} chunks")
            else:
                print("❌ Analysis failed - no results generated")

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()
