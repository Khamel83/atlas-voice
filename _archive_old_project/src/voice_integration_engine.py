#!/usr/bin/env python3
"""
Voice Integration Engine
Connects voice pattern extraction with dynamic prompt generation
Creates end-to-end workflow for personalized AI system prompts
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from voice_pattern_extractor import VoicePatternExtractor, VoiceProfile
from dynamic_prompt_generator import DynamicPromptGenerator
from nuclear_safe_room import NuclearSafeRoom

@dataclass
class IntegrationResult:
    """Result of voice integration process"""
    success: bool
    voice_profile: Optional[VoiceProfile] = None
    personalized_prompt: Optional[str] = None
    error_message: Optional[str] = None
    processing_stats: Optional[Dict[str, Any]] = None

class VoiceIntegrationEngine:
    """Main integration engine for end-to-end voice processing"""

    def __init__(self, safe_room_mode: bool = True):
        self.safe_room_mode = safe_room_mode
        self.voice_extractor = VoicePatternExtractor()
        self.prompt_generator = DynamicPromptGenerator()
        self.safe_room = NuclearSafeRoom() if safe_room_mode else None

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def create_personalized_voice(self,
                               data_path: str,
                               output_path: str = "personalized_voice_prompt.txt",
                               include_code_analysis: bool = True) -> IntegrationResult:
        """
        Complete workflow: Extract voice patterns → Generate personalized prompt

        Args:
            data_path: Path to user's data (emails, docs, code, etc.)
            output_path: Where to save the generated prompt
            include_code_analysis: Whether to analyze code style patterns

        Returns:
            IntegrationResult with voice profile and generated prompt
        """

        try:
            self.logger.info(f"🎤 Starting voice integration for: {data_path}")

            # Phase 1: Secure data processing with Nuclear Safe Room
            processed_data = self._process_data_securely(data_path)
            if not processed_data:
                return IntegrationResult(
                    success=False,
                    error_message="Failed to process input data"
                )

            # Phase 2: Extract voice patterns
            self.logger.info("🔍 Extracting voice patterns...")
            voice_profile = self._extract_voice_patterns(processed_data, include_code_analysis)

            # Phase 3: Generate personalized prompt
            self.logger.info("✨ Generating personalized system prompt...")
            personalized_prompt = self._generate_personalized_prompt(voice_profile)

            # Phase 4: Save results
            self._save_results(personalized_prompt, output_path, voice_profile)

            # Phase 5: Cleanup (if using safe room)
            if self.safe_room:
                self.safe_room.cleanup_temporary_data()

            processing_stats = {
                "files_processed": len(processed_data.get("files", [])),
                "total_characters": processed_data.get("total_chars", 0),
                "voice_confidence": voice_profile.confidence_score if hasattr(voice_profile, 'confidence_score') else 0.85,
                "prompt_tokens": len(personalized_prompt.split())
            }

            return IntegrationResult(
                success=True,
                voice_profile=voice_profile,
                personalized_prompt=personalized_prompt,
                processing_stats=processing_stats
            )

        except Exception as e:
            self.logger.error(f"❌ Voice integration failed: {str(e)}")
            return IntegrationResult(
                success=False,
                error_message=str(e)
            )

    def _process_data_securely(self, data_path: str) -> Optional[Dict[str, Any]]:
        """Process user data through nuclear safe room if enabled"""

        if self.safe_room:
            try:
                # Use nuclear safe room for secure processing
                batch_id = self.safe_room.enter_room_one(data_path)
                if self.safe_room.validate_airlock_transfer(batch_id):
                    success = self.safe_room.enter_room_two(batch_id)
                    if success:
                        status = self.safe_room.get_room_two_status()
                        # Extract processed data from safe room
                        processed_data = {
                            "files": [data_path],
                            "total_chars": status.get("total_chars", 0),
                            "batch_id": batch_id,
                            "processing_mode": "safe_room"
                        }
                        return processed_data
                return None
            except Exception as e:
                self.logger.error(f"Safe room processing failed: {e}")
                return None
        else:
            # Direct processing (less secure)
            return self._direct_process_data(data_path)

    def _direct_process_data(self, data_path: str) -> Dict[str, Any]:
        """Direct data processing without safe room"""

        data_path = Path(data_path)
        processed_files = []
        total_chars = 0

        if data_path.is_file():
            content = data_path.read_text(encoding='utf-8', errors='ignore')
            processed_files.append(str(data_path))
            total_chars += len(content)
        elif data_path.is_dir():
            for file_path in data_path.rglob("*"):
                if file_path.is_file() and self._is_processable_file(file_path):
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        processed_files.append(str(file_path))
                        total_chars += len(content)
                    except Exception as e:
                        self.logger.warning(f"Could not process {file_path}: {e}")

        return {
            "files": processed_files,
            "total_chars": total_chars,
            "processing_mode": "direct"
        }

    def _extract_voice_patterns(self, processed_data: Dict[str, Any], include_code_analysis: bool) -> VoiceProfile:
        """Extract comprehensive voice patterns from processed data"""

        # Handle different data formats
        files = processed_data.get("files", [])
        if isinstance(files, str):
            files = [files]

        # Prepare data sources for voice extractor
        data_sources = []
        for file_path in files:
            if self._is_text_file(Path(file_path)):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if len(content.strip()) > 50:  # Minimum content threshold
                            data_sources.append({
                                "type": "text",
                                "path": file_path,
                                "content": content
                            })
                except Exception as e:
                    self.logger.warning(f"Could not read {file_path}: {e}")

        # Use the voice extractor's analyze_user_data method
        user_id = "temp_user"  # Temporary ID for this session
        voice_profile = self.voice_extractor.analyze_user_data(user_id, data_sources)

        # Extract from code files if requested
        if include_code_analysis:
            code_files = [f for f in files if self._is_code_file(Path(f))]
            if code_files:
                code_patterns = self._extract_code_style_patterns(code_files)
                if hasattr(voice_profile, 'code_patterns'):
                    voice_profile.code_patterns = code_patterns

        return voice_profile

    def _extract_code_style_patterns(self, code_files: List[str]) -> Dict[str, Any]:
        """Extract coding style patterns from source code"""

        code_patterns = {
            "naming_conventions": {},
            "architecture_patterns": [],
            "comment_style": {},
            "documentation_patterns": []
        }

        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Analyze naming conventions
                code_patterns["naming_conventions"].update(
                    self._analyze_naming_conventions(content, file_path)
                )

                # Analyze comment style
                code_patterns["comment_style"].update(
                    self._analyze_comment_style(content, file_path)
                )

            except Exception as e:
                self.logger.warning(f"Could not analyze code patterns in {file_path}: {e}")

        return code_patterns

    def _analyze_naming_conventions(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze naming conventions in code"""
        # Simple pattern analysis - can be enhanced
        conventions = {
            "variable_case": "snake_case" if "_" in content else "camelCase",
            "function_case": "snake_case" if "def " in content and "_" in content else "camelCase",
            "class_case": "PascalCase" if "class " in content else "unknown"
        }
        return {file_path: conventions}

    def _analyze_comment_style(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze comment style in code"""
        import re

        # Count different comment types
        single_line_comments = len(re.findall(r'#.*', content))
        multi_line_comments = len(re.findall(r'""".*?"""', content, re.DOTALL))

        comment_style = {
            "prefers_single_line": single_line_comments > multi_line_comments,
            "comment_frequency": (single_line_comments + multi_line_comments) / max(len(content.split('\n')), 1)
        }

        return {file_path: comment_style}

    def _generate_personalized_prompt(self, voice_profile: VoiceProfile) -> str:
        """Generate personalized system prompt from voice profile"""

        try:
            # Use dynamic prompt generator
            personalized_prompt = self.prompt_generator.generate_personalized_prompt(
                voice_profile,
                target_model="claude"
            )

            return personalized_prompt
        except Exception as e:
            self.logger.error(f"Prompt generation failed: {e}")
            # Fallback to basic prompt
            return self._generate_fallback_prompt(voice_profile)

    def _generate_fallback_prompt(self, voice_profile: VoiceProfile) -> str:
        """Generate fallback prompt if dynamic generation fails"""

        # Extract key characteristics
        char = voice_profile.characteristics

        prompt = f"""You are an AI assistant that communicates in the style of the user.

Communication Style: {char.communication_style}
Key Phrases: {', '.join(char.key_phrases[:10]) if char.key_phrases else 'None identified'}
Sentence Length: {char.sentence_length:.1f} words on average
Formality Level: {char.formality:.2f}/1.0
Technical Depth: {char.technical_level:.2f}/1.0
Enthusiasm: {char.enthusiasm:.2f}/1.0
Directness: {char.directness:.2f}/1.0

Adapt your responses to match this communication style while maintaining clarity and helpfulness."""

        return prompt

    def _save_results(self, prompt: str, output_path: str, voice_profile: VoiceProfile):
        """Save the generated prompt and metadata"""

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save main prompt
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt)

        # Save metadata
        metadata_path = output_path.with_suffix('.json')
        metadata = {
            "voice_profile": asdict(voice_profile) if hasattr(voice_profile, '__dict__') else str(voice_profile),
            "prompt_length": len(prompt),
            "prompt_tokens": len(prompt.split()),
            "generated_at": str(Path().cwd())
        }

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)

    def _is_processable_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        return self._is_text_file(file_path) or self._is_code_file(file_path)

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file"""
        text_extensions = {'.txt', '.md', '.txt', '.log', '.eml', '.mbox'}
        return file_path.suffix.lower() in text_extensions

    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file"""
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs'}
        return file_path.suffix.lower() in code_extensions

def main():
    """Command line interface for voice integration"""

    import argparse

    parser = argparse.ArgumentParser(description='Create personalized AI voice prompt')
    parser.add_argument('data_path', help='Path to user data (files or directory)')
    parser.add_argument('-o', '--output', default='personalized_voice_prompt.txt',
                       help='Output file path')
    parser.add_argument('--no-code', action='store_true',
                       help='Skip code style analysis')
    parser.add_argument('--no-safe-room', action='store_true',
                       help='Disable nuclear safe room processing')

    args = parser.parse_args()

    # Create integration engine
    engine = VoiceIntegrationEngine(safe_room_mode=not args.no_safe_room)

    # Process and generate
    result = engine.create_personalized_voice(
        data_path=args.data_path,
        output_path=args.output,
        include_code_analysis=not args.no_code
    )

    if result.success:
        print(f"✅ Success! Personalized voice prompt created:")
        print(f"   📁 Output: {args.output}")
        if result.processing_stats:
            print(f"   📊 Processed {result.processing_stats['files_processed']} files")
            print(f"   📝 Generated {result.processing_stats['prompt_tokens']} tokens")
    else:
        print(f"❌ Failed: {result.error_message}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
