#!/usr/bin/env python3
"""
validate_phase97a_paths.py — Phase-97A-PATHS-002 Independent Validator Script.
Path: scripts/validate_phase97a_paths.py

Performs comprehensive validation for:
1. Deliverable files existence & integrity
2. Scenario Playbook YAML schema & 8-path coverage (PATH-001 to PATH-008)
3. CrossModuleInjectionEngine class initialization & safety boundary invariants
4. Step-by-step injection execution across all 8 paths
5. Simulated candidate breakthrough evaluation & exploit_chain_candidate generation
6. Standardized evidence_trace structure & synthetic placeholder compliance
"""

import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

checks_passed = 0
checks_failed = 0
errors = []


def check(condition: bool, msg: str) -> None:
    global checks_passed, checks_failed, errors
    if condition:
        checks_passed += 1
        print(f"  ✓ {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  ✗ {msg}")


def main() -> int:
    global checks_passed, checks_failed, errors
    print("=" * 70)
    print("Phase 97A Task 2 (Phase-97A-PATHS-002) — Cross-Module Paths & Injection Engine Validator")
    print("=" * 70)

    # ========================================================================
    # 1. Deliverables Files Existence
    # ========================================================================
    print("\n1. Deliverable Files Existence & Structure")
    expected_files = [
        ROOT / "playbooks" / "cross_module" / "path_001_to_008_scenarios.yaml",
        ROOT / "engine" / "cross_module_injection_engine.py",
        ROOT / "engine" / "__init__.py",
        ROOT / "tests" / "test_cross_module_injection_engine.py",
        ROOT / "scripts" / "validate_phase97a_paths.py",
        ROOT / "docs" / "phase97a_cross_module_playbook_catalog.md",
        ROOT / "phase97a_paths002_execution_summary.yaml",
        ROOT / "delivery.json",
    ]

    for ef in expected_files:
        check(ef.exists(), f"File exists: {ef.relative_to(ROOT)}")

    # ========================================================================
    # 2. Playbook YAML Validation (PATH-001 to PATH-008)
    # ========================================================================
    print("\n2. Playbook YAML Validation (PATH-001 to PATH-008)")
    playbook_file = ROOT / "playbooks" / "cross_module" / "path_001_to_008_scenarios.yaml"
    with open(playbook_file, "r", encoding="utf-8") as f:
        pb_data = yaml.safe_load(f)

    check(pb_data is not None, "Playbook YAML successfully parsed")
    meta = pb_data.get("catalog_metadata", {})
    check(meta.get("total_paths") == 8, f"Catalog metadata total_paths == 8 ({meta.get('total_paths')})")
    check(meta.get("evaluation_mode") == "adversarial_validation", "Catalog evaluation_mode == adversarial_validation")
    check(meta.get("default_attacker_type") == "compromised_user", "Default attacker_type == compromised_user")

    scenarios = pb_data.get("scenarios", [])
    check(len(scenarios) == 8, f"Playbook contains exactly 8 scenario paths ({len(scenarios)})")

    expected_path_ids = [
        "PATH-001", "PATH-002", "PATH-003", "PATH-004",
        "PATH-005", "PATH-006", "PATH-007", "PATH-008"
    ]

    actual_ids = [sc.get("path_id") for sc in scenarios]
    check(actual_ids == expected_path_ids, f"Path IDs match sequence PATH-001..PATH-008 ({actual_ids})")

    total_steps_in_yaml = 0
    for sc in scenarios:
        pid = sc.get("path_id", "UNKNOWN")
        steps = sc.get("steps", [])
        total_steps_in_yaml += len(steps)
        check(len(steps) >= 3, f"Path {pid} has >= 3 steps ({len(steps)} steps)")
        check("involved_modules" in sc and len(sc["involved_modules"]) >= 3, f"Path {pid} has >= 3 involved_modules")
        check("involved_layers" in sc and len(sc["involved_layers"]) >= 2, f"Path {pid} has >= 2 involved_layers")
        check("overall_breakthrough_evaluation" in sc, f"Path {pid} has overall_breakthrough_evaluation")

        for idx, step in enumerate(steps, start=1):
            check("boundary_crossed" in step, f"Path {pid} step {idx} defines boundary_crossed")
            check("simulated_event" in step, f"Path {pid} step {idx} defines simulated_event")
            check("expected_defense" in step, f"Path {pid} step {idx} defines expected_defense")
            check("target_evidence_fields" in step.get("expected_defense", {}), f"Path {pid} step {idx} defines target_evidence_fields")

    check(total_steps_in_yaml >= 30, f"Total steps across all 8 paths >= 30 ({total_steps_in_yaml})")

    # ========================================================================
    # 3. CrossModuleInjectionEngine Class & Invariants
    # ========================================================================
    print("\n3. CrossModuleInjectionEngine API & Safety Boundaries")
    from engine.cross_module_injection_engine import (
        CrossModuleInjectionEngine,
        INJECTION_ENGINE_SAFETY_BOUNDARIES,
    )

    engine = CrossModuleInjectionEngine(playbook_path=playbook_file)
    check(engine is not None, "CrossModuleInjectionEngine instantiated")
    check(len(engine.get_available_paths()) == 8, f"Engine loaded 8 paths ({len(engine.get_available_paths())})")

    # Safety boundary verification
    sb = engine.safety_boundaries
    check(sb.get("confirmed_vulnerability") is False, "Safety boundary: confirmed_vulnerability == false")
    check(sb.get("formal_finding_allowed") is False, "Safety boundary: formal_finding_allowed == false")
    check(sb.get("production_safety_claimed") is False, "Safety boundary: production_safety_claimed == false")
    check(sb.get("synthetic_only") is True, "Safety boundary: synthetic_only == true")
    check(sb.get("requires_human_review") is True, "Safety boundary: requires_human_review == true")
    check(sb.get("all_findings_are_candidate") is True, "Safety boundary: all_findings_are_candidate == true")
    check(sb.get("red_team_engine_not_executable") is True, "Safety boundary: red_team_engine_not_executable == true")

    # ========================================================================
    # 4. End-to-End Simulation of All 8 Paths (Contained Baseline)
    # ========================================================================
    print("\n4. End-to-End Execution Across All 8 Paths (Baseline Contained Mode)")
    batch_summary = engine.execute_all_paths()
    check(batch_summary["total_paths"] == 8, "Batch execution ran 8 paths")
    check(batch_summary["total_steps_executed"] == total_steps_in_yaml, f"Executed all {total_steps_in_yaml} steps")
    check(batch_summary["total_evidence_traces_generated"] == total_steps_in_yaml, f"Generated {total_steps_in_yaml} evidence traces")

    for pid in expected_path_ids:
        path_res = batch_summary["path_results"].get(pid, {})
        check(path_res.get("status") == "completed", f"Path {pid} execution completed successfully")
        check("exploit_chain_candidate" in path_res, f"Path {pid} generated exploit_chain_candidate")
        check("evidence_traces" in path_res, f"Path {pid} generated evidence_traces")
        traces = path_res.get("evidence_traces", [])
        for tr in traces:
            check(tr.get("synthetic_only") is True, f"Path {pid} trace {tr.get('trace_id')} synthetic_only == true")
            check(tr.get("trace_id", "").startswith("<SIM_TRACE_"), f"Path {pid} trace_id uses <SIM_TRACE_...>")

    # ========================================================================
    # 5. Adversarial Injection & Breakthrough Detection Verification
    # ========================================================================
    print("\n5. Adversarial Injection & Candidate Breakthrough Detection")
    # Simulate multi-step failure on PATH-001 (Full Lifecycle)
    p1_failures = [
        {"defense_held": False, "evidence_fields": {"descriptor_poisoning_detected": False, "fake_tool_invocation_blocked": False}},
        {"defense_held": False, "evidence_fields": {"instruction_boundary_decision": False, "code_review_bypass_blocked": False}},
        {"defense_held": False, "evidence_fields": {"rag_poisoning_detected": False, "safe_summary_generated": False}},
        {"defense_held": False, "evidence_fields": {"permission_boundary_preserved": False, "restricted_retrieval_blocked": False}},
        {"defense_held": False, "evidence_fields": {"sandbox_boundary_preserved": False, "audit_chain_consistent": False}},
    ]
    p1_adv_report = engine.execute_path("PATH-001", simulated_defense_outcomes=p1_failures)
    check(p1_adv_report["breakthrough_detected"] is True, "PATH-001 adversarial injection triggered breakthrough_detected == true")
    check(p1_adv_report["severity_tier"] == "candidate_critical", f"PATH-001 adversarial severity == candidate_critical ({p1_adv_report['severity_tier']})")

    candidate = p1_adv_report.get("exploit_chain_candidate", {})
    check(candidate.get("breakthrough_detected") is True, "Exploit chain candidate records breakthrough_detected == true")
    check(len(candidate.get("candidate_findings", [])) > 0, "Candidate findings list populated")
    f0 = candidate["candidate_findings"][0]
    check(f0.get("finding_status") == "candidate", "Finding status == candidate")
    check(f0.get("confirmed_vulnerability") is False, "Finding confirmed_vulnerability == false")
    check(f0.get("formal_finding_allowed") is False, "Finding formal_finding_allowed == false")
    check(f0.get("synthetic_only") is True, "Finding synthetic_only == true")

    # ========================================================================
    # 6. Safety Invariants & Execution Summary
    # ========================================================================
    print("\n6. Execution Summary File & Safety Metadata Integrity")
    summary_file = ROOT / "phase97a_paths002_execution_summary.yaml"
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            sum_data = yaml.safe_load(f)
        check(sum_data.get("task_id") == "Phase-97A-PATHS-002", "Summary task_id == Phase-97A-PATHS-002")
        check(sum_data.get("evaluation_mode") == "adversarial_validation", "Summary evaluation_mode == adversarial_validation")
        sb_sum = sum_data.get("safety_boundaries", {})
        check(sb_sum.get("confirmed_vulnerability") is False, "Summary safety: confirmed_vulnerability == false")
        check(sb_sum.get("formal_finding_allowed") is False, "Summary safety: formal_finding_allowed == false")
        check(sb_sum.get("production_safety_claimed") is False, "Summary safety: production_safety_claimed == false")
        check(sb_sum.get("synthetic_only") is True, "Summary safety: synthetic_only == true")
        check(sb_sum.get("all_findings_are_candidate") is True, "Summary safety: all_findings_are_candidate == true")
    else:
        check(False, "phase97a_paths002_execution_summary.yaml exists")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 70)
    if checks_failed == 0:
        print("Phase-97A-PATHS-002 Cross-Module Paths Validation: ALL CHECKS PASSED (100%)")
    else:
        print(f"Phase-97A-PATHS-002 Cross-Module Paths Validation: FAILED ({checks_failed} errors)")
    print(f"  checks_passed: {checks_passed}")
    print(f"  checks_failed: {checks_failed}")
    if errors:
        print("\nErrors encountered:")
        for e in errors:
            print(f"  - {e}")
    print("=" * 70)

    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
