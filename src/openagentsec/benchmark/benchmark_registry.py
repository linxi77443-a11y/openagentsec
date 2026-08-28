"""Benchmark Registry and BenchmarkSuite Definition (PRD v4.0.2 Phase 7.4.1).

Aggregates scenarios, metrics, target catalog, and evidence contracts into a versioned Benchmark Suite.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .evidence_contract import EvidenceContractMatrix, EvidenceRequirement
from .metric_registry import BenchmarkMetric, MetricRegistry
from .scenario_registry import BenchmarkScenario, ScenarioRegistry
from .target_catalog import TargetCatalog, TargetCatalogEntry


@dataclass
class BenchmarkSuite:
    """Consolidated, versioned Agent Security Benchmark Suite."""

    benchmark_id: str
    version: str
    name: str
    description: str
    domains: List[str]
    scenarios: List[BenchmarkScenario] = field(default_factory=list)
    metrics: List[BenchmarkMetric] = field(default_factory=list)
    targets: List[TargetCatalogEntry] = field(default_factory=list)
    evidence_matrix: Dict[str, EvidenceRequirement] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "domains": list(self.domains),
            "scenarios": [s.to_dict() for s in self.scenarios],
            "metrics": [m.to_dict() for m in self.metrics],
            "targets": [t.to_dict() for t in self.targets],
            "evidence_matrix": {k: v.to_dict() for k, v in self.evidence_matrix.items()},
            "metadata": dict(self.metadata),
        }


class BenchmarkRegistry:
    """Registry coordinating standard Benchmark Suites."""

    DEFAULT_BENCHMARK_ID = "OpenAgentSec-Agent-Security-Benchmark"
    DEFAULT_VERSION = "1.0.0"

    @classmethod
    def create_canonical_suite(
        cls,
        benchmark_id: Optional[str] = None,
        version: Optional[str] = None,
    ) -> BenchmarkSuite:
        """Construct the canonical OpenAgentSec v1.0.0 benchmark suite."""
        b_id = benchmark_id or cls.DEFAULT_BENCHMARK_ID
        ver = version or cls.DEFAULT_VERSION

        domains = [
            "memory_security",
            "retrieval_security",
            "authorization_security",
            "tool_boundary_security",
            "reproduction_governance",
        ]

        return BenchmarkSuite(
            benchmark_id=b_id,
            version=ver,
            name="OpenAgentSec AI Agent Security Evaluation Benchmark",
            description="Policy-driven, reproduction-validated security evaluation benchmark for autonomous AI agents.",
            domains=domains,
            scenarios=ScenarioRegistry.list_all(),
            metrics=MetricRegistry.list_all(),
            targets=TargetCatalog.list_all(),
            evidence_matrix=EvidenceContractMatrix.get_all_requirements(),
            metadata={
                "statutory_reproduction_runs": 5,
                "fail_closed_enabled": True,
                "zero_variance_required": True,
                "author": "OpenAgentSec Core Team",
            },
        )
