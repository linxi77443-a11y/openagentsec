#!/usr/bin/env python3
"""
M40 Agent Action Audit & Attribution — Static Validation Script
Phase 35G: Minimal Capability Framework

Validates that all M40 implementation files conform to the capability framework:
  - No formal finding fields
  - No API keys or Authorization headers
  - No unredacted endpoints
  - No .local/ paths
  - No false claims of confirmed vulnerability / formal finding / production impact
  - Schema field completeness
  - Security boundary compliance

Usage:
    python3 scripts/validate_m40_agent_action_audit_attribution.py
"""

import os
import sys
import yaml

M40_DIR = "capability_modules/implementations/M40_agent_action_audit_attribution"

FORBIDDEN_PATTERNS = [
    "formal_vulnerability",
    "confirmed_exploit",
    "validated_finding",
    "usable_for_formal_finding: true",
    "api_key",
    "api-key",
    "API_KEY",
    "Authorization:",
    "authorization:",
    "https://api.",
    "https://sandbox.",
    "https://target.",
    ".local/",
    "production_impact_confirmed",
    "promptfoo_eval_run",
    "eval_executed",
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


def check_formal_finding_allowed_false(filepath):
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
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []
    if "output_fields" not in data:
        return [f"{filepath}: missing 'output_fields'"]
    field_names = {f.get("name") for f in data["output_fields"] if isinstance(f, dict)}
    required = {"mapping_to_M14", "mapping_to_M15", "mapping_to_M16",
                "mapping_to_M21", "mapping_to_M22", "mapping_to_M41"}
    for r in required:
        if r not in field_names:
            errors.append(f"{filepath}: missing mapping field '{r}'")
    return errors


def check_markdown_no_forbidden(filepath):
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


def check_sample_audit_log(filepath):
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []

    if data.get("module_id") != "M40":
        errors.append(f"{filepath}: module_id should be M40")
    if data.get("formal_finding_allowed") is not False:
        errors.append(f"{filepath}: formal_finding_allowed must be false")
    if data.get("human_review_required") is not True:
        errors.append(f"{filepath}: human_review_required must be true")
    if data.get("production_environment") is not False:
        errors.append(f"{filepath}: production_environment must be false (sample only)")

    required_keys = [
        "trigger_user_id", "original_user_role", "agent_id",
        "tool_name", "tool_action", "tool_arguments_summary",
        "sensitive_arguments_redacted", "approval_required", "approval_status",
        "service_account_used", "original_user_authorization_checked",
    ]
    for key in required_keys:
        if key not in data:
            errors.append(f"{filepath}: missing required field '{key}'")

    return errors


def check_audit_log_schema(filepath):
    data = load_yaml(filepath)
    if data is None:
        return [f"UNPARSEABLE YAML: {filepath}"]
    errors = []

    if "required_fields" not in data:
        return [f"{filepath}: missing 'required_fields'"]
    field_names = {f.get("name") for f in data["required_fields"] if isinstance(f, dict)}

    required_fields = [
        "module_id", "module_name", "module_name_zh",
        "audit_event_id", "timestamp", "task_id",
        "trigger_user_id", "original_user_role",
        "agent_id", "agent_session_id",
        "tool_name", "tool_action", "tool_arguments_summary",
        "sensitive_arguments_redacted", "tool_result_summary",
        "approval_required", "approval_status", "approval_actor",
        "execution_environment", "production_environment",
        "service_account_used", "original_user_authorization_checked",
        "result_semantics", "human_review_required", "formal_finding_allowed",
    ]
    for r in required_fields:
        if r not in field_names:
            errors.append(f"{filepath}: missing required field '{r}'")

    return errors


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    print(f"M40 Agent Action Audit & Attribution — Static Validation")
    print(f"{'=' * 55}")
    print(f"Working directory: {base_dir}")
    print()

    req_files = [
        f"{M40_DIR}/audit_log_schema.yaml",
        f"{M40_DIR}/sample_audit_log.yaml",
        f"{M40_DIR}/audit_review_output_schema.yaml",
        f"{M40_DIR}/sample_audit_capability_review.md",
    ]

    all_errors = []
    checks = 0

    # 1. File existence
    print("[1/8] Checking required files exist...")
    for f in req_files:
        checks += 1
        err = check_file_exists(f)
        if err:
            all_errors.append(err)
    print(f"  → {len(req_files)} files checked")
    print()

    # 2. Forbidden patterns
    print("[2/8] Checking forbidden patterns...")
    for f in req_files:
        if not os.path.isfile(f):
            continue
        checks += 1
        all_errors.extend(check_forbidden_patterns(f))
    print(f"  → {len(req_files)} files scanned")
    print()

    # 3. formal_finding_allowed in schema + sample
    print("[3/8] Checking formal_finding_allowed constraints...")
    for f in [f"{M40_DIR}/audit_log_schema.yaml", f"{M40_DIR}/sample_audit_log.yaml"]:
        if not os.path.isfile(f):
            continue
        checks += 1
        all_errors.extend(check_formal_finding_allowed_false(f))
    print()

    # 4. result_semantics
    print("[4/8] Checking result_semantics constraints...")
    for f in [f"{M40_DIR}/audit_log_schema.yaml", f"{M40_DIR}/sample_audit_log.yaml"]:
        if not os.path.isfile(f):
            continue
        checks += 1
        all_errors.extend(check_result_semantics(f))
    print()

    # 5. review_status enum
    print("[5/8] Checking review_status enum...")
    f = f"{M40_DIR}/audit_review_output_schema.yaml"
    if os.path.isfile(f):
        checks += 1
        all_errors.extend(check_review_status_enum(f))
    print()

    # 6. Mapping fields
    print("[6/8] Checking mapping fields...")
    f = f"{M40_DIR}/audit_review_output_schema.yaml"
    if os.path.isfile(f):
        checks += 1
        all_errors.extend(check_mapping_fields(f))
    print()

    # 7. Markdown content
    print("[7/8] Checking sample_audit_capability_review.md...")
    f = f"{M40_DIR}/sample_audit_capability_review.md"
    if os.path.isfile(f):
        checks += 1
        all_errors.extend(check_markdown_no_forbidden(f))
    print()

    # 8. Module-specific checks
    print("[8/8] Running M40-specific checks...")
    for f_schema in [f"{M40_DIR}/audit_log_schema.yaml"]:
        if os.path.isfile(f_schema):
            checks += 1
            all_errors.extend(check_audit_log_schema(f_schema))
    for f_sample in [f"{M40_DIR}/sample_audit_log.yaml"]:
        if os.path.isfile(f_sample):
            checks += 1
            all_errors.extend(check_sample_audit_log(f_sample))
    print()

    # Summary
    print(f"{'=' * 55}")
    if all_errors:
        print(f"VALIDATION FAILED — {len(all_errors)} issue(s) found:")
        print()
        for err in all_errors:
            print(f"  ✗ {err}")
        print()
        sys.exit(1)
    else:
        print(f"VALIDATION PASSED — {checks} checks passed, 0 issues.")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
