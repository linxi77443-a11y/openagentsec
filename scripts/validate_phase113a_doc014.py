#!/usr/bin/env python3
"""Phase 113A — Release Documentation Validator (DOC-014)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    checks_passed = 0
    checks_failed = 0

    def check(condition, msg):
        nonlocal checks_passed, checks_failed
        if condition:
            checks_passed += 1
            print(f"  ✓ {msg}")
        else:
            checks_failed += 1
            print(f"  ✗ {msg}")

    print("=" * 60)
    print("Phase 113A DOC-014 Validation: Release Documentation")
    print("=" * 60)
    doc_path = os.path.join(ROOT, "docs", "release_notes_v5_2.md")
    check(os.path.exists(doc_path), f"Release notes v5.2.0 exists: {doc_path}")

    if os.path.exists(doc_path):
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        check("v5.2" in content or "v5.2.0" in content, "Document references v5.2.0")
        check(len(content) > 100, "Release notes has substantial content")

    print("=" * 60)
    if checks_failed > 0:
        print(f"Validation failed: {checks_failed} errors, {checks_passed} passed.")
        return 1
    print(f"Validation passed: {checks_passed} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
