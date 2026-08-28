"""Unit tests for Trajectory, TrajectoryStep, and TrajectoryValidator (PRD v4.0.2 §12.1)."""

from __future__ import annotations

import inspect
import pytest

from src.openagentsec.adapters.observation import (
    ObservationResult,
    ObservationStatus,
)
from src.openagentsec.models.enums import ObservabilityState
from src.openagentsec.state import (
    StateDimension,
    StateSnapshot,
    compute_state_diff,
)
from src.openagentsec.trajectory import (
    Trajectory,
    TrajectoryStep,
    TrajectoryValidationError,
    TrajectoryValidator,
)


def _obs(status: ObservationStatus, value=None) -> ObservationResult:
    obs_state = ObservabilityState.OBSERVABLE if status != ObservationStatus.NOT_OBSERVABLE else ObservabilityState.UNOBSERVABLE
    return ObservationResult(
        observability=obs_state,
        status=status,
        value=value,
        source="unit_test",
    )


def test_trajectory_core_contains_no_langgraph_dependency():
    """Verify Trajectory core modules do not import LangGraph or target frameworks."""
    import src.openagentsec.trajectory.models as mod_mod
    import src.openagentsec.trajectory.step as step_mod
    import src.openagentsec.trajectory.validation as val_mod

    for mod in (mod_mod, step_mod, val_mod):
        src = inspect.getsource(mod)
        assert "langgraph" not in src.lower()
        assert "langchain" not in src.lower()


def test_valid_ordered_trajectory_with_unpopulated_optional_refs():
    """A, B, C, D, E, F. Fabricated stimulus_ref, model_response_ref, and oracle_signal_refs are not required."""
    step1 = TrajectoryStep(
        run_id="RUN-001",
        step_id="STEP-001",
        stimulus_ref=None,
        model_response_ref=None,
        tool_trace_ref=None,
        runtime_decision_ref=None,
        state_before_ref="SNAP-001",
        state_after_ref="SNAP-002",
        state_diff_ref="DIFF-001",
        oracle_signal_refs=[],  # Clean: no synthetic oracle signal IDs
        evidence_refs=["EV-001"],
    )
    step2 = TrajectoryStep(
        run_id="RUN-001",
        step_id="STEP-002",
        stimulus_ref=None,
        model_response_ref=None,
        tool_trace_ref="call_export_01",
        runtime_decision_ref=None,
        state_before_ref="SNAP-002",
        state_after_ref="SNAP-003",
        state_diff_ref="DIFF-002",
        oracle_signal_refs=[],
        evidence_refs=["EV-002"],
    )

    traj = Trajectory(
        trajectory_id="TRAJ-001",
        run_id="RUN-001",
        objective_id="OBJ-001",
        target_id="TARGET-001",
        steps=[step1, step2],
    )

    assert traj.trajectory_id == "TRAJ-001"
    assert len(traj.steps) == 2
    assert traj.steps[0].step_id == "STEP-001"
    assert traj.steps[1].step_id == "STEP-002"

    snap1 = StateSnapshot("SNAP-001", "RUN-001", dimensions={StateDimension.TOOL: _obs(ObservationStatus.EMPTY)})
    snap2 = StateSnapshot("SNAP-002", "RUN-001", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["t1"])})
    snap3 = StateSnapshot("SNAP-003", "RUN-001", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["t1", "t2"])})
    diff1 = compute_state_diff(snap1, snap2, diff_id="DIFF-001", evidence_refs=["EV-001"])
    diff2 = compute_state_diff(snap2, snap3, diff_id="DIFF-002", evidence_refs=["EV-002"])

    snapshots_map = {"SNAP-001": snap1, "SNAP-002": snap2, "SNAP-003": snap3}
    diffs_map = {"DIFF-001": diff1, "DIFF-002": diff2}
    evidence_map = {"EV-001": object(), "EV-002": object()}
    tool_call_ids = {"call_export_01"}

    TrajectoryValidator.validate(
        traj,
        snapshots=snapshots_map,
        diffs=diffs_map,
        evidence_items=evidence_map,
        tool_call_ids=tool_call_ids,
    )


def test_step_ordering_preserved_without_lexicographic_sorting():
    """8. Step ordering preserves input execution sequence without lexicographic sorting."""
    step2 = TrajectoryStep(run_id="RUN-001", step_id="STEP-2")
    step10 = TrajectoryStep(run_id="RUN-001", step_id="STEP-10")

    traj = Trajectory(
        trajectory_id="TRAJ-001",
        run_id="RUN-001",
        objective_id="OBJ-001",
        target_id="TARGET-001",
        steps=[step2, step10],
    )

    # Order must remain [STEP-2, STEP-10], not reordered lexicographically
    assert traj.steps[0].step_id == "STEP-2"
    assert traj.steps[1].step_id == "STEP-10"
    TrajectoryValidator.validate(traj)


def test_duplicate_step_id_rejected():
    """B. Duplicate step_id in same trajectory is rejected."""
    step1 = TrajectoryStep(run_id="RUN-001", step_id="STEP-001")
    step2 = TrajectoryStep(run_id="RUN-001", step_id="STEP-001")

    traj = Trajectory(
        trajectory_id="TRAJ-001",
        run_id="RUN-001",
        objective_id="OBJ-001",
        target_id="TARGET-001",
        steps=[step1, step2],
    )

    with pytest.raises(TrajectoryValidationError, match="Duplicate step_id"):
        TrajectoryValidator.validate(traj)


def test_cross_run_step_rejected():
    """C. Step with mismatched run_id is rejected at construction."""
    step_wrong_run = TrajectoryStep(run_id="RUN-999", step_id="STEP-001")

    with pytest.raises(ValueError, match="does not match trajectory run_id"):
        Trajectory(
            trajectory_id="TRAJ-001",
            run_id="RUN-001",
            objective_id="OBJ-001",
            target_id="TARGET-001",
            steps=[step_wrong_run],
        )


def test_reference_integrity_with_context():
    """G. Reference integrity validation detects dangling snapshot/diff/evidence refs."""
    snap1 = StateSnapshot("SNAP-001", "RUN-001", dimensions={StateDimension.TOOL: _obs(ObservationStatus.EMPTY)})
    snap2 = StateSnapshot("SNAP-002", "RUN-001", dimensions={StateDimension.TOOL: _obs(ObservationStatus.OBSERVED, ["t1"])})
    diff1 = compute_state_diff(snap1, snap2, diff_id="DIFF-001", evidence_refs=["EV-001"])

    step = TrajectoryStep(
        run_id="RUN-001",
        step_id="STEP-001",
        state_before_ref="SNAP-001",
        state_after_ref="SNAP-002",
        state_diff_ref="DIFF-001",
        evidence_refs=["EV-001"],
    )
    traj = Trajectory("TRAJ-001", "RUN-001", "OBJ-001", "TARGET-001", steps=[step])

    snapshots_map = {"SNAP-001": snap1, "SNAP-002": snap2}
    diffs_map = {"DIFF-001": diff1}
    evidence_map = {"EV-001": object()}

    # All references present -> passes
    TrajectoryValidator.validate(traj, snapshots=snapshots_map, diffs=diffs_map, evidence_items=evidence_map)

    # Missing state_before_ref -> raises
    with pytest.raises(TrajectoryValidationError, match="unknown state_before_ref"):
        TrajectoryValidator.validate(traj, snapshots={"SNAP-002": snap2}, diffs=diffs_map, evidence_items=evidence_map)

    # Missing state_diff_ref -> raises
    with pytest.raises(TrajectoryValidationError, match="unknown state_diff_ref"):
        TrajectoryValidator.validate(traj, snapshots=snapshots_map, diffs={}, evidence_items=evidence_map)

    # Missing evidence_ref in step -> raises
    with pytest.raises(TrajectoryValidationError, match="unknown evidence_ref"):
        TrajectoryValidator.validate(traj, snapshots=snapshots_map, diffs=diffs_map, evidence_items={})

    # Dangling evidence_ref inside StateDiff -> raises
    diff_dangling_ev = compute_state_diff(snap1, snap2, diff_id="DIFF-002", evidence_refs=["EV-DANGLING"])
    step_dangling = TrajectoryStep(
        run_id="RUN-001",
        step_id="STEP-002",
        state_diff_ref="DIFF-002",
        evidence_refs=["EV-001"],
    )
    traj_dangling_diff_ev = Trajectory("TRAJ-002", "RUN-001", "OBJ-001", "TARGET-001", steps=[step_dangling])
    with pytest.raises(TrajectoryValidationError, match="references unknown evidence_ref 'EV-DANGLING'"):
        TrajectoryValidator.validate(
            traj_dangling_diff_ev,
            snapshots=snapshots_map,
            diffs={"DIFF-002": diff_dangling_ev},
            evidence_items=evidence_map,
        )


def test_tool_trace_ref_validation():
    """H. tool_trace_ref is validated against tool_call_ids when provided."""
    step = TrajectoryStep(
        run_id="RUN-001",
        step_id="STEP-001",
        tool_trace_ref="call_export_01",
    )
    traj = Trajectory("TRAJ-001", "RUN-001", "OBJ-001", "TARGET-001", steps=[step])

    # Valid tool_call_ids -> passes
    TrajectoryValidator.validate(traj, tool_call_ids={"call_export_01", "call_query_01"})

    # Unknown tool_trace_ref -> raises
    with pytest.raises(TrajectoryValidationError, match="unknown tool_trace_ref 'call_export_01'"):
        TrajectoryValidator.validate(traj, tool_call_ids={"call_other_01"})


def test_structural_no_cot_nested_and_prose_protection():
    """9. Nested structural CoT keys are caught, while normal prose mentioning CoT is not falsely rejected."""
    # 1. Structural assert: no top-level CoT fields
    step = TrajectoryStep(run_id="RUN-001", step_id="STEP-001")
    assert "chain_of_thought" not in step.to_dict()

    # 2. Nested dictionary with CoT key is caught
    step_nested_cot = TrajectoryStep(
        run_id="RUN-001",
        step_id="STEP-001",
        metadata={"debug": {"nested_section": {"chain_of_thought": "hidden thoughts"}}},
    )
    traj_nested = Trajectory("TRAJ-001", "RUN-001", "OBJ-001", "TARGET-001", steps=[step_nested_cot])
    with pytest.raises(TrajectoryValidationError, match="Forbidden structural reasoning key 'chain_of_thought'"):
        TrajectoryValidator.validate(traj_nested)

    # 3. Normal prose mentioning "chain of thought" in text content is NOT falsely rejected
    step_prose = TrajectoryStep(
        run_id="RUN-001",
        step_id="STEP-001",
        metadata={"note": "this system does not expose chain of thought"},
    )
    traj_prose = Trajectory("TRAJ-001", "RUN-001", "OBJ-001", "TARGET-001", steps=[step_prose])
    # Must pass without error
    TrajectoryValidator.validate(traj_prose)
