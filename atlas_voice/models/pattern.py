"""Voice pattern data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class FunctionWord:
    """Represents a function word and its frequency."""

    word: str
    frequency: float  # Percentage (e.g., 4.5 for 4.5%)


@dataclass
class StyleMarker:
    """Represents style markers (casual/formal phrases)."""

    category: str  # 'casual', 'formal', 'personal', 'technical'
    phrases: List[str]


@dataclass
class VoicePattern:
    """Complete voice pattern extracted from writing samples."""

    id: str
    name: str

    # Basic statistics
    total_words: int
    total_sentences: int
    avg_sentence_length: float
    vocab_richness: float  # unique words / total words
    avg_word_length: float

    # Linguistic patterns
    function_words: List[FunctionWord] = field(default_factory=list)
    style_markers: List[StyleMarker] = field(default_factory=list)
    sentence_starters: List[str] = field(default_factory=list)

    # Metadata
    source_description: str = ""  # e.g., "10,000 professional emails, 2020-2024"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "total_words": self.total_words,
            "total_sentences": self.total_sentences,
            "avg_sentence_length": self.avg_sentence_length,
            "vocab_richness": self.vocab_richness,
            "avg_word_length": self.avg_word_length,
            "function_words": [
                {"word": fw.word, "frequency": fw.frequency}
                for fw in self.function_words
            ],
            "style_markers": [
                {"category": sm.category, "phrases": sm.phrases}
                for sm in self.style_markers
            ],
            "sentence_starters": self.sentence_starters,
            "source_description": self.source_description,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VoicePattern":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            total_words=data["total_words"],
            total_sentences=data["total_sentences"],
            avg_sentence_length=data["avg_sentence_length"],
            vocab_richness=data["vocab_richness"],
            avg_word_length=data["avg_word_length"],
            function_words=[
                FunctionWord(word=fw["word"], frequency=fw["frequency"])
                for fw in data.get("function_words", [])
            ],
            style_markers=[
                StyleMarker(category=sm["category"], phrases=sm["phrases"])
                for sm in data.get("style_markers", [])
            ],
            sentence_starters=data.get("sentence_starters", []),
            source_description=data.get("source_description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
