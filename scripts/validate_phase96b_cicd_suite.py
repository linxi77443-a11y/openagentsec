#!/usr/bin/env python3
"""
Phase-96B CI/CD Automated Security Regression & Verification Suite Validation Script
Path: scripts/validate_phase96b_cicd_suite.py

Verifies:
1. CLI trigger & argument parsing (Phase, Modules, Tags, Adapters).
2. Security Gate pass/fail conditions & exit code standardization (Pass=0, Gate Fail=1).
3. Full 75-entry / 750-entry batch regression execution & Checkpoint persistence.
4. Anti-drift assertions (corpus entry count, module uniformity, format reconciliation).
5. Markdown report generation (reports/phase96b_cicd_regression_report.md).
6. Strict safety boundary compliance (synthetic_only=True, confirmed_vulnerability=False, etc.).

Task ID: Phase-96B-CICD-003
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from scripts.run_phase96b_security_regression import Phase96BSecurityRegressionRunner
from core.full_corpus_loader import SAFE_BOUNDARIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("Phase96BCICDValidation")


def test_1_cli_trigger_and_filtering():
    """Test 1: CLI Trigger & Multi-Criteria Task Filtering (Modules M31, M35)."""
    logger.info("--- Running Test 1: CLI Trigger & Multi-Criteria Task Filtering ---")
    ckpt_path = "artifacts/batch_checkpoints/test_cicd_filter_ckpt.json"
    report_path = "reports/test_cicd_filter_report.md"

    runner = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=["M31", "M35"],
        target_adapter="openai",
        checkpoint_file=ckpt_path,
        output_report=report_path,
        min_pass_rate=100.0,
        max_failures=0,
        workspace_root=WORKSPACE_ROOT
    )

    exit_code, summary = runner.execute_regression_suite()

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
    assert summary["total_tasks"] == 150, f"Expected 150 tasks for M31 and M35, got {summary['total_tasks']}"
    assert summary["gate_overall_status"] == "PASS", f"Expected gate status PASS, got {summary['gate_overall_status']}"
    assert Path(WORKSPACE_ROOT / report_path).exists(), f"Report file {report_path} was not created"

    logger.info(f"PASS Test 1: Filtered execution for M31/M35 (150 tasks) exited with code {exit_code}.")


def test_2_security_gate_pass_fail_exit_codes():
    """Test 2: Security Gate Exit Code Standardization (Pass=0, Gate Fail=1)."""
    logger.info("--- Running Test 2: Security Gate Exit Code Standardization ---")

    # Scenario A: Passing Scenario (Exit Code 0)
    runner_pass = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=["M31"],
        checkpoint_file="artifacts/batch_checkpoints/test_gate_pass_ckpt.json",
        output_report="reports/test_gate_pass_report.md",
        min_pass_rate=100.0,
        max_failures=0,
        workspace_root=WORKSPACE_ROOT
    )
    code_pass, sum_pass = runner_pass.execute_regression_suite()
    assert code_pass == 0, f"Passing gate should return exit code 0, got {code_pass}"
    assert sum_pass["gate_overall_status"] == "PASS"

    # Scenario B: Failing Scenario - Artificial threshold breach (Exit Code 1)
    runner_fail = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=["M31"],
        checkpoint_file="artifacts/batch_checkpoints/test_gate_fail_ckpt.json",
        output_report="reports/test_gate_fail_report.md",
        min_pass_rate=101.0,  # Impossible threshold to force gate fail
        max_failures=0,
        workspace_root=WORKSPACE_ROOT
    )
    code_fail, sum_fail = runner_fail.execute_regression_suite()
    assert code_fail == 1, f"Failing gate should return exit code 1, got {code_fail}"
    assert sum_fail["gate_overall_status"] == "FAIL"

    logger.info("PASS Test 2: Security Gate exit codes strictly validated (Pass=0, Fail=1).")


def test_3_full_750_entry_regression_execution():
    """Test 3: Full 750-Entry Security Regression Execution & Report Verification."""
    logger.info("--- Running Test 3: Full 750-Entry Security Regression Suite ---")
    ckpt_path = "artifacts/batch_checkpoints/phase96b_cicd_checkpoint.json"
    report_path = "reports/phase96b_cicd_regression_report.md"

    runner = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=None,  # Run all 10 modules
        target_adapter="generic",
        checkpoint_file=ckpt_path,
        output_report=report_path,
        min_pass_rate=100.0,
        max_failures=0,
        workspace_root=WORKSPACE_ROOT
    )

    exit_code, summary = runner.execute_regression_suite()

    assert exit_code == 0, f"Full regression suite failed with exit code {exit_code}"
    assert summary["total_tasks"] == 750, f"Expected 750 total tasks, got {summary['total_tasks']}"
    assert summary["completed_total"] == 750, f"Expected 750 completed tasks, got {summary['completed_total']}"
    assert summary["failed_total"] == 0, f"Expected 0 failed tasks, got {summary['failed_total']}"
    assert summary["pass_rate_percent"] == 100.0, f"Expected 100% pass rate, got {summary['pass_rate_percent']}%"
    assert len(summary["module_breakdown"]) == 10, f"Expected 10 modules, got {len(summary['module_breakdown'])}"

    # Verify Report file existence and content
    report_file = WORKSPACE_ROOT / report_path
    assert report_file.exists(), f"Primary regression report {report_path} was not created"

    with open(report_file, "r", encoding="utf-8") as f:
        report_text = f.read()

    assert "Phase-96B CI/CD 自动化安全回归测试与门禁摘要报告" in report_text
    assert "Security Gate 门禁状态" in report_text
    assert "防漂移断言 (Anti-Drift Assertions) 校验结果" in report_text
    assert "M31" in report_text and "M46" in report_text

    logger.info("PASS Test 3: Full 750-entry regression suite executed and report verified.")


def test_4_anti_drift_assertions():
    """Test 4: Anti-Drift Assertions Verification (Entries, Uniformity, Reconciliation)."""
    logger.info("--- Running Test 4: Anti-Drift Assertions ---")
    runner = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=None,
        workspace_root=WORKSPACE_ROOT
    )
    exit_code, summary = runner.execute_regression_suite()

    checks = summary["anti_drift_checks"]
    assert len(checks) >= 4, f"Expected at least 4 anti-drift checks, got {len(checks)}"
    assert all(c["passed"] for c in checks), f"Some anti-drift assertions failed: {checks}"

    logger.info("PASS Test 4: All anti-drift assertions verified 100% PASS.")


def test_5_safety_boundary_compliance():
    """Test 5: Safety Boundary Compliance Verification."""
    logger.info("--- Running Test 5: Safety Boundary Compliance ---")
    runner = Phase96BSecurityRegressionRunner(
        phase="Phase-96B",
        modules=["M31"],
        workspace_root=WORKSPACE_ROOT
    )
    _, summary = runner.execute_regression_suite()

    sb = summary["safety_boundaries"]
    assert sb["confirmed_vulnerability"] is False, "confirmed_vulnerability must be False"
    assert sb["formal_finding_allowed"] is False, "formal_finding_allowed must be False"
    assert sb["production_safety_claimed"] is False, "production_safety_claimed must be False"
    assert sb["synthetic_only"] is True, "synthetic_only must be True"

    logger.info("PASS Test 5: Safety boundaries strictly compliant.")


def main():
    logger.info("============================================================")
    logger.info("Starting Phase-96B-CICD-003 Validation Suite")
    logger.info("============================================================")

    try:
        test_1_cli_trigger_and_filtering()
        test_2_security_gate_pass_fail_exit_codes()
        test_3_full_750_entry_regression_execution()
        test_4_anti_drift_assertions()
        test_5_safety_boundary_compliance()

        logger.info("============================================================")
        logger.info("ALL TESTS PASSED 100%! Phase-96B CI/CD Regression Suite Verified.")
        logger.info("============================================================")
        sys.exit(0)
    except AssertionError as e:
        logger.error(f"Validation assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
