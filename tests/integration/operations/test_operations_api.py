"""Integration tests for Unified Operations API and Multi-Agent Fleet Isolation (Phase 11.5)."""

from __future__ import annotations

from typing import Any, Dict
import pytest

from src.openagentsec.benchmark import MetricRegistry
from src.openagentsec.governance.governance_model import BenchmarkGovernancePolicy
from src.openagentsec.operations import AgentAsset, SecurityOperationsAPI


def test_case1_operations_api_end_to_end() -> None:
    """Case 1: Full operations lifecycle via high-level SecurityOperationsAPI."""
    policy = BenchmarkGovernancePolicy(required_scenarios=["AUTH-IDENTITY-SPOOF-001"])
    api = SecurityOperationsAPI(governance_policy=policy)

    # 1. Register
    asset = AgentAsset(
        agent_id="AGENT-API-01",
        name="PaymentAgent",
        owner="lead@payment.internal",
        team="Fintech",
        environment="production",
        version="2.0.0",
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
    )
    api.register_agent(asset)
    assert api.get_agent("AGENT-API-01") is not None

    # 2. Evaluate with vulnerability
    mock_res = {
        "AUTH-IDENTITY-SPOOF-001": {
            "domain": "authorization_security",
            "decision": "CONFIRMED_DEVIATION",
            "evidence_score": 1.0,
        }
    }
    exec_res = api.evaluate_agent("AGENT-API-01", mock_scenario_results=mock_res)
    assert exec_res.gate_decision == "FAIL"

    # 3. Check Posture
    posture = api.get_security_posture("AGENT-API-01")
    assert posture.risk_level in ["CRITICAL", "HIGH"]
    assert posture.open_findings_count == 1

    # 4. Manage Finding
    findings = api.list_findings(agent_id="AGENT-API-01", status="OPEN")
    assert len(findings) == 1
    f_id = findings[0].finding_id

    # Remediate finding
    api.update_finding_status(f_id, "FIXED", "Patched authorization token check")
    open_findings_after = api.list_findings(agent_id="AGENT-API-01", status="OPEN")
    assert len(open_findings_after) == 0


def test_case2_multi_agent_fleet_isolation() -> None:
    """Case 2: Validate fleet multi-agent isolation across environments and business teams."""
    api = SecurityOperationsAPI()

    api.register_agent(AgentAsset(agent_id="A1", name="A1", owner="u1", team="Security", environment="production"))
    api.register_agent(AgentAsset(agent_id="A2", name="A2", owner="u2", team="Security", environment="staging"))
    api.register_agent(AgentAsset(agent_id="A3", name="A3", owner="u3", team="DataScience", environment="production"))

    prod_agents = api.list_agents(environment="production")
    assert len(prod_agents) == 2
    assert {a.agent_id for a in prod_agents} == {"A1", "A3"}

    sec_agents = api.list_agents(team="Security")
    assert len(sec_agents) == 2
    assert {a.agent_id for a in sec_agents} == {"A1", "A2"}


def test_case3_operations_metrics_registration() -> None:
    """Case 3: Validate that all 4 Phase 11 Operations metrics are registered in MetricRegistry."""
    req_metrics = [
        "registered_agent_count",
        "evaluation_execution_success_rate",
        "open_security_finding_rate",
        "security_posture_score",
    ]

    for m_id in req_metrics:
        metric = MetricRegistry.get(m_id)
        assert metric is not None, f"Metric '{m_id}' must be registered in MetricRegistry"
        assert metric.formula != ""
        assert metric.unit in ["count", "ratio"]
