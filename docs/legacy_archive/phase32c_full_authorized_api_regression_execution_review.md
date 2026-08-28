# Phase 32C Review: Full Authorized API Regression Execution

## 概述

Phase 32C 在 Phase 31F 单一冒烟测试审批包与 Go/No-Go 门禁层之上，建立了**全量授权 API 回归执行层**。该阶段是 Phase 31B/31D/31E/31F 授权 API 测试设计链路的最终执行层——在审批门禁通过后，对授权测试 API 执行全量回归测试，生成带脱敏的 evidence，所有 finding 作为 candidates 等待人工审核。

## 新增文件

### 设计文件（11 个）

| 文件 | 用途 |
|---|---|
| `full_regression_execution_schema.md` | 全量回归执行 schema，定义执行元数据、约束条件和输出规范 |
| `regression_test_target_config.yaml` | 回归测试目标配置，引用已授权的 test target |
| `full_regression_request_bundle.yaml` | 全量回归请求包，汇总所有允许的测试请求 |
| `expected_regression_response_contract.yaml` | 预期安全响应契约，定义正常/异常响应格式 |
| `regression_execution_preflight_gate.yaml` | 执行前 preflight gate，18 项检查清单 |
| `regression_execution_trace_schema.yaml` | 执行追踪 schema，记录每次 API 调用的完整链路 |
| `regression_evidence_normalization_schema.yaml` | Evidence 归一化 schema，定义脱敏规则和字段映射 |
| `finding_candidate_schema.yaml` | Finding candidate schema，定义 needs_human_review 状态字段 |
| `human_review_criteria.yaml` | 人工复核标准，定义 finding 从 candidate 升级为 confirmed/rejected 的判定条件 |
| `operator_execution_runbook.md` | 操作员执行手册，逐步指导回归执行流程 |
| `execution_post_processing_checklist.md` | 执行后处理检查清单，确保证据脱敏、凭证吊销和数据清理 |

### 脚本（2 个）

| 脚本 | 用途 |
|---|---|
| `scripts/run_full_authorized_api_regression.py` | 全量授权 API 回归执行主脚本 |
| `scripts/validate_full_authorized_api_regression_result.py` | 回归执行结果验证脚本，检查 evidence 完整性和脱敏正确性 |

## 设计约束

- **no_production_access=true**：不允许访问生产系统，仅限授权测试 API
- **read_only_operations_only=true**：只允许只读操作，不执行任何写操作
- **findings_are_candidates_only=true**：所有 finding 默认为 candidates
- **redaction_required=true**：evidence 生成时必须完成脱敏
- **human_review_required=true**：所有 finding candidates 需经人工复核后方可正式接受

## API Provider 目录结构扩展

```
api_provider/
  full_regression_execution/        # ← 新增：全量授权 API 回归执行层
    full_regression_execution_schema.md
    regression_test_target_config.yaml
    full_regression_request_bundle.yaml
    expected_regression_response_contract.yaml
    regression_execution_preflight_gate.yaml
    regression_execution_trace_schema.yaml
    regression_evidence_normalization_schema.yaml
    finding_candidate_schema.yaml
    human_review_criteria.yaml
    operator_execution_runbook.md
    execution_post_processing_checklist.md
```

## 安全边界

1. **不涉及生产系统**：回归执行目标为授权测试 API，经过 Phase 31B onboarding 流程确认、Phase 31D dry-run 计划设计、Phase 31E 冒烟测试设计和 Phase 31F 审批门禁后方可执行。
2. **不执行写操作**：所有测试请求为只读操作，不执行任何数据修改、配置变更或工具调用攻击。
3. **Evidence 脱敏前置**：evidence 生成时完成脱敏，不依赖事后处理。
4. **Finding 为 candidates**：执行输出的 finding 自动标记为 `needs_human_review=true`，`usable_for_formal_finding=false`，不可直接用于正式报告。
5. **人工复核门禁**：finding 从 candidate 升级为 confirmed/rejected 需要通过 human_review 流程。

## 执行结果

（待执行后填写）

| 项目 | 状态 |
|---|---|
| 回归执行完成 | pending |
| Total requests sent | - |
| Pass / Fail / Error | - |
| Evidence 生成 | - |
| Finding candidates 数量 | - |
| Human review 完成 | - |
| Confirmed findings | - |
| Rejected candidates | - |
| Quality check 通过 | - |

## 与相邻阶段的关系

```text
Phase 31 API Provider Formalization
        ↓
Phase 31B Authorized Test Target Onboarding
        ↓
Phase 31C Local Mock API Execution Harness
        ↓
Phase 31D Limited Authorized API Dry-Run Plan
        ↓
Phase 31E Single Authorized API Smoke Test Design
        ↓
Phase 31F Single Smoke Test Approval Packet & Go/No-Go Gate
        ↓
Phase 32C Full Authorized API Regression Execution（← 当前阶段）
        ↓
未来：Production System Testing（独立授权、审批和拆除流程）
```

## Phase 声明

- **No production access**: 全量回归执行不涉及生产系统访问
- **No write operations**: 所有执行操作为只读，不执行写操作
- **Findings are candidates only**: 所有执行产出为 finding candidates，需人工复核后方可正式接受
- **Evidence with redaction**: 所有 evidence 生成时完成脱敏
- **Usable_for_formal_finding**: false（所有 finding candidates 均需 human_review）
- **Production_target_allowed**: false
- **Completion**: pending（需执行后方可标记为 completed）
