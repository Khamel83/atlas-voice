"""Prompt generation service for creating AI system prompts."""

from datetime import datetime
from typing import Optional
from atlas_voice.models import VoicePattern, VoicePrompt


class GeneratorService:
    """Generates AI system prompts from voice patterns."""

    def generate(
        self,
        pattern: VoicePattern,
        context: str = "professional",
        name: Optional[str] = None
    ) -> VoicePrompt:
        """
        Generate an AI system prompt from a voice pattern.

        Args:
            pattern: Voice pattern to base prompt on
            context: Context for the prompt ('professional', 'casual', 'creative', 'technical')
            name: Optional custom name for the prompt

        Returns:
            VoicePrompt ready to use with any AI
        """
        prompt_text = self._build_prompt(pattern, context)

        prompt_id = f"prompt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        prompt_name = name or f"{pattern.name} - {context.title()}"

        return VoicePrompt(
            id=prompt_id,
            pattern_id=pattern.id,
            name=prompt_name,
            context=context,
            prompt_text=prompt_text,
            created_at=datetime.utcnow(),
        )

    def _build_prompt(self, pattern: VoicePattern, context: str) -> str:
        """Build the actual prompt text."""
        # Get top function words
        top_function_words = [fw.word for fw in pattern.function_words[:7]]

        # Get style markers by category
        casual_markers = []
        formal_markers = []
        personal_markers = []
        technical_markers = []

        for marker in pattern.style_markers:
            if marker.category == "casual":
                casual_markers = marker.phrases
            elif marker.category == "formal":
                formal_markers = marker.phrases
            elif marker.category == "personal":
                personal_markers = marker.phrases
            elif marker.category == "technical":
                technical_markers = marker.phrases

        # Determine formality
        if len(formal_markers) > len(casual_markers) * 2:
            formality = "formal and professional"
        elif len(casual_markers) > len(formal_markers) * 2:
            formality = "casual and conversational"
        else:
            formality = "balanced between formal and casual"

        # Build prompt sections
        sections = []

        # Header
        sections.append(f"You are writing in a specific person's voice. Follow these patterns closely:\n")

        # Writing style
        sections.append("## WRITING STYLE")
        sections.append(f"- Tone: {formality}")
        sections.append(f"- Average sentence length: {pattern.avg_sentence_length} words")
        sections.append(f"- Vocabulary: {'Rich and varied' if pattern.vocab_richness > 0.1 else 'Clear and concise'}")
        sections.append("")

        # Sentence structure
        sections.append("## SENTENCE STRUCTURE")
        sections.append(f"- Average {pattern.avg_sentence_length} words per sentence")
        if pattern.sentence_starters:
            starters = pattern.sentence_starters[:5]
            sections.append(f"- Common sentence starters: {', '.join(starters)}")
        sections.append("")

        # Language patterns
        sections.append("## LANGUAGE PATTERNS")
        if top_function_words:
            sections.append(f"- Frequently uses: {', '.join(top_function_words)}")

        # Personal voice markers
        if personal_markers:
            sections.append(f"- Personal phrases: {', '.join(personal_markers[:5])}")

        # Casual markers
        if casual_markers:
            sections.append(f"- Casual expressions: {', '.join(casual_markers[:5])}")

        # Formal markers (if present and context is professional)
        if formal_markers and context in ["professional", "technical"]:
            sections.append(f"- Formal transitions: {', '.join(formal_markers[:5])}")

        # Technical markers (if present)
        if technical_markers and context in ["technical", "professional"]:
            sections.append(f"- Technical terms used naturally: {', '.join(technical_markers[:5])}")

        sections.append("")

        # Communication approach
        sections.append("## COMMUNICATION APPROACH")

        if "i" in [fw.word for fw in pattern.function_words[:5]]:
            sections.append("- Uses first person ('I think', 'I would') to express opinions clearly")

        if "you" in [fw.word for fw in pattern.function_words[:5]]:
            sections.append("- Directly engages the reader with 'you'")

        if "we" in [fw.word for fw in pattern.function_words[:10]]:
            sections.append("- Uses 'we' for collaborative thinking")

        if "what" in [fw.word for fw in pattern.function_words[:15]]:
            sections.append("- Asks questions to drive thinking forward")

        sections.append("")

        # Context-specific guidance
        sections.append("## CONTEXT-SPECIFIC GUIDANCE")

        if context == "professional":
            sections.append("- Focus: Clear, professional communication")
            sections.append("- Goal: Be direct and solution-oriented")
            sections.append("- Avoid: Over-casual language or unnecessary jargon")
        elif context == "casual":
            sections.append("- Focus: Natural, conversational tone")
            sections.append("- Goal: Sound friendly and approachable")
            sections.append("- Embrace: Personal anecdotes and casual expressions")
        elif context == "creative":
            sections.append("- Focus: Engaging and expressive writing")
            sections.append("- Goal: Be vivid and compelling")
            sections.append("- Embrace: Varied sentence structures and rich vocabulary")
        elif context == "technical":
            sections.append("- Focus: Precise technical communication")
            sections.append("- Goal: Be accurate and clear about technical concepts")
            sections.append("- Balance: Technical accuracy with natural voice")

        sections.append("")

        # Quality checklist
        sections.append("## QUALITY CHECKLIST")
        sections.append("Before responding, verify:")
        sections.append(f"- ✓ Sentences average ~{pattern.avg_sentence_length} words with natural flow")
        sections.append("- ✓ Uses characteristic function words naturally")
        sections.append(f"- ✓ Maintains {formality} tone")
        sections.append("- ✓ Sounds like something this person would actually say")
        sections.append("")

        # Source info
        sections.append(f"_Based on analysis of {pattern.total_words:,} words from {pattern.source_description}_")

        return "\n".join(sections)
