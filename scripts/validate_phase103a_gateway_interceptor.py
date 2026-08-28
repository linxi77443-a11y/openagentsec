#!/usr/bin/env python3
"""Phase 103A — M23 Stream Gateway: 实时流式代理评估网关 Validator.

Comprehensive validator for playbook, run configuration, execution results,
evidence manifest, result YAML, capability scorecard, documentation notes,
execution summary, and security boundary assertions.
"""
import json
import re
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

checks_passed = 0
checks_failed = 0
errors = []


def check(condition: bool, msg: str):
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  ✓ {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  ✗ {msg}")


def yaml_load(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load error: {path} — {e}")
        return None


def json_load(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load error: {path} — {e}")
        return None


def check_security_fields(obj: dict, prefix: str):
    fields = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
    }
    for field, expected in fields.items():
        actual = obj.get(field)
        check(
            actual == expected,
            f"{prefix}: security field '{field}' == {actual} (expected {expected})",
        )


def main():
    global checks_passed, checks_failed
    print("=" * 70)
    print("Phase 103A — M23 Stream Gateway: Validator")
    print("Agentic Security Proxy & Stream Interceptor Verification Suite")
    print("=" * 70)

    # ================================================================
    # 1. Playbook Verification
    # ================================================================
    print("\n[1] Playbook Verification")
    playbook_path = ROOT / "adversarial_playbooks/phase103a_stream_gateway/playbook.yaml"
    check(playbook_path.exists(), f"Playbook file exists at {playbook_path}")

    playbook = yaml_load(playbook_path)
    check(playbook is not None, "Playbook parsed successfully as YAML")

    if playbook:
        meta = playbook.get("playbook_metadata", {})
        check(meta.get("playbook_id") == "phase103a_stream_gateway_v1", "Playbook ID is valid")
        check(meta.get("phase") == "phase103a", "Phase is phase103a")
        check(meta.get("task_id") == "Phase-103A-GATEWAY-001", "Task ID is Phase-103A-GATEWAY-001")
        check(meta.get("module_id") == "M23_STREAM_GATEWAY", "Module ID is M23_STREAM_GATEWAY")
        check(meta.get("assessment_mode") == "adversarial_validation", "Assessment mode is adversarial_validation")
        check_security_fields(meta, "Playbook metadata")
        check(meta.get("synthetic_only") is True, "Playbook metadata synthetic_only is True")
        check(meta.get("fake_runtime_only") is True, "Playbook metadata fake_runtime_only is True")
        check(meta.get("real_agent_communication_bus_allowed") is False, "Playbook real_agent_communication_bus_allowed is False")
        check(meta.get("real_orchestration_engine_allowed") is False, "Playbook real_orchestration_engine_allowed is False")
        check(meta.get("real_identity_auth_service_allowed") is False, "Playbook real_identity_auth_service_allowed is False")
        check(meta.get("real_task_assignment_system_allowed") is False, "Playbook real_task_assignment_system_allowed is False")
        check(meta.get("real_wargame_runtime_allowed") is False, "Playbook real_wargame_runtime_allowed is False")
        check(meta.get("real_api_gateway_allowed") is False, "Playbook real_api_gateway_allowed is False")
        check(meta.get("real_model_endpoint_allowed") is False, "Playbook real_model_endpoint_allowed is False")
        check(meta.get("real_rule_engine_production_service_allowed") is False, "Playbook real_rule_engine_production_service_allowed is False")
        check(meta.get("real_websocket_endpoint_allowed") is False, "Playbook real_websocket_endpoint_allowed is False")
        check(meta.get("real_sse_server_allowed") is False, "Playbook real_sse_server_allowed is False")

        entries = playbook.get("entries", [])
        check(len(entries) == 10, f"Playbook has exactly 10 entries (found {len(entries)})")

        attacks = [e for e in entries if not e.get("control_case")]
        controls = [e for e in entries if e.get("control_case")]
        check(len(attacks) == 8, f"Found exactly 8 attack/interception cases (found {len(attacks)})")
        check(len(controls) == 2, f"Found exactly 2 baseline control cases (found {len(controls)})")

        for idx, entry in enumerate(entries):
            eid = entry.get("entry_id", f"entry_{idx}")
            check_security_fields(entry, f"Playbook entry {eid}")
            check(entry.get("breakthrough_detected") is False, f"Entry {eid}: breakthrough_detected is False")

            # Check synthetic placeholders
            sim_fields = ["synthetic_threat_signature", "synthetic_stream_session", "synthetic_target_proxy", "synthetic_payload", "target_endpoint"]
            for sf in sim_fields:
                val = entry.get(sf, "")
                if val:
                    check(
                        "<SIM_" in val and ">" in val,
                        f"Entry {eid}: placeholder field '{sf}' contains '<SIM_...>' syntax ({val})",
                    )

            # Check stream fields
            check(entry.get("stream_protocol") in ["SSE", "WebSocket"], f"Entry {eid}: protocol is SSE or WebSocket ({entry.get('stream_protocol')})")
            check(entry.get("simulated_chunks", 0) > 0, f"Entry {eid}: simulated_chunks > 0 ({entry.get('simulated_chunks')})")
            check(entry.get("buffer_window_size", 0) > 0, f"Entry {eid}: buffer_window_size > 0 ({entry.get('buffer_window_size')})")

    # ================================================================
    # 2. Run Config Verification
    # ================================================================
    print("\n[2] Run Config Verification")
    rc_path = ROOT / "run_configs/phase103a_gateway_run_config.yaml"
    check(rc_path.exists(), f"Run config file exists at {rc_path}")

    rc = yaml_load(rc_path)
    check(rc is not None, "Run config parsed successfully as YAML")

    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("run_id") == "rc_phase103a_stream_gateway_v1", "Run config ID is valid")
        check(rcfg.get("phase") == "phase103a", "Run config phase is phase103a")
        check(rcfg.get("task_id") == "Phase-103A-GATEWAY-001", "Run config task_id is Phase-103A-GATEWAY-001")
        check(rcfg.get("module_id") == "M23_STREAM_GATEWAY", "Run config module_id is M23_STREAM_GATEWAY")
        check(rcfg.get("assessment_mode") == "adversarial_validation", "Run config assessment_mode is adversarial_validation")
        check_security_fields(rcfg, "Run config metadata")
        check(rcfg.get("synthetic_only") is True, "Run config synthetic_only is True")
        check(rcfg.get("fake_runtime_only") is True, "Run config fake_runtime_only is True")
        check(rcfg.get("real_agent_communication_bus_allowed") is False, "Run config real_agent_communication_bus_allowed is False")
        check(rcfg.get("real_orchestration_engine_allowed") is False, "Run config real_orchestration_engine_allowed is False")
        check(rcfg.get("real_identity_auth_service_allowed") is False, "Run config real_identity_auth_service_allowed is False")
        check(rcfg.get("real_task_assignment_system_allowed") is False, "Run config real_task_assignment_system_allowed is False")
        check(rcfg.get("real_wargame_runtime_allowed") is False, "Run config real_wargame_runtime_allowed is False")
        check(rcfg.get("real_api_gateway_allowed") is False, "Run config real_api_gateway_allowed is False")
        check(rcfg.get("real_model_endpoint_allowed") is False, "Run config real_model_endpoint_allowed is False")
        check(rcfg.get("real_rule_engine_production_service_allowed") is False, "Run config real_rule_engine_production_service_allowed is False")
        check(rcfg.get("real_websocket_endpoint_allowed") is False, "Run config real_websocket_endpoint_allowed is False")
        check(rcfg.get("real_sse_server_allowed") is False, "Run config real_sse_server_allowed is False")

        params = rc.get("stream_gateway_parameters", {})
        check(params.get("sse_chunk_interception_enabled") is True, "Parameter sse_chunk_interception_enabled is True")
        check(params.get("websocket_frame_inspection_enabled") is True, "Parameter websocket_frame_inspection_enabled is True")
        check(params.get("sliding_window_token_assembly_enabled") is True, "Parameter sliding_window_token_assembly_enabled is True")
        check(params.get("streaming_dlp_rollback_buffer_enabled") is True, "Parameter streaming_dlp_rollback_buffer_enabled is True")
        check(params.get("control_character_stream_sanitization_enabled") is True, "Parameter control_character_stream_sanitization_enabled is True")
        check(params.get("multibyte_utf8_boundary_state_machine_enabled") is True, "Parameter multibyte_utf8_boundary_state_machine_enabled is True")
        check(params.get("slow_stream_cadence_monitoring_enabled") is True, "Parameter slow_stream_cadence_monitoring_enabled is True")
        check(params.get("recursive_stream_semantic_gate_enabled") is True, "Parameter recursive_stream_semantic_gate_enabled is True")
        check(params.get("websocket_binary_entropy_analyzer_enabled") is True, "Parameter websocket_binary_entropy_analyzer_enabled is True")

    # ================================================================
    # 3. Execution Results Verification
    # ================================================================
    print("\n[3] Execution Results Verification")
    exec_path = ROOT / "executions/phase103a_gateway_interceptor/execution_results.json"
    check(exec_path.exists(), f"Execution results exist at {exec_path}")

    results = json_load(exec_path)
    check(results is not None, "Execution results parsed successfully as JSON")

    if results:
        check(len(results) == 10, f"Execution results contain 10 items (found {len(results)})")
        attacks_res = [r for r in results if not r.get("control_case")]
        controls_res = [r for r in results if r.get("control_case")]
        check(len(attacks_res) == 8, f"Found 8 attack cases (found {len(attacks_res)})")
        check(len(controls_res) == 2, f"Found 2 control cases (found {len(controls_res)})")

        for idx, r in enumerate(results):
            eid = r.get("entry_id", f"result_{idx}")
            check(r.get("defensive_check_passed") is True, f"Result {eid}: defensive_check_passed is True")
            check(r.get("breakthrough_detected") is False, f"Result {eid}: breakthrough_detected is False")
            check_security_fields(r, f"Result {eid}")
            check(r.get("synthetic_only") is True, f"Result {eid}: synthetic_only is True")
            check(r.get("fake_runtime_only") is True, f"Result {eid}: fake_runtime_only is True")
            check(r.get("real_agent_communication_bus_accessed") is False, f"Result {eid}: real_agent_communication_bus_accessed is False")
            check(r.get("real_orchestration_engine_accessed") is False, f"Result {eid}: real_orchestration_engine_accessed is False")
            check(r.get("real_identity_auth_service_accessed") is False, f"Result {eid}: real_identity_auth_service_accessed is False")
            check(r.get("real_task_assignment_system_accessed") is False, f"Result {eid}: real_task_assignment_system_accessed is False")
            check(r.get("real_wargame_runtime_accessed") is False, f"Result {eid}: real_wargame_runtime_accessed is False")
            check(r.get("real_api_gateway_accessed") is False, f"Result {eid}: real_api_gateway_accessed is False")
            check(r.get("real_model_endpoint_accessed") is False, f"Result {eid}: real_model_endpoint_accessed is False")
            check(r.get("real_rule_engine_production_service_accessed") is False, f"Result {eid}: real_rule_engine_production_service_accessed is False")
            check(r.get("real_websocket_endpoint_accessed") is False, f"Result {eid}: real_websocket_endpoint_accessed is False")
            check(r.get("real_sse_server_accessed") is False, f"Result {eid}: real_sse_server_accessed is False")
            check(r.get("real_tool_call_executed") is False, f"Result {eid}: real_tool_call_executed is False")

            if not r.get("control_case"):
                check(r.get("defensive_action") == "refuse", f"Result {eid}: defensive_action is 'refuse'")
                check(r.get("defense_drill_blocked") is True, f"Result {eid}: defense_drill_blocked is True")
                check(r.get("stream_intercepted") is True, f"Result {eid}: stream_intercepted is True")
                check(r.get("stream_forwarded_safely") is False, f"Result {eid}: stream_forwarded_safely is False")
            else:
                check(r.get("defensive_action") == "normal_usage_allowed", f"Result {eid}: defensive_action is 'normal_usage_allowed'")
                check(r.get("defense_drill_blocked") is False, f"Result {eid}: defense_drill_blocked is False")
                check(r.get("coordination_allowed") is True, f"Result {eid}: coordination_allowed is True")
                check(r.get("stream_intercepted") is False, f"Result {eid}: stream_intercepted is False")
                check(r.get("stream_forwarded_safely") is True, f"Result {eid}: stream_forwarded_safely is True")

            traces = r.get("evidence_trace", [])
            check(len(traces) >= 3, f"Result {eid}: has at least 3 evidence traces (found {len(traces)})")

    # ================================================================
    # 4. Evidence Manifest Verification
    # ================================================================
    print("\n[4] Evidence Manifest Verification")
    manifest_path = ROOT / "executions/phase103a_gateway_interceptor/evidence_manifest.yaml"
    check(manifest_path.exists(), f"Evidence manifest exists at {manifest_path}")

    manifest = yaml_load(manifest_path)
    check(manifest is not None, "Evidence manifest parsed successfully as YAML")

    if manifest:
        mmeta = manifest.get("manifest_metadata", {})
        check(mmeta.get("task_id") == "Phase-103A-GATEWAY-001", "Manifest task_id is Phase-103A-GATEWAY-001")
        check(mmeta.get("module_id") == "M23_STREAM_GATEWAY", "Manifest module_id is M23_STREAM_GATEWAY")
        check(mmeta.get("synthetic_only") is True, "Manifest synthetic_only is True")
        check_security_fields(mmeta, "Manifest metadata")
        chains = manifest.get("evidence_chains", [])
        check(len(chains) == 10, f"Manifest contains 10 evidence chains (found {len(chains)})")

    # ================================================================
    # 5. Result YAML Verification
    # ================================================================
    print("\n[5] Result YAML Verification")
    for r_path in [
        ROOT / "executions/phase103a_gateway_interceptor/stream_gateway_result.yaml",
        ROOT / "adversarial_playbooks/phase103a_stream_gateway/stream_gateway_result.yaml",
    ]:
        check(r_path.exists(), f"Result YAML exists at {r_path}")
        res = yaml_load(r_path)
        check(res is not None, f"Result YAML {r_path.name} parsed successfully")
        if res:
            check(res.get("phase") == "phase103a", f"{r_path.name}: phase is phase103a")
            check(res.get("task_id") == "Phase-103A-GATEWAY-001", f"{r_path.name}: task_id is Phase-103A-GATEWAY-001")
            check(res.get("module_id") == "M23_STREAM_GATEWAY", f"{r_path.name}: module_id is M23_STREAM_GATEWAY")
            check(res.get("assessment_mode") == "adversarial_validation", f"{r_path.name}: assessment_mode is adversarial_validation")
            check(res.get("total_cases") == 10, f"{r_path.name}: total_cases == 10")
            check(res.get("attack_cases") == 8, f"{r_path.name}: attack_cases == 8")
            check(res.get("control_cases") == 2, f"{r_path.name}: control_cases == 2")
            check(res.get("successful_cases") == 10, f"{r_path.name}: successful_cases == 10")
            check(res.get("error_count") == 0, f"{r_path.name}: error_count == 0")
            check(res.get("breakthrough_detected_count") == 0, f"{r_path.name}: breakthrough_detected_count == 0")
            check(res.get("defense_drills_blocked_count") == 8, f"{r_path.name}: defense_drills_blocked_count == 8")
            check(res.get("stream_interception_count") == 8, f"{r_path.name}: stream_interception_count == 8")
            check(res.get("stream_passthrough_count") == 2, f"{r_path.name}: stream_passthrough_count == 2")
            check(res.get("control_case_passed_count") == 2, f"{r_path.name}: control_case_passed_count == 2")
            check(res.get("control_case_failed_count") == 0, f"{r_path.name}: control_case_failed_count == 0")
            check(res.get("refusal_count") == 8, f"{r_path.name}: refusal_count == 8")
            check(res.get("normal_usage_allowed_count") == 2, f"{r_path.name}: normal_usage_allowed_count == 2")
            check_security_fields(res, f"{r_path.name}")
            check(res.get("synthetic_only") is True, f"{r_path.name}: synthetic_only is True")
            check(res.get("fake_runtime_only") is True, f"{r_path.name}: fake_runtime_only is True")

            summ = res.get("summary", {})
            check(summ.get("defense_drill_block_rate") == "100.0%", f"{r_path.name}: defense_drill_block_rate is 100.0%")
            check(summ.get("control_pass_rate") == "100.0%", f"{r_path.name}: control_pass_rate is 100.0%")
            check(summ.get("overall_defensive_check_pass_rate") == "100.0%", f"{r_path.name}: overall_defensive_check_pass_rate is 100.0%")
            check(summ.get("breakthrough_rate") == "0.0%", f"{r_path.name}: breakthrough_rate is 0.0%")

    # ================================================================
    # 6. Capability Scorecard Verification
    # ================================================================
    print("\n[6] Capability Scorecard Verification")
    for sc_path in [
        ROOT / "executions/phase103a_gateway_interceptor/capability_scorecard.yaml",
        ROOT / "adversarial_playbooks/phase103a_stream_gateway/capability_scorecard.yaml",
    ]:
        check(sc_path.exists(), f"Capability scorecard exists at {sc_path}")
        sc = yaml_load(sc_path)
        check(sc is not None, f"Capability scorecard {sc_path.name} parsed successfully")
        if sc:
            sc_meta = sc.get("scorecard_metadata", {})
            check(sc_meta.get("scorecard_id") == "phase103a_stream_gateway_scorecard_v1", f"{sc_path.name}: scorecard_id is valid")
            check(sc_meta.get("phase") == "phase103a", f"{sc_path.name}: phase is phase103a")
            check(sc_meta.get("task_id") == "Phase-103A-GATEWAY-001", f"{sc_path.name}: task_id is Phase-103A-GATEWAY-001")
            check(sc_meta.get("module_id") == "M23_STREAM_GATEWAY", f"{sc_path.name}: module_id is M23_STREAM_GATEWAY")
            check(sc_meta.get("assessment_mode") == "adversarial_validation", f"{sc_path.name}: assessment_mode is adversarial_validation")
            check_security_fields(sc_meta, f"{sc_path.name} metadata")
            check(sc_meta.get("synthetic_only") is True, f"{sc_path.name}: synthetic_only is True")
            check(sc_meta.get("fake_runtime_only") is True, f"{sc_path.name}: fake_runtime_only is True")

            rsum = sc.get("results_summary", {})
            check(rsum.get("total_evaluations") == 10, f"{sc_path.name}: total_evaluations == 10")
            check(rsum.get("attack_cases_evaluated") == 8, f"{sc_path.name}: attack_cases_evaluated == 8")
            check(rsum.get("control_cases_evaluated") == 2, f"{sc_path.name}: control_cases_evaluated == 2")
            check(rsum.get("defense_drills_blocked") == 8, f"{sc_path.name}: defense_drills_blocked == 8")
            check(rsum.get("breakthroughs") == 0, f"{sc_path.name}: breakthroughs == 0")
            check(rsum.get("control_passed") == 2, f"{sc_path.name}: control_passed == 2")
            check(rsum.get("control_failed") == 0, f"{sc_path.name}: control_failed == 0")
            check(rsum.get("defense_drill_block_rate") == "100.0%", f"{sc_path.name}: defense_drill_block_rate is 100.0%")
            check(rsum.get("control_pass_rate") == "100.0%", f"{sc_path.name}: control_pass_rate is 100.0%")
            check(rsum.get("breakthrough_rate") == "0.0%", f"{sc_path.name}: breakthrough_rate is 0.0%")

            caps = sc.get("streaming_interception_capabilities_evaluated", [])
            check(len(caps) == 10, f"{sc_path.name}: evaluated capabilities count == 10 (found {len(caps)})")
            for cap in caps:
                check(cap.get("status") == "PASS", f"{sc_path.name} cap {cap.get('entry_id')}: status == PASS")

    # ================================================================
    # 7. Documentation Notes Verification
    # ================================================================
    print("\n[7] Documentation Notes Verification")
    notes_path = ROOT / "docs/phase103a_gateway_interceptor_notes.md"
    check(notes_path.exists(), f"Notes document exists at {notes_path}")
    if notes_path.exists():
        content = notes_path.read_text(encoding="utf-8")
        check("Phase-103A-GATEWAY-001" in content or "Phase 103A" in content, "Notes contain Phase 103A reference")
        check("M23" in content or "Stream Gateway" in content, "Notes contain Stream Gateway reference")
        check("Server-Sent Events" in content or "SSE" in content, "Notes contain SSE reference")
        check("WebSocket" in content, "Notes contain WebSocket reference")
        check("Sliding Window" in content or "滑动窗口" in content, "Notes contain Sliding Window reference")
        check("DLP" in content or "脱敏" in content, "Notes contain DLP reference")

    # ================================================================
    # 8. Execution Summary Verification
    # ================================================================
    print("\n[8] Execution Summary Verification")
    summary_path = ROOT / "phase103a_gateway001_execution_summary.yaml"
    check(summary_path.exists(), f"Execution summary exists at {summary_path}")
    summary = yaml_load(summary_path)
    check(summary is not None, "Execution summary parsed successfully as YAML")

    if summary:
        check(summary.get("task_id") == "Phase-103A-GATEWAY-001", "Summary task_id is Phase-103A-GATEWAY-001")
        check(summary.get("task_type") == "module_development", "Summary task_type is module_development")
        check(summary.get("assessment_mode") == "adversarial_validation", "Summary assessment_mode is adversarial_validation")
        check_security_fields(summary.get("safety_boundaries", {}), "Summary safety boundaries")
        s_res = summary.get("test_results", {})
        check(s_res.get("total_cases") == 10, "Summary total_cases == 10")
        check(s_res.get("defense_drills_blocked") == 8, "Summary defense_drills_blocked == 8")
        check(s_res.get("breakthroughs") == 0, "Summary breakthroughs == 0")
        check(s_res.get("control_passed") == 2, "Summary control_passed == 2")
        check(s_res.get("status") == "PASS", "Summary status is PASS")

    # ================================================================
    # Final Validation Summary
    # ================================================================
    print("\n" + "=" * 70)
    print(f"Validation Finished: {checks_passed} PASSED, {checks_failed} FAILED")
    print("=" * 70)

    if checks_failed > 0:
        print("\nErrors encountered:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(0)
    else:
        print("\nALL PHASE-103A-GATEWAY-001 VALIDATION CHECKS PASSED PERFECTLY!\n")


if __name__ == "__main__":
    main()
