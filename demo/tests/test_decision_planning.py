"""
Unit tests for Decision Engine, Simulation Engine, and Execution tools.
"""
import pytest
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.decision_engine import DecisionEngine, DecisionPolicy, DecisionCriteria
from core.simulation import SimulationEngine
from execution.executor import ExecutionLayer
from execution.tools import Tool, ToolMetadata

def test_simulation_prediction():
    engine = SimulationEngine()
    initial_state = {"inventory": 5}
    actions = [
        {"type": "restock", "parameters": {"quantity": 10}},
        {"type": "sell", "parameters": {"quantity": 3}}
    ]
    result = engine.simulate_action_sequence(initial_state, actions)
    assert result.status.value == "completed"
    assert result.final_state["inventory"] == 12

def test_decision_policy_weighting():
    decision = DecisionEngine()
    policy = DecisionPolicy(
        policy_id="test_policy",
        name="Test Policy",
        description="Weights test",
        criteria=[
            DecisionCriteria("cost", 0.7, "Minimize cost"),
            DecisionCriteria("speed", 0.3, "Maximize speed")
        ]
    )
    decision.add_policy(policy)
    
    context = {"task": "delivery"}
    options = [
        {
            "name": "Slow Mail",
            "description": "Cheap and slow",
            "scores": {"cost": 0.9, "speed": 0.2} # total: 0.9*0.7 + 0.2*0.3 = 0.63 + 0.06 = 0.69
        },
        {
            "name": "Express",
            "description": "Expensive and fast",
            "scores": {"cost": 0.3, "speed": 0.9} # total: 0.3*0.7 + 0.9*0.3 = 0.21 + 0.27 = 0.48
        }
    ]
    result = decision.make_decision(context, options)
    assert result.selected_option.name == "Slow Mail"

def test_execution_tool_running():
    execution = ExecutionLayer()
    metadata = ToolMetadata(tool_id="math_add", name="Add", description="add tool", category="utility")
    tool = Tool(metadata)
    tool.register_executor(lambda p: p["a"] + p["b"])
    execution.register_tool(tool)
    
    result = execution.execute_single("math_add", {"a": 40, "b": 2})
    assert result == 42
