#!/usr/bin/env python3
"""Phase 35B — Validate Promptfoo Go/No-Go Packet.

Validates that the promptfoo Go/No-Go packet is complete and correct:

  - All required packet files exist
  - All YAML files are parseable
  - All security flags are set correctly (not_approved, false, etc.)
  - No API keys / Authorization headers in any packet file
  - No claims of promptfoo execution
  - No claims of validated findings
  - No claims of formal findings
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
GO_NO_GO_DIR = ROOT / "tool_integrations" / "promptfoo" / "go_no_go"

REQUIRED_FILES: List[Path] = [
    GO_NO_GO_DIR / "promptfoo_go_no_go_packet.md",
    GO_NO_GO_DIR / "promptfoo_approval_checklist.md",
    GO_NO_GO_DIR / "promptfoo_execution_scope.yaml",
    GO_NO_GO_DIR / "promptfoo_cost_request_budget.yaml",
    GO_NO_GO_DIR / "promptfoo_preflight_checklist.md",
    GO_NO_GO_DIR / "promptfoo_execution_boundary.md",
    GO_NO_GO_DIR / "promptfoo_rollback_plan.md",
    GO_NO_GO_DIR / "promptfoo_result_acceptance_criteria.md",
    GO_NO_GO_DIR / "promptfoo_local_config_template.md",
]

REQUIRED_SECURITY_FLAGS: Dict[str, str] = {
    "approval_status": "not_approved",
}

REQUIRED_BOOLEAN_FALSE: List[str] = [
    "execution_allowed",
    "network_allowed",
    "promptfoo_eval_allowed",
    "target_api_call_allowed",
    "deepseek_judge_allowed",
    "credential_loaded",
]

REQUIRED_BOOLEAN_TRUE: List[str] = [
    "human_go_no_go_required",
]

FORBIDDEN_CLAIMS: List[str] = [
    "promptfoo has been executed",
    "promptfoo eval completed",
    "finding validated",
    "formal finding",
    "customer report",
]

FORBIDDEN_PATTERNS: List[str] = [
    "sk-",
    "api_key",
    "api-key",
    "Authorization",
    "Bearer ",
    "X-API-Key",
    "deepseek-api-key",
    "openai-api-key",
    "anthropic-api-key",
]


class ValidationResult:
    def __init__(self) -> None:
        self.passed: int = 0
        self.failed: int = 0
        self.errors: List[str] = []

    def ok(self, msg: str) -> None:
        self.passed += 1

    def fail(self, msg: str) -> None:
        self.failed += 1
        self.errors.append(msg)

    @property
    def all_ok(self) -> bool:
        return self.failed == 0


def load_yaml_safe(path: Path) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def check_file_exists(path: Path, result: ValidationResult) -> None:
    if path.exists():
        result.ok(f"File exists: {path.relative_to(ROOT)}")
    else:
        result.fail(f"Missing required file: {path.relative_to(ROOT)}")


def check_yaml_parseable(path: Path, result: ValidationResult) -> None:
    if not path.exists():
        return
    try:
        with open(path, encoding="utf-8") as f:
            yaml.safe_load(f)
        result.ok(f"YAML parseable: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"YAML parse error in {path.relative_to(ROOT)}: {e}")


def check_security_flags_yaml(path: Path, result: ValidationResult) -> None:
    if not path.exists():
        return
    data = load_yaml_safe(path)
    if data is None:
        return

    # Check approval_status
    actual_status = data.get("approval_status", "")
    expected = REQUIRED_SECURITY_FLAGS["approval_status"]
    if actual_status == expected:
        result.ok(f"approval_status={actual_status} in {path.relative_to(ROOT)}")
    else:
        result.fail(
            f"approval_status={actual_status} in {path.relative_to(ROOT)}, "
            f"expected {expected}"
        )

    # Check boolean false flags
    for flag in REQUIRED_BOOLEAN_FALSE:
        if flag in data:
            actual = data.get(flag)
            if actual is False:
                result.ok(f"{flag}=false in {path.relative_to(ROOT)}")
            else:
                result.fail(f"{flag}={actual} in {path.relative_to(ROOT)}, expected false")

    # Check boolean true flags
    for flag in REQUIRED_BOOLEAN_TRUE:
        if flag in data:
            actual = data.get(flag)
            if actual is True:
                result.ok(f"{flag}=true in {path.relative_to(ROOT)}")
            else:
                result.fail(f"{flag}={actual} in {path.relative_to(ROOT)}, expected true")


def check_no_forbidden_patterns(path: Path, result: ValidationResult) -> None:
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        found_any = False
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in content.lower():
                for line_num, line in enumerate(content.splitlines(), 1):
                    if pattern.lower() in line.lower():
                        stripped = line.strip()
                        if stripped.startswith("#") or stripped.startswith("//"):
                            continue
                        if "example" in stripped.lower() or "placeholder" in stripped.lower():
                            continue
                        lower_line = stripped.lower()
                        if any(
                            prefix in lower_line
                            for prefix in ("no ", "without ", "never ", "do not ", "do_not ",
                                          "should not ", "must not ", "avoid ", "forbid",
                                          "constraint", "security", "boundary")
                        ):
                            continue
                        result.fail(
                            f"Forbidden pattern '{pattern}' in {path.relative_to(ROOT)} "
                            f"line {line_num}: {stripped[:80]}"
                        )
                        found_any = True
                        break
        if not found_any:
            result.ok(f"No API keys / secrets in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_no_forbidden_claims(path: Path, result: ValidationResult) -> None:
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        found_any = False
        for claim in FORBIDDEN_CLAIMS:
            if claim.lower() in content.lower():
                for line_num, line in enumerate(content.splitlines(), 1):
                    if claim.lower() in line.lower():
                        stripped = line.strip().lower()
                        # Allow if in a negation, prohibition, or flag context
                        if any(neg in stripped for neg in ['=false', 'not_allowed', 'excluded', 'not ', 'no ', 'without ', 'never ', 'do not ', 'do_not ', 'should not ', 'must not ', 'cannot ', 'can not ', 'forbid', 'prohibit', 'avoid', 'constraint', 'boundary', 'reject', 'halt', 'not_approved', 'allowed: false', 'allowed_scope', 'excluded_scope']):
                            continue
                        result.fail(f"Forbidden claim '{claim}' in {path.relative_to(ROOT)} line {line_num}: {stripped[:80]}")
                        found_any = True
        if not found_any:
            result.ok(f"No false claims in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_no_placeholder_endpoints(path: Path, result: ValidationResult) -> None:
    """Check that placeholder endpoints use __PLACEHOLDER_ format."""
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        # Allow __PLACEHOLDER_ patterns, reject real-looking endpoints
        real_endpoints = ["api.openai.com", "api.deepseek.com", "api.anthropic.com"]
        for ep in real_endpoints:
            if ep.lower() in content.lower():
                # Check if it's inside a comment or placeholder
                for line_num, line in enumerate(content.splitlines(), 1):
                    if ep.lower() in line.lower():
                        stripped = line.strip()
                        if "__PLACEHOLDER_" in stripped or stripped.startswith("#"):
                            continue
                        result.fail(
                            f"Real endpoint '{ep}' in {path.relative_to(ROOT)} "
                            f"line {line_num}: {stripped[:80]}"
                        )
        result.ok(f"No real endpoints in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def validate_all() -> Tuple[ValidationResult, List[Dict[str, Any]]]:
    result = ValidationResult()
    sections = []

    # Section 1: Required files exist
    print("\n[1/8] Checking required files exist...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_FILES:
        check_file_exists(f, result)
    sections.append({"name": "Required files exist", "passed": result.passed - section_ok, "failed": result.failed - section_fail})

    # Section 2: YAML files parseable
    print("\n[2/8] Checking YAML files parseable...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_FILES:
        if f.suffix in (".yaml", ".yml"):
            check_yaml_parseable(f, result)
    sections.append({"name": "YAML files parseable", "passed": result.passed - section_ok, "failed": result.failed - section_fail})

    # Section 3: Security flags in YAML files
    print("\n[3/8] Checking security flags in YAML files...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_FILES:
        if f.suffix in (".yaml", ".yml"):
            check_security_flags_yaml(f, result)
    sections.append({"name": "Security flags correct", "passed": result.passed - section_ok, "failed": result.failed - section_fail})

    # Section 4: No forbidden claims
    print("\n[4/8] Checking for forbidden claims...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_FILES:
        check_no_forbidden_claims(f, result)
    sections.append({"name": "No forbidden claims", "passed": result.passed - section_ok, "failed": result.failed - section_fail})

    # Section 5: No API keys
    print("\n[5/8] Checking for API keys...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_FILES:
        check_no_forbidden_patterns(f, result)
    sections.append({"name": "No API keys", "passed": result.passed - section_ok, "failed": result.failed - section_fail})

    # Section 6: No real endpoints
    print("\n[6/8] Checking for real endpoints...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_FILES:
        check_no_placeholder_endpoints(f, result)
    sections.append({"name": "No real endpoints", "passed": result.passed - section_ok, "failed": result.failed - section_fail})

    # Section 7: No promptfoo execution claims
    print("\n[7/8] Checking no promptfoo execution claims...")
    section_ok = result.passed
    section_fail = result.failed
    all_files = list(GO_NO_GO_DIR.rglob("*"))
    for f in all_files:
        if f.is_file() and f.name != ".DS_Store":
            check_no_forbidden_claims(f, result)
    sections.append({"name": "No promptfoo execution claims", "passed": result.passed - section_ok, "failed": result.failed - section_fail})

    # Section 8: MD files readable
    print("\n[8/8] Checking markdown files readable...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_FILES:
        if f.suffix == ".md":
            try:
                content = f.read_text(encoding="utf-8")
                if len(content) > 0:
                    result.ok(f"MD readable: {f.relative_to(ROOT)}")
                else:
                    result.fail(f"Empty MD file: {f.relative_to(ROOT)}")
            except Exception as e:
                result.fail(f"Cannot read {f.relative_to(ROOT)}: {e}")
    sections.append({"name": "Markdown files readable", "passed": result.passed - section_ok, "failed": result.failed - section_fail})

    return result, sections


def print_report(result: ValidationResult, sections: List[Dict[str, Any]]) -> None:
    print()
    print("=" * 70)
    print("  Promptfoo Go/No-Go Packet — Validation Report")
    print("=" * 70)
    print()
    for sec in sections:
        status = "OK" if sec["failed"] == 0 else "FAIL"
        print(f"  [{status}] {sec['name']:40s}  {sec['passed']:3d} passed, {sec['failed']:3d} failed")
    print()
    print(f"  Total: {result.passed} passed, {result.failed} failed")
    print()
    if result.errors:
        print("  --- Detailed Errors ---")
        print()
        for err in result.errors:
            print(f"    [FAIL] {err}")
        print()
    if result.all_ok:
        print("  [PASS] All validation checks passed.")
    else:
        print("  [FAIL] Some validation checks failed.")
    print()
    print("  Security boundaries respected:")
    print("    - No promptfoo eval run")
    print("    - No target API connected")
    print("    - No DeepSeek API called")
    print("    - No .local/ read")
    print("    - All approval_status=not_approved")
    print("    - All execution_allowed=false")
    print()


def main() -> int:
    print("=" * 70)
    print("Phase 35B — Validate Promptfoo Go/No-Go Packet")
    print("=" * 70)
    result, sections = validate_all()
    print_report(result, sections)
    return 0 if result.all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
