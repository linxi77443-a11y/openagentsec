#!/usr/bin/env python3
"""
M48 Registry Closure Sync Validator

Validates that module_registry.yaml and snapshot files have been correctly
updated to reflect the approved m48_closure_decision.yaml.

Checks:
  AC-01: M48.formal_simulated_mvp == true
  AC-02: M48.coverage_status includes simulated_mvp
  AC-03: snapshot M48 state synchronized
  AC-04: coverage claim no duplicates
  AC-05: safety fields unchanged
"""

import sys
import yaml
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_ROOT / "capability_modules" / "module_registry.yaml"
SNAPSHOT_PATH = PROJECT_ROOT / "m43_m50_registry_closure_consistency_snapshot.yaml"
CLOSURE_DECISION_PATH = PROJECT_ROOT / "m48_closure_decision.yaml"

# =============================================================================
# Helper Functions
# =============================================================================
def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def find_module(registry: dict, module_id: str) -> dict | None:
    for mod in registry.get("modules", []):
        if mod.get("module_id") == module_id:
            return mod
    return None

# =============================================================================
# Check Functions
# =============================================================================
def check_ac01_formal_simulated_mvp(registry: dict) -> bool:
    """AC-01: M48.formal_simulated_mvp == true"""
    mod = find_module(registry, "M48")
    if not mod:
        print("FAIL AC-01: M48 not found in registry")
        return False
    
    # Check in coverage or top-level
    coverage = mod.get("coverage", {})
    formal_mvp = coverage.get("formal_simulated_mvp", mod.get("formal_simulated_mvp"))
    
    if formal_mvp is True:
        print("PASS AC-01: M48.formal_simulated_mvp == true")
        return True
    else:
        print(f"FAIL AC-01: M48.formal_simulated_mvp == {formal_mvp} (expected true)")
        return False

def check_ac02_coverage_status(registry: dict) -> bool:
    """AC-02: M48.coverage_status includes simulated_mvp"""
    mod = find_module(registry, "M48")
    if not mod:
        print("FAIL AC-02: M48 not found in registry")
        return False
    
    coverage = mod.get("coverage", {})
    status = coverage.get("coverage_status", "")
    
    if "simulated_mvp" in str(status):
        print(f"PASS AC-02: M48.coverage_status == {status}")
        return True
    else:
        print(f"FAIL AC-02: M48.coverage_status == {status} (expected simulated_mvp)")
        return False

def check_ac03_snapshot_sync(snapshot: dict) -> bool:
    """AC-03: snapshot M48 state synchronized"""
    modules = snapshot.get("modules", {})
    m48 = modules.get("M48", {})
    
    if not m48:
        print("FAIL AC-03: M48 not found in snapshot")
        return False
    
    formal_mvp = m48.get("formal_simulated_mvp")
    closure_exists = m48.get("closure_file_exists")
    closure_status = m48.get("closure_evidence_status")
    
    issues = []
    if formal_mvp is not True:
        issues.append(f"formal_simulated_mvp={formal_mvp}")
    if closure_exists is not True:
        issues.append(f"closure_file_exists={closure_exists}")
    if closure_status != "approved":
        issues.append(f"closure_evidence_status={closure_status}")
    
    if not issues:
        print("PASS AC-03: snapshot M48 state synchronized")
        return True
    else:
        print(f"FAIL AC-03: snapshot M48 issues: {', '.join(issues)}")
        return False

def check_ac04_no_duplicate_claim() -> bool:
    """AC-04: coverage claim no duplicates"""
    # Check that M48 is not claimed by other tasks
    task_packages_dir = PROJECT_ROOT / "task_packages"
    claimed_by = []
    
    if task_packages_dir.exists():
        for pkg_dir in task_packages_dir.iterdir():
            if pkg_dir.is_dir() and pkg_dir.name != "M48-REG-SYNC-001":
                pkg_file = pkg_dir / "task_package.yaml"
                if pkg_file.exists():
                    pkg = load_yaml(pkg_file)
                    claim = pkg.get("coverage_claim", {})
                    if claim.get("module_id") == "M48":
                        claimed_by.append(pkg_dir.name)
    
    if not claimed_by:
        print("PASS AC-04: M48 coverage claim has no duplicates")
        return True
    else:
        print(f"FAIL AC-04: M48 claimed by other tasks: {claimed_by}")
        return False

def check_ac05_safety_fields(registry: dict) -> bool:
    """AC-05: safety fields unchanged"""
    mod = find_module(registry, "M48")
    if not mod:
        print("FAIL AC-05: M48 not found in registry")
        return False
    
    checks = [
        ("confirmed_vulnerability_allowed", False),
        ("formal_finding_allowed", False),
        ("production_safety", "out_of_scope"),
        ("synthetic_only", True),
        ("controlled_replay_claimed", False),
    ]
    
    issues = []
    for field, expected in checks:
        actual = mod.get(field)
        if actual != expected:
            issues.append(f"{field}={actual} (expected {expected})")
    
    if not issues:
        print("PASS AC-05: safety fields unchanged")
        return True
    else:
        print(f"FAIL AC-05: safety field issues: {', '.join(issues)}")
        return False

# =============================================================================
# Main
# =============================================================================
def main():
    print("=" * 60)
    print("M48 Registry Closure Sync Validator")
    print("=" * 60)
    
    # Load files
    try:
        registry = load_yaml(REGISTRY_PATH)
        snapshot = load_yaml(SNAPSHOT_PATH)
        closure_decision = load_yaml(CLOSURE_DECISION_PATH)
    except Exception as e:
        print(f"ERROR: Failed to load files: {e}")
        sys.exit(1)
    
    # Verify closure decision is approved
    if closure_decision.get("closure_decision") != "promote_to_formal_simulated_mvp":
        print("ERROR: m48_closure_decision.yaml not approved")
        sys.exit(1)
    
    # Run checks
    results = []
    results.append(("AC-01", check_ac01_formal_simulated_mvp(registry)))
    results.append(("AC-02", check_ac02_coverage_status(registry)))
    results.append(("AC-03", check_ac03_snapshot_sync(snapshot)))
    results.append(("AC-04", check_ac04_no_duplicate_claim()))
    results.append(("AC-05", check_ac05_safety_fields(registry)))
    
    # Summary
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    if all(r for _, r in results):
        print(f"ALL CHECKS PASSED ({passed}/{total})")
        sys.exit(0)
    else:
        failed = [(name, r) for name, r in results if not r]
        print(f"FAILED CHECKS: {len(failed)}/{total}")
        for name, _ in failed:
            print(f"  - {name}")
        sys.exit(1)

if __name__ == "__main__":
    main()
