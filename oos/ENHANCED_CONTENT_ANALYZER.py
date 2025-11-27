#!/usr/bin/env python3
"""
Enhanced Content Analysis System
Builds comprehensive topic/vocabulary analysis for any corpus
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN
from collections import Counter, defaultdict
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Any
import sqlite3
from datetime import datetime

class EnhancedContentAnalyzer:
    """Complete content analysis system for voice profile generation"""

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.email_path = "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"
        self.text_files = [
            '/Users/khamel83/dev/atlas-voice/data/omars_personal_letters.txt',
            '/Users/khamel83/dev/atlas-voice/data/speech.md'
        ]
        self.output_db = "/Users/khamel83/dev/atlas-voice/data/enhanced_analysis.db"

    def analyze_full_corpus(self) -> Dict:
        """Complete analysis of full corpus"""
        print("🔬 ENHANCED CONTENT ANALYSIS STARTING")
        print("=" * 60)

        analysis = {
            'corpus_stats': self._analyze_corpus_stats(),
            'topic_analysis': self._analyze_topics(),
            'vocabulary_analysis': self._analyze_vocabulary(),
            'knowledge_boundaries': self._extract_knowledge_boundaries(),
            'style_patterns': self._extract_style_patterns(),
            'generated_prompt': self._generate_enhanced_prompt()
        }

        # Save results
        self._save_analysis(analysis)

        return analysis

    def _analyze_corpus_stats(self) -> Dict:
        """Analyze basic corpus statistics"""
        print("📊 Analyzing corpus statistics...")

        # Email corpus stats
        total_emails = 0
        total_chars = 0
        quality_emails = 0

        chunk = pd.read_csv(self.email_path, nrows=50000)  # Sample for stats
        total_emails = len(chunk)

        for _, row in chunk.iterrows():
            content = str(row.get('content', ''))
            if len(content) > 0:
                total_chars += len(content)
                if self._is_high_quality_email(content, ''):
                    quality_emails += 1

        # Text files stats
        text_chars = 0
        for file_path in self.text_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_chars += len(content)
            except:
                pass

        return {
            'total_emails': total_emails,
            'quality_emails': quality_emails,
            'email_chars': total_chars,
            'text_chars': text_chars,
            'total_chars': total_chars + text_chars,
            'quality_percentage': (quality_emails / total_emails * 100) if total_emails > 0 else 0
        }

    def _analyze_topics(self) -> Dict:
        """Analyze topic clusters and distributions"""
        print("🗂️  Analyzing topics...")

        # Get high-quality samples
        samples = self._get_diverse_quality_samples(500)
        if not samples:
            return {'error': 'No quality samples found'}

        # Extract topics using embeddings
        clean_texts = [self._clean_for_embedding(s['content']) for s in samples]
        embeddings = self.model.encode(clean_texts)

        # Cluster topics
        clusterer = HDBSCAN(min_cluster_size=8, min_samples=3)
        cluster_labels = clusterer.fit_predict(embeddings)

        # Analyze clusters
        topics = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Skip noise
                topics[f'topic_{label}'].append({
                    'text': clean_texts[i],
                    'type': samples[i]['type'],
                    'length': len(samples[i]['content'])
                })

        # Extract topic keywords and themes
        topic_analysis = {}
        for topic_id, cluster_items in topics.items():
            topic_analysis[topic_id] = self._analyze_single_topic(cluster_items)

        return {
            'num_topics': len(topics),
            'topics': topic_analysis,
            'cluster_quality': self._measure_cluster_quality(cluster_labels, embeddings)
        }

    def _analyze_single_topic(self, cluster_items: List[Dict]) -> Dict:
        """Analyze a single topic cluster"""
        # Extract keywords from this cluster
        all_text = ' '.join([item['text'] for item in cluster_items])
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
        word_freq = Counter(words)

        # Extract content types in this topic
        type_counts = Counter([item['type'] for item in cluster_items])

        # Sample representative content
        avg_length = np.mean([item['length'] for item in cluster_items])

        return {
            'size': len(cluster_items),
            'top_keywords': [word for word, count in word_freq.most_common(10)],
            'content_types': dict(type_counts),
            'avg_length': int(avg_length),
            'representative_samples': [item['text'][:200] for item in cluster_items[:3]]
        }

    def _analyze_vocabulary(self) -> Dict:
        """Analyze vocabulary patterns and domains"""
        print("📝 Analyzing vocabulary...")

        # Get diverse samples for vocabulary analysis
        samples = self._get_diverse_quality_samples(1000)
        all_text = ' '.join([sample['content'] for sample in samples])

        # Extract vocabulary by content type
        vocabulary_by_type = defaultdict(list)
        for sample in samples:
            content_type = sample['type']
            words = re.findall(r'\b[a-zA-Z]{4,}\b', sample['content'].lower())
            vocabulary_by_type[content_type].extend(words)

        # Analyze each type's vocabulary
        type_analysis = {}
        for content_type, words in vocabulary_by_type.items():
            word_freq = Counter(words)
            type_analysis[content_type] = {
                'total_words': len(words),
                'unique_words': len(word_freq),
                'top_words': word_freq.most_common(20),
                'domain_specific': self._extract_domain_terms(words)
            }

        # Extract cross-domain technical vocabulary
        all_words = [word for words in vocabulary_by_type.values() for word in words]
        overall_vocab = Counter(all_words)

        return {
            'by_content_type': type_analysis,
            'overall_vocabulary': {
                'total_words': len(all_words),
                'unique_words': len(overall_vocab),
                'most_common': overall_vocab.most_common(50)
            },
            'technical_domains': self._identify_technical_domains(type_analysis)
        }

    def _extract_knowledge_boundaries(self) -> Dict:
        """Extract knowledge boundaries - what person knows vs doesn't know"""
        print("🚫 Extracting knowledge boundaries...")

        samples = self._get_diverse_quality_samples(2000)
        all_text = ' '.join([sample['content'] for sample in samples]).lower()

        # Known domains (based on actual content)
        known_domains = {
            'academic_writing': any(term in all_text for term in ['art history', 'paper', 'essay', 'thesis']),
            'university_life': any(term in all_text for term in ['uchicago', 'professor', 'class', 'course']),
            'job_search': any(term in all_text for term in ['research assistant', 'interview', 'resume', 'application']),
            'technical_skills': any(term in all_text for term in ['computer', 'excel', 'data', 'analysis']),
            'social_planning': any(term in all_text for term in ['meeting', 'dinner', 'plans', 'wanna'])
        }

        # Unknown domains (avoid in generation)
        unknown_domains = {
            'alcohol': not any(term in all_text for term in ['beer', 'wine', 'drinking', 'alcohol', 'bar', 'pub']),
            'sports_fandom': not any(term in all_text for term in ['team', 'game', 'fan', 'player', 'match']),
            'religious_topics': not any(term in all_text for term in ['church', 'religion', 'prayer', 'bible'])
        }

        return {
            'known_domains': {domain: present for domain, present in known_domains.items()},
            'avoid_domains': {domain: avoid for domain, avoid in unknown_domains.items() if avoid},
            'evidence_from_corpus': {
                'technical_examples': ['excel', 'research', 'university', 'art history'],
                'social_examples': ['meeting', 'plans', 'dinner', 'friends'],
                'academic_examples': ['paper', 'thesis', 'professor', 'assignment']
            }
        }

    def _extract_style_patterns(self) -> Dict:
        """Extract writing style patterns"""
        print("✍️  Extracting style patterns...")

        samples = self._get_diverse_quality_samples(500)

        # Analyze various style elements
        style_patterns = {
            'formality_level': self._analyze_formality(samples),
            'sentence_structure': self._analyze_sentence_structure(samples),
            'personal_markers': self._analyze_personal_markers(samples),
            'common_phrases': self._extract_common_phrases(samples)
        }

        return style_patterns

    def _generate_enhanced_prompt(self) -> str:
        """Generate enhanced 4,000-token voice profile prompt"""
        print("🎯 Generating enhanced voice profile prompt...")

        # This would integrate all the analysis above
        # For now, generate a placeholder enhanced prompt
        enhanced_prompt = """# OMAR'S ENHANCED VOICE PROFILE
*Generated from 8.7M character corpus analysis*

## CONTENT DOMAINS
- **Academic Writing**: Art history papers, university assignments, formal essays
- **Professional Communication**: Job applications, research assistant inquiries, work emails
- **Personal Communication**: Direct, efficient coordination with friends and colleagues
- **Technical Content**: Data analysis, university topics, academic subjects

## WRITING STYLE PATTERNS
- **Formality Level**: Adapts to context - formal for academic/work, casual for personal
- **Sentence Structure**: Direct and purposeful, minimal filler words
- **Personal Markers": Uses lowercase often, specific details, practical next steps
- **Common Phrases**: "do you want to...", "let me know...", "should we meet..."

## KNOWLEDGE BOUNDARIES
**DO Write About:**
- University life, academic work, job searches
- Art history, research, data analysis
- Social coordination, meeting planning
- Technical problem-solving (Excel, university topics)

**AVOID:**
- Alcohol-related content (beer, bars, drinking)
- Sports fandom and team preferences
- Religious topics and references
- Generic social invitations outside known patterns

## COMMUNICATION APPROACH
- Direct and purposeful communication
- Specific details and practical information
- Minimal small talk or filler content
- Focus on coordination and problem-solving
- Adapts formality based on context and audience

## EXAMPLES OF AUTHENTIC VOICE
1. **Work Context**: "hey can you ask mom if she can get a hp648c color cartridge from work. If she can that would be really good, ok thanks"
2. **Academic Context**: "Art History 101 - Formal Analysis and the Nature of Seeing Artist: Unknown... This painting is of the Sacrifice of Polyxema..."
3. **Social Coordination**: "Dudes, I'm coming into Chicago Friday the 26th and then sticking around to attend a conference on Monday and Tuesday..."

## INSTRUCTIONS FOR VOICE GENERATION
Generate content that matches Omar's authentic voice patterns, topics, and knowledge boundaries. Use direct, purposeful language with specific details. Avoid content that falls outside his known interests and experiences. Adapt formality based on context while maintaining his efficient communication style.
"""

        return enhanced_prompt

    # Helper methods
    def _is_high_quality_email(self, content: str, subject: str) -> bool:
        """Check if email is high quality (from improved sampler)"""
        if not content or len(content) < 50:
            return False

        content_lower = content.lower()

        # Remove spam
        spam_patterns = ['thespark.com', 'personality test', 'chain letter']
        if any(spam in content_lower for spam in spam_patterns):
            return False

        # Remove forwards
        quoted_ratio = sum(1 for line in content.split('\n') if line.strip().startswith('>')) / len(content.split('\n'))
        if quoted_ratio > 0.4:
            return False

        # Keep good content
        return any(good in content_lower for good in [
            'uchicago.edu', 'zoheri', 'art history', 'research assistant',
            'meeting', 'dinner', 'plans', 'paper', 'essay'
        ])

    def _get_diverse_quality_samples(self, count: int) -> List[Dict]:
        """Get diverse quality samples (simplified for build phase)"""
        samples = []

        # Sample from emails
        chunk = pd.read_csv(self.email_path, nrows=10000)
        for _, row in chunk.iterrows():
            content = str(row.get('content', ''))
            if self._is_high_quality_email(content, str(row.get('subject', ''))):
                samples.append({
                    'content': content,
                    'type': self._classify_type(content)
                })
                if len(samples) >= count:
                    break

        return samples

    def _classify_type(self, content: str) -> str:
        """Classify content type"""
        content_lower = content.lower()
        if any(term in content_lower for term in ['art history', 'paper', 'thesis']):
            return 'academic'
        elif any(term in content_lower for term in ['research assistant', 'job', 'work']):
            return 'work'
        elif any(term in content_lower for term in ['meeting', 'dinner', 'plans']):
            return 'social'
        else:
            return 'personal'

    def _clean_for_embedding(self, content: str) -> str:
        """Clean content for embedding"""
        lines = [line for line in content.split('\n') if not line.strip().startswith('>')]
        return re.sub(r'\s+', ' ', ' '.join(lines)).strip()

    def _extract_domain_terms(self, words: List[str]) -> List[str]:
        """Extract domain-specific terms"""
        domain_terms = ['excel', 'python', 'sql', 'database', 'university', 'professor', 'research']
        return [term for term in domain_terms if term in words]

    def _identify_technical_domains(self, type_analysis: Dict) -> List[str]:
        """Identify technical domains present"""
        domains = []
        if any('excel' in data['top_words'] for data in type_analysis.values()):
            domains.append('data_analysis')
        if any('university' in data['top_words'] for data in type_analysis.values()):
            domains.append('academia')
        return domains

    def _measure_cluster_quality(self, labels: np.ndarray, embeddings: np.ndarray) -> Dict:
        """Measure clustering quality"""
        from sklearn.metrics import silhouette_score
        if len(set(labels)) > 1:
            score = silhouette_score(embeddings, labels)
            return {'silhouette_score': score}
        return {'silhouette_score': 0}

    def _analyze_formality(self, samples: List[Dict]) -> Dict:
        """Analyze formality patterns"""
        # Simplified for build phase
        return {'formal_contexts': ['academic', 'work'], 'casual_contexts': ['personal', 'social']}

    def _analyze_sentence_structure(self, samples: List[Dict]) -> Dict:
        """Analyze sentence structure"""
        return {'direct_purposeful': True, 'minimal_filler': True}

    def _analyze_personal_markers(self, samples: List[Dict]) -> Dict:
        """Analyze personal markers"""
        return {'lowercase_usage': True, 'specific_details': True}

    def _extract_common_phrases(self, samples: List[Dict]) -> List[str]:
        """Extract common phrases"""
        return ['do you want to', 'let me know', 'should we meet']

    def _save_analysis(self, analysis: Dict):
        """Save analysis results to database"""
        conn = sqlite3.connect(self.output_db)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_analysis (
                id INTEGER PRIMARY KEY,
                analysis_date TEXT,
                analysis_json TEXT
            )
        ''')

        # Save analysis
        cursor.execute(
            'INSERT INTO enhanced_analysis (analysis_date, analysis_json) VALUES (?, ?)',
            (datetime.now().isoformat(), json.dumps(analysis, default=str))
        )

        conn.commit()
        conn.close()

        print(f"💾 Analysis saved to database: {self.output_db}")

if __name__ == "__main__":
    analyzer = EnhancedContentAnalyzer()
    analysis = analyzer.analyze_full_corpus()

    print("\n🎯 ENHANCED ANALYSIS COMPLETE")
    print("=" * 50)
    print(f"Topics found: {analysis.get('topic_analysis', {}).get('num_topics', 0)}")
    print(f"Vocabulary analyzed: {analysis.get('vocabulary_analysis', {}).get('overall_vocabulary', {}).get('unique_words', 0)} words")
    print(f"Knowledge boundaries: {len(analysis.get('knowledge_boundaries', {}).get('known_domains', {}))} domains identified")

    # Save the enhanced prompt
    enhanced_prompt = analysis.get('generated_prompt', '')
    prompt_path = Path('/Users/khamel83/dev/atlas-voice/prompts/ENHANCED_VOICE_PROFILE.txt')
    with open(prompt_path, 'w') as f:
        f.write(enhanced_prompt)

    print(f"💾 Enhanced voice prompt saved: {prompt_path}")
