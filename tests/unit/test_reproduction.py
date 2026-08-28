"""Unit tests for ReproductionAggregator and BaselineIdentity (PRD v4.0.2 Phase 4A)."""

from __future__ import annotations

import inspect
import pytest

from src.openagentsec.oracle.enums import OracleDecision
from src.openagentsec.reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionResult,
    ReproductionRun,
    ReproductionStatus,
    compute_config_hash,
)


@pytest.fixture
def eval_config():
    return {
        "execution_mode": "whitebox_instrumented",
        "deterministic_routing": True,
        "max_steps": 10,
        "oracle_mode": "deterministic_tool_boundary",
        "requested_runs": 5,
    }


@pytest.fixture
def baseline(eval_config):
    return BaselineIdentity(
        policy_id="POL-MVP1-TOOL-BOUNDARY-001",
        policy_version="1.0.0",
        objective_id="OBJ-MVP1-TOOL-SELECTION-001",
        target_id="TARGET-LANGGRAPH-MVP1-WHITEBOX",
        target_version="0.6.11",
        scenario_id="SCENARIO-MVP1-RISK-001",
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=compute_config_hash(eval_config),
    )


def _make_run(
    index: int,
    decision: OracleDecision,
    baseline_hash: str,
    evidence_id: str,
    reset_ok: bool = True,
    valid: bool = True,
) -> ReproductionRun:
    return ReproductionRun(
        run_id=f"RUN-{index:03d}",
        run_index=index,
        baseline_hash=baseline_hash,
        oracle_decision=decision,
        violated_invariants=["INV-TOOL-ALLOWLIST-001"] if decision == OracleDecision.CONFIRMED_DEVIATION else [],
        deviation_present=(decision == OracleDecision.CONFIRMED_DEVIATION),
        deviation_severity="critical" if decision == OracleDecision.CONFIRMED_DEVIATION else None,
        reason_codes=["test_reason"],
        evidence_refs=[evidence_id],
        reset_verified_before=reset_ok,
        reset_verified_after=reset_ok,
        valid=valid,
    )


def test_reproduction_core_contains_no_langgraph_dependency():
    """J. Verify Reproduction core does not import LangGraph or target frameworks."""
    import src.openagentsec.reproduction.aggregator as agg_mod
    import src.openagentsec.reproduction.baseline as base_mod
    import src.openagentsec.reproduction.result as res_mod

    agg_src = inspect.getsource(agg_mod)
    base_src = inspect.getsource(base_mod)
    res_src = inspect.getsource(res_mod)

    for src in (agg_src, base_src, res_src):
        assert "langgraph" not in src.lower()
        assert "langchain" not in src.lower()


def test_config_canonicalization_and_sensitivity():
    """1 & 2. Test config hash canonicalization and sensitivity to config parameter modifications."""
    cfg_a = {"mode": "deterministic", "steps": 10, "routing": True}
    cfg_a_reordered = {"routing": True, "mode": "deterministic", "steps": 10}
    cfg_b = {"mode": "deterministic", "steps": 10, "routing": False}  # Changed routing

    hash_a = compute_config_hash(cfg_a)
    hash_a_reordered = compute_config_hash(cfg_a_reordered)
    hash_b = compute_config_hash(cfg_b)

    assert len(hash_a) == 64
    assert hash_a == hash_a_reordered  # Canonicalization invariant
    assert hash_a != hash_b            # Sensitivity invariant


def test_baseline_identity_canonicalization_and_sensitivity(baseline, eval_config):
    """8. Test baseline hash canonicalization and sensitivity to any field change."""
    base_hash = baseline.compute_baseline_hash()
    assert len(base_hash) == 64

    cfg_hash = compute_config_hash(eval_config)

    # Identical baseline produces identical hash
    b_same = BaselineIdentity(
        policy_id="POL-MVP1-TOOL-BOUNDARY-001",
        policy_version="1.0.0",
        objective_id="OBJ-MVP1-TOOL-SELECTION-001",
        target_id="TARGET-LANGGRAPH-MVP1-WHITEBOX",
        target_version="0.6.11",
        scenario_id="SCENARIO-MVP1-RISK-001",
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=cfg_hash,
    )
    assert b_same.compute_baseline_hash() == base_hash

    # Changing any single field changes the hash
    assert BaselineIdentity("POL-DIFF", "1.0.0", "OBJ-MVP1-TOOL-SELECTION-001", "TARGET-LANGGRAPH-MVP1-WHITEBOX", "0.6.11", "SCENARIO-MVP1-RISK-001", "ORACLE-DETERMINISTIC-TOOL-001", cfg_hash).compute_baseline_hash() != base_hash
    assert BaselineIdentity("POL-MVP1-TOOL-BOUNDARY-001", "1.0.1", "OBJ-MVP1-TOOL-SELECTION-001", "TARGET-LANGGRAPH-MVP1-WHITEBOX", "0.6.11", "SCENARIO-MVP1-RISK-001", "ORACLE-DETERMINISTIC-TOOL-001", cfg_hash).compute_baseline_hash() != base_hash
    assert BaselineIdentity("POL-MVP1-TOOL-BOUNDARY-001", "1.0.0", "OBJ-DIFF", "TARGET-LANGGRAPH-MVP1-WHITEBOX", "0.6.11", "SCENARIO-MVP1-RISK-001", "ORACLE-DETERMINISTIC-TOOL-001", cfg_hash).compute_baseline_hash() != base_hash
    assert BaselineIdentity("POL-MVP1-TOOL-BOUNDARY-001", "1.0.0", "OBJ-MVP1-TOOL-SELECTION-001", "TARGET-DIFF", "0.6.11", "SCENARIO-MVP1-RISK-001", "ORACLE-DETERMINISTIC-TOOL-001", cfg_hash).compute_baseline_hash() != base_hash
    assert BaselineIdentity("POL-MVP1-TOOL-BOUNDARY-001", "1.0.0", "OBJ-MVP1-TOOL-SELECTION-001", "TARGET-LANGGRAPH-MVP1-WHITEBOX", "0.6.12", "SCENARIO-MVP1-RISK-001", "ORACLE-DETERMINISTIC-TOOL-001", cfg_hash).compute_baseline_hash() != base_hash
    assert BaselineIdentity("POL-MVP1-TOOL-BOUNDARY-001", "1.0.0", "OBJ-MVP1-TOOL-SELECTION-001", "TARGET-LANGGRAPH-MVP1-WHITEBOX", "0.6.11", "SCENARIO-DIFF", "ORACLE-DETERMINISTIC-TOOL-001", cfg_hash).compute_baseline_hash() != base_hash
    assert BaselineIdentity("POL-MVP1-TOOL-BOUNDARY-001", "1.0.0", "OBJ-MVP1-TOOL-SELECTION-001", "TARGET-LANGGRAPH-MVP1-WHITEBOX", "0.6.11", "SCENARIO-MVP1-RISK-001", "ORACLE-DIFF", cfg_hash).compute_baseline_hash() != base_hash
    assert BaselineIdentity("POL-MVP1-TOOL-BOUNDARY-001", "1.0.0", "OBJ-MVP1-TOOL-SELECTION-001", "TARGET-LANGGRAPH-MVP1-WHITEBOX", "0.6.11", "SCENARIO-MVP1-RISK-001", "ORACLE-DETERMINISTIC-TOOL-001", "cfg_diff_hash").compute_baseline_hash() != base_hash


def test_single_run_yields_repeat_observed(baseline):
    """A. 1 identical run -> REPEAT_OBSERVED (completed_runs < 5)."""
    b_hash = baseline.compute_baseline_hash()
    runs = [_make_run(1, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-001")]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.REPEAT_OBSERVED
    assert result.completed_runs == 1
    assert result.is_reproduced_deviation is False
    assert "reproduction_threshold_not_met" in result.reason_codes


def test_four_runs_yields_repeat_observed(baseline):
    """B. 4 identical runs -> REPEAT_OBSERVED (completed_runs < 5)."""
    b_hash = baseline.compute_baseline_hash()
    runs = [
        _make_run(i, OracleDecision.CONFIRMED_DEVIATION, b_hash, f"EV-RUN-{i:03d}")
        for i in range(1, 5)
    ]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.REPEAT_OBSERVED
    assert result.completed_runs == 4
    assert result.is_reproduced_deviation is False
    assert "reproduction_threshold_not_met" in result.reason_codes


def test_five_identical_confirmed_deviations_yields_reproduced_deviation(baseline):
    """C. 5 identical CONFIRMED_DEVIATION runs -> REPRODUCED with is_reproduced_deviation=True."""
    b_hash = baseline.compute_baseline_hash()
    runs = [
        _make_run(i, OracleDecision.CONFIRMED_DEVIATION, b_hash, f"EV-RUN-{i:03d}")
        for i in range(1, 6)
    ]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.REPRODUCED
    assert result.is_reproduced is True
    assert result.is_reproduced_deviation is True
    assert result.reproduced_outcome == OracleDecision.CONFIRMED_DEVIATION
    assert result.variance_detected is False
    assert result.decision_counts == {"CONFIRMED_DEVIATION": 5}
    assert "deterministic_reproduction_confirmed" in result.reason_codes


def test_five_identical_no_confirmed_deviations_yields_reproduced_safe(baseline):
    """D. 5 identical NO_CONFIRMED_DEVIATION runs -> REPRODUCED with is_reproduced_deviation=False."""
    b_hash = baseline.compute_baseline_hash()
    runs = [
        _make_run(i, OracleDecision.NO_CONFIRMED_DEVIATION, b_hash, f"EV-RUN-{i:03d}")
        for i in range(1, 6)
    ]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.REPRODUCED
    assert result.is_reproduced is True
    assert result.is_reproduced_deviation is False
    assert result.reproduced_outcome == OracleDecision.NO_CONFIRMED_DEVIATION
    assert result.variance_detected is False
    assert result.decision_counts == {"NO_CONFIRMED_DEVIATION": 5}


def test_five_identical_inconclusive_yields_reproduced_inconclusive(baseline):
    """E. 5 identical INCONCLUSIVE runs -> REPRODUCED outcome of INCONCLUSIVE (not a deviation)."""
    b_hash = baseline.compute_baseline_hash()
    runs = [
        _make_run(i, OracleDecision.INCONCLUSIVE, b_hash, f"EV-RUN-{i:03d}")
        for i in range(1, 6)
    ]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.REPRODUCED
    assert result.is_reproduced is True
    assert result.is_reproduced_deviation is False  # Must strictly be False
    assert result.reproduced_outcome == OracleDecision.INCONCLUSIVE
    assert result.variance_detected is False
    assert result.decision_counts == {"INCONCLUSIVE": 5}


def test_four_confirmed_and_one_inconclusive_yields_inconclusive_due_to_variance(baseline):
    """F. 4 CONFIRMED_DEVIATION + 1 INCONCLUSIVE -> variance detected -> INCONCLUSIVE (no majority voting)."""
    b_hash = baseline.compute_baseline_hash()
    runs = [
        _make_run(1, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-001"),
        _make_run(2, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-002"),
        _make_run(3, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-003"),
        _make_run(4, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-004"),
        _make_run(5, OracleDecision.INCONCLUSIVE, b_hash, "EV-RUN-005"),
    ]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert result.variance_detected is True
    assert result.reproduced_outcome is None
    assert result.is_reproduced_deviation is False
    assert "decision_variance_detected" in result.reason_codes
    assert result.decision_counts == {"CONFIRMED_DEVIATION": 4, "INCONCLUSIVE": 1}


def test_baseline_drift_yields_inconclusive_with_variance_false(baseline):
    """G. Runs 1-4 on baseline A, Run 5 on baseline B -> INCONCLUSIVE (baseline_drift_detected, variance_detected=False)."""
    b_hash_a = baseline.compute_baseline_hash()
    b_hash_b = "different_baseline_hash_999"

    runs = [
        _make_run(1, OracleDecision.CONFIRMED_DEVIATION, b_hash_a, "EV-RUN-001"),
        _make_run(2, OracleDecision.CONFIRMED_DEVIATION, b_hash_a, "EV-RUN-002"),
        _make_run(3, OracleDecision.CONFIRMED_DEVIATION, b_hash_a, "EV-RUN-003"),
        _make_run(4, OracleDecision.CONFIRMED_DEVIATION, b_hash_a, "EV-RUN-004"),
        _make_run(5, OracleDecision.CONFIRMED_DEVIATION, b_hash_b, "EV-RUN-005"),
    ]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert result.variance_detected is False  # Decision variance is not asserted across drifting baselines
    assert "baseline_drift_detected" in result.reason_codes


def test_failed_reset_yields_inconclusive_due_to_independence_failure(baseline):
    """H. A run failed pre/post reset -> INCONCLUSIVE (independence_verification_failed)."""
    b_hash = baseline.compute_baseline_hash()
    runs = [
        _make_run(1, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-001", reset_ok=True),
        _make_run(2, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-002", reset_ok=True),
        _make_run(3, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-003", reset_ok=False),  # Reset unverified/failed
        _make_run(4, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-004", reset_ok=True),
        _make_run(5, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-005", reset_ok=True),
    ]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert "independence_verification_failed" in result.reason_codes


def test_invalid_run_fails_reproduction_even_if_five_runs_present(baseline):
    """4. If one run is valid=False, reproduction fails closed -> INCONCLUSIVE."""
    b_hash = baseline.compute_baseline_hash()
    runs = [
        _make_run(1, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-001", valid=True),
        _make_run(2, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-002", valid=True),
        _make_run(3, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-003", valid=False),  # Invalid run
        _make_run(4, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-004", valid=True),
        _make_run(5, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-005", valid=True),
    ]

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)
    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert result.is_reproduced is False


def test_per_run_evidence_provenance_isolated(baseline):
    """I. Each run maintains isolated evidence references."""
    b_hash = baseline.compute_baseline_hash()
    runs = [
        _make_run(1, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-001"),
        _make_run(2, OracleDecision.CONFIRMED_DEVIATION, b_hash, "EV-RUN-002"),
    ]

    assert runs[0].evidence_refs != runs[1].evidence_refs
    assert runs[0].evidence_refs == ["EV-RUN-001"]
    assert runs[1].evidence_refs == ["EV-RUN-002"]
