"""
Unit and Integration Tests for Phase-96B CI/CD Security Regression Engine & Security Gate Suite.
Path: tests/test_phase96b_cicd_suite.py
"""

import os
import json
import pytest
from pathlib import Path
from typing import Dict, List, Any

from scripts.run_phase96b_security_regression import (
    Phase96BSecurityRegressionRunner,
    build_parser
)
from core.full_corpus_loader import SAFE_BOUNDARIES

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def tmp_cicd_paths(tmp_path):
    ckpt_file = tmp_path / "test_cicd_ckpt.json"
    report_file = tmp_path / "test_cicd_report.md"
    return str(ckpt_file), str(report_file)


def test_cli_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.phase == "Phase-96B"
    assert args.target_adapter == "generic"
    assert args.min_pass_rate == 100.0
    assert args.max_failures == 0
    assert args.strict_gate is True


def test_runner_filtered_execution(tmp_cicd_paths):
    ckpt, report = tmp_cicd_paths
    runner = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=["M31"],
        target_adapter="rest",
        checkpoint_file=ckpt,
        output_report=report,
        workspace_root=WORKSPACE_ROOT
    )

    exit_code, summary = runner.execute_regression_suite()

    assert exit_code == 0
    assert summary["total_tasks"] == 75
    assert summary["completed_total"] == 75
    assert summary["failed_total"] == 0
    assert summary["pass_rate_percent"] == 100.0
    assert summary["gate_overall_status"] == "PASS"
    assert Path(report).exists()


def test_security_gate_failure_on_unmet_threshold(tmp_cicd_paths):
    ckpt, report = tmp_cicd_paths
    runner = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=["M31"],
        checkpoint_file=ckpt,
        output_report=report,
        min_pass_rate=101.0,  # Impossible threshold
        max_failures=0,
        workspace_root=WORKSPACE_ROOT
    )

    exit_code, summary = runner.execute_regression_suite()

    assert exit_code == 1
    assert summary["gate_overall_status"] == "FAIL"


def test_anti_drift_assertions_structure(tmp_cicd_paths):
    ckpt, report = tmp_cicd_paths
    runner = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=["M31", "M32"],
        checkpoint_file=ckpt,
        output_report=report,
        workspace_root=WORKSPACE_ROOT
    )

    exit_code, summary = runner.execute_regression_suite()

    assert exit_code == 0
    checks = summary["anti_drift_checks"]
    assert len(checks) >= 3
    assert all(c["passed"] for c in checks)


def test_safety_boundaries_isolation(tmp_cicd_paths):
    ckpt, report = tmp_cicd_paths
    runner = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=["M31"],
        checkpoint_file=ckpt,
        output_report=report,
        workspace_root=WORKSPACE_ROOT
    )

    _, summary = runner.execute_regression_suite()

    sb = summary["safety_boundaries"]
    assert sb["confirmed_vulnerability"] is False
    assert sb["formal_finding_allowed"] is False
    assert sb["production_safety_claimed"] is False
    assert sb["synthetic_only"] is True
