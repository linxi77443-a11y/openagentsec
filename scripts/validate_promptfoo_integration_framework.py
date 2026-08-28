#!/usr/bin/env python3
"""Phase 35 — Validate Promptfoo Integration Framework.

Validates that the promptfoo integration framework is complete and correct:

  - All required integration files exist
  - All YAML files are parseable
  - All mock results have execution_mode=mock or dry_run
  - All mock results have real_target_connected=false
  - All mock results have usable_for_formal_finding=false
  - No API keys / Authorization headers in any integration file
  - Config index references exist for all expected profiles
  - Result schema has all required fields
  - Evidence mapping has bidirectional references
  - Finding candidate mapping has required fields
  - DeepSeek judge handoff schema has required fields
  - Adapter file exists and has dry_run_execute method

Security constraints:
  - No running promptfoo eval
  - No connecting target API
  - No calling DeepSeek API
  - No reading .local/
  - No modifying original drafts
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_DIR = ROOT / "tool_integrations" / "promptfoo"
ADAPTER_DIR = INTEGRATION_DIR / "adapter"

# ---------------------------------------------------------------------------
# Expected files (from README.md "Phase 35 Deliverables" table)
# ---------------------------------------------------------------------------

REQUIRED_FILES: List[Path] = [
    INTEGRATION_DIR / "README.md",
    INTEGRATION_DIR / "promptfoo_integration_boundary.md",
    INTEGRATION_DIR / "promptfoo_config_index.yaml",
    INTEGRATION_DIR / "promptfoo_result_schema.yaml",
    INTEGRATION_DIR / "promptfoo_mock_results.yaml",
    INTEGRATION_DIR / "promptfoo_evidence_mapping.yaml",
    INTEGRATION_DIR / "promptfoo_finding_candidate_mapping.yaml",
    INTEGRATION_DIR / "promptfoo_deepseek_judge_handoff.yaml",
    INTEGRATION_DIR / "adapter" / "README.md",
]

# Additional expected adapter files (beyond README)
EXPECTED_ADAPTER_FILES: List[Path] = [
    ADAPTER_DIR / "promptfoo_adapter.py",
]

EXPECTED_CONFIG_INDEX_PROFILES: List[str] = [
    # Generated testcase profiles
    "chatbot",
    "agent",
    "rag",
    "api",
    "regression",
    # Regression suite profiles
    "chatbot_regression",
    "agent_regression",
    "rag_regression",
    "api_regression",
    "owasp_agentic_regression",
    "owasp_llm_regression",
    "core_llm_regression",
]

REQUIRED_RESULT_SCHEMA_FIELDS: List[str] = [
    "execution_mode",
    "real_target_connected",
    "usable_for_formal_finding",
    "promptfoo_version",
    "evaluated_at",
    "profile",
    "target",
    "test_results",
]

REQUIRED_TEST_RESULT_FIELDS: List[str] = [
    "test_id",
    "prompt",
    "response",
    "assert_results",
    "passed",
    "metadata",
]

REQUIRED_EVIDENCE_MAPPING_FIELDS: List[str] = [
    "evidence_mapping",
]

REQUIRED_FINDING_CANDIDATE_FIELDS: List[str] = [
    "finding_candidate_mapping",
]

REQUIRED_JUDGE_HANDOFF_FIELDS: List[str] = [
    "judge_handoff",
]

# Patterns that should NOT appear in any integration file
FORBIDDEN_PATTERNS: List[str] = [
    "sk-",  # OpenAI-style API key
    "api_key",
    "api-key",
    "Authorization",
    "Bearer ",
    "X-API-Key",
    "deepseek-api-key",
    "openai-api-key",
    "anthropic-api-key",
]

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


class ValidationResult:
    """Collects validation results."""

    def __init__(self) -> None:
        self.passed: int = 0
        self.failed: int = 0
        self.errors: List[str] = []

    def ok(self, msg: str) -> None:
        self.passed += 1

    def fail(self, msg: str) -> None:
        self.failed += 1
        self.errors.append(msg)

    def summary(self) -> str:
        return f"  Passed: {self.passed}  |  Failed: {self.failed}"

    @property
    def all_ok(self) -> bool:
        return self.failed == 0


def load_yaml_safe(path: Path) -> Optional[dict]:
    """Load a YAML file, returning None on failure."""
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        return None


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------


def check_file_exists(path: Path, result: ValidationResult) -> None:
    """Check that a required file exists."""
    if path.exists():
        result.ok(f"File exists: {path.relative_to(ROOT)}")
    else:
        result.fail(f"Missing required file: {path.relative_to(ROOT)}")


def check_yaml_parseable(path: Path, result: ValidationResult) -> None:
    """Check that a YAML file is parseable."""
    if not path.exists():
        return  # already reported by file existence check
    try:
        with open(path, encoding="utf-8") as f:
            yaml.safe_load(f)
        result.ok(f"YAML parseable: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"YAML parse error in {path.relative_to(ROOT)}: {e}")


def check_no_forbidden_patterns(path: Path, result: ValidationResult) -> None:
    """Check that a file contains no API keys or Authorization headers."""
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
                        # Skip comments
                        if stripped.startswith("#") or stripped.startswith("//"):
                            continue
                        # Skip "example" or "placeholder" mentions
                        if "example" in stripped.lower() or "placeholder" in stripped.lower():
                            continue
                        # Skip prose mentions of constraints (e.g. "No API keys, no Authorization headers")
                        lower_line = stripped.lower()
                        if any(
                            prefix in lower_line
                            for prefix in (
                                "no ",
                                "without ",
                                "never ",
                                "do not ",
                                "don't ",
                                "should not ",
                                "must not ",
                                "avoid ",
                                "forbid",
                                "constraint",
                                "security",
                                "boundary",
                            )
                        ):
                            continue
                        # Skip lines that are clearly documentation prose (not code values)
                        # e.g., bullet points, sentence fragments, table content
                        if any(
                            marker in lower_line
                            for marker in (
                                "api keys",
                                "authorization headers",
                                "real endpoints",
                                "real api keys",
                                "secrets",
                            )
                        ):
                            continue
                        result.fail(
                            f"Forbidden pattern '{pattern}' found in "
                            f"{path.relative_to(ROOT)} line {line_num}: "
                            f"{stripped[:80]}"
                        )
                        found_any = True
                        break

        if not found_any:
            result.ok(f"No API keys / secrets in: {path.relative_to(ROOT)}")
    except Exception as e:
        result.fail(f"Cannot read {path.relative_to(ROOT)}: {e}")


def check_mock_results_security(path: Path, result: ValidationResult) -> None:
    """Check that mock results have correct security flags."""
    if not path.exists():
        return
    data = load_yaml_safe(path)
    if data is None:
        result.fail(f"Cannot parse mock results: {path.relative_to(ROOT)}")
        return

    execution_mode = data.get("execution_mode", "")
    if execution_mode in ("mock", "dry_run"):
        result.ok(f"execution_mode={execution_mode} in {path.relative_to(ROOT)}")
    else:
        result.fail(
            f"execution_mode={execution_mode} in {path.relative_to(ROOT)}, "
            f"expected 'mock' or 'dry_run'"
        )

    real_target = data.get("real_target_connected", None)
    if real_target is False:
        result.ok(f"real_target_connected=false in {path.relative_to(ROOT)}")
    else:
        result.fail(
            f"real_target_connected={real_target} in {path.relative_to(ROOT)}, "
            f"expected false"
        )

    usable = data.get("usable_for_formal_finding", None)
    if usable is False:
        result.ok(f"usable_for_formal_finding=false in {path.relative_to(ROOT)}")
    else:
        result.fail(
            f"usable_for_formal_finding={usable} in {path.relative_to(ROOT)}, "
            f"expected false"
        )


def check_config_index_profiles(path: Path, result: ValidationResult) -> None:
    """Check that config index references all expected profiles."""
    if not path.exists():
        return
    data = load_yaml_safe(path)
    if data is None:
        result.fail(f"Cannot parse config index: {path.relative_to(ROOT)}")
        return

    discovered_profiles = set()
    for section in ("generated_testcase_profiles", "regression_suite_profiles"):
        entries = data.get(section, [])
        if entries is None:
            continue
        for entry in entries:
            profile = entry.get("profile", "")
            if profile:
                discovered_profiles.add(profile)

    for expected in EXPECTED_CONFIG_INDEX_PROFILES:
        if expected in discovered_profiles:
            result.ok(f"Config index has profile: {expected}")
        else:
            result.fail(f"Config index missing expected profile: {expected}")


def check_result_schema(path: Path, result: ValidationResult) -> None:
    """Check that result schema has all required fields."""
    if not path.exists():
        return
    data = load_yaml_safe(path)
    if data is None:
        result.fail(f"Cannot parse result schema: {path.relative_to(ROOT)}")
        return

    for field in REQUIRED_RESULT_SCHEMA_FIELDS:
        if field in data:
            result.ok(f"Result schema has field: {field}")
        else:
            result.fail(f"Result schema missing required field: {field}")

    # Check nested test_results fields if test_results exists
    test_results = data.get("test_results", data.get("test_result_schema", None))
    if test_results and isinstance(test_results, dict):
        for field in REQUIRED_TEST_RESULT_FIELDS:
            if field in test_results:
                result.ok(f"Result schema test_results has field: {field}")
            else:
                result.fail(
                    f"Result schema test_results missing required field: {field}"
                )


def check_evidence_mapping(path: Path, result: ValidationResult) -> None:
    """Check that evidence mapping has required fields and bidirectional references."""
    if not path.exists():
        return
    data = load_yaml_safe(path)
    if data is None:
        result.fail(f"Cannot parse evidence mapping: {path.relative_to(ROOT)}")
        return

    for field in REQUIRED_EVIDENCE_MAPPING_FIELDS:
        if field in data:
            result.ok(f"Evidence mapping has field: {field}")
        else:
            result.fail(f"Evidence mapping missing required field: {field}")

    # Check for bidirectional references (evidence items linking back to test IDs)
    mapping = data.get("evidence_mapping", data)
    if isinstance(mapping, dict):
        has_source_ref = False
        has_target_ref = False
        for key, value in mapping.items():
            if isinstance(value, dict):
                if "source_test_id" in value or "test_id" in value:
                    has_source_ref = True
                if "evidence_id" in value or "evidence_path" in value:
                    has_target_ref = True
        if has_source_ref:
            result.ok("Evidence mapping has source test ID references")
        else:
            result.fail("Evidence mapping missing source test ID references")
        if has_target_ref:
            result.ok("Evidence mapping has evidence ID references")
        else:
            result.fail("Evidence mapping missing evidence ID references")


def check_finding_candidate_mapping(
    path: Path, result: ValidationResult
) -> None:
    """Check that finding candidate mapping has required fields."""
    if not path.exists():
        return
    data = load_yaml_safe(path)
    if data is None:
        result.fail(f"Cannot parse finding candidate mapping: {path.relative_to(ROOT)}")
        return

    for field in REQUIRED_FINDING_CANDIDATE_FIELDS:
        if field in data:
            result.ok(f"Finding candidate mapping has field: {field}")
        else:
            result.fail(
                f"Finding candidate mapping missing required field: {field}"
            )

    # Check individual finding candidate entries have required sub-fields
    mapping = data.get("finding_candidate_mapping", data)
    if isinstance(mapping, dict):
        entries = mapping.get("entries", mapping.get("candidates", []))
        if isinstance(entries, list):
            for i, entry in enumerate(entries):
                for req_field in ("candidate_id", "evidence_id", "risk_category"):
                    if req_field in entry:
                        result.ok(
                            f"Finding candidate #{i} has field: {req_field}"
                        )
                    else:
                        result.fail(
                            f"Finding candidate #{i} missing required field: "
                            f"{req_field}"
                        )


def check_judge_handoff(path: Path, result: ValidationResult) -> None:
    """Check that DeepSeek judge handoff schema has required fields."""
    if not path.exists():
        return
    data = load_yaml_safe(path)
    if data is None:
        result.fail(f"Cannot parse judge handoff: {path.relative_to(ROOT)}")
        return

    for field in REQUIRED_JUDGE_HANDOFF_FIELDS:
        if field in data:
            result.ok(f"Judge handoff has field: {field}")
        else:
            result.fail(f"Judge handoff missing required field: {field}")

    # Check nested handoff structure
    handoff = data.get("judge_handoff", data)
    if isinstance(handoff, dict):
        for req_sub in (
            "handoff_version",
            "source",
            "finding_candidates",
            "transfer_criteria",
        ):
            if req_sub in handoff:
                result.ok(f"Judge handoff has sub-field: {req_sub}")
            else:
                result.fail(f"Judge handoff missing sub-field: {req_sub}")


def check_adapter_file(path: Path, result: ValidationResult) -> None:
    """Check that adapter file exists and has dry_run_execute method."""
    if not path.exists():
        return
    try:
        content = path.read_text(encoding="utf-8")
        if "dry_run_execute" in content:
            result.ok(f"Adapter has dry_run_execute method: {path.relative_to(ROOT)}")
        else:
            result.fail(
                f"Adapter missing dry_run_execute method: {path.relative_to(ROOT)}"
            )

        # Check for NotImplementedError in real execute stubs
        if "NotImplementedError" in content:
            result.ok(
                f"Adapter has NotImplementedError guards: {path.relative_to(ROOT)}"
            )
        else:
            result.fail(
                f"Adapter missing NotImplementedError guards: "
                f"{path.relative_to(ROOT)}"
            )
    except Exception as e:
        result.fail(f"Cannot read adapter file {path.relative_to(ROOT)}: {e}")


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------


def validate_all() -> Tuple[ValidationResult, List[Dict[str, Any]]]:
    """Run all validation checks and return results + section summaries."""
    result = ValidationResult()
    sections: List[Dict[str, Any]] = []

    # --- Section 1: Required files exist ---
    print("\n[1/9] Checking required files exist...")
    section_ok = 0
    section_fail = 0
    for f in REQUIRED_FILES:
        check_file_exists(f, result)
    # Also check adapter files beyond README
    for f in EXPECTED_ADAPTER_FILES:
        check_file_exists(f, result)
    sections.append({
        "name": "Required files exist",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # --- Section 2: YAML files parseable ---
    print("\n[2/9] Checking YAML files are parseable...")
    section_ok = result.passed
    section_fail = result.failed
    yaml_files = [f for f in REQUIRED_FILES if f.suffix in (".yaml", ".yml")]
    yaml_files.extend(
        f for f in EXPECTED_ADAPTER_FILES if f.suffix in (".yaml", ".yml")
    )
    # Also find any other yaml files in the integration directory
    for f in sorted(INTEGRATION_DIR.rglob("*.yaml")):
        if f not in yaml_files:
            yaml_files.append(f)
    for f in yaml_files:
        check_yaml_parseable(f, result)
    sections.append({
        "name": "YAML files parseable",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # --- Section 3: No API keys / Authorization headers ---
    print("\n[3/9] Checking for forbidden patterns (API keys, secrets)...")
    section_ok = result.passed
    section_fail = result.failed
    all_integration_files = list(INTEGRATION_DIR.rglob("*"))
    all_integration_files = [
        f
        for f in all_integration_files
        if f.is_file() and f.name != ".DS_Store"
    ]
    for f in all_integration_files:
        check_no_forbidden_patterns(f, result)
    sections.append({
        "name": "No API keys / secrets",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # --- Section 4: Mock results security flags ---
    print("\n[4/9] Checking mock results security flags...")
    section_ok = result.passed
    section_fail = result.failed
    mock_path = INTEGRATION_DIR / "promptfoo_mock_results.yaml"
    check_mock_results_security(mock_path, result)
    sections.append({
        "name": "Mock results security flags",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # --- Section 5: Config index profiles ---
    print("\n[5/9] Checking config index profiles...")
    section_ok = result.passed
    section_fail = result.failed
    config_path = INTEGRATION_DIR / "promptfoo_config_index.yaml"
    check_config_index_profiles(config_path, result)
    sections.append({
        "name": "Config index profiles",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # --- Section 6: Result schema ---
    print("\n[6/9] Checking result schema...")
    section_ok = result.passed
    section_fail = result.failed
    schema_path = INTEGRATION_DIR / "promptfoo_result_schema.yaml"
    check_result_schema(schema_path, result)
    sections.append({
        "name": "Result schema fields",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # --- Section 7: Evidence mapping ---
    print("\n[7/9] Checking evidence mapping...")
    section_ok = result.passed
    section_fail = result.failed
    evidence_path = INTEGRATION_DIR / "promptfoo_evidence_mapping.yaml"
    check_evidence_mapping(evidence_path, result)
    sections.append({
        "name": "Evidence mapping",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # --- Section 8: Finding candidate mapping + Judge handoff ---
    print("\n[8/9] Checking finding candidate mapping & judge handoff...")
    section_ok = result.passed
    section_fail = result.failed
    finding_path = INTEGRATION_DIR / "promptfoo_finding_candidate_mapping.yaml"
    check_finding_candidate_mapping(finding_path, result)
    handoff_path = INTEGRATION_DIR / "promptfoo_deepseek_judge_handoff.yaml"
    check_judge_handoff(handoff_path, result)
    sections.append({
        "name": "Finding candidate & judge handoff",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    # --- Section 9: Adapter file ---
    print("\n[9/9] Checking adapter file...")
    section_ok = result.passed
    section_fail = result.failed
    for adapter_file in EXPECTED_ADAPTER_FILES:
        check_adapter_file(adapter_file, result)
    sections.append({
        "name": "Adapter file",
        "passed": result.passed - section_ok,
        "failed": result.failed - section_fail,
    })

    return result, sections


def print_validation_report(
    result: ValidationResult, sections: List[Dict[str, Any]]
) -> None:
    """Print a structured validation report."""
    print()
    print("=" * 70)
    print("  Promptfoo Integration Framework — Validation Report")
    print("=" * 70)
    print()

    for sec in sections:
        status = "OK" if sec["failed"] == 0 else "FAIL"
        print(
            f"  [{status}] {sec['name']:45s}  "
            f"{sec['passed']:3d} passed, {sec['failed']:3d} failed"
        )

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
        print("  [FAIL] Some validation checks failed — see errors above.")
        print(
            "  Note: Missing files may need to be created. Run "
            "scripts/build_promptfoo_integration_framework.py first."
        )

    print()
    print("  Security boundaries respected:")
    print("    - No promptfoo eval run")
    print("    - No target API connected")
    print("    - No DeepSeek API called")
    print("    - No .local/ read")
    print("    - No original drafts modified")
    print()
    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("=" * 70)
    print("Phase 35 — Validate Promptfoo Integration Framework")
    print("=" * 70)

    result, sections = validate_all()
    print_validation_report(result, sections)

    return 0 if result.all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
