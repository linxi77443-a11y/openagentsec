# Phase 35B Review: Promptfoo Go/No-Go Packet

## 概述

Phase 35B 在 Phase 35 (Promptfoo 集成框架) 之上建立了 Go/No-Go 审批门禁层，为未来真实 promptfoo eval 执行提供完整的审批框架。本阶段仅生成静态审批包文件，不执行任何实际网络操作。

## 核心产出

### go_no_go/ 目录（9 个文件）

| 文件 | 用途 | 关键安全标志 |
|------|------|-------------|
| `promptfoo_go_no_go_packet.md` | 整体审批包 | approval_status=not_approved, execution_allowed=false |
| `promptfoo_approval_checklist.md` | 10 项审批检查清单 + 3 角色签批 | Go/No-Go 决策页 |
| `promptfoo_execution_scope.yaml` | 7 项允许操作 + 6 项排除操作 | 明确 allowed/excluded scope |
| `promptfoo_cost_request_budget.yaml` | 预算字段（max_cases=52, initial_run=10, hard_limit=30） | hard_stop_on_budget_exceeded=true |
| `promptfoo_preflight_checklist.md` | 18 项前置检查（环境/预算/安全/签批） | 所有检查状态未通过 |
| `promptfoo_execution_boundary.md` | 安全边界 + 数据流图 | network_allowed=false, credential_loaded=false |
| `promptfoo_rollback_plan.md` | 7 触发条件 + 回滚程序（前/中/后） | 含凭证撤销与 git diff 检查 |
| `promptfoo_result_acceptance_criteria.md` | 13 项验收标准 + 三级评分 | 所有结果 usable_for_formal_finding=false |
| `promptfoo_local_config_template.md` | 本地配置模板（占位符） | PLACEHOLDER 替换规则 + 7 条安全规则 |

### 安全标志一览

| 标志 | 值 |
|------|-----|
| approval_status | not_approved |
| execution_allowed | false |
| network_allowed | false |
| promptfoo_eval_allowed | false |
| target_api_call_allowed | false |
| deepseek_judge_allowed | false |
| credential_loaded | false |
| human_go_no_go_required | true |
| result_can_create_formal_finding | false |

### 验证结果

- **检查项总数**: 58
- **通过**: 58
- **失败**: 0

覆盖范围：安全标志完整性验证、文档间交叉引用一致性、YAML 可解析性、占位符隔离、范围声明一致性、回滚流程完备性。

## 安全边界

- 所有标志：approval_status=not_approved, execution_allowed=false, network_allowed=false, credential_loaded=false, promptfoo_eval_allowed=false, target_api_call_allowed=false, deepseek_judge_allowed=false
- 配置模板仅含 `__PLACEHOLDER_*__` 占位符
- 不包含真实 API key、不包含 Authorization header
- 所有结果需要人工审批（human_go_no_go_required=true）
- 所有结果不可用于正式发现（result_can_create_formal_finding=false）

## 范围确认

所有操作均保持在允许范围内：

| 操作 | 范围 | 状态 |
|------|------|------|
| 配置验证 (config validation) | allowed | 始终允许，无需审批 |
| Dry-run 验证 | allowed | 始终允许，无需审批 |
| Mock 结果归一化 | allowed | 始终允许，无需审批 |
| Schema 验证 | allowed | 始终允许，无需审批 |
| Evidence 映射 | allowed | 始终允许，无需审批 |
| Finding 映射 | allowed | 始终允许，无需审批 |
| Judge 交接准备 | allowed | 始终允许，无需审批 |
| **promptfoo eval** | **excluded** | **需要 Go/No-Go 审批** |
| **真实 API 调用** | **excluded** | **需要 Go/No-Go 审批** |
| **DeepSeek API 调用** | **excluded** | **需要独立 Go/No-Go 审批** |
| **读取 .local/ 文件** | **excluded** | **凭证隔离** |

## 设计决策

1. **审批先行**：在允许任何 promptfoo eval 之前，先建立完整的审批框架
2. **默认拒绝**：所有安全标志默认为 false，需要显式满足 Go 条件后方可执行
3. **多层次检查**：从环境到预算到安全到回滚，每个维度独立检查
4. **配置安全**：凭证配置使用 `__PLACEHOLDER_*__` 占位符，不硬编码任何真实 key
5. **结果约束**：所有结果上限为 evidence_candidate → finding_candidate → judge_handoff，不可自动升级为正式发现
6. **与 Phase 34B 对称设计**：采用与 DeepSeek Judge Go/No-Go 相同的审批模式，便于操作者统一理解

## 本审查文档

- **文件**: `docs/phase35b_promptfoo_go_no_go_packet_review.md`
- **生成日期**: 2026-06-19
- **来源**: Phase 35B
- **方法**: 静态包生成审查，无实际执行
