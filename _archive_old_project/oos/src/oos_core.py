#!/usr/bin/env python3
"""
OOS Core - Operational Intelligence System
Main middleware layer for Claude Code integration
"""

import os
import sys
import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class OOSConfig:
    """Configuration for OOS system"""
    db_path: str = "~/.oos/oos.db"
    max_context_size: int = 10000
    token_reduction_target: float = 0.5
    enable_mcp: bool = True
    enable_auto_optimize: bool = True
    log_level: str = "INFO"

@dataclass
class ContextEntry:
    """Context entry for development sessions"""
    id: str
    timestamp: float
    session_id: str
    context_type: str
    content: str
    metadata: Dict[str, Any]
    confidence_score: float = 0.0

class OOSCore:
    """Core OOS middleware system"""

    def __init__(self, config: OOSConfig):
        self.config = config
        self.db_path = Path(config.db_path).expanduser()
        self.session_id = self._generate_session_id()
        self.context_store = ContextStore(self.db_path)
        self.context_engine = ContextEngine(self.context_store)
        self.optimizer = TokenOptimizer()
        self.clarifier = MetaClarifier()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"oos_{int(time.time())}_{os.getpid()}"

    def initialize(self) -> bool:
        """Initialize OOS system"""
        console.print("[bold green]🚀 Initializing OOS...[/bold green]")

        # Create database and directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.context_store.initialize()

        # Load existing context
        self.context_engine.load_context()

        console.print(f"[green]✓ OOS initialized (Session: {self.session_id})[/green]")
        return True

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process Claude Code request through OOS middleware"""
        start_time = time.time()

        # Meta-clarification
        if self.config.enable_auto_optimize:
            request = self.clarifier.clarify_request(request)

        # Context optimization
        optimized_context = self.context_engine.optimize_context(request)

        # Token optimization
        if self.config.enable_auto_optimize:
            optimized_request = self.optimizer.optimize_tokens(optimized_context)
        else:
            optimized_request = optimized_context

        # Store context
        self.context_store.store_context(
            self.session_id,
            "request",
            optimized_request,
            {"original_size": len(json.dumps(request))}
        )

        processing_time = time.time() - start_time

        return {
            "optimized_request": optimized_request,
            "session_id": self.session_id,
            "processing_time": processing_time,
            "tokens_saved": self.optimizer.get_tokens_saved(),
            "context_confidence": self.context_engine.get_confidence_score()
        }

class ContextStore:
    """Efficient context storage and retrieval"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None

    def initialize(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS context_entries (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                session_id TEXT,
                context_type TEXT,
                content TEXT,
                metadata TEXT,
                confidence_score REAL
            )
        ''')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_session ON context_entries(session_id)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON context_entries(timestamp)')
        self.conn.commit()

    def store_context(self, session_id: str, context_type: str, content: Any, metadata: Dict[str, Any]):
        """Store context entry"""
        entry = ContextEntry(
            id=f"{session_id}_{int(time.time() * 1000)}",
            timestamp=time.time(),
            session_id=session_id,
            context_type=context_type,
            content=json.dumps(content),
            metadata=json.dumps(metadata),
            confidence_score=0.85
        )

        self.conn.execute('''
            INSERT INTO context_entries VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (entry.id, entry.timestamp, entry.session_id, entry.context_type,
              entry.content, entry.metadata, entry.confidence_score))
        self.conn.commit()

    def get_context(self, session_id: str, limit: int = 10) -> List[ContextEntry]:
        """Retrieve recent context for session"""
        cursor = self.conn.execute('''
            SELECT * FROM context_entries
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))

        entries = []
        for row in cursor.fetchall():
            entries.append(ContextEntry(*row))
        return entries

class ContextEngine:
    """Context management and optimization"""

    def __init__(self, context_store: ContextStore):
        self.context_store = context_store
        self.current_context = {}
        self.confidence_score = 0.0

    def load_context(self):
        """Load existing context"""
        # Initialize with empty context
        self.current_context = {
            "session_history": [],
            "file_patterns": [],
            "project_structure": {},
            "user_preferences": {}
        }

    def optimize_context(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize context for current request"""
        # Add relevant context to request
        optimized = request.copy()
        optimized["oos_context"] = {
            "session_id": self.current_context.get("session_id"),
            "file_patterns": self._get_relevant_files(request),
            "project_insights": self._get_project_insights()
        }

        self.confidence_score = min(0.95, self.confidence_score + 0.05)
        return optimized

    def _get_relevant_files(self, request: Dict[str, Any]) -> List[str]:
        """Get relevant file patterns based on request"""
        # Simple file pattern detection
        patterns = []
        if "file" in request.get("content", "").lower():
            patterns.extend(["*.py", "*.js", "*.ts", "*.json"])
        return patterns

    def _get_project_insights(self) -> Dict[str, Any]:
        """Get insights about current project"""
        return {
            "has_tests": False,  # TODO: Detect test files
            "has_docs": False,   # TODO: Detect documentation
            "project_type": "unknown"
        }

    def get_confidence_score(self) -> float:
        """Get current context confidence score"""
        return self.confidence_score

class TokenOptimizer:
    """Token optimization and compression"""

    def __init__(self):
        self.tokens_saved = 0
        self.compression_strategies = [
            self._remove_redundancy,
            self._compress_patterns,
            self._optimize_structure
        ]

    def optimize_tokens(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Apply token optimization strategies"""
        original_size = len(json.dumps(content))

        optimized = content.copy()
        for strategy in self.compression_strategies:
            optimized = strategy(optimized)

        optimized_size = len(json.dumps(optimized))
        self.tokens_saved += (original_size - optimized_size)

        return optimized

    def _remove_redundancy(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Remove redundant information"""
        # Remove empty fields
        return {k: v for k, v in content.items() if v is not None and v != ""}

    def _compress_patterns(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Compress repetitive patterns"""
        # TODO: Implement pattern compression
        return content

    def _optimize_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize data structure"""
        # TODO: Implement structure optimization
        return content

    def get_tokens_saved(self) -> int:
        """Get total tokens saved"""
        return self.tokens_saved

class MetaClarifier:
    """Meta-clarification system for better understanding"""

    def clarify_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply meta-clarification to request"""
        clarified = request.copy()

        # Add clarification metadata
        clarified["oos_metadata"] = {
            "clarification_applied": True,
            "intent_detected": self._detect_intent(request),
            "complexity_score": self._assess_complexity(request),
            "optimization_suggestions": self._suggest_optimizations(request)
        }

        return clarified

    def _detect_intent(self, request: Dict[str, Any]) -> str:
        """Detect user intent from request"""
        content = request.get("content", "").lower()

        if any(word in content for word in ["create", "make", "build"]):
            return "creation"
        elif any(word in content for word in ["fix", "debug", "error"]):
            return "debugging"
        elif any(word in content for word in ["optimize", "improve", "refactor"]):
            return "optimization"
        else:
            return "general"

    def _assess_complexity(self, request: Dict[str, Any]) -> float:
        """Assess request complexity"""
        content = request.get("content", "")
        # Simple complexity assessment based on length and keywords
        complexity = min(1.0, len(content) / 1000)
        return complexity

    def _suggest_optimizations(self, request: Dict[str, Any]) -> List[str]:
        """Suggest optimizations for the request"""
        suggestions = []
        content = request.get("content", "")

        if len(content) > 500:
            suggestions.append("Consider breaking down into smaller tasks")

        if "file" in content.lower():
            suggestions.append("Specify file paths for better context")

        return suggestions

@click.command()
@click.option('--config', '-c', default='~/.oos/config.json', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(config: str, verbose: bool):
    """Main OOS CLI entry point"""
    console.print("[bold blue]🧠 OOS - Operational Intelligence System[/bold blue]")

    # Load configuration
    config_path = Path(config).expanduser()
    if config_path.exists():
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        oos_config = OOSConfig(**config_data)
    else:
        oos_config = OOSConfig()

    # Initialize OOS
    oos = OOSCore(oos_config)
    oos.initialize()

    console.print("[green]✓ OOS middleware ready[/green]")

if __name__ == "__main__":
    main()
