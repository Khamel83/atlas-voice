"""
OOS Voice Adaptation Engine

This module implements real-time voice adaptation with machine learning
capabilities for continuous voice profile optimization.
"""

import sys
import os
import json
import time
import math
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque

from oos_voice_engine import OOSVoiceEngine, VoiceProfile, get_voice_engine
from voice_session import get_session_manager


@dataclass
class AdaptationSignal:
    """Individual adaptation signal"""
    timestamp: float
    signal_type: str
    context_type: str
    voice_profile: str
    confidence: float
    success_rating: Optional[float] = None
    user_feedback: Optional[str] = None


@dataclass
class AdaptationModel:
    """Machine learning model for voice adaptation"""
    model_version: str
    feature_weights: Dict[str, float]
    adaptation_thresholds: Dict[str, float]
    learning_rate: float
    confidence_decay: float
    last_updated: float


class VoiceAdaptationEngine:
    """Real-time voice adaptation with machine learning"""

    def __init__(self, model_path: str = "/tmp/voice_adaptation_models.json"):
        self.model_path = model_path
        self.voice_engine = get_voice_engine()
        self.session_manager = get_session_manager()

        # Adaptation state
        self.adaptation_history = deque(maxlen=1000)
        self.current_model = self._load_or_create_model()
        self.feature_cache = {}
        self.adaptation_stats = {
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "average_confidence": 0.0,
            "learning_iterations": 0
        }

        # Real-time adaptation parameters
        self.adaptation_window = 300  # 5 minutes
        self.min_confidence_threshold = 0.7
        self.confidence_decay_rate = 0.95
        self.learning_rate = 0.1

        print(f"🎭 Adaptation engine initialized with model v{self.current_model.model_version}")

    def _load_or_create_model(self) -> AdaptationModel:
        """Load existing model or create new one"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r') as f:
                    data = json.load(f)
                return AdaptationModel(**data)
            except Exception as e:
                print(f"⚠️  Failed to load model: {e}")

        # Create default model
        return AdaptationModel(
            model_version="1.0.0",
            feature_weights={
                "context_keywords": 0.3,
                "sentence_length": 0.2,
                "formality_level": 0.2,
                "technical_content": 0.15,
                "emotional_tone": 0.15
            },
            adaptation_thresholds={
                "technical": 0.8,
                "casual": 0.7,
                "professional": 0.85,
                "analytical": 0.9,
                "creative": 0.75
            },
            learning_rate=0.1,
            confidence_decay=0.95,
            last_updated=time.time()
        )

    def real_time_adaptation(self, input_text: str, context_type: str, session_id: str = None) -> Dict[str, Any]:
        """Perform real-time voice adaptation"""
        start_time = time.time()

        # Extract features from input
        features = self._extract_features(input_text, context_type)

        # Calculate adaptation confidence
        confidence = self._calculate_adaptation_confidence(features, context_type)

        # Determine target profile
        target_profile = self._determine_target_profile(context_type, confidence)

        # Apply adaptation if confidence meets threshold
        adaptation_result = {
            "adaptation_applied": False,
            "target_profile": target_profile,
            "confidence": confidence,
            "features": features,
            "execution_time": 0.0
        }

        if confidence >= self.min_confidence_threshold:
            old_profile = self.voice_engine.active_profile.value

            # Apply voice adaptation
            if self.voice_engine.select_voice(target_profile):
                adaptation_result["adaptation_applied"] = True
                adaptation_result["from_profile"] = old_profile
                adaptation_result["to_profile"] = target_profile

                # Record adaptation signal
                signal = AdaptationSignal(
                    timestamp=time.time(),
                    signal_type="real_time_adaptation",
                    context_type=context_type,
                    voice_profile=target_profile,
                    confidence=confidence
                )
                self.adaptation_history.append(signal)

                # Update session if provided
                if session_id:
                    self.session_manager.adapt_to_context(session_id, context_type, input_text)

                # Update stats
                self.adaptation_stats["total_adaptations"] += 1
                if confidence > 0.8:
                    self.adaptation_stats["successful_adaptations"] += 1

        adaptation_result["execution_time"] = time.time() - start_time
        return adaptation_result

    def _extract_features(self, input_text: str, context_type: str) -> Dict[str, float]:
        """Extract linguistic features from input text"""
        cache_key = f"{hash(input_text)}:{context_type}"
        if cache_key in self.feature_cache:
            return self.feature_cache[cache_key]

        features = {}

        # Context keywords
        context_keywords = {
            "technical": ["code", "database", "api", "system", "implementation", "algorithm", "framework"],
            "casual": ["hey", "what's up", "cool", "awesome", "man", "like", "just", "actually"],
            "professional": ["regarding", "following up", "business", "meeting", "presentation", "formal"],
            "analytical": ["analysis", "research", "data", "study", "examine", "investigate", "trends"],
            "creative": ["ideas", "brainstorm", "create", "innovative", "what if", "imagine", "design"]
        }

        keyword_score = 0.0
        if context_type in context_keywords:
            text_lower = input_text.lower()
            for keyword in context_keywords[context_type]:
                if keyword in text_lower:
                    keyword_score += 1
            features["context_keywords"] = min(keyword_score / 3.0, 1.0)  # Normalize
        else:
            features["context_keywords"] = 0.0

        # Sentence length analysis
        sentences = [s.strip() for s in input_text.split('.') if s.strip()]
        if sentences:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            # Normalize to 0-1 scale (assuming 5-25 word range)
            features["sentence_length"] = max(0, min(1, (avg_length - 5) / 20))
        else:
            features["sentence_length"] = 0.5

        # Formality level (simple heuristic)
        formal_indicators = ["regarding", "therefore", "furthermore", "however", "consequently"]
        informal_indicators = ["hey", "yeah", "cool", "awesome", "like", "just", "man"]

        formal_count = sum(1 for word in formal_indicators if word in input_text.lower())
        informal_count = sum(1 for word in informal_indicators if word in input_text.lower())

        total_indicators = formal_count + informal_count
        if total_indicators > 0:
            features["formality_level"] = formal_count / total_indicators
        else:
            features["formality_level"] = 0.5

        # Technical content detection
        technical_terms = ["algorithm", "database", "api", "framework", "implementation", "system"]
        technical_count = sum(1 for term in technical_terms if term in input_text.lower())
        word_count = len(input_text.split())
        features["technical_content"] = min(technical_count / max(word_count / 20, 1), 1.0)

        # Emotional tone (simple sentiment proxy)
        positive_words = ["great", "awesome", "excellent", "love", "excited", "happy"]
        negative_words = ["frustrated", "annoying", "difficult", "problem", "issue", "hate"]

        positive_count = sum(1 for word in positive_words if word in input_text.lower())
        negative_count = sum(1 for word in negative_words if word in input_text.lower())

        emotional_words = positive_count + negative_count
        if emotional_words > 0:
            features["emotional_tone"] = (positive_count - negative_count) / emotional_words
        else:
            features["emotional_tone"] = 0.0

        # Cache result
        self.feature_cache[cache_key] = features
        return features

    def _calculate_adaptation_confidence(self, features: Dict[str, float], context_type: str) -> float:
        """Calculate adaptation confidence using machine learning model"""
        base_confidence = 0.0

        # Apply feature weights
        for feature_name, feature_value in features.items():
            if feature_name in self.current_model.feature_weights:
                weight = self.current_model.feature_weights[feature_name]
                base_confidence += weight * feature_value

        # Apply context-specific threshold adjustment
        if context_type in self.current_model.adaptation_thresholds:
            threshold_adjustment = self.current_model.adaptation_thresholds[context_type]
            base_confidence *= threshold_adjustment

        # Apply time-based decay for recent adaptations
        recent_adaptations = [s for s in self.adaptation_history
                           if time.time() - s.timestamp < self.adaptation_window]

        if recent_adaptations:
            decay_factor = math.pow(self.confidence_decay_rate, len(recent_adaptations))
            base_confidence *= decay_factor

        # Ensure confidence is in valid range
        return max(0.0, min(1.0, base_confidence))

    def _determine_target_profile(self, context_type: str, confidence: float) -> str:
        """Determine target voice profile based on context"""
        context_to_profile = {
            "technical": VoiceProfile.OMAR_TECH,
            "casual": VoiceProfile.OMAR_CASUAL,
            "professional": VoiceProfile.OMAR_PRO,
            "analytical": VoiceProfile.OMAR_ANALYSIS,
            "creative": VoiceProfile.OMAR_CREATIVITY,
            "programming": VoiceProfile.OMAR_TECH,
            "debugging": VoiceProfile.OMAR_TECH,
            "business": VoiceProfile.OMAR_PRO,
            "social": VoiceProfile.OMAR_CASUAL,
            "research": VoiceProfile.OMAR_ANALYSIS,
            "brainstorming": VoiceProfile.OMAR_CREATIVITY,
            "meeting": VoiceProfile.OMAR_PRO,
            "planning": VoiceProfile.OMAR_BASE
        }

        return context_to_profile.get(context_type, VoiceProfile.OMAR_BASE).value

    def record_user_feedback(self, adaptation_id: str, success_rating: float, feedback_text: str = ""):
        """Record user feedback on adaptation quality"""
        # Find the adaptation signal
        for signal in self.adaptation_history:
            if signal.signal_type == "real_time_adaptation" and str(id(signal)) == adaptation_id:
                signal.success_rating = success_rating
                signal.user_feedback = feedback_text

                # Update model based on feedback
                self._update_model_from_feedback(signal)
                break

    def _update_model_from_feedback(self, signal: AdaptationSignal):
        """Update adaptation model based on user feedback"""
        if signal.success_rating is None:
            return

        # Calculate learning adjustment
        rating_error = signal.success_rating - signal.confidence
        adjustment = self.current_model.learning_rate * rating_error

        # Update feature weights
        if signal.context_type == "technical":
            self.current_model.feature_weights["technical_content"] += adjustment * 0.1
        elif signal.context_type == "casual":
            self.current_model.feature_weights["emotional_tone"] += adjustment * 0.1
        elif signal.context_type == "professional":
            self.current_model.feature_weights["formality_level"] += adjustment * 0.1

        # Normalize weights to ensure they sum to 1
        total_weight = sum(self.current_model.feature_weights.values())
        if total_weight > 0:
            for key in self.current_model.feature_weights:
                self.current_model.feature_weights[key] /= total_weight

        # Update thresholds
        if signal.context_type in self.current_model.adaptation_thresholds:
            threshold = self.current_model.adaptation_thresholds[signal.context_type]
            self.current_model.adaptation_thresholds[signal.context_type] = max(0.1, min(1.0, threshold + adjustment * 0.05))

        # Update timestamp
        self.current_model.last_updated = time.time()

        # Save updated model
        self._save_model()

        # Update stats
        self.adaptation_stats["learning_iterations"] += 1

        print(f"🎭 Model updated based on feedback (rating: {signal.success_rating:.2f})")

    def get_adaptation_insights(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get insights about adaptation performance"""
        cutoff_time = time.time() - (time_range_hours * 3600)

        # Filter recent adaptations
        recent_adaptations = [s for s in self.adaptation_history if s.timestamp > cutoff_time]

        if not recent_adaptations:
            return {"message": "No adaptations in specified time range", "total_adaptations": 0, "success_rate": 0.0}

        # Calculate statistics
        total_adaptations = len(recent_adaptations)
        successful_adaptations = len([s for s in recent_adaptations if s.confidence > 0.8])
        avg_confidence = sum(s.confidence for s in recent_adaptations) / total_adaptations

        # Profile usage distribution
        profile_usage = defaultdict(int)
        for signal in recent_adaptations:
            profile_usage[signal.voice_profile] += 1

        # Context type distribution
        context_distribution = defaultdict(int)
        for signal in recent_adaptations:
            context_distribution[signal.context_type] += 1

        # Feedback analysis
        feedback_signals = [s for s in recent_adaptations if s.success_rating is not None]
        avg_feedback_rating = sum(s.success_rating for s in feedback_signals) / max(len(feedback_signals), 1)

        return {
            "time_range_hours": time_range_hours,
            "total_adaptations": total_adaptations,
            "successful_adaptations": successful_adaptations,
            "success_rate": successful_adaptations / total_adaptations,
            "average_confidence": avg_confidence,
            "profile_usage": dict(profile_usage),
            "context_distribution": dict(context_distribution),
            "average_feedback_rating": avg_feedback_rating,
            "feedback_count": len(feedback_signals),
            "model_version": self.current_model.model_version,
            "model_last_updated": datetime.fromtimestamp(self.current_model.last_updated).isoformat()
        }

    def optimize_adaptation_parameters(self):
        """Optimize adaptation parameters based on performance data"""
        insights = self.get_adaptation_insights(168)  # Last week

        if insights["total_adaptations"] < 10:
            return {"message": "Insufficient data for optimization"}

        # Adjust confidence threshold based on success rate
        success_rate = insights["success_rate"]
        if success_rate < 0.7:  # Too many failed adaptations
            self.min_confidence_threshold = min(0.9, self.min_confidence_threshold + 0.05)
        elif success_rate > 0.9:  # Can be more aggressive
            self.min_confidence_threshold = max(0.6, self.min_confidence_threshold - 0.05)

        # Adjust learning rate based on feedback
        if insights.get("feedback_count", 0) > 5:
            avg_rating = insights["average_feedback_rating"]
            if avg_rating < 0.7:  # Poor performance
                self.learning_rate = min(0.2, self.learning_rate * 1.1)
            elif avg_rating > 0.8:  # Good performance
                self.learning_rate = max(0.05, self.learning_rate * 0.9)

        print(f"🎭 Adaptation parameters optimized: threshold={self.min_confidence_threshold:.2f}, learning_rate={self.learning_rate:.3f}")

        return {
            "optimizations_applied": True,
            "new_confidence_threshold": self.min_confidence_threshold,
            "new_learning_rate": self.learning_rate,
            "based_on_data": insights["total_adaptations"]
        }

    def _save_model(self):
        """Save current model to file"""
        try:
            model_data = asdict(self.current_model)
            with open(self.model_path, 'w') as f:
                json.dump(model_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save model: {e}")

    def get_current_state(self) -> Dict[str, Any]:
        """Get current adaptation engine state"""
        return {
            "model_version": self.current_model.model_version,
            "feature_weights": self.current_model.feature_weights,
            "adaptation_thresholds": self.current_model.adaptation_thresholds,
            "learning_rate": self.learning_rate,
            "confidence_threshold": self.min_confidence_threshold,
            "adaptation_stats": self.adaptation_stats,
            "recent_adaptations_count": len(self.adaptation_history)
        }

    def reset_learning(self):
        """Reset learning state to default"""
        self.current_model = self._load_or_create_model()
        self.adaptation_history.clear()
        self.feature_cache.clear()
        self.adaptation_stats = {
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "average_confidence": 0.0,
            "learning_iterations": 0
        }

        print("🎭 Adaptation engine learning state reset")


# Global adaptation engine instance
adaptation_engine = None

def get_adaptation_engine() -> VoiceAdaptationEngine:
    """Get or create adaptation engine instance"""
    global adaptation_engine
    if adaptation_engine is None:
        adaptation_engine = VoiceAdaptationEngine()
    return adaptation_engine


if __name__ == "__main__":
    # Test adaptation engine
    engine = VoiceAdaptationEngine()

    print("🎭 OOS Voice Adaptation Engine Test")
    print("=" * 40)

    test_inputs = [
        ("Let me explain this database system architecture", "technical"),
        ("Hey what's up with this project?", "casual"),
        ("Regarding the upcoming meeting presentation", "professional"),
        ("We need to analyze the user engagement metrics", "analytical"),
        ("What if we brainstorm some new product ideas?", "creative")
    ]

    for text, context in test_inputs:
        print(f"\nTesting: {context} context")
        result = engine.real_time_adaptation(text, context, "test_session")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Applied: {result['adaptation_applied']}")
        print(f"Target: {result['target_profile']}")
        print(f"Time: {result['execution_time']:.3f}s")

    # Get insights
    insights = engine.get_adaptation_insights(1)
    print(f"\nAdaptation Insights: {insights['total_adaptations']} adaptations, {insights['success_rate']:.1%} success rate")

    # Test optimization
    optimization = engine.optimize_adaptation_parameters()
    print(f"Optimization: {optimization}")

    print("\n✅ Adaptation engine test completed!")
