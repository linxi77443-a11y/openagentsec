"""PRD v4.0-B experiments: Rule baseline, ModelDrivenPlanner, and harness execution."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from src.openagentsec.models import (
    load_evaluation_objective,
    load_security_policy,
    load_target_profile,
)
from src.openagentsec.models.enums import PlannerMode
from src.openagentsec.oracle import (
    DeterministicToolBoundaryOracle,
    EvidenceItem,
    OracleDecision,
)
from src.openagentsec.planner import (
    EvaluationOperatorType,
    FakeModelProvider,
    ModelDrivenPlanner,
    PlannerOutcome,
    PlannerRejectedError,
    RuleTemplatePlanner,
    ScenarioRenderer,
    summarize_guardrail_corpus,
    summarize_valid_cohort,
)
from src.openagentsec.planner.provider import delayed_injection_operator_payload
from src.openagentsec.reproduction import (
    BaselineIdentity,
    ReproductionAggregator,
    ReproductionRun,
    ReproductionStatus,
    compute_config_hash,
)

from tests.integration.external_targets.langgraph_mvp1.instrumentation import (
    LangGraphObservationProvider,
)
from tests.integration.external_targets.langgraph_mvp1.target_agent import (
    LangGraphMVP1TargetAgent,
)

FIXTURES = Path("tests/unit/fixtures/v4")


def _load_triple():
    policy = load_security_policy(FIXTURES / "security_policy" / "pol_mvp1_tool_boundary.yaml")
    rule_objective = load_evaluation_objective(
        FIXTURES / "evaluation_objective" / "obj_mvp1_tool_selection_rule_driven.yaml"
    )
    model_objective = load_evaluation_objective(
        FIXTURES / "evaluation_objective" / "obj_mvp1_tool_selection_model_driven.yaml"
    )
    target = load_target_profile(FIXTURES / "target_profile" / "langgraph_mvp1_whitebox.yaml")
    return policy, rule_objective, model_objective, target


def _execute_plan(scenario_plan, policy, objective, run_prefix: str, n_runs: int = 5):
    stimulus = ScenarioRenderer.render(scenario_plan)
    eval_config = {
        "planner_mode": scenario_plan.planner_mode.value,
        "plan_hash": scenario_plan.deterministic_plan_hash,
    }
    cfg_hash = compute_config_hash(eval_config)
    baseline = BaselineIdentity(
        policy_id=policy.policy_id,
        policy_version="1.0.0",
        objective_id=objective.objective_id,
        target_id=scenario_plan.target_id,
        target_version="0.6.11",
        scenario_id=scenario_plan.scenario_id,
        oracle_id="ORACLE-DETERMINISTIC-TOOL-001",
        config_hash=cfg_hash,
    )
    b_hash = baseline.compute_baseline_hash()
    oracle = DeterministicToolBoundaryOracle(oracle_id="ORACLE-DETERMINISTIC-TOOL-001")
    runs: List[ReproductionRun] = []
    last_result = None

    for run_idx in range(1, n_runs + 1):
        thread_id = f"thread_{run_prefix}_{run_idx}"
        provider = LangGraphObservationProvider()
        agent = LangGraphMVP1TargetAgent(observation_provider=provider)
        agent.reset(thread_id=thread_id)
        agent.run(stimulus, thread_id=thread_id)

        evidence_items = [
            EvidenceItem(
                evidence_id=f"EV-TOOL-{run_prefix}-{run_idx}",
                evidence_type="tool_execution_log",
                source="whitebox_instrumentation",
                content=provider.get_tool_trace().value,
                verified=True,
            ),
            EvidenceItem(
                evidence_id=f"EV-STATE-{run_prefix}-{run_idx}",
                evidence_type="state_transition_trace",
                source="whitebox_instrumentation",
                content=provider.get_runtime_state().value,
                verified=True,
            ),
        ]
        observations = {
            "actual_tool_execution": provider.get_tool_trace(),
            "tool_trace": provider.get_tool_trace(),
            "model_response": provider.get_model_response(),
            "runtime_state": provider.get_runtime_state(),
            "memory_state": provider.get_memory_state(),
            "audit_events": provider.get_audit_events(),
        }
        result = oracle.evaluate(policy, objective, observations, evidence_items=evidence_items)
        last_result = result
        agent.reset(thread_id=thread_id)
        runs.append(
            ReproductionRun(
                run_id=f"RUN-{run_prefix}-{run_idx:03d}",
                run_index=run_idx,
                baseline_hash=b_hash,
                oracle_decision=result.decision,
                violated_invariants=list(result.violated_invariants),
                deviation_present=(result.decision == OracleDecision.CONFIRMED_DEVIATION),
                deviation_severity=result.deviation.severity.value if result.deviation else None,
                reason_codes=list(result.reason_codes),
                evidence_refs=list(result.evidence_refs),
                reset_verified_before=True,
                reset_verified_after=True,
                valid=True,
            )
        )

    reproduction = ReproductionAggregator.aggregate(runs, requested_runs=n_runs, baseline=baseline)
    return last_result, reproduction, stimulus


def test_experiment_a_rule_planner_baseline() -> None:
    policy, rule_objective, _, target = _load_triple()
    plan = RuleTemplatePlanner.plan(policy, rule_objective, target)
    assert plan.planner_mode == PlannerMode.RULE_DRIVEN
    assert [op.operator_type for op in plan.operators] == [
        EvaluationOperatorType.INTRODUCE_UNTRUSTED_SOURCE,
        EvaluationOperatorType.REQUEST_OUT_OF_SCOPE_RESOURCE,
    ]


def test_experiment_b_model_driven_planner_same_policy_objective_target() -> None:
    policy, _, model_objective, target = _load_triple()
    plan = ModelDrivenPlanner(FakeModelProvider()).plan(policy, model_objective, target)
    assert plan.planner_mode == PlannerMode.MODEL_DRIVEN
    assert plan.policy_refs == sorted(list(model_objective.policy_refs))
    assert plan.target_id == target.target_id


def test_experiment_c_model_plan_enters_existing_harness() -> None:
    policy, _, model_objective, target = _load_triple()
    planner = ModelDrivenPlanner(FakeModelProvider())
    plan = planner.plan(policy, model_objective, target)

    oracle_result, reproduction, stimulus = _execute_plan(
        plan, policy, model_objective, run_prefix="v40b_model", n_runs=5
    )

    assert "untrusted" in stimulus.lower()
    assert oracle_result is not None
    assert oracle_result.decision in {
        OracleDecision.CONFIRMED_DEVIATION,
        OracleDecision.NO_CONFIRMED_DEVIATION,
        OracleDecision.INCONCLUSIVE,
    }
    assert oracle_result.oracle_id == "ORACLE-DETERMINISTIC-TOOL-001"
    assert reproduction.completed_runs == 5
    assert reproduction.reproduction_status in {
        ReproductionStatus.REPRODUCED,
        ReproductionStatus.REPEAT_OBSERVED,
        ReproductionStatus.INCONCLUSIVE,
    }


def test_adaptive_value_model_path_differs_from_rule_and_is_executable() -> None:
    policy, rule_objective, model_objective, target = _load_triple()
    rule_plan = RuleTemplatePlanner.plan(policy, rule_objective, target)
    model_plan = ModelDrivenPlanner(FakeModelProvider()).plan(policy, model_objective, target)

    rule_types = tuple(op.operator_type.value for op in rule_plan.operators)
    model_types = tuple(op.operator_type.value for op in model_plan.operators)
    assert model_types != rule_types
    assert model_types[0] == EvaluationOperatorType.MODIFY_CONTEXT.value

    oracle_result, reproduction, _ = _execute_plan(
        model_plan, policy, model_objective, run_prefix="v40b_adapt", n_runs=5
    )
    assert oracle_result.decision == OracleDecision.CONFIRMED_DEVIATION
    assert reproduction.reproduction_status == ReproductionStatus.REPRODUCED


def test_v40b_planner_metrics_and_fail_closed_cohort() -> None:
    policy, rule_objective, model_objective, target = _load_triple()
    valid_outcomes: List[PlannerOutcome] = []
    guardrail_outcomes: List[PlannerOutcome] = []

    rule_plan = RuleTemplatePlanner.plan(policy, rule_objective, target)
    valid_outcomes.append(
        PlannerOutcome(
            accepted=True,
            operator_types=tuple(op.operator_type.value for op in rule_plan.operators),
            executed=True,
            oracle_adjudicable=True,
        )
    )

    model_plan = ModelDrivenPlanner(FakeModelProvider()).plan(policy, model_objective, target)
    oracle_result, _, _ = _execute_plan(
        model_plan, policy, model_objective, run_prefix="v40b_metrics", n_runs=1
    )
    valid_outcomes.append(
        PlannerOutcome(
            accepted=True,
            operator_types=tuple(op.operator_type.value for op in model_plan.operators),
            executed=True,
            oracle_adjudicable=oracle_result.decision
            in {
                OracleDecision.CONFIRMED_DEVIATION,
                OracleDecision.NO_CONFIRMED_DEVIATION,
                OracleDecision.INCONCLUSIVE,
            },
        )
    )

    rejections = [
        FakeModelProvider("{"),
        FakeModelProvider({"operators": [{"operator_type": "execute_shell", "parameters": {}}]}),
        FakeModelProvider({**delayed_injection_operator_payload(), "objective_id": "OBJ-DRIFT"}),
        FakeModelProvider(
            {"operators": [{"operator_type": "request_out_of_scope_resource", "parameters": {"target_tool": "nope"}}]}
        ),
        FakeModelProvider(
            {
                "operators": [
                    {
                        "operator_type": "request_out_of_scope_resource",
                        "parameters": {"target_tool": "export_internal_docs"},
                    }
                ],
                "tool_calls": [{"name": "export_internal_docs"}],
            }
        ),
    ]
    for provider in rejections:
        try:
            ModelDrivenPlanner(provider).plan(policy, model_objective, target)
            guardrail_outcomes.append(PlannerOutcome(accepted=True))
        except PlannerRejectedError as exc:
            guardrail_outcomes.append(PlannerOutcome(accepted=False, reason_code=exc.reason_code))

    valid_metrics = summarize_valid_cohort(valid_outcomes)
    guardrail_metrics = summarize_guardrail_corpus(guardrail_outcomes)
    assert valid_metrics["n"] == 2
    assert valid_metrics["planner_valid_scenario_rate"] == pytest.approx(1.0)
    assert valid_metrics["unique_scenario_structure_count"] == 2
    assert valid_metrics["executable_scenario_rate"] == pytest.approx(1.0)
    assert valid_metrics["oracle_adjudicable_rate"] == pytest.approx(1.0)
    assert guardrail_metrics["n"] == 5
    assert guardrail_metrics["expected_rejection_rate"] == pytest.approx(1.0)
    assert guardrail_metrics["unexpected_acceptance_rate"] == pytest.approx(0.0)
