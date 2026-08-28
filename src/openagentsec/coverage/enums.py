"""CoverageStatus and governance lifecycle enums (PRD v4.0.2 §4)."""

from __future__ import annotations

from enum import Enum
from typing import Dict, Set


class CoverageStatus(str, Enum):
    """PRD v4.0.2 §4.3 Statutory Coverage Status."""

    # Mainline maturity progression (linear depth)
    MAPPED_ONLY = "mapped_only"
    OBJECTIVE_DEFINED = "objective_defined"
    SCENARIO_AVAILABLE = "scenario_available"
    EXECUTABLE = "executable"
    EVALUATED = "evaluated"
    REPRODUCED = "reproduced"
    RETEST_VERIFIED = "retest_verified"

    # Governance branch states (non-linear dispositions)
    DESIGN_GATE = "design_gate"
    OUT_OF_SCOPE = "out_of_scope"


MAINLINE_COVERAGE_STATUSES: Set[CoverageStatus] = {
    CoverageStatus.MAPPED_ONLY,
    CoverageStatus.OBJECTIVE_DEFINED,
    CoverageStatus.SCENARIO_AVAILABLE,
    CoverageStatus.EXECUTABLE,
    CoverageStatus.EVALUATED,
    CoverageStatus.REPRODUCED,
    CoverageStatus.RETEST_VERIFIED,
}

MAINLINE_COVERAGE_RANKS: Dict[CoverageStatus, int] = {
    CoverageStatus.MAPPED_ONLY: 1,
    CoverageStatus.OBJECTIVE_DEFINED: 2,
    CoverageStatus.SCENARIO_AVAILABLE: 3,
    CoverageStatus.EXECUTABLE: 4,
    CoverageStatus.EVALUATED: 5,
    CoverageStatus.REPRODUCED: 6,
    CoverageStatus.RETEST_VERIFIED: 7,
}

GOVERNANCE_BRANCH_STATUSES: Set[CoverageStatus] = {
    CoverageStatus.DESIGN_GATE,
    CoverageStatus.OUT_OF_SCOPE,
}
