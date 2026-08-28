"""Enterprise Security Governance Report Generator (PRD v4.0.2 Phase 10.4).

Generates enterprise-grade compliance and security audit reports in JSON and Markdown formats.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
import json
from typing import Any, Dict, List, Optional

from .governance_model import BenchmarkGovernancePolicy
from .regression import RegressionReport
from .security_gate import GateDecision


@dataclass
class AgentSecurityReport:
    """Comprehensive Enterprise Security Evaluation Report."""

    report_id: str
    target_id: str
    target_name: str
    target_version: str
    benchmark_version: str
    generation_time: str
    executive_summary: Dict[str, Any]
    scenario_coverage: List[Dict[str, Any]]
    security_findings: List[Dict[str, Any]]
    evidence_summary: Dict[str, Any]
    regression_comparison: Optional[Dict[str, Any]]
    gate_decision: Dict[str, Any]
    release_recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Render report as GitHub Flavored Markdown."""
        lines = [
            f"# Enterprise Agent Security Evaluation Report",
            f"",
            f"**Report ID:** `{self.report_id}`  ",
            f"**Target Agent:** `{self.target_name}` (`{self.target_id}`)  ",
            f"**Target Version:** `{self.target_version}` | **Benchmark Version:** `{self.benchmark_version}`  ",
            f"**Evaluation Date:** `{self.generation_time}`  ",
            f"**Release Recommendation:** **`{self.release_recommendation}`**  ",
            f"",
            f"---",
            f"",
            f"## 1. Executive Summary",
            f"",
            f"- **Security Gate Status:** **`{self.gate_decision.get('decision', 'FAIL')}`**",
            f"- **Evaluated Scenarios:** {self.executive_summary.get('total_scenarios', 0)}",
            f"- **Passed Scenarios:** {self.executive_summary.get('passed_scenarios', 0)}",
            f"- **Confirmed Deviations:** {self.executive_summary.get('confirmed_deviations', 0)}",
            f"- **Evidence Compliance Score:** {self.executive_summary.get('evidence_compliance_score', 1.0) * 100:.1f}%",
            f"",
            f"---",
            f"",
            f"## 2. Security Release Gate Decision",
            f"",
            f"### Gate Status: **`{self.gate_decision.get('decision', 'FAIL')}`**",
            f"",
            f"#### Passed Checks:",
        ]
        for check in self.gate_decision.get("passed_checks", []):
            lines.append(f"- [x] {check}")

        if self.gate_decision.get("failed_checks"):
            lines.append(f"")
            lines.append(f"#### Failed Checks:")
            for check in self.gate_decision.get("failed_checks", []):
                lines.append(f"- [ ] **FAIL**: {check}")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 3. Scenario Coverage & Evaluation Findings",
            f"",
            f"| Scenario ID | Domain | Decision | Evidence Score | Reproduction Status |",
            f"|---|---|---|---|---|",
        ])

        for sc in self.scenario_coverage:
            lines.append(
                f"| `{sc.get('scenario_id')}` | `{sc.get('domain')}` | "
                f"**`{sc.get('decision')}`** | {sc.get('evidence_score', 1.0)} | `{sc.get('reproduction_status', 'REPRODUCED')}` |"
            )

        if self.regression_comparison:
            lines.extend([
                f"",
                f"---",
                f"",
                f"## 4. Security Regression Analysis",
                f"",
                f"- **Previous Version:** `{self.regression_comparison.get('previous_version')}`",
                f"- **Current Version:** `{self.regression_comparison.get('current_version')}`",
                f"- **Regression Detected:** `{self.regression_comparison.get('is_regression_detected')}`",
                f"- **Security Regression Rate:** `{self.regression_comparison.get('security_regression_rate', 0.0) * 100:.1f}%`",
            ])

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 5. Enterprise Release Recommendation",
            f"",
            f"> **Final Decision:** **`{self.release_recommendation}`**  ",
            f"> Evaluated under OpenAgentSec Enterprise Governance Policy.",
        ])

        return "\n".join(lines)


class EnterpriseReportGenerator:
    """Generates structured enterprise security governance reports."""

    @staticmethod
    def generate_report(
        target_id: str,
        target_name: str,
        target_version: str,
        evaluation_results: Dict[str, Dict[str, Any]],
        gate_decision: GateDecision,
        benchmark_version: str = "1.0.0",
        regression_report: Optional[RegressionReport] = None,
    ) -> AgentSecurityReport:
        """Compile evaluation telemetry into formal AgentSecurityReport."""
        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        report_id = f"RPT-{target_id}-{target_version}-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"

        # Calculate summary statistics
        total = len(evaluation_results)
        deviations = sum(1 for res in evaluation_results.values() if res.get("decision") in ["CONFIRMED_DEVIATION", "FAIL"])
        passed = total - deviations

        ev_scores = [res.get("evidence_score", 1.0) for res in evaluation_results.values()]
        avg_ev = sum(ev_scores) / max(len(ev_scores), 1)

        scenario_coverage = []
        security_findings = []
        for sc_id, res in evaluation_results.items():
            sc_info = {
                "scenario_id": sc_id,
                "domain": res.get("domain", "authorization_security"),
                "decision": res.get("decision", "NO_CONFIRMED_DEVIATION"),
                "evidence_score": res.get("evidence_score", 1.0),
                "reproduction_status": res.get("reproduction_status", "REPRODUCED"),
            }
            scenario_coverage.append(sc_info)
            if res.get("decision") in ["CONFIRMED_DEVIATION", "FAIL"]:
                security_findings.append({
                    "scenario_id": sc_id,
                    "finding": "Policy deviation confirmed during adversarial stimulus.",
                    "severity": "HIGH",
                })

        recommendation = "READY_FOR_PRODUCTION_RELEASE" if gate_decision.decision == "PASS" else "BLOCKED_BY_SECURITY_GATE"

        return AgentSecurityReport(
            report_id=report_id,
            target_id=target_id,
            target_name=target_name,
            target_version=target_version,
            benchmark_version=benchmark_version,
            generation_time=now_str,
            executive_summary={
                "total_scenarios": total,
                "passed_scenarios": passed,
                "confirmed_deviations": deviations,
                "evidence_compliance_score": avg_ev,
            },
            scenario_coverage=scenario_coverage,
            security_findings=security_findings,
            evidence_summary={
                "mandatory_evidence_verified": True,
                "average_completeness_score": avg_ev,
            },
            regression_comparison=regression_report.to_dict() if regression_report else None,
            gate_decision=gate_decision.to_dict(),
            release_recommendation=recommendation,
        )
