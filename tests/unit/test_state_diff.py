"""Unit tests for StateSnapshot, StateDiff, and delta computation (PRD v4.0.2 §8.2 & §12.2)."""

from __future__ import annotations

import inspect
import pytest

from src.openagentsec.adapters.observation import (
    ObservationResult,
    ObservationStatus,
)
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.state import (
    ChangeStatus,
    InvalidStateDimensionError,
    StateDimension,
    StateSnapshot,
    compute_state_diff,
)


def _obs(status: ObservationStatus, value=None) -> ObservationResult:
    if status == ObservationStatus.NOT_OBSERVABLE:
        obs_state = ObservabilityState.UNOBSERVABLE
    elif status == ObservationStatus.PARTIAL:
        obs_state = ObservabilityState.PARTIALLY_OBSERVABLE
    else:
        obs_state = ObservabilityState.OBSERVABLE
    return ObservationResult(
        observability=obs_state,
        status=status,
        value=value,
        source="unit_test",
    )


def test_state_core_contains_no_langgraph_dependency():
    """Verify State core modules do not import LangGraph or target frameworks."""
    import src.openagentsec.state.diff as diff_mod
    import src.openagentsec.state.enums as enums_mod
    import src.openagentsec.state.snapshot as snap_mod

    for mod in (diff_mod, enums_mod, snap_mod):
        src = inspect.getsource(mod)
        assert "langgraph" not in src.lower()
        assert "langchain" not in src.lower()


def test_ten_statutory_dimensions_supported():
    """A. Verify all 10 statutory dimensions from PRD §8.2 are accepted."""
    dims = {
        StateDimension.IDENTITY: _obs(ObservationStatus.OBSERVED, {"user": "alice"}),
        StateDimension.GOAL: _obs(ObservationStatus.OBSERVED, "process_order"),
        StateDimension.TRUST: _obs(ObservationStatus.OBSERVED, True),
        StateDimension.CONTEXT: _obs(ObservationStatus.OBSERVED, ["msg1"]),
        StateDimension.RESOURCE: _obs(ObservationStatus.OBSERVED, ["doc1"]),
        StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["tool1"]),
        StateDimension.MEMORY: _obs(ObservationStatus.OBSERVED, {"k": "v"}),
        StateDimension.APPROVAL: _obs(ObservationStatus.EMPTY),
        StateDimension.CONTROL: _obs(ObservationStatus.OBSERVED, "running"),
        StateDimension.ENVIRONMENT: _obs(ObservationStatus.OBSERVED, "sandbox"),
    }

    snap = StateSnapshot(snapshot_id="SNAP-001", run_id="RUN-001", dimensions=dims)
    assert len(snap.dimensions) == 10
    for d in StateDimension:
        assert snap.has_dimension(d) is True
        assert snap.get_dimension(d) is not None


def test_unknown_state_dimension_rejected():
    """B. Unknown dimension key is rejected."""
    with pytest.raises(InvalidStateDimensionError):
        StateSnapshot(
            snapshot_id="SNAP-001",
            run_id="RUN-001",
            dimensions={"unknown_dim": _obs(ObservationStatus.OBSERVED, "data")},  # type: ignore
        )


def test_observation_statuses_preserved_without_defaults():
    """C, D, E, F, G, H. Preserves EMPTY, NOT_OBSERVABLE, PARTIAL, ERROR, missing != EMPTY."""
    dims = {
        StateDimension.TOOL: _obs(ObservationStatus.EMPTY),
        StateDimension.MEMORY: _obs(ObservationStatus.NOT_OBSERVABLE, None),
        StateDimension.IDENTITY: _obs(ObservationStatus.PARTIAL, {"intent_user": "bob"}),
        StateDimension.CONTROL: _obs(ObservationStatus.ERROR, None),
    }

    snap = StateSnapshot(snapshot_id="SNAP-002", run_id="RUN-001", dimensions=dims)

    assert snap.get_dimension(StateDimension.TOOL).status == ObservationStatus.EMPTY
    assert snap.get_dimension(StateDimension.MEMORY).status == ObservationStatus.NOT_OBSERVABLE
    assert snap.get_dimension(StateDimension.IDENTITY).status == ObservationStatus.PARTIAL
    assert snap.get_dimension(StateDimension.CONTROL).status == ObservationStatus.ERROR

    # missing != EMPTY
    assert snap.has_dimension(StateDimension.GOAL) is False
    assert snap.get_dimension(StateDimension.GOAL) is None


def test_state_diff_observed_same_yields_unchanged():
    """A. OBSERVED X -> OBSERVED X = UNCHANGED."""
    snap1 = StateSnapshot("S1", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["t1"])})
    snap2 = StateSnapshot("S2", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["t1"])})

    diff = compute_state_diff(snap1, snap2)
    assert diff.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.UNCHANGED
    assert StateDimension.TOOL not in diff.changed_dimensions


def test_state_diff_observed_different_yields_changed():
    """B. OBSERVED X -> OBSERVED Y = CHANGED."""
    snap1 = StateSnapshot("S1", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["t1"])})
    snap2 = StateSnapshot("S2", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["t1", "t2"])})

    diff = compute_state_diff(snap1, snap2)
    assert diff.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.CHANGED
    assert StateDimension.TOOL in diff.changed_dimensions


def test_state_diff_empty_and_observed_transitions():
    """C, D. EMPTY -> OBSERVED = CHANGED; OBSERVED -> EMPTY = CHANGED."""
    snap_empty = StateSnapshot("S1", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.EMPTY)})
    snap_obs = StateSnapshot("S2", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["t1"])})

    diff1 = compute_state_diff(snap_empty, snap_obs)
    assert diff1.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.CHANGED
    assert StateDimension.TOOL in diff1.changed_dimensions

    diff2 = compute_state_diff(snap_obs, snap_empty)
    assert diff2.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.CHANGED
    assert StateDimension.TOOL in diff2.changed_dimensions


def test_state_diff_partial_observation_transitions_all_yield_indeterminate():
    """4. Test complete PARTIAL observation transitions (A-E) all yield INDETERMINATE."""
    snap_partial = StateSnapshot("S1", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.PARTIAL, ["intent_t1"])})
    snap_partial_same = StateSnapshot("S2", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.PARTIAL, ["intent_t1"])})
    snap_obs = StateSnapshot("S3", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["exec_t1"])})
    snap_empty = StateSnapshot("S4", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.EMPTY)})

    # A. PARTIAL -> OBSERVED = INDETERMINATE
    diff_a = compute_state_diff(snap_partial, snap_obs)
    assert diff_a.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.INDETERMINATE
    assert "partial" in diff_a.dimension_deltas[StateDimension.TOOL].reason.lower()

    # B. OBSERVED -> PARTIAL = INDETERMINATE
    diff_b = compute_state_diff(snap_obs, snap_partial)
    assert diff_b.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.INDETERMINATE

    # C. PARTIAL -> PARTIAL = INDETERMINATE (even with identical payload, partial facts cannot confirm full equality)
    diff_c = compute_state_diff(snap_partial, snap_partial_same)
    assert diff_c.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.INDETERMINATE

    # D. PARTIAL -> EMPTY = INDETERMINATE
    diff_d = compute_state_diff(snap_partial, snap_empty)
    assert diff_d.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.INDETERMINATE

    # E. EMPTY -> PARTIAL = INDETERMINATE
    diff_e = compute_state_diff(snap_empty, snap_partial)
    assert diff_e.dimension_deltas[StateDimension.TOOL].change_status == ChangeStatus.INDETERMINATE


def test_state_diff_not_observable_yields_indeterminate():
    """E, F. NOT_OBSERVABLE on either side -> INDETERMINATE."""
    snap_not_obs = StateSnapshot("S1", "R1", dimensions={StateDimension.MEMORY: _obs(ObservationStatus.NOT_OBSERVABLE, None)})
    snap_obs = StateSnapshot("S2", "R1", dimensions={StateDimension.MEMORY: _obs(ObservationStatus.OBSERVED, {"k": "v"})})

    diff1 = compute_state_diff(snap_not_obs, snap_obs)
    assert diff1.dimension_deltas[StateDimension.MEMORY].change_status == ChangeStatus.INDETERMINATE
    assert StateDimension.MEMORY in diff1.indeterminate_dimensions

    diff2 = compute_state_diff(snap_obs, snap_not_obs)
    assert diff2.dimension_deltas[StateDimension.MEMORY].change_status == ChangeStatus.INDETERMINATE
    assert StateDimension.MEMORY in diff2.indeterminate_dimensions


def test_state_diff_error_yields_indeterminate():
    """G. ERROR on either side -> INDETERMINATE."""
    snap_err = StateSnapshot("S1", "R1", dimensions={StateDimension.CONTROL: _obs(ObservationStatus.ERROR, None)})
    snap_obs = StateSnapshot("S2", "R1", dimensions={StateDimension.CONTROL: _obs(ObservationStatus.OBSERVED, "active")})

    diff = compute_state_diff(snap_err, snap_obs)
    assert diff.dimension_deltas[StateDimension.CONTROL].change_status == ChangeStatus.INDETERMINATE


def test_state_diff_missing_yields_indeterminate():
    """H. Missing dimension on either side -> INDETERMINATE."""
    snap1 = StateSnapshot("S1", "R1", dimensions={})  # GOAL is missing
    snap2 = StateSnapshot("S2", "R1", dimensions={StateDimension.GOAL: _obs(ObservationStatus.OBSERVED, "goal1")})

    diff = compute_state_diff(snap1, snap2)
    assert diff.dimension_deltas[StateDimension.GOAL].change_status == ChangeStatus.INDETERMINATE
    assert StateDimension.GOAL in diff.indeterminate_dimensions
    assert "missing" in diff.dimension_deltas[StateDimension.GOAL].reason.lower()


def test_state_diff_does_not_perform_policy_evaluation():
    """I. StateDiff only outputs changed facts and does NOT contain policy/deviation judgments."""
    snap1 = StateSnapshot("S1", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.EMPTY)})
    snap2 = StateSnapshot("S2", "R1", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["export_internal_docs"])})

    diff = compute_state_diff(snap1, snap2)
    diff_dict = diff.to_dict()

    assert "deviation" not in diff_dict
    assert "severity" not in diff_dict
    assert "policy" not in diff_dict
    assert "verdict" not in diff_dict
    assert diff.changed_dimensions == ["tool"]
