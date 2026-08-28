#!/usr/bin/env python3
"""
scripts/validate_phase100a_mega_reconciliation.py — Automated Validator for Phase-100A-MEGA-001.
Path: scripts/validate_phase100a_mega_reconciliation.py

Task: Phase-100A-MEGA-001
Task Name: 全系统 50 模块、15+ 报告、传播动力学引擎、8-Node 审批门禁、全量看板与离线报告端到端大闭环超级对账门开发
PRD References:
  - 原 PRD v1.0 §5, §6, §7, §9, §10
  - 攻击者视角新增章节 §2, §4, §6, §7, §11
  - PRD v2.0 §1, §4, §6-§9, §9.3, §10, §13
  - PRD v3.1 §1, §2.1-§2.8, §3, §4

Verification Scope:
1. Deliverables files existence and size integrity.
2. MegaReconciliationGatekeeper instantiation and safety boundary invariants.
3. Pillar 1: Full System 50 capability modules (M01-M50) reconciliation.
4. Pillar 2: 15+ Red Team Action Reports (RED-001 ~ RED-020 + Summaries) reconciliation.
5. Pillar 3: Attack Propagation Dynamics Engine (4 layers, 7 edges, Markov 5-state model, equations) reconciliation.
6. Pillar 4: 8-Node Controlled Replay Gatekeeper (Node 1~8 approval workflow, role signatures, abort conditions, anti-step-skipping).
7. Pillar 5: Assessment Dashboard 4 views & Offline Report Export pipeline with Data Redaction.
8. Pillar 6: 10 Mega Known-Bad Anomaly Injections (KB-100A-001 ~ KB-100A-010) 100% defense interception.
9. YAML Matrix and JSON Master Compliance Summary snapshot verification.
10. Non-Retroactivity, 0 Production Penetration, and 0 Formal Disconnect Guarantees.

Usage:
    python3 scripts/validate_phase100a_mega_reconciliation.py
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

from multi_agent.replay.phase100a_mega_reconciliation_gate import (
    MegaReconciliationGatekeeper,
    MegaReconciliationResult,
    SYSTEM_50_MODULES_CATALOG,
    RED_TEAM_REPORTS_CATALOG,
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
logger = logging.getLogger("Phase100AMegaValidator")

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
        ("CORE_MEGA_GATE_PY", ROOT / "multi_agent/replay/phase100a_mega_reconciliation_gate.py"),
        ("DOC_GATE_NOTES", ROOT / "docs/phase100a_mega_reconciliation_gate_notes.md"),
        ("DOC_DESIGN_SPEC", ROOT / "docs/phase100a_mega_reconciliation_design.md"),
        ("RECON_MATRIX_YAML", ROOT / "phase100a_mega_reconciliation_matrix.yaml"),
        ("MASTER_COMPLIANCE_JSON", ROOT / "phase100a_master_compliance_summary.json"),
        ("VALIDATOR_SCRIPT", ROOT / "scripts/validate_phase100a_mega_reconciliation.py"),
        ("TEST_SUITE_PY", ROOT / "tests/test_phase100a_mega_reconciliation_gate.py"),
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
    gate = MegaReconciliationGatekeeper()
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
    logger.info("--- [Check 4] Pillar 2: 15+ Red Team Action Reports Reconciliation ---")
    gate = MegaReconciliationGatekeeper()
    r_res = gate.reconcile_red_team_reports()

    record_check("REP_COUNT_GTE_15", "Total Red Team Reports >= 15", r_res.get("total_reports_audited", 0) >= 15, f"Audited {r_res.get('total_reports_audited')} reports")
    record_check("REP_ALL_CLOSED", "All Reports Closed & Judge Approved", r_res.get("all_reports_closed") is True, "Status: closed/judge_approved")
    record_check("REP_ZERO_BREAKTHROUGHS", "Zero Real Breakthroughs", r_res.get("total_breakthroughs") == 0, "Breakthrough count: 0")
    record_check("REP_BOUNDARY_PRESERVATION", "Boundary Preservation Rate == 100%", r_res.get("boundary_preservation_rate") == 1.0, "100.0% boundary preserved")
    record_check("REP_CANDIDATE_LEVEL", "All Findings are Candidate Level", r_res.get("all_findings_candidate_level") is True, "all_findings_are_candidate: true")


def verify_pillar_3_propagation_dynamics() -> None:
    logger.info("--- [Check 5] Pillar 3: Attack Propagation Dynamics Reconciliation ---")
    gate = MegaReconciliationGatekeeper()
    p_res = gate.reconcile_propagation_dynamics()

    record_check("PROP_LAYERS_4", "4 Security Layers Configured", p_res.get("total_layers") == 4, "supply_chain, dev_env, rag_data, runtime_sandbox")
    record_check("PROP_EDGE_TYPES_7", "7 Edge Types Configured", p_res.get("total_edge_types") == 7, "7 standardized edge conductivity types")
    record_check("PROP_MARKOV_VALID", "Markov 5-State Transition Row Sum == 1.0", p_res.get("markov_stochastic_valid") is True, "Stochastic row-sum normalization valid")
    record_check("PROP_PRESSURE_EQ", "Edge Pressure Equation Consistent", p_res.get("pressure_equation_consistent") is True, "P_edge differential evaluated")
    record_check("PROP_PATH_DEG", "Path Degradation Equation Consistent", p_res.get("path_degradation_consistent") is True, "G_path evaluated")


def verify_pillar_4_gatekeeper_8node() -> None:
    logger.info("--- [Check 6] Pillar 4: 8-Node Gatekeeper Authorization Reconciliation ---")
    gate = MegaReconciliationGatekeeper()
    g_res = gate.reconcile_8node_gatekeeper()

    record_check("GATE_NODES_8", "8 Statutory Review Nodes", g_res.get("statutory_nodes") == 8, "Node 1 to Node 8 defined")
    record_check("GATE_SEQ_FLOW", "Sequential Flow Enforced", g_res.get("sequential_flow_enforced") is True, "Step skipping blocked")
    record_check("GATE_ROLE_SIGS", "Role-Based Signatures Verified", g_res.get("role_signatures_verified") is True, "Human review signatures validated")
    record_check("GATE_ABORT_7", "7 Standard Rollback Abort Conditions", g_res.get("abort_conditions_count") == 7, "ABORT-01 to ABORT-07 present")
    record_check("GATE_ROLLBACK_5", "5 Standard Rollback Steps", g_res.get("rollback_steps_count") == 5, "STEP-01 to STEP-05 present")


def verify_pillar_5_dashboard_and_reports() -> None:
    logger.info("--- [Check 7] Pillar 5: Dashboard Views & Offline Reports Reconciliation ---")
    gate = MegaReconciliationGatekeeper()
    d_res = gate.reconcile_dashboard_and_reports()

    record_check("DASH_VIEWS_4", "4 Core Dashboard Views Verified", d_res.get("total_views_verified") == 4, "Heatmap, Propagation, Degradation, RedTeam")
    record_check("DASH_OFFLINE", "Offline Self-Contained", d_res.get("offline_self_contained") is True, "Zero external network/CDN dependencies")
    record_check("DASH_DATA_REDACT", "Data Redaction Policy Enforced", d_res.get("data_redaction_verified") is True, "Sensitive credentials redacted")
    record_check("DASH_ZERO_TELEMETRY", "Zero Telemetry Guaranteed", d_res.get("zero_telemetry_guaranteed") is True, "No runtime phone-home")


def verify_pillar_6_known_bad_injections() -> None:
    logger.info("--- [Check 8] Pillar 6: 10 Mega Known-Bad Injections Defense ---")
    gate = MegaReconciliationGatekeeper()
    kb_res = gate.execute_known_bad_injections()

    record_check("KB_TOTAL_10", "10 Known-Bad Scenarios Injected", kb_res.get("total_scenarios_injected") == 10, "KB-100A-001 ~ KB-100A-010")
    record_check("KB_INTERCEPT_10", "10 Known-Bad Scenarios Intercepted", kb_res.get("total_scenarios_intercepted") == 10, "100.0% Interception rate")
    record_check("KB_RATE_100", "Interception Rate == 100%", kb_res.get("interception_rate") == 1.0, "Zero bypasses")
    record_check("KB_ZERO_UNHANDLED", "Zero Unhandled Exceptions", kb_res.get("zero_unhandled_exceptions") is True, "All exceptions mapped to security domain")


def verify_matrix_yaml_and_compliance_json() -> None:
    logger.info("--- [Check 9] Matrix YAML & Compliance Summary Snapshot Files ---")
    gate = MegaReconciliationGatekeeper()
    matrix_path = ROOT / "phase100a_mega_reconciliation_matrix.yaml"
    compliance_path = ROOT / "phase100a_master_compliance_summary.json"

    gate.generate_matrix_yaml(matrix_path)
    gate.generate_compliance_summary_json(compliance_path)

    # Verify YAML content
    with open(matrix_path, "r", encoding="utf-8") as f:
        ydata = yaml.safe_load(f) or {}
    record_check("YAML_TASK_ID", "Matrix YAML Task ID Match", ydata.get("task_id") == "Phase-100A-MEGA-001", "Task ID: Phase-100A-MEGA-001")
    record_check("YAML_STATUS_PASS", "Matrix YAML Status == PASS", ydata.get("joint_verification_summary", {}).get("status") == "PASS", "Joint verification PASS")
    record_check("YAML_50_MODULES", "Matrix YAML 50 Modules Present", len(ydata.get("modules_catalog_50", {})) == 50, "50 Modules in matrix catalog")

    # Verify JSON content
    with open(compliance_path, "r", encoding="utf-8") as f:
        jdata = json.load(f) or {}
    record_check("JSON_TASK_ID", "Compliance JSON Task ID Match", jdata.get("task_id") == "Phase-100A-MEGA-001", "Task ID: Phase-100A-MEGA-001")
    record_check("JSON_STATUS_PASS", "Compliance JSON Status == PASS", jdata.get("status") == "PASS", "Snapshot status PASS")
    record_check("JSON_NON_RETRO", "Compliance JSON Non-Retroactivity True", jdata.get("non_retroactivity_guarantee", {}).get("historical_phases_intact") is True, "Historical phases intact")


def main() -> int:
    logger.info("================================================================================")
    logger.info("  Phase 100A Mega Reconciliation Gatekeeper — Automated Verification Suite")
    logger.info("================================================================================")

    verify_deliverables_existence()
    verify_safety_boundaries_invariants()
    verify_pillar_1_50_modules()
    verify_pillar_2_red_team_reports()
    verify_pillar_3_propagation_dynamics()
    verify_pillar_4_gatekeeper_8node()
    verify_pillar_5_dashboard_and_reports()
    verify_pillar_6_known_bad_injections()
    verify_matrix_yaml_and_compliance_json()

    logger.info("================================================================================")
    logger.info(f"  Verification Complete: Passed: {checks_passed}, Failed: {checks_failed}")
    logger.info("================================================================================")

    if checks_failed == 0:
        logger.info("  ✓ ALL CHECKS PASSED: Phase-100A-MEGA-001 100% COMPLIANT & ALIGNED")
        return 0
    else:
        logger.error(f"  ✗ {checks_failed} CHECKS FAILED: See above logs for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
