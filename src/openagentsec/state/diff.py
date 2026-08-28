"""Agent Security StateDiff and delta computation engine (PRD v4.0.2 §12.2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional

from ..adapters.observation import ObservationStatus
from .enums import ChangeStatus, StateDimension
from .snapshot import StateSnapshot


@dataclass(frozen=True)
class DimensionDelta:
    """Detailed transition record for a single state dimension."""

    dimension: StateDimension
    before_status: Optional[ObservationStatus]
    after_status: Optional[ObservationStatus]
    change_status: ChangeStatus
    before_value: Any = None
    after_value: Any = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "before_status": self.before_status.value if self.before_status else None,
            "after_status": self.after_status.value if self.after_status else None,
            "change_status": self.change_status.value,
            "before_value": self.before_value,
            "after_value": self.after_value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class StateDiff:
    """Target-agnostic state transition diff object (PRD v4.0.2 §12.2)."""

    diff_id: str
    before_ref: str
    after_ref: str
    dimension_deltas: Dict[StateDimension, DimensionDelta] = field(default_factory=dict)
    changed_dimensions: List[StateDimension] = field(default_factory=list)
    indeterminate_dimensions: List[StateDimension] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diff_id": self.diff_id,
            "before_ref": self.before_ref,
            "after_ref": self.after_ref,
            "dimension_deltas": {
                dim.value: delta.to_dict()
                for dim, delta in self.dimension_deltas.items()
            },
            "changed_dimensions": [d.value for d in self.changed_dimensions],
            "indeterminate_dimensions": [d.value for d in self.indeterminate_dimensions],
            "evidence_refs": list(self.evidence_refs),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
        }


def compute_state_diff(
    before: StateSnapshot,
    after: StateSnapshot,
    diff_id: Optional[str] = None,
    evidence_refs: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> StateDiff:
    """Compute deterministic delta between two StateSnapshots without policy judgment."""
    if not isinstance(before, StateSnapshot):
        raise ValueError("before must be a StateSnapshot instance")
    if not isinstance(after, StateSnapshot):
        raise ValueError("after must be a StateSnapshot instance")

    if not diff_id:
        seed = f"{before.snapshot_id}->{after.snapshot_id}"
        h = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
        diff_id = f"DIFF-{before.snapshot_id}-{after.snapshot_id}-{h}"

    dimension_deltas: Dict[StateDimension, DimensionDelta] = {}
    changed_dimensions: List[StateDimension] = []
    indeterminate_dimensions: List[StateDimension] = []

    # Evaluate across all statutory dimensions in strict precedence order
    for dim in StateDimension:
        before_obs = before.get_dimension(dim)
        after_obs = after.get_dimension(dim)

        before_status = before_obs.status if before_obs else None
        after_status = after_obs.status if after_obs else None
        before_val = before_obs.value if before_obs else None
        after_val = after_obs.value if after_obs else None

        # Precedence 1: Missing on either side -> INDETERMINATE
        if before_obs is None or after_obs is None:
            delta = DimensionDelta(
                dimension=dim,
                before_status=before_status,
                after_status=after_status,
                change_status=ChangeStatus.INDETERMINATE,
                before_value=before_val,
                after_value=after_val,
                reason="Dimension missing in before or after snapshot",
            )
            dimension_deltas[dim] = delta
            indeterminate_dimensions.append(dim)
            continue

        # Precedence 2: ERROR on either side -> INDETERMINATE
        if before_status == ObservationStatus.ERROR or after_status == ObservationStatus.ERROR:
            delta = DimensionDelta(
                dimension=dim,
                before_status=before_status,
                after_status=after_status,
                change_status=ChangeStatus.INDETERMINATE,
                before_value=before_val,
                after_value=after_val,
                reason="Observation pipeline error on state dimension",
            )
            dimension_deltas[dim] = delta
            indeterminate_dimensions.append(dim)
            continue

        # Precedence 3: NOT_OBSERVABLE on either side -> INDETERMINATE
        if before_status == ObservationStatus.NOT_OBSERVABLE or after_status == ObservationStatus.NOT_OBSERVABLE:
            delta = DimensionDelta(
                dimension=dim,
                before_status=before_status,
                after_status=after_status,
                change_status=ChangeStatus.INDETERMINATE,
                before_value=before_val,
                after_value=after_val,
                reason="Dimension is unobservable (NOT_OBSERVABLE)",
            )
            dimension_deltas[dim] = delta
            indeterminate_dimensions.append(dim)
            continue

        # Precedence 4: PARTIAL on either side -> INDETERMINATE
        if before_status == ObservationStatus.PARTIAL or after_status == ObservationStatus.PARTIAL:
            delta = DimensionDelta(
                dimension=dim,
                before_status=before_status,
                after_status=after_status,
                change_status=ChangeStatus.INDETERMINATE,
                before_value=before_val,
                after_value=after_val,
                reason="Partial observation prevents determinate diff (PARTIAL)",
            )
            dimension_deltas[dim] = delta
            indeterminate_dimensions.append(dim)
            continue

        # Precedence 5: Both EMPTY -> UNCHANGED
        if before_status == ObservationStatus.EMPTY and after_status == ObservationStatus.EMPTY:
            delta = DimensionDelta(
                dimension=dim,
                before_status=before_status,
                after_status=after_status,
                change_status=ChangeStatus.UNCHANGED,
                before_value=before_val,
                after_value=after_val,
                reason="Both states observed empty",
            )
            dimension_deltas[dim] = delta
            continue

        # Precedence 6: EMPTY -> OBSERVED or OBSERVED -> EMPTY -> CHANGED
        if (before_status == ObservationStatus.EMPTY and after_status == ObservationStatus.OBSERVED) or (
            before_status == ObservationStatus.OBSERVED and after_status == ObservationStatus.EMPTY
        ):
            delta = DimensionDelta(
                dimension=dim,
                before_status=before_status,
                after_status=after_status,
                change_status=ChangeStatus.CHANGED,
                before_value=before_val,
                after_value=after_val,
                reason=f"Status transitioned between {before_status.value} and {after_status.value}",
            )
            dimension_deltas[dim] = delta
            changed_dimensions.append(dim)
            continue

        # Precedence 7: Both OBSERVED -> compare actual values
        if before_val == after_val:
            delta = DimensionDelta(
                dimension=dim,
                before_status=before_status,
                after_status=after_status,
                change_status=ChangeStatus.UNCHANGED,
                before_value=before_val,
                after_value=after_val,
                reason="Observed value unchanged",
            )
        else:
            delta = DimensionDelta(
                dimension=dim,
                before_status=before_status,
                after_status=after_status,
                change_status=ChangeStatus.CHANGED,
                before_value=before_val,
                after_value=after_val,
                reason="Observed value changed",
            )
            changed_dimensions.append(dim)

        dimension_deltas[dim] = delta

    return StateDiff(
        diff_id=diff_id,
        before_ref=before.snapshot_id,
        after_ref=after.snapshot_id,
        dimension_deltas=dimension_deltas,
        changed_dimensions=changed_dimensions,
        indeterminate_dimensions=indeterminate_dimensions,
        evidence_refs=list(evidence_refs or []),
        metadata=dict(metadata or {}),
    )
