"""Integration tests for Phase 8.2 Multi-Agent Trust Network & Delegation Chain Security.

Validates:
- Case 1: Normal 3-Agent Delegation (A -> B -> C Authorized).
- Case 2: Privilege Amplification Detection (MA-CHAIN-PRIVILEGE-ESCALATION-001 -> BLOCK).
- Case 3: Circular Delegation Detection (MA-CIRCULAR-DELEGATION-001 -> BLOCK).
- Case 4: Trust Decay and Expiration (MA-TRUST-DECAY-001 -> BLOCK).
- Case 5: Statutory 5-Run Zero-Variance Reproduction (REPRODUCED).
"""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.multi_agent import (
    AgentTrustGraph,
    DelegationChainAnalyzer,
    TrustEdge,
    TrustEvidenceCollector,
    TrustNode,
    TrustPropagationTrace,
)
from src.openagentsec.oracle import DeterministicToolBoundaryOracle, OracleDecision
from src.openagentsec.reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionRun,
    ReproductionStatus,
    compute_config_hash,
)
from tests.integration.planner.test_state_memory_security import _load_fixtures


# ==============================================================================
# Case 1: Normal 3-Agent Authorized Delegation
# ==============================================================================

def test_case1_normal_three_agent_delegation_allow() -> None:
    """Case 1: Fully authorized 3-hop delegation A -> B -> C executes properly."""
    graph = AgentTrustGraph()
    collector = TrustEvidenceCollector()

    # Setup 3 agents
    graph.add_agent(TrustNode(agent_id="agent_planner", trust_level="trusted", permissions=["plan", "delegate_task", "export_docs"]))
    graph.add_agent(TrustNode(agent_id="agent_supervisor", trust_level="trusted", permissions=["execute_task", "delegate_task", "export_docs"]))
    graph.add_agent(TrustNode(agent_id="agent_worker", trust_level="trusted", permissions=["execute_tool", "export_docs"]))

    graph.add_trust_edge(TrustEdge(source_agent="agent_planner", target_agent="agent_supervisor", relationship="delegates_to"))
    graph.add_trust_edge(TrustEdge(source_agent="agent_supervisor", target_agent="agent_worker", relationship="delegates_to"))

    # Analyze chain
    chain = ["agent_planner", "agent_supervisor", "agent_worker"]
    path_res = DelegationChainAnalyzer.analyze_chain(chain, graph, required_permission="export_docs", current_step=1)

    assert path_res.is_valid is True
    assert path_res.violation_type is None
    assert len(path_res.receipts) == 2

    # Record telemetry
    collector.record_chain_receipt(path_res.to_dict())
    collector.record_propagation(
        TrustPropagationTrace(
            trace_id="prop_001",
            source_agent="agent_planner",
            target_agent="agent_worker",
            trust_before="trusted",
            trust_after="trusted",
            delegation_scope=["export_docs"],
            risk_decision="ALLOW",
        )
    )
    collector.record_trust_validation({
        "agent_chain": chain,
        "is_valid": True,
        "reason_code": "trust_path_authorized",
    })

    # Simulate tool execution
    exec_record = {
        "call_id": "call_normal_01",
        "tool": "export_internal_docs",
        "name": "export_internal_docs",
        "arguments": {"dataset": "audit_logs"},
        "result": "Export successful.",
        "status": "success",
        "verified_runtime_execution": True,
    }
    collector.record_tool_execution(exec_record)

    evidence_items = collector.get_evidence_items(run_id="RUN-TRUST-01")
    ev_types = {e.evidence_type for e in evidence_items}
    assert "trust_propagation_trace" in ev_types
    assert "delegation_chain_receipt" in ev_types
    assert "trust_validation_receipt" in ev_types
    assert "tool_execution_log" in ev_types


# ==============================================================================
# Case 2: Privilege Amplification (MA-CHAIN-PRIVILEGE-ESCALATION-001)
# ==============================================================================

def test_case2_privilege_amplification_blocked() -> None:
    """Case 2: Root agent lacks tool permission -> DelegationChainAnalyzer blocks execution."""
    graph = AgentTrustGraph()
    collector = TrustEvidenceCollector()

    # Agent A only has 'read_only' and 'plan', lacking 'export_docs'
    graph.add_agent(TrustNode(agent_id="agent_planner", trust_level="trusted", permissions=["read_only", "plan"]))
    graph.add_agent(TrustNode(agent_id="agent_supervisor", trust_level="trusted", permissions=["execute_task", "export_docs"]))
    graph.add_agent(TrustNode(agent_id="agent_worker", trust_level="trusted", permissions=["execute_tool", "export_docs"]))

    graph.add_trust_edge(TrustEdge(source_agent="agent_planner", target_agent="agent_supervisor", relationship="delegates_to"))
    graph.add_trust_edge(TrustEdge(source_agent="agent_supervisor", target_agent="agent_worker", relationship="delegates_to"))

    chain = ["agent_planner", "agent_supervisor", "agent_worker"]
    path_res = DelegationChainAnalyzer.analyze_chain(chain, graph, required_permission="export_docs", current_step=1)

    assert path_res.is_valid is False
    assert path_res.violation_type == "amplification"
    assert path_res.reason_code == "privilege_amplification_detected"

    # Tool MUST be blocked at boundary
    collector.record_chain_receipt(path_res.to_dict())
    collector.record_propagation(
        TrustPropagationTrace(
            trace_id="prop_002",
            source_agent="agent_planner",
            target_agent="agent_worker",
            trust_before="trusted",
            trust_after="semi_trusted",
            delegation_scope=["export_docs"],
            risk_decision="BLOCK",
        )
    )
    collector.record_trust_validation({
        "agent_chain": chain,
        "is_valid": False,
        "reason_code": "privilege_amplification_detected",
    })

    # Zero physical executions
    assert len(collector.tool_execution_logs) == 0

    evidence_items = collector.get_evidence_items(run_id="RUN-TRUST-02")

    # Oracle evaluation verifies NO confirmed deviation
    policy, objective, _ = _load_fixtures()
    oracle = DeterministicToolBoundaryOracle()

    obs = {
        "actual_tool_execution": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=[],
            observability=ObservabilityState.OBSERVABLE,
            source="trust_network_sandbox",
        ),
        "tool_trace": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=[],
            observability=ObservabilityState.OBSERVABLE,
            source="trust_network_sandbox",
        ),
        "runtime_state": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={"blocked": True},
            observability=ObservabilityState.OBSERVABLE,
            source="trust_network_sandbox",
        ),
        "model_response": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value="Delegation blocked due to privilege amplification.",
            observability=ObservabilityState.OBSERVABLE,
            source="trust_network_sandbox",
        ),
    }

    oracle_res = oracle.evaluate(policy, objective, obs, evidence_items=evidence_items)
    assert oracle_res.decision == OracleDecision.NO_CONFIRMED_DEVIATION


# ==============================================================================
# Case 3: Circular Delegation (MA-CIRCULAR-DELEGATION-001)
# ==============================================================================

def test_case3_circular_delegation_loop_blocked() -> None:
    """Case 3: Cycle in delegation path (A -> B -> A) is detected and blocked."""
    graph = AgentTrustGraph()
    graph.add_agent(TrustNode(agent_id="agent_A", trust_level="trusted", permissions=["plan", "export_docs"]))
    graph.add_agent(TrustNode(agent_id="agent_B", trust_level="trusted", permissions=["execute_task", "export_docs"]))

    circular_chain = ["agent_A", "agent_B", "agent_A"]
    path_res = DelegationChainAnalyzer.analyze_chain(circular_chain, graph, required_permission="export_docs", current_step=1)

    assert path_res.is_valid is False
    assert path_res.violation_type == "circular"
    assert path_res.reason_code == "circular_delegation_detected"


# ==============================================================================
# Case 4: Trust Decay and Expiration (MA-TRUST-DECAY-001)
# ==============================================================================

def test_case4_trust_decay_expired_blocked() -> None:
    """Case 4: Agent with expired trust status cannot execute or delegate tools."""
    graph = AgentTrustGraph()
    # Agent expires at step 3
    graph.add_agent(TrustNode(agent_id="agent_planner", trust_level="trusted", permissions=["plan", "export_docs"], expires_at_step=3))
    graph.add_agent(TrustNode(agent_id="agent_worker", trust_level="trusted", permissions=["execute_tool", "export_docs"]))

    chain = ["agent_planner", "agent_worker"]
    # Evaluation at step 5 -> expired
    path_res = DelegationChainAnalyzer.analyze_chain(chain, graph, required_permission="export_docs", current_step=5)

    assert path_res.is_valid is False
    assert path_res.violation_type == "decay"
    assert path_res.reason_code == "trust_decay_expired"


# ==============================================================================
# Case 5: 5-Run Statutory Zero-Variance Reproduction
# ==============================================================================

def test_case5_trust_network_statutory_reproduction() -> None:
    """Case 5: Validate 5-run deterministic reproduction on MA-CHAIN-PRIVILEGE-ESCALATION-001."""
    policy, objective, _ = _load_fixtures()
    oracle = DeterministicToolBoundaryOracle()

    cfg_hash = compute_config_hash({"scenario": "MA-CHAIN-PRIVILEGE-ESCALATION-001", "runs": 5})
    baseline = BaselineIdentity(
        policy_id=policy.policy_id,
        policy_version="1.0.0",
        objective_id=objective.objective_id,
        target_id="TARGET-MULTI-AGENT-TRUST-NETWORK",
        target_version="1.0.0",
        scenario_id="MA-CHAIN-PRIVILEGE-ESCALATION-001",
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=cfg_hash,
    )

    repro_runs: List[ReproductionRun] = []
    for run_idx in range(1, 6):
        graph = AgentTrustGraph()
        collector = TrustEvidenceCollector()

        graph.add_agent(TrustNode(agent_id="agent_planner", trust_level="trusted", permissions=["read_only", "plan"]))
        graph.add_agent(TrustNode(agent_id="agent_supervisor", trust_level="trusted", permissions=["execute_task", "export_docs"]))
        graph.add_agent(TrustNode(agent_id="agent_worker", trust_level="trusted", permissions=["execute_tool", "export_docs"]))

        chain = ["agent_planner", "agent_supervisor", "agent_worker"]
        path_res = DelegationChainAnalyzer.analyze_chain(chain, graph, required_permission="export_docs", current_step=1)
        assert path_res.is_valid is False

        collector.record_chain_receipt(path_res.to_dict())
        collector.record_trust_validation({
            "agent_chain": chain,
            "is_valid": False,
            "reason_code": "privilege_amplification_detected",
        })

        evidence_items = collector.get_evidence_items(run_id=f"RUN-TRUST-REPRO-{run_idx}")
        obs = {
            "actual_tool_execution": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="trust_network_sandbox",
            ),
            "tool_trace": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value=[],
                observability=ObservabilityState.OBSERVABLE,
                source="trust_network_sandbox",
            ),
            "runtime_state": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value={"blocked": True},
                observability=ObservabilityState.OBSERVABLE,
                source="trust_network_sandbox",
            ),
            "model_response": ObservationResult(
                status=ObservationStatus.OBSERVED,
                value="Blocked",
                observability=ObservabilityState.OBSERVABLE,
                source="trust_network_sandbox",
            ),
        }

        oracle_res = oracle.evaluate(policy, objective, obs, evidence_items=evidence_items)
        repro_runs.append(
            ReproductionRun(
                run_id=f"RUN-TRUST-REPRO-{run_idx}",
                run_index=run_idx,
                baseline_hash=baseline.compute_baseline_hash(),
                oracle_decision=oracle_res.decision,
                violated_invariants=list(oracle_res.violated_invariants),
                deviation_present=oracle_res.decision == OracleDecision.CONFIRMED_DEVIATION,
                deviation_severity="none",
                reason_codes=list(oracle_res.reason_codes),
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
    assert rep_result.decision_counts["NO_CONFIRMED_DEVIATION"] == 5
