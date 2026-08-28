"""Trajectory validation and reference integrity engine (PRD v4.0.2 §12.1)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from ..state.diff import StateDiff
from ..state.snapshot import StateSnapshot
from .models import Trajectory
from .step import TrajectoryStep


class TrajectoryValidationError(ValueError):
    """Raised when trajectory structure or reference integrity is violated."""
    pass


class TrajectoryValidator:
    """Validator for Trajectory ordering, unique step IDs, reference integrity, and No-CoT policy."""

    FORBIDDEN_COT_KEYS = frozenset({
        "chain_of_thought",
        "hidden_reasoning",
        "reasoning_tokens",
        "internal_thought",
        "cot",
    })

    @classmethod
    def _check_nested_forbidden_keys(cls, obj: Any, step_id: str, path: str = "") -> None:
        """Recursively inspect structural dictionary keys for reserved CoT field names."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                cur_path = f"{path}.{k}" if path else str(k)
                if str(k).lower() in cls.FORBIDDEN_COT_KEYS:
                    raise TrajectoryValidationError(
                        f"Forbidden structural reasoning key '{k}' found at '{cur_path}' in step '{step_id}'. "
                        "PRD v4.0.2 strictly forbids recording internal chain-of-thought tokens."
                    )
                cls._check_nested_forbidden_keys(v, step_id, cur_path)
        elif isinstance(obj, (list, tuple, set)):
            for idx, item in enumerate(obj):
                cls._check_nested_forbidden_keys(item, step_id, f"{path}[{idx}]")

    @classmethod
    def validate(
        cls,
        trajectory: Trajectory,
        snapshots: Optional[Dict[str, StateSnapshot]] = None,
        diffs: Optional[Dict[str, StateDiff]] = None,
        evidence_items: Optional[Dict[str, Any]] = None,
        tool_call_ids: Optional[Set[str]] = None,
    ) -> List[str]:
        """Validate a Trajectory. Raises TrajectoryValidationError on failure.
        
        Returns a list of informational validation warnings if any.
        """
        if not isinstance(trajectory, Trajectory):
            raise TrajectoryValidationError(f"Expected Trajectory instance, got {type(trajectory)}")

        seen_step_ids: Set[str] = set()
        warnings: List[str] = []

        for idx, step in enumerate(trajectory.steps):
            if not isinstance(step, TrajectoryStep):
                raise TrajectoryValidationError(f"Step at index {idx} is not a TrajectoryStep instance")

            # 1. Unique step_id verification
            if step.step_id in seen_step_ids:
                raise TrajectoryValidationError(f"Duplicate step_id '{step.step_id}' found in trajectory")
            seen_step_ids.add(step.step_id)

            # 2. Run ID isolation
            if step.run_id != trajectory.run_id:
                raise TrajectoryValidationError(
                    f"Step '{step.step_id}' run_id '{step.run_id}' does not match trajectory run_id '{trajectory.run_id}'"
                )

            # 3. Structural No-CoT recursive check
            cls._check_nested_forbidden_keys(step.to_dict(), step.step_id)

            # 4. Reference integrity checks (when context is provided)
            if snapshots is not None:
                if step.state_before_ref and step.state_before_ref not in snapshots:
                    raise TrajectoryValidationError(
                        f"Step '{step.step_id}' references unknown state_before_ref '{step.state_before_ref}'"
                    )
                if step.state_after_ref and step.state_after_ref not in snapshots:
                    raise TrajectoryValidationError(
                        f"Step '{step.step_id}' references unknown state_after_ref '{step.state_after_ref}'"
                    )

            if diffs is not None:
                if step.state_diff_ref:
                    if step.state_diff_ref not in diffs:
                        raise TrajectoryValidationError(
                            f"Step '{step.step_id}' references unknown state_diff_ref '{step.state_diff_ref}'"
                        )
                    # Also validate StateDiff's internal evidence_refs if evidence_items context is available
                    if evidence_items is not None:
                        referenced_diff = diffs[step.state_diff_ref]
                        for diff_ev_ref in referenced_diff.evidence_refs:
                            if diff_ev_ref not in evidence_items:
                                raise TrajectoryValidationError(
                                    f"StateDiff '{referenced_diff.diff_id}' referenced by step '{step.step_id}' "
                                    f"references unknown evidence_ref '{diff_ev_ref}'"
                                )

            if evidence_items is not None:
                for ev_ref in step.evidence_refs:
                    if ev_ref not in evidence_items:
                        raise TrajectoryValidationError(
                            f"Step '{step.step_id}' references unknown evidence_ref '{ev_ref}'"
                        )

            if tool_call_ids is not None:
                if step.tool_trace_ref and step.tool_trace_ref not in tool_call_ids:
                    raise TrajectoryValidationError(
                        f"Step '{step.step_id}' references unknown tool_trace_ref '{step.tool_trace_ref}'"
                    )

        return warnings
