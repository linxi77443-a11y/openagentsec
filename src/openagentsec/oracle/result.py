"""Oracle Result and Policy Deviation models for OpenAgentSec Governance Plane."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models.enums import Severity
from .enums import OracleDecision


@dataclass
class PolicyDeviation:
    """Formal security policy deviation record generated ONLY upon CONFIRMED_DEVIATION.

    PRD v4.0.2 Phase 3A:
    - severity is strictly inherited from the violated SecurityPolicy invariant.
    - severity MUST NOT be dynamically scored or guessed by models.
    """
    policy_id: str
    invariant_id: str
    objective_id: str
    target_id: str
    severity: Severity
    evidence_refs: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    rationale: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "invariant_id": self.invariant_id,
            "objective_id": self.objective_id,
            "target_id": self.target_id,
            "severity": self.severity.value if isinstance(self.severity, Severity) else str(self.severity),
            "evidence_refs": list(self.evidence_refs),
            "details": dict(self.details),
            "rationale": self.rationale,
        }


@dataclass
class OracleResult:
    """Structured deterministic oracle judgment result.

    PRD v4.0.2 Phase 3A:
    - Independent judgment based purely on SecurityPolicy, EvaluationObjective, and observations.
    - NEVER clones or relies on target model self-reporting.
    """
    oracle_id: str
    objective_id: str
    policy_id: str
    target_id: str
    decision: OracleDecision
    violated_invariants: List[str] = field(default_factory=list)
    deviation: Optional[PolicyDeviation] = None
    evidence_refs: List[str] = field(default_factory=list)
    observation_basis: Dict[str, Any] = field(default_factory=dict)
    reason_codes: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    @property
    def is_confirmed_deviation(self) -> bool:
        return self.decision == OracleDecision.CONFIRMED_DEVIATION

    @property
    def is_inconclusive(self) -> bool:
        return self.decision == OracleDecision.INCONCLUSIVE

    @property
    def is_no_deviation(self) -> bool:
        return self.decision == OracleDecision.NO_CONFIRMED_DEVIATION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "oracle_id": self.oracle_id,
            "objective_id": self.objective_id,
            "policy_id": self.policy_id,
            "target_id": self.target_id,
            "decision": self.decision.value if isinstance(self.decision, OracleDecision) else str(self.decision),
            "violated_invariants": list(self.violated_invariants),
            "deviation": self.deviation.to_dict() if self.deviation else None,
            "evidence_refs": list(self.evidence_refs),
            "observation_basis": dict(self.observation_basis),
            "reason_codes": list(self.reason_codes),
            "limitations": list(self.limitations),
        }
