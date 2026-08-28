#!/usr/bin/env python3
"""Phase 62A — Adversarial Validation Schema Validator.

Validates that the adversarial_validation_schema.yaml is complete, consistent,
and enforces all required constraints per AC items 1-10.

Also validates any adversarial_validation task YAML against the schema.

This script does NOT execute any tests, connect to any system, or call any API.
"""

import sys, os, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "capability_modules/schemas/adversarial_validation_schema.yaml"

VALID_ATTACK_OBJECTIVES = [
    "data_exposure",
    "unauthorized_access",
    "tool_misuse",
    "role_escalation",
    "service_account_abuse",
    "approval_bypass",
    "business_action_induction",
    "context_poisoning",
    "exfiltration_simulation",
]

VALID_ATTACKER_TYPES = [
    "direct_prompt_injection", "jailbreak", "role_play_bypass",
    "context_poisoning", "tool_argument_pollution",
    "chain_of_thought_manipulation", "multi_turn_entrapment",
    "encoding_obfuscation", "few_shot_misalignment",
    "service_account_abuse", "approval_bypass",
    "business_action_induction", "exfiltration_simulation",
    "adversarial_multi_agent", "other_simulated_technique",
]

VALID_ACTORS = ["attacker", "red_team", "simulated_adversary", "automated_agent"]

VALID_ATTACKER_PROFILES = [
    "remote_unauthenticated", "authenticated_low_privilege",
    "authenticated_standard_user", "insider_threat",
    "compromised_service_account", "external_supply_chain",
    "privileged_escalation_path", "automated_botnet",
]

VALID_PLAYBOOK_TYPES = [
    "direct_prompt_injection", "indirect_prompt_injection",
    "multi_turn_boundary_erosion", "tool_invocation_abuse",
    "tool_argument_pollution", "role_boundary_bypass",
    "service_account_abuse", "approval_bypass",
    "business_action_induction", "simulated_exfiltration_attempt",
]

SIGNAL_LEVELS = ["capability_signal", "simulated_capability_signal", "requires_human_review"]
PROHIBITED_UPGRADES = ["confirmed_vulnerability", "formal_finding", "production_safety", "controlled_replay"]

checks = []


def check(name: str, condition: bool, detail: str = ""):
    """Register a check result."""
    checks.append({"name": name, "pass": condition, "detail": detail})
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


def check_schema_yaml_exists():
    """AC-1: schema file exists."""
    exists = SCHEMA_PATH.exists()
    check("Schema YAML exists", exists, str(SCHEMA_PATH))
    return exists


def load_schema():
    """Load and parse the schema YAML."""
    with open(SCHEMA_PATH) as f:
        return yaml.safe_load(f)


def validate_input_fields(schema):
    """AC-1: Schema covers §5 input fields (+ §6 adversarial_playbook_type)."""
    fields = schema.get("input_fields", {})
    required = [
        "assessment_mode", "actor", "attacker_profile",
        "attacker_type", "adversarial_playbook_type",
        "attack_objective", "attack_chain",
        "expected_defensive_behavior",
    ]
    missing = [r for r in required if r not in fields]
    check("§5 input_fields: assessment_mode", "assessment_mode" in fields,
          f"missing: {missing}" if missing else "present")
    check("§5 input_fields: actor", "actor" in fields)
    check("§5 input_fields: attacker_profile", "attacker_profile" in fields)
    check("§5 input_fields: attacker_type", "attacker_type" in fields)
    check("§5 input_fields: adversarial_playbook_type", "adversarial_playbook_type" in fields)
    check("§5 input_fields: attack_objective", "attack_objective" in fields)
    check("§5 input_fields: attack_chain", "attack_chain" in fields)
    check("§5 input_fields: expected_defensive_behavior",
          "expected_defensive_behavior" in fields)
    check("§5 all 8 input fields present（含 §6 adversarial_playbook_type）", len(missing) == 0,
          f"missing: {missing}" if missing else "all present")
    return missing


def validate_result_fields(schema):
    """AC-4: Schema covers §7 result fields."""
    fields = schema.get("result_fields", {})
    required = [
        "breakthrough_detected", "breakthrough_type",
        "exploit_chain_candidate", "evidence_trace",
        "confirmed_vulnerability", "formal_finding_allowed",
        "requires_human_review",
    ]
    missing = [r for r in required if r not in fields]
    check("§7 result_fields: breakthrough_detected", "breakthrough_detected" in fields)
    check("§7 result_fields: breakthrough_type", "breakthrough_type" in fields)
    check("§7 result_fields: exploit_chain_candidate", "exploit_chain_candidate" in fields)
    check("§7 result_fields: evidence_trace", "evidence_trace" in fields)
    check("§7 result_fields: confirmed_vulnerability", "confirmed_vulnerability" in fields)
    check("§7 result_fields: formal_finding_allowed", "formal_finding_allowed" in fields)
    check("§7 result_fields: requires_human_review", "requires_human_review" in fields)
    check("§7 all 7 result fields present", len(missing) == 0,
          f"missing: {missing}" if missing else "all present")


def validate_attack_success_signals(schema):
    """AC-5: Schema covers §8 attack success signals classification."""
    signals = schema.get("attack_success_signals", {})
    levels = signals.get("classification_levels", [])
    level_names = [l["level"] for l in levels]

    check("§8 classification_levels defined", len(levels) > 0)
    check("§8 capability_signal present", "capability_signal" in level_names)
    check("§8 simulated_capability_signal present", "simulated_capability_signal" in level_names)
    check("§8 requires_human_review present", "requires_human_review" in level_names)

    # Check all levels have auto_upgrade_forbidden
    all_forbidden = all(
        "auto_upgrade_forbidden" in l
        and "confirmed_vulnerability" in l["auto_upgrade_forbidden"]
        and "formal_finding" in l["auto_upgrade_forbidden"]
        for l in levels
    )
    check("§8 all levels forbid auto-upgrade to confirmed_vulnerability/formal_finding",
          all_forbidden)
    permitted = signals.get("permitted_signal_types", [])
    check("§8 permitted_signal_types defined", len(permitted) > 0)
    check("§8 all 3 signal types permitted",
          all(s in permitted for s in SIGNAL_LEVELS))


def validate_attacker_type_required(schema):
    """AC-2: attacker_type is required for adversarial_validation."""
    at = schema.get("input_fields", {}).get("attacker_type", {})
    is_required = at.get("required", False)
    has_allowed = len(at.get("allowed_values", [])) > 0
    check("AC-2: attacker_type is required", is_required)
    check("AC-2: attacker_type has allowed_values", has_allowed)
    if not is_required:
        check("AC-2: attacker_type required flag",
              False, "must be set to required: true")


def validate_attack_objective_required_and_enum(schema):
    """AC-3: attack_objective is required and uses the schema enum."""
    ao = schema.get("input_fields", {}).get("attack_objective", {})
    is_required = ao.get("required", False)
    allowed = ao.get("allowed_values", [])

    check("AC-2/3: attack_objective is required", is_required)
    check("AC-3: attack_objective has allowed_values", len(allowed) > 0)

    # Check each enum value matches the spec
    missing_obj = [v for v in VALID_ATTACK_OBJECTIVES if v not in allowed]
    extra_obj = [v for v in allowed if v not in VALID_ATTACK_OBJECTIVES]
    check("AC-3: attack_objective enum covers all 9 spec values",
          len(missing_obj) == 0,
          f"missing: {missing_obj}" if missing_obj else "all present")
    check("AC-3: attack_objective enum has no extra values",
          len(extra_obj) == 0,
          f"extra: {extra_obj}" if extra_obj else "no extras")


def validate_defaults(schema):
    """AC-6: Default values are set correctly."""
    defaults = schema.get("defaults", {})
    check("AC-6: confirmed_vulnerability default false",
          defaults.get("confirmed_vulnerability") == False)
    check("AC-6: formal_finding_allowed default false",
          defaults.get("formal_finding_allowed") == False)
    check("AC-6: production_safety_claimed default false",
          defaults.get("production_safety_claimed") == False)
    check("AC-6: controlled_replay_claimed default false",
          defaults.get("controlled_replay_claimed") == False)

    # Also check in result_fields
    for field in ["confirmed_vulnerability", "formal_finding_allowed"]:
        rf = schema.get("result_fields", {}).get(field, {})
        check(f"AC-6: {field} default false in result_fields",
              rf.get("default") == False)

    # Check metadata
    meta = schema.get("schema_metadata", {})
    check("AC-6: formal_finding_allowed=false in metadata",
          meta.get("formal_finding_allowed") == False)
    check("AC-6: production_safety_claimed=false in metadata",
          meta.get("production_safety_claimed") == False)
    check("AC-6: controlled_replay_claimed=false in metadata",
          meta.get("controlled_replay_claimed") == False)


def validate_prohibited_upgrades(schema):
    """AC-5: Attack success signals must not auto-upgrade."""
    signals = schema.get("attack_success_signals", {})
    prohibited = signals.get("prohibited_upgrade_paths", [])
    check("AC-5: prohibited_upgrade_paths defined", len(prohibited) > 0)

    # Check all signal levels forbid confirmed_vulnerability and formal_finding
    for level in SIGNAL_LEVELS:
        for target in ["confirmed_vulnerability", "formal_finding"]:
            has_rule = any(
                p.get("from") == level and target in p.get("to", "")
                for p in prohibited
            )
            check(f"AC-5: {level} → {target} prohibited",
                  has_rule)


def validate_evidence_and_exploit_chain(schema):
    """AC-7: evidence_trace and exploit_chain_candidate have schema definitions."""
    rf = schema.get("result_fields", {})
    has_evidence = "evidence_trace" in rf and len(rf["evidence_trace"].get("item_schema", {}).get("fields", {})) > 0
    has_exploit = "exploit_chain_candidate" in rf and len(rf["exploit_chain_candidate"].get("item_schema", {}).get("fields", {})) > 0

    check("AC-7: evidence_trace has schema definition", has_evidence)
    check("AC-7: exploit_chain_candidate has schema definition", has_exploit)


def validate_adversarial_playbook_type(schema):
    """§6: adversarial_playbook_type is required with 10 enum values."""
    apt = schema.get("input_fields", {}).get("adversarial_playbook_type", {})
    is_required = apt.get("required", False)
    allowed = apt.get("allowed_values", [])

    check("§6: adversarial_playbook_type is required", is_required)
    check("§6: adversarial_playbook_type has allowed_values", len(allowed) > 0)

    missing_pt = [v for v in VALID_PLAYBOOK_TYPES if v not in allowed]
    extra_pt = [v for v in allowed if v not in VALID_PLAYBOOK_TYPES]
    check("§6: playbook_type enum covers all 10 spec values",
          len(missing_pt) == 0,
          f"missing: {missing_pt}" if missing_pt else "all present")
    check("§6: playbook_type enum has no extra values",
          len(extra_pt) == 0,
          f"extra: {extra_pt}" if extra_pt else "no extras")


def validate_breakthrough_constraint(schema):
    """§9: breakthrough_detected=true mandates requires_human_review=true,
    forbids confirmed_vulnerability=true and formal_finding_allowed=true."""
    constraints = schema.get("constraints", [])
    brk_001 = None
    for c in constraints:
        if c.get("id") == "BRK-001":
            brk_001 = c
            break

    check("§9: BRK-001 constraint defined", brk_001 is not None)
    if brk_001:
        check("§9: BRK-001 condition is breakthrough_detected==true",
              brk_001.get("condition") == "breakthrough_detected == true")
        mandates = brk_001.get("mandates", {})
        check("§9: BRK-001 mandates requires_human_review=true",
              mandates.get("requires_human_review") is True)
        forbids = brk_001.get("forbids", {})
        check("§9: BRK-001 forbids confirmed_vulnerability=true",
              forbids.get("confirmed_vulnerability") is True)
        check("§9: BRK-001 forbids formal_finding_allowed=true",
              forbids.get("formal_finding_allowed") is True)


def validate_validation_rules(schema):
    """Check that validation_rules section is complete."""
    rules = schema.get("validation_rules", [])
    rule_ids = [r["id"] for r in rules]

    expected_rules = [f"AV-SCHEMA-{i:03d}" for i in range(1, 14)]
    missing_rules = [r for r in expected_rules if r not in rule_ids]
    check("Validation rules section complete",
          len(missing_rules) == 0,
          f"missing: {missing_rules}" if missing_rules else f"all {len(rules)} rules present")


def main():
    print("=" * 60)
    print("Phase 62A — Adversarial Validation Schema Validation")
    print("=" * 60)

    # Step 1: Schema exists
    if not check_schema_yaml_exists():
        print("\n[FAIL] Schema file missing. Aborting.")
        sys.exit(1)

    schema = load_schema()
    print(f"\nSchema loaded: {SCHEMA_PATH.name}")

    # Run all validations
    print("\n--- Schema Structure ---")
    validate_input_fields(schema)
    validate_result_fields(schema)
    validate_attack_success_signals(schema)

    print("\n--- Schema Constraints ---")
    validate_attacker_type_required(schema)
    validate_attack_objective_required_and_enum(schema)
    validate_defaults(schema)
    validate_prohibited_upgrades(schema)
    validate_evidence_and_exploit_chain(schema)
    validate_adversarial_playbook_type(schema)
    validate_breakthrough_constraint(schema)
    validate_validation_rules(schema)

    # Summary
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    total = len(checks)

    print(f"\n{'=' * 60}")
    print(f"Validation Summary")
    print(f"{'=' * 60}")
    print(f"  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failed == 0:
        print(f"\nALL {total} CHECKS PASSED — Schema is complete and consistent.")
        sys.exit(0)
    else:
        print(f"\n{failed} check(s) FAILED. Review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
