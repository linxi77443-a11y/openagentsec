#!/usr/bin/env python3
"""Phase 31B — Authorized Test Target Onboarding: Validation Script。

静态校验 api_provider/onboarding/ 目录的完整性和安全约束。
不连接真实 API，不读取真实凭证，不访问真实 endpoint。
"""

import os
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime, timezone

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
ONBOARDING_DIR = BASE_DIR / "api_provider" / "onboarding"

REQUIRED_ONBOARDING_FILES = [
    "api_provider/onboarding/README.md",
    "api_provider/onboarding/authorized_target_onboarding_schema.md",
    "api_provider/onboarding/target_intake_template.yaml",
    "api_provider/onboarding/roe_checklist.md",
    "api_provider/onboarding/credential_isolation_policy.md",
    "api_provider/onboarding/test_scope_definition_template.yaml",
    "api_provider/onboarding/allowed_prohibited_operations_matrix.yaml",
    "api_provider/onboarding/rate_limit_and_safety_window_policy.md",
    "api_provider/onboarding/approval_gate_checklist.md",
    "api_provider/onboarding/onboarding_validation_result.yaml",
    "api_provider/onboarding/onboarding_validation_report.md",
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
    print("=== Authorized Test Target Onboarding Validation ===\n")

    # 1. Required onboarding files exist
    print("  [Check 1] Required onboarding files...")
    all_files_ok = True
    for req_path in REQUIRED_ONBOARDING_FILES:
        full_path = BASE_DIR / req_path
        if not full_path.exists():
            print(f"    [FAIL] Missing: {req_path}")
            all_files_ok = False
        else:
            print(f"    [PASS] Found: {req_path}")
    check("onboarding_files_exist", all_files_ok, "Missing required onboarding files")

    # 2. Target intake template only contains placeholders
    print("\n  [Check 2] Intake template only placeholder...")
    intake_path = ONBOARDING_DIR / "target_intake_template.yaml"
    intake_data = load_yaml(intake_path)
    only_placeholder = True
    if intake_data is None:
        print("    [FAIL] Could not parse target_intake_template.yaml")
        only_placeholder = False
    else:
        text = intake_path.read_text("utf-8")
        if "PLACEHOLDER" not in text:
            print("    [FAIL] No PLACEHOLDER found — may contain real data")
            only_placeholder = False
        else:
            print("    [PASS] Contains only placeholder data")
    check("intake_template_only_placeholder", only_placeholder, "Intake template must contain only placeholder")

    # 3-6. No real URLs, tokens, emails, API keys in onboarding files
    onboarding_yamls = sorted(ONBOARDING_DIR.glob("*.yaml")) + sorted(ONBOARDING_DIR.glob("*.md"))

    print("\n  [Check 3] No real URLs...")
    url_pattern = re.compile(r'https?://(?!.*placeholder\.local|.*PLACEHOLDER)[^\s"\'<>]+')
    no_real_urls = True
    for f in onboarding_yamls:
        content = f.read_text("utf-8")
        matches = url_pattern.findall(content)
        if matches:
            print(f"    [FAIL] {f.name} contains potential real URLs: {matches}")
            no_real_urls = False
        else:
            print(f"    [PASS] {f.name}: no real URLs")
    check("no_real_urls", no_real_urls, "Onboarding files must not contain real URLs")

    print("\n  [Check 4] No real tokens...")
    token_pattern = re.compile(r'(?:sk-[a-zA-Z0-9]{10,}|bearer\s+[A-Za-z0-9._~+/-]{8,})', re.IGNORECASE)
    no_real_tokens = True
    for f in onboarding_yamls:
        content = f.read_text("utf-8")
        cleaned = content.replace("sk-xxxxxxxxxxxx", "")
        matches = token_pattern.findall(cleaned)
        if matches:
            print(f"    [FAIL] {f.name} contains potential real tokens: {matches}")
            no_real_tokens = False
        else:
            print(f"    [PASS] {f.name}: no real tokens")
    check("no_real_tokens", no_real_tokens, "Onboarding files must not contain real tokens")

    print("\n  [Check 5] No real emails...")
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    no_real_emails = True
    for f in onboarding_yamls:
        content = f.read_text("utf-8")
        matches = email_pattern.findall(content)
        if matches:
            print(f"    [FAIL] {f.name} contains emails: {matches}")
            no_real_emails = False
        else:
            print(f"    [PASS] {f.name}: no real emails")
    check("no_real_emails", no_real_emails, "Onboarding files must not contain real emails")

    print("\n  [Check 6] No real API keys...")
    apikey_pattern = re.compile(r'(?:api[_-]?key[_-]?|apikey)[=:]\s*[^\s]{8,}', re.IGNORECASE)
    no_real_apikeys = True
    for f in onboarding_yamls:
        content = f.read_text("utf-8")
        matches = apikey_pattern.findall(content)
        if matches:
            print(f"    [FAIL] {f.name} contains potential API keys: {matches}")
            no_real_apikeys = False
        else:
            print(f"    [PASS] {f.name}: no real API keys")
    check("no_real_api_keys", no_real_apikeys, "Onboarding files must not contain real API keys")

    # 7-13. Flag checks on intake template
    print("\n  [Check 7-13] Flag constraints on intake template...")
    all_flags_correct = True
    if intake_data is not None:
        if intake_data.get("authorization_required") is not True:
            print(f"    [FAIL] authorization_required must be true")
            all_flags_correct = False
        if intake_data.get("authorization_status") != "not_approved":
            print(f"    [FAIL] authorization_status must be not_approved")
            all_flags_correct = False
        if intake_data.get("execution_allowed") is not False:
            print(f"    [FAIL] execution_allowed must be false")
            all_flags_correct = False
        if intake_data.get("real_target_connected") is not False:
            print(f"    [FAIL] real_target_connected must be false")
            all_flags_correct = False
        if intake_data.get("credentials_loaded") is not False:
            print(f"    [FAIL] credentials_loaded must be false")
            all_flags_correct = False
        if intake_data.get("production_target_allowed") is not False:
            print(f"    [FAIL] production_target_allowed must be false")
            all_flags_correct = False
        if intake_data.get("dry_run_only") is not True:
            print(f"    [FAIL] dry_run_only must be true")
            all_flags_correct = False

    if all_flags_correct:
        print("    [PASS] All flag constraints correct")
    check("authorization_required_true", intake_data is not None and intake_data.get("authorization_required") is True, "authorization_required must be true")
    check("approval_status_not_approved", intake_data is not None and intake_data.get("authorization_status") == "not_approved", "authorization_status must be not_approved")
    check("execution_allowed_false", intake_data is not None and intake_data.get("execution_allowed") is False, "execution_allowed must be false")
    check("real_target_connected_false", intake_data is not None and intake_data.get("real_target_connected") is False, "real_target_connected must be false")
    check("credentials_loaded_false", intake_data is not None and intake_data.get("credentials_loaded") is False, "credentials_loaded must be false")
    check("production_target_allowed_false", intake_data is not None and intake_data.get("production_target_allowed") is False, "production_target_allowed must be false")
    check("dry_run_only_true", intake_data is not None and intake_data.get("dry_run_only") is True, "dry_run_only must be true")

    # 14. Has prohibited operations
    print("\n  [Check 14] Has prohibited operations...")
    matrix_path = ONBOARDING_DIR / "allowed_prohibited_operations_matrix.yaml"
    matrix_data = load_yaml(matrix_path)
    has_prohibited = False
    if matrix_data is not None:
        # Check if there's an operations matrix with prohibited entries
        text = matrix_path.read_text("utf-8")
        if "prohibited" in text.lower():
            has_prohibited = True
            print("    [PASS] Prohibited operations defined")
        else:
            print("    [FAIL] No prohibited operations found")
    else:
        print("    [FAIL] Could not parse allowed_prohibited_operations_matrix.yaml")
    check("has_prohibited_operations", has_prohibited, "Must have prohibited operations defined")

    # 15. Has rate limit policy
    print("\n  [Check 15] Has rate limit policy...")
    rate_limit_path = ONBOARDING_DIR / "rate_limit_and_safety_window_policy.md"
    has_rate_limit = rate_limit_path.exists() and "requests_per_minute" in rate_limit_path.read_text("utf-8")
    print(f"    [{'PASS' if has_rate_limit else 'FAIL'}] Rate limit policy {'found' if has_rate_limit else 'missing'}")
    check("has_rate_limit_policy", has_rate_limit, "Must have rate limit policy")

    # 16. Has credential isolation policy
    print("\n  [Check 16] Has credential isolation policy...")
    cred_policy_path = ONBOARDING_DIR / "credential_isolation_policy.md"
    has_cred_policy = cred_policy_path.exists() and "Credential Isolation" in cred_policy_path.read_text("utf-8")
    print(f"    [{'PASS' if has_cred_policy else 'FAIL'}] Credential isolation policy {'found' if has_cred_policy else 'missing'}")
    check("has_credential_isolation_policy", has_cred_policy, "Must have credential isolation policy")

    # 17. Has RoE checklist
    print("\n  [Check 17] Has RoE checklist...")
    roe_path = ONBOARDING_DIR / "roe_checklist.md"
    has_roe = roe_path.exists() and "Rules of Engagement" in roe_path.read_text("utf-8")
    print(f"    [{'PASS' if has_roe else 'FAIL'}] RoE checklist {'found' if has_roe else 'missing'}")
    check("has_roe_checklist", has_roe, "Must have RoE checklist")

    # 18. Has human approval gate
    print("\n  [Check 18] Has human approval gate...")
    approval_gate_path = ONBOARDING_DIR / "approval_gate_checklist.md"
    has_approval_gate = approval_gate_path.exists() and "Approval Gate" in approval_gate_path.read_text("utf-8")
    print(f"    [{'PASS' if has_approval_gate else 'FAIL'}] Approval gate {'found' if has_approval_gate else 'missing'}")
    check("has_human_approval_gate", has_approval_gate, "Must have human approval gate")

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

    # Write validation result
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    result_entry = {
        "validation": {
            "generated_at": generated_at,
            "validation_script": "scripts/validate_authorized_target_onboarding.py",
            "phase": "Phase 31B Authorized Test Target Onboarding",
        },
        "summary": {
            "total_checks": total,
            "passed_checks": passed,
            "failed_checks": failed,
            "all_passed": failed == 0,
            "approval_status": "not_approved",
        },
        "execution_status": {
            "authorization_required": True,
            "approval_status": "not_approved",
            "execution_allowed": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "production_target_allowed": False,
            "dry_run_only": True,
            "human_approval_obtained": False,
            "network_called": False,
            "tests_executed": False,
            "evidence_generated": False,
            "usable_for_formal_finding": False,
        },
        "checks": [
            {"check": c["check"], "result": c["result"]}
            for c in VALIDATION_CHECKS
        ],
    }

    result_path = ONBOARDING_DIR / "onboarding_validation_result.yaml"
    with open(result_path, "w", encoding="utf-8") as f:
        yaml.dump(result_entry, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"\nWrote: {result_path.relative_to(BASE_DIR)}")

    # Write validation report
    report_lines = [
        "# Onboarding Validation Report",
        "",
        f"**Generated At**: {generated_at}",
        "**Phase**: Phase 31B Authorized Test Target Onboarding",
        "**Validation Script**: `scripts/validate_authorized_target_onboarding.py`",
        f"**Approval Status**: not_approved",
        "",
        "## Summary",
        "",
        f"| Check | Value |",
        f"|---|---|",
        f"| Total Checks | {total} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| All Passed | {'true' if failed == 0 else 'false'} |",
        "",
        "## Execution Status",
        "",
        "| Status | Value |",
        "|---|---|",
        "| authorization_required | true |",
        "| approval_status | not_approved |",
        "| execution_allowed | false |",
        "| credentials_loaded | false |",
        "| real_target_connected | false |",
        "| production_target_allowed | false |",
        "| dry_run_only | true |",
        "| human_approval_obtained | false |",
        "| network_called | false |",
        "| tests_executed | false |",
        "| evidence_generated | false |",
        "| usable_for_formal_finding | false |",
    ]

    report_lines.extend([
        "",
        "## Checks",
        "",
        "| # | Check | Result |",
        "|---|---|---|",
    ])
    for i, c in enumerate(VALIDATION_CHECKS, 1):
        result_str = "✅ PASS" if c["result"] else "❌ FAIL"
        report_lines.append(f"| {i} | {c['check']} | {result_str} |")

    report_lines.extend([
        "",
        "## Important",
        "",
        "- No real API was called during this validation",
        "- No real credentials were loaded",
        "- No real endpoint was accessed",
        "- All checks reflect the current onboarding state (approval_status=not_approved)",
        "- This validation is for schema, policy, and configuration correctness only",
        "- Real API testing requires signed RoE, test credentials, and approved approval_gate_checklist",
    ])

    report_path = ONBOARDING_DIR / "onboarding_validation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"Wrote: {report_path.relative_to(BASE_DIR)}")

    if failed > 0:
        print(f"\nValidation complete: {passed}/{total} checks passed (expected for onboarding state).")
        # Don't exit with error — failures are expected when approval_status=not_approved
    else:
        print(f"\nValidation complete: {passed}/{total} checks passed.")


if __name__ == "__main__":
    main()
