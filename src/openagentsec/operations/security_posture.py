"""Agent Security Posture Model (PRD v4.0.2 Phase 11.3).

Aggregates vulnerability findings, compliance scores, and evaluation results into a unified security posture.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional

from .finding import SecurityFinding


@dataclass
class AgentSecurityPosture:
    """Consolidated security posture of an AI Agent asset."""

    agent_id: str
    risk_level: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    compliance_score: float  # 0.0 - 1.0
    evidence_score: float  # 0.0 - 1.0
    latest_result: str  # "PASS" | "FAIL" | "INCONCLUSIVE"
    regression_state: str = "NONE"  # "NONE" | "CRITICAL" | "HIGH"
    finding_count: int = 0
    open_findings_count: int = 0
    last_updated: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def calculate_posture(
        cls,
        agent_id: str,
        evaluation_results: Dict[str, Dict[str, Any]],
        findings: List[SecurityFinding],
        gate_decision: str = "PASS",
        regression_state: str = "NONE",
    ) -> AgentSecurityPosture:
        """Derive comprehensive security posture from evaluation telemetry and active findings."""
        total_scenarios = len(evaluation_results)
        deviated = sum(1 for r in evaluation_results.values() if r.get("decision") in ["CONFIRMED_DEVIATION", "FAIL"])
        compliance = (total_scenarios - deviated) / max(total_scenarios, 1)

        ev_scores = [r.get("evidence_score", 1.0) for r in evaluation_results.values()]
        avg_ev = sum(ev_scores) / max(len(ev_scores), 1)

        open_findings = [f for f in findings if f.status in ["OPEN", "ACKNOWLEDGED"]]
        open_count = len(open_findings)

        # Risk level determination
        has_critical = any(f.severity == "CRITICAL" for f in open_findings) or (gate_decision == "FAIL" and deviated > 0)
        has_high = any(f.severity == "HIGH" for f in open_findings)
        has_med = any(f.severity == "MEDIUM" for f in open_findings)

        if has_critical or regression_state == "CRITICAL":
            risk = "CRITICAL"
        elif has_high or regression_state == "HIGH":
            risk = "HIGH"
        elif has_med or open_count > 0:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        return cls(
            agent_id=agent_id,
            risk_level=risk,
            compliance_score=round(compliance, 4),
            evidence_score=round(avg_ev, 4),
            latest_result=gate_decision,
            regression_state=regression_state,
            finding_count=len(findings),
            open_findings_count=open_count,
            last_updated=now_str,
        )
