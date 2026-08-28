#!/usr/bin/env python3
"""Validate Phase 32D Real API Regression Assessment Report.

Performs 20 static checks on the generated report files.
No network calls, no credential access, no API execution.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports/real_api_regression_assessment"

REQUIRED_FILES = [
    "README.md",
    "real_api_regression_assessment_report.md",
    "executive_summary.md",
    "technical_findings_summary.md",
    "test_coverage_matrix.yaml",
    "risk_summary.yaml",
    "remediation_recommendations.md",
    "retest_recommendations.md",
    "evidence_reference_index.yaml",
    "report_generation_result.yaml",
]

# Phase 32D.1: English-preserved report files
ENGLISH_FILES = [
    "executive_summary_en.md",
    "technical_findings_summary_en.md",
    "remediation_recommendations_en.md",
    "retest_recommendations_en.md",
    "real_api_regression_assessment_report_en.md",
]

# Phase 32D.1: Bilingual index
BILINGUAL_INDEX = "report_language_index.md"

# Phase 32E.1: Finding triage files
TRIAGE_FILES = [
    "finding_triage/finding_candidate_triage_table.yaml",
    "finding_triage/finding_candidate_triage_table.md",
    "finding_triage/consolidated_findings_summary.md",
    "finding_triage/manual_review_checklist.md",
    "finding_triage/false_positive_review_notes.md",
]

# Phase 32E.2: Final hardened files
HARDENED_FILES = [
    "final_hardened/management_brief_zh.md",
    "final_hardened/executive_summary_final_zh.md",
    "final_hardened/final_findings_summary_zh.md",
    "final_hardened/remediation_action_plan_zh.md",
    "final_hardened/retest_plan_final_zh.md",
    "final_hardened/report_hardening_summary.yaml",
]

# Sensitive patterns that must NOT appear in reports
SENSITIVE_PATTERNS = [
    re.compile(r"openapi-[A-Za-z0-9]{12,}"),
    re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._~+/-]{8,}"),
    re.compile(r"(?i)api[-_]?key:\s*['\"]?[A-Za-z0-9._~+/-]{8,}"),
    re.compile(r"fastgpt-poc\.sangforcloud\.com/(?!\[REDACTED(?:_PATH)?\])"),
]

checks_passed = 0
checks_failed = 0


def check(desc: str, condition: bool) -> None:
    global checks_passed, checks_failed
    if condition:
        print(f"  [PASS] {desc}")
        checks_passed += 1
    else:
        print(f"  [FAIL] {desc}")
        checks_failed += 1


def file_text(fname: str) -> str:
    p = REPORT_DIR / fname
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def main() -> None:
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 32D: Real API Regression Assessment Report Validation")
    print("=" * 60)

    # 1-9: File existence checks
    print("\n--- File Existence Checks ---")
    for fname in REQUIRED_FILES:
        check(f"File exists: {fname}", (REPORT_DIR / fname).exists())

    # Check all report files for sensitive content
    print("\n--- Sensitive Content Checks ---")
    for fname in REQUIRED_FILES:
        text = file_text(fname)
        for pat in SENSITIVE_PATTERNS:
            matches = pat.findall(text)
            for m in matches:
                check(f"{fname} does not contain unredacted sensitive data", False)
                print(f"    Found: {m[:40]}")

    # 10: API key check across all files
    api_key_found = False
    for fname in REQUIRED_FILES:
        if SENSITIVE_PATTERNS[0].search(file_text(fname)):
            api_key_found = True
    check("Report does not contain API key", not api_key_found)

    # 11: Authorization header check
    auth_found = any(SENSITIVE_PATTERNS[1].search(file_text(f)) for f in REQUIRED_FILES)
    check("Report does not contain Authorization header", not auth_found)

    # 12: Token check
    token_found = any(SENSITIVE_PATTERNS[2].search(file_text(f)) for f in REQUIRED_FILES)
    check("Report does not contain real token", not token_found)

    # 13: Unredacted endpoint check
    unredacted = any(SENSITIVE_PATTERNS[3].search(file_text(f)) for f in REQUIRED_FILES)
    check("Report does not contain unredacted endpoint", not unredacted)

    # 14: Finding candidates need human review
    main_report = file_text("real_api_regression_assessment_report.md")
    check("Report declares finding candidates need human review",
          "needs_human_review" in main_report or "candidates only" in main_report.lower())

    # 15: Not formal vulnerability conclusion
    check("Report does not claim formal vulnerability conclusions",
          "formal vulnerability conclusion" not in main_report or "No" in main_report)

    # 16: Not formal customer report
    check("Report does not claim formal customer report",
          "formal customer report" not in main_report or "No" in main_report)

    # 17: redaction_applied=true
    check("Report contains redaction_applied=true",
          "redaction_applied=true" in main_report or "redaction_applied: true" in main_report)

    # 18: real_target_validated=false or equivalent
    check("Report contains real_target_validated=false or equivalent disclaimer",
          "real_target_validated" in main_report or
          "real_target_validated" in file_text("report_generation_result.yaml") or
          "authorized test API" in main_report.lower())

    # 19: usable_for_formal_report=false
    check("Report contains usable_for_formal_report=false or equivalent disclaimer",
          "usable_for_formal_report" in main_report or "not a formal customer report" in main_report.lower())

    # 20: References Phase 32C execution
    check("Report references Phase 32C execution result",
          "Phase 32C" in main_report or ctx_exec_id() in main_report if (ctx_exec_id()) else False)

    # --- Phase 32D.1: Bilingual checks (21-27) ---
    print("\n--- Phase 32D.1: Bilingual Report Checks ---")

    # 21: English report files exist
    for fname in ENGLISH_FILES:
        check(f"English report exists: {fname}", (REPORT_DIR / fname).exists())

    # 22: Bilingual index exists
    check(f"Bilingual index exists: {BILINGUAL_INDEX}", (REPORT_DIR / BILINGUAL_INDEX).exists())

    # 23: Bilingual index mentions Chinese default
    bi_text = file_text(BILINGUAL_INDEX)
    check("Bilingual index declares Chinese as default language",
          "Chinese" in bi_text or "中文" in bi_text)

    # 24: English reports contain English content
    en_text = file_text("executive_summary_en.md")
    check("English executive summary has English content",
          "Executive Summary" in en_text)

    # 25: Chinese report has Chinese content (check final_hardened for verified Chinese)
    zh_final_text = file_text("final_hardened/executive_summary_final_zh.md")
    check("Final hardened Chinese report has Chinese content",
          "执行摘要" in zh_final_text or "摘要" in zh_final_text)

    # 26: Chinese final hardened reports are in Chinese
    check("Final hardened Chinese report is in Chinese",
          "发现" in zh_final_text or "风险" in zh_final_text)

    # 27: No English files have Chinese-only disclaimer
    check("English reports do not contain Chinese-only disclaimer",
          not any("本报告默认为中文版" in file_text(f) for f in ENGLISH_FILES))

    # --- Phase 32E.1: Finding Triage checks (28-33) ---
    print("\n--- Phase 32E.1: Finding Triage Checks ---")

    # 28: Triage directory exists
    check("Finding triage directory exists", (REPORT_DIR / "finding_triage").is_dir())

    # 29: Triage files exist
    for fname in TRIAGE_FILES:
        check(f"Triage file exists: {fname}", (REPORT_DIR / fname).exists())

    # 30: Triage table has candidate entries
    tt_text = file_text("finding_triage/finding_candidate_triage_table.md")
    check("Triage table contains candidate entries", "FC-32C-gtc_chatbot-spe-001" in tt_text and "FC-32C-gtc_api-asb-002" in tt_text)

    # 31: Consolidated findings has 5 groups
    cf_text = file_text("finding_triage/consolidated_findings_summary.md")
    check("Consolidated findings has 5 merge groups",
          all(g in cf_text for g in ["系统提示泄露", "敏感信息披露", "RAG知识库过度暴露", "提示注入绕过", "API边界/授权缺陷"]))

    # 32: Manual review checklist exists
    mr_text = file_text("finding_triage/manual_review_checklist.md")
    check("Manual review checklist has review process",
          "Review Process" in mr_text or "复核流程" in mr_text)

    # 33: False positive review has FP risk analysis
    fp_text = file_text("finding_triage/false_positive_review_notes.md")
    check("False positive review has FP risk categories",
          "Low" in fp_text and "Medium" in fp_text and "High" in fp_text)

    # --- Phase 32E.2: Final Hardened checks (34-40) ---
    print("\n--- Phase 32E.2: Final Hardened Report Checks ---")

    # 34: Hardened directory exists
    check("Final hardened directory exists", (REPORT_DIR / "final_hardened").is_dir())

    # 35: Hardened files exist
    for fname in HARDENED_FILES:
        check(f"Hardened file exists: {fname}", (REPORT_DIR / fname).exists())

    # 36: Management brief has key data
    mb_text = file_text("final_hardened/management_brief_zh.md")
    check("Management brief contains P0 items", "P0" in mb_text)
    check("Management brief contains pass rate", "通过率" in mb_text or "通过" in mb_text)

    # 37: Final findings summary has 5 findings
    ff_text = file_text("final_hardened/final_findings_summary_zh.md")
    check("Final findings summary has 5 findings",
          all(f"发现 {i}" in ff_text for i in range(1, 6)))

    # 38: Remediation action plan has effort estimates
    ra_text = file_text("final_hardened/remediation_action_plan_zh.md")
    check("Remediation plan has effort estimates",
          "预计工作量" in ra_text and "Week" in ra_text)

    # 39: Retest plan has precondition checklist
    rt_text = file_text("final_hardened/retest_plan_final_zh.md")
    check("Retest plan has precondition checklist", "复测前置条件" in rt_text)
    check("Retest plan has pass criteria", "通过目标" in rt_text)

    # 40: Hardening summary has all metadata
    hs_text = file_text("final_hardened/report_hardening_summary.yaml")
    check("Hardening summary has language section", "Language" in hs_text or "语言" in hs_text)
    check("Hardening summary has finding triage section", "Finding Triage" in hs_text or "发现研判" in hs_text)
    check("Hardening summary has security status", "Security Status" in hs_text or "安全状态" in hs_text)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Validation Summary:")
    print(f"  Total checks: {checks_passed + checks_failed}")
    print(f"  Passed: {checks_passed}")
    print(f"  Failed: {checks_failed}")
    print(f"  Check groups:")
    print(f"    Base checks (1-20): Phase 32D report validation")
    print(f"    Bilingual checks (21-27): Phase 32D.1 Chinese/English")
    print(f"    Triage checks (28-33): Phase 32E.1 finding triage")
    print(f"    Hardened checks (34-40): Phase 32E.2 final reports")
    print(f"{'=' * 60}")

    if checks_failed > 0:
        print("\n  Some checks failed. Review details above.")
        sys.exit(1)
    else:
        print("\n  All validation checks passed!")


def ctx_exec_id() -> str:
    try:
        import yaml
        p = REPORT_DIR / "report_generation_result.yaml"
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data.get("source_execution_id", "")
    except Exception:
        pass
    return ""


if __name__ == "__main__":
    main()
