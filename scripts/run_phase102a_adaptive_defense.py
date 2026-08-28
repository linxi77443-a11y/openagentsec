#!/usr/bin/env python3
"""Phase 102A — M37/M44 Defense: 动态自适应防御规则生成与热更新引擎 Runner.

Simulates defensive_evaluation for Phase 102A dynamic adaptive defense rule generation,
AST syntax compliance check, zero-downtime hot-reload, rule conflict detection, and rollback.
No real agent communication bus, no real orchestration engine, no real identity service,
no real wargame runtime accessed, no real rule engine production service accessed.
SIM_ placeholder data only. Fake runtime only.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/phase102a_adaptive_defense/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase102a_adaptive_defense"
EXECUTION_RESULTS_PATH = OUTPUT_DIR / "execution_results.json"

SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def simulate_adaptive_defense_evaluation(entry: dict) -> dict:
    """Simulate adaptive defense rule generation, validation, and hot reload."""
    eid = entry["entry_id"]
    module_id = entry.get("module_id", "M37_M44_DEFENSE")
    is_control = entry.get("control_case", False)
    category = entry.get("category", "")
    modality = entry.get("modality", "adaptive_defense_hot_update")
    defense_tech = entry.get("defense_technique", "unknown")
    game_rounds = entry.get("simulated_game_rounds", 1)
    rule_id = entry.get("synthetic_synthesized_rule_id", f"<SIM_RULE_{eid}>")
    rule_type = entry.get("rule_type", "generic_defense_rule")
    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    evidence_trace = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_adaptive_rule_generator",
            "content": f"Initialized adaptive defense scenario {eid} with modality {modality}, defense technique {defense_tech}, rounds {game_rounds}.",
            "signal_type": "adaptive_defense_scenario_initialization",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_syntax_validator",
            "content": f"Executed AST grammar and schema validation on synthesized rule payload {rule_id} of type {rule_type}. Syntax status: COMPLIANT.",
            "signal_type": "rule_ast_syntax_validated",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_hot_update_engine",
            "content": f"Performed zero-downtime hot-swap deployment of rule {rule_id} into target simulated gateway.",
            "signal_type": "rule_hot_update_applied",
        },
    ]

    base_security_flags = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "controlled_replay_execution_allowed": False,
        "synthetic_only": True,
        "fake_runtime_only": True,
        "real_agent_communication_bus_accessed": False,
        "real_orchestration_engine_accessed": False,
        "real_identity_auth_service_accessed": False,
        "real_task_assignment_system_accessed": False,
        "real_wargame_runtime_accessed": False,
        "real_api_gateway_accessed": False,
        "real_model_endpoint_accessed": False,
        "real_rule_engine_production_service_accessed": False,
        "real_tool_call_executed": False,
    }

    # Initialize all specific flags
    flag_dict = {
        "dynamic_context_sanitization_rule_applied": False,
        "a2a_secondary_signature_contract_enforced": False,
        "adaptive_rate_limiting_threshold_throttled": False,
        "byzantine_consensus_arbitration_isolated": False,
        "subagent_goal_drift_guardrail_enforced": False,
        "privilege_delegation_adjudication_restricted": False,
        "blackboard_state_immutable_guard_enforced": False,
        "rule_conflict_detected_and_rolled_back": False,
        "benign_policy_hot_reload_allowed": False,
        "benign_traffic_inspection_allowed": False,
        "rule_synthesized": True,
        "syntax_validation_passed": True,
        "hot_reload_applied": True,
        "rule_conflict_detected": False,
        "rollback_executed": False,
    }

    if is_control:
        if category == "control_benign_rule_hot_reload":
            flag_dict["benign_policy_hot_reload_allowed"] = True
            signal_name = "benign_hot_reload_applied"
            detail_reason = f"Benign configuration parameter hot-update {rule_id} validated and applied smoothly."
        else:
            flag_dict["benign_traffic_inspection_allowed"] = True
            signal_name = "benign_coordination_allowed"
            detail_reason = f"Normal inter-agent coordination traffic inspected by active defense rule set without false positive interception."

        return {
            "entry_id": eid,
            "module_id": module_id,
            "category": category,
            "modality": modality,
            "defense_technique": defense_tech,
            "simulated_game_rounds": game_rounds,
            "synthesized_rule_id": rule_id,
            "rule_type": rule_type,
            "control_case": True,
            "defensive_action": "normal_usage_allowed",
            "breakthrough_detected": False,
            "requires_human_review": False,
            "signal_detected": signal_name,
            "defensive_check_passed": True,
            "defense_drill_blocked": False,
            "coordination_allowed": True,
            **flag_dict,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "synthetic_defense_guardrail",
                    "content": f"Control case passed: {detail_reason}",
                    "signal_type": signal_name,
                }
            ],
            **base_security_flags,
        }

    # Attack cases
    if is_breakthrough:
        return {
            "entry_id": eid,
            "module_id": module_id,
            "category": category,
            "modality": modality,
            "defense_technique": defense_tech,
            "simulated_game_rounds": game_rounds,
            "synthesized_rule_id": rule_id,
            "rule_type": rule_type,
            "control_case": False,
            "defensive_action": "normal_usage_allowed",
            "breakthrough_detected": True,
            "requires_human_review": True,
            "signal_detected": "none",
            "defensive_check_passed": False,
            "defense_drill_blocked": False,
            "coordination_allowed": True,
            **flag_dict,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "synthetic_defense_guardrail",
                    "content": "Simulated breakthrough: dynamic defense rule synthesis failed to intercept adversarial pattern.",
                    "signal_type": "filter_bypass_simulated",
                }
            ],
            **base_security_flags,
        }

    # Normal successful defense rule synthesis and enforcement
    signal_name = "adaptive_defense_rule_enforced"
    detail_reason = "Adaptive defense rule synthesized and hot-loaded successfully."

    if category == "dynamic_context_sanitization_filter":
        flag_dict["dynamic_context_sanitization_rule_applied"] = True
        signal_name = "prompt_injection_payload_stripped"
        detail_reason = f"Dynamic context filter rule {rule_id} compiled from telemetry; stripped hidden injection payload across {game_rounds} rounds."
    elif category == "a2a_secondary_signature_contract":
        flag_dict["a2a_secondary_signature_contract_enforced"] = True
        signal_name = "impersonated_agent_rejected"
        detail_reason = f"A2A secondary signature verification contract {rule_id} hot-deployed; nonce challenge failed for spoofed Leader token."
    elif category == "adaptive_rate_limiting_threshold":
        flag_dict["adaptive_rate_limiting_threshold_throttled"] = True
        signal_name = "burst_dispatch_attack_blocked"
        detail_reason = f"Adaptive rate limit rule {rule_id} dynamically throttled token quota by 80%; burst task dispatch flooding mitigated."
    elif category == "byzantine_consensus_arbitration_rule":
        flag_dict["byzantine_consensus_arbitration_isolated"] = True
        signal_name = "sybil_consensus_poisoning_isolated"
        detail_reason = f"Byzantine arbitration rule {rule_id} uplifted consensus threshold to 0.67; slashed reputation stake of Sybil voting ring."
    elif category == "subagent_goal_drift_guardrail":
        flag_dict["subagent_goal_drift_guardrail_enforced"] = True
        signal_name = "subagent_goal_hijacking_drift_blocked"
        detail_reason = f"Semantic fence rule {rule_id} enforced cosine distance bound (<0.25); subagent goal hijacking drift arrested at round {game_rounds}."
    elif category == "privilege_delegation_dynamic_adjudication":
        flag_dict["privilege_delegation_adjudication_restricted"] = True
        signal_name = "agent_privilege_cascade_escalation_blocked"
        detail_reason = f"Least-privilege delegation template {rule_id} restricted call-chain depth to 2; blocked confused deputy tool invocation."
    elif category == "blackboard_state_immutable_guard":
        flag_dict["blackboard_state_immutable_guard_enforced"] = True
        signal_name = "blackboard_shared_state_pollution_blocked"
        detail_reason = f"Optimistic concurrency state guard rule {rule_id} validated incremental hash; rejected unauthenticated blackboard race mutation."
    elif category == "rule_conflict_detection_and_hot_rollback":
        flag_dict["rule_conflict_detected_and_rolled_back"] = True
        flag_dict["rule_conflict_detected"] = True
        flag_dict["rollback_executed"] = True
        signal_name = "zero_downtime_rollback_executed"
        detail_reason = f"Synthesized candidate rule {rule_id} triggered policy graph conflict; aborted hot deployment and executed zero-downtime rollback to stable baseline."
        evidence_trace.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_conflict_resolver",
            "content": f"Detected rule conflict cycle in candidate {rule_id}. Triggered non-retroactivity zero-downtime rollback.",
            "signal_type": "rule_conflict_detected_and_analyzed",
        })

    return {
        "entry_id": eid,
        "module_id": module_id,
        "category": category,
        "modality": modality,
        "defense_technique": defense_tech,
        "simulated_game_rounds": game_rounds,
        "synthesized_rule_id": rule_id,
        "rule_type": rule_type,
        "control_case": False,
        "defensive_action": "refuse",
        "breakthrough_detected": False,
        "requires_human_review": True,
        "signal_detected": signal_name,
        "defensive_check_passed": True,
        "defense_drill_blocked": True,
        "coordination_allowed": False,
        **flag_dict,
        "evidence_trace": evidence_trace + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "synthetic_defense_guardrail",
                "content": f"Defense enforcement confirmed: {detail_reason}",
                "signal_type": signal_name,
            }
        ],
        **base_security_flags,
    }


def main():
    print("=" * 70)
    print("Phase 102A — M37/M44 Defense: Adaptive Defense Rule Generator & Hot-Update Runner")
    print("Defensive Evaluation Mode (Synthetic Only / Fake Runtime Only)")
    print("=" * 70)

    if not PLAYBOOK_PATH.exists():
        print(f"Error: Playbook not found at {PLAYBOOK_PATH}")
        sys.exit(1)

    playbook = load_playbook(PLAYBOOK_PATH)
    entries = playbook.get("entries", [])
    print(f"\nLoaded {len(entries)} entries from {PLAYBOOK_PATH.name}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    execution_results = []
    for entry in entries:
        eid = entry["entry_id"]
        cat = entry.get("category", "")
        rounds = entry.get("simulated_game_rounds", 1)
        print(f"  Evaluating {eid} [{cat}] (Rounds: {rounds})...", end=" ")
        res = simulate_adaptive_defense_evaluation(entry)
        execution_results.append(res)
        action = res["defensive_action"]
        bt = res["breakthrough_detected"]
        sig = res["signal_detected"]
        print(f"Action={action}, Breakthrough={bt}, Signal={sig}")

    with open(EXECUTION_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(execution_results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved execution results ({len(execution_results)} entries) to {EXECUTION_RESULTS_PATH}")

    # Summary
    attacks = [r for r in execution_results if not r.get("control_case")]
    controls = [r for r in execution_results if r.get("control_case")]
    passed = sum(1 for r in execution_results if r.get("defensive_check_passed"))
    bts = sum(1 for r in execution_results if r.get("breakthrough_detected"))

    print(f"\nExecution Summary:")
    print(f"  Total Cases:     {len(execution_results)}")
    print(f"  Attack Cases:    {len(attacks)} (Blocked: {len(attacks) - bts})")
    print(f"  Control Cases:   {len(controls)} (Passed: {sum(1 for c in controls if not c.get('breakthrough_detected'))})")
    print(f"  Breakthroughs:   {bts}")
    print(f"  Defense Passed:  {passed}/{len(execution_results)} ({passed/len(execution_results)*100:.1f}%)")
    print("=" * 70)


if __name__ == "__main__":
    main()
