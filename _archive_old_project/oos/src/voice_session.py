"""
OOS Voice Session Management

This module implements advanced session management for voice profiles,
including persistence, adaptation, and multi-session support.
"""

import sys
import os
import json
import time
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

from oos_voice_engine import OOSVoiceEngine, VoiceProfile, get_voice_engine


@dataclass
class SessionEvent:
    """Individual session event"""
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    voice_profile: str


@dataclass
class VoiceSession:
    """Complete voice session data"""
    session_id: str
    user_id: str
    start_time: float
    last_activity: float
    active_profile: str
    context_stack: List[str]
    events: List[SessionEvent]
    adaptations: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    session_data: Dict[str, Any]


class VoiceSessionManager:
    """Advanced voice session management"""

    def __init__(self, db_path: str = "/tmp/voice_sessions.db"):
        self.db_path = db_path
        self.voice_engine = get_voice_engine()
        self.active_sessions = {}
        self.session_stats = {
            "total_sessions": 0,
            "active_sessions": 0,
            "avg_session_duration": 0.0,
            "total_adaptations": 0
        }

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize session database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time REAL,
                last_activity REAL,
                active_profile TEXT,
                context_stack TEXT,
                adaptations TEXT,
                performance_metrics TEXT,
                session_data TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # Create session events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp REAL,
                event_type TEXT,
                event_data TEXT,
                voice_profile TEXT,
                FOREIGN KEY (session_id) REFERENCES voice_sessions (session_id)
            )
        ''')

        # Create voice usage analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_usage_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                voice_profile TEXT,
                context_type TEXT,
                adaptation_reason TEXT,
                confidence REAL,
                timestamp REAL,
                FOREIGN KEY (session_id) REFERENCES voice_sessions (session_id)
            )
        ''')

        conn.commit()
        conn.close()

    def create_session(self, user_id: str = "default", session_data: Dict[str, Any] = None) -> VoiceSession:
        """Create a new voice session"""
        session_id = f"voice_session_{int(time.time())}_{user_id}"

        session = VoiceSession(
            session_id=session_id,
            user_id=user_id,
            start_time=time.time(),
            last_activity=time.time(),
            active_profile=self.voice_engine.active_profile.value,
            context_stack=[],
            events=[],
            adaptations=[],
            performance_metrics={},
            session_data=session_data or {}
        )

        # Store session
        self.active_sessions[session_id] = session
        self._save_session(session)

        # Record session creation event
        self._record_event(session_id, "session_created", {
            "user_id": user_id,
            "initial_profile": session.active_profile
        })

        # Update stats
        self.session_stats["total_sessions"] += 1
        self.session_stats["active_sessions"] += 1

        print(f"🎭 Voice session created: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[VoiceSession]:
        """Get session by ID"""
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Load from database
        session = self._load_session(session_id)
        if session:
            self.active_sessions[session_id] = session
        return session

    def switch_voice(self, session_id: str, profile_name: str, reason: str = "") -> bool:
        """Switch voice profile in session"""
        session = self.get_session(session_id)
        if not session:
            return False

        old_profile = session.active_profile

        # Switch voice in engine
        if self.voice_engine.select_voice(profile_name):
            session.active_profile = profile_name
            session.last_activity = time.time()

            # Record adaptation
            adaptation = {
                "timestamp": time.time(),
                "from_profile": old_profile,
                "to_profile": profile_name,
                "reason": reason or "manual_switch",
                "confidence": 1.0
            }
            session.adaptations.append(adaptation)

            # Record event
            self._record_event(session_id, "voice_switch", {
                "from_profile": old_profile,
                "to_profile": profile_name,
                "reason": reason
            })

            # Save session
            self._save_session(session)

            # Update analytics
            self._record_usage_analytics(session_id, profile_name, "manual_switch", reason, 1.0)

            print(f"🎭 Session {session_id}: Voice switched {old_profile} → {profile_name}")
            return True

        return False

    def adapt_to_context(self, session_id: str, context_type: str, input_text: str = "") -> str:
        """Adapt voice to context in session"""
        session = self.get_session(session_id)
        if not session:
            return ""

        # Add to context stack
        if context_type not in session.context_stack:
            session.context_stack.append(context_type)
            session.context_stack = session.context_stack[-5:]  # Keep last 5 contexts

        # Adapt voice in engine
        adapted_profile = self.voice_engine.adapt_to_context(context_type, input_text)

        if adapted_profile != session.active_profile:
            old_profile = session.active_profile
            session.active_profile = adapted_profile
            session.last_activity = time.time()

            # Get adaptation confidence
            confidence = self.voice_engine._calculate_adaptation_confidence(context_type, input_text)

            # Record adaptation
            adaptation = {
                "timestamp": time.time(),
                "from_profile": old_profile,
                "to_profile": adapted_profile,
                "reason": f"context_adaptation:{context_type}",
                "confidence": confidence
            }
            session.adaptations.append(adaptation)

            # Record event
            self._record_event(session_id, "context_adaptation", {
                "context_type": context_type,
                "from_profile": old_profile,
                "to_profile": adapted_profile,
                "confidence": confidence,
                "input_text": input_text[:100] + "..." if len(input_text) > 100 else input_text
            })

            # Save session
            self._save_session(session)

            # Update analytics
            self._record_usage_analytics(session_id, adapted_profile, context_type, f"auto_adapt:{context_type}", confidence)

            # Update stats
            self.session_stats["total_adaptations"] += 1

            print(f"🎭 Session {session_id}: Context adapted {old_profile} → {adapted_profile} ({confidence:.0%})")

        return adapted_profile

    def record_workflow_execution(self, session_id: str, workflow_type: str, input_data: Dict[str, Any], result_data: Dict[str, Any]):
        """Record workflow execution in session"""
        session = self.get_session(session_id)
        if not session:
            return

        session.last_activity = time.time()

        # Record event
        self._record_event(session_id, "workflow_execution", {
            "workflow_type": workflow_type,
            "input_data": input_data,
            "result_data": result_data,
            "voice_profile": session.active_profile
        })

        # Update performance metrics
        execution_time = result_data.get("execution_time", 0)
        success = result_data.get("success", False)

        if workflow_type not in session.performance_metrics:
            session.performance_metrics[workflow_type] = {
                "executions": 0,
                "successful": 0,
                "total_time": 0,
                "avg_time": 0
            }

        metrics = session.performance_metrics[workflow_type]
        metrics["executions"] += 1
        if success:
            metrics["successful"] += 1
        metrics["total_time"] += execution_time
        metrics["avg_time"] = metrics["total_time"] / metrics["executions"]

        # Save session
        self._save_session(session)

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        session = self.get_session(session_id)
        if not session:
            return {}

        duration = time.time() - session.start_time
        total_events = len(session.events)
        total_adaptations = len(session.adaptations)

        # Calculate profile usage
        profile_usage = {}
        for event in session.events:
            if event.voice_profile:
                profile_usage[event.voice_profile] = profile_usage.get(event.voice_profile, 0) + 1

        # Calculate adaptation stats
        manual_switches = len([a for a in session.adaptations if a["reason"] == "manual_switch"])
        auto_adaptations = len([a for a in session.adaptations if "context_adaptation" in a["reason"]])
        avg_confidence = sum(a.get("confidence", 0) for a in session.adaptations) / max(total_adaptations, 1)

        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "duration_seconds": duration,
            "duration_formatted": str(timedelta(seconds=int(duration))),
            "active_profile": session.active_profile,
            "context_stack": session.context_stack,
            "total_events": total_events,
            "total_adaptations": total_adaptations,
            "manual_switches": manual_switches,
            "auto_adaptations": auto_adaptations,
            "avg_adaptation_confidence": avg_confidence,
            "profile_usage": profile_usage,
            "performance_metrics": session.performance_metrics,
            "is_active": session_id in self.active_sessions
        }

    def end_session(self, session_id: str) -> bool:
        """End a voice session"""
        session = self.get_session(session_id)
        if not session:
            return False

        # Record session end event
        self._record_event(session_id, "session_ended", {
            "duration": time.time() - session.start_time,
            "final_profile": session.active_profile,
            "total_events": len(session.events),
            "total_adaptations": len(session.adaptations)
        })

        # Remove from active sessions
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        # Update session in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE voice_sessions SET is_active = 0 WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

        # Update stats
        self.session_stats["active_sessions"] -= 1

        print(f"🎭 Voice session ended: {session_id}")
        return True

    def cleanup_inactive_sessions(self, timeout_hours: int = 24):
        """Clean up inactive sessions"""
        cutoff_time = time.time() - (timeout_hours * 3600)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Find inactive sessions
        cursor.execute("""
            SELECT session_id FROM voice_sessions
            WHERE is_active = 1 AND last_activity < ?
        """, (cutoff_time,))

        inactive_sessions = cursor.fetchall()

        for (session_id,) in inactive_sessions:
            self.end_session(session_id)

        conn.close()

        if inactive_sessions:
            print(f"🎭 Cleaned up {len(inactive_sessions)} inactive sessions")

    def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sessions for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, start_time, last_activity, active_profile
            FROM voice_sessions
            WHERE user_id = ?
            ORDER BY start_time DESC
            LIMIT ?
        """, (user_id, limit))

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "session_id": row[0],
                "start_time": row[1],
                "last_activity": row[2],
                "active_profile": row[3]
            })

        conn.close()
        return sessions

    def get_global_analytics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get global voice usage analytics"""
        cutoff_time = time.time() - (time_range_hours * 3600)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get profile usage
        cursor.execute("""
            SELECT voice_profile, COUNT(*) as usage_count
            FROM voice_usage_analytics
            WHERE timestamp > ?
            GROUP BY voice_profile
            ORDER BY usage_count DESC
        """, (cutoff_time,))

        profile_usage = dict(cursor.fetchall())

        # Get context adaptation stats
        cursor.execute("""
            SELECT context_type, AVG(confidence) as avg_confidence, COUNT(*) as adaptations
            FROM voice_usage_analytics
            WHERE timestamp > ? AND context_type IS NOT NULL
            GROUP BY context_type
            ORDER BY adaptations DESC
        """, (cutoff_time,))

        context_stats = []
        for row in cursor.fetchall():
            context_stats.append({
                "context_type": row[0],
                "avg_confidence": row[1],
                "adaptations": row[2]
            })

        # Get total sessions and adaptations
        cursor.execute("""
            SELECT COUNT(*) as total_sessions,
                   COUNT(DISTINCT user_id) as unique_users
            FROM voice_sessions
            WHERE start_time > ?
        """, (cutoff_time,))

        session_stats = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*) as total_adaptations
            FROM voice_usage_analytics
            WHERE timestamp > ?
        """, (cutoff_time,))

        adaptation_count = cursor.fetchone()[0]

        conn.close()

        return {
            "time_range_hours": time_range_hours,
            "total_sessions": session_stats[0],
            "unique_users": session_stats[1],
            "total_adaptations": adaptation_count,
            "profile_usage": profile_usage,
            "context_adaptations": context_stats,
            "active_sessions": len(self.active_sessions)
        }

    def _save_session(self, session: VoiceSession):
        """Save session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO voice_sessions
            (session_id, user_id, start_time, last_activity, active_profile,
             context_stack, adaptations, performance_metrics, session_data, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.user_id,
            session.start_time,
            session.last_activity,
            session.active_profile,
            json.dumps(session.context_stack),
            json.dumps(session.adaptations),
            json.dumps(session.performance_metrics),
            json.dumps(session.session_data),
            session.session_id in self.active_sessions
        ))

        conn.commit()
        conn.close()

    def _load_session(self, session_id: str) -> Optional[VoiceSession]:
        """Load session from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, user_id, start_time, last_activity, active_profile,
                   context_stack, adaptations, performance_metrics, session_data
            FROM voice_sessions
            WHERE session_id = ?
        """, (session_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            # Load events for this session
            events = self._load_session_events(session_id)

            return VoiceSession(
                session_id=row[0],
                user_id=row[1],
                start_time=row[2],
                last_activity=row[3],
                active_profile=row[4],
                context_stack=json.loads(row[5]),
                adaptations=json.loads(row[6]),
                performance_metrics=json.loads(row[7]),
                session_data=json.loads(row[8]),
                events=events
            )

        return None

    def _load_session_events(self, session_id: str) -> List[SessionEvent]:
        """Load events for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, event_type, event_data, voice_profile
            FROM session_events
            WHERE session_id = ?
            ORDER BY timestamp
        """, (session_id,))

        events = []
        for row in cursor.fetchall():
            events.append(SessionEvent(
                timestamp=row[0],
                event_type=row[1],
                data=json.loads(row[2]),
                voice_profile=row[3]
            ))

        conn.close()
        return events

    def _record_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Record session event"""
        session = self.get_session(session_id)
        if not session:
            return

        event = SessionEvent(
            timestamp=time.time(),
            event_type=event_type,
            data=data,
            voice_profile=self.voice_engine.active_profile.value
        )

        session.events.append(event)
        session.last_activity = time.time()

        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO session_events
            (session_id, timestamp, event_type, event_data, voice_profile)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            event.timestamp,
            event.event_type,
            json.dumps(event.data),
            event.voice_profile
        ))

        conn.commit()
        conn.close()

    def _record_usage_analytics(self, session_id: str, voice_profile: str, context_type: str, adaptation_reason: str, confidence: float):
        """Record voice usage analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO voice_usage_analytics
            (session_id, voice_profile, context_type, adaptation_reason, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            voice_profile,
            context_type,
            adaptation_reason,
            confidence,
            time.time()
        ))

        conn.commit()
        conn.close()


# Global session manager instance
session_manager = None

def get_session_manager() -> VoiceSessionManager:
    """Get or create session manager instance"""
    global session_manager
    if session_manager is None:
        session_manager = VoiceSessionManager()
    return session_manager


if __name__ == "__main__":
    # Test session management
    manager = VoiceSessionManager()

    print("🎭 OOS Voice Session Management Test")
    print("=" * 40)

    # Create session
    session = manager.create_session("test_user", {"test": True})
    print(f"Created session: {session.session_id}")

    # Test voice switching
    manager.switch_voice(session.session_id, "OMAR_TECH", "testing")
    manager.switch_voice(session.session_id, "OMAR_CASUAL", "casual test")

    # Test context adaptation
    manager.adapt_to_context(session.session_id, "technical", "explain databases")
    manager.adapt_to_context(session.session_id, "casual", "weekend plans")

    # Test workflow recording
    manager.record_workflow_execution(session.session_id, "voice_planning",
        {"task": "test task"}, {"success": True, "execution_time": 0.5})

    # Get session summary
    summary = manager.get_session_summary(session.session_id)
    print(f"Session summary: {summary['total_events']} events, {summary['total_adaptations']} adaptations")

    # Get analytics
    analytics = manager.get_global_analytics(1)  # Last hour
    print(f"Analytics: {analytics['total_sessions']} sessions, {analytics['total_adaptations']} adaptations")

    # End session
    manager.end_session(session.session_id)

    print("✅ Session management test completed!")
