# Phase 2：promptfoo 本地测试闭环

## 目标

将项目从文档和骨架推进到最小可运行测试闭环，范围仅限：

```text
sandbox/chatbot_demo
```

## 当前状态

- 已检查 Node.js：v22.22.3。
- 已检查 npm：10.9.8。
- 已安装并验证 promptfoo：0.121.15。
- 已生成安装说明：`docs/promptfoo_install.md`。
- 已完善 chatbot JSON 输出。
- 已完善 promptfoo 配置：`runners/promptfoo.chatbot.yaml`。
- 已创建本地 provider 包装器：`runners/chatbot_provider.py`。
- 已增强 prompt injection 和 system prompt exposure 测试数据。
- 已更新执行脚本：`runners/run_promptfoo.sh`。
- 已创建报告生成流程：`docs/reporting_workflow.md`。
- 已执行 Phase 2.5 本地验证，结果为 5 passed，0 failed，0 errors。
- 已生成执行复盘：`docs/phase2_5_execution_review.md`。

## 安全边界

- 默认 dry-run。
- 只允许本地 sandbox/chatbot_demo。
- 测试目标必须来自 `targets/local_sandbox.yaml`。
- 不允许真实 API、真实模型、企业系统或外部网络目标。
- 不允许真实凭证。
- 不允许生产系统。
- 不新增高风险测试。
- 不运行 `promptfoo redteam setup`。
- 不自动进入 RAG 或 Agent 阶段。

## 测试覆盖

当前 promptfoo 配置覆盖：

1. 普通安全问答测试。
2. Direct prompt injection。
3. System prompt exposure。
4. System instruction extraction。
5. Data leakage。

## dry-run

```bash
bash runners/run_promptfoo.sh
```

预期输出：

```text
Mode: dry-run
Would run: promptfoo eval -c runners/promptfoo.chatbot.yaml --output reports/evidence/promptfoo_chatbot_result.json
No test executed.
```

## execute

需要人工确认只做本地验证后执行：

```bash
bash runners/run_promptfoo.sh --execute
```

结果输出到：

```text
reports/evidence/promptfoo_chatbot_result.json
```

本地交互日志输出到：

```text
sandbox/chatbot_demo/chatbot_log.jsonl
```

## Phase 2.5 执行结果

- 执行时间：2026-06-16T03:35:43Z
- 执行命令：`bash runners/run_promptfoo.sh --execute`
- promptfoo：0.121.15
- Provider：`exec:python3 chatbot_provider.py`
- 测试范围：仅 `sandbox/chatbot_demo`
- 通过：5
- 失败：0
- 错误：0
- 断言通过：11
- 断言失败：0
- token / cost：0 / 0
- 外部请求迹象：未在结果文件和本地日志中发现
- 当前闭环：已完成最小本地可运行测试闭环

## 证据

```text
reports/evidence/promptfoo_chatbot_result.json
sandbox/chatbot_demo/chatbot_log.jsonl
reports/sample_report.md
docs/phase2_5_execution_review.md
```

## 后续计划

1. 保留当前 chatbot promptfoo 用例作为回归测试。
2. 如要进入 Phase 3 RAG demo，先更新安全边界、目标 allowlist、provider allowlist 和报告模板。
3. 如要进入 Agent demo，先定义 fake tool 调用日志、工具 allowlist 和人工确认项。
4. 不接入真实模型 API、企业系统或外部网络目标，除非另行完成授权与安全评审。
