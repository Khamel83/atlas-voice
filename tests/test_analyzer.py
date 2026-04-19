"""Tests for the analyzer service."""

import pytest
from atlas_voice.services import AnalyzerService
from atlas_voice.models import VoicePattern


class TestAnalyzerService:
    """Test the voice pattern analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return AnalyzerService()

    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing."""
        return [
            "I think we should focus on the core features first. Let's build something people actually want.",
            "The implementation looks good. However, we might want to consider edge cases.",
            "Actually, I'm not sure this is the right approach. What do you think?",
            "We need to optimize the database queries. Performance is critical here.",
        ]

    def test_analyze_basic(self, analyzer, sample_texts):
        """Test basic pattern analysis."""
        pattern = analyzer.analyze(sample_texts, name="Test Profile")

        assert isinstance(pattern, VoicePattern)
        assert pattern.name == "Test Profile"
        assert pattern.total_words > 0
        assert pattern.total_sentences > 0
        assert pattern.avg_sentence_length > 0
        assert pattern.vocab_richness > 0
        assert len(pattern.function_words) > 0

    def test_analyze_empty(self, analyzer):
        """Test with empty input."""
        pattern = analyzer.analyze([], name="Empty")

        assert pattern.total_words == 0
        assert pattern.total_sentences == 0

    def test_function_word_extraction(self, analyzer, sample_texts):
        """Test function word frequency extraction."""
        pattern = analyzer.analyze(sample_texts)

        # Should have common function words
        function_word_set = {fw.word for fw in pattern.function_words}

        assert "i" in function_word_set or "the" in function_word_set
        assert "we" in function_word_set or "to" in function_word_set

        # Frequencies should be between 0 and 100
        for fw in pattern.function_words:
            assert 0 < fw.frequency <= 100

    def test_style_marker_detection(self, analyzer, sample_texts):
        """Test style marker detection."""
        pattern = analyzer.analyze(sample_texts)

        # Should detect casual markers ("actually", "I think")
        marker_categories = {sm.category for sm in pattern.style_markers}

        assert "casual" in marker_categories or "personal" in marker_categories

    def test_sentence_starters(self, analyzer, sample_texts):
        """Test sentence starter extraction."""
        pattern = analyzer.analyze(sample_texts)

        # Should find common starters
        starters = set(pattern.sentence_starters)

        assert len(starters) > 0
        # At least one should start with a common word
        assert any(s.startswith(("i", "the", "we", "what")) for s in starters)

    def test_vocab_richness(self, analyzer):
        """Test vocabulary richness calculation."""
        # Repetitive text (low richness)
        repetitive = ["the the the the the"] * 10
        pattern1 = analyzer.analyze(repetitive)

        # Varied text (higher richness)
        varied = [
            "The quick brown fox jumps over lazy dog.",
            "Artificial intelligence transforms modern technology rapidly.",
            "Beautiful sunset painted vibrant colors across sky.",
        ]
        pattern2 = analyzer.analyze(varied)

        # Varied text should have higher vocabulary richness
        assert pattern2.vocab_richness > pattern1.vocab_richness

    def test_sentence_length_consistency(self, analyzer):
        """Test sentence length calculation."""
        # Short sentences
        short = ["I agree.", "Sounds good.", "Let's do it.", "Perfect."]
        pattern_short = analyzer.analyze(short)

        # Long sentences
        long = [
            "I think we should carefully consider all the potential implications before making a final decision on this matter.",
            "The implementation requires thorough testing across multiple environments to ensure compatibility and reliability.",
        ]
        pattern_long = analyzer.analyze(long)

        # Long sentences should have higher average length
        assert pattern_long.avg_sentence_length > pattern_short.avg_sentence_length

    def test_source_description(self, analyzer, sample_texts):
        """Test source description is preserved."""
        description = "Test emails from 2024"
        pattern = analyzer.analyze(sample_texts, source_description=description)

        assert pattern.source_description == description

    def test_pattern_id_generation(self, analyzer, sample_texts):
        """Test that each pattern gets a unique ID."""
        pattern1 = analyzer.analyze(sample_texts)
        pattern2 = analyzer.analyze(sample_texts)

        # IDs should be different (timestamp-based)
        assert pattern1.id != pattern2.id

    def test_large_text_handling(self, analyzer):
        """Test handling of large amounts of text."""
        # Generate large sample
        large_sample = [
            "This is a test sentence with various words and patterns."
        ] * 1000

        pattern = analyzer.analyze(large_sample)

        # Should successfully analyze without errors
        assert pattern.total_words > 10000
        assert pattern.total_sentences > 1000
        assert len(pattern.function_words) > 0
