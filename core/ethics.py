"""
Ethics Framework - Value systems and ethical frameworks for Octopus Decision Layer

Provides ethical guidelines and value-based constraints for decision making.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum


class EthicalPrinciple(Enum):
    NON_MALEFICENCE = "non_maleficence"
    BENEFICENCE = "beneficence"
    AUTONOMY = "autonomy"
    JUSTICE = "justice"
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"
    SECURITY = "security"
    SUSTAINABILITY = "sustainability"


class EthicsDecision(Enum):
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"
    BLOCKED = "blocked"


@dataclass
class EthicalRule:
    rule_id: str
    principle: EthicalPrinciple
    description: str
    condition: str
    action: str
    severity: int = 1
    exceptions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "principle": self.principle.value,
            "description": self.description,
            "condition": self.condition,
            "action": self.action,
            "severity": self.severity,
            "exceptions": self.exceptions,
            "metadata": self.metadata,
        }


@dataclass
class EthicsCheckResult:
    decision: EthicsDecision
    applicable_rules: List[EthicalRule] = field(default_factory=list)
    violated_rules: List[EthicalRule] = field(default_factory=list)
    approved_rules: List[EthicalRule] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    review_required: bool = False
    review_reason: Optional[str] = None
    ethical_score: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "applicable_rules": [r.to_dict() for r in self.applicable_rules],
            "violated_rules": [r.to_dict() for r in self.violated_rules],
            "approved_rules": [r.to_dict() for r in self.approved_rules],
            "conditions": self.conditions,
            "review_required": self.review_required,
            "review_reason": self.review_reason,
            "ethical_score": self.ethical_score,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class ValueWeight:
    principle: EthicalPrinciple
    weight: float
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "principle": self.principle.value,
            "weight": self.weight,
            "description": self.description,
        }


class ValueSystem:
    def __init__(
        self,
        name: str,
        description: str = "",
        weights: Optional[List[ValueWeight]] = None
    ):
        self.name = name
        self.description = description
        self.weights: Dict[EthicalPrinciple, float] = {}
        
        if weights:
            for w in weights:
                self.weights[w.principle] = w.weight
        
        self._set_defaults()
    
    def _set_defaults(self):
        default_weights = {
            EthicalPrinciple.NON_MALEFICENCE: 1.0,
            EthicalPrinciple.BENEFICENCE: 0.8,
            EthicalPrinciple.AUTONOMY: 0.7,
            EthicalPrinciple.JUSTICE: 0.7,
            EthicalPrinciple.FAIRNESS: 0.7,
            EthicalPrinciple.TRANSPARENCY: 0.6,
            EthicalPrinciple.ACCOUNTABILITY: 0.6,
            EthicalPrinciple.PRIVACY: 0.8,
            EthicalPrinciple.SECURITY: 0.9,
            EthicalPrinciple.SUSTAINABILITY: 0.5,
        }
        
        for principle, weight in default_weights.items():
            if principle not in self.weights:
                self.weights[principle] = weight
    
    def get_weight(self, principle: EthicalPrinciple) -> float:
        return self.weights.get(principle, 0.5)
    
    def normalize_weights(self):
        total = sum(self.weights.values())
        if total > 0:
            for principle in self.weights:
                self.weights[principle] /= total
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "weights": {
                p.value: w for p, w in self.weights.items()
            },
        }


@dataclass
class EthicalGuideline:
    guideline_id: str
    name: str
    description: str
    value_system: ValueSystem
    rules: List[EthicalRule] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "guideline_id": self.guideline_id,
            "name": self.name,
            "description": self.description,
            "value_system": self.value_system.to_dict(),
            "rules": [r.to_dict() for r in self.rules],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class EthicsFramework:
    def __init__(self):
        self.guidelines: Dict[str, EthicalGuideline] = {}
        self.active_guideline: Optional[EthicalGuideline] = None
        self.rule_evaluators: Dict[str, Callable] = {}
        self.audit_log: List[Dict[str, Any]] = []
    
    def add_guideline(self, guideline: EthicalGuideline):
        self.guidelines[guideline.guideline_id] = guideline
        if guideline.is_active:
            self.active_guideline = guideline
    
    def set_active_guideline(self, guideline_id: str) -> bool:
        if guideline_id in self.guidelines:
            self.active_guideline = self.guidelines[guideline_id]
            return True
        return False
    
    def register_rule_evaluator(self, rule_id: str, evaluator: Callable):
        self.rule_evaluators[rule_id] = evaluator
    
    def check_ethics(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> EthicsCheckResult:
        if not self.active_guideline:
            return EthicsCheckResult(
                decision=EthicsDecision.APPROVED,
                details={"message": "No active ethics guideline"}
            )
        
        applicable_rules = self._find_applicable_rules(action, context)
        violated_rules = []
        approved_rules = []
        conditions = []
        review_required = False
        review_reason = None
        
        for rule in applicable_rules:
            is_violated = self._evaluate_rule(rule, action, context)
            
            if is_violated:
                violated_rules.append(rule)
                
                if rule.action == "block":
                    self._log_audit(action, rule, "blocked")
                    return EthicsCheckResult(
                        decision=EthicsDecision.BLOCKED,
                        applicable_rules=applicable_rules,
                        violated_rules=[rule],
                        review_required=False,
                        ethical_score=0.0,
                        details={"violated_rule": rule.rule_id},
                    )
                elif rule.action == "reject":
                    review_required = True
                    review_reason = f"Rejected by rule: {rule.rule_id}"
                elif rule.action == "review":
                    review_required = True
                    review_reason = rule.description
                elif rule.action == "condition":
                    conditions.append(rule.description)
            else:
                approved_rules.append(rule)
        
        if review_required:
            self._log_audit(action, None, "requires_review")
            return EthicsCheckResult(
                decision=EthicsDecision.REQUIRES_REVIEW,
                applicable_rules=applicable_rules,
                violated_rules=violated_rules,
                approved_rules=approved_rules,
                review_required=True,
                review_reason=review_reason,
                ethical_score=self._calculate_ethical_score(applicable_rules, violated_rules),
                details={"violated_count": len(violated_rules)},
            )
        
        if conditions:
            self._log_audit(action, None, "approved_with_conditions")
            return EthicsCheckResult(
                decision=EthicsDecision.APPROVED_WITH_CONDITIONS,
                applicable_rules=applicable_rules,
                approved_rules=approved_rules,
                conditions=conditions,
                ethical_score=self._calculate_ethical_score(applicable_rules, violated_rules),
                details={"condition_count": len(conditions)},
            )
        
        self._log_audit(action, None, "approved")
        return EthicsCheckResult(
            decision=EthicsDecision.APPROVED,
            applicable_rules=applicable_rules,
            approved_rules=approved_rules,
            ethical_score=self._calculate_ethical_score(applicable_rules, violated_rules),
            details={"message": "All ethical checks passed"},
        )
    
    def _find_applicable_rules(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[EthicalRule]:
        if not self.active_guideline:
            return []
        
        applicable = []
        action_type = action.get("type", "")
        
        for rule in self.active_guideline.rules:
            if self._is_rule_applicable(rule, action, context):
                applicable.append(rule)
        
        return applicable
    
    def _is_rule_applicable(
        self,
        rule: EthicalRule,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        if rule.rule_id in self.rule_evaluators:
            try:
                return self.rule_evaluators[rule.rule_id](action, context)
            except Exception:
                return False
        
        return True
    
    def _evaluate_rule(
        self,
        rule: EthicalRule,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        if rule.rule_id in self.rule_evaluators:
            try:
                return self.rule_evaluators[rule.rule_id](action, context)
            except Exception:
                return False
        
        return False
    
    def _calculate_ethical_score(
        self,
        applicable_rules: List[EthicalRule],
        violated_rules: List[EthicalRule]
    ) -> float:
        if not applicable_rules:
            return 1.0
        
        if not self.active_guideline:
            return 1.0
        
        total_weight = 0.0
        satisfied_weight = 0.0
        
        for rule in applicable_rules:
            principle_weight = self.active_guideline.value_system.get_weight(
                rule.principle
            )
            total_weight += principle_weight * rule.severity
            
            if rule not in violated_rules:
                satisfied_weight += principle_weight * rule.severity
        
        if total_weight == 0:
            return 1.0
        
        return satisfied_weight / total_weight
    
    def _log_audit(
        self,
        action: Dict[str, Any],
        rule: Optional[EthicalRule],
        result: str
    ):
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "action_type": action.get("type", "unknown"),
            "result": result,
            "rule_id": rule.rule_id if rule else None,
            "action": action,
        })
    
    def get_audit_log(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if limit:
            return self.audit_log[-limit:]
        return self.audit_log
    
    def create_default_guideline(self) -> EthicalGuideline:
        value_system = ValueSystem(
            name="Default",
            description="Default ethical value system",
        )
        
        rules = [
            EthicalRule(
                rule_id="privacy_protection",
                principle=EthicalPrinciple.PRIVACY,
                description="Protect user privacy and personal data",
                condition="action involves user data",
                action="condition",
                severity=2,
            ),
            EthicalRule(
                rule_id="security_check",
                principle=EthicalPrinciple.SECURITY,
                description="Ensure security best practices",
                condition="action involves system access",
                action="review",
                severity=3,
            ),
            EthicalRule(
                rule_id="transparency_requirement",
                principle=EthicalPrinciple.TRANSPARENCY,
                description="Maintain transparency in operations",
                condition="action has significant impact",
                action="condition",
                severity=1,
            ),
        ]
        
        return EthicalGuideline(
            guideline_id="default_guideline",
            name="Default Ethics Guideline",
            description="Standard ethical guidelines for Octopus",
            value_system=value_system,
            rules=rules,
        )
    
    def get_framework_summary(self) -> Dict[str, Any]:
        return {
            "total_guidelines": len(self.guidelines),
            "active_guideline": (
                self.active_guideline.name 
                if self.active_guideline else None
            ),
            "total_rules": sum(
                len(g.rules) for g in self.guidelines.values()
            ),
            "audit_entries": len(self.audit_log),
        }
