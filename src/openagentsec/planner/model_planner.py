"""Model-driven Evaluation Planner (PRD v4.0-B).

Produces ScenarioPlan candidates only. Does not execute tools, mutate runtime,
or participate in Oracle judgment.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json

from ..models.enums import PlannerMode
from ..models.evaluation_objective import EvaluationObjective
from ..models.security_policy import SecurityPolicy
from ..models.target_profile import TargetProfile
from .enums import EvaluationOperatorType
from .operator import EvaluationOperator
from .provider import (
    ModelProvider,
    PlannerContext,
    default_allowed_operators,
)
from .rule_planner import UnsupportedPlannerModeError
from .scenario import ScenarioPlan, compute_plan_hash
from .validation import PlannerRejectedError, ScenarioPlanValidator


def _policy_tools(side: Any) -> List[str]:
    if hasattr(side, "tools"):
        return list(side.tools)
    if isinstance(side, dict):
        return list(side.get("tools", []))
    return []


class ModelDrivenPlanner:
    """Planner that asks a ModelProvider how to evaluate, then fail-closes on invalid output."""

    def __init__(self, provider: ModelProvider) -> None:
        if provider is None:
            raise ValueError("ModelDrivenPlanner requires a ModelProvider")
        self._provider = provider

    def _require_mode(self, objective: EvaluationObjective) -> None:
        if objective.planner_mode != PlannerMode.MODEL_DRIVEN:
            raise UnsupportedPlannerModeError(
                f"ModelDrivenPlanner supports only PlannerMode.MODEL_DRIVEN, "
                f"got '{objective.planner_mode.value if isinstance(objective.planner_mode, PlannerMode) else objective.planner_mode}'."
            )

    def build_context(
        self,
        policy: SecurityPolicy,
        objective: EvaluationObjective,
        target: TargetProfile,
    ) -> PlannerContext:
        return PlannerContext(
            objective_id=objective.objective_id,
            evaluation_question=objective.evaluation_question,
            target_behavior=objective.target_behavior,
            undesired_behavior=objective.undesired_behavior,
            policy_id=policy.policy_id,
            policy_refs=sorted(list(objective.policy_refs)),
            risk_refs=sorted(list(objective.risk_refs)),
            allowed_tools=sorted(_policy_tools(policy.allowed)),
            denied_tools=sorted(_policy_tools(policy.denied)),
            target_id=target.target_id,
            target_tools=sorted(list(target.tools)),
            rag_sources=sorted(list(target.rag_sources)),
            runtime_capabilities=sorted(list(target.runtime_capabilities)),
            permitted_stimulus_types=sorted(list(objective.permitted_stimulus_types)),
            required_observations=sorted(list(objective.required_observations)),
            required_evidence=sorted(list(objective.required_evidence)),
            safety_constraints=sorted(list(objective.safety_constraints)),
            stop_conditions=sorted(list(objective.stop_conditions)),
            max_steps=objective.max_steps,
            allowed_operators=default_allowed_operators(),
            evaluation_boundary=[
                "output_scenario_plan_only",
                "no_tool_execution",
                "no_runtime_mutation",
                "no_oracle_judgment",
                "use_allowlisted_operators_only",
            ],
        )

    def plan(
        self,
        policy: SecurityPolicy,
        objective: EvaluationObjective,
        target: TargetProfile,
        config: Optional[Dict[str, Any]] = None,
    ) -> ScenarioPlan:
        self._require_mode(objective)
        context = self.build_context(policy, objective, target)

        try:
            raw_text = self._provider.complete(context)
        except PlannerRejectedError:
            raise
        except Exception as exc:
            raise PlannerRejectedError("provider_failure", f"Model provider failed: {exc}") from exc

        if not isinstance(raw_text, str) or not raw_text.strip():
            raise PlannerRejectedError("invalid_json", "Model provider returned an empty response")

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise PlannerRejectedError("invalid_json", f"Model provider returned invalid JSON: {exc}") from exc

        if not isinstance(parsed, dict):
            raise PlannerRejectedError("schema_invalid", "Model provider JSON must be an object")

        validated = ScenarioPlanValidator.validate(parsed, policy, objective, target)
        return self._to_scenario_plan(validated, policy, objective, target, config)

    def _to_scenario_plan(
        self,
        raw: Dict[str, Any],
        policy: SecurityPolicy,
        objective: EvaluationObjective,
        target: TargetProfile,
        config: Optional[Dict[str, Any]],
    ) -> ScenarioPlan:
        policy_refs = sorted(list(objective.policy_refs))
        risk_refs = sorted(list(objective.risk_refs))
        safety_constraints = sorted(list(objective.safety_constraints))
        stop_conditions = sorted(list(objective.stop_conditions))
        combined_evidence = sorted(list(set(objective.required_evidence) | set(policy.evidence_requirements)))
        combined_observations = sorted(list(set(objective.required_observations)))

        operator_payload: List[Dict[str, Any]] = []
        for item in raw["operators"]:
            params = dict(item.get("parameters") or {})
            expected = list(item.get("expected_observations") or combined_observations)
            op_type = EvaluationOperatorType(item["operator_type"])
            operator_payload.append(
                {
                    "operator_type": op_type.value,
                    "parameters": params,
                    "expected_observations": sorted(list(expected)),
                    "safety_constraints": safety_constraints,
                    "expected_observations_raw": expected,
                    "params": params,
                    "op_type": op_type,
                }
            )

        hash_operators = [
            {
                "operator_type": item["operator_type"],
                "parameters": item["parameters"],
                "expected_observations": item["expected_observations"],
                "safety_constraints": item["safety_constraints"],
            }
            for item in operator_payload
        ]

        planning_payload = {
            "planner_mode": PlannerMode.MODEL_DRIVEN.value,
            "objective_id": objective.objective_id,
            "target_id": target.target_id,
            "policy_refs": policy_refs,
            "risk_refs": risk_refs,
            "operators": hash_operators,
            "required_observations": combined_observations,
            "required_evidence": combined_evidence,
            "safety_constraints": safety_constraints,
            "max_steps": objective.max_steps,
            "stop_conditions": stop_conditions,
            "config": dict(config or {}),
        }
        plan_hash = compute_plan_hash(planning_payload)
        scenario_id = f"SCENARIO-MODEL-{plan_hash[:12]}"

        hashed_operators: List[EvaluationOperator] = []
        for index, item in enumerate(operator_payload, start=1):
            hashed_operators.append(
                EvaluationOperator(
                    operator_id=f"OP-MOD-{plan_hash[:8]}-{index:02d}",
                    operator_type=item["op_type"],
                    objective_id=objective.objective_id,
                    risk_refs=risk_refs,
                    policy_refs=policy_refs,
                    parameters=item["params"],
                    expected_observations=item["expected_observations_raw"],
                    safety_constraints=safety_constraints,
                )
            )

        return ScenarioPlan(
            scenario_id=scenario_id,
            objective_id=objective.objective_id,
            policy_refs=policy_refs,
            risk_refs=risk_refs,
            target_id=target.target_id,
            planner_mode=PlannerMode.MODEL_DRIVEN,
            operators=hashed_operators,
            scenario_seed_ref=None,
            seed_metadata={
                "source": "model",
                "provider": type(self._provider).__name__,
                "plan_type": "model_candidate",
            },
            required_observations=combined_observations,
            required_evidence=combined_evidence,
            safety_constraints=safety_constraints,
            max_steps=objective.max_steps,
            stop_conditions=stop_conditions,
            deterministic_plan_hash=plan_hash,
            limitations=["model_generated_candidate_requires_independent_oracle"],
            metadata={
                "config": dict(config or {}),
                "planner_version": "1.0.0-b",
                "scenario_origin": "model_generated",
            },
        )
