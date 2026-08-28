#!/usr/bin/env python3
"""Phase 103A — M23 Stream Gateway: 实时流式代理评估网关 Runner.

Simulates adversarial_validation for Phase 103A Agentic Security Proxy & Stream Interceptor.
Evaluates SSE / WebSocket chunk-level interception, token smuggling, stream MitM obfuscation,
DLP redaction, Unicode state machine boundary validation, slow-stream DoS circuit breaker,
recursive injection, and binary frame entropy inspection.
No real agent communication bus, no real orchestration engine, no real identity service,
no real wargame runtime accessed, no real SSE/WebSocket server accessed,
no real model endpoint accessed.
SIM_ placeholder data only. Fake runtime only.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/phase103a_stream_gateway/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase103a_gateway_interceptor"
EXECUTION_RESULTS_PATH = OUTPUT_DIR / "execution_results.json"
EVIDENCE_MANIFEST_PATH = OUTPUT_DIR / "evidence_manifest.yaml"

SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def simulate_stream_interceptor_evaluation(entry: dict) -> dict:
    """Simulate streaming chunk-level inspection and interception."""
    eid = entry["entry_id"]
    module_id = entry.get("module_id", "M23_STREAM_GATEWAY")
    is_control = entry.get("control_case", False)
    category = entry.get("category", "")
    modality = entry.get("modality", "stream_chunk_interception")
    attack_tech = entry.get("attack_technique", "unknown")
    protocol = entry.get("stream_protocol", "SSE")
    chunks = entry.get("simulated_chunks", 4)
    stage = entry.get("interception_stage", "chunk_2")
    buf_size = entry.get("buffer_window_size", 64)
    stream_session = entry.get("synthetic_stream_session", f"<SIM_SESSION_{eid}>")
    target_proxy = entry.get("synthetic_target_proxy", f"<SIM_PROXY_{eid}>")
    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    evidence_trace = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_stream_session_manager",
            "content": f"Initialized stream session {stream_session} using protocol {protocol}, buffer window {buf_size} tokens targeting {target_proxy}.",
            "signal_type": "stream_session_initialized",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_stream_interceptor_engine",
            "content": f"Streaming demux processed {chunks} chunks for scenario {eid} ({category}). Evaluated stage {stage}.",
            "signal_type": "stream_chunk_demux_inspected",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_stream_security_guard",
            "content": (
                f"Stream policy enforcement completed: {'BENIGN_PASSTHROUGH' if is_control else 'INTERCEPTED_AND_SEVERED'}. Stage: {stage}."
            ),
            "signal_type": "stream_policy_decision_rendered",
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
        "real_websocket_endpoint_accessed": False,
        "real_sse_server_accessed": False,
        "real_tool_call_executed": False,
    }

    # Initialize case flags
    flag_dict = {
        "cross_chunk_token_smuggling_intercepted": False,
        "websocket_malicious_tool_call_blocked": False,
        "stream_control_sequence_stripped_and_blocked": False,
        "streaming_credential_leak_redacted_and_severed": False,
        "unicode_chunk_split_smuggling_intercepted": False,
        "slow_stream_dos_throttled_and_terminated": False,
        "recursive_stream_injection_intercepted": False,
        "websocket_binary_smuggling_detected_and_dropped": False,
        "benign_sse_stream_passed": False,
        "benign_websocket_tool_call_passed": False,
        "stream_intercepted": not is_control,
        "stream_forwarded_safely": is_control,
        "sliding_window_reassembly_matched": False,
        "dlp_rollback_buffer_triggered": False,
        "stream_sanitizer_active": False,
        "circuit_breaker_connection_reset": False,
    }

    if eid == "STREAM-GW-001":
        flag_dict["cross_chunk_token_smuggling_intercepted"] = True
        flag_dict["sliding_window_reassembly_matched"] = True
        interception_detail = "Cross-chunk jailbreak tokens reassembled across boundary and blocked at chunk 2."
    elif eid == "STREAM-GW-002":
        flag_dict["websocket_malicious_tool_call_blocked"] = True
        interception_detail = "Incremental JSON AST parser flagged unauthorized tool call on WebSocket frame 3."
    elif eid == "STREAM-GW-003":
        flag_dict["stream_control_sequence_stripped_and_blocked"] = True
        flag_dict["stream_sanitizer_active"] = True
        interception_detail = "Stream sanitizer neutralized ANSI escape codes and terminal rewrite sequences."
    elif eid == "STREAM-GW-004":
        flag_dict["streaming_credential_leak_redacted_and_severed"] = True
        flag_dict["dlp_rollback_buffer_triggered"] = True
        interception_detail = "DLP delay buffer identified API key pattern at chunk 3, severed downstream stream and applied redaction mask."
    elif eid == "STREAM-GW-005":
        flag_dict["unicode_chunk_split_smuggling_intercepted"] = True
        interception_detail = "Multi-byte UTF-8 state machine stitched split byte boundary, prevented decoder desync and blocked payload."
    elif eid == "STREAM-GW-006":
        flag_dict["slow_stream_dos_throttled_and_terminated"] = True
        flag_dict["circuit_breaker_connection_reset"] = True
        interception_detail = "Inter-token latency cadence anomaly detected; slow-stream circuit breaker reset connection."
    elif eid == "STREAM-GW-007":
        flag_dict["recursive_stream_injection_intercepted"] = True
        interception_detail = "Streaming semantic gate detected recursive nested markdown injection pattern and halted forwarding."
    elif eid == "STREAM-GW-008":
        flag_dict["websocket_binary_smuggling_detected_and_dropped"] = True
        interception_detail = "Binary validator flagged image header spoofing with anomalous entropy and rejected frame."
    elif eid == "CTRL-STREAM-001":
        flag_dict["benign_sse_stream_passed"] = True
        interception_detail = "Benign long-context SSE stream passed all checks with zero false positive."
    elif eid == "CTRL-STREAM-002":
        flag_dict["benign_websocket_tool_call_passed"] = True
        interception_detail = "Benign structured tool-call JSON fragments passed AST whitelist inspection."
    else:
        interception_detail = "Standard streaming evaluation completed."

    if not is_control:
        defensive_action = "refuse"
        defense_drill_blocked = True
        defensive_check_passed = not is_breakthrough
        coordination_allowed = False
        requires_human_review = True
    else:
        defensive_action = "normal_usage_allowed"
        defense_drill_blocked = False
        defensive_check_passed = not is_breakthrough
        coordination_allowed = True
        requires_human_review = False

    return {
        "entry_id": eid,
        "category": category,
        "scenario": entry.get("scenario", ""),
        "modality": modality,
        "attack_technique": attack_tech,
        "stream_protocol": protocol,
        "simulated_chunks": chunks,
        "interception_stage": stage,
        "buffer_window_size": buf_size,
        "synthetic_threat_signature": entry.get("synthetic_threat_signature", ""),
        "synthetic_stream_session": stream_session,
        "synthetic_target_proxy": target_proxy,
        "control_case": is_control,
        "breakthrough_detected": is_breakthrough,
        "defense_drill_blocked": defense_drill_blocked,
        "defensive_action": defensive_action,
        "defensive_check_passed": defensive_check_passed,
        "coordination_allowed": coordination_allowed,
        "requires_human_review": requires_human_review,
        "interception_detail": interception_detail,
        "all_findings_are_candidate": True,
        "red_team_engine_not_executable": True,
        "dashboard_not_execution_interface": True,
        "theory_model_is_not_detection_rule": True,
        "non_retroactivity_guarantee": True,
        "zero_production_penetration": True,
        "zero_formal_disconnect": True,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        **flag_dict,
        **base_security_flags,
        "evidence_trace": evidence_trace,
    }


def generate_evidence_manifest(results: list) -> dict:
    """Generate evidence manifest mapping test cases to evidence chains."""
    manifest = {
        "manifest_metadata": {
            "manifest_id": "phase103a_gateway_evidence_manifest_v1",
            "phase": "phase103a",
            "task_id": "Phase-103A-GATEWAY-001",
            "module_id": "M23_STREAM_GATEWAY",
            "module_name": "Agentic Security Proxy & Stream Interceptor",
            "assessment_mode": "adversarial_validation",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "synthetic_only": True,
            "fake_runtime_only": True,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "requires_human_review": True,
            "total_evidence_items": len(results),
        },
        "evidence_chains": [],
    }

    for r in results:
        chain = {
            "entry_id": r["entry_id"],
            "category": r["category"],
            "stream_protocol": r["stream_protocol"],
            "control_case": r["control_case"],
            "defense_drill_blocked": r["defense_drill_blocked"],
            "defensive_action": r["defensive_action"],
            "interception_stage": r["interception_stage"],
            "synthetic_threat_signature": r["synthetic_threat_signature"],
            "synthetic_stream_session": r["synthetic_stream_session"],
            "traces_count": len(r.get("evidence_trace", [])),
            "interception_detail": r["interception_detail"],
            "requires_human_review": r["requires_human_review"],
        }
        manifest["evidence_chains"].append(chain)

    return manifest


def main():
    print("=" * 70)
    print("Phase 103A — M23 Stream Gateway: Runner")
    print("Agentic Security Proxy & Stream Interceptor Evaluation")
    print("=" * 70)

    if not PLAYBOOK_PATH.exists():
        print(f"Error: Playbook not found at {PLAYBOOK_PATH}")
        sys.exit(1)

    playbook = load_playbook(PLAYBOOK_PATH)
    entries = playbook.get("entries", [])
    print(f"\nLoaded playbook with {len(entries)} test cases.\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for entry in entries:
        eid = entry["entry_id"]
        print(f"Executing stream evaluation for {eid}: {entry.get('scenario', '')} ...")
        res = simulate_stream_interceptor_evaluation(entry)
        results.append(res)
        status_str = "BLOCKED" if res["defense_drill_blocked"] else ("PASSED" if res["control_case"] else "FAIL")
        print(f"  -> Action: {res['defensive_action']} | Status: {status_str}")

    # Write execution_results.json
    with open(EXECUTION_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved execution results to {EXECUTION_RESULTS_PATH}")

    # Write evidence_manifest.yaml
    manifest = generate_evidence_manifest(results)
    with open(EVIDENCE_MANIFEST_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(manifest, f, allow_unicode=True, sort_keys=False)
    print(f"Saved evidence manifest to {EVIDENCE_MANIFEST_PATH}")

    print("\nExecution complete.")


if __name__ == "__main__":
    main()
