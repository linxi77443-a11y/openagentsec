#!/usr/bin/env python3
"""Validate Limited Authorized API Dry-Run Plan.

All checks are local-only: no network calls, no credential loading,
no real endpoint access. Only validates file existence, placeholder
content, flag declarations, and policy definitions.
"""

import os
import re
import sys
import yaml
from pathlib import Path

PLAN_DIR = Path("api_provider/authorized_dry_run_plan")
REQUIRED_FILES = [
    "README.md",
    "limited_authorized_dry_run_schema.md",
    "preflight_checklist.md",
    "test_target_readiness_gate.yaml",
    "credential_readiness_checklist.md",
    "rate_limit_request_budget_policy.md",
    "allowed_test_bundle_definition.yaml",
    "rollback_stop_condition_policy.md",
    "dry_run_approval_packet_template.md",
    "dry_run_plan_validation_result.yaml",
    "dry_run_plan_validation_report.md",
]

FORBIDDEN_PATTERNS = {
    "real URL": re.compile(r'https?://(?!.*(?:example\.com|\[PLACEHOLDER\]))'),
    "real token": re.compile(r'(?i)(sk-[a-zA-Z0-9]{10,}|ghp_[a-zA-Z0-9]{10,})'),
    "real email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?<!example\.com)'),
    "real API key": re.compile(r'(?i)(api[_-]?key|apikey|secret|token)\s*[:=]\s*["\']?[a-zA-Z0-9]{16,}["\']?'),
}

YAML_FLAG_FILES = [
    "test_target_readiness_gate.yaml",
    "allowed_test_bundle_definition.yaml",
]

YAML_FLAG_CHECKS = {
    "authorization_required": True,
    "approval_status": "not_approved",
    "execution_allowed": False,
    "credentials_loaded": False,
    "real_target_connected": False,
    "network_called": False,
    "evidence_generated": False,
    "production_target_allowed": False,
    "dry_run_plan_only": True,
}

MARKDOWN_FILES_WITH_FLAGS = [
    "limited_authorized_dry_run_schema.md",
    "README.md",
]

MARKDOWN_FLAG_CHECKS = {
    "authorization_required": "true",
    "approval_status": "not_approved",
    "execution_allowed": "false",
    "credentials_loaded": "false",
    "real_target_connected": "false",
    "network_called": "false",
    "evidence_generated": "false",
    "production_target_allowed": "false",
}

REQUIRED_POLICY_FILES = {
    "rate_limit_request_budget_policy.md": ["requests_per_minute", "request_budget_total", "rate_limit_tier"],
    "rollback_stop_condition_policy.md": ["stop_condition", "rollback", "dry_run_plan_only"],
    "dry_run_approval_packet_template.md": ["approval", "not_approved", "authorization_required"],
    "allowed_test_bundle_definition.yaml": ["bundle_id", "allowed_operations", "prohibited_operations"],
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
    print("Limited Authorized API Dry-Run Plan Validation")
    print("=" * 60)

    # 1. All files exist
    print("\n[Check 1] All plan files exist...")
    all_exist = True
    for f in REQUIRED_FILES:
        path = PLAN_DIR / f
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
        content = (PLAN_DIR / f).read_text()
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
            content = (PLAN_DIR / f).read_text()
            matches = pattern_re.findall(content)
            if matches and not all(m == "https://placeholder" or "example.com" in str(m) or "[PLACEHOLDER]" in str(m) for m in matches):
                print(f"    [FAIL] {f}: Found {pattern_name}")
                clean = False
        checks_total += 1
        if check(f"No {pattern_name} in any file", clean):
            checks_passed += 1

    # 7-14. Flag checks in YAML files
    print("\n[Check 7-14] Flag declarations in YAML files...")
    all_yaml_flags_ok = True
    for yf in YAML_FLAG_FILES:
        path = PLAN_DIR / yf
        data = yaml.safe_load(path.read_text())
        for flag, expected in YAML_FLAG_CHECKS.items():
            actual = data.get(flag)
            if actual != expected:
                print(f"    [FAIL] {yf}: {flag}={actual}, expected {expected}")
                all_yaml_flags_ok = False
            else:
                pass  # silent pass for individual flags
    checks_total += 1
    if check("All YAML flag declarations correct", all_yaml_flags_ok):
        checks_passed += 1

    print("\n[Check 7-14] Flag declarations in markdown files...")
    all_md_flags_ok = True
    for mf in MARKDOWN_FILES_WITH_FLAGS:
        content = (PLAN_DIR / mf).read_text()
        for flag, expected in MARKDOWN_FLAG_CHECKS.items():
            flag_pattern = f"{flag}: {expected}"
            if flag_pattern not in content:
                print(f"    [FAIL] {mf}: {flag}: {expected} not found")
                all_md_flags_ok = False
    checks_total += 1
    if check("All markdown flag declarations correct", all_md_flags_ok):
        checks_passed += 1

    # 15. Rate limit / request budget defined
    print("\n[Check 15] Rate limit / request budget defined...")
    budget_file = PLAN_DIR / "rate_limit_request_budget_policy.md"
    budget_content = budget_file.read_text()
    budget_ok = all(kw in budget_content for kw in REQUIRED_POLICY_FILES["rate_limit_request_budget_policy.md"])
    checks_total += 1
    if check("Rate limit and request budget policy defined", budget_ok):
        checks_passed += 1

    # 16. Rollback / stop conditions defined
    print("\n[Check 16] Rollback / stop conditions defined...")
    rollback_file = PLAN_DIR / "rollback_stop_condition_policy.md"
    rollback_content = rollback_file.read_text()
    rollback_ok = all(kw in rollback_content for kw in REQUIRED_POLICY_FILES["rollback_stop_condition_policy.md"])
    checks_total += 1
    if check("Rollback and stop conditions defined", rollback_ok):
        checks_passed += 1

    # 17. Human approval gate defined
    print("\n[Check 17] Human approval gate defined...")
    approval_file = PLAN_DIR / "dry_run_approval_packet_template.md"
    approval_content = approval_file.read_text()
    approval_ok = all(kw in approval_content for kw in REQUIRED_POLICY_FILES["dry_run_approval_packet_template.md"])
    checks_total += 1
    if check("Human approval gate defined", approval_ok):
        checks_passed += 1

    # 18. Allowed test bundle defined
    print("\n[Check 18] Allowed test bundle defined...")
    bundle_file = PLAN_DIR / "allowed_test_bundle_definition.yaml"
    bundle_data = yaml.safe_load(bundle_file.read_text())
    bundles = bundle_data.get("allowed_bundles", [])
    bundle_ok = len(bundles) >= 1
    if bundle_ok:
        for b in bundles:
            if not b.get("allowed_operations") or b.get("prohibited_operations") is None:
                bundle_ok = False
    checks_total += 1
    if check(f"Allowed test bundle defined ({len(bundles)} bundles)", bundle_ok):
        checks_passed += 1

    # 19. production_target_allowed=false
    print("\n[Check 19] production_target_allowed=false...")
    prod_allowed_ok = True
    for yf in YAML_FLAG_FILES + ["rate_limit_request_budget_policy.md"]:
        content = (PLAN_DIR / yf).read_text()
        if yf.endswith(".yaml"):
            data = yaml.safe_load(content)
            if data.get("production_target_allowed") is not False:
                print(f"    [FAIL] {yf}: production_target_allowed is not false")
                prod_allowed_ok = False
        else:
            if "production_target_allowed: false" not in content:
                print(f"    [FAIL] {yf}: production_target_allowed: false not found")
                prod_allowed_ok = False
    checks_total += 1
    if check("production_target_allowed=false in all config files", prod_allowed_ok):
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
