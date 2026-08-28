"""
test_controlled_replay_gatekeeper.py — Unit Tests for Controlled Replay 8-Node Gatekeeper.
Path: tests/test_controlled_replay_gatekeeper.py

Task: Phase-98A-REPLAY-002
PRD References:
  - PRD v2.0 §4, §9.3
  - 攻击者视角新增章节 §4, §11
  - 原 PRD v1.0 §4, §6, §7
  - PRD v3.1 §2.2, §3, §4
  - GAP-006 闭环要求
"""

import pytest
import tempfile
from pathlib import Path

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


@pytest.fixture
def gatekeeper():
    """Returns an instantiated ControlledReplayGatekeeper."""
    return ControlledReplayGatekeeper()


@pytest.fixture
def sample_payloads():
    """Returns valid sample payloads for all 8 statutory review nodes."""
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
def sample_signatures():
    """Returns valid human signatures for all 8 nodes."""
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
# 1. Initialization & Schema Tests
# ============================================================================

def test_gatekeeper_initialization(gatekeeper):
    assert gatekeeper is not None
    assert len(gatekeeper.node_definitions) == 8
    assert gatekeeper.safety_boundaries["confirmed_vulnerability"] is False
    assert gatekeeper.safety_boundaries["controlled_replay_execution_allowed"] is False
    assert gatekeeper.safety_boundaries["synthetic_only"] is True


def test_standard_abort_conditions_and_rollback_steps():
    assert len(STANDARD_ABORT_CONDITIONS) == 7
    assert len(STANDARD_ROLLBACK_STEPS) == 5


# ============================================================================
# 2. Session Creation Tests
# ============================================================================

def test_create_session_success(gatekeeper):
    session = gatekeeper.create_session("BRT-001")
    assert session is not None
    assert session.candidate_id == "BRT-001"
    assert session.overall_status == SessionStatusEnum.IN_PROGRESS.value
    assert len(session.node_states) == 8
    assert session.node_states["NODE-1"].status == NodeStatusEnum.PENDING.value


def test_create_session_invalid_candidate_id(gatekeeper):
    with pytest.raises(ValueError, match="Invalid candidate_id format"):
        gatekeeper.create_session("INVALID_CANDIDATE_123")


# ============================================================================
# 3. End-to-End 8-Node Happy Path Workflow
# ============================================================================

def test_full_8node_happy_path(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    session_id = session.session_id

    for i in range(1, 9):
        nid = f"NODE-{i}"
        res = gatekeeper.submit_node_review(
            session_id=session_id,
            node_id=nid,
            payload=sample_payloads[nid],
            signature=sample_signatures[nid],
            decision="approve",
        )
        assert res.success is True
        assert res.status == NodeStatusEnum.APPROVED.value
        assert session.node_states[nid].status == NodeStatusEnum.APPROVED.value

    assert session.overall_status == SessionStatusEnum.FULLY_APPROVED.value
    assert len(session.audit_chain) == 8

    # GAP-006 closure verification
    gap006 = gatekeeper.verify_gap006_closure(session_id)
    assert gap006["status"] == "closed"
    assert gap006["closure_criteria_evaluation"]["all_8_nodes_approved"] is True
    assert gap006["closure_criteria_evaluation"]["controlled_replay_hard_blocked"] is True


# ============================================================================
# 4. Anti-Step-Skipping Interceptions (HIG-005)
# ============================================================================

def test_step_skipping_node2_before_node1(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    with pytest.raises(StepSkippingViolation, match="HIG-005: Step skipping violation"):
        gatekeeper.submit_node_review(
            session_id=session.session_id,
            node_id="NODE-2",
            payload=sample_payloads["NODE-2"],
            signature=sample_signatures["NODE-2"],
        )


def test_step_skipping_node5_before_node4(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id

    # Approve Node 1 and Node 2 only
    gatekeeper.submit_node_review(sid, "NODE-1", sample_payloads["NODE-1"], sample_signatures["NODE-1"])
    gatekeeper.submit_node_review(sid, "NODE-2", sample_payloads["NODE-2"], sample_signatures["NODE-2"])

    # Try to jump to Node 5
    with pytest.raises(StepSkippingViolation, match="HIG-005: Step skipping violation"):
        gatekeeper.submit_node_review(sid, "NODE-5", sample_payloads["NODE-5"], sample_signatures["NODE-5"])


def test_step_skipping_node8_direct_jump(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    with pytest.raises(StepSkippingViolation):
        gatekeeper.submit_node_review(session.session_id, "NODE-8", sample_payloads["NODE-8"], sample_signatures["NODE-8"])


# ============================================================================
# 5. Human Review Signature Interceptions (HIG-004)
# ============================================================================

def test_missing_human_signature_text(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    bad_sig = HumanSignature(
        reviewer_id="REV-TEST-01",
        reviewer_role=ReviewerRoleEnum.SECURITY_TESTING_LEAD.value,
        signature_text="",  # Empty signature
    )
    res = gatekeeper.submit_node_review(session.session_id, "NODE-1", sample_payloads["NODE-1"], bad_sig)
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-004" in res.message


def test_automated_override_block(gatekeeper, sample_payloads):
    session = gatekeeper.create_session("BRT-001")
    auto_sig = HumanSignature(
        reviewer_id="AUTO_SYSTEM_BOT",
        reviewer_role=ReviewerRoleEnum.SECURITY_TESTING_LEAD.value,
        signature_text="AUTO_SIGN_OVERRIDE",
        is_automated_override=True,  # Automated override
    )
    res = gatekeeper.submit_node_review(session.session_id, "NODE-1", sample_payloads["NODE-1"], auto_sig)
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-004" in res.message


def test_reviewer_role_mismatch(gatekeeper, sample_payloads):
    session = gatekeeper.create_session("BRT-001")
    wrong_role_sig = HumanSignature(
        reviewer_id="REV-DATA-01",
        reviewer_role=ReviewerRoleEnum.DATA_SAFETY_LEAD.value,  # Wrong role for Node 1
        signature_text="Sign: DataSafetyLead reviewing Node 1",
    )
    res = gatekeeper.submit_node_review(session.session_id, "NODE-1", sample_payloads["NODE-1"], wrong_role_sig)
    assert res.success is False
    assert "Reviewer role mismatch" in res.message


# ============================================================================
# 6. Hard-Blocking Guardrail Interceptions (HIG-001 ~ HIG-009)
# ============================================================================

def test_hig001_production_environment_block(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id
    gatekeeper.submit_node_review(sid, "NODE-1", sample_payloads["NODE-1"], sample_signatures["NODE-1"])
    gatekeeper.submit_node_review(sid, "NODE-2", sample_payloads["NODE-2"], sample_signatures["NODE-2"])

    # Try to approve Node 3 with production environment
    bad_payload = dict(sample_payloads["NODE-3"])
    bad_payload["environment_type"] = "production"
    bad_payload["production_environment_allowed"] = True

    res = gatekeeper.submit_node_review(sid, "NODE-3", bad_payload, sample_signatures["NODE-3"])
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-001" in res.message


def test_hig002_real_network_access_block(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id
    gatekeeper.submit_node_review(sid, "NODE-1", sample_payloads["NODE-1"], sample_signatures["NODE-1"])
    gatekeeper.submit_node_review(sid, "NODE-2", sample_payloads["NODE-2"], sample_signatures["NODE-2"])

    # Try to enable external network
    bad_payload = dict(sample_payloads["NODE-3"])
    bad_payload["external_network_access_allowed"] = True

    res = gatekeeper.submit_node_review(sid, "NODE-3", bad_payload, sample_signatures["NODE-3"])
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-002" in res.message


def test_hig003_real_credential_block(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id
    gatekeeper.submit_node_review(sid, "NODE-1", sample_payloads["NODE-1"], sample_signatures["NODE-1"])
    gatekeeper.submit_node_review(sid, "NODE-2", sample_payloads["NODE-2"], sample_signatures["NODE-2"])
    gatekeeper.submit_node_review(sid, "NODE-3", sample_payloads["NODE-3"], sample_signatures["NODE-3"])

    # Inject real API token in Node 4 payload
    bad_payload = dict(sample_payloads["NODE-4"])
    bad_payload["authorized_test_accounts"] = ["sk-live-abcdef12345678901234567890"]

    res = gatekeeper.submit_node_review(sid, "NODE-4", bad_payload, sample_signatures["NODE-4"])
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-003" in res.message


def test_hig006_rollback_plan_missing_block(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id
    for i in range(1, 5):
        nid = f"NODE-{i}"
        gatekeeper.submit_node_review(sid, nid, sample_payloads[nid], sample_signatures[nid])

    # Node 5 missing rollback plan
    bad_payload = dict(sample_payloads["NODE-5"])
    bad_payload["rollback_plan_approved"] = False

    res = gatekeeper.submit_node_review(sid, "NODE-5", bad_payload, sample_signatures["NODE-5"])
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-006" in res.message


def test_hig007_unilateral_vulnerability_escalation_block(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id
    for i in range(1, 7):
        nid = f"NODE-{i}"
        gatekeeper.submit_node_review(sid, nid, sample_payloads[nid], sample_signatures[nid])

    # Node 7 attempting confirmed_vulnerability = True
    bad_payload = dict(sample_payloads["NODE-7"])
    bad_payload["confirmed_vulnerability"] = True

    res = gatekeeper.submit_node_review(sid, "NODE-7", bad_payload, sample_signatures["NODE-7"])
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-007" in res.message


def test_hig008_production_safety_claim_block(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id
    for i in range(1, 8):
        nid = f"NODE-{i}"
        gatekeeper.submit_node_review(sid, nid, sample_payloads[nid], sample_signatures[nid])

    # Node 8 attempting production_safety_claimed = True
    bad_payload = dict(sample_payloads["NODE-8"])
    bad_payload["production_safety_claimed"] = True

    res = gatekeeper.submit_node_review(sid, "NODE-8", bad_payload, sample_signatures["NODE-8"])
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-008" in res.message


def test_hig009_non_synthetic_data_block(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    bad_payload = dict(sample_payloads["NODE-1"])
    bad_payload["synthetic_only"] = False

    res = gatekeeper.submit_node_review(session.session_id, "NODE-1", bad_payload, sample_signatures["NODE-1"])
    assert res.success is False
    assert res.hard_block_triggered is True
    assert "HIG-009" in res.message


# ============================================================================
# 7. Rejection Flow & State Locking
# ============================================================================

def test_node_rejection_flow(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id

    rej_sig = HumanSignature(
        reviewer_id="REV-SEC-TEST-01",
        reviewer_role=ReviewerRoleEnum.SECURITY_TESTING_LEAD.value,
        signature_text="Sign: Rejecting candidate",
        comments="Candidate lacks sufficient evidence trace ref.",
    )

    res = gatekeeper.submit_node_review(sid, "NODE-1", sample_payloads["NODE-1"], rej_sig, decision="reject")
    assert res.success is False
    assert res.status == NodeStatusEnum.REJECTED.value
    assert session.overall_status == SessionStatusEnum.REJECTED.value

    # Subsequent submission should fail due to rejected session state
    with pytest.raises(SessionStateError, match="terminal status 'rejected'"):
        gatekeeper.submit_node_review(sid, "NODE-2", sample_payloads["NODE-2"], sample_signatures["NODE-2"])


# ============================================================================
# 8. Report Export & Audit Chain Inspection
# ============================================================================

def test_report_export(gatekeeper, sample_payloads, sample_signatures):
    session = gatekeeper.create_session("BRT-001")
    sid = session.session_id
    for i in range(1, 9):
        nid = f"NODE-{i}"
        gatekeeper.submit_node_review(sid, nid, sample_payloads[nid], sample_signatures[nid])

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tf:
        temp_path = tf.name

    report = gatekeeper.export_session_report(sid, output_path=temp_path)
    assert report is not None
    assert report["session"]["session_id"] == sid
    assert report["session"]["overall_status"] == SessionStatusEnum.FULLY_APPROVED.value
    assert len(report["audit_chain"]) == 8
    assert Path(temp_path).exists()
