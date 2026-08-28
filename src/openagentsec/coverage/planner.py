"""Minimal CoveragePlanner for governance lifecycle initialization and gap analysis (PRD v4.0.2 §4)."""

from __future__ import annotations

from typing import List, Optional

from .enums import CoverageStatus
from .record import CoverageRecord, compute_coverage_id


class CoveragePlanner:
    """Minimal governance planner for coverage unit initialization and lifecycle progression planning."""

    @classmethod
    def initialize_coverage(
        cls,
        risk_refs: List[str],
        policy_refs: Optional[List[str]] = None,
        objective_id: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> CoverageRecord:
        """Initialize a new deterministic CoverageRecord for an evaluation target unit."""
        if not risk_refs:
            raise ValueError("risk_refs must contain at least one risk reference")

        coverage_id = compute_coverage_id(
            risk_refs=risk_refs,
            objective_id=objective_id,
            target_id=target_id,
        )

        return CoverageRecord(
            coverage_id=coverage_id,
            risk_refs=sorted(list(set(risk_refs))),
            policy_refs=sorted(list(set(policy_refs or []))),
            objective_id=objective_id,
            target_id=target_id,
            status=CoverageStatus.MAPPED_ONLY,
        )

    @classmethod
    def get_next_missing_artifact(cls, record: CoverageRecord) -> str:
        """Analyze lifecycle gap and identify the next artifact required to advance coverage."""
        if record.status == CoverageStatus.MAPPED_ONLY:
            return "evaluation_objective"
        elif record.status == CoverageStatus.OBJECTIVE_DEFINED:
            return "scenario_plan"
        elif record.status == CoverageStatus.SCENARIO_AVAILABLE:
            return "execution_readiness"
        elif record.status == CoverageStatus.EXECUTABLE:
            return "trajectory_and_oracle_adjudication"
        elif record.status == CoverageStatus.EVALUATED:
            return "reproduction_result"
        elif record.status == CoverageStatus.REPRODUCED:
            return "retest_verification"
        elif record.status == CoverageStatus.RETEST_VERIFIED:
            return "none_fully_verified"
        elif record.status in (CoverageStatus.DESIGN_GATE, CoverageStatus.OUT_OF_SCOPE):
            return "governance_resolution_required"
        return "unknown_lifecycle_state"
