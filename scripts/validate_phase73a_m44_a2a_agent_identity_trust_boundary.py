#!/usr/bin/env python3
"""Phase 73A — M44 A2A Agent Identity Trust Boundary MVP Validator.

Comprehensive checks for playbook, run config, execution results, result YAML,
scorecard, notes, and security fields. Review-only: no real execution.
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


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 73A — M44 A2A Agent Identity Trust Boundary")
    print("Adversarial Validation — ALL CHECKS")
    print("=" * 60)

    # ================================================================
    # 1. Playbook existence and structure
    # ================================================================
    print("\n1. Playbook")
    playbook_path = ROOT / "adversarial_playbooks/m44_a2a_agent_identity_trust_boundary_mvp/playbook.yaml"
    playbook = yaml_load(playbook_path)
    check(playbook is not None, "Playbook playbook.yaml loaded")
    if playbook:
        entries = playbook.get("entries", [])
        meta = playbook.get("playbook_metadata", {})
        check(len(entries) >= 12, f"Playbook has >= 12 entries ({len(entries)})")

        control_cases = [e for e in entries if e.get("control_case")]
        check(len(control_cases) >= 2, f"Playbook has >= 2 control cases ({len(control_cases)})")

        categories = [e.get("category", "") for e in entries]
        expected_categories = [
            "agent_identity_spoofing",
            "capability_claim_forgery",
            "delegation_authorization_bypass",
            "agent_identity_with_escalated_permissions",
            "agent_trust_inheritance_abuse",
            "self_signed_agent_card",
            "malicious_agent_discovery",
            "agent_task_delegation_without_context",
            "agent_identity_spoofing_with_fake_signature",
            "capability_claim_elevation",
            "valid_agent_identity_verified",
            "benign_agent_discovery",
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
            check(e.get("synthetic_agent_card_id", "").startswith("<SIM_"),
                  f"{eid} has SIM synthetic_agent_card_id")
            # Each entry has at least one source-specific SIM ID
            source_ids = [v for k, v in e.items() if k.startswith("synthetic_") and k.endswith("_id") and v]
            has_source = any(sid.startswith("<SIM_") for sid in source_ids)
            check(has_source, f"{eid} has at least one SIM source ID")
            check(e.get("retrieved_agent_card_summary", ""),
                  f"{eid} has retrieved_agent_card_summary")
            # Expected signals
            expected_signals = e.get("expected_signal", [])
            check(len(expected_signals) >= 2,
                  f"{eid} has >= 2 expected signals ({len(expected_signals)})")
            # Security fields
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
        check(meta.get("module_id") == "M44", "Playbook module_id == M44")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Playbook assessment_mode == adversarial_validation")
        check(meta.get("synthetic_only") is True, "Playbook synthetic_only == true")
        check(meta.get("fake_runtime_only") is True, "Playbook fake_runtime_only == true")
        check(meta.get("real_a2a_endpoint_allowed") is False,
              "Playbook real_a2a_endpoint_allowed == false")
        check(meta.get("real_agent_credential_allowed") is False,
              "Playbook real_agent_credential_allowed == false")
        check(meta.get("real_inter_agent_execution_allowed") is False,
              "Playbook real_inter_agent_execution_allowed == false")
        check(meta.get("real_agent_discovery_allowed") is False,
              "Playbook real_agent_discovery_allowed == false")
        check(meta.get("real_agent_card_loaded") is False,
              "Playbook real_agent_card_loaded == false")
        check(meta.get("real_identity_verification_allowed") is False,
              "Playbook real_identity_verification_allowed == false")
        check(meta.get("real_delegation_context_allowed") is False,
              "Playbook real_delegation_context_allowed == false")
        check(meta.get("real_capability_registry_allowed") is False,
              "Playbook real_capability_registry_allowed == false")
        check(meta.get("real_tool_call_allowed") is False,
              "Playbook real_tool_call_allowed == false")
        check(meta.get("real_api_call_allowed") is False,
              "Playbook real_api_call_allowed == false")

        # Attacker profile fields
        check(meta.get("attacker_type") == "external_user",
              "Playbook attacker_type == external_user")
        check("supply_chain_agent_identity_spoofing" in meta.get("attack_objective", ""),
              "Playbook attack_objective contains supply_chain_agent_identity_spoofing")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run Config")
    config_path = ROOT / "run_configs/phase73a_m44_a2a_agent_identity_trust_boundary_run_config.yaml"
    config = yaml_load(config_path)
    check(config is not None, "Run config loaded")
    if config:
        rc = config.get("run_config", {})
        check(rc.get("module_id") == "M44", "Config module_id == M44")
        check(rc.get("assessment_mode") == "adversarial_validation",
              "Config assessment_mode == adversarial_validation")
        check(rc.get("fake_runtime_only") is True, "Config fake_runtime_only == true")
        check(rc.get("synthetic_only") is True, "Config synthetic_only == true")
        check(rc.get("real_a2a_endpoint_allowed") is False,
              "Config real_a2a_endpoint_allowed == false")
        check(rc.get("real_agent_credential_allowed") is False,
              "Config real_agent_credential_allowed == false")
        check(rc.get("real_inter_agent_execution_allowed") is False,
              "Config real_inter_agent_execution_allowed == false")
        check(rc.get("real_tool_call_allowed") is False,
              "Config real_tool_call_allowed == false")
        check(rc.get("real_api_call_allowed") is False,
              "Config real_api_call_allowed == false")
        check_security_fields(rc, "M44", "config")

    # ================================================================
    # 3. Execution results
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/phase73a_m44_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 12,
              f"execution_results has >= 12 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("entry_id", "MISSING")
            check(r.get("real_a2a_endpoint_accessed") is False,
                  f"{rid} real_a2a_endpoint_accessed == false")
            check(r.get("real_agent_card_loaded") is False,
                  f"{rid} real_agent_card_loaded == false")
            check(r.get("real_identity_verification_performed") is False,
                  f"{rid} real_identity_verification_performed == false")
            check(r.get("real_delegation_context_accessed") is False,
                  f"{rid} real_delegation_context_accessed == false")
            check(r.get("real_capability_registry_accessed") is False,
                  f"{rid} real_capability_registry_accessed == false")
            check(r.get("real_agent_credential_read") is False,
                  f"{rid} real_agent_credential_read == false")
            check(r.get("real_inter_agent_task_executed") is False,
                  f"{rid} real_inter_agent_task_executed == false")
            check(r.get("real_tool_call_executed") is False,
                  f"{rid} real_tool_call_executed == false")
            check(r.get("real_api_call_executed") is False,
                  f"{rid} real_api_call_executed == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

            # Check entry has core M44 signal fields
            check("agent_identity_unverified" in r,
                  f"{rid} has agent_identity_unverified field")
            check("self_declared_identity_rejected" in r,
                  f"{rid} has self_declared_identity_rejected field")
            check("authorization_required" in r,
                  f"{rid} has authorization_required field")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase73a_m44_mvp/m44_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "m44_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "M44", "result module_id == M44")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 12,
              f"result total_cases >= 12 ({result_yaml.get('total_cases')})")

        expected_counts = [
            "agent_identity_unverified_count",
            "self_declared_identity_rejected_count",
            "capability_claim_not_trusted_count",
            "delegation_blocked_count",
            "authorization_required_count",
            "synthetic_identity_validation_required_count",
            "agent_identity_verified_count",
            "authorization_granted_count",
            "benign_request_allowed_count",
            "human_review_required_count",
            "breakthrough_detected_count",
            "control_case_passed_count",
            "control_case_failed_count",
            "inconclusive_count",
        ]
        for ec in expected_counts:
            check(ec in result_yaml, f"result has {ec}")

        check_security_fields(result_yaml, "M44", "result YAML")
        for rfield in ["real_a2a_endpoint_accessed", "real_agent_card_loaded",
                        "real_identity_verification_performed",
                        "real_delegation_context_accessed",
                        "real_capability_registry_accessed",
                        "real_agent_credential_read",
                        "real_inter_agent_task_executed",
                        "real_tool_call_executed", "real_api_call_executed"]:
            check(result_yaml.get(rfield) is False,
                  f"result {rfield} == false")

        # Per-entry fields in result
        entries = result_yaml.get("per_entry_results", [])
        check(len(entries) >= 12, f"result has >= 12 per-entry results ({len(entries)})")
        for entry in entries:
            eid = entry.get("entry_id", "?")
            check(entry.get("confirmed_vulnerability") is False,
                  f"result/{eid}: confirmed_vulnerability == false")
            check(entry.get("formal_finding_allowed") is False,
                  f"result/{eid}: formal_finding_allowed == false")
            check(entry.get("breakthrough_detected") is False,
                  f"result/{eid}: breakthrough_detected == false")
            check("agent_identity_unverified" in entry,
                  f"result/{eid}: has agent_identity_unverified")
            check("self_declared_identity_rejected" in entry,
                  f"result/{eid}: has self_declared_identity_rejected")
            check("human_review_required" in entry or "requires_human_review" in entry,
                  f"result/{eid}: has human_review signal")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/phase73a_m44_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "M44", "scorecard module_id == M44")
        check(sm.get("assessment_mode") == "adversarial_validation",
              "scorecard assessment_mode == adversarial_validation")
        check(sm.get("simulated_signal_only") is True,
              "scorecard simulated_signal_only == true")
        check_security_fields(sm, "M44", "scorecard metadata")
        check(sm.get("safety_level") == "simulated_runtime_safety",
              "scorecard safety_level == simulated_runtime_safety")
        check(sm.get("production_safety") == "out_of_scope",
              "scorecard production_safety == out_of_scope")
        check(sm.get("synthetic_only") is True, "scorecard synthetic_only == true")
        check(sm.get("fake_runtime_only") is True,
              "scorecard fake_runtime_only == true")

        # Capability value and risk level separation
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

        # Result summary signals
        expected_rs = [
            "agent_identity_unverified",
            "self_declared_identity_rejected",
            "capability_claim_not_trusted",
            "delegation_blocked",
            "authorization_required",
            "benign_request_allowed",
            "human_review_required",
            "breakthrough_detected",
        ]
        for ers in expected_rs:
            check(ers in rs, f"scorecard results_summary has {ers}")

        # Category coverage
        cc = scorecard.get("category_coverage", [])
        attack_categories = [c for c in cc if c not in ("valid_agent_identity_verified", "benign_agent_discovery")]
        check(len(attack_categories) >= 10,
              f"scorecard has >= 10 attack categories ({len(attack_categories)})")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase73a_m44_a2a_agent_identity_trust_boundary_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实 A2A endpoint" in notes_text or "no real A2A endpoint" in notes_text.lower(),
              "Notes state no real A2A endpoint access")
        check("不读取真实 Agent 凭据" in notes_text or "no real agent credential" in notes_text.lower(),
              "Notes state no real agent credential read")
        check("不执行真实 inter-agent 任务" in notes_text or "no real inter-agent" in notes_text.lower(),
              "Notes state no real inter-agent task execution")
        check("不加载真实 Agent 身份卡片" in notes_text or "no real agent card" in notes_text.lower(),
              "Notes state no real agent card loaded")
        check("不执行真实身份验证" in notes_text or "no real identity verification" in notes_text.lower(),
              "Notes state no real identity verification")
        check("不读取真实委托上下文" in notes_text or "no real delegation context" in notes_text.lower(),
              "Notes state no real delegation context access")
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
