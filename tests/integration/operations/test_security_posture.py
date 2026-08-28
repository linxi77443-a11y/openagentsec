"""Integration tests for Security Posture Calculation (Phase 11.3)."""

from __future__ import annotations

from typing import Any, Dict
import pytest

from src.openagentsec.operations import AgentSecurityPosture, SecurityFinding


def test_case1_clean_agent_posture_low_risk() -> None:
    """Case 1: Agent with all passed scenarios and 0 findings has LOW risk and 1.0 compliance."""
    eval_results = {
        "SC-01": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0},
        "SC-02": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0},
    }

    posture = AgentSecurityPosture.calculate_posture(
        agent_id="AGENT-CLEAN-01",
        evaluation_results=eval_results,
        findings=[],
        gate_decision="PASS",
    )

    assert posture.risk_level == "LOW"
    assert posture.compliance_score == 1.0
    assert posture.evidence_score == 1.0
    assert posture.open_findings_count == 0
    assert posture.latest_result == "PASS"


def test_case2_critical_vulnerability_yields_critical_posture() -> None:
    """Case 2: Open CRITICAL finding triggers CRITICAL risk level."""
    eval_results = {
        "SC-01": {"decision": "CONFIRMED_DEVIATION", "evidence_score": 1.0},
    }
    findings = [
        SecurityFinding(
            finding_id="FIND-01",
            agent_id="AGENT-VULN-01",
            scenario_id="SC-01",
            title="Critical Data Leak",
            severity="CRITICAL",
            status="OPEN",
        )
    ]

    posture = AgentSecurityPosture.calculate_posture(
        agent_id="AGENT-VULN-01",
        evaluation_results=eval_results,
        findings=findings,
        gate_decision="FAIL",
    )

    assert posture.risk_level == "CRITICAL"
    assert posture.compliance_score == 0.0
    assert posture.open_findings_count == 1
    assert posture.latest_result == "FAIL"


def test_case3_resolved_finding_restores_low_risk() -> None:
    """Case 3: When finding is FIXED, risk level returns to LOW."""
    findings = [
        SecurityFinding(
            finding_id="FIND-01",
            agent_id="AGENT-REMEDIATED-01",
            scenario_id="SC-01",
            title="Resolved Auth Bug",
            severity="HIGH",
            status="FIXED",
        )
    ]

    posture = AgentSecurityPosture.calculate_posture(
        agent_id="AGENT-REMEDIATED-01",
        evaluation_results={"SC-01": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0}},
        findings=findings,
        gate_decision="PASS",
    )

    assert posture.risk_level == "LOW"
    assert posture.open_findings_count == 0
    assert posture.finding_count == 1
