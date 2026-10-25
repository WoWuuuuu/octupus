import pytest

from core.decision_guidance import (
    DecisionGuidance,
    DEFAULT_DECISION_GUIDANCE,
    load_decision_guidance,
    init_decision_guidance,
)


CONCRETE_GUIDANCE = """# decision.md

Status: Example
Schema Version: 0.1
Artifact Type: Decision Guidance

## Decision Scope

```md
Domain: personal_work_coordination
Decision Class: time_sensitive_attention
Authority: default_policy_guidance
```

## Primary Objective

```md
Primary Objective:
Maximize probability of leaving on time.
```

## Secondary Objectives

```md
- reduce blocker impact
- preserve reversibility
```

## Preferences / Weights

```md
- flight_readiness: 0.6
- pr_risk_reduction: 0.3
- reversibility: 0.1
```

## Hard Constraints

```md
- never endanger the fixed physical commitment
```

## Trade-off Rules

```md
- when time is tight, prefer reversible actions
```

## Decision Principles

```md
- prefer observability first
```

## Evaluation Criteria

```md
- does it improve decision quality
```

## Reflection Guidance

```md
- was a smaller reversible option available
```
"""


class TestParsing:
    def test_parse_template_sections(self):
        guidance = DecisionGuidance.from_text(DEFAULT_DECISION_GUIDANCE)

        assert guidance.schema_version == "0.1"
        assert guidance.artifact_type == "Decision Guidance"
        assert guidance.primary_objective
        assert guidance.secondary_objectives
        assert guidance.weights
        assert guidance.hard_constraints
        assert guidance.trade_off_rules
        assert guidance.decision_principles
        assert guidance.evaluation_criteria
        assert guidance.reflection_guidance

    def test_parse_template_weights_sum_to_one(self):
        guidance = DecisionGuidance.from_text(DEFAULT_DECISION_GUIDANCE)
        assert sum(guidance.weights.values()) == pytest.approx(1.0)
        assert guidance.weights["outcome_value"] == pytest.approx(0.40)

    def test_parse_concrete_values(self):
        guidance = DecisionGuidance.from_text(CONCRETE_GUIDANCE)

        assert guidance.primary_objective == "Maximize probability of leaving on time."
        assert guidance.weights == {
            "flight_readiness": 0.6,
            "pr_risk_reduction": 0.3,
            "reversibility": 0.1,
        }
        assert guidance.scope["Domain"] == "personal_work_coordination"
        assert guidance.hard_constraints == ["never endanger the fixed physical commitment"]

    def test_empty_document_yields_warnings(self):
        guidance = DecisionGuidance.from_text("# decision.md\n")
        warnings = guidance.validate()
        assert any("Primary Objective" in w for w in warnings)
        assert any("Weights" in w for w in warnings)
        assert any("Hard Constraints" in w for w in warnings)

    def test_weights_not_normalized_warns(self):
        guidance = DecisionGuidance.from_text(
            "# decision.md\n\n## Preferences / Weights\n\n```md\n- a: 0.9\n- b: 0.9\n```\n"
        )
        assert any("权重总和" in w for w in guidance.validate())


class TestMapping:
    def test_to_criteria(self):
        guidance = DecisionGuidance.from_text(CONCRETE_GUIDANCE)
        criteria = guidance.to_criteria()
        assert len(criteria) == 3
        assert criteria[0].name == "flight_readiness"
        assert criteria[0].weight == pytest.approx(0.6)

    def test_to_policy(self):
        guidance = DecisionGuidance.from_text(CONCRETE_GUIDANCE)
        policy = guidance.to_policy()
        assert policy.is_active is True
        assert len(policy.criteria) == 3
        assert policy.hard_constraints == ["never endanger the fixed physical commitment"]

    def test_to_prompt_contains_key_parts(self):
        guidance = DecisionGuidance.from_text(CONCRETE_GUIDANCE)
        prompt = guidance.to_prompt()
        assert "Maximize probability of leaving on time." in prompt
        assert "flight_readiness" in prompt
        assert "Hard Constraints" in prompt


class TestLoading:
    def test_load_returns_none_when_missing(self, tmp_path):
        assert load_decision_guidance(str(tmp_path)) is None

    def test_init_then_load(self, tmp_path):
        path = init_decision_guidance(str(tmp_path / ".octopus"))
        assert path.exists()

        guidance = load_decision_guidance(str(tmp_path))
        assert guidance is not None
        assert guidance.path.endswith("decision.md")
        assert guidance.primary_objective

    def test_init_does_not_overwrite_by_default(self, tmp_path):
        init_decision_guidance(str(tmp_path / ".octopus"))
        with pytest.raises(FileExistsError):
            init_decision_guidance(str(tmp_path / ".octopus"))

    def test_init_force_overwrites(self, tmp_path):
        target = tmp_path / ".octopus" / "decision.md"
        init_decision_guidance(str(tmp_path / ".octopus"))
        target.write_text("stale", encoding="utf-8")

        init_decision_guidance(str(tmp_path / ".octopus"), force=True)
        assert "stale" not in target.read_text(encoding="utf-8")


class TestEngineIntegration:
    def test_set_decision_guidance_activates_policy(self):
        from core.decision_engine import DecisionEngine

        engine = DecisionEngine()
        assert engine.decision_guidance is None

        guidance = DecisionGuidance.from_text(CONCRETE_GUIDANCE)
        engine.set_decision_guidance(guidance)

        assert engine.decision_guidance is guidance
        assert engine.active_policy is not None
        assert [c.name for c in engine.active_policy.criteria] == [
            "flight_readiness",
            "pr_risk_reduction",
            "reversibility",
        ]

    def test_clear_decision_guidance(self):
        from core.decision_engine import DecisionEngine

        engine = DecisionEngine()
        engine.set_decision_guidance(DecisionGuidance.from_text(CONCRETE_GUIDANCE))
        engine.clear_decision_guidance()
        assert engine.decision_guidance is None
