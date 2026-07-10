from typing import Dict, Any, Optional
from datetime import datetime

from .messages import (
    ODEPMessage,
    ExecutionIntent,
    ExecutionResult,
    WorldStateUpdate,
)
from .enums import MessageType, ExecutionStatus, Priority


class ODEPLegacyAdapter:
    def convert_v0_to_v1(self, v0_data: Dict[str, Any]) -> ODEPMessage:
        message_type = v0_data.get("message_type", "")
        
        type_mapping = {
            "execute.request": MessageType.EXECUTE_REQUEST,
            "execute.response": MessageType.EXECUTE_RESPONSE,
            "state.update": MessageType.STATE_UPDATE,
            "decision.request": MessageType.DECISION_REQUEST,
            "decision.response": MessageType.DECISION_RESPONSE,
            "observation": MessageType.OBSERVATION,
            "error": MessageType.ERROR,
            "heartbeat": MessageType.HEARTBEAT,
        }

        message_type_v1 = type_mapping.get(message_type, MessageType.ERROR)
        
        return ODEPMessage(
            message_id=v0_data.get("message_id", ""),
            message_type=message_type_v1,
            sender=v0_data.get("sender", ""),
            recipient=v0_data.get("recipient", ""),
            payload=v0_data.get("payload", {}),
            correlation_id=v0_data.get("correlation_id"),
            timestamp=datetime.fromisoformat(v0_data["timestamp"])
            if "timestamp" in v0_data
            else datetime.now(),
            ttl_seconds=v0_data.get("ttl_seconds"),
            retry_count=v0_data.get("retry_count", 0),
            metadata=v0_data.get("metadata", {}),
            protocol_version="1.0",
        )

    def convert_v1_to_v0(self, v1_message: ODEPMessage) -> Dict[str, Any]:
        data = v1_message.to_dict()
        data.pop("protocol_version", None)
        return data

    def convert_v0_intent_to_v1(self, v0_intent: Dict[str, Any]) -> ExecutionIntent:
        return ExecutionIntent(
            intent_id=v0_intent.get("intent_id", ""),
            action_type=v0_intent.get("action_type", ""),
            parameters=v0_intent.get("parameters", {}),
            priority=Priority(v0_intent.get("priority", 3)),
            timeout_seconds=v0_intent.get("timeout_seconds"),
            constraints=v0_intent.get("constraints", []),
            rollback_plan=v0_intent.get("rollback_plan"),
            metadata=v0_intent.get("metadata", {}),
            created_at=datetime.fromisoformat(v0_intent["created_at"])
            if "created_at" in v0_intent
            else datetime.now(),
        )

    def convert_v0_result_to_v1(self, v0_result: Dict[str, Any]) -> ExecutionResult:
        status_mapping = {
            "pending": ExecutionStatus.PENDING,
            "running": ExecutionStatus.RUNNING,
            "success": ExecutionStatus.SUCCESS,
            "failed": ExecutionStatus.FAILED,
            "cancelled": ExecutionStatus.CANCELLED,
            "timeout": ExecutionStatus.TIMEOUT,
        }

        status = v0_result.get("status", "pending")
        status_v1 = status_mapping.get(status, ExecutionStatus.FAILED)

        return ExecutionResult(
            intent_id=v0_result.get("intent_id", ""),
            status=status_v1,
            output=v0_result.get("output"),
            error=v0_result.get("error"),
            execution_time_ms=v0_result.get("execution_time_ms"),
            partial_results=v0_result.get("partial_results", []),
            metadata=v0_result.get("metadata", {}),
            completed_at=datetime.fromisoformat(v0_result["completed_at"])
            if "completed_at" in v0_result
            else datetime.now(),
        )