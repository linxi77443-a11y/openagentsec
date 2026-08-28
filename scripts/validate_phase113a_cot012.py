#!/usr/bin/env python3
"""Phase 113A — COT Reasoning Abnormality Analyzer Validator (COT-012)."""
import os
import sys
import yaml

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
    print("Phase 113A COT-012 Validation: COT Reasoning Abnormality Analyzer")
    print("=" * 60)
    src_file = os.path.join(ROOT, "src", "engine", "v2", "cot_analyzer.py")
    samples_file = os.path.join(ROOT, "adversarial_playbooks", "cot_reasoning_abnormality_mvp", "cot_samples.yaml")
    exec_file = os.path.join(ROOT, "executions", "phase113a_cot012", "analysis_report.yaml")

    check(os.path.exists(src_file), f"Source cot_analyzer.py exists: {src_file}")
    check(os.path.exists(samples_file), f"Corpus cot_samples.yaml exists: {samples_file}")
    check(os.path.exists(exec_file), f"Execution report exists: {exec_file}")

    if os.path.exists(samples_file):
        with open(samples_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        samples = data.get("samples", []) if data else []
        check(len(samples) >= 30, f"COT samples count >= 30 (got {len(samples)})")

    if os.path.exists(exec_file):
        with open(exec_file, "r", encoding="utf-8") as f:
            rep = yaml.safe_load(f)
        summary = rep.get("summary", {}) if rep else {}
        check(summary.get("total_samples", 0) >= 30, f"Report total_samples >= 30 (got {summary.get('total_samples')})")

    print("=" * 60)
    if checks_failed > 0:
        print(f"Validation failed: {checks_failed} errors, {checks_passed} passed.")
        return 1
    print(f"Validation passed: {checks_passed} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
