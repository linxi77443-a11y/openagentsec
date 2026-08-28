"""Tests for Phase 7.5.5 Public API Stability and JSON Contract.

Validates that all public OpenAgentSec benchmark classes, interfaces, and registries
maintain stable signatures, field contracts, and lossless JSON serialization.
"""

from __future__ import annotations

import json
from typing import Any, Dict
import pytest

from src.openagentsec.benchmark import (
    BenchmarkRegistry,
    BenchmarkScenario,
    BenchmarkSuite,
    EvidenceContractMatrix,
    MetricRegistry,
    ScenarioRegistry,
    TargetCatalog,
    TargetCatalogEntry,
)
from targets.api.target_adapter import TargetMessage, TargetResponse
from tests.integration.external_targets.langchain.adapter import BlackboxTargetAdapter


# ==============================================================================
# Case 1: TargetCatalog & TargetProfile API Contract
# ==============================================================================

def test_api_case1_target_catalog_contract() -> None:
    """Case 1: Validate TargetCatalogEntry fields and serialization."""
    targets = TargetCatalog.list_all()
    assert len(targets) >= 7

    for t in targets:
        d = t.to_dict()
        assert "target_id" in d
        assert "target_name" in d
        assert "architecture_tier" in d
        assert "capabilities" in d
        assert "observability_state" in d
        assert "supported_evidence_types" in d
        # Ensure json serializable
        json_str = json.dumps(d)
        assert len(json_str) > 0


# ==============================================================================
# Case 2: ScenarioRegistry API Contract
# ==============================================================================

def test_api_case2_scenario_registry_contract() -> None:
    """Case 2: Validate BenchmarkScenario schema and serialization."""
    scenarios = ScenarioRegistry.list_all()
    assert len(scenarios) >= 8

    for s in scenarios:
        d = s.to_dict()
        assert "scenario_id" in d
        assert "domain" in d
        assert "title" in d
        assert "attack_type" in d
        assert "required_capabilities" in d
        assert "oracle_rule" in d
        assert "reproduction_requirement" in d
        assert json.dumps(d)


# ==============================================================================
# Case 3: MetricRegistry API Contract
# ==============================================================================

def test_api_case3_metric_registry_contract() -> None:
    """Case 3: Validate BenchmarkMetric schema and serialization."""
    metrics = MetricRegistry.list_all()
    assert len(metrics) >= 9

    for m in metrics:
        d = m.to_dict()
        assert "metric_id" in d
        assert "domain" in d
        assert "name" in d
        assert "formula" in d
        assert "unit" in d
        assert json.dumps(d)


# ==============================================================================
# Case 4: EvidenceContractMatrix API Contract
# ==============================================================================

def test_api_case4_evidence_contract_matrix() -> None:
    """Case 4: Validate EvidenceContractMatrix requirements schema."""
    reqs = EvidenceContractMatrix.get_all_requirements()
    assert len(reqs) >= 7

    for k, req in reqs.items():
        d = req.to_dict()
        assert d["evidence_type"] == k
        assert "is_mandatory" in d
        assert "source" in d
        assert "description" in d
        assert json.dumps(d)


# ==============================================================================
# Case 5: BenchmarkSuite v1.0.0 Export Stability
# ==============================================================================

def test_api_case5_benchmark_suite_export_stability() -> None:
    """Case 5: Validate full BenchmarkSuite v1.0.0 serialization contract."""
    suite = BenchmarkRegistry.create_canonical_suite()
    d = suite.to_dict()

    assert d["benchmark_id"] == "OpenAgentSec-Agent-Security-Benchmark"
    assert d["version"] == "1.0.0"
    assert len(d["domains"]) == 5
    assert len(d["scenarios"]) >= 8
    assert len(d["metrics"]) >= 9
    assert len(d["targets"]) >= 7
    assert len(d["evidence_matrix"]) >= 7

    # Lossless round-trip test
    json_bytes = json.dumps(d).encode("utf-8")
    parsed = json.loads(json_bytes.decode("utf-8"))
    assert parsed["benchmark_id"] == d["benchmark_id"]
    assert len(parsed["scenarios"]) == len(d["scenarios"])
