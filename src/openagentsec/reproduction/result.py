"""Reproduction models for OpenAgentSec repeated evaluations (PRD v4.0.2 Phase 4A)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..oracle.enums import OracleDecision
from .enums import ReproductionStatus


@dataclass
class ReproductionRun:
    """Record of a single independent evaluation run within a reproduction suite."""
    run_id: str
    run_index: int
    baseline_hash: str
    oracle_decision: OracleDecision
    violated_invariants: List[str] = field(default_factory=list)
    deviation_present: bool = False
    deviation_severity: Optional[str] = None
    reason_codes: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    reset_verified_before: bool = True
    reset_verified_after: bool = True
    valid: bool = True
    session_id: Optional[str] = None
    evidence_hashes: Dict[str, str] = field(default_factory=dict)
    execution_receipt_ids: List[str] = field(default_factory=list)
    normalized_findings: List[Dict[str, Any]] = field(default_factory=list)
    evidence_instance_digest: Optional[str] = None
    evidence_outcome_digest: Optional[str] = None

    @property
    def has_integrity_claim(self) -> bool:
        """Whether this run opts into the Phase 22.0C integrity contract."""
        return any(
            (
                self.session_id,
                self.evidence_hashes,
                self.execution_receipt_ids,
                self.normalized_findings,
                self.evidence_instance_digest,
                self.evidence_outcome_digest,
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_index": self.run_index,
            "baseline_hash": self.baseline_hash,
            "oracle_decision": self.oracle_decision.value if isinstance(self.oracle_decision, OracleDecision) else str(self.oracle_decision),
            "violated_invariants": list(self.violated_invariants),
            "deviation_present": self.deviation_present,
            "deviation_severity": self.deviation_severity,
            "reason_codes": list(self.reason_codes),
            "evidence_refs": list(self.evidence_refs),
            "reset_verified_before": self.reset_verified_before,
            "reset_verified_after": self.reset_verified_after,
            "valid": self.valid,
            "session_id": self.session_id,
            "evidence_hashes": dict(self.evidence_hashes),
            "execution_receipt_ids": list(self.execution_receipt_ids),
            "normalized_findings": list(self.normalized_findings),
            "evidence_instance_digest": self.evidence_instance_digest,
            "evidence_outcome_digest": self.evidence_outcome_digest,
        }


@dataclass
class ReproductionResult:
    """Aggregated result of repeated independent evaluation runs against a fixed baseline."""
    reproduction_id: str
    baseline_hash: str
    objective_id: str
    policy_id: str
    target_id: str
    requested_runs: int
    completed_runs: int
    runs: List[ReproductionRun] = field(default_factory=list)
    decision_counts: Dict[str, int] = field(default_factory=dict)
    reproduction_status: ReproductionStatus = ReproductionStatus.INCONCLUSIVE
    reproduced_outcome: Optional[OracleDecision] = None
    variance_detected: bool = False
    is_reproduced_deviation: bool = False
    limitations: List[str] = field(default_factory=list)
    reason_codes: List[str] = field(default_factory=list)
    integrity_verified: bool = False
    evidence_outcome_digest: Optional[str] = None

    @property
    def is_reproduced(self) -> bool:
        return self.reproduction_status == ReproductionStatus.REPRODUCED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reproduction_id": self.reproduction_id,
            "baseline_hash": self.baseline_hash,
            "objective_id": self.objective_id,
            "policy_id": self.policy_id,
            "target_id": self.target_id,
            "requested_runs": self.requested_runs,
            "completed_runs": self.completed_runs,
            "runs": [r.to_dict() for r in self.runs],
            "decision_counts": dict(self.decision_counts),
            "reproduction_status": self.reproduction_status.value if isinstance(self.reproduction_status, ReproductionStatus) else str(self.reproduction_status),
            "reproduced_outcome": self.reproduced_outcome.value if isinstance(self.reproduced_outcome, OracleDecision) else (str(self.reproduced_outcome) if self.reproduced_outcome else None),
            "variance_detected": self.variance_detected,
            "is_reproduced_deviation": self.is_reproduced_deviation,
            "limitations": list(self.limitations),
            "reason_codes": list(self.reason_codes),
            "integrity_verified": self.integrity_verified,
            "evidence_outcome_digest": self.evidence_outcome_digest,
        }
