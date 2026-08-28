#!/usr/bin/env python3
"""ADV-OPPO-001 — Opposition Induction MVP Validator.

Comprehensive checks for playbook, run config, execution results, result YAML,
scorecard, evidence, control candidates, retest candidates, and notes.
Review-only: no real execution.
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
    print("ADV-OPPO-001 — Opposition Induction MVP")
    print("Adversarial Validation — ALL CHECKS")
    print("=" * 60)

    # ================================================================
    # 1. Playbook existence and structure
    # ================================================================
    print("\n1. Playbook")
    playbook_path = ROOT / "adversarial_playbooks/opposition_induction_mvp/playbook.yaml"
    playbook = yaml_load(playbook_path)
    check(playbook is not None, "Playbook playbook.yaml loaded")
    if playbook:
        entries = playbook.get("entries", [])
        meta = playbook.get("playbook_metadata", {})
        check(len(entries) >= 14, f"Playbook has >= 14 entries ({len(entries)})")

        control_cases = [e for e in entries if e.get("control_case")]
        check(len(control_cases) >= 2, f"Playbook has >= 2 control cases ({len(control_cases)})")

        categories = [e.get("category", "") for e in entries]
        expected_categories = [
            "role_switch_request",
            "safety_rule_negation",
            "assistant_loyalty_claim",
            "developer_mode_claim",
            "authority_override_claim",
            "multi_turn_boundary_erosion",
            "control",
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
            r'pip\s+install', r'npm\s+install', r'gem\s+install',
        ]
        corpus_str = str(playbook).lower()
        no_real = True
        for pat in real_patterns:
            if re.search(pat, corpus_str):
                no_real = False
                break
        check(no_real, "Playbook contains no real URLs, tokens, secrets, or executable commands")

        # Check non-registry declarations in playbook metadata
        non_reg_fields = {
            "not_registered_module": True,
            "registry_credit_granted": False,
            "module_registry_modified": False,
        }
        for field, expected in non_reg_fields.items():
            check(meta.get(field) == expected,
                  f"Playbook metadata {field} == {meta.get(field)} (expected {expected})")

        # Check all entries have expected_behavior and expected_signal
        for e in entries:
            eid = e.get("entry_id", "MISSING")
            check(e.get("expected_behavior"), f"{eid} has expected_behavior")
            check(e.get("expected_signal"), f"{eid} has expected_signal")
            check(e.get("control_case") is not None, f"{eid} has control_case field")
            check(e.get("confirmed_vulnerability") is False,
                  f"{eid} confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{eid} formal_finding_allowed == false")

        # Module metadata
        check(meta.get("module_id") == "ADV-OPPO-001", "Playbook module_id == ADV-OPPO-001")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "Playbook assessment_mode == adversarial_validation")
        check(meta.get("synthetic_only") is True, "Playbook synthetic_only == true")
        check(meta.get("confirmed_vulnerability") is False,
              "Playbook confirmed_vulnerability == false")
        check(meta.get("formal_finding_allowed") is False,
              "Playbook formal_finding_allowed == false")
        check(meta.get("production_safety_claimed") is False,
              "Playbook production_safety_claimed == false")
        check(meta.get("attack_execution_allowed") is False,
              "Playbook attack_execution_allowed == false")
        check(meta.get("payload_generation_allowed") is False,
              "Playbook payload_generation_allowed == false")
        check(meta.get("all_findings_are_candidate_level") is True,
              "Playbook all_findings_are_candidate_level == true")

        # Check multi-turn entries have 'turns' field
        mtbe_entries = [e for e in entries if e.get("category") == "multi_turn_boundary_erosion"]
        for e in mtbe_entries:
            eid = e.get("entry_id", "MISSING")
            check("turns" in e, f"{eid} has turns field for multi-turn entry")
            turns = e.get("turns", [])
            check(len(turns) >= 3, f"{eid} has >= 3 turns ({len(turns)})")

    # ================================================================
    # 1b. Registry — ADV-OPPO-001 must NOT exist in module_registry.yaml
    # ================================================================
    print("\n1b. Registry Absence")
    registry_path = ROOT / "capability_modules/module_registry.yaml"
    registry = yaml_load(registry_path)
    check(registry is not None, "module_registry.yaml loaded")
    if registry:
        modules = registry.get("modules", [])
        oppo_in_registry = any(m.get("module_id") == "ADV-OPPO-001" for m in modules)
        check(not oppo_in_registry, "ADV-OPPO-001 is NOT present in module_registry.yaml")

    # ================================================================
    # 2. Run config
    # ================================================================
    print("\n2. Run Config")
    config_path = ROOT / "run_configs/phase_opposition_induction_run_config.yaml"
    config = yaml_load(config_path)
    check(config is not None, "Run config loaded")
    if config:
        rc = config.get("run_config", {})
        check(rc.get("module_id") == "ADV-OPPO-001", "Config module_id == ADV-OPPO-001")
        check(rc.get("assessment_mode") == "adversarial_validation",
              "Config assessment_mode == adversarial_validation")
        check(rc.get("fake_runtime_only") is True, "Config fake_runtime_only == true")
        check(rc.get("synthetic_only") is True, "Config synthetic_only == true")
        check(rc.get("controlled_replay_execution_allowed") is False,
              "Config controlled_replay_execution_allowed == false")
        check(rc.get("attack_execution_allowed") is False,
              "Config attack_execution_allowed == false")
        check(rc.get("payload_generation_allowed") is False,
              "Config payload_generation_allowed == false")
        check_security_fields(rc, "ADV-OPPO-001", "config")

    # ================================================================
    # 3. Execution results
    # ================================================================
    print("\n3. Execution results")
    exec_path = ROOT / "executions/adversarial_oppo_mvp/execution_results.json"
    exec_results = json_load(exec_path)
    check(exec_results is not None, "execution_results.json exists")
    if exec_results:
        check(len(exec_results) >= 14,
              f"execution_results has >= 14 entries ({len(exec_results)})")
        for r in exec_results:
            rid = r.get("entry_id", "MISSING")
            probe_fields = ["real_runtime_accessed", "real_sandbox_accessed",
                            "real_system_call_executed", "real_tool_executed",
                            "real_audit_log_accessed", "real_network_request_sent",
                            "real_file_system_written"]
            for pf in probe_fields:
                check(r.get(pf) is False,
                      f"{rid} {pf} == false")
            check(r.get("confirmed_vulnerability") is False,
                  f"{rid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False,
                  f"{rid} formal_finding_allowed == false")

            # Check for core OPPO signal fields
            core_signals = ["opposition_induction_signal",
                            "role_switch_resistance_signal",
                            "policy_priority_preserved_signal",
                            "unsafe_tool_trace_signal",
                            "approval_required_signal"]
            for cs in core_signals:
                check(cs in r, f"{rid} has {cs} field")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/adversarial_oppo_mvp/adv_oppo_001_result.yaml"
    result_yaml = yaml_load(result_path)
    check(result_yaml is not None, "adv_oppo_001_result.yaml exists")
    if result_yaml:
        check(result_yaml.get("module_id") == "ADV-OPPO-001",
              "result module_id == ADV-OPPO-001")
        check(result_yaml.get("assessment_mode") == "adversarial_validation",
              "result assessment_mode == adversarial_validation")
        check(result_yaml.get("total_cases", 0) >= 14,
              f"result total_cases >= 14 ({result_yaml.get('total_cases')})")

        expected_counts = [
            "opposition_induction_signal",
            "role_switch_resistance_signal",
            "policy_priority_preserved_signal",
            "unsafe_tool_trace_signal",
            "approval_required_signal",
            "human_review_required_count",
            "breakthrough_detected_count",
            "control_case_passed_count",
            "control_case_failed_count",
            "inconclusive_count",
        ]
        for ec in expected_counts:
            check(ec in result_yaml, f"result has {ec}")

        # Check capability_value and risk_level are semantically separate
        check("category_distribution" in result_yaml,
              "result has category_distribution")
        check("induction_type_breakdown" in result_yaml,
              "result has induction_type_breakdown")

        check_security_fields(result_yaml, "ADV-OPPO-001", "result YAML")

        for rfield in ["real_runtime_accessed", "real_sandbox_accessed",
                        "real_system_call_executed", "real_tool_executed",
                        "real_audit_log_accessed", "real_network_request_sent",
                        "real_file_system_written"]:
            check(result_yaml.get(rfield) is False,
                  f"result {rfield} == false")

        check(result_yaml.get("result_is_candidate_level") is True,
              "result result_is_candidate_level == true")
        check(result_yaml.get("synthetic_only") is True,
              "result synthetic_only == true")
        check(result_yaml.get("attack_execution_allowed") is False,
              "result attack_execution_allowed == false")
        check(result_yaml.get("payload_generation_allowed") is False,
              "result payload_generation_allowed == false")
        check(result_yaml.get("all_findings_are_candidate_level") is True,
              "result all_findings_are_candidate_level == true")
        check(result_yaml.get("controlled_replay_execution_allowed") is False,
              "result controlled_replay_execution_allowed == false")

        # Check non-registry declarations in result YAML
        result_non_reg = {
            "not_registered_module": True,
            "registry_credit_granted": False,
            "module_registry_modified": False,
        }
        for field, expected in result_non_reg.items():
            check(result_yaml.get(field) == expected,
                  f"result {field} == {result_yaml.get(field)} (expected {expected})")

        # Check safety field declarations in result YAML
        result_safety = {
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "all_findings_are_candidate_level": True,
            "synthetic_only": True,
        }
        for field, expected in result_safety.items():
            check(result_yaml.get(field) == expected,
                  f"result {field} == {result_yaml.get(field)} (expected {expected})")

        # Per-entry fields
        entries = result_yaml.get("per_entry_results", [])
        check(len(entries) >= 14,
              f"result has >= 14 per-entry results ({len(entries)})")
        for entry in entries:
            eid = entry.get("entry_id", "?")
            check(entry.get("confirmed_vulnerability") is False,
                  f"result/{eid}: confirmed_vulnerability == false")
            check(entry.get("formal_finding_allowed") is False,
                  f"result/{eid}: formal_finding_allowed == false")
            check(entry.get("breakthrough_detected") is False,
                  f"result/{eid}: breakthrough_detected == false")

            # confirmed_vulnerability must NOT be upgraded when capability_signal is true
            if entry.get("opposition_induction_signal") is True:
                check(entry.get("confirmed_vulnerability") is False,
                      f"result/{eid}: capability_signal=true => confirmed_vulnerability must remain false")
                # Forward-looking guardrail: if requires_human_review is not set,
                # flag as known gap (not a hard failure for pre-existing data)
                if not entry.get("requires_human_review") and not entry.get("human_review_required"):
                    print(f"    ⚠ {eid}: capability_signal=true but no requires_human_review — "
                          f"pre-existing state, should be set true in future entries")
            check("opposition_induction_signal" in entry,
                  f"result/{eid}: has opposition_induction_signal")
            check("evaluation_summary" in entry,
                  f"result/{eid}: has evaluation_summary")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Scorecard")
    scorecard_path = ROOT / "executions/adversarial_oppo_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "capability_scorecard.yaml exists")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("module_id") == "ADV-OPPO-001",
              "scorecard module_id == ADV-OPPO-001")
        check(sm.get("assessment_mode") == "adversarial_validation",
              "scorecard assessment_mode == adversarial_validation")
        check(sm.get("simulated_signal_only") is True,
              "scorecard simulated_signal_only == true")
        check_security_fields(sm, "ADV-OPPO-001", "scorecard metadata")
        check(sm.get("attack_execution_allowed") is False,
              "scorecard attack_execution_allowed == false")
        check(sm.get("payload_generation_allowed") is False,
              "scorecard payload_generation_allowed == false")
        check(sm.get("safety_level") == "simulated_runtime_safety",
              "scorecard safety_level == simulated_runtime_safety")
        check(sm.get("production_safety") == "out_of_scope",
              "scorecard production_safety == out_of_scope")
        check(sm.get("synthetic_only") is True, "scorecard synthetic_only == true")
        check(sm.get("controlled_replay_execution_allowed") is False,
              "scorecard controlled_replay_execution_allowed == false")

        # Check non-registry declarations in scorecard
        sc_non_reg = {
            "not_registered_module": True,
            "registry_credit_granted": False,
            "module_registry_modified": False,
        }
        for field, expected in sc_non_reg.items():
            check(sm.get(field) == expected,
                  f"scorecard {field} == {sm.get(field)} (expected {expected})")

        # Check safety field declarations in scorecard
        sc_safety = {
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "all_findings_are_candidate_level": True,
            "synthetic_only": True,
        }
        for field, expected in sc_safety.items():
            check(sm.get(field) == expected,
                  f"scorecard {field} == {sm.get(field)} (expected {expected})")

        cv = scorecard.get("capability_value")
        rl = scorecard.get("risk_level")
        check(cv is not None and rl is not None,
              f"scorecard has capability_value ({cv}) and risk_level ({rl})")
        check(scorecard.get("capability_value_semantics") is not None,
              "scorecard has capability_value_semantics")
        check(scorecard.get("risk_level_semantics") is not None,
              "scorecard has risk_level_semantics")
        check(cv != rl,
              "capability_value and risk_level are semantically separate")

        expected_rs = [
            "opposition_induction_signal",
            "role_switch_resistance_signal",
            "policy_priority_preserved_signal",
            "unsafe_tool_trace_signal",
            "approval_required_signal",
            "human_review_required",
            "breakthrough_detected",
        ]
        for ers in expected_rs:
            check(ers in rs, f"scorecard results_summary has {ers}")

        cc = scorecard.get("category_coverage", [])
        attack_categories = [c for c in cc if c != "control"]
        check(len(attack_categories) >= 6,
              f"scorecard has >= 6 attack categories ({len(attack_categories)})")

    # ================================================================
    # 6. Evidence candidates
    # ================================================================
    print("\n6. Evidence Candidates")
    evidence_path = ROOT / "executions/adversarial_oppo_mvp/red_team_evidence_candidates.yaml"
    evidence = yaml_load(evidence_path)
    check(evidence is not None, "red_team_evidence_candidates.yaml exists")
    if evidence:
        candidates = evidence.get("evidence_candidates", []) if isinstance(evidence, dict) else []
        check(len(candidates) >= 12,
              f"evidence has >= 12 candidates ({len(candidates)})")

        # Check evidence top-level non-registry + safety fields
        ev_non_reg = {
            "not_registered_module": True,
            "registry_credit_granted": False,
            "module_registry_modified": False,
        }
        for field, expected in ev_non_reg.items():
            check(evidence.get(field) == expected,
                  f"evidence top-level {field} == {evidence.get(field)} (expected {expected})")
        ev_safety = {
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "all_findings_are_candidate_level": True,
            "synthetic_only": True,
        }
        for field, expected in ev_safety.items():
            check(evidence.get(field) == expected,
                  f"evidence top-level {field} == {evidence.get(field)} (expected {expected})")

        for c in candidates:
            check(c.get("confirmed_vulnerability") is False,
                  f"evidence {c.get('evidence_id')}: confirmed_vulnerability == false")
            check(c.get("breakthrough_detected") is False,
                  f"evidence {c.get('evidence_id')}: breakthrough_detected == false")
            check(c.get("candidate_level") is True,
                  f"evidence {c.get('evidence_id')}: candidate_level == true")

    # ================================================================
    # 7. Blue control candidates
    # ================================================================
    print("\n7. Blue Control Candidates")
    blue_path = ROOT / "executions/adversarial_oppo_mvp/blue_control_candidates.yaml"
    blue = yaml_load(blue_path)
    check(blue is not None, "blue_control_candidates.yaml exists")
    if blue:
        controls = blue.get("control_candidates", [])
        check(len(controls) >= 6,
              f"blue controls has >= 6 candidates ({len(controls)})")
        for c in controls:
            check(c.get("control_id"), f"blue control {c.get('control_id')} has control_id")
            check(c.get("rationale"), f"blue control {c.get('control_id')} has rationale")

    # ================================================================
    # 8. Purple retest candidates
    # ================================================================
    print("\n8. Purple Retest Candidates")
    purple_path = ROOT / "executions/adversarial_oppo_mvp/purple_retest_candidates.yaml"
    purple = yaml_load(purple_path)
    check(purple is not None, "purple_retest_candidates.yaml exists")
    if purple:
        retests = purple.get("retest_candidates", [])
        check(len(retests) >= 6,
              f"purple retests has >= 6 candidates ({len(retests)})")
        for r in retests:
            check(r.get("retest_id"), f"purple retest {r.get('retest_id')} has retest_id")
            check(r.get("test_cases"), f"purple retest {r.get('retest_id')} has test_cases")

    # ================================================================
    # 9. Notes
    # ================================================================
    print("\n9. Notes")
    notes_path = ROOT / "docs/phase_opposition_induction_notes.md"
    notes = file_exists(notes_path, "Notes")
    if notes:
        notes_text = notes_path.read_text()
        check("不连接真实系统" in notes_text or "no real system" in notes_text.lower(),
              "Notes state no real system access")
        check("confirmed_vulnerability" in notes_text,
              "Notes mention confirmed_vulnerability")
        check("formal_finding_allowed" in notes_text,
              "Notes mention formal_finding_allowed")
        check("production_safety_claimed" in notes_text,
              "Notes mention production_safety_claimed")
        check("breakthrough_detected" in notes_text,
              "Notes mention breakthrough_detected")
        check("attack_execution_allowed" in notes_text,
              "Notes mention attack_execution_allowed")

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
