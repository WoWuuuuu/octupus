"""
Decision Guidance - Human-readable decision guidance artifact for Octopus.

`decision.md` declares, in plain language, what a decision should optimise,
how much each scoring dimension matters, which constraints are absolute, and
how trade-offs should be resolved.

It is read by the decision layer and mapped into a DecisionPolicy, and it is
also injected into the LLM decision prompt. It is intentionally bounded to
decision guidance: it is not memory, not a log, and it never executes actions.

Default location: <workspace>/.octopus/decision.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = "0.1"
ARTIFACT_TYPE = "Decision Guidance"
DEFAULT_GUIDANCE_DIR = ".octopus"
DEFAULT_GUIDANCE_FILENAME = "decision.md"

# Sections that influence runtime behaviour in v1.
RUNTIME_ACTIVE_SECTIONS = (
    "Primary Objective",
    "Preferences / Weights",
    "Hard Constraints",
    "Trade-off Rules",
)

# Sections that are parsed and shown, but not yet used at runtime.
RUNTIME_INACTIVE_SECTIONS = (
    "Decision Principles",
    "Evaluation Criteria",
    "Reflection Guidance",
)

_SECTION_ALIASES = {
    "preferences / weights": "weights",
    "preferences": "weights",
    "weights": "weights",
    "primary objective": "primary_objective",
    "secondary objectives": "secondary_objectives",
    "hard constraints": "hard_constraints",
    "trade-off rules": "trade_off_rules",
    "tradeoff rules": "trade_off_rules",
    "decision principles": "decision_principles",
    "evaluation criteria": "evaluation_criteria",
    "reflection guidance": "reflection_guidance",
    "decision scope": "scope",
}


DEFAULT_DECISION_GUIDANCE = """# decision.md

Status: Template
Schema Version: 0.1
Artifact Type: Decision Guidance

`decision.md` 是 Octopus 的决策指导文件。

它用人类可读的方式声明：这次决策要优化什么、各项标准的权重、不可逾越的硬约束，
以及取舍规则。Octopus 在决策时会读取它，用来影响候选方案的评价与选择。

它只描述「决策应该如何被评价和选择」，不记录历史、不存记忆、不执行动作。

## Decision Scope

```md
Domain: <决策所属领域>
Decision Class: <决策类型>
Applies To: <适用情形>
Does Not Apply To: <不适用情形>
Authority: default_policy_guidance
```

## Primary Objective

```md
Primary Objective:
<一句话说明这次决策最想优化什么>
```

## Secondary Objectives

```md
- <次要目标 1>
- <次要目标 2>
```

## Preferences / Weights

```md
- outcome_value: 0.40
- risk_reduction: 0.25
- reversibility: 0.20
- confidence_alignment: 0.15
```

## Hard Constraints

```md
- <硬约束：一旦违反，候选方案直接淘汰>
```

## Trade-off Rules

```md
- <取舍规则：在什么条件下优先谁>
```

## Decision Principles

```md
- <决策原则>
```

## Evaluation Criteria

```md
- <评价标准说明>
```

## Reflection Guidance

```md
- <复盘时要问自己的问题>
```
"""


def _split_sections(text: str) -> Dict[str, str]:
    """Split a markdown document into {section title: body} by level-2 headings."""
    sections: Dict[str, str] = {}
    current: Optional[str] = None
    buffer: List[str] = []

    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = match.group(1).strip()
            buffer = []
        elif current is not None:
            buffer.append(line)

    if current is not None:
        sections[current] = "\n".join(buffer).strip()

    return sections


def _extract_block(body: str) -> str:
    """Return the first fenced code block, or the whole body if there is none."""
    match = re.search(r"```[a-zA-Z0-9_-]*\n(.*?)```", body, re.S)
    if match:
        return match.group(1).strip()
    return body.strip()


def _parse_bullets(block: str) -> List[str]:
    items: List[str] = []
    for line in block.splitlines():
        match = re.match(r"^\s*[-*]\s+(.*\S)\s*$", line)
        if match:
            items.append(match.group(1).strip())
    return items


def _parse_key_values(block: str) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^\s*([A-Za-z][\w /-]*?)\s*:\s*(.*\S)\s*$", line)
        if match:
            pairs[match.group(1).strip()] = match.group(2).strip()
    return pairs


def _parse_weights(block: str) -> Dict[str, float]:
    weights: Dict[str, float] = {}

    for item in _parse_bullets(block):
        match = re.match(r"^([\w /-]+?)\s*:\s*([0-9]*\.?[0-9]+)\s*$", item)
        if match:
            weights[match.group(1).strip()] = float(match.group(2))

    if not weights:
        for key, value in _parse_key_values(block).items():
            try:
                weights[key] = float(value)
            except ValueError:
                continue

    return weights


@dataclass
class DecisionGuidance:
    """Parsed representation of a `decision.md` artifact."""

    path: Optional[str] = None
    schema_version: str = SCHEMA_VERSION
    artifact_type: str = ARTIFACT_TYPE
    scope: Dict[str, str] = field(default_factory=dict)
    primary_objective: str = ""
    secondary_objectives: List[str] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    hard_constraints: List[str] = field(default_factory=list)
    trade_off_rules: List[str] = field(default_factory=list)
    decision_principles: List[str] = field(default_factory=list)
    evaluation_criteria: List[str] = field(default_factory=list)
    reflection_guidance: List[str] = field(default_factory=list)
    raw_text: str = ""

    # ------------------------------------------------------------------ load

    @classmethod
    def from_text(cls, text: str, path: Optional[str] = None) -> "DecisionGuidance":
        guidance = cls(path=path, raw_text=text)

        header = _parse_key_values(text.split("##", 1)[0])
        guidance.schema_version = header.get("Schema Version", SCHEMA_VERSION)
        guidance.artifact_type = header.get("Artifact Type", ARTIFACT_TYPE)

        for title, body in _split_sections(text).items():
            key = _SECTION_ALIASES.get(title.strip().lower())
            if key is None:
                continue

            block = _extract_block(body)

            if key == "weights":
                guidance.weights = _parse_weights(block)
            elif key == "scope":
                guidance.scope = _parse_key_values(block)
            elif key == "primary_objective":
                guidance.primary_objective = _parse_primary_objective(block)
            else:
                setattr(guidance, key, _parse_bullets(block))

        return guidance

    @classmethod
    def load(cls, path: str) -> "DecisionGuidance":
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        return cls.from_text(text, path=str(file_path))

    # -------------------------------------------------------------- mapping

    def to_criteria(self) -> List[Any]:
        """Map preference weights into decision criteria."""
        from core.decision_engine import DecisionCriteria

        return [
            DecisionCriteria(name=name, weight=weight, description="")
            for name, weight in self.weights.items()
        ]

    def to_policy(self, policy_id: str = "decision_guidance") -> Any:
        """Build a DecisionPolicy driven by this guidance."""
        from core.decision_engine import DecisionPolicy

        return DecisionPolicy(
            policy_id=policy_id,
            name="Decision Guidance Policy",
            description=self.primary_objective or "Policy derived from decision.md",
            criteria=self.to_criteria(),
            hard_constraints=list(self.hard_constraints),
            trade_off_rules={"rules": list(self.trade_off_rules)},
            is_active=True,
        )

    def to_prompt(self) -> str:
        """Render a compact guidance block for the LLM decision prompt."""
        lines: List[str] = []

        if self.primary_objective:
            lines.append(f"Primary Objective: {self.primary_objective}")

        if self.secondary_objectives:
            lines.append("Secondary Objectives:")
            lines.extend(f"- {item}" for item in self.secondary_objectives)

        if self.weights:
            lines.append("Scoring Weights:")
            lines.extend(f"- {name}: {weight}" for name, weight in self.weights.items())

        if self.hard_constraints:
            lines.append("Hard Constraints (a candidate violating any of these must be rejected):")
            lines.extend(f"- {item}" for item in self.hard_constraints)

        if self.trade_off_rules:
            lines.append("Trade-off Rules:")
            lines.extend(f"- {item}" for item in self.trade_off_rules)

        return "\n".join(lines)

    # ------------------------------------------------------------- validate

    def validate(self) -> List[str]:
        """Return human-readable warnings. An empty list means the artifact is usable."""
        warnings: List[str] = []

        if not self.primary_objective:
            warnings.append("缺少 Primary Objective：决策没有明确的优化目标。")

        if not self.weights:
            warnings.append("缺少 Preferences / Weights：将退回到默认评价标准。")
        else:
            total = sum(self.weights.values())
            if not 0.99 <= total <= 1.01:
                warnings.append(
                    f"权重总和为 {total:.2f}，建议归一化到 1.00。"
                )

        if not self.hard_constraints:
            warnings.append("未声明 Hard Constraints：没有任何候选方案会被直接淘汰。")

        return warnings

    def summary(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "schema_version": self.schema_version,
            "artifact_type": self.artifact_type,
            "scope": self.scope,
            "primary_objective": self.primary_objective,
            "secondary_objectives": self.secondary_objectives,
            "weights": self.weights,
            "hard_constraints": self.hard_constraints,
            "trade_off_rules": self.trade_off_rules,
            "decision_principles": self.decision_principles,
            "evaluation_criteria": self.evaluation_criteria,
            "reflection_guidance": self.reflection_guidance,
            "warnings": self.validate(),
        }


def _parse_primary_objective(block: str) -> str:
    """Support both `Primary Objective: <text>` and a labelled multi-line block."""
    pairs = _parse_key_values(block)
    for key, value in pairs.items():
        if key.strip().lower() == "primary objective" and value:
            return value

    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if lines and lines[0].lower().rstrip(":") == "primary objective":
        lines = lines[1:]
    return " ".join(lines).strip()


def guidance_candidates(workspace: Optional[str] = None) -> List[Path]:
    root = Path(workspace) if workspace else Path.cwd()
    return [
        root / DEFAULT_GUIDANCE_DIR / DEFAULT_GUIDANCE_FILENAME,
        root / DEFAULT_GUIDANCE_FILENAME,
    ]


def load_decision_guidance(workspace: Optional[str] = None) -> Optional[DecisionGuidance]:
    """Load the first existing decision.md, or return None if there is none."""
    for candidate in guidance_candidates(workspace):
        if candidate.is_file():
            return DecisionGuidance.load(str(candidate))
    return None


def init_decision_guidance(
    target_dir: Optional[str] = None,
    force: bool = False,
) -> Path:
    """Write the starter decision.md template and return its path."""
    directory = Path(target_dir) if target_dir else Path.cwd() / DEFAULT_GUIDANCE_DIR
    directory.mkdir(parents=True, exist_ok=True)

    target = directory / DEFAULT_GUIDANCE_FILENAME
    if target.exists() and not force:
        raise FileExistsError(
            f"{target} 已存在，使用 force=True 或 --force 覆盖。"
        )

    target.write_text(DEFAULT_DECISION_GUIDANCE, encoding="utf-8")
    return target
