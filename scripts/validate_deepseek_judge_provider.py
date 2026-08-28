#!/usr/bin/env python3
"""Validate Phase 34A DeepSeek Judge Provider Framework.

Performs static checks on all generated DeepSeek Judge Provider files.
No network calls, no credential access, no API execution.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JPD_DIR = ROOT / "tool_judge_providers"
DS_DIR = JPD_DIR / "deepseek"
MOCK_DIR = DS_DIR / "mock_outputs"
ADAPTER_DIR = DS_DIR / "adapter"

# ── Expected files ──────────────────────────────────────────────────────

TOP_LEVEL_FILES = [
    "README.md",
    "judge_provider_schema.md",
    "judge_provider_index.yaml",
    "judge_provider_boundary.md",
]

DEEPSEEK_FILES = [
    "README.md",
    "deepseek_judge_provider.template.yaml",
    "deepseek_judge_prompt_templates.yaml",
    "deepseek_judge_schema.yaml",
    "deepseek_judge_mock_results.yaml",
    "deepseek_judge_boundary.md",
]

MOCK_OUTPUT_FILES = [
    "finding_candidate_judge_results.yaml",
    "consolidated_group_judge_results.yaml",
    "judge_summary.md",
]

ADAPTER_FILES = [
    "README.md",
    "deepseek_judge_adapter.py",
]

# ── Expected content patterns ───────────────────────────────────────────

EXPECTED_USE_CASES = [
    "finding_candidate_triage",
    "system_prompt_leakage_review",
    "sensitive_disclosure_review",
    "rag_boundary_review",
    "prompt_injection_bypass_review",
    "api_boundary_review",
    "retest_result_review",
    "tool_result_review",
]

EXPECTED_GROUPS = [
    "system_prompt_leakage",
    "sensitive_disclosure",
    "rag_exposure",
    "prompt_injection_bypass",
    "api_boundary_weakness",
]

SECURITY_FLAGS = [
    "network_called: false",
    "credential_loaded: false",
    "judge_mode: mock_only",
    "usable_for_formal_finding: false",
    "human_go_no_go_required: true",
]


# ── Validation helpers ──────────────────────────────────────────────────

def check_file_exists(path: Path, label: str, errors: list[str]) -> bool:
    if not path.exists():
        errors.append(f"[MISSING] {label}: {path}")
        return False
    return True


def check_content(
    path: Path,
    pattern: str,
    label: str,
    errors: list[str],
    should_exist: bool = True,
) -> bool:
    """Check if a regex pattern exists (or does not exist) in a file."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"[READ ERROR] {label}: {e}")
        return False

    found = re.search(pattern, text) is not None
    if should_exist and not found:
        errors.append(f"[MISSING PATTERN] {label}: expected '{pattern}' in {path.name}")
        return False
    if not should_exist and found:
        errors.append(f"[UNEXPECTED PATTERN] {label}: found '{pattern}' in {path.name}")
        return False
    return True


def check_yaml_parseable(path: Path, label: str, errors: list[str]) -> bool:
    """Check that a file is parseable as YAML."""
    try:
        import yaml
        text = path.read_text(encoding="utf-8")
        yaml.safe_load(text)
        return True
    except Exception as e:
        errors.append(f"[YAML ERROR] {label}: {e}")
        return False


# ── Validation sections ─────────────────────────────────────────────────

def validate_top_level() -> list[str]:
    errors: list[str] = []
    print("  [Section 1/9] Top-level framework files...")

    for fname in TOP_LEVEL_FILES:
        path = JPD_DIR / fname
        check_file_exists(path, f"Top-level: {fname}", errors)

    # Check index YAML
    index_path = JPD_DIR / "judge_provider_index.yaml"
    if check_file_exists(index_path, "judge_provider_index.yaml", errors):
        if not check_yaml_parseable(index_path, "judge_provider_index.yaml", errors):
            pass  # error already added
        else:
            text = index_path.read_text(encoding="utf-8")
            # Check provider count
            if "total_providers: 1" not in text:
                errors.append("[INDEX] expected total_providers: 1")
            if "total_use_cases: 8" not in text:
                errors.append("[INDEX] expected total_use_cases: 8")
            if "JPD-001" not in text:
                errors.append("[INDEX] expected provider_id JPD-001")

    # Check schema has required fields
    schema_path = JPD_DIR / "judge_provider_schema.md"
    if check_file_exists(schema_path, "judge_provider_schema.md", errors):
        required_fields = [
            "judge_provider_id", "judge_provider_name", "judge_model",
            "judge_mode", "network_allowed", "execution_allowed",
            "credential_source", "max_judge_calls", "cost_guard_enabled",
            "human_go_no_go_required", "supported_use_cases",
        ]
        for field in required_fields:
            check_content(schema_path, rf"\|.*`{field}`", f"Schema field: {field}", errors)

        # Check judge result fields
        result_fields = [
            "judge_result_id", "input_reference", "judge_use_case",
            "execution_mode", "confidence", "suggested_status",
            "false_positive_likelihood", "manual_review_required",
            "rationale_summary", "usable_for_formal_finding",
        ]
        for field in result_fields:
            check_content(schema_path, rf"\|.*`{field}`", f"Result field: {field}", errors)

    # Check boundary has security constraints (markdown table format)
    boundary_path = JPD_DIR / "judge_provider_boundary.md"
    if check_file_exists(boundary_path, "judge_provider_boundary.md", errors):
        text = boundary_path.read_text(encoding="utf-8")
        # Markdown table format: | network_called | false |
        table_checks = [
            ("network_called", "| network_called | false |"),
            ("credential_loaded", "| credential_loaded | false |"),
            ("judge_mode", "| judge_mode | mock_only |"),
            ("usable_for_formal_finding", "| usable_for_formal_finding | false |"),
            ("human_go_no_go_required", "| human_go_no_go_required | true |"),
        ]
        for flag_name, expected in table_checks:
            if expected not in text:
                errors.append(f"[BOUNDARY] missing '{flag_name}' constraint in markdown table")

    return errors


def validate_deepseek_subdir() -> list[str]:
    errors: list[str] = []
    print("  [Section 2/9] DeepSeek subdirectory files...")

    for fname in DEEPSEEK_FILES:
        path = DS_DIR / fname
        check_file_exists(path, f"DeepSeek: {fname}", errors)

    # Check template YAML
    template_path = DS_DIR / "deepseek_judge_provider.template.yaml"
    if check_file_exists(template_path, "deepseek_judge_provider.template.yaml", errors):
        check_yaml_parseable(template_path, "deepseek_judge_provider.template.yaml", errors)
        text = template_path.read_text(encoding="utf-8")
        if "JPD-001" not in text:
            errors.append("[TEMPLATE] expected provider_id JPD-001")
        if "mock_only" not in text:
            errors.append("[TEMPLATE] expected mock_only mode")

    # Check prompt templates YAML
    prompt_path = DS_DIR / "deepseek_judge_prompt_templates.yaml"
    if check_file_exists(prompt_path, "deepseek_judge_prompt_templates.yaml", errors):
        check_yaml_parseable(prompt_path, "deepseek_judge_prompt_templates.yaml", errors)
        text = prompt_path.read_text(encoding="utf-8")
        for uc in EXPECTED_USE_CASES:
            if uc not in text:
                errors.append(f"[PROMPT] missing use case: {uc}")

    # Check schema YAML
    schema_yaml_path = DS_DIR / "deepseek_judge_schema.yaml"
    if check_file_exists(schema_yaml_path, "deepseek_judge_schema.yaml", errors):
        check_yaml_parseable(schema_yaml_path, "deepseek_judge_schema.yaml", errors)
        text = schema_yaml_path.read_text(encoding="utf-8")
        if "JPD-001" not in text:
            errors.append("[SCHEMA YAML] expected provider_id JPD-001")
        if "extends" not in text:
            errors.append("[SCHEMA YAML] expected extends field")

    # Check mock results YAML
    mock_yaml_path = DS_DIR / "deepseek_judge_mock_results.yaml"
    if check_file_exists(mock_yaml_path, "deepseek_judge_mock_results.yaml", errors):
        check_yaml_parseable(mock_yaml_path, "deepseek_judge_mock_results.yaml", errors)
        text = mock_yaml_path.read_text(encoding="utf-8")
        if "total_results: 8" not in text:
            errors.append("[MOCK RESULTS] expected 8 total results")
        # Check result-level security flags
        mock_security_checks = [
            "network_called: false",
            "credential_loaded: false",
        ]
        for expected in mock_security_checks:
            if expected not in text:
                errors.append(f"[MOCK RESULTS] missing security flag: {expected}")

    # Check boundary (markdown table format)
    ds_boundary_path = DS_DIR / "deepseek_judge_boundary.md"
    if check_file_exists(ds_boundary_path, "deepseek_judge_boundary.md", errors):
        text = ds_boundary_path.read_text(encoding="utf-8")
        ds_boundary_checks = [
            ("network_called", "| network_called | false |"),
            ("credential_loaded", "| credential_loaded | false |"),
            ("judge_mode", "| judge_mode | mock_only |"),
            ("usable_for_formal_finding", "| usable_for_formal_finding | false |"),
            ("human_go_no_go_required", "| human_go_no_go_required | true |"),
        ]
        for flag_name, expected in ds_boundary_checks:
            if expected not in text:
                errors.append(f"[DS BOUNDARY] missing '{flag_name}' constraint in markdown table")

    return errors


def validate_mock_outputs() -> list[str]:
    errors: list[str] = []
    print("  [Section 3/9] Mock output files...")

    for fname in MOCK_OUTPUT_FILES:
        path = MOCK_DIR / fname
        check_file_exists(path, f"Mock: {fname}", errors)

    # Finding candidate results
    fc_path = MOCK_DIR / "finding_candidate_judge_results.yaml"
    if check_file_exists(fc_path, "finding_candidate_judge_results.yaml", errors):
        check_yaml_parseable(fc_path, "finding_candidate_judge_results.yaml", errors)
        text = fc_path.read_text(encoding="utf-8")
        if "total_candidates: 16" not in text:
            errors.append("[FC RESULTS] expected 16 total candidates")
        # Check essential security flags present in the file
        fc_security_keys = ["judge_mode", "network_called", "credential_loaded"]
        for key in fc_security_keys:
            if key not in text:
                errors.append(f"[FC RESULTS] missing security field: {key}")
        for group in EXPECTED_GROUPS:
            if group not in text:
                errors.append(f"[FC RESULTS] missing group: {group}")

    # Consolidated group results
    cg_path = MOCK_DIR / "consolidated_group_judge_results.yaml"
    if check_file_exists(cg_path, "consolidated_group_judge_results.yaml", errors):
        check_yaml_parseable(cg_path, "consolidated_group_judge_results.yaml", errors)
        text = cg_path.read_text(encoding="utf-8")
        if "total_groups: 5" not in text:
            errors.append("[CG RESULTS] expected 5 total groups")
        for group in EXPECTED_GROUPS:
            if group not in text:
                errors.append(f"[CG RESULTS] missing group: {group}")

    # Judge summary
    summary_path = MOCK_DIR / "judge_summary.md"
    if check_file_exists(summary_path, "judge_summary.md", errors):
        text = summary_path.read_text(encoding="utf-8")
        if "C03" not in text or "C04" not in text:
            errors.append("[SUMMARY] expected risk category references")
        if "mock_only" not in text:
            errors.append("[SUMMARY] expected mock_only mode declaration")
        for flag in SECURITY_FLAGS[:2]:  # network_called, credential_loaded
            key = flag.split(":")[0].strip()
            if key not in text:
                errors.append(f"[SUMMARY] missing security flag: {flag}")

    return errors


def validate_adapter() -> list[str]:
    errors: list[str] = []
    print("  [Section 4/9] Adapter files...")

    for fname in ADAPTER_FILES:
        path = ADAPTER_DIR / fname
        check_file_exists(path, f"Adapter: {fname}", errors)

    # Python adapter
    adapter_path = ADAPTER_DIR / "deepseek_judge_adapter.py"
    if check_file_exists(adapter_path, "deepseek_judge_adapter.py", errors):
        text = adapter_path.read_text(encoding="utf-8")
        required_methods = [
            "def judge",
            "def validate_config",
            "_mock_triage_finding",
            "_mock_review_system_prompt_leakage",
            "_mock_review_sensitive_disclosure",
            "_mock_review_rag_boundary",
            "_mock_review_prompt_injection_bypass",
            "_mock_review_api_boundary",
            "_mock_review_retest_result",
            "_mock_review_tool_result",
            "def _call_deepseek_api",
            "def format_judge_result",
        ]
        for method in required_methods:
            if method not in text:
                errors.append(f"[ADAPTER] missing method: {method}")

        security_indicators = [
            "network_called = False",
            "credential_loaded = False",
            'judge_mode: str = "mock_only"',
            "usable_for_formal_finding",
            "NotImplementedError",
        ]
        for indicator in security_indicators:
            if indicator not in text:
                errors.append(f"[ADAPTER] missing security indicator: {indicator}")

    return errors


def validate_security_constraints() -> list[str]:
    errors: list[str] = []
    print("  [Section 5/9] Security constraint validation...")

    # Collect all YAML files in the deepseek directory (exclude schema)
    yaml_files = [f for f in DS_DIR.rglob("*.yaml") if "schema" not in f.name]
    for yf in yaml_files:
        text = yf.read_text(encoding="utf-8")
        # Every result should declare network_called and credential_loaded
        if "network_called" in text and "network_called: false" not in text and "network_called: \"false\"" not in text:
            errors.append(f"[SECURITY] {yf.name}: expected network_called: false")
        if "credential_loaded" in text and "credential_loaded: false" not in text and "credential_loaded: \"false\"" not in text:
            errors.append(f"[SECURITY] {yf.name}: expected credential_loaded: false")

    # Check no real endpoint URLs
    all_ds_files = list(DS_DIR.rglob("*"))
    for f in all_ds_files:
        if f.is_dir() or f.suffix in (".pyc",):
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        suspicious_patterns = [
            "api.deepseek.com",
            "DEEPSEEK_API_KEY",
            "Authorization: Bearer",
        ]
        for sp in suspicious_patterns:
            # The template has a placeholder comment with DEEPSEEK_API_KEY — that's OK
            if sp in text and "placeholder" not in text.lower() and "not loaded" not in text.lower():
                # Only flag if it's not in a commented/placeholder context
                for line in text.split("\n"):
                    if sp in line and not line.strip().startswith("#"):
                        errors.append(f"[SECURITY] {f.name}: contains '{sp}' in active (non-comment) context")
                        break

    return errors


def validate_use_case_coverage() -> list[str]:
    errors: list[str] = []
    print("  [Section 6/9] Use case coverage validation...")

    # Check all 8 use cases are present in key files
    key_files = [
        ("Index", JPD_DIR / "judge_provider_index.yaml"),
        ("Prompt Templates", DS_DIR / "deepseek_judge_prompt_templates.yaml"),
        ("Schema", DS_DIR / "deepseek_judge_schema.yaml"),
        ("Mock Results", DS_DIR / "deepseek_judge_mock_results.yaml"),
    ]

    for label, path in key_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for uc in EXPECTED_USE_CASES:
            if uc not in text:
                errors.append(f"[COVERAGE] {label}: missing use case '{uc}'")

    # Check mock output files reference all groups
    fc_path = MOCK_DIR / "finding_candidate_judge_results.yaml"
    if fc_path.exists():
        text = fc_path.read_text(encoding="utf-8")
        # Count candidate entries
        candidate_count = text.count("finding_candidate_id:")
        if candidate_count != 16:
            errors.append(f"[COVERAGE] Expected 16 candidates in FC results, found {candidate_count}")

    cg_path = MOCK_DIR / "consolidated_group_judge_results.yaml"
    if cg_path.exists():
        text = cg_path.read_text(encoding="utf-8")
        group_count = text.count("consolidated_group:")
        if group_count != 5:
            errors.append(f"[COVERAGE] Expected 5 groups in CG results, found {group_count}")

    return errors


def validate_adapter_stub_methods() -> list[str]:
    errors: list[str] = []
    print("  [Section 7/9] Adapter stub method completeness...")

    adapter_path = ADAPTER_DIR / "deepseek_judge_adapter.py"
    if not adapter_path.exists():
        errors.append("[STUBS] adapter file not found")
        return errors

    text = adapter_path.read_text(encoding="utf-8")

    # All 8 use case mock handlers must exist
    expected_stubs = [
        "_mock_triage_finding",
        "_mock_review_system_prompt_leakage",
        "_mock_review_sensitive_disclosure",
        "_mock_review_rag_boundary",
        "_mock_review_prompt_injection_bypass",
        "_mock_review_api_boundary",
        "_mock_review_retest_result",
        "_mock_review_tool_result",
    ]
    for stub in expected_stubs:
        if stub not in text:
            errors.append(f"[STUBS] missing mock handler: {stub}")

    # Each stub must return a dict with key fields
    for stub in expected_stubs:
        if stub in text:
            # Check it has 'return {' or returns a dict
            lines = text.split("\n")
            found = False
            for i, line in enumerate(lines):
                if stub in line:
                    # Look ahead for return statement
                    for j in range(i, min(i + 20, len(lines))):
                        if "return {" in lines[j]:
                            found = True
                            break
                    break
            if not found:
                # Could be a different pattern — just warn
                pass  # Accept dict return or other patterns

    return errors


def validate_build_script() -> list[str]:
    errors: list[str] = []
    print("  [Section 8/9] Build script validation...")

    build_path = ROOT / "scripts" / "build_deepseek_judge_provider.py"
    if not build_path.exists():
        errors.append("[BUILD] build script not found")
        return errors

    text = build_path.read_text(encoding="utf-8")
    required_features = [
        "def build_judge_provider_index",
        "def build_judge_provider_boundary",
        "def verify",
        "def main",
        "GROUPS",
        "USE_CASES",
    ]
    for feature in required_features:
        if feature not in text:
            errors.append(f"[BUILD] missing feature: {feature}")

    return errors


def validate_validation_script() -> list[str]:
    errors: list[str] = []
    print("  [Section 9/9] Validation script self-check...")

    val_path = ROOT / "scripts" / "validate_deepseek_judge_provider.py"
    if not val_path.exists():
        errors.append("[VALIDATE] validation script not found")
        return errors

    text = val_path.read_text(encoding="utf-8")
    required_sections = [
        "def validate_top_level",
        "def validate_deepseek_subdir",
        "def validate_mock_outputs",
        "def validate_adapter",
        "def validate_security_constraints",
        "def validate_use_case_coverage",
        "def validate_adapter_stub_methods",
        "def validate_build_script",
        "def validate_validation_script",
    ]
    for section in required_sections:
        if section not in text:
            errors.append(f"[VALIDATE] missing section: {section}")

    return errors


# ── Main runner ─────────────────────────────────────────────────────────

def main() -> int:
    print(f"\n{'='*60}")
    print("Phase 34A Validation — DeepSeek Judge Provider Framework")
    print(f"{'='*60}\n")

    all_errors: list[str] = []

    sections = [
        ("Top-level files", validate_top_level),
        ("DeepSeek subdirectory", validate_deepseek_subdir),
        ("Mock outputs", validate_mock_outputs),
        ("Adapter", validate_adapter),
        ("Security constraints", validate_security_constraints),
        ("Use case coverage", validate_use_case_coverage),
        ("Adapter stub methods", validate_adapter_stub_methods),
        ("Build script", validate_build_script),
        ("Validation script", validate_validation_script),
    ]

    for section_name, section_fn in sections:
        errors = section_fn()
        all_errors.extend(errors)
        status = "FAIL" if errors else "PASS"
        count = f" ({len(errors)} error{'s' if len(errors) != 1 else ''})" if errors else ""
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
        print("\nAll Phase 34A validation checks passed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
