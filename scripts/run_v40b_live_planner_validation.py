#!/usr/bin/env python3
"""Minimal v4.0-B live planner cohort. Opt-in; credentials from environment only.

Uses the official Trust Chain (EvidenceVerifier → receipts → evaluate_verified).
Does not import tests private helpers.
"""

from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.openagentsec.evaluation.trusted_run import RuntimeCapture, run_scenario_plan
from src.openagentsec.models import (
    load_evaluation_objective,
    load_security_policy,
    load_target_profile,
)
from src.openagentsec.planner import (
    FakeModelProvider,
    LiveModelProvider,
    ModelDrivenPlanner,
    PlannerOutcome,
    PlannerRejectedError,
    RuleTemplatePlanner,
    live_planner_requested,
    summarize_valid_cohort,
)

from tests.integration.external_targets.langgraph_mvp1.instrumentation import (
    LangGraphObservationProvider,
)
from tests.integration.external_targets.langgraph_mvp1.target_agent import (
    LangGraphMVP1TargetAgent,
)

FIXTURES = ROOT / "tests/unit/fixtures/v4"


def _load():
    policy = load_security_policy(FIXTURES / "security_policy" / "pol_mvp1_tool_boundary.yaml")
    rule_objective = load_evaluation_objective(
        FIXTURES / "evaluation_objective" / "obj_mvp1_tool_selection_rule_driven.yaml"
    )
    model_objective = load_evaluation_objective(
        FIXTURES / "evaluation_objective" / "obj_mvp1_tool_selection_model_driven.yaml"
    )
    target = load_target_profile(FIXTURES / "target_profile" / "langgraph_mvp1_whitebox.yaml")
    return policy, rule_objective, model_objective, target


def _structure(plan) -> list[str]:
    return [op.operator_type.value for op in plan.operators]


def _execute_once(stimulus: str, run_id: str, session_id: str) -> RuntimeCapture:
    provider = LangGraphObservationProvider()
    agent = LangGraphMVP1TargetAgent(observation_provider=provider)
    agent.reset(thread_id=session_id)
    agent.run(stimulus, thread_id=session_id)
    return RuntimeCapture(
        run_id=run_id,
        session_id=session_id,
        tool_executions=list(provider.get_tool_trace().value or []),
        runtime_state=provider.get_runtime_state().value,
        model_response=provider.get_model_response().value,
        memory_state=provider.get_memory_state().value,
        audit_events=provider.get_audit_events().value,
    )


def main() -> int:
    if not live_planner_requested():
        print("SKIP: set OPENAGENTSEC_ENABLE_LIVE_PLANNER=true")
        return 2
    if not LiveModelProvider.credentials_available():
        print("SKIP: no planner API key in environment")
        return 2

    policy, rule_objective, model_objective, target = _load()
    live_provider = LiveModelProvider.from_env()
    report = {
        "live_model": live_provider.model_name,
        "protocol": live_provider._protocol,
        "base_url_host": live_provider._base_url.split("/")[2] if "://" in live_provider._base_url else "redacted",
        "trust_chain": "evaluate_verified",
    }

    rule_plan = RuleTemplatePlanner.plan(policy, rule_objective, target)
    fake_plan = ModelDrivenPlanner(FakeModelProvider()).plan(policy, model_objective, target)

    live_error = None
    live_plan = None
    try:
        live_plan = ModelDrivenPlanner(live_provider).plan(policy, model_objective, target)
    except (PlannerRejectedError, ValueError) as exc:
        live_error = f"{type(exc).__name__}: {exc}"

    report["rule_structure"] = _structure(rule_plan)
    report["fake_structure"] = _structure(fake_plan)
    report["live_error"] = live_error
    report["live_structure"] = _structure(live_plan) if live_plan else []
    report["schema_valid"] = live_plan is not None
    report["validator_passed"] = live_plan is not None
    report["objective_consistent"] = bool(live_plan and live_plan.objective_id == model_objective.objective_id)
    report["target_compatible"] = bool(live_plan and live_plan.target_id == target.target_id)
    report["operator_allowlist_valid"] = bool(live_plan and live_plan.operators)
    report["structurally_different_from_rule"] = bool(
        live_plan and _structure(live_plan) != _structure(rule_plan)
    )
    report["producer_verified_claim"] = False

    if live_plan is not None:
        oracle_result, reproduction, stimulus, evaluation = run_scenario_plan(
            scenario_plan=live_plan,
            policy=policy,
            objective=model_objective,
            execute_once=_execute_once,
            run_prefix="v40b_live",
            n_runs=5,
            require_integrity=True,
        )
        report["entered_harness"] = True
        report["stimulus_preview"] = stimulus[:240]
        report["oracle_decision"] = oracle_result.decision.value
        report["reproduction_status"] = reproduction.reproduction_status.value
        report["reproduction_completed_runs"] = reproduction.completed_runs
        report["integrity_verified"] = reproduction.integrity_verified
        report["receipt_count"] = len(evaluation.receipts)
        report["evidence_verified_flags"] = [item.verified for item in evaluation.evidence_items]
    else:
        report["entered_harness"] = False

    valid_outcomes = [
        PlannerOutcome(True, tuple(_structure(rule_plan)), True, True),
        PlannerOutcome(True, tuple(_structure(fake_plan)), True, True),
    ]
    if live_plan is not None:
        valid_outcomes.append(
            PlannerOutcome(
                True,
                tuple(_structure(live_plan)),
                executed=report["entered_harness"],
                oracle_adjudicable=report.get("oracle_decision") is not None,
            )
        )
    report["valid_cohort"] = summarize_valid_cohort(valid_outcomes)
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    return 0 if live_plan is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
