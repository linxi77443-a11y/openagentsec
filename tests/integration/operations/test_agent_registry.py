"""Integration tests for Agent Asset Registry (Phase 11.1)."""

from __future__ import annotations

from typing import Any, Dict
import pytest

from src.openagentsec.operations import AgentAsset, AgentAssetRegistry


def test_case1_agent_registration_and_retrieval() -> None:
    """Case 1: Validate agent asset registration, partial update, filtering, and deletion."""
    registry = AgentAssetRegistry()

    asset1 = AgentAsset(
        agent_id="AGENT-PROD-FINANCE-01",
        name="FinanceAuditAgent",
        owner="alice@corp.internal",
        team="SecOps",
        environment="production",
        version="1.0.0",
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
    )
    asset2 = AgentAsset(
        agent_id="AGENT-STAGING-HR-02",
        name="HROnboardingAgent",
        owner="bob@corp.internal",
        team="HRTech",
        environment="staging",
        version="0.9.0",
        target_id="TARGET-LANGCHAIN-REAL-AGENT",
    )

    # 1. Register
    registry.register_agent(asset1)
    registry.register_agent(asset2)

    # 2. Retrieve
    retrieved = registry.get_agent("AGENT-PROD-FINANCE-01")
    assert retrieved is not None
    assert retrieved.name == "FinanceAuditAgent"
    assert retrieved.environment == "production"

    # 3. List & Filter
    prod_agents = registry.list_agents(environment="production")
    assert len(prod_agents) == 1
    assert prod_agents[0].agent_id == "AGENT-PROD-FINANCE-01"

    hr_agents = registry.list_agents(team="HRTech")
    assert len(hr_agents) == 1
    assert hr_agents[0].agent_id == "AGENT-STAGING-HR-02"

    # 4. Update
    updated = registry.update_agent("AGENT-PROD-FINANCE-01", {"version": "1.1.0", "security_status": "COMPLIANT"})
    assert updated.version == "1.1.0"
    assert updated.security_status == "COMPLIANT"

    # 5. Delete
    deleted = registry.delete_agent("AGENT-STAGING-HR-02")
    assert deleted is True
    assert registry.get_agent("AGENT-STAGING-HR-02") is None
    assert len(registry.list_agents()) == 1
