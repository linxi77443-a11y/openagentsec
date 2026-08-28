# 项目总复盘

## 项目目标

本项目是一个受控 AI 安全评估工作台，用于把 MITRE ATLAS、OWASP Agentic / LLM 风险转化为可学习、可测试、可留证、可报告的本地验证流程。

项目定位是防守、治理和学习，不是攻击工具。Claude Code 在项目中的角色是测试编排器、用例生成器和报告分析器，不是自主攻击 Agent。

核心目标：

- 建立 Chatbot、RAG、Agent 三类本地 sandbox。
- 使用 fake data、honeytoken 和本地 provider 验证安全控制。
- 生成 promptfoo evidence、本地 JSONL 日志和复盘报告。
- 沉淀企业 AI 安全评估模板、控制项清单和审批流程。

## 已完成阶段

| 阶段 | 内容 | 状态 | 主要产物 |
|---|---|---|---|
| Phase 1 | 项目骨架、安全边界、知识映射、本地 sandbox | 已完成 | `SAFETY.md`、`knowledge/`、`sandbox/`、`testcases/` |
| Phase 2 | Chatbot promptfoo dry-run 工作流 | 已完成 | `runners/promptfoo.chatbot.yaml`、`runners/run_promptfoo.sh` |
| Phase 2.5 | Chatbot promptfoo 本地执行闭环 | 已完成 | `reports/evidence/promptfoo_chatbot_result.json` |
| Phase 3 | RAG promptfoo dry-run 工作流 | 已完成 | `runners/promptfoo.rag.yaml`、RAG provider |
| Phase 3.5 | RAG promptfoo 本地执行闭环 | 已完成 | `reports/evidence/promptfoo_rag_result.json` |
| Phase 4 | Agent 工具调用 dry-run 工作流 | 已完成 | `runners/promptfoo.agent.yaml`、Agent fake tools |
| Phase 4.5 | Agent promptfoo 本地执行闭环 | 已完成 | `reports/evidence/promptfoo_agent_result.json` |
| Phase 5 | 项目复盘、企业模板和方法论沉淀 | 当前阶段 | `docs/` 与 `reports/` 模板 |

## 每个阶段的能力边界

### Phase 1

- 只建立项目结构、知识映射和本地 demo。
- 不执行真实安全测试。
- 不接入真实 API、真实模型、企业系统或真实凭证。

### Phase 2 / 2.5 Chatbot

- 只测试 `sandbox/chatbot_demo`。
- 只通过本地 `exec:python3 chatbot_provider.py` provider 调用。
- 关注 direct prompt injection、system prompt exposure、fake secret request。
- 不评估真实模型安全能力。

### Phase 3 / 3.5 RAG

- 只测试 `sandbox/rag_demo`。
- 只读取 `sandbox/rag_demo/fake_documents/*.md`。
- 关注 RAG poisoning、false RAG entry、indirect prompt injection、dummy data leakage。
- 不连接真实知识库、不索引企业文档、不访问外部网络。

### Phase 4 / 4.5 Agent

- 只测试 `sandbox/agent_demo`。
- 只调用本地 fake tools：`search_fake_docs`、`send_fake_email`、`read_fake_calendar`、`read_fake_secret`。
- 关注 tool allowlist、未授权工具拒绝、fake write dry-run、secret redaction、tool exfiltration blocking。
- 不访问真实邮件、真实日历、真实文件系统敏感路径或真实凭证。

## Chatbot / RAG / Agent 三类测试对象的差异

| 对象 | 主要输入 | 主要风险 | 关键证据 | 核心控制 |
|---|---|---|---|---|
| Chatbot | 用户 prompt | prompt injection、system prompt exposure、secret leakage | 输入、输出、risk signals、policy flags | 指令分层、输出过滤、敏感信息检测 |
| RAG | 用户 prompt + 检索文档 | poisoned context、false policy、indirect prompt injection、retrieval data leakage | retrieved document IDs、risk signals、followed flags | 来源校验、上下文隔离、引用可信度、污染检测 |
| Agent | 用户 goal + tool calls | tool misuse、unauthorized tool、write action abuse、tool exfiltration | tool_calls、tool_args、allowed、denied_reason、side_effect | tool allowlist、schema validation、least privilege、dry-run、人审 |

## 当前项目能做什么

- 在本地 sandbox 中执行 Chatbot / RAG / Agent 三类 promptfoo 测试。
- 输出结构化 JSON evidence。
- 记录本地 JSONL 日志。
- 验证 fake secret 不被完整输出。
- 验证 RAG 检索上下文不会覆盖任务规则。
- 验证 Agent 未授权工具请求被拒绝。
- 验证 fake write action 保持 dry-run。
- 生成安全报告、执行复盘、覆盖矩阵和企业模板。

## 当前项目不能做什么

- 不能代表真实企业系统安全结论。
- 不能测试真实模型 API 的完整安全能力。
- 不能扫描真实内网或生产系统。
- 不能读取、尝试或验证真实凭证。
- 不能执行真实邮件、日历、数据库、云资源或文件系统写操作。
- 不能作为自主攻击 Agent 使用。
- 不能绕过检测、规避审计或指导真实攻击。

## 后续扩展前提

扩展到任何非本地目标前，必须满足：

1. 完成 `docs/non_local_target_approval_checklist.md`。
2. 明确授权人、资产负责人、测试窗口和允许范围。
3. 明确 provider allowlist 和 target allowlist。
4. 明确日志脱敏、数据保留和回滚方案。
5. 明确禁止高频、破坏、外传、真实凭证尝试和未授权写操作。
6. 从 dry-run 开始，不直接 execute。

## 安全边界总结

- 默认只测试本地 sandbox。
- 默认 dry-run。
- 使用 fake data、dummy data 和 honeytoken。
- evidence 必须服务防守、治理、修复和复测。
- 真实日志、环境文件、API key、真实 token 或企业数据不得直接提交 Git。
- 没有非本地审批清单，不允许用于非本地目标。
