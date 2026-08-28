#!/usr/bin/env python3
"""Validate Phase 33 Remediation & Retest Packages.

Performs 24 static checks on the generated remediation and retest packages.
No network calls, no credential access, no API execution.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REM_DIR = ROOT / "remediation_packages"
RET_DIR = ROOT / "retest_packages"

# ── Expected files ─────────────────────────────────────────────────────

REMEDIATION_FILES = [
    "README.md",
    "remediation_package_schema.md",
    "remediation_package_index.yaml",
    "remediation_generation_boundary.md",
    "remediation_task_board.yaml",
    "remediation_task_board.md",
    "generated/system_prompt_leakage_remediation_package.md",
    "generated/sensitive_information_disclosure_remediation_package.md",
    "generated/rag_knowledge_boundary_remediation_package.md",
    "generated/prompt_injection_bypass_remediation_package.md",
    "generated/api_boundary_authorization_remediation_package.md",
]

RETEST_FILES = [
    "README.md",
    "retest_package_schema.md",
    "retest_package_index.yaml",
    "retest_generation_boundary.md",
    "retest_execution_plan.md",
    "retest_acceptance_criteria.md",
    "retest_before_after_comparison_template.md",
    "generated/system_prompt_leakage_retest_package.md",
    "generated/sensitive_information_disclosure_retest_package.md",
    "generated/rag_knowledge_boundary_retest_package.md",
    "generated/prompt_injection_bypass_retest_package.md",
    "generated/api_boundary_authorization_retest_package.md",
]

REMEDIATION_IDS = ["RP-SPL-001", "RP-SID-002", "RP-RKB-003", "RP-PIB-004", "RP-ABA-005"]
RETEST_IDS = ["RT-SPL-001", "RT-SID-002", "RT-RKB-003", "RT-PIB-004", "RT-ABA-005"]
TASK_IDS = ["TASK-P0-001", "TASK-P0-002", "TASK-P0-003", "TASK-P0-004",
            "TASK-P1-001", "TASK-P1-002", "TASK-P1-003",
            "TASK-P2-001", "TASK-P2-002", "TASK-P2-003"]
FINDING_GROUPS = ["system_prompt_leakage", "sensitive_disclosure", "rag_exposure",
                  "prompt_injection_bypass", "api_boundary_weakness"]

# Map finding group key → actual generated file name stem
FILE_STEM = {
    "system_prompt_leakage": "system_prompt_leakage",
    "sensitive_disclosure": "sensitive_information_disclosure",
    "rag_exposure": "rag_knowledge_boundary",
    "prompt_injection_bypass": "prompt_injection_bypass",
    "api_boundary_weakness": "api_boundary_authorization",
}

REQUIRED_FIELDS_REM = [
    "Remediation Goal", "Recommended Remediation Actions", "Acceptance Criteria",
    "Retest Recommendations", "Estimated Effort", "Manual Review Required",
]

REQUIRED_FIELDS_RET = [
    "Retest Goal", "Suggested Test Cases", "Pass Criteria", "Fail Criteria",
    "Manual Review Questions", "Evidence Requirements",
]

PASS = 0
FAIL = 0
WARN = 0
TOTAL_CHECKS = 0


def check(description: str, condition: bool, warn_only: bool = False) -> None:
    global PASS, FAIL, WARN, TOTAL_CHECKS
    TOTAL_CHECKS += 1
    if condition:
        PASS += 1
    elif warn_only:
        WARN += 1
        print(f"  ⚠  WARN #{TOTAL_CHECKS:02d}: {description}")
    else:
        FAIL += 1
        print(f"  ✖ FAIL #{TOTAL_CHECKS:02d}: {description}")


def file_exists(rel: str, base: Path) -> bool:
    return (base / rel).exists()


def file_contains(path: Path, pattern: str) -> bool:
    if not path.exists():
        return False
    try:
        content = path.read_text(encoding="utf-8")
        return bool(re.search(pattern, content, re.DOTALL))
    except Exception:
        return False


def main() -> int:
    global PASS, FAIL, WARN, TOTAL_CHECKS
    print("Phase 33 — Remediation & Retest Package Validation")
    print(f"{'='*60}\n")

    # ── Section 1: File existence (checks 01-23) ────────────────
    print("[Section 1: Remediation Package Files]")
    for f in REMEDIATION_FILES:
        check(f"Remediation file exists: {f}", file_exists(f, REM_DIR))
    print()

    print("[Section 2: Retest Package Files]")
    for f in RETEST_FILES:
        check(f"Retest file exists: {f}", file_exists(f, RET_DIR))
    print()

    # ── Section 3: Package IDs (checks 24-33) ───────────────────
    print("[Section 3: Package IDs]")
    for pid in REMEDIATION_IDS:
        found = False
        for f in REMEDIATION_FILES:
            if f.endswith(".md") or f.endswith(".yaml"):
                p = REM_DIR / f
                if file_contains(p, re.escape(pid)):
                    found = True
                    break
        check(f"Remediation package ID present: {pid}", found)
    print()

    for pid in RETEST_IDS:
        found = False
        for f in RETEST_FILES:
            if f.endswith(".md") or f.endswith(".yaml"):
                p = RET_DIR / f
                if file_contains(p, re.escape(pid)):
                    found = True
                    break
        check(f"Retest package ID present: {pid}", found)
    print()

    for tid in TASK_IDS:
        found = False
        for f in REMEDIATION_FILES:
            if f.endswith(".md") or f.endswith(".yaml"):
                p = REM_DIR / f
                if file_contains(p, re.escape(tid)):
                    found = True
                    break
        check(f"Task ID present: {tid}", found)
    print()

    # ── Section 4: Required fields in remediation packages ─────
    print("[Section 4: Remediation Package Fields]")
    for field in REQUIRED_FIELDS_REM:
        count = 0
        for name in FINDING_GROUPS:
            p = REM_DIR / "generated" / f"{FILE_STEM[name]}_remediation_package.md"
            if file_contains(p, rf"##\s*{re.escape(field)}"):
                count += 1
        check(f"Remediation field '{field}' in all 5 packages", count == 5)
    print()

    # ── Section 5: Required fields in retest packages ───────────
    print("[Section 5: Retest Package Fields]")
    for field in REQUIRED_FIELDS_RET:
        count = 0
        for name in FINDING_GROUPS:
            p = RET_DIR / "generated" / f"{FILE_STEM[name]}_retest_package.md"
            if file_contains(p, rf"##\s*{re.escape(field)}"):
                count += 1
        check(f"Retest field '{field}' in all 5 packages", count == 5)
    print()

    # ── Section 6: Status and constraints ───────────────────────
    print("[Section 6: Status & Constraints]")

    # Check remediation packages have remediation_planned status
    for name in FINDING_GROUPS:
        p = REM_DIR / "generated" / f"{FILE_STEM[name]}_remediation_package.md"
        check(f"Remediation status is 'remediation_planned': {name}",
              file_contains(p, r"remediation_planned"))
    print()

    # Check retest packages have retest_not_executed status
    for name in FINDING_GROUPS:
        p = RET_DIR / "generated" / f"{FILE_STEM[name]}_retest_package.md"
        check(f"Retest status is 'retest_not_executed': {name}",
              file_contains(p, r"retest_not_executed"))
    print()

    # Check all retest packages have real_api_execution_allowed=false
    for name in FINDING_GROUPS:
        p = RET_DIR / "generated" / f"{FILE_STEM[name]}_retest_package.md"
        check(f"real_api_execution_allowed=false: {name}",
              file_contains(p, r"real_api_execution_allowed.*false"))
    print()

    # Check all retest packages have next_step_human_go_no_go_required=true
    for name in FINDING_GROUPS:
        p = RET_DIR / "generated" / f"{FILE_STEM[name]}_retest_package.md"
        check(f"human_go_no_go_required=true: {name}",
              file_contains(p, r"human_go_no_go_required.*true"))
    print()

    # ── Section 7: Boundary docs ────────────────────────────────
    print("[Section 7: Boundary Documents]")
    rem_b = REM_DIR / "remediation_generation_boundary.md"
    check("Remediation boundary: no API key in output",
          file_contains(rem_b, r"API key in output.*false"))
    check("Remediation boundary: no formal vulnerability conclusion",
          file_contains(rem_b, r"formal vulnerability conclusion"))
    ret_b = RET_DIR / "retest_generation_boundary.md"
    check("Retest boundary: no API tests re-executed",
          file_contains(ret_b, r"API tests re-executed.*false"))
    check("Retest boundary: no promptfoo eval executed",
          file_contains(ret_b, r"promptfoo eval executed.*false"))
    print()

    # ── Section 8: Task board ───────────────────────────────────
    print("[Section 8: Task Board]")
    tb_yaml = REM_DIR / "remediation_task_board.yaml"
    check("Task board YAML exists", tb_yaml.exists())
    tb_md = REM_DIR / "remediation_task_board.md"
    check("Task board MD exists", tb_md.exists())
    check("Task board contains P0 count of 4",
          file_contains(tb_yaml, r"p0_count:\s*4"))
    check("Task board contains P1 count of 3",
          file_contains(tb_yaml, r"p1_count:\s*3"))
    check("Task board contains P2 count of 3",
          file_contains(tb_yaml, r"p2_count:\s*3"))
    print()

    # ── Section 9: Execution plan ───────────────────────────────
    print("[Section 9: Execution Plan]")
    ep = RET_DIR / "retest_execution_plan.md"
    check("Execution plan exists", ep.exists())
    check("Execution plan has execution ID",
          file_contains(ep, r"exec-32c-ae7a145d696a"))
    check("Execution plan has P0/P1/Full Regression phases",
          file_contains(ep, r"Phase 1.*P0") and file_contains(ep, r"Phase 2.*P1"))
    print()

    # ── Summary ─────────────────────────────────────────────────
    print(f"{'='*60}")
    print(f"Results: {PASS} passed, {FAIL} failed, {WARN} warnings out of {TOTAL_CHECKS} checks")

    if FAIL > 0:
        print("\n❌ Validation FAILED — some checks did not pass.")
        return 1
    print("\n✅ Validation PASSED — all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
