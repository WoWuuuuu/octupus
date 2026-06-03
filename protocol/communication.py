"""
ODEP - Octopus Decision Execution Protocol

Communication protocol between Decision Layer (Head) and Execution Layer (Tentacles).
Inspired by SDEP (Spice Decision Execution Protocol).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, List, Dict
from datetime import datetime
import json


class MessageType(Enum):
    EXECUTE_REQUEST = "execute.request"
    EXECUTE_RESPONSE = "execute.response"
    STATE_UPDATE = "state.update"
    DECISION_REQUEST = "decision.request"
    DECISION_RESPONSE = "decision.response"
    OBSERVATION = "observation"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


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
        return {
            "intent_id": self.intent_id,
            "action_type": self.action_type,
            "parameters": self.parameters,
            "priority": self.priority.value,
            "timeout_seconds": self.timeout_seconds,
            "constraints": self.constraints,
            "rollback_plan": self.rollback_plan,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionIntent':
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
        return {
            "intent_id": self.intent_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "partial_results": self.partial_results,
            "metadata": self.metadata,
            "completed_at": self.completed_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionResult':
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
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
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ODEPMessage':
        data["message_type"] = MessageType(data["message_type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ODEPMessage':
        return cls.from_dict(json.loads(json_str))


class ODEPProtocol:
    def __init__(self):
        self.message_queue: List[ODEPMessage] = []
        self.pending_requests: Dict[str, ODEPMessage] = {}
        self.subscribers: Dict[str, List[callable]] = {}
    
    def send_execute_request(
        self,
        sender: str,
        recipient: str,
        intent: ExecutionIntent
    ) -> ODEPMessage:
        message = ODEPMessage(
            message_id=f"msg_{datetime.now().timestamp()}",
            message_type=MessageType.EXECUTE_REQUEST,
            sender=sender,
            recipient=recipient,
            payload={"execution_intent": intent.to_dict()},
            correlation_id=intent.intent_id,
        )
        self.message_queue.append(message)
        self.pending_requests[intent.intent_id] = message
        return message
    
    def send_execute_response(
        self,
        sender: str,
        recipient: str,
        result: ExecutionResult,
        correlation_id: str
    ) -> ODEPMessage:
        message = ODEPMessage(
            message_id=f"msg_{datetime.now().timestamp()}",
            message_type=MessageType.EXECUTE_RESPONSE,
            sender=sender,
            recipient=recipient,
            payload={"execution_result": result.to_dict()},
            correlation_id=correlation_id,
        )
        self.message_queue.append(message)
        if correlation_id in self.pending_requests:
            del self.pending_requests[correlation_id]
        return message
    
    def send_state_update(
        self,
        sender: str,
        recipient: str,
        update: WorldStateUpdate
    ) -> ODEPMessage:
        message = ODEPMessage(
            message_id=f"msg_{datetime.now().timestamp()}",
            message_type=MessageType.STATE_UPDATE,
            sender=sender,
            recipient=recipient,
            payload={"state_update": update.to_dict()},
        )
        self.message_queue.append(message)
        return message
    
    def subscribe(self, component: str, callback: callable):
        if component not in self.subscribers:
            self.subscribers[component] = []
        self.subscribers[component].append(callback)
    
    def publish(self, component: str, message: ODEPMessage):
        if component in self.subscribers:
            for callback in self.subscribers[component]:
                callback(message)
    
    def get_pending_request(self, intent_id: str) -> Optional[ODEPMessage]:
        return self.pending_requests.get(intent_id)
    
    def get_messages_by_type(self, message_type: MessageType) -> List[ODEPMessage]:
        return [m for m in self.message_queue if m.message_type == message_type]
    
    def clear_processed_messages(self, before_timestamp: datetime):
        self.message_queue = [
            m for m in self.message_queue if m.timestamp > before_timestamp
        ]
