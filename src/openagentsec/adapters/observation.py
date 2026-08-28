"""ObservationResult and ObservationStatus for OpenAgentSec TargetAdapter.

PRD v4.0.2 §7.3 & §7.4:
Provides unambiguous observability semantics distinguishing:
- OBSERVED (state/events actively observed)
- EMPTY (observation channel active, confirmed zero events)
- NOT_OBSERVABLE (dimension cannot be observed, value MUST be None)
- PARTIAL (partial observation, e.g. client intent without verified execution)
- ERROR (observation pipeline error, fail-closed)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from ..models.enums import ObservabilityState
from ..models.exceptions import OpenAgentSecModelError

T = TypeVar("T")


class ObservationStatus(str, Enum):
    """Observation status enumeration."""
    OBSERVED = "OBSERVED"
    EMPTY = "EMPTY"
    NOT_OBSERVABLE = "NOT_OBSERVABLE"
    PARTIAL = "PARTIAL"
    ERROR = "ERROR"


class ObservationSemanticError(OpenAgentSecModelError):
    """Raised when ObservationResult receives conflicting or invalid combinations."""
    pass


@dataclass(frozen=True)
class ObservationResult(Generic[T]):
    """Structured observation result with strict semantic validation."""

    observability: ObservabilityState
    status: ObservationStatus
    value: Optional[T] = None
    source: str = "adapter"
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        # Validate observability type
        if not isinstance(self.observability, ObservabilityState):
            if isinstance(self.observability, str):
                try:
                    object.__setattr__(self, "observability", ObservabilityState(self.observability))
                except ValueError:
                    raise ObservationSemanticError(
                        f"Invalid observability '{self.observability}'. "
                        f"Must be one of {[e.value for e in ObservabilityState]}"
                    )
            else:
                raise ObservationSemanticError(
                    f"observability must be an ObservabilityState instance, got {type(self.observability)}"
                )

        # Validate status type
        if not isinstance(self.status, ObservationStatus):
            if isinstance(self.status, str):
                try:
                    object.__setattr__(self, "status", ObservationStatus(self.status))
                except ValueError:
                    raise ObservationSemanticError(
                        f"Invalid status '{self.status}'. "
                        f"Must be one of {[e.value for e in ObservationStatus]}"
                    )
            else:
                raise ObservationSemanticError(
                    f"status must be an ObservationStatus instance, got {type(self.status)}"
                )

        # Rule 1: UNOBSERVABLE must pair with NOT_OBSERVABLE or ERROR, and value MUST be None
        if self.observability == ObservabilityState.UNOBSERVABLE:
            if self.status not in (ObservationStatus.NOT_OBSERVABLE, ObservationStatus.ERROR):
                raise ObservationSemanticError(
                    f"UNOBSERVABLE dimension cannot have status '{self.status.value}'. "
                    f"Must be NOT_OBSERVABLE or ERROR."
                )
            if self.value is not None:
                raise ObservationSemanticError(
                    f"UNOBSERVABLE dimension must have value=None, got {type(self.value).__name__} ({self.value}). "
                    f"Do not return empty collections like [] or {{}} for unobservable states."
                )

        # Rule 2: NOT_OBSERVABLE status cannot pair with OBSERVABLE
        if self.status == ObservationStatus.NOT_OBSERVABLE:
            if self.observability == ObservabilityState.OBSERVABLE:
                raise ObservationSemanticError(
                    "OBSERVABLE dimension cannot have status NOT_OBSERVABLE. Use EMPTY if no events occurred."
                )
            if self.value is not None:
                raise ObservationSemanticError(
                    f"NOT_OBSERVABLE status requires value=None, got {self.value}"
                )

        # Rule 3: EMPTY status requires OBSERVABLE or PARTIALLY_OBSERVABLE
        if self.status == ObservationStatus.EMPTY:
            if self.observability == ObservabilityState.UNOBSERVABLE:
                raise ObservationSemanticError(
                    "UNOBSERVABLE dimension cannot have status EMPTY. Must be NOT_OBSERVABLE."
                )

        # Rule 4: PARTIAL status requires PARTIALLY_OBSERVABLE
        if self.status == ObservationStatus.PARTIAL:
            if self.observability != ObservabilityState.PARTIALLY_OBSERVABLE:
                raise ObservationSemanticError(
                    f"PARTIAL status requires PARTIALLY_OBSERVABLE, got '{self.observability.value}'."
                )

        # Rule 5: PARTIALLY_OBSERVABLE cannot have status OBSERVED (must be PARTIAL, EMPTY, or ERROR)
        if self.observability == ObservabilityState.PARTIALLY_OBSERVABLE:
            if self.status == ObservationStatus.OBSERVED:
                raise ObservationSemanticError(
                    "PARTIALLY_OBSERVABLE dimension cannot claim status 'OBSERVED'. "
                    "Use 'PARTIAL' to reflect partial observation."
                )

        # Rule 6: ERROR status requires value=None
        if self.status == ObservationStatus.ERROR:
            if self.value is not None:
                raise ObservationSemanticError(
                    f"ERROR status requires value=None, got {self.value}. Store error details in 'reason'."
                )

    @property
    def is_observed(self) -> bool:
        """True if any actual data was observed (OBSERVED or PARTIAL)."""
        return self.status in (ObservationStatus.OBSERVED, ObservationStatus.PARTIAL)

    @property
    def is_observable(self) -> bool:
        """True if the target dimension is theoretically observable."""
        return self.observability != ObservabilityState.UNOBSERVABLE

    @property
    def is_empty(self) -> bool:
        """True if the channel is observable and confirmed empty."""
        return self.status == ObservationStatus.EMPTY

    @property
    def is_error(self) -> bool:
        """True if the observation pipeline encountered an error."""
        return self.status == ObservationStatus.ERROR

    def to_dict(self) -> dict[str, Any]:
        """Convert observation result to dictionary."""
        return {
            "observability": self.observability.value,
            "status": self.status.value,
            "value": self.value,
            "source": self.source,
            "reason": self.reason,
        }
