
"""
Simple Example: Using Octopus Programmatically

A basic example showing how to use Octopus components.
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    DecisionEngine,
    DecisionPolicy,
    DecisionCriteria,
)
from execution import ExecutionLayer, Tool, ToolMetadata
from protocol import ExecutionIntent, Priority


def simple_example():
    print("="*60)
    print("Simple Octopus Example")
    print("="*60)
    
    print("\n1. Creating Components...")
    
    world_model = WorldModel()
    perception = PerceptionModule()
    simulation = SimulationEngine()
    decision = DecisionEngine()
    execution = ExecutionLayer()
    
    print("   Components created successfully!")
    
    print("\n2. Setting up Decision Policy...")
    
    policy = DecisionPolicy(
        policy_id="simple_policy",
        name="Simple Policy",
        description="A simple decision policy",
        criteria=[
            DecisionCriteria("outcome_value", 0.5, "Value of outcome"),
            DecisionCriteria("risk_reduction", 0.3, "Risk reduction"),
            DecisionCriteria("reversibility", 0.2, "Reversibility"),
        ],
    )
    decision.add_policy(policy)
    
    print(f"   Policy '{policy.name}' is active")
    
    print("\n3. Setting up a Tool...")
    
    metadata = ToolMetadata(
        tool_id="greeter",
        name="Greeter",
        description="A simple greeting tool",
        category="utility",
    )
    
    tool = Tool(metadata)
    tool.register_executor(lambda params: f"Hello, {params.get('name', 'World')}!")
    
    execution.register_tool(tool)
    
    print("   Tool 'greeter' registered")
    
    print("\n4. Processing User Input...")
    
    user_input = "Say hello to Alice"
    result = perception.perceive(user_input)
    
    if result.intents:
        print(f"   Detected intent: {result.intents[0].intent_type.value}")
    
    print("\n5. Making a Decision...")
    
    context = {"task": "greeting", "user": "Alice"}
    
    options = [
        {
            "name": "Standard Greeting",
            "description": "A simple greeting",
            "actions": [{"tool_id": "greeter", "parameters": {"name": "Alice"}}],
            "scores": {
                "outcome_value": 0.8,
                "risk_reduction": 0.7,
                "reversibility": 0.9,
            },
        },
        {
            "name": "Formal Greeting",
            "description": "A formal greeting",
            "actions": [{"tool_id": "greeter", "parameters": {"name": "Ms. Alice"}}],
            "scores": {
                "outcome_value": 0.7,
                "risk_reduction": 0.8,
                "reversibility": 0.8,
            },
        },
    ]
    
    decision_result = decision.make_decision(context, options)
    
    print(f"   Selected: {decision_result.selected_option.name}")
    print(f"   Reasoning: {decision_result.reasoning}")
    
    print("\n6. Executing the Decision...")
    
    if decision_result.execution_intent:
        intent = ExecutionIntent(
            intent_id=decision_result.decision_id,
            action_type="greeting",
            parameters=decision_result.execution_intent["parameters"],
            priority=Priority.NORMAL,
        )
        
        exec_result = execution.execute_intent(intent)
        
        if exec_result.status.value == "success":
            print(f"   Result: {exec_result.output}")
    
    print("\n" + "="*60)
    print("Example completed successfully!")
    print("="*60)


if __name__ == "__main__":
    simple_example()
