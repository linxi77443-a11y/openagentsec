#!/usr/bin/env python3
"""
tests/test_phase109a_master_audit.py — Automated Pytest Suite for Phase-109A-AUDIT-003.
Path: tests/test_phase109a_master_audit.py

Task: Phase-109A-AUDIT-003
Task Name: 全系统 Milestone 5.0 终局 360 度超级独立审查与全盘健康度汇总套件开发 (Milestone 5.0 Master 360-Degree Independent Master Audit & Health Scorecard)
Task Type: design_gate
Evaluation Mode: not_applicable
PRD References:
  - 原 PRD v1.0 §5, §6, §10, §13
  - 攻击者视角新增章节 §2, §4, §5, §6, §11
  - PRD v2.0 §1, §4, §10, §13
  - PRD v3.1 §1, §3, §4, §9
  - Milestone 5.0 Super Panoramic Closed-Loop
"""

import json
import logging
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from multi_agent.agents.milestone_5_0_master_auditor import (
    Milestone5MasterAuditor,
    MasterAuditResult,
    PillarAuditResult,
    AUDITOR_SAFETY_BOUNDARIES,
    CANONICAL_50_MODULES,
    CANONICAL_20_REPORTS,
    EXTENDED_60_SCENARIOS_CATALOG,
    SINGLE_AGENT_80_SCENARIOS_CATALOG,
    STATUTORY_10_KNOWN_BAD,
)
from scripts.run_phase109a_master_audit import main as runner_main


class TestMasterAuditDeliverablesExistence:
    """Test presence and non-emptiness of all required Phase-109A-AUDIT-003 deliverables."""

    def test_all_deliverables_exist_and_non_empty(self):
        deliverables = [
            ROOT / "multi_agent/agents/milestone_5_0_master_auditor.py",
            ROOT / "docs/milestone_5_0_master_audit_report.md",
            ROOT / "milestone_5_0_system_health_scorecard.yaml",
            ROOT / "milestone_5_0_gap_closure_verdict.json",
            ROOT / "scripts/run_phase109a_master_audit.py",
            ROOT / "tests/test_phase109a_master_audit.py",
            ROOT / "phase109a_audit003_execution_summary.yaml",
        ]
        for item in deliverables:
            assert item.exists(), f"Missing required deliverable: {item.name}"
            assert item.stat().st_size > 0, f"Deliverable is empty: {item.name}"


class TestMasterAuditorEnginePillars:
    """Test Milestone5MasterAuditor engine 10-pillar verification logic and health scoring."""

    @pytest.fixture
    def auditor(self) -> Milestone5MasterAuditor:
        return Milestone5MasterAuditor(root_dir=ROOT)

    def test_pillar_1_modules(self, auditor: Milestone5MasterAuditor):
        p1 = auditor.audit_pillar_1_modules()
        assert p1.status == "PASS"
        assert p1.score == 10.0
        assert p1.max_score == 10.0
        assert p1.checks_failed == 0
        assert p1.metrics["total_modules"] == 50
        assert p1.metrics["p0_count"] == 23
        assert p1.metrics["p1_count"] == 13
        assert p1.metrics["p2_count"] == 6
        assert p1.metrics["v2_count"] == 8
        assert p1.metrics["synthetic_only_rate"] == 1.0
        assert p1.metrics["fake_runtime_rate"] == 1.0

    def test_pillar_2_red_team_reports(self, auditor: Milestone5MasterAuditor):
        p2 = auditor.audit_pillar_2_red_team_reports()
        assert p2.status == "PASS"
        assert p2.score == 10.0
        assert p2.max_score == 10.0
        assert p2.checks_failed == 0
        assert p2.metrics["total_reports_audited"] == 20
        assert p2.metrics["total_breakthroughs"] == 0
        assert p2.metrics["candidate_level_rate"] == 1.0

    def test_pillar_3_extended_frontier_scenarios(self, auditor: Milestone5MasterAuditor):
        p3 = auditor.audit_pillar_3_extended_frontier_scenarios()
        assert p3.status == "PASS"
        assert p3.score == 10.0
        assert p3.max_score == 10.0
        assert p3.checks_failed == 0
        assert p3.metrics["total_frontier_scenarios"] == 60
        assert p3.metrics["total_attack_cases"] == 48
        assert p3.metrics["total_control_cases"] == 12
        assert p3.metrics["total_interceptions"] == 48
        assert p3.metrics["total_controls_passed"] == 12
        assert p3.metrics["total_breakthroughs"] == 0
        assert p3.metrics["boundary_preservation_rate"] == 1.0

    def test_pillar_4_single_agent_scenarios(self, auditor: Milestone5MasterAuditor):
        p4 = auditor.audit_pillar_4_single_agent_scenarios()
        assert p4.status == "PASS"
        assert p4.score == 10.0
        assert p4.max_score == 10.0
        assert p4.checks_failed == 0
        assert p4.metrics["total_single_agent_scenarios"] == 80
        assert p4.metrics["total_attack_cases"] == 64
        assert p4.metrics["total_control_cases"] == 16
        assert p4.metrics["total_interceptions"] == 64
        assert p4.metrics["total_controls_passed"] == 16
        assert p4.metrics["total_breakthroughs"] == 0
        assert p4.metrics["boundary_preservation_rate"] == 1.0

    def test_pillar_5_unified_140_adversarial_graph(self, auditor: Milestone5MasterAuditor):
        p5 = auditor.audit_pillar_5_unified_140_adversarial_graph()
        assert p5.status == "PASS"
        assert p5.score == 10.0
        assert p5.max_score == 10.0
        assert p5.checks_failed == 0
        assert p5.metrics["total_scenarios"] == 140
        assert p5.metrics["frontier_scenarios"] == 60
        assert p5.metrics["single_agent_scenarios"] == 80
        assert p5.metrics["total_attack_cases"] == 112
        assert p5.metrics["total_control_cases"] == 28
        assert p5.metrics["total_interceptions"] == 112
        assert p5.metrics["total_controls_passed"] == 28
        assert p5.metrics["total_breakthroughs"] == 0
        assert p5.metrics["boundary_preservation_rate"] == 1.0

    def test_pillar_6_propagation_dynamics(self, auditor: Milestone5MasterAuditor):
        p6 = auditor.audit_pillar_6_propagation_dynamics()
        assert p6.status == "PASS"
        assert p6.score == 10.0
        assert p6.max_score == 10.0
        assert p6.checks_failed == 0
        assert p6.metrics["total_security_layers"] == 4
        assert p6.metrics["total_edge_types"] == 7
        assert p6.metrics["markov_5state_stochastic_verified"] is True
        assert p6.metrics["markov_row_sums_equal_1"] is True
        assert p6.metrics["p_edge_equation_consistent"] is True
        assert p6.metrics["d_node_state_step_consistent"] is True
        assert p6.metrics["g_path_degradation_consistent"] is True

    def test_pillar_7_gatekeeper_8node(self, auditor: Milestone5MasterAuditor):
        p7 = auditor.audit_pillar_7_gatekeeper_8node()
        assert p7.status == "PASS"
        assert p7.score == 10.0
        assert p7.max_score == 10.0
        assert p7.checks_failed == 0
        assert p7.metrics["statutory_nodes_count"] == 8
        assert p7.metrics["step_skipping_blocked"] is True
        assert p7.metrics["abort_conditions_count"] == 7
        assert p7.metrics["rollback_steps_count"] == 5

    def test_pillar_8_dashboard_and_reports(self, auditor: Milestone5MasterAuditor):
        p8 = auditor.audit_pillar_8_dashboard_and_reports()
        assert p8.status == "PASS"
        assert p8.score == 10.0
        assert p8.max_score == 10.0
        assert p8.checks_failed == 0
        assert p8.metrics["total_views_verified"] == 4
        assert p8.metrics["offline_self_contained"] is True
        assert p8.metrics["dlp_data_redaction_verified"] is True
        assert p8.metrics["zero_outbound_telemetry"] is True

    def test_pillar_9_known_bad_defenses(self, auditor: Milestone5MasterAuditor):
        p9 = auditor.audit_pillar_9_known_bad_defenses()
        assert p9.status == "PASS"
        assert p9.score == 10.0
        assert p9.max_score == 10.0
        assert p9.checks_failed == 0
        assert p9.metrics["total_scenarios_injected"] == 10
        assert p9.metrics["total_scenarios_intercepted"] == 10
        assert p9.metrics["interception_rate"] == 1.0
        assert p9.metrics["unhandled_exceptions_count"] == 0

    def test_pillar_10_static_axioms_and_gap_closure(self, auditor: Milestone5MasterAuditor):
        p10 = auditor.audit_pillar_10_static_axioms_and_gap_closure()
        assert p10.status == "PASS"
        assert p10.score == 10.0
        assert p10.max_score == 10.0
        assert p10.checks_failed == 0
        assert p10.metrics["zero_real_credentials"] is True
        assert p10.metrics["mandatory_negative_flags_verified"] == 6
        assert p10.metrics["mandatory_positive_flags_verified"] == 10
        assert p10.metrics["open_gaps_count"] == 0
        assert p10.metrics["gap_closure_rate"] == 1.0


class TestMasterAuditFullRunAndScoring:
    """Test full system audit execution, health scoring calculation, and formal certification."""

    @pytest.fixture
    def auditor(self) -> Milestone5MasterAuditor:
        return Milestone5MasterAuditor(root_dir=ROOT)

    def test_full_audit_scoring_and_verdict(self, auditor: Milestone5MasterAuditor):
        result = auditor.run_full_audit()
        assert math.isclose(result.overall_health_score, 100.0, rel_tol=1e-5)
        assert math.isclose(result.max_health_score, 100.0, rel_tol=1e-5)
        assert result.verdict == "VERDICT_MILESTONE_5_0_PASSED_CERTIFIED"
        assert result.total_checks_failed == 0
        assert result.open_gaps_count == 0
        assert result.violations_count == 0
        assert len(result.pillars) == 10

        for pid, p in result.pillars.items():
            assert p.status == "PASS"
            assert p.score == 10.0
            assert p.max_score == 10.0
            assert p.checks_failed == 0


class TestArtifactGenerationAndIntegrity:
    """Test generated Scorecard, Verdict JSON, and Master Audit Markdown Report."""

    @pytest.fixture
    def auditor(self) -> Milestone5MasterAuditor:
        return Milestone5MasterAuditor(root_dir=ROOT)

    def test_scorecard_yaml_content(self, auditor: Milestone5MasterAuditor, tmp_path: Path):
        result = auditor.run_full_audit()
        target = tmp_path / "test_scorecard.yaml"
        auditor.generate_scorecard_yaml(result, target)
        assert target.exists()

        with open(target, "r", encoding="utf-8") as f:
            sc_data = yaml.safe_load(f)

        assert sc_data["scorecard_metadata"]["verdict"] == "VERDICT_MILESTONE_5_0_PASSED_CERTIFIED"
        assert "100.0" in sc_data["scorecard_metadata"]["overall_health_score"]
        assert sc_data["scorecard_metadata"]["open_gaps"] == 0
        assert sc_data["scorecard_metadata"]["violations_detected"] == 0
        assert len(sc_data["pillar_scorecards"]) == 10
        assert len(sc_data["canonical_50_modules_status"]) == 50
        assert len(sc_data["canonical_20_reports_status"]) == 20
        assert len(sc_data["extended_60_frontier_scenarios_status"]) == 3
        assert len(sc_data["single_agent_80_scenarios_status"]) == 4
        assert len(sc_data["known_bad_defenses_interception_summary"]) == 10

    def test_verdict_json_content(self, auditor: Milestone5MasterAuditor, tmp_path: Path):
        result = auditor.run_full_audit()
        target = tmp_path / "test_verdict.json"
        auditor.generate_verdict_json(result, target)
        assert target.exists()

        with open(target, "r", encoding="utf-8") as f:
            v_data = json.load(f)

        assert v_data["formal_verdict"] == "VERDICT_MILESTONE_5_0_PASSED_CERTIFIED"
        assert v_data["overall_health_score"] == 100.0
        assert v_data["gap_closure_status"]["active_gaps_count"] == 0
        assert v_data["gap_closure_status"]["gap_closure_rate"] == 1.0
        assert len(v_data["pillar_conclusions"]) == 10

    def test_audit_report_md_content(self, auditor: Milestone5MasterAuditor, tmp_path: Path):
        result = auditor.run_full_audit()
        target = tmp_path / "test_report.md"
        auditor.generate_audit_report_md(result, target)
        assert target.exists()

        text = target.read_text(encoding="utf-8")
        assert "Milestone 5.0 终局 360 度超级独立审查报告与全盘健康度裁决书" in text
        assert "VERDICT_MILESTONE_5_0_PASSED_CERTIFIED" in text
        assert "十大核心审查支柱详尽审计结论" in text
        assert "Pillar 1" in text
        assert "Pillar 10" in text


class TestRunnerScriptExecution:
    """Test run_phase109a_master_audit runner entrypoint."""

    def test_runner_main_return_zero(self):
        exit_code = runner_main()
        assert exit_code == 0
