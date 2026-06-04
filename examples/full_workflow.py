"""
Example: Complete Octopus Workflow

Demonstrates the complete Decision-Execution Layer workflow.
"""

from octopus.core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    SimulationConfig,
    Scenario,
    DecisionEngine,
    DecisionPolicy,
    DecisionCriteria,
    LongTermMemory,
    MemoryType,
    EthicsFramework,
    Entity,
)
from octopus.execution import ExecutionLayer, ToolRegistry, Tool, ToolMetadata
from octopus.protocol import ODEPProtocol, ExecutionIntent, Priority


def create_example_tools():
    registry = ToolRegistry()
    
    def simple_calculator(params):
        a = params.get("a", 0)
        b = params.get("b", 0)
        operation = params.get("operation", "add")
        
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    metadata = ToolMetadata(
        tool_id="calculator",
        name="Simple Calculator",
        description="Perform basic arithmetic operations",
        category="utility",
    )
    
    tool = Tool(metadata)
    tool.register_executor(simple_calculator)
    registry.register_tool(tool)
    
    def data_fetcher(params):
        data_type = params.get("type", "sample")
        return {
            "type": data_type,
            "data": [1, 2, 3, 4, 5],
            "timestamp": "2026-05-27",
        }
    
    metadata2 = ToolMetadata(
        tool_id="data_fetcher",
        name="Data Fetcher",
        description="Fetch sample data",
        category="data_retrieval",
    )
    
    tool2 = Tool(metadata2)
    tool2.register_executor(data_fetcher)
    registry.register_tool(tool2)
    
    return registry


def demonstrate_perception():
    print("\n" + "="*60)
    print("1. PERCEPTION MODULE - Intent Recognition")
    print("="*60)
    
    perception = PerceptionModule()
    
    test_inputs = [
        "Please calculate the sum of 15 and 27",
        "I need to fetch customer data for analysis",
        "Run the analysis and send the report",
    ]
    
    for input_text in test_inputs:
        result = perception.perceive(input_text)
        print(f"\nInput: {input_text}")
        print(f"Detected Intent: {result.intents[0].intent_type.value if result.intents else 'None'}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Extracted Entities: {result.extracted_entities}")


def demonstrate_world_model():
    print("\n" + "="*60)
    print("2. WORLD MODEL - State Representation")
    print("="*60)
    
    world = WorldModel()
    
    user = Entity(
        entity_id="user_1",
        entity_type="user",
        properties={
            "name": "Alice",
            "role": "analyst",
            "active": True,
        }
    )
    world.add_entity(user)
    
    project = Entity(
        entity_id="project_1",
        entity_type="project",
        properties={
            "name": "Q2 Analysis",
            "status": "active",
            "priority": "high",
        }
    )
    world.add_entity(project)
    
    world.add_goal("project_1")
    world.add_constraint("user_1 has permission")
    
    print(f"Entities: {len(world.entities)}")
    print(f"Active Goals: {world.get_global_state('active_goals', [])}")
    print(f"Constraints: {world.get_global_state('constraints', [])}")
    print(f"State Summary: {world.get_state_summary()}")


def demonstrate_simulation():
    print("\n" + "="*60)
    print("3. SIMULATION ENGINE - Future Scenario Exploration")
    print("="*60)
    
    config = SimulationConfig(
        max_depth=3,
        uncertainty_level=0.1,
        risk_weight=0.4,
        reward_weight=0.6,
    )
    
    engine = SimulationEngine(config)
    
    initial_state = {
        "resources": 100,
        "time_remaining": 10,
        "quality": 0.5,
    }
    
    actions = [
        {"type": "allocate_resources", "parameters": {"amount": 20}},
        {"type": "execute_task", "parameters": {"task_id": "analysis"}},
        {"type": "review_results", "parameters": {}},
    ]
    
    result = engine.simulate_action_sequence(initial_state, actions)
    
    print(f"Simulation Status: {result.status.value}")
    print(f"Final State: {result.final_state}")
    print(f"Risk Assessment: {result.risk_assessment}")
    print(f"Success Metrics: {result.success_metrics}")
    print(f"Execution Time: {result.execution_time_ms:.2f}ms")


def demonstrate_decision_engine():
    print("\n" + "="*60)
    print("4. DECISION ENGINE - Structured Decision Making")
    print("="*60)
    
    decision = DecisionEngine()
    
    policy = DecisionPolicy(
        policy_id="default_policy",
        name="Default Decision Policy",
        description="Standard decision criteria",
        criteria=[
            DecisionCriteria("outcome_value", 0.40, "Value of outcome"),
            DecisionCriteria("risk_reduction", 0.25, "Risk reduction"),
            DecisionCriteria("reversibility", 0.20, "Ease of reversal"),
            DecisionCriteria("confidence_alignment", 0.15, "Confidence match"),
        ],
    )
    
    decision.add_policy(policy)
    
    context = {
        "task": "data_analysis",
        "priority": "high",
        "deadline": "2026-05-30",
    }
    
    options = [
        {
            "name": "Quick Analysis",
            "description": "Fast but basic analysis",
            "actions": [
                {"tool_id": "calculator", "parameters": {"a": 1, "b": 2}}
            ],
            "scores": {
                "outcome_value": 0.6,
                "risk_reduction": 0.4,
                "reversibility": 0.8,
                "confidence_alignment": 0.7,
            },
            "risk_level": 0.3,
        },
        {
            "name": "Comprehensive Analysis",
            "description": "Detailed analysis with full metrics",
            "actions": [
                {"tool_id": "data_fetcher", "parameters": {"type": "full"}},
                {"tool_id": "calculator", "parameters": {"a": 1, "b": 2}},
            ],
            "scores": {
                "outcome_value": 0.9,
                "risk_reduction": 0.7,
                "reversibility": 0.5,
                "confidence_alignment": 0.9,
            },
            "risk_level": 0.5,
        },
    ]
    
    result = decision.make_decision(context, options)
    
    print(f"Decision ID: {result.decision_id}")
    print(f"Status: {result.status.value}")
    print(f"Selected Option: {result.selected_option.name if result.selected_option else 'None'}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Execution Intent: {result.execution_intent is not None}")


def demonstrate_memory():
    print("\n" + "="*60)
    print("5. LONG-TERM MEMORY - Persistent Storage")
    print("="*60)
    
    memory = LongTermMemory()
    
    memory.store(
        content={
            "event": "successful_analysis",
            "outcome": "positive",
            "metrics": {"accuracy": 0.95, "speed": "fast"},
        },
        memory_type=MemoryType.EPISODIC,
        tags=["analysis", "success"],
        relevance=0.8,
    )
    
    memory.store(
        content={
            "pattern": "recurring_issue",
            "description": "Data quality issues in reports",
            "frequency": "weekly",
        },
        memory_type=MemoryType.SEMANTIC,
        tags=["issue", "reports"],
        relevance=0.7,
    )
    
    results = memory.search(tags=["analysis"])
    
    print(f"Stored Memories: {len(memory.memories)}")
    print(f"Search Results: {len(results)} items found")
    print(f"Statistics: {memory.get_statistics()}")


def demonstrate_ethics():
    print("\n" + "="*60)
    print("6. ETHICS FRAMEWORK - Value-Based Decision Making")
    print("="*60)
    
    ethics = EthicsFramework()
    guideline = ethics.create_default_guideline()
    ethics.add_guideline(guideline)
    
    action = {
        "type": "data_access",
        "target": "user_records",
        "purpose": "analysis",
    }
    
    result = ethics.check_ethics(action, {"user_consent": True})
    
    print(f"Ethics Decision: {result.decision.value}")
    print(f"Ethical Score: {result.ethical_score:.2f}")
    print(f"Applicable Rules: {len(result.applicable_rules)}")
    print(f"Violated Rules: {len(result.violated_rules)}")


def demonstrate_execution():
    print("\n" + "="*60)
    print("7. EXECUTION LAYER - Tool Execution")
    print("="*60)
    
    registry = create_example_tools()
    execution = ExecutionLayer()
    
    for tool_id, tool in registry.tools.items():
        execution.register_tool(tool)
    
    result = execution.execute_single("calculator", {
        "a": 10,
        "b": 5,
        "operation": "add",
    })
    print(f"Calculator Result (10 + 5): {result}")
    
    result = execution.execute_single("data_fetcher", {
        "type": "sample",
    })
    print(f"Data Fetcher Result: {result}")
    
    print(f"\nExecution Summary: {execution.get_execution_summary()}")


def demonstrate_full_workflow():
    print("\n" + "="*60)
    print("COMPLETE WORKFLOW DEMONSTRATION")
    print("="*60)
    
    world_model = WorldModel()
    perception = PerceptionModule()
    simulation = SimulationEngine()
    decision = DecisionEngine()
    memory = LongTermMemory()
    ethics = EthicsFramework()
    protocol = ODEPProtocol()
    execution = ExecutionLayer(protocol)
    
    decision.set_world_model(world_model)
    decision.set_simulation_engine(simulation)
    ethics.add_guideline(ethics.create_default_guideline())
    
    for tool_id, tool in create_example_tools().tools.items():
        execution.register_tool(tool)
    
    print("\nStep 1: Perception - Understanding User Intent")
    input_text = "I need to analyze the quarterly sales data and create a report"
    perception_result = perception.perceive(input_text)
    print(f"  Detected: {perception_result.intents[0].intent_type.value if perception_result.intents else 'Unknown'}")
    
    print("\nStep 2: World Model - Current State")
    world_model.add_entity(Entity(
        entity_id="data_source",
        entity_type="database",
        properties={"name": "sales_db", "records": 50000}
    ))
    print(f"  Entities in model: {len(world_model.entities)}")
    
    print("\nStep 3: Simulation - Exploring Options")
    initial_state = {"data_ready": True, "analysis_type": "quarterly"}
    actions = [{"type": "analyze"}, {"type": "generate_report"}]
    sim_result = simulation.simulate_action_sequence(initial_state, actions)
    print(f"  Simulation Score: {sim_result.success_metrics.get('overall_score', 0):.2f}")
    
    print("\nStep 4: Decision - Selecting Best Action")
    context = {"task": "quarterly_analysis", "priority": "high"}
    options = [
        {
            "name": "Quick Report",
            "description": "Fast summary",
            "actions": [{"tool_id": "calculator", "parameters": {}}],
            "scores": {"outcome_value": 0.7, "risk_reduction": 0.5, "reversibility": 0.8, "confidence_alignment": 0.8},
        },
        {
            "name": "Detailed Report",
            "description": "Comprehensive analysis",
            "actions": [{"tool_id": "data_fetcher", "parameters": {}}],
            "scores": {"outcome_value": 0.9, "risk_reduction": 0.7, "reversibility": 0.6, "confidence_alignment": 0.9},
        },
    ]
    decision_result = decision.make_decision(context, options)
    print(f"  Selected: {decision_result.selected_option.name if decision_result.selected_option else 'None'}")
    
    print("\nStep 5: Ethics Check")
    ethics_result = ethics.check_ethics(
        decision_result.execution_intent or {},
        context
    )
    print(f"  Ethics Decision: {ethics_result.decision.value}")
    
    print("\nStep 6: Execution - Performing Actions")
    if decision_result.execution_intent:
        intent = ExecutionIntent(
            intent_id=decision_result.decision_id,
            action_type="report_generation",
            parameters=decision_result.execution_intent["parameters"],
            priority=Priority.NORMAL,
        )
        exec_result = execution.execute_intent(intent)
        print(f"  Execution Status: {exec_result.status.value}")
        print(f"  Output: {exec_result.output}")
    
    print("\nStep 7: Memory - Storing Outcome")
    memory.store(
        content={
            "task": "quarterly_analysis",
            "success": decision_result.status.value == "decided",
            "selected_option": decision_result.selected_option.name if decision_result.selected_option else None,
        },
        memory_type=MemoryType.EPISODIC,
        tags=["analysis", "report"],
    )
    print(f"  Total memories: {len(memory.memories)}")
    
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)


def main():
    print("\n" + "="*60)
    print("OCTOPUS ARCHITECTURE DEMONSTRATION")
    print("="*60)
    
    demonstrate_perception()
    demonstrate_world_model()
    demonstrate_simulation()
    demonstrate_decision_engine()
    demonstrate_memory()
    demonstrate_ethics()
    demonstrate_execution()
    demonstrate_full_workflow()
    
    print("\n" + "="*60)
    print("ALL DEMONSTRATIONS COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
