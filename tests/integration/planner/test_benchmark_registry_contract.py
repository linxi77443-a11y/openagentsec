"""Integration tests for Phase 7.4.1 & Phase 8.1 OpenAgentSec Benchmark Registry Contract.

Validates the formal consolidation of the OpenAgentSec Benchmark Framework:
- Case 1: Target Catalog Completeness (All standard targets registered with valid profile metadata).
- Case 2: Scenario Catalog Completeness (All canonical scenarios registered with unique IDs and requirements).
- Case 3: Metric Catalog Completeness (All canonical metrics formalized with formulas, units, and definitions).
- Case 4: Evidence Contract & Completeness Validation (Mandatory types and fail-closed checks).
- Case 5: Canonical Benchmark Suite Schema & Version Stability (Version 1.0.0 serialization contract).
"""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.benchmark import (
    BenchmarkRegistry,
    BenchmarkSuite,
    EvidenceContractMatrix,
    MetricRegistry,
    ScenarioRegistry,
    TargetCatalog,
)
from src.openagentsec.oracle.evidence import EvidenceItem


# ==============================================================================
# Case 1: Target Catalog Completeness
# ==============================================================================

def test_case1_target_catalog_completeness() -> None:
    """Case 1: Validate that all standard Target architectures are registered in TargetCatalog."""
    targets = TargetCatalog.list_all()
    assert len(targets) >= 7

    target_ids = {t.target_id for t in targets}
    expected_ids = {
        "TARGET-LANGGRAPH-MVP1",
        "TARGET-LANGGRAPH-RETRIEVAL-COUPLED",
        "TARGET-LANGGRAPH-AUTH-WHITEBOX",
        "TARGET-LANGGRAPH-PARAM-WHITEBOX",
        "TARGET-LANGCHAIN-REAL-AGENT",
        "TARGET-MCP-GATEWAY-BOUNDARY",
        "TARGET-COMMERCIAL-LLM-AGENT",
        "TARGET-MULTI-AGENT-COORDINATOR-EXECUTOR",
        "TARGET-MULTI-AGENT-TRUST-NETWORK",
    }
    assert expected_ids.issubset(target_ids)

    for t in targets:
        assert t.target_name != ""
        assert t.architecture_tier != ""
        assert t.observability_state in ["observable", "partially_observable", "unobservable"]
        assert t.adapter_type != ""
        assert len(t.supported_evidence_types) > 0


# ==============================================================================
# Case 2: Scenario Catalog Completeness
# ==============================================================================

def test_case2_scenario_catalog_completeness() -> None:
    """Case 2: Validate that all canonical Scenarios are registered across security domains."""
    scenarios = ScenarioRegistry.list_all()
    assert len(scenarios) >= 8

    scenario_ids = [s.scenario_id for s in scenarios]
    # Check uniqueness
    assert len(scenario_ids) == len(set(scenario_ids))

    expected_scenarios = {
        "MEM-POISON-001",
        "RET-DIRECT-INSTRUCTION-001",
        "RET-AUTHORITY-SPOOF-001",
        "RET-WORKFLOW-001",
        "AUTH-IDENTITY-SPOOF-001",
        "AUTH-APPROVAL-BYPASS-001",
        "AUTH-PARAMETER-SCOPE-001",
        "TOOL-DENIED-EXECUTION-001",
        "MA-IDENTITY-SPOOF-001",
        "MA-DELEGATION-ESCALATION-001",
        "MA-MESSAGE-TAMPERING-001",
        "MA-TRUST-PROPAGATION-001",
        "MA-CHAIN-PRIVILEGE-ESCALATION-001",
        "MA-CIRCULAR-DELEGATION-001",
        "MA-TRUST-DECAY-001",
    }
    assert expected_scenarios.issubset(set(scenario_ids))

    # Validate domain distribution
    domains = {s.domain for s in scenarios}
    assert "memory_security" in domains
    assert "retrieval_security" in domains
    assert "authorization_security" in domains
    assert "tool_boundary_security" in domains

    for s in scenarios:
        assert s.title != ""
        assert s.attack_type != ""
        assert s.oracle_rule != ""
        assert s.reproduction_requirement == 5
        assert len(s.expected_evidence) > 0
        assert len(s.applicable_targets) > 0


# ==============================================================================
# Case 3: Metric Catalog Completeness
# ==============================================================================

def test_case3_metric_catalog_completeness() -> None:
    """Case 3: Validate that all canonical Metrics are defined with formulas and units."""
    metrics = MetricRegistry.list_all()
    assert len(metrics) >= 9

    metric_ids = {m.metric_id for m in metrics}
    expected_metrics = {
        "memory_taint_rate",
        "memory_retrieved",
        "taint_to_action_lag",
        "subsequent_deviation_rate",
        "authorization_bypass_rate",
        "parameter_violation_block_rate",
        "actual_execution_rate",
        "reproduction_rate",
        "variance_detected",
        "trust_violation_rate",
        "delegation_chain_depth",
        "privilege_amplification_detected",
        "trust_decay_block_rate",
        "judge_false_positive_rate",
        "evaluation_variance_rate",
        "adapter_portability_score",
        "false_confirm_reduction_rate",
        "security_regression_rate",
        "benchmark_gate_pass_rate",
        "evidence_compliance_score",
        "version_compatibility_score",
        "registered_agent_count",
        "evaluation_execution_success_rate",
        "open_security_finding_rate",
        "security_posture_score",
        "attack_mutation_count",
        "discovery_success_rate",
        "mutation_reproduction_rate",
        "scenario_expansion_ratio",
    }
    assert expected_metrics.issubset(metric_ids)

    for m in metrics:
        assert m.name != ""
        assert m.definition != ""
        assert m.formula != ""
        assert m.unit in ["ratio", "count", "steps", "boolean"]
        assert len(m.applicable_targets) > 0


# ==============================================================================
# Case 4: Evidence Contract & Completeness Scoring
# ==============================================================================

def test_case4_evidence_contract_and_completeness_validation() -> None:
    """Case 4: Validate Evidence Contract Matrix, completeness scoring, and fail-closed behavior."""
    reqs = EvidenceContractMatrix.get_all_requirements()
    assert len(reqs) >= 7

    mandatory_types = EvidenceContractMatrix.get_mandatory_types()
    assert "tool_execution_log" in mandatory_types
    assert "state_transition_trace" in mandatory_types

    # 1. Complete evidence set -> Score 1.0, is_valid True
    complete_ev = [
        EvidenceItem(evidence_id="EV-1", evidence_type="tool_execution_log", source="runtime", content=[], verified=True),
        EvidenceItem(evidence_id="EV-2", evidence_type="state_transition_trace", source="runtime", content={}, verified=True),
    ]
    res_complete = EvidenceContractMatrix.validate_evidence_contract(
        complete_ev, required_types=["tool_execution_log", "state_transition_trace"]
    )
    assert res_complete["is_valid"] is True
    assert res_complete["completeness_score"] == 1.0
    assert res_complete["fail_closed_triggered"] is False

    # 2. Incomplete evidence set -> Score 0.5, is_valid False (fail-closed triggered)
    incomplete_ev = [
        EvidenceItem(evidence_id="EV-1", evidence_type="tool_execution_log", source="runtime", content=[], verified=True),
    ]
    res_incomplete = EvidenceContractMatrix.validate_evidence_contract(
        incomplete_ev, required_types=["tool_execution_log", "state_transition_trace"]
    )
    assert res_incomplete["is_valid"] is False
    assert res_incomplete["completeness_score"] == 0.5
    assert "state_transition_trace" in res_incomplete["missing_types"]
    assert res_incomplete["fail_closed_triggered"] is True


# ==============================================================================
# Case 5: Canonical Benchmark Suite Schema & Version Stability
# ==============================================================================

def test_case5_canonical_benchmark_suite_schema_and_version() -> None:
    """Case 5: Validate that canonical BenchmarkSuite v1.0.0 builds and serializes cleanly."""
    suite = BenchmarkRegistry.create_canonical_suite()

    assert suite.benchmark_id == "OpenAgentSec-Agent-Security-Benchmark"
    assert suite.version == "1.0.0"
    assert len(suite.domains) == 5
    assert len(suite.scenarios) >= 8
    assert len(suite.metrics) >= 9
    assert len(suite.targets) >= 7
    assert len(suite.evidence_matrix) >= 7

    # Export dictionary contract
    suite_dict = suite.to_dict()
    assert suite_dict["benchmark_id"] == "OpenAgentSec-Agent-Security-Benchmark"
    assert suite_dict["version"] == "1.0.0"
    assert suite_dict["metadata"]["statutory_reproduction_runs"] == 5
    assert suite_dict["metadata"]["fail_closed_enabled"] is True
    assert suite_dict["metadata"]["zero_variance_required"] is True

    # Validate json serializability
    import json
    json_str = json.dumps(suite_dict)
    assert len(json_str) > 1000
