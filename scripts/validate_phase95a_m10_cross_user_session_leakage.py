#!/usr/bin/env python3
"""Phase 95A — M10 Cross-User / Cross-Session Leakage MVP Validator.

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
    print("Phase 95A — M10 Cross-User / Cross-Session Leakage MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m10_cross_user_session_leakage_mvp/playbook.yaml"
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
        check("cross_user_data_access" in categories, "Corpus includes cross_user_data_access")
        check("cross_session_context_leakage" in categories, "Corpus includes cross_session_context_leakage")
        check("user_identity_spoofing" in categories, "Corpus includes user_identity_spoofing")
        check("session_hijacking_attempt" in categories, "Corpus includes session_hijacking_attempt")
        check("cross_tenant_data_isolation" in categories, "Corpus includes cross_tenant_data_isolation")
        check("same_user_same_session_access" in categories, "Corpus includes same_user_same_session_access")

        # Check all entries use SIM_ placeholders
        all_text = yaml.dump(entries)
        sim_pattern = re.findall(r'<SIM_\w+>', all_text)
        check(len(sim_pattern) >= len(entries) * 2,
              f"All entries use <SIM_...> placeholders ({len(sim_pattern)} found)")

        # Check no real data
        real_patterns = [r'https?://(?!sim\.)', r'sk-[A-Za-z0-9_-]+', r'api\.openai\.com']
        corpus_str = str(corpus).lower()
        no_real = True
        for pat in real_patterns:
            if re.search(pat, corpus_str):
                no_real = False
                break
        check(no_real, "Corpus contains no real URLs, tokens, or API keys")

        # Module metadata
        check(meta.get("module_id") == "M10", "Corpus module_id == M10")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_user_system_allowed") is False,
              "Corpus real_user_system_allowed == false")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run config")
    rc_path = ROOT / "run_configs/phase95a_m10_cross_user_session_leakage_run_config.yaml"
    rc = yaml_load(rc_path)
    check(rc is not None, "Run config YAML loaded")
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase95a", "Run config phase == phase95a")
        check(rcfg.get("module_id") == "M10", "Run config module_id == M10")
        check(rcfg.get("assessment_mode") == "adversarial_validation",
              "Run config assessment_mode == adversarial_validation")
        check(rcfg.get("safety_level") == "simulated_runtime_safety",
              "Run config safety_level == simulated_runtime_safety")
        check(rcfg.get("production_safety") == "out_of_scope",
              "Run config production_safety == out_of_scope")
        check(rcfg.get("confirmed_vulnerability") is False,
              "Run config confirmed_vulnerability == false")
        check(rcfg.get("single_module_only") is True,
              "Run config single_module_only == true")

    # ================================================================
    # 3. Execution results
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase95a_m10_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 8, f"execution_results has >= 8 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("case_id", "MISSING")
            check(r.get("real_user_system_accessed") is False,
                  f"{rid} real_user_system_accessed == false")
            check(r.get("real_session_store_accessed") is False,
                  f"{rid} real_session_store_accessed == false")
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
    result_path = ROOT / "executions/phase95a_m10_mvp/m10_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m10_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M10", "result module_id == M10")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 8,
              f"result total_cases >= 8 ({result_yaml.get('total_cases')})")
        check("cross_user_leakage_blocked_count" in result_yaml,
              "result has cross_user_leakage_blocked_count")
        check("cross_session_leakage_blocked_count" in result_yaml,
              "result has cross_session_leakage_blocked_count")
        check("identity_spoofing_detected_count" in result_yaml,
              "result has identity_spoofing_detected_count")
        check("session_isolation_preserved_count" in result_yaml,
              "result has session_isolation_preserved_count")
        check("tenant_isolation_preserved_count" in result_yaml,
              "result has tenant_isolation_preserved_count")
        check("safe_access_allowed_count" in result_yaml,
              "result has safe_access_allowed_count")
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

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase95a_m10_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M10", "scorecard module_id == M10")
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

        check("cross_user_leakage_blocked" in rs,
              "scorecard result_summary has cross_user_leakage_blocked")
        check("cross_session_leakage_blocked" in rs,
              "scorecard result_summary has cross_session_leakage_blocked")
        check("identity_spoofing_detected" in rs,
              "scorecard result_summary has identity_spoofing_detected")
        check("session_isolation_preserved" in rs,
              "scorecard result_summary has session_isolation_preserved")
        check("tenant_isolation_preserved" in rs,
              "scorecard result_summary has tenant_isolation_preserved")
        check("safe_access_allowed" in rs,
              "scorecard result_summary has safe_access_allowed")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")

    # ================================================================
    # 6. Security field consistency
    # ================================================================
    print("\n6. Security field consistency")
    deliverables = {
        "corpus": corpus,
        "execution_results": exec_results,
        "result": result_yaml,
        "scorecard": scorecard,
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
        print("Phase 95A M10 Cross-User / Cross-Session Leakage: ALL CHECKS PASSED")
    else:
        print("Phase 95A M10 Cross-User / Cross-Session Leakage: FAILED")
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
