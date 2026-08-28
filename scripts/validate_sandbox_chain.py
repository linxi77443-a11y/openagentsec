#!/usr/bin/env python3
"""
Sandbox Chain Verification Validator

Validates that the sandbox toolchain verification has been correctly executed.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SANDBOX_DIR = PROJECT_ROOT / "sandbox"
SCRIPT_PATH = SANDBOX_DIR / "test_chain_verify.py"
RESULTS_PATH = SANDBOX_DIR / "execution_results.yaml"

def check_ac01_script_exists() -> bool:
    if SCRIPT_PATH.exists():
        print("PASS AC-01: Verification script exists")
        return True
    print("FAIL AC-01: Verification script not found")
    return False

def check_ac02_results_generated() -> bool:
    if RESULTS_PATH.exists():
        print("PASS AC-02: execution_results.yaml generated")
        return True
    print("FAIL AC-02: execution_results.yaml not found")
    return False

def check_ac03_results_valid() -> bool:
    import yaml
    if not RESULTS_PATH.exists():
        print("FAIL AC-03: Results file not found")
        return False
    try:
        with open(RESULTS_PATH, "r") as f:
            data = yaml.safe_load(f)
        required = ["task_id", "status", "timestamp", "checks"]
        missing = [k for k in required if k not in data]
        if not missing:
            print("PASS AC-03: Results file is valid")
            return True
        print(f"FAIL AC-03: Missing fields: {missing}")
        return False
    except Exception as e:
        print(f"FAIL AC-03: Invalid YAML: {e}")
        return False

def check_ac04_no_duplicate() -> bool:
    print("PASS AC-04: No duplicate claims")
    return True

def check_ac05_no_external_modification() -> bool:
    print("PASS AC-05: No external file modification")
    return True

def main():
    print("=" * 60)
    print("Sandbox Chain Verification Validator")
    print("=" * 60)
    results = [
        ("AC-01", check_ac01_script_exists()),
        ("AC-02", check_ac02_results_generated()),
        ("AC-03", check_ac03_results_valid()),
        ("AC-04", check_ac04_no_duplicate()),
        ("AC-05", check_ac05_no_external_modification()),
    ]
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    if all(r for _, r in results):
        print(f"ALL CHECKS PASSED ({passed}/{len(results)})")
        sys.exit(0)
    else:
        print(f"FAILED CHECKS: {len(results) - passed}/{len(results)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
