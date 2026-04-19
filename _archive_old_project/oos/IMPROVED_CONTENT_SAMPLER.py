#!/usr/bin/env python3
"""
Improved Content Sampler with Better Filtering
Filters out spam, forwards, and focuses on high-quality content
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN
import re
from typing import List, Dict, Tuple

class ImprovedContentSampler:
    """Improved sampler with intelligent content filtering"""

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.email_path = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"

    def get_high_quality_samples(self, target_count: int = 200) -> List[Dict]:
        """Get high-quality content samples with filtering"""
        print(f"🔍 Extracting {target_count} high-quality samples...")

        # Load and filter emails
        all_emails = self._load_and_filter_emails()
        print(f"   Filtered from sample to {len(all_emails)} high-quality emails")

        # Extract topics using embeddings
        topics = self._extract_topics_with_embeddings(all_emails)
        print(f"   Found {len(topics)} distinct topic clusters")

        # Sample from each topic for diversity
        diverse_samples = self._sample_diverse_content(topics, target_count)
        print(f"   Selected {len(diverse_samples)} diverse samples")

        return diverse_samples

    def _load_and_filter_emails(self) -> List[Dict]:
        """Load emails and apply quality filters"""
        # Load in chunks for memory efficiency
        high_quality_emails = []
        chunk_size = 10000

        for chunk in pd.read_csv(self.email_path, chunksize=chunk_size):
            for _, row in chunk.iterrows():
                content = str(row.get('content', ''))
                subject = str(row.get('subject', ''))

                if self._is_high_quality_email(content, subject):
                    high_quality_emails.append({
                        'content': content,
                        'subject': subject,
                        'length': len(content),
                        'type': self._classify_content_type(content)
                    })

                if len(high_quality_emails) >= 1000:  # Reasonable limit for testing
                    break

            if len(high_quality_emails) >= 1000:
                break

        return high_quality_emails

    def _is_high_quality_email(self, content: str, subject: str) -> bool:
        """Determine if email is high-quality authentic content"""
        if not content or len(content) < 50:
            return False

        content_lower = content.lower()

        # REMOVE: Spam and chain letters
        spam_patterns = [
            'thespark.com', 'personality test', 'how well do you know me',
            'chain letter', 'forwarded message', 'fwd:', 'fw:',
            'survey with a twist', 'you fill in the blanks'
        ]
        if any(spam in content_lower for spam in spam_patterns):
            return False

        # REMOVE: Mostly quoted content (forwards)
        quoted_lines = sum(1 for line in content.split('\n') if line.strip().startswith('>'))
        total_lines = len([line for line in content.split('\n') if line.strip()])
        if total_lines > 0 and quoted_lines / total_lines > 0.4:
            return False

        # REMOVE: Auto-generated and system messages
        auto_patterns = [
            'auto-generated', 'automatic reply', 'out of office',
            'do not reply', 'this is an automated'
        ]
        if any(auto in content_lower for auto in auto_patterns):
            return False

        # KEEP: Academic content (your writing)
        academic_patterns = [
            'art history', 'paper', 'essay', 'assignment',
            'professor', 'class', 'course', 'polyxema',
            'formal analysis', 'aristotle', 'thesis'
        ]
        if any(academic in content_lower for academic in academic_patterns):
            return True

        # KEEP: Personal communication
        personal_patterns = [
            '@uchicago.edu', '@hotmail.com', 'zoheri',
            'meeting', 'dinner', 'plans', 'can you',
            'wanna', 'gonna', 'omar', 'omar zoheri'
        ]
        if any(personal in content_lower for personal in personal_patterns):
            return True

        # KEEP: Work/professional content
        work_patterns = [
            'research assistant', 'job', 'work', 'project',
            'interview', 'application', 'resume'
        ]
        if any(work in content_lower for work in work_patterns):
            return True

        # LENGTH FILTER: Reasonable email length
        word_count = len(content.split())
        return 30 <= word_count <= 800

    def _classify_content_type(self, content: str) -> str:
        """Classify the type of content"""
        content_lower = content.lower()

        if any(academic in content_lower for academic in ['art history', 'paper', 'essay', 'thesis']):
            return 'academic'
        elif any(work in content_lower for work in ['job', 'work', 'research assistant']):
            return 'work'
        elif any(social in content_lower for social in ['meeting', 'dinner', 'plans', 'wanna']):
            return 'social'
        elif any(tech in content_lower for tech in ['computer', 'excel', 'python', 'code']):
            return 'technical'
        else:
            return 'personal'

    def _extract_topics_with_embeddings(self, emails: List[Dict]) -> Dict:
        """Extract topic clusters using embeddings"""
        print("   Generating embeddings...")

        # Clean content for embeddings
        clean_texts = []
        for email in emails:
            clean_text = self._clean_content_for_embedding(email['content'])
            if clean_text:
                clean_texts.append({
                    'text': clean_text,
                    'original': email,
                    'type': email['type']
                })

        # Generate embeddings
        embeddings = self.model.encode([item['text'] for item in clean_texts])

        # Cluster with HDBSCAN
        clusterer = HDBSCAN(min_cluster_size=5, min_samples=2)
        cluster_labels = clusterer.fit_predict(embeddings)

        # Group by cluster
        topics = {}
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Skip noise points
                cluster_key = f'cluster_{label}'
                if cluster_key not in topics:
                    topics[cluster_key] = []
                topics[cluster_key].append({
                    'text': clean_texts[i]['text'],
                    'original': clean_texts[i]['original'],
                    'type': clean_texts[i]['type']
                })

        return topics

    def _clean_content_for_embedding(self, content: str) -> str:
        """Clean content for better embedding generation"""
        # Remove quoted lines
        lines = [line for line in content.split('\n') if not line.strip().startswith('>')]
        clean_content = ' '.join(lines)

        # Remove email headers and signatures
        clean_content = re.sub(r'From:.*?Subject:.*?\n', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r'On .* wrote:', '', clean_content)
        clean_content = re.sub(r'-\w+$', '', clean_content)  # Remove signatures

        # Remove extra whitespace
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()

        return clean_content

    def _sample_diverse_content(self, topics: Dict, target_count: int) -> List[Dict]:
        """Sample diverse content from different topic clusters"""
        samples = []
        samples_per_topic = max(1, target_count // len(topics))

        for cluster_name, cluster_emails in topics.items():
            # Sample from this cluster
            cluster_sample = cluster_emails[:samples_per_topic]

            for item in cluster_sample:
                samples.append({
                    'content': item['original']['content'],
                    'type': item['original']['type'],
                    'cluster': cluster_name,
                    'length': item['original']['length']
                })

                if len(samples) >= target_count:
                    break

            if len(samples) >= target_count:
                break

        return samples[:target_count]

    def analyze_content_distribution(self, samples: List[Dict]):
        """Analyze the distribution of content types"""
        type_counts = {}
        for sample in samples:
            content_type = sample['type']
            type_counts[content_type] = type_counts.get(content_type, 0) + 1

        print("📊 Content Type Distribution:")
        for content_type, count in sorted(type_counts.items()):
            percentage = (count / len(samples)) * 100
            print(f"   {content_type}: {count} samples ({percentage:.1f}%)")

if __name__ == "__main__":
    # Test the improved sampler
    sampler = ImprovedContentSampler()
    high_quality_samples = sampler.get_high_quality_samples(100)

    print("\\n🎯 IMPROVED SAMPLING RESULTS")
    print("=" * 40)
    sampler.analyze_content_distribution(high_quality_samples)

    print("\\n📝 SAMPLE CONTENT:")
    for i, sample in enumerate(high_quality_samples[:5], 1):
        print(f"{i}. [{sample['type']}] {sample['content'][:100]}...")
        print()
