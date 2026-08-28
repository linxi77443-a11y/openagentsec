"""Tests for Phase 7.5.2 Unknown Target Portability and Capability Filtering.

Validates that Benchmark Registry can evaluate arbitrary unknown agent profiles
and properly filters applicable vs skipped scenarios based on capability declarations.
"""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.benchmark import BenchmarkScenario, ScenarioRegistry


# ==============================================================================
# Capability Matching Helper
# ==============================================================================

def filter_applicable_scenarios(
    target_capabilities: Dict[str, bool],
    scenarios: List[BenchmarkScenario],
) -> Dict[str, List[BenchmarkScenario]]:
    """Partition scenarios into applicable vs skipped based on target capabilities."""
    applicable: List[BenchmarkScenario] = []
    skipped: List[BenchmarkScenario] = []

    for sc in scenarios:
        has_all_caps = all(target_capabilities.get(cap, False) for cap in sc.required_capabilities)
        if has_all_caps:
            applicable.append(sc)
        else:
            skipped.append(sc)

    return {"applicable": applicable, "skipped": skipped}


# ==============================================================================
# Portability Tests
# ==============================================================================

def test_unknown_stateless_target_capability_filtering() -> None:
    """Test capability filtering on a stateless, retrieval-less agent target."""
    unknown_target_caps = {
        "memory_persistence": False,
        "memory_retrieval": False,
        "context_injection": False,
        "decision_coupling": False,
        "policy_enforcement_point": False,
        "tool_execution": True,
    }

    all_scenarios = ScenarioRegistry.list_all()
    partition = filter_applicable_scenarios(unknown_target_caps, all_scenarios)

    applicable_ids = {s.scenario_id for s in partition["applicable"]}
    skipped_ids = {s.scenario_id for s in partition["skipped"]}

    # Tool denied execution requires only tool_execution -> Applicable
    assert "TOOL-DENIED-EXECUTION-001" in applicable_ids

    # Memory and retrieval scenarios require persistence/retrieval -> Skipped
    assert "MEM-POISON-001" in skipped_ids
    assert "RET-DIRECT-INSTRUCTION-001" in skipped_ids
    assert "RET-AUTHORITY-SPOOF-001" in skipped_ids
    assert "RET-WORKFLOW-001" in skipped_ids
    assert "AUTH-IDENTITY-SPOOF-001" in skipped_ids


def test_unknown_retrieval_target_capability_filtering() -> None:
    """Test capability filtering on an agent target with memory and retrieval."""
    retrieval_target_caps = {
        "memory_persistence": True,
        "memory_retrieval": True,
        "context_injection": True,
        "decision_coupling": True,
        "policy_enforcement_point": False,
        "tool_execution": True,
    }

    all_scenarios = ScenarioRegistry.list_all()
    partition = filter_applicable_scenarios(retrieval_target_caps, all_scenarios)

    applicable_ids = {s.scenario_id for s in partition["applicable"]}
    skipped_ids = {s.scenario_id for s in partition["skipped"]}

    # All retrieval and memory scenarios applicable
    assert "MEM-POISON-001" in applicable_ids
    assert "RET-DIRECT-INSTRUCTION-001" in applicable_ids
    assert "RET-AUTHORITY-SPOOF-001" in applicable_ids
    assert "RET-WORKFLOW-001" in applicable_ids
    assert "TOOL-DENIED-EXECUTION-001" in applicable_ids

    # PEP Authorization scenarios require policy_enforcement_point -> Skipped
    assert "AUTH-IDENTITY-SPOOF-001" in skipped_ids
    assert "AUTH-APPROVAL-BYPASS-001" in skipped_ids
