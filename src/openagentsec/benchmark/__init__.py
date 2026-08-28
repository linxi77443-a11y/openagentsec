"""OpenAgentSec Benchmark Framework (PRD v4.0.2 Phase 7.4.1).

Provides consolidated benchmark registries, scenario catalogs, metric definitions, target catalogs,
and evidence contracts for standardized AI agent security evaluations.
"""

from .benchmark_registry import BenchmarkRegistry, BenchmarkSuite
from .evidence_contract import EvidenceContractMatrix, EvidenceRequirement
from .metric_registry import BenchmarkMetric, MetricRegistry
from .scenario_registry import BenchmarkScenario, ScenarioRegistry
from .target_catalog import TargetCatalog, TargetCatalogEntry

__all__ = [
    "BenchmarkSuite",
    "BenchmarkRegistry",
    "BenchmarkScenario",
    "ScenarioRegistry",
    "BenchmarkMetric",
    "MetricRegistry",
    "TargetCatalogEntry",
    "TargetCatalog",
    "EvidenceRequirement",
    "EvidenceContractMatrix",
]
