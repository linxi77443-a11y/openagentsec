"""Integration tests for Enterprise Security Release Gate (Phase 10.3)."""

from __future__ import annotations

from typing import Any, Dict
import pytest

from src.openagentsec.governance import BenchmarkGovernancePolicy, SecurityReleaseGate


def test_case1_secure_agent_passes_release_gate() -> None:
    """Case 1: Fully compliant agent passing all required scenarios, evidence, and zero-variance reproduction."""
    policy = BenchmarkGovernancePolicy()
    eval_results = {
        "MEM-POISON-001": {"domain": "memory_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "RET-DIRECT-INSTRUCTION-001": {"domain": "retrieval_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "AUTH-IDENTITY-SPOOF-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "AUTH-PARAMETER-SCOPE-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "TOOL-DENIED-EXECUTION-001": {"domain": "tool_boundary_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
    }

    gate_dec = SecurityReleaseGate.evaluate_release(
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
        target_version="1.2.0",
        evaluation_results=eval_results,
        governance_policy=policy,
    )

    assert gate_dec.decision == "PASS"
    assert len(gate_dec.failed_checks) == 0
    assert len(gate_dec.passed_checks) == 4


def test_case2_policy_violation_triggers_gate_fail() -> None:
    """Case 2: Confirmed tool boundary deviation triggers release gate FAIL."""
    policy = BenchmarkGovernancePolicy()
    eval_results = {
        "MEM-POISON-001": {"domain": "memory_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "RET-DIRECT-INSTRUCTION-001": {"domain": "retrieval_security", "decision": "CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "AUTH-IDENTITY-SPOOF-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "AUTH-PARAMETER-SCOPE-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "TOOL-DENIED-EXECUTION-001": {"domain": "tool_boundary_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
    }

    gate_dec = SecurityReleaseGate.evaluate_release(
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
        target_version="1.2.1-vulnerable",
        evaluation_results=eval_results,
        governance_policy=policy,
    )

    assert gate_dec.decision == "FAIL"
    assert any("Security policy violations confirmed" in check for check in gate_dec.failed_checks)


def test_case3_incomplete_evidence_triggers_gate_fail() -> None:
    """Case 3: Missing mandatory telemetry / incomplete evidence triggers FAIL."""
    policy = BenchmarkGovernancePolicy()
    eval_results = {
        "MEM-POISON-001": {"domain": "memory_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 0.5, "variance_detected": False},
        "RET-DIRECT-INSTRUCTION-001": {"domain": "retrieval_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "AUTH-IDENTITY-SPOOF-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "AUTH-PARAMETER-SCOPE-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "TOOL-DENIED-EXECUTION-001": {"domain": "tool_boundary_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
    }

    gate_dec = SecurityReleaseGate.evaluate_release(
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
        target_version="1.2.0",
        evaluation_results=eval_results,
        governance_policy=policy,
    )

    assert gate_dec.decision == "FAIL"
    assert any("Evidence completeness below" in check for check in gate_dec.failed_checks)


def test_case4_reproduction_variance_triggers_gate_fail() -> None:
    """Case 4: Non-deterministic stochastic reproduction drift triggers FAIL."""
    policy = BenchmarkGovernancePolicy()
    eval_results = {
        "MEM-POISON-001": {"domain": "memory_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": True},
        "RET-DIRECT-INSTRUCTION-001": {"domain": "retrieval_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "AUTH-IDENTITY-SPOOF-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "AUTH-PARAMETER-SCOPE-001": {"domain": "authorization_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
        "TOOL-DENIED-EXECUTION-001": {"domain": "tool_boundary_security", "decision": "NO_CONFIRMED_DEVIATION", "evidence_score": 1.0, "variance_detected": False},
    }

    gate_dec = SecurityReleaseGate.evaluate_release(
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
        target_version="1.2.0",
        evaluation_results=eval_results,
        governance_policy=policy,
    )

    assert gate_dec.decision == "FAIL"
    assert any("Stochastic variance" in check for check in gate_dec.failed_checks)
