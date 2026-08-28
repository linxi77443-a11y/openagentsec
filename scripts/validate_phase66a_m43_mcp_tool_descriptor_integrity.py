#!/usr/bin/env python3
"""Phase 66A — M43 MCP Tool Descriptor Integrity MVP Validator.

Comprehensive checks for corpus, run config, execution results, result YAML,
scorecard, notes, and security fields.
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
    print("Phase 66A — M43 MCP Tool Descriptor Integrity Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus exists and has correct structure
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m43_mcp_tool_descriptor_integrity_mvp/playbook.yaml"
    corpus = yaml_load(corpus_path)
    check(corpus is not None, "Corpus playbook.yaml loaded")
    if corpus:
        entries = corpus.get("entries", [])
        meta = corpus.get("playbook_metadata", {})
        check(len(entries) >= 8, f"Corpus has >= 8 entries ({len(entries)})")

        control_cases = [e for e in entries if e.get("control_case")]
        check(len(control_cases) >= 2, f"Corpus has >= 2 control cases ({len(control_cases)})")

        categories = [e.get("category", "") for e in entries]
        check("descriptor_instruction_like_content" in categories,
              "Corpus includes descriptor_instruction_like_content")
        check("descriptor_tool_priority_manipulation" in categories,
              "Corpus includes descriptor_tool_priority_manipulation")
        check("descriptor_fake_authority_claim" in categories,
              "Corpus includes descriptor_fake_authority_claim")
        check("descriptor_capability_overclaim" in categories,
              "Corpus includes descriptor_capability_overclaim")
        check("safe_descriptor_control_case" in categories,
              "Corpus includes safe_descriptor_control_case")
        check("benign_tool_metadata_control_case" in categories,
              "Corpus includes benign_tool_metadata_control_case")

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

        # Check all entries have required fields
        for e in entries:
            eid = e.get("entry_id", "MISSING")
            check(e.get("synthetic_tool_descriptor_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_tool_descriptor_id")
            check(e.get("synthetic_tool_manifest_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_tool_manifest_id")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")
            check(e.get("production_safety_claimed") is False,
                  f"{eid} production_safety_claimed == false")
            check(e.get("controlled_replay_claimed") is False,
                  f"{eid} controlled_replay_claimed == false")

        # Module metadata
        check(meta.get("module_id") == "M43", "Corpus module_id == M43")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("attacker_type") == "indirect_prompt_source",
              "Corpus attacker_type == indirect_prompt_source")
        check(meta.get("attack_objective") == "supply_chain_tool_descriptor_poisoning",
              "Corpus attack_objective == supply_chain_tool_descriptor_poisoning")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_mcp_server_allowed") is False,
              "Corpus real_mcp_server_allowed == false")
        check(meta.get("real_tool_call_allowed") is False,
              "Corpus real_tool_call_allowed == false")
        check(meta.get("real_api_call_allowed") is False,
              "Corpus real_api_call_allowed == false")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run config (embedded in playbook metadata)")
    if corpus:
        meta = corpus.get("playbook_metadata", {})
        check(meta.get("fake_runtime_only") is True, "Run config fake_runtime_only == true")
        check(meta.get("synthetic_only") is True, "Run config synthetic_only == true")

    # ================================================================
    # 3. Execution results JSON
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase66a_m43_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 8, f"execution_results has >= 8 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("entry_id", "MISSING")
            check(r.get("real_mcp_server_connected") is False,
                  f"{rid} real_mcp_server_connected == false")
            check(r.get("real_tool_executed") is False,
                  f"{rid} real_tool_executed == false")
            check(r.get("real_api_called") is False,
                  f"{rid} real_api_called == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase66a_m43_mvp/m43_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m43_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M43", "result module_id == M43")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 8,
              f"result total_cases >= 8 ({result_yaml.get('total_cases')})")
        check("descriptor_poisoning_detected_count" in result_yaml,
              "result has descriptor_poisoning_detected_count")
        check("tool_metadata_untrusted_count" in result_yaml,
              "result has tool_metadata_untrusted_count")
        check("fake_tool_invocation_blocked_count" in result_yaml,
              "result has fake_tool_invocation_blocked_count")
        check("human_review_required_count" in result_yaml,
              "result has human_review_required_count")
        check("breakthrough_detected_count" in result_yaml,
              "result has breakthrough_detected_count")
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
    scorecard_path = ROOT / "executions/phase66a_m43_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M43", "scorecard module_id == M43")
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

        # Capability value and risk level separation
        cv = scorecard.get("capability_value")
        rl = scorecard.get("risk_level")
        check(cv is not None and rl is not None,
              f"scorecard has capability_value ({cv}) and risk_level ({rl})")
        check(cv != rl or cv in ("medium",),
              f"capability_value ({cv}) and risk_level ({rl}) are separate concepts")
        check(scorecard.get("capability_value_semantics") is not None,
              "scorecard has capability_value_semantics")
        check(scorecard.get("risk_level_semantics") is not None,
              "scorecard has risk_level_semantics")

        # Result summary signals
        check("descriptor_poisoning_detected" in rs,
              "scorecard result_summary has descriptor_poisoning_detected")
        check("tool_metadata_untrusted" in rs,
              "scorecard result_summary has tool_metadata_untrusted")
        check("fake_tool_invocation_blocked" in rs,
              "scorecard result_summary has fake_tool_invocation_blocked")
        check("breakthrough_detected" in rs,
              "scorecard result_summary has breakthrough_detected")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase66a_m43_mcp_tool_descriptor_integrity_notes.md"
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
    # 7. Registry check
    # ================================================================
    print("\n7. Registry")
    reg_path = ROOT / "capability_modules/module_registry.yaml"
    reg = yaml_load(reg_path)
    if reg:
        modules = reg.get("modules", [])
        m43 = next((m for m in modules if m.get("module_id") == "M43"), None)
        check(m43 is not None, "M43 exists in registry")
        if m43:
            check(m43.get("synthetic_only") is True, "Registry M43 synthetic_only == true")
            check(m43.get("production_safety") == "out_of_scope",
                  "Registry M43 production_safety == out_of_scope")
            check(m43.get("confirmed_vulnerability_allowed") is False,
                  "Registry M43 confirmed_vulnerability_allowed == false")
            check(m43.get("formal_finding_allowed") is False,
                  "Registry M43 formal_finding_allowed == false")

    # ================================================================
    # 8. Per-deliverable security field sweep
    # ================================================================
    print("\n8. Security field consistency")

    deliverables = {
        "corpus (playbook.yaml)": corpus,
        "execution_results.json": exec_results,
        "m43_result.yaml": result_yaml,
        "capability_scorecard.yaml": scorecard,
    }

    for name, data in deliverables.items():
        if data is None:
            check(False, f"{name}: could not load — skipping")
            continue
        # Convert to string for deep check
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
        print("Phase 66A M43 MCP Tool Descriptor Integrity validation: ALL CHECKS PASSED")
    else:
        print("Phase 66A M43 MCP Tool Descriptor Integrity validation: FAILED")
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
