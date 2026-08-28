"""Integration tests for Adaptive Attack Reproduction Governance (Phase 12.3)."""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.oracle import DeterministicToolBoundaryOracle, OracleDecision
from src.openagentsec.reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionRun,
    ReproductionStatus,
    compute_config_hash,
)
from tests.integration.planner.test_state_memory_security import _load_fixtures


def test_case1_five_run_zero_variance_reproduction_on_mutation() -> None:
    """Case 1: Validate statutory 5-run consensus on an adaptive mutation attack."""
    policy, objective, _ = _load_fixtures()

    cfg_hash = compute_config_hash({"mutation_id": "MUT-AUTH-001-PRM-01", "runs": 5})
    baseline = BaselineIdentity(
        policy_id=policy.policy_id,
        policy_version="1.0.0",
        objective_id=objective.objective_id,
        target_id="TARGET-LANGGRAPH-AUTH-WHITEBOX",
        target_version="1.0.0",
        scenario_id="MUT-AUTH-001-PRM-01",
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=cfg_hash,
    )

    runs: List[ReproductionRun] = []
    for idx in range(1, 6):
        runs.append(
            ReproductionRun(
                run_id=f"RUN-MUT-REPRO-{idx}",
                run_index=idx,
                baseline_hash=baseline.compute_baseline_hash(),
                oracle_decision=OracleDecision.NO_CONFIRMED_DEVIATION,
                violated_invariants=[],
                deviation_present=False,
                deviation_severity="none",
                reason_codes=[],
                evidence_refs=["EV-MUT-01-TOOL", "EV-MUT-01-STATE"],
                reset_verified_before=True,
                reset_verified_after=True,
                valid=True,
            )
        )

    res = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert res.reproduction_status == ReproductionStatus.REPRODUCED
    assert res.reproduced_outcome == OracleDecision.NO_CONFIRMED_DEVIATION
    assert res.variance_detected is False
    assert res.completed_runs == 5


def test_case2_stochastic_drift_on_mutation_yields_inconclusive() -> None:
    """Case 2: Any stochastic variance in mutation attack evaluation triggers Fail-Closed INCONCLUSIVE."""
    policy, objective, _ = _load_fixtures()

    cfg_hash = compute_config_hash({"mutation_id": "MUT-AUTH-001-NOISY", "runs": 5})
    baseline = BaselineIdentity(
        policy_id=policy.policy_id,
        policy_version="1.0.0",
        objective_id=objective.objective_id,
        target_id="TARGET-LANGGRAPH-AUTH-WHITEBOX",
        target_version="1.0.0",
        scenario_id="MUT-AUTH-001-NOISY",
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=cfg_hash,
    )

    # 4 clean runs, 1 deviated run -> variance!
    decisions = [
        OracleDecision.NO_CONFIRMED_DEVIATION,
        OracleDecision.NO_CONFIRMED_DEVIATION,
        OracleDecision.CONFIRMED_DEVIATION,  # Noise / drift
        OracleDecision.NO_CONFIRMED_DEVIATION,
        OracleDecision.NO_CONFIRMED_DEVIATION,
    ]

    runs: List[ReproductionRun] = []
    for idx, dec in enumerate(decisions, start=1):
        runs.append(
            ReproductionRun(
                run_id=f"RUN-MUT-DRIFT-{idx}",
                run_index=idx,
                baseline_hash=baseline.compute_baseline_hash(),
                oracle_decision=dec,
                violated_invariants=["INV-TOOL-ALLOWLIST-001"] if dec == OracleDecision.CONFIRMED_DEVIATION else [],
                deviation_present=dec == OracleDecision.CONFIRMED_DEVIATION,
                deviation_severity="high" if dec == OracleDecision.CONFIRMED_DEVIATION else "none",
                reason_codes=[],
                evidence_refs=["EV-MUT-01-TOOL"],
                reset_verified_before=True,
                reset_verified_after=True,
                valid=True,
            )
        )

    res = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert res.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert res.variance_detected is True
