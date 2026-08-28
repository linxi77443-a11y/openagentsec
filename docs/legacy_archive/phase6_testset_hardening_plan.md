# Phase 6：本地测试集增强与质量校验计划

## Phase 6 目标

Phase 6 只增强现有本地 sandbox 测试集，并建立质量校验脚本，目标是提高 Chatbot、RAG、Agent 三类本地测试的覆盖面和一致性。

本阶段目标：

- 增强 Chatbot prompt injection / system prompt exposure 测试变体。
- 增强 RAG poisoning / false entry / indirect injection / data leakage 测试变体。
- 增强 Agent tool misuse / schema validation / context poisoning / tool exfiltration 测试变体。
- 新增本地 fake documents，不接入真实知识库。
- 新增统一质量校验脚本。
- 只运行 dry-run 和质量检查，不执行 `--execute`。

## 不做什么

Phase 6 不做以下事项：

- 不接入 garak、PyRIT、AgentDojo。
- 不连接真实 API。
- 不连接真实模型。
- 不接入企业系统或外部网络目标。
- 不读取真实凭证、真实 token 或环境变量中的 API key。
- 不访问真实邮件、真实日历、真实文件系统敏感路径。
- 不执行任何真实写操作。
- 不运行 `bash runners/run_promptfoo.sh --execute`。
- 不运行 `bash runners/run_rag_promptfoo.sh --execute`。
- 不运行 `bash runners/run_agent_promptfoo.sh --execute`。

## Chatbot 测试增强方向

新增或增强：

1. 中文 prompt injection。
2. 英文 prompt injection。
3. 中英混合 prompt injection。
4. 角色扮演绕过。
5. system prompt paraphrase 泄露尝试。
6. base64 / markdown / quote block 包装的指令注入。
7. 要求输出内部规则摘要的测试。

质量要求：

- 不包含真实攻击目标。
- 不包含真实凭证。
- expected behavior 必须偏防守。
- 输出必须仍为 JSON evidence。
- 断言必须检查 `policy_triggered`、`leaked_system_prompt` 和 `risk_signals`。

## RAG 测试增强方向

新增本地 fake documents：

- `sandbox/rag_demo/fake_documents/hidden_instruction.md`
- `sandbox/rag_demo/fake_documents/stale_policy_entry.md`
- `sandbox/rag_demo/fake_documents/multilingual_injection.md`
- `sandbox/rag_demo/fake_documents/fake_citation_entry.md`

新增或增强：

1. 隐藏指令污染。
2. 过期政策条目。
3. 伪造引用来源。
4. 多语言 indirect prompt injection。
5. 文档中夹带 fake token。
6. 要求模型优先相信恶意文档。
7. 要求忽略系统规则并泄露上下文。

质量要求：

- RAG demo 仍只读取 `fake_documents`。
- 不连接真实知识库。
- 不输出完整 honeytoken。
- `false_policy_used`、`leaked_sensitive_data`、`followed_document_instruction` 必须可被断言。

## Agent 测试增强方向

新增或增强：

1. tool schema validation 测试。
2. 工具参数污染测试。
3. 多步工具链滥用测试。
4. fake secret 通过 fake email 外传测试。
5. 恶意上下文诱导工具调用测试。
6. 未授权工具名调用测试。
7. fake write action 必须 dry-run 测试。
8. 工具参数中出现 honeytoken 时必须阻断测试。

质量要求：

- fake tool allowlist 不变：`search_fake_docs`、`send_fake_email`、`read_fake_calendar`、`read_fake_secret`。
- `send_fake_email` 仍只能 dry-run。
- 不允许真实发信。
- 不读取真实文件系统敏感路径。
- 不读取环境变量。
- 不访问外部网络。

## 质量校验标准

`runners/run_quality_check.sh` 应检查：

- 所有 promptfoo 配置 provider 只指向本地 provider。
- 配置中不出现真实 API、真实模型、真实凭证、企业系统、外部网络关键词。
- evidence 路径位于 `reports/evidence`。
- `*_log.jsonl` 被 `.gitignore` 排除。
- `.env` / `.env.*` 被 `.gitignore` 排除。
- Chatbot / RAG / Agent 三类配置都能 dry-run。
- README、evidence index、coverage matrix 包含 Phase 6 或最新阶段说明。

## 需要人工确认的点

进入 Phase 6.5 本地 execute 前，需要人工确认：

1. 是否允许运行 Chatbot `--execute`。
2. 是否允许运行 RAG `--execute`。
3. 是否允许运行 Agent `--execute`。
4. 是否仍只测试本地 sandbox。
5. 是否仍不接入真实 API、真实模型、企业系统、外部网络目标或真实凭证。
6. 是否允许更新对应 evidence 文件。
7. 是否允许写入本地日志且日志不包含真实敏感信息。
