from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import json
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import BarColumn, Progress


class OutputFormat(Enum):
    TEXT = "text"
    JSON = "json"
    RICH = "rich"


@dataclass
class DecisionCardOption:
    option_id: str
    name: str
    description: str
    total_score: float
    risk_level: float
    reversibility: float
    confidence: float
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    action_sequence: List[Dict[str, Any]] = field(default_factory=list)
    constraints_satisfied: bool = True
    estimated_cost: float = 0.0
    estimated_benefit: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "option_id": self.option_id,
            "name": self.name,
            "description": self.description,
            "total_score": self.total_score,
            "risk_level": self.risk_level,
            "reversibility": self.reversibility,
            "confidence": self.confidence,
            "criteria_scores": self.criteria_scores,
            "action_sequence": self.action_sequence,
            "constraints_satisfied": self.constraints_satisfied,
            "estimated_cost": self.estimated_cost,
            "estimated_benefit": self.estimated_benefit,
            "metadata": self.metadata,
        }


@dataclass
class DecisionCard:
    decision_id: str
    goal: str
    status: str
    context: Dict[str, Any] = field(default_factory=dict)
    options: List[DecisionCardOption] = field(default_factory=list)
    selected_option: Optional[DecisionCardOption] = None
    reasoning: str = ""
    confidence: float = 0.0
    created_at: str = ""
    decided_at: Optional[str] = None
    criteria: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "goal": self.goal,
            "status": self.status,
            "context": self.context,
            "options": [opt.to_dict() for opt in self.options],
            "selected_option": self.selected_option.to_dict() if self.selected_option else None,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "decided_at": self.decided_at,
            "criteria": self.criteria,
            "constraints": self.constraints,
            "metadata": self.metadata,
        }

    def to_text(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f"DECISION CARD: {self.decision_id}")
        lines.append("=" * 60)
        lines.append(f"Goal: {self.goal}")
        lines.append(f"Status: {self.status}")
        lines.append(f"Created: {self.created_at}")
        if self.decided_at:
            lines.append(f"Decided: {self.decided_at}")
        lines.append("")
        lines.append("Options:")
        lines.append("-" * 60)
        for i, opt in enumerate(self.options, 1):
            lines.append(f"Option {i}: {opt.name}")
            lines.append(f"  ID: {opt.option_id}")
            lines.append(f"  Description: {opt.description}")
            lines.append(f"  Score: {opt.total_score:.2f}")
            lines.append(f"  Risk: {opt.risk_level:.2f}")
            lines.append(f"  Reversibility: {opt.reversibility:.2f}")
            lines.append(f"  Confidence: {opt.confidence:.2f}")
            if opt.criteria_scores:
                lines.append("  Criteria:")
                for name, score in opt.criteria_scores.items():
                    lines.append(f"    {name}: {score:.2f}")
            lines.append("")
        if self.selected_option:
            lines.append("=" * 60)
            lines.append(f"SELECTED: {self.selected_option.name}")
            lines.append(f"Confidence: {self.confidence:.2f}")
            lines.append(f"Reasoning: {self.reasoning}")
            lines.append("=" * 60)
        return "\n".join(lines)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class DecisionCardRenderer:
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def render(self, card: DecisionCard, format: OutputFormat = OutputFormat.RICH) -> str:
        if format == OutputFormat.TEXT:
            return card.to_text()
        elif format == OutputFormat.JSON:
            return card.to_json()
        elif format == OutputFormat.RICH:
            self._render_rich(card)
            return ""

    def _render_rich(self, card: DecisionCard):
        header = Panel(
            f"[bold]Goal:[/bold] {card.goal}\n"
            f"[bold]Status:[/bold] {card.status}\n"
            f"[bold]Confidence:[/bold] {card.confidence:.2%}",
            title=f"Decision Card - {card.decision_id}",
            style="blue",
            width=80,
        )
        self.console.print(header)

        if card.options:
            options_table = Table(title="Options Comparison")
            options_table.add_column("Option", style="cyan", width=20)
            options_table.add_column("Score", style="green", width=10)
            options_table.add_column("Risk", style="yellow", width=10)
            options_table.add_column("Reversibility", style="blue", width=15)
            options_table.add_column("Confidence", style="magenta", width=12)

            for opt in card.options:
                is_selected = opt.option_id == card.selected_option.option_id if card.selected_option else False
                if is_selected:
                    options_table.add_row(
                        f"[bold]{opt.name}[/bold]",
                        f"[bold]{opt.total_score:.2f}[/bold]",
                        f"[bold]{opt.risk_level:.2f}[/bold]",
                        f"[bold]{opt.reversibility:.2f}[/bold]",
                        f"[bold]{opt.confidence:.2%}[/bold]",
                    )
                else:
                    options_table.add_row(
                        opt.name,
                        f"{opt.total_score:.2f}",
                        f"{opt.risk_level:.2f}",
                        f"{opt.reversibility:.2f}",
                        f"{opt.confidence:.2%}",
                    )

            self.console.print(options_table)

            for opt in card.options:
                is_selected = opt.option_id == card.selected_option.option_id if card.selected_option else False
                if is_selected:
                    panel_color = "green"
                    title_prefix = "★ "
                else:
                    panel_color = "dim"
                    title_prefix = ""

                criteria_str = "\n".join(
                    f"  [bold]{name}:[/bold] {score:.2f}"
                    for name, score in opt.criteria_scores.items()
                )

                panel_content = (
                    f"[bold]Description:[/bold] {opt.description}\n\n"
                    f"[bold]Criteria Scores:[/bold]\n{criteria_str}\n\n"
                    f"[bold]Risk Level:[/bold] {opt.risk_level:.2f}\n"
                    f"[bold]Reversibility:[/bold] {opt.reversibility:.2f}"
                )

                panel = Panel(
                    panel_content,
                    title=f"{title_prefix}{opt.name}",
                    style=panel_color,
                    width=80,
                )
                self.console.print(panel)

        if card.selected_option:
            reasoning_panel = Panel(
                f"[bold]Selected Option:[/bold] {card.selected_option.name}\n\n"
                f"[bold]Reasoning:[/bold]\n{card.reasoning}",
                title="Decision Result",
                style="green",
                width=80,
            )
            self.console.print(reasoning_panel)

    def render_from_decision(self, decision) -> DecisionCard:
        options = []
        for opt in decision.options:
            options.append(DecisionCardOption(
                option_id=opt.option_id,
                name=opt.name,
                description=opt.description,
                total_score=opt.total_score,
                risk_level=opt.risk_level,
                reversibility=opt.reversibility,
                confidence=opt.confidence,
                criteria_scores=opt.criteria_scores,
                action_sequence=opt.action_sequence,
                constraints_satisfied=opt.constraints_satisfied,
                estimated_cost=opt.estimated_cost,
                estimated_benefit=opt.estimated_benefit,
                metadata=opt.metadata,
            ))

        selected_option = None
        if decision.selected_option:
            selected_option = DecisionCardOption(
                option_id=decision.selected_option.option_id,
                name=decision.selected_option.name,
                description=decision.selected_option.description,
                total_score=decision.selected_option.total_score,
                risk_level=decision.selected_option.risk_level,
                reversibility=decision.selected_option.reversibility,
                confidence=decision.selected_option.confidence,
                criteria_scores=decision.selected_option.criteria_scores,
                action_sequence=decision.selected_option.action_sequence,
                constraints_satisfied=decision.selected_option.constraints_satisfied,
                estimated_cost=decision.selected_option.estimated_cost,
                estimated_benefit=decision.selected_option.estimated_benefit,
                metadata=decision.selected_option.metadata,
            )

        criteria = []
        for c in decision.criteria:
            criteria.append({
                "name": c.name,
                "weight": c.weight,
                "description": c.description,
            })

        return DecisionCard(
            decision_id=decision.decision_id,
            goal=decision.context.get("goal", decision.context.get("task", "Unknown")),
            status=decision.status.value,
            context=decision.context,
            options=options,
            selected_option=selected_option,
            reasoning=decision.reasoning,
            confidence=decision.confidence,
            created_at=decision.created_at.isoformat() if decision.created_at else "",
            decided_at=decision.decided_at.isoformat() if decision.decided_at else None,
            criteria=criteria,
            constraints=decision.constraints,
            metadata=decision.metadata,
        )


class DecisionComparator:
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def compare(self, cards: List[DecisionCard], format: OutputFormat = OutputFormat.RICH) -> str:
        if format == OutputFormat.TEXT:
            return self._compare_text(cards)
        elif format == OutputFormat.JSON:
            return self._compare_json(cards)
        elif format == OutputFormat.RICH:
            self._compare_rich(cards)
            return ""

    def _compare_text(self, cards: List[DecisionCard]) -> str:
        lines = []
        lines.append("=" * 80)
        lines.append(f"DECISION COMPARISON - {len(cards)} Decisions")
        lines.append("=" * 80)

        for i, card in enumerate(cards, 1):
            lines.append("")
            lines.append(f"--- Decision {i}: {card.decision_id} ---")
            lines.append(f"Goal: {card.goal}")
            lines.append(f"Status: {card.status}")
            lines.append(f"Confidence: {card.confidence:.2%}")
            selected = card.selected_option.name if card.selected_option else "None"
            lines.append(f"Selected: {selected}")
            if card.options:
                avg_score = sum(opt.total_score for opt in card.options) / len(card.options)
                lines.append(f"Avg Option Score: {avg_score:.2f}")
            lines.append(f"Options Count: {len(card.options)}")

        lines.append("")
        lines.append("=" * 80)
        return "\n".join(lines)

    def _compare_json(self, cards: List[DecisionCard]) -> str:
        comparison = {
            "comparison_id": f"compare_{datetime.now().timestamp()}",
            "compared_at": datetime.now().isoformat(),
            "total_decisions": len(cards),
            "decisions": [card.to_dict() for card in cards],
            "summary": self._generate_summary(cards),
        }
        return json.dumps(comparison, indent=2, ensure_ascii=False)

    def _compare_rich(self, cards: List[DecisionCard]):
        header = Panel(
            f"[bold]Total Decisions:[/bold] {len(cards)}\n"
            f"[bold]Compared At:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="Decision Comparison",
            style="purple",
            width=100,
        )
        self.console.print(header)

        summary = self._generate_summary(cards)
        summary_table = Table(title="Comparison Summary")
        summary_table.add_column("Metric", style="cyan", width=30)
        summary_table.add_column("Value", style="green", width=70)

        for key, value in summary.items():
            if isinstance(value, float):
                summary_table.add_row(key, f"{value:.2f}")
            else:
                summary_table.add_row(key, str(value))
        self.console.print(summary_table)

        comparison_table = Table(title="Decision Details")
        comparison_table.add_column("Decision ID", style="cyan", width=35)
        comparison_table.add_column("Goal", style="blue", width=30)
        comparison_table.add_column("Selected", style="green", width=20)
        comparison_table.add_column("Confidence", style="magenta", width=15)
        comparison_table.add_column("Options", style="yellow", width=10)

        for card in cards:
            selected = card.selected_option.name[:18] if card.selected_option else "None"
            comparison_table.add_row(
                card.decision_id,
                card.goal[:28],
                selected,
                f"{card.confidence:.2%}",
                str(len(card.options)),
            )
        self.console.print(comparison_table)

        for card in cards:
            if card.selected_option:
                self.console.print("")
                self.console.print(f"[bold underline]{card.decision_id}[/bold underline]")
                self.console.print(f"[bold]Goal:[/bold] {card.goal}")
                self.console.print(f"[bold]Selected Option:[/bold] {card.selected_option.name}")
                self.console.print(f"[bold]Score:[/bold] {card.selected_option.total_score:.2f}")
                self.console.print(f"[bold]Risk:[/bold] {card.selected_option.risk_level:.2f}")
                self.console.print(f"[bold]Reversibility:[/bold] {card.selected_option.reversibility:.2f}")

    def _generate_summary(self, cards: List[DecisionCard]) -> Dict[str, Any]:
        if not cards:
            return {}

        total_options = sum(len(card.options) for card in cards)
        avg_options = total_options / len(cards)

        total_confidence = sum(card.confidence for card in cards)
        avg_confidence = total_confidence / len(cards)

        selected_count = sum(1 for card in cards if card.selected_option)
        avg_score = 0.0
        if selected_count > 0:
            selected_scores = [card.selected_option.total_score for card in cards if card.selected_option]
            avg_score = sum(selected_scores) / selected_count

        completed_count = sum(1 for card in cards if card.status == "decided")

        return {
            "total_decisions": len(cards),
            "total_options": total_options,
            "average_options_per_decision": avg_options,
            "average_confidence": avg_confidence,
            "decisions_with_selection": selected_count,
            "average_selected_score": avg_score,
            "completed_decisions": completed_count,
            "pending_decisions": len(cards) - completed_count,
        }