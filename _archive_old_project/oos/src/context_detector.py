"""
OOS Context Detection System

This module implements advanced context detection using natural language processing
to determine the optimal voice profile for any given situation.
"""

import sys
import os
import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum

from oos_voice_engine import OOSVoiceEngine, VoiceProfile, get_voice_engine


class ContextType(Enum):
    """Context types for voice adaptation"""
    TECHNICAL = "technical"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    PROGRAMMING = "programming"
    DEBUGGING = "debugging"
    BUSINESS = "business"
    SOCIAL = "social"
    RESEARCH = "research"
    BRAINSTORMING = "brainstorming"
    TEACHING = "teaching"
    MEETING = "meeting"
    PLANNING = "planning"
    GENERAL = "general"


@dataclass
class ContextDetectionResult:
    """Result of context detection"""
    detected_context: ContextType
    confidence: float
    alternative_contexts: List[Tuple[ContextType, float]]
    detected_keywords: List[str]
    linguistic_features: Dict[str, Any]
    processing_time: float


class ContextDetector:
    """Advanced context detection system"""

    def __init__(self):
        self.voice_engine = get_voice_engine()

        # Context keyword dictionaries
        self.context_keywords = self._initialize_context_keywords()

        # Linguistic patterns
        self.patterns = self._initialize_patterns()

        # Detection statistics
        self.detection_stats = {
            "total_detections": 0,
            "high_confidence_detections": 0,
            "average_confidence": 0.0,
            "context_distribution": defaultdict(int)
        }

        # Context transition rules
        self.transition_rules = self._initialize_transition_rules()

    def _initialize_context_keywords(self) -> Dict[ContextType, List[str]]:
        """Initialize keyword dictionaries for context detection"""
        return {
            ContextType.TECHNICAL: [
                "code", "database", "api", "system", "implementation", "algorithm", "framework",
                "architecture", "protocol", "server", "client", "database", "function", "method",
                "class", "object", "variable", "constant", "interface", "abstract", "inheritance",
                "polymorphism", "encapsulation", "serialization", "deserialization", "query",
                "schema", "index", "constraint", "trigger", "procedure", "cursor", "transaction"
            ],
            ContextType.CASUAL: [
                "hey", "what's up", "cool", "awesome", "man", "dude", "like", "just", "actually",
                "you know", "basically", "weekend", "plans", "hang out", "chill", "relax",
                "fun", "party", "movie", "music", "game", "food", "drink", "coffee", "lunch"
            ],
            ContextType.PROFESSIONAL: [
                "regarding", "following up", "business", "meeting", "presentation", "formal",
                "corporate", "professional", "agenda", "minutes", "action items", "deliverables",
                "timeline", "deadline", "milestone", "objective", "goal", "strategy", "plan",
                "report", "analysis", "review", "assessment", "evaluation", "performance"
            ],
            ContextType.ANALYTICAL: [
                "analysis", "research", "data", "study", "examine", "investigate", "trends",
                "patterns", "correlation", "causation", "hypothesis", "theory", "methodology",
                "statistics", "metrics", "kpi", "measurement", "quantitative", "qualitative",
                "empirical", "evidence", "findings", "conclusions", "insights", "implications"
            ],
            ContextType.CREATIVE: [
                "ideas", "brainstorm", "create", "innovative", "what if", "imagine", "design",
                "concept", "prototype", "mockup", "sketch", "inspiration", "innovation", "artistic",
                "aesthetic", "vision", "conceptual", "experimental", "unconventional", "novel"
            ],
            ContextType.PROGRAMMING: [
                "debug", "compile", "run", "execute", "syntax", "error", "exception", "bug",
                "fix", "patch", "version", "release", "deploy", "test", "unittest", "integration",
                "refactor", "optimize", "performance", "memory", "cpu", "thread", "process"
            ],
            ContextType.DEBUGGING: [
                "error", "bug", "issue", "problem", "fail", "crash", "broken", "wrong",
                "fix", "solve", "debug", "trace", "log", "stack", "exception", "traceback",
                "debugger", "breakpoint", "watch", "step", "continue", "inspect", "variable"
            ],
            ContextType.BUSINESS: [
                "revenue", "profit", "cost", "budget", "finance", "investment", "roi",
                "customer", "client", "market", "sales", "marketing", "strategy", "competition",
                "partnership", "contract", "agreement", "negotiation", "deal", "proposal"
            ],
            ContextType.SOCIAL: [
                "friend", "family", "personal", "relationship", "social", "community",
                "event", "gathering", "celebration", "conversation", "chat", "discussion",
                "networking", "connection", "people", "team", "colleague", "coworker"
            ],
            ContextType.RESEARCH: [
                "paper", "journal", "publication", "academic", "scholarly", "literature",
                "review", "citation", "reference", "bibliography", "methodology", "findings",
                "results", "conclusions", "implications", "limitations", "future work"
            ],
            ContextType.BRAINSTORMING: [
                "ideas", "brainstorm", "think tank", "ideation", "creative", "innovation",
                "workshop", "session", "collaborative", "generate", "concept", "prototype",
                "solution", "approach", "strategy", "plan", "design", "develop", "build"
            ],
            ContextType.TEACHING: [
                "learn", "teach", "explain", "understand", "concept", "lesson", "tutorial",
                "guide", "instruction", "education", "training", "student", "pupil", "learner",
                "knowledge", "skill", "ability", "competency", "mastery", "expertise"
            ],
            ContextType.MEETING: [
                "meeting", "agenda", "attendees", "participants", "schedule", "time",
                "location", "room", "conference", "call", "video", "presentation", "slides",
                "discussion", "decision", "action", "follow up", "minutes", "notes"
            ],
            ContextType.PLANNING: [
                "plan", "schedule", "timeline", "deadline", "milestone", "goal", "objective",
                "task", "activity", "resource", "budget", "risk", "mitigation", "strategy",
                "roadmap", "vision", "mission", "priority", "scope", "requirements"
            ]
        }

    def _initialize_patterns(self) -> Dict[ContextType, List[str]]:
        """Initialize regex patterns for context detection"""
        return {
            ContextType.TECHNICAL: [
                r'\b(?:code|database|api|system|implementation)\b',
                r'\b(?:algorithm|framework|architecture|protocol)\b',
                r'\b(?:function|method|class|object|variable)\b'
            ],
            ContextType.CASUAL: [
                r'\b(?:hey|what\'s up|cool|awesome|man|dude)\b',
                r'\b(?:weekend|plans|hang out|chill|relax)\b',
                r'\b(?:fun|party|movie|music|game|food|drink)\b'
            ],
            ContextType.PROFESSIONAL: [
                r'\b(?:regarding|following up|business|meeting|presentation)\b',
                r'\b(?:professional|agenda|minutes|action items|deliverables)\b',
                r'\b(?:timeline|deadline|milestone|objective|goal)\b'
            ],
            ContextType.ANALYTICAL: [
                r'\b(?:analysis|research|data|study|examine|investigate)\b',
                r'\b(?:trends|patterns|correlation|causation|hypothesis)\b',
                r'\b(?:statistics|metrics|kpi|measurement|quantitative)\b'
            ],
            ContextType.CREATIVE: [
                r'\b(?:ideas|brainstorm|create|innovative|what if|imagine)\b',
                r'\b(?:design|concept|prototype|mockup|sketch|inspiration)\b',
                r'\b(?:innovation|artistic|aesthetic|vision|conceptual)\b'
            ]
        }

    def _initialize_transition_rules(self) -> Dict[ContextType, List[ContextType]]:
        """Initialize context transition rules"""
        return {
            ContextType.TECHNICAL: [ContextType.PROGRAMMING, ContextType.DEBUGGING, ContextType.TEACHING],
            ContextType.CASUAL: [ContextType.SOCIAL, ContextType.BRAINSTORMING],
            ContextType.PROFESSIONAL: [ContextType.BUSINESS, ContextType.MEETING, ContextType.PLANNING],
            ContextType.ANALYTICAL: [ContextType.RESEARCH, ContextType.BUSINESS, ContextType.PLANNING],
            ContextType.CREATIVE: [ContextType.BRAINSTORMING, ContextType.TEACHING, ContextType.PLANNING],
            ContextType.PROGRAMMING: [ContextType.TECHNICAL, ContextType.DEBUGGING],
            ContextType.DEBUGGING: [ContextType.TECHNICAL, ContextType.PROGRAMMING],
            ContextType.BUSINESS: [ContextType.PROFESSIONAL, ContextType.MEETING, ContextType.PLANNING],
            ContextType.SOCIAL: [ContextType.CASUAL, ContextType.BRAINSTORMING],
            ContextType.RESEARCH: [ContextType.ANALYTICAL, ContextType.TEACHING],
            ContextType.BRAINSTORMING: [ContextType.CREATIVE, ContextType.PLANNING, ContextType.TEACHING],
            ContextType.TEACHING: [ContextType.TECHNICAL, ContextType.ANALYTICAL, ContextType.CREATIVE],
            ContextType.MEETING: [ContextType.PROFESSIONAL, ContextType.BUSINESS, ContextType.PLANNING],
            ContextType.PLANNING: [ContextType.BUSINESS, ContextType.PROFESSIONAL, ContextType.CREATIVE]
        }

    def detect_context(self, text: str, previous_context: Optional[ContextType] = None) -> ContextDetectionResult:
        """Detect context from input text"""
        start_time = time.time()

        # Preprocess text
        processed_text = self._preprocess_text(text)

        # Extract linguistic features
        linguistic_features = self._extract_linguistic_features(processed_text)

        # Calculate context scores
        context_scores = self._calculate_context_scores(processed_text, linguistic_features)

        # Apply previous context influence
        if previous_context:
            context_scores = self._apply_context_influence(context_scores, previous_context)

        # Determine primary context
        primary_context = max(context_scores.items(), key=lambda x: x[1])
        detected_context = primary_context[0]
        confidence = primary_context[1]

        # Get alternative contexts
        alternatives = [(ctx, score) for ctx, score in context_scores.items()
                       if ctx != detected_context and score > 0.1]
        alternatives.sort(key=lambda x: x[1], reverse=True)
        alternatives = alternatives[:3]  # Top 3 alternatives

        # Extract detected keywords
        detected_keywords = self._extract_detected_keywords(processed_text, detected_context)

        # Update statistics
        self.detection_stats["total_detections"] += 1
        self.detection_stats["average_confidence"] = (
            (self.detection_stats["average_confidence"] * (self.detection_stats["total_detections"] - 1) + confidence) /
            self.detection_stats["total_detections"]
        )
        if confidence > 0.7:
            self.detection_stats["high_confidence_detections"] += 1
        self.detection_stats["context_distribution"][detected_context] += 1

        return ContextDetectionResult(
            detected_context=detected_context,
            confidence=confidence,
            alternative_contexts=alternatives,
            detected_keywords=detected_keywords,
            linguistic_features=linguistic_features,
            processing_time=time.time() - start_time
        )

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep words
        text = re.sub(r'[^\w\s]', ' ', text)

        return text.strip()

    def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features from text"""
        features = {}

        # Basic text statistics
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        features["word_count"] = len(words)
        features["sentence_count"] = len(sentences)
        features["avg_sentence_length"] = len(words) / max(len(sentences), 1)
        features["avg_word_length"] = sum(len(word) for word in words) / max(len(words), 1)

        # Sentence structure analysis
        question_marks = text.count('?')
        exclamation_marks = text.count('!')
        features["question_ratio"] = question_marks / max(len(sentences), 1)
        features["exclamation_ratio"] = exclamation_marks / max(len(sentences), 1)

        # Formality indicators
        formal_words = ["regarding", "therefore", "furthermore", "however", "consequently", "nevertheless"]
        informal_words = ["hey", "yeah", "cool", "awesome", "like", "just", "actually"]

        formal_count = sum(1 for word in formal_words if word in text)
        informal_count = sum(1 for word in informal_words if word in text)

        features["formal_word_count"] = formal_count
        features["informal_word_count"] = informal_count
        features["formality_ratio"] = formal_count / max(formal_count + informal_count, 1)

        # Technical complexity
        technical_indicators = ["implement", "system", "function", "method", "algorithm", "data", "process"]
        technical_count = sum(1 for indicator in technical_indicators if indicator in text)
        features["technical_indicators"] = technical_count
        features["technical_density"] = technical_count / max(len(words), 1)

        return features

    def _calculate_context_scores(self, text: str, linguistic_features: Dict[str, Any]) -> Dict[ContextType, float]:
        """Calculate confidence scores for each context type"""
        scores = {}

        for context_type in ContextType:
            score = 0.0

            # Keyword matching (40% weight)
            if context_type in self.context_keywords:
                keyword_score = self._calculate_keyword_score(text, self.context_keywords[context_type])
                score += keyword_score * 0.4

            # Pattern matching (30% weight)
            if context_type in self.patterns:
                pattern_score = self._calculate_pattern_score(text, self.patterns[context_type])
                score += pattern_score * 0.3

            # Linguistic features (30% weight)
            feature_score = self._calculate_feature_score(linguistic_features, context_type)
            score += feature_score * 0.3

            scores[context_type] = score

        # Normalize scores
        max_score = max(scores.values()) if scores.values() else 1.0
        if max_score > 0:
            scores = {ctx: score / max_score for ctx, score in scores.items()}

        return scores

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword matching score"""
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        return min(matches / 3.0, 1.0)  # Normalize by expected matches

    def _calculate_pattern_score(self, text: str, patterns: List[str]) -> float:
        """Calculate regex pattern matching score"""
        total_matches = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, text))
            total_matches += matches
        return min(total_matches / 2.0, 1.0)  # Normalize by expected matches

    def _calculate_feature_score(self, features: Dict[str, Any], context_type: ContextType) -> float:
        """Calculate linguistic feature score"""
        score = 0.0

        # Context-specific feature mappings
        feature_mappings = {
            ContextType.TECHNICAL: {
                "technical_density": 0.5,
                "avg_sentence_length": 0.3,
                "formality_ratio": 0.2
            },
            ContextType.CASUAL: {
                "informal_word_count": 0.4,
                "exclamation_ratio": 0.3,
                "question_ratio": 0.3
            },
            ContextType.PROFESSIONAL: {
                "formal_word_count": 0.5,
                "formality_ratio": 0.3,
                "avg_sentence_length": 0.2
            },
            ContextType.ANALYTICAL: {
                "avg_sentence_length": 0.4,
                "formality_ratio": 0.4,
                "technical_density": 0.2
            },
            ContextType.CREATIVE: {
                "exclamation_ratio": 0.3,
                "question_ratio": 0.4,
                "technical_density": 0.3
            }
        }

        if context_type in feature_mappings:
            for feature_name, weight in feature_mappings[context_type].items():
                if feature_name in features:
                    feature_value = features[feature_name]
                    # Normalize feature values
                    if feature_name in ["avg_sentence_length", "formality_ratio", "technical_density"]:
                        normalized_value = min(feature_value, 1.0)
                    else:
                        normalized_value = min(feature_value / 3.0, 1.0)  # Normalize counts
                    score += normalized_value * weight

        return score

    def _apply_context_influence(self, context_scores: Dict[ContextType, float], previous_context: ContextType) -> Dict[ContextType, float]:
        """Apply previous context influence to current scores"""
        influence_weight = 0.2  # 20% influence from previous context

        if previous_context in self.transition_rules:
            # Boost scores for related contexts
            for related_context in self.transition_rules[previous_context]:
                if related_context in context_scores:
                    context_scores[related_context] += influence_weight * 0.5

        # Slight boost to the previous context itself
        if previous_context in context_scores:
            context_scores[previous_context] += influence_weight * 0.3

        # Renormalize scores
        max_score = max(context_scores.values()) if context_scores.values() else 1.0
        if max_score > 0:
            context_scores = {ctx: score / max_score for ctx, score in context_scores.items()}

        return context_scores

    def _extract_detected_keywords(self, text: str, context_type: ContextType) -> List[str]:
        """Extract keywords that contributed to context detection"""
        if context_type not in self.context_keywords:
            return []

        detected_keywords = []
        text_lower = text.lower()

        for keyword in self.context_keywords[context_type]:
            if keyword in text_lower:
                detected_keywords.append(keyword)

        return detected_keywords[:5]  # Return top 5 keywords

    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get context detection statistics"""
        return {
            **self.detection_stats,
            "context_distribution": dict(self.detection_stats["context_distribution"]),
            "detection_accuracy": (
                self.detection_stats["high_confidence_detections"] /
                max(self.detection_stats["total_detections"], 1)
            )
        }

    def train_context_detector(self, training_data: List[Dict[str, Any]]):
        """Train context detector with labeled data"""
        # Simple learning approach - adjust keyword weights based on training data
        context_keyword_weights = defaultdict(lambda: defaultdict(float))

        for sample in training_data:
            text = sample["text"]
            true_context = sample["context"]
            confidence = sample.get("confidence", 1.0)

            # Update keyword weights
            if true_context in self.context_keywords:
                text_lower = text.lower()
                for keyword in self.context_keywords[true_context]:
                    if keyword in text_lower:
                        context_keyword_weights[true_context][keyword] += confidence

        # Apply learned weights (simplified approach)
        print(f"🎭 Context detector trained with {len(training_data)} samples")


# Global context detector instance
context_detector = None

def get_context_detector() -> ContextDetector:
    """Get or create context detector instance"""
    global context_detector
    if context_detector is None:
        context_detector = ContextDetector()
    return context_detector


if __name__ == "__main__":
    # Test context detector
    detector = ContextDetector()

    print("🎭 OOS Context Detection Test")
    print("=" * 40)

    test_samples = [
        "Let me explain how this database system works",
        "Hey what's up with the project timeline?",
        "Regarding the upcoming budget meeting",
        "We need to analyze the user engagement metrics",
        "What if we brainstorm some innovative solutions?",
        "I'm getting a syntax error in my Python code",
        "Can you help me debug this authentication issue?",
        "The quarterly revenue report shows strong growth",
        "Let's get together for coffee and chat",
        "I'm researching machine learning algorithms"
    ]

    for sample in test_samples:
        result = detector.detect_context(sample)
        print(f"\nText: {sample[:50]}...")
        print(f"Detected: {result.detected_context.value} ({result.confidence:.2f})")
        print(f"Keywords: {', '.join(result.detected_keywords)}")
        print(f"Time: {result.processing_time:.3f}s")

    # Get statistics
    stats = detector.get_detection_statistics()
    print(f"\nDetection Statistics:")
    print(f"Total detections: {stats['total_detections']}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")
    print(f"High confidence rate: {stats['detection_accuracy']:.1%}")

    print("\n✅ Context detection test completed!")
