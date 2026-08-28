"""
tests/test_phase98a_metric_and_replay_integration.py — Integration Test Suite for Phase 98A.
Path: tests/test_phase98a_metric_and_replay_integration.py

Task: Phase-98A-GATE-003
Task Name: 阶段 98 评估指标与受控复现整合验证套件开发
PRD References:
  - 原 PRD v1.0 §6, §7, §10
  - 攻击者视角新增章节 §4, §7, §11
  - PRD v2.0 §4, §9.3, §13
  - PRD v3.1 §2.7, §4, §5
  - GAP-001 与 GAP-006 联合对账闭环

Test Coverage:
1. Dual-Engine Coupling & Safety Boundary Invariants.
2. Canonical Metric Engine Batch Evaluation across M43-M50.
3. Unapproved and Missing Mapping Rules Unresolved Fallback.
4. Controlled Replay 8-Node Gatekeeper Full Sequential Workflow (Happy Path).
5. 10 Groups of Known-Bad Injection Defense Interceptions (KB-001 to KB-010).
6. Forbidden Auto-Mapping Defense Catalog (FAM-001 to FAM-008).
7. Gatekeeper Hard-Blocking Invariant Guardrails (HIG-001 to HIG-009).
8. GAP-001 Formal Closure Verification (M44 Trust Boundary).
9. GAP-006 Formal Closure Verification (PRD v2.0 §9.3 8-Node Gatekeeper).
10. State Transition Simulator & Non-Retroactivity Guarantees.
11. Integrated Reconciliation Matrix & Master Compliance Summary Consistency.
12. Role Authorization & Anti-Step-Skipping State Machine Enforcement.
"""

import json
import yaml
import pytest
from pathlib import Path
from typing import Any, Dict

from src.engine.canonical_metric_quantification_engine import (
    CanonicalMetricQuantificationEngine,
    CapabilityValue,
    RiskLevel,
    CanonicalStatus,
    ReviewStatus,
    MappingAbsenceEffect,
    ForbiddenAutoMappingViolation,
    FORBIDDEN_AUTO_MAPPING_RULES,
)

from src.gatekeeper.controlled_replay_gatekeeper import (
    ControlledReplayGatekeeper,
    GateNodeEnum,
    NodeStatusEnum,
    ReviewerRoleEnum,
    SessionStatusEnum,
    HumanSignature,
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
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def metric_engine():
    """Initializes standard Canonical Metric Quantification Engine."""
    return CanonicalMetricQuantificationEngine()


@pytest.fixture
def gatekeeper():
    """Initializes standard Controlled Replay 8-Node Gatekeeper."""
    return ControlledReplayGatekeeper()


@pytest.fixture
def valid_node_payloads():
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


@pytest.fixture
def valid_signatures():
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


# ============================================================================
# Test 1: Dual-Engine Coupling & Safety Invariants
# ============================================================================

def test_dual_engine_coupling_and_safety_invariants(metric_engine, gatekeeper):
    """Verifies dual engine creation and non-negotiable safety invariant enforcement."""
    assert metric_engine is not None
    assert gatekeeper is not None

    sb_m = metric_engine.get_safety_boundaries()
    assert sb_m["confirmed_vulnerability"] is False
    assert sb_m["formal_finding_allowed"] is False
    assert sb_m["production_safety_claimed"] is False
    assert sb_m["synthetic_only"] is True
    assert sb_m["red_team_engine_not_executable"] is True

    sb_g = gatekeeper.safety_boundaries
    assert sb_g["confirmed_vulnerability"] is False
    assert sb_g["formal_finding_allowed"] is False
    assert sb_g["production_safety_claimed"] is False
    assert sb_g["controlled_replay_execution_allowed"] is False
    assert sb_g["synthetic_only"] is True
    assert sb_g["requires_human_review"] is True


# ============================================================================
# Test 2: Canonical Metric Engine Batch Evaluation across M43-M50
# ============================================================================

def test_canonical_metric_batch_evaluation_m43_m50(metric_engine):
    """Verifies that all 8 modules (M43-M50) are formally resolved via approved rules."""
    batch_res = metric_engine.evaluate_batch()

    assert batch_res.summary["total_evaluated"] == 8
    assert batch_res.summary["resolved_count"] == 8
    assert batch_res.summary["unresolved_count"] == 0
    assert batch_res.summary["blocked_count"] == 0

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

    for mod_id, (expected_cap, expected_risk) in expected_evaluations.items():
        ev = batch_res.evaluations[mod_id]
        assert ev.is_resolved()
        assert ev.canonical_capability_value == expected_cap
        assert ev.canonical_risk_level == expected_risk
        assert ev.canonical_capability_status == CanonicalStatus.RESOLVED.value
        assert ev.canonical_risk_status == CanonicalStatus.RESOLVED.value
        assert not ev.future_canonical_metric_normalization_blocked


# ============================================================================
# Test 3: Unapproved and Missing Mapping Rules Fallback
# ============================================================================

def test_unapproved_and_missing_rules_unresolved_fallback(metric_engine):
    """Verifies fallback to unresolved and documentation debt for unmapped or unapproved rules."""
    unmapped = metric_engine.evaluate_module("M999", "adversarial_validation")
    assert unmapped.canonical_capability_status == CanonicalStatus.UNRESOLVED.value
    assert unmapped.canonical_risk_status == CanonicalStatus.UNRESOLVED.value
    assert unmapped.canonical_capability_value is None
    assert unmapped.canonical_risk_level is None
    assert unmapped.future_canonical_metric_normalization_blocked is True
    assert unmapped.mapping_absence_effect == MappingAbsenceEffect.DOCUMENTATION_DEBT_ONLY.value


# ============================================================================
# Test 4: Controlled Replay 8-Node Gatekeeper Happy Path Workflow
# ============================================================================

def test_controlled_replay_8node_happy_path_workflow(gatekeeper, valid_node_payloads, valid_signatures):
    """Executes sequential reviews across all 8 nodes and verifies full approval."""
    session = gatekeeper.create_session("BRT-001")

    for i in range(1, 9):
        nid = f"NODE-{i}"
        res = gatekeeper.submit_node_review(session.session_id, nid, valid_node_payloads[nid], valid_signatures[nid])
        assert res.success, f"Node {nid} failed: {res.message}"
        assert res.status == NodeStatusEnum.APPROVED.value
        assert res.audit_record is not None

    assert session.overall_status == SessionStatusEnum.FULLY_APPROVED.value
    assert len(session.audit_chain) == 8


# ============================================================================
# Test 5: 10 Groups of Known-Bad Injection Defenses Matrix
# ============================================================================

@pytest.mark.parametrize("scenario_id,engine_target,payload_mod,expected_exception", [
    ("KB-001", "metric", {"success_rate": 0.95, "auto_capability_value": "high"}, ForbiddenAutoMappingViolation),
    ("KB-002", "metric", {"signal_count": 14, "auto_risk_level": "high"}, ForbiddenAutoMappingViolation),
    ("KB-003", "metric", {"breakthrough_detected": True, "inferred_risk_level": "high"}, ForbiddenAutoMappingViolation),
    ("KB-004", "metric", {"human_review_count": 5, "inferred_risk_level": "high"}, ForbiddenAutoMappingViolation),
    ("KB-005", "gatekeeper_node3", {"environment_type": "production", "production_environment_allowed": True}, ProductionEnvironmentViolationError),
    ("KB-006", "gatekeeper_node3", {"external_network_access_allowed": True}, RealNetworkAccessViolationError),
    ("KB-007", "gatekeeper_node4", {"authorized_test_accounts": ["sk-live-sec98765432109876543210"]}, RealCredentialViolationError),
    ("KB-008", "gatekeeper_node1", {"is_automated_override": True}, MissingHumanReviewSignatureError),
    ("KB-009", "gatekeeper_node5_jump", {}, StepSkippingViolation),
    ("KB-010", "gatekeeper_node7", {"confirmed_vulnerability": True}, UnilateralVulnerabilityEscalationError),
])
def test_ten_known_bad_injection_defenses_matrix(
    metric_engine, gatekeeper, valid_node_payloads, valid_signatures,
    scenario_id, engine_target, payload_mod, expected_exception
):
    """Verifies that all 10 Known-Bad attack vectors are strictly intercepted."""
    if engine_target == "metric":
        with pytest.raises(expected_exception):
            metric_engine.check_forbidden_auto_mapping(payload_mod, raise_on_violation=True)

    elif engine_target == "gatekeeper_node3":
        s = gatekeeper.create_session(f"BRT-{scenario_id}")
        gatekeeper.submit_node_review(s.session_id, "NODE-1", valid_node_payloads["NODE-1"], valid_signatures["NODE-1"])
        gatekeeper.submit_node_review(s.session_id, "NODE-2", valid_node_payloads["NODE-2"], valid_signatures["NODE-2"])
        bad_payload = dict(valid_node_payloads["NODE-3"])
        bad_payload.update(payload_mod)
        res = gatekeeper.submit_node_review(s.session_id, "NODE-3", bad_payload, valid_signatures["NODE-3"])
        assert res.hard_block_triggered
        assert not res.success
        assert res.status == NodeStatusEnum.BLOCKED.value

    elif engine_target == "gatekeeper_node4":
        s = gatekeeper.create_session(f"BRT-{scenario_id}")
        gatekeeper.submit_node_review(s.session_id, "NODE-1", valid_node_payloads["NODE-1"], valid_signatures["NODE-1"])
        gatekeeper.submit_node_review(s.session_id, "NODE-2", valid_node_payloads["NODE-2"], valid_signatures["NODE-2"])
        gatekeeper.submit_node_review(s.session_id, "NODE-3", valid_node_payloads["NODE-3"], valid_signatures["NODE-3"])
        bad_payload = dict(valid_node_payloads["NODE-4"])
        bad_payload.update(payload_mod)
        res = gatekeeper.submit_node_review(s.session_id, "NODE-4", bad_payload, valid_signatures["NODE-4"])
        assert res.hard_block_triggered
        assert not res.success

    elif engine_target == "gatekeeper_node1":
        s = gatekeeper.create_session(f"BRT-{scenario_id}")
        bot_sig = HumanSignature(
            reviewer_id="AUTO_BOT",
            reviewer_role=ReviewerRoleEnum.SECURITY_TESTING_LEAD.value,
            signature_text="AUTO",
            is_automated_override=True,
        )
        res = gatekeeper.submit_node_review(s.session_id, "NODE-1", valid_node_payloads["NODE-1"], bot_sig)
        assert res.hard_block_triggered
        assert "HIG-004" in res.message

    elif engine_target == "gatekeeper_node5_jump":
        s = gatekeeper.create_session(f"BRT-{scenario_id}")
        with pytest.raises(StepSkippingViolation):
            gatekeeper.submit_node_review(s.session_id, "NODE-5", valid_node_payloads["NODE-5"], valid_signatures["NODE-5"])

    elif engine_target == "gatekeeper_node7":
        s = gatekeeper.create_session(f"BRT-{scenario_id}")
        for i in range(1, 7):
            gatekeeper.submit_node_review(s.session_id, f"NODE-{i}", valid_node_payloads[f"NODE-{i}"], valid_signatures[f"NODE-{i}"])
        bad_payload = dict(valid_node_payloads["NODE-7"])
        bad_payload.update(payload_mod)
        res = gatekeeper.submit_node_review(s.session_id, "NODE-7", bad_payload, valid_signatures["NODE-7"])
        assert res.hard_block_triggered
        assert "HIG-007" in res.message


# ============================================================================
# Test 6: Forbidden Auto-Mapping Full Catalog Defense (FAM-001 ~ FAM-008)
# ============================================================================

def test_forbidden_auto_mapping_catalog_coverage(metric_engine):
    """Verifies all 8 Forbidden Auto-Mapping rules are identified by the engine."""
    assert len(FORBIDDEN_AUTO_MAPPING_RULES) == 8

    test_vectors = [
        ("FAM-001", {"validator_pass_rate": 0.95, "auto_capability_value": "high"}),
        ("FAM-002", {"raw_signals_count": 20, "auto_risk_level": "medium"}),
        ("FAM-003", {"breakthrough_detected": False, "inferred_risk_level": "low"}),
        ("FAM-004", {"breakthrough_detected": True, "inferred_risk_level": "high"}),
        ("FAM-005", {"human_review_required_count": 4, "inferred_risk_level": "medium"}),
        ("FAM-006", {"canonical_capability_value": "simulated_capability_signal"}),
        ("FAM-007", {"conflate_safety_with_risk": True}),
        ("FAM-008", {"claim_resolved_without_rule": True}),
    ]

    for rule_id, data in test_vectors:
        violations = metric_engine.check_forbidden_auto_mapping(data, raise_on_violation=False)
        assert any(rule_id in v for v in violations), f"Failed to detect {rule_id}"


# ============================================================================
# Test 7: Gatekeeper Hard-Blocking Invariant Guardrails (HIG-006, HIG-008, HIG-009)
# ============================================================================

def test_hard_blocking_invariant_guardrails_coverage(gatekeeper, valid_node_payloads, valid_signatures):
    """Verifies HIG-006 (rollback), HIG-008 (safety claim), and HIG-009 (non-synthetic)."""
    # HIG-006: Rollback missing on Node 5
    s1 = gatekeeper.create_session("BRT-HIG-006")
    for i in range(1, 5):
        gatekeeper.submit_node_review(s1.session_id, f"NODE-{i}", valid_node_payloads[f"NODE-{i}"], valid_signatures[f"NODE-{i}"])
    bad_rb = dict(valid_node_payloads["NODE-5"])
    bad_rb["rollback_plan_approved"] = False
    res1 = gatekeeper.submit_node_review(s1.session_id, "NODE-5", bad_rb, valid_signatures["NODE-5"])
    assert res1.hard_block_triggered and "HIG-006" in res1.message

    # HIG-008: Production safety claim on Node 8
    s2 = gatekeeper.create_session("BRT-HIG-008")
    for i in range(1, 8):
        gatekeeper.submit_node_review(s2.session_id, f"NODE-{i}", valid_node_payloads[f"NODE-{i}"], valid_signatures[f"NODE-{i}"])
    bad_safe = dict(valid_node_payloads["NODE-8"])
    bad_safe["production_safety_claimed"] = True
    res2 = gatekeeper.submit_node_review(s2.session_id, "NODE-8", bad_safe, valid_signatures["NODE-8"])
    assert res2.hard_block_triggered and "HIG-008" in res2.message

    # HIG-009: Non-synthetic data on Node 1
    s3 = gatekeeper.create_session("BRT-HIG-009")
    bad_synth = dict(valid_node_payloads["NODE-1"])
    bad_synth["synthetic_only"] = False
    res3 = gatekeeper.submit_node_review(s3.session_id, "NODE-1", bad_synth, valid_signatures["NODE-1"])
    assert res3.hard_block_triggered and "HIG-009" in res3.message


# ============================================================================
# Test 8: GAP-001 Formal Closure Verification
# ============================================================================

def test_gap001_formal_closure_verification(metric_engine):
    """Verifies formal resolution and non-retroactivity for GAP-001 (M44)."""
    gap_res = metric_engine.resolve_gap("GAP-001")
    assert gap_res["closure_status"] == "closed"
    assert gap_res["target_module"] == "M44"
    assert gap_res["resolving_rule_id"] == "RULE-M44-CANONICAL-001"
    assert gap_res["canonical_capability_value"] == "high"
    assert gap_res["canonical_risk_level"] == "low"
    assert gap_res["canonical_capability_status"] == "resolved"
    assert gap_res["canonical_risk_status"] == "resolved"
    assert not gap_res["future_canonical_metric_normalization_blocked"]
    assert gap_res["non_retroactivity_guarantee"]["retroactive_effect_on_existing_module_closure"] is False


# ============================================================================
# Test 9: GAP-006 Formal Closure Verification
# ============================================================================

def test_gap006_formal_closure_verification(gatekeeper, valid_node_payloads, valid_signatures):
    """Verifies formal closure criteria for GAP-006 under ControlledReplayGatekeeper."""
    session = gatekeeper.create_session("BRT-GAP006")
    for i in range(1, 9):
        nid = f"NODE-{i}"
        gatekeeper.submit_node_review(session.session_id, nid, valid_node_payloads[nid], valid_signatures[nid])

    closure_proof = gatekeeper.verify_gap006_closure(session.session_id)
    assert closure_proof["status"] == "closed"
    assert closure_proof["gap_id"] == "GAP-006"
    assert closure_proof["closure_criteria_evaluation"]["all_8_nodes_defined"] is True
    assert closure_proof["closure_criteria_evaluation"]["all_8_nodes_approved"] is True
    assert closure_proof["closure_criteria_evaluation"]["controlled_replay_hard_blocked"] is True
    assert closure_proof["closure_criteria_evaluation"]["human_review_chain_intact"] is True


# ============================================================================
# Test 10: State Transition Simulator & Non-Retroactivity
# ============================================================================

def test_state_transition_simulation_and_non_retroactivity(metric_engine):
    """Verifies state transition simulation and non-retroactivity guarantees."""
    trans = metric_engine.simulate_unresolved_to_resolved_transition("M44", assessment_mode="adversarial_validation")
    assert trans.previous_capability_status == "unresolved"
    assert trans.new_capability_status == "resolved"
    assert trans.transition_success is True
    assert trans.gap_closed == "GAP-001"
    assert trans.non_retroactive_verified is True


# ============================================================================
# Test 11: Reconciliation Matrix & Compliance Summary Consistency
# ============================================================================

def test_reconciliation_matrix_and_compliance_summary_files():
    """Verifies existence, schema, and content consistency of output artifacts."""
    matrix_path = ROOT / "phase98a_integrated_reconciliation_matrix.yaml"
    summary_path = ROOT / "phase98a_master_compliance_summary.json"

    assert matrix_path.exists(), "Reconciliation matrix YAML file is missing"
    assert summary_path.exists(), "Master compliance summary JSON file is missing"

    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix = yaml.safe_load(f)
    assert matrix["task_id"] == "Phase-98A-GATE-003"
    assert len(matrix["canonical_metrics_reconciliation"]["modules_evaluated"]) == 8
    assert len(matrix["eight_node_gatekeeper_reconciliation"]["state_machine_nodes"]) == 8
    assert len(matrix["known_bad_defense_matrix"]["scenarios"]) == 10

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    assert summary["gate_id"] == "Phase-98A-GATE-003"
    assert summary["compliance_status"] == "COMPLIANT"
    assert summary["gap_closures"]["GAP-001"]["status"] == "closed"
    assert summary["gap_closures"]["GAP-006"]["status"] == "closed"
    assert summary["known_bad_defense_summary"]["intercepted_scenarios"] == 10


# ============================================================================
# Test 12: Role Authorization & Anti-Step-Skipping State Machine
# ============================================================================

def test_gatekeeper_role_authorization_and_step_skipping(gatekeeper, valid_node_payloads, valid_signatures):
    """Verifies that role mismatch and step skipping are strictly rejected."""
    # Role mismatch test on Node 1 (requires security_testing_lead)
    s = gatekeeper.create_session("BRT-ROLE-MISMATCH")
    wrong_sig = HumanSignature(
        reviewer_id="REV-MGT-01",
        reviewer_role=ReviewerRoleEnum.SECURITY_MANAGEMENT_LEAD.value,
        signature_text="Sign: Wrong Role",
    )
    res = gatekeeper.submit_node_review(s.session_id, "NODE-1", valid_node_payloads["NODE-1"], wrong_sig)
    assert not res.success
    assert "Reviewer role mismatch" in res.message

    # Step skipping test (jumping directly to Node 8)
    s2 = gatekeeper.create_session("BRT-STEP-SKIP")
    with pytest.raises(StepSkippingViolation):
        gatekeeper.submit_node_review(s2.session_id, "NODE-8", valid_node_payloads["NODE-8"], valid_signatures["NODE-8"])
