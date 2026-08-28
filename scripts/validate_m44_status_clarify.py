#!/usr/bin/env python3
"""
M44 Status Clarification Validator

Validates that the M44 status clarification document has been correctly
generated and contains accurate information.

Checks:
  AC-01: Document exists and contains required sections
  AC-02: Content matches Registry state
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
SNAPSHOT_PATH = PROJECT_ROOT / "m43_m50_registry_closure_consistency_snapshot.yaml"
TASK_DOCS_DIR = PROJECT_ROOT / "docs"
DOCUMENT_NAME = "phase_m44_status_clarification.md"

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

def read_file(path: Path) -> str | None:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

# =============================================================================
# Check Functions
# =============================================================================
def check_ac01_document_exists() -> bool:
    """AC-01: Document exists and contains required sections"""
    doc_path = TASK_DOCS_DIR / DOCUMENT_NAME
    content = read_file(doc_path)
    
    if not content:
        print(f"FAIL AC-01: Document not found at {doc_path}")
        return False
    
    required_sections = [
        "当前状态",
        "gap",
        "下一步",
        "Registry",
        "M44"
    ]
    
    missing = [s for s in required_sections if s.lower() not in content.lower()]
    
    if not missing:
        print("PASS AC-01: Document exists with all required sections")
        return True
    else:
        print(f"FAIL AC-01: Missing sections: {missing}")
        return False

def check_ac02_content_matches_registry(registry: dict, snapshot: dict) -> bool:
    """AC-02: Content matches Registry state"""
    doc_path = TASK_DOCS_DIR / DOCUMENT_NAME
    content = read_file(doc_path)
    
    if not content:
        print("FAIL AC-02: Document not found")
        return False
    
    mod = find_module(registry, "M44")
    if not mod:
        print("FAIL AC-02: M44 not found in Registry")
        return False
    
    # Check key facts
    registry_status = mod.get("coverage", {}).get("coverage_status", "")
    mvp_acceptance = mod.get("mvp_acceptance", "")
    judge_status = mod.get("judge_review_status", "")
    
    issues = []
    if registry_status not in content:
        issues.append(f"Registry coverage_status '{registry_status}' not in document")
    if mvp_acceptance not in content:
        issues.append(f"mvp_acceptance '{mvp_acceptance}' not in document")
    if judge_status not in content:
        issues.append(f"judge_review_status '{judge_status}' not in document")
    
    if not issues:
        print("PASS AC-02: Document content matches Registry state")
        return True
    else:
        print(f"FAIL AC-02: Content mismatches: {issues}")
        return False

def check_ac03_no_false_content() -> bool:
    """AC-03: No false or speculative content"""
    doc_path = TASK_DOCS_DIR / DOCUMENT_NAME
    content = read_file(doc_path)
    
    if not content:
        print("FAIL AC-03: Document not found")
        return False
    
    # Check for speculative phrases
    speculative_phrases = [
        "可能",
        "大概",
        "也许",
        "估计",
        "推测",
        "应该是",
        "假设"
    ]
    
    found = [p for p in speculative_phrases if p in content]
    
    if not found:
        print("PASS AC-03: No false or speculative content detected")
        return True
    else:
        print(f"FAIL AC-03: Speculative content found: {found}")
        return False

def check_ac04_no_duplicate_claim() -> bool:
    """AC-04: coverage claim no duplicates"""
    task_packages_dir = PROJECT_ROOT / "task_packages"
    claimed_by = []
    
    if task_packages_dir.exists():
        for pkg_dir in task_packages_dir.iterdir():
            if pkg_dir.is_dir() and pkg_dir.name != "M44-STATUS-CLARIFY-001":
                pkg_file = pkg_dir / "task_package.yaml"
                if pkg_file.exists():
                    pkg = load_yaml(pkg_file)
                    claim = pkg.get("coverage_claim", {})
                    if claim.get("module_id") == "M44" and claim.get("coverage_change_claimed"):
                        claimed_by.append(pkg_dir.name)
    
    if not claimed_by:
        print("PASS AC-04: M44 coverage claim has no duplicates")
        return True
    else:
        print(f"FAIL AC-04: M44 claimed by other tasks: {claimed_by}")
        return False

def check_ac05_no_registry_modification() -> bool:
    """AC-05: No Registry or business file modifications"""
    # This check verifies the task package declares no registry modification
    task_package_path = PROJECT_ROOT / "task_packages" / "M44-STATUS-CLARIFY-001" / "task_package.yaml"
    
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
    print("M44 Status Clarification Validator")
    print("=" * 60)
    
    # Load files
    try:
        registry = load_yaml(REGISTRY_PATH)
        snapshot = load_yaml(SNAPSHOT_PATH)
    except Exception as e:
        print(f"ERROR: Failed to load files: {e}")
        sys.exit(1)
    
    # Run checks
    results = []
    results.append(("AC-01", check_ac01_document_exists()))
    results.append(("AC-02", check_ac02_content_matches_registry(registry, snapshot)))
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
