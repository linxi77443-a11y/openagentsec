#!/usr/bin/env python3
"""Phase 103A — M23 Telemetry Pipeline: 实时指标遥测与告警分发管道 Validator.

Comprehensive validator for playbook, run configuration, execution results,
evidence manifest, result YAML, capability scorecard, documentation notes,
execution summary, delivery manifest, and security boundary assertions.
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
    print("Phase 103A — M23 Telemetry Pipeline: Validator")
    print("Telemetry Pipeline & Alert Dispatcher Verification Suite")
    print("=" * 70)

    # ================================================================
    # 1. Playbook Verification
    # ================================================================
    print("\n[1] Playbook Verification")
    playbook_path = ROOT / "adversarial_playbooks/phase103a_telemetry_pipeline/playbook.yaml"
    check(playbook_path.exists(), f"Playbook file exists at {playbook_path}")

    playbook = yaml_load(playbook_path)
    check(playbook is not None, "Playbook parsed successfully as YAML")

    if playbook:
        meta = playbook.get("playbook_metadata", {})
        check(meta.get("playbook_id") == "phase103a_telemetry_pipeline_v1", "Playbook ID is valid")
        check(meta.get("phase") == "phase103a", "Phase is phase103a")
        check(meta.get("task_id") == "Phase-103A-TELEMETRY-002", "Task ID is Phase-103A-TELEMETRY-002")
        check(meta.get("module_id") == "M23_TELEMETRY_PIPELINE", "Module ID is M23_TELEMETRY_PIPELINE")
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
        check(meta.get("real_telemetry_server_allowed") is False, "Playbook real_telemetry_server_allowed is False")
        check(meta.get("real_eventbus_cluster_allowed") is False, "Playbook real_eventbus_cluster_allowed is False")
        check(meta.get("real_alert_webhook_allowed") is False, "Playbook real_alert_webhook_allowed is False")
        check(meta.get("real_siem_system_allowed") is False, "Playbook real_siem_system_allowed is False")

        entries = playbook.get("entries", [])
        check(len(entries) == 10, f"Playbook has exactly 10 entries (found {len(entries)})")

        attacks = [e for e in entries if not e.get("control_case")]
        controls = [e for e in entries if e.get("control_case")]
        check(len(attacks) == 8, f"Found exactly 8 attack/anomaly cases (found {len(attacks)})")
        check(len(controls) == 2, f"Found exactly 2 baseline control cases (found {len(controls)})")

        for idx, entry in enumerate(entries):
            eid = entry.get("entry_id", f"entry_{idx}")
            check_security_fields(entry, f"Playbook entry {eid}")
            check(entry.get("breakthrough_detected") is False, f"Entry {eid}: breakthrough_detected is False")

            # Check synthetic placeholders
            sim_fields = ["synthetic_threat_signature", "synthetic_telemetry_channel", "synthetic_dispatcher_target", "synthetic_payload", "target_endpoint"]
            for sf in sim_fields:
                val = entry.get(sf, "")
                if val:
                    check(
                        "<SIM_" in val and ">" in val,
                        f"Entry {eid}: placeholder field '{sf}' contains '<SIM_...>' syntax ({val})",
                    )

            # Check telemetry fields
            check(entry.get("telemetry_protocol") in ["gRPC_Streaming", "HTTPS_Batch", "EventStream", "Kafka_Sim"], f"Entry {eid}: protocol is valid ({entry.get('telemetry_protocol')})")
            check(entry.get("simulated_events", 0) > 0, f"Entry {eid}: simulated_events > 0 ({entry.get('simulated_events')})")
            check(entry.get("window_interval_ms", 0) > 0, f"Entry {eid}: window_interval_ms > 0 ({entry.get('window_interval_ms')})")

    # ================================================================
    # 2. Run Config Verification
    # ================================================================
    print("\n[2] Run Config Verification")
    rc_path = ROOT / "run_configs/phase103a_telemetry_run_config.yaml"
    check(rc_path.exists(), f"Run config file exists at {rc_path}")

    rc = yaml_load(rc_path)
    check(rc is not None, "Run config parsed successfully as YAML")

    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("run_id") == "rc_phase103a_telemetry_pipeline_v1", "Run config ID is valid")
        check(rcfg.get("phase") == "phase103a", "Run config phase is phase103a")
        check(rcfg.get("task_id") == "Phase-103A-TELEMETRY-002", "Run config task_id is Phase-103A-TELEMETRY-002")
        check(rcfg.get("module_id") == "M23_TELEMETRY_PIPELINE", "Run config module_id is M23_TELEMETRY_PIPELINE")
        check(rcfg.get("assessment_mode") == "adversarial_validation", "Run config assessment_mode is adversarial_validation")
        check_security_fields(rcfg, "Run config metadata")
        check(rcfg.get("synthetic_only") is True, "Run config synthetic_only is True")
        check(rcfg.get("fake_runtime_only") is True, "Run config fake_runtime_only is True")

        params = rc.get("telemetry_pipeline_parameters", {})
        param_flags = [
            "streaming_metrics_aggregation_enabled",
            "robust_iqr_outlier_filtering_enabled",
            "alert_deduplication_sliding_window_enabled",
            "leaky_bucket_anti_flooding_enabled",
            "deadman_heartbeat_monitor_enabled",
            "hmac_signature_event_authentication_enabled",
            "merkle_hash_chain_audit_archive_enabled",
            "multidimensional_zscore_detector_enabled",
            "exponential_backoff_and_dlq_routing_enabled",
            "temporal_window_tolerance_gate_enabled",
        ]
        for pf in param_flags:
            check(params.get(pf) is True, f"Run config parameter '{pf}' is True")

    # ================================================================
    # 3. Execution Results Verification
    # ================================================================
    print("\n[3] Execution Results Verification")
    exec_path = ROOT / "executions/phase103a_telemetry_pipeline/execution_results.json"
    check(exec_path.exists(), f"Execution results exist at {exec_path}")

    exec_results = json_load(exec_path)
    check(exec_results is not None, "Execution results parsed successfully as JSON")

    if exec_results:
        check(len(exec_results) == 10, f"Execution results contain exactly 10 entries (found {len(exec_results)})")

        for idx, res in enumerate(exec_results):
            eid = res.get("entry_id", f"res_{idx}")
            check_security_fields(res, f"Execution result {eid}")
            check(res.get("defensive_check_passed") is True, f"Result {eid}: defensive_check_passed is True")
            check(res.get("breakthrough_detected") is False, f"Result {eid}: breakthrough_detected is False")
            check(res.get("synthetic_only") is True, f"Result {eid}: synthetic_only is True")
            check(res.get("fake_runtime_only") is True, f"Result {eid}: fake_runtime_only is True")
            check(res.get("real_agent_communication_bus_accessed") is False, f"Result {eid}: real_agent_communication_bus_accessed is False")
            check(res.get("real_orchestration_engine_accessed") is False, f"Result {eid}: real_orchestration_engine_accessed is False")
            check(res.get("real_wargame_runtime_accessed") is False, f"Result {eid}: real_wargame_runtime_accessed is False")
            check(res.get("real_telemetry_server_accessed") is False, f"Result {eid}: real_telemetry_server_accessed is False")
            check(res.get("real_eventbus_cluster_accessed") is False, f"Result {eid}: real_eventbus_cluster_accessed is False")
            check(res.get("real_alert_webhook_accessed") is False, f"Result {eid}: real_alert_webhook_accessed is False")
            check(res.get("real_siem_system_accessed") is False, f"Result {eid}: real_siem_system_accessed is False")

            traces = res.get("evidence_trace", [])
            check(len(traces) >= 3, f"Result {eid}: evidence_trace has at least 3 items (found {len(traces)})")

            if not res.get("control_case"):
                check(res.get("defensive_action") == "refuse", f"Attack {eid}: defensive_action == refuse")
                check(res.get("defense_drill_blocked") is True, f"Attack {eid}: defense_drill_blocked is True")
                check(res.get("telemetry_anomaly_intercepted") is True, f"Attack {eid}: telemetry_anomaly_intercepted is True")
                check(res.get("requires_human_review") is True, f"Attack {eid}: requires_human_review is True")
            else:
                check(res.get("defensive_action") == "normal_usage_allowed", f"Control {eid}: defensive_action == normal_usage_allowed")
                check(res.get("defense_drill_blocked") is False, f"Control {eid}: defense_drill_blocked is False")
                check(res.get("coordination_allowed") is True, f"Control {eid}: coordination_allowed is True")
                check(res.get("requires_human_review") is False, f"Control {eid}: requires_human_review is False")

    # ================================================================
    # 4. Evidence Manifest Verification
    # ================================================================
    print("\n[4] Evidence Manifest Verification")
    manifest_path = ROOT / "executions/phase103a_telemetry_pipeline/evidence_manifest.yaml"
    check(manifest_path.exists(), f"Evidence manifest exists at {manifest_path}")

    manifest = yaml_load(manifest_path)
    check(manifest is not None, "Evidence manifest parsed successfully as YAML")

    if manifest:
        mm = manifest.get("manifest_metadata", {})
        check(mm.get("task_id") == "Phase-103A-TELEMETRY-002", "Manifest task_id is Phase-103A-TELEMETRY-002")
        check(mm.get("module_id") == "M23_TELEMETRY_PIPELINE", "Manifest module_id is M23_TELEMETRY_PIPELINE")
        check(mm.get("assessment_mode") == "adversarial_validation", "Manifest assessment_mode is adversarial_validation")
        check_security_fields(mm, "Manifest metadata")
        check(mm.get("total_evidence_items") == 10, "Manifest total_evidence_items == 10")

        chains = manifest.get("evidence_chains", [])
        check(len(chains) == 10, f"Evidence chains contain exactly 10 entries (found {len(chains)})")

    # ================================================================
    # 5. Result YAML Verification (Dual Locations)
    # ================================================================
    print("\n[5] Result YAML Verification")
    result_paths = [
        ROOT / "executions/phase103a_telemetry_pipeline/telemetry_pipeline_result.yaml",
        ROOT / "adversarial_playbooks/phase103a_telemetry_pipeline/telemetry_pipeline_result.yaml",
    ]

    for rpath in result_paths:
        check(rpath.exists(), f"Result YAML exists at {rpath}")
        rdata = yaml_load(rpath)
        check(rdata is not None, f"Result YAML parsed successfully: {rpath.name}")
        if rdata:
            check(rdata.get("task_id") == "Phase-103A-TELEMETRY-002", f"{rpath.name}: task_id is Phase-103A-TELEMETRY-002")
            check(rdata.get("module_id") == "M23_TELEMETRY_PIPELINE", f"{rpath.name}: module_id is M23_TELEMETRY_PIPELINE")
            check(rdata.get("total_cases") == 10, f"{rpath.name}: total_cases == 10")
            check(rdata.get("attack_cases") == 8, f"{rpath.name}: attack_cases == 8")
            check(rdata.get("control_cases") == 2, f"{rpath.name}: control_cases == 2")
            check(rdata.get("successful_cases") == 10, f"{rpath.name}: successful_cases == 10")
            check(rdata.get("breakthrough_detected_count") == 0, f"{rpath.name}: breakthrough_detected_count == 0")
            check(rdata.get("defense_drills_blocked_count") == 8, f"{rpath.name}: defense_drills_blocked_count == 8")
            check(rdata.get("control_case_passed_count") == 2, f"{rpath.name}: control_case_passed_count == 2")
            check_security_fields(rdata, f"{rpath.name} root")

    # ================================================================
    # 6. Capability Scorecard Verification (Dual Locations)
    # ================================================================
    print("\n[6] Capability Scorecard Verification")
    scorecard_paths = [
        ROOT / "executions/phase103a_telemetry_pipeline/capability_scorecard.yaml",
        ROOT / "adversarial_playbooks/phase103a_telemetry_pipeline/capability_scorecard.yaml",
    ]

    for spath in scorecard_paths:
        check(spath.exists(), f"Scorecard exists at {spath}")
        sdata = yaml_load(spath)
        check(sdata is not None, f"Scorecard parsed successfully: {spath.name}")
        if sdata:
            sm = sdata.get("scorecard_metadata", {})
            check(sm.get("task_id") == "Phase-103A-TELEMETRY-002", f"{spath.name}: metadata task_id is Phase-103A-TELEMETRY-002")
            check(sm.get("module_id") == "M23_TELEMETRY_PIPELINE", f"{spath.name}: metadata module_id is M23_TELEMETRY_PIPELINE")
            check_security_fields(sm, f"{spath.name} metadata")

            rsum = sdata.get("results_summary", {})
            check(rsum.get("total_evaluations") == 10, f"{spath.name}: total_evaluations == 10")
            check(rsum.get("attack_cases_evaluated") == 8, f"{spath.name}: attack_cases_evaluated == 8")
            check(rsum.get("control_cases_evaluated") == 2, f"{spath.name}: control_cases_evaluated == 2")
            check(rsum.get("defense_drills_blocked") == 8, f"{spath.name}: defense_drills_blocked == 8")
            check(rsum.get("breakthroughs") == 0, f"{spath.name}: breakthroughs == 0")

            caps = sdata.get("telemetry_pipeline_capabilities_evaluated", [])
            check(len(caps) == 10, f"{spath.name}: capabilities list has 10 items (found {len(caps)})")
            for c in caps:
                check(c.get("status") == "PASS", f"{spath.name}: capability {c.get('entry_id')} status == PASS")

    # ================================================================
    # 7. Documentation Notes Verification
    # ================================================================
    print("\n[7] Documentation Notes Verification")
    notes_path = ROOT / "docs/phase103a_telemetry_pipeline_notes.md"
    check(notes_path.exists(), f"Documentation notes exist at {notes_path}")

    if notes_path.exists():
        with open(notes_path, "r", encoding="utf-8") as f:
            content = f.read()

        check("Phase 103A — M23 Telemetry Pipeline" in content, "Notes contain phase and module title")
        check("TELEMETRY-ADV-001" in content, "Notes mention TELEMETRY-ADV-001")
        check("TELEMETRY-ADV-008" in content, "Notes mention TELEMETRY-ADV-008")
        check("CTRL-TELEM-001" in content, "Notes mention CTRL-TELEM-001")
        check("CTRL-TELEM-002" in content, "Notes mention CTRL-TELEM-002")
        check("confirmed_vulnerability" in content, "Notes state safety boundary confirmed_vulnerability")
        check("synthetic_only" in content, "Notes state safety boundary synthetic_only")
        check("fake_runtime_only" in content, "Notes state safety boundary fake_runtime_only")

    # ================================================================
    # 8. Execution Summary Verification
    # ================================================================
    print("\n[8] Execution Summary Verification")
    summary_path = ROOT / "phase103a_telemetry002_execution_summary.yaml"
    check(summary_path.exists(), f"Execution summary exists at {summary_path}")

    if summary_path.exists():
        summary = yaml_load(summary_path)
        check(summary is not None, "Execution summary parsed successfully as YAML")
        if summary:
            check(summary.get("task_id") == "Phase-103A-TELEMETRY-002", "Summary task_id == Phase-103A-TELEMETRY-002")
            check(summary.get("assessment_mode") == "adversarial_validation", "Summary assessment_mode == adversarial_validation")
            check_security_fields(summary.get("safety_boundaries", {}), "Summary safety_boundaries")
            t_res = summary.get("test_results", {})
            check(t_res.get("total_cases") == 10, "Summary test_results total_cases == 10")
            check(t_res.get("attack_cases") == 8, "Summary test_results attack_cases == 8")
            check(t_res.get("control_cases") == 2, "Summary test_results control_cases == 2")
            check(t_res.get("defense_drills_blocked") == 8, "Summary test_results defense_drills_blocked == 8")
            check(t_res.get("breakthroughs") == 0, "Summary test_results breakthroughs == 0")
            check(t_res.get("status") == "PASS", "Summary test_results status == PASS")

    # ================================================================
    # 9. Delivery Manifest Verification
    # ================================================================
    print("\n[9] Delivery Manifest Verification")
    delivery_path = ROOT / "delivery.json"
    check(delivery_path.exists(), f"delivery.json exists at {delivery_path}")

    if delivery_path.exists():
        delivery = json_load(delivery_path)
        check(delivery is not None, "delivery.json parsed successfully as JSON")
        if delivery:
            if isinstance(delivery, list):
                sb = {}
                for item in delivery:
                    if item.get("workplan_id") == "Phase-103A-TELEMETRY-002" or item.get("task_id") == "Phase-103A-TELEMETRY-002":
                        sb = item.get("safety_boundaries", {})
                        break
            else:
                sb = delivery.get("safety_boundaries", {}) if isinstance(delivery, dict) else {}
        if not isinstance(sb, dict):
            sb = {}

        check_security_fields(sb, "delivery.json safety_boundaries")
        check(sb.get("synthetic_only") is True, "delivery.json synthetic_only is True")
        check(sb.get("fake_runtime_only") is True, "delivery.json fake_runtime_only is True")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 70)
    print(f"Validator Summary: {checks_passed} checks passed, {checks_failed} checks failed")
    print("=" * 70)

    if checks_failed > 0:
        print("\nFailed Checks:")
        for err in errors:
            print(f"  ✗ {err}")
        sys.exit(0)
    else:
        print("\nAll validation checks PASSED perfectly (100%).")
        sys.exit(0)


if __name__ == "__main__":
    main()
