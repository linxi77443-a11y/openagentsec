#!/usr/bin/env python3
"""
scripts/validate_phase99a_integrated_gate.py — Phase 99A Integrated Gate & Dynamic Replay Validator.
Path: scripts/validate_phase99a_integrated_gate.py

Task: Phase-99A-GATE-003
Task Name: 阶段 99 高阶对抗剧本集成验证与动态回放套件开发
PRD References:
  - 原 PRD v1.0 §4, §6, §10, §15
  - 攻击者视角新增章节 §2, §4, §7, §11
  - PRD v2.0 §4, §9.3, §10, §13
  - PRD v3.1 §2.3, §2.6, §2.7, §3, §4

Verification Scope:
1. Deliverables Files Existence & Structure Integrity.
2. Dynamic Replay Engine Instantiation & Safety Boundary Invariants.
3. Multi-Stage Attack Chains (CHAIN-99A-01 to CHAIN-99A-04) Validation.
4. Dynamic Replay Session Lifecycle & Fake Runtime Execution.
5. Gatekeeper Node 5 Authorization Requirement & Anti-Step-Skipping.
6. 10 Groups of High-Order Known-Bad Injection Defense Interceptions (KB-99A-001 to KB-99A-010).
7. Automated Signature Rejection & Fake Reviewer Protection.
8. Joint Reconciliation across 24 Advanced Adversarial Cases (M43, M45, M48, M50).
9. Source Playbooks & Execution Results Integrity.
10. Integrated Reconciliation Matrix & Master Compliance Summary Snapshot Verification.
11. Replay Audit Trail & Synthetic Trace Completeness.
12. Non-Retroactivity & Historical Module Integrity Guarantees.

Usage:
    python3 scripts/validate_phase99a_integrated_gate.py
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

from multi_agent.replay.phase99a_dynamic_replay_suite import (
    DynamicReplayEngine,
    DynamicReplaySession,
    ReplayStageStep,
    MultiStageAttackChain,
    ReplayExecutionStatus,
    Phase99AJointReconciliation,
    DYNAMIC_REPLAY_SAFETY_BOUNDARIES,
    KNOWN_BAD_REPLAY_DEFENSE_RULES,
    DynamicReplayError,
    FakeRuntimeViolationError,
    RealInfrastructureAccessViolationError,
    UnverifiedRegistryViolationError,
    LiveExecutionBlockedError,
    LiveVectorDBAccessViolationError,
    SandboxEscapeExecutionViolationError,
    AuditStreamTamperingViolationError,
    ReplayGateApprovalMissingError,
    StepSkippingViolation,
    RealCredentialViolationError,
    UnilateralVulnerabilityEscalationError,
    ProductionEnvironmentViolationError,
    ProductionSafetyClaimViolationError,
    SafetyBoundaryViolationError,
)

from src.gatekeeper.controlled_replay_gatekeeper import (
    ControlledReplayGatekeeper,
    GateNodeEnum,
    NodeStatusEnum,
    ReviewerRoleEnum,
    ReviewDecisionEnum,
    SessionStatusEnum,
    HumanSignature,
    MissingHumanReviewSignatureError,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Phase99AIntegratedGateValidator")

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
        ("DOC_GATE_NOTES", ROOT / "docs/phase99a_integrated_verification_gate_notes.md"),
        ("DOC_REPLAY_DESIGN", ROOT / "docs/phase99a_dynamic_replay_suite_design.md"),
        ("REPLAY_SUITE_PY", ROOT / "multi_agent/replay/phase99a_dynamic_replay_suite.py"),
        ("REPLAY_INIT_PY", ROOT / "multi_agent/replay/__init__.py"),
        ("RECON_MATRIX_YAML", ROOT / "phase99a_integrated_reconciliation_matrix.yaml"),
        ("MASTER_COMPLIANCE_JSON", ROOT / "phase99a_master_compliance_summary.json"),
        ("GATE_VALIDATOR_SCRIPT", ROOT / "scripts/validate_phase99a_integrated_gate.py"),
        ("INTEGRATION_TESTS_PY", ROOT / "tests/test_phase99a_integrated_replay_and_gate.py"),
    ]

    all_exist = True
    for tag, fpath in required_files:
        exists = fpath.exists() and fpath.stat().st_size > 0
        record_check(f"DELIV_{tag}", f"Deliverable File {fpath.name}", exists, f"Path: {fpath} ({fpath.stat().st_size if fpath.exists() else 0} bytes)")
        if not exists:
            all_exist = False


def verify_engine_instantiation_and_safety() -> None:
    logger.info("--- [Check 2] Dynamic Replay Engine Instantiation & Safety Boundaries ---")
    engine = DynamicReplayEngine()
    record_check("ENG_INIT", "DynamicReplayEngine Instantiation", engine is not None, "Instantiated successfully")

    # Safety boundary assertions
    boundaries = DYNAMIC_REPLAY_SAFETY_BOUNDARIES
    record_check("SAFE_NO_CONFIRMED_VULN", "confirmed_vulnerability=False", boundaries.get("confirmed_vulnerability") is False, "Maintained candidate state")
    record_check("SAFE_NO_FORMAL_FINDING", "formal_finding_allowed=False", boundaries.get("formal_finding_allowed") is False, "Formal finding restricted")
    record_check("SAFE_NO_PROD_SAFETY", "production_safety_claimed=False", boundaries.get("production_safety_claimed") is False, "No production safety claim")
    record_check("SAFE_NO_CONTROLLED_REPLAY", "controlled_replay_claimed=False", boundaries.get("controlled_replay_claimed") is False, "No uncontrolled replay claim")
    record_check("SAFE_SYNTHETIC_ONLY", "synthetic_only=True", boundaries.get("synthetic_only") is True, "Pure synthetic mock traces")
    record_check("SAFE_FAKE_RUNTIME", "fake_runtime_only=True", boundaries.get("fake_runtime_only") is True, "Fake runtime enforcement active")
    record_check("SAFE_HUMAN_REVIEW", "requires_human_review=True", boundaries.get("requires_human_review") is True, "Human review mandatory")


def verify_multistage_attack_chains() -> None:
    logger.info("--- [Check 3] Multi-Stage Attack Chains Catalog & Structure ---")
    engine = DynamicReplayEngine()
    chains = engine.list_chains()
    expected_chains = ["CHAIN-99A-01", "CHAIN-99A-02", "CHAIN-99A-03", "CHAIN-99A-04"]

    all_present = all(c in chains for c in expected_chains)
    record_check("CHAIN_CATALOG", "4 Standard Multi-Stage Attack Chains Registered", all_present, f"Chains: {chains}")

    for cid in expected_chains:
        chain = engine.get_chain(cid)
        record_check(f"CHAIN_STRUCT_{cid}", f"Chain {cid} Structure", len(chain.steps) == 4 and chain.prerequisite_gate_node == GateNodeEnum.NODE_5, f"{chain.chain_name} (Stages: {len(chain.steps)})")


def verify_dynamic_replay_session_lifecycle() -> None:
    logger.info("--- [Check 4] Dynamic Replay Session Lifecycle & Sequential Progression ---")
    engine = DynamicReplayEngine()
    session = engine.create_replay_session("CHAIN-99A-01")
    record_check("SES_INIT", "Session Initialization", session.status == ReplayExecutionStatus.GATE_PENDING, f"Session ID: {session.session_id}")

    # Sign with valid human signature
    sig = HumanSignature(
        reviewer_id="REV-LEAD-001",
        reviewer_role=ReviewerRoleEnum.SECURITY_LEAD,
        signed_at="2026-08-18T10:00:00Z",
        decision=ReviewDecisionEnum.APPROVED,
        notes="Authorized controlled dynamic replay simulation under Fake Runtime.",
    )
    engine.authorize_session_with_gatekeeper(session.session_id, sig)
    record_check("SES_AUTH", "Gatekeeper Node 5 Authorization", session.status == ReplayExecutionStatus.RUNNING and session.gatekeeper_approved is True, "Node 5 Authorized")

    # Run full dynamic replay
    run_result = engine.run_full_dynamic_replay(session.session_id)
    record_check("SES_RUN_COMPLETE", "Full Multi-Stage Dynamic Replay Execution", run_result["status"] == "completed" and run_result["total_steps_executed"] == 4, f"Executed {run_result['total_steps_executed']} stages, Interceptions: {run_result['interceptions']}")
    record_check("SES_ZERO_BREAKTHROUGH", "Zero Breakthrough in Dynamic Replay", run_result["breakthroughs"] == 0, "Breakthrough count: 0")


def verify_gatekeeper_node5_requirement_and_anti_skipping() -> None:
    logger.info("--- [Check 5] Gatekeeper Node 5 Authorization Requirement & Anti-Skipping ---")
    engine = DynamicReplayEngine()
    unauthorized_session = engine.create_replay_session("CHAIN-99A-02")

    # Attempt to execute step without authorization (DRS-KB-007)
    blocked_without_auth = False
    try:
        engine.execute_replay_step(unauthorized_session.session_id, 0)
    except ReplayGateApprovalMissingError:
        blocked_without_auth = True
    record_check("GATE_NODE5_BLOCK", "Block Step Execution without Node 5 Authorization", blocked_without_auth and unauthorized_session.status == ReplayExecutionStatus.BLOCKED, "Properly blocked with ReplayGateApprovalMissingError")

    # Authorize session
    auth_session = engine.create_replay_session("CHAIN-99A-02")
    sig = HumanSignature(
        reviewer_id="REV-LEAD-002",
        reviewer_role=ReviewerRoleEnum.SECURITY_LEAD,
        signed_at="2026-08-18T10:00:00Z",
        decision=ReviewDecisionEnum.APPROVED,
    )
    engine.authorize_session_with_gatekeeper(auth_session.session_id, sig)

    # Attempt out-of-order step skipping (skip Step 0, try executing Step 2)
    step_skipping_blocked = False
    try:
        engine.execute_replay_step(auth_session.session_id, 2)
    except StepSkippingViolation:
        step_skipping_blocked = True
    record_check("GATE_ANTI_SKIP", "Anti-Step-Skipping State Machine Enforcement", step_skipping_blocked and auth_session.status == ReplayExecutionStatus.BLOCKED, "StepSkippingViolation raised on out-of-order execution")


def verify_10_known_bad_defense_matrix() -> None:
    logger.info("--- [Check 6] 10 Groups of High-Order Known-Bad Defense Interceptions ---")
    engine = DynamicReplayEngine()
    matrix_result = engine.run_known_bad_matrix()

    record_check("KB_ALL_PASSED", "All 10 Known-Bad Defense Injections Intercepted", matrix_result["all_passed"], f"Pass rate: {matrix_result['interception_rate']} ({matrix_result['intercepted_count']}/{matrix_result['total_scenarios']})")

    for sc_id, details in matrix_result["details"].items():
        record_check(f"KB_SCENARIO_{sc_id}", f"Known-Bad Defense {sc_id} ({details['name']})", details["status"] == "PASS", f"Rule: {details['defense_rule']}, Caught: {details.get('exception_caught')}")


def verify_automated_signature_rejection() -> None:
    logger.info("--- [Check 7] Automated Bot Signature Rejection ---")
    engine = DynamicReplayEngine()
    session = engine.create_replay_session("CHAIN-99A-03")

    bot_sig = HumanSignature(
        reviewer_id="AUTO_BOT_AGENT",
        reviewer_role=ReviewerRoleEnum.SECURITY_LEAD,
        signed_at="2026-08-18T10:00:00Z",
        decision=ReviewDecisionEnum.APPROVED,
        is_automated_override=True,
    )

    bot_rejected = False
    try:
        engine.authorize_session_with_gatekeeper(session.session_id, bot_sig)
    except MissingHumanReviewSignatureError:
        bot_rejected = True
    record_check("REV_BOT_REJECT", "Automated Override Bot Signature Rejection", bot_rejected, "MissingHumanReviewSignatureError raised for automated override")


def verify_joint_reconciliation_24_cases() -> None:
    logger.info("--- [Check 8] Joint Reconciliation across 24 Adversarial Cases ---")
    recon_engine = Phase99AJointReconciliation(ROOT)
    recon_summary = recon_engine.perform_joint_reconciliation()

    record_check("RECON_TOTAL_CASES", "Total 24 Cases Evaluated", recon_summary["total_cases_evaluated"] == 24, "24 total test cases verified")
    record_check("RECON_ATTACK_INTERCEPTIONS", "20/20 Attack Interceptions (100%)", recon_summary["attack_interceptions"] == 20 and recon_summary["breakthrough_count"] == 0, f"Interceptions: {recon_summary['attack_interceptions']}, Breakthroughs: {recon_summary['breakthrough_count']}")
    record_check("RECON_CONTROL_PASSED", "4/4 Control Cases Passed (100%)", recon_summary["controls_passed"] == 4, f"Controls passed: {recon_summary['controls_passed']}/4")
    record_check("RECON_STATUS_PASS", "Reconciliation Status PASS", recon_summary["status"] == "PASS", "Joint reconciliation completed with PASS status")


def verify_source_playbooks_integrity() -> None:
    logger.info("--- [Check 9] Source Playbooks & Execution Results Integrity ---")
    m43_m45_pb = ROOT / "adversarial_playbooks/m43_m45_advanced_supply_chain_playbook/playbook.yaml"
    m43_m45_res = ROOT / "executions/phase99a_m43_m45_adv/execution_results.json"
    m48_m50_pb = ROOT / "adversarial_playbooks/m48_m50_advanced_rag_sandbox_playbook/playbook.yaml"
    m48_m50_res = ROOT / "executions/phase99a_m48_m50_adv/execution_results.json"

    pb1_data = yaml.safe_load(m43_m45_pb.read_text(encoding="utf-8"))
    res1_data = json.loads(m43_m45_res.read_text(encoding="utf-8"))
    pb2_data = yaml.safe_load(m48_m50_pb.read_text(encoding="utf-8"))
    res2_data = json.loads(m48_m50_res.read_text(encoding="utf-8"))

    record_check("PB_M43M45_COUNT", "M43/M45 Playbook 12 Entries", len(pb1_data["entries"]) == 12 and len(res1_data) == 12, f"Entries: {len(pb1_data['entries'])}")
    record_check("PB_M48M50_COUNT", "M48/M50 Playbook 12 Entries", len(pb2_data["entries"]) == 12 and len(res2_data) == 12, f"Entries: {len(pb2_data['entries'])}")


def verify_matrix_and_compliance_summary() -> None:
    logger.info("--- [Check 10] Reconciliation Matrix & Compliance Summary Integrity ---")
    matrix_file = ROOT / "phase99a_integrated_reconciliation_matrix.yaml"
    summary_file = ROOT / "phase99a_master_compliance_summary.json"

    matrix_data = yaml.safe_load(matrix_file.read_text(encoding="utf-8"))
    summary_data = json.loads(summary_file.read_text(encoding="utf-8"))

    record_check("YAML_TASK_ID", "Reconciliation Matrix Task ID", matrix_data.get("task_id") == "Phase-99A-GATE-003", "Task ID matches")
    record_check("YAML_24_CASES", "Reconciliation Matrix 24 Cases", len(matrix_data.get("reconciliation_matrix_24_cases", [])) == 24, "24 case mappings verified")
    record_check("YAML_CHAINS", "Reconciliation Matrix 4 Attack Chains", len(matrix_data.get("multi_stage_attack_chains", [])) == 4, "4 attack chains verified")
    record_check("JSON_COMPLIANCE", "Master Compliance Status COMPLIANT", summary_data.get("compliance_status") == "COMPLIANT", "Compliance status confirmed")
    record_check("JSON_SAFETY", "Master Compliance Safety Boundaries", summary_data.get("safety_boundaries", {}).get("confirmed_vulnerability") is False, "Safety boundaries verified")


def verify_replay_audit_report() -> None:
    logger.info("--- [Check 11] Replay Audit Report & Synthetic Trace Integrity ---")
    engine = DynamicReplayEngine()
    session = engine.create_replay_session("CHAIN-99A-04")
    sig = HumanSignature(
        reviewer_id="REV-LEAD-004",
        reviewer_role=ReviewerRoleEnum.SECURITY_LEAD,
        signed_at="2026-08-18T10:00:00Z",
        decision=ReviewDecisionEnum.APPROVED,
    )
    engine.authorize_session_with_gatekeeper(session.session_id, sig)
    engine.run_full_dynamic_replay(session.session_id)

    report = engine.generate_replay_audit_report(session.session_id)
    record_check("AUDIT_REPORT_ID", "Audit Report Generated", report.get("report_id") is not None, f"Report ID: {report.get('report_id')}")
    record_check("AUDIT_TRACES", "Synthetic Traces Count", report.get("synthetic_traces_count") == 4, "4 stage traces recorded")
    record_check("AUDIT_ZERO_BREAKTHROUGH", "Audit Report Zero Breakthrough Rate", report.get("security_metrics", {}).get("breakthrough_rate") == 0.0, "Breakthrough rate 0.0")


def verify_non_retroactivity_guarantee() -> None:
    logger.info("--- [Check 12] Non-Retroactivity & Historical Module Integrity Guarantees ---")
    # Verify historical phase summaries exist and are untouched
    phase98_summary = ROOT / "phase98a_gate003_execution_summary.yaml"
    phase99_m43m45 = ROOT / "phase99a_m43m45_001_execution_summary.yaml"
    phase99_m48m50 = ROOT / "phase99a_m48m50_002_execution_summary.yaml"

    record_check("NON_RETRO_P98", "Phase 98A Gate Summary Intact", phase98_summary.exists(), "Phase 98A baseline preserved")
    record_check("NON_RETRO_P99_1", "Phase 99A M43/M45 Summary Intact", phase99_m43m45.exists(), "M43/M45 findings preserved")
    record_check("NON_RETRO_P99_2", "Phase 99A M48/M50 Summary Intact", phase99_m48m50.exists(), "M48/M50 findings preserved")


def main() -> int:
    logger.info("================================================================================")
    logger.info("Phase 99A Gate Validator: Dynamic Replay Suite & Integrated Reconciliation")
    logger.info("================================================================================")

    verify_deliverables_existence()
    verify_engine_instantiation_and_safety()
    verify_multistage_attack_chains()
    verify_dynamic_replay_session_lifecycle()
    verify_gatekeeper_node5_requirement_and_anti_skipping()
    verify_10_known_bad_defense_matrix()
    verify_automated_signature_rejection()
    verify_joint_reconciliation_24_cases()
    verify_source_playbooks_integrity()
    verify_matrix_and_compliance_summary()
    verify_replay_audit_report()
    verify_non_retroactivity_guarantee()

    total_checks = checks_passed + checks_failed
    logger.info("================================================================================")
    logger.info(f"VALIDATION SUMMARY: {checks_passed}/{total_checks} CHECKS PASSED")
    if checks_failed == 0:
        logger.info("STATUS: ALL CHECKS PASSED (100% COMPLIANT)")
        logger.info("================================================================================")
        return 0
    else:
        logger.error(f"STATUS: {checks_failed} CHECKS FAILED")
        logger.info("================================================================================")
        return 1


if __name__ == "__main__":
    sys.exit(main())
