"""
Simulation Engine - Future scenario simulation for Octopus Decision Layer

Simulates possible futures in a virtual environment before making decisions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import random


class SimulationState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    FAILED = "failed"


@dataclass
class Scenario:
    scenario_id: str
    name: str
    initial_state: Dict[str, Any]
    actions_sequence: List[Dict[str, Any]]
    predicted_outcomes: Dict[str, Any]
    probability: float = 1.0
    risk_score: float = 0.0
    reward_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "initial_state": self.initial_state,
            "actions_sequence": self.actions_sequence,
            "predicted_outcomes": self.predicted_outcomes,
            "probability": self.probability,
            "risk_score": self.risk_score,
            "reward_score": self.reward_score,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class SimulationResult:
    scenario_id: str
    status: SimulationState
    final_state: Optional[Dict[str, Any]] = None
    intermediate_states: List[Dict[str, Any]] = field(default_factory=list)
    outcome_probability: float = 1.0
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "status": self.status.value,
            "final_state": self.final_state,
            "intermediate_states": self.intermediate_states,
            "outcome_probability": self.outcome_probability,
            "risk_assessment": self.risk_assessment,
            "success_metrics": self.success_metrics,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "completed_at": self.completed_at.isoformat(),
        }


@dataclass
class SimulationConfig:
    max_depth: int = 5
    max_branches: int = 3
    simulation_time_horizon: int = 100
    uncertainty_level: float = 0.1
    risk_weight: float = 0.4
    reward_weight: float = 0.6
    enable_monte_carlo: bool = False
    monte_carlo_iterations: int = 100
    early_stopping_threshold: float = 0.9


class ActionSimulator:
    def __init__(self):
        self.action_models: Dict[str, Callable] = {}
    
    def register_action_model(self, action_type: str, model: Callable):
        self.action_models[action_type] = model
    
    def simulate_action(
        self, 
        action: Dict[str, Any], 
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        action_type = action.get("type", "unknown")
        
        if action_type in self.action_models:
            return self.action_models[action_type](action, current_state)
        
        return self._default_simulation(action, current_state)
    
    def _default_simulation(
        self, 
        action: Dict[str, Any], 
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        new_state = dict(current_state)
        new_state["last_action"] = action
        new_state["action_applied"] = True
        return new_state


class SimulationEngine:
    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.action_simulator = ActionSimulator()
        self.world_model_accessor: Optional[Callable] = None
        self.simulation_history: List[SimulationResult] = []
        self.scenario_templates: Dict[str, Scenario] = {}
    
    def set_world_model_accessor(self, accessor: Callable):
        self.world_model_accessor = accessor
    
    def simulate_scenario(self, scenario: Scenario) -> SimulationResult:
        start_time = datetime.now()
        
        try:
            current_state = dict(scenario.initial_state)
            intermediate_states = []
            
            for i, action in enumerate(scenario.actions_sequence):
                if i >= self.config.max_depth:
                    break
                
                simulated_state = self.action_simulator.simulate_action(
                    action, current_state
                )
                intermediate_states.append(simulated_state)
                current_state = simulated_state
            
            final_state = self._predict_final_outcome(
                current_state, 
                scenario
            )
            
            risk_assessment = self._assess_risk(
                final_state, 
                scenario
            )
            
            success_metrics = self._calculate_success_metrics(
                final_state,
                scenario
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = SimulationResult(
                scenario_id=scenario.scenario_id,
                status=SimulationState.COMPLETED,
                final_state=final_state,
                intermediate_states=intermediate_states,
                outcome_probability=scenario.probability,
                risk_assessment=risk_assessment,
                success_metrics=success_metrics,
                execution_time_ms=execution_time,
            )
            
            self.simulation_history.append(result)
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return SimulationResult(
                scenario_id=scenario.scenario_id,
                status=SimulationState.FAILED,
                error=str(e),
                execution_time_ms=execution_time,
            )
    
    def simulate_action_sequence(
        self,
        initial_state: Dict[str, Any],
        actions: List[Dict[str, Any]]
    ) -> SimulationResult:
        scenario = Scenario(
            scenario_id=f"scenario_{datetime.now().timestamp()}",
            name="Ad-hoc Simulation",
            initial_state=initial_state,
            actions_sequence=actions,
            predicted_outcomes={},
        )
        return self.simulate_scenario(scenario)
    
    def generate_scenario_variants(
        self,
        base_scenario: Scenario,
        variation_count: int = 3
    ) -> List[Scenario]:
        variants = []
        
        for i in range(variation_count):
            variant = self._create_variant(base_scenario, i)
            variants.append(variant)
        
        return variants
    
    def _create_variant(
        self, 
        base: Scenario, 
        variant_index: int
    ) -> Scenario:
        variant_state = dict(base.initial_state)
        
        for key in variant_state:
            if isinstance(variant_state[key], (int, float)):
                variation = variant_state[key] * self.config.uncertainty_level
                variant_state[key] += random.uniform(-variation, variation)
        
        variant_actions = []
        for action in base.actions_sequence:
            variant_action = dict(action)
            if random.random() < self.config.uncertainty_level:
                if "parameters" in variant_action:
                    variant_action["parameters"] = dict(variant_action["parameters"])
            variant_actions.append(variant_action)
        
        return Scenario(
            scenario_id=f"{base.scenario_id}_variant_{variant_index}",
            name=f"{base.name} - Variant {variant_index}",
            initial_state=variant_state,
            actions_sequence=variant_actions,
            predicted_outcomes={},
            probability=base.probability * (1 - self.config.uncertainty_level),
        )
    
    def _predict_final_outcome(
        self,
        current_state: Dict[str, Any],
        scenario: Scenario
    ) -> Dict[str, Any]:
        outcome = dict(current_state)
        outcome["predicted_success"] = True
        outcome["confidence"] = scenario.probability
        return outcome
    
    def _assess_risk(
        self,
        final_state: Dict[str, Any],
        scenario: Scenario
    ) -> Dict[str, float]:
        risk_factors = {
            "execution_risk": random.uniform(0, 0.3),
            "state_risk": random.uniform(0, 0.2),
            "uncertainty_risk": self.config.uncertainty_level,
        }
        
        total_risk = sum(risk_factors.values()) / len(risk_factors)
        risk_factors["total_risk"] = total_risk
        
        return risk_factors
    
    def _calculate_success_metrics(
        self,
        final_state: Dict[str, Any],
        scenario: Scenario
    ) -> Dict[str, float]:
        metrics = {
            "goal_achievement": random.uniform(0.7, 1.0),
            "efficiency": random.uniform(0.6, 0.95),
            "resource_usage": random.uniform(0.3, 0.8),
        }
        
        metrics["overall_score"] = (
            metrics["goal_achievement"] * self.config.reward_weight +
            (1 - metrics["resource_usage"]) * self.config.risk_weight
        )
        
        return metrics
    
    def compare_scenarios(
        self,
        scenarios: List[Scenario]
    ) -> List[SimulationResult]:
        results = []
        
        for scenario in scenarios:
            result = self.simulate_scenario(scenario)
            results.append(result)
        
        results.sort(key=lambda x: x.success_metrics.get("overall_score", 0), reverse=True)
        return results
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        return {
            "total_simulations": len(self.simulation_history),
            "successful_simulations": sum(
                1 for r in self.simulation_history 
                if r.status == SimulationState.COMPLETED
            ),
            "failed_simulations": sum(
                1 for r in self.simulation_history 
                if r.status == SimulationState.FAILED
            ),
            "average_execution_time_ms": (
                sum(r.execution_time_ms for r in self.simulation_history) / 
                len(self.simulation_history) if self.simulation_history else 0
            ),
            "templates_count": len(self.scenario_templates),
        }
