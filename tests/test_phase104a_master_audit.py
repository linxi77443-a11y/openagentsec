"""
tests/test_phase104a_master_audit.py
Phase 104A Milestone 4.0 Master Audit — System Health Scorecard & Gap Closure Verdict.

Task: Phase-104A-AUDIT-003
Task Name: 阶段 104 主审计与里程碑 4.0 认证

Test Coverage:
1. System Health Scorecard YAML (v4.0): metadata, 7 pillars, 50 modules, 20 reports, 3 extended scenarios.
2. Gap Closure Verdict JSON (v4.0): formal verdict content.
3. Safety Boundaries & Assertions: negative flags strictly false, positive flags strictly true.
4. Runner Script Execution: main() returns 0.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent

SCORECARD_PATH = ROOT / "milestone_4_0_system_health_scorecard.yaml"
VERDICT_PATH = ROOT / "milestone_4_0_gap_closure_verdict.json"
RUNNER_PATH = ROOT / "scripts/run_phase104a_master_audit.py"


def _load_scorecard():
    with open(SCORECARD_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_verdict():
    with open(VERDICT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestSystemHealthScorecardYaml:
    def test_scorecard_metadata(self):
        assert SCORECARD_PATH.exists(), "milestone_4_0_system_health_scorecard.yaml must exist"
        sc = _load_scorecard()
        md = sc.get("scorecard_metadata", {})
        assert md.get("release_version") == "v4.0", f"Expected v4.0, got {md.get('release_version')}"
        assert md.get("document_type"), "document_type must be present"

    def test_scorecard_all_7_pillars_pass(self):
        sc = _load_scorecard()
        pillars = sc.get("pillar_scorecards", {})
        assert isinstance(pillars, dict), "pillar_scorecards must be a mapping"
        assert len(pillars) == 7, f"Expected 7 pillars, got {len(pillars)}"
        passed = sum(1 for p in pillars.values() if (p or {}).get("status") == "PASS")
        assert passed == 7, f"{passed}/7 pillars PASS"

    def test_scorecard_50_modules_pass(self):
        sc = _load_scorecard()
        modules = sc.get("canonical_50_modules_status", {})
        assert isinstance(modules, dict), "canonical_50_modules_status must be a mapping"
        assert len(modules) == 50, f"Expected 50 modules, got {len(modules)}"
        passed = sum(1 for m in modules.values() if (m or {}).get("status") == "PASS")
        assert passed == 50, f"{passed}/50 modules PASS"

    def test_scorecard_20_reports_pass(self):
        sc = _load_scorecard()
        reports = sc.get("canonical_20_reports_status", {})
        assert isinstance(reports, dict), "canonical_20_reports_status must be a mapping"
        assert len(reports) == 20, f"Expected 20 reports, got {len(reports)}"
        passed = sum(1 for r in reports.values() if (r or {}).get("status") == "PASS")
        assert passed == 20, f"{passed}/20 reports PASS"

    def test_scorecard_extended_scenarios_pass(self):
        sc = _load_scorecard()
        extended = sc.get("extended_60_frontier_scenarios_status", sc.get("extended_scenarios_status", {}))
        assert isinstance(extended, dict), "extended scenarios status must be a mapping"
        assert len(extended) == 3, f"Expected 3 extended scenarios, got {len(extended)}"
        passed = sum(1 for e in extended.values() if (e or {}).get("status") == "PASS")
        assert passed == 3, f"{passed}/3 extended scenarios PASS"


class TestGapClosureVerdictJson:
    def test_verdict_content(self):
        assert VERDICT_PATH.exists(), "milestone_4_0_gap_closure_verdict.json must exist"
        v = _load_verdict()
        assert v.get("release_version") == "v4.0", f"Expected v4.0, got {v.get('release_version')}"
        assert v.get("formal_verdict") in (
            "MILESTONE_4_0_CERTIFIED", "MASTER_AUDIT_PASS", "ALL_CHECKS_PASSED",
        ), f"Unexpected formal verdict: {v.get('formal_verdict')}"
        assert v.get("total_checks_failed") == 0


class TestSafetyBoundariesAndAssertions:
    def test_negative_safety_flags_strictly_false(self):
        sc = _load_scorecard()
        sd = sc.get("safety_declarations", {})
        negative_flags = [
            "confirmed_vulnerability",
            "formal_finding_allowed",
            "production_safety_claimed",
            "controlled_replay_claimed",
            "controlled_replay_execution_allowed",
            "assessment_execution_performed",
        ]
        for flag in negative_flags:
            assert sd.get(flag) is False, f"{flag} must be strictly False, got {sd.get(flag)}"

    def test_positive_safety_flags_strictly_true(self):
        sc = _load_scorecard()
        sd = sc.get("safety_declarations", {})
        positive_flags = [
            "synthetic_only",
            "fake_runtime_only",
            "requires_human_review",
        ]
        for flag in positive_flags:
            assert sd.get(flag) is True, f"{flag} must be strictly True, got {sd.get(flag)}"


class TestRunnerScriptExecution:
    def test_runner_main_returns_zero(self):
        assert RUNNER_PATH.exists(), "run_phase104a_master_audit.py must exist"
        res = subprocess.run(
            [sys.executable, str(RUNNER_PATH)],
            capture_output=True, text=True, timeout=600,
        )
        assert res.returncode == 0, (
            f"Runner exited {res.returncode}:\n{res.stdout[-2000:]}\n{res.stderr[-2000:]}"
        )
