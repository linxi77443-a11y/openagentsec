#!/usr/bin/env python3
"""
Phase 44B.1 — Matrix Coverage Registry Alignment Validation
"""
import os, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []
WARNINGS = []

def check(condition, msg, severity="error"):
    if not condition:
        (ERRORS if severity == "error" else WARNINGS).append(msg)

def main():
    print("=" * 60)
    print("Phase 44B.1 — Matrix Coverage Registry Alignment Validation")
    print("=" * 60)

    # Registry file existence
    print("\n[1/6] Registry file existence...")
    reg_path = ROOT / "capability_modules/module_registry.yaml"
    check(reg_path.exists(), f"Missing: {reg_path.relative_to(ROOT)}")

    # Load registry
    with open(reg_path) as f:
        data = yaml.safe_load(f)
    modules = {m["module_id"]: m for m in data.get("modules", [])}

    # Key completed modules present
    print("\n[2/6] Key completed modules present...")
    for mid in ["M01", "M02", "M03", "M06", "M12", "M13", "M14", "M15", "M38", "M39"]:
        check(mid in modules, f"Missing module: {mid}")

    # P0 blank candidate modules present
    print("\n[3/6] P0 blank candidate modules present...")
    for mid in ["M04", "M07", "M08", "M19", "M41"]:
        check(mid in modules, f"Missing P0 blank module: {mid}")

    # Coverage blocks present on completed modules
    print("\n[4/6] Coverage blocks present on completed modules...")
    required_fields = ["matrix_area", "coverage_status", "implementation_status",
                       "evidence", "gaps", "next_action"]
    for mid in ["M01", "M06", "M12", "M13", "M14", "M15", "M38", "M39"]:
        c = modules[mid].get("coverage", {})
        for field in required_fields:
            check(field in c, f"{mid} coverage missing field: {field}")

    # M16 reference_only
    print("\n[5/6] M16 status check...")
    c16 = modules.get("M16", {}).get("coverage", {})
    check(c16.get("coverage_status") == "reference_only",
          "M16 should be reference_only")
    next_action = c16.get("next_action", "")
    check("defer" in next_action.lower() or "reference" in next_action.lower(),
          f"M16 next_action should reference defer: {next_action}")

    # At least one P0 data/permission module has reference spike next_action
    print("\n[6/6] P0 blank module next_action check...")
    blank_modules = {"M07", "M08", "M04", "M19", "M41"}
    found_ref_spike = False
    for mid in blank_modules:
        if mid in modules:
            c = modules[mid].get("coverage", {})
            na = c.get("next_action", "")
            if "reference spike" in na.lower():
                found_ref_spike = True
                break
    check(found_ref_spike, "No P0 blank module has 'reference spike' next_action")

    # Report
    print("\n" + "=" * 60)
    if ERRORS:
        print(f"FAILED — {len(ERRORS)} error(s):")
        for e in ERRORS:
            print(f"  x {e}")
    else:
        print("ALL CHECKS PASSED")
    if WARNINGS:
        print(f"\n{len(WARNINGS)} warning(s):")
        for w in WARNINGS:
            print(f"  ! {w}")
    print("=" * 60)
    return len(ERRORS) == 0

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
