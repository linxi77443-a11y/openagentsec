"""Tests for Phase 7.5.1 Third-Party Adapter Simulation.

Validates that an external developer with a proprietary Python Agent runtime
can integrate into OpenAgentSec via BlackboxTargetAdapter without modifying their agent.
"""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.oracle import DeterministicToolBoundaryOracle, OracleDecision
from src.openagentsec.reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionRun,
    ReproductionStatus,
    compute_config_hash,
)
from tests.integration.external_validation.mock_third_party_agent import (
    CustomEnterpriseAgent,
    ThirdPartyAgentAdapter,
)
from tests.integration.planner.test_state_memory_security import _load_fixtures


# ==============================================================================
# Case 1: Third-Party Agent Independent Operation
# ==============================================================================

def test_case1_third_party_agent_independent_operation() -> None:
    """Case 1: Custom enterprise agent operates independently without OpenAgentSec dependencies."""
    agent = CustomEnterpriseAgent()
    res = agent.handle_user_prompt("Please lookup internal employee directory")
    assert "Found 12 matching directory records" in res["reply"]
    assert len(res["tool_dispatches"]) == 1
    assert res["tool_dispatches"][0]["tool_name"] == "lookup_internal_directory"


# ==============================================================================
# Case 2: Adapter Protocol Conformance
# ==============================================================================

def test_case2_adapter_protocol_conformance() -> None:
    """Case 2: Validate that ThirdPartyAgentAdapter conforms to BlackboxTargetAdapter interface."""
    adapter = ThirdPartyAgentAdapter()
    adapter.reset_session(clean_state=True)

    caps = adapter.get_capabilities()
    assert caps["target_id"] == "TARGET-THIRD-PARTY-ENTERPRISE-AGENT"
    assert caps["capabilities"]["tool_execution"] is True
    assert caps["capabilities"]["blackbox_adapter_supported"] is True

    resp = adapter.send_message("Please lookup internal employee directory")
    assert resp.status == "success"
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0]["name"] == "lookup_internal_directory"

    execs = adapter.observe_tool_execution()
    assert len(execs) == 1
    assert execs[0]["tool"] == "lookup_internal_directory"
    assert execs[0]["verified_runtime_execution"] is True


# ==============================================================================
# Case 3: Evidence Generation & Oracle Adjudication
# ==============================================================================

def test_case3_evidence_generation_and_oracle_adjudication() -> None:
    """Case 3: Verify adapter produces formal EvidenceItems and Oracle adjudicates correctly."""
    policy, objective, _ = _load_fixtures()
    adapter = ThirdPartyAgentAdapter()
    adapter.reset_session(clean_state=True)

    adapter.send_message("Please lookup internal employee directory")
    evidence_items = adapter.collect_evidence(step_id="STEP-001", run_id="RUN-EXT-01")

    assert len(evidence_items) == 2
    types = {e.evidence_type for e in evidence_items}
    assert "tool_execution_log" in types
    assert "state_transition_trace" in types

    # Oracle evaluation
    oracle = DeterministicToolBoundaryOracle()
    tool_execs = adapter.observe_tool_execution()
    obs = {
        "actual_tool_execution": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=tool_execs,
            observability=ObservabilityState.OBSERVABLE,
            source="custom_adapter",
        ),
        "tool_trace": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=tool_execs,
            observability=ObservabilityState.OBSERVABLE,
            source="custom_adapter",
        ),
        "runtime_state": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={"tools": len(tool_execs)},
            observability=ObservabilityState.OBSERVABLE,
            source="custom_adapter",
        ),
        "model_response": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value="Found 12 matching directory records.",
            observability=ObservabilityState.OBSERVABLE,
            source="custom_adapter",
        ),
    }

    res = oracle.evaluate(policy, objective, obs, evidence_items=evidence_items)
    assert res.decision == OracleDecision.NO_CONFIRMED_DEVIATION


# ==============================================================================
# Case 4: 5-Run Statutory Reproduction
# ==============================================================================

def test_case4_third_party_agent_statutory_reproduction() -> None:
    """Case 4: Multi-run deterministic reproduction over third-party agent adapter."""
    policy, objective, _ = _load_fixtures()
    oracle = DeterministicToolBoundaryOracle()
    adapter = ThirdPartyAgentAdapter()

    cfg_hash = compute_config_hash(
        {"target": "ThirdPartyAgentAdapter", "scenario": "safe_lookup", "runs": 5}
    )
    baseline = BaselineIdentity(
        policy_id=policy.policy_id,
        policy_version="1.0.0",
        objective_id=objective.objective_id,
        target_id="TARGET-THIRD-PARTY-ENTERPRISE-AGENT",
        target_version="1.0.0",
        scenario_id="SCENARIO-EXT-001",
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=cfg_hash,
    )

    repro_runs: List[ReproductionRun] = []
    for run_idx in range(1, 6):
        adapter.reset_session(clean_state=True)
        adapter.send_message("Please lookup internal employee directory")
        evidence_items = adapter.collect_evidence(step_id="STEP-001", run_id=f"RUN-EXT-REPRO-{run_idx}")
        tool_execs = adapter.observe_tool_execution()
        obs = {
            "actual_tool_execution": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=tool_execs,
                observability=ObservabilityState.OBSERVABLE,
                source="custom_adapter",
            ),
            "tool_trace": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=tool_execs,
                observability=ObservabilityState.OBSERVABLE,
                source="custom_adapter",
            ),
            "runtime_state": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value={"tools": len(tool_execs)},
                observability=ObservabilityState.OBSERVABLE,
                source="custom_adapter",
            ),
            "model_response": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value="Found 12 records",
                observability=ObservabilityState.OBSERVABLE,
                source="custom_adapter",
            ),
        }
        res = oracle.evaluate(policy, objective, obs, evidence_items=evidence_items)
        repro_runs.append(
            ReproductionRun(
                run_id=f"RUN-EXT-REPRO-{run_idx}",
                run_index=run_idx,
                baseline_hash=baseline.compute_baseline_hash(),
                oracle_decision=res.decision,
                violated_invariants=list(res.violated_invariants),
                deviation_present=res.decision == OracleDecision.CONFIRMED_DEVIATION,
                deviation_severity="none",
                reason_codes=list(res.reason_codes),
                evidence_refs=[e.evidence_id for e in evidence_items],
                reset_verified_before=True,
                reset_verified_after=True,
                valid=True,
            )
        )

    rep_result = ReproductionAggregator.aggregate(repro_runs, requested_runs=5, baseline=baseline)
    assert rep_result.reproduction_status == ReproductionStatus.REPRODUCED
    assert rep_result.reproduced_outcome == OracleDecision.NO_CONFIRMED_DEVIATION
    assert rep_result.variance_detected is False
    assert rep_result.completed_runs == 5
