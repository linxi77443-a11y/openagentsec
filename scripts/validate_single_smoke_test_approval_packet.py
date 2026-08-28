#!/usr/bin/env python3
"""Validate Single Smoke Test Approval Packet.

All checks are local-only: no network calls, no credential loading,
no real endpoint access. Only validates file existence, placeholder
content, flag declarations, and phase references.
"""

import os
import re
import sys
import yaml
from pathlib import Path

PACKET_DIR = Path("api_provider/smoke_test_approval_packet")
REQUIRED_FILES = [
    "README.md",
    "approval_packet_schema.md",
    "go_no_go_gate_checklist.md",
    "smoke_test_approval_packet_template.md",
    "final_pre_execution_readiness_summary.yaml",
    "operator_signoff_placeholder.md",
    "risk_acceptance_placeholder.md",
    "execution_hold_statement.md",
    "approval_packet_validation_result.yaml",
    "approval_packet_validation_report.md",
]

FORBIDDEN_PATTERNS = {
    "real URL": re.compile(r'https?://(?!.*(?:example\.com|\[PLACEHOLDER\]))'),
    "real token": re.compile(r'(?i)(sk-[a-zA-Z0-9]{10,}|ghp_[a-zA-Z0-9]{10,})'),
    "real email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?<!example\.com)'),
    "real API key": re.compile(r'(?i)(api[_-]?key|apikey|secret|token)\s*[:=]\s*["\']?[a-zA-Z0-9]{16,}["\']?'),
}

YAML_FLAG_FILES = [
    "final_pre_execution_readiness_summary.yaml",
    "approval_packet_validation_result.yaml",
]

YAML_FLAG_CHECKS = {
    "approval_packet_ready": True,
    "approval_status": "not_approved",
    "go_no_go_status": "no_go",
    "execution_allowed": False,
    "human_approval_required": True,
    "operator_signoff_required": True,
    "risk_acceptance_required": True,
    "credentials_loaded": False,
    "real_target_connected": False,
    "network_called": False,
    "evidence_generated": False,
    "production_target_allowed": False,
}

MARKDOWN_FILES_WITH_FLAGS = [
    "README.md",
    "approval_packet_schema.md",
]

MARKDOWN_FLAG_CHECKS = {
    "approval_packet_ready": "true",
    "approval_status": "not_approved",
    "go_no_go_status": "no_go",
    "execution_allowed": "false",
    "human_approval_required": "true",
    "operator_signoff_required": "true",
    "risk_acceptance_required": "true",
    "credentials_loaded": "false",
    "real_target_connected": "false",
    "network_called": "false",
    "evidence_generated": "false",
    "production_target_allowed": "false",
}

PHASE_REFERENCE_FILES = [
    "README.md",
    "approval_packet_schema.md",
    "smoke_test_approval_packet_template.md",
    "final_pre_execution_readiness_summary.yaml",
]

PHASE_REFERENCES = {
    "Phase 31B": ["onboarding", "Phase 31B", "authorized_target_onboarding"],
    "Phase 31D": ["authorized_dry_run_plan", "Phase 31D", "dry_run_plan"],
    "Phase 31E": ["single_smoke_test_design", "Phase 31E", "smoke_test_design"],
}

EXECUTION_HOLD_KEYWORDS = ["execution_hold", "execution hold", "EXECUTION_HOLD"]


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
    print("Single Smoke Test Approval Packet Validation")
    print("=" * 60)

    # 1. All files exist
    print("\n[Check 1] All files exist...")
    all_exist = True
    for f in REQUIRED_FILES:
        path = PACKET_DIR / f
        exists = path.exists()
        if not exists:
            print(f"    [FAIL] Missing: {f}")
        all_exist = all_exist and exists
    checks_total += 1
    if check(f"All {len(REQUIRED_FILES)} files exist", all_exist):
        checks_passed += 1

    # 2-5. No real URLs, tokens, emails, API keys
    for pattern_name, pattern_re in FORBIDDEN_PATTERNS.items():
        print(f"\n[Check 2-5] No {pattern_name}...")
        clean = True
        for f in REQUIRED_FILES:
            content = (PACKET_DIR / f).read_text()
            matches = pattern_re.findall(content)
            if matches:
                print(f"    [FAIL] {f}: Found {pattern_name}")
                clean = False
        checks_total += 1
        if check(f"No {pattern_name} in any file", clean):
            checks_passed += 1

    # 6-16. Flag checks in YAML files
    print("\n[Check 6-16] Flag declarations in YAML files...")
    all_yaml_flags_ok = True
    for yf in YAML_FLAG_FILES:
        path = PACKET_DIR / yf
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
    print("\n[Check 6-16] Flag declarations in markdown files...")
    all_md_flags_ok = True
    for mf in MARKDOWN_FILES_WITH_FLAGS:
        content = (PACKET_DIR / mf).read_text()
        for flag, expected in MARKDOWN_FLAG_CHECKS.items():
            flag_pattern = f"{flag}: {expected}"
            if flag_pattern not in content:
                print(f"    [FAIL] {mf}: {flag}: {expected} not found")
                all_md_flags_ok = False
    checks_total += 1
    if check("All markdown flag declarations correct", all_md_flags_ok):
        checks_passed += 1

    # 17. References Phase 31B onboarding
    print("\n[Check 17] References Phase 31B onboarding...")
    ref_31b_ok = True
    for f in PHASE_REFERENCE_FILES:
        content = (PACKET_DIR / f).read_text()
        has_ref = any(kw in content for kw in PHASE_REFERENCES["Phase 31B"])
        if not has_ref:
            print(f"    [FAIL] {f}: No Phase 31B reference found")
            ref_31b_ok = False
    checks_total += 1
    if check("All phase reference files reference Phase 31B", ref_31b_ok):
        checks_passed += 1

    # 18. References Phase 31D dry-run plan
    print("\n[Check 18] References Phase 31D dry-run plan...")
    ref_31d_ok = True
    for f in PHASE_REFERENCE_FILES:
        content = (PACKET_DIR / f).read_text()
        has_ref = any(kw in content for kw in PHASE_REFERENCES["Phase 31D"])
        if not has_ref:
            print(f"    [FAIL] {f}: No Phase 31D reference found")
            ref_31d_ok = False
    checks_total += 1
    if check("All phase reference files reference Phase 31D", ref_31d_ok):
        checks_passed += 1

    # 19. References Phase 31E smoke test design
    print("\n[Check 19] References Phase 31E smoke test design...")
    ref_31e_ok = True
    for f in PHASE_REFERENCE_FILES:
        content = (PACKET_DIR / f).read_text()
        has_ref = any(kw in content for kw in PHASE_REFERENCES["Phase 31E"])
        if not has_ref:
            print(f"    [FAIL] {f}: No Phase 31E reference found")
            ref_31e_ok = False
    checks_total += 1
    if check("All phase reference files reference Phase 31E", ref_31e_ok):
        checks_passed += 1

    # 20. Execution hold declared
    print("\n[Check 20] Execution hold declared...")
    hold_ok = True
    for f in REQUIRED_FILES:
        content = (PACKET_DIR / f).read_text()
        has_hold = any(kw in content for kw in EXECUTION_HOLD_KEYWORDS)
        if not has_hold:
            print(f"    [FAIL] {f}: No execution_hold declaration found")
            hold_ok = False
    checks_total += 1
    if check("All files declare execution_hold", hold_ok):
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
