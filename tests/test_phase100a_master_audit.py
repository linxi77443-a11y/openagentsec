#!/usr/bin/env python3
"""
tests/test_phase100a_master_audit.py — Automated Pytest Suite for Phase-100A-AUDIT-003.
Path: tests/test_phase100a_master_audit.py

Task: Phase-100A-AUDIT-003
Task Name: 全系统 Milestone 3.1 终局超级独立审查与全盘健康度汇总套件开发
PRD References:
  - 原 PRD v1.0 §4, §6, §7, §10
  - 攻击者视角新增章节 §5, §7, §11
  - PRD v2.0 §4, §10, §13
  - PRD v3.1 §1, §2, §3, §4
"""

import json
import logging
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

from multi_agent.agents.milestone_master_auditor import (
    MilestoneMasterAuditor,
    MasterAuditResult,
    PillarAuditResult,
    AUDITOR_SAFETY_BOUNDARIES,
    CANONICAL_50_MODULES,
    CANONICAL_20_REPORTS,
    STATUTORY_10_KNOWN_BAD,
)
from scripts.run_phase100a_master_audit import main as runner_main


class TestMasterAuditDeliverablesExistence:
    """Test presence and non-emptiness of all required Phase-100A-AUDIT-003 deliverables."""

    def test_all_deliverables_exist_and_non_empty(self):
        deliverables = [
            ROOT / "multi_agent/agents/milestone_master_auditor.py",
            ROOT / "docs/milestone_3_1_master_audit_report.md",
            ROOT / "milestone_3_1_system_health_scorecard.yaml",
            ROOT / "milestone_3_1_gap_closure_verdict.json",
            ROOT / "scripts/run_phase100a_master_audit.py",
            ROOT / "tests/test_phase100a_master_audit.py",
            ROOT / "phase100a_audit003_execution_summary.yaml",
        ]
        for item in deliverables:
            assert item.exists(), f"Missing required deliverable: {item.name}"
            assert item.stat().st_size > 0, f"Deliverable is empty: {item.name}"


class TestMasterAuditorEnginePillars:
    """Test MilestoneMasterAuditor engine 6-pillar verification logic and health scoring."""

    @pytest.fixture
    def auditor(self) -> MilestoneMasterAuditor:
        return MilestoneMasterAuditor(root_dir=ROOT)

    def test_pillar_1_modules(self, auditor: MilestoneMasterAuditor):
        p1 = auditor.audit_pillar_1_modules()
        print(p1.details); assert p1.status == "PASS"
        assert p1.score == 20.0
        assert p1.max_score == 20.0
        assert p1.checks_failed == 0
        assert p1.metrics["total_modules"] == 50
        assert p1.metrics["synthetic_only_rate"] == 1.0
        assert p1.metrics["fake_runtime_rate"] == 1.0

    def test_pillar_2_red_team_reports(self, auditor: MilestoneMasterAuditor):
        p2 = auditor.audit_pillar_2_red_team_reports()
        assert p2.status == "PASS"
        assert p2.score == 15.0
        assert p2.max_score == 15.0
        assert p2.checks_failed == 0
        assert p2.metrics["total_reports_audited"] == 20
        assert p2.metrics["total_breakthroughs"] == 0
        assert p2.metrics["candidate_level_rate"] == 1.0

    def test_pillar_3_propagation_dynamics(self, auditor: MilestoneMasterAuditor):
        p3 = auditor.audit_pillar_3_propagation_dynamics()
        assert p3.status == "PASS"
        assert p3.score == 15.0
        assert p3.max_score == 15.0
        assert p3.checks_failed == 0
        assert p3.metrics["total_security_layers"] == 4
        assert p3.metrics["total_edge_types"] == 7
        assert p3.metrics["markov_row_sums_equal_1"] is True

    def test_pillar_4_gatekeeper_8node(self, auditor: MilestoneMasterAuditor):
        p4 = auditor.audit_pillar_4_gatekeeper_8node()
        assert p4.status == "PASS"
        assert p4.score == 15.0
        assert p4.max_score == 15.0
        assert p4.checks_failed == 0
        assert p4.metrics["statutory_nodes_count"] == 8
        assert p4.metrics["step_skipping_blocked"] is True
        assert p4.metrics["abort_conditions_count"] == 7
        assert p4.metrics["rollback_steps_count"] == 5

    def test_pillar_5_known_bad_defenses(self, auditor: MilestoneMasterAuditor):
        p5 = auditor.audit_pillar_5_known_bad_defenses()
        assert p5.status == "PASS"
        assert p5.score == 15.0
        assert p5.max_score == 15.0
        assert p5.checks_failed == 0
        assert p5.metrics["total_scenarios_injected"] == 10
        assert p5.metrics["total_scenarios_intercepted"] == 10
        assert p5.metrics["interception_rate"] == 1.0

    def test_pillar_6_static_code_and_axioms(self, auditor: MilestoneMasterAuditor):
        p6 = auditor.audit_pillar_6_static_code_and_axioms()
        assert p6.status == "PASS"
        assert p6.score == 20.0
        assert p6.max_score == 20.0
        assert p6.checks_failed == 0
        assert p6.metrics["zero_real_credentials"] is True
        assert p6.metrics["non_retroactivity_preserved"] is True

    def test_run_full_audit_score_and_verdict(self, auditor: MilestoneMasterAuditor):
        res = auditor.run_full_audit()
        assert res.overall_health_score == 100.0
        assert res.max_health_score == 100.0
        assert res.total_checks_failed == 0
        assert res.open_gaps_count == 0
        assert res.violations_count == 0
        assert res.verdict == "VERDICT_MILESTONE_3_1_PASSED_CERTIFIED"


class TestSystemHealthScorecardYaml:
    """Test schema and invariant content in milestone_3_1_system_health_scorecard.yaml."""

    @pytest.fixture
    def scorecard_data(self) -> Dict[str, Any]:
        path = ROOT / "milestone_3_1_system_health_scorecard.yaml"
        assert path.exists()
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_scorecard_metadata(self, scorecard_data: Dict[str, Any]):
        meta = scorecard_data.get("scorecard_metadata", {})
        assert meta.get("release_version") == "v3.1"
        assert meta.get("verdict") == "VERDICT_MILESTONE_3_1_PASSED_CERTIFIED"
        assert "100.0" in str(meta.get("overall_health_score"))
        assert meta.get("open_gaps") == 0
        assert meta.get("violations_detected") == 0

    def test_scorecard_all_6_pillars_pass(self, scorecard_data: Dict[str, Any]):
        pillars = scorecard_data.get("pillar_scorecards", {})
        assert len(pillars) == 6
        for pid, pmeta in pillars.items():
            assert pmeta.get("status") == "PASS"
            assert pmeta.get("score") == pmeta.get("max_score")
            assert pmeta.get("checks_failed") == 0

    def test_scorecard_50_modules_pass(self, scorecard_data: Dict[str, Any]):
        mods = scorecard_data.get("canonical_50_modules_status", {})
        assert len(mods) == 50
        for mod_id, meta in mods.items():
            assert meta.get("status") == "PASS"

    def test_scorecard_20_reports_pass(self, scorecard_data: Dict[str, Any]):
        reps = scorecard_data.get("canonical_20_reports_status", {})
        assert len(reps) == 20
        for rep_id, meta in reps.items():
            assert meta.get("status") in ["closed/judge_approved", "closed"]
            assert meta.get("breakthroughs") == 0


class TestGapClosureVerdictJson:
    """Test schema and formal declarations in milestone_3_1_gap_closure_verdict.json."""

    @pytest.fixture
    def verdict_data(self) -> Dict[str, Any]:
        path = ROOT / "milestone_3_1_gap_closure_verdict.json"
        assert path.exists()
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_verdict_content(self, verdict_data: Dict[str, Any]):
        assert verdict_data.get("release_version") == "v3.1"
        assert verdict_data.get("formal_verdict") == "VERDICT_MILESTONE_3_1_PASSED_CERTIFIED"
        assert verdict_data.get("overall_health_score") == 100.0
        assert verdict_data.get("total_checks_failed") == 0
        gap_status = verdict_data.get("gap_closure_status", {})
        assert gap_status.get("active_gaps_count") == 0
        assert gap_status.get("gap_closure_rate") == 1.0
        assert gap_status.get("zero_hang_verified") is True


class TestSafetyBoundariesAndAssertions:
    """Test strict safety declarations and credential sanitization."""

    def test_negative_safety_flags_strictly_false(self):
        verdict_path = ROOT / "milestone_3_1_gap_closure_verdict.json"
        with open(verdict_path, "r", encoding="utf-8") as f:
            v = json.load(f)
        b = v.get("safety_boundaries", {})
        assert b.get("confirmed_vulnerability") is False
        assert b.get("formal_finding_allowed") is False
        assert b.get("production_safety_claimed") is False
        assert b.get("controlled_replay_claimed") is False
        assert b.get("controlled_replay_execution_allowed") is False
        assert b.get("assessment_execution_performed") is False

    def test_positive_safety_flags_strictly_true(self):
        verdict_path = ROOT / "milestone_3_1_gap_closure_verdict.json"
        with open(verdict_path, "r", encoding="utf-8") as f:
            v = json.load(f)
        b = v.get("safety_boundaries", {})
        assert b.get("synthetic_only") is True
        assert b.get("fake_runtime_only") is True
        assert b.get("requires_human_review") is True
        assert b.get("all_findings_are_candidate") is True
        assert b.get("red_team_engine_not_executable") is True
        assert b.get("dashboard_not_execution_interface") is True
        assert b.get("theory_model_is_not_detection_rule") is True
        assert b.get("non_retroactivity_guarantee") is True
        assert b.get("zero_production_penetration") is True

    def test_zero_real_credentials_in_audit_artifacts(self):
        files_to_check = [
            ROOT / "docs/milestone_3_1_master_audit_report.md",
            ROOT / "milestone_3_1_system_health_scorecard.yaml",
            ROOT / "milestone_3_1_gap_closure_verdict.json",
        ]
        for f in files_to_check:
            text = f.read_text(encoding="utf-8")
            assert "sk-proj-" not in text
            assert "AKIA" not in text
            assert "-----BEGIN RSA PRIVATE KEY-----" not in text


class TestRunnerScriptExecution:
    """Test that scripts/run_phase100a_master_audit.py runs cleanly with returncode 0."""

    def test_runner_main_returns_zero(self):
        ret = runner_main()
        assert ret == 0
