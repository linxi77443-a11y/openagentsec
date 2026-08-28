#!/usr/bin/env python3
"""
M01 / M02 Minimal Capability — Static Validation Script
Phase 35F: Minimal Capability Framework

Validates that all M01 and M02 implementation files conform to the capability framework:
  - No formal finding fields
  - No API keys or Authorization headers
  - No unredacted endpoints
  - No .local/ paths
  - No false claims of confirmed vulnerability / formal finding / production impact
  - Schema field completeness
  - Security boundary compliance

Usage:
    python3 scripts/validate_m01_m02_minimal_capabilities.py
"""

import os
import sys
import yaml

M01_DIR = "capability_modules/implementations/M01_prompt_injection_bypass"
M02_DIR = "capability_modules/implementations/M02_system_prompt_leakage"

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

# ── Helpers ──────────────────────────────────────────────────────

def get_required_files(module_dir):
    return [
        f"{module_dir}/module_input_schema.yaml",
        f"{module_dir}/sample_module_input.yaml",
        f"{module_dir}/review_output_schema.yaml",
        f"{module_dir}/sample_capability_review.md",
    ]


def check_file_exists(filepath):
    if not os.path.isfile(filepath):
        return f"MISSING: {filepath}"
    return None


def load_yaml(filepath):
    try:
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def check_forbidden_patterns(filepath):
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

    forbidden_md = ["confirmed_exploit", "validated_finding", "formal_vulnerability"]
    for pattern in forbidden_md:
        if pattern.lower() in content.lower():
            errors.append(f"{filepath}: contains forbidden pattern '{pattern}'")

    required_sections = ["不构成 formal finding", "usable_for_formal_finding", "capability_gap"]
    for section in required_sections:
        if section not in content:
            errors.append(f"{filepath}: missing required section/statement '{section}'")

    return errors


# ── Schema checks ────────────────────────────────────────────────

def check_formal_finding_allowed_false(filepath):
    """Check formal_finding_allowed is set to false in YAML."""
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    if "formal_finding_allowed" in data:
        if data["formal_finding_allowed"] is not False:
            errors.append(f"{filepath}: formal_finding_allowed must be false, got {data['formal_finding_allowed']}")
    if "required_fields" in data:
        for field in data["required_fields"]:
            if field.get("name") == "formal_finding_allowed":
                if field.get("must_be") is not False:
                    errors.append(f"{filepath}: field formal_finding_allowed must_be must be false")
            if field.get("name") == "human_review_required":
                if field.get("must_be") is not True:
                    errors.append(f"{filepath}: field human_review_required must_be must be true")
    return errors


def check_result_semantics(filepath):
    """Check result_semantics enum is restricted."""
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    allowed = {"assistant_review_only", "needs_human_review", "capability_review"}
    if "result_semantics" in data:
        if data["result_semantics"] not in allowed:
            errors.append(f"{filepath}: result_semantics '{data['result_semantics']}' not in allowed set")
    if "required_fields" in data:
        for field in data["required_fields"]:
            if field.get("name") == "result_semantics":
                for v in field.get("enum", []):
                    if v not in allowed:
                        errors.append(f"{filepath}: result_semantics enum contains '{v}' not in allowed set")
    return errors


def check_review_status_enum(filepath):
    """Check review_status enum in output schema."""
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    if "output_fields" not in data:
        return [f"{filepath}: missing 'output_fields'"]
    for field in data["output_fields"]:
        if field.get("name") == "review_status":
            allowed = {"assistant_review", "needs_human_review", "inconclusive", "capability_gap"}
            vals = set(field.get("enum", []))
            for v in vals:
                if v not in allowed:
                    errors.append(f"{filepath}: review_status enum contains '{v}' not in allowed set")
            for a in allowed:
                if a not in vals:
                    errors.append(f"{filepath}: review_status enum missing '{a}'")
        if field.get("name") == "human_review_required":
            if field.get("must_be") is not True:
                errors.append(f"{filepath}: human_review_required must_be must be true")
        if field.get("name") == "formal_finding_allowed":
            if field.get("must_be") is not False:
                errors.append(f"{filepath}: formal_finding_allowed must_be must be false")
    return errors


def check_mapping_fields(filepath):
    """Check output schema has mapping_to_M21/M22/M25."""
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    if "output_fields" not in data:
        return [f"{filepath}: missing 'output_fields'"]
    field_names = {f.get("name") for f in data["output_fields"] if isinstance(f, dict)}
    required = {"mapping_to_M21", "mapping_to_M22", "mapping_to_M25"}
    for r in required:
        if r not in field_names:
            errors.append(f"{filepath}: missing mapping field '{r}'")
    return errors


# ── Module-specific checks ───────────────────────────────────────

def check_m01_specific(filepath):
    """M01-specific sample input checks."""
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    if data.get("candidate_id") != "FC-32C-gtc_chatbot-mb-001":
        errors.append(f"{filepath}: candidate_id should be FC-32C-gtc_chatbot-mb-001")
    if "prompt_injection_variant" not in data:
        errors.append(f"{filepath}: missing prompt_injection_variant")
    if "bypass_language" not in data:
        errors.append(f"{filepath}: missing bypass_language")
    return errors


def check_m01_output_schema(filepath):
    """M01 output schema specific checks."""
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    if "output_fields" not in data:
        return [f"{filepath}: missing 'output_fields'"]
    field_names = {f.get("name") for f in data["output_fields"] if isinstance(f, dict)}
    required = {"prompt_injection_bypass_observed", "multilingual_bypass_likelihood"}
    for r in required:
        if r not in field_names:
            errors.append(f"{filepath}: missing M01-specific field '{r}'")
    return errors


def check_m02_specific(filepath):
    """M02-specific sample input checks."""
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    if data.get("candidate_id") != "FC-32C-gtc_chatbot-spe-001":
        errors.append(f"{filepath}: candidate_id should be FC-32C-gtc_chatbot-spe-001")
    if "leakage_target" not in data:
        errors.append(f"{filepath}: missing leakage_target")
    if "leakage_method" not in data:
        errors.append(f"{filepath}: missing leakage_method")
    return errors


def check_m02_output_schema(filepath):
    """M02 output schema specific checks."""
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    if "output_fields" not in data:
        return [f"{filepath}: missing 'output_fields'"]
    field_names = {f.get("name") for f in data["output_fields"] if isinstance(f, dict)}
    required = {"system_prompt_leakage_observed", "encoding_based_leakage_likelihood"}
    for r in required:
        if r not in field_names:
            errors.append(f"{filepath}: missing M02-specific field '{r}'")
    return errors


# ── Main ─────────────────────────────────────────────────────────

def run_checks():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    print(f"M01 / M02 Minimal Capability — Static Validation")
    print(f"{'=' * 55}")
    print(f"Working directory: {base_dir}")
    print()

    all_errors = []
    stats = {"checks": 0, "files": 0}

    for label, module_dir in [("M01", M01_DIR), ("M02", M02_DIR)]:
        print(f"── [{label}] ──")
        req_files = get_required_files(module_dir)

        # 1. File existence
        for f in req_files:
            stats["files"] += 1
            err = check_file_exists(f)
            if err:
                all_errors.append(err)

        # 2. Forbidden patterns in data files (not self)
        for f in req_files:
            if not os.path.isfile(f):
                continue
            stats["checks"] += 1
            all_errors.extend(check_forbidden_patterns(f))

        # 3. formal_finding_allowed
        for f in [f"{module_dir}/module_input_schema.yaml", f"{module_dir}/sample_module_input.yaml"]:
            if not os.path.isfile(f):
                continue
            stats["checks"] += 1
            all_errors.extend(check_formal_finding_allowed_false(f))

        # 4. result_semantics
        for f in [f"{module_dir}/module_input_schema.yaml", f"{module_dir}/sample_module_input.yaml"]:
            if not os.path.isfile(f):
                continue
            stats["checks"] += 1
            all_errors.extend(check_result_semantics(f))

        # 5. review_status enum
        f = f"{module_dir}/review_output_schema.yaml"
        if os.path.isfile(f):
            stats["checks"] += 1
            all_errors.extend(check_review_status_enum(f))

        # 6. Mapping fields
        f = f"{module_dir}/review_output_schema.yaml"
        if os.path.isfile(f):
            stats["checks"] += 1
            all_errors.extend(check_mapping_fields(f))

        # 7. Markdown content
        f = f"{module_dir}/sample_capability_review.md"
        if os.path.isfile(f):
            stats["checks"] += 1
            all_errors.extend(check_markdown_no_forbidden(f))

        # Module-specific checks
        if label == "M01":
            f = f"{module_dir}/sample_module_input.yaml"
            if os.path.isfile(f):
                stats["checks"] += 1
                all_errors.extend(check_m01_specific(f))
            f = f"{module_dir}/review_output_schema.yaml"
            if os.path.isfile(f):
                stats["checks"] += 1
                all_errors.extend(check_m01_output_schema(f))
        elif label == "M02":
            f = f"{module_dir}/sample_module_input.yaml"
            if os.path.isfile(f):
                stats["checks"] += 1
                all_errors.extend(check_m02_specific(f))
            f = f"{module_dir}/review_output_schema.yaml"
            if os.path.isfile(f):
                stats["checks"] += 1
                all_errors.extend(check_m02_output_schema(f))

        print()

    # ── Summary ──
    print(f"{'=' * 55}")
    if all_errors:
        print(f"VALIDATION FAILED — {len(all_errors)} issue(s) found:")
        print()
        for err in all_errors:
            print(f"  ✗ {err}")
        print()
        return False
    else:
        print(f"VALIDATION PASSED — {stats['checks']} checks on {stats['files']} files, 0 issues.")
        print()
        return True


if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
