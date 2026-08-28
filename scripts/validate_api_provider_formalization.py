#!/usr/bin/env python3
"""Phase 31 — Generic API Provider Formalization: Provider Validation。

静态校验 api_provider/ 目录的完整性和安全性。
"""

import os
import sys
import yaml
import re
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
API_PROVIDER_DIR = BASE_DIR / "api_provider"
SAMPLE_TARGETS_DIR = API_PROVIDER_DIR / "sample_targets"

REQUIRED_PATHS = [
    "api_provider/README.md",
    "api_provider/api_provider_schema.md",
    "api_provider/target_profile_schema.md",
    "api_provider/provider_config_template.local.example.yaml",
    "api_provider/request_response_normalization_schema.md",
    "api_provider/provider_safety_guardrails.md",
    "api_provider/provider_execution_boundary.md",
    "scripts/api_provider_dry_run_simulator.py",
    "scripts/validate_api_provider_formalization.py",
]

VALIDATION_CHECKS = []


def check(name, condition, fail_msg=""):
    """Register a validation check."""
    result = bool(condition)
    VALIDATION_CHECKS.append({"check": name, "result": result, "fail_msg": fail_msg})
    status = "PASS" if result else "FAIL"
    print(f"  [{status}] {name}")
    return result


def load_yaml(path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    print("=== Generic API Provider Formalization Validation ===\n")

    # 1. Required paths exist
    print("  [Check 1] Required paths...")
    all_paths_ok = True
    for req_path in REQUIRED_PATHS:
        full_path = BASE_DIR / req_path
        if not full_path.exists():
            print(f"    [FAIL] Missing: {req_path}")
            all_paths_ok = False
        else:
            print(f"    [PASS] Found: {req_path}")
    check("required_paths_exist", all_paths_ok, "Missing required api_provider files")

    # 2. Sample targets are parseable
    print("\n  [Check 2] Sample targets parseable...")
    sample_targets = sorted(SAMPLE_TARGETS_DIR.glob("*.yaml"))
    targets_loaded = []
    all_parseable = True
    for tf in sample_targets:
        data = load_yaml(tf)
        if data is None:
            print(f"    [FAIL] Could not parse: {tf.name}")
            all_parseable = False
        else:
            print(f"    [PASS] Parsed: {tf.name}")
            targets_loaded.append(data)
    check("sample_targets_parseable", all_parseable, "Sample targets must be valid YAML")

    # 3. No real URLs in sample targets
    print("\n  [Check 3] No real URLs...")
    url_pattern = re.compile(r'https?://(?!.*placeholder\.local)[^\s"\'<>]+')
    no_real_urls = True
    for tf in sample_targets:
        content = tf.read_text("utf-8")
        matches = url_pattern.findall(content)
        if matches:
            print(f"    [FAIL] {tf.name} contains potential real URLs: {matches}")
            no_real_urls = False
        else:
            print(f"    [PASS] {tf.name}: no real URLs")
    check("no_real_urls", no_real_urls, "Sample targets must not contain real URLs")

    # 4. No real tokens in sample targets
    print("\n  [Check 4] No real tokens...")
    token_pattern = re.compile(r'(?:sk-[a-zA-Z0-9]{10,}|bearer\s+[A-Za-z0-9._~+/-]{8,})', re.IGNORECASE)
    no_real_tokens = True
    for tf in sample_targets:
        content = tf.read_text("utf-8")
        # Allow the placeholder pattern
        cleaned = content.replace("sk-placeholder-replace-with-real-key-in-local-config", "")
        matches = token_pattern.findall(cleaned)
        if matches:
            print(f"    [FAIL] {tf.name} contains potential real tokens: {matches}")
            no_real_tokens = False
        else:
            print(f"    [PASS] {tf.name}: no real tokens")
    check("no_real_tokens", no_real_tokens, "Sample targets must not contain real tokens")

    # 5. No real emails in sample targets
    print("\n  [Check 5] No real emails...")
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    no_real_emails = True
    for tf in sample_targets:
        content = tf.read_text("utf-8")
        matches = email_pattern.findall(content)
        if matches:
            print(f"    [FAIL] {tf.name} contains emails: {matches}")
            no_real_emails = False
        else:
            print(f"    [PASS] {tf.name}: no real emails")
    check("no_real_emails", no_real_emails, "Sample targets must not contain real emails")

    # 6-11. Sample target field checks
    print("\n  [Check 6-11] Sample target field constraints...")
    all_flags_correct = True
    for data in targets_loaded:
        tid = data.get("target_id", "unknown")
        if data.get("real_target") is not False:
            print(f"    [FAIL] {tid}: real_target must be false")
            all_flags_correct = False
        if data.get("dry_run_only") is not True:
            print(f"    [FAIL] {tid}: dry_run_only must be true")
            all_flags_correct = False
        if data.get("execution_allowed") is not False:
            print(f"    [FAIL] {tid}: execution_allowed must be false")
            all_flags_correct = False
        if data.get("usable_for_real_test") is not False:
            print(f"    [FAIL] {tid}: usable_for_real_test must be false")
            all_flags_correct = False
    if all_flags_correct:
        print("    [PASS] All target field constraints correct")

    check("all_targets_real_target_false", all_flags_correct, "All targets must have real_target=false")
    check("all_targets_dry_run_only_true", all_flags_correct, "All targets must have dry_run_only=true")
    check("all_targets_execution_allowed_false", all_flags_correct, "All targets must have execution_allowed=false")
    check("all_targets_usable_for_real_test_false", all_flags_correct, "All targets must have usable_for_real_test=false")

    # 12. Provider validation result checks
    print("\n  [Check 12] Provider validation result...")
    validation_result_path = API_PROVIDER_DIR / "provider_validation_result.yaml"
    if validation_result_path.exists():
        vdata = load_yaml(validation_result_path)
        if vdata:
            exec_status = vdata.get("execution_status", {})
            nc = exec_status.get("network_called", None)
            cl = exec_status.get("credentials_loaded", None)
            rt = exec_status.get("real_target_connected", None)
            te = exec_status.get("tests_executed", None)
            eg = exec_status.get("evidence_generated", None)
            uf = exec_status.get("usable_for_formal_finding", None)

            check("network_called_false", nc is False, "network_called must be false")
            check("credentials_loaded_false", cl is False, "credentials_loaded must be false")
            check("real_target_connected_false", rt is False, "real_target_connected must be false")
            check("tests_executed_false", te is False, "tests_executed must be false")
            check("evidence_generated_false", eg is False, "evidence_generated must be false")
            check("usable_for_formal_finding_false", uf is False, "usable_for_formal_finding must be false")
        else:
            print("    [FAIL] Could not parse validation result")
            for c in ["network_called", "credentials_loaded", "real_target_connected",
                       "tests_executed", "evidence_generated", "usable_for_formal_finding"]:
                check(f"{c}_false", False, f"Validation result not parseable")
    else:
        print("    [FAIL] provider_validation_result.yaml not found")
        print("    Run python3 scripts/api_provider_dry_run_simulator.py first")
        for c in ["network_called", "credentials_loaded", "real_target_connected",
                   "tests_executed", "evidence_generated", "usable_for_formal_finding"]:
            check(f"{c}_false", False, f"Validation result not found")

    # Summary
    total = len(VALIDATION_CHECKS)
    passed = sum(1 for c in VALIDATION_CHECKS if c["result"])
    failed = total - passed

    print(f"\n=== Validation Summary ===")
    print(f"Total checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed checks:")
        for c in VALIDATION_CHECKS:
            if not c["result"]:
                print(f"  - {c['check']}: {c['fail_msg']}")
        sys.exit(1)
    else:
        print("All validation checks passed!")

    # Write validation result entry
    from datetime import datetime, timezone
    GENERATED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    result_entry = {
        "validation_script": "scripts/validate_api_provider_formalization.py",
        "generated_at": GENERATED_AT,
        "total_checks": total,
        "passed_checks": passed,
        "failed_checks": failed,
        "all_passed": failed == 0,
        "checks": [
            {"check": c["check"], "result": c["result"]}
            for c in VALIDATION_CHECKS
        ],
    }

    # Update validation result or write standalone
    # We'll write a companion entry to avoid overwriting the simulator output
    print(f"\nValidation complete: {passed}/{total} checks passed.")


if __name__ == "__main__":
    main()
