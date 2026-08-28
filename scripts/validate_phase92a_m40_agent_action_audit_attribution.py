#!/usr/bin/env python3
"""Phase 92A — M40 Agent Action Audit & Attribution MVP Validator.

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
    print("Phase 92A — M40 Agent Action Audit & Attribution MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m40_agent_action_audit_attribution_mvp/playbook.yaml"
    corpus = yaml_load(corpus_path)
    check(corpus is not None, "Corpus playbook.yaml loaded")
    if corpus:
        entries = corpus.get("entries", [])
        meta = corpus.get("playbook_metadata", {})
        check(len(entries) >= 8, f"Corpus has >= 8 entries ({len(entries)})")

        attack_cases = [e for e in entries if not e.get("control_case")]
        control_cases = [e for e in entries if e.get("control_case")]
        check(len(attack_cases) >= 8, f"Corpus has >= 8 attack cases ({len(attack_cases)})")
        check(len(control_cases) >= 2, f"Corpus has >= 2 control cases ({len(control_cases)})")

        categories = [e.get("category", "") for e in entries]
        check("tool_call_audit_completeness" in categories,
              "Corpus includes tool_call_audit_completeness")
        check("attribution_correctness" in categories,
              "Corpus includes attribution_correctness")
        check("tamper_evidence_hash_chain" in categories,
              "Corpus includes tamper_evidence_hash_chain")
        check("missing_audit_field_detection" in categories,
              "Corpus includes missing_audit_field_detection")
        check("cross_tenant_audit_isolation" in categories,
              "Corpus includes cross_tenant_audit_isolation")
        check("standard_operation_audit" in categories,
              "Corpus includes standard_operation_audit")

        # Check all entries use SIM_ placeholders
        all_text = yaml.dump(entries)
        sim_pattern = re.findall(r'<SIM_\w+>', all_text)
        check(len(sim_pattern) >= len(entries) * 3,
              f"All entries use <SIM_...> placeholders ({len(sim_pattern)} found)")

        # Check no real data
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

        # Check all entries have required fields
        for e in entries:
            eid = e.get("case_id", "MISSING")
            check(e.get("synthetic_audit_event_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_audit_event_id")
            check(e.get("synthetic_tool_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_tool_id")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")
            check(e.get("production_safety_claimed") is False,
                  f"{eid} production_safety_claimed == false")

        # Module metadata
        check(meta.get("module_id") == "M40", "Corpus module_id == M40")
        check(meta.get("assessment_mode") == "defensive_evaluation",
              "Corpus assessment_mode == defensive_evaluation")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_audit_system_allowed") is False,
              "Corpus real_audit_system_allowed == false")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run config")
    rc_path = ROOT / "run_configs/phase92a_m40_agent_action_audit_attribution_run_config.yaml"
    rc = yaml_load(rc_path)
    check(rc is not None, "Run config YAML loaded")
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase92a", "Run config phase == phase92a")
        check(rcfg.get("module_id") == "M40", "Run config module_id == M40")
        check(rcfg.get("assessment_mode") == "defensive_evaluation",
              "Run config assessment_mode == defensive_evaluation")
        check(rcfg.get("safety_level") == "simulated_runtime_safety",
              "Run config safety_level == simulated_runtime_safety")
        check(rcfg.get("production_safety") == "out_of_scope",
              "Run config production_safety == out_of_scope")
        check(rcfg.get("real_audit_system_allowed") is False,
              "Run config real_audit_system_allowed == false")
        check(rcfg.get("confirmed_vulnerability") is False,
              "Run config confirmed_vulnerability == false")
        check(rcfg.get("single_module_only") is True,
              "Run config single_module_only == true")

    # ================================================================
    # 3. Execution results
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase92a_m40_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        # Handle both legacy array format and new nested format
        if isinstance(exec_results, list):
            exec_entries = exec_results
        elif isinstance(exec_results, dict):
            exec_entries = exec_results.get("entries", [])
            # Check new lineage_break_reason_summary structure
            if "lineage_break_reason_summary" in exec_results:
                check(True, "execution_results has lineage_break_reason_summary")
            if "overall_attribution_consistency" in exec_results:
                check(True, "execution_results has overall_attribution_consistency")
                oac = exec_results["overall_attribution_consistency"]
                check("score" in oac, "overall_attribution_consistency has score")
                check("level" in oac, "overall_attribution_consistency has level")
        else:
            exec_entries = []

        check(len(exec_entries) >= 8, f"execution_results has >= 8 entries ({len(exec_entries)})")
        for r in exec_entries:
            if not isinstance(r, dict):
                continue
            rid = r.get("case_id", "MISSING")
            check(r.get("real_audit_system_accessed") is False,
                  f"{rid} real_audit_system_accessed == false")
            check(r.get("real_log_platform_accessed") is False,
                  f"{rid} real_log_platform_accessed == false")
            check(r.get("real_tool_executed") is False,
                  f"{rid} real_tool_executed == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase92a_m40_mvp/m40_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m40_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M40", "result module_id == M40")
        check(result_yaml.get("assessment_mode") == "defensive_evaluation",
              "result assessment_mode == defensive_evaluation")
        check(result_yaml.get("total_cases", 0) >= 8,
              f"result total_cases >= 8 ({result_yaml.get('total_cases')})")
        check("audit_log_complete_count" in result_yaml,
              "result has audit_log_complete_count")
        check("attribution_correct_count" in result_yaml,
              "result has attribution_correct_count")
        check("tamper_evidence_present_count" in result_yaml,
              "result has tamper_evidence_present_count")
        check("audit_gap_detected_count" in result_yaml,
              "result has audit_gap_detected_count")
        check("cross_tenant_isolation_count" in result_yaml,
              "result has cross_tenant_isolation_count")
        check("safe_audit_allowed_count" in result_yaml,
              "result has safe_audit_allowed_count")
        check("human_review_required_count" in result_yaml,
              "result has human_review_required_count")
        check("breakthrough_detected_count" in result_yaml,
              "result has breakthrough_detected_count")
        check("inconclusive_count" in result_yaml, "result has inconclusive_count")
        check(result_yaml.get("confirmed_vulnerability") is False,
              "result confirmed_vulnerability == false")
        check(result_yaml.get("formal_finding_allowed") is False,
              "result formal_finding_allowed == false")
        check(result_yaml.get("production_safety_claimed") is False,
              "result production_safety_claimed == false")
        check(result_yaml.get("real_audit_system_accessed") is False,
              "result real_audit_system_accessed == false")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase92a_m40_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M40", "scorecard module_id == M40")
        check(sm.get("assessment_mode") == "defensive_evaluation",
              "scorecard assessment_mode == defensive_evaluation")
        check(sm.get("simulated_signal_only") is True,
              "scorecard simulated_signal_only == true")
        check(sm.get("confirmed_vulnerability") is False,
              "scorecard confirmed_vulnerability == false")
        check(sm.get("formal_finding_allowed") is False,
              "scorecard formal_finding_allowed == false")
        check(sm.get("production_safety_claimed") is False,
              "scorecard production_safety_claimed == false")
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

        check("audit_log_complete" in rs,
              "scorecard result_summary has audit_log_complete")
        check("attribution_correct" in rs,
              "scorecard result_summary has attribution_correct")
        check("tamper_evidence_present" in rs,
              "scorecard result_summary has tamper_evidence_present")
        check("audit_gap_detected" in rs,
              "scorecard result_summary has audit_gap_detected")
        check("cross_tenant_isolation" in rs,
              "scorecard result_summary has cross_tenant_isolation")
        check("safe_audit_allowed" in rs,
              "scorecard result_summary has safe_audit_allowed")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase92a_m40_agent_action_audit_attribution_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实审计" in notes_text or "no real audit" in notes_text.lower()
              or "real_audit_system" in notes_text.lower(),
              "Notes state no real audit system connection")
        check("confirmed_vulnerability" in notes_text,
              "Notes mention confirmed_vulnerability")
        check("formal_finding_allowed" in notes_text,
              "Notes mention formal_finding_allowed")
        check("defensive_evaluation" in notes_text,
              "Notes mention defensive_evaluation mode")

    # ================================================================
    # 7. Registry check
    # ================================================================
    print("\n7. Registry")
    reg_path = ROOT / "capability_modules/module_registry.yaml"
    reg = yaml_load(reg_path)
    if reg:
        modules = reg.get("modules", [])
        m40 = next((m for m in modules if m.get("module_id") == "M40"), None)
        check(m40 is not None, "M40 exists in registry")
        if m40:
            check(m40.get("production_safety") == "out_of_scope",
                  "Registry M40 production_safety == out_of_scope")
            check(m40.get("confirmed_vulnerability_allowed") is False,
                  "Registry M40 confirmed_vulnerability_allowed == false")

    # ================================================================
    # 8. Security field consistency
    # ================================================================
    print("\n8. Security field consistency")
    deliverables = {
        "corpus (playbook.yaml)": corpus,
        "execution_results.json": exec_results,
        "m40_result.yaml": result_yaml,
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

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Phase 92A M40 Agent Action Audit & Attribution: ALL CHECKS PASSED")
    else:
        print("Phase 92A M40 Agent Action Audit & Attribution: FAILED")
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
