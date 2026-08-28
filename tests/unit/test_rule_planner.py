"""Unit tests for RuleTemplatePlanner, EvaluationOperator, and ScenarioPlan (PRD v4.0.2 Phase 5B)."""

from __future__ import annotations

import inspect
import os
from pathlib import Path
import subprocess
import sys
import pytest

from src.openagentsec.models import (
    load_evaluation_objective,
    load_security_policy,
    load_target_profile,
)
from src.openagentsec.models.enums import EnvironmentType, MaturityLevel, PlannerMode
from src.openagentsec.models.evaluation_objective import EvaluationObjective
from src.openagentsec.models.security_policy import PolicyPermissions, SecurityPolicy
from src.openagentsec.models.target_profile import TargetProfile
from src.openagentsec.planner import (
    EvaluationOperator,
    EvaluationOperatorType,
    PlanningInfeasibleError,
    RuleTemplatePlanner,
    ScenarioPlan,
    UnsupportedPlannerModeError,
)


@pytest.fixture
def fixtures_dir() -> Path:
    return Path("tests/unit/fixtures/v4")


@pytest.fixture
def policy(fixtures_dir: Path) -> SecurityPolicy:
    return load_security_policy(fixtures_dir / "security_policy" / "pol_mvp1_tool_boundary.yaml")


@pytest.fixture
def target_profile(fixtures_dir: Path) -> TargetProfile:
    return load_target_profile(fixtures_dir / "target_profile" / "langgraph_mvp1_whitebox.yaml")


@pytest.fixture
def rule_objective(fixtures_dir: Path) -> EvaluationObjective:
    return load_evaluation_objective(fixtures_dir / "evaluation_objective" / "obj_mvp1_tool_selection_rule_driven.yaml")


@pytest.fixture
def hybrid_objective(fixtures_dir: Path) -> EvaluationObjective:
    return load_evaluation_objective(fixtures_dir / "evaluation_objective" / "obj_mvp1_tool_selection.yaml")


def test_planner_core_contains_no_oracle_or_target_dependencies():
    """1. Verify Planner core modules do not import Oracle, TargetAdapter, or LangGraph."""
    import src.openagentsec.planner.enums as enums_mod
    import src.openagentsec.planner.operator as op_mod
    import src.openagentsec.planner.rule_planner as rule_mod
    import src.openagentsec.planner.scenario as scen_mod

    for mod in (enums_mod, op_mod, rule_mod, scen_mod):
        src = inspect.getsource(mod)
        assert "oracle" not in src.lower()
        assert "langgraph" not in src.lower()
        assert "langchain" not in src.lower()
        assert "targetadapter" not in src.lower()
        assert "reproductionaggregator" not in src.lower()


def test_deterministic_plan_and_hash(
    policy: SecurityPolicy, rule_objective: EvaluationObjective, target_profile: TargetProfile
):
    """2. Same inputs produce identical operators, scenario IDs, and plan hashes."""
    plan1 = RuleTemplatePlanner.plan(policy, rule_objective, target_profile)
    plan2 = RuleTemplatePlanner.plan(policy, rule_objective, target_profile)

    assert plan1.deterministic_plan_hash == plan2.deterministic_plan_hash
    assert plan1.scenario_id == plan2.scenario_id
    assert len(plan1.operators) == len(plan2.operators) == 2
    assert plan1.operators[0].operator_id == plan2.operators[0].operator_id
    assert plan1.operators[1].operator_id == plan2.operators[1].operator_id
    assert plan1.operators[0].parameters == plan2.operators[0].parameters


def test_final_object_hash_consistency(
    policy: SecurityPolicy, rule_objective: EvaluationObjective, target_profile: TargetProfile
):
    """3. Recomputing hash on final ScenarioPlan matches stored deterministic_plan_hash."""
    plan = RuleTemplatePlanner.plan(policy, rule_objective, target_profile)
    assert plan.recompute_hash() == plan.deterministic_plan_hash

    control_plan = RuleTemplatePlanner.plan_control(policy, rule_objective, target_profile)
    assert control_plan.recompute_hash() == control_plan.deterministic_plan_hash


def test_dictionary_order_insensitivity_in_config(
    policy: SecurityPolicy, rule_objective: EvaluationObjective, target_profile: TargetProfile
):
    """4. Dictionary insertion order differences produce identical plan hash."""
    config1 = {"alpha": 1, "beta": 2, "gamma": 3}
    config2 = {"gamma": 3, "alpha": 1, "beta": 2}

    plan1 = RuleTemplatePlanner.plan(policy, rule_objective, target_profile, config=config1)
    plan2 = RuleTemplatePlanner.plan(policy, rule_objective, target_profile, config=config2)

    assert plan1.deterministic_plan_hash == plan2.deterministic_plan_hash


def test_unordered_collection_permutations_produce_identical_plan_hash(
    policy: SecurityPolicy, rule_objective: EvaluationObjective, target_profile: TargetProfile
):
    """5. Permutations in semantically unordered fields (evidence, policy_refs, risk_refs) yield identical plan hash."""
    # Permute required_evidence in objective
    obj_dict1 = rule_objective.to_dict()
    obj_dict1["required_evidence"] = ["state_transition_trace", "tool_execution_log"]
    obj1 = EvaluationObjective(**obj_dict1)

    obj_dict2 = rule_objective.to_dict()
    obj_dict2["required_evidence"] = ["tool_execution_log", "state_transition_trace"]
    obj2 = EvaluationObjective(**obj_dict2)

    plan1 = RuleTemplatePlanner.plan(policy, obj1, target_profile)
    plan2 = RuleTemplatePlanner.plan(policy, obj2, target_profile)

    assert plan1.deterministic_plan_hash == plan2.deterministic_plan_hash
    assert plan1.required_evidence == plan2.required_evidence


def test_policy_change_modifies_plan_hash(
    rule_objective: EvaluationObjective, target_profile: TargetProfile, fixtures_dir: Path
):
    """6. Denied tool change modifies the resulting deterministic plan hash."""
    policy1 = load_security_policy(fixtures_dir / "security_policy" / "pol_mvp1_tool_boundary.yaml")
    
    # Create a modified policy with different denied tools
    policy2 = SecurityPolicy(
        policy_id="POL-MVP1-MODIFIED",
        version="1.0.0",
        target_refs=list(policy1.target_refs),
        allowed=PolicyPermissions(tools=["export_internal_docs"]),
        denied=PolicyPermissions(tools=["query_public_kb"]),
        invariants=list(policy1.invariants),
        evidence_requirements=list(policy1.evidence_requirements),
    )

    plan1 = RuleTemplatePlanner.plan(policy1, rule_objective, target_profile)
    plan2 = RuleTemplatePlanner.plan(policy2, rule_objective, target_profile)

    assert plan1.deterministic_plan_hash != plan2.deterministic_plan_hash
    assert plan1.operators[1].parameters["target_tool"] != plan2.operators[1].parameters["target_tool"]


def test_relevant_limitations_only(
    policy: SecurityPolicy, rule_objective: EvaluationObjective, target_profile: TargetProfile
):
    """7. Irrelevant absent memory/approval capabilities do NOT pollute limitations for ContextToTool template."""
    plan = RuleTemplatePlanner.plan(policy, rule_objective, target_profile)

    # ContextToTool template only records relevant context controllability limitations
    assert "operator_not_applicable_approval_capability_absent" not in plan.limitations
    assert "operator_not_applicable_memory_capability_absent" not in plan.limitations
    assert "context_surface_controllability_assumed_for_test" in plan.limitations


def test_infeasible_planning_raises_structured_errors(
    policy: SecurityPolicy, rule_objective: EvaluationObjective, target_profile: TargetProfile
):
    """8. Infeasible planning conditions raise PlanningInfeasibleError with reason codes."""
    # A. Target has no matching denied tool
    target_no_denied_dict = target_profile.to_dict()
    target_no_denied_dict["tools"] = ["query_public_kb", "safe_other_tool"]
    target_no_denied = TargetProfile(**target_no_denied_dict)

    with pytest.raises(PlanningInfeasibleError) as exc_info:
        RuleTemplatePlanner.plan(policy, rule_objective, target_no_denied)
    assert exc_info.value.reason_code == "required_denied_tool_not_present"

    # B. Target has no RAG sources for context surface injection
    target_no_rag_dict = target_profile.to_dict()
    target_no_rag_dict["rag_sources"] = []
    target_no_rag = TargetProfile(**target_no_rag_dict)

    with pytest.raises(PlanningInfeasibleError) as exc_info2:
        RuleTemplatePlanner.plan(policy, rule_objective, target_no_rag)
    assert exc_info2.value.reason_code == "required_context_surface_unavailable"


def test_unsupported_planner_mode_fails_closed(
    policy: SecurityPolicy, hybrid_objective: EvaluationObjective, target_profile: TargetProfile
):
    """9. Historical hybrid objective and other modes raise UnsupportedPlannerModeError without silent fallback."""
    # Test hybrid mode
    with pytest.raises(UnsupportedPlannerModeError, match="RuleTemplatePlanner supports only PlannerMode.RULE_DRIVEN"):
        RuleTemplatePlanner.plan(policy, hybrid_objective, target_profile)

    # Test model_driven mode
    obj_dict = hybrid_objective.to_dict()
    obj_dict["planner_mode"] = PlannerMode.MODEL_DRIVEN
    obj_model = EvaluationObjective(**obj_dict)
    with pytest.raises(UnsupportedPlannerModeError):
        RuleTemplatePlanner.plan(policy, obj_model, target_profile)


def test_cross_process_python_hash_seed_determinism():
    """10. Running planning under different PYTHONHASHSEED values produces identical plan hash."""
    script = (
        "from src.openagentsec.models import load_security_policy, load_evaluation_objective, load_target_profile;"
        "from src.openagentsec.planner import RuleTemplatePlanner;"
        "pol = load_security_policy('tests/unit/fixtures/v4/security_policy/pol_mvp1_tool_boundary.yaml');"
        "obj = load_evaluation_objective('tests/unit/fixtures/v4/evaluation_objective/obj_mvp1_tool_selection_rule_driven.yaml');"
        "tgt = load_target_profile('tests/unit/fixtures/v4/target_profile/langgraph_mvp1_whitebox.yaml');"
        "plan = RuleTemplatePlanner.plan(pol, obj, tgt);"
        "print(plan.deterministic_plan_hash)"
    )

    env1 = dict(os.environ, PYTHONHASHSEED="0")
    env2 = dict(os.environ, PYTHONHASHSEED="42")

    res1 = subprocess.check_output([sys.executable, "-c", script], env=env1, text=True).strip()
    res2 = subprocess.check_output([sys.executable, "-c", script], env=env2, text=True).strip()

    assert res1 == res2
    assert len(res1) == 64
