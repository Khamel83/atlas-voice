"""Tests for the prompt generator service."""

import pytest
from atlas_voice.services import AnalyzerService, GeneratorService
from atlas_voice.models import VoicePrompt


class TestGeneratorService:
    """Test the prompt generator."""

    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return GeneratorService()

    @pytest.fixture
    def sample_pattern(self):
        """Create a sample voice pattern."""
        analyzer = AnalyzerService()
        texts = [
            "I think this is a great approach. Let's move forward with it.",
            "We should focus on the core features first. What do you think?",
            "Actually, I'm not convinced this will work. Can we explore alternatives?",
            "The implementation looks solid. However, we need to test thoroughly.",
        ]
        return analyzer.analyze(texts, name="Test Voice", source_description="Test data")

    def test_generate_professional(self, generator, sample_pattern):
        """Test professional context prompt generation."""
        prompt = generator.generate(sample_pattern, context="professional")

        assert isinstance(prompt, VoicePrompt)
        assert prompt.pattern_id == sample_pattern.id
        assert prompt.context == "professional"
        assert len(prompt.prompt_text) > 100

        # Should mention professional context
        assert "professional" in prompt.prompt_text.lower() or "clear" in prompt.prompt_text.lower()

    def test_generate_casual(self, generator, sample_pattern):
        """Test casual context prompt generation."""
        prompt = generator.generate(sample_pattern, context="casual")

        assert prompt.context == "casual"
        assert len(prompt.prompt_text) > 100

    def test_generate_creative(self, generator, sample_pattern):
        """Test creative context prompt generation."""
        prompt = generator.generate(sample_pattern, context="creative")

        assert prompt.context == "creative"
        assert len(prompt.prompt_text) > 100

    def test_generate_technical(self, generator, sample_pattern):
        """Test technical context prompt generation."""
        prompt = generator.generate(sample_pattern, context="technical")

        assert prompt.context == "technical"
        assert len(prompt.prompt_text) > 100

    def test_prompt_includes_statistics(self, generator, sample_pattern):
        """Test that prompt includes key statistics."""
        prompt = generator.generate(sample_pattern)

        # Should mention sentence length
        assert str(sample_pattern.avg_sentence_length) in prompt.prompt_text

        # Should include some function words
        top_words = [fw.word for fw in sample_pattern.function_words[:5]]
        assert any(word in prompt.prompt_text.lower() for word in top_words)

    def test_prompt_includes_source_info(self, generator, sample_pattern):
        """Test that prompt includes source description."""
        prompt = generator.generate(sample_pattern)

        # Should mention the source
        assert sample_pattern.source_description in prompt.prompt_text

    def test_custom_name(self, generator, sample_pattern):
        """Test custom prompt naming."""
        custom_name = "My Custom Prompt"
        prompt = generator.generate(sample_pattern, name=custom_name)

        assert prompt.name == custom_name

    def test_default_name_format(self, generator, sample_pattern):
        """Test default prompt naming."""
        prompt = generator.generate(sample_pattern, context="professional")

        # Should include pattern name and context
        assert "Test Voice" in prompt.name
        assert "Professional" in prompt.name

    def test_prompt_quality_checklist(self, generator, sample_pattern):
        """Test that prompts include quality checklist."""
        prompt = generator.generate(sample_pattern)

        # Should have checklist section
        assert "CHECKLIST" in prompt.prompt_text.upper() or "✓" in prompt.prompt_text

    def test_prompt_sections(self, generator, sample_pattern):
        """Test that prompts have clear sections."""
        prompt = generator.generate(sample_pattern)

        text = prompt.prompt_text

        # Should have key sections
        assert "##" in text or "STRUCTURE" in text.upper()
        assert "STYLE" in text.upper() or "TONE" in text.upper()

    def test_unique_prompt_ids(self, generator, sample_pattern):
        """Test that each prompt gets a unique ID."""
        prompt1 = generator.generate(sample_pattern)
        prompt2 = generator.generate(sample_pattern)

        assert prompt1.id != prompt2.id

    def test_prompt_timestamp(self, generator, sample_pattern):
        """Test that prompts have creation timestamps."""
        prompt = generator.generate(sample_pattern)

        assert prompt.created_at is not None
        # Should be recent (within last minute)
        from datetime import datetime, timedelta
        assert datetime.utcnow() - prompt.created_at < timedelta(minutes=1)
