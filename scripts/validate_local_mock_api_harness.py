#!/usr/bin/env python3
"""Validate Local Mock API Execution Harness — check file existence, parseable YAML, and safety constraints."""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required for YAML parsing") from exc

ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = ROOT / "api_provider/mock_harness"

REQUIRED_FILES = [
    "README.md",
    "mock_api_target_schema.md",
    "mock_request_fixtures.yaml",
    "mock_response_fixtures.yaml",
    "mock_execution_trace.yaml",
    "mock_normalized_response_samples.yaml",
    "mock_execution_boundary.md",
]

YAML_FILES = [
    "mock_request_fixtures.yaml",
    "mock_response_fixtures.yaml",
    "mock_execution_trace.yaml",
    "mock_normalized_response_samples.yaml",
]

BOUNDARY_FILES = [
    "mock_execution_trace.yaml",
    "mock_normalized_response_samples.yaml",
]

SAFETY_FLAGS = {
    "external_network_called": False,
    "real_target_connected": False,
    "credentials_loaded": False,
    "tests_executed": False,
    "evidence_generated": False,
    "usable_for_formal_finding": False,
}

URL_PATTERN = re.compile(r"https?://[^\s'\"]+")
TOKEN_PATTERN = re.compile(r"(sk-[A-Za-z0-9]{20,})")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
API_KEY_PATTERN = re.compile(r"(api[_-]?key['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,})", re.IGNORECASE)


def read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check(description: str, passed: bool, detail: str = "") -> dict[str, Any]:
    return {
        "check": description,
        "passed": passed,
        "detail": detail,
    }


def validate() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    # Check 1: All required files exist
    missing = []
    for fname in REQUIRED_FILES:
        if not (HARNESS_DIR / fname).exists():
            missing.append(fname)
    results.append(check(
        "All required mock_harness files exist",
        len(missing) == 0,
        f"Missing: {', '.join(missing)}" if missing else f"All {len(REQUIRED_FILES)} files present",
    ))

    # Check 2: Mock request fixtures parseable
    req_path = HARNESS_DIR / "mock_request_fixtures.yaml"
    req_data = None
    req_ok = False
    if req_path.exists():
        try:
            req_data = read_yaml(req_path)
            if req_data and "fixtures" in req_data:
                req_ok = True
                results.append(check(
                    "Mock request fixtures parseable and valid",
                    True,
                    f"Loaded {len(req_data['fixtures'])} request fixtures",
                ))
            else:
                results.append(check(
                    "Mock request fixtures parseable and valid",
                    False,
                    "Missing 'fixtures' key",
                ))
        except Exception as e:
            results.append(check(
                "Mock request fixtures parseable and valid",
                False,
                str(e),
            ))
    else:
        results.append(check(
            "Mock request fixtures parseable and valid",
            False,
            "File not found",
        ))

    # Check 3: Mock response fixtures parseable
    resp_path = HARNESS_DIR / "mock_response_fixtures.yaml"
    resp_data = None
    if resp_path.exists():
        try:
            resp_data = read_yaml(resp_path)
            if resp_data and "fixtures" in resp_data:
                results.append(check(
                    "Mock response fixtures parseable and valid",
                    True,
                    f"Loaded {len(resp_data['fixtures'])} response fixtures",
                ))
            else:
                results.append(check(
                    "Mock response fixtures parseable and valid",
                    False,
                    "Missing 'fixtures' key",
                ))
        except Exception as e:
            results.append(check(
                "Mock response fixtures parseable and valid",
                False,
                str(e),
            ))
    else:
        results.append(check(
            "Mock response fixtures parseable and valid",
            False,
            "File not found",
        ))

    # Check 4: Mock execution trace parseable
    trace_path = HARNESS_DIR / "mock_execution_trace.yaml"
    trace_data = None
    if trace_path.exists():
        try:
            trace_data = read_yaml(trace_path)
            if trace_data and "operations" in trace_data:
                results.append(check(
                    "Mock execution trace parseable",
                    True,
                    f"Loaded {len(trace_data['operations'])} operations",
                ))
            else:
                results.append(check(
                    "Mock execution trace parseable",
                    False,
                    "Missing 'operations' key",
                ))
        except Exception as e:
            results.append(check(
                "Mock execution trace parseable",
                False,
                str(e),
            ))
    else:
        results.append(check(
            "Mock execution trace parseable",
            False,
            "File not found",
        ))

    # Check 5: Normalized response samples parseable
    norm_path = HARNESS_DIR / "mock_normalized_response_samples.yaml"
    norm_data = None
    if norm_path.exists():
        try:
            norm_data = read_yaml(norm_path)
            if norm_data and "normalized_samples" in norm_data:
                results.append(check(
                    "Normalized response samples parseable",
                    True,
                    f"Loaded {len(norm_data['normalized_samples'])} samples",
                ))
            else:
                results.append(check(
                    "Normalized response samples parseable",
                    False,
                    "Missing 'normalized_samples' key",
                ))
        except Exception as e:
            results.append(check(
                "Normalized response samples parseable",
                False,
                str(e),
            ))
    else:
        results.append(check(
            "Normalized response samples parseable",
            False,
            "File not found",
        ))

    # Check 6-14: Safety flag constraints in boundary files
    for fname in BOUNDARY_FILES:
        fpath = HARNESS_DIR / fname
        if not fpath.exists():
            for flag in SAFETY_FLAGS:
                results.append(check(
                    f"Safety flag {flag}=false in {fname}",
                    False,
                    "File not found",
                ))
            continue

        try:
            data = read_yaml(fpath)
            if not isinstance(data, dict):
                for flag in SAFETY_FLAGS:
                    results.append(check(
                        f"Safety flag {flag}=false in {fname}",
                        False,
                        "Data is not a dict",
                    ))
                continue

            # Check direct boundary section
            boundary = data.get("boundary", {})
            for flag, expected in SAFETY_FLAGS.items():
                actual = boundary.get(flag, data.get(flag, "not_found"))
                if actual == expected:
                    results.append(check(
                        f"Safety flag {flag}={expected} in {fname}",
                        True,
                        f"Found {flag}={actual}",
                    ))
                elif actual == "not_found":
                    results.append(check(
                        f"Safety flag {flag}={expected} in {fname}",
                        False,
                        f"Flag {flag} not found in file",
                    ))
                else:
                    results.append(check(
                        f"Safety flag {flag}={expected} in {fname}",
                        False,
                        f"Expected {expected}, got {actual}",
                    ))
        except Exception as e:
            for flag in SAFETY_FLAGS:
                results.append(check(
                    f"Safety flag {flag}=false in {fname}",
                    False,
                    str(e),
                ))

    # Check 15: No real URLs in fixture files
    all_text = ""
    for fname in YAML_FILES:
        fpath = HARNESS_DIR / fname
        if fpath.exists():
            all_text += fpath.read_text(encoding="utf-8") + "\n"
    urls_found = URL_PATTERN.findall(all_text)
    # Exclude mock URLs like mock_*, localhost, example.com
    real_urls = [u for u in urls_found if "mock" not in u and "example" not in u and "localhost" not in u]
    results.append(check(
        "No real URLs in fixture files",
        len(real_urls) == 0,
        f"Real URLs found: {real_urls[:5]}" if real_urls else "No real URLs found",
    ))

    # Check 16: No real tokens
    tokens = TOKEN_PATTERN.findall(all_text)
    results.append(check(
        "No real tokens in fixture files",
        len(tokens) == 0,
        f"Found {len(tokens)} potential tokens" if tokens else "No real tokens found",
    ))

    # Check 17: No real emails
    emails = EMAIL_PATTERN.findall(all_text)
    results.append(check(
        "No real emails in fixture files",
        len(emails) == 0,
        f"Found {len(emails)} emails" if emails else "No real emails found",
    ))

    # Check 18: No real API keys
    api_keys = API_KEY_PATTERN.findall(all_text)
    results.append(check(
        "No real API keys in fixture files",
        len(api_keys) == 0,
        f"Found {len(api_keys)} potential keys" if api_keys else "No real API keys found",
    ))

    return results


def main() -> None:
    print("=" * 60)
    print("Local Mock API Execution Harness Validation")
    print("=" * 60)

    results = validate()

    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)

    print(f"\nResults ({passed}/{total} passed, {failed} failed):\n")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['check']}")
        if r["detail"]:
            print(f"         {r['detail']}")

    summary = {
        "validation": {
            "harness": "local_mock_api_execution_harness",
            "phase": "Phase 31C",
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "all_passed": failed == 0,
            "results": results,
        }
    }

    result_yaml_path = HARNESS_DIR / "mock_harness_validation_result.yaml"
    result_yaml_path.write_text(yaml.safe_dump(summary, default_flow_style=False, allow_unicode=True, sort_keys=False), encoding="utf-8")

    report_lines = [
        "# Mock Harness Validation Report",
        "",
        f"**Phase**: Phase 31C Local Mock API Execution Harness",
        f"**Validated At**: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Summary",
        "",
        f"- Total checks: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- All passed: {failed == 0}",
        "",
        "## Check Details",
        "",
    ]
    for r in results:
        status_icon = "✅" if r["passed"] else "❌"
        report_lines.append(f"### {status_icon} {r['check']}")
        report_lines.append("")
        if r["detail"]:
            report_lines.append(f"{r['detail']}")
        report_lines.append("")

    report_lines.extend([
        "## Safety Boundary",
        "",
        "| Flag | Value |",
        "|---|---|",
    ])
    for flag, val in SAFETY_FLAGS.items():
        report_lines.append(f"| {flag} | {val} |")
    report_lines.extend([
        "",
        "## Important",
        "",
        "- No real network calls were made during validation.",
        "- No real credentials were loaded.",
        "- No real endpoints were accessed.",
        "- No real security tests were executed.",
        "- No real evidence was generated.",
        "- All mock execution is local, in-process, and sandboxed.",
    ])

    report_md_path = HARNESS_DIR / "mock_harness_validation_report.md"
    report_md_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"\nValidation result: {result_yaml_path.relative_to(ROOT)}")
    print(f"Validation report: {report_md_path.relative_to(ROOT)}")

    if failed > 0:
        print(f"\nWarning: {failed} check(s) failed.")
        sys.exit(1)
    else:
        print(f"\nAll {total} validation checks passed!")


if __name__ == "__main__":
    main()
