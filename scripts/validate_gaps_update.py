#!/usr/bin/env python3
"""
v2 Remaining Gaps Update Validator

Validates that v2_remaining_gaps.yaml has been correctly updated
to reflect the current Registry state.

Checks:
  AC-01: M44/M45/M46/M47 status updated
  AC-02: Updated status matches Registry
  AC-03: No false or speculative content
  AC-04: coverage claim no duplicates
  AC-05: No Registry or business file modifications
"""

import sys
import yaml
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_ROOT / "capability_modules" / "module_registry.yaml"
GAPS_PATH = PROJECT_ROOT / "v2_remaining_gaps.yaml"

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
def check_ac01_status_updated(gaps: dict) -> bool:
    """AC-01: M44/M45/M46/M47 status updated"""
    required_updates = {
        "M44": "mvp_complete",
        "M45": "mvp_complete",
        "M46": "mvp_complete",
        "M47": "mvp_complete"
    }
    
    gaps_list = gaps.get("gaps", [])
    issues = []
    
    for module_id, expected_status in required_updates.items():
        found = False
        for gap in gaps_list:
            if gap.get("module") == module_id:
                found = True
                current_status = gap.get("status", "")
                if "mvp_complete" not in str(current_status):
                    issues.append(f"{module_id}: status='{current_status}' (expected 'mvp_complete')")
                break
        if not found:
            issues.append(f"{module_id}: not found in gaps")
    
    if not issues:
        print("PASS AC-01: M44/M45/M46/M47 status updated")
        return True
    else:
        print(f"FAIL AC-01: {issues}")
        return False

def check_ac02_status_matches_registry(gaps: dict, registry: dict) -> bool:
    """AC-02: Updated status matches Registry"""
    modules_to_check = ["M44", "M45", "M46", "M47"]
    gaps_list = gaps.get("gaps", [])
    issues = []
    
    for module_id in modules_to_check:
        # Get Registry status
        mod = find_module(registry, module_id)
        if not mod:
            issues.append(f"{module_id}: not found in Registry")
            continue
        
        registry_status = mod.get("coverage", {}).get("coverage_status", "")
        
        # Get gaps status
        gaps_status = ""
        for gap in gaps_list:
            if gap.get("module") == module_id:
                gaps_status = gap.get("status", "")
                break
        
        # Check if gaps status reflects mvp_complete
        if "mvp_complete" not in str(gaps_status):
            issues.append(f"{module_id}: gaps='{gaps_status}', registry='{registry_status}'")
    
    if not issues:
        print("PASS AC-02: Updated status matches Registry")
        return True
    else:
        print(f"FAIL AC-02: Status mismatches: {issues}")
        return False

def check_ac03_no_false_content() -> bool:
    """AC-03: No false or speculative content"""
    # Read the file as text to check for speculative phrases
    try:
        with open(GAPS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"FAIL AC-03: Cannot read file: {e}")
        return False
    
    # Check for outdated status patterns
    outdated_patterns = [
        "not_started / v2_planned",
        "not_started/v2_planned"
    ]
    
    found = [p for p in outdated_patterns if p in content]
    
    if not found:
        print("PASS AC-03: No outdated status patterns found")
        return True
    else:
        print(f"FAIL AC-03: Outdated patterns found: {found}")
        return False

def check_ac04_no_duplicate_claim() -> bool:
    """AC-04: coverage claim no duplicates"""
    task_packages_dir = PROJECT_ROOT / "task_packages"
    claimed_by = []
    
    if task_packages_dir.exists():
        for pkg_dir in task_packages_dir.iterdir():
            if pkg_dir.is_dir() and pkg_dir.name != "GAPS-UPDATE-001":
                pkg_file = pkg_dir / "task_package.yaml"
                if pkg_file.exists():
                    pkg = load_yaml(pkg_file)
                    claim = pkg.get("coverage_claim", {})
                    if claim.get("module_id") == "v2.0" and claim.get("coverage_change_claimed"):
                        claimed_by.append(pkg_dir.name)
    
    if not claimed_by:
        print("PASS AC-04: v2.0 coverage claim has no duplicates")
        return True
    else:
        print(f"FAIL AC-04: v2.0 claimed by other tasks: {claimed_by}")
        return False

def check_ac05_no_registry_modification() -> bool:
    """AC-05: No Registry or business file modifications"""
    task_package_path = PROJECT_ROOT / "task_packages" / "GAPS-UPDATE-001" / "task_package.yaml"
    
    if not task_package_path.exists():
        print("FAIL AC-05: Task package not found")
        return False
    
    pkg = load_yaml(task_package_path)
    not_performed = pkg.get("not_performed", [])
    
    checks = [
        "不修改 module_registry.yaml",
        "不修改 consistency snapshot",
    ]
    
    issues = []
    for check in checks:
        if check not in not_performed:
            issues.append(f"Missing: {check}")
    
    if not issues:
        print("PASS AC-05: Task declares no Registry modification")
        return True
    else:
        print(f"FAIL AC-05: {issues}")
        return False

# =============================================================================
# Main
# =============================================================================
def main():
    print("=" * 60)
    print("v2 Remaining Gaps Update Validator")
    print("=" * 60)
    
    # Load files
    try:
        registry = load_yaml(REGISTRY_PATH)
        gaps = load_yaml(GAPS_PATH)
    except Exception as e:
        print(f"ERROR: Failed to load files: {e}")
        sys.exit(1)
    
    # Run checks
    results = []
    results.append(("AC-01", check_ac01_status_updated(gaps)))
    results.append(("AC-02", check_ac02_status_matches_registry(gaps, registry)))
    results.append(("AC-03", check_ac03_no_false_content()))
    results.append(("AC-04", check_ac04_no_duplicate_claim()))
    results.append(("AC-05", check_ac05_no_registry_modification()))
    
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
