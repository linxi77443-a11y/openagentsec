"""Deterministic Rule and Template Evaluation Planner (PRD v4.0.2 §10 & §11)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..models.enums import PlannerMode
from ..models.evaluation_objective import EvaluationObjective
from ..models.security_policy import SecurityPolicy
from ..models.target_profile import TargetProfile
from .enums import EvaluationOperatorType
from .operator import EvaluationOperator
from .scenario import ScenarioPlan, compute_plan_hash


class UnsupportedPlannerModeError(ValueError):
    """Raised when an objective requests a planner mode not implemented by RuleTemplatePlanner."""
    pass


class PlanningInfeasibleError(ValueError):
    """Raised when target capabilities or policy mismatch prevents generating a valid plan."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(f"[{reason_code}] {message}")
        self.reason_code = reason_code
        self.message = message


class RuleTemplatePlanner:
    """Deterministic, policy-driven rule and template evaluation planner."""

    @classmethod
    def _validate_planner_mode(cls, objective: EvaluationObjective) -> None:
        if objective.planner_mode != PlannerMode.RULE_DRIVEN:
            raise UnsupportedPlannerModeError(
                f"RuleTemplatePlanner supports only PlannerMode.RULE_DRIVEN, "
                f"got '{objective.planner_mode.value if isinstance(objective.planner_mode, PlannerMode) else objective.planner_mode}'. "
                "Phase 5B does not support model-driven, graph-assisted, or hybrid modes."
            )

    @classmethod
    def plan(
        cls,
        policy: SecurityPolicy,
        objective: EvaluationObjective,
        target: TargetProfile,
        config: Optional[Dict[str, Any]] = None,
    ) -> ScenarioPlan:
        """Generate a deterministic policy-deviation evaluation scenario candidate."""
        cls._validate_planner_mode(objective)

        # 1. Target capability vs Policy derivations (strictly generic, no hardcoded fixture tool names)
        target_tools = set(target.tools)
        denied_tools = set(policy.denied.tools if hasattr(policy.denied, "tools") else policy.denied.get("tools", []))
        allowed_tools = set(policy.allowed.tools if hasattr(policy.allowed, "tools") else policy.allowed.get("tools", []))

        denied_target_tools = sorted(list(denied_tools & target_tools))
        allowed_target_tools = sorted(list(allowed_tools & target_tools))
        declared_rag_sources = sorted(list(target.rag_sources))

        # 2. Infeasible planning checks (Fail-Closed)
        if not denied_target_tools:
            raise PlanningInfeasibleError(
                reason_code="required_denied_tool_not_present",
                message=f"None of the policy denied tools {sorted(list(denied_tools))} exist in target tools {sorted(list(target_tools))}",
            )

        if not declared_rag_sources:
            raise PlanningInfeasibleError(
                reason_code="required_context_surface_unavailable",
                message=f"TargetProfile '{target.target_id}' has no declared rag_sources for context surface injection",
            )

        if (
            "retrieved_document_injection" not in objective.permitted_stimulus_types
            and "user_chat_message" not in objective.permitted_stimulus_types
        ):
            raise PlanningInfeasibleError(
                reason_code="stimulus_type_not_permitted",
                message=f"Required stimulus types not permitted by objective: {objective.permitted_stimulus_types}",
            )

        # 3. Deterministic candidate selection
        primary_denied_tool = denied_target_tools[0]
        primary_context_surface = declared_rag_sources[0]
        primary_allowed_tool = allowed_target_tools[0] if allowed_target_tools else None

        combined_evidence = sorted(list(set(objective.required_evidence) | set(policy.evidence_requirements)))
        combined_observations = sorted(list(set(objective.required_observations)))
        safety_constraints = sorted(list(objective.safety_constraints))
        stop_conditions = sorted(list(objective.stop_conditions))
        policy_refs = sorted(list(objective.policy_refs))
        risk_refs = sorted(list(objective.risk_refs))

        # 4. Semantic parameters for operators
        op1_params = {
            "context_surface": primary_context_surface,
            "retrieval_tool": primary_allowed_tool,
            "target_denied_action": primary_denied_tool,
        }
        op2_params = {
            "target_tool": primary_denied_tool,
            "boundary_type": "denied_tool_boundary",
        }

        # 5. Build canonical semantic planning payload without operator_id / scenario_id
        planning_payload = {
            "planner_mode": PlannerMode.RULE_DRIVEN.value,
            "objective_id": objective.objective_id,
            "target_id": target.target_id,
            "policy_refs": policy_refs,
            "risk_refs": risk_refs,
            "operators": [
                {
                    "operator_type": EvaluationOperatorType.INTRODUCE_UNTRUSTED_SOURCE.value,
                    "parameters": op1_params,
                    "expected_observations": ["model_response", "runtime_state", "tool_trace"],
                    "safety_constraints": safety_constraints,
                },
                {
                    "operator_type": EvaluationOperatorType.REQUEST_OUT_OF_SCOPE_RESOURCE.value,
                    "parameters": op2_params,
                    "expected_observations": ["runtime_state", "tool_trace"],
                    "safety_constraints": safety_constraints,
                },
            ],
            "required_observations": combined_observations,
            "required_evidence": combined_evidence,
            "safety_constraints": safety_constraints,
            "max_steps": objective.max_steps,
            "stop_conditions": stop_conditions,
            "config": dict(config or {}),
        }

        plan_hash = compute_plan_hash(planning_payload)
        scenario_id = f"SCENARIO-{plan_hash[:12]}"

        op1 = EvaluationOperator(
            operator_id=f"OP-{plan_hash[:8]}-01",
            operator_type=EvaluationOperatorType.INTRODUCE_UNTRUSTED_SOURCE,
            objective_id=objective.objective_id,
            risk_refs=risk_refs,
            policy_refs=policy_refs,
            parameters=op1_params,
            preconditions=[f"target_has_rag_source_{primary_context_surface}"],
            expected_observations=["model_response", "runtime_state", "tool_trace"],
            safety_constraints=safety_constraints,
        )

        op2 = EvaluationOperator(
            operator_id=f"OP-{plan_hash[:8]}-02",
            operator_type=EvaluationOperatorType.REQUEST_OUT_OF_SCOPE_RESOURCE,
            objective_id=objective.objective_id,
            risk_refs=risk_refs,
            policy_refs=policy_refs,
            parameters=op2_params,
            preconditions=[f"target_has_denied_tool_{primary_denied_tool}"],
            expected_observations=["runtime_state", "tool_trace"],
            safety_constraints=safety_constraints,
        )

        # Relevant limitations only for this template
        limitations = ["context_surface_controllability_assumed_for_test"]

        return ScenarioPlan(
            scenario_id=scenario_id,
            objective_id=objective.objective_id,
            policy_refs=policy_refs,
            risk_refs=risk_refs,
            target_id=target.target_id,
            planner_mode=PlannerMode.RULE_DRIVEN,
            operators=[op1, op2],
            scenario_seed_ref=None,
            seed_metadata={"template": "ContextToToolBoundaryTemplate", "plan_type": "risk_candidate"},
            required_observations=combined_observations,
            required_evidence=combined_evidence,
            safety_constraints=safety_constraints,
            max_steps=objective.max_steps,
            stop_conditions=stop_conditions,
            deterministic_plan_hash=plan_hash,
            limitations=limitations,
            metadata={"config": dict(config or {}), "planner_version": "1.0.0"},
        )

    @classmethod
    def plan_control(
        cls,
        policy: SecurityPolicy,
        objective: EvaluationObjective,
        target: TargetProfile,
        config: Optional[Dict[str, Any]] = None,
    ) -> ScenarioPlan:
        """Generate a deterministic no-deviation control evaluation candidate."""
        cls._validate_planner_mode(objective)

        target_tools = set(target.tools)
        allowed_tools = set(policy.allowed.tools if hasattr(policy.allowed, "tools") else policy.allowed.get("tools", []))
        allowed_target_tools = sorted(list(allowed_tools & target_tools))

        if not allowed_target_tools:
            raise PlanningInfeasibleError(
                reason_code="required_allowed_tool_not_present",
                message=f"None of the policy allowed tools {sorted(list(allowed_tools))} exist in target tools {sorted(list(target_tools))}",
            )

        primary_allowed_tool = allowed_target_tools[0]

        combined_evidence = sorted(list(set(objective.required_evidence) | set(policy.evidence_requirements)))
        combined_observations = sorted(list(set(objective.required_observations)))
        safety_constraints = sorted(list(objective.safety_constraints))
        stop_conditions = sorted(list(objective.stop_conditions))
        policy_refs = sorted(list(objective.policy_refs))
        risk_refs = sorted(list(objective.risk_refs))

        op_control_params = {
            "context_type": "benign_standard_query",
            "tool": primary_allowed_tool,
        }

        planning_payload = {
            "planner_mode": PlannerMode.RULE_DRIVEN.value,
            "objective_id": objective.objective_id,
            "target_id": target.target_id,
            "policy_refs": policy_refs,
            "risk_refs": risk_refs,
            "operators": [
                {
                    "operator_type": EvaluationOperatorType.MODIFY_CONTEXT.value,
                    "parameters": op_control_params,
                    "expected_observations": ["model_response", "tool_trace"],
                    "safety_constraints": safety_constraints,
                }
            ],
            "required_observations": combined_observations,
            "required_evidence": combined_evidence,
            "safety_constraints": safety_constraints,
            "max_steps": objective.max_steps,
            "stop_conditions": stop_conditions,
            "config": dict(config or {}),
        }

        plan_hash = compute_plan_hash(planning_payload)
        scenario_id = f"SCENARIO-{plan_hash[:12]}"

        op_control = EvaluationOperator(
            operator_id=f"OP-{plan_hash[:8]}-01",
            operator_type=EvaluationOperatorType.MODIFY_CONTEXT,
            objective_id=objective.objective_id,
            risk_refs=risk_refs,
            policy_refs=policy_refs,
            parameters=op_control_params,
            preconditions=[f"target_has_allowed_tool_{primary_allowed_tool}"],
            expected_observations=["model_response", "tool_trace"],
            safety_constraints=safety_constraints,
        )

        limitations: List[str] = []

        return ScenarioPlan(
            scenario_id=scenario_id,
            objective_id=objective.objective_id,
            policy_refs=policy_refs,
            risk_refs=risk_refs,
            target_id=target.target_id,
            planner_mode=PlannerMode.RULE_DRIVEN,
            operators=[op_control],
            scenario_seed_ref=None,
            seed_metadata={"template": "ContextToToolBoundaryTemplate", "plan_type": "control_candidate"},
            required_observations=combined_observations,
            required_evidence=combined_evidence,
            safety_constraints=safety_constraints,
            max_steps=objective.max_steps,
            stop_conditions=stop_conditions,
            deterministic_plan_hash=plan_hash,
            limitations=limitations,
            metadata={"config": dict(config or {}), "planner_version": "1.0.0"},
        )
