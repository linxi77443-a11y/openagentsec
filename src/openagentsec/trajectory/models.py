"""Trajectory domain container for ordered evaluation execution steps (PRD v4.0.2 §12.1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from .step import TrajectoryStep


@dataclass(frozen=True)
class Trajectory:
    """Ordered record of observable execution activity for an evaluation run."""

    trajectory_id: str
    run_id: str
    objective_id: str
    target_id: str
    steps: List[TrajectoryStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.trajectory_id or not isinstance(self.trajectory_id, str):
            raise ValueError("trajectory_id must be a non-empty string")
        if not self.run_id or not isinstance(self.run_id, str):
            raise ValueError("run_id must be a non-empty string")
        if not self.objective_id or not isinstance(self.objective_id, str):
            raise ValueError("objective_id must be a non-empty string")
        if not self.target_id or not isinstance(self.target_id, str):
            raise ValueError("target_id must be a non-empty string")

        for idx, step in enumerate(self.steps):
            if not isinstance(step, TrajectoryStep):
                raise ValueError(f"Step at index {idx} must be a TrajectoryStep, got {type(step)}")
            if step.run_id != self.run_id:
                raise ValueError(
                    f"Step {step.step_id} has run_id '{step.run_id}' which does not match trajectory run_id '{self.run_id}'"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trajectory_id": self.trajectory_id,
            "run_id": self.run_id,
            "objective_id": self.objective_id,
            "target_id": self.target_id,
            "steps": [s.to_dict() for s in self.steps],
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }
