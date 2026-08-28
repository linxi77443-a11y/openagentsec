"""Integration tests for Evaluation Workflow Engine (Phase 11.2)."""

from __future__ import annotations

from typing import Any, Dict
import pytest

from src.openagentsec.governance.governance_model import BenchmarkGovernancePolicy
from src.openagentsec.operations import (
    AgentAsset,
    AgentAssetRegistry,
    FindingManager,
    SecurityEvaluationWorkflow,
)


def test_case1_clean_workflow_execution() -> None:
    """Case 1: Workflow runs on compliant agent, updates asset status to COMPLIANT."""
    reg = AgentAssetRegistry()
    findings = FindingManager()
    policy = BenchmarkGovernancePolicy(
        required_scenarios=["AUTH-IDENTITY-SPOOF-001", "TOOL-DENIED-EXECUTION-001"]
    )

    asset = AgentAsset(
        agent_id="AGENT-CLEAN-WF",
        name="CleanAgent",
        owner="ops@corp.internal",
        team="Security",
        version="1.0.0",
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
    )
    reg.register_agent(asset)

    workflow = SecurityEvaluationWorkflow(
        asset_registry=reg,
        finding_manager=findings,
        governance_policy=policy,
    )

    exec_result = workflow.run_evaluation("AGENT-CLEAN-WF")

    assert exec_result.gate_decision == "PASS"
    assert exec_result.posture.risk_level == "LOW"
    assert len(exec_result.new_findings) == 0

    # Verify Asset state was updated in registry
    updated_asset = reg.get_agent("AGENT-CLEAN-WF")
    assert updated_asset.security_status == "COMPLIANT"
    assert updated_asset.last_evaluation is not None


def test_case2_vulnerable_workflow_generates_finding_and_blocks() -> None:
    """Case 2: Workflow on vulnerable agent generates SecurityFinding and sets NON_COMPLIANT."""
    reg = AgentAssetRegistry()
    findings = FindingManager()
    policy = BenchmarkGovernancePolicy(
        required_scenarios=["AUTH-IDENTITY-SPOOF-001"]
    )

    asset = AgentAsset(
        agent_id="AGENT-VULN-WF",
        name="VulnerableAgent",
        owner="dev@corp.internal",
        team="Engineering",
        version="1.0.0",
        target_id="TARGET-LANGGRAPH-AUTH-WHITEBOX",
    )
    reg.register_agent(asset)

    workflow = SecurityEvaluationWorkflow(
        asset_registry=reg,
        finding_manager=findings,
        governance_policy=policy,
    )

    # Simulate vulnerability
    mock_results = {
        "AUTH-IDENTITY-SPOOF-001": {
            "domain": "authorization_security",
            "decision": "CONFIRMED_DEVIATION",
            "evidence_score": 1.0,
            "variance_detected": False,
        }
    }

    exec_result = workflow.run_evaluation(
        agent_id="AGENT-VULN-WF",
        mock_scenario_results=mock_results,
    )

    assert exec_result.gate_decision == "FAIL"
    assert len(exec_result.new_findings) == 1
    assert exec_result.new_findings[0].scenario_id == "AUTH-IDENTITY-SPOOF-001"

    # Verify findings manager has the open finding
    open_findings = findings.list_findings(agent_id="AGENT-VULN-WF", status="OPEN")
    assert len(open_findings) == 1

    # Verify Asset state was updated to NON_COMPLIANT
    updated_asset = reg.get_agent("AGENT-VULN-WF")
    assert updated_asset.security_status == "NON_COMPLIANT"
