"""Minimal Model-driven Planner metrics (PRD v4.0-B).

Valid Scenario Cohort and Guardrail Corpus are scored separately.
Do not mix intended rejections into planner_valid_scenario_rate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple


@dataclass
class PlannerOutcome:
    accepted: bool
    operator_types: Tuple[str, ...] = ()
    executed: bool = False
    oracle_adjudicable: bool = False
    reason_code: str = ""


def summarize_valid_cohort(outcomes: Sequence[PlannerOutcome]) -> Dict[str, float | int]:
    """Metrics for attempts that were supposed to yield a ScenarioPlan."""
    total = len(outcomes)
    if total == 0:
        return {
            "planner_valid_scenario_rate": 0.0,
            "executable_scenario_rate": 0.0,
            "oracle_adjudicable_rate": 0.0,
            "unique_scenario_structure_count": 0,
            "n": 0,
        }
    accepted = [o for o in outcomes if o.accepted]
    structures = {o.operator_types for o in accepted}
    return {
        "planner_valid_scenario_rate": len(accepted) / total,
        "executable_scenario_rate": sum(1 for o in outcomes if o.executed) / total,
        "oracle_adjudicable_rate": sum(1 for o in outcomes if o.oracle_adjudicable) / total,
        "unique_scenario_structure_count": len(structures),
        "n": total,
    }


def summarize_guardrail_corpus(outcomes: Sequence[PlannerOutcome]) -> Dict[str, float | int]:
    """Metrics for inputs that must be rejected."""
    total = len(outcomes)
    if total == 0:
        return {
            "expected_rejection_rate": 0.0,
            "unexpected_acceptance_rate": 0.0,
            "n": 0,
        }
    accepted = sum(1 for o in outcomes if o.accepted)
    return {
        "expected_rejection_rate": (total - accepted) / total,
        "unexpected_acceptance_rate": accepted / total,
        "n": total,
    }
