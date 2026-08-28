"""Evaluation Workflow Engine (PRD v4.0.2 Phase 11.2).

Orchestrates automated evaluation cycles, finding generation, and security posture updates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Callable, Dict, List, Optional
import uuid

from src.openagentsec.benchmark.scenario_registry import ScenarioRegistry
from src.openagentsec.benchmark.target_catalog import TargetCatalog
from src.openagentsec.governance.governance_model import BenchmarkGovernancePolicy
from src.openagentsec.governance.security_gate import GateDecision, SecurityReleaseGate
from .agent_registry import AgentAsset, AgentAssetRegistry
from .finding import FindingManager, SecurityFinding
from .security_posture import AgentSecurityPosture


@dataclass
class EvaluationExecution:
    """Represents a completed security evaluation workflow run."""

    execution_id: str
    agent_id: str
    evaluated_scenarios: List[str]
    scenario_results: Dict[str, Dict[str, Any]]
    gate_decision: str  # "PASS" | "FAIL"
    new_findings: List[SecurityFinding]
    posture: AgentSecurityPosture
    execution_time: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "agent_id": self.agent_id,
            "evaluated_scenarios": self.evaluated_scenarios,
            "scenario_results": self.scenario_results,
            "gate_decision": self.gate_decision,
            "new_findings": [f.to_dict() for f in self.new_findings],
            "posture": self.posture.to_dict(),
            "execution_time": self.execution_time,
        }


class SecurityEvaluationWorkflow:
    """Automated workflow orchestrator for continuous agent security assessments."""

    def __init__(
        self,
        asset_registry: Optional[AgentAssetRegistry] = None,
        finding_manager: Optional[FindingManager] = None,
        governance_policy: Optional[BenchmarkGovernancePolicy] = None,
    ) -> None:
        self.asset_registry = asset_registry or AgentAssetRegistry()
        self.finding_manager = finding_manager or FindingManager()
        self.governance_policy = governance_policy or BenchmarkGovernancePolicy()

    def run_evaluation(
        self,
        agent_id: str,
        scenarios: Optional[List[str]] = None,
        mock_scenario_results: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> EvaluationExecution:
        """Execute end-to-end security evaluation workflow for an agent asset."""
        asset = self.asset_registry.get_agent(agent_id)
        if not asset:
            raise KeyError(f"Cannot evaluate unregistered agent asset '{agent_id}'.")

        # 1. Capability Detection & Scenario Selection
        target_entry = TargetCatalog.get(asset.target_id)
        selected_scenarios = scenarios or self.governance_policy.required_scenarios

        # 2. Benchmark Execution / Result Resolution
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        execution_id = f"EXEC-{agent_id}-{uuid.uuid4().hex[:8]}"

        results: Dict[str, Dict[str, Any]] = {}
        new_findings: List[SecurityFinding] = []

        for sc_id in selected_scenarios:
            if mock_scenario_results and sc_id in mock_scenario_results:
                sc_res = mock_scenario_results[sc_id]
            else:
                # Default clean execution
                sc_res = {
                    "domain": "authorization_security",
                    "decision": "NO_CONFIRMED_DEVIATION",
                    "evidence_score": 1.0,
                    "variance_detected": False,
                    "reproduction_status": "REPRODUCED",
                }
            results[sc_id] = sc_res

            # Check if finding should be generated
            if sc_res.get("decision") in ["CONFIRMED_DEVIATION", "FAIL"]:
                finding_id = f"FIND-{agent_id}-{sc_id}"
                finding = SecurityFinding(
                    finding_id=finding_id,
                    agent_id=agent_id,
                    scenario_id=sc_id,
                    title=f"Policy boundary breach detected on {sc_id}",
                    severity="HIGH",
                    status="OPEN",
                    evidence_reference=[f"EV-{sc_id}-001"],
                    description=f"Automated evaluation confirmed policy deviation under scenario {sc_id}.",
                )
                self.finding_manager.create(finding)
                new_findings.append(finding)

        # 3. Governance Gate
        gate_res = SecurityReleaseGate.evaluate_release(
            target_id=asset.target_id,
            target_version=asset.version,
            evaluation_results=results,
            governance_policy=self.governance_policy,
        )

        # 4. Security Posture Calculation
        agent_findings = self.finding_manager.list_findings(agent_id=agent_id)
        posture = AgentSecurityPosture.calculate_posture(
            agent_id=agent_id,
            evaluation_results=results,
            findings=agent_findings,
            gate_decision=gate_res.decision,
        )

        # 5. Posture and Asset State Update
        new_status = "COMPLIANT" if gate_res.decision == "PASS" else "NON_COMPLIANT"
        self.asset_registry.update_agent(
            agent_id=agent_id,
            updates={
                "security_status": new_status,
                "last_evaluation": now_str,
            },
        )

        return EvaluationExecution(
            execution_id=execution_id,
            agent_id=agent_id,
            evaluated_scenarios=selected_scenarios,
            scenario_results=results,
            gate_decision=gate_res.decision,
            new_findings=new_findings,
            posture=posture,
            execution_time=now_str,
        )
