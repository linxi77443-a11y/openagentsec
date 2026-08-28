#!/usr/bin/env python3
"""
Phase 116A — M37 Multi-Agent Simulation & Coordination Safety Full Corpus Validator
Validates playbook structure, execution results, and generates summary statistics.
"""

import json
import sys
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
PLAYBOOK_PATH = BASE_DIR / "adversarial_playbooks" / "m37_full_corpus" / "playbook.yaml"
EXECUTION_RESULTS_PATH = BASE_DIR / "executions" / "phase116a_m37_full_corpus" / "execution_results.json"
RESULT_YAML_PATH = BASE_DIR / "executions" / "phase116a_m37_full_corpus" / "m37_full_corpus_result.yaml"
SCORECARD_PATH = BASE_DIR / "executions" / "phase116a_m37_full_corpus" / "capability_scorecard.yaml"


def validate_playbook():
    """Validate playbook.yaml structure and content."""
    import yaml
    with open(PLAYBOOK_PATH) as f:
        data = yaml.safe_load(f)

    errors = []
    warnings = []

    # Metadata checks
    meta = data.get("playbook_metadata", {})
    if meta.get("total_entries") != 50:
        errors.append(f"total_entries is {meta.get('total_entries')}, expected 50")
    if meta.get("fake_runtime_only") is not True:
        errors.append("fake_runtime_only must be true")
    if meta.get("synthetic_only") is not True:
        errors.append("synthetic_only must be true")
    if meta.get("confirmed_vulnerability") is not False:
        errors.append("confirmed_vulnerability must be false")
    if meta.get("formal_finding_allowed") is not False:
        errors.append("formal_finding_allowed must be false")
    if meta.get("production_safety_claimed") is not False:
        errors.append("production_safety_claimed must be false")
    if meta.get("real_agent_communication_bus_allowed") is not False:
        errors.append("real_agent_communication_bus_allowed must be false")
    if meta.get("real_orchestration_engine_allowed") is not False:
        errors.append("real_orchestration_engine_allowed must be false")
    if meta.get("real_identity_auth_service_allowed") is not False:
        errors.append("real_identity_auth_service_allowed must be false")
    if meta.get("real_task_assignment_system_allowed") is not False:
        errors.append("real_task_assignment_system_allowed must be false")

    entries = data.get("entries", [])
    if len(entries) != 50:
        errors.append(f"Entry count is {len(entries)}, expected 50")

    # Category counts
    categories = {}
    control_count = 0
    attack_count = 0
    for entry in entries:
        cat = entry.get("category", "")
        is_control = entry.get("control_case", False)
        if is_control:
            control_count += 1
        else:
            attack_count += 1
        categories.setdefault(cat, {"attack": 0, "control": 0})
        if is_control:
            categories[cat]["control"] += 1
        else:
            categories[cat]["attack"] += 1

    # Validate category distribution
    comm_entries = sum(1 for e in entries if e.get("category", "").startswith("agent_communication"))
    chain_entries = sum(1 for e in entries if e.get("category", "").startswith("collaboration_chain"))
    sec_entries = sum(1 for e in entries if e.get("category", "").startswith("multi_agent"))
    ctrl_entries = sum(1 for e in entries if e.get("control_case", False))

    if comm_entries < 15:
        errors.append(f"Agent communication entries: {comm_entries}, expected >= 15")
    if chain_entries < 15:
        errors.append(f"Collaboration chain entries: {chain_entries}, expected >= 15")
    if sec_entries < 10:
        errors.append(f"Multi-agent security entries: {sec_entries}, expected >= 10")
    if ctrl_entries < 10:
        errors.append(f"Control entries: {ctrl_entries}, expected >= 10")

    # Entry-level checks
    seen_ids = set()
    for i, entry in enumerate(entries):
        eid = entry.get("entry_id", "")
        if not eid:
            errors.append(f"Entry {i}: missing entry_id")
        elif eid in seen_ids:
            errors.append(f"Entry {i}: duplicate entry_id {eid}")
        seen_ids.add(eid)

        if not entry.get("scenario"):
            errors.append(f"Entry {eid}: missing scenario")
        if not entry.get("user_query"):
            errors.append(f"Entry {eid}: missing user_query")
        if not entry.get("expected_behavior"):
            errors.append(f"Entry {eid}: missing expected_behavior")
        if not entry.get("expected_signal"):
            errors.append(f"Entry {eid}: missing expected_signal")
        if entry.get("breakthrough_detected") is not False:
            errors.append(f"Entry {eid}: breakthrough_detected must be false")
        if entry.get("confirmed_vulnerability") is not False:
            errors.append(f"Entry {eid}: confirmed_vulnerability must be false")
        if entry.get("formal_finding_allowed") is not False:
            errors.append(f"Entry {eid}: formal_finding_allowed must be false")
        if entry.get("production_safety_claimed") is not False:
            errors.append(f"Entry {eid}: production_safety_claimed must be false")

        # Check for SIM_ placeholders
        user_query = entry.get("user_query", "")
        if "<SIM_" not in user_query and not entry.get("control_case"):
            warnings.append(f"Entry {eid}: user_query may not use SIM_ placeholders")

    return errors, warnings, {
        "total": len(entries),
        "attack": attack_count,
        "control": control_count,
        "categories": categories,
        "comm_entries": comm_entries,
        "chain_entries": chain_entries,
        "sec_entries": sec_entries,
        "ctrl_entries": ctrl_entries,
    }


def validate_execution_results():
    """Validate execution_results.json."""
    with open(EXECUTION_RESULTS_PATH) as f:
        results = json.load(f)

    errors = []
    warnings = []

    if len(results) != 50:
        errors.append(f"Execution results count: {len(results)}, expected 50")

    attack_results = [r for r in results if not r.get("control_case")]
    control_results = [r for r in results if r.get("control_case")]

    if len(attack_results) != 40:
        errors.append(f"Attack results: {len(attack_results)}, expected 40")
    if len(control_results) != 10:
        errors.append(f"Control results: {len(control_results)}, expected 10")

    for r in results:
        case_id = r.get("case_id", "")
        if r.get("execution_status") != "completed":
            errors.append(f"Case {case_id}: status is {r.get('execution_status')}, expected completed")
        if r.get("breakthrough_detected") is not False:
            errors.append(f"Case {case_id}: breakthrough_detected must be false")
        if r.get("confirmed_vulnerability") is not False:
            errors.append(f"Case {case_id}: confirmed_vulnerability must be false")
        if r.get("formal_finding_allowed") is not False:
            errors.append(f"Case {case_id}: formal_finding_allowed must be false")
        if r.get("production_safety_claimed") is not False:
            errors.append(f"Case {case_id}: production_safety_claimed must be false")
        if r.get("real_agent_communication_bus_accessed") is not False:
            errors.append(f"Case {case_id}: real_agent_communication_bus_accessed must be false")
        if r.get("real_orchestration_engine_accessed") is not False:
            errors.append(f"Case {case_id}: real_orchestration_engine_accessed must be false")
        if r.get("real_identity_auth_service_accessed") is not False:
            errors.append(f"Case {case_id}: real_identity_auth_service_accessed must be false")
        if r.get("real_task_assignment_system_accessed") is not False:
            errors.append(f"Case {case_id}: real_task_assignment_system_accessed must be false")

    return errors, warnings, {
        "total": len(results),
        "attack": len(attack_results),
        "control": len(control_results),
    }


def validate_result_yaml():
    """Validate m37_full_corpus_result.yaml."""
    import yaml
    with open(RESULT_YAML_PATH) as f:
        data = yaml.safe_load(f)

    errors = []
    warnings = []

    if data.get("total_entries") != 50:
        errors.append(f"total_entries is {data.get('total_entries')}, expected 50")
    if data.get("attack_entries") != 40:
        errors.append(f"attack_entries is {data.get('attack_entries')}, expected 40")
    if data.get("control_entries") != 10:
        errors.append(f"control_entries is {data.get('control_entries')}, expected 10")
    if data.get("breakthrough_detected_count") != 0:
        errors.append(f"breakthrough_detected_count is {data.get('breakthrough_detected_count')}, expected 0")
    if data.get("confirmed_vulnerability") is not False:
        errors.append("confirmed_vulnerability must be false")
    if data.get("formal_finding_allowed") is not False:
        errors.append("formal_finding_allowed must be false")
    if data.get("production_safety_claimed") is not False:
        errors.append("production_safety_claimed must be false")

    # Category breakdown validation
    cb = data.get("category_breakdown", {})
    expected_cats = ["agent_communication", "collaboration_chain", "multi_agent_security", "control_cases"]
    for cat in expected_cats:
        if cat not in cb:
            errors.append(f"Missing category in breakdown: {cat}")

    return errors, warnings


def validate_scorecard():
    """Validate capability_scorecard.yaml."""
    import yaml
    with open(SCORECARD_PATH) as f:
        data = yaml.safe_load(f)

    errors = []
    warnings = []

    meta = data.get("scorecard_metadata", {})
    if meta.get("total_entries") != 50:
        errors.append(f"total_entries is {meta.get('total_entries')}, expected 50")
    if meta.get("confirmed_vulnerability") is not False:
        errors.append("confirmed_vulnerability must be false")
    if meta.get("formal_finding_allowed") is not False:
        errors.append("formal_finding_allowed must be false")
    if meta.get("production_safety_claimed") is not False:
        errors.append("production_safety_claimed must be false")

    caps = data.get("category_capabilities", {})
    expected_caps = ["agent_communication", "collaboration_chain", "multi_agent_security", "control_cases"]
    for cat in expected_caps:
        if cat not in caps:
            errors.append(f"Missing capability for: {cat}")
        elif caps[cat].get("coverage") != "100%":
            errors.append(f"Category {cat} coverage is {caps[cat].get('coverage')}, expected 100%")

    return errors, warnings


def main():
    print("=" * 70)
    print("M37 Full Corpus Validation Report")
    print("=" * 70)

    all_errors = []
    all_warnings = []

    # 1. Playbook validation
    print("\n[1/4] Validating playbook.yaml...")
    try:
        pb_errors, pb_warnings, pb_stats = validate_playbook()
        all_errors.extend(pb_errors)
        all_warnings.extend(pb_warnings)
        print(f"  Entries: {pb_stats['total']} (attack: {pb_stats['attack']}, control: {pb_stats['control']})")
        print(f"  Agent Communication: {pb_stats['comm_entries']} entries")
        print(f"  Collaboration Chain: {pb_stats['chain_entries']} entries")
        print(f"  Multi-Agent Security: {pb_stats['sec_entries']} entries")
        print(f"  Control Cases: {pb_stats['ctrl_entries']} entries")
        print(f"  Categories: {list(pb_stats['categories'].keys())}")
        if pb_errors:
            for e in pb_errors:
                print(f"  ERROR: {e}")
        else:
            print("  PASS")
    except Exception as ex:
        print(f"  FAILED: {ex}")
        all_errors.append(f"Playbook validation failed: {ex}")

    # 2. Execution results validation
    print("\n[2/4] Validating execution_results.json...")
    try:
        er_errors, er_warnings, er_stats = validate_execution_results()
        all_errors.extend(er_errors)
        all_warnings.extend(er_warnings)
        print(f"  Results: {er_stats['total']} (attack: {er_stats['attack']}, control: {er_stats['control']})")
        if er_errors:
            for e in er_errors:
                print(f"  ERROR: {e}")
        else:
            print("  PASS")
    except Exception as ex:
        print(f"  FAILED: {ex}")
        all_errors.append(f"Execution results validation failed: {ex}")

    # 3. Result YAML validation
    print("\n[3/4] Validating m37_full_corpus_result.yaml...")
    try:
        ry_errors, ry_warnings = validate_result_yaml()
        all_errors.extend(ry_errors)
        all_warnings.extend(ry_warnings)
        if ry_errors:
            for e in ry_errors:
                print(f"  ERROR: {e}")
        else:
            print("  PASS")
    except Exception as ex:
        print(f"  FAILED: {ex}")
        all_errors.append(f"Result YAML validation failed: {ex}")

    # 4. Scorecard validation
    print("\n[4/4] Validating capability_scorecard.yaml...")
    try:
        sc_errors, sc_warnings = validate_scorecard()
        all_errors.extend(sc_errors)
        all_warnings.extend(sc_warnings)
        if sc_errors:
            for e in sc_errors:
                print(f"  ERROR: {e}")
        else:
            print("  PASS")
    except Exception as ex:
        print(f"  FAILED: {ex}")
        all_errors.append(f"Scorecard validation failed: {ex}")

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"  Total checks: 4")
    print(f"  Errors: {len(all_errors)}")
    print(f"  Warnings: {len(all_warnings)}")

    if all_errors:
        print("\n  ERRORS:")
        for e in all_errors:
            print(f"    - {e}")

    if all_warnings:
        print("\n  WARNINGS:")
        for w in all_warnings:
            print(f"    - {w}")

    if not all_errors:
        print("\n  RESULT: ALL CHECKS PASSED")
        print("  M37 Full Corpus validation successful.")
        print("  - 50 entries (40 attack + 10 control)")
        print("  - 15 agent communication scenarios")
        print("  - 15 collaboration chain attack scenarios")
        print("  - 10 multi-agent security scenarios")
        print("  - 10 control cases")
        print("  - All synthetic, no real system access")
        print("  - No breakthroughs detected")
        print("  - confirmed_vulnerability=false, formal_finding_allowed=false")
        return 0
    else:
        print("\n  RESULT: VALIDATION FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
