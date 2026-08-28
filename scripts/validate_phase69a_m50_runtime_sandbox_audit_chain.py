#!/usr/bin/env python3
"""Phase 69A — M50 Agent Runtime Sandbox and Audit Chain Integrity MVP Validator.

Comprehensive checks for corpus, run config, execution results, result YAML,
scorecard, notes, registry, and security fields.
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


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 69A — M50 Agent Runtime Sandbox and Audit Chain Integrity MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus exists and has correct structure
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m50_runtime_sandbox_audit_chain_mvp/playbook.yaml"
    corpus = yaml_load(corpus_path)
    check(corpus is not None, "Corpus playbook.yaml loaded")
    if corpus:
        entries = corpus.get("entries", [])
        meta = corpus.get("playbook_metadata", {})
        check(len(entries) >= 12, f"Corpus has >= 12 entries ({len(entries)})")

        control_cases = [e for e in entries if e.get("control_case")]
        check(len(control_cases) >= 2, f"Corpus has >= 2 control cases ({len(control_cases)})")

        categories = [e.get("category", "") for e in entries]
        check("runtime_sandbox_escape_signal" in categories,
              "Corpus includes runtime_sandbox_escape_signal")
        check("runtime_fake_tool_boundary_violation" in categories,
              "Corpus includes runtime_fake_tool_boundary_violation")
        check("tool_trace_missing_required_field" in categories,
              "Corpus includes tool_trace_missing_required_field")
        check("tool_trace_inconsistent_trace_id" in categories,
              "Corpus includes tool_trace_inconsistent_trace_id")
        check("audit_chain_tampering_signal" in categories,
              "Corpus includes audit_chain_tampering_signal")
        check("controlled_replay_admission_bypass_attempt" in categories,
              "Corpus includes controlled_replay_admission_bypass_attempt")
        check("safe_fake_runtime_control_case" in categories,
              "Corpus includes safe_fake_runtime_control_case")
        check("complete_audit_chain_control_case" in categories,
              "Corpus includes complete_audit_chain_control_case")

        # Check all entries use SIM_ placeholders
        all_text = yaml.dump(entries)
        sim_pattern = re.findall(r'<SIM_\w+>', all_text)
        check(len(sim_pattern) >= len(entries) * 3,
              f"All entries use <SIM_...> placeholders ({len(sim_pattern)} found)")

        # Check no real data in corpus
        real_patterns = [
            r'https?://(?!sim\.)', r'(?<![a-zA-Z])sk-[A-Za-z0-9_-]+',
            r'api[a-zA-Z]*\.[a-zA-Z]+\.com', r'secret[a-zA-Z]*=',
            r'token[a-zA-Z]*=', r'password=',
        ]
        corpus_str = str(corpus).lower()
        no_real = True
        for pat in real_patterns:
            if re.search(pat, corpus_str):
                no_real = False
                break
        check(no_real, "Corpus contains no real URLs, tokens, secrets, or API keys")

        # Check attack_objectives are valid
        valid_objectives = {
            "runtime_sandbox_escape_signal",
            "runtime_fake_tool_boundary_violation",
            "runtime_audit_chain_tampering_signal",
            "runtime_trace_integrity_gap_detection",
            "runtime_policy_enforcement_bypass",
        }
        for e in entries:
            obj = e.get("attack_objective", "")
            check(obj in valid_objectives, f"{e['case_id']} valid attack_objective ({obj})")

        # Check all entries have required fields
        for e in entries:
            eid = e.get("case_id", "MISSING")
            check(e.get("synthetic_runtime_sandbox_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_runtime_sandbox_id")
            check(e.get("synthetic_runtime_policy_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_runtime_policy_id")
            check(e.get("synthetic_fake_tool_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_fake_tool_id")
            check(e.get("synthetic_tool_trace_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_tool_trace_id")
            check(e.get("synthetic_audit_event_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_audit_event_id")
            check(e.get("synthetic_trace_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_trace_id")
            check(e.get("synthetic_request_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_request_id")
            check(e.get("synthetic_decision_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_decision_id")
            check(e.get("synthetic_review_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_review_id")
            check(e.get("synthetic_replay_candidate_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_replay_candidate_id")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")
            check(e.get("production_safety_claimed") is False,
                  f"{eid} production_safety_claimed == false")
            check(e.get("controlled_replay_claimed") is False,
                  f"{eid} controlled_replay_claimed == false")
            check(e.get("controlled_replay_execution_allowed") is False,
                  f"{eid} controlled_replay_execution_allowed == false")
            check(e.get("replay_executable") is False,
                  f"{eid} replay_executable == false")

        # Module metadata
        check(meta.get("module_id") == "M50", "Corpus module_id == M50")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("attacker_type") == "compromised_user",
              "Corpus attacker_type == compromised_user")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("fake_runtime_only") is True, "Corpus fake_runtime_only == true")
        check(meta.get("real_runtime_allowed") is False,
              "Corpus real_runtime_allowed == false")
        check(meta.get("real_sandbox_escape_allowed") is False,
              "Corpus real_sandbox_escape_allowed == false")
        check(meta.get("real_tool_call_allowed") is False,
              "Corpus real_tool_call_allowed == false")
        check(meta.get("real_api_call_allowed") is False,
              "Corpus real_api_call_allowed == false")
        check(meta.get("real_system_connection_allowed") is False,
              "Corpus real_system_connection_allowed == false")
        check(meta.get("real_audit_log_allowed") is False,
              "Corpus real_audit_log_allowed == false")
        check(meta.get("real_trace_allowed") is False,
              "Corpus real_trace_allowed == false")
        check(meta.get("real_command_execution_allowed") is False,
              "Corpus real_command_execution_allowed == false")
        check(meta.get("controlled_replay_execution_allowed") is False,
              "Corpus controlled_replay_execution_allowed == false")
        check(meta.get("replay_executable") is False,
              "Corpus replay_executable == false")

    # ================================================================
    # 2. Run config (embedded in playbook metadata)
    # ================================================================
    print("\n2. Run config (embedded in playbook metadata)")
    if corpus:
        meta = corpus.get("playbook_metadata", {})
        check(meta.get("fake_runtime_only") is True, "Run config fake_runtime_only == true")
        check(meta.get("synthetic_only") is True, "Run config synthetic_only == true")
        check(meta.get("controlled_replay_execution_allowed") is False,
              "Run config controlled_replay_execution_allowed == false")
        check(meta.get("replay_executable") is False,
              "Run config replay_executable == false")

    # ================================================================
    # 3. Execution results JSON
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase69a_m50_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 12, f"execution_results has >= 12 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("entry_id", "MISSING")
            check(r.get("real_runtime_connected") is False,
                  f"{rid} real_runtime_connected == false")
            check(r.get("real_sandbox_escape_attempted") is False,
                  f"{rid} real_sandbox_escape_attempted == false")
            check(r.get("real_command_executed") is False,
                  f"{rid} real_command_executed == false")
            check(r.get("real_audit_log_accessed") is False,
                  f"{rid} real_audit_log_accessed == false")
            check(r.get("real_trace_accessed") is False,
                  f"{rid} real_trace_accessed == false")
            check(r.get("real_tool_executed") is False,
                  f"{rid} real_tool_executed == false")
            check(r.get("real_api_called") is False,
                  f"{rid} real_api_called == false")
            check(r.get("controlled_replay_executed") is False,
                  f"{rid} controlled_replay_executed == false")
            check(r.get("real_payload_generated") is False,
                  f"{rid} real_payload_generated == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase69a_m50_mvp/m50_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m50_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M50", "result module_id == M50")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 12,
              f"result total_cases >= 12 ({result_yaml.get('total_cases')})")
        check("sandbox_boundary_preserved_count" in result_yaml,
              "result has sandbox_boundary_preserved_count")
        check("runtime_escape_blocked_count" in result_yaml,
              "result has runtime_escape_blocked_count")
        check("tool_trace_complete_count" in result_yaml,
              "result has tool_trace_complete_count")
        check("tool_trace_missing_field_detected_count" in result_yaml,
              "result has tool_trace_missing_field_detected_count")
        check("trace_integrity_failed_count" in result_yaml,
              "result has trace_integrity_failed_count")
        check("audit_chain_consistent_count" in result_yaml,
              "result has audit_chain_consistent_count")
        check("audit_chain_gap_detected_count" in result_yaml,
              "result has audit_chain_gap_detected_count")
        check("audit_chain_tampering_signal_detected_count" in result_yaml,
              "result has audit_chain_tampering_signal_detected_count")
        check("replay_blocked_count" in result_yaml,
              "result has replay_blocked_count")
        check("design_gate_preserved_count" in result_yaml,
              "result has design_gate_preserved_count")
        check("controlled_replay_execution_blocked_count" in result_yaml,
              "result has controlled_replay_execution_blocked_count")
        check("human_review_required_count" in result_yaml,
              "result has human_review_required_count")
        check("breakthrough_detected_count" in result_yaml,
              "result has breakthrough_detected_count")
        check(result_yaml.get("confirmed_vulnerability") is False,
              "result confirmed_vulnerability == false")
        check(result_yaml.get("formal_finding_allowed") is False,
              "result formal_finding_allowed == false")
        check(result_yaml.get("production_safety_claimed") is False,
              "result production_safety_claimed == false")
        check(result_yaml.get("controlled_replay_claimed") is False,
              "result controlled_replay_claimed == false")
        check(result_yaml.get("controlled_replay_execution_allowed") is False,
              "result controlled_replay_execution_allowed == false")
        check(result_yaml.get("replay_executable") is False,
              "result replay_executable == false")
        check(result_yaml.get("real_runtime_connected") is False,
              "result real_runtime_connected == false")
        check(result_yaml.get("real_sandbox_escape_attempted") is False,
              "result real_sandbox_escape_attempted == false")
        check(result_yaml.get("real_command_executed") is False,
              "result real_command_executed == false")
        check(result_yaml.get("real_audit_log_accessed") is False,
              "result real_audit_log_accessed == false")
        check(result_yaml.get("real_trace_accessed") is False,
              "result real_trace_accessed == false")
        check(result_yaml.get("real_tool_executed") is False,
              "result real_tool_executed == false")
        check(result_yaml.get("real_api_called") is False,
              "result real_api_called == false")
        check(result_yaml.get("evidence_trace_present") is True,
              "result evidence_trace_present == true")
        check(result_yaml.get("exploit_chain_candidate_generated") is False,
              "result exploit_chain_candidate_generated == false")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase69a_m50_mvp/capability_scorecard.yaml"
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
        check(sm.get("fake_runtime_only") is True,
              "scorecard fake_runtime_only == true")
        check(sm.get("controlled_replay_execution_allowed") is False,
              "scorecard controlled_replay_execution_allowed == false")
        check(sm.get("replay_executable") is False,
              "scorecard replay_executable == false")
        check(sm.get("confirmed_vulnerability") is False,
              "scorecard confirmed_vulnerability == false")
        check(sm.get("formal_finding_allowed") is False,
              "scorecard formal_finding_allowed == false")
        check(sm.get("production_safety_claimed") is False,
              "scorecard production_safety_claimed == false")
        check(sm.get("controlled_replay_claimed") is False,
              "scorecard controlled_replay_claimed == false")
        check(sm.get("safety_level") == "simulated_runtime_safety",
              "scorecard safety_level == simulated_runtime_safety")
        check(sm.get("production_safety") == "out_of_scope",
              "scorecard production_safety == out_of_scope")

        cv = scorecard.get("capability_value")
        rl = scorecard.get("risk_level")
        check(cv is not None and rl is not None,
              f"scorecard has capability_value ({cv}) and risk_level ({rl})")
        check(cv != rl,
              f"capability_value ({cv}) and risk_level ({rl}) are separate concepts")
        check(scorecard.get("capability_value_semantics") is not None,
              "scorecard has capability_value_semantics")
        check(scorecard.get("risk_level_semantics") is not None,
              "scorecard has risk_level_semantics")

        check("sandbox_boundary_preserved" in rs,
              "scorecard result_summary has sandbox_boundary_preserved")
        check("runtime_escape_blocked" in rs,
              "scorecard result_summary has runtime_escape_blocked")
        check("tool_trace_complete" in rs,
              "scorecard result_summary has tool_trace_complete")
        check("tool_trace_missing_field_detected" in rs,
              "scorecard result_summary has tool_trace_missing_field_detected")
        check("trace_integrity_failed" in rs,
              "scorecard result_summary has trace_integrity_failed")
        check("audit_chain_consistent" in rs,
              "scorecard result_summary has audit_chain_consistent")
        check("audit_chain_gap_detected" in rs,
              "scorecard result_summary has audit_chain_gap_detected")
        check("audit_chain_tampering_signal_detected" in rs,
              "scorecard result_summary has audit_chain_tampering_signal_detected")
        check("replay_blocked" in rs,
              "scorecard result_summary has replay_blocked")
        check("design_gate_preserved" in rs,
              "scorecard result_summary has design_gate_preserved")
        check("controlled_replay_execution_blocked" in rs,
              "scorecard result_summary has controlled_replay_execution_blocked")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase69a_m50_runtime_sandbox_audit_chain_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实 runtime" in notes_text or "no real runtime" in notes_text.lower(),
              "Notes state no real runtime connection")
        check("不执行真实沙箱" in notes_text or "no real sandbox" in notes_text.lower(),
              "Notes state no real sandbox test")
        check("不访问真实审计日志" in notes_text or "no real audit log" in notes_text.lower(),
              "Notes state no real audit log access")
        check("不执行 controlled replay" in notes_text or "no controlled replay" in notes_text.lower(),
              "Notes state no controlled replay execution")
        check("不生成真实 payload" in notes_text or "no real payload" in notes_text.lower(),
              "Notes state no real payload generated")
        check("confirmed_vulnerability" in notes_text,
              "Notes mention confirmed_vulnerability")
        check("formal_finding_allowed" in notes_text,
              "Notes mention formal_finding_allowed")
        check("adversarial_validation" in notes_text,
              "Notes mention adversarial_validation mode")
        check("controlled_replay_execution_allowed" in notes_text,
              "Notes mention controlled_replay_execution_allowed")
        check("replay_executable" in notes_text,
              "Notes mention replay_executable")

    # ================================================================
    # 7. Registry check
    # ================================================================
    print("\n7. Registry")
    reg_path = ROOT / "capability_modules/module_registry.yaml"
    reg = yaml_load(reg_path)
    if reg:
        modules = reg.get("modules", [])
        m50 = next((m for m in modules if m.get("module_id") == "M50"), None)
        check(m50 is not None, "M50 exists in registry")
        if m50:
            check(m50.get("synthetic_only") is True, "Registry M50 synthetic_only == true")
            check(m50.get("production_safety") == "out_of_scope",
                  "Registry M50 production_safety == out_of_scope")
            check(m50.get("confirmed_vulnerability_allowed") is False,
                  "Registry M50 confirmed_vulnerability_allowed == false")
            check(m50.get("formal_finding_allowed") is False,
                  "Registry M50 formal_finding_allowed == false")

    # ================================================================
    # 8. Per-deliverable security field sweep
    # ================================================================
    print("\n8. Security field consistency")

    deliverables = {
        "corpus (playbook.yaml)": corpus,
        "execution_results.json": exec_results,
        "m50_result.yaml": result_yaml,
        "capability_scorecard.yaml": scorecard,
    }

    for name, data in deliverables.items():
        if data is None:
            check(False, f"{name}: could not load — skipping")
            continue
        data_str = str(data).lower()
        check("confirmed_vulnerability" not in data_str or 'false' in data_str,
              f"{name}: confirmed_vulnerability == false")
        check("formal_finding_allowed" not in data_str or 'false' in data_str,
              f"{name}: formal_finding_allowed == false")
        check("production_safety_claimed" not in data_str or 'false' in data_str,
              f"{name}: production_safety_claimed == false")
        check("controlled_replay_claimed" not in data_str or 'false' in data_str,
              f"{name}: controlled_replay_claimed == false")
        check("controlled_replay_execution_allowed" not in data_str or 'false' in data_str,
              f"{name}: controlled_replay_execution_allowed == false")
        check("replay_executable" not in data_str or 'false' in data_str,
              f"{name}: replay_executable == false")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Phase 69A M50 Runtime Sandbox and Audit Chain validation: ALL CHECKS PASSED")
    else:
        print("Phase 69A M50 Runtime Sandbox and Audit Chain validation: FAILED")
    print(f"  checks_passed: {checks_passed}")
    print(f"  checks_failed: {checks_failed}")
    if errors:
        print("\n  Errors:")
        for e in errors:
            print(f"    - {e}")
    print("=" * 60)

    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
