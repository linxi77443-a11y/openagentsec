"""OpenAgentSec Trajectory domain package (PRD v4.0.2 §12.1)."""

from __future__ import annotations

from .models import Trajectory
from .step import TrajectoryStep
from .validation import TrajectoryValidationError, TrajectoryValidator

__all__ = [
    "Trajectory",
    "TrajectoryStep",
    "TrajectoryValidationError",
    "TrajectoryValidator",
]
