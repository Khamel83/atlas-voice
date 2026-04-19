"""Voice prompt data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class VoicePrompt:
    """Generated AI system prompt based on voice patterns."""

    id: str
    pattern_id: str
    name: str
    context: str  # e.g., "professional", "casual", "creative"
    prompt_text: str
    created_at: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "pattern_id": self.pattern_id,
            "name": self.name,
            "context": self.context,
            "prompt_text": self.prompt_text,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VoicePrompt":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            pattern_id=data["pattern_id"],
            name=data["name"],
            context=data["context"],
            prompt_text=data["prompt_text"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )
