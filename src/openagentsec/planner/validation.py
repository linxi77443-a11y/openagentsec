"""Independent validation of model-generated ScenarioPlan candidates (PRD v4.0-B).

Fail closed: any violation raises PlannerRejectedError and must not enter the Executor.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Set

from ..models.evaluation_objective import EvaluationObjective
from ..models.security_policy import SecurityPolicy
from ..models.target_profile import TargetProfile
from .enums import EvaluationOperatorType
from .rule_planner import PlanningInfeasibleError


class PlannerRejectedError(PlanningInfeasibleError):
    """Model-generated plan rejected before execution. Closest existing contract: PlanningInfeasibleError."""


UNSAFE_KEYS = frozenset({
    "tool_call",
    "tool_calls",
    "execute",
    "execution",
    "shell",
    "subprocess",
    "runtime_command",
    "code",
    "os.system",
})

TOOL_PARAM_KEYS = frozenset({
    "tool",
    "target_tool",
    "retrieval_tool",
    "target_denied_action",
})

CONTEXT_PARAM_KEYS = frozenset({
    "context_surface",
})


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _walk_keys(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def _as_tool_set(policy_side: Any) -> Set[str]:
    if hasattr(policy_side, "tools"):
        return set(policy_side.tools)
    if isinstance(policy_side, dict):
        return set(policy_side.get("tools", []))
    return set()


class ScenarioPlanValidator:
    """Validates a raw planner JSON object against policy, objective, and target capability."""

    @classmethod
    def validate(
        cls,
        raw: Dict[str, Any],
        policy: SecurityPolicy,
        objective: EvaluationObjective,
        target: TargetProfile,
    ) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            raise PlannerRejectedError("schema_invalid", "Planner response must be a JSON object")

        for key in _walk_keys(raw):
            if key in UNSAFE_KEYS:
                raise PlannerRejectedError(
                    "unsafe_action",
                    f"Planner response contains forbidden execution key '{key}'",
                )

        operators = raw.get("operators")
        if not isinstance(operators, list) or not operators:
            raise PlannerRejectedError("schema_invalid", "Planner response must include a non-empty operators list")

        if len(operators) > objective.max_steps:
            raise PlannerRejectedError(
                "max_steps_exceeded",
                f"Operator count {len(operators)} exceeds objective.max_steps {objective.max_steps}",
            )

        declared_objective = raw.get("objective_id")
        if declared_objective is not None and declared_objective != objective.objective_id:
            raise PlannerRejectedError(
                "objective_drift",
                f"Planner objective_id '{declared_objective}' does not match '{objective.objective_id}'",
            )

        declared_target = raw.get("target_id")
        if declared_target is not None and declared_target != target.target_id:
            raise PlannerRejectedError(
                "objective_drift",
                f"Planner target_id '{declared_target}' does not match '{target.target_id}'",
            )

        allowed_ops = {op.value for op in EvaluationOperatorType}
        target_tools = set(target.tools)
        rag_sources = set(target.rag_sources)
        permitted_evidence = set(objective.required_evidence) | set(policy.evidence_requirements)

        for index, operator in enumerate(operators):
            if not isinstance(operator, dict):
                raise PlannerRejectedError("schema_invalid", f"Operator at index {index} is not an object")
            op_type = operator.get("operator_type")
            if not isinstance(op_type, str) or op_type not in allowed_ops:
                raise PlannerRejectedError(
                    "unsupported_operator",
                    f"Operator '{op_type}' is not in the EvaluationOperatorType allowlist",
                )
            try:
                EvaluationOperatorType(op_type)
            except ValueError as exc:
                raise PlannerRejectedError("unsupported_operator", str(exc)) from exc

            params = operator.get("parameters", {})
            if params is None:
                params = {}
            if not isinstance(params, dict):
                raise PlannerRejectedError("schema_invalid", f"Operator {op_type} parameters must be an object")

            for key in TOOL_PARAM_KEYS:
                tool_name = params.get(key)
                if tool_name is None:
                    continue
                if not isinstance(tool_name, str) or not tool_name:
                    raise PlannerRejectedError("schema_invalid", f"Parameter '{key}' must be a non-empty string")
                if tool_name not in target_tools:
                    raise PlannerRejectedError(
                        "unsupported_target_capability",
                        f"Tool '{tool_name}' is not declared on target '{target.target_id}'",
                    )

            for key in CONTEXT_PARAM_KEYS:
                surface = params.get(key)
                if surface is None:
                    continue
                if surface not in rag_sources:
                    raise PlannerRejectedError(
                        "unsupported_target_capability",
                        f"Context surface '{surface}' is not declared on target '{target.target_id}'",
                    )

            op_objective = operator.get("objective_id")
            if op_objective is not None and op_objective != objective.objective_id:
                raise PlannerRejectedError(
                    "objective_drift",
                    f"Operator objective_id '{op_objective}' does not match '{objective.objective_id}'",
                )

        requested_evidence = raw.get("required_evidence")
        if requested_evidence is not None:
            if not isinstance(requested_evidence, list):
                raise PlannerRejectedError("schema_invalid", "required_evidence must be a list")
            extra = set(requested_evidence) - permitted_evidence
            if extra:
                raise PlannerRejectedError(
                    "evidence_incompatible",
                    f"Required evidence {sorted(extra)} is not permitted by objective/policy",
                )

        declared_max = raw.get("max_steps")
        if declared_max is not None:
            if not isinstance(declared_max, int) or declared_max < 1:
                raise PlannerRejectedError("schema_invalid", "max_steps must be a positive integer")
            if declared_max > objective.max_steps:
                raise PlannerRejectedError(
                    "max_steps_exceeded",
                    f"Plan max_steps {declared_max} exceeds objective.max_steps {objective.max_steps}",
                )

        return raw
