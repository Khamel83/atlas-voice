"""
OOS Voice Commands Integration

This module implements voice-aware slash commands for OOS,
enabling seamless voice profile management and adaptation.
"""

import sys
import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from oos_voice_engine import OOSVoiceEngine, VoiceProfile, get_voice_engine


@dataclass
class CommandResult:
    """Result of voice command execution"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0


class VoiceCommands:
    """Voice command processor for OOS integration"""

    def __init__(self):
        self.voice_engine = get_voice_engine()
        self.command_history = []
        self.command_stats = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "avg_execution_time": 0.0
        }

    def register_commands(self) -> Dict[str, callable]:
        """Register all voice-related OOS commands"""
        return {
            "/voice-list": self.list_voices,
            "/voice-use": self.use_voice,
            "/voice-context": self.set_context,
            "/voice-analyze": self.analyze_voice,
            "/voice-stats": self.voice_stats,
            "/voice-adapt": self.adapt_voice,
            "/voice-create": self.create_voice,
            "/voice-export": self.export_voice,
            "/voice-history": self.voice_history,
            "/voice-optimize": self.optimize_voice,
            "/voice-reset": self.reset_voice,
            "/voice-test": self.test_voice
        }

    def execute_command(self, command: str, args: List[str] = None) -> CommandResult:
        """Execute a voice command with timing and stats"""
        start_time = time.time()
        args = args or []

        try:
            # Get command handler
            commands = self.register_commands()
            command_key = command.lower()

            if command_key not in commands:
                return CommandResult(
                    success=False,
                    message=f"Unknown voice command: {command}",
                    execution_time=time.time() - start_time
                )

            # Execute command
            handler = commands[command_key]
            result = handler(args)

            # Update stats
            self.command_stats["total_commands"] += 1
            if result.success:
                self.command_stats["successful_commands"] += 1
            else:
                self.command_stats["failed_commands"] += 1

            # Record command
            self.command_history.append({
                "timestamp": time.time(),
                "command": command,
                "args": args,
                "success": result.success,
                "execution_time": result.execution_time
            })

            # Update average execution time
            total_time = sum(h["execution_time"] for h in self.command_history)
            self.command_stats["avg_execution_time"] = total_time / len(self.command_history)

            return result

        except Exception as e:
            error_result = CommandResult(
                success=False,
                message=f"Error executing {command}: {str(e)}",
                execution_time=time.time() - start_time
            )

            self.command_stats["total_commands"] += 1
            self.command_stats["failed_commands"] += 1
            self.command_history.append({
                "timestamp": time.time(),
                "command": command,
                "args": args,
                "success": False,
                "execution_time": error_result.execution_time
            })

            return error_result

    def list_voices(self, args: List[str]) -> CommandResult:
        """List available voice profiles"""
        try:
            profiles = self.voice_engine.list_profiles()

            output = "🎭 Available Voice Profiles:\n\n"
            for profile in profiles:
                output += f"**{profile['profile_id']}**: {profile['description']}\n"
                output += f"   - Use cases: {', '.join(profile['use_cases'])}\n"
                output += f"   - Optimization score: {profile['optimization_score']:.2f}\n\n"

            return CommandResult(
                success=True,
                message=output,
                data={"profiles": profiles}
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to list voices: {str(e)}"
            )

    def use_voice(self, args: List[str]) -> CommandResult:
        """Switch to specific voice profile"""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: /voice-use [profile_name]\nAvailable profiles: OMAR_BASE, OMAR_TECH, OMAR_CASUAL, OMAR_PRO, OMAR_ANALYSIS, OMAR_CREATIVITY"
            )

        profile_name = args[0].upper()

        if self.voice_engine.select_voice(profile_name):
            profile_info = self.voice_engine.get_profile_info()
            return CommandResult(
                success=True,
                message=f"🎭 Voice profile switched to: {profile_name}\n\n{profile_info['description']}",
                data={"active_profile": profile_name, "profile_info": profile_info}
            )
        else:
            return CommandResult(
                success=False,
                message=f"❌ Voice profile not found: {profile_name}\nUse /voice-list to see available profiles"
            )

    def set_context(self, args: List[str]) -> CommandResult:
        """Set context and adapt voice accordingly"""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: /voice-context [context_type]\nAvailable contexts: technical, casual, professional, analytical, creative, programming, debugging, business, social, research, brainstorming"
            )

        context_type = args[0].lower()
        input_text = " ".join(args[1:]) if len(args) > 1 else ""

        current_profile = self.voice_engine.adapt_to_context(context_type, input_text)

        return CommandResult(
            success=True,
            message=f"🎭 Context set to: {context_type}\n🎭 Voice adapted to: {current_profile}",
            data={
                "context_type": context_type,
                "adapted_profile": current_profile,
                "input_text": input_text
            }
        )

    def analyze_voice(self, args: List[str]) -> CommandResult:
        """Analyze text for voice characteristics"""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: /voice-analyze [text to analyze]"
            )

        text = " ".join(args)

        # Get current profile characteristics
        profile_info = self.voice_engine.get_profile_info()
        characteristics = profile_info["characteristics"]

        # Simple analysis (can be enhanced with actual NLP)
        word_count = len(text.split())
        avg_sentence_length = word_count / max(len(text.split('.')), 1)

        # Check for key phrases
        key_phrases_found = []
        for phrase in characteristics["key_phrases"]:
            if phrase.lower() in text.lower():
                key_phrases_found.append(phrase)

        analysis = {
            "word_count": word_count,
            "avg_sentence_length": avg_sentence_length,
            "key_phrases_found": key_phrases_found,
            "current_profile": profile_info["active_profile"],
            "voice_match_score": len(key_phrases_found) / len(characteristics["key_phrases"])
        }

        output = f"🎭 Voice Analysis:\n"
        output += f"- Words: {word_count}\n"
        output += f"- Avg sentence length: {avg_sentence_length:.1f}\n"
        output += f"- Key phrases found: {', '.join(key_phrases_found) if key_phrases_found else 'None'}\n"
        output += f"- Current profile: {profile_info['active_profile']}\n"
        output += f"- Voice match: {analysis['voice_match_score']:.1%}"

        return CommandResult(
            success=True,
            message=output,
            data=analysis
        )

    def voice_stats(self, args: List[str]) -> CommandResult:
        """Show voice usage statistics"""
        profile_info = self.voice_engine.get_profile_info()
        session_stats = profile_info["session_stats"]

        output = "🎭 Voice Usage Statistics:\n\n"
        output += f"**Current Profile**: {profile_info['active_profile']}\n"
        output += f"**Description**: {profile_info['description']}\n\n"

        output += "📊 Session Statistics:\n"
        output += f"- Manual switches: {session_stats['total_switches']}\n"
        output += f"- Auto-adaptations: {session_stats['adaptations']}\n"
        output += f"- Session duration: {session_stats['session_duration']:.1f}s\n\n"

        output += "🎯 Current Profile Characteristics:\n"
        for key, value in profile_info["characteristics"].items():
            if isinstance(value, list):
                output += f"- {key}: {', '.join(value[:3])}{'...' if len(value) > 3 else ''}\n"
            else:
                output += f"- {key}: {value}\n"

        return CommandResult(
            success=True,
            message=output,
            data=profile_info
        )

    def adapt_voice(self, args: List[str]) -> CommandResult:
        """Adapt voice to specific requirements"""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: /voice-adapt [adaptation_type] [parameters]\nTypes: technical, casual, professional, analytical, creative"
            )

        adaptation_type = args[0].lower()
        parameters = args[1:]

        # Get current profile
        current_profile = self.voice_engine.active_profile
        profile_data = self.voice_engine.profiles[current_profile]

        # Apply adaptation rules
        if adaptation_type in profile_data.adaptation_rules:
            rules = profile_data.adaptation_rules[adaptation_type]

            # Create adapted characteristics
            adapted_chars = profile_data.characteristics
            for param, adjustment in rules.items():
                if hasattr(adapted_chars, param):
                    current_value = getattr(adapted_chars, param)
                    setattr(adapted_chars, param, max(0, min(1, current_value + adjustment)))

            return CommandResult(
                success=True,
                message=f"🎭 Voice adapted for {adaptation_type}\nApplied rules: {rules}",
                data={
                    "adaptation_type": adaptation_type,
                    "rules_applied": rules,
                    "new_characteristics": adapted_chars.__dict__
                }
            )
        else:
            return CommandResult(
                success=False,
                message=f"No adaptation rules found for: {adaptation_type}"
            )

    def create_voice(self, args: List[str]) -> CommandResult:
        """Create custom voice profile (simplified)"""
        if len(args) < 2:
            return CommandResult(
                success=False,
                message="Usage: /voice-create [profile_name] [description]"
            )

        profile_name = args[0].upper()
        description = " ".join(args[1:])

        # Basic validation
        if profile_name in [p.value for p in VoiceProfile]:
            return CommandResult(
                success=False,
                message=f"Profile {profile_name} already exists"
            )

        return CommandResult(
            success=True,
            message=f"🎭 Custom voice profile creation initiated: {profile_name}\nDescription: {description}\n\nNote: Full custom profile creation requires advanced configuration.",
            data={
                "profile_name": profile_name,
                "description": description,
                "status": "initiated"
            }
        )

    def export_voice(self, args: List[str]) -> CommandResult:
        """Export voice profile"""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: /voice-export [profile_name] [format:json|prompt]"
            )

        profile_name = args[0]
        format_type = args[1] if len(args) > 1 else "json"

        try:
            exported_data = self.voice_engine.export_profile(profile_name, format_type)

            return CommandResult(
                success=True,
                message=f"🎭 Voice profile '{profile_name}' exported in {format_type} format",
                data={
                    "profile_name": profile_name,
                    "format": format_type,
                    "exported_data": exported_data
                }
            )
        except ValueError as e:
            return CommandResult(
                success=False,
                message=str(e)
            )

    def voice_history(self, args: List[str]) -> CommandResult:
        """Show voice usage history"""
        history = self.voice_engine.session_history[-10:]  # Last 10 events

        if not history:
            return CommandResult(
                success=True,
                message="🎭 No voice activity in current session"
            )

        output = "🎭 Recent Voice Activity:\n\n"
        for event in history:
            timestamp = time.strftime("%H:%M:%S", time.localtime(event["timestamp"]))
            if event["reason"] == "manual_selection":
                output += f"{timestamp} - Manual switch: {event['from_profile']} → {event['to_profile']}\n"
            elif "context_adaptation" in event["reason"]:
                context = event["reason"].split(":")[1]
                confidence = event.get("confidence", 0)
                output += f"{timestamp} - Context '{context}': {event['from_profile']} → {event['to_profile']} ({confidence:.0%})\n"

        return CommandResult(
            success=True,
            message=output,
            data={"recent_history": history}
        )

    def optimize_voice(self, args: List[str]) -> CommandResult:
        """Optimize voice for current task"""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: /voice-optimize [task_type]\nTypes: writing, analysis, technical, creative, casual"
            )

        task_type = args[0].lower()

        # Task to profile mapping
        task_mapping = {
            "writing": VoiceProfile.OMAR_BASE,
            "analysis": VoiceProfile.OMAR_ANALYSIS,
            "technical": VoiceProfile.OMAR_TECH,
            "creative": VoiceProfile.OMAR_CREATIVITY,
            "casual": VoiceProfile.OMAR_CASUAL
        }

        if task_type in task_mapping:
            target_profile = task_mapping[task_type]
            old_profile = self.voice_engine.active_profile

            self.voice_engine.active_profile = target_profile

            return CommandResult(
                success=True,
                message=f"🎭 Voice optimized for {task_type}: {old_profile.value} → {target_profile.value}",
                data={
                    "task_type": task_type,
                    "optimized_profile": target_profile.value,
                    "previous_profile": old_profile.value
                }
            )
        else:
            return CommandResult(
                success=False,
                message=f"Unknown task type: {task_type}"
            )

    def reset_voice(self, args: List[str]) -> CommandResult:
        """Reset to default voice profile"""
        old_profile = self.voice_engine.active_profile
        self.voice_engine.active_profile = VoiceProfile.OMAR_BASE

        return CommandResult(
            success=True,
            message=f"🎭 Voice reset to default: {old_profile.value} → OMAR_BASE",
            data={
                "reset_from": old_profile.value,
                "reset_to": "OMAR_BASE"
            }
        )

    def test_voice(self, args: List[str]) -> CommandResult:
        """Test current voice with sample text"""
        test_topics = {
            "technical": "Explain how databases work",
            "casual": "What are your weekend plans?",
            "professional": "Project status update",
            "creative": "New ideas for the product",
            "analytical": "Analysis of market trends"
        }

        topic = args[0] if args else "general"

        if topic in test_topics:
            sample_text = test_topics[topic]
        else:
            sample_text = f"Sample text about {topic}"

        # Generate prompt for current voice
        prompt = self.voice_engine.get_voice_prompt(sample_text)

        return CommandResult(
            success=True,
            message=f"🎭 Voice test - {topic} topic\n\nPrompt generated for {self.voice_engine.active_profile.value}:\n\n{prompt[:300]}...",
            data={
                "test_topic": topic,
                "sample_text": sample_text,
                "generated_prompt": prompt,
                "active_profile": self.voice_engine.active_profile.value
            }
        )

    def get_command_stats(self) -> Dict[str, Any]:
        """Get command execution statistics"""
        return {
            **self.command_stats,
            "recent_commands": self.command_history[-5:],
            "command_distribution": self._get_command_distribution()
        }

    def _get_command_distribution(self) -> Dict[str, int]:
        """Get distribution of command usage"""
        distribution = {}
        for cmd in self.command_history:
            command = cmd["command"]
            distribution[command] = distribution.get(command, 0) + 1
        return distribution


# Global command processor instance
voice_commands = None

def get_voice_commands() -> VoiceCommands:
    """Get or create voice commands instance"""
    global voice_commands
    if voice_commands is None:
        voice_commands = VoiceCommands()
    return voice_commands


if __name__ == "__main__":
    # Test voice commands
    commands = VoiceCommands()

    print("🎭 OOS Voice Commands Test")
    print("=" * 40)

    test_commands = [
        ("/voice-list", []),
        ("/voice-use", ["OMAR_TECH"]),
        ("/voice-context", ["technical", "explain databases"]),
        ("/voice-stats", []),
        ("/voice-test", ["technical"]),
        ("/voice-history", [])
    ]

    for command, args in test_commands:
        print(f"\nTesting: {command} {args}")
        result = commands.execute_command(command, args)
        print(f"Result: {'✅' if result.success else '❌'}")
        print(f"Message: {result.message[:100]}...")
        print(f"Execution time: {result.execution_time:.3f}s")

    print("\n✅ Voice commands test completed!")
