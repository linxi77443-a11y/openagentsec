"""Agent Security State Snapshot contract (PRD v4.0.2 §8.2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from ..adapters.observation import ObservationResult, ObservationStatus
from .enums import StateDimension


class InvalidStateDimensionError(ValueError):
    """Raised when an unknown or invalid state dimension is provided."""
    pass


@dataclass(frozen=True)
class StateSnapshot:
    """Immutable snapshot of Agent Security State across the 10 statutory dimensions."""

    snapshot_id: str
    run_id: str
    step_id: Optional[str] = None
    dimensions: Dict[StateDimension, ObservationResult[Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.snapshot_id or not isinstance(self.snapshot_id, str):
            raise ValueError("snapshot_id must be a non-empty string")
        if not self.run_id or not isinstance(self.run_id, str):
            raise ValueError("run_id must be a non-empty string")

        validated_dims: Dict[StateDimension, ObservationResult[Any]] = {}
        for dim_key, obs in self.dimensions.items():
            if isinstance(dim_key, str):
                try:
                    dim_enum = StateDimension(dim_key)
                except ValueError:
                    raise InvalidStateDimensionError(
                        f"Unknown state dimension '{dim_key}'. Allowed dimensions: {[d.value for d in StateDimension]}"
                    )
            elif isinstance(dim_key, StateDimension):
                dim_enum = dim_key
            else:
                raise InvalidStateDimensionError(f"Invalid state dimension key type: {type(dim_key)}")

            if not isinstance(obs, ObservationResult):
                raise ValueError(
                    f"Dimension '{dim_enum.value}' value must be an ObservationResult, got {type(obs)}"
                )
            validated_dims[dim_enum] = obs

        object.__setattr__(self, "dimensions", validated_dims)

    def get_dimension(self, dim: Union[StateDimension, str]) -> Optional[ObservationResult[Any]]:
        """Get observation result for a dimension. Returns None if missing (not provided)."""
        if isinstance(dim, str):
            try:
                dim = StateDimension(dim)
            except ValueError:
                return None
        return self.dimensions.get(dim)

    def has_dimension(self, dim: Union[StateDimension, str]) -> bool:
        """Check if a dimension is present in the snapshot (missing != EMPTY)."""
        if isinstance(dim, str):
            try:
                dim = StateDimension(dim)
            except ValueError:
                return False
        return dim in self.dimensions

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary representation."""
        return {
            "snapshot_id": self.snapshot_id,
            "run_id": self.run_id,
            "step_id": self.step_id,
            "dimensions": {
                dim.value: {
                    "observability": obs.observability.value,
                    "status": obs.status.value,
                    "value": obs.value,
                    "source": obs.source,
                    "reason": obs.reason,
                }
                for dim, obs in self.dimensions.items()
            },
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }
