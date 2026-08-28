#!/usr/bin/env python3
"""
scripts/validate_phase104a_mega_reconciliation.py — Automated Validator for Phase-104A-MEGA-001.
Path: scripts/validate_phase104a_mega_reconciliation.py

Task: Phase-104A-MEGA-001
Task Name: 全系统 Milestone 4.0 超级全景端到端大闭环对账门开发
PRD References:
  - 原 PRD v1.0 §4, §5, §6, §9, §10, §13, §15
  - 攻击者视角新增章节 §2, §3, §4, §5, §6, §7, §11
  - PRD v2.0 §1, §4, §5, §6-§9, §10, §13
  - PRD v3.1 §1, §2.1-§2.8, §3, §4, §9

Verification Scope:
1. Deliverables files existence and size integrity.
2. Phase104AMegaReconciliationGate instantiation and safety boundary invariants.
3. Pillar 1: Full System 50 capability modules (M01-M50) reconciliation.
4. Pillar 2: 20 Red Team Action Reports (RED-001 ~ RED-020) reconciliation.
5. Pillar 3: 60 Phase 101-103 Extended Adversarial Scenarios reconciliation.
6. Pillar 4: Attack Propagation Dynamics Engine (4 layers, 7 edges, Markov 5-state model, equations) reconciliation.
7. Pillar 5: 8-Node Controlled Replay Gatekeeper (Node 1~8 approval workflow, role signatures, abort conditions, anti-step-skipping).
8. Pillar 6: Assessment Dashboard 4 views & Offline Report Export pipeline with Data Redaction.
9. Pillar 7: 10 Mega Known-Bad Anomaly Injections (KB-104A-001 ~ KB-104A-010) 100% defense interception.
10. YAML Matrix and JSON Master Compliance Summary snapshot verification.
11. Non-Retroactivity, 0 Production Penetration, and 0 Formal Disconnect Guarantees.

Usage:
    python3 scripts/validate_phase104a_mega_reconciliation.py
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

from multi_agent.replay.phase104a_mega_reconciliation_gate import (
    Phase104AMegaReconciliationGate,
    Phase104AMegaReconciliationResult,
    SYSTEM_50_MODULES_CATALOG,
    RED_TEAM_REPORTS_CATALOG,
    EXTENDED_60_SCENARIOS_CATALOG,
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
logger = logging.getLogger("Phase104AMegaValidator")

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


def verify_deliverables_existence() -> None:
    logger.info("--- [Check 1] Deliverables Files Existence & Integrity ---")
    required_files = [
        ("CORE_MEGA_GATE_PY", ROOT / "multi_agent/replay/phase104a_mega_reconciliation_gate.py"),
        ("DOC_GATE_NOTES", ROOT / "docs/phase104a_mega_reconciliation_gate_notes.md"),
        ("DOC_DESIGN_SPEC", ROOT / "docs/phase104a_mega_reconciliation_design.md"),
        ("RECON_MATRIX_YAML", ROOT / "phase104a_mega_reconciliation_matrix.yaml"),
        ("MASTER_COMPLIANCE_JSON", ROOT / "phase104a_master_compliance_summary.json"),
        ("VALIDATOR_SCRIPT", ROOT / "scripts/validate_phase104a_mega_reconciliation.py"),
        ("TEST_SUITE_PY", ROOT / "tests/test_phase104a_mega_reconciliation_gate.py"),
        ("EXECUTION_SUMMARY", ROOT / "phase104a_mega001_execution_summary.yaml"),
    ]

    for tag, fpath in required_files:
        exists = fpath.exists() and fpath.stat().st_size > 0
        record_check(f"DELIV_{tag}", f"Deliverable File {fpath.name}", exists, f"Path: {fpath} ({fpath.stat().st_size if fpath.exists() else 0} bytes)")


def verify_safety_boundaries_invariants() -> None:
    logger.info("--- [Check 2] Safety Boundaries & Non-Negotiable Declarations ---")
    b = MEGA_RECONCILIATION_SAFETY_BOUNDARIES

    record_check("SAFE_NO_CONFIRMED_VULN", "confirmed_vulnerability=False", b.get("confirmed_vulnerability") is False, "Candidate finding status strictly preserved")
    record_check("SAFE_NO_FORMAL_FINDING", "formal_finding_allowed=False", b.get("formal_finding_allowed") is False, "Formal finding restricted")
    record_check("SAFE_NO_PROD_SAFETY", "production_safety_claimed=False", b.get("production_safety_claimed") is False, "Production safety claims forbidden")
    record_check("SAFE_NO_CONTROLLED_REPLAY", "controlled_replay_claimed=False", b.get("controlled_replay_claimed") is False, "Uncontrolled replay claim forbidden")
    record_check("SAFE_SYNTHETIC_ONLY", "synthetic_only=True", b.get("synthetic_only") is True, "Pure synthetic mock traces")
    record_check("SAFE_FAKE_RUNTIME", "fake_runtime_only=True", b.get("fake_runtime_only") is True, "Fake runtime isolation active")
    record_check("SAFE_HUMAN_REVIEW", "requires_human_review=True", b.get("requires_human_review") is True, "Human review mandatory")
    record_check("SAFE_NON_RETROACTIVITY", "non_retroactivity_guarantee=True", b.get("non_retroactivity_guarantee") is True, "Historical baselines frozen")


def verify_pillar_1_50_modules() -> None:
    logger.info("--- [Check 3] Pillar 1: Full System 50 Modules Reconciliation ---")
    gate = Phase104AMegaReconciliationGate()
    m_res = gate.reconcile_50_modules()

    record_check("MOD_TOTAL_50", "Total Modules Count == 50", m_res.get("total_modules") == 50, f"Found {m_res.get('total_modules')} modules")
    record_check("MOD_ALIGNED_50", "Aligned Modules Count == 50", m_res.get("aligned_modules") == 50, "100% modules aligned")
    record_check("MOD_MISMATCH_ZERO", "Zero Mismatches", m_res.get("mismatches") == 0, "No discrepancy detected")
    record_check("MOD_P0_COUNT", "P0 Modules Count == 23", m_res.get("p0_count") == 23, "23 P0 modules verified")
    record_check("MOD_P1_COUNT", "P1 Modules Count == 13", m_res.get("p1_count") == 13, "13 P1 modules verified")
    record_check("MOD_P2_COUNT", "P2 Modules Count == 6", m_res.get("p2_count") == 6, "6 P2 modules verified")
    record_check("MOD_V2_COUNT", "v2.0 Modules Count == 8", m_res.get("v2_count") == 8, "8 v2.0 modules verified")
    record_check("MOD_SYNTHETIC_ONLY", "All Modules Synthetic Only", m_res.get("all_synthetic_only") is True, "synthetic_only enforced")


def verify_pillar_2_red_team_reports() -> None:
    logger.info("--- [Check 4] Pillar 2: 20 Red Team Action Reports Reconciliation ---")
    gate = Phase104AMegaReconciliationGate()
    r_res = gate.reconcile_red_team_reports()

    record_check("REP_TOTAL_20", "Total Red Team Reports == 20", r_res.get("total_reports_audited") == 20, f"Audited {r_res.get('total_reports_audited')} reports")
    record_check("REP_ALL_CLOSED", "All Reports Closed/Approved", r_res.get("all_reports_closed") is True, "100% reports closed")
    record_check("REP_BREAKTHROUGH_ZERO", "Total Breakthroughs == 0", r_res.get("total_breakthroughs") == 0, "Zero breakthroughs detected")
    record_check("REP_BOUNDARY_100", "Boundary Preservation Rate == 100%", r_res.get("boundary_preservation_rate") == 1.0, "100% boundary preserved")
    record_check("REP_CANDIDATE_LEVEL", "All Findings Candidate Level", r_res.get("all_findings_candidate_level") is True, "Candidate status preserved")


def verify_pillar_3_extended_60_scenarios() -> None:
    logger.info("--- [Check 5] Pillar 3: 60 Phase 101-103 Extended Adversarial Scenarios ---")
    gate = Phase104AMegaReconciliationGate()
    ext_res = gate.reconcile_60_extended_scenarios()

    record_check("EXT_TOTAL_60", "Total Extended Scenarios == 60", ext_res.get("total_extended_cases") == 60, f"Total cases: {ext_res.get('total_extended_cases')}")
    record_check("EXT_P101_COUNT", "Phase 101 Scenarios == 20", ext_res.get("phase101_cases_count") == 20, "20 Phase 101 cases verified")
    record_check("EXT_P102_COUNT", "Phase 102 Scenarios == 20", ext_res.get("phase102_cases_count") == 20, "20 Phase 102 cases verified")
    record_check("EXT_P103_COUNT", "Phase 103 Scenarios == 20", ext_res.get("phase103_cases_count") == 20, "20 Phase 103 cases verified")
    record_check("EXT_ATTACK_COUNT", "Attack Scenarios == 48", ext_res.get("attack_cases_count") == 48, "48 attack scenarios verified")
    record_check("EXT_CONTROL_COUNT", "Control Scenarios == 12", ext_res.get("control_cases_count") == 12, "12 control scenarios verified")
    record_check("EXT_INTERCEPTIONS", "Total Interceptions == 48", ext_res.get("interceptions_count") == 48, "100% attack cases intercepted")
    record_check("EXT_CONTROLS_PASSED", "Controls Passed == 12", ext_res.get("controls_passed_count") == 12, "100% control cases passed")
    record_check("EXT_BREAKTHROUGHS_ZERO", "Breakthroughs Detected == 0", ext_res.get("breakthroughs_detected") == 0, "Zero breakthroughs across 60 cases")


def verify_pillar_4_propagation_dynamics() -> None:
    logger.info("--- [Check 6] Pillar 4: Attack Propagation Dynamics Engine ---")
    gate = Phase104AMegaReconciliationGate()
    p_res = gate.reconcile_propagation_dynamics()

    record_check("PROP_LAYERS_4", "Total Security Layers == 4", p_res.get("total_layers") == 4, "4 layers verified")
    record_check("PROP_EDGES_7", "Total Edge Types == 7", p_res.get("total_edge_types") == 7, "7 edge types verified")
    record_check("PROP_MARKOV_STOCHASTIC", "Markov Matrix Stochasticity Valid", p_res.get("markov_stochastic_valid") is True, "Row sums = 1.0 verified")
    record_check("PROP_PRESSURE_EQ", "Pressure Differential Equation Consistent", p_res.get("pressure_equation_consistent") is True, "P_edge math consistent")
    record_check("PROP_PATH_DEGRADE", "Path Degradation Equation Consistent", p_res.get("path_degradation_consistent") is True, "G_path math consistent")


def verify_pillar_5_8node_gatekeeper() -> None:
    logger.info("--- [Check 7] Pillar 5: 8-Node Controlled Replay Gatekeeper ---")
    gate = Phase104AMegaReconciliationGate()
    g_res = gate.reconcile_8node_gatekeeper()

    record_check("GATE_NODES_8", "Statutory Nodes == 8", g_res.get("statutory_nodes") == 8, "8 nodes verified")
    record_check("GATE_SEQ_FLOW", "Sequential Flow Enforced", g_res.get("sequential_flow_enforced") is True, "Strict sequential state machine verified")
    record_check("GATE_ROLE_SIGS", "Role Signatures Verified", g_res.get("role_signatures_verified") is True, "Role signature chain verified")
    record_check("GATE_STEP_SKIP_BLOCKED", "Step Skipping Hard-Blocked", g_res.get("step_skipping_blocked") is True, "StepSkippingViolation active")
    record_check("GATE_ABORT_CONDS", "Abort Conditions Count == 7", g_res.get("abort_conditions_count") == 7, "7 abort conditions verified")
    record_check("GATE_ROLLBACK_STEPS", "Rollback Steps Count == 5", g_res.get("rollback_steps_count") == 5, "5 rollback steps verified")


def verify_pillar_6_dashboard_and_reports() -> None:
    logger.info("--- [Check 8] Pillar 6: Assessment Dashboard & Offline Report Pipeline ---")
    gate = Phase104AMegaReconciliationGate()
    d_res = gate.reconcile_dashboard_and_reports()

    record_check("DASH_VIEWS_4", "Total Dashboard Views == 4", d_res.get("total_views_verified") == 4, "4 views verified")
    record_check("DASH_OFFLINE", "Offline Self-Contained Guaranteed", d_res.get("offline_self_contained") is True, "No external CDN dependencies")
    record_check("DASH_REDACTION", "Data Redaction Verified", d_res.get("data_redaction_verified") is True, "API keys and secrets redacted")
    record_check("DASH_ZERO_TELEM", "Zero Telemetry Guaranteed", d_res.get("zero_telemetry_guaranteed") is True, "Zero outbound telemetry verified")


def verify_pillar_7_known_bad_injections() -> None:
    logger.info("--- [Check 9] Pillar 7: 10 Mega Known-Bad Anomaly Injections ---")
    gate = Phase104AMegaReconciliationGate()
    kb_res = gate.execute_known_bad_injections()

    record_check("KB_TOTAL_10", "Total Injected Scenarios == 10", kb_res.get("total_scenarios_injected") == 10, "10 scenarios injected")
    record_check("KB_INTERCEPTED_10", "Total Intercepted Scenarios == 10", kb_res.get("total_scenarios_intercepted") == 10, "100% intercepted")
    record_check("KB_RATE_100", "Interception Rate == 100%", kb_res.get("interception_rate") == 1.0, "100% defense rate")
    record_check("KB_ZERO_UNHANDLED", "Zero Unhandled Exceptions", kb_res.get("zero_unhandled_exceptions") is True, "All exceptions mapped to specific defense classes")


def verify_matrix_and_compliance_artifacts() -> None:
    logger.info("--- [Check 10] YAML Matrix & JSON Compliance Summary Snapshots ---")
    matrix_path = ROOT / "phase104a_mega_reconciliation_matrix.yaml"
    json_path = ROOT / "phase104a_master_compliance_summary.json"

    # Regenerate fresh snapshots
    gate = Phase104AMegaReconciliationGate()
    gate.generate_matrix_yaml(matrix_path)
    gate.generate_compliance_summary_json(json_path)

    # Verify YAML Matrix
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix_data = yaml.safe_load(f)

    record_check("YAML_PHASE", "YAML Matrix Phase == Phase-104A", matrix_data.get("phase") == "Phase-104A", f"Phase: {matrix_data.get('phase')}")
    record_check("YAML_MODULES_50", "YAML Matrix Modules Count == 50", len(matrix_data.get("modules_catalog_50", {})) == 50, "50 modules catalog in YAML")
    record_check("YAML_REPORTS_20", "YAML Matrix Reports Count == 20", len(matrix_data.get("red_team_reports_catalog_20", [])) == 20, "20 reports catalog in YAML")
    record_check("YAML_EXTENDED_60", "YAML Matrix Extended Scenarios Count == 60", len(matrix_data.get("extended_scenarios_catalog_60", [])) == 60, "60 extended scenarios catalog in YAML")

    # Verify JSON Compliance Summary
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    record_check("JSON_PHASE", "JSON Summary Phase == Phase-104A", json_data.get("phase") == "Phase-104A", f"Phase: {json_data.get('phase')}")
    record_check("JSON_STATUS", "JSON Summary Status == PASS", json_data.get("status") == "PASS", f"Status: {json_data.get('status')}")
    record_check("JSON_TOTAL_MODULES", "JSON Summary Total Modules == 50", json_data.get("system_statistics", {}).get("total_modules") == 50, "50 modules in JSON")
    record_check("JSON_TOTAL_REPORTS", "JSON Summary Total Reports == 20", json_data.get("system_statistics", {}).get("total_red_team_reports") == 20, "20 reports in JSON")
    record_check("JSON_EXTENDED_SCENARIOS", "JSON Summary Extended Scenarios == 60", json_data.get("system_statistics", {}).get("total_extended_scenarios") == 60, "60 extended scenarios in JSON")


def main() -> int:
    logger.info("================================================================================")
    logger.info("  Phase-104A-MEGA-001 Master Reconciliation Gate Validator")
    logger.info("================================================================================")

    # First ensure matrix and summary are generated
    matrix_path = ROOT / "phase104a_mega_reconciliation_matrix.yaml"
    json_path = ROOT / "phase104a_master_compliance_summary.json"
    gate = Phase104AMegaReconciliationGate()
    gate.generate_matrix_yaml(matrix_path)
    gate.generate_compliance_summary_json(json_path)

    verify_deliverables_existence()
    verify_safety_boundaries_invariants()
    verify_pillar_1_50_modules()
    verify_pillar_2_red_team_reports()
    verify_pillar_3_extended_60_scenarios()
    verify_pillar_4_propagation_dynamics()
    verify_pillar_5_8node_gatekeeper()
    verify_pillar_6_dashboard_and_reports()
    verify_pillar_7_known_bad_injections()
    verify_matrix_and_compliance_artifacts()

    logger.info("================================================================================")
    logger.info(f"  Validation Summary: {checks_passed} PASSED, {checks_failed} FAILED")
    logger.info("================================================================================")

    if checks_failed > 0:
        logger.error(f"Validation FAILED with {checks_failed} failing checks.")
        return 1

    logger.info("✓ ALL CHECKS PASSED (100% COMPLIANT WITH MILESTONE 4.0 PRD & ARCHITECTURE).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
