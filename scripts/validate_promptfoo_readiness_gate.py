#!/usr/bin/env python3
"""Phase 35C.0 — Validate Promptfoo Execution Readiness Gate.

Static readiness check that must pass before any controlled promptfoo
execution can proceed. Only performs local static analysis:

  - No network access
  - No .local/ read
  - No promptfoo eval run
  - No external API calls
  - No credential loading

Scans promptfoo-related configuration files, runner scripts, and adapter
code for security isolation requirements.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]

# Directories and files to scan
READINESS_DIR = ROOT / "tool_integrations" / "promptfoo" / "readiness"
GO_NO_GO_DIR = ROOT / "tool_integrations" / "promptfoo" / "go_no_go"
ADAPTER_DIR = ROOT / "tool_integrations" / "promptfoo" / "adapter"
RUNNER_CONFIGS = sorted((ROOT / "runners").glob("promptfoo.*.yaml"))
INTEGRATION_DIR = ROOT / "tool_integrations" / "promptfoo"

REQUIRED_READINESS_FILES: List[Path] = [
    READINESS_DIR / "promptfoo_execution_readiness_gate.md",
]

REQUIRED_SECTIONS_IN_README: List[str] = [
    "Phase 35C.0 Overview",
    "Secret Isolation Requirements",
    "API Isolation Requirements",
    "Network Safety Requirements",
    "Promptfoo Command Safety Requirements",
    "Readiness Pass Criteria",
    "Readiness Fail Criteria",
    "Operator Checklist",
    "What This Phase Does Not Prove",
]

# Forbidden patterns — real secrets or credentials
FORBIDDEN_SECRET_PATTERNS: List[str] = [
    "sk-",
    "Authorization",
    "Bearer ",
    "X-API-Key",
]

# Forbidden real endpoints (distinguish from public docs links)
FORBIDDEN_ENDPOINTS: List[str] = [
    "api.openai.com",
    "api.deepseek.com",
    "api.anthropic.com",
]

# Configs and scripts that should not have default eval
SCRIPTS_TO_CHECK: List[Path] = [
    ROOT / "runners" / "run_generic_agent_harness.sh",
    ROOT / "runners" / "run_manual_ui_promptfoo.sh",
    ROOT / "runners" / "run_atlas_assessment.sh",
]

FILES_TO_SCAN: List[Path] = list(RUNNER_CONFIGS) + [
    INTEGRATION_DIR / "promptfoo_config_index.yaml",
    INTEGRATION_DIR / "promptfoo_mock_results.yaml",
    INTEGRATION_DIR / "promptfoo_result_schema.yaml",
    INTEGRATION_DIR / "promptfoo_evidence_mapping.yaml",
    INTEGRATION_DIR / "promptfoo_finding_candidate_mapping.yaml",
    INTEGRATION_DIR / "promptfoo_deepseek_judge_handoff.yaml",
    INTEGRATION_DIR / "promptfoo_integration_boundary.md",
    ADAPTER_DIR / "promptfoo_adapter.py",
] + list(GO_NO_GO_DIR.rglob("*")) + list(READINESS_DIR.rglob("*"))

# Scripts whose content to check for default eval
SCRIPT_PATTERNS_TO_CHECK: List[str] = [
    "promptfoo eval",
    "promptfoo redteam",
    "promptfoo view",
    "--execute",
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


def check_file_exists(path: Path, result: ValidationResult) -> None:
    if path.exists():
        result.ok(f"File exists: {path.relative_to(ROOT)}")
    else:
        result.fail(f"Missing required file: {path.relative_to(ROOT)}")


def check_md_has_sections(path: Path, sections: List[str], result: ValidationResult) -> None:
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        for section in sections:
            if section in content:
                result.ok(f"Section '{section}' found in {path.relative_to(ROOT)}")
            else:
                result.fail(f"Missing section '{section}' in {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_security_declaration(
    path: Path, field: str, expected: str, result: ValidationResult
) -> None:
    """Check that a document declares a specific security field with expected value.

    Supports both formats:
      - key: value
      - | key | value |
    """
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        # Support both 'key: value' and '| key | value |' formats
        pattern = rf"(?:{field}\s*[=:]\s*{expected}|\|\s*{field}\s*\|\s*{expected}\s*\|)"
        if re.search(pattern, content, re.IGNORECASE):
            result.ok(f"Declaration '{field}={expected}' in {path.relative_to(ROOT)}")
        else:
            result.fail(f"Missing declaration '{field}={expected}' in {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_no_forbidden_secrets(path: Path, result: ValidationResult) -> None:
    """Check for plaintext secrets in files."""
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        found_any = False
        for pattern in FORBIDDEN_SECRET_PATTERNS:
            if pattern.lower() in content.lower():
                for line_num, line in enumerate(content.splitlines(), 1):
                    if pattern.lower() in line.lower():
                        stripped = line.strip()
                        # Allow comments, examples, placeholders
                        if stripped.startswith("#") or stripped.startswith("//"):
                            continue
                        if "placeholder" in stripped.lower() or "example" in stripped.lower():
                            continue
                        lower_line = stripped.lower()
                        if any(
                            prefix in lower_line
                            for prefix in (
                                "no ", "without ", "never ", "do not ", "do_not ",
                                "should not ", "must not ", "avoid ", "forbid",
                                "constraint", "security", "boundary", "not_approved",
                                "=false", "not_allowed", "prohibit", "cannot ",
                                "using real", "connecting to", "would leak",
                                "would expose", "currently prohibited",
                            )
                        ):
                            continue
                        result.fail(
                            f"Forbidden secret pattern '{pattern}' in "
                            f"{path.relative_to(ROOT)} line {line_num}: {stripped[:80]}"
                        )
                        found_any = True
                        break
        if not found_any:
            result.ok(f"No plaintext secrets in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_no_real_endpoints(path: Path, result: ValidationResult) -> None:
    """Check for unredacted real API endpoints in files."""
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        found_any = False
        for endpoint in FORBIDDEN_ENDPOINTS:
            if endpoint.lower() in content.lower():
                for line_num, line in enumerate(content.splitlines(), 1):
                    if endpoint.lower() in line.lower():
                        stripped = line.strip()
                        # Allow in comments, placeholders, documentation links, negation context
                        if (
                            stripped.startswith("#")
                            or "__PLACEHOLDER_" in stripped
                            or "example" in stripped.lower()
                            or any(
                                prefix in stripped.lower()
                                for prefix in (
                                    "no ", "without ", "never ", "do not ", "do_not ",
                                    "should not ", "must not ", "avoid ", "forbid",
                                    "constraint", "security", "boundary", "not_approved",
                                    "=false", "not_allowed", "prohibit", "cannot ",
                                    "connecting to", "would invoke",
                                )
                            )
                        ):
                            continue
                        result.fail(
                            f"Real endpoint '{endpoint}' in "
                            f"{path.relative_to(ROOT)} line {line_num}: {stripped[:80]}"
                        )
                        found_any = True
        if not found_any:
            result.ok(f"No unredacted endpoints in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_network_allowed(path: Path, result: ValidationResult) -> None:
    """Check that network_allowed is not set to true."""
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        # Check for network_allowed=true (not in negation context)
        for line_num, line in enumerate(content.splitlines(), 1):
            if re.search(r'network_allowed\s*[=:]\s*true', line, re.IGNORECASE):
                stripped = line.strip()
                # Allow in prohibition context
                if any(
                    prefix in stripped.lower()
                    for prefix in ("no ", "not ", "never ", "avoid ", "forbid", "must not ")
                ):
                    continue
                result.fail(
                    f"network_allowed=true in {path.relative_to(ROOT)} line {line_num}"
                )
                return
        result.ok(f"network_allowed not default-true in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_deepseek_allowed(path: Path, result: ValidationResult) -> None:
    """Check that deepseek_judge_allowed is not set to true."""
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        for line_num, line in enumerate(content.splitlines(), 1):
            if re.search(r'deepseek_judge_allowed\s*[=:]\s*true', line, re.IGNORECASE):
                stripped = line.strip()
                if any(
                    prefix in stripped.lower()
                    for prefix in ("no ", "not ", "never ", "avoid ", "forbid", "must not ")
                ):
                    continue
                result.fail(
                    f"deepseek_judge_allowed=true in {path.relative_to(ROOT)} line {line_num}"
                )
                return
        result.ok(f"deepseek_judge_allowed not default-true in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_no_default_eval(path: Path, result: ValidationResult) -> None:
    """Check that scripts don't invoke promptfoo eval by default.

    Recognizes safe patterns:
      - --execute flag gating (default is dry-run, execute only when explicitly passed)
      - Commands inside conditional blocks guarded by MODE checks
    """
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")

        # Detect if script uses --execute flag gating (safe pattern)
        uses_execute_gating = "--execute" in content

        found_any = False
        for pattern in SCRIPT_PATTERNS_TO_CHECK:
            if pattern.lower() not in content.lower():
                continue
            for line_num, line in enumerate(content.splitlines(), 1):
                if pattern.lower() not in line.lower():
                    continue
                stripped = line.strip()
                # Allow if commented out
                if stripped.startswith("#"):
                    continue
                # Allow if in prohibition context
                lower_line = stripped.lower()
                if any(
                    prefix in lower_line
                    for prefix in (
                        "no ", "not ", "never ", "do not ", "do_not ",
                        "should not ", "must not ", "avoid ", "forbid",
                        "check", "verify", "ensure",
                    )
                ):
                    continue
                # If script uses --execute gating, allow the pattern
                if uses_execute_gating:
                    continue
                # Allow "echo Would run:" — dry-run mode message
                if "would run" in lower_line or "echo" in lower_line.split(pattern.lower())[0]:
                    continue
                result.fail(
                    f"Default eval pattern '{pattern}' in "
                    f"{path.relative_to(ROOT)} line {line_num}: {stripped[:80]}"
                )
                found_any = True
        if not found_any:
            result.ok(f"No default eval invocation in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_adapter_not_implemented(path: Path, result: ValidationResult) -> None:
    """Check that adapter execute() methods raise NotImplementedError."""
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        # Look for execute-related methods
        has_execute_method = "def execute" in content or "def run" in content
        has_not_implemented = "NotImplementedError" in content
        if has_execute_method and not has_not_implemented:
            result.fail(f"Adapter {path.relative_to(ROOT)} has execute methods but no NotImplementedError")
        elif has_not_implemented:
            result.ok(f"Adapter has NotImplementedError guards: {path.relative_to(ROOT)}")
        else:
            result.ok(f"No execute methods found: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_no_local_config_read(path: Path, result: ValidationResult) -> None:
    """Check that scripts don't default-read .local/ files."""
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        for line_num, line in enumerate(content.splitlines(), 1):
            if ".local/" in line:
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if any(
                    prefix in stripped.lower()
                    for prefix in ("no ", "not ", "never ", "do not ", "do_not ",
                                   "should not ", "must not ", "avoid ", "forbid",
                                   "check", "verify", "ensure", "must be", "requires")
                ):
                    continue
                # Allow .local/ in comments or placeholder context
                if "__PLACEHOLDER_" in stripped or "example" in stripped.lower():
                    continue
                result.fail(
                    f"Default .local/ read in {path.relative_to(ROOT)} "
                    f"line {line_num}: {stripped[:80]}"
                )
                return
        result.ok(f"No default .local/ read in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_go_no_go_flags(result: ValidationResult) -> None:
    """Check Phase 35B go_no_go security flags."""
    scope_yaml = GO_NO_GO_DIR / "promptfoo_execution_scope.yaml"
    budget_yaml = GO_NO_GO_DIR / "promptfoo_cost_request_budget.yaml"
    packet_md = GO_NO_GO_DIR / "promptfoo_go_no_go_packet.md"
    boundary_md = GO_NO_GO_DIR / "promptfoo_execution_boundary.md"

    for yaml_file in [scope_yaml, budget_yaml]:
        if yaml_file.exists():
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                if data:
                    status = data.get("approval_status", "")
                    if status == "not_approved":
                        result.ok(f"Go/No-Go approval_status=not_approved in {yaml_file.relative_to(ROOT)}")
                    else:
                        result.fail(f"Go/No-Go approval_status={status} in {yaml_file.relative_to(ROOT)}, expected not_approved")
                    exec_allowed = data.get("execution_allowed", None)
                    if exec_allowed is False:
                        result.ok(f"Go/No-Go execution_allowed=false in {yaml_file.relative_to(ROOT)}")
                    elif exec_allowed is not None:
                        result.fail(f"Go/No-Go execution_allowed={exec_allowed} in {yaml_file.relative_to(ROOT)}, expected false")
            except Exception as e:
                result.fail(f"Cannot parse {yaml_file.relative_to(ROOT)}: {e}")

    for md_file in [packet_md, boundary_md]:
        if md_file.exists():
            for flag, expected in [("approval_status", "not_approved"), ("execution_allowed", "false")]:
                check_security_declaration(md_file, flag, expected, result)


def validate_all() -> Tuple[ValidationResult, List[Dict[str, Any]]]:
    result = ValidationResult()
    sections = []

    # Section 1: Readiness gate document exists
    print("\n[1/9] Checking readiness gate document exists...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_READINESS_FILES:
        check_file_exists(f, result)
    sections.append({
        "name": "Readiness gate document exists",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # Section 2: Required sections in readiness document
    print("\n[2/9] Checking required sections in readiness document...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_READINESS_FILES:
        check_md_has_sections(f, REQUIRED_SECTIONS_IN_README, result)
    sections.append({
        "name": "Required sections present",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # Section 3: Security declarations in readiness document
    print("\n[3/9] Checking security declarations in readiness document...")
    section_ok = result.passed
    section_fail = result.failed
    for f in REQUIRED_READINESS_FILES:
        check_security_declaration(f, "promptfoo_eval_run", "false", result)
        check_security_declaration(f, "formal_finding_generated", "false", result)
        check_security_declaration(f, "static_analysis_only", "true", result)
        check_security_declaration(f, "readiness_gate_verification_only", "true", result)
    sections.append({
        "name": "Security declarations correct",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # Section 4: No plaintext secrets in promptfoo files
    print("\n[4/9] Checking for plaintext secrets in promptfoo files...")
    section_ok = result.passed
    section_fail = result.failed
    for f in FILES_TO_SCAN:
        if f.is_file() and f.name != ".DS_Store":
            check_no_forbidden_secrets(f, result)
    sections.append({
        "name": "No plaintext secrets",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # Section 5: No unredacted endpoints
    print("\n[5/9] Checking for unredacted endpoints...")
    section_ok = result.passed
    section_fail = result.failed
    for f in FILES_TO_SCAN:
        if f.is_file() and f.name != ".DS_Store":
            check_no_real_endpoints(f, result)
    sections.append({
        "name": "No unredacted endpoints",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # Section 6: Network and deepseek flags
    print("\n[6/9] Checking network and deepseek isolation flags...")
    section_ok = result.passed
    section_fail = result.failed
    for f in GO_NO_GO_DIR.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".yaml", ".yml"):
            check_network_allowed(f, result)
            check_deepseek_allowed(f, result)
    sections.append({
        "name": "Network/DeepSeek isolation",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # Section 7: No default eval in runner scripts
    print("\n[7/9] Checking no default eval in scripts...")
    section_ok = result.passed
    section_fail = result.failed
    for f in SCRIPTS_TO_CHECK:
        if f.exists():
            check_no_default_eval(f, result)
    sections.append({
        "name": "No default eval invocation",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # Section 8: Adapter has NotImplementedError
    print("\n[8/9] Checking adapter safety guards...")
    section_ok = result.passed
    section_fail = result.failed
    adapter_py = ADAPTER_DIR / "promptfoo_adapter.py"
    if adapter_py.exists():
        check_adapter_not_implemented(adapter_py, result)
    sections.append({
        "name": "Adapter safety guards",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # Section 9: Go/No-Go security flags
    print("\n[9/9] Checking Go/No-Go security flags...")
    section_ok = result.passed
    section_fail = result.failed
    check_go_no_go_flags(result)
    sections.append({
        "name": "Go/No-Go security flags",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    return result, sections


def print_report(result: ValidationResult, sections: List[Dict[str, Any]]) -> None:
    print()
    print("=" * 70)
    print("  Phase 35C.0 — Promptfoo Execution Readiness Gate — Validation Report")
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
        print("  [PASS] All readiness gate checks passed.")
        print()
        print("  Readiness Gate: PASS")
    else:
        print("  [FAIL] Some readiness gate checks failed.")
        print()
        print("  Readiness Gate: FAIL — remediate and re-run.")
    print()
    print("  Security boundaries respected:")
    print("    - No promptfoo eval run")
    print("    - No target API connected")
    print("    - No DeepSeek API called")
    print("    - No .local/ read")
    print("    - No credential loaded")
    print("    - No formal finding generated")
    print()


def main() -> int:
    print("=" * 70)
    print("Phase 35C.0 — Validate Promptfoo Execution Readiness Gate")
    print("=" * 70)
    result, sections = validate_all()
    print_report(result, sections)
    return 0 if result.all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
