"""Unit tests for Coverage lifecycle governance, tracking, and separation from security outcomes (PRD v4.0.2 Phase 5C)."""

from __future__ import annotations

import inspect
from pathlib import Path
import pytest

from src.openagentsec.coverage import (
    CoveragePlanner,
    CoverageRecord,
    CoverageStatus,
    CoverageTracker,
    ExecutionReadiness,
    MAINLINE_COVERAGE_RANKS,
    compute_coverage_id,
)
from src.openagentsec.models import (
    load_evaluation_objective,
    load_security_policy,
    load_target_profile,
)
from src.openagentsec.oracle.enums import OracleDecision
from src.openagentsec.oracle.result import OracleResult
from src.openagentsec.planner import RuleTemplatePlanner
from src.openagentsec.preflight import PreflightCheck, PreflightResult
from src.openagentsec.reproduction.enums import ReproductionStatus
from src.openagentsec.reproduction.result import ReproductionResult
from src.openagentsec.trajectory.models import Trajectory, TrajectoryStep


@pytest.fixture
def fixtures_dir() -> Path:
    return Path("tests/unit/fixtures/v4")


@pytest.fixture
def rule_objective(fixtures_dir: Path):
    return load_evaluation_objective(fixtures_dir / "evaluation_objective" / "obj_mvp1_tool_selection_rule_driven.yaml")


@pytest.fixture
def policy(fixtures_dir: Path):
    return load_security_policy(fixtures_dir / "security_policy" / "pol_mvp1_tool_boundary.yaml")


@pytest.fixture
def target_profile(fixtures_dir: Path):
    return load_target_profile(fixtures_dir / "target_profile" / "langgraph_mvp1_whitebox.yaml")


def test_coverage_core_contains_no_target_or_langgraph_dependencies():
    """1. Verify Coverage core modules do not import Target implementations, LangGraph, or Semantic Judge."""
    import src.openagentsec.coverage.enums as enums_mod
    import src.openagentsec.coverage.planner as plan_mod
    import src.openagentsec.coverage.record as rec_mod
    import src.openagentsec.coverage.tracker as track_mod

    for mod in (enums_mod, plan_mod, rec_mod, track_mod):
        src = inspect.getsource(mod)
        assert "langgraph" not in src.lower()
        assert "langchain" not in src.lower()
        assert "targetagent" not in src.lower()
        assert "semanticjudge" not in src.lower()


def test_deterministic_coverage_id_and_immutability():
    """2. Verify deterministic coverage ID calculation is independent of order and status changes."""
    cov_id1 = compute_coverage_id(risk_refs=["RISK-A", "RISK-B"], objective_id="OBJ-01", target_id="TGT-01")
    cov_id2 = compute_coverage_id(risk_refs=["RISK-B", "RISK-A"], objective_id="OBJ-01", target_id="TGT-01")

    assert cov_id1 == cov_id2
    assert cov_id1.startswith("COV-")

    record = CoveragePlanner.initialize_coverage(risk_refs=["RISK-A", "RISK-B"], objective_id="OBJ-01", target_id="TGT-01")
    assert record.coverage_id == cov_id1

    # Advance status and verify coverage_id is completely immutable
    record.status = CoverageStatus.EVALUATED
    assert record.coverage_id == cov_id1


def test_result_coverage_independence_all_oracle_decisions_yield_evaluated(
    policy, rule_objective, target_profile
):
    """3. PRD §4.4: CONFIRMED_DEVIATION, NO_CONFIRMED_DEVIATION, and INCONCLUSIVE all produce CoverageStatus.EVALUATED."""
    traj = Trajectory(
        trajectory_id="TRAJ-TEST-001",
        run_id="RUN-TEST-001",
        target_id=target_profile.target_id,
        objective_id=rule_objective.objective_id,
        steps=[TrajectoryStep(run_id="RUN-TEST-001", step_id="STEP-01", stimulus_ref="STIM-01")],
    )

    for decision in (OracleDecision.CONFIRMED_DEVIATION, OracleDecision.NO_CONFIRMED_DEVIATION, OracleDecision.INCONCLUSIVE):
        record = CoveragePlanner.initialize_coverage(
            risk_refs=rule_objective.risk_refs,
            objective_id=rule_objective.objective_id,
            target_id=target_profile.target_id,
        )
        record.status = CoverageStatus.EXECUTABLE

        oracle_result = OracleResult(
            oracle_id="ORACLE-MOCK-001",
            policy_id=policy.policy_id,
            objective_id=rule_objective.objective_id,
            target_id=target_profile.target_id,
            decision=decision,
            observation_basis={"basis": f"Mock decision {decision.value}"},
        )

        CoverageTracker.advance_evaluated(record, traj, oracle_result)
        assert record.status == CoverageStatus.EVALUATED
        assert record.trajectory_ref == "TRAJ-TEST-001"

        # Assert no security verdict leakage into CoverageRecord fields
        record_dict = record.to_dict()
        assert "safe" not in record_dict
        assert "vulnerable" not in record_dict
        assert "severity" not in record_dict
        assert "attack_success" not in record_dict


def test_artifact_driven_mainline_lifecycle_progression(policy, rule_objective, target_profile):
    """4. Full progression across the 6 implemented mainline stages."""
    # 1. Initialize mapped_only
    record = CoveragePlanner.initialize_coverage(
        risk_refs=rule_objective.risk_refs,
        policy_refs=policy.target_refs,
    )
    assert record.status == CoverageStatus.MAPPED_ONLY

    # 2. Objective defined
    CoverageTracker.advance_objective(record, rule_objective)
    assert record.status == CoverageStatus.OBJECTIVE_DEFINED
    assert record.objective_id == rule_objective.objective_id

    # 3. Scenario available
    scenario_plan = RuleTemplatePlanner.plan(policy, rule_objective, target_profile)
    CoverageTracker.advance_scenario(record, scenario_plan)
    assert record.status == CoverageStatus.SCENARIO_AVAILABLE
    assert record.scenario_ref == scenario_plan.scenario_id

    # 4. Executable with real PreflightResult object
    preflight_res = PreflightResult(
        overall="PASS",
        ready=True,
        checks=[PreflightCheck(name="network", status="PASS")],
    )
    readiness = ExecutionReadiness(
        target_id=target_profile.target_id,
        adapter_available=True,
        preflight_result=preflight_res,
    )
    CoverageTracker.advance_executable(record, readiness)
    assert record.status == CoverageStatus.EXECUTABLE

    # 5. Evaluated
    traj = Trajectory(
        trajectory_id="TRAJ-TEST-002",
        run_id="RUN-TEST-002",
        target_id=target_profile.target_id,
        objective_id=rule_objective.objective_id,
    )
    oracle_res = OracleResult(
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        policy_id=policy.policy_id,
        objective_id=rule_objective.objective_id,
        target_id=target_profile.target_id,
        decision=OracleDecision.CONFIRMED_DEVIATION,
    )
    CoverageTracker.advance_evaluated(record, traj, oracle_res)
    assert record.status == CoverageStatus.EVALUATED

    # 6. Reproduced
    repro_res = ReproductionResult(
        reproduction_id="REPRO-TEST-001",
        baseline_hash="hash_baseline_test",
        objective_id=rule_objective.objective_id,
        policy_id=policy.policy_id,
        target_id=target_profile.target_id,
        requested_runs=5,
        completed_runs=5,
        reproduction_status=ReproductionStatus.REPRODUCED,
    )
    CoverageTracker.advance_reproduced(record, repro_res)
    assert record.status == CoverageStatus.REPRODUCED
    assert record.reproduction_ref == "REPRO-TEST-001"
    assert len(record.transition_history) == 5


def test_reproduction_gate_fail_closed_on_repeat_observed_or_inconclusive(rule_objective, target_profile, policy):
    """5. Only ReproductionStatus.REPRODUCED can advance to CoverageStatus.REPRODUCED."""
    record = CoveragePlanner.initialize_coverage(
        risk_refs=rule_objective.risk_refs,
        objective_id=rule_objective.objective_id,
        target_id=target_profile.target_id,
    )
    record.status = CoverageStatus.EVALUATED

    # REPEAT_OBSERVED fails closed
    repro_repeat = ReproductionResult(
        reproduction_id="REPRO-REPEAT-001",
        baseline_hash="hash_baseline_test",
        objective_id=rule_objective.objective_id,
        policy_id=policy.policy_id,
        target_id=target_profile.target_id,
        requested_runs=5,
        completed_runs=3,
        reproduction_status=ReproductionStatus.REPEAT_OBSERVED,
    )
    CoverageTracker.advance_reproduced(record, repro_repeat)
    assert record.status == CoverageStatus.EVALUATED
    assert "reproduction_not_confirmed_REPEAT_OBSERVED" in record.limitations

    # INCONCLUSIVE fails closed
    repro_inconc = ReproductionResult(
        reproduction_id="REPRO-INCONC-001",
        baseline_hash="hash_baseline_test",
        objective_id=rule_objective.objective_id,
        policy_id=policy.policy_id,
        target_id=target_profile.target_id,
        requested_runs=5,
        completed_runs=5,
        reproduction_status=ReproductionStatus.INCONCLUSIVE,
    )
    CoverageTracker.advance_reproduced(record, repro_inconc)
    assert record.status == CoverageStatus.EVALUATED


def test_retest_guard_fails_closed():
    """6. Retest transition raises NotImplementedError in Phase 5C."""
    record = CoveragePlanner.initialize_coverage(risk_refs=["RISK-01"])
    record.status = CoverageStatus.REPRODUCED

    with pytest.raises(NotImplementedError, match="Retest verification is not implemented in Phase 5C"):
        CoverageTracker.advance_retest_verified(record)


def test_idempotency_and_no_accidental_downgrade(rule_objective, target_profile, policy):
    """7. Same artifacts do not create duplicate transitions; lower-rank artifacts do not downgrade."""
    record = CoveragePlanner.initialize_coverage(
        risk_refs=rule_objective.risk_refs,
        objective_id=rule_objective.objective_id,
        target_id=target_profile.target_id,
    )
    CoverageTracker.advance_objective(record, rule_objective)
    assert len(record.transition_history) == 1

    # Idempotent call
    CoverageTracker.advance_objective(record, rule_objective)
    assert len(record.transition_history) == 1

    # Advance to SCENARIO_AVAILABLE
    scenario_plan = RuleTemplatePlanner.plan(policy, rule_objective, target_profile)
    CoverageTracker.advance_scenario(record, scenario_plan)
    assert len(record.transition_history) == 2
    assert record.status == CoverageStatus.SCENARIO_AVAILABLE

    # Lower-rank update does NOT downgrade
    CoverageTracker.advance_objective(record, rule_objective)
    assert record.status == CoverageStatus.SCENARIO_AVAILABLE


def test_governance_branch_preserves_mainline_maturity():
    """8. Governance branch states preserve historical highest mainline maturity without ranking above RETEST_VERIFIED."""
    record = CoveragePlanner.initialize_coverage(risk_refs=["RISK-01"])
    record.status = CoverageStatus.EVALUATED

    CoverageTracker.set_design_gate(
        record,
        reason_codes=["missing_whitebox_instrumentation", "unobservable_memory_store"],
    )
    assert record.status == CoverageStatus.DESIGN_GATE
    assert record.highest_mainline_status == CoverageStatus.EVALUATED

    # Branch idempotency
    CoverageTracker.set_design_gate(
        record,
        reason_codes=["missing_whitebox_instrumentation", "unobservable_memory_store"],
    )
    assert len(record.transition_history) == 1

    # OUT_OF_SCOPE branch
    record.status = CoverageStatus.REPRODUCED
    CoverageTracker.set_out_of_scope(
        record,
        reason_codes=["governance_exclusion_synthetic_environment_only"],
    )
    assert record.status == CoverageStatus.OUT_OF_SCOPE
    assert record.highest_mainline_status == CoverageStatus.REPRODUCED


def test_coverage_planner_gap_analysis():
    """9. CoveragePlanner identifies the exact missing artifact for each maturity level."""
    record = CoveragePlanner.initialize_coverage(risk_refs=["RISK-01"])
    assert CoveragePlanner.get_next_missing_artifact(record) == "evaluation_objective"

    record.status = CoverageStatus.OBJECTIVE_DEFINED
    assert CoveragePlanner.get_next_missing_artifact(record) == "scenario_plan"

    record.status = CoverageStatus.SCENARIO_AVAILABLE
    assert CoveragePlanner.get_next_missing_artifact(record) == "execution_readiness"

    record.status = CoverageStatus.EXECUTABLE
    assert CoveragePlanner.get_next_missing_artifact(record) == "trajectory_and_oracle_adjudication"

    record.status = CoverageStatus.EVALUATED
    assert CoveragePlanner.get_next_missing_artifact(record) == "reproduction_result"

    record.status = CoverageStatus.REPRODUCED
    assert CoveragePlanner.get_next_missing_artifact(record) == "retest_verification"

    record.status = CoverageStatus.DESIGN_GATE
    assert CoveragePlanner.get_next_missing_artifact(record) == "governance_resolution_required"


def test_artifact_coherence_mismatches_fail_closed(rule_objective, policy, target_profile):
    """10. Objective/target/policy identity mismatches across artifacts block lifecycle progression."""
    # A. Scenario objective mismatch
    rec1 = CoveragePlanner.initialize_coverage(risk_refs=rule_objective.risk_refs, objective_id="OBJ-OTHER", target_id=target_profile.target_id)
    plan = RuleTemplatePlanner.plan(policy, rule_objective, target_profile)
    CoverageTracker.advance_scenario(rec1, plan)
    assert rec1.status == CoverageStatus.MAPPED_ONLY
    assert "scenario_objective_mismatch_detected" in rec1.limitations

    # B. Trajectory target mismatch
    rec2 = CoveragePlanner.initialize_coverage(risk_refs=rule_objective.risk_refs, objective_id=rule_objective.objective_id, target_id="TARGET-MAIN")
    rec2.status = CoverageStatus.EXECUTABLE
    traj_mismatch = Trajectory(trajectory_id="TRAJ-MISMATCH", run_id="RUN-01", objective_id=rule_objective.objective_id, target_id="TARGET-FOREIGN")
    oracle_res = OracleResult(oracle_id="ORACLE-01", policy_id=policy.policy_id, objective_id=rule_objective.objective_id, target_id="TARGET-MAIN", decision=OracleDecision.CONFIRMED_DEVIATION)
    CoverageTracker.advance_evaluated(rec2, traj_mismatch, oracle_res)
    assert rec2.status == CoverageStatus.EXECUTABLE
    assert "evaluated_target_mismatch_detected" in rec2.limitations

    # C. Reproduction foreign objective mismatch
    rec3 = CoveragePlanner.initialize_coverage(risk_refs=rule_objective.risk_refs, objective_id=rule_objective.objective_id, target_id=target_profile.target_id)
    rec3.status = CoverageStatus.EVALUATED
    repro_mismatch = ReproductionResult(
        reproduction_id="REPRO-FOREIGN",
        baseline_hash="hash_01",
        objective_id="OBJ-FOREIGN",
        policy_id=policy.policy_id,
        target_id=target_profile.target_id,
        requested_runs=5,
        completed_runs=5,
        reproduction_status=ReproductionStatus.REPRODUCED,
    )
    CoverageTracker.advance_reproduced(rec3, repro_mismatch)
    assert rec3.status == CoverageStatus.EVALUATED
    assert "reproduction_objective_mismatch_detected" in rec3.limitations
