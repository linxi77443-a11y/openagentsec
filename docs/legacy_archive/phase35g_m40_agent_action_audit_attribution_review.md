# Phase 35G: M40 Agent Action Audit & Attribution Minimal Implementation — Review Document

## 概述

Phase 35G 基于 Phase 35D 输出的 M40 模块实现规格单，构建 Agent 动作审计与归因的最小能力框架。本阶段不做真实 Agent tool call，不连接业务系统，不跑 eval，不生成 formal finding。

## 交付物

| # | 文件 | 用途 |
|---|---|---|
| 1 | `capability_modules/implementations/M40_agent_action_audit_attribution/audit_log_schema.yaml` | 审计日志 schema，27 个必需字段 |
| 2 | `capability_modules/implementations/M40_agent_action_audit_attribution/sample_audit_log.yaml` | 脱敏样例审计日志 |
| 3 | `capability_modules/implementations/M40_agent_action_audit_attribution/audit_review_output_schema.yaml` | 审计评审输出 schema，含 M14/M15/M16/M21/M22/M41 映射 |
| 4 | `capability_modules/implementations/M40_agent_action_audit_attribution/sample_audit_capability_review.md` | 人工可读的审计能力评审样本 |
| 5 | `scripts/validate_m40_agent_action_audit_attribution.py` | 静态验证脚本 |
| 6 | `docs/phase35g_m40_agent_action_audit_attribution_review.md` | 本文件：阶段评审文档 |

## M40 最小能力实现摘要

- **audit_log_schema.yaml**: 27 个必需字段，覆盖审计事件完整链路：谁触发（trigger_user_id / original_user_role）、哪个 Agent（agent_id / agent_session_id）、哪个工具（tool_name / tool_action）、参数是否脱敏（sensitive_arguments_redacted）、审批状态（approval_required / approval_status / approval_actor）、执行环境（execution_environment / production_environment）、服务账号（service_account_used / original_user_authorization_checked）
- **sample_audit_log.yaml**: 基于 sandbox 环境的脱敏样例审计日志，formal_finding_allowed: false，human_review_required: true，production_environment: false
- **audit_review_output_schema.yaml**: 输出结构包含审计字段完整性判断、归因可用性、工具链路追踪、审批记录、service account 边界、mapping_to_M14/M15/M16/M21/M22/M41
- **sample_audit_capability_review.md**: 评审模板含审计字段完整性判断矩阵、审计能力评估、6 个下游模块映射、能力缺口清单、不构成 formal finding 声明

## 最小审计字段说明

M40 定义了 27 个审计字段，覆盖 Agent 行为审计的完整链路：

| 字段类别 | 字段 | 说明 |
|---|---|---|
| 事件标识 | audit_event_id / timestamp / task_id / finding_candidate_id | 唯一标识和关联 |
| 用户归因 | trigger_user_id / original_user_role | 谁触发了动作 |
| Agent 归因 | agent_id / agent_session_id | 哪个 Agent 执行了动作 |
| 工具调用 | tool_name / tool_action / tool_arguments_summary / sensitive_arguments_redacted / tool_result_summary | 调用了什么、做了什么 |
| 审批记录 | approval_required / approval_status / approval_actor | 是否经过审批 |
| 环境标记 | execution_environment / production_environment | 执行环境区分 |
| 权限边界 | service_account_used / service_account_id / original_user_authorization_checked | 权限验证情况 |

## 安全边界确认

| 边界 | 值 |
|---|---|
| promptfoo_eval_run | false |
| target_api_connected | false |
| deepseek_api_called | false |
| local_config_read | false |
| formal_finding_generated | false |
| test_cases_added | false |
| agent_tool_runner_implemented | false |
| static_analysis_only | true |
| human_review_required | true |
| formal_finding_allowed | false |

## 能力缺口

1. M40 当前只有 schema 框架，尚未接入真实 Agent 系统的审计日志输出
2. 缺少结构化日志解析器（需后续阶段实现）
3. 缺少日志不可篡改性验证机制
4. 缺少与 M14/M15/M16 的结构化关联
5. 未实现审计字段自动覆盖率计算

## 下一步建议

1. 运行验证脚本确认所有文件合规
2. 提交当前阶段成果
3. M40 与 M01/M02/M03 形成四件套基础能力框架
4. 后续阶段可接入真实 Agent 审计日志输出，验证字段完整性
5. M40 验证通过后，M21/M22 可基于审计日志进行影响路径重建
