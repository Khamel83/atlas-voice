"""SQLite database for pattern and prompt storage."""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from atlas_voice.models import VoicePattern, VoicePrompt


class Database:
    """SQLite database for voice patterns and prompts."""

    def __init__(self, db_path: str = "data/atlas_voice.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Voice patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_patterns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                total_words INTEGER NOT NULL,
                total_sentences INTEGER NOT NULL,
                avg_sentence_length REAL NOT NULL,
                vocab_richness REAL NOT NULL,
                avg_word_length REAL NOT NULL,
                function_words TEXT,  -- JSON
                style_markers TEXT,   -- JSON
                sentence_starters TEXT,  -- JSON
                source_description TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Voice prompts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_prompts (
                id TEXT PRIMARY KEY,
                pattern_id TEXT NOT NULL,
                name TEXT NOT NULL,
                context TEXT NOT NULL,
                prompt_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (pattern_id) REFERENCES voice_patterns (id)
            )
        """)

        self.conn.commit()

    def save_pattern(self, pattern: VoicePattern) -> None:
        """Save a voice pattern to the database."""
        cursor = self.conn.cursor()
        data = pattern.to_dict()

        cursor.execute("""
            INSERT OR REPLACE INTO voice_patterns
            (id, name, total_words, total_sentences, avg_sentence_length,
             vocab_richness, avg_word_length, function_words, style_markers,
             sentence_starters, source_description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id"],
            data["name"],
            data["total_words"],
            data["total_sentences"],
            data["avg_sentence_length"],
            data["vocab_richness"],
            data["avg_word_length"],
            json.dumps(data["function_words"]),
            json.dumps(data["style_markers"]),
            json.dumps(data["sentence_starters"]),
            data["source_description"],
            data["created_at"],
        ))

        self.conn.commit()

    def get_pattern(self, pattern_id: str) -> Optional[VoicePattern]:
        """Retrieve a voice pattern by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM voice_patterns WHERE id = ?", (pattern_id,))
        row = cursor.fetchone()

        if not row:
            return None

        data = dict(row)
        data["function_words"] = json.loads(data["function_words"])
        data["style_markers"] = json.loads(data["style_markers"])
        data["sentence_starters"] = json.loads(data["sentence_starters"])

        return VoicePattern.from_dict(data)

    def list_patterns(self) -> List[VoicePattern]:
        """List all voice patterns."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM voice_patterns ORDER BY created_at DESC
        """)

        patterns = []
        for row in cursor.fetchall():
            data = dict(row)
            data["function_words"] = json.loads(data["function_words"])
            data["style_markers"] = json.loads(data["style_markers"])
            data["sentence_starters"] = json.loads(data["sentence_starters"])
            patterns.append(VoicePattern.from_dict(data))

        return patterns

    def save_prompt(self, prompt: VoicePrompt) -> None:
        """Save a voice prompt to the database."""
        cursor = self.conn.cursor()
        data = prompt.to_dict()

        cursor.execute("""
            INSERT OR REPLACE INTO voice_prompts
            (id, pattern_id, name, context, prompt_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["id"],
            data["pattern_id"],
            data["name"],
            data["context"],
            data["prompt_text"],
            data["created_at"],
        ))

        self.conn.commit()

    def get_prompt(self, prompt_id: str) -> Optional[VoicePrompt]:
        """Retrieve a voice prompt by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM voice_prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return VoicePrompt.from_dict(dict(row))

    def list_prompts(self, pattern_id: Optional[str] = None) -> List[VoicePrompt]:
        """List all voice prompts, optionally filtered by pattern_id."""
        cursor = self.conn.cursor()

        if pattern_id:
            cursor.execute("""
                SELECT * FROM voice_prompts
                WHERE pattern_id = ?
                ORDER BY created_at DESC
            """, (pattern_id,))
        else:
            cursor.execute("""
                SELECT * FROM voice_prompts ORDER BY created_at DESC
            """)

        prompts = []
        for row in cursor.fetchall():
            prompts.append(VoicePrompt.from_dict(dict(row)))

        return prompts

    def delete_pattern(self, pattern_id: str) -> None:
        """Delete a pattern and all its prompts."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM voice_prompts WHERE pattern_id = ?", (pattern_id,))
        cursor.execute("DELETE FROM voice_patterns WHERE id = ?", (pattern_id,))
        self.conn.commit()

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
