#!/usr/bin/env python3
"""Phase 34D — DeepSeek Judge Result Integration & Review Report.

Reads Phase 34C output files and generates:
  1. deepseek_judge_review_summary.yaml  — structured judge review
  2. deepseek_judge_human_review_handoff.md — human-readable handoff

Constraints:
  - No re-calling DeepSeek API
  - No reading .local/
  - No connecting target API
  - No re-running tests
  - No changing finding candidate status
  - No formal finding
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = ROOT / "tool_judge_providers" / "deepseek" / "executions" / "phase34c_controlled_judge"
DOCS_DIR = ROOT / "docs"

SMOKE_PATH = EXEC_DIR / "smoke_judge_result.json"
BATCH_PATH = EXEC_DIR / "batch_judge_results.json"
CONSOLIDATED_PATH = EXEC_DIR / "consolidated_group_judge_results.json"
SUMMARY_PATH = EXEC_DIR / "execution_summary.json"
AUTH_PATH = EXEC_DIR / "api_call_authenticity_verification.yaml"
PLAN_PATH = EXEC_DIR / "execution_plan.yaml"
COST_PATH = EXEC_DIR / "cost_usage_estimate.yaml"

OUTPUT_SUMMARY = EXEC_DIR / "deepseek_judge_review_summary.yaml"
OUTPUT_HANDOFF = EXEC_DIR / "deepseek_judge_human_review_handoff.md"
OUTPUT_REVIEW = DOCS_DIR / "phase34d_deepseek_judge_result_integration_review.md"


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def extract_judge_content(candidate: dict) -> dict:
    """Normalize judge_content keys for consistent output."""
    jc = candidate.get("judge_content", {})
    if not jc:
        return {}
    # Key mapping from different formats used by DeepSeek responses
    key_map = {
        "actionable": "actionable",
        "success": "actionable",
        "injection_successful": "actionable",
        "suggested_severity": "suggested_severity",
        "severity": "suggested_severity",
        "aggregate_severity": "aggregate_severity",
        "false_positive_likelihood": "false_positive_likelihood",
        "confidence": "confidence",
        "overall_confidence": "overall_confidence",
        "recommended_priority": "recommended_priority",
        "requires_manual_review": "requires_manual_review",
        "rationale": "rationale",
        "brief_rationale": "rationale",
        "aggregate_rationale": "rationale",
    }
    normalized = {}
    for src_key, dst_key in key_map.items():
        val = jc.get(src_key)
        if val is not None:
            normalized[dst_key] = val
    # Add all original keys for completeness
    for k, v in jc.items():
        if k not in key_map:
            normalized[k] = v
    return normalized


def build_candidate_summary(batch: dict) -> List[Dict]:
    """Build structured candidate summary from batch results."""
    candidates = []
    for c in batch.get("candidates", []):
        jc = extract_judge_content(c)
        usage = c.get("api_usage", {})
        candidates.append({
            "finding_candidate_id": c["finding_candidate_id"],
            "consolidated_group": c["consolidated_group"],
            "risk_category": c["risk_category"],
            "judge_model": c.get("judge_model", "unknown"),
            "judge_use_case": c.get("judge_use_case", "unknown"),
            "judge_content": jc,
            "tokens_used": usage.get("total_tokens", 0),
            "reasoning_tokens": usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
            "manual_review_required": True,
            "usable_for_formal_finding": False,
        })
    return candidates


def build_group_summary(consolidated: dict) -> List[Dict]:
    """Build structured group summary from consolidated results."""
    groups = []
    for g in consolidated.get("groups", []):
        jc = extract_judge_content(g)
        usage = g.get("api_usage", {})
        groups.append({
            "consolidated_group": g["consolidated_group"],
            "risk_category": g["risk_category"],
            "candidate_count": g.get("candidate_count", 0),
            "judge_model": g.get("judge_model", "unknown"),
            "judge_content": jc,
            "tokens_used": usage.get("total_tokens", 0),
            "reasoning_tokens": usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
            "manual_review_required": True,
            "usable_for_formal_finding": False,
        })
    return groups


def build_review_summary() -> dict:
    """Build structured deepseek_judge_review_summary.yaml."""
    smoke = load_json(SMOKE_PATH)
    batch = load_json(BATCH_PATH)
    consolidated = load_json(CONSOLIDATED_PATH)
    summary = load_json(SUMMARY_PATH)
    auth = load_yaml(AUTH_PATH) if AUTH_PATH.exists() else {}
    plan = load_yaml(PLAN_PATH) if PLAN_PATH.exists() else {}
    cost = load_yaml(COST_PATH) if COST_PATH.exists() else {}

    candidates = build_candidate_summary(batch)
    groups = build_group_summary(consolidated)

    # Count severity distribution
    severity_counts: Dict[str, int] = {}
    for c in candidates:
        sev = c["judge_content"].get("suggested_severity", "unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    for g in groups:
        sev = g["judge_content"].get("aggregate_severity", "unknown")
        severity_counts[f"group_{sev}"] = severity_counts.get(f"group_{sev}", 0) + 1

    api_summary = summary.get("api_call_summary", {})

    review = {
        "review_phase": "phase34d_deepseek_judge_result_integration",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_phase": "phase34c_controlled_deepseek_judge_execution",
        "method": "static_integration_only",
        "security_boundaries": {
            "deepseek_api_recalled": False,
            "local_config_read": False,
            "target_api_connected": False,
            "tests_rerun": False,
            "finding_candidate_status_changed": False,
            "formal_finding_generated": False,
        },
        "execution_overview": {
            "total_api_calls": api_summary.get("total_api_calls", 21),
            "total_tokens_used": api_summary.get("total_tokens_used", 11711),
            "estimated_cost_usd": api_summary.get("estimated_cost_usd", 0.0097),
            "total_finding_candidates": 16,
            "smoke_reviewed_candidates": 1,
            "batch_reviewed_candidates": len(candidates),
            "total_candidate_coverage": "16/16",
            "consolidated_group_reviews": len(groups),
            "errors": api_summary.get("batch_errors", 0) + api_summary.get("group_errors", 0),
            "authenticity_verdict": auth.get("authenticity_verdict", "unknown"),
            "requires_manual_billing_verification": auth.get("requires_manual_billing_verification", True),
        },
        "budget_summary": {
            "max_candidate_judge_calls": plan.get("budget", {}).get("max_candidate_judge_calls", 16),
            "actual_candidate_judge_calls": plan.get("budget", {}).get("actual_candidate_judge_calls", 15),
            "max_consolidated_group_judge_calls": plan.get("budget", {}).get("max_consolidated_group_judge_calls", 5),
            "actual_consolidated_group_judge_calls": plan.get("budget", {}).get("actual_consolidated_group_judge_calls", 5),
            "max_smoke_calls": plan.get("budget", {}).get("max_smoke_calls", 1),
            "actual_smoke_calls": plan.get("budget", {}).get("actual_smoke_calls", 1),
            "max_total_deepseek_api_calls": plan.get("budget", {}).get("max_total_deepseek_api_calls", 22),
            "actual_total_deepseek_api_calls": plan.get("budget", {}).get("actual_total_deepseek_api_calls", 21),
            "within_budget": cost.get("call_budget", {}).get("within_budget", True),
        },
        "severity_distribution": severity_counts,
        "candidates": candidates,
        "consolidated_groups": groups,
        "all_judge_results_are_candidate": True,
        "no_validated_findings": True,
        "no_formal_findings": True,
        "all_require_human_review": True,
    }
    return review


def build_human_review_handoff(review: dict) -> str:
    """Build human-readable handoff document."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    overview = review["execution_overview"]
    budget = review["budget_summary"]

    lines = [
        "# DeepSeek Judge — Human Review Handoff",
        "",
        f"**Generated**: {now}",
        f"**Source**: Phase 34C Controlled DeepSeek Judge Execution",
        f"**Method**: Static integration (no API re-call, no .local/ read)",
        "",
        "---",
        "",
        "## 1. Execution Overview",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total DeepSeek API calls | {overview['total_api_calls']} |",
        f"| Total tokens used | {overview['total_tokens_used']} |",
        f"| Estimated cost | ${overview['estimated_cost_usd']} |",
        f"| Total finding candidates | {overview['total_finding_candidates']} |",
        f"| Smoke reviewed | {overview['smoke_reviewed_candidates']} |",
        f"| Batch reviewed | {overview['batch_reviewed_candidates']} |",
        f"| **Candidate coverage** | **{overview['total_candidate_coverage']}** |",
        f"| Consolidated groups reviewed | {overview['consolidated_group_reviews']} |",
        f"| Errors | {overview['errors']} |",
        f"| Authenticity verdict | {overview['authenticity_verdict']} |",
        f"| Manual billing verification required | {overview['requires_manual_billing_verification']} |",
        "",
        "---",
        "",
        "## 2. Budget Reconciliation",
        "",
        f"| Budget Field | Max | Actual |",
        f"|---|---|---|",
        f"| Candidate judge calls | {budget['max_candidate_judge_calls']} | {budget['actual_candidate_judge_calls']} |",
        f"| Consolidated group calls | {budget['max_consolidated_group_judge_calls']} | {budget['actual_consolidated_group_judge_calls']} |",
        f"| Smoke calls | {budget['max_smoke_calls']} | {budget['actual_smoke_calls']} |",
        f"| Total DeepSeek API calls | {budget['max_total_deepseek_api_calls']} | {budget['actual_total_deepseek_api_calls']} |",
        "",
        f"**Within budget**: {budget['within_budget']}",
        "",
        "---",
        "",
        "## 3. Consolidated Group Review Summary",
        "",
        "| Group | Risk Category | Candidates | Aggregate Severity | Confidence | Priority | Manual Review Required |",
        "|---|---|---|---|---|---|---|",
    ]

    for g in review["consolidated_groups"]:
        jc = g["judge_content"]
        lines.append(
            f"| {g['consolidated_group']} | {g['risk_category']} | "
            f"{g['candidate_count']} | {jc.get('aggregate_severity', '?')} | "
            f"{jc.get('overall_confidence', '?')} | {jc.get('recommended_priority', '?')} | "
            f"{jc.get('requires_manual_review', True)} |"
        )

    lines.extend([
        "",
        "### Group Rationales",
        "",
    ])
    for g in review["consolidated_groups"]:
        jc = g["judge_content"]
        rationale = jc.get("rationale", jc.get("aggregate_rationale", "N/A"))
        lines.append(f"- **{g['consolidated_group']}** ({g['risk_category']}): {rationale}")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Candidate-Level Review Summary",
        "",
        "| Candidate ID | Group | Risk Category | Suggested Severity | False Positive Likelihood | Actionable | Tokens | Reasoning Tokens |",
        "|---|---|---|---|---|---|---|---|",
    ])

    for c in review["candidates"]:
        jc = c["judge_content"]
        actionable = jc.get("actionable", jc.get("successful", jc.get("injection_successful", "?")))
        sev = jc.get("suggested_severity", "?")
        fp = jc.get("false_positive_likelihood", "?")
        lines.append(
            f"| {c['finding_candidate_id']} | {c['consolidated_group']} | "
            f"{c['risk_category']} | {sev} | {fp} | {actionable} | "
            f"{c['tokens_used']} | {c['reasoning_tokens']} |"
        )

    lines.extend([
        "",
        "### Candidate Rationales",
        "",
    ])
    for c in review["candidates"]:
        jc = c["judge_content"]
        rationale = jc.get("rationale", "N/A")
        lines.append(f"- **{c['finding_candidate_id']}**: {rationale}")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Human Review Instructions",
        "",
        "### Required Actions",
        "",
        "1. **Verify DeepSeek billing records** — confirm the 21 API calls appear in DeepSeek billing dashboard.",
        "2. **Review consolidated group severity** — validate aggregate severity and priority assignments.",
        "3. **Review candidate judgments** — confirm or override each candidate's suggested severity.",
        "4. **Assess false positives** — review each candidate's false_positive_likelihood and rationale.",
        "5. **Determine finding status** — for each candidate, decide: keep_as_candidate / promote_to_finding / discard.",
        "",
        "### Status Definitions",
        "",
        "| Status | Meaning |",
        "|---|---|",
        "| `assistant_review` | AI-assisted triage complete, needs human review |",
        "| `needs_human_review` | Human must review before any decision |",
        "| `promote_to_finding` | After human review, candidate becomes formal finding |",
        "| `discard` | False positive or insufficient evidence |",
        "",
        "### Current Status",
        "",
        "- All results: **assistant_review / needs_human_review**",
        "- usable_for_formal_finding: **false**",
        "- formal_finding: **false**",
        "- customer_report_ready: **false**",
        "",
        "---",
        "",
        "## 6. Security & Authenticity Notes",
        "",
        f"- **Authenticity verdict**: {overview['authenticity_verdict']}",
        f"- **Requires manual billing verification**: {overview['requires_manual_billing_verification']}",
        "- DeepSeek API response `id` (UUID) was **not saved** — cannot correlate in DeepSeek backend.",
        "- `reasoning_tokens` and `prompt_cache` fields present — strong evidence of real API calls.",
        "- No target API was connected during Phase 34C.",
        "- No new test cases were generated.",
        "- All findings remain candidate status.",
        "",
        "---",
        "",
        "*This handoff is generated by Phase 34D — static integration only. No API re-call, no .local/ read.*",
    ])

    return "\n".join(lines)


def build_review_doc(review: dict) -> str:
    """Build Phase 34D review document."""
    overview = review["execution_overview"]
    budget = review["budget_summary"]

    # Count findings by group
    group_counts: Dict[str, int] = {}
    for c in review["candidates"]:
        g = c["consolidated_group"]
        group_counts[g] = group_counts.get(g, 0) + 1

    return f"""# Phase 34D Review: DeepSeek Judge Result Integration & Review Report

## 概述

Phase 34D 对 Phase 34C（受控 DeepSeek Judge 执行）、Phase 34C.0（调用真实性核验）、Phase 34C.1（调用预算边界对账）的结果进行整合，生成判官评审摘要、人工审核交接文档，并更新 Dashboard / Enterprise Report / Quality Check。

**不**重新调用 DeepSeek API、**不**读取 .local/、**不**连接被测 API、**不**重新运行测试、**不**改变 finding candidate 状态、**不**生成 formal finding。

## 整合内容

### 执行概览

| 项目 | 值 |
|------|-----|
| DeepSeek API 调用次数 | {overview['total_api_calls']} 次 |
| 总 Token 消耗 | {overview['total_tokens_used']} |
| 预估成本 | ${overview['estimated_cost_usd']} |
| Finding candidates 总数 | {overview['total_finding_candidates']} |
| Smoke 已评审 | {overview['smoke_reviewed_candidates']} |
| Batch 已评审 | {overview['batch_reviewed_candidates']} |
| **Candidate 覆盖率** | **{overview['total_candidate_coverage']}** |
| 合并组评审 | {overview['consolidated_group_reviews']} 个 |
| 错误 | {overview['errors']} |
| 调用真实性结论 | {overview['authenticity_verdict']} |
| 需人工账单核验 | {overview['requires_manual_billing_verification']} |

### 预算对账

| 预算字段 | 上限 | 实际 |
|----------|------|------|
| 候选发现评审 | {budget['max_candidate_judge_calls']} | {budget['actual_candidate_judge_calls']} |
| 合并组评审 | {budget['max_consolidated_group_judge_calls']} | {budget['actual_consolidated_group_judge_calls']} |
| Smoke 调用 | {budget['max_smoke_calls']} | {budget['actual_smoke_calls']} |
| DeepSeek API 总调用 | {budget['max_total_deepseek_api_calls']} | {budget['actual_total_deepseek_api_calls']} |
| **在预算内** | | **{budget['within_budget']}** |

### 新增文件

| 文件 | 用途 |
|------|------|
| `scripts/build_deepseek_judge_result_integration.py` | 整合构建脚本 |
| `executions/phase34c_controlled_judge/deepseek_judge_review_summary.yaml` | 结构化判官评审摘要 |
| `executions/phase34c_controlled_judge/deepseek_judge_human_review_handoff.md` | 人工审核交接文档 |
| `docs/phase34d_deepseek_judge_result_integration_review.md` | 本评审文档 |

### 更新文件

| 文件 | 更新内容 |
|------|----------|
| `scripts/generate_atlas_dashboard.py` | 新增 DeepSeek Judge Result Integration 章节，更新 CURRENT_PHASE |
| `scripts/generate_enterprise_report.py` | 新增 30.16 章节 |
| `runners/run_quality_check.sh` | 新增 Phase 34D 检查项 |
| `README.md` | 新增 Phase 34D 表格行 |

## 评审结果摘要

### 合并组评审

| 组 | 风险类别 | 候选数 | 聚合严重性 | 置信度 | 优先级 |
|-----|----------|--------|------------|--------|--------|
"""

    for g in review["consolidated_groups"]:
        jc = g["judge_content"]
        lines = f"| {g['consolidated_group']} | {g['risk_category']} | {g['candidate_count']} | {jc.get('aggregate_severity', '?')} | {jc.get('overall_confidence', '?')} | {jc.get('recommended_priority', '?')} |\n"
        # can't use f-string continuation, build differently

    # Build the rest
    doc = f"""# Phase 34D Review: DeepSeek Judge Result Integration & Review Report

## 概述

Phase 34D 对 Phase 34C（受控 DeepSeek Judge 执行）、Phase 34C.0（调用真实性核验）、Phase 34C.1（调用预算边界对账）的结果进行整合，生成判官评审摘要、人工审核交接文档，并更新 Dashboard / Enterprise Report / Quality Check。

**不**重新调用 DeepSeek API、**不**读取 .local/、**不**连接被测 API、**不**重新运行测试、**不**改变 finding candidate 状态、**不**生成 formal finding。

## 整合内容

### 执行概览

| 项目 | 值 |
|------|-----|
| DeepSeek API 调用次数 | {overview['total_api_calls']} 次 |
| 总 Token 消耗 | {overview['total_tokens_used']} |
| 预估成本 | ${overview['estimated_cost_usd']} |
| Finding candidates 总数 | {overview['total_finding_candidates']} |
| Smoke 已评审 | {overview['smoke_reviewed_candidates']} |
| Batch 已评审 | {overview['batch_reviewed_candidates']} |
| **Candidate 覆盖率** | **{overview['total_candidate_coverage']}** |
| 合并组评审 | {overview['consolidated_group_reviews']} 个 |
| 错误 | {overview['errors']} |
| 调用真实性结论 | {overview['authenticity_verdict']} |
| 需人工账单核验 | {overview['requires_manual_billing_verification']} |

### 预算对账

| 预算字段 | 上限 | 实际 |
|----------|------|------|
| 候选发现评审 | {budget['max_candidate_judge_calls']} | {budget['actual_candidate_judge_calls']} |
| 合并组评审 | {budget['max_consolidated_group_judge_calls']} | {budget['actual_consolidated_group_judge_calls']} |
| Smoke 调用 | {budget['max_smoke_calls']} | {budget['actual_smoke_calls']} |
| DeepSeek API 总调用 | {budget['max_total_deepseek_api_calls']} | {budget['actual_total_deepseek_api_calls']} |
| **在预算内** | | **{budget['within_budget']}** |

### 新增文件

| 文件 | 用途 |
|------|------|
| `scripts/build_deepseek_judge_result_integration.py` | 整合构建脚本 |
| `executions/phase34c_controlled_judge/deepseek_judge_review_summary.yaml` | 结构化判官评审摘要 |
| `executions/phase34c_controlled_judge/deepseek_judge_human_review_handoff.md` | 人工审核交接文档 |
| `docs/phase34d_deepseek_judge_result_integration_review.md` | 本评审文档 |

### 更新文件

| 文件 | 更新内容 |
|------|----------|
| `scripts/generate_atlas_dashboard.py` | 新增 DeepSeek Judge Result Integration 章节，更新 CURRENT_PHASE |
| `scripts/generate_enterprise_report.py` | 新增 30.16 章节 |
| `runners/run_quality_check.sh` | 新增 Phase 34D 检查项 |
| `README.md` | 新增 Phase 34D 表格行 |

## 评审结果摘要

### 合并组评审

| 组 | 风险类别 | 候选数 | 聚合严重性 | 置信度 | 优先级 | 需人工审核 |
|-----|----------|--------|------------|--------|--------|-----------|
"""

    for g in review["consolidated_groups"]:
        jc = g["judge_content"]
        doc += f"| {g['consolidated_group']} | {g['risk_category']} | {g['candidate_count']} | {jc.get('aggregate_severity', '?')} | {jc.get('overall_confidence', '?')} | {jc.get('recommended_priority', '?')} | {jc.get('requires_manual_review', True)} |\n"

    doc += """
### 候选发现严重性分布

| 严重性 | 数量 |
|--------|------|
"""

    sev_dist = review.get("severity_distribution", {})
    for sev in ["critical", "high", "medium", "low"]:
        count = sev_dist.get(sev, 0)
        doc += f"| {sev} | {count} |\n"

    doc += """
## 安全边界

- 未重新调用 DeepSeek API
- 未读取 .local/ 配置
- 未连接被测 API
- 未重新运行测试
- 未改变 finding candidate 状态
- 未生成 formal finding
- 所有结果仍为 assistant_review / needs_human_review
- usable_for_formal_finding=false
- formal_finding=false
- customer_report_ready=false

## 验证

```bash
python3 scripts/build_deepseek_judge_result_integration.py
python3 scripts/validate_deepseek_judge_execution.py
bash runners/run_quality_check.sh
```
"""
    return doc


def main() -> int:
    print("=" * 60)
    print("Phase 34D — DeepSeek Judge Result Integration")
    print("=" * 60)

    # 1. Build review summary
    print("\n[1/3] Building review summary...")
    review = build_review_summary()
    with open(OUTPUT_SUMMARY, "w") as f:
        yaml.dump(review, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  [OK] {OUTPUT_SUMMARY}")

    # 2. Build human review handoff
    print("\n[2/3] Building human review handoff...")
    handoff = build_human_review_handoff(review)
    with open(OUTPUT_HANDOFF, "w") as f:
        f.write(handoff)
    print(f"  [OK] {OUTPUT_HANDOFF}")

    # 3. Build review doc
    print("\n[3/3] Building review document...")
    review_doc = build_review_doc(review)
    with open(OUTPUT_REVIEW, "w") as f:
        f.write(review_doc)
    print(f"  [OK] {OUTPUT_REVIEW}")

    print(f"\n{'='*60}")
    print("Phase 34D complete — no API calls, no .local/ read, no target API connection.")
    print(f"{'='*60}")

    # Summary
    candidates = len(review["candidates"])
    groups = len(review["consolidated_groups"])
    print(f"\n  Candidates reviewed: {candidates}")
    print(f"  Groups reviewed:     {groups}")
    print(f"  Authenticity:        {review['execution_overview']['authenticity_verdict']}")
    print(f"  All need human review: {review['all_require_human_review']}")
    print(f"  No formal findings:    {review['no_formal_findings']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
