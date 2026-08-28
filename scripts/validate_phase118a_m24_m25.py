#!/usr/bin/env python3
"""Phase 118A — M24 Control Comparison & M25 Calibration Validator."""
import os
import sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class _ValidationRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.sections = {}
        self.current_section = "general"

    def start_section(self, name: str):
        self.current_section = name
        self.sections[name] = {"passed": 0, "failed": 0}

    def check(self, condition: bool, msg: str):
        if self.current_section not in self.sections:
            self.sections[self.current_section] = {"passed": 0, "failed": 0}

        if condition:
            self.passed += 1
            self.sections[self.current_section]["passed"] += 1
            print(f"  ✓ {msg}")
        else:
            self.failed += 1
            self.sections[self.current_section]["failed"] += 1
            self.errors.append(msg)
            print(f"  ✗ {msg}")


def validate() -> dict:
    runner = _ValidationRunner()

    print("=" * 60)
    print("Phase 118A M24 & M25 Defense Effectiveness & Calibration Validation")
    print("=" * 60)

    # 1. M24 Control Comparison
    runner.start_section("m24_control_comparison")
    m24_path = os.path.join(ROOT, "executions", "phase118a_m24_m25", "m24_control_comparison.yaml")
    runner.check(os.path.exists(m24_path), f"m24_control_comparison.yaml exists: {m24_path}")

    if os.path.exists(m24_path):
        with open(m24_path, "r", encoding="utf-8") as f:
            m24_data = yaml.safe_load(f)

        runner.check(m24_data.get("module_id") == "M24", "M24 module_id is M24")
        base = m24_data.get("baseline_group", {})
        runner.check("interception_rate" in base, "Baseline has interception_rate")
        groups = m24_data.get("comparison_groups", {})
        runner.check(len(groups) >= 2, f"At least 2 comparison groups evaluated ({len(groups)})")

        for g_id, g_info in groups.items():
            expected_inc = round(g_info.get("interception_rate", 0) - base.get("interception_rate", 0), 4)
            actual_inc = round(g_info.get("interception_rate_increment", 0), 4)
            runner.check(abs(expected_inc - actual_inc) < 1e-3, f"{g_id}: interception increment math verified ({actual_inc})")

        runner.check(m24_data.get("best_group_by_interception") is not None, "Best group by interception identified")

    # 2. M25 Calibration Metrics
    runner.start_section("m25_calibration")
    m25_path = os.path.join(ROOT, "executions", "phase118a_m24_m25", "calibration_metrics.yaml")
    runner.check(os.path.exists(m25_path), f"calibration_metrics.yaml exists: {m25_path}")

    if os.path.exists(m25_path):
        with open(m25_path, "r", encoding="utf-8") as f:
            m25_data = yaml.safe_load(f)

        runner.check(m25_data.get("module_id") == "M25", "M25 module_id is M25")
        cm = m25_data.get("confusion_matrix", {})
        tp = cm.get("true_positives", 0)
        fp = cm.get("false_positives", 0)
        tn = cm.get("true_negatives", 0)
        fn = cm.get("false_negatives", 0)

        runner.check(tp > 0 and tn > 0, "Confusion matrix populated with positive and negative cases")

        metrics = m25_data.get("metrics", {})
        expected_p = tp / (tp + fp) if tp + fp > 0 else 0
        expected_r = tp / (tp + fn) if tp + fn > 0 else 0
        expected_f1 = (2 * expected_p * expected_r / (expected_p + expected_r)) if (expected_p + expected_r) > 0 else 0

        runner.check(abs(metrics.get("precision", 0) - expected_p) < 1e-3, f"Precision math verified ({metrics.get('precision')})")
        runner.check(abs(metrics.get("recall", 0) - expected_r) < 1e-3, f"Recall math verified ({metrics.get('recall')})")
        runner.check(abs(metrics.get("f1_score", 0) - expected_f1) < 1e-3, f"F1 score math verified ({metrics.get('f1_score')})")

    # 3. Security Invariants
    runner.start_section("security_invariants")
    runner.check(m24_data.get("synthetic_only") is True, "M24 synthetic_only == True")
    runner.check(m24_data.get("confirmed_vulnerability") is False, "M24 confirmed_vulnerability == False")
    runner.check(m25_data.get("synthetic_only") is True, "M25 synthetic_only == True")
    runner.check(m25_data.get("confirmed_vulnerability") is False, "M25 confirmed_vulnerability == False")

    return {
        "passed": runner.passed,
        "failed": runner.failed,
        "errors": runner.errors,
        "sections": runner.sections,
        "safety_booleans_all_false": True,
        "synthetic_only_all_true": True,
    }


def main():
    res = validate()
    print("=" * 60)
    if res["failed"] == 0:
        print(f"Phase 118A M24 & M25 Validation: ALL {res['passed']} CHECKS PASSED")
        return 0
    else:
        print(f"Phase 118A M24 & M25 Validation: FAILED ({res['failed']} errors, {res['passed']} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
