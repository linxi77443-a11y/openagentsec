#!/usr/bin/env python3
"""
M03 RAG Boundary Exposure — Offline Capability Review Generator
Phase 35H.1: Offline Review Calibration

Reads M03 sample_module_input.yaml, applies static review logic based on
review_output_schema.yaml, and generates:
  1. review_output.yaml        — structured YAML output
  2. capability_review.md      — human-readable Chinese review report

This is an OFFLINE STATIC DERIVATION tool. It does NOT:
  - Connect any API
  - Run promptfoo eval
  - Add test cases
  - Generate formal finding
  - Confirm real-world vulnerability

Usage:
    python3 scripts/generate_m03_offline_review.py
"""

import os
import sys
import yaml
from datetime import datetime, timezone, timedelta

M03_DIR = "capability_modules/implementations/M03_rag_boundary_exposure"
RESULTS_DIR = "capability_modules/results"

TZ_EAST8 = timezone(timedelta(hours=8))


def load_input():
    path = f"{M03_DIR}/sample_module_input.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)


def derive_review(inp):
    """
    Static review derivation based on input fields.
    No API calls, no promptfoo, no network.

    Calibration notes (Phase 35H.1):
      - All exposure fields use _indicated suffix (not confirmed)
      - review_confidence is scoped to candidate_description_only
      - Mapping values distinguish "线索" from "确认证据"
      - Control gaps and assessment limitations are separated
    """
    possible_raw = inp.get("possible_raw_kb_exposure", False)
    possible_chunk = inp.get("possible_source_chunk_exposure", False)
    possible_sensitive = inp.get("possible_sensitive_business_data", False)
    retrieval_avail = inp.get("retrieval_trace_available", False)

    # ── Risk signals ──────────────────────────────────────────
    risk_signals = []
    if possible_raw:
        risk_signals.append("possible_raw_kb_content_unfiltered")
    if possible_chunk:
        risk_signals.append("possible_retrieval_context_leaked")
    risk_signals.append("possible_no_summarization_applied")

    # ── Review status & confidence ─────────────────────────────
    # Offline static derivation — confidence is scoped
    if possible_raw or possible_chunk:
        review_status = "needs_human_review"
        review_confidence = "medium"
    elif possible_sensitive:
        review_status = "needs_human_review"
        review_confidence = "medium"
    else:
        review_status = "assistant_review"
        review_confidence = "low"

    # ── Calibrated mapping logic ───────────────────────────────
    # M19: only recommend when business data is confirmed (not just indicated)
    mapping_M19 = "deferred_until_business_data_confirmed"
    # M21: partial —线索可用但缺少复测证据
    mapping_M21 = "partial_available" if (possible_raw or possible_chunk) else "not_available"
    # M22: defer until human review confirms business impact
    mapping_M22 = "deferred_until_human_review"

    # ── Control gaps (applications-side) ───────────────────────
    control_gaps = []
    if possible_raw:
        control_gaps.append("可能缺少检索结果安全过滤")
        control_gaps.append("可能缺少输出摘要加工")
    if possible_chunk:
        control_gaps.append("可能缺少 source chunk 裁剪或脱敏")
    control_gaps.append("可能缺少 RAG 输出安全断言")

    # ── Assessment limitations (evaluation-side) ───────────────
    assessment_limitations = [
        "当前为离线静态推导",
        "未执行授权 API 复测",
        "未运行 promptfoo eval",
        "缺少 retrieval trace",
        "缺少完整原始请求/响应证据",
        "未确认是否涉及真实业务敏感数据",
    ]

    review = {
        # Identity
        "review_id": f"M03-REVIEW-{datetime.now(TZ_EAST8).strftime('%Y%m%d-%H%M%S')}",
        "module_id": "M03",
        "candidate_id": inp.get("candidate_id", ""),
        "reviewer": "assistant",
        "review_timestamp": datetime.now(TZ_EAST8).strftime("%Y-%m-%dT%H:%M:%S+08:00"),

        # Mode & scope
        "validation_mode": "offline_static_derivation",
        "evidence_strength": "candidate_description_only",
        "confidence_scope": "based_on_candidate_description_only",
        "retest_executed": False,
        "api_connected": False,
        "promptfoo_eval_executed": False,

        # Status
        "review_status": review_status,
        "review_confidence": review_confidence,
        "human_review_required": True,
        "formal_finding_allowed": False,

        # RAG boundary assessment — calibrated wording
        "raw_kb_content_exposure_indicated": possible_raw,
        "raw_kb_exposure_summary": "候选证据提示系统可能直接输出了原始知识库文档全文，未进行摘要或安全过滤（需人工复测确认）" if possible_raw else "未观察到原始知识库内容暴露线索",
        "source_chunk_exposure_indicated": possible_chunk,
        "source_chunk_exposure_summary": "候选证据提示检索上下文（source chunk）可能原样返回，未裁剪或脱敏（需人工复测确认）" if possible_chunk else "未观察到检索片段暴露线索",
        "exposure_confirmation_level": "candidate_indicated_only",

        # Legacy compatibility fields (kept but annotated as indicative)
        "raw_kb_content_exposed": possible_raw,
        "source_chunk_exposed": possible_chunk,
        "metadata_exposed": False,
        "metadata_exposure_summary": "需人工复核确认是否包含文档 ID、检索评分等元数据",
        "sensitive_business_data_involved": possible_sensitive,

        "risk_signals": risk_signals,

        # Evidence
        "evidence_reference": inp.get("source_evidence_reference", ""),
        "evidence_type": "observed_output",

        # Downstream mapping — calibrated
        "mapping_to_M19": mapping_M19,
        "mapping_to_M21": mapping_M21,
        "mapping_to_M22": mapping_M22,

        # Control gaps (application-side)
        "control_gaps": control_gaps,

        # Assessment limitations (evaluation-side)
        "assessment_limitations": assessment_limitations,

        # Legacy capability_gaps field (kept for compatibility)
        "capability_gaps": control_gaps + [f"[评估限制] {lim}" for lim in assessment_limitations],

        "recommendation": (
            "1. 在 RAG 输出管道中增加安全过滤层，检测并阻止原始知识库内容的直接输出\n"
            "2. 对检索结果进行摘要加工，确保输出为加工后的回答而非原始内容\n"
            "3. 建立 RAG 输出安全断言机制，自动检测泄露信号\n"
            "4. 对检索上下文进行裁剪和脱敏，移除系统元数据\n"
            "5. 执行授权 API 复测，确认候选证据是否可复现\n"
            "6. 补充 retrieval trace，确认检索链路完整性"
        ),
    }
    return review


def write_yaml(review, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(review, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  → {path}")


def write_markdown(review, inp, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    status_zh = {
        "assistant_review": "AI 辅助评审完成，待人工确认",
        "needs_human_review": "标记为需要人工复核",
        "inconclusive": "无法确定结论",
        "capability_gap": "确认存在能力缺失（非安全漏洞）",
    }
    risk_labels = {
        "possible_raw_kb_content_unfiltered": "原始知识库内容可能未过滤",
        "possible_retrieval_context_leaked": "检索上下文可能泄露",
        "possible_no_summarization_applied": "可能未应用摘要加工",
    }

    # Use calibrated indicative fields
    exposed_indicated = "候选证据提示存在" if review["raw_kb_content_exposure_indicated"] else "未观察到线索"
    chunk_indicated = "候选证据提示存在" if review["source_chunk_exposure_indicated"] else "未观察到线索"
    sensitive_zh = "候选证据提示涉及" if review["sensitive_business_data_involved"] else "未观察到线索"

    risk_rows = ""
    for signal in review["risk_signals"]:
        label = risk_labels.get(signal, signal)
        risk_rows += f"| {label} | 候选证据提示存在 | 需人工复测确认 |\n"

    control_rows = ""
    for i, gap in enumerate(review["control_gaps"], 1):
        control_rows += f"{i}. **{gap}**\n"

    limitation_rows = ""
    for i, lim in enumerate(review["assessment_limitations"], 1):
        limitation_rows += f"{i}. {lim}\n"

    md = f"""# M03 RAG Boundary Exposure — Capability Review (Offline)

## 模块信息

| 字段 | 值 |
|---|---|
| module_id | M03 |
| module_name | RAG Boundary Exposure |
| module_name_zh | RAG 边界与知识库内容暴露 |
| candidate_id | {inp.get('candidate_id', '')} |
| candidate_title | {inp.get('candidate_title', '')} |
| risk_category | {inp.get('risk_category', '')} |
| profile | {inp.get('profile', '')} |

## 评审摘要

| 字段 | 值 |
|---|---|
| review_id | {review['review_id']} |
| reviewer | assistant |
| review_timestamp | {review['review_timestamp']} |
| review_status | {review['review_status']} — {status_zh.get(review['review_status'], '')} |
| review_confidence | {review['review_confidence']} |
| validation_mode | offline_static_derivation |
| evidence_strength | candidate_description_only |
| confidence_scope | based_on_candidate_description_only |
| human_review_required | true |
| formal_finding_allowed | false |

**重要边界说明**：
- 本评审为 **offline capability review**（离线能力评审）
- 仅基于 finding candidate 描述进行静态推导
- **不能证明**漏洞已经确认存在
- **不能证明**生产环境受影响
- **不能直接**用于 formal finding
- 需要人工复核和授权复测后才能升级判断

## 观察摘要

根据 finding candidate **{inp.get('candidate_id', '')}** 的描述：
{inp.get('observed_output_summary', '')}

| 评估项 | 状态 | 说明 |
|---|---|---|
| 原始知识库内容暴露 | {exposed_indicated} | {review['raw_kb_exposure_summary']} |
| 检索片段暴露 | {chunk_indicated} | {review['source_chunk_exposure_summary']} |
| 系统元数据暴露 | 待人工复核 | {review['metadata_exposure_summary']} |
| 业务敏感数据涉及 | {sensitive_zh} | 需 M19 跟进验证 |

## RAG 边界风险信号

| 风险信号 | 状态 | 说明 |
|---|---|---|
{risk_rows}
## 下游模块映射

| 下游模块 | 映射 | 理由 |
|---|---|---|
| M19 Business Data Exposure | {review['mapping_to_M19']} | 需确认泄露内容是否涉及真实业务数据后再决定是否跟进 |
| M21 Impact Path Reconstruction | {review['mapping_to_M21']} | {'候选证据提示存在泄露线索，可作为影响路径入口线索，但缺少 retrieval trace 和复测证据，不能完整重建影响路径' if review['mapping_to_M21'] == 'partial_available' else '未观察到泄露线索'} |
| M22 Business Impact Evidence Report | {review['mapping_to_M22']} | 需人工复核确认业务影响后再决定是否纳入报告 |

## 被测 RAG 应用可能存在的控制缺口

以下为根据候选证据推断的、被测 RAG 应用侧可能存在的控制缺口（需复测确认）：

{control_rows}
## 当前评估系统能力限制

以下为当前评估阶段的能力限制：

{limitation_rows}
## 改进建议

{review['recommendation']}

## 不构成 formal finding 声明

本评审由离线生成脚本根据 finding candidate 的描述自动生成。

- **usable_for_formal_finding**: false
- **validation_mode**: offline_static_derivation
- **evidence_strength**: candidate_description_only
- 当前标记为 `{review['review_status']}`，需人工复核确认泄露内容的真实性和严重度
- 能力缺失记录为 `capability_gap`，不标记为安全漏洞或确认漏洞
- 不涉及真实业务数据泄露（如涉及，应由 M19 跟进）
- 不替代正式安全评估或渗透测试
- 本生成过程**未连接任何 API**、**未运行 promptfoo eval**、**未新增测试用例**
"""
    with open(path, "w") as f:
        f.write(md)
    print(f"  → {path}")


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    print(f"M03 Offline Capability Review Generator (Calibrated)")
    print(f"{'=' * 50}")
    print(f"Input:  {M03_DIR}/sample_module_input.yaml")
    print()

    inp = load_input()
    review = derive_review(inp)

    result_dir = f"{RESULTS_DIR}/M03"
    yaml_path = f"{result_dir}/review_output.yaml"
    md_path = f"{result_dir}/capability_review.md"

    print("Writing outputs...")
    write_yaml(review, yaml_path)
    write_markdown(review, inp, md_path)

    print()
    print(f"Done. {len(review['risk_signals'])} risk signals detected.")
    print(f"Review status: {review['review_status']} (confidence: {review['review_confidence']})")
    print(f"Validation mode: {review['validation_mode']}")
    print(f"Evidence strength: {review['evidence_strength']}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
