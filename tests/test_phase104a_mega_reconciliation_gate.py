"""
tests/test_phase104a_mega_reconciliation_gate.py — Automated Unit & Integration Tests for Phase-104A-MEGA-001.
Path: tests/test_phase104a_mega_reconciliation_gate.py

Task: Phase-104A-MEGA-001
Task Name: 全系统 Milestone 4.0 超级全景端到端大闭环对账门开发
PRD References:
  - 原 PRD v1.0 §4, §5, §6, §9, §10, §13, §15
  - 攻击者视角新增章节 §2, §3, §4, §5, §6, §7, §11
  - PRD v2.0 §1, §4, §5, §6-§9, §10, §13
  - PRD v3.1 §1, §2.1-§2.8, §3, §4, §9
"""

import json
import os
import pytest
import yaml
from pathlib import Path

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
    RealCredentialViolationError,
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
    UnilateralVulnerabilityEscalationError,
    ProductionSafetyClaimViolationError,
    NonSyntheticDataViolationError,
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


class TestPhase104AMegaReconciliation:
    """Test suite covering the 7 Pillars of Milestone 4.0 Mega Reconciliation Gatekeeper."""

    @pytest.fixture
    def gatekeeper(self):
        return Phase104AMegaReconciliationGate(root_dir=ROOT)

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
    # Pillar 2: 20 Red Team Reports (RED-001 ~ RED-020)
    # --------------------------------------------------------------------------
    def test_pillar_2_red_team_reports_catalog(self, gatekeeper):
        """Verify red team reports integrity, 100% boundary preservation, and zero real breakthrough."""
        r_res = gatekeeper.reconcile_red_team_reports()
        assert r_res["total_reports_audited"] == 20
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
    # Pillar 3: 60 Phase 101-103 Extended Adversarial Scenarios
    # --------------------------------------------------------------------------
    def test_pillar_3_extended_scenarios_completeness(self, gatekeeper):
        """Verify all 60 extended scenarios from Phase 101, 102, 103 are reconciled."""
        ext_res = gatekeeper.reconcile_60_extended_scenarios()
        assert ext_res["total_extended_cases"] == 60
        assert ext_res["phase101_cases_count"] == 20
        assert ext_res["phase102_cases_count"] == 20
        assert ext_res["phase103_cases_count"] == 20
        assert ext_res["attack_cases_count"] == 48
        assert ext_res["control_cases_count"] == 12
        assert ext_res["interceptions_count"] == 48
        assert ext_res["controls_passed_count"] == 12
        assert ext_res["breakthroughs_detected"] == 0
        assert ext_res["boundary_preservation_rate"] == 1.0
        assert ext_res["status"] == "PASS"

    def test_pillar_3_extended_scenarios_breakdowns(self):
        """Verify each scenario in EXTENDED_60_SCENARIOS_CATALOG."""
        for sc in EXTENDED_60_SCENARIOS_CATALOG:
            assert sc["phase"] in ["Phase-101A", "Phase-102A", "Phase-103A"]
            assert sc["breakthrough_detected"] is False
            assert sc["status"] == "PASS"
            if sc["control_case"]:
                assert sc["defensive_action"] == "normal_usage_allowed"
            else:
                assert sc["defensive_action"] == "refuse"

    # --------------------------------------------------------------------------
    # Pillar 4: Attack Propagation Dynamics Engine
    # --------------------------------------------------------------------------
    def test_pillar_4_propagation_dynamics_layers_and_edges(self, gatekeeper):
        """Verify propagation dynamics layers, edges, and Markov stochastic row sums."""
        p_res = gatekeeper.reconcile_propagation_dynamics()
        assert p_res["total_layers"] == 4
        assert p_res["total_edge_types"] == 7
        assert p_res["markov_stochastic_valid"] is True
        assert p_res["pressure_equation_consistent"] is True
        assert p_res["path_degradation_consistent"] is True
        assert p_res["status"] == "PASS"

    def test_pillar_4_differential_equation_execution(self, gatekeeper):
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
    # Pillar 5: 8-Node Controlled Replay Gatekeeper
    # --------------------------------------------------------------------------
    def test_pillar_5_gatekeeper_workflow(self, gatekeeper):
        """Verify 8-node sequential approval and role signatures."""
        g_res = gatekeeper.reconcile_8node_gatekeeper()
        assert g_res["statutory_nodes"] == 8
        assert g_res["sequential_flow_enforced"] is True
        assert g_res["role_signatures_verified"] is True
        assert g_res["step_skipping_blocked"] is True
        assert g_res["abort_conditions_count"] == 7
        assert g_res["rollback_steps_count"] == 5
        assert g_res["status"] == "PASS"

    # --------------------------------------------------------------------------
    # Pillar 6: Assessment Dashboard & Offline Report Pipeline
    # --------------------------------------------------------------------------
    def test_pillar_6_dashboard_and_reports(self, gatekeeper):
        """Verify 4 dashboard views and offline report data redaction."""
        d_res = gatekeeper.reconcile_dashboard_and_reports()
        assert d_res["total_views_verified"] == 4
        assert d_res["offline_self_contained"] is True
        assert d_res["data_redaction_verified"] is True
        assert d_res["zero_telemetry_guaranteed"] is True
        assert d_res["status"] == "PASS"

    # --------------------------------------------------------------------------
    # Pillar 7: 10 Mega Known-Bad Anomaly Injections
    # --------------------------------------------------------------------------
    def test_pillar_7_known_bad_injections(self, gatekeeper):
        """Verify 10 known-bad injection scenarios are 100% intercepted."""
        kb_res = gatekeeper.execute_known_bad_injections()
        assert kb_res["total_scenarios_injected"] == 10
        assert kb_res["total_scenarios_intercepted"] == 10
        assert kb_res["interception_rate"] == 1.0
        assert kb_res["zero_unhandled_exceptions"] is True
        assert kb_res["status"] == "PASS"

    def test_pillar_7_individual_known_bad_exceptions(self, gatekeeper):
        """Verify specific exceptions are raised for each of the 10 known-bad scenarios."""
        expected_mappings = {
            "KB-104A-001": FakeRuntimeViolationError,
            "KB-104A-002": RealCredentialViolationError,
            "KB-104A-003": LiveExecutionBlockedError,
            "KB-104A-004": LiveVectorDBAccessViolationError,
            "KB-104A-005": SandboxEscapeExecutionViolationError,
            "KB-104A-006": AuditStreamTamperingViolationError,
            "KB-104A-007": ReplayGateApprovalMissingError,
            "KB-104A-008": UnilateralVulnerabilityEscalationError,
            "KB-104A-009": ProductionSafetyClaimViolationError,
            "KB-104A-010": NonSyntheticDataViolationError,
        }

        for sc_id, exc_cls in expected_mappings.items():
            with pytest.raises(exc_cls):
                gatekeeper._inject_anomaly_payload(sc_id)

    # --------------------------------------------------------------------------
    # Master Reconciliation & Artifact Generation Tests
    # --------------------------------------------------------------------------
    def test_master_full_reconciliation_run(self, gatekeeper, tmp_path):
        """Verify master full reconciliation run returns PASS and generates valid artifacts."""
        result = gatekeeper.run_full_reconciliation()
        assert isinstance(result, Phase104AMegaReconciliationResult)
        assert result.task_id == "Phase-104A-MEGA-001"
        assert result.status == "PASS"
        assert result.module_summary.status == "PASS"
        assert result.report_summary.status == "PASS"
        assert result.extended_scenarios_summary.status == "PASS"
        assert result.propagation_summary.status == "PASS"
        assert result.gatekeeper_summary.status == "PASS"
        assert result.dashboard_summary.status == "PASS"
        assert result.known_bad_summary.status == "PASS"
        assert result.safety_boundaries["confirmed_vulnerability"] is False
        assert result.safety_boundaries["formal_finding_allowed"] is False
        assert result.safety_boundaries["production_safety_claimed"] is False
        assert result.safety_boundaries["synthetic_only"] is True
        assert result.safety_boundaries["fake_runtime_only"] is True

        # Test YAML matrix generation
        tmp_yaml = tmp_path / "matrix.yaml"
        gatekeeper.generate_matrix_yaml(tmp_yaml)
        assert tmp_yaml.exists()
        with open(tmp_yaml, "r", encoding="utf-8") as f:
            y_data = yaml.safe_load(f)
        assert y_data["phase"] == "Phase-104A"
        assert len(y_data["modules_catalog_50"]) == 50
        assert len(y_data["red_team_reports_catalog_20"]) == 20
        assert len(y_data["extended_scenarios_catalog_60"]) == 60

        # Test JSON summary generation
        tmp_json = tmp_path / "summary.json"
        gatekeeper.generate_compliance_summary_json(tmp_json)
        assert tmp_json.exists()
        with open(tmp_json, "r", encoding="utf-8") as f:
            j_data = json.load(f)
        assert j_data["phase"] == "Phase-104A"
        assert j_data["status"] == "PASS"
        assert j_data["system_statistics"]["total_modules"] == 50
        assert j_data["system_statistics"]["total_extended_scenarios"] == 60
