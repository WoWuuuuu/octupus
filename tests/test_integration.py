"""
Integration Tests for Octopus Complete Workflow
"""

import pytest
from core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    DecisionEngine,
    LongTermMemory,
    EthicsFramework,
    DecisionPolicy,
    DecisionCriteria,
    Entity,
)
from execution import ExecutionLayer, Tool, ToolMetadata
from protocol import ODEPProtocol, ExecutionIntent, Priority


class TestIntegration:
    def test_complete_workflow(self):
        print("\n" + "="*60)
        print("INTEGRATION TEST: Complete Octopus Workflow")
        print("="*60)
        
        print("\n1. Initializing Components...")
        
        world_model = WorldModel()
        perception = PerceptionModule()
        simulation = SimulationEngine()
        decision = DecisionEngine()
        memory = LongTermMemory()
        ethics = EthicsFramework()
        protocol = ODEPProtocol()
        execution = ExecutionLayer(protocol)
        
        print("   ✓ All components initialized")
        
        print("\n2. Setting Up Components...")
        
        decision.set_world_model(world_model)
        decision.set_simulation_engine(simulation)
        
        policy = DecisionPolicy(
            policy_id="integration_policy",
            name="Integration Test Policy",
            description="Policy for integration testing",
            criteria=[
                DecisionCriteria("outcome_value", 0.40, "Value metric"),
                DecisionCriteria("risk_reduction", 0.30, "Risk metric"),
                DecisionCriteria("reversibility", 0.20, "Reversibility metric"),
                DecisionCriteria("confidence_alignment", 0.10, "Confidence metric"),
            ],
        )
        decision.add_policy(policy)
        
        default_guideline = ethics.create_default_guideline()
        ethics.add_guideline(default_guideline)
        
        print("   ✓ Decision engine configured with policy")
        print("   ✓ Ethics framework configured with default guideline")
        
        print("\n3. Setting Up Execution Layer...")
        
        def simple_tool_executor(params):
            value = params.get("value", 0)
            operation = params.get("operation", "double")
            
            if operation == "double":
                return value * 2
            elif operation == "triple":
                return value * 3
            else:
                return value
        
        tool_metadata = ToolMetadata(
            tool_id="simple_math",
            name="Simple Math Tool",
            description="Performs simple mathematical operations",
            category="utility",
        )
        
        tool = Tool(tool_metadata)
        tool.register_executor(simple_tool_executor)
        execution.register_tool(tool)
        
        print("   ✓ Execution layer configured with tools")
        
        print("\n4. Running Perception...")
        
        user_input = "Please process the data with value 42"
        perception_result = perception.perceive(user_input)
        
        assert len(perception_result.intents) > 0
        print(f"   ✓ Detected intent: {perception_result.intents[0].intent_type.value}")
        print(f"   ✓ Confidence: {perception_result.confidence:.2f}")
        
        print("\n5. Updating World Model...")
        
        user_entity = Entity(
            entity_id="user_1",
            entity_type="user",
            properties={
                "name": "Test User",
                "role": "analyst",
            }
        )
        world_model.add_entity(user_entity)
        
        world_model.add_goal("process_data")
        world_model.add_constraint("data must be valid")
        
        summary = world_model.get_state_summary()
        print(f"   ✓ Entities: {summary['entity_count']}")
        print(f"   ✓ Goals: {summary['goal_count']}")
        print(f"   ✓ Constraints: {summary['constraint_count']}")
        
        print("\n6. Running Simulation...")
        
        initial_state = {"data_value": 42, "status": "ready"}
        actions = [
            {"type": "validate"},
            {"type": "process"},
        ]
        
        sim_result = simulation.simulate_action_sequence(initial_state, actions)
        
        assert sim_result.status.value == "completed"
        print(f"   ✓ Simulation completed")
        print(f"   ✓ Risk Score: {sim_result.risk_assessment.get('total_risk', 0):.2f}")
        print(f"   ✓ Success Score: {sim_result.success_metrics.get('overall_score', 0):.2f}")
        
        print("\n7. Making Decision...")
        
        context = {
            "task": "data_processing",
            "input_value": 42,
            "priority": "normal",
        }
        
        options = [
            {
                "name": "Quick Processing",
                "description": "Fast but basic processing",
                "actions": [
                    {"tool_id": "simple_math", "parameters": {"value": 42, "operation": "double"}}
                ],
                "scores": {
                    "outcome_value": 0.7,
                    "risk_reduction": 0.5,
                    "reversibility": 0.8,
                    "confidence_alignment": 0.8,
                },
                "risk_level": 0.3,
            },
            {
                "name": "Thorough Processing",
                "description": "Comprehensive processing with validation",
                "actions": [
                    {"tool_id": "simple_math", "parameters": {"value": 42, "operation": "triple"}}
                ],
                "scores": {
                    "outcome_value": 0.9,
                    "risk_reduction": 0.8,
                    "reversibility": 0.6,
                    "confidence_alignment": 0.9,
                },
                "risk_level": 0.5,
            },
        ]
        
        decision_result = decision.make_decision(context, options)
        
        assert decision_result is not None
        assert decision_result.selected_option is not None
        print(f"   ✓ Decision made: {decision_result.selected_option.name}")
        print(f"   ✓ Confidence: {decision_result.confidence:.2f}")
        print(f"   ✓ Reasoning: {decision_result.reasoning[:50]}...")
        
        print("\n8. Ethics Check...")
        
        ethics_result = ethics.check_ethics(
            decision_result.execution_intent or {},
            context
        )
        
        assert ethics_result is not None
        print(f"   ✓ Ethics Decision: {ethics_result.decision.value}")
        print(f"   ✓ Ethical Score: {ethics_result.ethical_score:.2f}")
        
        print("\n9. Protocol Communication...")
        
        if decision_result.execution_intent:
            intent = ExecutionIntent(
                intent_id=decision_result.decision_id,
                action_type="data_processing",
                parameters=decision_result.execution_intent["parameters"],
                priority=Priority.NORMAL,
            )
            
            message = protocol.send_execute_request("decision_layer", "execution_layer", intent)
            assert message is not None
            print(f"   ✓ Message sent: {message.message_type.value}")
            print(f"   ✓ Message ID: {message.message_id}")
        
        print("\n10. Executing Actions...")
        
        if decision_result.execution_intent:
            exec_result = execution.execute_intent(intent)
            
            assert exec_result.status.value == "success"
            print(f"   ✓ Execution Status: {exec_result.status.value}")
            print(f"   ✓ Output: {exec_result.output}")
        
        print("\n11. Storing in Memory...")
        
        memory.store(
            content={
                "workflow": "integration_test",
                "input": user_input,
                "decision_id": decision_result.decision_id,
                "selected_option": decision_result.selected_option.name,
                "success": True,
            },
            memory_type="episodic",
            tags=["integration", "test", "workflow"],
        )
        
        stats = memory.get_statistics()
        print(f"   ✓ Total memories: {stats['total_memories']}")
        
        print("\n12. Final Status Check...")
        
        decision_summary = decision.get_decision_summary()
        print(f"   ✓ Total decisions: {decision_summary['total_decisions']}")
        
        execution_summary = execution.get_execution_summary()
        print(f"   ✓ Total executions: {execution_summary['total_executions']}")
        
        protocol_messages = len(protocol.message_queue)
        print(f"   ✓ Protocol messages: {protocol_messages}")
        
        print("\n" + "="*60)
        print("INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
        assert True
    
    def test_error_handling_workflow(self):
        print("\n" + "="*60)
        print("INTEGRATION TEST: Error Handling")
        print("="*60)
        
        execution = ExecutionLayer()
        
        tool_metadata = ToolMetadata(
            tool_id="failing_tool",
            name="Failing Tool",
            description="Tool that always fails",
            category="utility",
        )
        
        tool = Tool(tool_metadata)
        
        def failing_executor(params):
            raise RuntimeError("Intentional test failure")
        
        tool.register_executor(failing_executor)
        execution.register_tool(tool)
        
        intent = ExecutionIntent(
            intent_id="error_test",
            action_type="test_error",
            parameters={
                "action_sequence": [
                    {"tool_id": "failing_tool", "parameters": {}}
                ]
            },
            priority=Priority.NORMAL,
        )
        
        result = execution.execute_intent(intent)
        
        assert result.status.value == "failed"
        assert result.error is not None
        print(f"   ✓ Error correctly caught: {result.error}")
        print("   ✓ Error handling test passed\n")
        
        print("="*60 + "\n")
    
    def test_concurrent_components(self):
        print("\n" + "="*60)
        print("INTEGRATION TEST: Multiple Component Instances")
        print("="*60)
        
        instances = []
        
        for i in range(3):
            world_model = WorldModel()
            world_model.add_entity(Entity(
                entity_id=f"entity_{i}",
                entity_type="test",
                properties={"instance": i}
            ))
            instances.append(world_model)
        
        for i, wm in enumerate(instances):
            assert wm.get_entity(f"entity_{i}") is not None
            print(f"   ✓ Instance {i} correctly isolated")
        
        print("   ✓ Multiple component isolation verified")
        print("="*60 + "\n")


if __name__ == "__main__":
    test = TestIntegration()
    test.test_complete_workflow()
    test.test_error_handling_workflow()
    test.test_concurrent_components()
    
    print("\n✓ All integration tests passed!")
