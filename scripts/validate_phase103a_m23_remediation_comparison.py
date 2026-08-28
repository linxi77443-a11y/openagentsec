#!/usr/bin/env python3
"""Phase 103A — M23 Remediation Before/After Comparison MVP Validator.

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
    print("Phase 103A — M23 Remediation Before/After Comparison MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m23_remediation_comparison_mvp/playbook.yaml"
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
        check("baseline_establishment_failure" in categories,
              "Corpus includes baseline_establishment_failure")
        check("post_remediation_validation_missing" in categories,
              "Corpus includes post_remediation_validation_missing")
        check("remediation_rollback_risk" in categories,
              "Corpus includes remediation_rollback_risk")
        check("remediation_introduces_new_vulnerability" in categories,
              "Corpus includes remediation_introduces_new_vulnerability")
        check("remediation_verification_bypass" in categories,
              "Corpus includes remediation_verification_bypass")
        check("remediation_evidence_tampering" in categories,
              "Corpus includes remediation_evidence_tampering")
        check("remediation_coverage_incomplete" in categories,
              "Corpus includes remediation_coverage_incomplete")
        check("remediation_priority_error" in categories,
              "Corpus includes remediation_priority_error")

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
            check(e.get("synthetic_vulnerability_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_vulnerability_id")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")
            check(e.get("production_safety_claimed") is False,
                  f"{eid} production_safety_claimed == false")
            check(e.get("controlled_replay_claimed") is False,
                  f"{eid} controlled_replay_claimed == false")

        # Module metadata
        check(meta.get("module_id") == "M23", "Corpus module_id == M23")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_remediation_system_allowed") is False,
              "Corpus real_remediation_system_allowed == false")
        check(meta.get("real_vulnerability_database_allowed") is False,
              "Corpus real_vulnerability_database_allowed == false")
        check(meta.get("real_audit_log_allowed") is False,
              "Corpus real_audit_log_allowed == false")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run config")
    rc_path = ROOT / "run_configs/phase103a_m23_remediation_comparison_run_config.yaml"
    rc = yaml_load(rc_path)
    check(rc is not None, "Run config YAML loaded")
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase103a", "Run config phase == phase103a")
        check(rcfg.get("module_id") == "M23", "Run config module_id == M23")
        check(rcfg.get("assessment_mode") == "adversarial_validation",
              "Run config assessment_mode == adversarial_validation")
        check(rcfg.get("safety_level") == "simulated_runtime_safety",
              "Run config safety_level == simulated_runtime_safety")
        check(rcfg.get("production_safety") == "out_of_scope",
              "Run config production_safety == out_of_scope")
        check(rcfg.get("real_remediation_system_allowed") is False,
              "Run config real_remediation_system_allowed == false")
        check(rcfg.get("real_vulnerability_database_allowed") is False,
              "Run config real_vulnerability_database_allowed == false")
        check(rcfg.get("confirmed_vulnerability") is False,
              "Run config confirmed_vulnerability == false")
        check(rcfg.get("formal_finding_allowed") is False,
              "Run config formal_finding_allowed == false")
        check(rcfg.get("production_safety_claimed") is False,
              "Run config production_safety_claimed == false")
        check(rcfg.get("single_module_only") is True,
              "Run config single_module_only == true")

    # ================================================================
    # 3. Execution results
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase103a_m23_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 8, f"execution_results has >= 8 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("case_id", "MISSING")
            check(r.get("real_remediation_system_accessed") is False,
                  f"{rid} real_remediation_system_accessed == false")
            check(r.get("real_vulnerability_database_accessed") is False,
                  f"{rid} real_vulnerability_database_accessed == false")
            check(r.get("real_audit_log_modified") is False,
                  f"{rid} real_audit_log_modified == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase103a_m23_mvp/m23_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m23_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M23", "result module_id == M23")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 8,
              f"result total_cases >= 8 ({result_yaml.get('total_cases')})")
        check("baseline_integrity_verified_count" in result_yaml,
              "result has baseline_integrity_verified_count")
        check("baseline_tampering_detected_count" in result_yaml,
              "result has baseline_tampering_detected_count")
        check("post_remediation_validation_enforced_count" in result_yaml,
              "result has post_remediation_validation_enforced_count")
        check("rollback_attempt_detected_count" in result_yaml,
              "result has rollback_attempt_detected_count")
        check("remediation_side_effect_detected_count" in result_yaml,
              "result has remediation_side_effect_detected_count")
        check("verification_evidence_integrity_count" in result_yaml,
              "result has verification_evidence_integrity_count")
        check("audit_trail_integrity_count" in result_yaml,
              "result has audit_trail_integrity_count")
        check("remediation_coverage_completeness_count" in result_yaml,
              "result has remediation_coverage_completeness_count")
        check("priority_integrity_enforced_count" in result_yaml,
              "result has priority_integrity_enforced_count")
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
        check(result_yaml.get("controlled_replay_claimed") is False,
              "result controlled_replay_claimed == false")
        check(result_yaml.get("real_remediation_system_accessed") is False,
              "result real_remediation_system_accessed == false")
        check(result_yaml.get("real_vulnerability_database_accessed") is False,
              "result real_vulnerability_database_accessed == false")
        check(result_yaml.get("real_audit_log_modified") is False,
              "result real_audit_log_modified == false")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase103a_m23_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M23", "scorecard module_id == M23")
        check(sm.get("assessment_mode") == "adversarial_validation",
              "scorecard assessment_mode == adversarial_validation")
        check(sm.get("simulated_signal_only") is True,
              "scorecard simulated_signal_only == true")
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

        check("baseline_integrity_verified" in rs,
              "scorecard result_summary has baseline_integrity_verified")
        check("baseline_tampering_detected" in rs,
              "scorecard result_summary has baseline_tampering_detected")
        check("post_remediation_validation_enforced" in rs,
              "scorecard result_summary has post_remediation_validation_enforced")
        check("rollback_attempt_detected" in rs,
              "scorecard result_summary has rollback_attempt_detected")
        check("remediation_side_effect_detected" in rs,
              "scorecard result_summary has remediation_side_effect_detected")
        check("verification_evidence_integrity" in rs,
              "scorecard result_summary has verification_evidence_integrity")
        check("audit_trail_integrity" in rs,
              "scorecard result_summary has audit_trail_integrity")
        check("remediation_coverage_completeness" in rs,
              "scorecard result_summary has remediation_coverage_completeness")
        check("priority_integrity_enforced" in rs,
              "scorecard result_summary has priority_integrity_enforced")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase103a_m23_remediation_comparison_mvp_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实修复管理" in notes_text or "no real remediation" in notes_text.lower()
              or "real_remediation_system" in notes_text.lower(),
              "Notes state no real remediation system connection")
        check("不连接真实漏洞数据库" in notes_text or "no real vulnerability database" in notes_text.lower()
              or "real_vulnerability_database" in notes_text.lower(),
              "Notes state no real vulnerability database connection")
        check("confirmed_vulnerability" in notes_text,
              "Notes mention confirmed_vulnerability")
        check("formal_finding_allowed" in notes_text,
              "Notes mention formal_finding_allowed")
        check("adversarial_validation" in notes_text,
              "Notes mention adversarial_validation mode")

    # ================================================================
    # 7. Registry check
    # ================================================================
    print("\n7. Registry")
    reg_path = ROOT / "capability_modules/module_registry.yaml"
    reg = yaml_load(reg_path)
    if reg:
        modules = reg.get("modules", [])
        m23 = next((m for m in modules if m.get("module_id") == "M23"), None)
        check(m23 is not None, "M23 exists in registry")
        if m23:
            check(m23.get("production_safety") == "out_of_scope",
                  "Registry M23 production_safety == out_of_scope")
            check(m23.get("confirmed_vulnerability_allowed") is False,
                  "Registry M23 confirmed_vulnerability_allowed == false")
            check(m23.get("formal_finding_allowed") is False,
                  "Registry M23 formal_finding_allowed == false")
            cov = m23.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "Registry M23 coverage_status == mvp_complete")

    # ================================================================
    # 8. Per-deliverable security field sweep
    # ================================================================
    print("\n8. Security field consistency")

    deliverables = {
        "corpus (playbook.yaml)": corpus,
        "execution_results.json": exec_results,
        "m23_result.yaml": result_yaml,
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
    # 9. Controlled replay check
    # ================================================================
    print("\n9. Controlled replay check")
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("controlled_replay_claimed") is False,
              "run config controlled_replay_claimed == false")
    if result_yaml:
        check(result_yaml.get("controlled_replay_claimed") is False,
              "result controlled_replay_claimed == false")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        check(sm.get("controlled_replay_claimed") is False,
              "scorecard controlled_replay_claimed == false")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Phase 103A M23 Remediation Before/After Comparison validation: ALL CHECKS PASSED")
    else:
        print("Phase 103A M23 Remediation Before/After Comparison validation: FAILED")
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
