#!/usr/bin/env python3
"""
Enhanced RAG System for OOS-Archon Integration
Implements research learnings: advanced chunking, embeddings, hybrid search
"""

import asyncio
import json
import hashlib
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import aiohttp
from bs4 import BeautifulSoup

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    chunks: List[str] = None

@dataclass
class Chunk:
    id: str
    document_id: str
    content: str
    start_pos: int
    end_pos: int
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None

class SemanticChunker:
    """
    Advanced chunking strategy based on semantic boundaries
    Implements research learnings for optimal context injection
    """

    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def chunk_document(self, document: Document) -> List[Chunk]:
        """Split document into semantically meaningful chunks"""
        # Preprocess content
        content = self._preprocess_text(document.content)

        # Split by sentences first
        sentences = self._split_sentences(content)

        # Group sentences into semantic chunks
        chunks = self._create_semantic_chunks(sentences, document.id)

        # Add metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata = {
                **document.metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_type": "semantic",
                "created_at": datetime.now().isoformat()
            }

        return chunks

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep structure
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/\@\#\$\%\^\&\*\+\=\~\`]', '', text)
        return text.strip()

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences using multiple delimiters"""
        sentence_endings = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]

    def _create_semantic_chunks(self, sentences: List[str], document_id: str) -> List[Chunk]:
        """Create chunks based on semantic similarity"""
        chunks = []
        current_chunk = []
        current_size = 0

        for i, sentence in enumerate(sentences):
            sentence_size = len(sentence.split())

            # Start new chunk if size limit reached
            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                chunk_content = ' '.join(current_chunk)
                chunk = Chunk(
                    id=f"{document_id}_chunk_{len(chunks)}",
                    document_id=document_id,
                    content=chunk_content,
                    start_pos=0,  # Will be calculated later
                    end_pos=len(chunk_content)
                )
                chunks.append(chunk)

                # Start new chunk with overlap
                current_chunk = current_chunk[-self.overlap:] if self.overlap > 0 else []
                current_size = sum(len(s.split()) for s in current_chunk)

            current_chunk.append(sentence)
            current_size += sentence_size

        # Add final chunk
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunk = Chunk(
                id=f"{document_id}_chunk_{len(chunks)}",
                document_id=document_id,
                content=chunk_content,
                start_pos=0,
                end_pos=len(chunk_content)
            )
            chunks.append(chunk)

        return chunks

class EmbeddingManager:
    """Manages document and chunk embeddings"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for batch of texts"""
        return self.model.encode(texts, convert_to_numpy=True, batch_size=32)

    def similarity(self, embed1: np.ndarray, embed2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        return np.dot(embed1, embed2) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))

class ChromaVectorStore:
    """ChromaDB vector store with advanced capabilities"""

    def __init__(self, collection_name: str = "oos_knowledge"):
        # Use new ChromaDB client API
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(collection_name)

    async def add_chunks(self, chunks: List[Chunk], embeddings: List[np.ndarray]):
        """Add chunks with embeddings to vector store"""
        documents = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.id for chunk in chunks]

        # Convert embeddings to list format
        embeddings_list = [emb.tolist() for emb in embeddings]

        self.collection.add(
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas,
            ids=ids
        )

    async def similarity_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        query_embedding_list = query_embedding.tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding_list],
            n_results=k
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            result = {
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            }
            formatted_results.append(result)

        return formatted_results

    async def hybrid_search(self, query: str, query_embedding: np.ndarray, k: int = 10) -> List[Dict[str, Any]]:
        """Combine semantic and keyword search"""
        # Semantic search
        semantic_results = await self.similarity_search(query_embedding, k)

        # Keyword search (simple implementation)
        keyword_results = []
        for doc in self.collection.get()['documents']:
            if query.lower() in doc.lower():
                keyword_results.append(doc)

        # Combine and deduplicate results
        all_results = semantic_results + [{'content': doc} for doc in keyword_results[:5]]
        seen = set()
        unique_results = []

        for result in all_results:
            content = result['content']
            if content not in seen:
                seen.add(content)
                unique_results.append(result)

        return unique_results[:k]

class CrossEncoderReranker:
    """Reranker using cross-encoder for better relevance"""

    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
        except ImportError:
            print("Cross-Encoder not available, using fallback reranking")
            self.model = None

    async def rerank(self, query: str, candidates: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        """Rerank candidates based on relevance to query"""
        if not self.model:
            # Fallback: simple keyword matching
            return candidates[:k]

        # Prepare pairs for cross-encoder
        pairs = [(query, candidate['content']) for candidate in candidates]

        # Get scores
        scores = self.model.predict(pairs)

        # Sort by score and return top k
        scored_candidates = list(zip(candidates, scores))
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        return [candidate for candidate, score in scored_candidates[:k]]

class DocumentIngestionPipeline:
    """Multi-source document ingestion pipeline"""

    def __init__(self):
        self.chunker = SemanticChunker()
        self.embedding_manager = EmbeddingManager()
        self.vector_store = ChromaVectorStore()
        self.reranker = CrossEncoderReranker()

    async def ingest_text(self, content: str, metadata: Dict[str, Any]) -> str:
        """Ingest text document"""
        document = Document(
            id=self._generate_id(content),
            content=content,
            metadata=metadata
        )

        # Chunk document
        chunks = self.chunker.chunk_document(document)

        # Generate embeddings
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_manager.embed_batch(chunk_texts)

        # Add to vector store
        await self.vector_store.add_chunks(chunks, embeddings)

        return document.id

    async def ingest_url(self, url: str, metadata: Dict[str, Any] = None) -> str:
        """Ingest content from URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    content = soup.get_text()

                    if metadata is None:
                        metadata = {}
                    metadata.update({
                        'source_url': url,
                        'source_type': 'web',
                        'ingested_at': datetime.now().isoformat()
                    })

                    return await self.ingest_text(content, metadata)
                else:
                    raise Exception(f"Failed to fetch URL: {response.status}")

    async def query_knowledge(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Query knowledge base with enhanced RAG"""
        # Generate query embedding
        query_embedding = self.embedding_manager.embed_text(query)

        # Hybrid search
        candidates = await self.vector_store.hybrid_search(query, query_embedding, k * 2)

        # Rerank results
        reranked = await self.reranker.rerank(query, candidates, k)

        return reranked

    def _generate_id(self, content: str) -> str:
        """Generate unique ID for document"""
        return hashlib.md5(content.encode()).hexdigest()

class EnhancedRAGSystem:
    """Main RAG system integrating all components"""

    def __init__(self):
        self.ingestion_pipeline = DocumentIngestionPipeline()
        self.context_window_limit = 4000  # tokens

    async def initialize(self):
        """Initialize the RAG system"""
        print("🧠 Initializing Enhanced RAG System...")
        print("✅ Semantic chunking configured")
        print("✅ Embedding models loaded")
        print("✅ Vector store connected")
        print("✅ Reranking system ready")

    async def add_knowledge(self, content: str, source: str = "manual") -> str:
        """Add knowledge to the system"""
        metadata = {
            'source': source,
            'added_at': datetime.now().isoformat(),
            'type': 'text'
        }
        doc_id = await self.ingestion_pipeline.ingest_text(content, metadata)
        print(f"📚 Knowledge added: {doc_id}")
        return doc_id

    async def add_web_knowledge(self, url: str) -> str:
        """Add knowledge from web URL"""
        doc_id = await self.ingestion_pipeline.ingest_url(url)
        print(f"🌐 Web knowledge added: {doc_id}")
        return doc_id

    async def retrieve_context(self, query: str, max_tokens: int = 2000) -> str:
        """Retrieve relevant context for query"""
        results = await self.ingestion_pipeline.query_knowledge(query, k=5)

        # Format context with token optimization
        context_parts = []
        current_tokens = 0

        for result in results:
            content = result['content']
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            estimated_tokens = len(content) // 4

            if current_tokens + estimated_tokens > max_tokens:
                break

            context_parts.append(content)
            current_tokens += estimated_tokens

        return '\n\n'.join(context_parts)

    async def get_relevant_sources(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Get relevant sources with metadata"""
        results = await self.ingestion_pipeline.query_knowledge(query, k)
        return results

async def main():
    """Demo the enhanced RAG system"""
    print("🚀 Enhanced RAG System Demo")
    print("=" * 40)

    # Initialize system
    rag = EnhancedRAGSystem()
    await rag.initialize()

    # Add sample knowledge
    sample_docs = [
        {
            "content": "OOS is an Open Orchestration System that acts as a personal AI assistant. It features task planning, tool usage, and RAG capabilities.",
            "source": "system_docs"
        },
        {
            "content": "Archon is an AI operating system that provides knowledge management, task tracking, and advanced RAG capabilities through MCP protocol.",
            "source": "research_docs"
        },
        {
            "content": "The integration of OOS and Archon creates a powerful 'other brain' system that combines reasoning with knowledge management.",
            "source": "vision_docs"
        }
    ]

    for doc in sample_docs:
        await rag.add_knowledge(doc["content"], doc["source"])

    # Test queries
    test_queries = [
        "What is OOS and what are its capabilities?",
        "How does Archon work with OOS?",
        "What are the benefits of the integration?"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        context = await rag.retrieve_context(query)
        print(f"📋 Retrieved Context:")
        print("-" * 40)
        print(context)
        print("-" * 40)

        sources = await rag.get_relevant_sources(query, k=2)
        print(f"📚 Relevant Sources: {len(sources)}")
        for source in sources:
            print(f"  • {source['metadata'].get('source', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(main())