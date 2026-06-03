"""
Tests for Octopus Decision Layer Components
"""

import pytest
from datetime import datetime
from octopus.core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    SimulationConfig,
    DecisionEngine,
    DecisionPolicy,
    DecisionCriteria,
    LongTermMemory,
    MemoryType,
    EthicsFramework,
    Entity,
    Intent,
    IntentType,
)


class TestWorldModel:
    def test_create_world_model(self):
        world = WorldModel()
        assert world is not None
        assert len(world.entities) == 0
    
    def test_add_entity(self):
        world = WorldModel()
        entity = Entity(
            entity_id="test_1",
            entity_type="test",
            properties={"name": "test"}
        )
        world.add_entity(entity)
        assert len(world.entities) == 1
        assert world.get_entity("test_1") is not None
    
    def test_update_entity(self):
        world = WorldModel()
        entity = Entity(
            entity_id="test_1",
            entity_type="test",
            properties={"name": "original"}
        )
        world.add_entity(entity)
        
        result = world.update_entity("test_1", {"name": "updated"})
        assert result is True
        assert world.get_entity("test_1").properties["name"] == "updated"
    
    def test_global_state(self):
        world = WorldModel()
        world.set_global_state("key", "value")
        assert world.get_global_state("key") == "value"
        assert world.get_global_state("nonexistent", "default") == "default"
    
    def test_goals(self):
        world = WorldModel()
        world.add_goal("goal_1")
        assert "goal_1" in world.get_global_state("active_goals", [])
        world.remove_goal("goal_1")
        assert "goal_1" not in world.get_global_state("active_goals", [])
    
    def test_constraints(self):
        world = WorldModel()
        world.add_constraint("constraint_1")
        assert world.check_constraint("constraint_1") is True
        assert world.check_constraint("constraint_2") is False
    
    def test_snapshot(self):
        world = WorldModel()
        entity = Entity(
            entity_id="test_1",
            entity_type="test",
            properties={"value": 1}
        )
        world.add_entity(entity)
        
        snapshot = world.create_snapshot()
        assert snapshot is not None
        assert len(world.snapshots) == 1
        
        world.update_entity("test_1", {"value": 2})
        assert world.get_entity("test_1").properties["value"] == 2
        
        world.restore_snapshot(snapshot.snapshot_id)
        assert world.get_entity("test_1").properties["value"] == 1


class TestPerceptionModule:
    def test_create_perception_module(self):
        perception = PerceptionModule()
        assert perception is not None
    
    def test_perceive_query(self):
        perception = PerceptionModule()
        result = perception.perceive("What is the weather today?")
        assert len(result.intents) > 0
        assert result.intents[0].intent_type == IntentType.QUERY
    
    def test_perceive_command(self):
        perception = PerceptionModule()
        result = perception.perceive("Please execute the analysis")
        assert len(result.intents) > 0
        assert result.intents[0].intent_type == IntentType.COMMAND
    
    def test_perceive_error_observation(self):
        perception = PerceptionModule()
        result = perception.perceive("The system failed with error")
        assert len(result.intents) > 0
        assert result.intents[0].intent_type == IntentType.ERROR_OBSERVATION
    
    def test_confidence_calculation(self):
        perception = PerceptionModule()
        result = perception.perceive("Test input")
        assert 0.0 <= result.confidence <= 1.0


class TestSimulationEngine:
    def test_create_simulation_engine(self):
        engine = SimulationEngine()
        assert engine is not None
    
    def test_simulate_action_sequence(self):
        engine = SimulationEngine()
        initial_state = {"value": 10}
        actions = [
            {"type": "add", "parameters": {"amount": 5}},
            {"type": "multiply", "parameters": {"factor": 2}},
        ]
        
        result = engine.simulate_action_sequence(initial_state, actions)
        assert result is not None
        assert result.status.value == "completed"
    
    def test_scenario_variants(self):
        engine = SimulationEngine()
        from octopus.core.simulation import Scenario
        
        base_scenario = Scenario(
            scenario_id="base",
            name="Base Scenario",
            initial_state={"value": 10},
            actions_sequence=[{"type": "action"}],
            predicted_outcomes={},
        )
        
        variants = engine.generate_scenario_variants(base_scenario, 3)
        assert len(variants) == 3
    
    def test_compare_scenarios(self):
        engine = SimulationEngine()
        from octopus.core.simulation import Scenario
        
        scenarios = [
            Scenario(
                scenario_id=f"scenario_{i}",
                name=f"Scenario {i}",
                initial_state={"value": 10},
                actions_sequence=[],
                predicted_outcomes={},
            )
            for i in range(3)
        ]
        
        results = engine.compare_scenarios(scenarios)
        assert len(results) == 3


class TestDecisionEngine:
    def test_create_decision_engine(self):
        decision = DecisionEngine()
        assert decision is not None
    
    def test_make_decision_no_options(self):
        decision = DecisionEngine()
        result = decision.make_decision({}, [])
        assert result is not None
        assert result.selected_option is None
    
    def test_make_decision_with_options(self):
        decision = DecisionEngine()
        context = {"task": "test"}
        options = [
            {
                "name": "Option A",
                "description": "Test option",
                "actions": [],
                "scores": {
                    "outcome_value": 0.8,
                    "risk_reduction": 0.6,
                    "reversibility": 0.7,
                    "confidence_alignment": 0.9,
                },
            },
            {
                "name": "Option B",
                "description": "Another option",
                "actions": [],
                "scores": {
                    "outcome_value": 0.6,
                    "risk_reduction": 0.8,
                    "reversibility": 0.9,
                    "confidence_alignment": 0.7,
                },
            },
        ]
        
        result = decision.make_decision(context, options)
        assert result is not None
        assert result.selected_option is not None
        assert result.selected_option.name in ["Option A", "Option B"]
    
    def test_decision_with_policy(self):
        decision = DecisionEngine()
        policy = DecisionPolicy(
            policy_id="test_policy",
            name="Test Policy",
            description="Test policy description",
            criteria=[
                DecisionCriteria("outcome_value", 0.50, "Value metric"),
                DecisionCriteria("risk_reduction", 0.30, "Risk metric"),
                DecisionCriteria("reversibility", 0.20, "Reversibility metric"),
            ],
        )
        
        decision.add_policy(policy)
        assert decision.active_policy is not None
        assert decision.active_policy.name == "Test Policy"
    
    def test_decision_reasoning(self):
        decision = DecisionEngine()
        options = [
            {
                "name": "Best Option",
                "description": "Clearly better",
                "actions": [],
                "scores": {
                    "outcome_value": 1.0,
                    "risk_reduction": 1.0,
                    "reversibility": 1.0,
                    "confidence_alignment": 1.0,
                },
            },
        ]
        
        result = decision.make_decision({}, options)
        assert result.reasoning != ""
        assert "Best Option" in result.reasoning


class TestLongTermMemory:
    def test_create_long_term_memory(self):
        memory = LongTermMemory()
        assert memory is not None
        assert len(memory.memories) == 0
    
    def test_store_memory(self):
        memory = LongTermMemory()
        result = memory.store(
            content={"event": "test"},
            memory_type=MemoryType.EPISODIC,
            tags=["test"],
        )
        assert result is not None
        assert len(memory.memories) == 1
    
    def test_retrieve_memory(self):
        memory = LongTermMemory()
        stored = memory.store(
            content={"event": "test"},
            memory_type=MemoryType.EPISODIC,
        )
        
        retrieved = memory.retrieve(stored.memory_id)
        assert retrieved is not None
        assert retrieved.content["event"] == "test"
    
    def test_search_by_type(self):
        memory = LongTermMemory()
        memory.store(
            content={"type": "A"},
            memory_type=MemoryType.EPISODIC,
        )
        memory.store(
            content={"type": "B"},
            memory_type=MemoryType.SEMANTIC,
        )
        
        results = memory.search(memory_type=MemoryType.EPISODIC)
        assert len(results) == 1
        assert results[0].content["type"] == "A"
    
    def test_search_by_tags(self):
        memory = LongTermMemory()
        memory.store(
            content={"data": "1"},
            tags=["important", "urgent"],
        )
        memory.store(
            content={"data": "2"},
            tags=["important"],
        )
        
        results = memory.search(tags=["important"])
        assert len(results) == 2
    
    def test_cleanup_expired(self):
        memory = LongTermMemory(default_ttl=0)
        memory.store(
            content={"test": "data"},
            memory_type=MemoryType.EPISODIC,
        )
        
        import time
        time.sleep(0.1)
        
        cleaned = memory.cleanup_expired()
        assert cleaned >= 0


class TestEthicsFramework:
    def test_create_ethics_framework(self):
        ethics = EthicsFramework()
        assert ethics is not None
    
    def test_default_guideline(self):
        ethics = EthicsFramework()
        guideline = ethics.create_default_guideline()
        assert guideline is not None
        assert len(guideline.rules) > 0
    
    def test_ethics_check(self):
        ethics = EthicsFramework()
        guideline = ethics.create_default_guideline()
        ethics.add_guideline(guideline)
        
        action = {
            "type": "read",
            "target": "user_data",
        }
        
        result = ethics.check_ethics(action, {})
        assert result is not None
        assert result.decision.value in ["approved", "approved_with_conditions"]
    
    def test_audit_log(self):
        ethics = EthicsFramework()
        guideline = ethics.create_default_guideline()
        ethics.add_guideline(guideline)
        
        ethics.check_ethics({"type": "test"}, {})
        
        log = ethics.get_audit_log()
        assert len(log) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
