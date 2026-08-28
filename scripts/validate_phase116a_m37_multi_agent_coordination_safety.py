#!/usr/bin/env python3
"""Phase 116A — M37 Multi-Agent Simulation & Coordination Safety MVP Validator.

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
        check(False, f"YAML load: {path} -- {e}")
        return None


def json_load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load: {path} -- {e}")
        return None


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 116A -- M37 Multi-Agent Simulation & Coordination Safety MVP Validation")
    print("=" * 60)

    # ================================================================
    # 1. Corpus
    # ================================================================
    print("\n1. Corpus")
    corpus_path = ROOT / "adversarial_playbooks/m37_multi_agent_coordination_safety_mvp/playbook.yaml"
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
        required_categories = [
            "agent_communication_injection",
            "collaboration_chain_attack",
            "agent_identity_spoofing",
            "task_assignment_deception",
            "shared_state_pollution",
            "inter_agent_privilege_escalation",
            "coordination_protocol_bypass",
            "multi_agent_resource_contention",
        ]
        for cat in required_categories:
            check(cat in categories, f"Corpus includes {cat}")

        # Check all entries have SIM placeholders
        for entry in entries:
            eid = entry.get("entry_id", "?")
            check("<SIM_" in json.dumps(entry),
                  f"Entry {eid} uses <SIM_...> synthetic placeholders")

        # Check security fields on all entries
        for entry in entries:
            eid = entry.get("entry_id", "?")
            check(entry.get("confirmed_vulnerability") is False,
                  f"Entry {eid} confirmed_vulnerability=false")
            check(entry.get("formal_finding_allowed") is False,
                  f"Entry {eid} formal_finding_allowed=false")
            check(entry.get("production_safety_claimed") is False,
                  f"Entry {eid} production_safety_claimed=false")

        # Check metadata
        check(meta.get("module_id") == "M37", "playbook_metadata module_id=M37")
        check(meta.get("assessment_mode") == "adversarial_validation",
              "playbook_metadata assessment_mode=adversarial_validation")
        check(meta.get("confirmed_vulnerability") is False,
              "playbook_metadata confirmed_vulnerability=false")
        check(meta.get("formal_finding_allowed") is False,
              "playbook_metadata formal_finding_allowed=false")
        check(meta.get("production_safety_claimed") is False,
              "playbook_metadata production_safety_claimed=false")
        check(meta.get("total_entries") == 10, "playbook_metadata total_entries=10")

    # ================================================================
    # 2. Run Config
    # ================================================================
    print("\n2. Run Config")
    run_config_path = ROOT / "run_configs/phase116a_m37_multi_agent_coordination_safety_run_config.yaml"
    run_config_file = file_exists(run_config_path, "Run config")
    run_config = yaml_load(run_config_path) if run_config_file else None
    if run_config:
        rc = run_config.get("run_config", {})
        check(rc.get("phase") == "phase116a", "run_config.phase=phase116a")
        check(rc.get("module_id") == "M37", "run_config.module_id=M37")
        check(rc.get("assessment_mode") == "adversarial_validation",
              "run_config.assessment_mode=adversarial_validation")
        check(rc.get("confirmed_vulnerability") is False,
              "run_config.confirmed_vulnerability=false")
        check(rc.get("formal_finding_allowed") is False,
              "run_config.formal_finding_allowed=false")
        check(rc.get("production_safety_claimed") is False,
              "run_config.production_safety_claimed=false")
        check(rc.get("real_agent_communication_bus_allowed") is False,
              "run_config.real_agent_communication_bus_allowed=false")
        check(rc.get("real_orchestration_engine_allowed") is False,
              "run_config.real_orchestration_engine_allowed=false")
        check(rc.get("real_identity_auth_service_allowed") is False,
              "run_config.real_identity_auth_service_allowed=false")
        check(rc.get("real_task_assignment_system_allowed") is False,
              "run_config.real_task_assignment_system_allowed=false")

    # ================================================================
    # 3. Execution Results
    # ================================================================
    print("\n3. Execution Results")
    er_path = ROOT / "executions/phase116a_m37_mvp/execution_results.json"
    er_file = file_exists(er_path, "execution_results.json")
    er_data = json_load(er_path) if er_file else None
    if er_data:
        check(isinstance(er_data, list), "execution_results is a list")
        check(len(er_data) == 10, f"execution_results has 10 entries ({len(er_data)})")

        attack_results = [r for r in er_data if not r.get("control_case")]
        control_results = [r for r in er_data if r.get("control_case")]
        check(len(attack_results) == 8, f"execution_results has 8 attack cases ({len(attack_results)})")
        check(len(control_results) == 2, f"execution_results has 2 control cases ({len(control_results)})")

        for result in er_data:
            cid = result.get("case_id", "?")
            check(result.get("breakthrough_detected") is False,
                  f"Case {cid} breakthrough_detected=false")
            check(result.get("confirmed_vulnerability") is False,
                  f"Case {cid} confirmed_vulnerability=false")
            check(result.get("formal_finding_allowed") is False,
                  f"Case {cid} formal_finding_allowed=false")
            check(result.get("defensive_check_passed") is True,
                  f"Case {cid} defensive_check_passed=true")
            check(result.get("evidence_trace"), f"Case {cid} has evidence_trace")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase116a_m37_mvp/m37_result.yaml"
    result_file = file_exists(result_path, "m37_result.yaml")
    result_data = yaml_load(result_path) if result_file else None
    if result_data:
        check(result_data.get("phase") == "116A", "result.phase=116A")
        check(result_data.get("module_id") == "M37", "result.module_id=M37")
        check(result_data.get("total_cases") == 10, "result.total_cases=10")
        check(result_data.get("attack_cases") == 8, "result.attack_cases=8")
        check(result_data.get("control_cases") == 2, "result.control_cases=2")
        check(result_data.get("breakthrough_detected_count") == 0,
              "result.breakthrough_detected_count=0")
        check(result_data.get("confirmed_vulnerability") is False,
              "result.confirmed_vulnerability=false")
        check(result_data.get("formal_finding_allowed") is False,
              "result.formal_finding_allowed=false")
        check(result_data.get("production_safety_claimed") is False,
              "result.production_safety_claimed=false")
        check(result_data.get("capability_value") == "high",
              "result.capability_value=high")
        check(result_data.get("risk_level") == "low",
              "result.risk_level=low")

    # ================================================================
    # 5. Capability Scorecard
    # ================================================================
    print("\n5. Capability Scorecard")
    sc_path = ROOT / "executions/phase116a_m37_mvp/capability_scorecard.yaml"
    sc_file = file_exists(sc_path, "capability_scorecard.yaml")
    sc_data = yaml_load(sc_path) if sc_file else None
    if sc_data:
        meta_sc = sc_data.get("scorecard_metadata", {})
        check(meta_sc.get("module_id") == "M37", "scorecard.module_id=M37")
        check(meta_sc.get("total_entries") == 10, "scorecard.total_entries=10")
        check(meta_sc.get("confirmed_vulnerability") is False,
              "scorecard.confirmed_vulnerability=false")
        check(meta_sc.get("formal_finding_allowed") is False,
              "scorecard.formal_finding_allowed=false")
        check(meta_sc.get("production_safety_claimed") is False,
              "scorecard.production_safety_claimed=false")
        check(meta_sc.get("result_is_candidate_level") is True,
              "scorecard.result_is_candidate_level=true")

        results_summary = sc_data.get("results_summary", {})
        check(results_summary.get("total") == 10, "scorecard.results_summary.total=10")
        check(results_summary.get("attack_cases") == 8,
              "scorecard.results_summary.attack_cases=8")
        check(results_summary.get("control_cases") == 2,
              "scorecard.results_summary.control_cases=2")
        check(results_summary.get("breakthrough_detected") == 0,
              "scorecard.results_summary.breakthrough_detected=0")
        check(results_summary.get("control_passed") == 2,
              "scorecard.results_summary.control_passed=2")
        check(results_summary.get("control_failed") == 0,
              "scorecard.results_summary.control_failed=0")
        check(results_summary.get("inconclusive") == 0,
              "scorecard.results_summary.inconclusive=0")
        check(sc_data.get("category_coverage") and len(sc_data.get("category_coverage", [])) == 10,
              "scorecard has 10 category_coverage entries")

    # ================================================================
    # 6. Notes
    # ================================================================
    print("\n6. Notes")
    notes_path = ROOT / "docs/phase116a_m37_multi_agent_coordination_safety_notes.md"
    notes_file = file_exists(notes_path, "notes file")
    if notes_file:
        notes_content = notes_path.read_text()
        check("M37" in notes_content, "Notes mentions M37")
        check("Multi-Agent" in notes_content or "multi-agent" in notes_content,
              "Notes mentions Multi-Agent")
        check("confirmed_vulnerability: false" in notes_content or
              "confirmed_vulnerability=false" in notes_content,
              "Notes has confirmed_vulnerability=false")
        check("formal_finding_allowed: false" in notes_content or
              "formal_finding_allowed=false" in notes_content,
              "Notes has formal_finding_allowed=false")
        check("production_safety_claimed: false" in notes_content or
              "production_safety_claimed=false" in notes_content,
              "Notes has production_safety_claimed=false")

    # ================================================================
    # 7. Registry
    # ================================================================
    print("\n7. Module Registry")
    registry_path = ROOT / "capability_modules/module_registry.yaml"
    registry_file = file_exists(registry_path, "module_registry.yaml")
    registry = yaml_load(registry_path) if registry_file else None
    if registry:
        modules = registry.get("modules", [])
        m37 = None
        for m in modules:
            if m.get("module_id") == "M37":
                m37 = m
                break
        check(m37 is not None, "M37 entry found in module_registry.yaml")
        if m37:
            check(m37.get("coverage", {}).get("coverage_status") == "mvp_complete",
                  "M37 coverage_status=mvp_complete")
            check(m37.get("coverage", {}).get("implementation_status") == "mvp_complete",
                  "M37 implementation_status=mvp_complete")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    total = checks_passed + checks_failed
    print(f"Total checks: {total} | Passed: {checks_passed} | Failed: {checks_failed}")
    if checks_failed == 0:
        print("ALL CHECKS PASSED")
    else:
        print("FAILURES:")
        for e in errors:
            print(f"  - {e}")
    print("=" * 60)
    return 1 if checks_failed else 0


if __name__ == "__main__":
    sys.exit(main())
