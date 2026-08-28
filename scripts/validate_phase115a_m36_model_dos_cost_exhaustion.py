#!/usr/bin/env python3
"""Phase 115A — M36 Model DoS / Cost Exhaustion MVP Validator.

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
        print(f"  \u2713 {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  \u2717 {msg}")


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
    print("Phase 115A — M36 Model DoS / Cost Exhaustion MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m36_model_dos_cost_exhaustion_mvp/playbook.yaml"
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
        check("request_flooding_attack" in categories,
              "Corpus includes request_flooding_attack")
        check("long_context_exhaustion" in categories,
              "Corpus includes long_context_exhaustion")
        check("nested_call_loop" in categories,
              "Corpus includes nested_call_loop")
        check("resource_intensive_query" in categories,
              "Corpus includes resource_intensive_query")
        check("cost_exhaustion_attack" in categories,
              "Corpus includes cost_exhaustion_attack")
        check("api_quota_exhaustion" in categories,
              "Corpus includes api_quota_exhaustion")
        check("model_inference_overload" in categories,
              "Corpus includes model_inference_overload")
        check("async_task_pileup" in categories,
              "Corpus includes async_task_pileup")

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
            check(e.get("synthetic_target_endpoint", "").startswith("<SIM_")
                  or e.get("synthetic_flood_config", "").startswith("<SIM_")
                  or e.get("synthetic_long_context", "").startswith("<SIM_")
                  or e.get("synthetic_loop_trigger", "").startswith("<SIM_")
                  or e.get("synthetic_computation_bomb", "").startswith("<SIM_")
                  or e.get("synthetic_budget_target", "").startswith("<SIM_")
                  or e.get("synthetic_quota_pool", "").startswith("<SIM_")
                  or e.get("synthetic_concurrent_config", "").startswith("<SIM_")
                  or e.get("synthetic_task_generator", "").startswith("<SIM_")
                  or e.get("synthetic_request_config", "").startswith("<SIM_")
                  or e.get("synthetic_batch_config", "").startswith("<SIM_"),
                  f"{eid} has SIM placeholder")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")
            check(e.get("production_safety_claimed") is False,
                  f"{eid} production_safety_claimed == false")
            check(e.get("controlled_replay_claimed") is False,
                  f"{eid} controlled_replay_claimed == false")

        # Module metadata
        check(meta.get("module_id") == "M36", "Corpus module_id == M36")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Corpus assessment_mode == adversarial_validation")
        check(meta.get("synthetic_only") is True, "Corpus synthetic_only == true")
        check(meta.get("real_api_gateway_allowed") is False,
              "Corpus real_api_gateway_allowed == false")
        check(meta.get("real_billing_system_allowed") is False,
              "Corpus real_billing_system_allowed == false")
        check(meta.get("real_model_endpoint_allowed") is False,
              "Corpus real_model_endpoint_allowed == false")
        check(meta.get("real_quota_system_allowed") is False,
              "Corpus real_quota_system_allowed == false")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run config")
    rc_path = ROOT / "run_configs/phase115a_m36_model_dos_cost_exhaustion_run_config.yaml"
    rc = yaml_load(rc_path)
    check(rc is not None, "Run config YAML loaded")
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase115a", "Run config phase == phase115a")
        check(rcfg.get("module_id") == "M36", "Run config module_id == M36")
        check(rcfg.get("assessment_mode") == "adversarial_validation",
              "Run config assessment_mode == adversarial_validation")
        check(rcfg.get("safety_level") == "simulated_runtime_safety",
              "Run config safety_level == simulated_runtime_safety")
        check(rcfg.get("production_safety") == "out_of_scope",
              "Run config production_safety == out_of_scope")
        check(rcfg.get("real_api_gateway_allowed") is False,
              "Run config real_api_gateway_allowed == false")
        check(rcfg.get("real_billing_system_allowed") is False,
              "Run config real_billing_system_allowed == false")
        check(rcfg.get("real_model_endpoint_allowed") is False,
              "Run config real_model_endpoint_allowed == false")
        check(rcfg.get("real_quota_system_allowed") is False,
              "Run config real_quota_system_allowed == false")
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
    exec_path = ROOT / "executions/phase115a_m36_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 8, f"execution_results has >= 8 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("case_id", "MISSING")
            check(r.get("real_api_gateway_accessed") is False,
                  f"{rid} real_api_gateway_accessed == false")
            check(r.get("real_billing_system_accessed") is False,
                  f"{rid} real_billing_system_accessed == false")
            check(r.get("real_model_endpoint_accessed") is False,
                  f"{rid} real_model_endpoint_accessed == false")
            check(r.get("real_quota_system_accessed") is False,
                  f"{rid} real_quota_system_accessed == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase115a_m36_mvp/m36_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m36_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M36", "result module_id == M36")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 8,
              f"result total_cases >= 8 ({result_yaml.get('total_cases')})")
        check("request_flooding_attack_count" in result_yaml,
              "result has request_flooding_attack_count")
        check("long_context_exhaustion_count" in result_yaml,
              "result has long_context_exhaustion_count")
        check("nested_call_loop_count" in result_yaml,
              "result has nested_call_loop_count")
        check("resource_intensive_query_count" in result_yaml,
              "result has resource_intensive_query_count")
        check("cost_exhaustion_attack_count" in result_yaml,
              "result has cost_exhaustion_attack_count")
        check("api_quota_exhaustion_count" in result_yaml,
              "result has api_quota_exhaustion_count")
        check("model_inference_overload_count" in result_yaml,
              "result has model_inference_overload_count")
        check("async_task_pileup_count" in result_yaml,
              "result has async_task_pileup_count")
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
        check(result_yaml.get("real_api_gateway_accessed") is False,
              "result real_api_gateway_accessed == false")
        check(result_yaml.get("real_billing_system_accessed") is False,
              "result real_billing_system_accessed == false")
        check(result_yaml.get("real_model_endpoint_accessed") is False,
              "result real_model_endpoint_accessed == false")
        check(result_yaml.get("real_quota_system_accessed") is False,
              "result real_quota_system_accessed == false")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase115a_m36_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M36", "scorecard module_id == M36")
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

        check("request_flooding_attack_detected" in rs,
              "scorecard result_summary has request_flooding_attack_detected")
        check("long_context_exhaustion_detected" in rs,
              "scorecard result_summary has long_context_exhaustion_detected")
        check("nested_call_loop_detected" in rs,
              "scorecard result_summary has nested_call_loop_detected")
        check("resource_intensive_query_detected" in rs,
              "scorecard result_summary has resource_intensive_query_detected")
        check("cost_exhaustion_attack_detected" in rs,
              "scorecard result_summary has cost_exhaustion_attack_detected")
        check("api_quota_exhaustion_detected" in rs,
              "scorecard result_summary has api_quota_exhaustion_detected")
        check("model_inference_overload_detected" in rs,
              "scorecard result_summary has model_inference_overload_detected")
        check("async_task_pileup_detected" in rs,
              "scorecard result_summary has async_task_pileup_detected")
        check("human_review_required" in rs,
              "scorecard result_summary has human_review_required")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase115a_m36_model_dos_cost_exhaustion_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实 API 网关" in notes_text or "no real api gateway" in notes_text.lower()
              or "real_api_gateway" in notes_text.lower(),
              "Notes state no real API gateway connection")
        check("不连接真实计费系统" in notes_text or "no real billing" in notes_text.lower()
              or "real_billing_system" in notes_text.lower(),
              "Notes state no real billing system connection")
        check("不连接真实模型推理端点" in notes_text or "no real model endpoint" in notes_text.lower()
              or "real_model_endpoint" in notes_text.lower(),
              "Notes state no real model endpoint connection")
        check("不连接真实配额管理系统" in notes_text or "no real quota" in notes_text.lower()
              or "real_quota_system" in notes_text.lower(),
              "Notes state no real quota system connection")
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
        m36 = next((m for m in modules if m.get("module_id") == "M36"), None)
        check(m36 is not None, "M36 exists in registry")
        if m36:
            check(m36.get("production_safety") == "out_of_scope",
                  "Registry M36 production_safety == out_of_scope")
            check(m36.get("confirmed_vulnerability_allowed") is False,
                  "Registry M36 confirmed_vulnerability_allowed == false")
            check(m36.get("formal_finding_allowed") is False,
                  "Registry M36 formal_finding_allowed == false")
            cov = m36.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "Registry M36 coverage_status == mvp_complete")

    # ================================================================
    # 8. Per-deliverable security field sweep
    # ================================================================
    print("\n8. Security field consistency")

    deliverables = {
        "corpus (playbook.yaml)": corpus,
        "execution_results.json": exec_results,
        "m36_result.yaml": result_yaml,
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
        print("Phase 115A M36 Model DoS / Cost Exhaustion validation: ALL CHECKS PASSED")
    else:
        print("Phase 115A M36 Model DoS / Cost Exhaustion validation: FAILED")
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
