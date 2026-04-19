#!/usr/bin/env python3
"""
Speech Analyzer - Make AI Sound Like You

The goal: AI should speak/sound like you when it communicates.
This analyzes your writing patterns to create system prompts that make
Claude, ChatGPT, and other AI services communicate in your authentic voice.

Hybrid Architecture:
- Local preprocessing for speed/privacy
- AI-enhanced analysis for quality
- Context-aware pattern extraction
- Optimized for AI speech/communication
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import hashlib

# Optional imports for enhanced analysis
try:
    import tiktoken
except ImportError:
    tiktoken = None

try:
    import spacy
    from textstat import flesch_reading_ease, flesch_kincaid_grade, coleman_liau_index
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None
    flesch_reading_ease = None
    flesch_kincaid_grade = None
    coleman_liau_index = None

try:
    import openai
except ImportError:
    openai = None

@dataclass
class TextMetadata:
    """Rich metadata for text context"""
    source_type: str  # email, chat, document, code, social_media, etc.
    platform: str     # gmail, slack, github, twitter, etc.
    audience: str     # professional, casual, technical, general
    purpose: str      # informative, persuasive, creative, instructional
    timestamp: Optional[datetime] = None
    author: Optional[str] = None
    word_count: int = 0
    file_path: Optional[str] = None

@dataclass
class StyleProfile:
    """Comprehensive writing style profile"""
    core_patterns: Dict = field(default_factory=dict)
    vocabulary_signature: List[str] = field(default_factory=list)
    phrase_patterns: List[str] = field(default_factory=list)
    sentence_structure: Dict = field(default_factory=dict)
    communication_style: Dict = field(default_factory=dict)
    context_adaptations: Dict = field(default_factory=dict)  # How style changes by context
    usage_recommendations: List[str] = field(default_factory=list)

@dataclass
class AnalysisConfig:
    """Configuration for style analysis"""
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    model: str = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-flash-lite')
    max_output_tokens: int = int(os.getenv('SPEECH_ANALYZER_MAX_TOKENS', '4000'))
    chunk_size: int = int(os.getenv('SPEECH_ANALYZER_CHUNK_SIZE', '50000'))
    enable_ai_analysis: bool = True
    enable_context_analysis: bool = True  # NEW: metadata-aware analysis

    @classmethod
    def from_env(cls):
        return cls(
            openrouter_api_key=os.getenv('OPENROUTER_API_KEY'),
            enable_ai_analysis=bool(os.getenv('OPENROUTER_API_KEY'))
        )

class SpeechAnalyzer:
    """
    Speech Pattern Analyzer - Make AI Sound Like You

    The key insight: Your writing patterns reveal how you "speak" and communicate.
    This tool captures your authentic communication style and creates
    optimized prompts so AI can communicate like you would.
    """

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.encoding = None

        if tiktoken:
            try:
                self.encoding = tiktoken.encoding_for_model("gpt-4")
            except:
                self.encoding = tiktoken.get_encoding("cl100k_base")

        self.ai_client = None
        if config.enable_ai_analysis and openai and config.openrouter_api_key:
            self.ai_client = openai.OpenAI(
                api_key=config.openrouter_api_key,
                base_url=config.openrouter_base_url
            )

    def extract_metadata(self, file_path: str, content: str) -> TextMetadata:
        """Extract rich metadata from file and content"""

        # Determine source type from file path and content
        source_type = self._detect_source_type(file_path, content)
        platform = self._detect_platform(file_path)

        # Analyze content for audience and purpose
        audience, purpose = self._analyze_content_intent(content)

        return TextMetadata(
            source_type=source_type,
            platform=platform,
            audience=audience,
            purpose=purpose,
            timestamp=datetime.fromtimestamp(os.path.getmtime(file_path)),
            word_count=len(content.split()),
            file_path=file_path
        )

    def _detect_source_type(self, file_path: str, content: str) -> str:
        """Detect what type of text this is"""
        path_lower = file_path.lower()

        # Email patterns
        if any(marker in path_lower for marker in ['email', 'mail', '.eml']):
            return 'email'

        # Chat/messaging patterns
        if any(marker in path_lower for marker in ['chat', 'slack', 'discord', 'message']):
            return 'chat'

        # Code patterns
        if any(marker in path_lower for marker in ['code', 'src', '.py', '.js', '.java']):
            return 'code'

        # Documentation patterns
        if any(marker in path_lower for marker in ['doc', 'readme', 'guide', 'manual']):
            return 'documentation'

        # Social media patterns
        if any(marker in path_lower for marker in ['twitter', 'reddit', 'social']):
            return 'social_media'

        # Content analysis fallback
        if self._looks_like_email(content):
            return 'email'
        elif self._looks_like_chat(content):
            return 'chat'
        elif self._looks_like_code(content):
            return 'code'
        else:
            return 'document'

    def _detect_platform(self, file_path: str) -> str:
        """Detect the platform where this was written"""
        path_lower = file_path.lower()

        platform_markers = {
            'gmail': ['gmail', 'google_mail'],
            'slack': ['slack', 'slack_export'],
            'discord': ['discord'],
            'github': ['github', 'git'],
            'twitter': ['twitter', 'x'],
            'reddit': ['reddit'],
            'notion': ['notion'],
            'docs': ['google_doc', 'document']
        }

        for platform, markers in platform_markers.items():
            if any(marker in path_lower for marker in markers):
                return platform

        return 'unknown'

    def _analyze_content_intent(self, content: str) -> Tuple[str, str]:
        """Analyze content to determine audience and purpose"""
        content_lower = content.lower()

        # Audience detection
        professional_indicators = ['dear', 'regarding', 'sincerely', 'best regards', 'thank you for']
        casual_indicators = ['hey', 'yo', 'sup', 'lol', 'btw', 'omg']
        technical_indicators = ['api', 'function', 'code', 'implement', 'debug', 'algorithm']

        if any(indicator in content_lower for indicator in technical_indicators):
            audience = 'technical'
        elif any(indicator in content_lower for indicator in professional_indicators):
            audience = 'professional'
        elif any(indicator in content_lower for indicator in casual_indicators):
            audience = 'casual'
        else:
            audience = 'general'

        # Purpose detection
        informative_indicators = ['here is', 'this shows', 'the data indicates', 'information about']
        persuasive_indicators = ['should', 'recommend', 'suggest', 'consider', 'we need to']
        creative_indicators = ['imagine', 'what if', 'story', 'narrative', 'character']
        instructional_indicators = ['how to', 'steps', 'first', 'then', 'finally', 'tutorial']

        if any(indicator in content_lower for indicator in instructional_indicators):
            purpose = 'instructional'
        elif any(indicator in content_lower for indicator in persuasive_indicators):
            purpose = 'persuasive'
        elif any(indicator in content_lower for indicator in creative_indicators):
            purpose = 'creative'
        elif any(indicator in content_lower for indicator in informative_indicators):
            purpose = 'informative'
        else:
            purpose = 'general'

        return audience, purpose

    def _looks_like_email(self, content: str) -> bool:
        """Check if content looks like email"""
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b(dear|hi|hello|regarding|subject|)\b',
            r'\b(best regards|sincerely|thank you|)\b'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in email_patterns)

    def _looks_like_chat(self, content: str) -> bool:
        """Check if content looks like chat"""
        chat_patterns = [
            r'\b\d{1,2}:\d{2}\s*(AM|PM|am|pm)?\b',  # Timestamps
            r'\b(hey|hi|yo|sup|lol|btw|omg)\b',  # Casual markers
            r'<[^>]+>.*:</[^>]+>',  # XML-style chat
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in chat_patterns)

    def _looks_like_code(self, content: str) -> bool:
        """Check if content looks like code"""
        code_patterns = [
            r'\b(function|def|class|var|let|const)\b',
            r'\b(if|else|for|while|switch)\b',
            r'\b(import|from|require)\b',
            r'[{}();\[\]]'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in code_patterns)

    def analyze_with_context(self, text: str, metadata: TextMetadata) -> Dict:
        """AI-enhanced analysis with metadata context"""
        if not self.ai_client:
            return self._fallback_analysis(text, metadata)

        try:
            context_prompt = f"""
            Analyze this writing sample with full context awareness.

            CONTEXT METADATA:
            - Source Type: {metadata.source_type}
            - Platform: {metadata.platform}
            - Intended Audience: {metadata.audience}
            - Purpose: {metadata.purpose}
            - Word Count: {metadata.word_count}

            WRITING SAMPLE:
            {text[:6000]}

            Extract comprehensive writing style patterns and return JSON:
            {{
                "core_patterns": {{
                    "signature_vocabulary": ["word1", "word2", ...],
                    "distinctive_phrases": ["phrase1", "phrase2", ...],
                    "sentence_flow": "rhythmic|structured|varied|repetitive",
                    "complexity_level": "simple|moderate|complex"
                }},
                "contextual_adaptations": {{
                    "professional_adjustments": ["adjustment1", "adjustment2", ...],
                    "casual_elements": ["element1", "element2", ...],
                    "technical_specialization": ["specialty1", "specialty2", ...]
                }},
                "communication_strategy": {{
                    "primary_approach": "direct|indirect|collaborative|authoritative",
                    "engagement_style": "questioning|declarative|conversational|formal",
                    "persuasion_techniques": ["technique1", "technique2", ...]
                }},
                "usage_optimization": {{
                    "best_for_{{metadata.platform}}": "recommendation",
                    "audience_alignment": "alignment_score",
                    "purpose_effectiveness": "effectiveness_score"
                }}
            }}

            Focus on what makes this writing distinctive and effective for its context.
            """

            response = self.ai_client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": context_prompt}],
                temperature=0.1,
                max_tokens=1200
            )

            result_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_analysis(text, metadata)

        except Exception as e:
            print(f"⚠ Context analysis failed, using fallback: {e}")
            return self._fallback_analysis(text, metadata)

    def _extract_stylometric_features(self, text: str) -> Dict:
        """Extract comprehensive stylometric features using industry standards"""
        features = {}

        # Basic text stats
        sentences = re.split(r'[.!?]+', text)
        words = text.lower().split()
        clean_words = [re.sub(r'[^\w\s]', '', w) for w in words if len(w) > 2]

        features['total_words'] = len(words)
        features['total_sentences'] = len([s for s in sentences if s.strip()])
        features['avg_sentence_length'] = len(words) / max(len(sentences), 1)
        features['vocabulary_richness'] = len(set(clean_words)) / max(len(clean_words), 1)

        # Enhanced features with SpaCy/TextStat if available
        if SPACY_AVAILABLE and spacy:
            try:
                doc = spacy.load('en_core_web_sm')(text[:50000])  # Limit for performance

                # Syntactic features
                features['avg_words_per_sentence'] = sum(len(sent) for sent in doc.sents) / len(list(doc.sents))
                features['punctuation_ratio'] = sum(1 for token in doc if token.is_punct) / len(doc)
                features['function_word_ratio'] = sum(1 for token in doc if token.is_stop) / len(doc)

                # Part-of-speech patterns
                pos_counts = {}
                for token in doc:
                    pos = token.pos_
                    pos_counts[pos] = pos_counts.get(pos, 0) + 1
                features['pos_distribution'] = pos_counts

            except Exception as e:
                print(f"⚠ SpaCy analysis failed: {e}")

        # TextStat features if available
        if SPACY_AVAILABLE and flesch_reading_ease:
            try:
                features['readability_ease'] = flesch_reading_ease(text)
                features['grade_level'] = flesch_kincaid_grade(text)
                features['coleman_liau'] = coleman_liau_index(text)
            except Exception as e:
                print(f"⚠ TextStat analysis failed: {e}")

        # Content type detection
        features['content_type'] = self._detect_content_type(text)

        # Style markers
        features['formality_markers'] = self._extract_formality_markers(text)
        features['casual_markers'] = self._extract_casual_markers(text)

        return features

    def _detect_content_type(self, text: str) -> str:
        """Detect if content is email, chat, speech, or documentation"""
        email_indicators = ['@', 'subject:', 'dear', 'regards', 'sincerely', 'best regards']
        chat_indicators = ['lol', 'btw', 'imo', 'brb', 'afk', ':)', ':(', '<3']
        speech_indicators = ['um', 'uh', 'like', 'you know', 'i mean', 'sort of']

        text_lower = text.lower()

        email_score = sum(1 for indicator in email_indicators if indicator in text_lower)
        chat_score = sum(1 for indicator in chat_indicators if indicator in text_lower)
        speech_score = sum(1 for indicator in speech_indicators if indicator in text_lower)

        if email_score > 2:
            return 'email'
        elif chat_score > 2:
            return 'chat'
        elif speech_score > 3:
            return 'speech'
        else:
            return 'documentation'

    def _extract_formality_markers(self, text: str) -> List[str]:
        """Extract formal language markers"""
        formal_words = ['therefore', 'however', 'furthermore', 'consequently', 'utilize', 'assist', 'request']
        text_lower = text.lower()
        return [word for word in formal_words if word in text_lower]

    def _extract_casual_markers(self, text: str) -> List[str]:
        """Extract casual language markers"""
        casual_words = ['gonna', 'wanna', 'kinda', 'sorta', 'yeah', 'okay', 'cool']
        text_lower = text.lower()
        return [word for word in casual_words if word in text_lower]

    def _fallback_analysis(self, text: str, metadata: TextMetadata) -> Dict:
        """Enhanced analysis with stylometric features"""
        # Get enhanced stylometric features
        stylometric_features = self._extract_stylometric_features(text)

        # Basic word frequency analysis
        words = text.lower().split()
        word_freq = {}

        for word in words:
            word_clean = re.sub(r'[^\w\s]', '', word)
            if len(word_clean) > 2:
                word_freq[word_clean] = word_freq.get(word_clean, 0) + 1

        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]

        # Enhanced analysis with stylometric features
        result = {
            "core_patterns": {
                "signature_vocabulary": [word for word, count in common_words[:8]],
                "distinctive_phrases": [],
                "sentence_flow": "varied" if stylometric_features.get('avg_sentence_length', 0) > 15 else "direct",
                "complexity_level": "complex" if stylometric_features.get('vocabulary_richness', 0) > 0.7 else "moderate"
            },
            "contextual_adaptations": {
                "professional_adjustments": stylometric_features.get('formality_markers', []),
                "casual_elements": stylometric_features.get('casual_markers', []),
                "technical_specialization": []
            },
            "communication_strategy": {
                "primary_approach": "direct" if stylometric_features.get('content_type') == 'documentation' else "collaborative",
                "engagement_style": "declarative",
                "persuasion_techniques": []
            },
            "usage_optimization": {
                f"best_for_{metadata.platform}": f"optimized for {metadata.source_type}",
                "audience_alignment": "medium",
                "purpose_effectiveness": "medium"
            },
            "stylometric_features": stylometric_features  # Include full feature set
        }

        return result

    def create_speech_prompt(self, profile_data: List[Dict], all_metadata: List[TextMetadata]) -> str:
        """Generate optimized system prompt for authentic AI speech"""

        # Aggregate patterns across all contexts
        all_vocab = set()
        all_phrases = set()
        context_styles = {}

        for i, data in enumerate(profile_data):
            metadata = all_metadata[i]
            context_key = f"{metadata.source_type}_{metadata.audience}"

            all_vocab.update(data.get("core_patterns", {}).get("signature_vocabulary", []))
            all_phrases.update(data.get("core_patterns", {}).get("distinctive_phrases", []))

            if context_key not in context_styles:
                context_styles[context_key] = []
            context_styles[context_key].append(data)

        # Build context-aware prompt
        prompt_sections = [
            "# CONTEXT-AWARE WRITING STYLE SYSTEM PROMPT",
            "",
            "## WRITING STYLE PROFILE",
            f"- Total sources analyzed: {len(all_metadata)}",
            f"- Context variety: {len(set(m.source_type for m in all_metadata))} source types",
            f"- Vocabulary richness: {len(all_vocab)} unique markers",
            "",
            "## CORE WRITING SIGNATURE",
        ]

        # Add vocabulary and phrases
        if all_vocab:
            prompt_sections.append(f"### Signature Vocabulary (use naturally): {', '.join(list(all_vocab)[:20])}")
        if all_phrases:
            prompt_sections.append("### Distinctive Phrases:")
            for i, phrase in enumerate(list(all_phrases)[:10], 1):
                prompt_sections.append(f"{i}. {phrase}")

        prompt_sections.append("")

        # Add context-specific adaptations
        prompt_sections.append("## CONTEXT ADAPTATIONS")
        for context, styles in context_styles.items():
            if styles:
                source_type, audience = context.split('_', 1)
                prompt_sections.append(f"### {source_type.title()} for {audience} audience:")

                # Aggregate common patterns for this context
                approaches = [s["communication_strategy"]["primary_approach"] for s in styles]
                most_common = max(set(approaches), key=approaches.count)
                prompt_sections.append(f"- Primary approach: {most_common}")

                # Add any contextual adaptations
                adaptations = []
                for style in styles:
                    adaptations.extend(style.get("contextual_adaptations", {}).get("professional_adjustments", []))
                    adaptations.extend(style.get("contextual_adaptations", {}).get("casual_elements", []))

                if adaptations:
                    unique_adaptations = list(set(adaptations))[:3]
                    prompt_sections.append(f"- Key adaptations: {', '.join(unique_adaptations)}")

        prompt_sections.append("")

        # Add usage requirements
        prompt_sections.extend([
            "## USAGE REQUIREMENTS",
            "1. Adapt writing style to match the context and audience",
            "2. Use signature vocabulary and phrases naturally within context",
            "3. Maintain consistent communication approach across topics",
            "4. Adjust formality level based on platform and purpose",
            "5. Be authentic to the analyzed writing patterns",
            "6. Think through problems step by step when analyzing",
            "7. Prioritize clear, effective communication",
            "8. Maintain style consistency across all responses",
            "",
            "## TECHNICAL NOTES",
            f"- Based on analysis of {sum(m.word_count for m in all_metadata):,} words",
            f"- Generated using context-aware hybrid intelligence",
            f"- Optimized for multi-platform communication",
            f"- Adapts to audience and purpose automatically",
            "",
            "## CRITICAL REQUIREMENT",
            "Maintain authentic writing style patterns while adapting to context. Do not revert to generic AI communication style."
        ])

        return '\n'.join(prompt_sections)

    def analyze_speech_patterns(self, input_paths: List[str]) -> Dict:
        """Main analysis function with metadata awareness"""
        print("🔍 Starting speech pattern analysis...")
        print("=" * 70)

        all_text_chunks = []
        all_metadata = []
        total_words = 0

        # Process files with metadata extraction
        for path in input_paths:
            if os.path.isfile(path):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if content.strip():
                            metadata = self.extract_metadata(path, content)
                            all_text_chunks.append(content)
                            all_metadata.append(metadata)
                            total_words += metadata.word_count

                            print(f"✓ {metadata.source_type.title()} ({metadata.audience}, {metadata.purpose}): {os.path.basename(path)}")
                except Exception as e:
                    print(f"⚠ Error reading {path}: {e}")

            elif os.path.isdir(path):
                print(f"📂 Scanning directory: {os.path.basename(path)}")
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.txt', '.md', '.csv', '.json')):
                            try:
                                file_path = os.path.join(root, file)
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if content.strip():
                                        metadata = self.extract_metadata(file_path, content)
                                        all_text_chunks.append(content)
                                        all_metadata.append(metadata)
                                        total_words += metadata.word_count
                            except Exception as e:
                                print(f"⚠ Error reading {file}: {e}")

        if not all_text_chunks:
            raise ValueError("No text content found in provided files")

        print(f"\n📊 Analysis Context:")
        print(f"   Total files: {len(all_metadata)}")
        print(f"   Total words: {total_words:,}")
        print(f"   Source types: {', '.join(set(m.source_type for m in all_metadata))}")
        print(f"   Platforms: {', '.join(set(m.platform for m in all_metadata if m.platform != 'unknown'))}")

        # Analyze each chunk with its metadata
        analysis_results = []
        estimated_cost = 0

        for i, (text, metadata) in enumerate(zip(all_text_chunks, all_metadata)):
            print(f"🧠 Analyzing {metadata.source_type} sample {i+1}/{len(all_text_chunks)}...")

            if self.config.enable_ai_analysis and self.ai_client:
                result = self.analyze_with_context(text, metadata)
                # Rough cost estimate
                estimated_cost += (len(text) // 4 * 2 / 1_000_000) * 0.075
            else:
                result = self._fallback_analysis(text, metadata)

            analysis_results.append(result)

        # Generate speech prompt
        print("🎯 Generating speech pattern system prompt...")
        final_prompt = self.create_speech_prompt(analysis_results, all_metadata)

        # Display results
        actual_tokens = len(self.encoding.encode(final_prompt)) if self.encoding else len(final_prompt) // 4
        print(f"✅ Analysis complete:")
        print(f"   Final prompt: {actual_tokens} tokens")
        print(f"   Estimated cost: ${estimated_cost:.4f}")

        return {
            "prompt": final_prompt,
            "metadata_summary": {
                "total_files": len(all_metadata),
                "total_words": total_words,
                "source_types": list(set(m.source_type for m in all_metadata)),
                "platforms": list(set(m.platform for m in all_metadata if m.platform != 'unknown')),
                "audiences": list(set(m.audience for m in all_metadata)),
                "purposes": list(set(m.purpose for m in all_metadata))
            },
            "analysis_results": analysis_results,
            "token_count": actual_tokens,
            "cost": estimated_cost
        }

def main():
    parser = argparse.ArgumentParser(description='Speech Analyzer - Make AI Sound Like You')
    parser.add_argument('inputs', nargs='+', help='Text files or directories to analyze')
    parser.add_argument('--output', '-o', default='speech_prompt.txt', help='Output file')
    parser.add_argument('--no-ai', action='store_true', help='Disable AI analysis (local only)')
    parser.add_argument('--model', default='openai/gpt-3.5-turbo', help='Model for AI analysis')
    parser.add_argument('--style-type', choices=['email', 'chat', 'speech', 'documentation', 'auto'],
                       default='auto', help='Target style type (auto-detect if not specified)')

    args = parser.parse_args()

    config = AnalysisConfig.from_env()
    if args.no_ai:
        config.enable_ai_analysis = False
    config.model = args.model

    analyzer = SpeechAnalyzer(config)

    try:
        result = analyzer.analyze_speech_patterns(args.inputs)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result['prompt'])

        print(f"\n✅ Speech pattern prompt saved to: {args.output}")
        print(f"🎯 AI WILL NOW SPEAK LIKE YOU")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
