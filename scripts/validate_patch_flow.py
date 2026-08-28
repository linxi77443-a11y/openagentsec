#!/usr/bin/env python3
"""
Patch Flow Test Validator

Validates the workflow patch flow synthetic test fixtures.
"""
import sys
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = PROJECT_ROOT / "workflow_test_fixtures" / "patch_flow"
EXPECTED_PATH = FIXTURES_DIR / "expected_manifest.yaml"
GENERATED_PATH = FIXTURES_DIR / "generated_manifest.yaml"
README_PATH = FIXTURES_DIR / "README.md"

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def check_ac01_files_exist() -> bool:
    """AC-01: Required files exist"""
    required_files = [EXPECTED_PATH, GENERATED_PATH, README_PATH]
    missing = [f for f in required_files if not f.exists()]
    if not missing:
        print("PASS AC-01: All required files exist")
        return True
    print(f"FAIL AC-01: Missing files: {missing}")
    return False

def check_ac02_yaml_parseable() -> bool:
    """AC-02: YAML files are parseable"""
    try:
        load_yaml(EXPECTED_PATH)
        load_yaml(GENERATED_PATH)
        print("PASS AC-02: YAML files are parseable")
        return True
    except Exception as e:
        print(f"FAIL AC-02: YAML parse error: {e}")
        return False

def check_ac03_required_fields() -> bool:
    """AC-03: Required synthetic fields exist in expected"""
    try:
        expected = load_yaml(EXPECTED_PATH)
        required_fields = ["task_id", "synthetic_workflow_version", "synthetic_only"]
        missing = [f for f in required_fields if f not in expected]
        if not missing:
            print("PASS AC-03: Required synthetic fields exist in expected")
            return True
        print(f"FAIL AC-03: Missing fields in expected: {missing}")
        return False
    except Exception as e:
        print(f"FAIL AC-03: Error: {e}")
        return False

def check_ac04_expected_generated_differs() -> bool:
    """AC-04: Expected and generated differ (intentional issue)"""
    try:
        expected = load_yaml(EXPECTED_PATH)
        generated = load_yaml(GENERATED_PATH)
        
        # Check for the intentional missing field
        if "synthetic_workflow_version" in expected and "synthetic_workflow_version" not in generated:
            print("PASS AC-04: Expected and generated differ (missing field detected)")
            return True
        else:
            print("FAIL AC-04: Expected difference not found")
            return False
    except Exception as e:
        print(f"FAIL AC-04: Error: {e}")
        return False

def check_ac05_no_real_data() -> bool:
    """AC-05: No real data or external targets"""
    try:
        generated = load_yaml(GENERATED_PATH)
        safety = generated.get("safety_boundary", {})
        
        if safety.get("synthetic_only") == True and safety.get("real_data_used") == False:
            print("PASS AC-05: No real data or external targets")
            return True
        else:
            print("FAIL AC-05: Safety boundary not properly set")
            return False
    except Exception as e:
        print(f"FAIL AC-05: Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Patch Flow Test Validator")
    print("=" * 60)
    
    results = [
        ("AC-01", check_ac01_files_exist()),
        ("AC-02", check_ac02_yaml_parseable()),
        ("AC-03", check_ac03_required_fields()),
        ("AC-04", check_ac04_expected_generated_differs()),
        ("AC-05", check_ac05_no_real_data()),
    ]
    
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    if all(r for _, r in results):
        print(f"ALL CHECKS PASSED ({passed}/{total})")
        print("\nNOTE: AC-04 confirms intentional difference exists.")
        print("This difference is the test issue for Qoder to identify.")
        sys.exit(0)
    else:
        failed = [(name, r) for name, r in results if not r]
        print(f"FAILED CHECKS: {len(failed)}/{total}")
        for name, _ in failed:
            print(f"  - {name}")
        sys.exit(1)

if __name__ == "__main__":
    main()
