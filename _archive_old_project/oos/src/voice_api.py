"""
OOS Voice API Endpoints

This module implements REST API endpoints for the voice integration system,
providing programmatic access to all voice functionality.
"""

import sys
import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from oos_voice_engine import OOSVoiceEngine, VoiceProfile, get_voice_engine
from voice_commands import VoiceCommands, get_voice_commands
from voice_workflows import VoiceWorkflows, get_voice_workflows
from voice_session import VoiceSessionManager, get_session_manager
from voice_adaptation_engine import VoiceAdaptationEngine, get_adaptation_engine
from context_detector import ContextDetector, get_context_detector, ContextType


# Pydantic models for API
class VoiceProfileSelect(BaseModel):
    profile_name: str = Field(..., description="Voice profile name to select")

class ContextAdaptation(BaseModel):
    context_type: str = Field(..., description="Context type for adaptation")
    input_text: str = Field("", description="Input text for context analysis")

class VoiceAnalysis(BaseModel):
    text: str = Field(..., description="Text to analyze for voice characteristics")

class WorkflowExecution(BaseModel):
    workflow_type: str = Field(..., description="Type of workflow to execute")
    input_data: Dict[str, Any] = Field(..., description="Input data for workflow")

class SessionCreate(BaseModel):
    user_id: str = Field("default", description="User ID for session")
    session_data: Optional[Dict[str, Any]] = Field(None, description="Additional session data")

class FeedbackData(BaseModel):
    adaptation_id: str = Field(..., description="ID of the adaptation")
    success_rating: float = Field(..., ge=0.0, le=1.0, description="Success rating (0-1)")
    feedback_text: str = Field("", description="Optional feedback text")

class CommandExecution(BaseModel):
    command: str = Field(..., description="Command to execute")
    args: List[str] = Field([], description="Command arguments")


# Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: float = Field(default_factory=time.time)


# Global instances
voice_engine = None
voice_commands = None
voice_workflows = None
session_manager = None
adaptation_engine = None
context_detector = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global voice_engine, voice_commands, voice_workflows, session_manager, adaptation_engine, context_detector

    # Initialize on startup
    voice_engine = get_voice_engine()
    voice_commands = get_voice_commands()
    voice_workflows = get_voice_workflows()
    session_manager = get_session_manager()
    adaptation_engine = get_adaptation_engine()
    context_detector = get_context_detector()

    print("🎭 OOS Voice API initialized successfully")
    yield

    # Cleanup on shutdown
    print("🎭 OOS Voice API shutting down")


# Create FastAPI app
app = FastAPI(
    title="OOS Voice Integration API",
    description="REST API for voice profile management and context-aware adaptation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        success=True,
        message="OOS Voice API is healthy",
        data={
            "voice_profiles_loaded": len(voice_engine.profiles),
            "active_sessions": len(session_manager.active_sessions),
            "timestamp": time.time()
        }
    )


# Voice profile endpoints
@app.get("/api/voice/profiles", response_model=APIResponse)
async def get_voice_profiles():
    """Get all available voice profiles"""
    try:
        profiles = voice_engine.list_profiles()
        return APIResponse(
            success=True,
            message="Voice profiles retrieved successfully",
            data={"profiles": profiles}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/select", response_model=APIResponse)
async def select_voice_profile(profile_data: VoiceProfileSelect):
    """Select active voice profile"""
    try:
        success = voice_engine.select_voice(profile_data.profile_name)
        if success:
            profile_info = voice_engine.get_profile_info()
            return APIResponse(
                success=True,
                message=f"Voice profile switched to {profile_data.profile_name}",
                data={"active_profile": profile_data.profile_name, "profile_info": profile_info}
            )
        else:
            raise HTTPException(status_code=400, detail=f"Voice profile not found: {profile_data.profile_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/current", response_model=APIResponse)
async def get_current_profile():
    """Get current voice profile information"""
    try:
        profile_info = voice_engine.get_profile_info()
        return APIResponse(
            success=True,
            message="Current profile retrieved successfully",
            data=profile_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Context detection and adaptation endpoints
@app.post("/api/voice/detect-context", response_model=APIResponse)
async def detect_context(analysis_data: VoiceAnalysis):
    """Detect context from input text"""
    try:
        result = context_detector.detect_context(analysis_data.text)
        return APIResponse(
            success=True,
            message="Context detected successfully",
            data={
                "detected_context": result.detected_context.value,
                "confidence": result.confidence,
                "alternative_contexts": [(ctx.value, conf) for ctx, conf in result.alternative_contexts],
                "detected_keywords": result.detected_keywords,
                "processing_time": result.processing_time
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/adapt", response_model=APIResponse)
async def adapt_to_context(adaptation_data: ContextAdaptation, session_id: Optional[str] = None):
    """Adapt voice to specific context"""
    try:
        # Use real-time adaptation engine
        result = adaptation_engine.real_time_adaptation(
            adaptation_data.input_text,
            adaptation_data.context_type,
            session_id
        )

        return APIResponse(
            success=True,
            message="Voice adaptation processed successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/generate-prompt", response_model=APIResponse)
async def generate_voice_prompt(topic: str = "", style_hints: List[str] = None):
    """Generate AI prompt for current voice profile"""
    try:
        prompt = voice_engine.get_voice_prompt(topic, style_hints or [])
        return APIResponse(
            success=True,
            message="Voice prompt generated successfully",
            data={
                "prompt": prompt,
                "topic": topic,
                "style_hints": style_hints,
                "active_profile": voice_engine.active_profile.value
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Voice commands endpoints
@app.post("/api/voice/command", response_model=APIResponse)
async def execute_voice_command(command_data: CommandExecution):
    """Execute a voice command"""
    try:
        result = voice_commands.execute_command(command_data.command, command_data.args)
        return APIResponse(
            success=result.success,
            message=result.message,
            data={
                "command": command_data.command,
                "args": command_data.args,
                "execution_time": result.execution_time,
                "result_data": result.data
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/commands", response_model=APIResponse)
async def get_available_commands():
    """Get available voice commands"""
    try:
        commands = voice_commands.register_commands()
        command_list = {
            "available_commands": list(commands.keys()),
            "descriptions": {
                "/voice-list": "List available voice profiles",
                "/voice-use": "Switch to specific voice profile",
                "/voice-context": "Set context and adapt voice",
                "/voice-analyze": "Analyze text for voice characteristics",
                "/voice-stats": "Show voice usage statistics",
                "/voice-adapt": "Adapt voice to requirements",
                "/voice-create": "Create custom voice profile",
                "/voice-export": "Export voice profile data",
                "/voice-history": "Show voice usage history",
                "/voice-optimize": "Optimize voice for task",
                "/voice-reset": "Reset to default voice",
                "/voice-test": "Test current voice profile"
            }
        }
        return APIResponse(
            success=True,
            message="Available commands retrieved successfully",
            data=command_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Workflow endpoints
@app.post("/api/voice/workflow", response_model=APIResponse)
async def execute_voice_workflow(workflow_data: WorkflowExecution, session_id: Optional[str] = None):
    """Execute a voice-enhanced workflow"""
    try:
        result = voice_workflows.execute_workflow(workflow_data.workflow_type, workflow_data.input_data)

        # Record in session if provided
        if session_id:
            session_manager.record_workflow_execution(
                session_id,
                workflow_data.workflow_type,
                workflow_data.input_data,
                {
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "voice_prompt_length": len(result.voice_prompt) if result.voice_prompt else 0
                }
            )

        return APIResponse(
            success=result.success,
            message=result.message,
            data={
                "workflow_type": workflow_data.workflow_type,
                "voice_prompt": result.voice_prompt,
                "workflow_data": result.workflow_data,
                "execution_time": result.execution_time
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/workflows", response_model=APIResponse)
async def get_available_workflows():
    """Get available voice workflows"""
    try:
        workflows = voice_workflows.register_workflows()
        workflow_list = {
            "available_workflows": list(workflows.keys()),
            "descriptions": {
                "voice_planning": "Create project plans in your voice",
                "voice_writing": "Generate content in your voice",
                "voice_analysis": "Analyze data in your voice",
                "voice_debugging": "Debug technical issues in your voice",
                "voice_documentation": "Create documentation in your voice",
                "voice_code_review": "Review code in your voice",
                "voice_brainstorming": "Brainstorm ideas in your voice",
                "voice_meeting_summary": "Create meeting summaries in your voice",
                "voice_technical_explanation": "Explain technical concepts in your voice",
                "voice_user_communication": "Communicate with users in your voice"
            }
        }
        return APIResponse(
            success=True,
            message="Available workflows retrieved successfully",
            data=workflow_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Session management endpoints
@app.post("/api/voice/sessions", response_model=APIResponse)
async def create_voice_session(session_data: SessionCreate):
    """Create a new voice session"""
    try:
        session = session_manager.create_session(session_data.user_id, session_data.session_data)
        return APIResponse(
            success=True,
            message="Voice session created successfully",
            data={
                "session_id": session.session_id,
                "user_id": session.user_id,
                "active_profile": session.active_profile,
                "start_time": session.start_time
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/sessions/{session_id}", response_model=APIResponse)
async def get_voice_session(session_id: str):
    """Get voice session information"""
    try:
        summary = session_manager.get_session_summary(session_id)
        if summary:
            return APIResponse(
                success=True,
                message="Session retrieved successfully",
                data=summary
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/sessions/{session_id}/switch", response_model=APIResponse)
async def switch_session_voice(session_id: str, profile_data: VoiceProfileSelect):
    """Switch voice profile in session"""
    try:
        success = session_manager.switch_voice(session_id, profile_data.profile_name, "api_call")
        if success:
            return APIResponse(
                success=True,
                message=f"Voice switched in session {session_id}",
                data={"session_id": session_id, "new_profile": profile_data.profile_name}
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to switch voice profile")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/sessions/{session_id}/adapt", response_model=APIResponse)
async def adapt_session_context(session_id: str, adaptation_data: ContextAdaptation):
    """Adapt context in session"""
    try:
        adapted_profile = session_manager.adapt_to_context(
            session_id,
            adaptation_data.context_type,
            adaptation_data.input_text
        )
        return APIResponse(
            success=True,
            message=f"Context adapted in session {session_id}",
            data={
                "session_id": session_id,
                "context_type": adaptation_data.context_type,
                "adapted_profile": adapted_profile
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/voice/sessions/{session_id}", response_model=APIResponse)
async def end_voice_session(session_id: str):
    """End a voice session"""
    try:
        success = session_manager.end_session(session_id)
        if success:
            return APIResponse(
                success=True,
                message=f"Session {session_id} ended successfully",
                data={"session_id": session_id}
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analytics and insights endpoints
@app.get("/api/voice/analytics", response_model=APIResponse)
async def get_voice_analytics(time_range_hours: int = 24):
    """Get voice usage analytics"""
    try:
        analytics = session_manager.get_global_analytics(time_range_hours)
        adaptation_insights = adaptation_engine.get_adaptation_insights(time_range_hours)
        detection_stats = context_detector.get_detection_statistics()

        return APIResponse(
            success=True,
            message="Analytics retrieved successfully",
            data={
                "session_analytics": analytics,
                "adaptation_insights": adaptation_insights,
                "detection_statistics": detection_stats,
                "time_range_hours": time_range_hours
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/engine/state", response_model=APIResponse)
async def get_engine_state():
    """Get current voice engine state"""
    try:
        engine_state = voice_engine.get_profile_info()
        adaptation_state = adaptation_engine.get_current_state()
        command_stats = voice_commands.get_command_stats()
        workflow_stats = voice_workflows.get_workflow_stats()

        return APIResponse(
            success=True,
            message="Engine state retrieved successfully",
            data={
                "voice_engine": engine_state,
                "adaptation_engine": adaptation_state,
                "command_stats": command_stats,
                "workflow_stats": workflow_stats
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Feedback and learning endpoints
@app.post("/api/voice/feedback", response_model=APIResponse)
async def submit_voice_feedback(feedback_data: FeedbackData):
    """Submit feedback for voice adaptation"""
    try:
        adaptation_engine.record_user_feedback(
            feedback_data.adaptation_id,
            feedback_data.success_rating,
            feedback_data.feedback_text
        )
        return APIResponse(
            success=True,
            message="Feedback submitted successfully",
            data={
                "adaptation_id": feedback_data.adaptation_id,
                "success_rating": feedback_data.success_rating,
                "feedback_text": feedback_data.feedback_text
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice/optimize", response_model=APIResponse)
async def optimize_adaptation_engine():
    """Optimize adaptation engine parameters"""
    try:
        optimization_result = adaptation_engine.optimize_adaptation_parameters()
        return APIResponse(
            success=True,
            message="Adaptation engine optimized successfully",
            data=optimization_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export endpoints
@app.get("/api/voice/export/{profile_name}", response_model=APIResponse)
async def export_voice_profile(profile_name: str, format: str = "json"):
    """Export voice profile data"""
    try:
        exported_data = voice_engine.export_profile(profile_name, format)
        return APIResponse(
            success=True,
            message=f"Voice profile {profile_name} exported successfully",
            data={
                "profile_name": profile_name,
                "format": format,
                "exported_data": exported_data
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": f"Internal server error: {str(exc)}",
            "timestamp": time.time()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
