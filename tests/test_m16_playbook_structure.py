#!/usr/bin/env python3
"""TDD Test: M16 Adversarial Playbook Structure.

RED phase: This test defines what the playbook MUST satisfy.
Run it first — it should FAIL if the playbook is missing or malformed.
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/m16_human_approval_gate_mvp/playbook.yaml"

checks_passed = 0
checks_failed = 0
errors = []


def check(condition, msg):
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  ✓ {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  ✗ {msg}")


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("TDD Test: M16 Playbook Structure")
    print("=" * 60)

    # --- File existence ---
    check(PLAYBOOK_PATH.exists(), f"playbook.yaml exists at {PLAYBOOK_PATH}")

    if not PLAYBOOK_PATH.exists():
        print("\nFAILED: playbook.yaml not found — test correctly fails (RED)")
        sys.exit(1)

    # --- Load ---
    with open(PLAYBOOK_PATH) as f:
        pb = yaml.safe_load(f)

    check(pb is not None, "playbook.yaml loads successfully")

    entries = pb.get("entries", [])
    meta = pb.get("playbook_metadata", {})

    # --- Entry counts ---
    attack = [e for e in entries if not e.get("control_case")]
    control = [e for e in entries if e.get("control_case")]
    check(len(entries) == 10, f"Exactly 10 entries (got {len(entries)})")
    check(len(attack) == 8, f"Exactly 8 attack entries (got {len(attack)})")
    check(len(control) == 2, f"Exactly 2 control entries (got {len(control)})")

    # --- Safety booleans in metadata ---
    check(meta.get("confirmed_vulnerability") is False,
          "Metadata confirmed_vulnerability == false")
    check(meta.get("formal_finding_allowed") is False,
          "Metadata formal_finding_allowed == false")
    check(meta.get("production_safety_claimed") is False,
          "Metadata production_safety_claimed == false")

    # --- SIM_ placeholders ---
    pb_text = yaml.dump(pb)
    sim_count = pb_text.count("<SIM_")
    check(sim_count >= 10, f"Contains >= 10 SIM_ placeholders (got {sim_count})")

    # --- 8 required categories ---
    required_categories = [
        "approval_required_not_obtained",
        "approval_level_mismatch",
        "approval_bypass_social_engineering",
        "approval_role_impersonation",
        "approval_scope_mismatch",
        "multi_level_approval_incomplete",
        "approval_retrospective_claim",
        "approval_urgency_pressure",
    ]
    categories = [e.get("category", "") for e in entries]
    for cat in required_categories:
        check(cat in categories, f"Category '{cat}' present")

    # --- Per-entry safety booleans ---
    for entry in entries:
        eid = entry.get("entry_id", "unknown")
        check(entry.get("confirmed_vulnerability") is False,
              f"{eid} confirmed_vulnerability == false")
        check(entry.get("formal_finding_allowed") is False,
              f"{eid} formal_finding_allowed == false")
        check(entry.get("production_safety_claimed") is False,
              f"{eid} production_safety_claimed == false")

    # --- Summary ---
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Playbook structure verified")
    else:
        print(f"FAILED: {checks_failed} check(s) failed")
        for e in errors:
            print(f"  - {e}")
    print(f"Results: {checks_passed} passed, {checks_failed} failed")
    print("=" * 60)
    sys.exit(0 if checks_failed == 0 else 1)


if __name__ == "__main__":
    main()
