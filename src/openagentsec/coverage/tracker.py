"""CoverageTracker domain service for artifact-driven lifecycle advancement (PRD v4.0.2 §4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..models.evaluation_objective import EvaluationObjective
from ..oracle.result import OracleResult
from ..planner.scenario import ScenarioPlan
from ..reproduction.enums import ReproductionStatus
from ..reproduction.result import ReproductionResult
from ..trajectory.models import Trajectory
from .enums import (
    GOVERNANCE_BRANCH_STATUSES,
    MAINLINE_COVERAGE_RANKS,
    MAINLINE_COVERAGE_STATUSES,
    CoverageStatus,
)
from .record import CoverageRecord, CoverageTransition


@dataclass(frozen=True)
class ExecutionReadiness:
    """Execution readiness facts required to advance to CoverageStatus.EXECUTABLE."""

    target_id: str
    adapter_available: bool = True
    safe_preflight_passed: bool = True
    preflight_result: Optional[Any] = None
    permitted_stimulus_available: bool = True
    observation_channels_available: bool = True
    reason_codes: List[str] = field(default_factory=list)

    @property
    def is_preflight_ready(self) -> bool:
        if self.preflight_result is not None:
            return bool(getattr(self.preflight_result, "ready", False))
        return self.safe_preflight_passed


class CoverageTracker:
    """Artifact-driven monotonic Coverage lifecycle state machine."""

    @classmethod
    def _can_advance_mainline(
        cls, current_status: CoverageStatus, target_status: CoverageStatus
    ) -> bool:
        """Determine if target_status is a valid forward progression in mainline."""
        if current_status in GOVERNANCE_BRANCH_STATUSES:
            # Branch status can re-enter mainline if unblocked
            return True
        if target_status not in MAINLINE_COVERAGE_STATUSES:
            return False
        current_rank = MAINLINE_COVERAGE_RANKS.get(current_status, 0)
        target_rank = MAINLINE_COVERAGE_RANKS.get(target_status, 0)
        return target_rank > current_rank

    @classmethod
    def _record_transition(
        cls,
        record: CoverageRecord,
        to_status: CoverageStatus,
        trigger: str,
        artifact_refs: Dict[str, str],
        reason_codes: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Apply status change and append transition audit log."""
        if record.status == to_status:
            # Idempotency check: if last transition has same reason_codes, avoid duplicating
            if (
                record.transition_history
                and record.transition_history[-1].to_status == to_status
                and record.transition_history[-1].reason_codes == reason_codes
            ):
                return

        transition = CoverageTransition(
            from_status=record.status,
            to_status=to_status,
            trigger=trigger,
            artifact_refs=artifact_refs,
            reason_codes=reason_codes,
            metadata=metadata or {},
        )
        record.status = to_status
        record.transition_history.append(transition)
        record.updated_at = datetime.now(timezone.utc).isoformat()

    @classmethod
    def advance_objective(
        cls, record: CoverageRecord, objective: EvaluationObjective
    ) -> CoverageRecord:
        """Advance coverage unit upon receipt of formal EvaluationObjective."""
        if not objective.objective_id:
            raise ValueError("EvaluationObjective must have a non-empty objective_id")

        record.objective_id = objective.objective_id
        record.policy_refs = sorted(list(set(record.policy_refs) | set(objective.policy_refs)))

        if cls._can_advance_mainline(record.status, CoverageStatus.OBJECTIVE_DEFINED):
            cls._record_transition(
                record,
                to_status=CoverageStatus.OBJECTIVE_DEFINED,
                trigger="evaluation_objective_defined",
                artifact_refs={"objective_id": objective.objective_id},
                reason_codes=["formal_objective_available"],
            )
        return record

    @classmethod
    def advance_scenario(
        cls, record: CoverageRecord, scenario: ScenarioPlan
    ) -> CoverageRecord:
        """Advance coverage unit upon receipt of formal ScenarioPlan."""
        if not scenario.scenario_id or not scenario.deterministic_plan_hash:
            raise ValueError("ScenarioPlan must have a non-empty scenario_id and deterministic_plan_hash")

        # Coherence verification
        if record.objective_id and scenario.objective_id != record.objective_id:
            record.limitations.append("scenario_objective_mismatch_detected")
            return record

        if record.target_id and scenario.target_id and scenario.target_id != record.target_id:
            record.limitations.append("scenario_target_mismatch_detected")
            return record

        record.scenario_ref = scenario.scenario_id
        if scenario.target_id and not record.target_id:
            record.target_id = scenario.target_id

        if cls._can_advance_mainline(record.status, CoverageStatus.SCENARIO_AVAILABLE):
            cls._record_transition(
                record,
                to_status=CoverageStatus.SCENARIO_AVAILABLE,
                trigger="scenario_plan_available",
                artifact_refs={"scenario_ref": scenario.scenario_id},
                reason_codes=["formal_scenario_plan_generated"],
            )
        return record

    @classmethod
    def advance_executable(
        cls, record: CoverageRecord, readiness: ExecutionReadiness
    ) -> CoverageRecord:
        """Advance coverage unit upon verification of execution readiness facts."""
        if not (
            readiness.adapter_available
            and readiness.is_preflight_ready
            and readiness.permitted_stimulus_available
            and readiness.observation_channels_available
        ):
            record.limitations.extend(readiness.reason_codes or ["execution_readiness_unsatisfied"])
            return record

        if record.target_id and readiness.target_id != record.target_id:
            record.limitations.append("readiness_target_mismatch_detected")
            return record

        if not record.target_id:
            record.target_id = readiness.target_id

        if cls._can_advance_mainline(record.status, CoverageStatus.EXECUTABLE):
            cls._record_transition(
                record,
                to_status=CoverageStatus.EXECUTABLE,
                trigger="execution_readiness_verified",
                artifact_refs={"target_id": readiness.target_id},
                reason_codes=["preflight_passed", "adapter_available", "observability_ready"],
            )
        return record

    @classmethod
    def advance_evaluated(
        cls,
        record: CoverageRecord,
        trajectory: Trajectory,
        oracle_result: OracleResult,
    ) -> CoverageRecord:
        """Advance coverage unit upon formal execution trajectory and independent Oracle adjudication."""
        if not trajectory.trajectory_id:
            raise ValueError("Trajectory must have a valid trajectory_id")

        # Coherence verification
        if record.objective_id and (
            trajectory.objective_id != record.objective_id
            or oracle_result.objective_id != record.objective_id
        ):
            record.limitations.append("evaluated_objective_mismatch_detected")
            return record

        if record.target_id and (
            trajectory.target_id != record.target_id
            or oracle_result.target_id != record.target_id
        ):
            record.limitations.append("evaluated_target_mismatch_detected")
            return record

        record.trajectory_ref = trajectory.trajectory_id
        record.metadata["oracle_implementation_id"] = oracle_result.oracle_id
        record.metadata["oracle_decision_summary"] = (
            oracle_result.decision.value
            if hasattr(oracle_result.decision, "value")
            else str(oracle_result.decision)
        )

        if cls._can_advance_mainline(record.status, CoverageStatus.EVALUATED):
            cls._record_transition(
                record,
                to_status=CoverageStatus.EVALUATED,
                trigger="execution_and_oracle_adjudication_completed",
                artifact_refs={"trajectory_ref": trajectory.trajectory_id},
                reason_codes=["trajectory_recorded", "oracle_adjudicated"],
                metadata={
                    "oracle_id": oracle_result.oracle_id,
                    "oracle_decision": record.metadata["oracle_decision_summary"],
                },
            )
        return record

    @classmethod
    def advance_reproduced(
        cls, record: CoverageRecord, reproduction_result: ReproductionResult
    ) -> CoverageRecord:
        """Advance coverage unit upon formal Reproduction verification."""
        if not reproduction_result.reproduction_id:
            raise ValueError("ReproductionResult must have a valid reproduction_id")

        # Coherence verification
        if record.objective_id and reproduction_result.objective_id != record.objective_id:
            record.limitations.append("reproduction_objective_mismatch_detected")
            return record

        if record.target_id and reproduction_result.target_id != record.target_id:
            record.limitations.append("reproduction_target_mismatch_detected")
            return record

        if record.policy_refs and reproduction_result.policy_id not in record.policy_refs:
            record.limitations.append("reproduction_policy_mismatch_detected")
            return record

        status = getattr(reproduction_result, "reproduction_status", None) or getattr(reproduction_result, "status", None)
        if status != ReproductionStatus.REPRODUCED:
            record.limitations.append(
                f"reproduction_not_confirmed_{status.value if hasattr(status, 'value') else status}"
            )
            return record

        record.reproduction_ref = reproduction_result.reproduction_id

        if cls._can_advance_mainline(record.status, CoverageStatus.REPRODUCED):
            cls._record_transition(
                record,
                to_status=CoverageStatus.REPRODUCED,
                trigger="reproduction_verification_confirmed",
                artifact_refs={"reproduction_ref": reproduction_result.reproduction_id},
                reason_codes=["reproduction_rate_verified"],
                metadata={"reproduction_runs": reproduction_result.completed_runs},
            )
        return record

    @classmethod
    def advance_retest_verified(
        cls, record: CoverageRecord, retest_artifact: Any = None
    ) -> CoverageRecord:
        """Guard against unsupported retest transitions in Phase 5C (Fail-Closed)."""
        raise NotImplementedError(
            "Retest verification is not implemented in Phase 5C; retest engine is deferred to Phase 5E"
        )

    @classmethod
    def set_design_gate(
        cls,
        record: CoverageRecord,
        reason_codes: List[str],
        trigger: str = "governance_design_blocked",
    ) -> CoverageRecord:
        """Transition coverage unit to DESIGN_GATE governance branch."""
        if not reason_codes:
            raise ValueError("design_gate transition requires at least one reason code")

        cls._record_transition(
            record,
            to_status=CoverageStatus.DESIGN_GATE,
            trigger=trigger,
            artifact_refs={},
            reason_codes=reason_codes,
        )
        return record

    @classmethod
    def set_out_of_scope(
        cls,
        record: CoverageRecord,
        reason_codes: List[str],
        trigger: str = "governance_scope_decision",
    ) -> CoverageRecord:
        """Transition coverage unit to OUT_OF_SCOPE governance branch."""
        if not reason_codes:
            raise ValueError("out_of_scope transition requires at least one reason code")

        cls._record_transition(
            record,
            to_status=CoverageStatus.OUT_OF_SCOPE,
            trigger=trigger,
            artifact_refs={},
            reason_codes=reason_codes,
        )
        return record
