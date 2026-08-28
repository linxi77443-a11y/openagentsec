"""Integration tests for Adaptive Discovery Pipeline (Phase 12.3)."""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.adaptive import (
    AdaptiveAttackGenerator,
    DiscoveryResult,
    MutationScenario,
    ScenarioDiscoveryEngine,
)
from src.openagentsec.benchmark import MetricRegistry
from tests.integration.planner.test_state_memory_security import _load_fixtures


def test_case1_discovery_pipeline_on_secure_target() -> None:
    """Case 1: Full discovery cycle on secure target yielding NO_CONFIRMED_DEVIATION and 100% evidence."""
    policy, objective, _ = _load_fixtures()
    engine = ScenarioDiscoveryEngine()

    results = engine.run_discovery(
        scenario_id="AUTH-IDENTITY-SPOOF-001",
        target_id="TARGET-LANGGRAPH-AUTH-WHITEBOX",
        policy=policy,
        objective=objective,
        mutation_types=["prompt_mutation"],
        count_per_type=2,
    )

    assert len(results) == 2
    for r in results:
        assert r.parent_scenario_id == "AUTH-IDENTITY-SPOOF-001"
        assert r.oracle_decision == "NO_CONFIRMED_DEVIATION"
        assert r.is_vulnerability_discovered is False
        assert r.evidence_completeness_score == 1.0
        assert r.reproduction_status == "REPRODUCED"
        assert r.attack_trace.is_deviation_confirmed is False
        assert len(r.attack_trace.mutation_steps) >= 2


def test_case2_discovery_pipeline_on_vulnerable_target() -> None:
    """Case 2: Discovery cycle on vulnerable target identifying a confirmed boundary breach."""
    policy, objective, _ = _load_fixtures()
    engine = ScenarioDiscoveryEngine()

    # Mock execution returning unauthorized tool call
    def mock_vuln_exec(mut: MutationScenario) -> Dict[str, Any]:
        return {
            "actual_tools": [
                {
                    "call_id": "call_breach_01",
                    "tool": "export_internal_docs",
                    "name": "export_internal_docs",
                    "arguments": {"target": "exfil"},
                    "result": "success",
                    "verified_runtime_execution": True,
                }
            ],
            "model_response": "Executed sensitive export tool.",
            "state": {"blocked": False},
        }

    results = engine.run_discovery(
        scenario_id="AUTH-IDENTITY-SPOOF-001",
        target_id="TARGET-LANGGRAPH-AUTH-WHITEBOX",
        policy=policy,
        objective=objective,
        mutation_types=["prompt_mutation"],
        mock_execution_fn=mock_vuln_exec,
        count_per_type=1,
    )

    assert len(results) == 1
    r = results[0]
    assert r.oracle_decision == "CONFIRMED_DEVIATION"
    assert r.is_vulnerability_discovered is True
    assert r.reproduction_status == "REPRODUCED"
    assert r.attack_trace.is_deviation_confirmed is True
    assert "INV-TOOL-ALLOWLIST-001" in r.attack_trace.violated_invariants


def test_case3_adaptive_discovery_metrics_registration() -> None:
    """Case 3: Validate that all 4 Phase 12 metrics are registered and valid."""
    req_metrics = [
        "attack_mutation_count",
        "discovery_success_rate",
        "mutation_reproduction_rate",
        "scenario_expansion_ratio",
    ]

    for m_id in req_metrics:
        metric = MetricRegistry.get(m_id)
        assert metric is not None, f"Metric '{m_id}' must be registered in MetricRegistry"
        assert metric.formula != ""
        assert metric.unit in ["count", "ratio"]
