"""CoverageRecord and CoverageTransition domain models (PRD v4.0.2 §4.2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional

from .enums import (
    MAINLINE_COVERAGE_RANKS,
    MAINLINE_COVERAGE_STATUSES,
    CoverageStatus,
)


def compute_coverage_id(
    risk_refs: List[str],
    objective_id: Optional[str] = None,
    target_id: Optional[str] = None,
) -> str:
    """Compute deterministic coverage identity based on core evaluation target facts."""
    payload = {
        "objective_id": objective_id,
        "risk_refs": sorted(list(set(risk_refs))),
        "target_id": target_id,
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()[:12]
    return f"COV-{digest}"


@dataclass(frozen=True)
class CoverageTransition:
    """Audit record of a Coverage lifecycle status transition."""

    from_status: CoverageStatus
    to_status: CoverageStatus
    trigger: str
    artifact_refs: Dict[str, str] = field(default_factory=dict)
    reason_codes: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_status": (
                self.from_status.value
                if isinstance(self.from_status, CoverageStatus)
                else str(self.from_status)
            ),
            "to_status": (
                self.to_status.value
                if isinstance(self.to_status, CoverageStatus)
                else str(self.to_status)
            ),
            "trigger": self.trigger,
            "artifact_refs": dict(self.artifact_refs),
            "reason_codes": list(self.reason_codes),
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }


@dataclass
class CoverageRecord:
    """Governance tracking record for evaluation lifecycle depth of an evaluation unit.
    
    PRD v4.0.2 §4:
    Answers 'TO WHAT DEPTH HAS THIS UNIT BEEN EVALUATED?'.
    Does NOT answer 'Is the target safe?' and contains no PASS/FAIL or severity scores.
    """

    coverage_id: str
    risk_refs: List[str]
    policy_refs: List[str] = field(default_factory=list)
    objective_id: Optional[str] = None
    target_id: Optional[str] = None
    status: CoverageStatus = CoverageStatus.MAPPED_ONLY
    scenario_ref: Optional[str] = None
    trajectory_ref: Optional[str] = None
    reproduction_ref: Optional[str] = None
    retest_ref: Optional[str] = None
    limitations: List[str] = field(default_factory=list)
    transition_history: List[CoverageTransition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.coverage_id or not isinstance(self.coverage_id, str):
            raise ValueError("coverage_id must be a non-empty string")
        if not isinstance(self.status, CoverageStatus):
            if isinstance(self.status, str):
                self.status = CoverageStatus(self.status)
            else:
                raise ValueError(f"status must be a CoverageStatus, got {type(self.status)}")

    @property
    def highest_mainline_status(self) -> CoverageStatus:
        """Derive the highest achieved mainline maturity status without conflating branch dispositions."""
        highest = CoverageStatus.MAPPED_ONLY
        highest_rank = MAINLINE_COVERAGE_RANKS[CoverageStatus.MAPPED_ONLY]

        if self.status in MAINLINE_COVERAGE_STATUSES:
            highest = self.status
            highest_rank = MAINLINE_COVERAGE_RANKS[self.status]

        for t in self.transition_history:
            for s in (t.from_status, t.to_status):
                if s in MAINLINE_COVERAGE_STATUSES:
                    rank = MAINLINE_COVERAGE_RANKS[s]
                    if rank > highest_rank:
                        highest = s
                        highest_rank = rank
        return highest

    def to_dict(self) -> Dict[str, Any]:
        return {
            "coverage_id": self.coverage_id,
            "risk_refs": list(self.risk_refs),
            "policy_refs": list(self.policy_refs),
            "objective_id": self.objective_id,
            "target_id": self.target_id,
            "status": self.status.value,
            "highest_mainline_status": self.highest_mainline_status.value,
            "scenario_ref": self.scenario_ref,
            "trajectory_ref": self.trajectory_ref,
            "reproduction_ref": self.reproduction_ref,
            "retest_ref": self.retest_ref,
            "limitations": list(self.limitations),
            "transition_history": [t.to_dict() for t in self.transition_history],
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
