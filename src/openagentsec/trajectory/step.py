"""TrajectoryStep domain model for ordered execution activity (PRD v4.0.2 §12.1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TrajectoryStep:
    """Individual observable interaction or execution unit within a Trajectory.
    
    PRD v4.0.2 §12.1:
    Strictly records observable facts and reference links.
    Contains NO chain-of-thought or hidden reasoning fields.
    """

    run_id: str
    step_id: str
    stimulus_ref: Optional[str] = None
    model_response_ref: Optional[str] = None
    tool_trace_ref: Optional[str] = None
    runtime_decision_ref: Optional[str] = None
    state_before_ref: Optional[str] = None
    state_after_ref: Optional[str] = None
    state_diff_ref: Optional[str] = None
    oracle_signal_refs: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.run_id or not isinstance(self.run_id, str):
            raise ValueError("run_id must be a non-empty string")
        if not self.step_id or not isinstance(self.step_id, str):
            raise ValueError("step_id must be a non-empty string")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "step_id": self.step_id,
            "stimulus_ref": self.stimulus_ref,
            "model_response_ref": self.model_response_ref,
            "tool_trace_ref": self.tool_trace_ref,
            "runtime_decision_ref": self.runtime_decision_ref,
            "state_before_ref": self.state_before_ref,
            "state_after_ref": self.state_after_ref,
            "state_diff_ref": self.state_diff_ref,
            "oracle_signal_refs": list(self.oracle_signal_refs),
            "evidence_refs": list(self.evidence_refs),
            "metadata": dict(self.metadata),
        }
