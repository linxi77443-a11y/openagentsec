# 敏感信息处理与脱敏说明

## 当前项目中的 fake secret / honeytoken 示例

本项目只使用本地 fake data，不使用真实凭证。当前示例包括：

- Chatbot：`FAKE_SECRET_CHATBOT_DEMO_12345`
- RAG：`HONEYTOKEN_RAG_DEMO_000`
- Agent：`HONEYTOKEN_AGENT_DEMO_123456`
- 未来测试可使用 `DUMMY_TOKEN_*` 形式表示 dummy token。

这些值不是可用凭证，但仍应按敏感信息处理，因为 evidence 和日志会被复制、归档、复盘或作为报告模板复用。

## evidence 中可能出现敏感信息的位置

promptfoo evidence 通常可能在以下字段中保留原始输入或输出：

- `response.output`
- `vars.input`
- `prompt.raw`
- `testCase.vars.input`
- `tool_args`
- `tool_result`
- `retrieved_documents`
- `output`
- `risk_signals`

即使工具调用被阻断，原始 prompt 仍可能包含 honeytoken、fake secret、email-like 字符串或 token-like 字符串。

## JSONL 日志中可能出现敏感信息的位置

本地 sandbox 日志通常写入：

- `sandbox/chatbot_demo/chatbot_log.jsonl`
- `sandbox/rag_demo/rag_log.jsonl`
- `sandbox/agent_demo/agent_log.jsonl`

JSONL 日志中需要重点检查：

- `input`
- `output`
- `retrieved_documents`
- `tool_calls`
- `tool_args`
- `tool_result`
- `risk_signals`
- `denied_reason`

## 脱敏原则

### prompt / input

用户输入或测试输入可以用于内部风险判断，但写入 evidence 或 log 前应替换敏感片段。

### tool_args

工具参数可能包含 email、token、path、body 等，应递归脱敏，不删除字段。

### tool_result

工具返回值可能包含 secret、token、body preview 或检索片段，应递归脱敏。

### output

模型输出或 sandbox 输出应保留结构和判断字段，但替换敏感片段。

### risk_signals

风险信号应稳定、可引用，但不应把完整 secret 放入 signal 名称。

## 为什么测试 secret 也要脱敏

测试 secret 不是生产凭证，但仍需要脱敏：

- evidence 可能进入长期报告或模板。
- 日志可能被复制给其他工具或人员。
- honeytoken 的完整值出现在报告中会降低检测价值。
- 真实企业评估中，同样路径可能承载真实敏感信息。
- 对 fake data 也脱敏能形成稳定的工程习惯。

## 统一脱敏格式

项目使用固定替换标记：

- `HONEYTOKEN_*` -> `[REDACTED_HONEYTOKEN]`
- `FAKE_SECRET_*` -> `[REDACTED_FAKE_SECRET]`
- `DUMMY_TOKEN_*` -> `[REDACTED_DUMMY_TOKEN]`
- email-like 字符串 -> `[REDACTED_EMAIL]`
- bearer token-like / API key-like 字符串 -> `[REDACTED_TOKEN]`

## 企业评估时 evidence 脱敏建议

- 在执行前定义 evidence 保留字段和脱敏策略。
- 不把完整 prompt、tool body、retrieved chunk 默认写入长期日志。
- 对 secret、email、URL、路径、账号 ID、ticket ID、客户名执行分类脱敏。
- 用布尔字段表达是否泄露，如 `leaked_secret=true/false`，不要依赖输出完整 secret 来证明问题。
- evidence 文件应有访问权限、保留周期和删除流程。
- 非本地目标评估必须先完成授权和数据处理确认。
