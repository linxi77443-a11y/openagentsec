#!/usr/bin/env python3
"""
scripts/run_phase104a_master_audit.py — Milestone 4.0 Third-Party Super Independent Audit Automation Runner.
Path: scripts/run_phase104a_master_audit.py

Task: Phase-104A-AUDIT-003
Task Name: 全系统 Milestone 4.0 终局 360 度超级独立审查与全盘健康度汇总套件开发
PRD References:
  - 原 PRD v1.0 §4, §6, §7, §10
  - 攻击者视角新增章节 §5, §7, §11
  - PRD v2.0 §4, §10, §13
  - PRD v3.1 §1, §2, §3, §4
  - Milestone 4.0 Super Panoramic Closed-Loop

Usage:
    python3 scripts/run_phase104a_master_audit.py
"""

import json
import logging
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from multi_agent.agents.milestone_4_0_master_auditor import (
    Milestone4MasterAuditor,
    MasterAuditResult,
    AUDITOR_SAFETY_BOUNDARIES,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Phase104AMasterAuditRunner")


def run_and_verify_master_audit() -> int:
    logger.info("================================================================================")
    logger.info("  🚀 Starting Phase 104A Master Independent Audit & Health Suite Verification")
    logger.info("================================================================================")

    auditor = Milestone4MasterAuditor(root_dir=ROOT)
    result: MasterAuditResult = auditor.run_full_audit()

    # Log each pillar result
    for pid, p in result.pillars.items():
        icon = "✓" if p.status == "PASS" else "✗"
        logger.info(f"  {icon} [{p.pillar_id}] {p.pillar_name} -> Score: {p.score}/{p.max_score} (Checks: {p.checks_passed}/{p.checks_total})")
        for detail in p.details:
            logger.info(f"      • {detail}")

    # Generate / write artifacts
    scorecard_path = ROOT / "milestone_4_0_system_health_scorecard.yaml"
    verdict_path = ROOT / "milestone_4_0_gap_closure_verdict.json"
    report_path = ROOT / "docs" / "milestone_4_0_master_audit_report.md"

    auditor.generate_scorecard_yaml(result, scorecard_path)
    auditor.generate_verdict_json(result, verdict_path)
    auditor.generate_audit_report_md(result, report_path)

    # Verification Checks on generated artifacts
    verification_passed = True

    # 1. Verify Scorecard exists and score == 100.0
    if scorecard_path.exists() and scorecard_path.stat().st_size > 0:
        with open(scorecard_path, "r", encoding="utf-8") as f:
            sc_data = yaml.safe_load(f) or {}
        sc_score = sc_data.get("scorecard_metadata", {}).get("overall_health_score", "")
        sc_pillars = sc_data.get("pillar_scorecards", {})
        if "100.0" in str(sc_score) and len(sc_pillars) == 7:
            logger.info("  ✓ [VERIFY_SCORECARD] Scorecard exists, 7 pillars verified, and Health Score is 100.0/100.0")
        else:
            logger.error(f"  ✗ [VERIFY_SCORECARD] Scorecard health score mismatch: {sc_score}, pillars: {len(sc_pillars)}")
            verification_passed = False
    else:
        logger.error("  ✗ [VERIFY_SCORECARD] Scorecard file missing or empty")
        verification_passed = False

    # 2. Verify Verdict JSON exists and verdict matches
    if verdict_path.exists() and verdict_path.stat().st_size > 0:
        with open(verdict_path, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        if v_data.get("formal_verdict") in ("MILESTONE_4_0_CERTIFIED", "MASTER_AUDIT_PASS", "ALL_CHECKS_PASSED"):
            logger.info("  ✓ [VERIFY_VERDICT] Verdict JSON certified with 0 active gaps and formal certification")
        else:
            logger.error(f"  ✗ [VERIFY_VERDICT] Formal verdict mismatch: {v_data.get('formal_verdict')}")
            verification_passed = False
    else:
        logger.error("  ✗ [VERIFY_VERDICT] Verdict JSON file missing or empty")
        verification_passed = False

    # 3. Verify Report MD exists and contains key sections
    if report_path.exists() and report_path.stat().st_size > 0:
        rep_text = report_path.read_text(encoding="utf-8")
        if "Milestone 4.0 终局 360 度超级独立审查报告与全盘健康度裁决书" in rep_text and "七大核心审查支柱详尽审计结论" in rep_text:
            logger.info("  ✓ [VERIFY_REPORT] Master audit markdown report complete and valid")
        else:
            logger.error("  ✗ [VERIFY_REPORT] Master audit report missing key headers")
            verification_passed = False
    else:
        logger.error("  ✗ [VERIFY_REPORT] Master audit report file missing or empty")
        verification_passed = False

    # 4. Final summary
    logger.info("================================================================================")
    logger.info(f"  Overall Health Score: {result.overall_health_score} / {result.max_health_score}")
    logger.info(f"  Checks: {result.total_checks_passed} Passed, {result.total_checks_failed} Failed")
    logger.info(f"  Active GAPs: {result.open_gaps_count}, Safety Violations: {result.violations_count}")
    logger.info(f"  Formal Verdict: {result.verdict}")
    logger.info("================================================================================")

    if verification_passed and result.total_checks_failed == 0 and math.isclose(result.overall_health_score, 100.0, rel_tol=1e-5):
        logger.info("  🏆 [MASTER AUDIT SUCCESS] ALL 7 DIMENSIONS 100% PASS — MILESTONE 4.0 CERTIFIED")
        return 0
    else:
        logger.error("  🚨 [MASTER AUDIT FAILURE] Verification failed or score < 100.0")
        return 1


def main() -> int:
    return run_and_verify_master_audit()


if __name__ == "__main__":
    sys.exit(main())
