from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError


EXECUTION_INTENT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ExecutionIntent",
    "type": "object",
    "required": ["intent_id", "action_type", "parameters", "priority", "created_at"],
    "properties": {
        "intent_id": {"type": "string"},
        "action_type": {"type": "string"},
        "parameters": {"type": "object"},
        "priority": {"type": "integer", "enum": [1, 2, 3, 4]},
        "timeout_seconds": {"type": "integer", "minimum": 0},
        "constraints": {"type": "array", "items": {"type": "string"}},
        "rollback_plan": {"type": "object"},
        "metadata": {"type": "object"},
        "created_at": {"type": "string", "format": "date-time"},
    },
}


EXECUTION_RESULT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ExecutionResult",
    "type": "object",
    "required": ["intent_id", "status", "completed_at"],
    "properties": {
        "intent_id": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["pending", "running", "success", "failed", "cancelled", "timeout", "partial"],
        },
        "output": {},
        "error": {"type": "string"},
        "execution_time_ms": {"type": "number", "minimum": 0},
        "partial_results": {"type": "array"},
        "metadata": {"type": "object"},
        "completed_at": {"type": "string", "format": "date-time"},
    },
}


ODEP_MESSAGE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ODEPMessage",
    "type": "object",
    "required": [
        "message_id",
        "message_type",
        "sender",
        "recipient",
        "payload",
        "timestamp",
        "protocol_version",
    ],
    "properties": {
        "message_id": {"type": "string"},
        "message_type": {
            "type": "string",
            "enum": [
                "execute.request",
                "execute.response",
                "state.update",
                "decision.request",
                "decision.response",
                "approval.request",
                "approval.response",
                "observation",
                "error",
                "heartbeat",
            ],
        },
        "sender": {"type": "string"},
        "recipient": {"type": "string"},
        "payload": {"type": "object"},
        "correlation_id": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "ttl_seconds": {"type": "integer", "minimum": 0},
        "retry_count": {"type": "integer", "minimum": 0},
        "metadata": {"type": "object"},
        "protocol_version": {"type": "string", "default": "1.0"},
    },
}


def validate_execution_intent(data: Dict[str, Any]) -> Optional[str]:
    try:
        validate(instance=data, schema=EXECUTION_INTENT_SCHEMA)
        return None
    except ValidationError as e:
        return str(e)


def validate_execution_result(data: Dict[str, Any]) -> Optional[str]:
    try:
        validate(instance=data, schema=EXECUTION_RESULT_SCHEMA)
        return None
    except ValidationError as e:
        return str(e)


def validate_odep_message(data: Dict[str, Any]) -> Optional[str]:
    try:
        validate(instance=data, schema=ODEP_MESSAGE_SCHEMA)
        return None
    except ValidationError as e:
        return str(e)