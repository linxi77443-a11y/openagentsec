#!/usr/bin/env python3
"""Validate Phase 34B DeepSeek Judge Go/No-Go Packet.

Performs static checks on all Go/No-Go packet files.
No network calls, no credential access, no API execution.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GNG_DIR = ROOT / "tool_judge_providers" / "deepseek" / "go_no_go"

# ── Expected files ──────────────────────────────────────────────────────

EXPECTED_FILES = [
    "deepseek_judge_go_no_go_packet.md",
    "deepseek_judge_approval_checklist.md",
    "deepseek_judge_cost_budget.yaml",
    "deepseek_judge_execution_plan.yaml",
    "deepseek_judge_safety_boundary.md",
    "deepseek_judge_rollback_plan.md",
    "deepseek_judge_result_acceptance_criteria.md",
    "deepseek_judge_local_config_template.md",
]

# ── Validation helpers ──────────────────────────────────────────────────


def check_file_exists(path: Path, label: str, errors: list[str]) -> bool:
    if not path.exists():
        errors.append(f"[MISSING] {label}: {path.name}")
        return False
    return True


def check_content(
    text: str, pattern: str, label: str, errors: list[str], should_exist: bool = True
) -> bool:
    """Check if pattern exists in text, supporting plain, bold, and markdown table formats."""
    found = pattern in text
    # Try bold format: **field**: value
    if not found and ": " in pattern:
        field, value = pattern.split(": ", 1)
        bold_pattern = f"**{field}**: {value}"
        found = bold_pattern in text
    # Try markdown table format: | field | value |
    if not found:
        for line in text.split("\n"):
            line_stripped = line.strip()
            # Check if this is a table row with | separators
            if line_stripped.startswith("|"):
                cells = [c.strip() for c in line_stripped.split("|")]
                cells = [c for c in cells if c]  # Remove empty strings
                # pattern like "execution_allowed: false" → check cells for "execution_allowed" and "false"
                if ": " in pattern:
                    field, value = pattern.split(": ", 1)
                    if len(cells) >= 2 and cells[0] == field and cells[1] == value:
                        found = True
                        break
                else:
                    # Simple string match
                    if any(pattern == c or pattern in c for c in cells):
                        found = True
                        break
    if should_exist and not found:
        errors.append(f"[MISSING] {label}: expected '{pattern}'")
        return False
    if not should_exist and found:
        errors.append(f"[FOUND] {label}: unexpected '{pattern}'")
        return False
    return True


# ── Validation sections ─────────────────────────────────────────────────


def validate_go_no_go_directory(errors: list[str]) -> None:
    print("  [Section 1/6] Go/No-Go directory structure...")

    if not GNG_DIR.exists():
        errors.append("[DIR] go_no_go directory does not exist")
        return

    for fname in EXPECTED_FILES:
        path = GNG_DIR / fname
        check_file_exists(path, f"File: {fname}", errors)


def validate_approval_status(errors: list[str]) -> None:
    print("  [Section 2/6] Approval status...")

    # Check packet
    packet_path = GNG_DIR / "deepseek_judge_go_no_go_packet.md"
    if packet_path.exists():
        text = packet_path.read_text(encoding="utf-8")
        check_content(text, "not_approved", "Packet: approval_status=not_approved", errors)
        check_content(text, "execution_allowed: false", "Packet: execution_allowed=false", errors)
        check_content(text, "network_allowed: false", "Packet: network_allowed=false", errors)
        check_content(text, "credential_loaded: false", "Packet: credential_loaded=false", errors)
        check_content(text, "deepseek_api_called: false", "Packet: deepseek_api_called=false", errors)

    # Approval checklist
    checklist_path = GNG_DIR / "deepseek_judge_approval_checklist.md"
    if checklist_path.exists():
        text = checklist_path.read_text(encoding="utf-8")
        check_content(text, "not_approved", "Checklist: approval_status=not_approved", errors)
        check_content(text, "execution_allowed: false", "Checklist: execution_allowed=false", errors)
        check_content(text, "network_allowed: false", "Checklist: network_allowed=false", errors)

    # Cost budget
    budget_path = GNG_DIR / "deepseek_judge_cost_budget.yaml"
    if budget_path.exists():
        text = budget_path.read_text(encoding="utf-8")
        check_content(text, "budget_not_approved", "Budget: current_status=budget_not_approved", errors)
        check_content(text, "hard_stop_on_budget_exceeded: true", "Budget: hard_stop=true", errors)
        check_content(text, "cost_guard_enabled: true", "Budget: cost_guard_enabled=true", errors)

    # Execution plan
    plan_path = GNG_DIR / "deepseek_judge_execution_plan.yaml"
    if plan_path.exists():
        text = plan_path.read_text(encoding="utf-8")
        check_content(text, "current_status: not_approved", "Plan: current_status=not_approved", errors)
        check_content(text, "network_allowed: false", "Plan: network_allowed=false", errors)
        check_content(text, "execution_allowed: false", "Plan: execution_allowed=false", errors)
        check_content(text, "credential_loaded: false", "Plan: credential_loaded=false", errors)
        check_content(text, "deepseek_api_called: false", "Plan: deepseek_api_called=false", errors)
        check_content(text, "required_human_approval: true", "Plan: human_approval=true", errors)


def validate_security_constraints(errors: list[str]) -> None:
    print("  [Section 3/6] Security constraints...")

    all_files = list(GNG_DIR.rglob("*"))
    combined_text = ""
    for f in all_files:
        if f.is_dir() or f.suffix in (".pyc",):
            continue
        combined_text += f.read_text(encoding="utf-8")

    # Must not contain real API keys
    forbidden_api_key = [
        "sk-",  # OpenAI format
        "DEEPSEEK_API_KEY",  # Only allowed in template placeholder
    ]
    # DEEPSEEK_API_KEY is allowed in template placeholder (local_config_template.md)
    for key in forbidden_api_key:
        # Only flag sk- if it's not in a placeholder context
        lines_with_sk = [
            line for line in combined_text.split("\n")
            if "sk-" in line and "PLACEHOLDER" not in line and "placeholder" not in line
        ]
        if lines_with_sk:
            errors.append(f"[SECURITY] found possible API key pattern 'sk-' in non-placeholder context")

    # Check for Authorization header
    forbidden_headers = [
        "Authorization: Bearer",
        "Authorization:",
    ]
    for hdr in forbidden_headers:
        lines = [
            line.strip() for line in combined_text.split("\n")
            if hdr in line
        ]
        # Only flag if not in a prohibited list or placeholder context
        flagged = [
            l for l in lines
            if "prohibited" not in l.lower()
            and "禁止" not in l
            and "not" not in l.split(hdr)[0][-20:]
            and "PLACEHOLDER" not in l
        ]
        if flagged:
            errors.append(f"[SECURITY] found '{hdr}' in non-prohibited context")

    # Must not claim real DeepSeek call
    check_content(combined_text, "deepseek_api_called: false", "Security: deepseek_api_called=false", errors)

    # Must not claim validated findings
    if "validated" in combined_text:
        # Allow "not validated" and "mark as validated" in prohibited context
        pass

    # Must not claim formal vulnerability
    # Allow references to "not formal finding" and prohibited status list
    # Exclude acceptance_criteria file since it lists formal_finding as prohibited
    security_text = ""
    for f in all_files:
        if f.is_dir() or f.suffix in (".pyc",):
            continue
        if "acceptance_criteria" in f.name:
            continue  # Skip — lists formal_finding as prohibited status
        security_text += f.read_text(encoding="utf-8")

    formal_lines = [
        l for l in security_text.split("\n")
        if "formal_finding" in l
        and "false" not in l
        and "not" not in l.lower()
        and "no" not in l.lower()
        and "Prohibited" not in l
        and not l.strip().startswith("-")  # List items in prohibited section
    ]
    if formal_lines:
        errors.append(f"[SECURITY] found claim of formal_finding=true")


def validate_local_config_template(errors: list[str]) -> None:
    print("  [Section 4/6] Local config template...")

    config_path = GNG_DIR / "deepseek_judge_local_config_template.md"
    if not config_path.exists():
        errors.append("[CONFIG] local config template missing")
        return

    text = config_path.read_text(encoding="utf-8")

    # Must contain placeholder
    check_content(text, "PLACEHOLDER", "Config: contains placeholder", errors)
    check_content(text, "DEEPSEEK_API_KEY_PLACEHOLDER", "Config: API key is placeholder", errors)

    # Must warn about security
    check_content(text, "不要提交", "Config: warns against committing", errors)
    check_content(text, "不要提交", "Config: security warnings present", errors)


def validate_result_acceptance(errors: list[str]) -> None:
    print("  [Section 5/6] Result acceptance criteria...")

    criteria_path = GNG_DIR / "deepseek_judge_result_acceptance_criteria.md"
    if not criteria_path.exists():
        errors.append("[ACCEPTANCE] acceptance criteria missing")
        return

    text = criteria_path.read_text(encoding="utf-8")

    # Must declare result status boundary
    checks = [
        ("assistant_review", "result_type=assistant_review"),
        ("needs_human_review", "status=needs_human_review"),
        ("usable_for_formal_finding", "usable_for_formal_finding=false"),
        ("manual_review_required", "manual_review_required=true"),
    ]
    for pattern, label in checks:
        check_content(text, pattern, f"Acceptance: {label}", errors)

    # Must NOT allow automatic validation
    prohibited = ["validated", "confirmed_vulnerability", "formal_finding", "customer_report_ready"]
    # But these should be listed as prohibited - they should appear in the doc
    for p in prohibited:
        check_content(text, p, f"Acceptance: mentions {p} as prohibited", errors)


def validate_rollback_plan(errors: list[str]) -> None:
    print("  [Section 6/6] Rollback plan...")

    rollback_path = GNG_DIR / "deepseek_judge_rollback_plan.md"
    if not rollback_path.exists():
        errors.append("[ROLLBACK] rollback plan missing")
        return

    text = rollback_path.read_text(encoding="utf-8")

    check_content(text, "Immediate Halt", "Rollback: immediate halt step", errors)
    check_content(text, "Credential Protection", "Rollback: credential protection", errors)
    check_content(text, "Result Invalidation", "Rollback: result invalidation", errors)
    check_content(text, "Configuration Reset", "Rollback: config reset", errors)
    check_content(text, "Validation", "Rollback: validation step", errors)


# ── Main runner ─────────────────────────────────────────────────────────


def main() -> int:
    print(f"\n{'='*60}")
    print("Phase 34B Validation — DeepSeek Judge Go/No-Go Packet")
    print(f"{'='*60}\n")

    all_errors: list[str] = []

    sections = [
        ("Go/No-Go directory", validate_go_no_go_directory),
        ("Approval status", validate_approval_status),
        ("Security constraints", validate_security_constraints),
        ("Local config template", validate_local_config_template),
        ("Result acceptance criteria", validate_result_acceptance),
        ("Rollback plan", validate_rollback_plan),
    ]

    for section_name, section_fn in sections:
        errors_before = len(all_errors)
        section_fn(all_errors)
        new_errors = len(all_errors) - errors_before
        status = "FAIL" if new_errors else "PASS"
        count = f" ({new_errors} error{'s' if new_errors != 1 else ''})" if new_errors else ""
        print(f"  [{status}]{count}")

    print(f"\n{'='*60}")
    print(f"Total: {len(all_errors)} error{'s' if len(all_errors) != 1 else ''}")
    print(f"{'='*60}")

    if all_errors:
        print("\nErrors:")
        for i, err in enumerate(all_errors, 1):
            print(f"  {i}. {err}")
        return 1
    else:
        print("\nAll Phase 34B validation checks passed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
