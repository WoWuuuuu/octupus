from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import json
import os


class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class SessionType(Enum):
    DECISION = "decision"
    EXPLORATION = "exploration"
    RESEARCH = "research"
    REVIEW = "review"
    OTHER = "other"


@dataclass
class SessionEvent:
    event_id: str
    event_type: str
    timestamp: datetime
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionEvent':
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class Session:
    session_id: str
    title: str
    description: str = ""
    status: SessionStatus = SessionStatus.ACTIVE
    session_type: SessionType = SessionType.DECISION
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    decision_ids: List[str] = field(default_factory=list)
    events: List[SessionEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "session_type": self.session_type.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "context": self.context,
            "tags": self.tags,
            "decision_ids": self.decision_ids,
            "events": [e.to_dict() for e in self.events],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        data["status"] = SessionStatus(data["status"])
        data["session_type"] = SessionType(data["session_type"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if data.get("ended_at"):
            data["ended_at"] = datetime.fromisoformat(data["ended_at"])
        data["events"] = [SessionEvent.from_dict(e) for e in data.get("events", [])]
        return cls(**data)

    def add_event(self, event_type: str, description: str, metadata: Optional[Dict[str, Any]] = None):
        event = SessionEvent(
            event_id=f"evt_{datetime.now().timestamp()}",
            event_type=event_type,
            timestamp=datetime.now(),
            description=description,
            metadata=metadata or {},
        )
        self.events.append(event)
        self.updated_at = datetime.now()
        return event

    def add_decision(self, decision_id: str):
        if decision_id not in self.decision_ids:
            self.decision_ids.append(decision_id)
            self.updated_at = datetime.now()

    def start(self):
        self.status = SessionStatus.ACTIVE
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
        self.add_event("session_started", "Session started")

    def pause(self):
        self.status = SessionStatus.PAUSED
        self.updated_at = datetime.now()
        self.add_event("session_paused", "Session paused")

    def resume(self):
        self.status = SessionStatus.ACTIVE
        self.updated_at = datetime.now()
        self.add_event("session_resumed", "Session resumed")

    def complete(self):
        self.status = SessionStatus.COMPLETED
        self.ended_at = datetime.now()
        self.updated_at = datetime.now()
        self.add_event("session_completed", "Session completed")

    def archive(self):
        self.status = SessionStatus.ARCHIVED
        self.ended_at = datetime.now()
        self.updated_at = datetime.now()
        self.add_event("session_archived", "Session archived")


class SessionStore:
    def __init__(self, storage_path: str = "data/sessions"):
        self.storage_path = storage_path
        self.sessions: Dict[str, Session] = {}
        self.current_session_id: Optional[str] = None
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_all()

    def _load_all(self):
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                session_id = filename[:-5]
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        session = Session.from_dict(data)
                        self.sessions[session_id] = session
                except Exception:
                    pass

        current_file = os.path.join(self.storage_path, "_current.json")
        if os.path.exists(current_file):
            try:
                with open(current_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_session_id = data.get("current_session_id")
            except Exception:
                pass

    def _save_session(self, session: Session):
        filepath = os.path.join(self.storage_path, f"{session.session_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

    def _save_current(self):
        current_file = os.path.join(self.storage_path, "_current.json")
        with open(current_file, "w", encoding="utf-8") as f:
            json.dump({"current_session_id": self.current_session_id}, f, indent=2)

    def create(self, title: str, description: str = "", session_type: SessionType = SessionType.DECISION,
               context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> Session:
        session_id = f"session_{datetime.now().timestamp()}"
        session = Session(
            session_id=session_id,
            title=title,
            description=description,
            session_type=session_type,
            context=context or {},
            tags=tags or [],
        )
        session.start()
        self.sessions[session_id] = session
        self._save_session(session)
        return session

    def get(self, session_id: str) -> Optional[Session]:
        return self.sessions.get(session_id)

    def get_current(self) -> Optional[Session]:
        if self.current_session_id and self.current_session_id in self.sessions:
            return self.sessions[self.current_session_id]
        return None

    def set_current(self, session_id: str) -> bool:
        if session_id in self.sessions:
            self.current_session_id = session_id
            self._save_current()
            return True
        return False

    def list(self, status: Optional[SessionStatus] = None, session_type: Optional[SessionType] = None,
             limit: int = 50) -> List[Session]:
        filtered = [s for s in self.sessions.values()]
        if status:
            filtered = [s for s in filtered if s.status == status]
        if session_type:
            filtered = [s for s in filtered if s.session_type == session_type]
        filtered.sort(key=lambda s: s.created_at, reverse=True)
        return filtered[:limit]

    def search(self, query: str, limit: int = 20) -> List[Session]:
        query_lower = query.lower()
        results = []
        for session in self.sessions.values():
            if (query_lower in session.title.lower() or
                query_lower in session.description.lower() or
                any(query_lower in tag.lower() for tag in session.tags)):
                results.append(session)
        results.sort(key=lambda s: s.created_at, reverse=True)
        return results[:limit]

    def update(self, session_id: str, **kwargs) -> Optional[Session]:
        session = self.sessions.get(session_id)
        if not session:
            return None

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        session.updated_at = datetime.now()
        self._save_session(session)
        return session

    def delete(self, session_id: str) -> bool:
        if session_id in self.sessions:
            filepath = os.path.join(self.storage_path, f"{session_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = None
                self._save_current()
            return True
        return False

    def get_timeline(self, session_id: str) -> Optional[List[SessionEvent]]:
        session = self.sessions.get(session_id)
        if not session:
            return None
        return sorted(session.events, key=lambda e: e.timestamp)

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self.sessions)
        active = sum(1 for s in self.sessions.values() if s.status == SessionStatus.ACTIVE)
        paused = sum(1 for s in self.sessions.values() if s.status == SessionStatus.PAUSED)
        completed = sum(1 for s in self.sessions.values() if s.status == SessionStatus.COMPLETED)
        archived = sum(1 for s in self.sessions.values() if s.status == SessionStatus.ARCHIVED)

        type_counts = {}
        for s in self.sessions.values():
            t = s.session_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total_sessions": total,
            "active_sessions": active,
            "paused_sessions": paused,
            "completed_sessions": completed,
            "archived_sessions": archived,
            "session_types": type_counts,
            "current_session": self.current_session_id,
        }