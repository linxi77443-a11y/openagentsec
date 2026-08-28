# Phase 31D Review: Limited Authorized API Dry-Run Plan

## 概述

Phase 31D 在 Phase 31C (Local Mock API Execution Harness) 基础上增加 Limited Authorized API Dry-Run Plan，规划未来第一次连接真实测试 API 前的授权、配置、凭证、限频、数据保护、执行门禁和回滚条件。

## 新增内容

### 新增文件（11 个 + 1 个验证脚本）

| 文件 | 说明 |
|------|------|
| api_provider/authorized_dry_run_plan/README.md | 目录说明和边界声明 |
| api_provider/authorized_dry_run_plan/limited_authorized_dry_run_schema.md | Dry-run 计划 schema |
| api_provider/authorized_dry_run_plan/preflight_checklist.md | 前置检查清单 (20 项) |
| api_provider/authorized_dry_run_plan/test_target_readiness_gate.yaml | 测试目标就绪门禁 (10 项) |
| api_provider/authorized_dry_run_plan/credential_readiness_checklist.md | 凭证就绪检查清单 (14 项) |
| api_provider/authorized_dry_run_plan/rate_limit_request_budget_policy.md | 限频/请求预算策略 |
| api_provider/authorized_dry_run_plan/allowed_test_bundle_definition.yaml | 允许的测试包定义 (4 个 bundle) |
| api_provider/authorized_dry_run_plan/rollback_stop_condition_policy.md | 回滚/停止条件策略 |
| api_provider/authorized_dry_run_plan/dry_run_approval_packet_template.md | Dry-run 审批包模板 |
| api_provider/authorized_dry_run_plan/dry_run_plan_validation_result.yaml | 验证结果 |
| api_provider/authorized_dry_run_plan/dry_run_plan_validation_report.md | 验证报告 |
| scripts/validate_limited_authorized_api_dry_run_plan.py | 验证脚本 (19 项检查) |

## 安全边界

所有新增文件声明以下安全标志：

- authorization_required=true
- approval_status=not_approved
- execution_allowed=false
- credentials_loaded=false
- real_target_connected=false
- network_called=false
- evidence_generated=false
- production_target_allowed=false
- dry_run_plan_only=true

## 更新文件

- api_provider/README.md
- api_provider/provider_execution_boundary.md
- api_provider/provider_safety_guardrails.md
- api_provider/onboarding/onboarding_validation_report.md
- api_provider/mock_harness/mock_harness_validation_report.md
- README.md
- docs/roadmap.md
- docs/learning_summary.md
- docs/release_notes_v1.md
- dashboard/README.md
- release/release_manifest_v1_4.yaml
- release/system_release_v1_4.md
- release/execution_status_matrix_v1_4.md
- release/known_limitations_v1_4.md
- release/next_phase_roadmap_v1_4.md
- scripts/generate_atlas_dashboard.py
- scripts/generate_enterprise_report.py
- scripts/generate_all_reports.sh
- runners/run_quality_check.sh

## 验证结果

- 验证脚本: scripts/validate_limited_authorized_api_dry_run_plan.py
- 检查项: 19
- 预期结果: 全部通过

## 本阶段声明

- 不连接真实 API
- 不读取真实 token
- 不读取真实 API key
- 不访问真实 endpoint
- 不运行 promptfoo eval
- 不运行 garak / PyRIT
- 不调用 curl / wget
- 不访问外网
- 不生成真实 evidence
- 不生成真实 finding
- 不改变 Phase 16.5 执行统计
