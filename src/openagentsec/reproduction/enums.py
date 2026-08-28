"""Reproduction enumerations for OpenAgentSec PRD v4.0.2 Phase 4A."""

from __future__ import annotations

from enum import Enum


class ReproductionStatus(str, Enum):
    """Statutory status for repeated evaluation runs against a fixed baseline.

    PRD v4.0.2 Phase 4A:
    - REPEAT_OBSERVED: Completed runs < 5 (cannot declare formal reproduction).
    - REPRODUCED: Completed runs >= 5 with 100% identical Oracle decision outcome.
    - INCONCLUSIVE: Variance detected among runs, baseline drift, or reset failure.
    """
    REPEAT_OBSERVED = "REPEAT_OBSERVED"
    REPRODUCED = "REPRODUCED"
    INCONCLUSIVE = "INCONCLUSIVE"
