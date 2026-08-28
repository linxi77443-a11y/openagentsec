#!/usr/bin/env python3
"""Phase 98A — M27 File Upload / Document Ingestion Safety MVP Validator.

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
    print("Phase 98A — M27 File Upload / Document Ingestion Safety MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m27_file_upload_document_ingestion_safety_mvp/playbook.yaml"
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
        check("malicious_file_upload" in categories,
              "Corpus includes malicious_file_upload")
        check("document_injection" in categories,
              "Corpus includes document_injection")
        check("file_type_confusion" in categories,
              "Corpus includes file_type_confusion")
        check("path_traversal" in categories,
              "Corpus includes path_traversal")
        check("metadata_tampering" in categories,
              "Corpus includes metadata_tampering")
        check("permission_bypass" in categories,
              "Corpus includes permission_bypass")
        check("content_poisoning" in categories,
              "Corpus includes content_poisoning")
        check("batch_upload_attack" in categories,
              "Corpus includes batch_upload_attack")
        check("control_normal_file_upload" in categories,
              "Corpus includes control_normal_file_upload")
        check("control_standard_document_retrieval" in categories,
              "Corpus includes control_standard_document_retrieval")

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
        check(meta.get("module_id") == "M27", "Corpus module_id == M27")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_file_system_allowed") is False,
              "Corpus real_file_system_allowed == false")
        check(meta.get("real_upload_service_allowed") is False,
              "Corpus real_upload_service_allowed == false")
        check(meta.get("real_storage_backend_allowed") is False,
              "Corpus real_storage_backend_allowed == false")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run config")
    rc_path = ROOT / "run_configs/phase98a_m27_file_upload_document_ingestion_safety_run_config.yaml"
    rc = yaml_load(rc_path)
    check(rc is not None, "Run config YAML loaded")
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase98a", "Run config phase == phase98a")
        check(rcfg.get("module_id") == "M27", "Run config module_id == M27")
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
    exec_path = ROOT / "executions/phase98a_m27_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 8, f"execution_results has >= 8 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("case_id", "MISSING")
            check(r.get("real_file_system_accessed") is False,
                  f"{rid} real_file_system_accessed == false")
            check(r.get("real_upload_service_used") is False,
                  f"{rid} real_upload_service_used == false")
            check(r.get("real_storage_backend_used") is False,
                  f"{rid} real_storage_backend_used == false")
            check(r.get("real_document_parser_used") is False,
                  f"{rid} real_document_parser_used == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase98a_m27_mvp/m27_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m27_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M27", "result module_id == M27")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 8,
              f"result total_cases >= 8 ({result_yaml.get('total_cases')})")
        check("file_type_mismatch_count" in result_yaml,
              "result has file_type_mismatch_count")
        check("document_injection_count" in result_yaml,
              "result has document_injection_count")
        check("path_traversal_count" in result_yaml,
              "result has path_traversal_count")
        check("metadata_tampering_count" in result_yaml,
              "result has metadata_tampering_count")
        check("permission_bypass_count" in result_yaml,
              "result has permission_bypass_count")
        check("content_poisoning_count" in result_yaml,
              "result has content_poisoning_count")
        check("batch_upload_rate_limited_count" in result_yaml,
              "result has batch_upload_rate_limited_count")
        check("benign_request_allowed_count" in result_yaml,
              "result has benign_request_allowed_count")
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
    scorecard_path = ROOT / "executions/phase98a_m27_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M27", "scorecard module_id == M27")
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

        check("file_type_mismatch_detected" in rs,
              "scorecard result_summary has file_type_mismatch_detected")
        check("document_injection_detected" in rs,
              "scorecard result_summary has document_injection_detected")
        check("path_traversal_detected" in rs,
              "scorecard result_summary has path_traversal_detected")
        check("metadata_tampering_detected" in rs,
              "scorecard result_summary has metadata_tampering_detected")
        check("permission_bypass_detected" in rs,
              "scorecard result_summary has permission_bypass_detected")
        check("content_poisoning_detected" in rs,
              "scorecard result_summary has content_poisoning_detected")
        check("batch_upload_rate_limited" in rs,
              "scorecard result_summary has batch_upload_rate_limited")
        check("benign_request_allowed" in rs,
              "scorecard result_summary has benign_request_allowed")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase98a_m27_file_upload_document_ingestion_safety_notes.md"
    check(notes_path.exists(), "Notes file exists")
    if notes_path.exists():
        notes_text = notes_path.read_text()
        check("M27" in notes_text, "Notes reference M27")
        check("File Upload" in notes_text, "Notes reference File Upload")
        check("confirmed_vulnerability: false" in notes_text,
              "Notes include confirmed_vulnerability: false")
        check("formal_finding_allowed: false" in notes_text,
              "Notes include formal_finding_allowed: false")
        check("production_safety_claimed: false" in notes_text,
              "Notes include production_safety_claimed: false")

    # ================================================================
    # 7. Security field consistency
    # ================================================================
    print("\n7. Security field consistency")
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
    # 8. Registry
    # ================================================================
    print("\n8. Registry")
    registry_path = ROOT / "capability_modules/module_registry.yaml"
    registry = yaml_load(registry_path)
    check(registry is not None, "module_registry.yaml loaded")
    if registry:
        modules = registry.get("modules", [])
        m27 = None
        for m in modules:
            if m.get("module_id") == "M27":
                m27 = m
                break
        check(m27 is not None, "M27 entry found in registry")
        if m27:
            check(m27.get("current_status") == "mvp_complete",
                  f"M27 current_status == mvp_complete (got: {m27.get('current_status')})")
            cov = m27.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  f"M27 coverage_status == mvp_complete (got: {cov.get('coverage_status')})")
            check(cov.get("implementation_status") == "mvp_done",
                  f"M27 implementation_status == mvp_done (got: {cov.get('implementation_status')})")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Phase 98A M27 File Upload / Document Ingestion Safety: ALL CHECKS PASSED")
    else:
        print("Phase 98A M27 File Upload / Document Ingestion Safety: FAILED")
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
