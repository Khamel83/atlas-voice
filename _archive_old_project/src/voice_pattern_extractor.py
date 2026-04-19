#!/usr/bin/env python3
"""
Voice Pattern Extraction Engine
Automatically analyzes user writing samples to extract personal linguistic patterns
"""

import os
import re
import json
import sqlite3
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
from collections import Counter, defaultdict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

@dataclass
class VoiceCharacteristics:
    """Extracted voice characteristics for a user"""
    communication_style: str
    key_phrases: List[str]
    sentence_length: float
    formality: float
    positivity: float
    technical_level: float
    enthusiasm: float
    directness: float
    paragraph_length: float
    question_frequency: float
    exclamation_frequency: float

@dataclass
class VoiceProfile:
    """Complete voice profile for a user"""
    user_id: str
    profile_name: str
    characteristics: VoiceCharacteristics
    signature_phrases: List[str]
    context_preferences: Dict[str, float]
    sample_sentences: List[str]
    confidence_score: float

class VoicePatternExtractor:
    """Extracts linguistic patterns from user writing samples"""

    def __init__(self, db_path: str = "voice_patterns.db"):
        self.db_path = db_path
        self.stop_words = set(stopwords.words('english'))
        self.setup_database()

        # Communication style indicators
        self.style_indicators = {
            'casual': ['like', 'just', 'you know', 'kinda', 'sorta', 'pretty much', 'basically'],
            'formal': ['regarding', 'furthermore', 'therefore', 'consequently', 'nevertheless'],
            'technical': ['implementation', 'architecture', 'algorithm', 'framework', 'methodology'],
            'creative': ['imagine', 'what if', 'possibilities', 'innovative', 'brainstorm'],
            'analytical': ['analysis', 'data suggests', 'research indicates', 'evidence shows']
        }

        # Enthusiasm indicators
        self.enthusiasm_indicators = {
            'high': ['awesome', 'amazing', 'incredible', 'fantastic', 'love', '!', 'wow'],
            'medium': ['good', 'nice', 'cool', 'interesting', 'great'],
            'low': ['okay', 'fine', 'adequate', 'reasonable']
        }

    def setup_database(self):
        """Setup SQLite database for storing voice patterns"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS voice_profiles (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sample_texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                source_type TEXT,
                content TEXT,
                analyzed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES voice_profiles (user_id)
            )
        ''')
        conn.commit()
        conn.close()

    def analyze_user_data(self, user_id: str, data_sources: List[Dict[str, Any]]) -> VoiceProfile:
        """
        Analyze user data from multiple sources and extract voice patterns

        Args:
            user_id: Unique identifier for the user
            data_sources: List of data sources with 'type' and 'content' keys

        Returns:
            VoiceProfile with extracted characteristics
        """
        # Store raw data
        self._store_sample_texts(user_id, data_sources)

        # Combine all text content
        all_text = self._combine_text_sources(data_sources)

        if len(all_text) < 1000:  # Minimum text requirement
            raise ValueError(f"Insufficient text data. Need at least 1000 characters, got {len(all_text)}")

        # Extract linguistic characteristics
        characteristics = self._extract_characteristics(all_text)

        # Identify signature phrases
        signature_phrases = self._extract_signature_phrases(all_text)

        # Determine context preferences
        context_preferences = self._analyze_context_preferences(all_text)

        # Extract sample sentences
        sample_sentences = self._extract_sample_sentences(all_text)

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(len(all_text), len(data_sources))

        # Create voice profile
        profile = VoiceProfile(
            user_id=user_id,
            profile_name=f"{user_id}_voice_profile",
            characteristics=characteristics,
            signature_phrases=signature_phrases,
            context_preferences=context_preferences,
            sample_sentences=sample_sentences,
            confidence_score=confidence_score
        )

        # Store profile
        self._store_voice_profile(profile)

        return profile

    def _store_sample_texts(self, user_id: str, data_sources: List[Dict[str, Any]]):
        """Store sample texts in database"""
        conn = sqlite3.connect(self.db_path)
        for source in data_sources:
            conn.execute('''
                INSERT INTO sample_texts (user_id, source_type, content)
                VALUES (?, ?, ?)
            ''', (user_id, source.get('type', 'unknown'), source['content']))
        conn.commit()
        conn.close()

    def _combine_text_sources(self, data_sources: List[Dict[str, Any]]) -> str:
        """Combine all text from data sources"""
        return '\n\n'.join([source['content'] for source in data_sources])

    def _extract_characteristics(self, text: str) -> VoiceCharacteristics:
        """Extract detailed voice characteristics from text"""

        # Basic text analysis
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        # Sentence length analysis
        sentence_lengths = [len(word_tokenize(s)) for s in sentences]
        avg_sentence_length = statistics.mean(sentence_lengths) if sentence_lengths else 0

        # Paragraph length analysis
        paragraph_lengths = [len(sent_tokenize(p)) for p in paragraphs]
        avg_paragraph_length = statistics.mean(paragraph_lengths) if paragraph_lengths else 0

        # Communication style analysis
        communication_style = self._detect_communication_style(text)

        # Key phrases extraction
        key_phrases = self._extract_key_phrases(text)

        # Formality analysis
        formality = self._calculate_formality(text, words)

        # Positivity analysis
        positivity = self._calculate_positivity(words)

        # Technical level analysis
        technical_level = self._calculate_technical_level(words)

        # Enthusiasm analysis
        enthusiasm = self._calculate_enthusiasm(text, words)

        # Directness analysis
        directness = self._calculate_directness(sentences)

        # Question and exclamation frequency
        question_freq = text.count('?') / len(sentences) if sentences else 0
        exclamation_freq = text.count('!') / len(sentences) if sentences else 0

        return VoiceCharacteristics(
            communication_style=communication_style,
            key_phrases=key_phrases,
            sentence_length=avg_sentence_length,
            formality=formality,
            positivity=positivity,
            technical_level=technical_level,
            enthusiasm=enthusiasm,
            directness=directness,
            paragraph_length=avg_paragraph_length,
            question_frequency=question_freq,
            exclamation_frequency=exclamation_freq
        )

    def _detect_communication_style(self, text: str) -> str:
        """Detect primary communication style"""
        text_lower = text.lower()
        style_scores = {}

        for style, indicators in self.style_indicators.items():
            score = sum(text_lower.count(indicator) for indicator in indicators)
            style_scores[style] = score

        # Normalize by text length
        text_length = len(text.split())
        for style in style_scores:
            style_scores[style] = style_scores[style] / text_length * 1000

        # Find dominant style
        dominant_style = max(style_scores, key=style_scores.get)

        # Create compound style if multiple styles are prominent
        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_styles) > 1 and sorted_styles[1][1] > sorted_styles[0][1] * 0.7:
            return f"{sorted_styles[0][0]}_{sorted_styles[1][0]}"

        return dominant_style

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract frequently used phrases and words"""
        text_lower = text.lower()

        # Extract common transition words and phrases
        common_phrases = [
            'basically', 'like', 'just', 'actually', 'you know', 'i think',
            'i mean', 'sort of', 'kind of', 'obviously', 'clearly',
            'honestly', 'personally', 'in fact', 'to be honest'
        ]

        found_phrases = []
        for phrase in common_phrases:
            count = text_lower.count(phrase)
            if count >= 2:  # Appears at least twice
                found_phrases.append(phrase)

        # Sort by frequency
        phrase_counts = [(phrase, text_lower.count(phrase)) for phrase in found_phrases]
        phrase_counts.sort(key=lambda x: x[1], reverse=True)

        return [phrase for phrase, count in phrase_counts[:10]]  # Top 10

    def _calculate_formality(self, text: str, words: List[str]) -> float:
        """Calculate formality level (0-1 scale)"""
        formal_indicators = [
            'regarding', 'furthermore', 'therefore', 'consequently', 'nevertheless',
            'however', 'moreover', 'accordingly', 'subsequently', 'wherein'
        ]

        informal_indicators = [
            'gonna', 'wanna', 'gotta', 'kinda', 'sorta', 'yeah', 'nah',
            'ok', 'cool', 'awesome', 'stuff', 'things'
        ]

        formal_count = sum(words.count(word) for word in formal_indicators)
        informal_count = sum(words.count(word) for word in informal_indicators)

        # Check for contractions
        contraction_count = len(re.findall(r"\w+'\w+", text))

        # Calculate formality score
        total_words = len(words)
        if total_words == 0:
            return 0.5

        formal_score = formal_count / total_words * 100
        informal_score = (informal_count + contraction_count) / total_words * 100

        # Normalize to 0-1 scale
        if formal_score + informal_score == 0:
            return 0.5

        return formal_score / (formal_score + informal_score)

    def _calculate_positivity(self, words: List[str]) -> float:
        """Calculate positivity level (0-1 scale)"""
        positive_words = [
            'good', 'great', 'awesome', 'amazing', 'excellent', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'excited', 'wonderful'
        ]

        negative_words = [
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'frustrated',
            'annoying', 'difficult', 'problem', 'issue', 'wrong'
        ]

        positive_count = sum(words.count(word) for word in positive_words)
        negative_count = sum(words.count(word) for word in negative_words)

        total_sentiment = positive_count + negative_count
        if total_sentiment == 0:
            return 0.5

        return positive_count / total_sentiment

    def _calculate_technical_level(self, words: List[str]) -> float:
        """Calculate technical sophistication level (0-1 scale)"""
        technical_words = [
            'algorithm', 'implementation', 'framework', 'architecture', 'database',
            'api', 'function', 'method', 'class', 'module', 'library', 'package',
            'server', 'client', 'protocol', 'interface', 'configuration'
        ]

        technical_count = sum(words.count(word) for word in technical_words)
        total_words = len(words)

        if total_words == 0:
            return 0

        # Normalize to 0-1 scale
        technical_ratio = technical_count / total_words * 100
        return min(technical_ratio / 5, 1.0)  # Cap at 1.0

    def _calculate_enthusiasm(self, text: str, words: List[str]) -> float:
        """Calculate enthusiasm level (0-1 scale)"""
        exclamation_count = text.count('!')
        caps_words = len([word for word in words if word.isupper() and len(word) > 1])

        enthusiasm_words = []
        for level, word_list in self.enthusiasm_indicators.items():
            enthusiasm_words.extend(word_list)

        enthusiasm_count = sum(words.count(word) for word in enthusiasm_words)

        # Calculate enthusiasm score
        total_words = len(words)
        if total_words == 0:
            return 0.5

        enthusiasm_score = (enthusiasm_count + exclamation_count + caps_words) / total_words * 100
        return min(enthusiasm_score / 2, 1.0)  # Cap at 1.0

    def _calculate_directness(self, sentences: List[str]) -> float:
        """Calculate directness level (0-1 scale)"""
        short_sentences = len([s for s in sentences if len(word_tokenize(s)) <= 10])
        imperative_patterns = len([s for s in sentences if re.match(r'^[A-Z][a-z]*\s', s.strip())])

        total_sentences = len(sentences)
        if total_sentences == 0:
            return 0.5

        directness_score = (short_sentences + imperative_patterns) / total_sentences
        return min(directness_score, 1.0)

    def _extract_signature_phrases(self, text: str) -> List[str]:
        """Extract user's signature phrases and expressions"""
        # This is a simplified version - could be enhanced with more sophisticated NLP
        phrases = []

        # Extract repeated phrases
        words = text.lower().split()
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]

        # Count phrase frequency
        bigram_counts = Counter(bigrams)
        trigram_counts = Counter(trigrams)

        # Get most common phrases (appearing at least 3 times)
        common_bigrams = [phrase for phrase, count in bigram_counts.most_common(10) if count >= 3]
        common_trigrams = [phrase for phrase, count in trigram_counts.most_common(5) if count >= 3]

        phrases.extend(common_bigrams)
        phrases.extend(common_trigrams)

        return phrases[:15]  # Return top 15 signature phrases

    def _analyze_context_preferences(self, text: str) -> Dict[str, float]:
        """Analyze what contexts the user writes in"""
        context_indicators = {
            'technical': ['code', 'system', 'database', 'api', 'implementation'],
            'casual': ['hey', 'what\'s up', 'cool', 'awesome'],
            'professional': ['meeting', 'project', 'deadline', 'team', 'client'],
            'creative': ['idea', 'design', 'creative', 'brainstorm'],
            'analytical': ['data', 'analysis', 'research', 'study', 'metrics']
        }

        text_lower = text.lower()
        context_scores = {}

        for context, indicators in context_indicators.items():
            score = sum(text_lower.count(indicator) for indicator in indicators)
            context_scores[context] = score / len(text.split()) * 1000  # Normalize

        # Convert to preferences (0-1 scale)
        total_score = sum(context_scores.values())
        if total_score == 0:
            return {context: 0.2 for context in context_scores}  # Default equal preferences

        return {context: score / total_score for context, score in context_scores.items()}

    def _extract_sample_sentences(self, text: str) -> List[str]:
        """Extract representative sample sentences"""
        sentences = sent_tokenize(text)

        # Filter sentences by length (not too short or too long)
        good_sentences = [
            s for s in sentences
            if 5 <= len(word_tokenize(s)) <= 25 and len(s) >= 20
        ]

        # Return a diverse sample
        if len(good_sentences) > 10:
            step = len(good_sentences) // 10
            return good_sentences[::step][:10]

        return good_sentences[:10]

    def _calculate_confidence_score(self, text_length: int, num_sources: int) -> float:
        """Calculate confidence score based on data quality and quantity"""
        # Base score on text length
        length_score = min(text_length / 10000, 1.0)  # 10k chars = max score

        # Bonus for multiple sources
        source_bonus = min(num_sources / 5, 0.2)  # Up to 20% bonus for 5+ sources

        # Combined confidence score
        confidence = (length_score * 0.8) + source_bonus
        return min(confidence, 1.0)

    def _store_voice_profile(self, profile: VoiceProfile):
        """Store voice profile in database"""
        conn = sqlite3.connect(self.db_path)
        profile_json = json.dumps(asdict(profile), indent=2)

        conn.execute('''
            INSERT OR REPLACE INTO voice_profiles (user_id, profile_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (profile.user_id, profile_json))

        conn.commit()
        conn.close()

    def load_voice_profile(self, user_id: str) -> Optional[VoiceProfile]:
        """Load voice profile from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            'SELECT profile_data FROM voice_profiles WHERE user_id = ?',
            (user_id,)
        )

        result = cursor.fetchone()
        conn.close()

        if result:
            profile_data = json.loads(result[0])
            # Reconstruct VoiceProfile object
            characteristics = VoiceCharacteristics(**profile_data['characteristics'])
            profile_data['characteristics'] = characteristics
            return VoiceProfile(**profile_data)

        return None

    def get_all_profiles(self) -> List[str]:
        """Get list of all user IDs with profiles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT user_id FROM voice_profiles')
        user_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return user_ids


def main():
    """Example usage of VoicePatternExtractor"""
    extractor = VoicePatternExtractor()

    # Example data sources
    sample_data = [
        {
            'type': 'email',
            'content': '''Hey team,

I wanted to follow up on our discussion yesterday about the new API implementation. Basically, I think we need to approach this differently. Like, the current architecture isn't going to scale well, you know?

Here's what I'm thinking - we should probably refactor the authentication layer first. It's just not robust enough for what we're trying to do. I mean, it works fine for our current load, but when we scale up, we're going to hit issues.

Let me know what you think. I'm happy to dive deeper into any of these points.

Thanks!'''
        },
        {
            'type': 'chat',
            'content': '''honestly this whole thing is pretty straightforward once you get the hang of it. like, you just need to understand the basic patterns and then everything else falls into place, you know?

the key thing is to not overthink it. i see people get stuck because they're trying to make it more complicated than it needs to be. just focus on the core functionality first and then you can add the fancy stuff later.

basically what i do is start with a simple implementation and then iterate. works every time.'''
        }
    ]

    # Extract voice patterns
    profile = extractor.analyze_user_data('test_user', sample_data)

    print("Voice Profile Analysis:")
    print(f"Communication Style: {profile.characteristics.communication_style}")
    print(f"Key Phrases: {profile.characteristics.key_phrases}")
    print(f"Formality: {profile.characteristics.formality:.2f}")
    print(f"Technical Level: {profile.characteristics.technical_level:.2f}")
    print(f"Enthusiasm: {profile.characteristics.enthusiasm:.2f}")
    print(f"Confidence Score: {profile.confidence_score:.2f}")


if __name__ == "__main__":
    main()
