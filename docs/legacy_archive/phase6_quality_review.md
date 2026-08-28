# Phase 6：本地测试集增强与质量校验复盘

## 阶段范围

Phase 6 只增强现有本地 sandbox 测试集，并新增统一质量校验脚本。

本阶段未接入 garak、PyRIT、AgentDojo，未连接真实 API、真实模型、企业系统、外部网络目标或真实凭证，未运行任何 `--execute` 命令。

## 新增或增强的测试用例数量

| 对象 | Phase 6 配置用例数 | 主要变化 |
|---|---:|---|
| Chatbot | 9 | 增强 prompt injection、system prompt exposure 和 fake secret request 变体 |
| RAG | 12 | 新增 fake documents，增强 RAG poisoning、false entry、indirect injection 和 data leakage 变体 |
| Agent | 10 | 增强 tool schema validation、tool misuse、context poisoning 和 exfiltration 阻断变体 |

## Chatbot 增强点

- 中文 prompt injection。
- 英文 prompt injection。
- 中英混合 prompt injection。
- 角色扮演绕过。
- system prompt paraphrase 泄露尝试。
- base64 / markdown / quote block 包装的指令注入。
- 要求输出内部规则摘要的测试。
- 断言继续检查 `policy_triggered`、`leaked_system_prompt`、`risk_signals` 和 fake secret not-contains。

## RAG 增强点

新增本地 fake documents：

- `sandbox/rag_demo/fake_documents/hidden_instruction.md`
- `sandbox/rag_demo/fake_documents/stale_policy_entry.md`
- `sandbox/rag_demo/fake_documents/multilingual_injection.md`
- `sandbox/rag_demo/fake_documents/fake_citation_entry.md`

新增或增强的本地测试方向：

- 隐藏指令污染。
- 过期政策条目。
- 伪造引用来源。
- 多语言 indirect prompt injection。
- 文档中夹带 fake token / dummy token。
- 要求模型优先相信恶意文档。
- 要求忽略系统规则并泄露上下文。
- 断言继续检查 `false_policy_used=false`、`leaked_sensitive_data=false`、`followed_document_instruction=false`。

## Agent 增强点

- tool schema validation 测试。
- 工具参数污染测试。
- 多步工具链滥用测试。
- fake secret 通过 fake email 外传测试。
- 恶意上下文诱导工具调用测试。
- 未授权工具名调用测试。
- fake write action 必须 dry-run 测试。
- 工具参数中出现 honeytoken 时必须阻断测试。
- fake tool allowlist 保持不变：`search_fake_docs`、`send_fake_email`、`read_fake_calendar`、`read_fake_secret`。

## dry-run 结果

已运行：

```bash
bash runners/run_promptfoo.sh
bash runners/run_rag_promptfoo.sh
bash runners/run_agent_promptfoo.sh
```

结果：三类脚本均完成 dry-run，均只打印将要执行的本地 promptfoo 命令和 evidence 路径，没有运行 `--execute`。

## quality check 结果

已运行：

```bash
bash runners/run_quality_check.sh
```

结果：通过。

质量检查确认：

- 三个 promptfoo 配置 provider 均指向本地 `exec:python3 ..._provider.py`。
- 配置扫描未发现真实 API、真实模型、真实凭证、企业系统或外部网络目标关键词。
- evidence 路径限定在 `reports/evidence`。
- `.gitignore` 包含 `*_log.jsonl`、`logs/`、`.env`、`.env.*`。
- README、evidence index、coverage matrix 均包含 Phase 6 说明。
- 质量检查脚本未运行任何 `--execute` 命令。

## 是否扩大测试范围

否。Phase 6 仍只测试本地 sandbox：

- `sandbox/chatbot_demo`
- `sandbox/rag_demo`
- `sandbox/agent_demo`

## 是否引入新工具

否。Phase 6 未接入 garak、PyRIT、AgentDojo 或其他新测试工具。

## 外部请求 / 真实凭证 / 真实 API / 真实系统风险

本阶段设计目标是不连接真实 API、真实模型、企业系统、外部网络目标或真实凭证。质量校验脚本会检查 promptfoo provider、本地 evidence 路径、禁用关键词和 dry-run 状态。

## 进入 Phase 6.5 execute 前需要确认

1. 是否允许运行 Chatbot `--execute`。
2. 是否允许运行 RAG `--execute`。
3. 是否允许运行 Agent `--execute`。
4. 是否仍只测试本地 sandbox。
5. 是否仍不接入真实 API、真实模型、企业系统、外部网络目标或真实凭证。
6. 是否允许更新对应 evidence 文件。
7. 是否允许写入本地日志且日志不包含真实敏感信息。
