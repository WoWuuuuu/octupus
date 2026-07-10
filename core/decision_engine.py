"""
Decision Engine - Core decision-making component for Octopus Decision Layer

Evaluates options, compares trade-offs, and makes structured decisions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid


class DecisionStatus(Enum):
    PENDING = "pending"
    EVALUATING = "evaluating"
    DECIDED = "decided"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DecisionPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class DecisionCriteria:
    name: str
    weight: float
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "weight": self.weight,
            "description": self.description,
        }


@dataclass
class DecisionOption:
    option_id: str
    name: str
    description: str
    action_sequence: List[Dict[str, Any]]
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0
    risk_level: float = 0.0
    reversibility: float = 0.5
    confidence: float = 1.0
    constraints_satisfied: bool = True
    estimated_cost: float = 0.0
    estimated_benefit: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_total_score(self, criteria: List[DecisionCriteria]) -> float:
        if not self.criteria_scores:
            return 0.0
        
        total_weight = sum(c.weight for c in criteria)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            self.criteria_scores.get(c.name, 0.0) * c.weight 
            for c in criteria
        )
        
        self.total_score = weighted_sum / total_weight
        return self.total_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "option_id": self.option_id,
            "name": self.name,
            "description": self.description,
            "action_sequence": self.action_sequence,
            "criteria_scores": self.criteria_scores,
            "total_score": self.total_score,
            "risk_level": self.risk_level,
            "reversibility": self.reversibility,
            "confidence": self.confidence,
            "constraints_satisfied": self.constraints_satisfied,
            "estimated_cost": self.estimated_cost,
            "estimated_benefit": self.estimated_benefit,
            "metadata": self.metadata,
        }


@dataclass
class Decision:
    decision_id: str
    context: Dict[str, Any]
    options: List[DecisionOption]
    selected_option: Optional[DecisionOption] = None
    status: DecisionStatus = DecisionStatus.PENDING
    priority: DecisionPriority = DecisionPriority.NORMAL
    criteria: List[DecisionCriteria] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 0.0
    execution_intent: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    decided_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def select_best_option(self) -> Optional[DecisionOption]:
        if not self.options:
            return None
        
        valid_options = [
            opt for opt in self.options 
            if opt.constraints_satisfied and opt.total_score > 0
        ]
        
        if not valid_options:
            valid_options = self.options
        
        best_option = max(valid_options, key=lambda x: x.total_score)
        self.selected_option = best_option
        self.status = DecisionStatus.DECIDED
        self.decided_at = datetime.now()
        self.confidence = best_option.confidence
        
        return best_option
    
    def create_execution_intent(self) -> Optional[Dict[str, Any]]:
        if not self.selected_option:
            return None
        
        self.execution_intent = {
            "intent_id": str(uuid.uuid4()),
            "action_type": "decision_execution",
            "parameters": {
                "decision_id": self.decision_id,
                "selected_option": self.selected_option.to_dict(),
                "action_sequence": self.selected_option.action_sequence,
            },
            "priority": self.priority.value,
            "constraints": self.constraints,
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "reasoning": self.reasoning,
            },
        }
        
        return self.execution_intent
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "context": self.context,
            "options": [o.to_dict() for o in self.options],
            "selected_option": self.selected_option.to_dict() if self.selected_option else None,
            "status": self.status.value,
            "priority": self.priority.value,
            "criteria": [c.to_dict() for c in self.criteria],
            "constraints": self.constraints,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "execution_intent": self.execution_intent,
            "created_at": self.created_at.isoformat(),
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


@dataclass
class DecisionPolicy:
    policy_id: str
    name: str
    description: str
    criteria: List[DecisionCriteria]
    hard_constraints: List[str] = field(default_factory=list)
    trade_off_rules: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    priority_override: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "criteria": [c.to_dict() for c in self.criteria],
            "hard_constraints": self.hard_constraints,
            "trade_off_rules": self.trade_off_rules,
            "is_active": self.is_active,
            "priority_override": self.priority_override,
        }


class DecisionEngine:
    def __init__(self):
        self.policies: Dict[str, DecisionPolicy] = {}
        self.active_policy: Optional[DecisionPolicy] = None
        self.decision_history: List[Decision] = []
        self.simulation_engine = None
        self.world_model = None
        self.decision_callbacks: List[Callable] = []
    
    def set_simulation_engine(self, engine):
        self.simulation_engine = engine
    
    def set_world_model(self, world_model):
        self.world_model = world_model
    
    def add_policy(self, policy: DecisionPolicy):
        self.policies[policy.policy_id] = policy
        if policy.is_active:
            self.active_policy = policy
    
    def set_active_policy(self, policy_id: str) -> bool:
        if policy_id in self.policies:
            self.active_policy = self.policies[policy_id]
            return True
        return False
    
    def make_decision(
        self,
        context: Dict[str, Any],
        options: List[Dict[str, Any]],
        constraints: Optional[List[str]] = None,
        priority: DecisionPriority = DecisionPriority.NORMAL
    ) -> Decision:
        import json
        from core.llm_client import llm
        
        decision_id = f"decision_{datetime.now().timestamp()}"
        
        criteria = self.active_policy.criteria if self.active_policy else self._get_default_criteria()
        hard_constraints = self.active_policy.hard_constraints if self.active_policy else []
        
        decision = Decision(
            decision_id=decision_id,
            context=context,
            options=[],
            priority=priority,
            criteria=criteria,
            constraints=constraints or [],
        )
        
        for option_data in options:
            option = self._create_option(option_data, criteria, hard_constraints)
            decision.options.append(option)
        
        if self.simulation_engine:
            decision = self._enrich_with_simulation(decision)
            
        # ==========================================
        # SPICE-PATTERN: LLM Integration (Phase 2)
        # ==========================================
        try:
            options_json = json.dumps([opt.to_dict() for opt in decision.options], indent=2)
            context_json = json.dumps(context, indent=2)
            
            system_prompt = """
You are the Brain/Decision Engine of the Octopus framework.
Your task is to evaluate the provided Decision Options against the current World State (Context) and select the best one.
You must output a strictly formatted JSON object:
{
    "selected_option_id": "the ID of the best option",
    "reasoning": "detailed explanation of why this option is best, including trade-offs considered",
    "confidence": 0.95
}
"""
            prompt = f"WORLD STATE CONTEXT:\n{context_json}\n\nOPTIONS:\n{options_json}\n\nPlease evaluate and select the best option in JSON."
            
            # Using higher temperature for creative reasoning, following Spice pattern
            response = llm.chat(
                prompt=prompt, 
                system_prompt=system_prompt, 
                json_mode=True,
                temperature=0.7
            )
            
            llm_result = json.loads(response)
            
            selected_id = llm_result.get("selected_option_id")
            selected_opt = next((opt for opt in decision.options if opt.option_id == selected_id), None)
            
            if selected_opt:
                decision.selected_option = selected_opt
                decision.reasoning = llm_result.get("reasoning", "LLM provided no reasoning.")
                decision.confidence = float(llm_result.get("confidence", 0.5))
                decision.status = DecisionStatus.DECIDED
                decision.decided_at = datetime.now()
            else:
                # LLM hallucinated an invalid ID
                print(f"[DecisionEngine] LLM returned invalid option_id: {selected_id}")
                decision.status = DecisionStatus.FAILED
                
        except Exception as e:
            print(f"[DecisionEngine] LLM Decision failed: {e}")
            decision.status = DecisionStatus.FAILED
            decision.reasoning = f"LLM Failure: {str(e)}"
            
        # Create execution intent if decided successfully
        if decision.status == DecisionStatus.DECIDED and decision.selected_option:
            decision.create_execution_intent()
        
        self.decision_history.append(decision)
        
        for callback in self.decision_callbacks:
            try:
                callback(decision)
            except Exception:
                pass
        
        return decision
    
    def _get_default_criteria(self) -> List[DecisionCriteria]:
        return [
            DecisionCriteria(
                name="outcome_value",
                weight=0.40,
                description="Value of the expected outcome"
            ),
            DecisionCriteria(
                name="risk_reduction",
                weight=0.25,
                description="Reduction in potential risks"
            ),
            DecisionCriteria(
                name="reversibility",
                weight=0.20,
                description="Ease of reversing the decision"
            ),
            DecisionCriteria(
                name="confidence_alignment",
                weight=0.15,
                description="Alignment with confidence levels"
            ),
        ]
    
    def _create_option(
        self,
        option_data: Dict[str, Any],
        criteria: List[DecisionCriteria],
        hard_constraints: List[str]
    ) -> DecisionOption:
        option = DecisionOption(
            option_id=option_data.get("option_id", str(uuid.uuid4())),
            name=option_data.get("name", "Unnamed Option"),
            description=option_data.get("description", ""),
            action_sequence=option_data.get("actions", []),
            criteria_scores=option_data.get("scores", {}),
            risk_level=option_data.get("risk_level", 0.5),
            reversibility=option_data.get("reversibility", 0.5),
            confidence=option_data.get("confidence", 1.0),
            estimated_cost=option_data.get("cost", 0.0),
            estimated_benefit=option_data.get("benefit", 0.0),
        )
        
        for criterion in criteria:
            if criterion.name not in option.criteria_scores:
                option.criteria_scores[criterion.name] = 0.5
        
        option.calculate_total_score(criteria)
        
        option.constraints_satisfied = self._check_constraints(
            option, 
            hard_constraints
        )
        
        return option
    
    def _check_constraints(
        self,
        option: DecisionOption,
        hard_constraints: List[str]
    ) -> bool:
        for constraint in hard_constraints:
            if constraint in option.metadata.get("violated_constraints", []):
                return False
        return True
    
    def _enrich_with_simulation(self, decision: Decision) -> Decision:
        for option in decision.options:
            try:
                result = self.simulation_engine.simulate_action_sequence(
                    decision.context,
                    option.action_sequence
                )
                
                if result.status.value == "completed":
                    option.criteria_scores["outcome_value"] = (
                        result.success_metrics.get("overall_score", 0.5)
                    )
                    option.risk_level = result.risk_assessment.get("total_risk", 0.5)
                    option.calculate_total_score(decision.criteria)
            except Exception:
                pass
        
        return decision
    
    def _generate_reasoning(self, decision: Decision) -> str:
        if not decision.selected_option:
            return "No suitable option found."
        
        best = decision.selected_option
        reasoning_parts = [
            f"Selected '{best.name}' with total score {best.total_score:.2f}.",
            f"Risk level: {best.risk_level:.2f}.",
            f"Reversibility: {best.reversibility:.2f}.",
        ]
        
        if decision.criteria:
            top_criteria = sorted(
                [(c.name, best.criteria_scores.get(c.name, 0)) 
                 for c in decision.criteria],
                key=lambda x: x[1],
                reverse=True
            )[:2]
            
            reasoning_parts.append(
                f"Top criteria: {', '.join(f'{k}({v:.2f})' for k, v in top_criteria)}."
            )
        
        return " ".join(reasoning_parts)
    
    def register_decision_callback(self, callback: Callable):
        self.decision_callbacks.append(callback)
    
    def get_decision(self, decision_id: str) -> Optional[Decision]:
        for decision in self.decision_history:
            if decision.decision_id == decision_id:
                return decision
        return None
    
    def get_decision_summary(self) -> Dict[str, Any]:
        return {
            "total_decisions": len(self.decision_history),
            "active_policy": (
                self.active_policy.name if self.active_policy else None
            ),
            "policies_count": len(self.policies),
            "recent_decisions": [
                {
                    "decision_id": d.decision_id,
                    "status": d.status.value,
                    "selected_option": (
                        d.selected_option.name if d.selected_option else None
                    ),
                    "confidence": d.confidence,
                }
                for d in self.decision_history[-5:]
            ],
        }
