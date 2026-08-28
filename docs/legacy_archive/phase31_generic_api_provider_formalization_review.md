# Phase 31 复盘：Generic API Provider Formalization

## 概述

- **Phase**: 31
- **名称**: Generic API Provider Formalization
- **目标**: 将 API Provider 从早期 skeleton 规范化为可配置、可审计、可 dry-run 的 provider 层
- **日期**: 2026-06-17

## 完成内容

### api_provider/ 目录结构

| 文件 | 内容 |
|---|---|
| `api_provider/README.md` | 目录概览，包含边界声明和标志位 |
| `api_provider/api_provider_schema.md` | Provider 通用 Schema（6 种 provider type） |
| `api_provider/target_profile_schema.md` | Target Profile Schema（5 种 environment type） |
| `api_provider/provider_config_template.local.example.yaml` | Config Template（placeholder only） |
| `api_provider/request_response_normalization_schema.md` | Request/Response Normalization Schema（6 条 redaction rules） |
| `api_provider/provider_safety_guardrails.md` | Safety Guardrails（G01-G16，3 层：config/execution/credential） |
| `api_provider/provider_execution_boundary.md` | Execution Boundary 声明 |

### sample_targets/（5 个 sample target）

| 文件 | target_id | provider_type |
|---|---|---|
| `openai_compatible_chat_sample.yaml` | sample_openai_chat | openai_compatible_chat |
| `rag_qa_api_sample.yaml` | sample_rag_qa_api | rag_qa_api |
| `agent_api_sample.yaml` | sample_agent_api | agent_api |
| `workflow_api_sample.yaml` | sample_workflow_api | workflow_api |
| `fastgpt_compatible_sample.yaml` | sample_fastgpt_compatible | fastgpt_compatible |

### Scripts

| 脚本 | 功能 | 结果 |
|---|---|---|
| `scripts/api_provider_dry_run_simulator.py` | 对 5 个 sample target 做 dry-run simulation | 5 targets simulated，6 ops，0 network calls |
| `scripts/validate_api_provider_formalization.py` | 15 项静态校验 | 15/15 PASS |

## Safety Flags

| 标志 | 值 |
|---|---|
| network_called | False |
| credentials_loaded | False |
| real_target_connected | False |
| tests_executed | False |
| evidence_generated | False |
| usable_for_formal_finding | False |

所有 sample target 声明：
- real_target=false
- dry_run_only=true
- execution_allowed=false
- usable_for_real_test=false

## 关键设计决策

1. **Schema formalization 优先**：先定义 provider type、target profile、normalization、guardrails 的 schema，再实现具体 adapter。
2. **Safety guardrails 三层分离**：Config Layer（G01-G06）、Execution Layer（G07-G12）、Credential Layer（G13-G16），确保配置、执行、凭证的安全边界独立可审计。
3. **.auth_mode 枚举**：定义 6 种受支持的 auth mode（none/api_key_header/bearer_token/basic_auth/oauth2_client_credentials/placeholder_only），禁止未在枚举中的认证方式。
4. **target_environment 分类**：定义 5 种 environment（local_mock/sandbox/test/staging/production_not_allowed），production 被显式禁止。
5. **Sample target 不可执行**：所有 sample target 的 execution_allowed=false，确保误操作不会导致真实 API 调用。

## 与 Phase 11 的关系

Phase 11 创建了 API Provider Skeleton（`targets/api/`、`providers/api_chatbot_provider.py`、`providers/api_rag_provider.py`），是早期原型阶段的最小骨架。

Phase 31 在 Phase 11 基础上进行全面形式化：
- 新增 `api_provider/` 独立目录，替代原来的 `targets/api/` 和 `providers/`
- 新增 provider schema、target profile schema、normalization schema、guardrails、execution boundary 等正式文档
- 新增 dry-run simulator 和 validation script
- 保留 Phase 11 的 skeleton 文件不变，保持向后兼容

## 已验证项

- [x] api_provider/ 目录结构完整
- [x] 5 个 sample target 文件创建
- [x] 所有 sample target 使用 placeholder endpoint
- [x] 无真实 URL/token/email
- [x] 所有 safety flags 为 false
- [x] Dry-run simulator 可运行
- [x] Validation script 15/15 通过
- [x] Provider validation result 符合安全约束
- [x] Provider validation report 已生成
- [x] .local/ 配置模板使用 placeholder（不提交到 git）

## 未包含

以下内容不在 Phase 31 范围：
- 连接真实 API
- 读取真实凭证
- 访问真实 endpoint
- 执行真实安全测试
- 运行 garak/PyRIT/AgentDojo
- 运行 promptfoo
- 生成真实 evidence
- 生成真实 finding
- 提交 .local/ 配置到 git

## 后续条件（Real API Testing 需要）

参考 `api_provider/provider_execution_boundary.md`，后续 Real API Testing 需要：
1. RoE 授权
2. Test credentials（非生产环境）
3. Safety guardrail review
4. execution_allowed=true 的 target profile
5. Guardrail bypass 审批（如需）
