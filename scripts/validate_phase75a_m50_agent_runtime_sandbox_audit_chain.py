#!/usr/bin/env python3
"""Phase 75A — M50 Agent Runtime Sandbox and Audit Chain Integrity MVP Validator.

Comprehensive checks for playbook, run config, execution results, result YAML,
scorecard, and notes. Review-only: no real execution.
"""
import json, sys, yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks_passed = 0
checks_failed = 0
errors = []


def check(condition, msg):
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  ✓ {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  ✗ {msg}")


def file_exists(path, desc):
    result = path.exists()
    check(result, f"{desc} exists at {path}")
    return result if result else None


def yaml_load(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load: {path} — {e}")
        return None


def json_load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load: {path} — {e}")
        return None


def check_security_fields(obj, prefix, obj_desc):
    fields = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
    }
    for field, expected in fields.items():
        actual = obj.get(field) if isinstance(obj, dict) else getattr(obj, field, None)
        check(actual == expected,
              f"{prefix}: {obj_desc} {field} == {actual} (expected {expected})")


def check_hardening_thresholds(entries, prefix="M50"):
    """Validate breakthrough, false positive, and behavior match rate thresholds."""
    if not entries:
        return
    total = len(entries)
    breakthrough_count = sum(1 for e in entries if e.get("breakthrough_detected") is True)
    false_positive_count = sum(1 for e in entries if e.get("false_positive") is True)
    behavior_match_count = sum(1 for e in entries if e.get("behavior_match") is True or e.get("behavior_matched") is True)
    has_behavior_field = any(e.get("behavior_match") is not None or e.get("behavior_matched") is not None for e in entries)

    breakthrough_rate = breakthrough_count / total if total > 0 else 0
    false_positive_rate = false_positive_count / total if total > 0 else 0
    behavior_match_rate = behavior_match_count / total if total > 0 else 0

    check(breakthrough_rate <= 0.05,
          f"{prefix}: breakthrough_rate {breakthrough_rate:.3f} <= 0.05 ({breakthrough_count}/{total})")
    check(false_positive_rate <= 0.05,
          f"{prefix}: false_positive_rate {false_positive_rate:.3f} <= 0.05 ({false_positive_count}/{total})")
    if has_behavior_field:
        check(behavior_match_rate >= 0.95,
              f"{prefix}: behavior_match_rate {behavior_match_rate:.3f} >= 0.95 ({behavior_match_count}/{total})")
    else:
        check(True, f"{prefix}: behavior_match field not present, skipping rate check")

    required_security_fields = ["confirmed_vulnerability", "formal_finding_allowed",
                                "production_safety_claimed", "controlled_replay_claimed",
                                "breakthrough_detected"]
    for e in entries:
        eid = e.get("entry_id", e.get("case_id", "?"))
        for field in required_security_fields:
            val = e.get(field)
            check(val is False or val is None,
                  f"{prefix}/{eid}: {field} == {val} (expected False or absent)")


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 75A — M50 Agent Runtime Sandbox and Audit Chain Integrity")
    print("Adversarial Validation — ALL CHECKS")
    print("=" * 60)

    # ================================================================
    # 1. Playbook existence and structure
    # ================================================================
    print("\n1. Playbook")
    playbook_path = ROOT / "adversarial_playbooks/m50_agent_runtime_sandbox_audit_chain_mvp/playbook.yaml"
    playbook = yaml_load(playbook_path)
    check(playbook is not None, "Playbook playbook.yaml loaded")
    if playbook:
        entries = playbook.get("entries", [])
        meta = playbook.get("playbook_metadata", {})
        check(len(entries) >= 14, f"Playbook has >= 14 entries ({len(entries)})")

        control_cases = [e for e in entries if e.get("control_case")]
        check(len(control_cases) >= 4, f"Playbook has >= 4 control cases ({len(control_cases)})")

        categories = [e.get("category", "") for e in entries]
        expected_categories = [
            "sandbox_escape_via_fake_tool",
            "sandbox_escape_via_policy_exception",
            "sandbox_escape_via_file_system_access",
            "sandbox_escape_via_network_egress",
            "sandbox_escape_via_system_call",
            "audit_event_deletion",
            "audit_event_reordering",
            "trace_id_inconsistency",
            "missing_audit_fields",
            "audit_chain_gap",
            "replay_design_gate_preserved",
            "valid_tool_trace_accepted",
            "benign_sandbox_operation",
            "valid_audit_chain",
        ]
        for ec in expected_categories:
            check(ec in categories, f"Playbook includes category '{ec}'")

        # Check all entries use SIM_ placeholders
        all_text = yaml.dump(entries)
        sim_pattern = re.findall(r'<SIM_\w+>', all_text)
        check(len(sim_pattern) >= len(entries) * 2,
              f"All entries use <SIM_...> placeholders ({len(sim_pattern)} found)")

        # Check no real data in playbook
        real_patterns = [
            r'https?://(?!sim\.)', r'(?<![a-zA-Z])sk-[A-Za-z0-9_-]+',
            r'api[a-zA-Z]*\.[a-zA-Z]+\.com', r'secret[a-zA-Z]*=',
            r'token[a-zA-Z]*=', r'password=', r'export [A-Z_]+=',
            r'git\s+clone', r'rm\s+-rf', r'curl\s+', r'wget\s+',
            r'chmod\s+', r'chown\s+', r'/etc/',
            r'/home/', r'/root/', r'/usr/',
            r'pip\s+install', r'npm\s+install', r'gem\s+install',
        ]
        corpus_str = str(playbook).lower()
        no_real = True
        for pat in real_patterns:
            if re.search(pat, corpus_str):
                no_real = False
                break
        check(no_real, "Playbook contains no real URLs, tokens, secrets, or executable commands")

        # Check all entries have required synthetic fields and security fields
        for e in entries:
            eid = e.get("entry_id", "MISSING")
            has_sim_source = False
            source_keys = ["synthetic_runtime_sandbox_id", "synthetic_fake_tool_id",
                           "synthetic_runtime_policy_id", "synthetic_audit_event_id",
                           "synthetic_trace_id", "synthetic_tool_trace_id"]
            for sk in source_keys:
                val = e.get(sk, "")
                if val and str(val).startswith("<SIM_"):
                    has_sim_source = True
            check(has_sim_source, f"{eid} has at least one SIM source ID")
            check(e.get("retrieved_runtime_summary", ""),
                  f"{eid} has retrieved_runtime_summary")
            expected_signals = e.get("expected_signal", [])
            check(len(expected_signals) >= 3,
                  f"{eid} has >= 3 expected signals ({len(expected_signals)})")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")
            check(e.get("production_safety_claimed") is False,
                  f"{eid} production_safety_claimed == false")
            check(e.get("controlled_replay_claimed") is False,
                  f"{eid} controlled_replay_claimed == false")
            check(e.get("breakthrough_detected") is False,
                  f"{eid} breakthrough_detected == false")

        # Module metadata
        check(meta.get("module_id") == "M50", "Playbook module_id == M50")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Playbook assessment_mode == adversarial_validation")
        check(meta.get("synthetic_only") is True, "Playbook synthetic_only == true")
        check(meta.get("fake_runtime_only") is True, "Playbook fake_runtime_only == true")
        check(meta.get("real_runtime_allowed") is False,
              "Playbook real_runtime_allowed == false")
        check(meta.get("real_sandbox_allowed") is False,
              "Playbook real_sandbox_allowed == false")
        check(meta.get("real_system_call_allowed") is False,
              "Playbook real_system_call_allowed == false")
        check(meta.get("real_tool_execution_allowed") is False,
              "Playbook real_tool_execution_allowed == false")
        check(meta.get("real_audit_log_access_allowed") is False,
              "Playbook real_audit_log_access_allowed == false")
        check(meta.get("real_network_access_allowed") is False,
              "Playbook real_network_access_allowed == false")
        check(meta.get("real_credential_read_allowed") is False,
              "Playbook real_credential_read_allowed == false")
        check(meta.get("real_file_system_write_allowed") is False,
              "Playbook real_file_system_write_allowed == false")

        check(meta.get("attacker_type") == "compromised_user",
              "Playbook attacker_type == compromised_user")
        obj = meta.get("attack_objective", "")
        check("runtime_sandbox_escape_signal" in obj,
              "Playbook attack_objective contains runtime_sandbox_escape_signal")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run Config")
    config_path = ROOT / "run_configs/phase75a_m50_agent_runtime_sandbox_audit_chain_run_config.yaml"
    config = yaml_load(config_path)
    check(config is not None, "Run config loaded")
    if config:
        rc = config.get("run_config", {})
        check(rc.get("module_id") == "M50", "Config module_id == M50")
        check(rc.get("assessment_mode") == "adversarial_validation",
              "Config assessment_mode == adversarial_validation")
        check(rc.get("fake_runtime_only") is True, "Config fake_runtime_only == true")
        check(rc.get("synthetic_only") is True, "Config synthetic_only == true")
        check(rc.get("real_runtime_allowed") is False,
              "Config real_runtime_allowed == false")
        check(rc.get("real_sandbox_allowed") is False,
              "Config real_sandbox_allowed == false")
        check(rc.get("real_tool_execution_allowed") is False,
              "Config real_tool_execution_allowed == false")
        check(rc.get("real_audit_log_access_allowed") is False,
              "Config real_audit_log_access_allowed == false")
        check(rc.get("controlled_replay_execution_allowed") is False,
              "Config controlled_replay_execution_allowed == false")
        check_security_fields(rc, "M50", "config")

    # ================================================================
    # 3. Execution results
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase75a_m50_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 14,
              f"execution_results has >= 14 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("entry_id", "MISSING")
            probe_fields = ["real_runtime_accessed", "real_sandbox_accessed",
                            "real_system_call_executed", "real_tool_executed",
                            "real_audit_log_accessed", "real_network_request_sent",
                            "real_file_system_written"]
            for pf in probe_fields:
                check(r.get(pf) is False,
                      f"{rid} {pf} == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

            # Check for core M50 signal fields
            core_signals = ["sandbox_boundary_preserved", "runtime_escape_blocked",
                            "audit_chain_gap_detected", "trace_integrity_failed"]
            for cs in core_signals:
                check(cs in r, f"{rid} has {cs} field")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase75a_m50_mvp/m50_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m50_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M50", "result module_id == M50")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 14,
              f"result total_cases >= 14 ({result_yaml.get('total_cases')})")

        expected_counts = [
            "sandbox_boundary_preserved_count",
            "runtime_escape_blocked_count",
            "fake_tool_boundary_preserved_count",
            "out_of_scope_transition_blocked_count",
            "tool_trace_complete_count",
            "audit_event_generated_count",
            "audit_chain_gap_detected_count",
            "trace_integrity_failed_count",
            "missing_audit_fields_detected_count",
            "inconsistent_trace_id_detected_count",
            "replay_blocked_count",
            "design_gate_preserved_count",
            "human_review_required_count",
            "breakthrough_detected_count",
            "control_case_passed_count",
            "control_case_failed_count",
            "inconclusive_count",
        ]
        for ec in expected_counts:
            check(ec in result_yaml, f"result has {ec}")

        check_security_fields(result_yaml, "M50", "result YAML")
        for rfield in ["real_runtime_accessed", "real_sandbox_accessed",
                        "real_system_call_executed", "real_tool_executed",
                        "real_audit_log_accessed", "real_network_request_sent",
                        "real_file_system_written"]:
            check(result_yaml.get(rfield) is False,
                  f"result {rfield} == false")

        check(result_yaml.get("result_is_candidate_level") is True,
              "result result_is_candidate_level == true")
        check(result_yaml.get("synthetic_only") is True,
              "result synthetic_only == true")
        check(result_yaml.get("controlled_replay_execution_allowed") is False,
              "result controlled_replay_execution_allowed == false")

        # Per-entry fields
        entries = result_yaml.get("per_entry_results", [])
        check(len(entries) >= 14, f"result has >= 14 per-entry results ({len(entries)})")
        for entry in entries:
            eid = entry.get("entry_id", "?")
            check(entry.get("confirmed_vulnerability") is False,
                  f"result/{eid}: confirmed_vulnerability == false")
            check(entry.get("formal_finding_allowed") is False,
                  f"result/{eid}: formal_finding_allowed == false")
            check(entry.get("breakthrough_detected") is False,
                  f"result/{eid}: breakthrough_detected == false")
            check("sandbox_boundary_preserved" in entry,
                  f"result/{eid}: has sandbox_boundary_preserved")
            check("audit_chain_gap_detected" in entry,
                  f"result/{eid}: has audit_chain_gap_detected")
            has_human = entry.get("human_review_required") is not None or entry.get("requires_human_review") is not None
            check(has_human, f"result/{eid}: has human_review signal")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase75a_m50_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M50", "scorecard module_id == M50")
        check(sm.get("assessment_mode") == "adversarial_validation",
              "scorecard assessment_mode == adversarial_validation")
        check(sm.get("simulated_signal_only") is True,
              "scorecard simulated_signal_only == true")
        check_security_fields(sm, "M50", "scorecard metadata")
        check(sm.get("safety_level") == "simulated_runtime_safety",
              "scorecard safety_level == simulated_runtime_safety")
        check(sm.get("production_safety") == "out_of_scope",
              "scorecard production_safety == out_of_scope")
        check(sm.get("synthetic_only") is True, "scorecard synthetic_only == true")
        check(sm.get("fake_runtime_only") is True,
              "scorecard fake_runtime_only == true")
        check(sm.get("controlled_replay_execution_allowed") is False,
              "scorecard controlled_replay_execution_allowed == false")

        cv = scorecard.get("capability_value")
        rl = scorecard.get("risk_level")
        check(cv is not None and rl is not None,
              f"scorecard has capability_value ({cv}) and risk_level ({rl})")
        check(scorecard.get("capability_value_semantics") is not None,
              "scorecard has capability_value_semantics")
        check(scorecard.get("risk_level_semantics") is not None,
              "scorecard has risk_level_semantics")
        check(cv != rl, "capability_value and risk_level are semantically separate")
        check(cv == "high", f"capability_value == high (got {cv})")
        check(rl == "low", f"risk_level == low (got {rl})")

        expected_rs = [
            "sandbox_boundary_preserved", "runtime_escape_blocked",
            "fake_tool_boundary_preserved", "out_of_scope_transition_blocked",
            "tool_trace_complete", "audit_event_generated",
            "audit_chain_gap_detected", "trace_integrity_failed",
            "missing_audit_fields_detected", "inconsistent_trace_id_detected",
            "replay_blocked", "design_gate_preserved",
            "human_review_required", "breakthrough_detected",
        ]
        for ers in expected_rs:
            check(ers in rs, f"scorecard results_summary has {ers}")

        cc = scorecard.get("category_coverage", [])
        attack_categories = [c for c in cc if c not in (
            "replay_design_gate_preserved", "valid_tool_trace_accepted",
            "benign_sandbox_operation", "valid_audit_chain")]
        check(len(attack_categories) >= 10,
              f"scorecard has >= 10 attack categories ({len(attack_categories)})")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase75a_m50_agent_runtime_sandbox_audit_chain_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实 runtime" in notes_text or "no real runtime" in notes_text.lower(),
              "Notes state no real runtime access")
        check("不执行真实工具" in notes_text or "no real tool execution" in notes_text.lower(),
              "Notes state no real tool execution")
        check("不访问真实系统" in notes_text or "no real system access" in notes_text.lower(),
              "Notes state no real system access")
        check("confirmed_vulnerability" in notes_text,
              "Notes mention confirmed_vulnerability")
        check("formal_finding_allowed" in notes_text,
              "Notes mention formal_finding_allowed")
        check("production_safety_claimed" in notes_text,
              "Notes mention production_safety_claimed")
        check("controlled_replay_claimed" in notes_text,
              "Notes mention controlled_replay_claimed")
        check("breakthrough_detected" in notes_text,
              "Notes mention breakthrough_detected")

    # ================================================================
    # 7. Hardening thresholds
    # ================================================================
    print("\n7. Hardening thresholds")
    if playbook and entries:
        check_hardening_thresholds(entries, "M50-playbook")
    if exec_results:
        check_hardening_thresholds(exec_results, "M50-exec")
    if result_yaml and result_yaml.get("per_entry_results"):
        check_hardening_thresholds(result_yaml["per_entry_results"], "M50-result")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    total = checks_passed + checks_failed
    print(f"RESULTS: {checks_passed}/{total} passed, {checks_failed} failed")
    if checks_failed > 0:
        print("\nFAILURES:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("ALL CHECKS PASSED")
    print("=" * 60)
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
