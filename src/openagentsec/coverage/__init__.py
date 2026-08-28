"""OpenAgentSec Coverage Governance package (PRD v4.0.2 §4)."""

from __future__ import annotations

from .enums import (
    GOVERNANCE_BRANCH_STATUSES,
    MAINLINE_COVERAGE_RANKS,
    MAINLINE_COVERAGE_STATUSES,
    CoverageStatus,
)
from .planner import CoveragePlanner
from .record import (
    CoverageRecord,
    CoverageTransition,
    compute_coverage_id,
)
from .tracker import CoverageTracker, ExecutionReadiness

__all__ = [
    "CoverageStatus",
    "MAINLINE_COVERAGE_STATUSES",
    "MAINLINE_COVERAGE_RANKS",
    "GOVERNANCE_BRANCH_STATUSES",
    "CoverageRecord",
    "CoverageTransition",
    "compute_coverage_id",
    "ExecutionReadiness",
    "CoverageTracker",
    "CoveragePlanner",
]
