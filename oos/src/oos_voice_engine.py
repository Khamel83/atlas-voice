"""
OOS Voice Integration - Core Voice Engine

This module implements the core voice profile engine for OOS integration,
enabling context-aware voice stratification and adaptation.
"""

import sys
import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Add voice profile path
sys.path.append('/Users/khamel83/dev/atlas-voice/voice_profile/src')

try:
    from comprehensive_analyzer import ComprehensiveAnalyzer
    from voice_analyzer import VoiceAnalyzer
except ImportError:
    # Fallback for development
    ComprehensiveAnalyzer = None
    VoiceAnalyzer = None


class VoiceProfile(Enum):
    """Voice profile enumeration"""
    OMAR_BASE = "OMAR_BASE"
    OMAR_TECH = "OMAR_TECH"
    OMAR_CASUAL = "OMAR_CASUAL"
    OMAR_PRO = "OMAR_PRO"
    OMAR_ANALYSIS = "OMAR_ANALYSIS"
    OMAR_CREATIVITY = "OMAR_CREATIVITY"


@dataclass
class VoiceCharacteristics:
    """Voice characteristics data structure"""
    communication_style: str
    key_phrases: List[str]
    sentence_length: float
    formality: float
    positivity: float
    technical_level: float
    enthusiasm: float
    directness: float


@dataclass
class VoiceProfileData:
    """Complete voice profile data"""
    profile_id: str
    description: str
    characteristics: VoiceCharacteristics
    use_cases: List[str]
    adaptation_rules: Dict[str, Any]
    context_optimization: Dict[str, float]


class OOSVoiceEngine:
    """Core voice engine for OOS integration"""

    def __init__(self, voice_profile_path: str = "/Users/khamel83/dev/atlas-voice/voice_profile"):
        self.voice_profile_path = voice_profile_path
        self.active_profile = VoiceProfile.OMAR_BASE
        self.analyzer = None
        self.profiles = {}
        self.session_history = []
        self.adaptation_cache = {}

        # Initialize analyzer if available
        if ComprehensiveAnalyzer:
            try:
                self.analyzer = ComprehensiveAnalyzer(voice_profile_path)
                print(f"✅ Voice analyzer initialized with {self.analyzer.total_words} words")
            except Exception as e:
                print(f"⚠️  Voice analyzer initialization failed: {e}")

        # Load voice profiles
        self._load_voice_profiles()
        print(f"✅ Loaded {len(self.profiles)} voice profiles")

    def _load_voice_profiles(self):
        """Load all available voice profiles"""

        # Base profile - OMAR_BASE (from actual analysis)
        self.profiles[VoiceProfile.OMAR_BASE] = VoiceProfileData(
            profile_id="OMAR_BASE",
            description="Authentic balanced communication style",
            characteristics=VoiceCharacteristics(
                communication_style="collaborative_inclusive",
                key_phrases=["basically", "like", "just", "actually", "you know"],
                sentence_length=12.8,
                formality=0.3,
                positivity=0.11,
                technical_level=0.06,
                enthusiasm=0.45,
                directness=0.72
            ),
            use_cases=["general_communication", "default_voice"],
            adaptation_rules={
                "technical": {"technical_level": +0.3, "formality": +0.2},
                "casual": {"formality": -0.2, "positivity": +0.1},
                "professional": {"formality": +0.4, "technical_level": +0.2}
            },
            context_optimization={
                "technical": 0.85,
                "casual": 0.78,
                "professional": 0.92,
                "analytical": 0.81,
                "creative": 0.76
            }
        )

        # Technical profile
        self.profiles[VoiceProfile.OMAR_TECH] = VoiceProfileData(
            profile_id="OMAR_TECH",
            description="Technical but accessible explanations",
            characteristics=VoiceCharacteristics(
                communication_style="technical_collaborative",
                key_phrases=["basically", "like", "implementation", "system", "architecture"],
                sentence_length=14.2,
                formality=0.5,
                positivity=0.08,
                technical_level=0.34,
                enthusiasm=0.41,
                directness=0.75
            ),
            use_cases=["technical_documentation", "code_explanation", "system_design"],
            adaptation_rules={
                "complexity": {"technical_level": +0.2},
                "audience": {"formality": +0.3}
            },
            context_optimization={
                "technical": 0.95,
                "programming": 0.98,
                "system_design": 0.92,
                "debugging": 0.89
            }
        )

        # Casual profile
        self.profiles[VoiceProfile.OMAR_CASUAL] = VoiceProfileData(
            profile_id="OMAR_CASUAL",
            description="Friend-to-friend conversational style",
            characteristics=VoiceCharacteristics(
                communication_style="casual_direct",
                key_phrases=["like", "just", "you know", "man", "actually"],
                sentence_length=10.5,
                formality=0.1,
                positivity=0.15,
                technical_level=0.02,
                enthusiasm=0.68,
                directness=0.85
            ),
            use_cases=["social_media", "personal_emails", "casual_conversation"],
            adaptation_rules={
                "formality": {"formality": -0.1},
                "enthusiasm": {"positivity": +0.2}
            },
            context_optimization={
                "casual": 0.96,
                "personal": 0.93,
                "social": 0.91,
                "friendly": 0.95
            }
        )

        # Professional profile
        self.profiles[VoiceProfile.OMAR_PRO] = VoiceProfileData(
            profile_id="OMAR_PRO",
            description="Professional correspondence style",
            characteristics=VoiceCharacteristics(
                communication_style="professional_collaborative",
                key_phrases=["regarding", "following up", "basically", "implementation"],
                sentence_length=15.1,
                formality=0.7,
                positivity=0.18,
                technical_level=0.28,
                enthusiasm=0.52,
                directness=0.63
            ),
            use_cases=["business_communication", "formal_documentation", "client_emails"],
            adaptation_rules={
                "formality": {"formality": +0.2},
                "technical": {"technical_level": +0.15}
            },
            context_optimization={
                "professional": 0.97,
                "business": 0.94,
                "formal": 0.95,
                "corporate": 0.91
            }
        )

        # Analysis profile
        self.profiles[VoiceProfile.OMAR_ANALYSIS] = VoiceProfileData(
            profile_id="OMAR_ANALYSIS",
            description="Deep analytical writing style",
            characteristics=VoiceCharacteristics(
                communication_style="analytical_academic",
                key_phrases=["analysis", "research", "basically", "implementation", "system"],
                sentence_length=16.8,
                formality=0.8,
                positivity=0.05,
                technical_level=0.45,
                enthusiasm=0.32,
                directness=0.58
            ),
            use_cases=["academic_papers", "data_analysis", "research_documentation"],
            adaptation_rules={
                "complexity": {"technical_level": +0.25},
                "depth": {"formality": +0.15}
            },
            context_optimization={
                "analytical": 0.96,
                "research": 0.94,
                "academic": 0.98,
                "data_analysis": 0.92
            }
        )

        # Creativity profile
        self.profiles[VoiceProfile.OMAR_CREATIVITY] = VoiceProfileData(
            profile_id="OMAR_CREATIVITY",
            description="Creative/brainstorming mode",
            characteristics=VoiceCharacteristics(
                communication_style="creative_divergent",
                key_phrases=["ideas", "brainstorm", "basically", "like", "what if"],
                sentence_length=11.2,
                formality=0.2,
                positivity=0.35,
                technical_level=0.12,
                enthusiasm=0.89,
                directness=0.48
            ),
            use_cases=["brainstorming", "creative_writing", "ideation"],
            adaptation_rules={
                "creativity": {"positivity": +0.3, "enthusiasm": +0.2},
                "collaboration": {"directness": -0.15}
            },
            context_optimization={
                "creative": 0.97,
                "brainstorming": 0.95,
                "ideation": 0.93,
                "innovation": 0.91
            }
        )

    def select_voice(self, profile_name: str) -> bool:
        """Select active voice profile"""
        try:
            profile_enum = VoiceProfile(profile_name)
            if profile_enum in self.profiles:
                old_profile = self.active_profile
                self.active_profile = profile_enum

                # Record switch
                self.session_history.append({
                    "timestamp": time.time(),
                    "from_profile": old_profile.value,
                    "to_profile": profile_name,
                    "reason": "manual_selection"
                })

                print(f"🎭 Voice switched: {old_profile.value} → {profile_name}")
                return True
        except ValueError:
            pass

        return False

    def adapt_to_context(self, context_type: str, input_text: str = "") -> str:
        """Adapt voice to specific context"""
        context_mapping = {
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
            "brainstorming": VoiceProfile.OMAR_CREATIVITY
        }

        if context_type in context_mapping:
            target_profile = context_mapping[context_type]

            # Check adaptation confidence
            confidence = self._calculate_adaptation_confidence(context_type, input_text)

            if confidence > 0.7:  # 70% confidence threshold
                old_profile = self.active_profile
                self.active_profile = target_profile

                # Record adaptation
                self.session_history.append({
                    "timestamp": time.time(),
                    "from_profile": old_profile.value,
                    "to_profile": target_profile.value,
                    "reason": f"context_adaptation:{context_type}",
                    "confidence": confidence
                })

                print(f"🎭 Context adaptation: {context_type} → {target_profile.value} (confidence: {confidence:.2f})")

                return target_profile.value

        return self.active_profile.value

    def _calculate_adaptation_confidence(self, context_type: str, input_text: str) -> float:
        """Calculate confidence score for context adaptation"""
        current_profile = self.profiles[self.active_profile]

        # Get context optimization score
        context_score = current_profile.context_optimization.get(context_type, 0.5)

        # Simple keyword matching in input text
        keywords = {
            "technical": ["code", "database", "api", "system", "implementation"],
            "casual": ["hey", "what's up", "cool", "awesome", "man"],
            "professional": ["regarding", "following up", "business", "meeting"],
            "analytical": ["analysis", "research", "data", "study", "examine"],
            "creative": ["ideas", "brainstorm", "create", "innovative", "what if"]
        }

        keyword_score = 0.0
        if input_text and context_type in keywords:
            for keyword in keywords[context_type]:
                if keyword.lower() in input_text.lower():
                    keyword_score += 0.2

        # Combine scores
        total_confidence = min(context_score + keyword_score, 1.0)

        # Cache result
        self.adaptation_cache[f"{context_type}:{hash(input_text)}"] = total_confidence

        return total_confidence

    def get_voice_prompt(self, topic: str = "", style_hints: List[str] = None) -> str:
        """Generate AI prompt for current voice profile"""
        profile = self.profiles[self.active_profile]

        # Base prompt structure
        prompt = f"Write this in Omar's voice using the {profile.profile_id} profile:\n\n"

        # Add voice characteristics
        prompt += f"Voice Characteristics:\n"
        prompt += f"- Style: {profile.characteristics.communication_style}\n"
        prompt += f"- Key phrases: {', '.join(profile.characteristics.key_phrases[:5])}\n"
        prompt += f"- Sentence length: {profile.characteristics.sentence_length:.1f} words\n"
        prompt += f"- Formality: {profile.characteristics.formality:.1f}\n"
        prompt += f"- Technical level: {profile.characteristics.technical_level:.1f}\n"
        prompt += f"- Enthusiasm: {profile.characteristics.enthusiasm:.1f}\n"

        # Add specific phrases for this profile
        if profile.profile_id == "OMAR_BASE":
            prompt += "\nUse these phrases naturally: \"basically\", \"like\", \"just\", \"actually\", \"you know\"\n"
            prompt += "Structure: Direct opening → Personal context → Analysis → Practical advice\n"
        elif profile.profile_id == "OMAR_TECH":
            prompt += "\nStart with: \"Basically, you want to think about [concept] as [framework]\"\n"
            prompt += "Use technical terms but explain them accessibly\n"
        elif profile.profile_id == "OMAR_CASUAL":
            prompt += "\nBe direct and conversational: \"man,\" \"OK so far?\" \"like,\"\n"
            prompt += "Show authentic emotion and be honest\n"

        # Add topic if provided
        if topic:
            prompt += f"\nTopic: {topic}\n"

        # Add style hints if provided
        if style_hints:
            prompt += f"Style considerations: {', '.join(style_hints)}\n"

        return prompt

    def get_profile_info(self) -> Dict[str, Any]:
        """Get current profile information"""
        profile = self.profiles[self.active_profile]
        return {
            "active_profile": self.active_profile.value,
            "description": profile.description,
            "characteristics": asdict(profile.characteristics),
            "use_cases": profile.use_cases,
            "session_stats": {
                "total_switches": len([h for h in self.session_history if h["reason"] != "context_adaptation"]),
                "adaptations": len([h for h in self.session_history if "context_adaptation" in h["reason"]]),
                "session_duration": time.time() - self.session_history[0]["timestamp"] if self.session_history else 0
            }
        }

    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all available voice profiles"""
        return [
            {
                "profile_id": profile_id.value,
                "description": profile.description,
                "use_cases": profile.use_cases[:3],  # Show first 3 use cases
                "optimization_score": max(profile.context_optimization.values())
            }
            for profile_id, profile in self.profiles.items()
        ]

    def export_profile(self, profile_name: str, format: str = "json") -> str:
        """Export voice profile data"""
        if profile_name not in [p.value for p in VoiceProfile]:
            raise ValueError(f"Unknown profile: {profile_name}")

        profile_enum = VoiceProfile(profile_name)
        profile = self.profiles[profile_enum]

        if format == "json":
            return json.dumps(asdict(profile), indent=2)
        elif format == "prompt":
            return self.get_voice_prompt()
        else:
            raise ValueError(f"Unsupported format: {format}")


# Singleton instance for global use
voice_engine = None

def get_voice_engine() -> OOSVoiceEngine:
    """Get or create voice engine instance"""
    global voice_engine
    if voice_engine is None:
        voice_engine = OOSVoiceEngine()
    return voice_engine


if __name__ == "__main__":
    # Test the voice engine
    engine = OOSVoiceEngine()

    print("🎭 OOS Voice Engine Test")
    print("=" * 40)

    # Test profile switching
    print("\n1. Testing profile switching:")
    engine.select_voice("OMAR_TECH")
    engine.select_voice("OMAR_CASUAL")
    engine.select_voice("OMAR_BASE")

    # Test context adaptation
    print("\n2. Testing context adaptation:")
    engine.adapt_to_context("technical", "Let me explain this database system")
    engine.adapt_to_context("casual", "Hey what's up with this project")
    engine.adapt_to_context("professional", "Regarding the upcoming meeting")

    # Test prompt generation
    print("\n3. Testing prompt generation:")
    prompt = engine.get_voice_prompt("machine learning", ["technical", "educational"])
    print(prompt[:200] + "...")

    # Test profile listing
    print(f"\n4. Available profiles: {len(engine.list_profiles())}")
    for profile in engine.list_profiles():
        print(f"   - {profile['profile_id']}: {profile['description']}")

    print("\n✅ Voice engine test completed successfully!")
