"""Integration tests for Benchmark Version Compatibility (Phase 10.6)."""

from __future__ import annotations

from typing import Any, Dict
import pytest

from src.openagentsec.benchmark import MetricRegistry
from src.openagentsec.governance import BenchmarkCompatibilityChecker


def test_case1_compatible_target_passes_check() -> None:
    """Case 1: Standard target catalog entry is fully compatible with benchmark version 1.0.0."""
    report = BenchmarkCompatibilityChecker.check_target_compatibility(
        benchmark_version="1.0.0",
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
        target_version="1.0.0",
    )

    assert report.is_compatible is True
    assert report.compatibility_score == 1.0
    assert len(report.incompatibilities) == 0


def test_case2_unregistered_target_fails_check() -> None:
    """Case 2: Target not in TargetCatalog is flagged as incompatible."""
    report = BenchmarkCompatibilityChecker.check_target_compatibility(
        benchmark_version="1.0.0",
        target_id="TARGET-UNKNOWN-CUSTOM-XYZ",
        target_version="1.0.0",
    )

    assert report.is_compatible is False
    assert report.compatibility_score == 0.0
    assert any("not found in canonical TargetCatalog" in err for err in report.incompatibilities)


def test_case3_unsupported_benchmark_version_fails_check() -> None:
    """Case 3: Unsupported benchmark version (e.g. 99.0.0) is flagged as incompatible."""
    report = BenchmarkCompatibilityChecker.check_target_compatibility(
        benchmark_version="99.0.0",
        target_id="TARGET-LANGGRAPH-PARAM-WHITEBOX",
        target_version="1.0.0",
    )

    assert report.is_compatible is False
    assert any("not in supported list" in err for err in report.incompatibilities)


def test_case4_governance_metrics_registration() -> None:
    """Case 4: Validate all 4 Phase 10 Enterprise Governance metrics in MetricRegistry."""
    req_metrics = [
        "security_regression_rate",
        "benchmark_gate_pass_rate",
        "evidence_compliance_score",
        "version_compatibility_score",
    ]

    for m_id in req_metrics:
        metric = MetricRegistry.get(m_id)
        assert metric is not None, f"Metric '{m_id}' must be registered in MetricRegistry"
        assert metric.formula != ""
        assert metric.unit == "ratio"
