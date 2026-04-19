#!/usr/bin/env python3
"""
Dynamic Prompt Generator
Takes extracted voice patterns and generates personalized 4000-token system prompts
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from voice_pattern_extractor import VoiceProfile, VoiceCharacteristics


@dataclass
class PromptTemplate:
    """Template for generating personalized prompts"""
    name: str
    target_model: str  # 'claude', 'gpt', 'generic'
    base_template: str
    voice_sections: Dict[str, str]
    context_sections: Dict[str, str]
    max_tokens: int = 4000


class DynamicPromptGenerator:
    """Generates personalized system prompts from voice patterns"""

    def __init__(self, templates_path: str = "prompt_templates"):
        self.templates_path = Path(templates_path)
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, PromptTemplate]:
        """Load prompt templates"""
        templates = {}

        # Base OOS template for Claude
        claude_template = PromptTemplate(
            name="oos_claude",
            target_model="claude",
            base_template=self._get_claude_base_template(),
            voice_sections=self._get_voice_sections(),
            context_sections=self._get_context_sections(),
            max_tokens=4000
        )

        # GPT template (slightly different structure)
        gpt_template = PromptTemplate(
            name="oos_gpt",
            target_model="gpt",
            base_template=self._get_gpt_base_template(),
            voice_sections=self._get_voice_sections(),
            context_sections=self._get_context_sections(),
            max_tokens=4000
        )

        templates["claude"] = claude_template
        templates["gpt"] = gpt_template
        templates["generic"] = claude_template  # Default to Claude format

        return templates

    def generate_personalized_prompt(
        self,
        voice_profile: VoiceProfile,
        target_model: str = "claude",
        include_examples: bool = True
    ) -> str:
        """
        Generate a personalized system prompt from voice profile

        Args:
            voice_profile: Extracted voice patterns
            target_model: Target AI model ('claude', 'gpt', 'generic')
            include_examples: Whether to include example responses

        Returns:
            Personalized 4000-token system prompt
        """
        template = self.templates.get(target_model, self.templates["generic"])

        # Build personalized sections
        voice_section = self._build_voice_section(voice_profile, template)
        context_section = self._build_context_section(voice_profile, template)
        execution_section = self._build_execution_section(voice_profile, template)
        examples_section = self._build_examples_section(voice_profile) if include_examples else ""

        # Combine all sections
        prompt = template.base_template.format(
            user_name=voice_profile.user_id.replace('_', ' ').title(),
            voice_section=voice_section,
            context_section=context_section,
            execution_section=execution_section,
            examples_section=examples_section,
            confidence_note=self._build_confidence_note(voice_profile)
        )

        # Ensure we're within token limits
        prompt = self._optimize_token_usage(prompt, template.max_tokens)

        return prompt

    def _get_claude_base_template(self) -> str:
        """Base template for Claude models"""
        return """# Personalized AI Assistant for {user_name}

You are an AI assistant that communicates in {user_name}'s authentic voice while maintaining high intelligence and capability. Your core principle is **ACTION OVER CLARIFICATION** - make smart assumptions based on context rather than asking endless questions.

{voice_section}

{context_section}

{execution_section}

{examples_section}

{confidence_note}

Remember: **Make intelligent assumptions, execute immediately, adapt communication to {user_name}'s authentic patterns, and optimize for rapid progress over perfect precision.**"""

    def _get_gpt_base_template(self) -> str:
        """Base template for GPT models"""
        return """You are an AI assistant that communicates exactly like {user_name} while maintaining high intelligence and capability.

{voice_section}

{context_section}

{execution_section}

{examples_section}

{confidence_note}

Always respond in {user_name}'s authentic voice style while providing intelligent, helpful assistance."""

    def _get_voice_sections(self) -> Dict[str, str]:
        """Voice-related template sections"""
        return {
            "characteristics": """## Voice Characteristics

**Communication Style**: {communication_style}
**Key Phrases**: Use these naturally: {key_phrases}
**Sentence Structure**: Average {sentence_length:.1f} words per sentence
**Formality Level**: {formality_description} (score: {formality:.2f})
**Technical Depth**: {technical_description} (score: {technical_level:.2f})
**Enthusiasm**: {enthusiasm_description} (score: {enthusiasm:.2f})
**Directness**: {directness_description} (score: {directness:.2f})""",

            "signature_phrases": """## Signature Communication Patterns

**Primary Phrases**: {primary_phrases}
**Transition Words**: {transition_words}
**Response Patterns**: {response_patterns}""",

            "tone_adaptation": """## Tone Adaptation Rules

{tone_rules}"""
        }

    def _get_context_sections(self) -> Dict[str, str]:
        """Context-related template sections"""
        return {
            "preferences": """## Context Preferences

{context_preferences}""",

            "detection": """## Automatic Context Detection

{context_detection_rules}""",

            "switching": """## Voice Adaptation Triggers

{voice_switching_rules}"""
        }

    def _build_voice_section(self, profile: VoiceProfile, template: PromptTemplate) -> str:
        """Build the voice characteristics section"""
        char = profile.characteristics

        # Describe formality level
        if char.formality < 0.3:
            formality_desc = "Very casual and informal"
        elif char.formality < 0.5:
            formality_desc = "Casual but professional"
        elif char.formality < 0.7:
            formality_desc = "Balanced formal and informal"
        else:
            formality_desc = "Formal and professional"

        # Describe technical level
        if char.technical_level < 0.2:
            technical_desc = "Minimal technical jargon, accessible explanations"
        elif char.technical_level < 0.4:
            technical_desc = "Moderate technical depth with clear explanations"
        elif char.technical_level < 0.6:
            technical_desc = "Comfortable with technical concepts and terminology"
        else:
            technical_desc = "High technical sophistication and specialized vocabulary"

        # Describe enthusiasm
        if char.enthusiasm < 0.3:
            enthusiasm_desc = "Measured and calm tone"
        elif char.enthusiasm < 0.6:
            enthusiasm_desc = "Moderately enthusiastic and engaged"
        else:
            enthusiasm_desc = "High energy and enthusiastic communication"

        # Describe directness
        if char.directness < 0.4:
            directness_desc = "Thoughtful and diplomatic approach"
        elif char.directness < 0.7:
            directness_desc = "Balanced directness with context"
        else:
            directness_desc = "Direct and straightforward communication"

        # Build key phrases string
        key_phrases_str = ", ".join([f'"{phrase}"' for phrase in char.key_phrases[:8]])

        voice_section = f"""## Voice Characteristics

**Communication Style**: {char.communication_style}
**Key Phrases**: Use these naturally: {key_phrases_str}
**Sentence Structure**: Average {char.sentence_length:.1f} words per sentence
**Formality Level**: {formality_desc} (score: {char.formality:.2f})
**Technical Depth**: {technical_desc} (score: {char.technical_level:.2f})
**Enthusiasm**: {enthusiasm_desc} (score: {char.enthusiasm:.2f})
**Directness**: {directness_desc} (score: {char.directness:.2f})

## Signature Communication Patterns

**Primary Phrases**: {self._format_signature_phrases(profile.signature_phrases)}
**Question Frequency**: {char.question_frequency:.2f} questions per sentence
**Exclamation Usage**: {char.exclamation_frequency:.2f} exclamations per sentence
**Paragraph Style**: Average {char.paragraph_length:.1f} sentences per paragraph"""

        return voice_section

    def _build_context_section(self, profile: VoiceProfile, template: PromptTemplate) -> str:
        """Build the context preferences section"""
        context_prefs = profile.context_preferences

        # Sort contexts by preference
        sorted_contexts = sorted(context_prefs.items(), key=lambda x: x[1], reverse=True)

        context_section = "## Context Preferences\n\n"

        for context, preference in sorted_contexts:
            if preference > 0.3:  # Only include significant preferences
                context_section += f"**{context.title()} Context**: {preference:.1%} preference\n"

        context_section += "\n## Automatic Context Detection\n\n"

        # Add context-specific communication rules
        if context_prefs.get('technical', 0) > 0.3:
            context_section += "- **Technical discussions**: Increase technical depth while maintaining accessibility\n"

        if context_prefs.get('casual', 0) > 0.3:
            context_section += "- **Casual conversations**: Use more informal language and personal expressions\n"

        if context_prefs.get('professional', 0) > 0.3:
            context_section += "- **Professional contexts**: Maintain appropriate formality while keeping personal voice\n"

        if context_prefs.get('creative', 0) > 0.3:
            context_section += "- **Creative discussions**: Embrace enthusiasm and exploratory language\n"

        return context_section

    def _build_execution_section(self, profile: VoiceProfile, template: PromptTemplate) -> str:
        """Build the execution framework section"""
        char = profile.characteristics

        execution_section = """## Execution Framework

### Smart Assumption Rules
- Analyze existing context and patterns
- Make intelligent inferences about user intent
- Default to modern, well-supported approaches
- Prefer action over endless clarification

### Response Structure"""

        # Adapt response structure based on user's style
        if char.directness > 0.7:
            execution_section += """
1. **Direct Response**: Address the core request immediately
2. **Key Implementation**: Provide working solution
3. **Brief Context**: Explain key decisions concisely"""

        elif char.formality > 0.6:
            execution_section += """
1. **Professional Opening**: Acknowledge the request formally
2. **Structured Solution**: Provide organized, detailed response
3. **Summary**: Recap key points and next steps"""

        else:
            execution_section += """
1. **Friendly Opening**: Casual but helpful acknowledgment
2. **Practical Solution**: Working answer with explanation
3. **Follow-up**: Check understanding and offer additional help"""

        # Add quality standards based on technical level
        execution_section += "\n\n### Quality Standards\n"

        if char.technical_level > 0.4:
            execution_section += "- Include technical details and implementation considerations\n"
            execution_section += "- Provide code examples and architectural guidance\n"

        if char.formality > 0.5:
            execution_section += "- Maintain professional documentation standards\n"
            execution_section += "- Include error handling and edge cases\n"

        execution_section += "- Focus on practical, working solutions\n"
        execution_section += "- Anticipate related needs and provide comprehensive answers\n"

        return execution_section

    def _build_examples_section(self, profile: VoiceProfile) -> str:
        """Build example responses section"""
        char = profile.characteristics

        examples_section = "## Example Response Patterns\n\n"

        # Technical example
        if profile.context_preferences.get('technical', 0) > 0.2:
            if char.formality < 0.4:
                examples_section += """**Technical Question Response**:
"Yeah, so basically what you want to do here is set up a REST API. Like, the key thing to understand is that you're dealing with stateless requests, you know? Here's how I'd approach it..."

"""
            else:
                examples_section += """**Technical Question Response**:
"For this implementation, you'll want to consider the architectural patterns. The key components include the API layer, business logic, and data persistence. Let me walk you through the approach..."

"""

        # Problem-solving example
        if char.directness > 0.6:
            examples_section += """**Problem-Solving Response**:
"I'll fix this for you. Based on the error message, the issue is [specific problem]. Here's the solution..."

"""
        else:
            examples_section += """**Problem-Solving Response**:
"Let me help you work through this. It looks like there might be a few things going on here. First, let's address [main issue], then we can look at [related concerns]..."

"""

        # Include sample sentences from the user's actual writing
        if profile.sample_sentences:
            examples_section += "**Your Natural Communication Style**:\n"
            for i, sentence in enumerate(profile.sample_sentences[:3], 1):
                examples_section += f"{i}. \"{sentence}\"\n"
            examples_section += "\n"

        return examples_section

    def _build_confidence_note(self, profile: VoiceProfile) -> str:
        """Build confidence and adaptation note"""
        confidence = profile.confidence_score

        if confidence > 0.8:
            confidence_level = "High confidence"
            adaptation_note = "Patterns are well-established and reliable."
        elif confidence > 0.6:
            confidence_level = "Good confidence"
            adaptation_note = "Patterns are solid with room for refinement."
        else:
            confidence_level = "Moderate confidence"
            adaptation_note = "Continue learning and adapting patterns as more data becomes available."

        return f"""## Voice Pattern Confidence

**Confidence Level**: {confidence_level} ({confidence:.1%})
**Adaptation**: {adaptation_note}

This voice profile is based on analysis of {len(profile.sample_sentences)} sample communications with {confidence:.1%} pattern confidence."""

    def _format_signature_phrases(self, phrases: List[str]) -> str:
        """Format signature phrases for display"""
        if not phrases:
            return "No distinctive phrases identified"

        formatted = []
        for phrase in phrases[:8]:  # Limit to top 8
            formatted.append(f'"{phrase}"')

        return ", ".join(formatted)

    def _optimize_token_usage(self, prompt: str, max_tokens: int) -> str:
        """Optimize prompt to stay within token limits"""
        # Rough estimation: 1 token ≈ 0.75 words
        estimated_tokens = len(prompt.split()) / 0.75

        if estimated_tokens <= max_tokens:
            return prompt

        # If over limit, trim less important sections
        lines = prompt.split('\n')

        # Priority order for trimming (trim lowest priority first)
        trim_priorities = [
            '**Example Response Patterns**',
            '**Your Natural Communication Style**',
            '**Voice Pattern Confidence**',
            '## Example Response Patterns',
            'This voice profile is based on'
        ]

        for trim_target in trim_priorities:
            if estimated_tokens <= max_tokens:
                break

            # Remove sections containing trim target
            filtered_lines = []
            skip_section = False

            for line in lines:
                if trim_target in line:
                    skip_section = True
                    continue
                elif line.startswith('##') and skip_section:
                    skip_section = False

                if not skip_section:
                    filtered_lines.append(line)

            lines = filtered_lines
            prompt = '\n'.join(lines)
            estimated_tokens = len(prompt.split()) / 0.75

        return prompt

    def export_prompt(
        self,
        voice_profile: VoiceProfile,
        output_path: str,
        target_model: str = "claude",
        include_metadata: bool = True
    ) -> str:
        """
        Export personalized prompt to file

        Args:
            voice_profile: Voice profile to generate prompt from
            output_path: Path to save the prompt
            target_model: Target AI model
            include_metadata: Whether to include generation metadata

        Returns:
            Path to exported file
        """
        prompt = self.generate_personalized_prompt(voice_profile, target_model)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = prompt

        if include_metadata:
            metadata = f"""<!--
Generated by Dynamic Prompt Generator
User ID: {voice_profile.user_id}
Target Model: {target_model}
Confidence Score: {voice_profile.confidence_score:.2%}
Generation Date: {self._get_current_timestamp()}
-->

"""
            content = metadata + content

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_file)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.now().isoformat()

    def compare_prompts(self, profile1: VoiceProfile, profile2: VoiceProfile) -> Dict[str, Any]:
        """Compare two voice profiles and their generated prompts"""
        prompt1 = self.generate_personalized_prompt(profile1)
        prompt2 = self.generate_personalized_prompt(profile2)

        comparison = {
            "profiles": {
                "profile1": {
                    "user_id": profile1.user_id,
                    "formality": profile1.characteristics.formality,
                    "technical_level": profile1.characteristics.technical_level,
                    "enthusiasm": profile1.characteristics.enthusiasm,
                    "confidence": profile1.confidence_score
                },
                "profile2": {
                    "user_id": profile2.user_id,
                    "formality": profile2.characteristics.formality,
                    "technical_level": profile2.characteristics.technical_level,
                    "enthusiasm": profile2.characteristics.enthusiasm,
                    "confidence": profile2.confidence_score
                }
            },
            "prompt_lengths": {
                "profile1": len(prompt1.split()),
                "profile2": len(prompt2.split())
            },
            "key_differences": self._identify_key_differences(profile1, profile2)
        }

        return comparison

    def _identify_key_differences(self, profile1: VoiceProfile, profile2: VoiceProfile) -> List[str]:
        """Identify key differences between two profiles"""
        differences = []

        char1, char2 = profile1.characteristics, profile2.characteristics

        if abs(char1.formality - char2.formality) > 0.3:
            differences.append(f"Formality: {char1.formality:.2f} vs {char2.formality:.2f}")

        if abs(char1.technical_level - char2.technical_level) > 0.2:
            differences.append(f"Technical Level: {char1.technical_level:.2f} vs {char2.technical_level:.2f}")

        if abs(char1.enthusiasm - char2.enthusiasm) > 0.3:
            differences.append(f"Enthusiasm: {char1.enthusiasm:.2f} vs {char2.enthusiasm:.2f}")

        if char1.communication_style != char2.communication_style:
            differences.append(f"Style: {char1.communication_style} vs {char2.communication_style}")

        return differences


def main():
    """Example usage of DynamicPromptGenerator"""
    from voice_pattern_extractor import VoicePatternExtractor

    # Load existing voice profile or create a sample one
    extractor = VoicePatternExtractor()
    generator = DynamicPromptGenerator()

    # Try to load existing profile
    profile = extractor.load_voice_profile("test_user")

    if not profile:
        print("No existing profile found. Please run voice_pattern_extractor.py first.")
        return

    # Generate personalized prompt
    claude_prompt = generator.generate_personalized_prompt(profile, "claude")

    print("Generated Personalized Prompt:")
    print("=" * 50)
    print(claude_prompt[:1000] + "...")
    print(f"\nTotal length: {len(claude_prompt.split())} words")

    # Export to file
    output_path = generator.export_prompt(profile, f"prompts/{profile.user_id}_claude_prompt.md")
    print(f"\nPrompt exported to: {output_path}")


if __name__ == "__main__":
    main()
