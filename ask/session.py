"""Session management for conversation history"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import uuid4


@dataclass
class Session:
    """Represents a conversation session"""

    session_id: str
    created_at: datetime
    last_used: datetime
    messages: list = field(default_factory=list)

    def add_message(self, role: str, content):
        """Add a message to the session"""
        self.messages.append({
            "role": role,
            "content": content
        })
        self.last_used = datetime.now()

    def to_api_messages(self) -> list:
        """Convert session messages to API format"""
        return self.messages

    def save(self, session_dir: Path):
        """Persist session to disk"""
        session_dir.mkdir(parents=True, exist_ok=True)
        session_file = session_dir / f"{self.session_id}.json"

        data = {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "messages": self.messages
        }

        session_file.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, session_id: str, session_dir: Path) -> Optional["Session"]:
        """Load session from disk"""
        session_file = session_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            data = json.loads(session_file.read_text())
            return cls(
                session_id=data["session_id"],
                created_at=datetime.fromisoformat(data["created_at"]),
                last_used=datetime.fromisoformat(data["last_used"]),
                messages=data["messages"]
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted session file
            return None

    @classmethod
    def create_new(cls) -> "Session":
        """Create a new session with generated ID"""
        now = datetime.now()
        return cls(
            session_id=str(uuid4()),
            created_at=now,
            last_used=now
        )


class SessionManager:
    """Manages session lifecycle"""

    def __init__(self, config):
        self.config = config

    def get_or_create_session(self) -> Session:
        """Get current session or create new one"""
        # Check for session ID in environment
        session_id = os.getenv('ASK_SESSION_ID')

        if not session_id:
            # No session ID - create ephemeral session
            return Session.create_new()

        # Try to load existing session
        session = Session.load(session_id, self.config.session_dir)

        if session:
            return session

        # Create new session with this ID
        now = datetime.now()
        return Session(
            session_id=session_id,
            created_at=now,
            last_used=now
        )

    def cleanup_expired_sessions(self):
        """Remove sessions older than timeout"""
        if not self.config.session_dir.exists():
            return

        cutoff = datetime.now() - timedelta(hours=self.config.session_timeout_hours)

        for session_file in self.config.session_dir.glob("*.json"):
            try:
                data = json.loads(session_file.read_text())
                last_used = datetime.fromisoformat(data["last_used"])

                if last_used < cutoff:
                    session_file.unlink()
            except (json.JSONDecodeError, KeyError, ValueError):
                # Corrupted or invalid session file - delete it
                session_file.unlink()
