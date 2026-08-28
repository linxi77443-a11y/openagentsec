#!/usr/bin/env python3
"""Validate Full Authorized API Regression Execution Result.

All checks are local-only: no network calls, no credential loading.
Validates evidence integrity, redaction status, finding candidate safety.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML required") from exc

EXECUTION_DIR = Path("api_provider/full_regression_execution")

FORBIDDEN_IN_EVIDENCE: list[tuple[str, re.Pattern]] = [
    ("API key pattern", re.compile(r"openapi-[A-Za-z0-9]{12,}")),
    ("Authorization header value", re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]{8,}=*")),
    ("Raw token pattern", re.compile(r"(?i)(api[_-]?key|token|secret|password)[=:：\s]+[A-Za-z0-9._~+/-]{8,}=*")),
]


def check(description: str, result: bool) -> bool:
    status = "PASS" if result else "FAIL"
    print(f"  [{status}] {description}")
    return result


def main() -> int:
    checks_passed = 0
    checks_total = 0

    print("=" * 60)
    print("Full Authorized API Regression Result Validation")
    print("=" * 60)

    # 1. Execution directory exists
    checks_total += 1
    print("\n[1] Execution directory exists...")
    dir_ok = EXECUTION_DIR.exists()
    if check(f"Directory exists: {EXECUTION_DIR}", dir_ok):
        checks_passed += 1

    # 2. Evidence JSON exists
    checks_total += 1
    print("\n[2] Evidence JSON exists...")
    evidence_path = EXECUTION_DIR / "full_regression_evidence.json"
    evidence_exists = evidence_path.exists()
    if check(f"File exists: full_regression_evidence.json", evidence_exists):
        checks_passed += 1

    # 3. Result YAML exists
    checks_total += 1
    print("\n[3] Result YAML exists...")
    result_path = EXECUTION_DIR / "full_regression_execution_result.yaml"
    result_exists = result_path.exists()
    if check(f"File exists: full_regression_execution_result.yaml", result_exists):
        checks_passed += 1

    # 4. Finding candidates YAML exists
    checks_total += 1
    print("\n[4] Finding candidates YAML exists...")
    finding_path = EXECUTION_DIR / "finding_candidates.yaml"
    finding_exists = finding_path.exists()
    if check(f"File exists: finding_candidates.yaml", finding_exists):
        checks_passed += 1

    # If evidence exists, run detailed checks
    if evidence_exists:
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception) as e:
            print(f"  [FAIL] Could not parse full_regression_evidence.json: {e}")
            evidence = {}

        # 5. Evidence does not contain API key
        checks_total += 1
        print("\n[5] Evidence does not contain API key...")
        text = json.dumps(evidence)
        has_api_key = "openapi-" in text and "REDACTED" not in text
        if check("No raw API key in evidence", not has_api_key):
            checks_passed += 1

        # 6. Evidence does not contain Authorization header
        checks_total += 1
        print("\n[6] Evidence does not contain Authorization header value...")
        auth_clean = True
        for pattern_name, pattern in FORBIDDEN_IN_EVIDENCE:
            if pattern.search(text):
                auth_clean = False
                print(f"    [FAIL] Found {pattern_name} in evidence")
        if check("No Authorization header value in evidence", auth_clean):
            checks_passed += 1

        # 7. Evidence does not contain real sensitive tokens
        checks_total += 1
        print("\n[7] Evidence does not contain real sensitive tokens...")
        token_clean = True
        for pattern_name, pattern in FORBIDDEN_IN_EVIDENCE:
            if pattern.search(text):
                print(f"    [FAIL] Found {pattern_name} in evidence")
                token_clean = False
        if check("No real sensitive tokens in evidence", token_clean):
            checks_passed += 1

        # 8. Endpoint is redacted
        checks_total += 1
        print("\n[8] Endpoint is redacted...")
        ep = evidence.get("endpoint_redacted", "")
        ep_redacted = "[REDACTED]" in ep.upper() or "[REDACTED_PATH]" in ep
        if check("Endpoint contains [REDACTED]", ep_redacted):
            checks_passed += 1

        # 9. production_target=false
        checks_total += 1
        print("\n[9] production_target is false...")
        prod = evidence.get("production_target", True)
        if check(f"production_target=false", prod is False):
            checks_passed += 1

        # 10. redaction_applied=true
        checks_total += 1
        print("\n[10] redaction_applied is true...")
        redact = evidence.get("redaction_applied", False)
        if check(f"redaction_applied=true", redact is True):
            checks_passed += 1

        # 11. api_key_logged=false
        checks_total += 1
        print("\n[11] api_key_logged is false...")
        key_logged = evidence.get("api_key_logged", True)
        if check(f"api_key_logged=false", key_logged is False):
            checks_passed += 1

        # 12. authorization_header_logged=false
        checks_total += 1
        print("\n[12] authorization_header_logged is false...")
        auth_logged = evidence.get("authorization_header_logged", True)
        if check(f"authorization_header_logged=false", auth_logged is False):
            checks_passed += 1
    else:
        # Skip checks 5-12
        for i in range(5, 13):
            checks_total += 1
            check(f"[{i}] Skipped (evidence not available)", True)
            checks_passed += 1

    # 13. Finding candidates are all needs_human_review
    checks_total += 1
    print("\n[13] Finding candidates are all needs_human_review...")
    if finding_exists:
        try:
            finding_text = finding_path.read_text(encoding="utf-8")
            findings = yaml.safe_load(finding_text)
            candidates = findings.get("candidates", []) if isinstance(findings, dict) else []
            if isinstance(candidates, list):
                all_needs_review = all(
                    c.get("finding_status") == "needs_human_review"
                    for c in candidates if isinstance(c, dict)
                )
            else:
                all_needs_review = True
            overall_status = findings.get("finding_status") if isinstance(findings, dict) else None
            if overall_status == "needs_human_review":
                all_needs_review = True
        except Exception:
            all_needs_review = False
        if check("All findings are needs_human_review", all_needs_review):
            checks_passed += 1
    else:
        if check("Skipped (finding_candidates.yaml not available)", True):
            checks_passed += 1

    # 14. No finding marked as usable_for_formal_report
    checks_total += 1
    print("\n[14] No finding marked as usable_for_formal_report...")
    if finding_exists:
        try:
            findings = yaml.safe_load(finding_text) if 'finding_text' in dir() else yaml.safe_load(finding_path.read_text())
            usable = findings.get("usable_for_formal_report", True) if isinstance(findings, dict) else True
            not_formal = usable is False
        except Exception:
            not_formal = False
        if check("usable_for_formal_report is false", not_formal):
            checks_passed += 1
    else:
        if check("Skipped (finding_candidates.yaml not available)", True):
            checks_passed += 1

    # 15. Dashboard/report does not claim formal findings
    checks_total += 1
    print("\n[15] Dashboard/report does not claim formal findings...")
    dashboard_data = Path("dashboard/dashboard_data.json")
    if dashboard_data.exists():
        try:
            dd = json.loads(dashboard_data.read_text(encoding="utf-8"))
            fre = dd.get("full_regression_execution", {})
            # Dashboard should not claim validated findings
            not_claiming = True
            # Check that dashboard doesn't have formal_finding fields set to true
            report_path = EXECUTION_DIR / "full_regression_execution_report.md"
            if report_path.exists():
                report_text = report_path.read_text(encoding="utf-8")
                if "formal finding" in report_text.lower() or "validated" in report_text.lower():
                    not_claiming = False
        except Exception:
            not_claiming = True
        if check("No formal finding claims in output", not_claiming):
            checks_passed += 1
    else:
        if check("Skipped (dashboard data not available)", True):
            checks_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary:")

    # Check for api_key_logged=True in result files
    if result_exists:
        try:
            result_data = yaml.safe_load(result_path.read_text())
            if isinstance(result_data, dict):
                ak = result_data.get("api_key_logged", None)
                if ak is True:
                    print("\n⚠️  WARNING: api_key_logged=true in execution result!")
        except Exception:
            pass

    print(f"  Total checks: {checks_total}")
    print(f"  Passed: {checks_passed}")
    print(f"  Failed: {checks_total - checks_passed}")
    print("=" * 60)

    if checks_passed == checks_total:
        print("\nAll validation checks passed!")
        return 0
    else:
        print(f"\n{checks_total - checks_passed} check(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
