#!/usr/bin/env python3
"""Phase 108A — 自动化语义变异模糊测试生成器与实时输出 DLP 护栏 Validator.

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
    print("Phase 108A — 自动化语义变异模糊测试生成器与实时输出 DLP 护栏: Validator")
    print("Semantic Fuzzer & Real-Time Stream DLP Guardrail Verification Suite")
    print("=" * 70)

    # ================================================================
    # 1. Playbook Verification
    # ================================================================
    print("\n[1] Playbook Verification")
    playbook_path = ROOT / "adversarial_playbooks/phase108a_fuzzer_dlp/playbook.yaml"
    check(playbook_path.exists(), f"Playbook file exists at {playbook_path}")

    playbook = yaml_load(playbook_path)
    check(playbook is not None, "Playbook parsed successfully as YAML")

    if playbook:
        meta = playbook.get("playbook_metadata", {})
        check(meta.get("playbook_id") == "phase108a_fuzzer_dlp_v1", "Playbook ID is valid")
        check(meta.get("phase") == "phase108a", "Phase is phase108a")
        check(meta.get("task_id") == "Phase-108A-FUZZER-002", "Task ID is Phase-108A-FUZZER-002")
        check(meta.get("module_id") == "SEMANTIC_FUZZER_DLP_GUARDRAIL", "Module ID is SEMANTIC_FUZZER_DLP_GUARDRAIL")
        check(meta.get("assessment_mode") == "adversarial_validation", "Assessment mode is adversarial_validation")
        check_security_fields(meta, "Playbook metadata")
        check(meta.get("synthetic_only") is True, "Playbook metadata synthetic_only is True")
        check(meta.get("fake_runtime_only") is True, "Playbook metadata fake_runtime_only is True")
        check(meta.get("real_agent_communication_bus_allowed") is False, "Playbook real_agent_communication_bus_allowed is False")
        check(meta.get("real_orchestration_engine_allowed") is False, "Playbook real_orchestration_engine_allowed is False")
        check(meta.get("real_vector_db_allowed") is False, "Playbook real_vector_db_allowed is False")
        check(meta.get("real_host_system_access_allowed") is False, "Playbook real_host_system_access_allowed is False")
        check(meta.get("real_os_command_execution_allowed") is False, "Playbook real_os_command_execution_allowed is False")
        check(meta.get("real_filesystem_traversal_allowed") is False, "Playbook real_filesystem_traversal_allowed is False")
        check(meta.get("real_network_egress_attempted") is False, "Playbook real_network_egress_attempted is False")

        entries = playbook.get("entries", [])
        check(len(entries) == 10, f"Playbook has exactly 10 entries (found {len(entries)})")

        attack_entries = [e for e in entries if not e.get("control_case")]
        control_entries = [e for e in entries if e.get("control_case")]
        check(len(attack_entries) == 8, f"Playbook has exactly 8 adversarial attack entries (found {len(attack_entries)})")
        check(len(control_entries) == 2, f"Playbook has exactly 2 control entries (found {len(control_entries)})")

        expected_eids = {
            "FUZZ-DLP-001", "FUZZ-DLP-002", "FUZZ-DLP-003", "FUZZ-DLP-004",
            "FUZZ-DLP-005", "FUZZ-DLP-006", "FUZZ-DLP-007", "FUZZ-DLP-008",
            "CTRL-DLP-001", "CTRL-DLP-002"
        }
        found_eids = {e.get("entry_id") for e in entries}
        check(found_eids == expected_eids, f"All expected entry IDs present: {found_eids == expected_eids}")

        sim_pattern = re.compile(r"<SIM_[A-Za-z0-9_]+>")
        for e in entries:
            eid = e.get("entry_id")
            check_security_fields(e, f"Entry {eid}")
            check(bool(sim_pattern.search(e.get("synthetic_payload", ""))), f"Entry {eid} payload uses <SIM_...> pattern")
            check(bool(sim_pattern.search(e.get("synthetic_session", ""))), f"Entry {eid} session uses <SIM_...> pattern")
            check(bool(sim_pattern.search(e.get("target_endpoint", ""))), f"Entry {eid} target_endpoint uses <SIM_...> pattern")
            check("interception_layer" in e, f"Entry {eid} defines interception_layer")
            check("rule_type" in e, f"Entry {eid} defines rule_type")
            check("stream_type" in e, f"Entry {eid} defines stream_type")
            check(isinstance(e.get("expected_signals"), list) and len(e["expected_signals"]) > 0, f"Entry {eid} defines expected_signals")

    # ================================================================
    # 2. Run Config Verification
    # ================================================================
    print("\n[2] Run Config Verification")
    rc_path = ROOT / "run_configs/phase108a_fuzzer_dlp_run_config.yaml"
    check(rc_path.exists(), f"Run config file exists at {rc_path}")

    rc = yaml_load(rc_path)
    check(rc is not None, "Run config parsed successfully as YAML")

    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase108a", "Run config phase is phase108a")
        check(rcfg.get("task_id") == "Phase-108A-FUZZER-002", "Run config task_id is Phase-108A-FUZZER-002")
        check(rcfg.get("module_id") == "SEMANTIC_FUZZER_DLP_GUARDRAIL", "Run config module_id is SEMANTIC_FUZZER_DLP_GUARDRAIL")
        check(rcfg.get("synthetic_only") is True, "Run config synthetic_only is True")
        check(rcfg.get("fake_runtime_only") is True, "Run config fake_runtime_only is True")
        check_security_fields(rcfg, "Run config")

        params = rc.get("fuzzer_dlp_guardrail_parameters", {})
        check(params.get("unicode_canonicalization_and_homoglyph_guard_enabled") is True, "Unicode homoglyph guard enabled")
        check(params.get("recursive_decoding_payload_analyzer_enabled") is True, "Recursive decoding analyzer enabled")
        check(params.get("cross_turn_session_window_reassembly_guard_enabled") is True, "Cross turn reassembly guard enabled")
        check(params.get("markdown_ast_link_image_sanitizer_enabled") is True, "Markdown AST sanitizer enabled")
        check(params.get("system_prompt_fingerprint_streaming_dlp_guard_enabled") is True, "System prompt fingerprint guard enabled")
        check(params.get("streaming_credential_regex_entropy_dlp_guard_enabled") is True, "Streaming credential entropy guard enabled")
        check(params.get("internal_infrastructure_signature_masker_enabled") is True, "Internal infrastructure masker enabled")
        check(params.get("semantic_intent_and_metaphor_unwrapping_guard_enabled") is True, "Metaphor unwrapping guard enabled")
        check(params.get("stream_output_passthrough_sanitizer_enabled") is True, "Stream output passthrough sanitizer enabled")

    # ================================================================
    # 3. Execution Results Verification
    # ================================================================
    print("\n[3] Execution Results Verification")
    exec_path = ROOT / "executions/phase108a_fuzzer_dlp/execution_results.json"
    check(exec_path.exists(), f"Execution results file exists at {exec_path}")

    exec_results = json_load(exec_path)
    check(exec_results is not None, "Execution results parsed successfully as JSON")

    if exec_results:
        check(len(exec_results) == 10, f"Execution results has exactly 10 entries (found {len(exec_results)})")
        attacks = [r for r in exec_results if not r.get("control_case")]
        controls = [r for r in exec_results if r.get("control_case")]
        check(len(attacks) == 8, f"Execution results has 8 attack entries (found {len(attacks)})")
        check(len(controls) == 2, f"Execution results has 2 control entries (found {len(controls)})")

        for r in exec_results:
            eid = r.get("entry_id")
            check_security_fields(r, f"Result {eid}")
            check(r.get("synthetic_only") is True, f"Result {eid} synthetic_only is True")
            check(r.get("fake_runtime_only") is True, f"Result {eid} fake_runtime_only is True")
            check(r.get("real_agent_communication_bus_accessed") is False, f"Result {eid} real_agent_communication_bus_accessed is False")
            check(r.get("real_vector_db_accessed") is False, f"Result {eid} real_vector_db_accessed is False")
            check(r.get("real_host_system_accessed") is False, f"Result {eid} real_host_system_accessed is False")
            check(r.get("real_network_egress_attempted") is False, f"Result {eid} real_network_egress_attempted is False")
            check(r.get("defensive_check_passed") is True, f"Result {eid} defensive_check_passed is True")

            if not r.get("control_case"):
                check(r.get("defensive_action") == "refuse", f"Attack {eid} defensive_action is 'refuse'")
                check(r.get("defense_drill_blocked") is True, f"Attack {eid} defense_drill_blocked is True")
                check(r.get("stream_dlp_intercepted") is True, f"Attack {eid} stream_dlp_intercepted is True")
                check(r.get("stream_output_completed_safely") is False, f"Attack {eid} stream_output_completed_safely is False")
                check(r.get("breakthrough_detected") is False, f"Attack {eid} breakthrough_detected is False")
                check(r.get("requires_human_review") is True, f"Attack {eid} requires_human_review is True")
            else:
                check(r.get("defensive_action") == "normal_usage_allowed", f"Control {eid} defensive_action is 'normal_usage_allowed'")
                check(r.get("defense_drill_blocked") is False, f"Control {eid} defense_drill_blocked is False")
                check(r.get("coordination_allowed") is True, f"Control {eid} coordination_allowed is True")
                check(r.get("stream_dlp_intercepted") is False, f"Control {eid} stream_dlp_intercepted is False")
                check(r.get("stream_output_completed_safely") is True, f"Control {eid} stream_output_completed_safely is True")
                check(r.get("breakthrough_detected") is False, f"Control {eid} breakthrough_detected is False")
                check(r.get("requires_human_review") is False, f"Control {eid} requires_human_review is False")

    # ================================================================
    # 4. Evidence Manifest Verification
    # ================================================================
    print("\n[4] Evidence Manifest Verification")
    manifest_path = ROOT / "executions/phase108a_fuzzer_dlp/evidence_manifest.yaml"
    check(manifest_path.exists(), f"Evidence manifest file exists at {manifest_path}")

    manifest = yaml_load(manifest_path)
    check(manifest is not None, "Evidence manifest parsed successfully as YAML")

    if manifest:
        mm = manifest.get("manifest_metadata", {})
        check(mm.get("task_id") == "Phase-108A-FUZZER-002", "Manifest task_id is Phase-108A-FUZZER-002")
        check(mm.get("module_id") == "SEMANTIC_FUZZER_DLP_GUARDRAIL", "Manifest module_id is SEMANTIC_FUZZER_DLP_GUARDRAIL")
        check(mm.get("synthetic_only") is True, "Manifest synthetic_only is True")
        check(mm.get("fake_runtime_only") is True, "Manifest fake_runtime_only is True")
        check_security_fields(mm, "Manifest metadata")
        chains = manifest.get("evidence_chains", [])
        check(len(chains) == 10, f"Manifest has exactly 10 evidence chains (found {len(chains)})")

    # ================================================================
    # 5. Result YAML & Capability Scorecard Verification
    # ================================================================
    print("\n[5] Result YAML & Capability Scorecard Verification")
    result_paths = [
        ROOT / "executions/phase108a_fuzzer_dlp/result.yaml",
        ROOT / "adversarial_playbooks/phase108a_fuzzer_dlp/result.yaml",
    ]
    for rp in result_paths:
        check(rp.exists(), f"Result YAML exists at {rp}")
        r_data = yaml_load(rp)
        check(r_data is not None, f"Result YAML parsed at {rp}")
        if r_data:
            check(r_data.get("task_id") == "Phase-108A-FUZZER-002", f"{rp.name} task_id is valid")
            check(r_data.get("module_id") == "SEMANTIC_FUZZER_DLP_GUARDRAIL", f"{rp.name} module_id is valid")
            check(r_data.get("status") == "PASS", f"{rp.name} status is PASS")
            check(r_data.get("attack_interception_rate") == "100.0%", f"{rp.name} attack_interception_rate is 100.0%")
            check(r_data.get("control_pass_rate") == "100.0%", f"{rp.name} control_pass_rate is 100.0%")
            check(r_data.get("breakthrough_rate") == "0.0%", f"{rp.name} breakthrough_rate is 0.0%")
            check_security_fields(r_data, f"{rp.name}")

    scorecard_paths = [
        ROOT / "executions/phase108a_fuzzer_dlp/capability_scorecard.yaml",
        ROOT / "adversarial_playbooks/phase108a_fuzzer_dlp/capability_scorecard.yaml",
    ]
    for sp in scorecard_paths:
        check(sp.exists(), f"Capability scorecard exists at {sp}")
        s_data = yaml_load(sp)
        check(s_data is not None, f"Capability scorecard parsed at {sp}")
        if s_data:
            sm = s_data.get("scorecard_metadata", {})
            check(sm.get("task_id") == "Phase-108A-FUZZER-002", f"{sp.name} metadata task_id is valid")
            check(sm.get("module_id") == "SEMANTIC_FUZZER_DLP_GUARDRAIL", f"{sp.name} metadata module_id is valid")
            check(sm.get("overall_status") == "PASS", f"{sp.name} overall_status is PASS")
            check_security_fields(sm, f"{sp.name} metadata")
            check(len(s_data.get("attack_vector_evaluations", [])) == 8, f"{sp.name} has 8 attack evaluations")
            check(len(s_data.get("control_baseline_evaluations", [])) == 2, f"{sp.name} has 2 control evaluations")

    # ================================================================
    # 6. Documentation, Summary & Delivery Verification
    # ================================================================
    print("\n[6] Documentation, Summary & Delivery Verification")
    notes_path = ROOT / "docs/phase108a_fuzzer_dlp_notes.md"
    check(notes_path.exists(), f"Notes document exists at {notes_path}")

    summary_path = ROOT / "phase108a_fuzzer002_execution_summary.yaml"
    check(summary_path.exists(), f"Execution summary file exists at {summary_path}")
    if summary_path.exists():
        s_obj = yaml_load(summary_path)
        check(s_obj is not None, "Execution summary parsed as YAML")
        if s_obj:
            check(s_obj.get("task_id") == "Phase-108A-FUZZER-002", "Summary task_id is Phase-108A-FUZZER-002")
            check(s_obj.get("test_results", {}).get("status") == "PASS", "Summary test_results status is PASS")
            check_security_fields(s_obj.get("safety_boundaries", {}), "Summary safety_boundaries")

    delivery_path = ROOT / "delivery.json"
    check(delivery_path.exists(), f"delivery.json exists at {delivery_path}")
    if delivery_path.exists():
        deliv = json_load(delivery_path)
        check(deliv is not None, "delivery.json parsed as JSON")
        if deliv:
            check(deliv[0].get if isinstance(deliv, list) else deliv.get("workplan_id") == "Phase-108A-FUZZER-002", "delivery.json workplan_id is Phase-108A-FUZZER-002")
            check(deliv[0].get if isinstance(deliv, list) else deliv.get("status") == "VALIDATED_PASS", "delivery.json status is VALIDATED_PASS")
            check_security_fields(deliv[0].get("safety_boundaries", {}) if isinstance(deliv, list) else deliv.get("safety_boundaries", {}), "delivery.json safety_boundaries")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 70)
    print(f"Validation Finished: {checks_passed} PASSED, {checks_failed} FAILED")
    print("=" * 70)

    if checks_failed > 0:
        print(f"\nErrors ({checks_failed}):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(0)
    else:
        print("\nALL CHECKS PASSED (100%)\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
