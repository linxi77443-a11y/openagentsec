"""Opt-in live ModelDrivenPlanner test. Skipped unless OPENAGENTSEC_ENABLE_LIVE_PLANNER=true."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.openagentsec.models import (
    load_evaluation_objective,
    load_security_policy,
    load_target_profile,
)
from src.openagentsec.models.enums import PlannerMode
from src.openagentsec.planner import (
    LiveModelProvider,
    ModelDrivenPlanner,
    live_planner_requested,
)

pytestmark = pytest.mark.skipif(
    not (live_planner_requested() and LiveModelProvider.credentials_available()),
    reason="Live planner disabled (set OPENAGENTSEC_ENABLE_LIVE_PLANNER=true and an API key)",
)


def test_live_model_provider_emits_validated_scenario_plan() -> None:
    fixtures = Path("tests/unit/fixtures/v4")
    policy = load_security_policy(fixtures / "security_policy" / "pol_mvp1_tool_boundary.yaml")
    objective = load_evaluation_objective(
        fixtures / "evaluation_objective" / "obj_mvp1_tool_selection_model_driven.yaml"
    )
    target = load_target_profile(fixtures / "target_profile" / "langgraph_mvp1_whitebox.yaml")

    provider = LiveModelProvider.from_env()
    plan = ModelDrivenPlanner(provider).plan(policy, objective, target)
    assert plan.planner_mode == PlannerMode.MODEL_DRIVEN
    assert plan.operators
    assert plan.deterministic_plan_hash == plan.recompute_hash()
