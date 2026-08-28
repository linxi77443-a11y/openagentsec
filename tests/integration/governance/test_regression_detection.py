"""Integration tests for Agent Security Regression Detection (Phase 10.2)."""

from __future__ import annotations

from typing import Any, Dict
import pytest

from src.openagentsec.governance import AgentSecurityRegressionRunner


def test_case1_new_vulnerability_regression_detected() -> None:
    """Case 1: Regression from NO_CONFIRMED_DEVIATION to CONFIRMED_DEVIATION is flagged as CRITICAL."""
    prev_results = {
        "AUTH-IDENTITY-SPOOF-001": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0},
        "TOOL-DENIED-EXECUTION-001": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0},
    }
    curr_results = {
        "AUTH-IDENTITY-SPOOF-001": {"decision": "CONFIRMED_DEVIATION", "evidence_score": 1.0},  # Regressed!
        "TOOL-DENIED-EXECUTION-001": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0},
    }

    report = AgentSecurityRegressionRunner.compare_evaluations(
        target_id="TARGET-LANGGRAPH-AUTH-WHITEBOX",
        previous_version="1.0.0",
        current_version="1.1.0",
        previous_results=prev_results,
        current_results=curr_results,
    )

    assert report.is_regression_detected is True
    assert report.security_regression_rate == 0.5
    assert len(report.regressed_scenarios) == 1
    assert report.regressed_scenarios[0]["scenario_id"] == "AUTH-IDENTITY-SPOOF-001"
    assert report.regressed_scenarios[0]["severity"] == "CRITICAL"


def test_case2_vulnerability_fix_detected_as_improvement() -> None:
    """Case 2: Improvement from CONFIRMED_DEVIATION to NO_CONFIRMED_DEVIATION is flagged as improvement."""
    prev_results = {
        "AUTH-APPROVAL-BYPASS-001": {"decision": "CONFIRMED_DEVIATION", "evidence_score": 1.0},
    }
    curr_results = {
        "AUTH-APPROVAL-BYPASS-001": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0},
    }

    report = AgentSecurityRegressionRunner.compare_evaluations(
        target_id="TARGET-LANGGRAPH-AUTH-WHITEBOX",
        previous_version="1.0.0",
        current_version="1.1.0",
        previous_results=prev_results,
        current_results=curr_results,
    )

    assert report.is_regression_detected is False
    assert len(report.improved_scenarios) == 1
    assert report.improved_scenarios[0]["scenario_id"] == "AUTH-APPROVAL-BYPASS-001"


def test_case3_evidence_completeness_drop_flagged_as_regression() -> None:
    """Case 3: Drop in evidence completeness score is flagged as HIGH regression."""
    prev_results = {
        "MEM-POISON-001": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0},
    }
    curr_results = {
        "MEM-POISON-001": {"decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 0.4},  # Evidence degraded
    }

    report = AgentSecurityRegressionRunner.compare_evaluations(
        target_id="TARGET-LANGGRAPH-RETRIEVAL-COUPLED",
        previous_version="1.0.0",
        current_version="1.1.0",
        previous_results=prev_results,
        current_results=curr_results,
    )

    assert report.is_regression_detected is True
    assert len(report.regressed_scenarios) == 1
    assert report.regressed_scenarios[0]["regression_type"] == "evidence_completeness_decay"
    assert report.regressed_scenarios[0]["severity"] == "HIGH"
