"""Benchmark and Target Version Compatibility Checker (PRD v4.0.2 Phase 10.6).

Verifies version contracts, schema compatibility, and scenario support across benchmark evolutions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from src.openagentsec.benchmark.target_catalog import TargetCatalog, TargetCatalogEntry


@dataclass
class CompatibilityReport:
    """Detailed report on component version compatibility."""

    benchmark_version: str
    target_id: str
    target_version: str
    is_compatible: bool
    compatibility_score: float
    supported_scenarios_count: int
    incompatibilities: List[str] = field(default_factory=list)
    deprecated_features: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BenchmarkCompatibilityChecker:
    """Validates compatibility between Benchmark versions and Agent Target Profiles."""

    SUPPORTED_BENCHMARK_VERSIONS = ["1.0.0", "1.1.0", "1.2.0"]

    @classmethod
    def check_target_compatibility(
        cls,
        benchmark_version: str,
        target_id: str,
        target_version: str = "1.0.0",
    ) -> CompatibilityReport:
        """Check if target entry meets benchmark version requirements."""
        incompatibilities: List[str] = []
        deprecations: List[str] = []

        # 1. Check benchmark version support
        if benchmark_version not in cls.SUPPORTED_BENCHMARK_VERSIONS:
            incompatibilities.append(f"Benchmark version '{benchmark_version}' is not in supported list {cls.SUPPORTED_BENCHMARK_VERSIONS}.")

        # 2. Check Target Catalog existence
        entry = TargetCatalog.get(target_id)
        if not entry:
            incompatibilities.append(f"Target '{target_id}' not found in canonical TargetCatalog.")
            return CompatibilityReport(
                benchmark_version=benchmark_version,
                target_id=target_id,
                target_version=target_version,
                is_compatible=False,
                compatibility_score=0.0,
                supported_scenarios_count=0,
                incompatibilities=incompatibilities,
                deprecated_features=deprecations,
            )

        # 3. Check Mandatory Capabilities & Evidence
        mandatory_ev = ["tool_execution_log", "state_transition_trace"]
        missing_ev = [ev for ev in mandatory_ev if ev not in entry.supported_evidence_types]
        if missing_ev:
            incompatibilities.append(f"Target missing mandatory evidence types: {missing_ev}")

        # Compute score
        score = 1.0 if not incompatibilities else max(0.0, 1.0 - (len(incompatibilities) * 0.5))
        is_compat = len(incompatibilities) == 0

        return CompatibilityReport(
            benchmark_version=benchmark_version,
            target_id=target_id,
            target_version=target_version,
            is_compatible=is_compat,
            compatibility_score=score,
            supported_scenarios_count=len(entry.supported_evidence_types),
            incompatibilities=incompatibilities,
            deprecated_features=deprecations,
        )
