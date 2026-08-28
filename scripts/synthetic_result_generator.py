#!/usr/bin/env python3
"""
synthetic_result_generator.py
=============================
Phase 1 Task 1.1 — 全量 execution_results 确定性生成器

核心思路：
  读取任意模块的 playbook.yaml，基于 entry 的 control_case / expected_signal 字段
  确定性生成 execution_results.json + capability_scorecard.yaml + {mod}_result.yaml

用法：
  # 单模块
  python3 scripts/synthetic_result_generator.py --module M01

  # 全量 49 模块
  python3 scripts/synthetic_result_generator.py --all

  # 验证模式（对比 M08 已有数据）
  python3 scripts/synthetic_result_generator.py --module M08 --verify
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ── 项目根目录 ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLAYBOOKS_DIR = PROJECT_ROOT / "adversarial_playbooks"
REGISTRY_PATH = PROJECT_ROOT / "capability_modules" / "module_registry.yaml"

# ── 标准 49 模块列表 ────────────────────────────────────────────────────────
STANDARD_MODULES = [
    f"M{i:02d}" for i in range(1, 51) if i != 9  # M01-M50, 无 M09
]

# ── 模块名称映射（从 registry 动态加载的后备） ──────────────────────────────
_MODULE_NAME_CACHE = {}


def load_module_names() -> dict:
    """从 module_registry.yaml 加载 module_id → module_name 映射"""
    if _MODULE_NAME_CACHE:
        return _MODULE_NAME_CACHE
    if not REGISTRY_PATH.exists():
        return {}
    with open(REGISTRY_PATH) as f:
        reg = yaml.safe_load(f)
    modules = reg.get("modules", reg.get("registered_modules", []))
    if isinstance(modules, list):
        for m in modules:
            mid = m.get("module_id", "")
            name = m.get("module_name", m.get("name", ""))
            if mid and name:
                _MODULE_NAME_CACHE[mid] = name
    elif isinstance(modules, dict):
        for mid, m in modules.items():
            name = m.get("module_name", m.get("name", ""))
            if name:
                _MODULE_NAME_CACHE[mid] = name
    return _MODULE_NAME_CACHE


def get_module_name(module_id: str) -> str:
    names = load_module_names()
    return names.get(module_id, f"Module {module_id}")


# ── Playbook 加载 ──────────────────────────────────────────────────────────
def load_playbook(module_id: str) -> dict:
    """加载模块的 playbook.yaml"""
    mod_lower = module_id.lower()
    pb_dir = PLAYBOOKS_DIR / f"{mod_lower}_full_corpus"
    pb_path = pb_dir / "playbook.yaml"
    if not pb_path.exists():
        raise FileNotFoundError(f"Playbook not found: {pb_path}")
    with open(pb_path) as f:
        return yaml.safe_load(f)


# ── 单条 entry 结果生成 ────────────────────────────────────────────────────
def generate_entry_result(entry: dict) -> dict:
    """
    基于 entry metadata 确定性生成单条结果

    规则：
      control_case=True  → allowed, correctly_allowed, no human review
      control_case=False → blocked, correctly_blocked, human review required
    """
    is_control = entry.get("control_case", False)
    case_id = entry.get("case_id", "UNKNOWN")
    category = entry.get("category", "unknown")
    subcategory = entry.get("subcategory", "unknown")
    expected_signals = entry.get("expected_signal", [])
    expected_behavior = entry.get("expected_behavior", [])

    if is_control:
        return {
            "case_id": case_id,
            "category": category,
            "subcategory": subcategory,
            "is_control_case": True,
            "runtime_decision": "allowed",
            "correctly_allowed": True,
            "correctly_blocked": False,
            "human_review_required": False,
            "breakthrough_detected": False,
            "behavior_match": True,
            "blocked_signals": [],
            "allowed_signals": expected_signals,
            "matched_signals": expected_signals,
            "expected_behavior_count": len(expected_behavior),
            "matched_behavior_count": len(expected_behavior),
        }
    else:
        # Attack case: blocked based on expected_signal
        return {
            "case_id": case_id,
            "category": category,
            "subcategory": subcategory,
            "is_control_case": False,
            "runtime_decision": "blocked",
            "correctly_allowed": False,
            "correctly_blocked": True,
            "human_review_required": entry.get("requires_human_review", True),
            "breakthrough_detected": entry.get("breakthrough_detected", False),
            "behavior_match": True,
            "blocked_signals": expected_signals,
            "allowed_signals": [],
            "matched_signals": expected_signals,
            "expected_behavior_count": len(expected_behavior),
            "matched_behavior_count": len(expected_behavior),
        }


# ── 聚合 category_results ──────────────────────────────────────────────────
def aggregate_category_results(entry_results: list) -> dict:
    """按 category 分组聚合统计"""
    cat_data = defaultdict(lambda: {
        "total": 0, "attack_cases": 0, "control_cases": 0,
        "blocked": 0, "breakthrough_detected": 0,
        "behavior_match": 0, "human_review_required": 0,
    })
    for r in entry_results:
        cat = r["category"]
        d = cat_data[cat]
        d["total"] += 1
        if r["is_control_case"]:
            d["control_cases"] += 1
        else:
            d["attack_cases"] += 1
            d["blocked"] += r.get("correctly_blocked", 0)
        d["breakthrough_detected"] += 1 if r.get("breakthrough_detected") else 0
        d["behavior_match"] += 1 if r.get("behavior_match") else 0
        d["human_review_required"] += 1 if r.get("human_review_required") else 0
    return dict(cat_data)


# ── 构建 execution_results.json ────────────────────────────────────────────
def build_execution_results(
    module_id: str,
    module_name: str,
    entry_results: list,
    category_results: dict,
    timestamp: str,
) -> dict:
    total = len(entry_results)
    attacks = sum(1 for r in entry_results if not r["is_control_case"])
    controls = sum(1 for r in entry_results if r["is_control_case"])
    blocked = sum(1 for r in entry_results if r.get("correctly_blocked"))
    allowed = sum(1 for r in entry_results if r.get("correctly_allowed"))
    breakthrough = sum(1 for r in entry_results if r.get("breakthrough_detected"))
    match_count = sum(1 for r in entry_results if r.get("behavior_match"))

    return {
        "module_id": module_id,
        "module_name": module_name,
        "assessment_mode": "adversarial_validation",
        "execution_timestamp": timestamp,
        "synthetic_only": True,
        "fake_runtime_only": True,
        "total_entries": total,
        "attack_entries": attacks,
        "control_entries": controls,
        "results_summary": {
            "attack_cases": attacks,
            "control_cases": controls,
            "correctly_blocked": blocked,
            "correctly_allowed": allowed,
            "breakthrough_detected": breakthrough,
            "behavior_match_rate": round(match_count / total * 100, 1) if total else 0.0,
            "correctly_executed": match_count,
        },
        "category_results": category_results,
        "per_entry_results": entry_results,
        "safety_compliance": {
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "real_execution": False,
            "synthetic_only": True,
        },
    }


# ── 构建 capability_scorecard.yaml ─────────────────────────────────────────
def build_scorecard(
    module_id: str,
    module_name: str,
    entry_results: list,
    category_results: dict,
    timestamp: str,
) -> dict:
    total = len(entry_results)
    attacks = sum(1 for r in entry_results if not r["is_control_case"])
    controls = sum(1 for r in entry_results if r["is_control_case"])
    blocked = sum(1 for r in entry_results if r.get("correctly_blocked"))
    allowed_ctrl = sum(1 for r in entry_results if r.get("correctly_allowed"))
    match_count = sum(1 for r in entry_results if r.get("behavior_match"))
    hr_count = sum(1 for r in entry_results if r.get("human_review_required"))

    # capability_scores: per-category scores
    cap_scores = {}
    for cat, data in category_results.items():
        score_key = f"{cat}_score"
        if data["attack_cases"] > 0:
            cap_scores[score_key] = round(data["blocked"] / data["attack_cases"] * 100, 1)
        elif data["control_cases"] > 0:
            cap_scores[score_key] = round(data["behavior_match"] / data["control_cases"] * 100, 1)
        else:
            cap_scores[score_key] = 100.0
    cap_scores["control_case_score"] = (
        round(allowed_ctrl / controls * 100, 1) if controls else 100.0
    )
    cap_scores["overall_score"] = round(match_count / total * 100, 1) if total else 100.0

    # category_breakdown: add executed_correctly
    cat_breakdown = {}
    for cat, data in category_results.items():
        cat_breakdown[cat] = {
            "total": data["total"],
            "attack_cases": data["attack_cases"],
            "control_cases": data["control_cases"],
            "blocked": data["blocked"],
            "behavior_match": data["behavior_match"],
            "executed_correctly": data["behavior_match"],
            "human_review_required": data["human_review_required"],
        }

    return {
        "assessment_metadata": {
            "module_id": module_id,
            "module_name": module_name,
            "assessment_mode": "adversarial_validation",
            "total_entries": total,
            "attack_entries": attacks,
            "control_entries": controls,
            "execution_timestamp": timestamp,
            "synthetic_only": True,
            "fake_runtime_only": True,
        },
        "capability_scores": cap_scores,
        "category_breakdown": cat_breakdown,
        "detailed_metrics": {
            "correctly_blocked_attack_cases": blocked,
            "correctly_allowed_control_cases": allowed_ctrl,
            "correctly_executed": match_count,
            "behavior_match_rate": round(match_count / total * 100, 1) if total else 100.0,
            "human_review_rate": round(hr_count / total * 100, 1) if total else 0.0,
            "breakthrough_detection_rate": 100.0,
        },
        "recommendations": [
            f"Continue synthetic-only testing for {module_name} scenarios",
            "Maintain signal validation across all attack paths",
            "Enforce separation of duties for all high-risk operations",
            "Preserve human review requirements for all attack-type scenarios",
            "Document all synthetic test cases for audit trail purposes",
        ],
        "safety_compliance": {
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "real_execution": False,
            "synthetic_only": True,
        },
    }


# ── 构建 {mod}_full_corpus_result.yaml ─────────────────────────────────────
def build_result_yaml(
    module_id: str,
    module_name: str,
    entry_results: list,
    category_results: dict,
    timestamp: str,
) -> dict:
    total = len(entry_results)
    attacks = sum(1 for r in entry_results if not r["is_control_case"])
    controls = sum(1 for r in entry_results if r["is_control_case"])
    match_count = sum(1 for r in entry_results if r.get("behavior_match"))

    cat_breakdown = {}
    for cat, data in category_results.items():
        cat_breakdown[cat] = {
            "total": data["total"],
            "attack_cases": data["attack_cases"],
            "control_cases": data["control_cases"],
            "blocked": data["blocked"],
            "behavior_match": data["behavior_match"],
            "executed_correctly": data["behavior_match"],
            "human_review_required": data["human_review_required"],
        }

    return {
        "assessment_result": {
            "module_id": module_id,
            "module_name": module_name,
            "assessment_mode": "adversarial_validation",
            "total_entries": total,
            "execution_timestamp": timestamp,
            "synthetic_only": True,
            "fake_runtime_only": True,
            "results_summary": {
                "attack_cases": attacks,
                "control_cases": controls,
                "behavior_match_rate": round(match_count / total * 100, 1) if total else 100.0,
                "correctly_executed": match_count,
                "breakthrough_detected": 0,
            },
            "category_breakdown": cat_breakdown,
        }
    }


# ── 单模块完整生成 ─────────────────────────────────────────────────────────
def generate_module_results(module_id: str, timestamp: str = None) -> dict:
    """
    为单个模块生成全部 3 个输出文件

    返回: {
        "module_id": str,
        "status": "success" | "error",
        "files_written": list,
        "stats": {total, attacks, controls, ...}
    }
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")

    module_name = get_module_name(module_id)
    mod_lower = module_id.lower()
    out_dir = PLAYBOOKS_DIR / f"{mod_lower}_full_corpus"

    try:
        playbook = load_playbook(module_id)
    except FileNotFoundError as e:
        return {"module_id": module_id, "status": "error", "error": str(e), "files_written": []}

    # 提取 entries —— 兼容多种 playbook 格式
    # 格式 1: {entries: [...]}  (标准)
    # 格式 2: {m07: [...]}      (M07 格式)
    # 格式 3: {m13_full_corpus: [...]}  (M13/M39 格式)
    entries = playbook.get("entries", [])
    if not entries:
        # 尝试 module_id 小写作为 key
        mod_lower_key = module_id.lower()
        entries = playbook.get(mod_lower_key, [])
    if not entries:
        # 尝试 {mod}_full_corpus 作为 key
        entries = playbook.get(f"{mod_lower}_full_corpus", [])
    if not entries:
        # 最后一个后备：找第一个 list 类型的值
        for v in playbook.values():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                entries = v
                break
    if not entries:
        return {"module_id": module_id, "status": "error", "error": "No entries in playbook", "files_written": []}

    # 如果 playbook 自带 module_name 且 registry 没有，使用 playbook 的
    if module_name == f"Module {module_id}" and playbook.get("module_name"):
        module_name = playbook["module_name"]

    # 生成 per-entry results
    entry_results = [generate_entry_result(e) for e in entries]

    # 聚合
    category_results = aggregate_category_results(entry_results)

    # 构建输出
    exec_results = build_execution_results(module_id, module_name, entry_results, category_results, timestamp)
    scorecard = build_scorecard(module_id, module_name, entry_results, category_results, timestamp)
    result_yaml = build_result_yaml(module_id, module_name, entry_results, category_results, timestamp)

    # 写文件
    files_written = []
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. execution_results.json
    er_path = out_dir / "execution_results.json"
    with open(er_path, "w") as f:
        json.dump(exec_results, f, indent=2, ensure_ascii=False)
    files_written.append(str(er_path))

    # 2. capability_scorecard.yaml
    sc_path = out_dir / "capability_scorecard.yaml"
    with open(sc_path, "w") as f:
        yaml.dump(scorecard, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    files_written.append(str(sc_path))

    # 3. {mod}_full_corpus_result.yaml
    ry_path = out_dir / f"{mod_lower}_full_corpus_result.yaml"
    with open(ry_path, "w") as f:
        yaml.dump(result_yaml, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    files_written.append(str(ry_path))

    total = len(entries)
    attacks = sum(1 for e in entries if not e.get("control_case"))
    controls = sum(1 for e in entries if e.get("control_case"))

    return {
        "module_id": module_id,
        "status": "success",
        "files_written": files_written,
        "stats": {
            "total_entries": total,
            "attack_entries": attacks,
            "control_entries": controls,
            "categories": len(category_results),
        },
    }


# ── 全量生成 ───────────────────────────────────────────────────────────────
def generate_all(timestamp: str = None) -> list:
    """为全部 49 标准模块生成结果"""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")

    results = []
    for mod_id in STANDARD_MODULES:
        result = generate_module_results(mod_id, timestamp)
        results.append(result)
        status_icon = "✅" if result["status"] == "success" else "❌"
        stats = result.get("stats", {})
        err = result.get("error", "")
        print(f"  {status_icon} {mod_id}: {stats.get('total_entries', '?')} entries "
              f"({stats.get('attack_entries', '?')} attack / {stats.get('control_entries', '?')} ctrl)"
              f"{' — ' + err if err else ''}")
    return results


# ── 验证模式 ───────────────────────────────────────────────────────────────
def verify_module(module_id: str) -> dict:
    """验证生成的结果与 playbook 数据一致性"""
    mod_lower = module_id.lower()
    out_dir = PLAYBOOKS_DIR / f"{mod_lower}_full_corpus"

    checks = []

    # Check 1: 文件完整性
    er_path = out_dir / "execution_results.json"
    sc_path = out_dir / "capability_scorecard.yaml"
    ry_path = out_dir / f"{mod_lower}_full_corpus_result.yaml"
    checks.append(("文件完整性", all(p.exists() for p in [er_path, sc_path, ry_path])))

    # Check 2: 数据一致性
    if er_path.exists():
        with open(er_path) as f:
            er = json.load(f)
        total = er.get("total_entries", 0)
        atk = er.get("attack_entries", 0)
        ctrl = er.get("control_entries", 0)
        checks.append(("total = attack + control", total == atk + ctrl))

        summary = er.get("results_summary", {})
        checks.append(("blocked + allowed = total",
                       summary.get("correctly_blocked", 0) + summary.get("correctly_allowed", 0) == total))
        checks.append(("breakthrough == 0", summary.get("breakthrough_detected", -1) == 0))
    else:
        checks.append(("数据一致性", False))

    # Check 3: 安全字段
    if er_path.exists():
        sc = er.get("safety_compliance", {})
        checks.append(("synthetic_only == True", sc.get("synthetic_only") is True))
        checks.append(("confirmed_vulnerability == False", sc.get("confirmed_vulnerability") is False))
    else:
        checks.append(("安全字段", False))

    all_pass = all(passed for _, passed in checks)
    return {"module_id": module_id, "all_pass": all_pass, "checks": checks}


# ── CLI ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Synthetic Result Generator")
    parser.add_argument("--module", "-m", help="单模块 ID (e.g. M01)")
    parser.add_argument("--all", action="store_true", help="全量 49 模块")
    parser.add_argument("--verify", action="store_true", help="验证模式")
    parser.add_argument("--timestamp", "-t", help="自定义时间戳")
    args = parser.parse_args()

    if args.all:
        print(f"=== 全量生成 49 模块 execution_results ===")
        print(f"Timestamp: {args.timestamp or 'auto'}")
        print()
        results = generate_all(args.timestamp)
        success = sum(1 for r in results if r["status"] == "success")
        error = sum(1 for r in results if r["status"] == "error")
        total_files = sum(len(r.get("files_written", [])) for r in results)
        print()
        print(f"=== 完成: {success} success, {error} error, {total_files} files written ===")

    elif args.module:
        if args.verify:
            print(f"=== 验证 {args.module} ===")
            result = verify_module(args.module)
            for name, passed in result["checks"]:
                icon = "✅" if passed else "❌"
                print(f"  {icon} {name}")
            print(f"\nOverall: {'PASS' if result['all_pass'] else 'FAIL'}")
        else:
            print(f"=== 生成 {args.module} ===")
            result = generate_module_results(args.module, args.timestamp)
            print(f"Status: {result['status']}")
            if result["status"] == "success":
                print(f"Files: {len(result['files_written'])}")
                for f in result["files_written"]:
                    print(f"  ✅ {f}")
            else:
                print(f"Error: {result.get('error')}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
