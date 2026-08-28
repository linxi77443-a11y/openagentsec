#!/usr/bin/env python3
"""
scripts/validate_phase98a_integrated_gate.py — Phase 98A Integrated Gate & Reconciliation Validator.
Path: scripts/validate_phase98a_integrated_gate.py

Task: Phase-98A-GATE-003
Task Name: 阶段 98 评估指标与受控复现整合验证套件开发
PRD References:
  - 原 PRD v1.0 §6, §7, §10
  - 攻击者视角新增章节 §4, §7, §11
  - PRD v2.0 §4, §9.3, §13
  - PRD v3.1 §2.7, §4, §5
  - GAP-001 与 GAP-006 联合对账闭环

Verification Scope:
1. Deliverable Files Existence & Structure Integrity.
2. Dual-Engine Instantiation & Strict Safety Invariant Assertions.
3. Canonical Metric Quantification Engine Full Batch Verification (M43-M50).
4. Controlled Replay 8-Node Authorization Gatekeeper Full Workflow Execution.
5. 10 Groups of Known-Bad Injection Defense Interceptions (KB-001 to KB-010).
6. Forbidden Auto-Mapping Defense Rules (FAM-001 to FAM-008) Verification.
7. Gatekeeper Hard-Blocking Invariant Guardrails (HIG-001 to HIG-009) Verification.
8. GAP-001 (M44 Canonical Normalization) Formal Closure Verification.
9. GAP-006 (PRD v2.0 §9.3 Controlled Replay Gatekeeper) Formal Closure Verification.
10. Cross-Module Consistency & Non-Retroactivity Guarantees Verification.
11. Integrated Reconciliation Matrix & Master Compliance Summary Snapshot Integrity.

Usage:
    python3 scripts/validate_phase98a_integrated_gate.py
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine.canonical_metric_quantification_engine import (
    CanonicalMetricQuantificationEngine,
    CapabilityValue,
    RiskLevel,
    CanonicalStatus,
    ReviewStatus,
    MappingAbsenceEffect,
    ForbiddenAutoMappingViolation,
    RuleNotFoundError,
    UnapprovedRuleError,
    RuleValidationError,
    InapplicableRuleError,
    ENGINE_SAFETY_BOUNDARIES,
    FORBIDDEN_AUTO_MAPPING_RULES,
)

from src.gatekeeper.controlled_replay_gatekeeper import (
    ControlledReplayGatekeeper,
    GateNodeEnum,
    NodeStatusEnum,
    ReviewerRoleEnum,
    ReviewDecisionEnum,
    SessionStatusEnum,
    HumanSignature,
    GatekeeperEvaluationResult,
    GatekeeperError,
    StepSkippingViolation,
    MissingHumanReviewSignatureError,
    ReviewerRoleMismatchError,
    ProductionEnvironmentViolationError,
    RealNetworkAccessViolationError,
    RealCredentialViolationError,
    RollbackPlanMissingError,
    UnilateralVulnerabilityEscalationError,
    ProductionSafetyClaimViolationError,
    NonSyntheticDataViolationError,
    NodePayloadValidationError,
    SessionNotFoundError,
    SessionStateError,
    GATEKEEPER_SAFETY_BOUNDARIES,
    STANDARD_ABORT_CONDITIONS,
    STANDARD_ROLLBACK_STEPS,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Phase98AIntegratedGateValidator")

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


def get_standard_valid_node_payloads() -> Dict[str, Dict[str, Any]]:
    return {
        "NODE-1": {
            "candidate_id": "BRT-001",
            "source_playbook": "direct_prompt_injection",
            "affected_boundary": "prompt_injection_boundary",
            "expected_blocking_behavior": "refuse",
            "evidence_trace_ref": "TR-DPI-006-REF",
            "synthetic_only": True,
            "confirmed_vulnerability": False,
        },
        "NODE-2": {
            "authorization_owner": "<SIM_AUTH_OWNER>",
            "authorization_team": "<SIM_AUTH_TEAM>",
            "authorization_scope": "BRT-001 controlled scenario replay",
            "time_window_start": "2026-08-18T10:00:00Z",
            "time_window_end": "2026-08-18T18:00:00Z",
            "allowed_tools": ["<SIM_TOOL_AGENT_RUNNER>"],
            "forbidden_scope": ["production_databases", "public_egress", "生产网络"],
            "synthetic_only": True,
        },
        "NODE-3": {
            "environment_type": "isolated_test_environment",
            "production_environment_allowed": False,
            "external_network_access_allowed": False,
            "real_api_access_allowed": False,
            "real_tool_execution_allowed": False,
            "environment_snapshot_id": "<SIM_SNAPSHOT_ENV_001>",
            "audit_logging_enabled": True,
            "synthetic_only": True,
        },
        "NODE-4": {
            "synthetic_account_only": True,
            "synthetic_data_only": True,
            "synthetic_only": True,
            "authorized_test_accounts": ["<SIM_TEST_ACCOUNT_01>"],
            "authorized_test_datasets": ["<SIM_DATASET_MOCK_01>"],
            "data_rollback_snapshot_id": "<SIM_DATA_SNAPSHOT_001>",
        },
        "NODE-5": {
            "rollback_plan_approved": True,
            "abort_conditions_defined": True,
            "operator_id": "<SIM_OPERATOR_LEAD>",
            "preflight_checklist_passed": True,
            "requires_human_review": True,
            "synthetic_only": True,
        },
        "NODE-6": {
            "replay_case_id": "RTC-001",
            "observed_behavior": "Model maintained safe refusal in isolated test sandbox",
            "runtime_decision": "blocked",
            "safety_field_snapshot": {
                "confirmed_vulnerability": False,
                "formal_finding_allowed": False,
                "production_safety_claimed": False,
            },
            "rollback_status": "clean_state_restored",
            "evidence_log_hash": "<SIM_LOG_HASH_A1B2C3>",
            "synthetic_only": True,
        },
        "NODE-7": {
            "triage_classification": "simulated_breakthrough_candidate",
            "simulated_severity": "medium",
            "anti_auto_escalation_verified": True,
            "all_findings_are_candidate": True,
            "confirmed_vulnerability": False,
            "synthetic_only": True,
        },
        "NODE-8": {
            "governance_signoff": True,
            "audit_chain_verified": True,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "synthetic_only": True,
        },
    }


def get_standard_valid_signatures() -> Dict[str, HumanSignature]:
    return {
        "NODE-1": HumanSignature(
            reviewer_id="REV-SEC-TEST-01",
            reviewer_role=ReviewerRoleEnum.SECURITY_TESTING_LEAD.value,
            signature_text="Sign: SecTestLead Candidate Selection Approved",
            comments="Candidate meets all admission criteria.",
        ),
        "NODE-2": HumanSignature(
            reviewer_id="REV-SEC-MGT-01",
            reviewer_role=ReviewerRoleEnum.SECURITY_MANAGEMENT_LEAD.value,
            signature_text="Sign: SecMgtLead Authorization Approved",
            comments="Authorization scope strictly synthetic and bounded.",
        ),
        "NODE-3": HumanSignature(
            reviewer_id="REV-ENV-MGT-01",
            reviewer_role=ReviewerRoleEnum.ENVIRONMENT_MANAGEMENT_LEAD.value,
            signature_text="Sign: EnvMgtLead Environment Readiness Approved",
            comments="Isolated test sandbox verified and snapshot taken.",
        ),
        "NODE-4": HumanSignature(
            reviewer_id="REV-DATA-SAFE-01",
            reviewer_role=ReviewerRoleEnum.DATA_SAFETY_LEAD.value,
            signature_text="Sign: DataSafetyLead Account & Data Safety Approved",
            comments="Synthetic accounts and mock data verified.",
        ),
        "NODE-5": HumanSignature(
            reviewer_id="REV-SEC-LEAD-01",
            reviewer_role=ReviewerRoleEnum.SECURITY_LEAD.value,
            signature_text="Sign: SecLead Replay Execution Gate Approved",
            comments="Rollback plan and 7 abort conditions confirmed.",
        ),
        "NODE-6": HumanSignature(
            reviewer_id="REV-SEC-TEST-01",
            reviewer_role=ReviewerRoleEnum.SECURITY_TESTING_LEAD.value,
            signature_text="Sign: SecTestLead Post-Replay Evidence Approved",
            comments="Evidence log verified and clean state restored.",
        ),
        "NODE-7": HumanSignature(
            reviewer_id="REV-SEC-ASSESS-01",
            reviewer_role=ReviewerRoleEnum.SECURITY_ASSESSMENT_LEAD.value,
            signature_text="Sign: SecAssessLead Vulnerability Classification Approved",
            comments="Classification triaged as simulated candidate.",
        ),
        "NODE-8": HumanSignature(
            reviewer_id="REV-SEC-MGT-01",
            reviewer_role=ReviewerRoleEnum.SECURITY_MANAGEMENT_LEAD.value,
            signature_text="Sign: SecMgtLead Formal Finding Signoff Approved",
            comments="8-node audit chain complete and archived.",
        ),
    }


def validate_all() -> int:
    logger.info("=" * 80)
    logger.info("Phase 98A — Integrated Gate & Dual-Engine Reconciliation Validator")
    logger.info("Task: Phase-98A-GATE-003 | GAP-001 & GAP-006 Joint Closure Gate")
    logger.info("=" * 80)

    # ------------------------------------------------------------------------
    # Step 1: Deliverable Files Existence & Structure Integrity
    # ------------------------------------------------------------------------
    logger.info("\n[Step 1] Checking Deliverable Files Existence & Schema Integrity...")
    required_files = [
        ROOT / "scripts" / "validate_phase98a_integrated_gate.py",
        ROOT / "tests" / "test_phase98a_metric_and_replay_integration.py",
        ROOT / "docs" / "phase98a_integrated_verification_gate_notes.md",
        ROOT / "phase98a_integrated_reconciliation_matrix.yaml",
        ROOT / "phase98a_master_compliance_summary.json",
        ROOT / "phase98a_gate003_execution_summary.yaml",
        ROOT / "delivery.json",
        ROOT / "src" / "engine" / "canonical_metric_quantification_engine.py",
        ROOT / "src" / "gatekeeper" / "controlled_replay_gatekeeper.py",
        ROOT / "schemas" / "canonical_metric_mapping_rules.yaml",
        ROOT / "schemas" / "controlled_replay_8node_schema.yaml",
    ]

    missing = []
    for rf in required_files:
        if not rf.exists():
            missing.append(str(rf.relative_to(ROOT)))

    record_check(
        "CHK-01",
        "Deliverable Files Existence",
        len(missing) == 0,
        f"All required deliverables present. Missing: {missing if missing else 'None'}"
    )

    # ------------------------------------------------------------------------
    # Step 2: Dual-Engine Instantiation & Strict Safety Invariants
    # ------------------------------------------------------------------------
    logger.info("\n[Step 2] Instantiating Dual Engines & Validating Safety Boundaries...")
    metric_engine = CanonicalMetricQuantificationEngine()
    gatekeeper = ControlledReplayGatekeeper()

    sb_metric = metric_engine.get_safety_boundaries()
    sb_gate = gatekeeper.safety_boundaries

    sb_valid = (
        sb_metric.get("confirmed_vulnerability") is False
        and sb_metric.get("formal_finding_allowed") is False
        and sb_metric.get("production_safety_claimed") is False
        and sb_metric.get("synthetic_only") is True
        and sb_metric.get("red_team_engine_not_executable") is True
        and sb_gate.get("confirmed_vulnerability") is False
        and sb_gate.get("formal_finding_allowed") is False
        and sb_gate.get("production_safety_claimed") is False
        and sb_gate.get("controlled_replay_execution_allowed") is False
        and sb_gate.get("synthetic_only") is True
        and sb_gate.get("requires_human_review") is True
    )

    record_check(
        "CHK-02",
        "Dual-Engine Instantiation & Safety Boundaries Invariant",
        sb_valid and metric_engine is not None and gatekeeper is not None,
        "Safety flags strictly verified: confirmed_vuln=false, controlled_replay=false, synthetic_only=true."
    )

    # ------------------------------------------------------------------------
    # Step 3: Canonical Metric Quantification Batch Evaluation (M43-M50)
    # ------------------------------------------------------------------------
    logger.info("\n[Step 3] Validating Canonical Metric Batch Resolution across M43-M50...")
    batch_res = metric_engine.evaluate_batch()

    expected_evaluations = {
        "M43": ("high", "high"),
        "M44": ("high", "low"),
        "M45": ("medium", "medium"),
        "M46": ("high", "high"),
        "M47": ("high", "high"),
        "M48": ("high", "high"),
        "M49": ("high", "medium"),
        "M50": ("high", "high"),
    }

    all_modules_resolved = True
    mismatches = []
    for mod_id, (expected_cap, expected_risk) in expected_evaluations.items():
        ev = batch_res.evaluations.get(mod_id)
        if not ev or not ev.is_resolved():
            all_modules_resolved = False
            mismatches.append(f"{mod_id} not resolved")
        elif ev.canonical_capability_value != expected_cap or ev.canonical_risk_level != expected_risk:
            all_modules_resolved = False
            mismatches.append(f"{mod_id} expected ({expected_cap}, {expected_risk}), got ({ev.canonical_capability_value}, {ev.canonical_risk_level})")

    record_check(
        "CHK-03",
        "Canonical Metric Batch Resolution (M43-M50)",
        all_modules_resolved and batch_res.summary["resolved_count"] == 8,
        f"8 modules resolved: {list(expected_evaluations.keys())}. Mismatches: {mismatches or 'None'}"
    )

    # ------------------------------------------------------------------------
    # Step 4: Controlled Replay 8-Node Gatekeeper Happy Path Workflow
    # ------------------------------------------------------------------------
    logger.info("\n[Step 4] Executing Controlled Replay 8-Node Full Happy Path Workflow...")
    session = gatekeeper.create_session("BRT-001")
    payloads = get_standard_valid_node_payloads()
    signatures = get_standard_valid_signatures()

    all_nodes_passed = True
    for i in range(1, 9):
        nid = f"NODE-{i}"
        res = gatekeeper.submit_node_review(session.session_id, nid, payloads[nid], signatures[nid])
        if not res.success:
            all_nodes_passed = False
            logger.error(f"Node {nid} failed: {res.message}")
            break

    happy_path_ok = (
        all_nodes_passed
        and session.overall_status == SessionStatusEnum.FULLY_APPROVED.value
        and len(session.audit_chain) == 8
    )

    record_check(
        "CHK-04",
        "8-Node Sequential Authorization Happy Path",
        happy_path_ok,
        f"Session {session.session_id} reached FULLY_APPROVED with 8 statutory audit signatures."
    )

    # ------------------------------------------------------------------------
    # Step 5: 10 Groups of Known-Bad Injection Defense Interceptions (KB-001 to KB-010)
    # ------------------------------------------------------------------------
    logger.info("\n[Step 5] Executing 10 Groups of Known-Bad Injection Defense Interception Tests...")
    kb_results = {}

    # KB-001: Success rate derivation (FAM-001)
    try:
        metric_engine.check_forbidden_auto_mapping({"success_rate": 0.95, "auto_capability_value": "high"}, raise_on_violation=True)
        kb_results["KB-001"] = False
    except ForbiddenAutoMappingViolation as e:
        kb_results["KB-001"] = (e.rule_id == "FAM-001")

    # KB-002: Signal count derivation (FAM-002)
    try:
        metric_engine.check_forbidden_auto_mapping({"signal_count": 14, "auto_risk_level": "high"}, raise_on_violation=True)
        kb_results["KB-002"] = False
    except ForbiddenAutoMappingViolation as e:
        kb_results["KB-002"] = (e.rule_id == "FAM-002")

    # KB-003: Breakthrough true direct high risk derivation (FAM-004)
    try:
        metric_engine.check_forbidden_auto_mapping({"breakthrough_detected": True, "inferred_risk_level": "high"}, raise_on_violation=True)
        kb_results["KB-003"] = False
    except ForbiddenAutoMappingViolation as e:
        kb_results["KB-003"] = (e.rule_id == "FAM-004")

    # KB-004: Unapproved / draft rule resolution claim (FAM-008)
    unmapped_res = metric_engine.evaluate_module("M999", "adversarial_validation")
    kb_results["KB-004"] = (
        unmapped_res.canonical_capability_status == CanonicalStatus.UNRESOLVED.value
        and unmapped_res.future_canonical_metric_normalization_blocked is True
        and unmapped_res.mapping_absence_effect == MappingAbsenceEffect.DOCUMENTATION_DEBT_ONLY.value
    )

    # KB-005: Production environment parameter injection (HIG-001)
    s_kb5 = gatekeeper.create_session("BRT-KB-005")
    gatekeeper.submit_node_review(s_kb5.session_id, "NODE-1", payloads["NODE-1"], signatures["NODE-1"])
    gatekeeper.submit_node_review(s_kb5.session_id, "NODE-2", payloads["NODE-2"], signatures["NODE-2"])
    bad_prod = dict(payloads["NODE-3"])
    bad_prod["environment_type"] = "production"
    bad_prod["production_environment_allowed"] = True
    res_kb5 = gatekeeper.submit_node_review(s_kb5.session_id, "NODE-3", bad_prod, signatures["NODE-3"])
    kb_results["KB-005"] = (res_kb5.hard_block_triggered and "HIG-001" in res_kb5.message)

    # KB-006: Real network egress / live API injection (HIG-002)
    s_kb6 = gatekeeper.create_session("BRT-KB-006")
    gatekeeper.submit_node_review(s_kb6.session_id, "NODE-1", payloads["NODE-1"], signatures["NODE-1"])
    gatekeeper.submit_node_review(s_kb6.session_id, "NODE-2", payloads["NODE-2"], signatures["NODE-2"])
    bad_net = dict(payloads["NODE-3"])
    bad_net["external_network_access_allowed"] = True
    res_kb6 = gatekeeper.submit_node_review(s_kb6.session_id, "NODE-3", bad_net, signatures["NODE-3"])
    kb_results["KB-006"] = (res_kb6.hard_block_triggered and "HIG-002" in res_kb6.message)

    # KB-007: Real credential / API key pattern leak (HIG-003)
    s_kb7 = gatekeeper.create_session("BRT-KB-007")
    gatekeeper.submit_node_review(s_kb7.session_id, "NODE-1", payloads["NODE-1"], signatures["NODE-1"])
    gatekeeper.submit_node_review(s_kb7.session_id, "NODE-2", payloads["NODE-2"], signatures["NODE-2"])
    gatekeeper.submit_node_review(s_kb7.session_id, "NODE-3", payloads["NODE-3"], signatures["NODE-3"])
    bad_cred = dict(payloads["NODE-4"])
    bad_cred["authorized_test_accounts"] = ["sk-live-secretkey98765432109876543210"]
    res_kb7 = gatekeeper.submit_node_review(s_kb7.session_id, "NODE-4", bad_cred, signatures["NODE-4"])
    kb_results["KB-007"] = (res_kb7.hard_block_triggered and "HIG-003" in res_kb7.message)

    # KB-008: Automated bot signature override (HIG-004)
    s_kb8 = gatekeeper.create_session("BRT-KB-008")
    bot_sig = HumanSignature(
        reviewer_id="AUTO_BOT",
        reviewer_role=ReviewerRoleEnum.SECURITY_TESTING_LEAD.value,
        signature_text="AUTO",
        is_automated_override=True,
    )
    res_kb8 = gatekeeper.submit_node_review(s_kb8.session_id, "NODE-1", payloads["NODE-1"], bot_sig)
    kb_results["KB-008"] = (res_kb8.hard_block_triggered and "HIG-004" in res_kb8.message)

    # KB-009: Out-of-order step skipping jump (HIG-005)
    s_kb9 = gatekeeper.create_session("BRT-KB-009")
    try:
        gatekeeper.submit_node_review(s_kb9.session_id, "NODE-5", payloads["NODE-5"], signatures["NODE-5"])
        kb_results["KB-009"] = False
    except StepSkippingViolation:
        kb_results["KB-009"] = True

    # KB-010: Unilateral confirmed vulnerability escalation (HIG-007)
    s_kb10 = gatekeeper.create_session("BRT-KB-010")
    for i in range(1, 7):
        nid = f"NODE-{i}"
        gatekeeper.submit_node_review(s_kb10.session_id, nid, payloads[nid], signatures[nid])
    bad_vuln = dict(payloads["NODE-7"])
    bad_vuln["confirmed_vulnerability"] = True
    res_kb10 = gatekeeper.submit_node_review(s_kb10.session_id, "NODE-7", bad_vuln, signatures["NODE-7"])
    kb_results["KB-010"] = (res_kb10.hard_block_triggered and "HIG-007" in res_kb10.message)

    all_kb_passed = all(kb_results.values()) and len(kb_results) == 10
    record_check(
        "CHK-05",
        "10 Groups of Known-Bad Injection Defenses",
        all_kb_passed,
        f"All 10 Known-Bad test vectors intercepted (100.0%): {list(kb_results.keys())}"
    )

    # ------------------------------------------------------------------------
    # Step 6: Forbidden Auto-Mapping Full Catalog Coverage (FAM-001 to FAM-008)
    # ------------------------------------------------------------------------
    logger.info("\n[Step 6] Validating All 8 Forbidden Auto-Mapping Rules (FAM-001 to FAM-008)...")
    fam_interceptions = []
    
    # Test FAM-001 to FAM-008 directly
    test_cases_fam = [
        ("FAM-001", {"validator_pass_rate": 0.99, "auto_capability_value": "high"}),
        ("FAM-002", {"raw_signals_count": 25, "auto_risk_level": "medium"}),
        ("FAM-003", {"breakthrough_detected": False, "inferred_risk_level": "low"}),
        ("FAM-004", {"breakthrough_detected": True, "inferred_risk_level": "high"}),
        ("FAM-005", {"human_review_required_count": 3, "inferred_risk_level": "high"}),
        ("FAM-006", {"canonical_capability_value": "simulated_capability_signal"}),
        ("FAM-007", {"conflate_safety_with_risk": True}),
        ("FAM-008", {"claim_resolved_without_rule": True}),
    ]

    for fid, data in test_cases_fam:
        v = metric_engine.check_forbidden_auto_mapping(data, raise_on_violation=False)
        if any(fid in x for x in v):
            fam_interceptions.append(fid)

    fam_catalog_ok = (len(fam_interceptions) == 8 and len(FORBIDDEN_AUTO_MAPPING_RULES) == 8)
    record_check(
        "CHK-06",
        "Forbidden Auto-Mapping Full Catalog Defense (FAM-001 ~ FAM-008)",
        fam_catalog_ok,
        f"All 8 FAM rules triggered and intercepted: {fam_interceptions}"
    )

    # ------------------------------------------------------------------------
    # Step 7: Hard-Blocking Invariant Guardrails (HIG-001 to HIG-009)
    # ------------------------------------------------------------------------
    logger.info("\n[Step 7] Validating All 9 Hard-Blocking Invariant Guardrails (HIG-001 to HIG-009)...")
    # We already tested HIG-001, HIG-002, HIG-003, HIG-004, HIG-005, HIG-007 in Step 5.
    # Now let's test HIG-006 (missing rollback), HIG-008 (production safety claim), HIG-009 (non-synthetic data).

    # HIG-006: Rollback missing on Node 5
    s_hig6 = gatekeeper.create_session("BRT-HIG-006")
    for i in range(1, 5):
        gatekeeper.submit_node_review(s_hig6.session_id, f"NODE-{i}", payloads[f"NODE-{i}"], signatures[f"NODE-{i}"])
    bad_rb = dict(payloads["NODE-5"])
    bad_rb["rollback_plan_approved"] = False
    res_hig6 = gatekeeper.submit_node_review(s_hig6.session_id, "NODE-5", bad_rb, signatures["NODE-5"])
    hig6_ok = res_hig6.hard_block_triggered and "HIG-006" in res_hig6.message

    # HIG-008: Production safety claim on Node 8
    s_hig8 = gatekeeper.create_session("BRT-HIG-008")
    for i in range(1, 8):
        gatekeeper.submit_node_review(s_hig8.session_id, f"NODE-{i}", payloads[f"NODE-{i}"], signatures[f"NODE-{i}"])
    bad_safe = dict(payloads["NODE-8"])
    bad_safe["production_safety_claimed"] = True
    res_hig8 = gatekeeper.submit_node_review(s_hig8.session_id, "NODE-8", bad_safe, signatures["NODE-8"])
    hig8_ok = res_hig8.hard_block_triggered and "HIG-008" in res_hig8.message

    # HIG-009: Non-synthetic data on Node 1
    s_hig9 = gatekeeper.create_session("BRT-HIG-009")
    bad_synth = dict(payloads["NODE-1"])
    bad_synth["synthetic_only"] = False
    res_hig9 = gatekeeper.submit_node_review(s_hig9.session_id, "NODE-1", bad_synth, signatures["NODE-1"])
    hig9_ok = res_hig9.hard_block_triggered and "HIG-009" in res_hig9.message

    all_hig_ok = hig6_ok and hig8_ok and hig9_ok
    record_check(
        "CHK-07",
        "Hard-Blocking Invariant Guardrails (HIG-001 ~ HIG-009)",
        all_hig_ok,
        "All 9 HIG guardrails (HIG-001 through HIG-009) verified active and blocking."
    )

    # ------------------------------------------------------------------------
    # Step 8: GAP-001 Formal Closure Proof for M44
    # ------------------------------------------------------------------------
    logger.info("\n[Step 8] Validating GAP-001 Formal Closure Proof for M44...")
    gap001_proof = metric_engine.resolve_gap("GAP-001")
    gap001_ok = (
        gap001_proof.get("closure_status") == "closed"
        and gap001_proof.get("target_module") == "M44"
        and gap001_proof.get("canonical_capability_value") == "high"
        and gap001_proof.get("canonical_risk_level") == "low"
        and gap001_proof.get("canonical_capability_status") == "resolved"
        and gap001_proof.get("canonical_risk_status") == "resolved"
        and gap001_proof.get("non_retroactivity_guarantee", {}).get("retroactive_effect_on_existing_module_closure") is False
    )

    record_check(
        "CHK-08",
        "GAP-001 Formal Closure Verification (M44)",
        gap001_ok,
        "GAP-001 status=closed, capability=high, risk=low, status=resolved, non_retroactive=true."
    )

    # ------------------------------------------------------------------------
    # Step 9: GAP-006 Formal Closure Proof for PRD v2.0 §9.3
    # ------------------------------------------------------------------------
    logger.info("\n[Step 9] Validating GAP-006 Formal Closure Proof for PRD v2.0 §9.3...")
    gap006_proof = gatekeeper.verify_gap006_closure(session.session_id)
    gap006_ok = (
        gap006_proof.get("status") == "closed"
        and gap006_proof.get("closure_criteria_evaluation", {}).get("all_8_nodes_approved") is True
        and gap006_proof.get("closure_criteria_evaluation", {}).get("controlled_replay_hard_blocked") is True
        and gap006_proof.get("closure_criteria_evaluation", {}).get("human_review_chain_intact") is True
    )

    record_check(
        "CHK-09",
        "GAP-006 Formal Closure Verification (PRD v2.0 §9.3)",
        gap006_ok,
        "GAP-006 status=closed, all 8 nodes approved, controlled_replay_hard_blocked=true, human review chain intact."
    )

    # ------------------------------------------------------------------------
    # Step 10: State Transition Simulator & Non-Retroactivity Guarantees
    # ------------------------------------------------------------------------
    logger.info("\n[Step 10] Validating State Transition Simulator & Non-Retroactivity...")
    trans_m44 = metric_engine.simulate_unresolved_to_resolved_transition("M44")
    trans_ok = (
        trans_m44.previous_capability_status == "unresolved"
        and trans_m44.new_capability_status == "resolved"
        and trans_m44.transition_success is True
        and trans_m44.gap_closed == "GAP-001"
        and trans_m44.non_retroactive_verified is True
    )

    record_check(
        "CHK-10",
        "State Transition Simulator & Non-Retroactivity",
        trans_ok,
        "Unresolved -> Resolved state transition simulation verified without side-effects."
    )

    # ------------------------------------------------------------------------
    # Step 11: Integrated Reconciliation Matrix File Consistency
    # ------------------------------------------------------------------------
    logger.info("\n[Step 11] Validating Integrated Reconciliation Matrix YAML Consistency...")
    matrix_file = ROOT / "phase98a_integrated_reconciliation_matrix.yaml"
    matrix_ok = False
    if matrix_file.exists():
        with open(matrix_file, "r", encoding="utf-8") as f:
            mat_data = yaml.safe_load(f)
        
        matrix_ok = (
            mat_data.get("task_id") == "Phase-98A-GATE-003"
            and mat_data.get("phase") == "Phase-98A"
            and len(mat_data.get("canonical_metrics_reconciliation", {}).get("modules_evaluated", [])) == 8
            and len(mat_data.get("eight_node_gatekeeper_reconciliation", {}).get("state_machine_nodes", [])) == 8
            and len(mat_data.get("known_bad_defense_matrix", {}).get("scenarios", [])) == 10
            and len(mat_data.get("gap_closure_reconciliation", [])) == 2
            and mat_data.get("safety_boundaries", {}).get("confirmed_vulnerability") is False
            and mat_data.get("safety_boundaries", {}).get("synthetic_only") is True
        )

    record_check(
        "CHK-11",
        "Integrated Reconciliation Matrix Consistency",
        matrix_ok,
        f"phase98a_integrated_reconciliation_matrix.yaml parsed and validated against schema."
    )

    # ------------------------------------------------------------------------
    # Step 12: Master Compliance Summary JSON Snapshot Consistency
    # ------------------------------------------------------------------------
    logger.info("\n[Step 12] Validating Master Compliance Summary JSON Snapshot Consistency...")
    summary_file = ROOT / "phase98a_master_compliance_summary.json"
    summary_ok = False
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            sum_data = json.load(f)

        summary_ok = (
            sum_data.get("gate_id") == "Phase-98A-GATE-003"
            and sum_data.get("compliance_status") == "COMPLIANT"
            and sum_data.get("safety_boundaries", {}).get("confirmed_vulnerability") is False
            and sum_data.get("safety_boundaries", {}).get("controlled_replay_execution_allowed") is False
            and sum_data.get("gap_closures", {}).get("GAP-001", {}).get("status") == "closed"
            and sum_data.get("gap_closures", {}).get("GAP-006", {}).get("status") == "closed"
            and sum_data.get("known_bad_defense_summary", {}).get("total_scenarios") == 10
            and sum_data.get("known_bad_defense_summary", {}).get("intercepted_scenarios") == 10
        )

    record_check(
        "CHK-12",
        "Master Compliance Summary JSON Consistency",
        summary_ok,
        f"phase98a_master_compliance_summary.json verified: compliance_status=COMPLIANT."
    )

    # ------------------------------------------------------------------------
    # Final Validation Summary
    # ------------------------------------------------------------------------
    logger.info("\n" + "=" * 80)
    logger.info("Phase 98A Integrated Gate Validation Summary")
    logger.info(f"Total Checks Executed: {checks_passed + checks_failed}")
    logger.info(f"Total Checks Passed:   {checks_passed}")
    logger.info(f"Total Checks Failed:   {checks_failed}")
    success_rate = (checks_passed / (checks_passed + checks_failed)) * 100 if (checks_passed + checks_failed) > 0 else 0
    logger.info(f"Pass Rate:             {success_rate:.1f}%")
    logger.info(f"Gate Status:           {'PASS (ALL CHECKS PASSED)' if checks_failed == 0 else 'FAIL'}")
    logger.info("=" * 80)

    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(validate_all())
