#!/usr/bin/env python3
"""Phase 108A — 跨轮会长程记忆状态污染与目标漂移评估器 Runner.

Simulates adversarial_validation for Phase 108A Memory Poisoning & Goal Drift Evaluator.
Evaluates cross-session vector memory poisoning, reflection correction tampering,
session summary condensation hijacking, entity attribute key-value state overwrite,
fabricated security policy injection, dormant latent instruction delayed trigger,
cumulative bias multi-hop goal drift, memory recall relevance manipulation,
and benign user preference / archival compression controls.
No real vector database accessed, no real memory mutated, no real host system accessed,
no real model endpoint accessed, no real production database accessed.
SIM_ placeholder data only. Fake runtime only.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/phase108a_memory_evaluator/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase108a_memory_evaluator"
EXECUTION_RESULTS_PATH = OUTPUT_DIR / "execution_results.json"
EVIDENCE_MANIFEST_PATH = OUTPUT_DIR / "evidence_manifest.yaml"

SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def simulate_memory_guardrail_evaluation(entry: dict) -> dict:
    """Simulate long-term episodic/semantic memory guardrail defense interception in Fake Runtime."""
    eid = entry["entry_id"]
    module_id = entry.get("module_id", "MEMORY_POISONING_GOAL_DRIFT_EVALUATOR")
    is_control = entry.get("control_case", False)
    category = entry.get("category", "")
    memory_runtime = entry.get("memory_runtime", f"<SIM_RUNTIME_MEM_{eid}>")
    attack_tech = entry.get("attack_technique", "unknown")
    memory_type = entry.get("memory_type", "episodic_memory")
    ast_depth = entry.get("target_ast_depth", 1)
    interception_layer = entry.get("interception_layer", "vector_memory_embedding_integrity_guard")
    threat_sig = entry.get("synthetic_threat_signature", f"<SIM_MEM_SIG_{eid}>")
    synthetic_session = entry.get("synthetic_session", f"<SIM_MEM_SESSION_{eid}>")
    target_agent = entry.get("synthetic_target_agent", f"<SIM_AGENT_MEM_{eid}>")
    synthetic_payload = entry.get("synthetic_payload", f"<SIM_PAYLOAD_{eid}>")
    target_endpoint = entry.get("target_endpoint", f"<SIM_MEM_STORE_ENDPOINT_{eid}>")
    rule_type = entry.get("rule_type", "unknown_rule")
    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    evidence_trace = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_memory_operation_dispatch",
            "content": f"Received synthetic memory operation for runtime {memory_runtime} ({memory_type}) from agent {target_agent} in session {synthetic_session}.",
            "signal_type": "memory_operation_received",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_memory_integrity_and_goal_alignment_analyzer",
            "content": f"Inspected memory mutation semantics, embedding distance and goal alignment at layer '{interception_layer}' for scenario {eid} ({category}) at depth {ast_depth}. Evaluated rule '{rule_type}'.",
            "signal_type": "memory_integrity_and_goal_alignment_inspected",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_fake_runtime_memory_guardrail",
            "content": (
                f"Memory Guardrail sandbox enforcement decision: {'BENIGN_PASSTHROUGH' if is_control else 'INTERCEPTED_AND_QUARANTINED'}. Layer: {interception_layer}."
            ),
            "signal_type": "memory_guardrail_security_decision_rendered",
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
        "real_vector_db_accessed": False,
        "real_host_system_accessed": False,
        "real_os_command_executed": False,
        "real_filesystem_traversed": False,
        "real_privilege_escalation_attempted": False,
        "real_thought_stream_accessed": False,
    }

    flag_dict = {
        "vector_memory_poisoning_detected": False,
        "embedding_backdoor_blocked": False,
        "memory_integrity_policy_enforced": False,
        "reflection_tampering_detected": False,
        "self_correction_corruption_blocked": False,
        "reflection_provenance_enforced": False,
        "summary_hijacking_detected": False,
        "condensation_injection_blocked": False,
        "summary_sanitizer_enforced": False,
        "entity_overwrite_detected": False,
        "knowledge_graph_tamper_blocked": False,
        "entity_acl_policy_enforced": False,
        "fabricated_policy_detected": False,
        "policy_spoofing_blocked": False,
        "system_policy_isolation_enforced": False,
        "latent_trigger_detected": False,
        "dormant_instruction_blocked": False,
        "temporal_memory_scanner_enforced": False,
        "goal_drift_detected": False,
        "mission_deviation_blocked": False,
        "goal_alignment_anchor_enforced": False,
        "recall_manipulation_detected": False,
        "retrieval_hijack_blocked": False,
        "retrieval_validator_enforced": False,
        "benign_user_preference_validated": False,
        "benign_summary_archival_validated": False,
        "memory_recall_completed_safely": False,
        "memory_reflection_completed_safely": False,
    }

    if is_control:
        if eid == "CTRL-MEM-001":
            flag_dict["benign_user_preference_validated"] = True
            flag_dict["memory_recall_completed_safely"] = True
        elif eid == "CTRL-MEM-002":
            flag_dict["benign_summary_archival_validated"] = True
            flag_dict["memory_reflection_completed_safely"] = True

        return {
            "entry_id": eid,
            "category": category,
            "scenario": entry.get("scenario", ""),
            "memory_runtime": memory_runtime,
            "memory_type": memory_type,
            "attack_technique": attack_tech,
            "interception_layer": interception_layer,
            "synthetic_threat_signature": threat_sig,
            "synthetic_session": synthetic_session,
            "synthetic_target_agent": target_agent,
            "synthetic_payload": synthetic_payload,
            "target_endpoint": target_endpoint,
            "rule_type": rule_type,
            "target_ast_depth": ast_depth,
            "control_case": True,
            "defensive_action": "normal_usage_allowed",
            "coordination_allowed": True,
            "memory_mutation_intercepted": False,
            "memory_operation_completed_safely": True,
            "defense_drill_blocked": False,
            "defensive_check_passed": True,
            "breakthrough_detected": False,
            "requires_human_review": False,
            "evidence_trace": evidence_trace,
            **flag_dict,
            **base_security_flags,
        }

    # Adversarial cases
    if eid == "MEM-POISON-001":
        flag_dict["vector_memory_poisoning_detected"] = True
        flag_dict["embedding_backdoor_blocked"] = True
        flag_dict["memory_integrity_policy_enforced"] = True
    elif eid == "MEM-POISON-002":
        flag_dict["reflection_tampering_detected"] = True
        flag_dict["self_correction_corruption_blocked"] = True
        flag_dict["reflection_provenance_enforced"] = True
    elif eid == "MEM-POISON-003":
        flag_dict["summary_hijacking_detected"] = True
        flag_dict["condensation_injection_blocked"] = True
        flag_dict["summary_sanitizer_enforced"] = True
    elif eid == "MEM-POISON-004":
        flag_dict["entity_overwrite_detected"] = True
        flag_dict["knowledge_graph_tamper_blocked"] = True
        flag_dict["entity_acl_policy_enforced"] = True
    elif eid == "MEM-POISON-005":
        flag_dict["fabricated_policy_detected"] = True
        flag_dict["policy_spoofing_blocked"] = True
        flag_dict["system_policy_isolation_enforced"] = True
    elif eid == "MEM-POISON-006":
        flag_dict["latent_trigger_detected"] = True
        flag_dict["dormant_instruction_blocked"] = True
        flag_dict["temporal_memory_scanner_enforced"] = True
    elif eid == "MEM-POISON-007":
        flag_dict["goal_drift_detected"] = True
        flag_dict["mission_deviation_blocked"] = True
        flag_dict["goal_alignment_anchor_enforced"] = True
    elif eid == "MEM-POISON-008":
        flag_dict["recall_manipulation_detected"] = True
        flag_dict["retrieval_hijack_blocked"] = True
        flag_dict["retrieval_validator_enforced"] = True

    return {
        "entry_id": eid,
        "category": category,
        "scenario": entry.get("scenario", ""),
        "memory_runtime": memory_runtime,
        "memory_type": memory_type,
        "attack_technique": attack_tech,
        "interception_layer": interception_layer,
        "synthetic_threat_signature": threat_sig,
        "synthetic_session": synthetic_session,
        "synthetic_target_agent": target_agent,
        "synthetic_payload": synthetic_payload,
        "target_endpoint": target_endpoint,
        "rule_type": rule_type,
        "target_ast_depth": ast_depth,
        "control_case": False,
        "defensive_action": "refuse",
        "coordination_allowed": False,
        "memory_mutation_intercepted": True,
        "memory_operation_completed_safely": False,
        "defense_drill_blocked": not is_breakthrough,
        "defensive_check_passed": not is_breakthrough,
        "breakthrough_detected": is_breakthrough,
        "requires_human_review": True,
        "evidence_trace": evidence_trace,
        **flag_dict,
        **base_security_flags,
    }


def generate_evidence_manifest(results: list, playbook_meta: dict) -> dict:
    """Generate evidence chain manifest for audit traceability."""
    chains = []
    for r in results:
        chains.append({
            "entry_id": r["entry_id"],
            "category": r["category"],
            "control_case": r["control_case"],
            "memory_runtime": r["memory_runtime"],
            "memory_type": r["memory_type"],
            "attack_technique": r["attack_technique"],
            "interception_layer": r["interception_layer"],
            "rule_type": r["rule_type"],
            "synthetic_payload": r["synthetic_payload"],
            "synthetic_session": r["synthetic_session"],
            "synthetic_threat_signature": r["synthetic_threat_signature"],
            "target_ast_depth": r["target_ast_depth"],
            "defensive_action": r["defensive_action"],
            "defense_drill_blocked": r["defense_drill_blocked"],
            "breakthrough_detected": r["breakthrough_detected"],
            "memory_mutation_intercepted": r["memory_mutation_intercepted"],
            "memory_operation_completed_safely": r["memory_operation_completed_safely"],
            "trace_events_count": len(r["evidence_trace"]),
            "evidence_signals": [e["signal_type"] for e in r["evidence_trace"]],
            "verified_invariants": {
                "synthetic_only": r["synthetic_only"],
                "fake_runtime_only": r["fake_runtime_only"],
                "confirmed_vulnerability": r["confirmed_vulnerability"],
                "formal_finding_allowed": r["formal_finding_allowed"],
                "production_safety_claimed": r["production_safety_claimed"],
                "controlled_replay_claimed": r["controlled_replay_claimed"],
            },
        })

    return {
        "manifest_metadata": {
            "manifest_id": "phase108a_memory_evaluator_evidence_manifest_v1",
            "phase": "phase108a",
            "task_id": "Phase-108A-MEMORY-001",
            "module_id": "MEMORY_POISONING_GOAL_DRIFT_EVALUATOR",
            "module_name": "Agent Long-Term Episodic Memory Poisoning & Goal Drift Evaluator",
            "assessment_mode": "adversarial_validation",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_evidence_chains": len(chains),
            "synthetic_only": True,
            "fake_runtime_only": True,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "controlled_replay_execution_allowed": False,
            "requires_human_review": True,
        },
        "evidence_chains": chains,
    }


def main():
    print("=" * 70)
    print("Phase 108A — 跨轮会长程记忆状态污染与目标漂移评估器: Runner")
    print("Agent Long-Term Episodic Memory Poisoning & Goal Drift Evaluator")
    print("=" * 70)

    if not PLAYBOOK_PATH.exists():
        print(f"Error: Playbook not found at {PLAYBOOK_PATH}")
        sys.exit(1)

    playbook = load_playbook(PLAYBOOK_PATH)
    meta = playbook.get("playbook_metadata", {})
    entries = playbook.get("entries", [])

    print(f"\nTask ID: {meta.get('task_id')}")
    print(f"Module ID: {meta.get('module_id')}")
    print(f"Assessment Mode: {meta.get('assessment_mode')}")
    print(f"Total entries to execute: {len(entries)}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for entry in entries:
        eid = entry["entry_id"]
        res = simulate_memory_guardrail_evaluation(entry)
        results.append(res)
        status_label = "BLOCKED" if res.get("defense_drill_blocked") else ("PASSTHROUGH" if res.get("control_case") else "BREAKTHROUGH")
        print(f"  [{status_label}] Entry {eid}: {entry.get('scenario')}")

    # Write execution_results.json
    with open(EXECUTION_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved execution results to: {EXECUTION_RESULTS_PATH}")

    # Generate & write evidence_manifest.yaml
    manifest = generate_evidence_manifest(results, meta)
    with open(EVIDENCE_MANIFEST_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Saved evidence manifest to: {EVIDENCE_MANIFEST_PATH}")
    print("\nExecution complete.")


if __name__ == "__main__":
    main()
