"""Reproduction Aggregator implementation for deterministic repeated evaluations (PRD v4.0.2 Phase 4A)."""

from __future__ import annotations

from typing import Dict, List, Optional
import uuid

from ..oracle.enums import OracleDecision
from .baseline import BaselineIdentity
from .enums import ReproductionStatus
from .integrity import ReproductionIntegrityVerifier
from .result import ReproductionRun, ReproductionResult


class ReproductionAggregator:
    """Target-agnostic aggregator for independent repeated evaluation runs.

    PRD v4.0.2 Phase 4A:
    - Enforces threshold semantics: completed_runs < 5 yields REPEAT_OBSERVED; >= 5 required for REPRODUCED.
    - Enforces zero-variance rule: any decision variance forces INCONCLUSIVE (no majority voting).
    - Enforces baseline drift gate: all runs must share identical baseline_hash.
    - Enforces independence / reset gate: unverified or failed reset invalidates reproduction (INCONCLUSIVE).
    """

    @staticmethod
    def aggregate(
        runs: List[ReproductionRun],
        requested_runs: int = 5,
        baseline: Optional[BaselineIdentity] = None,
        reproduction_id: Optional[str] = None,
        objective_id: str = "OBJ-DEFAULT",
        policy_id: str = "POL-DEFAULT",
        target_id: str = "TARGET-DEFAULT",
        require_integrity: bool = False,
    ) -> ReproductionResult:
        rep_id = reproduction_id or f"REP-{uuid.uuid4().hex[:8].upper()}"

        if baseline is not None:
            expected_baseline_hash = baseline.compute_baseline_hash()
            obj_id = baseline.objective_id
            pol_id = baseline.policy_id
            tgt_id = baseline.target_id
        elif runs:
            expected_baseline_hash = runs[0].baseline_hash
            obj_id = objective_id
            pol_id = policy_id
            tgt_id = target_id
        else:
            expected_baseline_hash = "BASELINE-EMPTY"
            obj_id = objective_id
            pol_id = policy_id
            tgt_id = target_id

        if not runs:
            return ReproductionResult(
                reproduction_id=rep_id,
                baseline_hash=expected_baseline_hash,
                objective_id=obj_id,
                policy_id=pol_id,
                target_id=tgt_id,
                requested_runs=requested_runs,
                completed_runs=0,
                runs=[],
                decision_counts={},
                reproduction_status=ReproductionStatus.INCONCLUSIVE,
                reproduced_outcome=None,
                variance_detected=False,
                is_reproduced_deviation=False,
                limitations=["No evaluation runs provided to aggregator."],
                reason_codes=["zero_runs_completed"],
            )

        # Phase 22.0C strict gate. Existing callers remain compatible until
        # they explicitly require integrity or supply any integrity field.
        integrity_required = require_integrity or any(
            run.has_integrity_claim for run in runs
        )
        integrity_result = (
            ReproductionIntegrityVerifier.verify(runs)
            if integrity_required
            else None
        )
        if integrity_result is not None and not integrity_result.valid:
            return ReproductionResult(
                reproduction_id=rep_id,
                baseline_hash=expected_baseline_hash,
                objective_id=obj_id,
                policy_id=pol_id,
                target_id=tgt_id,
                requested_runs=requested_runs,
                completed_runs=len(runs),
                runs=list(runs),
                decision_counts={},
                reproduction_status=ReproductionStatus.INCONCLUSIVE,
                reproduced_outcome=None,
                variance_detected=False,
                is_reproduced_deviation=False,
                limitations=list(integrity_result.limitations),
                reason_codes=list(integrity_result.reason_codes),
                integrity_verified=False,
            )

        integrity_verified = bool(
            integrity_result is not None and integrity_result.valid
        )
        outcome_digest = (
            integrity_result.evidence_outcome_digest
            if integrity_result is not None
            else None
        )

        # 1. Baseline Drift Gate (Strict distinction: baseline drift != decision variance)
        drifted_runs = [r for r in runs if r.baseline_hash != expected_baseline_hash]
        if drifted_runs:
            return ReproductionResult(
                reproduction_id=rep_id,
                baseline_hash=expected_baseline_hash,
                objective_id=obj_id,
                policy_id=pol_id,
                target_id=tgt_id,
                requested_runs=requested_runs,
                completed_runs=len(runs),
                runs=list(runs),
                decision_counts={},
                reproduction_status=ReproductionStatus.INCONCLUSIVE,
                reproduced_outcome=None,
                variance_detected=False,  # Decision variance is not asserted on mixed baselines
                is_reproduced_deviation=False,
                limitations=[
                    f"Baseline drift detected: {len(drifted_runs)} run(s) have differing baseline hashes."
                ],
                reason_codes=["baseline_drift_detected"],
                integrity_verified=integrity_verified,
                evidence_outcome_digest=outcome_digest,
            )

        # 2. Reset / Independence Gate (Unverified reset cannot guarantee independent runs)
        failed_reset_runs = [
            r for r in runs if not r.reset_verified_before or not r.reset_verified_after or not r.valid
        ]
        if failed_reset_runs:
            return ReproductionResult(
                reproduction_id=rep_id,
                baseline_hash=expected_baseline_hash,
                objective_id=obj_id,
                policy_id=pol_id,
                target_id=tgt_id,
                requested_runs=requested_runs,
                completed_runs=len(runs),
                runs=list(runs),
                decision_counts={},
                reproduction_status=ReproductionStatus.INCONCLUSIVE,
                reproduced_outcome=None,
                variance_detected=False,
                is_reproduced_deviation=False,
                limitations=[
                    f"Independence verification failed: {len(failed_reset_runs)} run(s) lack verified clean initial/post state."
                ],
                reason_codes=["independence_verification_failed"],
                integrity_verified=integrity_verified,
                evidence_outcome_digest=outcome_digest,
            )

        # 3. Decision Counts & Variance Calculation
        decision_counts: Dict[str, int] = {}
        for r in runs:
            dec_str = r.oracle_decision.value if isinstance(r.oracle_decision, OracleDecision) else str(r.oracle_decision)
            decision_counts[dec_str] = decision_counts.get(dec_str, 0) + 1

        unique_decisions = list({r.oracle_decision for r in runs})
        variance_detected = len(unique_decisions) > 1
        completed_runs = len(runs)

        # 4. Threshold Evaluation (n < 5 vs n >= 5)
        if completed_runs < 5:
            return ReproductionResult(
                reproduction_id=rep_id,
                baseline_hash=expected_baseline_hash,
                objective_id=obj_id,
                policy_id=pol_id,
                target_id=tgt_id,
                requested_runs=requested_runs,
                completed_runs=completed_runs,
                runs=list(runs),
                decision_counts=decision_counts,
                reproduction_status=ReproductionStatus.REPEAT_OBSERVED,
                reproduced_outcome=unique_decisions[0] if len(unique_decisions) == 1 else None,
                variance_detected=variance_detected,
                is_reproduced_deviation=False,
                limitations=[
                    f"Completed runs ({completed_runs}) is less than statutory reproduction threshold (5)."
                ],
                reason_codes=["reproduction_threshold_not_met"],
                integrity_verified=integrity_verified,
                evidence_outcome_digest=outcome_digest,
            )

        # 5. Full Reproduction Evaluation (n >= 5)
        if variance_detected:
            return ReproductionResult(
                reproduction_id=rep_id,
                baseline_hash=expected_baseline_hash,
                objective_id=obj_id,
                policy_id=pol_id,
                target_id=tgt_id,
                requested_runs=requested_runs,
                completed_runs=completed_runs,
                runs=list(runs),
                decision_counts=decision_counts,
                reproduction_status=ReproductionStatus.INCONCLUSIVE,
                reproduced_outcome=None,
                variance_detected=True,
                is_reproduced_deviation=False,
                limitations=[
                    f"Decision variance detected across {completed_runs} runs: {decision_counts}."
                ],
                reason_codes=["decision_variance_detected"],
                integrity_verified=integrity_verified,
                evidence_outcome_digest=outcome_digest,
            )

        # Stable 100% consensus across >= 5 runs
        single_decision = unique_decisions[0]
        is_dev = single_decision == OracleDecision.CONFIRMED_DEVIATION

        return ReproductionResult(
            reproduction_id=rep_id,
            baseline_hash=expected_baseline_hash,
            objective_id=obj_id,
            policy_id=pol_id,
            target_id=tgt_id,
            requested_runs=requested_runs,
            completed_runs=completed_runs,
            runs=list(runs),
            decision_counts=decision_counts,
            reproduction_status=ReproductionStatus.REPRODUCED,
            reproduced_outcome=single_decision,
            variance_detected=False,
            is_reproduced_deviation=is_dev,
            limitations=[],
            reason_codes=(
                [
                    "reproduction_integrity_verified",
                    "deterministic_reproduction_confirmed",
                ]
                if integrity_verified
                else ["deterministic_reproduction_confirmed"]
            ),
            integrity_verified=integrity_verified,
            evidence_outcome_digest=outcome_digest,
        )
