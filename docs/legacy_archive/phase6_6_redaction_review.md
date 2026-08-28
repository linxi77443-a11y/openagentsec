# Phase 6.6：证据与日志脱敏加固复盘

## 为什么要做 evidence / log 脱敏

Phase 6.5 发现 Agent 工具调用已经被阻断，但 evidence / log 的 `input` 字段曾回显完整 honeytoken。虽然该值是本地 fake honeytoken，没有造成外部影响，但说明测试证据本身也可能成为敏感信息载体。

Phase 6.6 的目标是把脱敏控制前移到 sandbox 输出和日志写入路径，让 evidence、JSONL log、provider 输出都尽量不保留完整测试 secret。

## 增加的脱敏规则

新增统一脱敏模块：`utils/redaction.py`。

规则包括：

- `HONEYTOKEN_*` -> `[REDACTED_HONEYTOKEN]`
- `FAKE_SECRET_*` -> `[REDACTED_FAKE_SECRET]`
- `DUMMY_TOKEN_*` -> `[REDACTED_DUMMY_TOKEN]`
- email-like 字符串 -> `[REDACTED_EMAIL]`
- bearer token-like 字符串 -> `[REDACTED_TOKEN]`
- API key-like / token-like 测试字符串 -> `[REDACTED_TOKEN]`

`redact_json(obj)` 会递归处理 dict / list / string，不删除字段，只替换字段值中的敏感片段。

## 接入脱敏的文件

- `sandbox/agent_demo/agent.py`
  - Agent 内部仍使用原始输入进行风险判断和 `leaked_secret` 判断。
  - 返回 evidence 和写入 JSONL log 前统一 `redact_json(event)`。
- `runners/agent_provider.py`
  - provider 输出层再次使用 `redact_json()` 兜底。
- `sandbox/agent_demo/agent_provider.py`
  - 直接调用 provider 输出层也使用 `redact_json()` 兜底。
- `sandbox/rag_demo/rag_demo.py`
  - RAG 内部先完成检索、风险判断和泄露布尔判断，再对 event 脱敏后返回和写日志。
- `runners/rag_provider.py`
  - provider 输出层使用 `redact_json()` 兜底。
- `sandbox/rag_demo/rag_provider.py`
  - 直接调用 provider 输出层使用 `redact_json()` 兜底。
- `sandbox/chatbot_demo/chatbot.py`
  - Chatbot 日志写入和 CLI 输出使用 `redact_json()`。
- `runners/chatbot_provider.py`
  - promptfoo provider 输出层使用 `redact_json()`。

## Chatbot risk_signals 增强

Phase 6.6 在不降低原有断言的前提下，增加更细粒度且稳定的 risk signals：

- `multilingual_prompt_injection`
- `system_prompt_paraphrase_attempt`
- `encoded_instruction_attempt`

原有兼容信号仍保留：

- `possible_prompt_injection`
- `possible_system_prompt_exposure`
- `possible_secret_request`
- `possible_instruction_extraction`
- `possible_roleplay_bypass`

## quality check 增强

`runners/run_quality_check.sh` 新增检查：

- `reports/evidence/*.json` 不应出现完整 `HONEYTOKEN_`、`FAKE_SECRET_`、`DUMMY_TOKEN_` 前缀。
- `sandbox/**/*_log.jsonl` 不应出现完整 `HONEYTOKEN_`、`FAKE_SECRET_`、`DUMMY_TOKEN_` 前缀。
- `.env` / `.env.*` 仍必须被 `.gitignore` 排除。
- `*_log.jsonl` 仍必须被 `.gitignore` 排除。

## 是否执行了 --execute

否。Phase 6.6 只允许 quality check 和 dry-run，本阶段未执行任何 `--execute`。

## 当前是否仍然只限本地 sandbox

是。Phase 6.6 只修改本地项目文件，只运行本地质量检查和 dry-run，不连接真实 API、真实模型、企业系统或外部网络目标。

## 后续如果进入 garak / PyRIT / AgentDojo，如何保持 evidence 脱敏

- 先使用本地 mock provider / fake tools。
- 将 `utils.redaction.redact_json()` 作为所有 provider 输出和日志写入的统一兜底。
- 对新工具生成的 evidence 增加质量检查扫描。
- 不依赖完整 secret 输出作为断言依据，改用 `leaked_secret`、`contains_honeytoken`、`redaction_applied` 等布尔字段。
- 对外部工具的默认报告输出先做本地审阅，再决定是否归档。

## Phase 6.6 执行结果

已运行：

```bash
bash runners/run_quality_check.sh
bash runners/run_promptfoo.sh
bash runners/run_rag_promptfoo.sh
bash runners/run_agent_promptfoo.sh
```

结果：

- quality check：通过。
- Chatbot dry-run：通过。
- RAG dry-run：通过。
- Agent dry-run：通过。
- `--execute`：未执行。

首次 quality check 曾发现既有 Phase 6.5 evidence 中仍包含完整测试 secret 前缀。随后使用 `utils.redaction.redact_json()` 对本地 evidence 和 JSONL logs 做离线脱敏，再次运行 quality check 后通过。
