#!/usr/bin/env python3
"""Phase 113A — HTML Report Generator Validator (VIEW-013)."""
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
    print("Phase 113A VIEW-013 Validation: HTML Report Generator")
    print("=" * 60)
    src_file = os.path.join(ROOT, "src", "engine", "v2", "html_report.py")
    report_file = os.path.join(ROOT, "executions", "phase113a_view013", "sample_report.html")

    check(os.path.exists(src_file), f"Source html_report.py exists: {src_file}")
    check(os.path.exists(report_file), f"HTML report output exists: {report_file}")

    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            html = f.read()
        check("<html" in html.lower() and "</html>" in html.lower(), "Valid HTML structure generated")
        check(len(html) > 100, f"HTML report has content length ({len(html)} bytes)")

    print("=" * 60)
    if checks_failed > 0:
        print(f"Validation failed: {checks_failed} errors, {checks_passed} passed.")
        return 1
    print(f"Validation passed: {checks_passed} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
