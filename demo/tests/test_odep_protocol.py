"""
Unit tests for ODEP Layer Communication Protocol
"""
import pytest
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from protocol.communication import ODEPProtocol, ExecutionIntent, MessageType, Priority

def test_odep_publish_subscribe():
    protocol = ODEPProtocol()
    received_messages = []
    
    # Subscribe to execution requests
    def callback(message):
        received_messages.append(message)
        
    protocol.subscribe("execution_layer", callback)
    
    # Create intent and send request
    intent = ExecutionIntent(
        intent_id="intent_1",
        action_type="test_action",
        parameters={"value": 42},
        priority=Priority.NORMAL
    )
    
    msg = protocol.send_execute_request("decision_layer", "execution_layer", intent)
    assert msg.message_type == MessageType.EXECUTE_REQUEST
    
    # Verify subscriber received message
    assert len(received_messages) == 1
    assert received_messages[0].message_id == msg.message_id
    assert received_messages[0].payload["intent_id"] == "intent_1"
