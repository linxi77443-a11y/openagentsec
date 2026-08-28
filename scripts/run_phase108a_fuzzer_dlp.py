#!/usr/bin/env python3
"""Phase 108A — 自动化语义变异模糊测试生成器与实时输出 DLP 护栏 Runner.

Simulates adversarial_validation for Phase 108A Automated Semantic Fuzzing Generator & Real-Time Output DLP Guardrail.
Evaluates Unicode homoglyph/zero-width mutations, multi-layer nested encoding evasion,
cross-turn context splitting and reassembly, Markdown OOB image/hyperlink exfiltration,
system prompt reverse extraction, synthetic credential/JWT leakage induction,
internal network topology fingerprint leakage, adversarial metaphor camouflage,
and benign technical documentation / troubleshooting guidance controls.
No real model endpoint accessed, no real network egress dispatched, no real DLP production engine contacted.
SIM_ placeholder data only. Fake runtime only.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/phase108a_fuzzer_dlp/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase108a_fuzzer_dlp"
EXECUTION_RESULTS_PATH = OUTPUT_DIR / "execution_results.json"
EVIDENCE_MANIFEST_PATH = OUTPUT_DIR / "evidence_manifest.yaml"

SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def simulate_fuzzer_dlp_evaluation(entry: dict) -> dict:
    """Simulate streaming output DLP guardrail defense interception in Fake Runtime."""
    eid = entry["entry_id"]
    module_id = entry.get("module_id", "SEMANTIC_FUZZER_DLP_GUARDRAIL")
    is_control = entry.get("control_case", False)
    category = entry.get("category", "")
    fuzz_runtime = entry.get("fuzz_runtime", f"<SIM_RUNTIME_FUZZ_{eid}>")
    attack_tech = entry.get("attack_technique", "unknown")
    stream_type = entry.get("stream_type", "token_stream_dlp")
    ast_depth = entry.get("target_ast_depth", 1)
    interception_layer = entry.get("interception_layer", "streaming_credential_regex_entropy_dlp_guard")
    threat_sig = entry.get("synthetic_threat_signature", f"<SIM_FUZZ_SIG_{eid}>")
    synthetic_session = entry.get("synthetic_session", f"<SIM_DLP_SESSION_{eid}>")
    target_agent = entry.get("synthetic_target_agent", f"<SIM_AGENT_DLP_{eid}>")
    synthetic_payload = entry.get("synthetic_payload", f"<SIM_PAYLOAD_{eid}>")
    target_endpoint = entry.get("target_endpoint", f"<SIM_DLP_STREAM_ENDPOINT_{eid}>")
    rule_type = entry.get("rule_type", "unknown_rule")
    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    evidence_trace = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_stream_token_dispatch",
            "content": f"Received synthetic streaming output chunks for runtime {fuzz_runtime} ({stream_type}) from agent {target_agent} in session {synthetic_session}.",
            "signal_type": "stream_chunks_received",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_streaming_dlp_and_fuzzing_analyzer",
            "content": f"Inspected semantic mutation, decoding entropy and streaming token buffer at layer '{interception_layer}' for scenario {eid} ({category}) at AST depth {ast_depth}. Evaluated rule '{rule_type}'.",
            "signal_type": "streaming_dlp_mutation_inspected",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_fake_runtime_stream_dlp_guardrail",
            "content": (
                f"Stream DLP Guardrail enforcement decision: {'BENIGN_STREAM_PASSTHROUGH' if is_control else 'STREAM_INTERCEPTED_AND_REDACTED'}. Layer: {interception_layer}."
            ),
            "signal_type": "stream_dlp_security_decision_rendered",
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
        "real_network_egress_attempted": False,
        "real_thought_stream_accessed": False,
    }

    flag_dict = {
        "unicode_homoglyph_mutation_detected": False,
        "zero_width_character_blocked": False,
        "dlp_normalization_policy_enforced": False,
        "nested_encoding_evasion_detected": False,
        "recursive_decoding_blocked": False,
        "encoding_depth_limiter_enforced": False,
        "context_splitting_detected": False,
        "reassembly_fragmentation_blocked": False,
        "session_sliding_window_enforced": False,
        "markdown_oob_exfiltration_detected": False,
        "beacon_rendering_blocked": False,
        "markdown_ast_sanitizer_enforced": False,
        "system_prompt_extraction_detected": False,
        "meta_instruction_leakage_blocked": False,
        "streaming_dlp_guard_enforced": False,
        "credential_leakage_detected": False,
        "api_key_jwt_exfiltration_blocked": False,
        "streaming_entropy_dlp_enforced": False,
        "network_topology_leakage_detected": False,
        "infrastructure_fingerprint_blocked": False,
        "topology_masker_enforced": False,
        "adversarial_metaphor_detected": False,
        "semantic_camouflage_blocked": False,
        "intent_unwrapping_guard_enforced": False,
        "benign_technical_doc_validated": False,
        "benign_troubleshooting_guidance_validated": False,
        "stream_output_completed_safely": False,
        "stream_dlp_completed_safely": False,
    }

    if is_control:
        if eid == "CTRL-DLP-001":
            flag_dict["benign_technical_doc_validated"] = True
            flag_dict["stream_output_completed_safely"] = True
        elif eid == "CTRL-DLP-002":
            flag_dict["benign_troubleshooting_guidance_validated"] = True
            flag_dict["stream_dlp_completed_safely"] = True

        return {
            "entry_id": eid,
            "category": category,
            "scenario": entry.get("scenario", ""),
            "fuzz_runtime": fuzz_runtime,
            "stream_type": stream_type,
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
            "stream_dlp_intercepted": False,
            "stream_output_completed_safely": True,
            "defense_drill_blocked": False,
            "defensive_check_passed": True,
            "breakthrough_detected": False,
            "requires_human_review": False,
            "evidence_trace": evidence_trace,
            **flag_dict,
            **base_security_flags,
        }

    # Adversarial cases
    if eid == "FUZZ-DLP-001":
        flag_dict["unicode_homoglyph_mutation_detected"] = True
        flag_dict["zero_width_character_blocked"] = True
        flag_dict["dlp_normalization_policy_enforced"] = True
    elif eid == "FUZZ-DLP-002":
        flag_dict["nested_encoding_evasion_detected"] = True
        flag_dict["recursive_decoding_blocked"] = True
        flag_dict["encoding_depth_limiter_enforced"] = True
    elif eid == "FUZZ-DLP-003":
        flag_dict["context_splitting_detected"] = True
        flag_dict["reassembly_fragmentation_blocked"] = True
        flag_dict["session_sliding_window_enforced"] = True
    elif eid == "FUZZ-DLP-004":
        flag_dict["markdown_oob_exfiltration_detected"] = True
        flag_dict["beacon_rendering_blocked"] = True
        flag_dict["markdown_ast_sanitizer_enforced"] = True
    elif eid == "FUZZ-DLP-005":
        flag_dict["system_prompt_extraction_detected"] = True
        flag_dict["meta_instruction_leakage_blocked"] = True
        flag_dict["streaming_dlp_guard_enforced"] = True
    elif eid == "FUZZ-DLP-006":
        flag_dict["credential_leakage_detected"] = True
        flag_dict["api_key_jwt_exfiltration_blocked"] = True
        flag_dict["streaming_entropy_dlp_enforced"] = True
    elif eid == "FUZZ-DLP-007":
        flag_dict["network_topology_leakage_detected"] = True
        flag_dict["infrastructure_fingerprint_blocked"] = True
        flag_dict["topology_masker_enforced"] = True
    elif eid == "FUZZ-DLP-008":
        flag_dict["adversarial_metaphor_detected"] = True
        flag_dict["semantic_camouflage_blocked"] = True
        flag_dict["intent_unwrapping_guard_enforced"] = True

    return {
        "entry_id": eid,
        "category": category,
        "scenario": entry.get("scenario", ""),
        "fuzz_runtime": fuzz_runtime,
        "stream_type": stream_type,
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
        "stream_dlp_intercepted": True,
        "stream_output_completed_safely": False,
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
            "fuzz_runtime": r["fuzz_runtime"],
            "stream_type": r["stream_type"],
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
            "stream_dlp_intercepted": r["stream_dlp_intercepted"],
            "stream_output_completed_safely": r["stream_output_completed_safely"],
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
            "manifest_id": "phase108a_fuzzer_dlp_evidence_manifest_v1",
            "phase": "phase108a",
            "task_id": "Phase-108A-FUZZER-002",
            "module_id": "SEMANTIC_FUZZER_DLP_GUARDRAIL",
            "module_name": "Automated Semantic Fuzzing Generator & Real-Time Output DLP Guardrail",
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
    print("Phase 108A — 自动化语义变异模糊测试生成器与实时输出 DLP 护栏: Runner")
    print("Automated Semantic Fuzzing Generator & Real-Time Output DLP Guardrail")
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
        res = simulate_fuzzer_dlp_evaluation(entry)
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
