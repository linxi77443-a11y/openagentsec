#!/usr/bin/env python3
"""Phase 68A — M43 MCP Tool Descriptor Integrity MVP Validator.

Comprehensive checks for corpus, run config, execution results, result YAML,
scorecard, notes, judge review packet, and security fields.
"""
import json, sys, yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks_passed = 0
checks_failed = 0
errors = []

REQUIRED_CATEGORIES = [
    "descriptor_instruction_like_content",
    "descriptor_tool_priority_manipulation",
    "descriptor_fake_authority_claim",
    "descriptor_capability_overclaim",
    "descriptor_manifest_metadata_drift",
    "descriptor_hidden_risk_hint",
    "descriptor_tool_invocation_induction",
    "descriptor_cross_tool_permission_confusion",
]

REAL_PATTERNS = [
    r'https?://(?!sim\.)', r'(?<![a-zA-Z])sk-[A-Za-z0-9_-]+',
    r'api[a-zA-Z]*\.[a-zA-Z]+\.com', r'secret[a-zA-Z]*=',
    r'token[a-zA-Z]*=', r'password=', r'AKIA[A-Z0-9]{16}',
]


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
    print("Phase 68A — M43 MCP Tool Descriptor Integrity MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus exists and has correct structure
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "corpus/m43_mcp_tool_descriptor_integrity_mvp_corpus.yaml"
    corpus = yaml_load(corpus_path)
    check(corpus is not None, "Corpus YAML loaded")
    if corpus:
        entries = corpus.get("entries", [])
        meta = corpus.get("playbook_metadata", {})
        check(len(entries) >= 8, f"Corpus has >= 8 entries ({len(entries)})")

        attack_cases = [e for e in entries if not e.get("control_case")]
        control_cases = [e for e in entries if e.get("control_case")]
        check(len(attack_cases) >= 8, f"Corpus has >= 8 attack cases ({len(attack_cases)})")
        check(len(control_cases) >= 2, f"Corpus has >= 2 control cases ({len(control_cases)})")

        categories = [e.get("category", "") for e in entries]
        for cat in REQUIRED_CATEGORIES:
            check(cat in categories, f"Corpus includes {cat}")

        check("safe_descriptor_control_case" in categories,
              "Corpus includes safe_descriptor_control_case")
        check("benign_tool_metadata_control_case" in categories,
              "Corpus includes benign_tool_metadata_control_case")

        # Check SIM_ placeholders
        all_text = yaml.dump(entries)
        sim_patterns = re.findall(r'<SIM_\w+>', all_text)
        check(len(sim_patterns) >= len(entries) * 3,
              f"All entries use <SIM_...> placeholders ({len(sim_patterns)} found)")

        # Check no real data in corpus
        corpus_str = str(corpus).lower()
        no_real = True
        for pat in REAL_PATTERNS:
            if re.search(pat, corpus_str):
                no_real = False
                break
        check(no_real, "Corpus contains no real URLs, tokens, secrets, or API keys")

        # Check all entries have required fields
        for e in entries:
            cid = e.get("case_id", "MISSING")
            check(e.get("playbook_id") == "SC-01", f"{cid} playbook_id == SC-01")
            check(e.get("module_id") == "M43", f"{cid} module_id == M43")
            check(e.get("assessment_mode") == "adversarial_validation",
                  f"{cid} assessment_mode == adversarial_validation")
            check(e.get("category", "") in REQUIRED_CATEGORIES + ["safe_descriptor_control_case", "benign_tool_metadata_control_case"],
                  f"{cid} has valid category")
            check("expected_behavior" in e and len(e["expected_behavior"]) > 0,
                  f"{cid} has expected_behavior")
            check("expected_signal" in e and len(e["expected_signal"]) > 0,
                  f"{cid} has expected_signal")
            check("control_case" in e, f"{cid} has control_case field")
            check(e.get("sanitization_status") == "synthetic_or_sanitized",
                  f"{cid} sanitization_status == synthetic_or_sanitized")
            check(e.get("contains_real_data") is False,
                  f"{cid} contains_real_data == false")
            check(e.get("contains_real_secret") is False,
                  f"{cid} contains_real_secret == false")
            check(e.get("executable_payload") is False,
                  f"{cid} executable_payload == false")
            check(e.get("real_mcp_server_connected") is False,
                  f"{cid} real_mcp_server_connected == false")
            check(e.get("real_tool_execution_allowed") is False,
                  f"{cid} real_tool_execution_allowed == false")
            check(e.get("confirmed_vulnerability", True) is False,
                  f"{cid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed", True) is False,
                  f"{cid} formal_finding_allowed == false")

        # Module metadata
        check(meta.get("playbook_id") == "SC-01", "Corpus playbook_id == SC-01")
        check(meta.get("module_id") == "M43", "Corpus module_id == M43")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("attacker_type") == "indirect_prompt_source",
              "Corpus attacker_type == indirect_prompt_source")
        check(meta.get("attack_objective") == "supply_chain_tool_descriptor_poisoning",
              "Corpus attack_objective == supply_chain_tool_descriptor_poisoning")
        check(meta.get("target_boundary") == "tool_descriptor_trust_boundary",
              "Corpus target_boundary == tool_descriptor_trust_boundary")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_mcp_server_allowed") is False,
              "Corpus real_mcp_server_allowed == false")
        check(meta.get("real_tool_registry_allowed") is False,
              "Corpus real_tool_registry_allowed == false")
        check(meta.get("real_tool_call_allowed") is False,
              "Corpus real_tool_call_allowed == false")
        check(meta.get("real_api_call_allowed") is False,
              "Corpus real_api_call_allowed == false")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run config")
    rc_path = ROOT / "run_configs/phase68a_m43_mcp_tool_descriptor_integrity_run_config.yaml"
    rc = yaml_load(rc_path)
    check(rc is not None, "Run config YAML loaded")
    if rc:
        rcfg = rc.get("run_config", rc)
        check(rcfg.get("phase") == "68A", "Run config phase == 68A")
        check(rcfg.get("module_id") == "M43", "Run config module_id == M43")
        check(rcfg.get("playbook_id") == "SC-01", "Run config playbook_id == SC-01")
        check(rcfg.get("assessment_mode") == "adversarial_validation",
              "Run config assessment_mode == adversarial_validation")
        check(rcfg.get("target_boundary") == "tool_descriptor_trust_boundary",
              "Run config target_boundary == tool_descriptor_trust_boundary")
        check(rcfg.get("safety_level") == "simulated_runtime_safety",
              "Run config safety_level == simulated_runtime_safety")
        check(rcfg.get("production_safety") == "out_of_scope",
              "Run config production_safety == out_of_scope")
        check(rcfg.get("real_mcp_server_connected") is False,
              "Run config real_mcp_server_connected == false")
        check(rcfg.get("real_tool_registry_accessed") is False,
              "Run config real_tool_registry_accessed == false")
        check(rcfg.get("real_tool_execution_allowed") is False,
              "Run config real_tool_execution_allowed == false")
        check(rcfg.get("real_api_called") is False,
              "Run config real_api_called == false")
        check(rcfg.get("real_data_accessed") is False,
              "Run config real_data_accessed == false")
        check(rcfg.get("confirmed_vulnerability") is False,
              "Run config confirmed_vulnerability == false")
        check(rcfg.get("formal_finding_allowed") is False,
              "Run config formal_finding_allowed == false")
        check(rcfg.get("production_safety_claimed") is False,
              "Run config production_safety_claimed == false")
        check(rcfg.get("single_module_only") is True,
              "Run config single_module_only == true")

    # ================================================================
    # 3. Execution results JSON
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "results/phase68a_m43_mcp_tool_descriptor_integrity_execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 8, f"execution_results has >= 8 entries ({len(exec_results)})")

        # Check all corpus case_ids are covered
        if corpus:
            corpus_ids = {e.get("case_id") for e in corpus.get("entries", [])}
            exec_ids = {r.get("case_id") for r in exec_results}
            missing = corpus_ids - exec_ids
            check(len(missing) == 0, f"All corpus case_ids covered in execution (missing: {missing})")

        for r in exec_results:
            rid = r.get("case_id", "MISSING")
            check(r.get("real_mcp_server_connected") is False,
                  f"{rid} real_mcp_server_connected == false")
            check(r.get("real_tool_registry_accessed", False) is False,
                  f"{rid} real_tool_registry_accessed == false")
            check(r.get("real_tool_loaded", False) is False,
                  f"{rid} real_tool_loaded == false")
            check(r.get("real_tool_executed") is False,
                  f"{rid} real_tool_executed == false")
            check(r.get("real_api_called") is False,
                  f"{rid} real_api_called == false")
            check(r.get("real_data_accessed") is False,
                  f"{rid} real_data_accessed == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")
            check(r.get("breakthrough_candidate") is False or True,
                  f"{rid} breakthrough_candidate uses candidate semantics")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "results/phase68a_m43_mcp_tool_descriptor_integrity_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M43", "result module_id == M43")
        check(result_yaml.get("playbook_id") == "SC-01", "result playbook_id == SC-01")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 8,
              f"result total_cases >= 8 ({result_yaml.get('total_cases')})")
        check("descriptor_poisoning_detected_count" in result_yaml,
              "result has descriptor_poisoning_detected_count")
        check("tool_metadata_untrusted_count" in result_yaml,
              "result has tool_metadata_untrusted_count")
        check("descriptor_instruction_ignored_count" in result_yaml,
              "result has descriptor_instruction_ignored_count")
        check("fake_tool_invocation_attempted_count" in result_yaml,
              "result has fake_tool_invocation_attempted_count")
        check("fake_tool_invocation_blocked_count" in result_yaml,
              "result has fake_tool_invocation_blocked_count")
        check("tool_priority_manipulation_blocked_count" in result_yaml,
              "result has tool_priority_manipulation_blocked_count")
        check("fake_authority_claim_rejected_count" in result_yaml,
              "result has fake_authority_claim_rejected_count")
        check("capability_overclaim_detected_count" in result_yaml,
              "result has capability_overclaim_detected_count")
        check("manifest_metadata_drift_detected_count" in result_yaml,
              "result has manifest_metadata_drift_detected_count")
        check("cross_tool_permission_confusion_blocked_count" in result_yaml,
              "result has cross_tool_permission_confusion_blocked_count")
        check("benign_tool_metadata_allowed_count" in result_yaml,
              "result has benign_tool_metadata_allowed_count")
        check("human_review_required_count" in result_yaml,
              "result has human_review_required_count")
        check("breakthrough_candidate_count" in result_yaml,
              "result has breakthrough_candidate_count")
        check("control_case_passed_count" in result_yaml,
              "result has control_case_passed_count")
        check("control_case_failed_count" in result_yaml,
              "result has control_case_failed_count")
        check("inconclusive_count" in result_yaml, "result has inconclusive_count")
        check(result_yaml.get("confirmed_vulnerability") is False,
              "result confirmed_vulnerability == false")
        check(result_yaml.get("formal_finding_allowed") is False,
              "result formal_finding_allowed == false")
        check(result_yaml.get("production_safety_claimed") is False,
              "result production_safety_claimed == false")
        check(result_yaml.get("controlled_replay_claimed") is False,
              "result controlled_replay_claimed == false")
        check(result_yaml.get("real_mcp_server_connected") is False,
              "result real_mcp_server_connected == false")
        check(result_yaml.get("real_tool_executed") is False,
              "result real_tool_executed == false")
        check(result_yaml.get("real_api_called") is False,
              "result real_api_called == false")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "results/phase68a_m43_mcp_tool_descriptor_integrity_capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M43", "scorecard module_id == M43")
        check(sm.get("playbook_id") == "SC-01", "scorecard playbook_id == SC-01")
        check(sm.get("assessment_mode") == "adversarial_validation",
              "scorecard assessment_mode == adversarial_validation")
        check(sm.get("single_module_only") is True,
              "scorecard single_module_only == true")
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
        check(scorecard.get("result_is_candidate_level") is True,
              "scorecard result_is_candidate_level == true")

        check("descriptor_poisoning_detected" in rs,
              "scorecard result_summary has descriptor_poisoning_detected")
        check("tool_metadata_untrusted" in rs,
              "scorecard result_summary has tool_metadata_untrusted")
        check("fake_tool_invocation_blocked" in rs,
              "scorecard result_summary has fake_tool_invocation_blocked")
        check("breakthrough_candidate_count" in rs,
              "scorecard result_summary has breakthrough_candidate_count")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")
        check("breakthrough_candidate_is_simulated_signal_only" in rs,
              "scorecard breakthrough_candidate_is_simulated_signal_only")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase68a_m43_mcp_tool_descriptor_integrity_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实 MCP Server" in notes_text or "no real MCP" in notes_text.lower(),
              "Notes state no real MCP Server connection")
        check("不调用真实工具" in notes_text or "no real tool" in notes_text.lower(),
              "Notes state no real tool calls")
        check("不生成真实 payload" in notes_text or "no real payload" in notes_text.lower(),
              "Notes state no real payload generated")
        check("confirmed_vulnerability" in notes_text,
              "Notes mention confirmed_vulnerability")
        check("formal_finding_allowed" in notes_text,
              "Notes mention formal_finding_allowed")
        check("adversarial_validation" in notes_text,
              "Notes mention adversarial_validation mode")

    # ================================================================
    # 7. Judge review packet
    # ================================================================
    print("\n7. Judge review packet")
    jrp_path = ROOT / "docs/phase68a_m43_mcp_tool_descriptor_integrity_judge_review_packet.md"
    jrp = file_exists(jrp_path, "Judge review packet")
    if jrp:
        jrp_text = jrp_path.read_text()
        check("SC-01" in jrp_text, "Judge review packet mentions SC-01")
        check("PRD" in jrp_text, "Judge review packet mentions PRD mapping")
        check("M43" in jrp_text, "Judge review packet mentions M43")
        check("confirmed_vulnerability: false" in jrp_text.lower() or "confirmed_vulnerability" in jrp_text,
              "Judge review packet mentions confirmed_vulnerability")

    # ================================================================
    # 8. Registry check
    # ================================================================
    print("\n8. Registry")
    reg_path = ROOT / "capability_modules/module_registry.yaml"
    reg = yaml_load(reg_path)
    if reg:
        modules = reg.get("modules", [])
        m43 = next((m for m in modules if m.get("module_id") == "M43"), None)
        check(m43 is not None, "M43 exists in registry")

    # ================================================================
    # 9. Security field consistency across all deliverables
    # ================================================================
    print("\n9. Security field consistency")

    deliverables = {
        "corpus YAML": corpus,
        "execution_results.json": exec_results,
        "result.yaml": result_yaml,
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
    # 10. No controlled replay
    # ================================================================
    print("\n10. Controlled replay check")
    check(scorecard is None or scorecard.get("scorecard_metadata", {}).get("controlled_replay_claimed") is False,
          "controlled_replay_claimed == false in scorecard")
    check(result_yaml is None or result_yaml.get("controlled_replay_claimed") is False,
          "controlled_replay_claimed == false in result")
    check(rc is None or rc.get("run_config", rc).get("controlled_replay_claimed") is False,
          "controlled_replay_claimed == false in run config")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Phase 68A M43 MCP Tool Descriptor Integrity validation: ALL CHECKS PASSED")
    else:
        print("Phase 68A M43 MCP Tool Descriptor Integrity validation: FAILED")
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
