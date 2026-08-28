#!/usr/bin/env python3
"""Validate Single Authorized API Smoke Test Design.

All checks are local-only: no network calls, no credential loading,
no real endpoint access. Only validates file existence, placeholder
content, flag declarations, and policy definitions.
"""

import os
import re
import sys
import yaml
from pathlib import Path

DESIGN_DIR = Path("api_provider/single_smoke_test_design")
REQUIRED_FILES = [
    "README.md",
    "single_smoke_test_schema.md",
    "candidate_target_template.yaml",
    "minimal_request_bundle.yaml",
    "expected_safe_response_contract.md",
    "execution_preflight_gate.yaml",
    "abort_condition_checklist.md",
    "operator_runbook_template.md",
    "evidence_placeholder_schema.md",
    "smoke_test_design_validation_result.yaml",
    "smoke_test_design_validation_report.md",
]

FORBIDDEN_PATTERNS = {
    "real URL": re.compile(r'https?://(?!.*(?:example\.com|\[PLACEHOLDER\]))'),
    "real token": re.compile(r'(?i)(sk-[a-zA-Z0-9]{10,}|ghp_[a-zA-Z0-9]{10,})'),
    "real email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?<!example\.com)'),
    "real API key": re.compile(r'(?i)(api[_-]?key|apikey|secret|token)\s*[:=]\s*["\']?[a-zA-Z0-9]{16,}["\']?'),
}

YAML_FLAG_FILES = [
    "candidate_target_template.yaml",
    "minimal_request_bundle.yaml",
    "execution_preflight_gate.yaml",
]

YAML_FLAG_CHECKS = {
    "smoke_test_design_only": True,
    "only_one_target_allowed": True,
    "read_only_operations_only": True,
    "approval_status": "not_approved",
    "execution_allowed": False,
    "credentials_loaded": False,
    "real_target_connected": False,
    "network_called": False,
    "evidence_generated": False,
    "production_target_allowed": False,
}

MARKDOWN_FILES_WITH_FLAGS = [
    "single_smoke_test_schema.md",
    "README.md",
]

MARKDOWN_FLAG_CHECKS = {
    "smoke_test_design_only": "true",
    "only_one_target_allowed": "true",
    "read_only_operations_only": "true",
    "approval_status": "not_approved",
    "execution_allowed": "false",
    "credentials_loaded": "false",
    "real_target_connected": "false",
    "network_called": "false",
    "evidence_generated": "false",
}

REQUIRED_POLICY_FILES = {
    "minimal_request_bundle.yaml": ["request_budget", "requests", "total_requests"],
    "abort_condition_checklist.md": ["abort", "stop", "smoke_test_design_only"],
    "operator_runbook_template.md": ["smoke_test_design_only", "execution_allowed", "credentials_loaded"],
    "evidence_placeholder_schema.md": ["evidence_generated", "smoke_test_design_only", "placeholder"],
}


def check(description, result, verbose=True):
    status = "PASS" if result else "FAIL"
    symbol = "[PASS]" if result else "[FAIL]"
    if verbose or not result:
        print(f"  {symbol} {description}")
    return result


def main():
    checks_passed = 0
    checks_total = 0

    print("=" * 60)
    print("Single Authorized API Smoke Test Design Validation")
    print("=" * 60)

    # 1. All files exist
    print("\n[Check 1] All design files exist...")
    all_exist = True
    for f in REQUIRED_FILES:
        path = DESIGN_DIR / f
        exists = path.exists()
        if not exists:
            print(f"    [FAIL] Missing: {f}")
        all_exist = all_exist and exists
    checks_total += 1
    if check(f"All {len(REQUIRED_FILES)} files exist", all_exist):
        checks_passed += 1

    # 2. Placeholder only
    print("\n[Check 2] Placeholder only...")
    placeholders_found = 0
    for f in REQUIRED_FILES:
        content = (DESIGN_DIR / f).read_text()
        if "[PLACEHOLDER]" in content:
            placeholders_found += 1
    all_have_placeholder = placeholders_found == len(REQUIRED_FILES)
    checks_total += 1
    if check(f"{placeholders_found}/{len(REQUIRED_FILES)} files contain placeholder data", all_have_placeholder):
        checks_passed += 1

    # 3-6. No real URLs, tokens, emails, API keys
    for pattern_name, pattern_re in FORBIDDEN_PATTERNS.items():
        print(f"\n[Check 3-6] No {pattern_name}...")
        clean = True
        for f in REQUIRED_FILES:
            content = (DESIGN_DIR / f).read_text()
            matches = pattern_re.findall(content)
            if matches:
                print(f"    [FAIL] {f}: Found {pattern_name}")
                clean = False
        checks_total += 1
        if check(f"No {pattern_name} in any file", clean):
            checks_passed += 1

    # 7-14. Flag checks in YAML files
    print("\n[Check 7-14] Flag declarations in YAML files...")
    all_yaml_flags_ok = True
    for yf in YAML_FLAG_FILES:
        path = DESIGN_DIR / yf
        data = yaml.safe_load(path.read_text())
        for flag, expected in YAML_FLAG_CHECKS.items():
            actual = data.get(flag)
            if actual != expected:
                print(f"    [FAIL] {yf}: {flag}={actual}, expected {expected}")
                all_yaml_flags_ok = False
    checks_total += 1
    if check("All YAML flag declarations correct", all_yaml_flags_ok):
        checks_passed += 1

    # Flag checks in markdown files
    print("\n[Check 7-14] Flag declarations in markdown files...")
    all_md_flags_ok = True
    for mf in MARKDOWN_FILES_WITH_FLAGS:
        content = (DESIGN_DIR / mf).read_text()
        for flag, expected in MARKDOWN_FLAG_CHECKS.items():
            flag_pattern = f"{flag}: {expected}"
            if flag_pattern not in content:
                print(f"    [FAIL] {mf}: {flag}: {expected} not found")
                all_md_flags_ok = False
    checks_total += 1
    if check("All markdown flag declarations correct", all_md_flags_ok):
        checks_passed += 1

    # 15. Request budget defined
    print("\n[Check 15] Request budget defined...")
    bundle_file = DESIGN_DIR / "minimal_request_bundle.yaml"
    bundle_data = yaml.safe_load(bundle_file.read_text())
    budget = bundle_data.get("request_budget", {})
    budget_ok = all(kw in bundle_file.read_text() for kw in REQUIRED_POLICY_FILES["minimal_request_bundle.yaml"])
    checks_total += 1
    if check("Request budget defined", budget_ok):
        checks_passed += 1

    # 16. Abort conditions defined
    print("\n[Check 16] Abort conditions defined...")
    abort_file = DESIGN_DIR / "abort_condition_checklist.md"
    abort_content = abort_file.read_text()
    abort_ok = all(kw in abort_content for kw in REQUIRED_POLICY_FILES["abort_condition_checklist.md"])
    checks_total += 1
    if check("Abort conditions defined", abort_ok):
        checks_passed += 1

    # 17. Human approval gate defined
    print("\n[Check 17] Human approval gate defined...")
    gate_file = DESIGN_DIR / "execution_preflight_gate.yaml"
    gate_data = yaml.safe_load(gate_file.read_text())
    checks_list = gate_data.get("preflight_checks", [])
    has_approval_check = any("approval" in c.get("check_name", "").lower() for c in checks_list)
    checks_total += 1
    if check("Human approval gate defined (approval check in preflight)", has_approval_check):
        checks_passed += 1

    # 18. Evidence placeholder schema defined
    print("\n[Check 18] Evidence placeholder schema defined...")
    evidence_file = DESIGN_DIR / "evidence_placeholder_schema.md"
    evidence_content = evidence_file.read_text()
    evidence_ok = all(kw in evidence_content for kw in REQUIRED_POLICY_FILES["evidence_placeholder_schema.md"])
    checks_total += 1
    if check("Evidence placeholder schema defined", evidence_ok):
        checks_passed += 1

    # 19. only_one_target_allowed=true
    print("\n[Check 19] only_one_target_allowed=true...")
    one_target_ok = True
    for yf in YAML_FLAG_FILES:
        data = yaml.safe_load((DESIGN_DIR / yf).read_text())
        if data.get("only_one_target_allowed") is not True:
            print(f"    [FAIL] {yf}: only_one_target_allowed is not true")
            one_target_ok = False
    checks_total += 1
    if check("only_one_target_allowed=true in all YAML files", one_target_ok):
        checks_passed += 1

    # 20. read_only_operations_only=true
    print("\n[Check 20] read_only_operations_only=true...")
    read_only_ok = True
    for yf in YAML_FLAG_FILES:
        data = yaml.safe_load((DESIGN_DIR / yf).read_text())
        if data.get("read_only_operations_only") is not True:
            print(f"    [FAIL] {yf}: read_only_operations_only is not true")
            read_only_ok = False
    checks_total += 1
    if check("read_only_operations_only=true in all YAML files", read_only_ok):
        checks_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary:")
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
