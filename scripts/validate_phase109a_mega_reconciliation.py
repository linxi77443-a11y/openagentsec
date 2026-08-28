#!/usr/bin/env python3
"""
scripts/validate_phase109a_mega_reconciliation.py — Automated Validator for Phase-109A-MEGA-001.
Path: scripts/validate_phase109a_mega_reconciliation.py

Task: Phase-109A-MEGA-001
Task Name: Milestone 5.0 单智能体全景端到端大闭环对账门开发 (Milestone 5.0 Single-Agent Super Panoramic Mega Reconciliation Gate)
PRD References:
  - 原 PRD v1.0 §4, §5, §6, §7, §9, §10, §11, §13, §15
  - 攻击者视角新增章节 §2, §3, §4, §5, §6, §7, §8, §9, §11
  - PRD v2.0 §1, §4, §5, §6-§9, §10, §13
  - PRD v3.1 §1, §2.1-§2.8, §3, §4, §8, §9

Verification Scope:
1. Deliverables files existence and size integrity.
2. Phase109AMegaReconciliationGate instantiation and safety boundary invariants.
3. Pillar 1: Full System 50 capability modules (M01-M50) reconciliation.
4. Pillar 2: 20 Red Team Action Reports (RED-001 ~ RED-020) reconciliation.
5. Pillar 3: 60 Phase 101-103 Frontier Adversarial Scenarios reconciliation.
6. Pillar 4: 80 Phase 105-108 Single-Agent Advanced Adversarial Scenarios reconciliation.
7. Grand Unified 140 Extended Adversarial Scenarios spectrum reconciliation.
8. Pillar 5: Attack Propagation Dynamics Engine (4 layers, 7 edges, Markov 5-state model, equations) reconciliation.
9. Pillar 6: 8-Node Controlled Replay Gatekeeper (Node 1~8 approval workflow, role signatures, abort conditions, anti-step-skipping).
10. Pillar 7: Assessment Dashboard 4 views & Offline Report Export pipeline with Data Redaction.
11. Pillar 8: 10 Mega Known-Bad Anomaly Injections (KB-109A-001 ~ KB-109A-010) 100% defense interception.
12. YAML Matrix and JSON Master Compliance Summary snapshot verification.
13. Non-Retroactivity, 0 Production Penetration, and 0 Formal Disconnect Guarantees.

Usage:
    python3 scripts/validate_phase109a_mega_reconciliation.py
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from multi_agent.replay.phase109a_mega_reconciliation_gate import (
    Phase109AMegaReconciliationGate,
    Phase109AMegaReconciliationResult,
    SYSTEM_50_MODULES_CATALOG,
    RED_TEAM_REPORTS_CATALOG,
    FRONTIER_60_SCENARIOS_CATALOG,
    SINGLE_AGENT_80_SCENARIOS_CATALOG,
    ALL_140_EXTENDED_SCENARIOS_CATALOG,
    MEGA_RECONCILIATION_SAFETY_BOUNDARIES,
    KNOWN_BAD_MEGA_DEFENSE_RULES,
    MegaReconciliationError,
    FakeRuntimeViolationError,
    RealInfrastructureAccessViolationError,
    LiveExecutionBlockedError,
    LiveVectorDBAccessViolationError,
    SandboxEscapeExecutionViolationError,
    AuditStreamTamperingViolationError,
    ReplayGateApprovalMissingError,
    ModuleAlignmentMismatchError,
    ReportIntegrityViolationError,
    ExtendedScenarioMismatchError,
    SingleAgentScenarioMismatchError,
    PropagationDynamicsMismatchError,
    DashboardDataContractViolationError,
)

from src.gatekeeper.controlled_replay_gatekeeper import (
    ControlledReplayGatekeeper,
    GateNodeEnum,
    NodeStatusEnum,
    ReviewerRoleEnum,
    ReviewDecisionEnum,
    SessionStatusEnum,
    HumanSignature,
    STANDARD_ABORT_CONDITIONS,
    STANDARD_ROLLBACK_STEPS,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Phase109AMegaValidator")

checks_passed = 0
checks_failed = 0
check_details: List[Dict[str, Any]] = []


def record_check(check_id: str, name: str, condition: bool, details: str = "") -> bool:
    global checks_passed, checks_failed, check_details
    if condition:
        checks_passed += 1
        logger.info(f"  ✓ [{check_id}] PASS: {name} - {details}")
    else:
        checks_failed += 1
        logger.error(f"  ✗ [{check_id}] FAIL: {name} - {details}")
    check_details.append({
        "check_id": check_id,
        "name": name,
        "passed": condition,
        "details": details,
    })
    return condition


def main() -> int:
    logger.info("================================================================================")
    logger.info("  Starting Automated Validator for Phase-109A-MEGA-001 (Milestone 5.0 Mega Gate)")
    logger.info("================================================================================")

    # --------------------------------------------------------------------------
    # Check 1: Deliverables Existence and Size
    # --------------------------------------------------------------------------
    deliverables = [
        "multi_agent/replay/phase109a_mega_reconciliation_gate.py",
        "docs/phase109a_mega_reconciliation_design.md",
        "docs/phase109a_mega_reconciliation_gate_notes.md",
        "phase109a_mega_reconciliation_matrix.yaml",
        "phase109a_master_compliance_summary.json",
        "scripts/validate_phase109a_mega_reconciliation.py",
        "tests/test_phase109a_mega_reconciliation_gate.py",
        "phase109a_mega001_execution_summary.yaml",
        "delivery.json",
    ]
    all_files_exist = True
    for rel_path in deliverables:
        p = ROOT / rel_path
        if not p.exists() or p.stat().st_size == 0:
            all_files_exist = False
            logger.error(f"Missing or empty deliverable: {rel_path}")
    record_check("CHK-109A-01", "Deliverables Integrity", all_files_exist, f"Verified {len(deliverables)} required core files")

    # --------------------------------------------------------------------------
    # Check 2: Gatekeeper Engine Instantiation & Safety Boundaries
    # --------------------------------------------------------------------------
    gate = Phase109AMegaReconciliationGate(root_dir=ROOT)
    boundaries = MEGA_RECONCILIATION_SAFETY_BOUNDARIES
    sb_valid = (
        boundaries["confirmed_vulnerability"] is False
        and boundaries["formal_finding_allowed"] is False
        and boundaries["production_safety_claimed"] is False
        and boundaries["controlled_replay_claimed"] is False
        and boundaries["synthetic_only"] is True
        and boundaries["fake_runtime_only"] is True
        and boundaries["requires_human_review"] is True
        and boundaries["all_findings_are_candidate"] is True
        and boundaries["non_retroactivity_guarantee"] is True
        and boundaries["zero_production_penetration"] is True
    )
    record_check("CHK-109A-02", "Safety Boundaries & Non-Negotiable Declarations", sb_valid, "100% strict non-vulnerability & fake runtime invariants")

    # --------------------------------------------------------------------------
    # Check 3: Pillar 1 - 50 Modules Reconciliation
    # --------------------------------------------------------------------------
    m_summary = gate.reconcile_50_modules()
    p1_valid = (
        m_summary["total_modules"] == 50
        and m_summary["aligned_modules"] == 50
        and m_summary["mismatches"] == 0
        and m_summary["p0_count"] == 23
        and m_summary["p1_count"] == 13
        and m_summary["p2_count"] == 6
        and m_summary["v2_count"] == 8
        and m_summary["status"] == "PASS"
    )
    record_check("CHK-109A-03", "Pillar 1: 50 Capability Modules (M01-M50)", p1_valid, "P0(23), P1(13), P2(6), v2(8) 100% aligned")

    # --------------------------------------------------------------------------
    # Check 4: Pillar 2 - 20 Red Team Action Reports Reconciliation
    # --------------------------------------------------------------------------
    r_summary = gate.reconcile_red_team_reports()
    p2_valid = (
        r_summary["total_reports_audited"] == 20
        and r_summary["all_reports_closed"] is True
        and r_summary["total_breakthroughs"] == 0
        and r_summary["boundary_preservation_rate"] == 1.0
        and r_summary["all_findings_candidate_level"] is True
        and r_summary["status"] == "PASS"
    )
    record_check("CHK-109A-04", "Pillar 2: 20 Red Team Action Reports (RED-001~RED-020)", p2_valid, "20 reports closed, 0 breakthroughs, 100% boundary preservation")

    # --------------------------------------------------------------------------
    # Check 5: Pillar 3 - 60 Frontier Adversarial Scenarios (Phase 101-103)
    # --------------------------------------------------------------------------
    f_summary = gate.reconcile_frontier_scenarios_p101_p103()
    p3_valid = (
        f_summary["total_frontier_cases"] == 60
        and f_summary["phase101_cases_count"] == 20
        and f_summary["phase102_cases_count"] == 20
        and f_summary["phase103_cases_count"] == 20
        and f_summary["attack_cases_count"] == 48
        and f_summary["control_cases_count"] == 12
        and f_summary["interceptions_count"] == 48
        and f_summary["controls_passed_count"] == 12
        and f_summary["breakthroughs_detected"] == 0
        and f_summary["status"] == "PASS"
    )
    record_check("CHK-109A-05", "Pillar 3: 60 Frontier Scenarios (Phase 101-103)", p3_valid, "48 attacks intercepted, 12 controls passed, 0 breakthroughs")

    # --------------------------------------------------------------------------
    # Check 6: Pillar 4 - 80 Single-Agent Scenarios (Phase 105-108)
    # --------------------------------------------------------------------------
    s_summary = gate.reconcile_single_agent_scenarios_p105_p108()
    p4_valid = (
        s_summary["total_single_agent_cases"] == 80
        and s_summary["phase105_cases_count"] == 20
        and s_summary["phase106_cases_count"] == 20
        and s_summary["phase107_cases_count"] == 20
        and s_summary["phase108_cases_count"] == 20
        and s_summary["attack_cases_count"] == 64
        and s_summary["control_cases_count"] == 16
        and s_summary["interceptions_count"] == 64
        and s_summary["controls_passed_count"] == 16
        and s_summary["breakthroughs_detected"] == 0
        and s_summary["status"] == "PASS"
    )
    record_check("CHK-109A-06", "Pillar 4: 80 Single-Agent Scenarios (Phase 105-108)", p4_valid, "64 attacks intercepted, 16 controls passed, 0 breakthroughs")

    # --------------------------------------------------------------------------
    # Check 7: Grand Unified 140 Extended Adversarial Scenarios Spectrum
    # --------------------------------------------------------------------------
    all_adv_summary = gate.reconcile_all_140_adversarial_scenarios()
    all_adv_valid = (
        all_adv_summary["total_cases"] == 140
        and all_adv_summary["total_frontier_cases"] == 60
        and all_adv_summary["total_single_agent_cases"] == 80
        and all_adv_summary["attack_cases_count"] == 112
        and all_adv_summary["control_cases_count"] == 28
        and all_adv_summary["interceptions_count"] == 112
        and all_adv_summary["controls_passed_count"] == 28
        and all_adv_summary["breakthroughs_detected"] == 0
        and all_adv_summary["status"] == "PASS"
    )
    record_check("CHK-109A-07", "Grand Unified 140 Adversarial Scenarios", all_adv_valid, "140 scenarios (112 attacks intercepted, 28 controls passed)")

    # --------------------------------------------------------------------------
    # Check 8: Pillar 5 - Attack Propagation Dynamics Mathematical Model
    # --------------------------------------------------------------------------
    p_summary = gate.reconcile_propagation_dynamics()
    p5_valid = (
        p_summary["total_layers"] == 4
        and p_summary["total_edge_types"] == 7
        and p_summary["markov_stochastic_valid"] is True
        and p_summary["pressure_equation_consistent"] is True
        and p_summary["path_degradation_consistent"] is True
        and p_summary["status"] == "PASS"
    )
    record_check("CHK-109A-08", "Pillar 5: Attack Propagation Dynamics Engine", p5_valid, "4 layers, 7 edges, Markov stochasticity valid, equations consistent")

    # --------------------------------------------------------------------------
    # Check 9: Pillar 6 - 8-Node Controlled Replay Gatekeeper Workflow
    # --------------------------------------------------------------------------
    g_summary = gate.reconcile_8node_gatekeeper()
    p6_valid = (
        g_summary["statutory_nodes"] == 8
        and g_summary["sequential_flow_enforced"] is True
        and g_summary["role_signatures_verified"] is True
        and g_summary["step_skipping_blocked"] is True
        and g_summary["abort_conditions_count"] == 7
        and g_summary["rollback_steps_count"] == 5
        and g_summary["status"] == "PASS"
    )
    record_check("CHK-109A-09", "Pillar 6: 8-Node Gatekeeper Workflow", p6_valid, "8 statutory nodes, role signatures verified, step-skipping blocked")

    # --------------------------------------------------------------------------
    # Check 10: Pillar 7 - Assessment Dashboard & Offline Report Exporter
    # --------------------------------------------------------------------------
    d_summary = gate.reconcile_dashboard_and_reports()
    p7_valid = (
        d_summary["total_views_verified"] == 4
        and d_summary["offline_self_contained"] is True
        and d_summary["data_redaction_verified"] is True
        and d_summary["zero_telemetry_guaranteed"] is True
        and d_summary["status"] == "PASS"
    )
    record_check("CHK-109A-10", "Pillar 7: Dashboard 4-View & Offline Report Pipeline", p7_valid, "4 views verified, offline self-contained, DLP redaction verified")

    # --------------------------------------------------------------------------
    # Check 11: Pillar 8 - 10 Final Known-Bad Anomaly Injections
    # --------------------------------------------------------------------------
    kb_summary = gate.execute_known_bad_injections()
    p8_valid = (
        kb_summary["total_scenarios_injected"] == 10
        and kb_summary["total_scenarios_intercepted"] == 10
        and kb_summary["interception_rate"] == 1.0
        and kb_summary["zero_unhandled_exceptions"] is True
        and kb_summary["status"] == "PASS"
    )
    record_check("CHK-109A-11", "Pillar 8: 10 Final Known-Bad Injections (KB-109A-001~010)", p8_valid, "10/10 hard blocked with typed exception defenses")

    # --------------------------------------------------------------------------
    # Check 12: Full Master Reconciliation Execution
    # --------------------------------------------------------------------------
    master_res = gate.run_full_reconciliation()
    master_valid = (
        master_res.task_id == "Phase-109A-MEGA-001"
        and master_res.milestone == "Milestone 5.0"
        and master_res.status == "PASS"
        and master_res.module_summary.status == "PASS"
        and master_res.report_summary.status == "PASS"
        and master_res.frontier_scenarios_summary.status == "PASS"
        and master_res.single_agent_scenarios_summary.status == "PASS"
        and master_res.all_adversarial_scenarios_summary.status == "PASS"
        and master_res.propagation_summary.status == "PASS"
        and master_res.gatekeeper_summary.status == "PASS"
        and master_res.dashboard_summary.status == "PASS"
        and master_res.known_bad_summary.status == "PASS"
    )
    record_check("CHK-109A-12", "Master Mega Reconciliation Execution", master_valid, "All Eight Pillars executed and returned PASS status")

    # --------------------------------------------------------------------------
    # Check 13: YAML Reconciliation Matrix Verification
    # --------------------------------------------------------------------------
    matrix_path = ROOT / "phase109a_mega_reconciliation_matrix.yaml"
    gate.generate_matrix_yaml(matrix_path)
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix_data = yaml.safe_load(f)
    matrix_valid = (
        matrix_data.get("task_id") == "Phase-109A-MEGA-001"
        and matrix_data.get("milestone") == "Milestone 5.0"
        and len(matrix_data.get("modules_catalog_50", {})) == 50
        and len(matrix_data.get("red_team_reports_catalog_20", [])) == 20
        and len(matrix_data.get("frontier_scenarios_catalog_60", [])) == 60
        and len(matrix_data.get("single_agent_scenarios_catalog_80", [])) == 80
        and len(matrix_data.get("all_adversarial_scenarios_catalog_140", [])) == 140
        and len(matrix_data.get("known_bad_defense_matrix_10", [])) == 10
        and matrix_data.get("joint_verification_summary", {}).get("status") == "PASS"
    )
    record_check("CHK-109A-13", "YAML Reconciliation Matrix Integrity", matrix_valid, "phase109a_mega_reconciliation_matrix.yaml verified")

    # --------------------------------------------------------------------------
    # Check 14: JSON Master Compliance Summary Snapshot Verification
    # --------------------------------------------------------------------------
    json_path = ROOT / "phase109a_master_compliance_summary.json"
    gate.generate_compliance_summary_json(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        compliance_data = json.load(f)
    json_valid = (
        compliance_data.get("task_id") == "Phase-109A-MEGA-001"
        and compliance_data.get("milestone") == "Milestone 5.0"
        and compliance_data.get("status") == "PASS"
        and compliance_data.get("system_statistics", {}).get("total_modules") == 50
        and compliance_data.get("system_statistics", {}).get("total_red_team_reports") == 20
        and compliance_data.get("system_statistics", {}).get("total_frontier_scenarios") == 60
        and compliance_data.get("system_statistics", {}).get("total_single_agent_scenarios") == 80
        and compliance_data.get("system_statistics", {}).get("total_adversarial_scenarios") == 140
        and compliance_data.get("system_statistics", {}).get("known_bad_scenarios_intercepted") == 10
    )
    record_check("CHK-109A-14", "JSON Master Compliance Summary Snapshot", json_valid, "phase109a_master_compliance_summary.json verified")

    # --------------------------------------------------------------------------
    # Check 15: Delivery Manifest Consistency
    # --------------------------------------------------------------------------
    delivery_path = ROOT / "delivery.json"
    delivery_valid = False
    if delivery_path.exists():
        with open(delivery_path, "r", encoding="utf-8") as f:
            deliv_data = json.load(f)
        delivery_valid = (
            deliv_data.get("workplan_id") == "Phase-109A-MEGA-001"
            and deliv_data.get("status") == "VALIDATED_PASS"
            and deliv_data.get("safety_boundaries", {}).get("synthetic_only") is True
            and deliv_data.get("safety_boundaries", {}).get("confirmed_vulnerability") is False
        )
    record_check("CHK-109A-15", "Delivery Manifest Integrity", delivery_valid, "delivery.json workplan_id and status match Phase-109A")

    # --------------------------------------------------------------------------
    # Final Result Summary
    # --------------------------------------------------------------------------
    total_checks = checks_passed + checks_failed
    pass_rate = (checks_passed / total_checks * 100.0) if total_checks > 0 else 0.0
    logger.info("================================================================================")
    logger.info(f"  Phase-109A Mega Reconciliation Validation Results: {checks_passed}/{total_checks} PASSED ({pass_rate:.1f}%)")
    logger.info("================================================================================")

    if checks_failed > 0:
        logger.error(f"VALIDATION FAILED with {checks_failed} failures.")
        return 1
    else:
        logger.info("ALL VALIDATION CHECKS PASSED PERFECTLY (100%).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
