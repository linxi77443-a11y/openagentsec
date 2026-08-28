#!/usr/bin/env python3
"""
validate_phase97a_gate_suite.py — Phase-97A-GATE-003 Integration Gate Validator Script.
Path: scripts/validate_phase97a_gate_suite.py

Comprehensive independent validation for:
1. Deliverable files existence and integrity.
2. PropagationDynamicsEngine + CrossModuleInjectionEngine dual-engine coupling.
3. Strict safety boundary invariants across both engines.
4. 8-path scenario catalog coverage (PATH-001 to PATH-008, 32 steps).
5. End-to-end joint execution under baseline contained conditions.
6. Markov 5-state distribution row-sum = 1.0 strict convergence.
7. Dynamic edge propagation pressure (P_edge) and node defense state evolution (D_node).
8. Attenuation and amplification mechanics across 4 security layers & 7 edge types.
9. Adversarial injection & candidate breakthrough detection matrix.
10. Checkpoint snapshot (artifacts/batch_checkpoints/phase97a_checkpoint.json) integrity.
11. Results summary and delivery manifest compliance.
"""

import sys
import json
import math
import yaml
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

checks_passed = 0
checks_failed = 0
errors: List[str] = []


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
    print("=" * 75)
    print("Phase 97A Task 3 (Phase-97A-GATE-003) — Integration Gate & Joint Simulation Validator")
    print("=" * 75)

    # ========================================================================
    # 1. Deliverables Files Existence & Structure
    # ========================================================================
    print("\n[Step 1] Validating Deliverable Files Existence & Structure...")
    expected_files = [
        ROOT / "scripts" / "validate_phase97a_gate_suite.py",
        ROOT / "tests" / "test_phase97a_integration_suite.py",
        ROOT / "docs" / "phase97a_dynamic_propagation_and_cross_module_integration_design.md",
        ROOT / "reports" / "phase97a_integration_suite_validation_report.md",
        ROOT / "artifacts" / "batch_checkpoints" / "phase97a_checkpoint.json",
        ROOT / "phase97a_gate003_execution_summary.yaml",
        ROOT / "delivery.json",
        ROOT / "engine" / "propagation_dynamics_engine.py",
        ROOT / "engine" / "cross_module_injection_engine.py",
        ROOT / "playbooks" / "cross_module" / "path_001_to_008_scenarios.yaml",
    ]

    for ef in expected_files:
        check(ef.exists(), f"File exists: {ef.relative_to(ROOT)}")

    # ========================================================================
    # 2. Dual-Engine Instantiation & Safety Invariants
    # ========================================================================
    print("\n[Step 2] Validating Dual-Engine Instantiation & Safety Boundary Invariants...")
    from engine.propagation_dynamics_engine import (
        PropagationDynamicsEngine,
        MARKOV_STATES,
        SECURITY_LAYERS,
        EDGE_TYPES,
        ATTENUATION_RULES,
        BLOCKING_RULES,
    )
    from engine.cross_module_injection_engine import (
        CrossModuleInjectionEngine,
        INJECTION_ENGINE_SAFETY_BOUNDARIES,
    )

    prop_engine = PropagationDynamicsEngine()
    check(prop_engine is not None, "PropagationDynamicsEngine instantiated successfully")

    inj_engine = CrossModuleInjectionEngine(propagation_engine=prop_engine)
    check(inj_engine is not None, "CrossModuleInjectionEngine instantiated with PropagationEngine")
    check(inj_engine.propagation_engine is prop_engine, "PropagationEngine reference bound to InjectionEngine")

    # Safety boundary checks
    sb_inj = inj_engine.safety_boundaries
    check(sb_inj.get("confirmed_vulnerability") is False, "Safety invariant: confirmed_vulnerability == false")
    check(sb_inj.get("formal_finding_allowed") is False, "Safety invariant: formal_finding_allowed == false")
    check(sb_inj.get("production_safety_claimed") is False, "Safety invariant: production_safety_claimed == false")
    check(sb_inj.get("synthetic_only") is True, "Safety invariant: synthetic_only == true")
    check(sb_inj.get("requires_human_review") is True, "Safety invariant: requires_human_review == true")
    check(sb_inj.get("all_findings_are_candidate") is True, "Safety invariant: all_findings_are_candidate == true")
    check(sb_inj.get("red_team_engine_not_executable") is True, "Safety invariant: red_team_engine_not_executable == true")

    sb_prop = prop_engine.get_safety_boundaries()
    check(sb_prop.get("propagation_equation_is_not_exploit_chain") is True, "Safety invariant: propagation_equation_is_not_exploit_chain == true")
    check(sb_prop.get("theory_model_is_not_detection_rule") is True, "Safety invariant: theory_model_is_not_detection_rule == true")

    # ========================================================================
    # 3. 8-Path Scenario Catalog Coverage
    # ========================================================================
    print("\n[Step 3] Validating 8-Path Multi-Layer Scenario Catalog Coverage...")
    paths = inj_engine.get_available_paths()
    check(len(paths) == 8, f"Playbook catalog contains 8 paths ({len(paths)})")

    expected_pids = [
        "PATH-001", "PATH-002", "PATH-003", "PATH-004",
        "PATH-005", "PATH-006", "PATH-007", "PATH-008"
    ]
    check(paths == expected_pids, f"Path IDs match sequence PATH-001..PATH-008 ({paths})")

    total_catalog_steps = 0
    for pid in expected_pids:
        sc = inj_engine.get_scenario(pid)
        check(sc is not None, f"Scenario {pid} loaded successfully")
        steps = sc.get("steps", [])
        total_catalog_steps += len(steps)
        check(len(steps) >= 3, f"Scenario {pid} has >= 3 steps ({len(steps)})")
        check(len(sc.get("involved_modules", [])) >= 3, f"Scenario {pid} covers >= 3 modules")
        check(len(sc.get("involved_layers", [])) >= 2, f"Scenario {pid} covers >= 2 layers")

    check(total_catalog_steps == 32, f"Total catalog steps across all 8 paths == 32 ({total_catalog_steps})")

    # ========================================================================
    # 4. End-to-End Joint Simulation (Baseline Contained Mode)
    # ========================================================================
    print("\n[Step 4] Executing End-to-End Joint Simulation (Baseline Contained Mode)...")
    batch_summary = inj_engine.execute_all_paths()

    check(batch_summary.get("total_paths") == 8, "Batch executed 8 paths")
    check(batch_summary.get("total_steps_executed") == 32, "Executed exactly 32 steps")
    check(batch_summary.get("total_evidence_traces_generated") == 32, "Generated 32 evidence traces")
    check(batch_summary.get("breakthrough_paths_count") == 0, "Contained baseline has 0 breakthrough paths")
    check(batch_summary.get("contained_paths_count") == 8, "Contained baseline has 8 contained paths")

    for pid in expected_pids:
        res = batch_summary["path_results"].get(pid, {})
        check(res.get("status") == "completed", f"Path {pid} status == completed")
        check(res.get("breakthrough_detected") is False, f"Path {pid} breakthrough_detected == false")
        check(res.get("severity_tier") == "candidate_contained", f"Path {pid} severity_tier == candidate_contained")
        check(res.get("path_degradation_g_path", 0.0) < 0.0, f"Path {pid} G_path < 0.0 ({res.get('path_degradation_g_path')})")
        check(res.get("trajectory_classification") == "stable_or_pressured", f"Path {pid} trajectory == stable_or_pressured")

    # ========================================================================
    # 5. Markov 5-State Distribution Convergence Verification
    # ========================================================================
    print("\n[Step 5] Validating Markov 5-State Distribution Convergence (Row Sum = 1.0)...")
    markov_step_check_count = 0
    for pid, res in batch_summary["path_results"].items():
        for tr in res.get("evidence_traces", []):
            dist = tr.get("markov_distribution", {})
            check(len(dist) == 5, f"Path {pid} step {tr['step_number']} Markov dist has 5 states")
            row_sum = sum(dist.values())
            check(math.isclose(row_sum, 1.0, rel_tol=1e-6, abs_tol=1e-6), f"Path {pid} step {tr['step_number']} Markov row sum == 1.0 ({row_sum:.6f})")
            markov_step_check_count += 1

        for mod_id, dist in res.get("node_final_markov_distributions", {}).items():
            row_sum = sum(dist.values())
            check(math.isclose(row_sum, 1.0, rel_tol=1e-6, abs_tol=1e-6), f"Path {pid} node {mod_id} final Markov row sum == 1.0 ({row_sum:.6f})")

    check(markov_step_check_count == 32, f"Verified Markov convergence across all 32 steps ({markov_step_check_count})")

    # ========================================================================
    # 6. Edge Propagation Pressure & Node Defense Evolution Math
    # ========================================================================
    print("\n[Step 6] Validating Edge Pressure (P_edge) & Node Defense Evolution (D_node) Math...")
    # Verify P_edge bounding & edge weights
    for etype, edata in prop_engine.get_supported_edge_types().items():
        p_val = prop_engine.calculate_p_edge(source_signal=0.75, edge_type=etype, target_defense=0.50)
        check(0.0 <= p_val <= 1.0, f"P_edge for {etype} bounded in [0, 1] ({p_val:.4f})")

    # Verify P_edge boundary conditions
    check(prop_engine.calculate_p_edge(source_signal=0.0, edge_type="context_influence", target_defense=0.5) == 0.0, "P_edge == 0.0 when source signal == 0.0")
    check(prop_engine.calculate_p_edge(source_signal=1.0, edge_type="context_influence", target_defense=1.0) == 0.0, "P_edge == 0.0 when target defense == 1.0")

    # Verify D_node evolution
    d_next = prop_engine.step_node_defense(current_defense=0.80, incoming_pressure=0.30, node_vulnerability=0.60, control_recovery=0.05, human_review=0.05)
    expected_d = round(0.80 + 0.05 - (0.30 * 0.60) + 0.05, 4)  # 0.80 + 0.05 - 0.18 + 0.05 = 0.72
    check(math.isclose(d_next, expected_d, rel_tol=1e-4), f"D_node evolution matches theoretical formula ({d_next:.4f} == {expected_d:.4f})")

    # ========================================================================
    # 7. Attenuation & Amplification Mechanics Verification
    # ========================================================================
    print("\n[Step 7] Validating Attenuation & Amplification Dynamics...")
    atten_sum = prop_engine.compute_attenuation(active_rules=["ATTEN-HRG-001", "ATTEN-BND-001", "ATTEN-RED-001"])
    check(math.isclose(atten_sum, 0.90), f"Attenuation rules sum matches theoretical weight ({atten_sum:.2f})")

    check(prop_engine.compute_sequential_amplification(0) == 0.00, "Sequential amplification (0 weak boundaries) == 0.00")
    check(prop_engine.compute_sequential_amplification(2) == 0.25, "Sequential amplification (2 weak boundaries) == 0.25")
    check(prop_engine.compute_sequential_amplification(3) == 0.50, "Sequential amplification (3 weak boundaries) == 0.50")

    cross_ampl = prop_engine.compute_cross_layer_amplification("supply_chain", "runtime_sandbox")
    check(math.isclose(cross_ampl, 0.60), f"Cross-layer crossing amplification L1->L4 == 0.60 ({cross_ampl:.2f})")

    # ========================================================================
    # 8. Adversarial Injection & Breakthrough Detection Matrix
    # ========================================================================
    print("\n[Step 8] Validating Adversarial Injection & Candidate Breakthrough Detection Matrix...")
    adv_scenarios = [
        ("PATH-001", [
            {"defense_held": False, "evidence_fields": {"descriptor_poisoning_detected": False, "fake_tool_invocation_blocked": False}},
            {"defense_held": False, "evidence_fields": {"instruction_boundary_decision": False, "code_review_bypass_blocked": False}},
            {"defense_held": False, "evidence_fields": {"rag_poisoning_detected": False, "safe_summary_generated": False}},
            {"defense_held": False, "evidence_fields": {"permission_boundary_preserved": False, "restricted_retrieval_blocked": False}},
            {"defense_held": False, "evidence_fields": {"sandbox_boundary_preserved": False, "audit_chain_consistent": False}},
        ], "candidate_critical"),
        ("PATH-003", [
            {"defense_held": False, "evidence_fields": {"rag_poisoning_detected": False, "safe_summary_generated": False}},
            {"defense_held": False, "evidence_fields": {"permission_boundary_preserved": False, "restricted_retrieval_blocked": False}},
            {"defense_held": True, "evidence_fields": {"sandbox_boundary_preserved": True}},
        ], "candidate_high"),
        ("PATH-005", [
            {"defense_held": False, "evidence_fields": {"agent_input_filtering_enforced": False}},
            {"defense_held": False, "evidence_fields": {"mcp_descriptor_tampering_detected": False}},
            {"defense_held": False, "evidence_fields": {"a2a_identity_spoofing_blocked": False}},
            {"defense_held": True, "evidence_fields": {"sandbox_boundary_preserved": True}},
        ], "candidate_high"),
        ("PATH-007", [
            {"defense_held": False, "evidence_fields": {"cross_session_leakage_prevented": False}},
            {"defense_held": False, "evidence_fields": {"datasource_trust_verification_passed": False}},
            {"defense_held": False, "evidence_fields": {"role_boundary_enforced": False}},
            {"defense_held": False, "evidence_fields": {"service_account_abuse_blocked": False}},
        ], "candidate_critical"),
    ]

    for pid, simulated_outcomes, expected_tier in adv_scenarios:
        adv_report = inj_engine.execute_path(pid, simulated_defense_outcomes=simulated_outcomes)
        check(adv_report.get("breakthrough_detected") is True, f"Adversarial {pid} triggered breakthrough_detected == true")
        check(adv_report.get("severity_tier") == expected_tier, f"Adversarial {pid} severity_tier == {expected_tier} ({adv_report.get('severity_tier')})")
        check(adv_report.get("path_degradation_g_path", 0.0) >= 0.0, f"Adversarial {pid} G_path indicates degradation ({adv_report.get('path_degradation_g_path')})")

        candidate = adv_report.get("exploit_chain_candidate", {})
        check(candidate.get("breakthrough_detected") is True, f"Candidate {pid} records breakthrough == true")
        findings = candidate.get("candidate_findings", [])
        check(len(findings) > 0, f"Candidate {pid} findings populated ({len(findings)})")
        f0 = findings[0]
        check(f0.get("finding_status") == "candidate", f"Candidate {pid} finding status == candidate")
        check(f0.get("confirmed_vulnerability") is False, f"Candidate {pid} finding confirmed_vulnerability == false")
        check(f0.get("formal_finding_allowed") is False, f"Candidate {pid} finding formal_finding_allowed == false")
        check(f0.get("synthetic_only") is True, f"Candidate {pid} finding synthetic_only == true")
        check(f0.get("requires_human_review") is True, f"Candidate {pid} finding requires_human_review == true")

    # ========================================================================
    # 9. Phase Checkpoint Snapshot Verification
    # ========================================================================
    print("\n[Step 9] Validating Checkpoint Snapshot (artifacts/batch_checkpoints/phase97a_checkpoint.json)...")
    cp_file = ROOT / "artifacts" / "batch_checkpoints" / "phase97a_checkpoint.json"
    check(cp_file.exists(), "Checkpoint snapshot file exists")

    with open(cp_file, "r", encoding="utf-8") as f:
        cp_data = json.load(f)

    check(cp_data.get("checkpoint_version") == "1.0", "Checkpoint version == 1.0")
    check(cp_data.get("phase") == "Phase-97A", "Checkpoint phase == Phase-97A")
    check(cp_data.get("task_id") == "Phase-97A-GATE-003", "Checkpoint task_id == Phase-97A-GATE-003")
    check(cp_data.get("status") == "completed", "Checkpoint status == completed")
    check(cp_data.get("total_scenarios") == 8, "Checkpoint total_scenarios == 8")
    check(cp_data.get("total_steps_executed") == 32, "Checkpoint total_steps_executed == 32")
    check(cp_data.get("total_evidence_traces") == 32, "Checkpoint total_evidence_traces == 32")

    cp_sb = cp_data.get("safety_boundaries", {})
    check(cp_sb.get("confirmed_vulnerability") is False, "Checkpoint safety: confirmed_vulnerability == false")
    check(cp_sb.get("formal_finding_allowed") is False, "Checkpoint safety: formal_finding_allowed == false")
    check(cp_sb.get("production_safety_claimed") is False, "Checkpoint safety: production_safety_claimed == false")
    check(cp_sb.get("synthetic_only") is True, "Checkpoint safety: synthetic_only == true")
    check(cp_sb.get("dashboard_not_execution_interface") is True, "Checkpoint safety: dashboard_not_execution_interface == true")
    check(cp_sb.get("red_team_engine_not_executable") is True, "Checkpoint safety: red_team_engine_not_executable == true")

    cp_paths = cp_data.get("paths", {})
    check(len(cp_paths) == 8, f"Checkpoint contains 8 paths ({len(cp_paths)})")
    for pid in expected_pids:
        check(pid in cp_paths, f"Checkpoint contains {pid}")
        p_entry = cp_paths[pid]
        check(p_entry.get("status") == "completed", f"Checkpoint {pid} status == completed")
        check(len(p_entry.get("steps", [])) >= 3, f"Checkpoint {pid} contains steps")

    cp_adv = cp_data.get("adversarial_stress_scenarios", {})
    check(len(cp_adv) >= 4, f"Checkpoint contains >= 4 adversarial stress scenarios ({len(cp_adv)})")

    # ========================================================================
    # 10. Results Summary & Delivery Manifest Compliance
    # ========================================================================
    print("\n[Step 10] Validating Execution Summary & Delivery Manifest Compliance...")
    summary_file = ROOT / "phase97a_gate003_execution_summary.yaml"
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            sum_data = yaml.safe_load(f)
        check(sum_data.get("task_id") == "Phase-97A-GATE-003", "Summary task_id == Phase-97A-GATE-003")
        check(sum_data.get("evaluation_mode") == "defensive_evaluation", "Summary evaluation_mode == defensive_evaluation")
        check(sum_data.get("safety_boundaries", {}).get("confirmed_vulnerability") is False, "Summary safety confirmed_vulnerability == false")
        check(sum_data.get("safety_boundaries", {}).get("synthetic_only") is True, "Summary safety synthetic_only == true")
    else:
        check(False, "phase97a_gate003_execution_summary.yaml exists")

    delivery_file = ROOT / "delivery.json"
    if delivery_file.exists():
        with open(delivery_file, "r", encoding="utf-8") as f:
            deliv_data = json.load(f)
        check("workplan_id" in deliv_data, "Delivery manifest contains workplan_id")
        check(deliv_data.get("safety_boundaries", {}).get("confirmed_vulnerability") is False, "Delivery manifest safety confirmed_vulnerability == false")
    else:
        check(False, "delivery.json exists")

    # ========================================================================
    # Final Validation Summary
    # ========================================================================
    print("\n" + "=" * 75)
    if checks_failed == 0:
        print(f"Phase-97A-GATE-003 Integration Gate Validation: ALL CHECKS PASSED (100%)")
    else:
        print(f"Phase-97A-GATE-003 Integration Gate Validation: FAILED ({checks_failed} errors)")
    print(f"  Total Checks Passed: {checks_passed}")
    print(f"  Total Checks Failed: {checks_failed}")
    if errors:
        print("\nErrors encountered:")
        for e in errors:
            print(f"  - {e}")
    print("=" * 75)

    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
