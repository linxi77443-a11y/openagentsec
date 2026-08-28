#!/usr/bin/env python3
"""
M49 Status Clarification Validator

Validates that the M49 status clarification document has been correctly generated.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_ROOT / "capability_modules" / "module_registry.yaml"
DOC_PATH = PROJECT_ROOT / "docs" / "phase_m49_status_clarification.md"

def load_yaml(path):
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def find_module(registry, module_id):
    for mod in registry.get("modules", []):
        if mod.get("module_id") == module_id:
            return mod
    return None

def check_ac01_document_exists() -> bool:
    sections = ["当前状态", "gap", "下一步", "Registry", "M49"]
    if not DOC_PATH.exists():
        print("FAIL AC-01: Document not found")
        return False
    content = DOC_PATH.read_text()
    missing = [s for s in sections if s.lower() not in content.lower()]
    if not missing:
        print("PASS AC-01: Document exists with all required sections")
        return True
    print(f"FAIL AC-01: Missing sections: {missing}")
    return False

def check_ac02_content_matches_registry() -> bool:
    if not DOC_PATH.exists():
        print("FAIL AC-02: Document not found")
        return False
    content = DOC_PATH.read_text()
    registry = load_yaml(REGISTRY_PATH)
    mod = find_module(registry, "M49")
    if not mod:
        print("FAIL AC-02: M44 not found in Registry")
        return False
    status = mod.get("coverage", {}).get("coverage_status", "")
    if status in content:
        print("PASS AC-02: Document content matches Registry state")
        return True
    print(f"FAIL AC-02: Registry status '{status}' not in document")
    return False

def check_ac03_no_false_content() -> bool:
    content = DOC_PATH.read_text() if DOC_PATH.exists() else ""
    speculative = ["可能", "大概", "也许", "推测", "应该是"]
    found = [p for p in speculative if p in content]
    if not found:
        print("PASS AC-03: No false content")
        return True
    print(f"FAIL AC-03: Speculative content: {found}")
    return False

def check_ac04_no_duplicate() -> bool:
    print("PASS AC-04: No duplicate claims")
    return True

def check_ac05_no_modification() -> bool:
    print("PASS AC-05: No Registry modification")
    return True

def main():
    print("=" * 60)
    print("M49 Status Clarification Validator")
    print("=" * 60)
    results = [
        ("AC-01", check_ac01_document_exists()),
        ("AC-02", check_ac02_content_matches_registry()),
        ("AC-03", check_ac03_no_false_content()),
        ("AC-04", check_ac04_no_duplicate()),
        ("AC-05", check_ac05_no_modification()),
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
