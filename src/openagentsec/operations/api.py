"""Security Operations Python API Contract (PRD v4.0.2 Phase 11.5).

Provides a programmatic interface for managing AI agent assets, running continuous evaluations,
and tracking vulnerabilities across an enterprise fleet.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.openagentsec.governance.governance_model import BenchmarkGovernancePolicy
from .agent_registry import AgentAsset, AgentAssetRegistry
from .finding import FindingManager, SecurityFinding
from .security_posture import AgentSecurityPosture
from .workflow import EvaluationExecution, SecurityEvaluationWorkflow


class SecurityOperationsAPI:
    """Unified Python API for OpenAgentSec Security Operations."""

    def __init__(
        self,
        governance_policy: Optional[BenchmarkGovernancePolicy] = None,
    ) -> None:
        self.asset_registry = AgentAssetRegistry()
        self.finding_manager = FindingManager()
        self.governance_policy = governance_policy or BenchmarkGovernancePolicy()
        self.workflow_engine = SecurityEvaluationWorkflow(
            asset_registry=self.asset_registry,
            finding_manager=self.finding_manager,
            governance_policy=self.governance_policy,
        )

    # 1. Asset Management
    def register_agent(self, asset: AgentAsset) -> AgentAsset:
        """Register a new AI agent asset."""
        return self.asset_registry.register_agent(asset)

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> AgentAsset:
        """Update an existing AI agent asset."""
        return self.asset_registry.update_agent(agent_id, updates)

    def get_agent(self, agent_id: str) -> Optional[AgentAsset]:
        """Retrieve an agent asset."""
        return self.asset_registry.get_agent(agent_id)

    def list_agents(
        self,
        environment: Optional[str] = None,
        team: Optional[str] = None,
    ) -> List[AgentAsset]:
        """List registered agent assets."""
        return self.asset_registry.list_agents(environment=environment, team=team)

    # 2. Continuous Evaluation Workflow
    def evaluate_agent(
        self,
        agent_id: str,
        scenarios: Optional[List[str]] = None,
        mock_scenario_results: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> EvaluationExecution:
        """Trigger an automated security evaluation cycle for an agent."""
        return self.workflow_engine.run_evaluation(
            agent_id=agent_id,
            scenarios=scenarios,
            mock_scenario_results=mock_scenario_results,
        )

    # 3. Security Posture
    def get_security_posture(self, agent_id: str) -> AgentSecurityPosture:
        """Compute and return current security posture for an agent."""
        asset = self.get_agent(agent_id)
        if not asset:
            raise KeyError(f"Agent '{agent_id}' not found.")

        findings = self.finding_manager.list_findings(agent_id=agent_id)
        gate_decision = "PASS" if asset.security_status == "COMPLIANT" else "FAIL"

        return AgentSecurityPosture.calculate_posture(
            agent_id=agent_id,
            evaluation_results={},
            findings=findings,
            gate_decision=gate_decision,
        )

    # 4. Finding Lifecycle Management
    def list_findings(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """List security findings with filtering."""
        return self.finding_manager.list_findings(
            agent_id=agent_id,
            status=status,
            severity=severity,
        )

    def update_finding_status(
        self,
        finding_id: str,
        status: str,
        note: Optional[str] = None,
    ) -> SecurityFinding:
        """Update finding state (OPEN -> ACKNOWLEDGED -> FIXED / SUPPRESSED)."""
        return self.finding_manager.update_status(finding_id, status, note)
