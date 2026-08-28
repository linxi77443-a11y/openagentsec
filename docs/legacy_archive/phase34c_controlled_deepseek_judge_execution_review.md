# Phase 34C.1 Review: DeepSeek Judge Call Boundary Reconciliation

## 概述

Phase 34C.1 是 Phase 34C 的小补丁阶段，不重新调用 DeepSeek API、不读取 .local/、不连接被测 API。

核心任务：对 Phase 34C 执行结果的调用预算字段进行边界对账与语义澄清。

## 背景

Phase 34C 原审批包使用 `max_judge_calls=16`，但实际执行结果为 21 次 DeepSeek API 调用：

| 调用类别 | 次数 | 说明 |
|----------|------|------|
| Smoke judge | 1 | 调试验证 |
| Batch candidate judge | 15 | 候选发现评审（1 个由 smoke 覆盖） |
| Consolidated group judge | 5 | 合并组评审 |
| **总计** | **21** | |

这不是安全事故，但需要明确边界语义，避免后续工具调用预算理解错误。

## 修正内容

### 新增文件

| 文件 | 用途 |
|------|------|
| `execution_plan.yaml` | 调用预算字段定义（四类预算：candidate/group/smoke/total） |
| `deepseek_judge_summary.md` | 执行摘要（Markdown 可读格式） |
| `cost_usage_estimate.yaml` | 成本估算与预算对账 |
| `docs/phase34c_controlled_deepseek_judge_execution_review.md` | 本评审文档 |

### 调用预算字段

| 字段 | 上限 | 实际 | 说明 |
|------|------|------|------|
| max_candidate_judge_calls | 16 | 15 | 候选发现评审 |
| max_consolidated_group_judge_calls | 5 | 5 | 合并组评审 |
| max_smoke_calls | 1 | 1 | 调试验证 |
| max_total_deepseek_api_calls | 22 | 21 | DeepSeek API 总调用 |

## 安全边界

- 未连接被测 API
- 未生成新测试用例
- 未改变 finding candidate 状态
- 所有结果仍为 assistant_review / needs_human_review / usable_for_formal_finding=false
- 未重新调用 DeepSeek API
- 未读取 .local/ 配置

## 设计决策

1. **不修改原始执行结果**：Phase 34C 的输出 JSON 文件保持原样，不重写 execution_summary.json。
2. **新增独立对账文件**：调用预算字段单独写入 execution_plan.yaml / cost_usage_estimate.yaml / deepseek_judge_summary.md。
3. **语义澄清而非修正**：原 max_judge_calls=16 表示候选发现评审上限，不含 smoke call 和 consolidated group review。
4. **四类预算字段设计**：后续真实工具调用必须同时配置 candidate/group/smoke/total 四类预算字段。

## 验证

- python3 scripts/validate_deepseek_judge_execution.py — 新增预算边界检查
- bash runners/run_quality_check.sh — Phase 34C 质量检查
- 不重新调用 DeepSeek API
- 不读取 .local/
