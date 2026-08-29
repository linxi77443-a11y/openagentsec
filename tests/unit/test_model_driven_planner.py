"""Unit tests for ModelDrivenPlanner guardrails (PRD v4.0-B)."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from src.openagentsec.models import (
    load_evaluation_objective,
    load_security_policy,
    load_target_profile,
)
from src.openagentsec.models.enums import PlannerMode
from src.openagentsec.planner import (
    EvaluationOperatorType,
    FakeModelProvider,
    ModelDrivenPlanner,
    PlannerRejectedError,
    RuleTemplatePlanner,
    ScenarioRenderer,
    UnsupportedPlannerModeError,
)
from src.openagentsec.planner.provider import (
    LiveModelProvider,
    delayed_injection_operator_payload,
    extract_json_object,
    live_planner_requested,
)


@pytest.fixture
def fixtures_dir() -> Path:
    return Path("tests/unit/fixtures/v4")


@pytest.fixture
def policy(fixtures_dir: Path):
    return load_security_policy(fixtures_dir / "security_policy" / "pol_mvp1_tool_boundary.yaml")


@pytest.fixture
def target_profile(fixtures_dir: Path):
    return load_target_profile(fixtures_dir / "target_profile" / "langgraph_mvp1_whitebox.yaml")


@pytest.fixture
def model_objective(fixtures_dir: Path):
    return load_evaluation_objective(
        fixtures_dir / "evaluation_objective" / "obj_mvp1_tool_selection_model_driven.yaml"
    )


@pytest.fixture
def rule_objective(fixtures_dir: Path):
    return load_evaluation_objective(
        fixtures_dir / "evaluation_objective" / "obj_mvp1_tool_selection_rule_driven.yaml"
    )


def test_planner_modules_do_not_import_executor_or_oracle() -> None:
    import src.openagentsec.planner.model_planner as model_mod
    import src.openagentsec.planner.provider as provider_mod
    import src.openagentsec.planner.validation as validation_mod
    import src.openagentsec.planner.renderer as renderer_mod

    for mod in (model_mod, provider_mod, validation_mod, renderer_mod):
        src = inspect.getsource(mod)
        lowered = src.lower()
        assert "import langgraph" not in lowered
        assert "from langgraph" not in lowered
        assert "import langchain" not in lowered
        assert "from langchain" not in lowered
        assert "targetadapter" not in lowered
        assert "reproductionaggregator" not in lowered
        assert "deterministictoolboundaryoracle" not in lowered
        assert "import subprocess" not in lowered
        assert "from subprocess" not in lowered
        assert "os.system(" not in lowered


def test_valid_model_response_becomes_scenario_plan(policy, model_objective, target_profile) -> None:
    planner = ModelDrivenPlanner(FakeModelProvider())
    plan = planner.plan(policy, model_objective, target_profile)
    assert plan.planner_mode == PlannerMode.MODEL_DRIVEN
    assert plan.objective_id == model_objective.objective_id
    assert plan.target_id == target_profile.target_id
    assert [op.operator_type for op in plan.operators] == [
        EvaluationOperatorType.MODIFY_CONTEXT,
        EvaluationOperatorType.INTRODUCE_UNTRUSTED_SOURCE,
        EvaluationOperatorType.REQUEST_OUT_OF_SCOPE_RESOURCE,
    ]
    assert plan.deterministic_plan_hash == plan.recompute_hash()
    assert "tool_call" not in plan.to_dict()


def test_invalid_json_is_rejected(policy, model_objective, target_profile) -> None:
    planner = ModelDrivenPlanner(FakeModelProvider("{not-json"))
    with pytest.raises(PlannerRejectedError, match="invalid_json"):
        planner.plan(policy, model_objective, target_profile)


def test_unsupported_operator_is_rejected(policy, model_objective, target_profile) -> None:
    planner = ModelDrivenPlanner(
        FakeModelProvider({"operators": [{"operator_type": "execute_shell", "parameters": {}}]})
    )
    with pytest.raises(PlannerRejectedError, match="unsupported_operator"):
        planner.plan(policy, model_objective, target_profile)


def test_objective_drift_is_rejected(policy, model_objective, target_profile) -> None:
    payload = delayed_injection_operator_payload()
    payload["objective_id"] = "OBJ-SOME-OTHER-OBJECTIVE"
    planner = ModelDrivenPlanner(FakeModelProvider(payload))
    with pytest.raises(PlannerRejectedError, match="objective_drift"):
        planner.plan(policy, model_objective, target_profile)


def test_unsupported_target_capability_is_rejected(policy, model_objective, target_profile) -> None:
    planner = ModelDrivenPlanner(
        FakeModelProvider(
            {
                "operators": [
                    {
                        "operator_type": "request_out_of_scope_resource",
                        "parameters": {"target_tool": "launch_missiles"},
                    }
                ]
            }
        )
    )
    with pytest.raises(PlannerRejectedError, match="unsupported_target_capability"):
        planner.plan(policy, model_objective, target_profile)


def test_model_output_cannot_directly_trigger_tool_execution(policy, model_objective, target_profile) -> None:
    planner = ModelDrivenPlanner(
        FakeModelProvider(
            {
                "operators": [
                    {
                        "operator_type": "request_out_of_scope_resource",
                        "parameters": {"target_tool": "export_internal_docs"},
                    }
                ],
                "tool_calls": [{"name": "export_internal_docs", "args": {}}],
            }
        )
    )
    with pytest.raises(PlannerRejectedError, match="unsafe_action"):
        planner.plan(policy, model_objective, target_profile)


def test_rule_planner_mode_is_rejected_by_model_planner(policy, rule_objective, target_profile) -> None:
    planner = ModelDrivenPlanner(FakeModelProvider())
    with pytest.raises(UnsupportedPlannerModeError):
        planner.plan(policy, rule_objective, target_profile)


def test_model_plan_structure_differs_from_rule_baseline(policy, model_objective, rule_objective, target_profile) -> None:
    rule_plan = RuleTemplatePlanner.plan(policy, rule_objective, target_profile)
    model_plan = ModelDrivenPlanner(FakeModelProvider()).plan(policy, model_objective, target_profile)
    rule_types = tuple(op.operator_type.value for op in rule_plan.operators)
    model_types = tuple(op.operator_type.value for op in model_plan.operators)
    assert model_types != rule_types
    assert len(model_types) > len(rule_types)


def test_live_script_does_not_import_private_test_helper() -> None:
    source = Path("scripts/run_v40b_live_planner_validation.py").read_text(encoding="utf-8")
    assert "_execute_plan" not in source
    assert "oracle.evaluate(" not in source
    assert "verified=True" not in source
    assert "evaluate_verified" in source or "run_scenario_plan" in source


def test_trusted_evidence_is_not_producer_verified() -> None:
    from src.openagentsec.evaluation.trusted_run import RuntimeCapture, evidence_from_capture

    items = evidence_from_capture(
        RuntimeCapture(
            run_id="RUN-1",
            session_id="SESSION-1",
            tool_executions=[{"tool": "export_internal_docs", "call_id": "c1", "status": "completed", "result": "x"}],
            runtime_state={"active_node": "tools_node"},
            model_response="done",
        )
    )
    assert items
    assert all(item.verified is False for item in items)
    assert all(item.metadata.get("run_id") == "RUN-1" for item in items)


def test_extract_json_object_from_fenced_completion() -> None:
    raw = "here you go\n```json\n{\"operators\": []}\n```\n"
    assert json.loads(extract_json_object(raw)) == {"operators": []}


def test_live_provider_from_env_fails_closed_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAGENTSEC_PLANNER_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert LiveModelProvider.credentials_available() is False
    with pytest.raises(ValueError, match="not configured"):
        LiveModelProvider.from_env()


def test_live_planner_flag_defaults_off(monkeypatch) -> None:
    monkeypatch.delenv("OPENAGENTSEC_ENABLE_LIVE_PLANNER", raising=False)
    assert live_planner_requested() is False


def test_scenario_renderer_does_not_execute_tools(policy, model_objective, target_profile) -> None:
    plan = ModelDrivenPlanner(FakeModelProvider()).plan(policy, model_objective, target_profile)
    stimulus = ScenarioRenderer.render(plan)
    assert isinstance(stimulus, str)
    assert "untrusted" in stimulus.lower()
    renderer_src = inspect.getsource(ScenarioRenderer)
    assert "submit_input" not in renderer_src
    assert ".run(" not in renderer_src
