"""
Unit tests for Ethics Framework (Financial / Ethical safety rules verification)
"""
import pytest
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.ethics import EthicsFramework, EthicalGuideline, EthicalRule, ValueSystem, EthicalPrinciple, EthicsDecision

def test_ethics_blocking_rule():
    ethics = EthicsFramework()
    
    value_system = ValueSystem(name="safety", description="safety first")
    guideline = EthicalGuideline(
        guideline_id="safety_guideline",
        name="Safety Guideline",
        description="protect system",
        value_system=value_system,
        rules=[
            EthicalRule(
                rule_id="block_delete",
                principle=EthicalPrinciple.SECURITY,
                description="block root deletions",
                condition="delete_root",
                action="block",
                severity=3
            )
        ]
    )
    ethics.add_guideline(guideline)
    
    # Custom evaluator to check if action deletes root
    def evaluator(action, context):
        return action.get("type") == "delete_root"
        
    ethics.register_rule_evaluator("block_delete", evaluator)
    
    # Test case 1: Safe action
    result_safe = ethics.check_ethics({"type": "read_file"}, {})
    assert result_safe.decision == EthicsDecision.APPROVED
    
    # Test case 2: Unsafe action (triggers block rule)
    result_unsafe = ethics.check_ethics({"type": "delete_root"}, {})
    assert result_unsafe.decision == EthicsDecision.BLOCKED
    assert result_unsafe.ethical_score == 0.0
