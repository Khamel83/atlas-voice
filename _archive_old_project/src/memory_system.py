#!/usr/bin/env python3
"""
Long-Term Memory and Context Management System
Implements research learnings: multi-level memory, summarization, external storage
"""

import asyncio
import json
import hashlib
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from collections import defaultdict, deque
import aiofiles
import asyncio

@dataclass
class Memory:
    id: str
    content: str
    memory_type: str  # "working", "short_term", "long_term", "user_preference"
    importance_score: float
    access_count: int
    created_at: datetime
    last_accessed: datetime
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

@dataclass
class Interaction:
    id: str
    user_input: str
    system_response: str
    context_used: List[str]
    timestamp: datetime
    session_id: str
    metadata: Dict[str, Any]

class ImportanceScorer:
    """Scores memory importance based on various factors"""

    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def calculate_importance(self, content: str, context: Dict[str, Any]) -> float:
        """Calculate importance score for memory content"""
        score = 0.0

        # Length factor (longer content might be more important)
        length_score = min(len(content.split()) / 100, 1.0) * 0.2
        score += length_score

        # User feedback factor
        if context.get('user_satisfaction'):
            satisfaction_score = context['user_satisfaction'] * 0.3
            score += satisfaction_score

        # Recency factor (newer interactions might be more important)
        recency_score = 0.1
        score += recency_score

        # Keyword importance (technical terms, questions, etc.)
        keywords = ['important', 'critical', 'remember', 'key', 'essential', 'must', 'should']
        keyword_score = sum(1 for keyword in keywords if keyword.lower() in content.lower()) * 0.05
        score += min(keyword_score, 0.2)

        # Question/Answer pattern
        if '?' in content or any(word in content.lower() for word in ['answer', 'solution', 'fix']):
            score += 0.15

        # Code or technical content
        if any(marker in content for marker in ['```', 'def ', 'class ', 'import ', 'function']):
            score += 0.1

        return min(score, 1.0)

class MemorySummarizer:
    """Summarizes and compresses memory content"""

    def __init__(self):
        # Simple summarization - in production, use a proper summarization model
        self.max_summary_length = 200

    def summarize_interactions(self, interactions: List[Interaction]) -> str:
        """Summarize a list of interactions"""
        if not interactions:
            return ""

        # Extract key information
        topics = []
        actions = []
        key_points = []

        for interaction in interactions:
            # Simple topic extraction
            if '?' in interaction.user_input:
                topics.append(f"Q: {interaction.user_input}")
            if '```' in interaction.system_response:
                actions.append("Code solution provided")
            if any(word in interaction.system_response.lower() for word in ['important', 'remember', 'note']):
                key_points.append(interaction.system_response)

        # Create summary
        summary_parts = []
        if topics:
            summary_parts.append(f"Discussed: {', '.join(topics[:3])}")
        if actions:
            summary_parts.append(f"Actions: {', '.join(actions)}")
        if key_points:
            summary_parts.append(f"Key points: {'; '.join(key_points[:2])}")

        return " | ".join(summary_parts) if summary_parts else "General conversation"

    def compress_memory(self, memory: Memory, target_length: int = 100) -> str:
        """Compress memory content to target length"""
        words = memory.content.split()
        if len(words) <= target_length:
            return memory.content

        # Simple truncation with preservation of key points
        compressed = ' '.join(words[:target_length])
        if len(words) > target_length:
            compressed += "..."

        return compressed

class MultiLevelMemorySystem:
    """
    Multi-level memory system implementing research learnings:
    - Working memory (current session)
    - Short-term memory (recent interactions)
    - Long-term memory (archived knowledge)
    - User preferences (persistent settings)
    """

    def __init__(self, working_memory_limit: int = 10, short_term_limit: int = 100):
        self.working_memory_limit = working_memory_limit
        self.short_term_limit = short_term_limit

        # Memory stores
        self.working_memory = deque(maxlen=working_memory_limit)
        self.short_term_memory = deque(maxlen=short_term_limit)
        self.long_term_memory = []  # Will use ChromaDB for efficient retrieval
        self.user_preferences = {}

        # Supporting components
        self.importance_scorer = ImportanceScorer()
        self.summarizer = MemorySummarizer()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # ChromaDB for long-term memory
        self.chroma_client = chromadb.PersistentClient(path="./memory_db")
        self.memory_collection = self.chroma_client.get_or_create_collection("long_term_memory")

        # Memory decay settings
        self.decay_threshold = 0.3  # Minimum importance to keep in memory
        self.access_decay_rate = 0.95  # Decay factor for importance over time

    async def store_interaction(self, interaction: Interaction, context: Dict[str, Any] = None):
        """Store a new interaction in the memory system"""
        # Add to working memory
        self.working_memory.append(interaction)

        # Calculate importance
        importance = self.importance_scorer.calculate_importance(
            f"{interaction.user_input} {interaction.system_response}",
            context or {}
        )

        # Create memory object
        memory = Memory(
            id=self._generate_memory_id(interaction.id),
            content=f"User: {interaction.user_input}\nSystem: {interaction.system_response}",
            memory_type="short_term",
            importance_score=importance,
            access_count=1,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            metadata={
                **interaction.metadata,
                "interaction_id": interaction.id,
                "session_id": interaction.session_id,
                "context_used": interaction.context_used
            }
        )

        # Add to short-term memory
        self.short_term_memory.append(memory)

        # Check if we need to archive to long-term memory
        if len(self.short_term_memory) >= self.short_term_limit * 0.8:
            await self._archive_to_long_term()

        # Update working memory summary if needed
        if len(self.working_memory) >= self.working_memory_limit * 0.8:
            await self._summarize_working_memory()

    async def _archive_to_long_term(self):
        """Archive important memories from short-term to long-term"""
        memories_to_archive = []

        # Select memories to archive based on importance
        for memory in self.short_term_memory:
            if memory.importance_score > self.decay_threshold:
                memories_to_archive.append(memory)

        # Sort by importance and archive top memories
        memories_to_archive.sort(key=lambda x: x.importance_score, reverse=True)
        archive_count = max(1, len(self.short_term_memory) // 2)  # Archive half

        for memory in memories_to_archive[:archive_count]:
            # Generate embedding
            embedding = self.embedding_model.encode(memory.content, convert_to_numpy=True)

            # Store in ChromaDB
            self.memory_collection.add(
                documents=[memory.content],
                embeddings=[embedding.tolist()],
                metadatas=[{
                    **memory.metadata,
                    "memory_type": "long_term",
                    "importance_score": memory.importance_score,
                    "access_count": memory.access_count,
                    "created_at": memory.created_at.isoformat(),
                    "last_accessed": memory.last_accessed.isoformat()
                }],
                ids=[memory.id]
            )

            # Remove from short-term memory
            self.short_term_memory = deque(
                [m for m in self.short_term_memory if m.id != memory.id],
                maxlen=self.short_term_limit
            )

        print(f"📦 Archived {len(memories_to_archive[:archive_count])} memories to long-term storage")

    async def _summarize_working_memory(self):
        """Summarize working memory to prevent overflow"""
        if len(self.working_memory) < self.working_memory_limit:
            return

        # Take oldest interactions and summarize them
        interactions_to_summarize = list(self.working_memory)[:self.working_memory_limit // 2]
        summary = self.summarizer.summarize_interactions(interactions_to_summarize)

        # Create summary memory
        summary_memory = Memory(
            id=self._generate_memory_id(f"summary_{time.time()}"),
            content=f"Summary: {summary}",
            memory_type="working",
            importance_score=0.5,  # Moderate importance for summaries
            access_count=1,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            metadata={
                "type": "summary",
                "summarized_interactions": [i.id for i in interactions_to_summarize],
                "original_count": len(interactions_to_summarize)
            }
        )

        # Remove summarized interactions and add summary
        self.working_memory = deque(
            list(self.working_memory)[self.working_memory_limit // 2:],
            maxlen=self.working_memory_limit
        )
        self.working_memory.append(summary_memory)

    async def retrieve_relevant_context(self, query: str, max_tokens: int = 2000) -> List[str]:
        """Retrieve relevant context from all memory levels"""
        context_parts = []
        current_tokens = 0

        # 1. Check working memory (most recent)
        working_context = await self._retrieve_from_working_memory(query)
        if working_context:
            context_parts.append("Recent Context:")
            context_parts.extend(working_context)
            current_tokens += self._estimate_tokens('\n'.join(working_context))

        # 2. Search short-term memory
        short_term_context = await self._retrieve_from_short_term_memory(query)
        if short_term_context and current_tokens < max_tokens * 0.7:
            context_parts.append("Short-term Memory:")
            context_parts.extend(short_term_context)
            current_tokens += self._estimate_tokens('\n'.join(short_term_context))

        # 3. Search long-term memory
        if current_tokens < max_tokens * 0.5:
            long_term_context = await self._retrieve_from_long_term_memory(query)
            if long_term_context:
                context_parts.append("Long-term Memory:")
                context_parts.extend(long_term_context)

        # 4. Add user preferences if relevant
        preferences = await self._get_relevant_preferences(query)
        if preferences:
            context_parts.append("User Preferences:")
            context_parts.extend(preferences)

        return context_parts

    async def _retrieve_from_working_memory(self, query: str) -> List[str]:
        """Retrieve from working memory"""
        relevant_memories = []
        query_lower = query.lower()

        for interaction in self.working_memory:
            # Simple keyword matching for working memory
            if any(keyword in interaction.user_input.lower() for keyword in query_lower.split()):
                relevant_memories.append(f"User: {interaction.user_input}")
                relevant_memories.append(f"System: {interaction.system_response}")

        return relevant_memories[-5:]  # Return last 5 relevant interactions

    async def _retrieve_from_short_term_memory(self, query: str) -> List[str]:
        """Retrieve from short-term memory using semantic search"""
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)

        relevant_memories = []
        for memory in self.short_term_memory:
            if memory.embedding is None:
                memory.embedding = self.embedding_model.encode(memory.content, convert_to_numpy=True)

            # Calculate similarity
            similarity = np.dot(query_embedding, memory.embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(memory.embedding)
            )

            if similarity > 0.3:  # Similarity threshold
                memory.access_count += 1
                memory.last_accessed = datetime.now()
                relevant_memories.append((memory.content, similarity))

        # Sort by similarity and return top results
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        return [content for content, _ in relevant_memories[:3]]

    async def _retrieve_from_long_term_memory(self, query: str) -> List[str]:
        """Retrieve from long-term memory using ChromaDB"""
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)

        results = self.memory_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=3
        )

        retrieved = []
        if results['documents']:
            for doc in results['documents'][0]:
                retrieved.append(doc)

        return retrieved

    async def _get_relevant_preferences(self, query: str) -> List[str]:
        """Get relevant user preferences"""
        relevant = []

        # Simple keyword matching for preferences
        query_lower = query.lower()
        for key, value in self.user_preferences.items():
            if key.lower() in query_lower or any(word in query_lower for word in key.lower().split()):
                relevant.append(f"{key}: {value}")

        return relevant

    async def store_user_preference(self, key: str, value: Any, source: str = "user"):
        """Store user preference"""
        self.user_preferences[key] = {
            "value": value,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        print(f"💾 Stored preference: {key} = {value}")

    async def get_user_preference(self, key: str) -> Optional[Any]:
        """Get user preference"""
        preference = self.user_preferences.get(key)
        if preference:
            # Update last accessed
            preference["last_updated"] = datetime.now().isoformat()
            return preference["value"]
        return None

    async def decay_memories(self):
        """Apply importance decay to memories"""
        current_time = datetime.now()

        # Decay short-term memory importance
        for memory in self.short_term_memory:
            time_since_access = (current_time - memory.last_accessed).total_seconds()
            decay_factor = self.access_decay_rate ** (time_since_access / 3600)  # Hourly decay
            memory.importance_score *= decay_factor

        # Remove low-importance memories from short-term
        self.short_term_memory = deque(
            [m for m in self.short_term_memory if m.importance_score > self.decay_threshold],
            maxlen=self.short_term_limit
        )

    def _generate_memory_id(self, content: str) -> str:
        """Generate unique ID for memory"""
        return hashlib.md5(f"{content}_{time.time()}".encode()).hexdigest()

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text.split()) // 4  # Rough estimate: 1 token ≈ 4 characters

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            "working_memory_count": len(self.working_memory),
            "short_term_memory_count": len(self.short_term_memory),
            "long_term_memory_count": self.memory_collection.count(),
            "user_preferences_count": len(self.user_preferences),
            "average_importance": np.mean([m.importance_score for m in self.short_term_memory]) if self.short_term_memory else 0,
            "memory_types": {
                "working": len(self.working_memory),
                "short_term": len(self.short_term_memory),
                "long_term": self.memory_collection.count(),
                "preferences": len(self.user_preferences)
            }
        }

class ContextOptimizer:
    """Optimizes context window usage for token efficiency"""

    def __init__(self, memory_system: MultiLevelMemorySystem):
        self.memory_system = memory_system
        self.max_context_tokens = 4000  # Target context window

    async def get_optimized_context(self, query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Get optimized context for query"""
        context_parts = []

        # 1. Add recent conversation history (most recent first)
        if conversation_history:
            recent_history = conversation_history[-5:]  # Last 5 exchanges
            history_text = self._format_conversation_history(recent_history)
            if history_text:
                context_parts.append("Recent Conversation:")
                context_parts.append(history_text)

        # 2. Retrieve relevant memories
        memory_context = await self.memory_system.retrieve_relevant_context(
            query, max_tokens=self.max_context_tokens // 2
        )

        if memory_context:
            context_parts.append("Relevant Memory Context:")
            context_parts.extend(memory_context)

        # 3. Combine and optimize
        full_context = '\n'.join(context_parts)

        # Ensure we don't exceed token limit
        if self._estimate_tokens(full_context) > self.max_context_tokens:
            full_context = self._truncate_context(full_context, self.max_context_tokens)

        return full_context

    def _format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for context"""
        formatted = []
        for exchange in history:
            if 'user' in exchange:
                formatted.append(f"User: {exchange['user']}")
            if 'assistant' in exchange:
                formatted.append(f"Assistant: {exchange['assistant']}")
        return '\n'.join(formatted)

    def _truncate_context(self, context: str, max_tokens: int) -> str:
        """Truncate context to fit token limit"""
        words = context.split()
        target_words = max_tokens * 4  # Rough word count
        if len(words) <= target_words:
            return context

        truncated = ' '.join(words[:target_words])
        return truncated + "\n[Context truncated to fit token limit]"

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text.split())

async def main():
    """Demo the memory system"""
    print("🧠 Multi-Level Memory System Demo")
    print("=" * 40)

    # Initialize memory system
    memory_system = MultiLevelMemorySystem()
    context_optimizer = ContextOptimizer(memory_system)

    # Simulate some interactions
    interactions = [
        Interaction(
            id="1",
            user_input="What is OOS?",
            system_response="OOS is an Open Orchestration System that acts as a personal AI assistant.",
            context_used=[],
            timestamp=datetime.now(),
            session_id="session_1",
            metadata={"topic": "system_info"}
        ),
        Interaction(
            id="2",
            user_input="How does it work with Archon?",
            system_response="OOS integrates with Archon through MCP protocol for knowledge management and task tracking.",
            context_used=[],
            timestamp=datetime.now(),
            session_id="session_1",
            metadata={"topic": "integration"}
        ),
        Interaction(
            id="3",
            user_input="Remember that I prefer detailed technical explanations",
            system_response="I'll remember that you prefer detailed technical explanations in our future interactions.",
            context_used=[],
            timestamp=datetime.now(),
            session_id="session_1",
            metadata={"preference": True}
        )
    ]

    # Store interactions
    for interaction in interactions:
        await memory_system.store_interaction(interaction)

    # Store user preference
    await memory_system.store_user_preference(
        "explanation_style", "detailed_technical", "user_explicit"
    )

    # Test memory retrieval
    print("\n🔍 Testing Memory Retrieval:")
    query = "How does OOS work with Archon?"
    context = await context_optimizer.get_optimized_context(query)

    print("Retrieved Context:")
    print("-" * 40)
    print(context)
    print("-" * 40)

    # Show memory stats
    stats = await memory_system.get_memory_stats()
    print(f"\n📊 Memory System Stats:")
    print(f"Working Memory: {stats['working_memory_count']}")
    print(f"Short-term Memory: {stats['short_term_memory_count']}")
    print(f"Long-term Memory: {stats['long_term_memory_count']}")
    print(f"User Preferences: {stats['user_preferences_count']}")

    # Test preference retrieval
    explanation_style = await memory_system.get_user_preference("explanation_style")
    print(f"\n👤 Retrieved Preference: explanation_style = {explanation_style}")

    print("\n✅ Memory System Demo Complete")

if __name__ == "__main__":
    asyncio.run(main())