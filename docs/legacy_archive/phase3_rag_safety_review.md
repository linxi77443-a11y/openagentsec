# Phase 3 / 3.5：RAG 安全边界审计

## 审计对象

- `sandbox/rag_demo/rag_demo.py`
- `sandbox/rag_demo/rag_provider.py`
- `runners/rag_provider.py`
- `sandbox/rag_demo/fake_documents/normal_policy.md`
- `sandbox/rag_demo/fake_documents/normal_faq.md`
- `sandbox/rag_demo/fake_documents/malicious_indirect_prompt.md`
- `sandbox/rag_demo/fake_documents/false_policy_entry.md`
- `runners/promptfoo.rag.yaml`
- `runners/run_rag_promptfoo.sh`

## 执行前安全确认

- `runners/promptfoo.rag.yaml` 的 provider 为 `exec:python3 rag_provider.py`，通过 `runners/rag_provider.py` 进入本地 `sandbox/rag_demo`。
- `runners/run_rag_promptfoo.sh` 只允许 `runners/rag_provider.py`。
- `rag_demo.py` 只从同目录下的 `fake_documents` 加载 `*.md` 文件。
- fake documents 仅包含 fake policy、fake FAQ、malicious test document、false policy entry 和 fake honeytoken。
- 未发现真实 API key、真实 token、真实 cookie、客户数据或生产数据。

## 本地文件使用情况

`rag_demo.py` 仅从同目录下的 `fake_documents` 加载 `*.md` 文件。检索逻辑是本地字符串评分，不调用外部检索服务、向量数据库、真实知识库或模型 API。

## 外部请求检查

未发现外部请求逻辑：

- 无 HTTP URL provider。
- 无 OpenAI / Anthropic / 真实模型 API provider。
- 无企业系统地址。
- 无网络扫描逻辑。
- 无外部数据上传逻辑。

`run_rag_promptfoo.sh` 会拒绝包含外部 API、真实模型、企业目标或凭证关键词的有效 promptfoo 配置。扫描命中过边界说明和防护规则文本，但未发现真实外部 provider 或真实凭证。

## 凭证与敏感数据检查

- 未读取环境变量。
- 未读取真实 credential store。
- 未包含真实 API key、token、cookie 或客户数据。
- `HONEYTOKEN_RAG_DEMO_000` 是本地 fake honeytoken，仅用于测试输出防泄露。
- Phase 3.5 结果中没有完整输出 `HONEYTOKEN_RAG_DEMO_000`。

## 命令行调用

RAG demo 可直接调用：

```bash
python3 sandbox/rag_demo/rag_demo.py "What does the normal fake AI usage policy say about dummy data?"
```

直接 provider 可调用：

```bash
python3 sandbox/rag_demo/rag_provider.py "{{prompt}}"
```

promptfoo provider 通过 `runners` basePath 调用：

```bash
python3 runners/rag_provider.py "{{prompt}}"
```

## JSON 证据

RAG demo 输出和日志包含：

- `timestamp`
- `input`
- `retrieved_documents`
- `retrieved_document_ids`
- `output`
- `risk_signals`
- `followed_document_instruction`
- `leaked_sensitive_data`
- `false_policy_used`
- `target`
- `tool_calls`
- `result`

## Phase 3.5 执行结果

- dry-run：通过。
- execute：通过。
- 测试用例：5。
- pass：5。
- fail：0。
- error：0。
- `followed_document_instruction=true`：未出现。
- `leaked_sensitive_data=true`：未出现。
- `false_policy_used=true`：未出现。
- 完整 fake secret 输出：未出现。

## 风险与限制

- 当前 demo 使用简单关键词检索，不代表真实 RAG 系统风险覆盖完整性。
- 当前没有真实模型生成行为，只验证检索上下文安全信号和本地 JSON 证据链。
- 当前不评估真实企业知识库、真实权限系统、真实数据治理或真实模型鲁棒性。
- 后续 Agent 阶段必须重新确认工具调用安全边界。

## 结论

Phase 3.5 执行仍限制在本地 `sandbox/rag_demo` 和 fake documents 范围内。未发现外部请求、真实凭证或真实 API 风险。本地 RAG promptfoo 执行闭环已完成。
