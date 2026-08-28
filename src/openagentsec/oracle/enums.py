"""Oracle decision enumerations for OpenAgentSec Governance and Evaluation Plane."""

from __future__ import annotations

from enum import Enum


class OracleDecision(str, Enum):
    """Statutory decisions produced by independent Oracle evaluators.

    PRD v4.0.2 Phase 3A:
    - CONFIRMED_DEVIATION: Deterministic, verified evidence confirms policy invariant violation.
    - NO_CONFIRMED_DEVIATION: Observable evidence confirms no violation of evaluated invariant.
    - INCONCLUSIVE: Required evidence is unobservable, missing, in error, or limited to intent-only.
    """
    CONFIRMED_DEVIATION = "CONFIRMED_DEVIATION"
    NO_CONFIRMED_DEVIATION = "NO_CONFIRMED_DEVIATION"
    INCONCLUSIVE = "INCONCLUSIVE"
