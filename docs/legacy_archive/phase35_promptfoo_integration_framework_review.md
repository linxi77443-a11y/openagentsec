# Phase 35 审查: Promptfoo 集成框架

## 概述

Phase 35 搭建 promptfoo 接入框架，将已有 promptfoo drafts / regression suites / runner 脚本 / 结果证据纳入统一的工具结果处理链路。核心目标是通过 adapter 模式对 promptfoo 的配置、执行、结果解析和下游交接（evidence / finding / judge）进行归一化管理，消除各 profile 各自为政的碎片化现状。

本阶段**不**运行 promptfoo eval、**不**连接被测 API、**不**调用 DeepSeek。

## 范围

| 范围项 | 说明 |
|--------|------|
| 配置归一化 | 统一扫描所有 promptfoo runner YAML、draft YAML、generated testcase YAML，建立配置索引 |
| Dry-run 校验 | 验证配置可解析、draft 安全标志位正确（generated_only / executed / real_target_connected） |
| 结果 schema | 定义统一的结果结构，适配 promptfoo JSON 输出格式 |
| 结果归一化 | 将各 profile 结果（agent / chatbot / rag / manual_ui / generic_agent_harness）映射为统一记录 |
| Evidence handoff | 归一化结果 → reports/evidence/ 写入 |
| Finding handoff | 归一化结果 → finding candidate 生成 |
| Judge handoff | 归一化结果 → DeepSeek Judge 评审流程 |

### 明确不在范围

| 排除项 | 原因 |
|--------|------|
| 运行 promptfoo eval | 由各 runner 脚本负责，adapter 只处理已产生的结果 |
| 连接被测 API | 安全边界要求所有测试限于 sandbox/ 本地靶场 |
| 调用 DeepSeek | 由 Phase 34 系列处理，adapter 只准备 judge 入参 |
| 修改已有 runner 脚本 | 现有 runner 安全机制保持不动 |
| 修改已有 draft / regression suite | 只读索引，不修改内容 |
| 生成 formal finding | 只准备 finding candidate 入参 |

## 目录结构

```
tool_integrations/promptfoo/
├── __init__.py                          # 包入口，暴露 PromptfooIntegration 类
├── config_index.py                      # 扫描并索引所有 promptfoo YAML 配置
├── result_schema.py                     # 统一结果 Schema 定义
├── normalizer.py                        # 将各 profile 结果归一化为统一格式
├── validator.py                         # dry-run 校验：YAML 可解析性 + 安全标志位
├── evidence_writer.py                   # 归一化结果 → evidence JSON 写入
├── finding_prep.py                      # 归一化结果 → finding candidate 入参准备
├── judge_prep.py                        # 归一化结果 → DeepSeek Judge 入参准备
├── adapter.py                           # 主入口适配器，编排整个 pipeline
└── adapter/
    ├── __init__.py                      # adapter 子包入口
    ├── profile_registry.py              # profile 注册表（agent / chatbot / rag / manual_ui / generic_agent_harness）
    └── dry_run_execute.py               # dry-run 执行模拟（需人工 Go/No-Go 决定是否启用真实执行）
```

## 配置索引

### 发现的 promptfoo drafts（regression suites）

| Suite ID | 文件 | 用例数 | 行数 | 安全标志位 | 已验证 |
|----------|------|--------|------|-----------|--------|
| suite_core_llm_regression | `regression_suites/promptfoo_drafts/promptfoo_core_llm_regression.yaml` | 6 | — | generated_only / not executed / not connected | ✅ |
| suite_chatbot_regression | `regression_suites/promptfoo_drafts/promptfoo_chatbot_regression.yaml` | 8 | — | 同上 | ✅ |
| suite_agent_regression | `regression_suites/promptfoo_drafts/promptfoo_agent_regression.yaml` | 10 | — | 同上 | ✅ |
| suite_rag_regression | `regression_suites/promptfoo_drafts/promptfoo_rag_regression.yaml` | 8 | — | 同上 | ✅ |
| suite_api_regression | `regression_suites/promptfoo_drafts/promptfoo_api_regression.yaml` | 1 | — | 同上 | ✅ |
| suite_owasp_llm_regression | `regression_suites/promptfoo_drafts/promptfoo_owasp_llm_regression.yaml` | 55 | 976 | 同上 | ✅ |
| suite_owasp_agentic_regression | `regression_suites/promptfoo_drafts/promptfoo_owasp_agentic_regression.yaml` | 16 | 303 | 同上 | ✅ |
| **合计** | | **104** | | | **7/7** |

### 发现的 generated testcases

| 文件 | 用例数 |
|------|--------|
| `generated_testcases/agent/promptfoo_agent_generated.yaml` | 16 |
| `generated_testcases/chatbot/promptfoo_chatbot_generated.yaml` | 14 |
| `generated_testcases/rag/promptfoo_rag_generated.yaml` | 14 |
| `generated_testcases/api/promptfoo_api_generated.yaml` | 0 |
| `generated_testcases/regression/promptfoo_regression_generated.yaml` | 8 |
| **合计** | **52** |

### 发现的 runner 配置

| 文件 | 对应 profile | 目标 target |
|------|-------------|-------------|
| `runners/promptfoo.chatbot.yaml` | chatbot | local_chatbot_demo |
| `runners/promptfoo.agent.yaml` | agent | local_agent_demo |
| `runners/promptfoo.rag.yaml` | rag | local_rag_demo |
| `runners/promptfoo.manual_ui.yaml` | manual_ui | local_chatbot_demo |
| `runners/promptfoo.generic_agent_harness.yaml` | generic_agent_harness | local_agent_demo |
| `runners/promptfoo.api_chatbot.yaml` | api_chatbot | local_chatbot_demo |
| `runners/promptfoo.api_rag.yaml` | api_rag | local_rag_demo |

### 发现的 runner 脚本

| 脚本 | 对应 profile | 默认模式 | 安全边界检查 |
|------|-------------|---------|-------------|
| `runners/run_promptfoo.sh` | chatbot | dry-run | target / provider / API key 检查 |
| `runners/run_agent_promptfoo.sh` | agent | dry-run | target / provider / fake tools 检查 |
| `runners/run_rag_promptfoo.sh` | rag | dry-run | target / provider 检查 |
| `runners/run_manual_ui_promptfoo.sh` | manual_ui | dry-run | target / provider 检查 |

## 结果 Schema

| 字段 | 类型 | 说明 |
|------|------|------|
| `eval_id` | str | promptfoo eval 唯一标识 |
| `profile` | str | 测试 profile（agent / chatbot / rag / manual_ui / generic_agent_harness） |
| `timestamp` | str | ISO 8601 执行时间戳 |
| `target_id` | str | 目标靶场标识（local_chatbot_demo / local_agent_demo / local_rag_demo） |
| `total_tests` | int | 总测试数 |
| `passed` | int | 通过数 |
| `failed` | int | 失败数 |
| `errors` | int | 错误数 |
| `assertions_passed` | int | 断言通过数 |
| `assertions_failed` | int | 断言失败数 |
| `total_latency_ms` | int | 总延迟 |
| `cost` | float | 预估成本（sandbox 靶场为 0） |
| `token_usage` | dict | token 用量（prompt / completion / total） |
| `results` | list[dict] | 每条测试的详细结果 |
| `assertion_details` | list[dict] | 每条断言的详细结果 |
| `risk_signals` | list[str] | 聚合的风险信号列表 |
| `profiles_covered` | list[str] | 覆盖的 profile 列表 |
| `executed` | bool | 是否真实执行（sandbox 为 true，draft 为 false） |
| `real_target_connected` | bool | 是否连接真实目标（全部为 false） |

## Mock Results（已有证据文件）

| Profile | 文件 | 测试数 | 通过 | 断言通过 | 断言失败 | 大小 |
|---------|------|--------|------|---------|---------|------|
| agent | `reports/evidence/promptfoo_agent_result.json` | 10 | 10 | 14 | 0 | 60 KB |
| chatbot | `reports/evidence/promptfoo_chatbot_result.json` | 9 | 9 | 18 | 0 | 51 KB |
| rag | `reports/evidence/promptfoo_rag_result.json` | 12 | 12 | 18 | 0 | 72 KB |
| manual_ui | `reports/evidence/promptfoo_manual_ui_result.json` | 16 | 16 | 56 | 0 | 87 KB |
| generic_agent_harness | `reports/evidence/promptfoo_generic_agent_harness_result.json` | 12 | 12 | 47 | 0 | 70 KB |
| **合计** | | **59** | **59** | **153** | **0** | **342 KB** |

所有已执行结果均为 sandbox 本地靶场产生，未连接真实 API、未使用真实凭证。

## Adapter 结构

```
PromptfooIntegration
├── load_config_index()          # config_index.py → 扫描所有 YAML
├── validate_all()               # validator.py → dry-run 校验
├── normalize_results()          # normalizer.py → 统一结果格式
├── write_evidence()             # evidence_writer.py → 写入 reports/evidence/
├── prep_finding_candidates()    # finding_prep.py → 准备 finding 入参
├── prep_judge_input()           # judge_prep.py → 准备 DeepSeek Judge 入参
└── dry_run_execute()            # adapter/dry_run_execute.py → 模拟执行
                                  # ⚠️ 如需接入真实 promptfoo eval 调用，
                                  #    需人工 Go/No-Go 确认后方可启用
```

### dry_run_execute 方法

```
dry_run_execute(profile: str, config_path: str) → dict
  行为:
    1. 解析指定 profile 的 runner YAML
    2. 校验安全边界标志位
    3. 模拟执行（不调 promptfoo CLI）
    4. 返回 mock 结果（符合 result_schema）
    5. 标记 executed=False, real_target_connected=False

  ⚠️ 人工 Go/No-Go:
     如需将此方法升级为真实执行（调用 promptfoo eval CLI），
     必须由人工逐 profile 确认:
       - target 仅限 local sandbox
       - provider 仅限本地 Python provider
       - 无 external API / 真实凭证引用
       - 无高频 / 批量 / 外传 / 写操作测试
```

## 安全边界

| 安全标志 | 说明 | 强制值 | 检查位置 |
|----------|------|--------|---------|
| `generated_only` | 仅为自动生成，未人工审核 | true | validator.py |
| `curated_from_static_analysis` | 来自静态分析整理 | true | validator.py |
| `executed` | 是否真实执行 | false（draft）/ true（evidence） | validator.py / normalizer.py |
| `real_target_connected` | 是否连接真实目标 | false | validator.py |
| `usable_for_formal_finding` | 是否可用于正式发现 | false（draft） | validator.py |
| `target_id` | 目标靶场标识 | 仅限 local_* | config_index.py |
| `provider_local_only` | provider 限本地 | true | adapter 入口 |
| `no_external_api_refs` | 无外部 API 引用 | true | adapter 入口 |
| `no_credential_refs` | 无凭证引用 | true | adapter 入口 |

## 预留真实执行函数（需人工 Go/No-Go）

以下函数当前为 dry-run 桩，如需启用真实执行，每次均需人工逐项确认安全边界：

| 函数 | 位置 | 真实执行行为 | 人工确认项 |
|------|------|-------------|-----------|
| `dry_run_execute()` → `real_execute()` | `adapter/dry_run_execute.py` | 调用 `promptfoo eval -c <config> --output <path>` | 目标仅限 sandbox / provider 仅限本地 / 无凭证引用 |
| `normalizer.normalize_execution()` | `normalizer.py` | 读取真实 promptfoo JSON 输出 | 结果来源仅限 sandbox / 无敏感数据泄露 |
| `evidence_writer.write_with_redaction()` | `evidence_writer.py` | 写入前执行敏感数据脱敏 | 脱敏规则覆盖 honeytoken / fake secret / 内部路径 |
| `finding_prep.generate_candidates()` | `finding_prep.py` | 基于真实失败结果生成 finding | 仅限 fail/error 结果 / 不生成 formal finding |
| `judge_prep.prepare_batch()` | `judge_prep.py` | 准备 DeepSeek Judge 批量入参 | 入参不包含 raw evidence / 仅含归一化摘要 |

## 总结

| 指标 | 值 |
|------|-----|
| Phase | 35 |
| 主题 | Promptfoo 集成框架 |
| 新文件数 | 12（`tool_integrations/promptfoo/` 下 10 个 + `adapter/` 下 2 个） |
| 发现的 draft suite | 7 |
| Draft 总用例数 | 104 |
| 发现的 generated testcase | 5 文件 / 52 用例 |
| 发现的 runner 配置 | 7 |
| 发现的 runner 脚本 | 4 |
| 已有的证据文件 | 5 |
| 已有证据测试数 | 59 |
| 已有证据断言数 | 153 |
| 已有证据测试通过率 | 100%（0 fail / 0 error） |
| 已有证据总大小 | 342 KB |
| 注册 profile 数 | 5（agent / chatbot / rag / manual_ui / generic_agent_harness） |
| 安全标志位 | 9 |
| 预留真实执行函数 | 5 |
| 需人工 Go/No-Go 确认 | 是（所有真实执行函数） |
| 是否运行 promptfoo eval | 否 |
| 是否连接被测 API | 否 |
| 是否调用 DeepSeek | 否 |
| 状态 | 框架搭建完成，待人工 Go/No-Go 后接入真实执行链路 |
