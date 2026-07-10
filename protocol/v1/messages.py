from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List, Dict
from .enums import (
    MessageType,
    ExecutionStatus,
    Priority,
    ApprovalStatus,
    PROTOCOL_VERSION,
)


def _filter_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}


@dataclass
class ExecutionIntent:
    intent_id: str
    action_type: str
    parameters: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    timeout_seconds: Optional[int] = None
    constraints: List[str] = field(default_factory=list)
    rollback_plan: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return _filter_none({
            "intent_id": self.intent_id,
            "action_type": self.action_type,
            "parameters": self.parameters,
            "priority": self.priority.value,
            "timeout_seconds": self.timeout_seconds,
            "constraints": self.constraints,
            "rollback_plan": self.rollback_plan,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionIntent":
        data = data.copy()
        data["priority"] = Priority(data["priority"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class ExecutionResult:
    intent_id: str
    status: ExecutionStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    partial_results: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return _filter_none({
            "intent_id": self.intent_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "partial_results": self.partial_results,
            "metadata": self.metadata,
            "completed_at": self.completed_at.isoformat(),
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionResult":
        data = data.copy()
        data["status"] = ExecutionStatus(data["status"])
        data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        return cls(**data)


@dataclass
class WorldStateUpdate:
    state_type: str
    changes: Dict[str, Any]
    source: str
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    causal_links: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_type": self.state_type,
            "changes": self.changes,
            "source": self.source,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "causal_links": self.causal_links,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldStateUpdate":
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class ApprovalRequest:
    approval_id: str
    intent_id: str
    intent: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "intent_id": self.intent_id,
            "intent": self.intent,
            "context": self.context,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApprovalRequest":
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class ApprovalResponse:
    approval_id: str
    status: ApprovalStatus
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return _filter_none({
            "approval_id": self.approval_id,
            "status": self.status.value,
            "reason": self.reason,
            "metadata": self.metadata,
            "completed_at": self.completed_at.isoformat(),
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApprovalResponse":
        data = data.copy()
        data["status"] = ApprovalStatus(data["status"])
        data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        return cls(**data)


@dataclass
class DecisionRequest:
    decision_id: str
    goal: str
    context: Dict[str, Any] = field(default_factory=dict)
    options: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "goal": self.goal,
            "context": self.context,
            "options": self.options,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionRequest":
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class DecisionResponse:
    decision_id: str
    selected: Dict[str, Any]
    reasoning: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return _filter_none({
            "decision_id": self.decision_id,
            "selected": self.selected,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "completed_at": self.completed_at.isoformat(),
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DecisionResponse":
        data = data.copy()
        data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        return cls(**data)


@dataclass
class ODEPMessage:
    message_id: str
    message_type: MessageType
    sender: str
    recipient: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    ttl_seconds: Optional[int] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    protocol_version: str = PROTOCOL_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return _filter_none({
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "ttl_seconds": self.ttl_seconds,
            "retry_count": self.retry_count,
            "metadata": self.metadata,
            "protocol_version": self.protocol_version,
        })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ODEPMessage":
        data = data.copy()
        data["message_type"] = MessageType(data["message_type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)