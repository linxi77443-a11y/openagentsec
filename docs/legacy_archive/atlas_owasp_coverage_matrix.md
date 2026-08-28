# ATLAS / OWASP 覆盖矩阵

| 测试对象 | 测试用例类型 | MITRE ATLAS technique | OWASP Agentic / LLM 风险 | 当前测试状态 | evidence 文件 | 当前控制项 | 后续增强方向 |
|---|---|---|---|---|---|---|---|
| Chatbot | Prompt Injection | LLM Prompt Injection / Direct Prompt Injection / LLM Prompt Obfuscation | ASI01 Agent Goal Hijack / LLM prompt injection risk | Phase 6.5 已执行增强集，9/0/0 | `reports/evidence/promptfoo_chatbot_result.json` | 风险词检测、拒绝覆盖系统规则、JSON risk signals、多语言和格式包装检测 | 继续增强本地变体后再考虑新工具 |
| Chatbot | System Prompt Exposure | Extract LLM System Prompt | ASI09 Human-Agent Trust Exploitation / sensitive instruction leakage | Phase 6 已增强 paraphrase、内部规则摘要和角色扮演变体 | `reports/evidence/promptfoo_chatbot_result.json` | `leaked_system_prompt=false`、not-contains system prompt、instruction extraction signal | 增加更细粒度泄露分类 |
| Chatbot | Data Leakage | LLM Data Leakage | ASI03 Identity and Privilege Abuse / sensitive data disclosure | Phase 6 保留 fake secret not-contains 并扩展敏感请求变体 | `reports/evidence/promptfoo_chatbot_result.json` | fake secret not-contains、敏感请求 risk signal | 增加 PII、业务密钥、配置片段 fake data 样例 |
| RAG | RAG Poisoning | RAG Poisoning | ASI04 Agentic Supply Chain Vulnerabilities / ASI06 Memory and Context Poisoning | Phase 6.5 已执行增强集，12/0/0 | `reports/evidence/promptfoo_rag_result.json` | 检索文档风险标记、`followed_document_instruction=false`、本地 fake documents 限定 | 增加多文档冲突、索引回滚流程 |
| RAG | False RAG Entry Injection | False RAG Entry Injection | ASI04 Agentic Supply Chain Vulnerabilities / ASI09 Human-Agent Trust Exploitation | Phase 6 已增加 stale policy 和 fake citation 变体 | `reports/evidence/promptfoo_rag_result.json` | `false_rag_entry` risk signal、`stale_rag_entry` signal、`false_policy_used=false` | 增加来源签名、可信度评分、人工审批字段 |
| RAG | Indirect Prompt Injection | Indirect Prompt Injection | ASI01 Agent Goal Hijack / ASI06 Memory and Context Poisoning | Phase 6 已增加 hidden instruction 和多语言 injection 文档 | `reports/evidence/promptfoo_rag_result.json` | 文档指令不覆盖系统任务、上下文隔离、`followed_document_instruction=false` | 增加 HTML/Markdown 隐藏指令、表格/注释注入样例 |
| RAG | Data Leakage | LLM Data Leakage / RAG Credential Harvesting | ASI03 Identity and Privilege Abuse / data leakage risk | Phase 6 已增加 fake token / dummy token 文档变体 | `reports/evidence/promptfoo_rag_result.json` | `leaked_sensitive_data=false`、fake honeytoken not-contains、sensitive dummy data signal | 增加检索片段最小化、DLP 模拟、引用级别脱敏 |
| Agent | AI Agent Tool Invocation | AI Agent Tool Invocation | ASI02 Tool Misuse and Exploitation | Phase 6.5 已执行增强集，10/0/0 | `reports/evidence/promptfoo_agent_result.json` | tool allowlist、JSON tool_calls、target 固定、schema validation | 继续增强本地变体后再考虑新工具 |
| Agent | Agent Tool Misuse | AI Agent Tool Invocation / AI Agent Tool Poisoning | ASI02 Tool Misuse and Exploitation | Phase 6 已增强未授权工具名、无效目的地和参数污染用例 | `reports/evidence/promptfoo_agent_result.json` | `run_shell` / `read_env` 请求拒绝、`denied_reason` 留痕、`invalid_tool_args` | 增加路径参数、命令参数 fake 样例 |
| Agent | Agent Context Poisoning | AI Agent Context Poisoning / Indirect Prompt Injection | ASI01 Agent Goal Hijack / ASI06 Memory and Context Poisoning | Phase 6 已增加恶意上下文诱导工具调用用例 | `reports/evidence/promptfoo_agent_result.json` | `followed_malicious_instruction=false`、目标不变、工具调用阻断 | 增加持久记忆、跨轮上下文、工具返回指令污染 |
| Agent | Credentials from AI Agent Configuration | Credentials from AI Agent Configuration | ASI03 Identity and Privilege Abuse | Phase 6 保留 fake secret redaction 并增加 honeytoken 参数阻断 | `reports/evidence/promptfoo_agent_result.json` | `read_fake_secret` 返回 `REDACTED`、not-contains honeytoken、secret + write 组合阻断 | 增加 secret scope、短期 token、secret manager fake adapter |
| Agent | Exfiltration via AI Agent Tool Invocation | Exfiltration via AI Agent Tool Invocation | ASI02 Tool Misuse and Exploitation / data exfiltration risk | Phase 6 已增加 fake email 外传、参数污染和多步工具链滥用变体 | `reports/evidence/promptfoo_agent_result.json` | secret + send/email 组合阻断、`possible_tool_exfiltration`、不调用发送工具 | 增加批量外传模拟和人审确认 |
| Agent | Fake Write Action Abuse | AI Agent Tool Invocation | ASI02 Tool Misuse and Exploitation / human-agent trust risk | Phase 6 保持 fake email dry-run only 并断言 side effect | `reports/evidence/promptfoo_agent_result.json` | `dry_run=true`、`sent=false`、`side_effect=dry_run_only`、`schema_valid` | 增加双人审批、高风险动作分级 |

## 覆盖结论

当前覆盖已形成 Chatbot、RAG、Agent 三条本地测试闭环。Phase 6.5 已执行增强后的三类本地测试集并更新 execute evidence：Chatbot 9/0/0，RAG 12/0/0，Agent 10/0/0。Phase 6.6 进一步加固 evidence / JSONL log 脱敏和 Chatbot risk signal 分类。覆盖矩阵只代表本地 sandbox 的学习验证结果，不代表真实企业系统安全结论。

## Phase 24 Corpus-to-Testcase Compiler

Phase 24 新增 Corpus-to-Testcase Compiler（`scripts/compile_corpus_to_testcases.py`），将 `corpus/` 下的 YAML 语料自动编译为 61 个标准化测试用例和 52 个 promptfoo 草稿，输出到 `generated_testcases/`。编译为 draft only，不执行测试，不连接真实系统，不影响现有覆盖矩阵的执行状态。
