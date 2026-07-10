import pytest
from datetime import datetime
from protocol.v1 import (
    MessageType,
    ExecutionStatus,
    Priority,
    ApprovalStatus,
    ExecutionIntent,
    ExecutionResult,
    WorldStateUpdate,
    ApprovalRequest,
    ApprovalResponse,
    DecisionRequest,
    DecisionResponse,
    ODEPMessage,
    validate_execution_intent,
    validate_execution_result,
    validate_odep_message,
    ODEPLegacyAdapter,
)


class TestEnums:
    def test_message_type_values(self):
        assert MessageType.EXECUTE_REQUEST.value == "execute.request"
        assert MessageType.EXECUTE_RESPONSE.value == "execute.response"
        assert MessageType.STATE_UPDATE.value == "state.update"
        assert MessageType.DECISION_REQUEST.value == "decision.request"
        assert MessageType.DECISION_RESPONSE.value == "decision.response"
        assert MessageType.APPROVAL_REQUEST.value == "approval.request"
        assert MessageType.APPROVAL_RESPONSE.value == "approval.response"
        assert MessageType.OBSERVATION.value == "observation"
        assert MessageType.ERROR.value == "error"
        assert MessageType.HEARTBEAT.value == "heartbeat"

    def test_execution_status_values(self):
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.CANCELLED.value == "cancelled"
        assert ExecutionStatus.TIMEOUT.value == "timeout"
        assert ExecutionStatus.PARTIAL.value == "partial"

    def test_priority_values(self):
        assert Priority.CRITICAL.value == 1
        assert Priority.HIGH.value == 2
        assert Priority.NORMAL.value == 3
        assert Priority.LOW.value == 4

    def test_approval_status_values(self):
        assert ApprovalStatus.PENDING.value == "pending"
        assert ApprovalStatus.APPROVED.value == "approved"
        assert ApprovalStatus.REJECTED.value == "rejected"
        assert ApprovalStatus.DELEGATED.value == "delegated"


class TestExecutionIntent:
    def test_to_dict(self):
        intent = ExecutionIntent(
            intent_id="test_intent",
            action_type="test_action",
            parameters={"key": "value"},
            priority=Priority.HIGH,
            timeout_seconds=30,
            constraints=["test"],
            metadata={"source": "test"},
        )
        data = intent.to_dict()
        assert data["intent_id"] == "test_intent"
        assert data["action_type"] == "test_action"
        assert data["parameters"] == {"key": "value"}
        assert data["priority"] == 2
        assert data["timeout_seconds"] == 30
        assert data["constraints"] == ["test"]
        assert "created_at" in data

    def test_from_dict(self):
        data = {
            "intent_id": "test_intent",
            "action_type": "test_action",
            "parameters": {"key": "value"},
            "priority": 2,
            "timeout_seconds": 30,
            "constraints": ["test"],
            "metadata": {"source": "test"},
            "created_at": datetime.now().isoformat(),
        }
        intent = ExecutionIntent.from_dict(data)
        assert intent.intent_id == "test_intent"
        assert intent.action_type == "test_action"
        assert intent.parameters == {"key": "value"}
        assert intent.priority == Priority.HIGH
        assert intent.timeout_seconds == 30


class TestExecutionResult:
    def test_to_dict(self):
        result = ExecutionResult(
            intent_id="test_intent",
            status=ExecutionStatus.SUCCESS,
            output="result",
            execution_time_ms=100.5,
        )
        data = result.to_dict()
        assert data["intent_id"] == "test_intent"
        assert data["status"] == "success"
        assert data["output"] == "result"
        assert data["execution_time_ms"] == 100.5

    def test_from_dict(self):
        data = {
            "intent_id": "test_intent",
            "status": "success",
            "output": "result",
            "execution_time_ms": 100.5,
            "completed_at": datetime.now().isoformat(),
        }
        result = ExecutionResult.from_dict(data)
        assert result.intent_id == "test_intent"
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output == "result"


class TestODEPMessage:
    def test_to_dict(self):
        message = ODEPMessage(
            message_id="test_msg",
            message_type=MessageType.EXECUTE_REQUEST,
            sender="decision_layer",
            recipient="execution_layer",
            payload={"test": "data"},
            correlation_id="test_corr",
        )
        data = message.to_dict()
        assert data["message_id"] == "test_msg"
        assert data["message_type"] == "execute.request"
        assert data["sender"] == "decision_layer"
        assert data["recipient"] == "execution_layer"
        assert data["payload"] == {"test": "data"}
        assert data["protocol_version"] == "1.0"

    def test_from_dict(self):
        data = {
            "message_id": "test_msg",
            "message_type": "execute.request",
            "sender": "decision_layer",
            "recipient": "execution_layer",
            "payload": {"test": "data"},
            "correlation_id": "test_corr",
            "timestamp": datetime.now().isoformat(),
            "protocol_version": "1.0",
        }
        message = ODEPMessage.from_dict(data)
        assert message.message_id == "test_msg"
        assert message.message_type == MessageType.EXECUTE_REQUEST
        assert message.protocol_version == "1.0"


class TestValidators:
    def test_validate_execution_intent_valid(self):
        intent = ExecutionIntent(
            intent_id="test",
            action_type="action",
            parameters={},
            priority=Priority.NORMAL,
            created_at=datetime.now(),
        )
        error = validate_execution_intent(intent.to_dict())
        assert error is None

    def test_validate_execution_intent_invalid(self):
        data = {"intent_id": "test"}
        error = validate_execution_intent(data)
        assert error is not None

    def test_validate_execution_result_valid(self):
        result = ExecutionResult(
            intent_id="test",
            status=ExecutionStatus.SUCCESS,
            completed_at=datetime.now(),
        )
        error = validate_execution_result(result.to_dict())
        assert error is None

    def test_validate_odep_message_valid(self):
        message = ODEPMessage(
            message_id="test",
            message_type=MessageType.EXECUTE_REQUEST,
            sender="a",
            recipient="b",
            payload={},
            timestamp=datetime.now(),
            protocol_version="1.0",
        )
        error = validate_odep_message(message.to_dict())
        assert error is None


class TestLegacyAdapter:
    def test_convert_v0_to_v1(self):
        v0_data = {
            "message_id": "test",
            "message_type": "execute.request",
            "sender": "a",
            "recipient": "b",
            "payload": {},
            "timestamp": datetime.now().isoformat(),
        }
        adapter = ODEPLegacyAdapter()
        v1_message = adapter.convert_v0_to_v1(v0_data)
        assert v1_message.message_id == "test"
        assert v1_message.message_type == MessageType.EXECUTE_REQUEST
        assert v1_message.protocol_version == "1.0"

    def test_convert_v1_to_v0(self):
        v1_message = ODEPMessage(
            message_id="test",
            message_type=MessageType.EXECUTE_REQUEST,
            sender="a",
            recipient="b",
            payload={},
        )
        adapter = ODEPLegacyAdapter()
        v0_data = adapter.convert_v1_to_v0(v1_message)
        assert v0_data["message_id"] == "test"
        assert "protocol_version" not in v0_data