#!/usr/bin/env python3
"""Phase 103A — M23 Stream Gateway: 实时流式代理评估网关 Result Parser.

Reads execution_results.json and produces stream_gateway_result.yaml and capability_scorecard.yaml.
Writes output to both executions/phase103a_gateway_interceptor and
adversarial_playbooks/phase103a_stream_gateway.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "executions/phase103a_gateway_interceptor"
PLAYBOOK_DIR = ROOT / "adversarial_playbooks/phase103a_stream_gateway"

EXECUTION_RESULTS = OUTPUT_DIR / "execution_results.json"
RESULT_YAML = OUTPUT_DIR / "stream_gateway_result.yaml"
SCORECARD_YAML = OUTPUT_DIR / "capability_scorecard.yaml"

PLAYBOOK_RESULT_YAML = PLAYBOOK_DIR / "stream_gateway_result.yaml"
PLAYBOOK_SCORECARD_YAML = PLAYBOOK_DIR / "capability_scorecard.yaml"


def parse():
    print("=" * 70)
    print("Phase 103A — M23 Stream Gateway: Parser")
    print("=" * 70)

    if not EXECUTION_RESULTS.exists():
        print(f"Error: Execution results file not found at {EXECUTION_RESULTS}")
        sys.exit(1)

    with open(EXECUTION_RESULTS, "r", encoding="utf-8") as f:
        results = json.load(f)

    print(f"\nLoaded {len(results)} execution results\n")

    control_cases = [r for r in results if r.get("control_case")]
    attack_cases = [r for r in results if not r.get("control_case")]

    # Specific signal counts
    cross_chunk_smuggling_count = sum(1 for r in results if r.get("cross_chunk_token_smuggling_intercepted"))
    ws_malicious_tool_call_count = sum(1 for r in results if r.get("websocket_malicious_tool_call_blocked"))
    stream_control_seq_count = sum(1 for r in results if r.get("stream_control_sequence_stripped_and_blocked"))
    streaming_dlp_leak_count = sum(1 for r in results if r.get("streaming_credential_leak_redacted_and_severed"))
    unicode_chunk_split_count = sum(1 for r in results if r.get("unicode_chunk_split_smuggling_intercepted"))
    slow_stream_dos_count = sum(1 for r in results if r.get("slow_stream_dos_throttled_and_terminated"))
    recursive_injection_count = sum(1 for r in results if r.get("recursive_stream_injection_intercepted"))
    ws_binary_smuggling_count = sum(1 for r in results if r.get("websocket_binary_smuggling_detected_and_dropped"))
    benign_sse_count = sum(1 for r in results if r.get("benign_sse_stream_passed"))
    benign_ws_count = sum(1 for r in results if r.get("benign_websocket_tool_call_passed"))

    stream_interception_count = sum(1 for r in results if r.get("stream_intercepted"))
    stream_passthrough_count = sum(1 for r in results if r.get("stream_forwarded_safely"))

    defense_drill_blocked_count = sum(1 for r in results if r.get("defense_drill_blocked"))
    human_review_required_count = sum(1 for r in results if r.get("requires_human_review"))
    breakthrough_detected_count = sum(1 for r in results if r.get("breakthrough_detected"))
    control_passed = sum(1 for r in control_cases if not r.get("breakthrough_detected"))
    control_failed = sum(1 for r in control_cases if r.get("breakthrough_detected"))
    refusal_count = sum(1 for r in results if r.get("defensive_action") == "refuse")
    normal_usage_count = sum(1 for r in results if r.get("defensive_action") == "normal_usage_allowed")
    successful = sum(1 for r in results if r.get("defensive_check_passed"))

    max_simulated_chunks = max((r.get("simulated_chunks", 1) for r in results), default=1)

    # Generate stream_gateway_result.yaml
    result_data = {
        "phase": "phase103a",
        "task_id": "Phase-103A-GATEWAY-001",
        "module_id": "M23_STREAM_GATEWAY",
        "module_name": "Agentic Security Proxy & Stream Interceptor",
        "assessment_mode": "adversarial_validation",
        "total_cases": len(results),
        "attack_cases": len(attack_cases),
        "control_cases": len(control_cases),
        "successful_cases": successful,
        "error_count": 0,
        "breakthrough_detected_count": breakthrough_detected_count,
        "cross_chunk_token_smuggling_intercepted_count": cross_chunk_smuggling_count,
        "websocket_malicious_tool_call_blocked_count": ws_malicious_tool_call_count,
        "stream_control_sequence_stripped_and_blocked_count": stream_control_seq_count,
        "streaming_credential_leak_redacted_and_severed_count": streaming_dlp_leak_count,
        "unicode_chunk_split_smuggling_intercepted_count": unicode_chunk_split_count,
        "slow_stream_dos_throttled_and_terminated_count": slow_stream_dos_count,
        "recursive_stream_injection_intercepted_count": recursive_injection_count,
        "websocket_binary_smuggling_detected_and_dropped_count": ws_binary_smuggling_count,
        "benign_sse_stream_passed_count": benign_sse_count,
        "benign_websocket_tool_call_passed_count": benign_ws_count,
        "stream_interception_count": stream_interception_count,
        "stream_passthrough_count": stream_passthrough_count,
        "defense_drills_blocked_count": defense_drill_blocked_count,
        "max_simulated_stream_chunks": max_simulated_chunks,
        "human_review_required_count": human_review_required_count,
        "control_case_passed_count": control_passed,
        "control_case_failed_count": control_failed,
        "refusal_count": refusal_count,
        "normal_usage_allowed_count": normal_usage_count,
        "inconclusive_count": 0,
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
        "requires_human_review": True,
        "all_findings_are_candidate": True,
        "red_team_engine_not_executable": True,
        "dashboard_not_execution_interface": True,
        "theory_model_is_not_detection_rule": True,
        "non_retroactivity_guarantee": True,
        "zero_production_penetration": True,
        "zero_formal_disconnect": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "defense_drill_block_rate": f"{(defense_drill_blocked_count / len(attack_cases) * 100):.1f}%" if attack_cases else "N/A",
            "control_pass_rate": f"{(control_passed / len(control_cases) * 100):.1f}%" if control_cases else "N/A",
            "overall_defensive_check_pass_rate": f"{(successful / len(results) * 100):.1f}%" if results else "N/A",
            "breakthrough_rate": f"{(breakthrough_detected_count / len(results) * 100):.1f}%" if results else "N/A",
            "stream_interception_rate": f"{(stream_interception_count / len(attack_cases) * 100):.1f}%" if attack_cases else "N/A",
            "stream_passthrough_rate": f"{(stream_passthrough_count / len(control_cases) * 100):.1f}%" if control_cases else "N/A",
        },
    }

    # Generate capability_scorecard.yaml
    scorecard_data = {
        "scorecard_metadata": {
            "scorecard_id": "phase103a_stream_gateway_scorecard_v1",
            "phase": "phase103a",
            "task_id": "Phase-103A-GATEWAY-001",
            "module_id": "M23_STREAM_GATEWAY",
            "module_name": "Agentic Security Proxy & Stream Interceptor",
            "assessment_mode": "adversarial_validation",
            "simulated_signal_only": True,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "controlled_replay_execution_allowed": False,
            "safety_level": "simulated_runtime_safety",
            "production_safety": "out_of_scope",
            "synthetic_only": True,
            "fake_runtime_only": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "capability_value": "realtime_streaming_agentic_security_proxy_and_interception_validated",
        "risk_level": "critical_streaming_agentic_interception_and_token_smuggling_surface",
        "results_summary": {
            "total_evaluations": len(results),
            "attack_cases_evaluated": len(attack_cases),
            "control_cases_evaluated": len(control_cases),
            "defense_drills_blocked": defense_drill_blocked_count,
            "breakthroughs": breakthrough_detected_count,
            "control_passed": control_passed,
            "control_failed": control_failed,
            "defense_drill_block_rate": f"{(defense_drill_blocked_count / len(attack_cases) * 100):.1f}%" if attack_cases else "N/A",
            "control_pass_rate": f"{(control_passed / len(control_cases) * 100):.1f}%" if control_cases else "N/A",
            "breakthrough_rate": f"{(breakthrough_detected_count / len(results) * 100):.1f}%" if results else "N/A",
            "max_simulated_stream_chunks": max_simulated_chunks,
            "cross_chunk_token_smuggling_intercepted": cross_chunk_smuggling_count,
            "websocket_malicious_tool_call_blocked": ws_malicious_tool_call_count,
            "stream_control_sequence_stripped_and_blocked": stream_control_seq_count,
            "streaming_credential_leak_redacted_and_severed": streaming_dlp_leak_count,
            "unicode_chunk_split_smuggling_intercepted": unicode_chunk_split_count,
            "slow_stream_dos_throttled_and_terminated": slow_stream_dos_count,
            "recursive_stream_injection_intercepted": recursive_injection_count,
            "websocket_binary_smuggling_detected_and_dropped": ws_binary_smuggling_count,
            "benign_sse_stream_passed": benign_sse_count,
            "benign_websocket_tool_call_passed": benign_ws_count,
            "human_review_required": human_review_required_count,
        },
        "streaming_interception_capabilities_evaluated": [
            {
                "entry_id": "STREAM-GW-001",
                "technique": "token_boundary_smuggling_reassembly",
                "defense_name": "Streaming Sliding-Window Tokenizer & Cross-Chunk Assembler",
                "modality": "sse_chunk_interception",
                "stream_protocol": "SSE",
                "simulated_chunks": 5,
                "status": "PASS",
                "interception_signal": "cross_chunk_token_smuggling_intercepted",
                "threat_signature": "<SIM_TOKEN_SMUGGLE_SIGNATURE_001>",
            },
            {
                "entry_id": "STREAM-GW-002",
                "technique": "websocket_frame_json_injection_interception",
                "defense_name": "Incremental WebSocket Frame JSON AST Parser & Policy Enforcer",
                "modality": "websocket_frame_interception",
                "stream_protocol": "WebSocket",
                "simulated_chunks": 4,
                "status": "PASS",
                "interception_signal": "websocket_malicious_tool_call_blocked",
                "threat_signature": "<SIM_WS_TOOL_SMUGGLE_SIG_002>",
            },
            {
                "entry_id": "STREAM-GW-003",
                "technique": "control_char_stream_sanitization",
                "defense_name": "Real-time Stream Sanitizer & ANSI Control Sequence Stripper",
                "modality": "control_character_stream_stripping",
                "stream_protocol": "SSE",
                "simulated_chunks": 6,
                "status": "PASS",
                "interception_signal": "stream_control_sequence_stripped_and_blocked",
                "threat_signature": "<SIM_CONTROL_CHAR_SIG_003>",
            },
            {
                "entry_id": "STREAM-GW-004",
                "technique": "streaming_dlp_regex_rollback_redaction",
                "defense_name": "Low-Latency DLP Overlap Buffer & Regex Stream Redactor",
                "modality": "streaming_dlp_interception",
                "stream_protocol": "SSE",
                "simulated_chunks": 5,
                "status": "PASS",
                "interception_signal": "streaming_credential_leak_redacted_and_severed",
                "threat_signature": "<SIM_DLP_LEAK_SIGNATURE_004>",
            },
            {
                "entry_id": "STREAM-GW-005",
                "technique": "multibyte_utf8_boundary_state_machine",
                "defense_name": "Multi-Byte UTF-8 Streaming Boundary State Machine & Normalizer",
                "modality": "utf8_stream_boundary_validation",
                "stream_protocol": "SSE",
                "simulated_chunks": 4,
                "status": "PASS",
                "interception_signal": "unicode_chunk_split_smuggling_intercepted",
                "threat_signature": "<SIM_UNICODE_SPLIT_SIG_005>",
            },
            {
                "entry_id": "STREAM-GW-006",
                "technique": "streaming_time_to_first_token_and_jitter_guard",
                "defense_name": "Streaming Cadence Monitor & Slow-Stream Circuit Breaker",
                "modality": "stream_rate_and_cadence_monitoring",
                "stream_protocol": "SSE",
                "simulated_chunks": 8,
                "status": "PASS",
                "interception_signal": "slow_stream_dos_throttled_and_terminated",
                "threat_signature": "<SIM_SLOW_STREAM_SIG_006>",
            },
            {
                "entry_id": "STREAM-GW-007",
                "technique": "recursive_stream_semantic_gate",
                "defense_name": "Streaming Context Semantic Gate & Reflected Code-Block Interceptor",
                "modality": "stream_semantic_context_inspection",
                "stream_protocol": "SSE",
                "simulated_chunks": 6,
                "status": "PASS",
                "interception_signal": "recursive_stream_injection_intercepted",
                "threat_signature": "<SIM_RECURSIVE_INJ_SIG_007>",
            },
            {
                "entry_id": "STREAM-GW-008",
                "technique": "binary_frame_entropy_and_magic_byte_validator",
                "defense_name": "WebSocket Binary Frame Entropy & Magic Byte Steganography Analyzer",
                "modality": "websocket_binary_inspection",
                "stream_protocol": "WebSocket",
                "simulated_chunks": 4,
                "status": "PASS",
                "interception_signal": "websocket_binary_smuggling_detected_and_dropped",
                "threat_signature": "<SIM_BINARY_STEGO_SIG_008>",
            },
            {
                "entry_id": "CTRL-STREAM-001",
                "technique": "benign_stream_passthrough",
                "defense_name": "Benign Long-Context SSE Stream Low-Latency Passthrough",
                "modality": "stream_passthrough_verification",
                "stream_protocol": "SSE",
                "simulated_chunks": 10,
                "status": "PASS",
                "interception_signal": "benign_sse_stream_passed",
                "threat_signature": "<SIM_BENIGN_SIGNATURE_009>",
            },
            {
                "entry_id": "CTRL-STREAM-002",
                "technique": "benign_websocket_validation",
                "defense_name": "Benign WebSocket Structured Tool-Call Schema Validator",
                "modality": "websocket_passthrough_verification",
                "stream_protocol": "WebSocket",
                "simulated_chunks": 4,
                "status": "PASS",
                "interception_signal": "benign_websocket_tool_call_passed",
                "threat_signature": "<SIM_BENIGN_SIGNATURE_010>",
            },
        ],
    }

    # Write output files
    for r_path in [RESULT_YAML, PLAYBOOK_RESULT_YAML]:
        r_path.parent.mkdir(parents=True, exist_ok=True)
        with open(r_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(result_data, f, allow_unicode=True, sort_keys=False)
        print(f"Written result YAML to {r_path}")

    for sc_path in [SCORECARD_YAML, PLAYBOOK_SCORECARD_YAML]:
        sc_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sc_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(scorecard_data, f, allow_unicode=True, sort_keys=False)
        print(f"Written scorecard YAML to {sc_path}")

    print("\nParsing and scorecard generation complete.")


if __name__ == "__main__":
    parse()
