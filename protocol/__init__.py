"""
Octopus Protocol - Communication Protocol Components

ODEP (Octopus Decision Execution Protocol) for layer communication.

v1: New protocol version with JSON Schema validation and transport abstraction
legacy: Original ODEP v0 implementation (backward compatible)
"""

from protocol.communication import (
    ODEPProtocol,
    ODEPMessage,
    MessageType,
    ExecutionIntent,
    ExecutionResult,
    ExecutionStatus,
    Priority,
    WorldStateUpdate,
)

from protocol.v1 import (
    MessageType as MessageTypeV1,
    ExecutionStatus as ExecutionStatusV1,
    Priority as PriorityV1,
    ApprovalStatus,
    PROTOCOL_VERSION,
    ExecutionIntent as ExecutionIntentV1,
    ExecutionResult as ExecutionResultV1,
    WorldStateUpdate as WorldStateUpdateV1,
    ApprovalRequest,
    ApprovalResponse,
    DecisionRequest,
    DecisionResponse,
    ODEPMessage as ODEPMessageV1,
    validate_execution_intent,
    validate_execution_result,
    validate_odep_message,
    Transport,
    StdioTransport,
    ODEPLegacyAdapter,
)

__all__ = [
    "ODEPProtocol",
    "ODEPMessage",
    "MessageType",
    "ExecutionIntent",
    "ExecutionResult",
    "ExecutionStatus",
    "Priority",
    "WorldStateUpdate",
    "MessageTypeV1",
    "ExecutionStatusV1",
    "PriorityV1",
    "ApprovalStatus",
    "PROTOCOL_VERSION",
    "ExecutionIntentV1",
    "ExecutionResultV1",
    "WorldStateUpdateV1",
    "ApprovalRequest",
    "ApprovalResponse",
    "DecisionRequest",
    "DecisionResponse",
    "ODEPMessageV1",
    "validate_execution_intent",
    "validate_execution_result",
    "validate_odep_message",
    "Transport",
    "StdioTransport",
    "ODEPLegacyAdapter",
]
