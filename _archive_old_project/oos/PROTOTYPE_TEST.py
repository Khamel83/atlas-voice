#!/usr/bin/env python3
"""
PROTOTYPE TEST: Content Analysis System
Tests embeddings and topic clustering approach on Omar's corpus
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans, HDBSCAN
from sklearn.metrics import silhouette_score
# import matplotlib.pyplot as plt  # Not needed for basic testing
from pathlib import Path
import re
import json
from typing import List, Dict, Tuple

class ContentAnalysisPrototype:
    """Prototype for testing content analysis approach"""

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.email_path = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"
        self.text_files = [
            '/Users/khamel83/dev/atlas-voice/data/omars_personal_letters.txt',
            '/Users/khamel83/dev/atlas-voice/data/speech.md'
        ]

    def test_content_analysis(self) -> Dict:
        """Run prototype test of content analysis pipeline"""
        print("🧪 PROTOTYPE TEST: Content Analysis System")
        print("=" * 60)

        results = {
            'embeddings_test': self.test_embeddings(),
            'clustering_test': self.test_topic_clustering(),
            'vocabulary_extraction': self.test_vocabulary_extraction(),
            'performance_metrics': self.measure_performance()
        }

        return results

    def test_embeddings(self) -> Dict:
        """Test embedding generation on sample content"""
        print("🔍 Testing embedding generation...")

        # Get sample content from emails
        sample_emails = self._get_sample_emails(50)  # 50 emails for testing
        print(f"   Loaded {len(sample_emails)} sample emails")

        # Generate embeddings
        texts = [email['content'] for email in sample_emails if email['content']]
        embeddings = self.model.encode(texts[:20])  # Test with first 20
        print(f"   Generated embeddings: {embeddings.shape}")
        print(f"   Embedding dimension: {embeddings.shape[1]}")

        return {
            'sample_count': len(texts[:20]),
            'embedding_shape': embeddings.shape,
            'test_passed': embeddings.shape[1] == 384  # Expected dimension
        }

    def test_topic_clustering(self) -> Dict:
        """Test topic clustering approach"""
        print("🔍 Testing topic clustering...")

        # Get sample content
        sample_emails = self._get_sample_emails(100)
        texts = [email['content'] for email in sample_emails if len(email['content']) > 50][:50]

        # Generate embeddings
        embeddings = self.model.encode(texts)

        # Test K-means clustering
        kmeans = KMeans(n_clusters=5, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)

        # Calculate silhouette score
        score = silhouette_score(embeddings, cluster_labels)
        print(f"   K-means (5 clusters): silhouette score = {score:.3f}")

        # Test HDBSCAN
        hdbscan = HDBSCAN(min_cluster_size=3, min_samples=2)
        hdbscan_labels = hdbscan.fit_predict(embeddings)
        n_clusters = len(set(hdbscan_labels)) - (1 if -1 in hdbscan_labels else 0)
        print(f"   HDBSCAN: found {n_clusters} clusters")

        # Sample topics from each cluster
        topics = self._extract_topic_samples(texts, cluster_labels, 5)

        return {
            'kmeans_score': score,
            'hdbscan_clusters': n_clusters,
            'sample_topics': topics,
            'test_passed': score > 0.1  # Minimum acceptable score
        }

    def test_vocabulary_extraction(self) -> Dict:
        """Test vocabulary and knowledge extraction"""
        print("🔍 Testing vocabulary extraction...")

        # Get sample content
        sample_emails = self._get_sample_emails(100)
        all_text = ' '.join([email['content'] for email in sample_emails if email['content']])

        # Extract key vocabulary
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        print(f"   Top vocabulary: {[w for w, c in top_words[:10]]}")

        # Extract technical terms
        tech_terms = self._extract_technical_terms(all_text)
        print(f"   Technical terms found: {len(tech_terms)}")
        print(f"   Sample tech terms: {tech_terms[:5]}")

        return {
            'vocabulary_size': len(word_freq),
            'top_words': top_words[:20],
            'technical_terms': tech_terms[:10],
            'test_passed': len(tech_terms) > 0
        }

    def measure_performance(self) -> Dict:
        """Measure processing performance"""
        print("🔍 Measuring performance...")

        import time
        start_time = time.time()

        # Test with sample data
        sample_emails = self._get_sample_emails(50)
        texts = [email['content'] for email in sample_emails if email['content']][:30]

        # Measure embedding time
        embed_start = time.time()
        embeddings = self.model.encode(texts)
        embed_time = time.time() - embed_start

        # Measure clustering time
        cluster_start = time.time()
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(embeddings)
        cluster_time = time.time() - cluster_start

        total_time = time.time() - start_time

        # Project to full corpus scale
        full_scale_emails = 80927  # Your full email count
        projected_time = (total_time / 30) * full_scale_emails

        return {
            'sample_size': len(texts),
            'embedding_time': embed_time,
            'clustering_time': cluster_time,
            'total_time': total_time,
            'projected_full_corpus_time': projected_time,
            'test_passed': projected_time < 1800  # Under 30 minutes for full corpus
        }

    def _get_sample_emails(self, n: int = 50) -> List[Dict]:
        """Get sample emails for testing"""
        try:
            # Read first chunk for testing
            chunk = pd.read_csv(self.email_path, nrows=n*2)
            emails = chunk[chunk['content'].notna() & (chunk['content'].str.len() > 50)]
            return emails.head(n).to_dict('records')
        except Exception as e:
            print(f"   Error loading emails: {e}")
            return []

    def _extract_topic_samples(self, texts: List[str], labels: np.ndarray, n_clusters: int) -> Dict:
        """Extract sample content for each cluster"""
        topics = {}
        for i in range(n_clusters):
            cluster_texts = [texts[j] for j in range(len(labels)) if labels[j] == i]
            if cluster_texts:
                topics[f'cluster_{i}'] = cluster_texts[:2]  # Top 2 samples per cluster
        return topics

    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text"""
        # Simple technical term extraction (can be enhanced)
        tech_patterns = [
            r'\b\w+\.?\w*\.(com|org|net|io|ai)\b',  # Tech companies
            r'\b\w+\.(js|py|java|cpp|html|css|sql)\b',  # File extensions
            r'\b(excel|python|sql|api|database|server|cloud|app|web)\b',  # Tech terms
            r'\b\w+\s+(project|system|platform|app|tool)\b'  # Tech concepts
        ]

        tech_terms = set()
        for pattern in tech_patterns:
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            tech_terms.update(matches)

        return list(tech_terms)

    def save_results(self, results: Dict):
        """Save test results"""
        results_path = Path('/Users/khamel83/dev/atlas-voice/oos/prototype_test_results.json')
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📊 Results saved to: {results_path}")

if __name__ == "__main__":
    # Run prototype test
    prototype = ContentAnalysisPrototype()
    results = prototype.test_content_analysis()
    prototype.save_results(results)

    print("\n🎯 PROTOTYPE TEST SUMMARY")
    print("=" * 40)
    for test_name, test_result in results.items():
        if isinstance(test_result, dict) and 'test_passed' in test_result:
            status = "✅ PASSED" if test_result['test_passed'] else "❌ FAILED"
            print(f"{test_name}: {status}")
        else:
            print(f"{test_name}: Test completed")
