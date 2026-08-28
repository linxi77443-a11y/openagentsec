# Phase 6.7：脱敏控制后的本地复测复盘

## 复测目标

Phase 6.7 用于验证 Phase 6.6 新增的 evidence / JSONL log 脱敏控制在本地 execute 后仍然有效。

本阶段只复测本地 Chatbot、RAG、Agent 三类 sandbox，不新增 provider，不连接真实 API、真实模型、企业系统或外部网络目标。

## 执行边界

- 只允许测试本地 sandbox。
- 只允许执行 Chatbot、RAG、Agent 三类本地 promptfoo 测试。
- 不新增外部 provider。
- 不连接真实 API、真实模型、企业系统或外部网络目标。
- 不读取真实凭证、真实 API key、真实环境变量。
- 不访问真实邮件、真实日历、真实文件系统敏感路径。
- fake write action 必须保持 dry-run only。
- 允许更新本地 evidence：
  - `reports/evidence/promptfoo_chatbot_result.json`
  - `reports/evidence/promptfoo_rag_result.json`
  - `reports/evidence/promptfoo_agent_result.json`
- 允许写入本地 JSONL 日志，但日志必须脱敏。
- 不进入 garak、PyRIT、AgentDojo 或真实目标测试阶段。

## 执行前状态

执行前 `git status --short` 只显示运行时缓存和本地 JSONL 日志变更：

```text
 M sandbox/chatbot_demo/__pycache__/chatbot.cpython-311.pyc
 M sandbox/chatbot_demo/chatbot_log.jsonl
 M sandbox/rag_demo/rag_log.jsonl
```

未发现源码、配置或文档存在未提交变更，因此继续执行本地复测。

## 预检查与 dry-run

已执行：

```bash
bash runners/run_quality_check.sh
bash runners/run_promptfoo.sh
bash runners/run_rag_promptfoo.sh
bash runners/run_agent_promptfoo.sh
```

结果：

- quality check：通过。
- Chatbot dry-run：通过，只打印本地 promptfoo 命令，不执行测试。
- RAG dry-run：通过，只打印本地 promptfoo 命令，不执行测试。
- Agent dry-run：通过，只打印本地 promptfoo 命令，不执行测试。

## 初次 execute 结果

已按顺序执行：

```bash
bash runners/run_promptfoo.sh --execute
bash runners/run_rag_promptfoo.sh --execute
bash runners/run_agent_promptfoo.sh --execute
```

结果：

| 测试对象 | 用例数量 | Pass / Fail / Error | 断言 Pass / Fail |
|---|---:|---|---|
| Chatbot | 9 | 9 / 0 / 0 | 18 / 0 |
| RAG | 12 | 12 / 0 / 0 | 18 / 0 |
| Agent | 10 | 10 / 0 / 0 | 14 / 0 |

## 发现的问题

初次 execute 后，sandbox JSONL 日志已经脱敏，但 promptfoo evidence 文件仍在测试输入、配置元数据或断言文本中保留完整测试 secret 前缀或邮箱样例。

扫描结果显示：

- `reports/evidence/promptfoo_chatbot_result.json` 仍包含 `FAKE_SECRET_` 前缀。
- `reports/evidence/promptfoo_rag_result.json` 仍包含 `HONEYTOKEN_` 前缀。
- `reports/evidence/promptfoo_agent_result.json` 仍包含 `HONEYTOKEN_` 前缀和 email-like 字符串。
- `sandbox/**/*_log.jsonl` 未发现完整 `HONEYTOKEN_`、`FAKE_SECRET_`、`DUMMY_TOKEN_` 前缀。

判定：这是脱敏逻辑接入位置不完整。provider 输出和 sandbox 日志已脱敏，但 promptfoo 自身生成的 evidence 会包含测试用例输入、变量或断言元数据，因此还需要对 promptfoo 写出的 result JSON 做本地后处理脱敏。

这不是测试断言问题，也不是真实系统风险；没有降低任何安全断言。

## 修复方式

在三个本地执行脚本的 `--execute` 路径中，在 promptfoo 写出 JSON evidence 后追加 `utils.redaction.redact_json()` 后处理：

- `runners/run_promptfoo.sh`
- `runners/run_rag_promptfoo.sh`
- `runners/run_agent_promptfoo.sh`

修复后，对现有 evidence 做一次离线脱敏，并重新运行 quality check。

## 修复后复测结果

修复后再次按顺序执行三类本地 `--execute`：

```bash
bash runners/run_promptfoo.sh --execute
bash runners/run_rag_promptfoo.sh --execute
bash runners/run_agent_promptfoo.sh --execute
```

最终结果：

| 测试对象 | 用例数量 | Pass / Fail / Error | 断言 Pass / Fail |
|---|---:|---|---|
| Chatbot | 9 | 9 / 0 / 0 | 18 / 0 |
| RAG | 12 | 12 / 0 / 0 | 18 / 0 |
| Agent | 10 | 10 / 0 / 0 | 14 / 0 |

最终 quality check：通过。

## 最终脱敏检查

最终 evidence 与 JSONL log 扫描结果：

| 文件 | 完整 secret 前缀 | email-like | bearer-like | 脱敏标记数量 |
|---|---:|---:|---:|---:|
| `reports/evidence/promptfoo_chatbot_result.json` | 0 | 0 | 0 | 9 |
| `reports/evidence/promptfoo_rag_result.json` | 0 | 0 | 0 | 9 |
| `reports/evidence/promptfoo_agent_result.json` | 0 | 0 | 0 | 31 |
| `sandbox/chatbot_demo/chatbot_log.jsonl` | 0 | 0 | 0 | 0 |
| `sandbox/rag_demo/rag_log.jsonl` | 0 | 0 | 0 | 0 |
| `sandbox/agent_demo/agent_log.jsonl` | 0 | 0 | 0 | 46 |

确认未发现完整：

- `HONEYTOKEN_`
- `FAKE_SECRET_`
- `DUMMY_TOKEN_`
- email-like 字符串
- bearer token-like 字符串

## 关键布尔字段可用性

脱敏后字段结构未被删除，关键布尔字段仍可用于断言和复盘：

- RAG evidence 保留：
  - `leaked_sensitive_data`
  - `followed_document_instruction`
  - `false_policy_used`
- Agent evidence 保留：
  - `leaked_secret`
  - `dry_run`
  - `sent`

Chatbot 当前不使用上述 RAG / Agent 专属布尔字段。

## 安全结论

Phase 6.7 证明：

- Phase 6.6 的 sandbox 日志脱敏路径有效。
- provider 输出层脱敏有效。
- promptfoo evidence 还需要执行脚本级后处理脱敏，已补齐。
- 修复后，三类本地增强测试集仍全部通过，没有降低安全断言。
- fake write action 仍保持 dry-run only。
- 未发现真实 API、真实模型、企业系统、外部网络目标或真实凭证访问迹象。

当前结论只适用于本地 fake sandbox，不代表真实企业系统安全结论。
