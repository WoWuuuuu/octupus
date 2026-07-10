from enum import Enum


class MessageType(Enum):
    EXECUTE_REQUEST = "execute.request"
    EXECUTE_RESPONSE = "execute.response"
    STATE_UPDATE = "state.update"
    DECISION_REQUEST = "decision.request"
    DECISION_RESPONSE = "decision.response"
    APPROVAL_REQUEST = "approval.request"
    APPROVAL_RESPONSE = "approval.response"
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
    PARTIAL = "partial"


class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"


PROTOCOL_VERSION = "1.0"