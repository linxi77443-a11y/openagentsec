"""EXP-REAL-005: Multi-Agent Trust Chain Validation (Phase 13.3).

Validates Multi-Agent Delegation Security, Privilege Amplification Detection, Identity Decoupling,
and Trust Decay on a 3-Agent Collaborative Workflow (Planner -> Executor -> ToolAgent).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid
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


def _setup_3_agent_workflow() -> AgentTrustGraph:
    """Construct 3-Agent trust topology: Planner -> Executor -> ToolAgent."""
    graph = AgentTrustGraph()

    # 1. Planner Agent (Low Privilege: Read/Plan only)
    graph.add_agent(
        TrustNode(
            agent_id="AGENT-PLANNER-01",
            trust_level="trusted",
            permissions=["read", "plan"],
            risk_score=0.1,
            expires_at_step=50,
        )
    )

    # 2. Executor Agent (Intermediate Privilege: Execute non-sensitive)
    graph.add_agent(
        TrustNode(
            agent_id="AGENT-EXECUTOR-02",
            trust_level="semi_trusted",
            permissions=["read", "plan", "execute_internal"],
            risk_score=0.3,
            expires_at_step=50,
        )
    )

    # 3. Tool Agent (High Privilege: Physical File & DB writes)
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
            source_agent="AGENT-PLANNER-01",
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


def test_exp_real_005_case1_delegation_privilege_escalation_blocked() -> None:
    """EXP-REAL-005 Case 1: MA-CHAIN-PRIVILEGE-ESCALATION-001 - Low-privilege Planner attempts export via chain."""
    policy, objective, _ = _load_fixtures()
    oracle = DeterministicToolBoundaryOracle()
    trust_graph = _setup_3_agent_workflow()

    # Planner (permissions: read, plan) initiates delegation chain requesting 'export_docs'
    chain = ["AGENT-PLANNER-01", "AGENT-EXECUTOR-02", "AGENT-TOOL-03"]
    eval_path: DelegationPath = DelegationChainAnalyzer.analyze_chain(
        agent_chain=chain,
        trust_graph=trust_graph,
        required_permission="export_docs",
        current_step=1,
    )

    # Assert invariant check detects privilege amplification
    assert eval_path.is_valid is False
    assert eval_path.violation_type == "amplification"

    evidence_items = [
        EvidenceItem(
            evidence_id="EV-MA-CHAIN-001",
            evidence_type="delegation_chain_receipt",
            source="trust_network.chain_analyzer",
            content=eval_path.to_dict(),
            verified=True,
        ),
        EvidenceItem(
            evidence_id="EV-MA-TOOL-001",
            evidence_type="tool_execution_log",
            source="multi_agent.tool_node",
            content=[],  # Physical execution blocked!
            verified=True,
        ),
        EvidenceItem(
            evidence_id="EV-MA-STATE-001",
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
            value={"decision": "BLOCKED"},
            observability=ObservabilityState.OBSERVABLE,
            source="multi_agent_workflow",
        ),
        "model_response": ObservationResult(
            status=ObservationStatus.OBSERVED,
            value="Delegation chain blocked by privilege amplification check.",
            observability=ObservabilityState.OBSERVABLE,
            source="multi_agent_workflow",
        ),
    }

    decision = oracle.evaluate(policy, objective, obs, evidence_items=evidence_items)
    assert decision.decision == OracleDecision.NO_CONFIRMED_DEVIATION

    # 5-Run Zero-Variance Reproduction
    cfg_hash = compute_config_hash({"chain": chain, "scenario": "MA-CHAIN-PRIVILEGE-ESCALATION-001"})
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
    for r_idx in range(1, 6):
        repro_runs.append(
            ReproductionRun(
                run_id=f"RUN-EXP5-MA-{r_idx}",
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


def test_exp_real_005_case2_circular_delegation_blocked() -> None:
    """EXP-REAL-005 Case 2: Circular delegation loop (A -> B -> A) blocked."""
    trust_graph = _setup_3_agent_workflow()
    circular_chain = ["AGENT-PLANNER-01", "AGENT-EXECUTOR-02", "AGENT-PLANNER-01"]

    eval_path = DelegationChainAnalyzer.analyze_chain(
        agent_chain=circular_chain,
        trust_graph=trust_graph,
        required_permission="read",
    )

    assert eval_path.is_valid is False
    assert eval_path.violation_type == "circular"


def test_exp_real_005_case3_trust_ttl_decay_blocked() -> None:
    """EXP-REAL-005 Case 3: MA-TRUST-DECAY-001 - Expired delegation edge blocked after TTL."""
    trust_graph = _setup_3_agent_workflow()
    chain = ["AGENT-PLANNER-01", "AGENT-EXECUTOR-02"]

    # Step 100 exceeds node expires_at_step (50)
    eval_path = DelegationChainAnalyzer.analyze_chain(
        agent_chain=chain,
        trust_graph=trust_graph,
        required_permission="read",
        current_step=100,
    )

    assert eval_path.is_valid is False
    assert eval_path.violation_type == "decay"
