# ATLAS AI Security Assessment System v1 系统总览

## 系统定位

ATLAS AI Security Assessment System v1 是一个本地受控的 AI 安全评估工作台，用于把 MITRE ATLAS、OWASP LLM / Agentic 风险映射转化为可执行、可复核、可报告的本地评估流程。

系统目标不是提供攻击工具，而是帮助防守方在 sandbox、fake data、fake tools 和 evidence 的约束下验证安全控制、沉淀评估证据、生成 dashboard 和报告。

## 当前支持的评估对象

### Chatbot

用于评估直接用户输入对模型输出的影响，覆盖 prompt injection、system prompt exposure、prompt obfuscation 和 data leakage 等风险。

- Runner：`runners/run_promptfoo.sh`
- Evidence：`reports/evidence/promptfoo_chatbot_result.json`
- 当前结果：9 / 0 / 0

### RAG

用于评估检索文档对回答上下文的污染风险，覆盖 RAG poisoning、false / stale entry、fake citation、indirect prompt injection 和 sensitive output 等风险。

- Runner：`runners/run_rag_promptfoo.sh`
- Evidence：`reports/evidence/promptfoo_rag_result.json`
- 当前结果：12 / 0 / 0

### Agent

用于评估 Agent 工具调用、tool allowlist、schema validation、fake write action、secret access 和 exfiltration blocking 等风险。

- Runner：`runners/run_agent_promptfoo.sh`
- Evidence：`reports/evidence/promptfoo_agent_result.json`
- 当前结果：10 / 0 / 0

### Manual UI Replay

用于把人工页面输入输出复制为本地 replay JSON，再由本地 provider 做风险信号分析、脱敏和 evidence 生成。当前只使用 fake replay 样例，不访问真实页面。

- Runner：`runners/run_manual_ui_promptfoo.sh`
- Evidence：`reports/evidence/promptfoo_manual_ui_result.json`
- 当前结果：6 / 0 / 0

### API Provider Skeleton

用于为未来测试环境 Chatbot / RAG API 接入准备 target schema、placeholder target、provider skeleton、dry-run runner 和 readiness evidence。当前不连接真实 API，不读取真实凭证，不执行真实 HTTP 请求。

- Target schema：`targets/api/api_target_schema.md`
- Provider：`providers/api_chatbot_provider.py`、`providers/api_rag_provider.py`
- Runner：`runners/run_api_chatbot_provider.sh`、`runners/run_api_rag_provider.sh`
- Evidence：`reports/evidence/api_chatbot_provider_dry_run.json`、`reports/evidence/api_rag_provider_dry_run.json`
- 当前状态：skeleton / dry-run only

### Generic Agent Assessment Pack

用于评估通用 Agent 系统的 12 模块攻击面模型，覆盖 Hermes / OpenClaw / Claude Code / LangGraph / AutoGen / MCP / 企业流程 Agent 等架构。提供 18 项测试能力、80 项控制项清单和 5 种评估模式。

- Profile：`assessment_profiles/generic_agent_profile.yaml`
- 攻击面文档：`docs/generic_agent_attack_surface.md`
- 评估方法论：`docs/generic_agent_assessment_methodology.md`
- 控制项清单：`docs/generic_agent_control_checklist.md`
- 测试能力目录：`test_catalog/generic_agent_test_catalog.yaml`
- Manual replay 样例：`replays/manual_ui_samples/generic_agent_manual_replay_sample.json`
- 报告模板：`reports/generic_agent_assessment_template.md`
- 当前状态：framework / methodology only，不连接任何真实 Agent，不支持真实 API 调用。

## 当前基于的框架

### MITRE ATLAS

系统使用 ATLAS tactic / technique 作为风险分类和覆盖矩阵的主线，核心文件位于：

- `atlas/`
- `coverage/atlas_coverage_matrix.yaml`
- `coverage/atlas_coverage_summary.md`

### OWASP LLM / Agentic 风险映射

系统用 OWASP 风险视角补充工程治理关注点，例如 prompt injection、sensitive data disclosure、excessive agency、tool misuse、supply chain 和 governance 控制项。

相关文档：

- `docs/atlas_owasp_coverage_matrix.md`
- `docs/control_checklist.md`

## 当前能力边界

当前 v1 只支持：

- 本地 sandbox。
- fake data / dummy data / honeytoken。
- 本地 promptfoo `exec:` provider。
- 本地 JSON / YAML / Markdown evidence 和报告生成。
- Manual UI fake replay。
- dashboard / report 静态生成。
- API Provider Skeleton dry-run readiness 检查。
- Generic Agent Assessment Pack 框架和方法论。
- quality check 和脱敏检查。

## 当前不能做什么

当前 v1 不支持，也不应直接用于：

- 真实企业系统评估。
- 真实 API、真实模型或真实页面连接。
- 把 API Provider Skeleton 当作真实 API 测试能力使用。
- 真实账号、密码、token、API key 或 session cookie 测试。
- 浏览器自动化。
- 生产或预生产系统测试。
- 高频、批量、DoS 或破坏性测试。
- garak / PyRIT / AgentDojo 自动接入。
- Agent 通用评估包 framework 与方法论。
- garak / PyRIT / AgentDojo 自动接入。

## 适合的使用场景

- 学习 MITRE ATLAS 和 OWASP AI 风险映射。
- 本地验证 Chatbot / RAG / Agent 安全控制。
- 生成可复核 evidence。
- 演示安全评估流程和 dashboard。
- 生成内部汇报用的 Markdown / HTML 报告。
- 为未来测试环境接入设计数据结构和流程。

## 不适合的使用场景

- 直接评估真实企业系统。
- 真实红队攻击演练。
- 批量扫描外部目标。
- 凭证测试或账号测试。
- 绕过检测、防护或审计。
- 未授权页面或 API 测试。

## v1 结论

当前系统可以标记为本地受控的 ATLAS AI Security Assessment System v1。它适合用作学习、演示、内部方法论验证和本地 evidence/report 流水线，不适合作为真实系统自动评估工具直接使用。
