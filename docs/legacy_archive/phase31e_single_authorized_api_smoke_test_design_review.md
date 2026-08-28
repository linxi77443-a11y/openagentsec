# Phase 31E Review: Single Authorized API Smoke Test Design

## 概述

Phase 31E 在 Phase 31D (Limited Authorized API Dry-Run Plan) 基础上设计 Single Authorized API Smoke Test，定义未来第一次真实连接测试 API 前的最小冒烟测试方案。

## 新增内容

### 新增文件（11 个 + 1 个验证脚本）

| 文件 | 说明 |
|------|------|
| api_provider/single_smoke_test_design/README.md | 目录说明和安全声明 |
| api_provider/single_smoke_test_design/single_smoke_test_schema.md | 冒烟测试 schema |
| api_provider/single_smoke_test_design/candidate_target_template.yaml | 候选目标模板 |
| api_provider/single_smoke_test_design/minimal_request_bundle.yaml | 最小请求包（4 条低风险请求） |
| api_provider/single_smoke_test_design/expected_safe_response_contract.md | 预期安全响应契约 |
| api_provider/single_smoke_test_design/execution_preflight_gate.yaml | 执行前置门禁（12 项） |
| api_provider/single_smoke_test_design/abort_condition_checklist.md | 中止条件清单（9 硬中止 + 4 软中止） |
| api_provider/single_smoke_test_design/operator_runbook_template.md | 操作人员 runbook 模板 |
| api_provider/single_smoke_test_design/evidence_placeholder_schema.md | Evidence 占位 schema |
| api_provider/single_smoke_test_design/smoke_test_design_validation_result.yaml | 验证结果 |
| api_provider/single_smoke_test_design/smoke_test_design_validation_report.md | 验证报告 |
| scripts/validate_single_authorized_api_smoke_test_design.py | 验证脚本（20 项检查） |

## 设计约束

- 只允许 1 个目标（only_one_target_allowed=true）
- 只允许只读操作（read_only_operations_only=true）
- 只包含 4 条低风险请求（无 jailbreak、无数据外泄、无系统提示词提取、无工具调用攻击）
- 所有请求为 benign / read-only / non-adversarial

## 安全边界

所有新增文件声明以下安全标志：

- smoke_test_design_only=true
- only_one_target_allowed=true
- read_only_operations_only=true
- approval_status=not_approved
- execution_allowed=false
- credentials_loaded=false
- real_target_connected=false
- network_called=false
- evidence_generated=false
- production_target_allowed=false

## 验证结果

- 验证脚本: scripts/validate_single_authorized_api_smoke_test_design.py
- 检查项: 20
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
