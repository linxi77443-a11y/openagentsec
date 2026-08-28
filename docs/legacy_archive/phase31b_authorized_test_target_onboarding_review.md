# Phase 31B 复盘：Authorized Test Target Onboarding

## 概述

- **Phase**: 31B
- **名称**: Authorized Test Target Onboarding
- **目标**: 在连接任何真实 API 前建立结构化授权、RoE、测试范围、凭证隔离、限频、测试窗口、禁止操作、审批状态和安全门禁层
- **日期**: 2026-06-17

## 完成内容

### api_provider/onboarding/ 目录结构（11 个文件）

| 文件 | 内容 |
|---|---|
| `README.md` | 目录概览，包含边界声明和标志位 |
| `authorized_target_onboarding_schema.md` | Onboarding Schema 定义（30+ 字段，13 个安全约束） |
| `target_intake_template.yaml` | Target Intake 模板（所有字段为 PLACEHOLDER） |
| `roe_checklist.md` | RoE 检查清单（8 类 40 项，全部未签署） |
| `credential_isolation_policy.md` | 凭证隔离策略（5 类存储方式、4 类凭证分类、轮换策略） |
| `test_scope_definition_template.yaml` | 测试范围定义模板（10 种测试类型、安全约束、清理要求） |
| `allowed_prohibited_operations_matrix.yaml` | 允许/禁止操作矩阵（19 项操作，全部为 prohibited） |
| `rate_limit_and_safety_window_policy.md` | 限频和安全窗口策略（5 个限频参数、4 类限频策略、紧急停止） |
| `approval_gate_checklist.md` | 审批门禁检查清单（7 个门禁 G01-G07，全部未通过） |
| `onboarding_validation_result.yaml` | Onboarding 验证结果 |
| `onboarding_validation_report.md` | Onboarding 验证报告 |

### Scripts

| 脚本 | 功能 | 结果 |
|---|---|---|
| `scripts/validate_authorized_target_onboarding.py` | 18 项静态校验 | 18/18 PASS |

## Safety Flags

| 标志 | 值 |
|---|---|
| authorization_required | true |
| approval_status | not_approved |
| execution_allowed | false |
| credentials_loaded | false |
| real_target_connected | false |
| production_target_allowed | false |
| dry_run_only | true |
| human_approval_obtained | false |
| network_called | false |
| tests_executed | false |
| evidence_generated | false |
| usable_for_formal_finding | false |

## Guardrails 扩展

Phase 31B 在 Phase 31 的 G01-G16 基础上新增 G17-G24：

| # | 检查项 | 说明 |
|---|---|---|
| G17 | authorization_required | 所有 target 必须获得授权 |
| G18 | approval_status approved | 未审批的 target 不可用 |
| G19 | production_target_allowed false | 生产环境默认禁止 |
| G20 | human_approval_obtained | 缺少人工审批不可执行 |
| G21 | RoE 已签署 | 缺少 RoE 不可执行 |
| G22 | Credential isolation policy | 缺少凭证隔离不可执行 |
| G23 | Rate limit policy | 缺少限频策略不可执行 |
| G24 | Approval gate checklist | 缺少审批门禁不可执行 |

## 关键设计决策

1. **默认禁止**：所有操作默认 prohibited，approval_status=not_approved，确保无默认权限
2. **审批门禁 G01-G07**：7 个独立门禁覆盖授权、凭证、限频、范围、数据、人工、安全
3. **凭证隔离独立策略**：credential_isolation_policy.md 作为独立文件，不与其他策略混用
4. **限频参数可配置**：rate_limit_and_safety_window_policy.md 定义默认值，但允许按 target 调整
5. **RoE checklist 独立签署**：8 类 40 项检查，需要 4 方签署（执行方、目标所有者、安全、法务）

## 已验证项

- [x] api_provider/onboarding/ 目录结构完整（11 个文件）
- [x] Target intake template 仅包含 PLACEHOLDER
- [x] 无真实 URL/token/email/API key
- [x] authorization_required=true
- [x] approval_status=not_approved
- [x] execution_allowed=false
- [x] real_target_connected=false
- [x] credentials_loaded=false
- [x] production_target_allowed=false
- [x] dry_run_only=true
- [x] 有 prohibited operations 定义
- [x] 有 rate limit policy
- [x] 有 credential isolation policy
- [x] 有 RoE checklist
- [x] 有 human approval gate
- [x] Guardrails 扩展（G17-G24）
- [x] Validation script 18/18 通过

## 未包含

- 连接真实 API
- 读取真实凭证
- 访问真实 endpoint
- 执行真实安全测试
- 运行 garak/PyRIT/AgentDojo
- 运行 promptfoo
- 生成真实 evidence
- 生成真实 finding
- 发起 curl/wget 请求
- 访问 .local/ 真实配置

## 后续条件（Real API Testing 需要）

1. RoE 签署（roe_checklist.md 所有 40 项通过）
2. Authorization 审批（approval_status → approved）
3. 测试凭证隔离配置（credential_isolation_policy.md 实施）
4. 限频策略生效（rate_limit_and_safety_window_policy.md 配置）
5. 审批门禁 G01-G07 全部通过
6. execution_allowed → true
7. dry_run_only → false
8. Provider schema 确认 + Safety guardrails 检查
