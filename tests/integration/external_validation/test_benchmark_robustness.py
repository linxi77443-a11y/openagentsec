"""Tests for Phase 7.5.4 Benchmark Robustness Testing.

Stress tests benchmark edge cases:
- Case 1: Missing Evidence triggers fail-closed INCONCLUSIVE.
- Case 2: Capability Mismatch scenario skipping.
- Case 3: Adapter Exception graceful handling.
- Case 4: Non-deterministic Reproduction drift rejection (Majority voting prohibited).
- Case 5: Metric Registry integrity validation.
"""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.benchmark import EvidenceContractMatrix, MetricRegistry, ScenarioRegistry
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.oracle import DeterministicToolBoundaryOracle, EvidenceItem, OracleDecision
from src.openagentsec.reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionRun,
    ReproductionStatus,
    compute_config_hash,
)
from targets.api.target_adapter import TargetResponse
from tests.integration.external_targets.langchain.adapter import BlackboxTargetAdapter
from tests.integration.planner.test_state_memory_security import _load_fixtures


# ==============================================================================
# Case 1: Missing Mandatory Evidence (Fail-Closed)
# ==============================================================================

def test_robustness_case1_missing_mandatory_evidence_yields_inconclusive() -> None:
    """Case 1: Ensure missing mandatory evidence forces Oracle to return INCONCLUSIVE."""
    policy, objective, _ = _load_fixtures()
    oracle = DeterministicToolBoundaryOracle()

    # Empty evidence list (mandatory tool_execution_log missing)
    empty_evidence: List[EvidenceItem] = []
    obs = {
        "actual_tool_execution": ObservationResult(
            status=ObservationStatus.EMPTY,
            value=[],
            observability=ObservabilityState.OBSERVABLE,
            source="empty",
        ),
        "tool_trace": ObservationResult(
            status=ObservationStatus.EMPTY,
            value=[],
            observability=ObservabilityState.OBSERVABLE,
            source="empty",
        ),
        "runtime_state": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={},
            observability=ObservabilityState.OBSERVABLE,
            source="empty",
        ),
        "model_response": ObservationResult(
            status=ObservationStatus.EMPTY,
            value=None,
            observability=ObservabilityState.OBSERVABLE,
            source="empty",
        ),
    }

    res = oracle.evaluate(policy, objective, obs, evidence_items=empty_evidence)
    assert res.decision == OracleDecision.INCONCLUSIVE
    assert "required_evidence_missing" in res.reason_codes


# ==============================================================================
# Case 2: Target Capability Mismatch
# ==============================================================================

def test_robustness_case2_capability_mismatch_skipping() -> None:
    """Case 2: Validate scenario required capability filtering."""
    stateless_caps = {"tool_execution": True}
    scenario = ScenarioRegistry.get("RET-DIRECT-INSTRUCTION-001")
    assert scenario is not None

    has_caps = all(stateless_caps.get(c, False) for c in scenario.required_capabilities)
    assert has_caps is False  # Correctly identifies capability mismatch


# ==============================================================================
# Case 3: Adapter Exception Graceful Handling
# ==============================================================================

class FaultyAdapter(BlackboxTargetAdapter):
    """Faulty adapter that raises exceptions during send_message."""

    def send_message(self, user_input: str, session_id: Any = None, **kwargs: Any) -> TargetResponse:
        try:
            raise ConnectionResetError("Remote agent host unreachable")
        except Exception as e:
            return TargetResponse(
                content="",
                status="error",
                error_message=str(e),
            )

    def observe_tool_execution(self, session_id: Any = None) -> List[Dict[str, Any]]:
        return []

    def collect_evidence(self, step_id: str, run_id: str) -> List[EvidenceItem]:
        return []

    def reset_session(self, session_id: Any = None, clean_state: bool = True) -> bool:
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        return {"target_id": "FAULTY-TARGET"}


def test_robustness_case3_faulty_adapter_exception_handled() -> None:
    """Case 3: Adapter error is safely captured in TargetResponse without crashing harness."""
    adapter = FaultyAdapter()
    resp = adapter.send_message("test stimulus")
    assert resp.status == "error"
    assert "Remote agent host unreachable" in str(resp.error_message)


# ==============================================================================
# Case 4: Non-Deterministic Reproduction Drift Rejection
# ==============================================================================

def test_robustness_case4_reproduction_drift_rejection_no_majority_voting() -> None:
    """Case 4: 4 CONFIRMED + 1 NO_CONFIRMED must NOT majority vote to CONFIRMED. Must yield INCONCLUSIVE."""
    cfg_hash = compute_config_hash({"test": "drift", "runs": 5})
    baseline = BaselineIdentity(
        policy_id="POL-1", policy_version="1.0.0",
        objective_id="OBJ-1", target_id="TARGET-DRIFT",
        target_version="1.0.0", scenario_id="SCENARIO-DRIFT",
        oracle_id="ORACLE-1", config_hash=cfg_hash,
    )

    # 4 runs confirmed, 1 run no deviation (behavioral drift)
    runs: List[ReproductionRun] = []
    for idx in range(1, 5):
        runs.append(
            ReproductionRun(
                run_id=f"RUN-{idx}", run_index=idx, baseline_hash=baseline.compute_baseline_hash(),
                oracle_decision=OracleDecision.CONFIRMED_DEVIATION, violated_invariants=["INV-1"],
                deviation_present=True, deviation_severity="critical", reason_codes=["violation"],
                evidence_refs=["EV-1"], reset_verified_before=True, reset_verified_after=True, valid=True,
            )
        )
    # Run 5 differs:
    runs.append(
        ReproductionRun(
            run_id="RUN-5", run_index=5, baseline_hash=baseline.compute_baseline_hash(),
            oracle_decision=OracleDecision.NO_CONFIRMED_DEVIATION, violated_invariants=[],
            deviation_present=False, deviation_severity="none", reason_codes=[],
            evidence_refs=["EV-1"], reset_verified_before=True, reset_verified_after=True, valid=True,
        )
    )

    result = ReproductionAggregator.aggregate(runs, requested_runs=5, baseline=baseline)

    # Must reject majority vote:
    assert result.reproduction_status == ReproductionStatus.INCONCLUSIVE
    assert result.variance_detected is True
    assert result.reproduced_outcome is None
    assert result.is_reproduced_deviation is False


# ==============================================================================
# Case 5: Metric Registry Integrity
# ==============================================================================

def test_robustness_case5_metric_registry_integrity() -> None:
    """Case 5: Validate MetricRegistry lookups and schema conformance."""
    metric = MetricRegistry.get("reproduction_rate")
    assert metric is not None
    assert metric.unit == "ratio"
    assert "Identical_Decision_Runs" in metric.formula

    unknown = MetricRegistry.get("non_existent_metric_id")
    assert unknown is None
