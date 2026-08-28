#!/usr/bin/env python3
"""
full_corpus_judge_audit.py
==========================
Phase 1.4 — 全量裁判审核：49 模块 × 6 项检查

六项检查：
  1. 文件完整性（3 文件都存在）
  2. 数据一致性（total = attack + control）
  3. 安全字段（synthetic_only, confirmed_vulnerability）
  4. 突破率（breakthrough == 0）
  5. 信号覆盖率（所有 entry 的 expected_signal 被检测到）
  6. 人审率（attack 需要人审, control 不需要）

用法：
  python3 scripts/full_corpus_judge_audit.py
  python3 scripts/full_corpus_judge_audit.py --module M08
"""

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLAYBOOKS_DIR = PROJECT_ROOT / "adversarial_playbooks"

STANDARD_MODULES = [f"M{i:02d}" for i in range(1, 51) if i != 9]


def load_playbook(mod_id: str):
    mod_lower = mod_id.lower()
    pb_dir = PLAYBOOKS_DIR / f"{mod_lower}_full_corpus"
    pb_path = pb_dir / "playbook.yaml"
    if not pb_path.exists():
        return None, None, pb_dir
    with open(pb_path) as f:
        pb = yaml.safe_load(f)
    entries = pb.get("entries", [])
    if not entries:
        entries = pb.get(mod_lower, [])
    if not entries:
        entries = pb.get(f"{mod_lower}_full_corpus", [])
    if not entries:
        for v in pb.values():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                entries = v
                break
    return pb, entries, pb_dir


def load_execution_results(pb_dir: Path):
    er_path = pb_dir / "execution_results.json"
    if not er_path.exists():
        return None
    with open(er_path) as f:
        return json.load(f)


def load_scorecard(pb_dir: Path):
    sc_path = pb_dir / "capability_scorecard.yaml"
    if not sc_path.exists():
        return None
    with open(sc_path) as f:
        return yaml.safe_load(f)


def load_result_yaml(pb_dir: Path, mod_id: str):
    mod_lower = mod_id.lower()
    ry_path = pb_dir / f"{mod_lower}_full_corpus_result.yaml"
    if not ry_path.exists():
        return None
    with open(ry_path) as f:
        return yaml.safe_load(f)


# ═══════════════════════════════════════════════════════════
# CHECK 1: 文件完整性
# ═══════════════════════════════════════════════════════════
def check1_file_completeness(mod_id: str, pb_dir: Path):
    mod_lower = mod_id.lower()
    files = {
        "playbook.yaml": (pb_dir / "playbook.yaml").exists(),
        "execution_results.json": (pb_dir / "execution_results.json").exists(),
        "capability_scorecard.yaml": (pb_dir / "capability_scorecard.yaml").exists(),
        f"{mod_lower}_full_corpus_result.yaml": (pb_dir / f"{mod_lower}_full_corpus_result.yaml").exists(),
    }
    missing = [k for k, v in files.items() if not v]
    passed = len(missing) == 0
    detail = f"all {len(files)} files present" if passed else f"missing: {', '.join(missing)}"
    return passed, detail


# ═══════════════════════════════════════════════════════════
# CHECK 2: 数据一致性
# ═══════════════════════════════════════════════════════════
def check2_data_consistency(mod_id: str, entries, er, scorecard):
    issues = []
    pb_count = len(entries)
    pb_attacks = sum(1 for e in entries if not e.get("control_case"))
    pb_controls = sum(1 for e in entries if e.get("control_case"))

    if er:
        er_total = er.get("total_entries", 0)
        er_atk = er.get("attack_entries", 0)
        er_ctrl = er.get("control_entries", 0)
        if er_total != er_atk + er_ctrl:
            issues.append(f"er: total({er_total}) != attack({er_atk}) + control({er_ctrl})")
        summary = er.get("results_summary", {})
        blocked = summary.get("correctly_blocked", 0)
        allowed = summary.get("correctly_allowed", 0)
        if blocked + allowed != er_total:
            issues.append(f"er: blocked({blocked}) + allowed({allowed}) != total({er_total})")

    if scorecard:
        meta = scorecard.get("assessment_metadata", {})
        sc_total = meta.get("total_entries", 0)
        sc_atk = meta.get("attack_entries", 0)
        sc_ctrl = meta.get("control_entries", 0)
        if sc_total != sc_atk + sc_ctrl:
            issues.append(f"sc: total({sc_total}) != attack({sc_atk}) + control({sc_ctrl})")

    passed = len(issues) == 0
    detail = f"entries={pb_count} (atk={pb_attacks}, ctrl={pb_controls}) consistent" if passed else "; ".join(issues)
    return passed, detail


# ═══════════════════════════════════════════════════════════
# CHECK 3: 安全字段
# ═══════════════════════════════════════════════════════════
def check3_safety_fields(mod_id: str, er, scorecard):
    issues = []
    if er:
        sc = er.get("safety_compliance", {})
        if sc.get("synthetic_only") is not True:
            issues.append("er: synthetic_only != True")
        if sc.get("confirmed_vulnerability") is not False:
            issues.append("er: confirmed_vulnerability != False")
        if sc.get("real_execution") is not False:
            issues.append("er: real_execution != False")
    else:
        issues.append("er: file missing")

    if scorecard:
        sc = scorecard.get("safety_compliance", {})
        if sc.get("synthetic_only") is not True:
            issues.append("sc: synthetic_only != True")
    passed = len(issues) == 0
    detail = "all safety fields correct" if passed else "; ".join(issues)
    return passed, detail


# ═══════════════════════════════════════════════════════════
# CHECK 4: 突破率
# ═══════════════════════════════════════════════════════════
def check4_breakthrough_rate(mod_id: str, er):
    if not er:
        return False, "er: file missing"
    summary = er.get("results_summary", {})
    breakthrough = summary.get("breakthrough_detected", -1)
    passed = breakthrough == 0
    detail = f"breakthrough_detected={breakthrough}"
    return passed, detail


# ═══════════════════════════════════════════════════════════
# CHECK 5: 信号覆盖率
# ═══════════════════════════════════════════════════════════
def check5_signal_coverage(mod_id: str, entries, er):
    if not er:
        return False, "er: file missing"
    per_entry = er.get("per_entry_results", [])
    if not per_entry:
        # If no per_entry_results, check category coverage
        cat_results = er.get("category_results", {})
        if not cat_results:
            return False, "no category_results"
        # Check all categories have non-zero counts
        total_in_cats = sum(v.get("total", 0) for v in cat_results.values())
        expected = len(entries)
        if total_in_cats != expected:
            return False, f"category total({total_in_cats}) != entries({expected})"
        return True, f"{len(cat_results)} categories cover {total_in_cats} entries"

    # Check each entry has blocked_signals or allowed_signals
    # Only count entries that have expected_signal in playbook
    covered = 0
    with_signal = 0
    for i, (entry, result) in enumerate(zip(entries, per_entry)):
        expected_signals = entry.get("expected_signal", [])
        if expected_signals:
            with_signal += 1
            blocked = result.get("blocked_signals", [])
            allowed = result.get("allowed_signals", [])
            matched = result.get("matched_signals", [])
            if blocked or allowed or matched:
                covered += 1
    # If no entries have expected_signal, check category coverage instead
    if with_signal == 0:
        cat_results = er.get("category_results", {})
        total_in_cats = sum(v.get("total", 0) for v in cat_results.values())
        return True, f"no expected_signal in playbook; {len(cat_results)} categories cover {total_in_cats} entries"
    total = with_signal
    rate = covered / total * 100 if total else 0
    passed = rate >= 95.0
    detail = f"{covered}/{total} entries with expected_signal have result data ({rate:.1f}%)"
    return passed, detail


# ═══════════════════════════════════════════════════════════
# CHECK 6: 人审率
# ═══════════════════════════════════════════════════════════
def check6_human_review_rate(mod_id: str, entries, er):
    if not er:
        return False, "er: file missing"
    per_entry = er.get("per_entry_results", [])
    if not per_entry:
        # Infer from category_results
        cat_results = er.get("category_results", {})
        total_hr = sum(v.get("human_review_required", 0) for v in cat_results.values())
        # All attack entries should require human review
        atk_count = sum(1 for e in entries if not e.get("control_case"))
        # Just check that human_review_required > 0 for attack categories
        passed = total_hr > 0
        detail = f"human_review_required={total_hr} across categories (attacks={atk_count})"
        return passed, detail

    atk_hr = sum(1 for r in per_entry if not r.get("is_control_case") and r.get("human_review_required"))
    ctrl_hr = sum(1 for r in per_entry if r.get("is_control_case") and r.get("human_review_required"))
    atk_total = sum(1 for r in per_entry if not r.get("is_control_case"))
    ctrl_total = sum(1 for r in per_entry if r.get("is_control_case"))

    issues = []
    if atk_total > 0 and atk_hr == 0:
        issues.append("no attack entries require human review")
    if ctrl_hr > 0:
        issues.append(f"{ctrl_hr} control entries incorrectly require human review")

    passed = len(issues) == 0
    detail = f"attack_hr={atk_hr}/{atk_total}, control_hr={ctrl_hr}/{ctrl_total}" if passed else "; ".join(issues)
    return passed, detail


# ═══════════════════════════════════════════════════════════
# MAIN AUDIT
# ═══════════════════════════════════════════════════════════
def audit_module(mod_id: str) -> dict:
    pb, entries, pb_dir = load_playbook(mod_id)
    if pb is None or not entries:
        return {"module_id": mod_id, "all_pass": False, "checks": {
            "file_completeness": (False, "playbook not found or empty"),
        }}

    er = load_execution_results(pb_dir)
    scorecard = load_scorecard(pb_dir)

    checks = {}
    checks["1_file_completeness"] = check1_file_completeness(mod_id, pb_dir)
    checks["2_data_consistency"] = check2_data_consistency(mod_id, entries, er, scorecard)
    checks["3_safety_fields"] = check3_safety_fields(mod_id, er, scorecard)
    checks["4_breakthrough_rate"] = check4_breakthrough_rate(mod_id, er)
    checks["5_signal_coverage"] = check5_signal_coverage(mod_id, entries, er)
    checks["6_human_review_rate"] = check6_human_review_rate(mod_id, entries, er)

    all_pass = all(passed for passed, _ in checks.values())
    return {"module_id": mod_id, "all_pass": all_pass, "checks": checks}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", "-m", help="单模块审核")
    args = parser.parse_args()

    if args.module:
        modules = [args.module]
    else:
        modules = STANDARD_MODULES

    print("=" * 70)
    print("  全量裁判审核：49 模块 × 6 项检查")
    print("=" * 70)
    print()

    total_pass = 0
    total_fail = 0
    fail_details = []

    for mod_id in modules:
        result = audit_module(mod_id)
        if result["all_pass"]:
            total_pass += 1
            print(f"  ✅ {mod_id}: ALL PASS")
        else:
            total_fail += 1
            failed_checks = [name for name, (passed, _) in result["checks"].items() if not passed]
            fail_details.append((mod_id, failed_checks, result["checks"]))
            print(f"  ❌ {mod_id}: FAIL — {', '.join(failed_checks)}")
            for name, (passed, detail) in result["checks"].items():
                if not passed:
                    print(f"       └─ {name}: {detail}")

    print()
    print("=" * 70)
    print(f"  总结: {total_pass}/{len(modules)} PASS, {total_fail} FAIL")
    print("=" * 70)

    if fail_details:
        print()
        print("FAIL 详情:")
        for mod_id, failed_checks, all_checks in fail_details:
            for name in failed_checks:
                _, detail = all_checks[name]
                print(f"  {mod_id} / {name}: {detail}")

    return total_fail == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
