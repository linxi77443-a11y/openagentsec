"""EvaluationObjective model for OpenAgentSec Evaluation Plane.

PRD v4.0.2 §6:
EvaluationObjective defines *why* and *what* to evaluate:
- The core evaluation question
- Expected target behavior
- Undesired behavior (deviations)
- Required observations and evidence
- Safe operational parameters (capped max_steps, capped max_runs, single planner_mode)

SEMANTIC BOUNDARY:
EvaluationObjective ≠ EvaluationScenario.
Objective defines questions, behavior expectations, observation requirements,
and safety constraints. It does NOT contain concrete attack payloads, scenario
steps, or execution planners.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .enums import MaturityLevel, PlannerMode

# Implementation safety caps (PRD v4.0.2 §6 / Phase 1B)
MAX_OBJECTIVE_STEPS: int = 100
MAX_OBJECTIVE_RUNS: int = 50


@dataclass
class EvaluationObjective:
    """Evaluation Plane objective defining evaluation scope and safety boundaries."""
    objective_id: str
    risk_refs: List[str]
    policy_refs: List[str]
    target_refs: List[str]
    evaluation_question: str
    target_behavior: str
    undesired_behavior: str
    required_observations: List[str]
    required_evidence: List[str]
    permitted_stimulus_types: List[str]
    planner_mode: PlannerMode
    maturity_required: MaturityLevel
    max_steps: int
    max_runs: int
    stop_conditions: List[str] = field(default_factory=list)
    safety_constraints: List[str] = field(default_factory=list)
    title: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "objective_id": self.objective_id,
            "risk_refs": list(self.risk_refs),
            "policy_refs": list(self.policy_refs),
            "target_refs": list(self.target_refs),
            "evaluation_question": self.evaluation_question,
            "target_behavior": self.target_behavior,
            "undesired_behavior": self.undesired_behavior,
            "required_observations": list(self.required_observations),
            "required_evidence": list(self.required_evidence),
            "permitted_stimulus_types": list(self.permitted_stimulus_types),
            "planner_mode": (
                self.planner_mode.value
                if isinstance(self.planner_mode, PlannerMode)
                else str(self.planner_mode)
            ),
            "maturity_required": (
                self.maturity_required.value
                if isinstance(self.maturity_required, MaturityLevel)
                else str(self.maturity_required)
            ),
            "max_steps": self.max_steps,
            "max_runs": self.max_runs,
            "stop_conditions": list(self.stop_conditions),
            "safety_constraints": list(self.safety_constraints),
        }
        if self.title is not None:
            data["title"] = self.title
        return data
