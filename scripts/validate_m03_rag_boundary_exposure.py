#!/usr/bin/env python3
"""
M03 RAG Boundary Exposure — Static Validation Script
Phase 35E: Minimal Capability Framework

Validates that all M03 implementation files conform to the capability framework:
  - No formal finding fields
  - No API keys or Authorization headers
  - No unredacted endpoints
  - No .local/ paths
  - No false claims of confirmed vulnerability
  - Schema field completeness
  - Security boundary compliance

Usage:
    python3 scripts/validate_m03_rag_boundary_exposure.py
"""

import os
import sys
import yaml

MODULE_DIR = "capability_modules/implementations/M03_rag_boundary_exposure"
SCRIPTS_DIR = "scripts"

# ── Files to check ───────────────────────────────────────────────

REQUIRED_FILES = [
    f"{MODULE_DIR}/module_input_schema.yaml",
    f"{MODULE_DIR}/sample_module_input.yaml",
    f"{MODULE_DIR}/review_output_schema.yaml",
    f"{MODULE_DIR}/sample_capability_review.md",
]

GENERATED_OUTPUT = "capability_modules/results/M03/review_output.yaml"

# ── Forbidden patterns ───────────────────────────────────────────

FORBIDDEN_PATTERNS = [
    # No formal finding escalation
    "formal_vulnerability",
    "confirmed_exploit",
    "validated_finding",
    "usable_for_formal_finding: true",
    # No API credentials
    "api_key",
    "api-key",
    "API_KEY",
    "Authorization:",
    "authorization:",
    # No unredacted endpoints
    "https://api.",
    "https://sandbox.",
    "https://target.",
    # No .local/ paths
    ".local/",
    # No false claims
    "production_impact_confirmed",
    "promptfoo_eval_run",
    "eval_executed",
]

# ── Checks ───────────────────────────────────────────────────────

def check_file_exists(filepath):
    """Check that a required file exists."""
    if not os.path.isfile(filepath):
        return f"MISSING: {filepath}"
    return None


def check_yaml_safe(filepath):
    """Safely load YAML, returning None on failure."""
    try:
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        return None


def check_no_forbidden_patterns(filepath):
    """Check file does not contain forbidden patterns."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except Exception:
        return [f"UNREADABLE: {filepath}"]

    errors = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in content.lower():
            errors.append(f"FORBIDDEN PATTERN '{pattern}' found in {filepath}")
    return errors


def check_formal_finding_allowed_false(filepath):
    """Check formal_finding_allowed is set to false."""
    data = check_yaml_safe(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]

    errors = []
    # Check top-level
    if "formal_finding_allowed" in data:
        if data["formal_finding_allowed"] is not False:
            errors.append(f"{filepath}: formal_finding_allowed must be false, got {data['formal_finding_allowed']}")

    # Check in required_fields list
    if "required_fields" in data:
        for field in data["required_fields"]:
            if field.get("name") == "formal_finding_allowed":
                if field.get("must_be") is not False:
                    errors.append(f"{filepath}: field formal_finding_allowed must_be must be false")
            if field.get("name") == "human_review_required":
                if field.get("must_be") is not True:
                    errors.append(f"{filepath}: field human_review_required must_be must be true")

    return errors


def check_output_fields(filepath):
    """Check review_output_schema.yaml output_fields."""
    data = check_yaml_safe(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]

    errors = []
    if "output_fields" not in data:
        return [f"{filepath}: missing 'output_fields' key"]

    field_names = [f.get("name") for f in data["output_fields"] if isinstance(f, dict)]

    # Check required fields exist
    required = [
        "review_status", "human_review_required", "formal_finding_allowed",
        "raw_kb_content_exposed", "risk_signals",
        "mapping_to_M19", "mapping_to_M21", "mapping_to_M22",
        "capability_gaps", "recommendation",
    ]
    for r in required:
        if r not in field_names:
            errors.append(f"{filepath}: missing required output field '{r}'")

    # Check review_status enum is restricted
    for field in data["output_fields"]:
        if field.get("name") == "review_status":
            enum_vals = field.get("enum", [])
            allowed = {"assistant_review", "needs_human_review", "inconclusive", "capability_gap"}
            for v in enum_vals:
                if v not in allowed:
                    errors.append(f"{filepath}: review_status enum contains disallowed value '{v}'")
            for a in allowed:
                if a not in enum_vals:
                    errors.append(f"{filepath}: review_status enum missing allowed value '{a}'")

        if field.get("name") == "human_review_required":
            if field.get("must_be") is not True:
                errors.append(f"{filepath}: human_review_required must_be must be true")

        if field.get("name") == "formal_finding_allowed":
            if field.get("must_be") is not False:
                errors.append(f"{filepath}: formal_finding_allowed must_be must be false")

    return errors


def check_result_semantics(filepath):
    """Check result_semantics enum is restricted to allowed values."""
    data = check_yaml_safe(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]

    errors = []
    allowed_semantics = {"assistant_review_only", "needs_human_review", "capability_review"}

    # Check top-level
    if "result_semantics" in data:
        if data["result_semantics"] not in allowed_semantics:
            errors.append(f"{filepath}: result_semantics '{data['result_semantics']}' not in allowed set")

    # Check in required_fields
    if "required_fields" in data:
        for field in data["required_fields"]:
            if field.get("name") == "result_semantics":
                enum_vals = field.get("enum", [])
                for v in enum_vals:
                    if v not in allowed_semantics:
                        errors.append(f"{filepath}: result_semantics enum contains disallowed value '{v}'")

    return errors


def check_module_input_schema(filepath):
    """Check module_input_schema.yaml required fields."""
    data = check_yaml_safe(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]

    errors = []
    if "required_fields" not in data:
        return [f"{filepath}: missing 'required_fields' key"]

    field_names = [f.get("name") for f in data["required_fields"] if isinstance(f, dict)]

    required_fields = [
        "module_id", "module_name", "module_name_zh",
        "candidate_id", "candidate_title", "risk_category",
        "profile", "source_phase", "source_evidence_reference",
        "observed_output_summary",
        "possible_raw_kb_exposure", "possible_source_chunk_exposure",
        "possible_sensitive_business_data",
        "retrieval_trace_available", "promptfoo_config_reference",
        "authorized_api_required", "deepseek_judge_required",
        "human_review_required", "formal_finding_allowed", "result_semantics",
    ]
    for r in required_fields:
        if r not in field_names:
            errors.append(f"{filepath}: missing required field '{r}'")

    return errors


def check_markdown_no_forbidden(filepath):
    """Check sample capability review markdown for forbidden content."""
    errors = []
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except Exception:
        return [f"UNREADABLE: {filepath}"]

    if "formal_finding_allowed" in content and "false" not in content:
        errors.append(f"{filepath}: formal_finding_allowed should be false")

    forbidden_md = [
        "confirmed_exploit",
        "validated_finding",
        "formal_vulnerability",
    ]
    for pattern in forbidden_md:
        if pattern.lower() in content.lower():
            errors.append(f"{filepath}: contains forbidden pattern '{pattern}'")

    required_sections = [
        "不构成 formal finding",
        "usable_for_formal_finding",
        "capability_gap",
    ]
    for section in required_sections:
        if section not in content:
            errors.append(f"{filepath}: missing required section/statement '{section}'")

    return errors


def check_generated_review_calibration(filepath):
    """Check generated review_output.yaml has calibration fields."""
    data = check_yaml_safe(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []

    required_calibration = [
        "validation_mode",
        "evidence_strength",
        "confidence_scope",
        "retest_executed",
        "api_connected",
        "promptfoo_eval_executed",
        "raw_kb_content_exposure_indicated",
        "source_chunk_exposure_indicated",
        "exposure_confirmation_level",
        "control_gaps",
        "assessment_limitations",
    ]
    for field in required_calibration:
        if field not in data:
            errors.append(f"{filepath}: missing calibration field '{field}'")

    # Check calibration field values
    if data.get("validation_mode") != "offline_static_derivation":
        errors.append(f"{filepath}: validation_mode should be 'offline_static_derivation'")
    if data.get("evidence_strength") != "candidate_description_only":
        errors.append(f"{filepath}: evidence_strength should be 'candidate_description_only'")
    if data.get("retest_executed") is not False:
        errors.append(f"{filepath}: retest_executed must be false")
    if data.get("api_connected") is not False:
        errors.append(f"{filepath}: api_connected must be false")
    if data.get("promptfoo_eval_executed") is not False:
        errors.append(f"{filepath}: promptfoo_eval_executed must be false")
    if data.get("exposure_confirmation_level") != "candidate_indicated_only":
        errors.append(f"{filepath}: exposure_confirmation_level should be 'candidate_indicated_only'")
    if data.get("formal_finding_allowed") is not False:
        errors.append(f"{filepath}: formal_finding_allowed must be false")

    # Check mapping calibration
    m19 = data.get("mapping_to_M19", "")
    if m19 != "deferred_until_business_data_confirmed":
        errors.append(f"{filepath}: mapping_to_M19 should be 'deferred_until_business_data_confirmed', got '{m19}'")
    m21 = data.get("mapping_to_M21", "")
    if m21 not in ("partial_available", "not_available"):
        errors.append(f"{filepath}: mapping_to_M21 should be 'partial_available' or 'not_available', got '{m21}'")
    m22 = data.get("mapping_to_M22", "")
    if m22 != "deferred_until_human_review":
        errors.append(f"{filepath}: mapping_to_M22 should be 'deferred_until_human_review', got '{m22}'")

    return errors


# ── Main ─────────────────────────────────────────────────────────

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    print(f"M03 RAG Boundary Exposure — Static Validation")
    print(f"{'=' * 50}")
    print(f"Working directory: {base_dir}")
    print()

    all_errors = []
    all_checks = 0

    # 1. File existence
    print("[1/7] Checking required files exist...")
    for f in REQUIRED_FILES:
        all_checks += 1
        err = check_file_exists(f)
        if err:
            all_errors.append(err)
    print(f"  → {len(REQUIRED_FILES)} files checked, {len([e for e in all_errors if 'MISSING' in e])} missing")
    print()

    # 2. Forbidden patterns in all files (excluding this script itself)
    print("[2/7] Checking forbidden patterns...")
    all_files = list(REQUIRED_FILES)  # Don't scan the validator itself
    for f in all_files:
        if not os.path.isfile(f):
            continue
        all_checks += 1
        errors = check_no_forbidden_patterns(f)
        all_errors.extend(errors)
    print(f"  → {len(all_files)} files scanned, {len(errors)} pattern violations")
    print()

    # 3. formal_finding_allowed
    print("[3/7] Checking formal_finding_allowed constraints...")
    for f in [f"{MODULE_DIR}/module_input_schema.yaml", f"{MODULE_DIR}/sample_module_input.yaml"]:
        all_checks += 1
        errors = check_formal_finding_allowed_false(f)
        all_errors.extend(errors)
    print(f"  → {len([e for e in all_errors if 'formal_finding_allowed' in e])} violations found")
    print()

    # 4. review_output_schema structure
    print("[4/7] Checking review_output_schema.yaml...")
    all_checks += 1
    errors = check_output_fields(f"{MODULE_DIR}/review_output_schema.yaml")
    all_errors.extend(errors)
    print(f"  → {len(errors)} schema violations")
    print()

    # 5. result_semantics
    print("[5/7] Checking result_semantics constraints...")
    for f in [f"{MODULE_DIR}/module_input_schema.yaml", f"{MODULE_DIR}/sample_module_input.yaml"]:
        all_checks += 1
        errors = check_result_semantics(f)
        all_errors.extend(errors)
    print(f"  → {len([e for e in all_errors if 'result_semantics' in e])} violations found")
    print()

    # 6. module_input_schema field completeness
    print("[6/7] Checking module_input_schema field completeness...")
    all_checks += 1
    errors = check_module_input_schema(f"{MODULE_DIR}/module_input_schema.yaml")
    all_errors.extend(errors)
    print(f"  → {len(errors)} field violations")
    print()

    # 7. sample_capability_review.md content
    print("[7/7] Checking sample_capability_review.md...")
    all_checks += 1
    errors = check_markdown_no_forbidden(f"{MODULE_DIR}/sample_capability_review.md")
    all_errors.extend(errors)
    print(f"  → {len(errors)} content violations")
    print()

    # 8. Generated review_output.yaml calibration fields
    print("[8/8] Checking generated review_output.yaml calibration...")
    if os.path.isfile(GENERATED_OUTPUT):
        all_checks += 1
        errors = check_generated_review_calibration(GENERATED_OUTPUT)
        all_errors.extend(errors)
    print(f"  → {len(errors)} calibration violations")
    print()

    # ── Summary ──
    print(f"{'=' * 50}")
    if all_errors:
        print(f"VALIDATION FAILED — {len(all_errors)} issue(s) found:")
        print()
        for err in all_errors:
            print(f"  ✗ {err}")
        print()
        sys.exit(1)
    else:
        print(f"VALIDATION PASSED — {all_checks} checks passed, 0 issues.")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
