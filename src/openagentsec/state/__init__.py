"""OpenAgentSec Agent Security State and StateDiff domain package (PRD v4.0.2 §8.2 & §12.2)."""

from __future__ import annotations

from .diff import DimensionDelta, StateDiff, compute_state_diff
from .enums import ChangeStatus, StateDimension
from .snapshot import InvalidStateDimensionError, StateSnapshot

__all__ = [
    "StateDimension",
    "ChangeStatus",
    "StateSnapshot",
    "InvalidStateDimensionError",
    "DimensionDelta",
    "StateDiff",
    "compute_state_diff",
]
