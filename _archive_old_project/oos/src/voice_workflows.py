"""
OOS Voice-Enhanced Workflows

This module implements voice-aware OOS workflows that enhance
existing OOS functionality with voice profile integration.
"""

import sys
import os
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from oos_voice_engine import OOSVoiceEngine, VoiceProfile, get_voice_engine
from voice_commands import VoiceCommands, get_voice_commands


@dataclass
class WorkflowResult:
    """Result of voice workflow execution"""
    success: bool
    message: str
    voice_prompt: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0


class WorkflowType(Enum):
    """Supported workflow types"""
    PLANNING = "planning"
    WRITING = "writing"
    ANALYSIS = "analysis"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"
    BRAINSTORMING = "brainstorming"
    MEETING_SUMMARY = "meeting_summary"
    TECHNICAL_EXPLANATION = "technical_explanation"
    USER_COMMUNICATION = "user_communication"


class VoiceWorkflows:
    """Voice-enhanced workflow processor for OOS"""

    def __init__(self):
        self.voice_engine = get_voice_engine()
        self.voice_commands = get_voice_commands()
        self.workflow_history = []
        self.workflow_stats = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "voice_enhancements": 0,
            "avg_execution_time": 0.0
        }

    def register_workflows(self) -> Dict[str, Callable]:
        """Register all voice-enhanced workflows"""
        return {
            "voice_planning": self.voice_planning_workflow,
            "voice_writing": self.voice_writing_workflow,
            "voice_analysis": self.voice_analysis_workflow,
            "voice_debugging": self.voice_debugging_workflow,
            "voice_documentation": self.voice_documentation_workflow,
            "voice_code_review": self.voice_code_review_workflow,
            "voice_brainstorming": self.voice_brainstorming_workflow,
            "voice_meeting_summary": self.voice_meeting_summary_workflow,
            "voice_technical_explanation": self.voice_technical_explanation_workflow,
            "voice_user_communication": self.voice_user_communication_workflow
        }

    def execute_workflow(self, workflow_type: str, input_data: Dict[str, Any]) -> WorkflowResult:
        """Execute a voice-enhanced workflow"""
        start_time = time.time()

        try:
            # Get workflow handler
            workflows = self.register_workflows()

            if workflow_type not in workflows:
                return WorkflowResult(
                    success=False,
                    message=f"Unknown workflow type: {workflow_type}",
                    execution_time=time.time() - start_time
                )

            # Auto-adapt voice based on workflow type
            self._adapt_voice_for_workflow(workflow_type)

            # Execute workflow
            handler = workflows[workflow_type]
            result = handler(input_data)

            # Update stats
            self.workflow_stats["total_workflows"] += 1
            if result.success:
                self.workflow_stats["successful_workflows"] += 1

            # Check if voice was enhanced
            if result.voice_prompt:
                self.workflow_stats["voice_enhancements"] += 1

            # Record workflow
            self.workflow_history.append({
                "timestamp": time.time(),
                "workflow_type": workflow_type,
                "input_data": input_data,
                "success": result.success,
                "voice_profile": self.voice_engine.active_profile.value,
                "execution_time": result.execution_time
            })

            # Update average execution time
            total_time = sum(w["execution_time"] for w in self.workflow_history)
            self.workflow_stats["avg_execution_time"] = total_time / len(self.workflow_history)

            return result

        except Exception as e:
            error_result = WorkflowResult(
                success=False,
                message=f"Error executing {workflow_type}: {str(e)}",
                execution_time=time.time() - start_time
            )

            self.workflow_stats["total_workflows"] += 1
            self.workflow_history.append({
                "timestamp": time.time(),
                "workflow_type": workflow_type,
                "input_data": input_data,
                "success": False,
                "voice_profile": self.voice_engine.active_profile.value,
                "execution_time": error_result.execution_time
            })

            return error_result

    def _adapt_voice_for_workflow(self, workflow_type: str):
        """Automatically adapt voice profile based on workflow type"""
        workflow_to_voice = {
            "voice_planning": VoiceProfile.OMAR_BASE,
            "voice_writing": VoiceProfile.OMAR_BASE,
            "voice_analysis": VoiceProfile.OMAR_ANALYSIS,
            "voice_debugging": VoiceProfile.OMAR_TECH,
            "voice_documentation": VoiceProfile.OMAR_PRO,
            "voice_code_review": VoiceProfile.OMAR_TECH,
            "voice_brainstorming": VoiceProfile.OMAR_CREATIVITY,
            "voice_meeting_summary": VoiceProfile.OMAR_PRO,
            "voice_technical_explanation": VoiceProfile.OMAR_TECH,
            "voice_user_communication": VoiceProfile.OMAR_BASE
        }

        if workflow_type in workflow_to_voice:
            target_voice = workflow_to_voice[workflow_type]
            if self.voice_engine.active_profile != target_voice:
                old_profile = self.voice_engine.active_profile
                self.voice_engine.active_profile = target_voice

                print(f"🎭 Auto-adapted voice for {workflow_type}: {old_profile.value} → {target_voice.value}")

    def voice_planning_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Create project plan in your voice"""
        task_description = input_data.get("task", "")
        complexity = input_data.get("complexity", "medium")
        timeline = input_data.get("timeline", "flexible")

        # Generate voice prompt
        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"creating a project plan for {task_description}",
            style_hints=["collaborative", "practical", "step-by-step"]
        )

        # Add planning-specific guidance
        voice_prompt += f"""

Create a comprehensive project plan for: {task_description}

Requirements:
- Complexity: {complexity}
- Timeline: {timeline}
- Use Omar's authentic planning style
- Be practical and actionable
- Include phases with clear deliverables
- Show your natural phrases: "basically", "like", "just", "actually"
- Mix collaborative tone with technical substance

Structure your response as:
1. Overview/Context
2. Key Phases (with timelines)
3. Resources Needed
4. Risk Assessment
5. Success Metrics

Write this exactly like Omar would create a project plan for his team.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced planning workflow for: {task_description}",
            voice_prompt=voice_prompt,
            workflow_data={
                "task": task_description,
                "complexity": complexity,
                "timeline": timeline,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_writing_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Generate content in your voice"""
        topic = input_data.get("topic", "")
        audience = input_data.get("audience", "general")
        tone = input_data.get("tone", "conversational")
        length = input_data.get("length", "medium")

        # Generate voice prompt
        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=topic,
            style_hints=[tone, audience]
        )

        voice_prompt += f"""

Write content about: {topic}

Target Audience: {audience}
Tone: {tone}
Length: {length}

Voice Requirements:
- Use Omar's natural phrases: "basically", "like", "just", "actually"
- Maintain your authentic conversational style
- Mix casual delivery with substantive content
- Be direct and honest
- Include personal examples when relevant
- End with practical takeaways

Write this exactly like Omar would explain this topic to {audience}.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced writing workflow for: {topic}",
            voice_prompt=voice_prompt,
            workflow_data={
                "topic": topic,
                "audience": audience,
                "tone": tone,
                "length": length,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_analysis_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Analyze data in your voice"""
        data_type = input_data.get("data_type", "")
        analysis_focus = input_data.get("focus", "comprehensive")
        context = input_data.get("context", "")

        # Switch to analytical voice
        self.voice_engine.active_profile = VoiceProfile.OMAR_ANALYSIS

        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"analyzing {data_type}",
            style_hints=["analytical", "detailed", "structured"]
        )

        voice_prompt += f"""

Analyze the following data:

Data Type: {data_type}
Analysis Focus: {analysis_focus}
Context: {context}

Voice Requirements:
- Use Omar's analytical voice style
- Be thorough and methodical
- Show your natural curiosity
- Use phrases: "basically", "like", "actually", "you know"
- Balance depth with accessibility
- Include your personal analytical perspective
- End with actionable insights

Provide a comprehensive analysis that sounds exactly like Omar explaining complex data.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced analysis workflow for: {data_type}",
            voice_prompt=voice_prompt,
            workflow_data={
                "data_type": data_type,
                "focus": analysis_focus,
                "context": context,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_debugging_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Debug technical issues in your voice"""
        issue = input_data.get("issue", "")
        technology = input_data.get("technology", "")
        error_context = input_data.get("context", "")

        # Switch to technical voice
        self.voice_engine.active_profile = VoiceProfile.OMAR_TECH

        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"debugging {technology}",
            style_hints=["technical", "problem-solving", "frustrated"]
        )

        voice_prompt += f"""

Debug this technical issue:

Issue: {issue}
Technology: {technology}
Context: {error_context}

Voice Requirements:
- Use Omar's technical debugging voice
- Show authentic problem-solving approach
- Be willing to show frustration with the issue
- Use natural technical phrases: "basically", "like", "implementation", "system"
- Mix directness with collaborative approach
- Include personal debugging experiences
- End with clear next steps

Debug this exactly like Omar would help a teammate solve this technical problem.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced debugging workflow for: {issue}",
            voice_prompt=voice_prompt,
            workflow_data={
                "issue": issue,
                "technology": technology,
                "context": error_context,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_documentation_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Create documentation in your voice"""
        doc_type = input_data.get("doc_type", "")
        topic = input_data.get("topic", "")
        audience = input_data.get("audience", "developers")

        # Switch to professional voice
        self.voice_engine.active_profile = VoiceProfile.OMAR_PRO

        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"creating {doc_type} documentation",
            style_hints=["professional", "clear", "structured"]
        )

        voice_prompt += f"""

Create {doc_type} documentation for: {topic}

Target Audience: {audience}

Voice Requirements:
- Use Omar's professional documentation style
- Be clear and structured
- Use professional variations of your phrases: "regarding", "following up", "basically"
- Mix professionalism with your authentic voice
- Include practical examples
- Be thorough but accessible

Document this exactly like Omar would create professional documentation for {audience}.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced documentation workflow for: {topic}",
            voice_prompt=voice_prompt,
            workflow_data={
                "doc_type": doc_type,
                "topic": topic,
                "audience": audience,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_code_review_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Review code in your voice"""
        language = input_data.get("language", "")
        review_focus = input_data.get("focus", "comprehensive")
        context = input_data.get("context", "")

        # Switch to technical voice
        self.voice_engine.active_profile = VoiceProfile.OMAR_TECH

        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"code review for {language}",
            style_hints=["technical", "constructive", "collaborative"]
        )

        voice_prompt += f"""

Review this {language} code:

Review Focus: {review_focus}
Context: {context}

Voice Requirements:
- Use Omar's technical code review voice
- Be constructive and collaborative
- Use natural technical phrases: "basically", "like", "implementation", "system"
- Show your authentic code review approach
- Balance criticism with encouragement
- Include specific improvement suggestions
- End with clear recommendations

Review this code exactly like Omar would review code with his teammates.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced code review workflow for {language}",
            voice_prompt=voice_prompt,
            workflow_data={
                "language": language,
                "focus": review_focus,
                "context": context,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_brainstorming_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Brainstorm ideas in your voice"""
        topic = input_data.get("topic", "")
        constraints = input_data.get("constraints", "")
        ideation_type = input_data.get("type", "open")

        # Switch to creative voice
        self.voice_engine.active_profile = VoiceProfile.OMAR_CREATIVITY

        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"brainstorming {topic}",
            style_hints=["creative", "enthusiastic", "divergent"]
        )

        voice_prompt += f"""

Brainstorm ideas for: {topic}

Constraints: {constraints}
Ideation Type: {ideation_type}

Voice Requirements:
- Use Omar's creative brainstorming voice
- Show authentic enthusiasm and curiosity
- Use creative phrases: "what if", "ideas", "like", "basically"
- Be willing to suggest unconventional ideas
- Mix creativity with practical thinking
- Include personal creative experiences
- End with actionable next steps

Brainstorm exactly like Omar would ideate with his team on {topic}.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced brainstorming workflow for: {topic}",
            voice_prompt=voice_prompt,
            workflow_data={
                "topic": topic,
                "constraints": constraints,
                "type": ideation_type,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_meeting_summary_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Create meeting summary in your voice"""
        meeting_type = input_data.get("meeting_type", "")
        key_points = input_data.get("key_points", [])
        action_items = input_data.get("action_items", [])

        # Switch to professional voice
        self.voice_engine.active_profile = VoiceProfile.OMAR_PRO

        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"meeting summary for {meeting_type}",
            style_hints=["professional", "concise", "action-oriented"]
        )

        voice_prompt += f"""

Create a meeting summary:

Meeting Type: {meeting_type}
Key Points: {', '.join(key_points[:5])}{'...' if len(key_points) > 5 else ''}
Action Items: {', '.join(action_items[:5])}{'...' if len(action_items) > 5 else ''}

Voice Requirements:
- Use Omar's professional meeting summary style
- Be clear and action-oriented
- Use professional phrases: "regarding", "following up", "basically"
- Mix professionalism with your authentic voice
- Focus on outcomes and next steps
- Be concise but comprehensive

Summarize this meeting exactly like Omar would summarize for his team.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced meeting summary for: {meeting_type}",
            voice_prompt=voice_prompt,
            workflow_data={
                "meeting_type": meeting_type,
                "key_points": key_points,
                "action_items": action_items,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_technical_explanation_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Explain technical concepts in your voice"""
        concept = input_data.get("concept", "")
        audience = input_data.get("audience", "mixed")
        depth = input_data.get("depth", "medium")

        # Switch to technical voice
        self.voice_engine.active_profile = VoiceProfile.OMAR_TECH

        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"explaining {concept}",
            style_hints=["technical", "educational", "accessible"]
        )

        voice_prompt += f"""

Explain this technical concept:

Concept: {concept}
Target Audience: {audience}
Depth Level: {depth}

Voice Requirements:
- Use Omar's technical explanation voice
- Start with: "Basically, you want to think about {concept} as..."
- Use analogies and frameworks
- Mix technical accuracy with accessibility
- Use natural technical phrases: "basically", "like", "implementation", "system"
- Show your authentic teaching style
- End with practical applications

Explain this concept exactly like Omar would teach it to {audience}.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced technical explanation for: {concept}",
            voice_prompt=voice_prompt,
            workflow_data={
                "concept": concept,
                "audience": audience,
                "depth": depth,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def voice_user_communication_workflow(self, input_data: Dict[str, Any]) -> WorkflowResult:
        """Communicate with users in your voice"""
        message_type = input_data.get("message_type", "")
        user_situation = input_data.get("user_situation", "")
        goal = input_data.get("goal", "help")

        # Use base voice for user communication
        self.voice_engine.active_profile = VoiceProfile.OMAR_BASE

        voice_prompt = self.voice_engine.get_voice_prompt(
            topic=f"user communication - {message_type}",
            style_hints=["empathetic", "helpful", "clear"]
        )

        voice_prompt += f"""

Communicate with a user:

Message Type: {message_type}
User Situation: {user_situation}
Communication Goal: {goal}

Voice Requirements:
- Use Omar's authentic user communication voice
- Be empathetic and collaborative
- Use natural phrases: "basically", "like", "just", "actually", "you know"
- Show your authentic desire to help
- Mix clarity with personal approach
- Be direct but supportive
- End with clear next steps

Communicate this exactly like Omar would help a user with {user_situation}.
"""

        return WorkflowResult(
            success=True,
            message=f"🎭 Voice-enhanced user communication for: {message_type}",
            voice_prompt=voice_prompt,
            workflow_data={
                "message_type": message_type,
                "user_situation": user_situation,
                "goal": goal,
                "voice_profile": self.voice_engine.active_profile.value
            }
        )

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        return {
            **self.workflow_stats,
            "recent_workflows": self.workflow_history[-5:],
            "workflow_distribution": self._get_workflow_distribution(),
            "voice_profile_usage": self._get_voice_profile_usage()
        }

    def _get_workflow_distribution(self) -> Dict[str, int]:
        """Get distribution of workflow usage"""
        distribution = {}
        for workflow in self.workflow_history:
            workflow_type = workflow["workflow_type"]
            distribution[workflow_type] = distribution.get(workflow_type, 0) + 1
        return distribution

    def _get_voice_profile_usage(self) -> Dict[str, int]:
        """Get voice profile usage across workflows"""
        usage = {}
        for workflow in self.workflow_history:
            profile = workflow["voice_profile"]
            usage[profile] = usage.get(profile, 0) + 1
        return usage


# Global workflow processor instance
voice_workflows = None

def get_voice_workflows() -> VoiceWorkflows:
    """Get or create voice workflows instance"""
    global voice_workflows
    if voice_workflows is None:
        voice_workflows = VoiceWorkflows()
    return voice_workflows


if __name__ == "__main__":
    # Test voice workflows
    workflows = VoiceWorkflows()

    print("🎭 OOS Voice Workflows Test")
    print("=" * 40)

    test_workflows = [
        ("voice_planning", {"task": "implement user authentication", "complexity": "medium"}),
        ("voice_writing", {"topic": "machine learning basics", "audience": "beginners"}),
        ("voice_analysis", {"data_type": "user engagement metrics", "focus": "trends"}),
        ("voice_debugging", {"issue": "database connection timeout", "technology": "PostgreSQL"}),
        ("voice_documentation", {"doc_type": "API reference", "topic": "authentication endpoints"}),
    ]

    for workflow_type, input_data in test_workflows:
        print(f"\nTesting: {workflow_type}")
        result = workflows.execute_workflow(workflow_type, input_data)
        print(f"Result: {'✅' if result.success else '❌'}")
        print(f"Message: {result.message}")
        print(f"Voice profile: {result.workflow_data['voice_profile'] if result.workflow_data else 'N/A'}")
        print(f"Voice prompt length: {len(result.voice_prompt) if result.voice_prompt else 0}")

    print("\n✅ Voice workflows test completed!")
