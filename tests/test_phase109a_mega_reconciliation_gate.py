"""
tests/test_phase109a_mega_reconciliation_gate.py — Automated Unit & Integration Tests for Phase-109A-MEGA-001.
Path: tests/test_phase109a_mega_reconciliation_gate.py

Task: Phase-109A-MEGA-001
Task Name: Milestone 5.0 单智能体全景端到端大闭环对账门开发 (Milestone 5.0 Single-Agent Super Panoramic Mega Reconciliation Gate)
PRD References:
  - 原 PRD v1.0 §4, §5, §6, §7, §9, §10, §11, §13, §15
  - 攻击者视角新增章节 §2, §3, §4, §5, §6, §7, §8, §9, §11
  - PRD v2.0 §1, §4, §5, §6-§9, §10, §13
  - PRD v3.1 §1, §2.1-§2.8, §3, §4, §8, §9
"""

import json
import os
import pytest
import yaml
from pathlib import Path

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
    RealCredentialViolationError,
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
    HumanSignature,
    StepSkippingViolation,
    ProductionEnvironmentViolationError,
    UnilateralVulnerabilityEscalationError,
    ProductionSafetyClaimViolationError,
    NonSyntheticDataViolationError,
    STANDARD_ABORT_CONDITIONS,
    STANDARD_ROLLBACK_STEPS,
)

ROOT = Path(__file__).resolve().parent.parent


class TestPhase109AMegaReconciliation:
    """Test suite covering the Eight Pillars of Milestone 5.0 Mega Reconciliation Gatekeeper."""

    @pytest.fixture
    def gatekeeper(self):
        return Phase109AMegaReconciliationGate(root_dir=ROOT)

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

    # --------------------------------------------------------------------------
    # Pillar 3: 60 Frontier Adversarial Scenarios (Phase 101-103)
    # --------------------------------------------------------------------------
    def test_pillar_3_frontier_scenarios(self, gatekeeper):
        """Verify 60 frontier adversarial scenarios across Phase 101-103."""
        f_res = gatekeeper.reconcile_frontier_scenarios_p101_p103()
        assert f_res["total_frontier_cases"] == 60
        assert f_res["phase101_cases_count"] == 20
        assert f_res["phase102_cases_count"] == 20
        assert f_res["phase103_cases_count"] == 20
        assert f_res["attack_cases_count"] == 48
        assert f_res["control_cases_count"] == 12
        assert f_res["interceptions_count"] == 48
        assert f_res["controls_passed_count"] == 12
        assert f_res["breakthroughs_detected"] == 0
        assert f_res["boundary_preservation_rate"] == 1.0
        assert f_res["status"] == "PASS"

    # --------------------------------------------------------------------------
    # Pillar 4: 80 Single-Agent Scenarios (Phase 105-108)
    # --------------------------------------------------------------------------
    def test_pillar_4_single_agent_scenarios(self, gatekeeper):
        """Verify 80 single-agent advanced adversarial scenarios across Phase 105-108."""
        s_res = gatekeeper.reconcile_single_agent_scenarios_p105_p108()
        assert s_res["total_single_agent_cases"] == 80
        assert s_res["phase105_cases_count"] == 20
        assert s_res["phase106_cases_count"] == 20
        assert s_res["phase107_cases_count"] == 20
        assert s_res["phase108_cases_count"] == 20
        assert s_res["attack_cases_count"] == 64
        assert s_res["control_cases_count"] == 16
        assert s_res["interceptions_count"] == 64
        assert s_res["controls_passed_count"] == 16
        assert s_res["breakthroughs_detected"] == 0
        assert s_res["boundary_preservation_rate"] == 1.0
        assert s_res["status"] == "PASS"

    def test_grand_unified_140_scenarios_spectrum(self, gatekeeper):
        """Verify grand unified 140 adversarial scenarios spectrum (60 frontier + 80 single-agent)."""
        all_res = gatekeeper.reconcile_all_140_adversarial_scenarios()
        assert all_res["total_cases"] == 140
        assert all_res["total_frontier_cases"] == 60
        assert all_res["total_single_agent_cases"] == 80
        assert all_res["attack_cases_count"] == 112
        assert all_res["control_cases_count"] == 28
        assert all_res["interceptions_count"] == 112
        assert all_res["controls_passed_count"] == 28
        assert all_res["breakthroughs_detected"] == 0
        assert all_res["boundary_preservation_rate"] == 1.0
        assert all_res["status"] == "PASS"

    # --------------------------------------------------------------------------
    # Pillar 5: Attack Propagation Dynamics Engine
    # --------------------------------------------------------------------------
    def test_pillar_5_propagation_dynamics_invariants(self, gatekeeper):
        """Verify propagation dynamics layers, edges, Markov stochastic matrix row sums, and equations."""
        p_res = gatekeeper.reconcile_propagation_dynamics()
        assert p_res["total_layers"] == 4
        assert p_res["total_edge_types"] == 7
        assert p_res["markov_stochastic_valid"] is True
        assert p_res["pressure_equation_consistent"] is True
        assert p_res["path_degradation_consistent"] is True
        assert p_res["status"] == "PASS"

    # --------------------------------------------------------------------------
    # Pillar 6: 8-Node Controlled Replay Gatekeeper
    # --------------------------------------------------------------------------
    def test_pillar_6_8node_gatekeeper_workflow(self, gatekeeper):
        """Verify sequential approval workflow across Nodes 1 to 5 and abort/rollback structures."""
        g_res = gatekeeper.reconcile_8node_gatekeeper()
        assert g_res["statutory_nodes"] == 8
        assert g_res["sequential_flow_enforced"] is True
        assert g_res["role_signatures_verified"] is True
        assert g_res["step_skipping_blocked"] is True
        assert g_res["abort_conditions_count"] == 7
        assert g_res["rollback_steps_count"] == 5
        assert g_res["status"] == "PASS"

    # --------------------------------------------------------------------------
    # Pillar 7: Assessment Dashboard & Offline Report Pipeline
    # --------------------------------------------------------------------------
    def test_pillar_7_dashboard_and_offline_reports(self, gatekeeper):
        """Verify 4 dashboard views, offline HTML/Markdown exporter, and regex redaction."""
        d_res = gatekeeper.reconcile_dashboard_and_reports()
        assert d_res["total_views_verified"] == 4
        assert d_res["offline_self_contained"] is True
        assert d_res["data_redaction_verified"] is True
        assert d_res["zero_telemetry_guaranteed"] is True
        assert d_res["status"] == "PASS"

    # --------------------------------------------------------------------------
    # Pillar 8: 10 Final Known-Bad Anomaly Injections
    # --------------------------------------------------------------------------
    def test_pillar_8_known_bad_injections_100_percent_defense(self, gatekeeper):
        """Verify that all 10 Known-Bad injections (KB-109A-001 ~ KB-109A-010) are intercepted 100%."""
        kb_res = gatekeeper.execute_known_bad_injections()
        assert kb_res["total_scenarios_injected"] == 10
        assert kb_res["total_scenarios_intercepted"] == 10
        assert kb_res["interception_rate"] == 1.0
        assert kb_res["zero_unhandled_exceptions"] is True
        assert kb_res["status"] == "PASS"

    # --------------------------------------------------------------------------
    # Master Full Reconciliation Run & Snapshots
    # --------------------------------------------------------------------------
    def test_full_master_reconciliation_run(self, gatekeeper):
        """Verify end-to-end master reconciliation run and status across all eight pillars."""
        res = gatekeeper.run_full_reconciliation()
        assert isinstance(res, Phase109AMegaReconciliationResult)
        assert res.task_id == "Phase-109A-MEGA-001"
        assert res.milestone == "Milestone 5.0"
        assert res.status == "PASS"
        assert res.non_retroactivity_guarantee is True
        assert res.module_summary.status == "PASS"
        assert res.report_summary.status == "PASS"
        assert res.frontier_scenarios_summary.status == "PASS"
        assert res.single_agent_scenarios_summary.status == "PASS"
        assert res.all_adversarial_scenarios_summary.status == "PASS"
        assert res.propagation_summary.status == "PASS"
        assert res.gatekeeper_summary.status == "PASS"
        assert res.dashboard_summary.status == "PASS"
        assert res.known_bad_summary.status == "PASS"

    def test_matrix_yaml_and_compliance_json_generation(self, gatekeeper, tmp_path):
        """Verify YAML matrix and JSON master compliance snapshot generation in temporary test folder."""
        temp_yaml = tmp_path / "phase109a_mega_reconciliation_matrix.yaml"
        temp_json = tmp_path / "phase109a_master_compliance_summary.json"

        gatekeeper.generate_matrix_yaml(temp_yaml)
        gatekeeper.generate_compliance_summary_json(temp_json)

        assert temp_yaml.exists() and temp_yaml.stat().st_size > 1000
        assert temp_json.exists() and temp_json.stat().st_size > 500

        with open(temp_yaml, "r", encoding="utf-8") as f:
            y_data = yaml.safe_load(f)
        assert y_data["task_id"] == "Phase-109A-MEGA-001"
        assert y_data["milestone"] == "Milestone 5.0"
        assert len(y_data["all_adversarial_scenarios_catalog_140"]) == 140
        assert len(y_data["known_bad_defense_matrix_10"]) == 10

        with open(temp_json, "r", encoding="utf-8") as f:
            j_data = json.load(f)
        assert j_data["task_id"] == "Phase-109A-MEGA-001"
        assert j_data["milestone"] == "Milestone 5.0"
        assert j_data["system_statistics"]["total_adversarial_scenarios"] == 140
        assert j_data["system_statistics"]["known_bad_scenarios_intercepted"] == 10
