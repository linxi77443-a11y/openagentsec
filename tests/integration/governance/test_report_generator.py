"""Integration tests for Enterprise Report Generator (Phase 10.4)."""

from __future__ import annotations

import json
from typing import Any, Dict
import pytest

from src.openagentsec.governance import (
    BenchmarkGovernancePolicy,
    EnterpriseReportGenerator,
    GateDecision,
    SecurityReleaseGate,
)


def test_case1_report_generator_json_and_markdown_completeness() -> None:
    """Case 1: Validate structured enterprise report generation in JSON and Markdown formats."""
    eval_results = {
        "MEM-POISON-001": {"domain": "memory_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "reproduction_status": "REPRODUCED"},
        "AUTH-IDENTITY-SPOOF-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "reproduction_status": "REPRODUCED"},
    }

    policy = BenchmarkGovernancePolicy(
        required_scenarios=["MEM-POISON-001", "AUTH-IDENTITY-SPOOF-001"]
    )

    gate_decision = SecurityReleaseGate.evaluate_release(
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
        target_version="1.0.0",
        evaluation_results=eval_results,
        governance_policy=policy,
    )

    report = EnterpriseReportGenerator.generate_report(
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
        target_name="LangGraphParamWhiteboxAgent",
        target_version="1.0.0",
        evaluation_results=eval_results,
        gate_decision=gate_decision,
        benchmark_version="1.0.0",
    )

    # 1. Check Data Structure
    assert report.report_id.startswith("RPT-")
    assert report.target_id == "TARGET-LANGGRAPH-PARAM-WHITEBOX"
    assert report.release_recommendation == "READY_FOR_PRODUCTION_RELEASE"
    assert report.executive_summary["total_scenarios"] == 2
    assert report.executive_summary["passed_scenarios"] == 2

    # 2. Check JSON Export
    json_str = report.to_json()
    parsed = json.loads(json_str)
    assert parsed["report_id"] == report.report_id
    assert parsed["release_recommendation"] == "READY_FOR_PRODUCTION_RELEASE"

    # 3. Check Markdown Export
    md_str = report.to_markdown()
    assert "# Enterprise Agent Security Evaluation Report" in md_str
    assert "## 1. Executive Summary" in md_str
    assert "## 2. Security Release Gate Decision" in md_str
    assert "## 3. Scenario Coverage & Evaluation Findings" in md_str
    assert "## 5. Enterprise Release Recommendation" in md_str
    assert "READY_FOR_PRODUCTION_RELEASE" in md_str
