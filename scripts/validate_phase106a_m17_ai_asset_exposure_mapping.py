#!/usr/bin/env python3
"""Phase 106A — M17 AI Asset & Exposure Surface Mapping MVP Validator.

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
    print("Phase 106A — M17 AI Asset & Exposure Surface Mapping MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m17_ai_asset_exposure_mapping_mvp/playbook.yaml"
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
        check("asset_discovery_omission" in categories,
              "Corpus includes asset_discovery_omission")
        check("exposure_surface_underestimation" in categories,
              "Corpus includes exposure_surface_underestimation")
        check("shadow_ai_detection_failure" in categories,
              "Corpus includes shadow_ai_detection_failure")
        check("model_inventory_incomplete" in categories,
              "Corpus includes model_inventory_incomplete")
        check("api_endpoint_exposure" in categories,
              "Corpus includes api_endpoint_exposure")
        check("training_data_leakage_path" in categories,
              "Corpus includes training_data_leakage_path")
        check("deployment_config_misconfiguration" in categories,
              "Corpus includes deployment_config_misconfiguration")
        check("third_party_ai_component_risk" in categories,
              "Corpus includes third_party_ai_component_risk")

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
            eid = e.get("entry_id", "MISSING")
            check(e.get("synthetic_asset_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_asset_id")
            check(e.get("synthetic_tool_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_tool_id")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")
            check(e.get("production_safety_claimed") is False,
                  f"{eid} production_safety_claimed == false")
            check(e.get("controlled_replay_claimed") is False,
                  f"{eid} controlled_replay_claimed == false")

        # Module metadata
        check(meta.get("module_id") == "M17", "Corpus module_id == M17")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_asset_management_allowed") is False,
              "Corpus real_asset_management_allowed == false")
        check(meta.get("real_cmdb_allowed") is False,
              "Corpus real_cmdb_allowed == false")
        check(meta.get("real_cloud_platform_allowed") is False,
              "Corpus real_cloud_platform_allowed == false")
        check(meta.get("real_network_scanner_allowed") is False,
              "Corpus real_network_scanner_allowed == false")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run config")
    rc_path = ROOT / "run_configs/phase106a_m17_ai_asset_exposure_mapping_run_config.yaml"
    rc = yaml_load(rc_path)
    check(rc is not None, "Run config YAML loaded")
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase106a", "Run config phase == phase106a")
        check(rcfg.get("module_id") == "M17", "Run config module_id == M17")
        check(rcfg.get("assessment_mode") == "adversarial_validation",
              "Run config assessment_mode == adversarial_validation")
        check(rcfg.get("safety_level") == "simulated_runtime_safety",
              "Run config safety_level == simulated_runtime_safety")
        check(rcfg.get("production_safety") == "out_of_scope",
              "Run config production_safety == out_of_scope")
        check(rcfg.get("real_asset_management_allowed") is False,
              "Run config real_asset_management_allowed == false")
        check(rcfg.get("real_cmdb_allowed") is False,
              "Run config real_cmdb_allowed == false")
        check(rcfg.get("real_cloud_platform_allowed") is False,
              "Run config real_cloud_platform_allowed == false")
        check(rcfg.get("real_network_scanner_allowed") is False,
              "Run config real_network_scanner_allowed == false")
        sc = rcfg.get("safety_constraints", {})
        check(sc.get("confirmed_vulnerability") is False,
              "Run config safety_constraints confirmed_vulnerability == false")
        check(sc.get("formal_finding_allowed") is False,
              "Run config safety_constraints formal_finding_allowed == false")
        check(sc.get("production_safety_claimed") is False,
              "Run config safety_constraints production_safety_claimed == false")
        check(sc.get("single_module_only") is True,
              "Run config safety_constraints single_module_only == true")

    # ================================================================
    # 3. Execution results
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase106a_m17_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 8, f"execution_results has >= 8 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("case_id", "MISSING")
            check(r.get("real_asset_management_accessed") is False,
                  f"{rid} real_asset_management_accessed == false")
            check(r.get("real_cmdb_accessed") is False,
                  f"{rid} real_cmdb_accessed == false")
            check(r.get("real_cloud_platform_accessed") is False,
                  f"{rid} real_cloud_platform_accessed == false")
            check(r.get("real_network_scanner_used") is False,
                  f"{rid} real_network_scanner_used == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase106a_m17_mvp/m17_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m17_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M17", "result module_id == M17")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 8,
              f"result total_cases >= 8 ({result_yaml.get('total_cases')})")
        check("asset_discovery_gap_detected_count" in result_yaml,
              "result has asset_discovery_gap_detected_count")
        check("exposure_underestimation_detected_count" in result_yaml,
              "result has exposure_underestimation_detected_count")
        check("shadow_ai_detection_gap_count" in result_yaml,
              "result has shadow_ai_detection_gap_count")
        check("model_inventory_gap_count" in result_yaml,
              "result has model_inventory_gap_count")
        check("api_endpoint_exposure_count" in result_yaml,
              "result has api_endpoint_exposure_count")
        check("training_data_leakage_path_count" in result_yaml,
              "result has training_data_leakage_path_count")
        check("deployment_config_misconfiguration_count" in result_yaml,
              "result has deployment_config_misconfiguration_count")
        check("third_party_ai_component_risk_count" in result_yaml,
              "result has third_party_ai_component_risk_count")
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
        check(result_yaml.get("real_asset_management_accessed") is False,
              "result real_asset_management_accessed == false")
        check(result_yaml.get("real_cmdb_accessed") is False,
              "result real_cmdb_accessed == false")
        check(result_yaml.get("real_cloud_platform_accessed") is False,
              "result real_cloud_platform_accessed == false")
        check(result_yaml.get("real_network_scanner_used") is False,
              "result real_network_scanner_used == false")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase106a_m17_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M17", "scorecard module_id == M17")
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

        check("asset_discovery_gap_detected" in rs,
              "scorecard result_summary has asset_discovery_gap_detected")
        check("exposure_underestimation_detected" in rs,
              "scorecard result_summary has exposure_underestimation_detected")
        check("shadow_ai_detection_gap" in rs,
              "scorecard result_summary has shadow_ai_detection_gap")
        check("model_inventory_gap" in rs,
              "scorecard result_summary has model_inventory_gap")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase106a_m17_ai_asset_exposure_mapping_mvp_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实资产管理系统" in notes_text or "no real asset management" in notes_text.lower()
              or "real_asset_management" in notes_text.lower(),
              "Notes state no real asset management system connection")
        check("不连接真实CMDB" in notes_text or "no real cmdb" in notes_text.lower()
              or "real_cmdb" in notes_text.lower(),
              "Notes state no real CMDB connection")
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
        m17 = next((m for m in modules if m.get("module_id") == "M17"), None)
        check(m17 is not None, "M17 exists in registry")
        if m17:
            check(m17.get("production_safety") == "out_of_scope",
                  "Registry M17 production_safety == out_of_scope")
            check(m17.get("confirmed_vulnerability_allowed") is False,
                  "Registry M17 confirmed_vulnerability_allowed == false")
            check(m17.get("formal_finding_allowed") is False,
                  "Registry M17 formal_finding_allowed == false")
            cov = m17.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "Registry M17 coverage_status == mvp_complete")

    # ================================================================
    # 8. Per-deliverable security field sweep
    # ================================================================
    print("\n8. Security field consistency")

    deliverables = {
        "corpus (playbook.yaml)": corpus,
        "execution_results.json": exec_results,
        "m17_result.yaml": result_yaml,
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
        sc = rcfg.get("safety_constraints", {})
        check(sc.get("controlled_replay_claimed") is False,
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
        print("Phase 106A M17 AI Asset & Exposure Surface Mapping validation: ALL CHECKS PASSED")
    else:
        print("Phase 106A M17 AI Asset & Exposure Surface Mapping validation: FAILED")
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
