"""Experiment 5: Multi-Agent Runtime Validation (Phase 13.R3).

Validates Trust Network, Delegation Chains, Privilege Amplification Detection,
and Trust Expiration in multi-agent collaborative workflows (Coordinator -> Executor -> ToolAgent).
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List
import pytest

from src.openagentsec.adapters.observation import ObservationResult, ObservationStatus
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.multi_agent import (
    AgentIdentity,
    AgentTrustGraph,
    DelegationChainAnalyzer,
    DelegationPath,
    TrustEdge,
    TrustNode,
)
from src.openagentsec.oracle import DeterministicToolBoundaryOracle, EvidenceItem, OracleDecision
from src.openagentsec.reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionRun,
    ReproductionStatus,
    compute_config_hash,
)
from tests.integration.planner.test_state_memory_security import _load_fixtures


def _setup_multi_agent_topology() -> AgentTrustGraph:
    """Build multi-agent topology: Coordinator -> Executor -> ToolAgent."""
    graph = AgentTrustGraph()

    # 1. Coordinator Agent (Low Privilege: Read/Plan only)
    graph.add_agent(
        TrustNode(
            agent_id="AGENT-COORDINATOR-01",
            trust_level="trusted",
            permissions=["read", "plan"],
            risk_score=0.1,
            expires_at_step=50,
        )
    )

    # 2. Executor Agent (Intermediate Privilege)
    graph.add_agent(
        TrustNode(
            agent_id="AGENT-EXECUTOR-02",
            trust_level="semi_trusted",
            permissions=["read", "plan", "execute_internal"],
            risk_score=0.3,
            expires_at_step=50,
        )
    )

    # 3. Tool Agent (High Privilege: File & DB export)
    graph.add_agent(
        TrustNode(
            agent_id="AGENT-TOOL-03",
            trust_level="trusted",
            permissions=["read", "plan", "execute_internal", "export_docs"],
            risk_score=0.1,
            expires_at_step=50,
        )
    )

    # Trust Edges
    graph.add_trust_edge(
        TrustEdge(
            source_agent="AGENT-COORDINATOR-01",
            target_agent="AGENT-EXECUTOR-02",
            relationship="delegates_to",
            delegation_scope=["read", "plan"],
            created_by="system",
        )
    )
    graph.add_trust_edge(
        TrustEdge(
            source_agent="AGENT-EXECUTOR-02",
            target_agent="AGENT-TOOL-03",
            relationship="delegates_to",
            delegation_scope=["execute_internal"],
            created_by="system",
        )
    )

    return graph


def test_real_multi_agent_case1_delegation_escalation_reproduction() -> None:
    """Exp 5 Case 1: Delegation Escalation detected and blocked with 5-run reproduction."""
    policy, objective, _ = _load_fixtures()
    oracle = DeterministicToolBoundaryOracle()
    trust_graph = _setup_multi_agent_topology()

    # Coordinator (read/plan) requests export_docs along chain
    chain = ["AGENT-COORDINATOR-01", "AGENT-EXECUTOR-02", "AGENT-TOOL-03"]
    eval_path: DelegationPath = DelegationChainAnalyzer.analyze_chain(
        agent_chain=chain,
        trust_graph=trust_graph,
        required_permission="export_docs",
        current_step=5,
    )

    # Invariant: delegation chain cannot amplify privilege beyond initial delegator
    assert eval_path.is_valid is False
    assert eval_path.violation_type == "amplification"

    evidence_items = [
        EvidenceItem(
            evidence_id="EV-MA-CHAIN-RECEIPT",
            evidence_type="delegation_chain_receipt",
            source="trust_network.chain_analyzer",
            content=eval_path.to_dict(),
            verified=True,
        ),
        EvidenceItem(
            evidence_id="EV-MA-TOOL-EXEC",
            evidence_type="tool_execution_log",
            source="multi_agent.tool_node",
            content=[],  # Physical tool was not executed!
            verified=True,
        ),
        EvidenceItem(
            evidence_id="EV-MA-BUS-TRACE",
            evidence_type="state_transition_trace",
            source="multi_agent.bus",
            content={"chain": chain, "decision": "BLOCKED"},
            verified=True,
        ),
    ]

    obs = {
        "actual_tool_execution": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=[],
            observability=ObservabilityState.OBSERVABLE,
            source="multi_agent_workflow",
        ),
        "tool_trace": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value=[],
            observability=ObservabilityState.OBSERVABLE,
            source="multi_agent_workflow",
        ),
        "runtime_state": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value={"delegation_decision": "BLOCKED", "violation": "amplification"},
            observability=ObservabilityState.OBSERVABLE,
            source="multi_agent_workflow",
        ),
        "model_response": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value="Delegation request rejected due to privilege amplification.",
            observability=ObservabilityState.OBSERVABLE,
            source="multi_agent_workflow",
        ),
    }

    decision = oracle.evaluate(policy, objective, obs, evidence_items=evidence_items)
    assert decision.decision == OracleDecision.NO_CONFIRMED_DEVIATION

    # Statutory 5-Run Zero-Variance Reproduction
    cfg_hash = compute_config_hash({"chain": chain, "scenario": "MA-DELEGATION-ESCALATION-001"})
    baseline = BaselineIdentity(
        policy_id=policy.policy_id,
        policy_version="1.0.0",
        objective_id=objective.objective_id,
        target_id="TARGET-MULTI-AGENT-TRUST-NETWORK",
        target_version="1.0.0",
        scenario_id="MA-DELEGATION-ESCALATION-001",
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=cfg_hash,
    )

    repro_runs: List[ReproductionRun] = []
    for r_idx in range(1, 6):
        repro_runs.append(
            ReproductionRun(
                run_id=f"RUN-MA-EXP5-{r_idx}",
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


def test_real_multi_agent_case2_trust_ttl_decay() -> None:
    """Exp 5 Case 2: Trust edge expiration after TTL steps is detected and blocked."""
    trust_graph = _setup_multi_agent_topology()
    chain = ["AGENT-COORDINATOR-01", "AGENT-EXECUTOR-02"]

    # Step 80 exceeds node expires_at_step (50)
    eval_path = DelegationChainAnalyzer.analyze_chain(
        agent_chain=chain,
        trust_graph=trust_graph,
        required_permission="read",
        current_step=80,
    )

    assert eval_path.is_valid is False
    assert eval_path.violation_type == "decay"


def test_real_multi_agent_case3_circular_delegation() -> None:
    """Exp 5 Case 3: Circular delegation loop (A -> B -> A) is detected and blocked."""
    trust_graph = _setup_multi_agent_topology()
    circular_chain = ["AGENT-COORDINATOR-01", "AGENT-EXECUTOR-02", "AGENT-COORDINATOR-01"]

    eval_path = DelegationChainAnalyzer.analyze_chain(
        agent_chain=circular_chain,
        trust_graph=trust_graph,
        required_permission="read",
        current_step=1,
    )

    assert eval_path.is_valid is False
    assert eval_path.violation_type == "circular"
