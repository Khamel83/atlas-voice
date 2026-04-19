"""Pattern analysis service for extracting voice characteristics."""

import re
from collections import Counter
from datetime import datetime
from typing import List, Dict
from atlas_voice.models import VoicePattern, FunctionWord, StyleMarker


class AnalyzerService:
    """Analyzes text samples to extract voice patterns."""

    # Common function words to track
    FUNCTION_WORDS = [
        "i", "you", "he", "she", "it", "we", "they",
        "a", "an", "the",
        "to", "of", "in", "for", "on", "with", "at", "from", "by", "about",
        "and", "or", "but", "if", "because", "as", "that", "which",
        "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did",
        "will", "would", "can", "could", "should", "may", "might", "must",
        "not", "no", "yes",
        "this", "that", "these", "those",
        "what", "when", "where", "who", "why", "how",
    ]

    # Style markers
    CASUAL_MARKERS = [
        "actually", "basically", "like", "you know", "i mean", "sort of",
        "kind of", "really", "pretty much", "just", "maybe", "probably",
        "totally", "definitely", "honestly", "literally",
    ]

    FORMAL_MARKERS = [
        "however", "therefore", "consequently", "furthermore", "moreover",
        "nevertheless", "accordingly", "subsequently", "hence", "thus",
        "whereas", "whereby", "herein", "thereof", "notwithstanding",
    ]

    PERSONAL_MARKERS = [
        "i think", "i feel", "i believe", "in my opinion", "personally",
        "i would say", "it seems to me", "from my perspective",
    ]

    TECHNICAL_MARKERS = [
        "implementation", "architecture", "optimize", "refactor", "debug",
        "deploy", "configure", "parameter", "function", "class", "method",
        "database", "api", "endpoint", "query", "schema",
    ]

    def analyze(
        self,
        texts: List[str],
        name: str = "Voice Profile",
        source_description: str = ""
    ) -> VoicePattern:
        """
        Analyze text samples and extract voice patterns.

        Args:
            texts: List of text samples
            name: Name for this voice profile
            source_description: Description of data source

        Returns:
            VoicePattern with extracted characteristics
        """
        # Combine all texts for analysis
        all_text = " ".join(texts)

        # Basic statistics
        words = self._tokenize(all_text)
        sentences = self._split_sentences(all_text)

        total_words = len(words)
        total_sentences = len(sentences)
        unique_words = len(set(word.lower() for word in words))

        avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
        vocab_richness = unique_words / total_words if total_words > 0 else 0
        avg_word_length = sum(len(w) for w in words) / total_words if total_words > 0 else 0

        # Function word frequencies
        function_words = self._analyze_function_words(words)

        # Style markers
        style_markers = self._analyze_style_markers(all_text.lower())

        # Sentence starters
        sentence_starters = self._analyze_sentence_starters(sentences)

        # Create pattern
        pattern_id = f"pattern_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        return VoicePattern(
            id=pattern_id,
            name=name,
            total_words=total_words,
            total_sentences=total_sentences,
            avg_sentence_length=round(avg_sentence_length, 1),
            vocab_richness=round(vocab_richness, 3),
            avg_word_length=round(avg_word_length, 1),
            function_words=function_words,
            style_markers=style_markers,
            sentence_starters=sentence_starters,
            source_description=source_description,
        )

    def _tokenize(self, text: str) -> List[str]:
        """Split text into words."""
        # Simple word tokenization
        return re.findall(r'\b\w+\b', text.lower())

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _analyze_function_words(self, words: List[str]) -> List[FunctionWord]:
        """Analyze function word frequencies."""
        total = len(words)
        if total == 0:
            return []

        word_counts = Counter(words)

        function_word_list = []
        for word in self.FUNCTION_WORDS:
            count = word_counts.get(word, 0)
            if count > 0:
                frequency = (count / total) * 100
                function_word_list.append(
                    FunctionWord(word=word, frequency=round(frequency, 2))
                )

        # Sort by frequency
        function_word_list.sort(key=lambda x: x.frequency, reverse=True)

        # Return top 20
        return function_word_list[:20]

    def _analyze_style_markers(self, text: str) -> List[StyleMarker]:
        """Analyze style markers (casual/formal phrases)."""
        markers = []

        # Casual markers
        casual = [phrase for phrase in self.CASUAL_MARKERS if phrase in text]
        if casual:
            markers.append(StyleMarker(category="casual", phrases=casual[:10]))

        # Formal markers
        formal = [phrase for phrase in self.FORMAL_MARKERS if phrase in text]
        if formal:
            markers.append(StyleMarker(category="formal", phrases=formal[:10]))

        # Personal markers
        personal = [phrase for phrase in self.PERSONAL_MARKERS if phrase in text]
        if personal:
            markers.append(StyleMarker(category="personal", phrases=personal[:10]))

        # Technical markers
        technical = [phrase for phrase in self.TECHNICAL_MARKERS if phrase in text]
        if technical:
            markers.append(StyleMarker(category="technical", phrases=technical[:10]))

        return markers

    def _analyze_sentence_starters(self, sentences: List[str]) -> List[str]:
        """Analyze common sentence starters."""
        if not sentences:
            return []

        # Get first 1-2 words of each sentence
        starters = []
        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) >= 2:
                starter = f"{words[0]} {words[1]}"
                starters.append(starter.lower())
            elif len(words) == 1:
                starters.append(words[0].lower())

        # Count and return top 10 most common
        starter_counts = Counter(starters)
        top_starters = [s for s, _ in starter_counts.most_common(10)]

        return top_starters
