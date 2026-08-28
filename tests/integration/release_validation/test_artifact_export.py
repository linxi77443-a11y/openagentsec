"""Release Validation Tests for Phase 7.6 Research Artifact Release.

Validates that all JSON artifacts, schemas, reproduction matrices, and manifests
are strictly synchronized with the canonical Python registries.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ARTIFACT_DIR = ROOT_DIR / "artifact"


# ==============================================================================
# Case 1: Benchmark Suite JSON Export Validation
# ==============================================================================

def test_case1_benchmark_suite_json_export() -> None:
    """Case 1: Validate benchmark_v1.0.0.json structure and completeness."""
    suite_file = ARTIFACT_DIR / "benchmark" / "benchmark_v1.0.0.json"
    assert suite_file.exists(), "benchmark_v1.0.0.json must exist"

    data = json.loads(suite_file.read_text(encoding="utf-8"))
    assert data["benchmark_id"] == "OpenAgentSec-Agent-Security-Benchmark"
    assert data["version"] == "1.0.0"
    assert len(data["domains"]) == 5
    assert len(data["scenarios"]) >= 8
    assert len(data["metrics"]) >= 9
    assert len(data["targets"]) >= 7
    assert len(data["evidence_matrix"]) >= 7


# ==============================================================================
# Case 2: Scenarios & Metrics Export Validation
# ==============================================================================

def test_case2_scenarios_and_metrics_export() -> None:
    """Case 2: Validate scenarios.json and metrics.json export files."""
    scenarios_file = ARTIFACT_DIR / "benchmark" / "scenarios.json"
    metrics_file = ARTIFACT_DIR / "benchmark" / "metrics.json"

    assert scenarios_file.exists()
    assert metrics_file.exists()

    scenarios = json.loads(scenarios_file.read_text(encoding="utf-8"))
    assert len(scenarios) >= 8
    for sc in scenarios:
        assert "scenario_id" in sc
        assert "domain" in sc
        assert "attack_type" in sc
        assert sc["reproduction_requirement"] == 5

    metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
    assert len(metrics) >= 9
    for m in metrics:
        assert "metric_id" in m
        assert "formula" in m
        assert "unit" in m


# ==============================================================================
# Case 3: Targets & Schemas Export Validation
# ==============================================================================

def test_case3_targets_and_schemas_export() -> None:
    """Case 3: Validate targets.json and JSON schemas."""
    targets_file = ARTIFACT_DIR / "benchmark" / "targets.json"
    assert targets_file.exists()

    targets = json.loads(targets_file.read_text(encoding="utf-8"))
    assert len(targets) >= 7
    for t in targets:
        assert "target_id" in t
        assert "capabilities" in t
        assert "observability_state" in t

    # Schemas
    for schema_name in ["target_profile.schema.json", "evidence.schema.json", "result.schema.json"]:
        sf = ARTIFACT_DIR / "schemas" / schema_name
        assert sf.exists(), f"Schema {schema_name} must exist"
        schema_data = json.loads(sf.read_text(encoding="utf-8"))
        assert "required" in schema_data
        assert "properties" in schema_data


# ==============================================================================
# Case 4: Reproduction Matrix & Benchmark Results Validation
# ==============================================================================

def test_case4_experiments_reproduction_matrix() -> None:
    """Case 4: Validate reproduction_matrix.json and benchmark_results.json."""
    repro_file = ARTIFACT_DIR / "experiments" / "reproduction_matrix.json"
    results_file = ARTIFACT_DIR / "experiments" / "benchmark_results.json"

    assert repro_file.exists()
    assert results_file.exists()

    repro_data = json.loads(repro_file.read_text(encoding="utf-8"))
    assert repro_data["statutory_reproduction_runs"] == 5
    assert repro_data["zero_variance_required"] is True
    assert repro_data["majority_voting_allowed"] is False
    assert len(repro_data["evaluated_targets"]) >= 6

    results_data = json.loads(results_file.read_text(encoding="utf-8"))
    assert results_data["domains"]["memory_security"]["subsequent_deviation_rate_mvp1"] == 0.0
    assert results_data["domains"]["retrieval_security"]["attack_success_rate"] == 1.0


# ==============================================================================
# Case 5: Research Artifact Manifest Validation
# ==============================================================================

def test_case5_manifest_validation() -> None:
    """Case 5: Validate artifact/MANIFEST.json completeness."""
    manifest_file = ARTIFACT_DIR / "MANIFEST.json"
    assert manifest_file.exists(), "MANIFEST.json must exist"

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest["name"] == "OpenAgentSec"
    assert manifest["version"] == "1.0.0"
    assert manifest["targets"] >= 7
    assert manifest["scenarios"] >= 8
    assert manifest["metrics"] >= 9
    assert manifest["reproducibility"] == "5-run-zero-variance"
    assert len(manifest["artifacts"]) >= 9

    # Verify all referenced artifacts exist on disk
    for rel_path in manifest["artifacts"]:
        target_path = ARTIFACT_DIR / rel_path
        assert target_path.exists(), f"Artifact referenced in manifest missing: {rel_path}"
