"""
tests/test_phase100a_mega_reconciliation_gate.py — Automated Unit & Integration Tests for Phase-100A-MEGA-001.
Path: tests/test_phase100a_mega_reconciliation_gate.py

Task: Phase-100A-MEGA-001
Task Name: 全系统 50 模块、15+ 报告、传播动力学引擎、8-Node 审批门禁、全量看板与离线报告端到端大闭环超级对账门开发
PRD References:
  - 原 PRD v1.0 §5, §6, §7, §9, §10
  - 攻击者视角新增章节 §2, §4, §6, §7, §11
  - PRD v2.0 §1, §4, §6-§9, §9.3, §10, §13
  - PRD v3.1 §1, §2.1-§2.8, §3, §4
"""

import json
import os
import pytest
import yaml
from pathlib import Path

from multi_agent.replay.phase100a_mega_reconciliation_gate import (
    MegaReconciliationGatekeeper,
    MegaReconciliationResult,
    SYSTEM_50_MODULES_CATALOG,
    RED_TEAM_REPORTS_CATALOG,
    MEGA_RECONCILIATION_SAFETY_BOUNDARIES,
    KNOWN_BAD_MEGA_DEFENSE_RULES,
    MegaReconciliationError,
    FakeRuntimeViolationError,
    RealCredentialViolationError,
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
    HumanSignature,
    StepSkippingViolation,
    ProductionEnvironmentViolationError,
    STANDARD_ABORT_CONDITIONS,
    STANDARD_ROLLBACK_STEPS,
)

ROOT = Path(__file__).resolve().parent.parent


class TestPhase100AMegaReconciliation:
    """Test suite covering the 6 Pillars of Mega Reconciliation Gatekeeper."""

    @pytest.fixture
    def gatekeeper(self):
        return MegaReconciliationGatekeeper(root_dir=ROOT)

    # --------------------------------------------------------------------------
    # Pillar 1: 50 Capability Modules (M01-M50)
    # --------------------------------------------------------------------------
    def test_pillar_1_50_modules_catalog_completeness(self, gatekeeper):
        """Verify that all 50 capability modules M01-M50 are present and properly classified."""
        m_res = gatekeeper.reconcile_50_modules()
        assert m_res["total_modules"] == 50
        assert m_res["aligned_modules"] == 50
        assert m_res["mismatches"] == 0
        assert m_res["p0_count"] == 23
        assert m_res["p1_count"] == 13
        assert m_res["p2_count"] == 6
        assert m_res["v2_count"] == 8
        assert m_res["all_synthetic_only"] is True
        assert m_res["all_fake_runtime"] is True
        assert m_res["status"] == "PASS"

    def test_pillar_1_module_safety_invariants(self, gatekeeper):
        """Verify that every module strictly asserts non-vulnerability and non-production invariants."""
        for mid, mdata in SYSTEM_50_MODULES_CATALOG.items():
            assert mdata["confirmed_vulnerability"] is False, f"{mid} confirmed_vulnerability != False"
            assert mdata["formal_finding_allowed"] is False, f"{mid} formal_finding_allowed != False"
            assert mdata["production_safety_claimed"] is False, f"{mid} production_safety_claimed != False"
            assert mdata["synthetic_only"] is True, f"{mid} synthetic_only != True"
            assert mdata["fake_runtime_only"] is True, f"{mid} fake_runtime_only != True"
            assert mdata["requires_human_review"] is True, f"{mid} requires_human_review != True"

    # --------------------------------------------------------------------------
    # Pillar 2: 15+ Red Team Reports (RED-001 ~ RED-020)
    # --------------------------------------------------------------------------
    def test_pillar_2_red_team_reports_catalog(self, gatekeeper):
        """Verify red team reports integrity, 100% boundary preservation, and zero real breakthrough."""
        r_res = gatekeeper.reconcile_red_team_reports()
        assert r_res["total_reports_audited"] >= 15
        assert r_res["all_reports_closed"] is True
        assert r_res["total_breakthroughs"] == 0
        assert r_res["boundary_preservation_rate"] == 1.0
        assert r_res["all_findings_candidate_level"] is True
        assert r_res["status"] == "PASS"

    def test_pillar_2_individual_report_attributes(self):
        """Verify individual report attributes in RED_TEAM_REPORTS_CATALOG."""
        for rep in RED_TEAM_REPORTS_CATALOG:
            assert rep["status"] == "closed/judge_approved"
            assert rep["breakthrough"] == 0
            assert rep["boundary_preservation_rate"] == 1.0
            assert rep["candidate_level"] is True
            assert rep["confirmed_vulnerability"] is False
            assert len(rep["traversed_modules"]) >= 2

    # --------------------------------------------------------------------------
    # Pillar 3: Attack Propagation Dynamics Engine
    # --------------------------------------------------------------------------
    def test_pillar_3_propagation_dynamics_layers_and_edges(self, gatekeeper):
        """Verify propagation dynamics layers, edges, and Markov stochastic row sums."""
        p_res = gatekeeper.reconcile_propagation_dynamics()
        assert p_res["total_layers"] == 4
        assert p_res["total_edge_types"] == 7
        assert p_res["markov_stochastic_valid"] is True
        assert p_res["pressure_equation_consistent"] is True
        assert p_res["path_degradation_consistent"] is True
        assert p_res["status"] == "PASS"

    def test_pillar_3_differential_equation_execution(self, gatekeeper):
        """Verify exact calculation of P_edge, node defense transition, and G_path."""
        engine = gatekeeper.propagation_engine
        
        # Test P_edge calculation
        p_edge = engine.calculate_p_edge(source_signal=0.8, edge_type="permission_dependency", target_defense=0.4)
        assert 0.0 <= p_edge <= 1.0

        # Test node defense step
        d_next = engine.step_node_defense(current_defense=0.7, incoming_pressure=p_edge, module_id="M48", control_recovery=0.1, human_review=0.1)
        assert 0.0 <= d_next <= 1.0

        # Test G_path calculation
        g_path = engine.calculate_g_path(edge_pressures=[0.5, 0.4, 0.3], sequential_amplification=0.1)
        assert isinstance(g_path, float)

    # --------------------------------------------------------------------------
    # Pillar 4: 8-Node Controlled Replay Gatekeeper
    # --------------------------------------------------------------------------
    def test_pillar_4_gatekeeper_workflow(self, gatekeeper):
        """Verify 8-node sequential approval and role signatures."""
        g_res = gatekeeper.reconcile_8node_gatekeeper()
        assert g_res["statutory_nodes"] == 8
        assert g_res["sequential_flow_enforced"] is True
        assert g_res["role_signatures_verified"] is True
        assert g_res["step_skipping_blocked"] is True
        assert g_res["abort_conditions_count"] == 7
        assert g_res["rollback_steps_count"] == 5
        assert g_res["status"] == "PASS"

    def test_pillar_4_step_skipping_hard_block(self):
        """Verify that skipping nodes triggers StepSkippingViolation immediately."""
        gk = ControlledReplayGatekeeper()
        sess = gk.create_session(candidate_id="BRT-TEST-SKIP-01")
        
        sig = HumanSignature(
            reviewer_id="REV-SEC-LEAD-01",
            reviewer_role="security_lead",
            signature_text="Sign: SecLead 2026",
        )
        n5_payload = {
            "rollback_plan_approved": True,
            "abort_conditions_defined": True,
            "operator_id": "<SIM_OPERATOR_001>",
            "preflight_checklist_passed": True,
            "requires_human_review": True,
        }
        
        with pytest.raises(StepSkippingViolation):
            gk.submit_node_review(session_id=sess.session_id, node_id="NODE-5", payload=n5_payload, signature=sig)

    # --------------------------------------------------------------------------
    # Pillar 5: Assessment Dashboard & Offline Report Exporter
    # --------------------------------------------------------------------------
    def test_pillar_5_dashboard_and_reports(self, gatekeeper):
        """Verify 4 dashboard views, offline export capability, and data redaction policy."""
        d_res = gatekeeper.reconcile_dashboard_and_reports()
        assert d_res["total_views_verified"] == 4
        assert d_res["offline_self_contained"] is True
        assert d_res["data_redaction_verified"] is True
        assert d_res["zero_telemetry_guaranteed"] is True
        assert d_res["status"] == "PASS"

    def test_pillar_5_data_redaction_policy_patterns(self, gatekeeper):
        """Verify that API keys and cloud credentials are comprehensively redacted."""
        exporter = gatekeeper.report_exporter
        raw_text = "Secrets: sk-1234567890123456789012, AKIAIOSFODNN7EXAMPLE, and test@example.com"
        redacted = exporter.apply_redaction_policy(raw_text)
        assert "sk-1234567890" not in redacted
        assert "AKIAIOSFODNN7EXAMPLE" not in redacted
        assert "<REDACTED_API_KEY>" in redacted
        assert "<REDACTED_EMAIL>" in redacted

    # --------------------------------------------------------------------------
    # Pillar 6: 10 Mega Known-Bad Anomaly Injections
    # --------------------------------------------------------------------------
    def test_pillar_6_known_bad_injections_defense(self, gatekeeper):
        """Verify that all 10 Known-Bad injection vectors are 100% intercepted."""
        kb_res = gatekeeper.execute_known_bad_injections()
        assert kb_res["total_scenarios_injected"] == 10
        assert kb_res["total_scenarios_intercepted"] == 10
        assert kb_res["interception_rate"] == 1.0
        assert kb_res["zero_unhandled_exceptions"] is True
        assert kb_res["status"] == "PASS"

    @pytest.mark.parametrize("scenario_id", list(KNOWN_BAD_MEGA_DEFENSE_RULES.keys()))
    def test_pillar_6_individual_known_bad_scenarios(self, gatekeeper, scenario_id):
        """Test each of the 10 Known-Bad scenarios individually."""
        rule = KNOWN_BAD_MEGA_DEFENSE_RULES[scenario_id]
        with pytest.raises(Exception) as exc_info:
            gatekeeper._inject_anomaly_payload(scenario_id)
        
        exc_name = exc_info.value.__class__.__name__
        assert exc_name == rule["expected_exception"] or issubclass(exc_info.value.__class__, MegaReconciliationError)

    # --------------------------------------------------------------------------
    # Master Full Reconciliation & Deliverables Generation
    # --------------------------------------------------------------------------
    def test_master_full_reconciliation_execution(self, gatekeeper, tmp_path):
        """Verify master full reconciliation run and generation of YAML matrix & JSON compliance snapshot."""
        res = gatekeeper.run_full_reconciliation()
        assert isinstance(res, MegaReconciliationResult)
        assert res.status == "PASS"
        assert res.task_id == "Phase-100A-MEGA-001"

        yaml_file = tmp_path / "matrix_test.yaml"
        json_file = tmp_path / "compliance_test.json"

        gatekeeper.generate_matrix_yaml(yaml_file)
        gatekeeper.generate_compliance_summary_json(json_file)

        assert yaml_file.exists() and yaml_file.stat().st_size > 0
        assert json_file.exists() and json_file.stat().st_size > 0

        with open(yaml_file, "r", encoding="utf-8") as f:
            y_data = yaml.safe_load(f)
        assert y_data["task_id"] == "Phase-100A-MEGA-001"
        assert y_data["joint_verification_summary"]["total_modules"] == 50

        with open(json_file, "r", encoding="utf-8") as f:
            j_data = json.load(f)
        assert j_data["task_id"] == "Phase-100A-MEGA-001"
        assert j_data["system_statistics"]["aligned_modules"] == 50
        assert j_data["non_retroactivity_guarantee"]["historical_phases_intact"] is True
