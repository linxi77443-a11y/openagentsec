# Phase 16：AI Red Teaming Playbook + Severity Model 复盘

## 本阶段做了什么

Phase 16 新增 AI Red Teaming 执行方法论层，位于 `red_team/`。本阶段是纯方法论和模板层，不执行测试、不修改 evidence、不连接真实目标。

### 新增文件（`red_team/` 目录）

| 文件 | 用途 |
|---|---|
| `README.md` | 目录总览、文件索引、系统关系图、使用前提、局限性 |
| `ai_red_team_playbook.md` | 12 步标准红队评估流程，说明位置、适用对象（Chatbot/RAG/Agent/API/Manual UI）、不适用对象、系统组件关系 |
| `rules_of_engagement_template.md` | 15 节正式授权模板：基本信息、目标、参与者、授权范围、允许测试、禁止测试、数据边界、频率限制、时间窗口、停止条件、应急联系人、证据处理、报告分发、复测安排、签署栏 |
| `test_session_template.md` | 9 节 session 记录模板：基本信息、范围引用、语料选择、测试用例选择、runner 配置、执行日志、evidence 输出、观察记录、初步发现项、后续行动 |
| `finding_severity_model.md` | 7 维度严重性评分模型：D1 Impact Scope、D2 Data Sensitivity、D3 Agentic Capability、D4 Exploitability、D5 Control Failure、D6 Persistence、D7 Evidence Confidence。计算公式 `base_score = D1+D2+D3+D4+D5+D6`，映射 Informational/Low/Medium/High/Critical 5 个等级 |
| `finding_template.md` | 完整 finding 记录模板：severity assessment（7 维度表）、MITRE ATLAS/OWASP Agentic/OWASP LLM 框架映射、evidence 引用、reproduction steps、root cause hypothesis、recommended controls、retest method、residual risk |
| `evidence_handling_guide.md` | 9 节 evidence 指南：evidence 类型（6 种）、命名规则、必须包含的信息、禁止包含的信息、脱敏规则（5 类）、fake secret/honeytoken 处理、API key/bearer/endpoint 处理、finding 引用方式、保留与清理策略 |
| `mitigation_retest_workflow.md` | 4 节工作流：9 类控制建议（Prompt/Policy Hardening、Retrieval Filtering、Tool Allowlist、Schema Validation、Memory Governance、Human Confirmation、Egress Control、Audit Logging、Rate Limit/Loop Guard）+ 复测流程 + finding 关闭条件 + residual risk 记录 |
| `red_team_report_outline.md` | 13 节 + 1 附录正式红队报告大纲：Executive Summary、Scope、Target Architecture、Methodology、Framework Mapping、Test Coverage、Findings Summary、Detailed Findings、Evidence Index、Control Recommendations、Retest Plan、Limitations、Appendix |

### 更新文件

- `README.md` — 新增 Phase 16 阶段行、red_team/ 目录结构、red_team/ 文件引用列表
- `docs/atlas_assessment_system_guide.md` — 新增 Phase 16 说明区（Playbook、Severity Model、Finding Template、Evidence Guide、Mitigation & Retest、Report Outline）
- `docs/assessment_workflow_v1.md` — 流程图顶部新增 AI Red Teaming Playbook 12 步流程、evidence 后新增 Finding 分析 + Severity 评分步骤
- `docs/daily_operation_guide.md` — 新增"如何查阅 AI Red Teaming 方法论"章节
- `docs/capability_matrix_v1.md` — 新增 AI Red Teaming Playbook、Severity Model、Finding Template、Evidence Guide、Retest Workflow、Report Outline 6 行
- `docs/release_notes_v1.md` — 新增 Phase 16 条目、测试统计行、未来路线图编号调整
- `docs/roadmap.md` — Phase 16 从 Planned→Completed、新增完成说明、后续 Phase 编号更新（17→20）
- `docs/learning_summary.md` — 新增 Phase 16 额外收获段落
- `reports/evidence_index.md` — 新增 AI Red Teaming Methodology 节、3 条证据行
- `reports/generated_atlas_assessment_report.md` — 新增 AI Red Teaming Methodology 章节
- `reports/generic_agent_assessment_template.md` — 评估背景新增 red_team/ 方法论引用
- `dashboard/README.md` — 新增 AI Red Teaming Methodology 说明
- `scripts/generate_atlas_dashboard.py` — 新增 red_team_methodology 数据块和 Markdown/HTML 渲染区
- `scripts/generate_enterprise_report.py` — 新增 AI Red Teaming Methodology 章节
- `scripts/generate_all_reports.sh` — 新增 red_team/ 输入文件检查
- `runners/run_quality_check.sh` — 新增 Phase 16 路径检查、forbidden pattern 检查、dashboard JSON 检查、README.md Phase 16 引用检查

## 关键设计决策

### 1. Severity Model 与 evidence 的关联

7 维度严重性评分模型的每个维度（D1-D6）都对应 evidence 中可观察的布尔字段：

- D1 Impact Scope ← `tool_calls`、`side_effect`、`memory_updated` 等字段
- D2 Data Sensitivity ← `leaked_secret`、`leaked_sensitive_data`、`leaked_system_prompt` 等
- D3 Agentic Capability ← 目标类型和工具 allowlist
- D4 Exploitability ← `followed_malicious_instruction`、`followed_document_instruction` 等
- D5 Control Failure ← `should_refuse`、`should_block`、`unauthorized_tool_call`、`dry_run` 等
- D6 Persistence ← 是否写入 memory/skill/plugin

这保证了评分结果可追溯、可复核。但当前红队评估方法论层与现有 evidence 之间**没有自动关联机制**——Severity Model 的 D1-D6 取值需要由评估者手动从 evidence 中提取，是未来自动化方向。

### 2. 方法论层不执行测试

`red_team/` 的所有文件都是防君子不防小人的模板和指南。如果将红队评估视为"项目交付"而非"功能执行"，这些模板提供了必需的流程框架——包括授权（RoE）、记录（test session）、映射（framework mapping）、评分（severity model）、修复（mitigation）、复测（retest）和报告（report outline）。

### 3. 与现有系统的关系

| 层 | 目录 | 回答的问题 |
|---|---|---|
| 执行方法论 | `red_team/` | 如何组织一次红队评估？流程是什么？ |
| ATLAS 知识 | `atlas/` | 用什么 technique 来测？ |
| 评估对象 | `assessment_profiles/` | 测什么类型的系统？ |
| 语料设计 | `corpus/` | 用什么测试输入？ |
| 测试执行 | `runners/` + `providers/` | 怎么执行？用哪个 runner？ |
| 测试用例 | `testcases/` | 具体的 test case 是什么？ |
| 结果证据 | `reports/evidence/` | 测试结果是什么？ |

### 4. 不做什么

- 不对任何真实系统执行红队评估
- 不修改现有 evidence、coverage 或 test results
- 不新增 test capability、runner、provider
- 不新增 offensive test corpus
- 不声称已经完成真实红队项目

## 质量检查结果

- 所有 `red_team/` 文件存在性验证：通过
- Forbidden pattern 扫描（real credentials、--execute、production systems）：通过
- Dashboard 中 `real_red_team_executed` 字段检查：通过
- README.md Phase 16 引用检查：通过
- 所有 dry-run 通过（Chatbot / RAG / Agent）

## 已知局限性

1. **无自动评分**：Severity Model 的 D1-D6 取值目前需要人工提取，没有自动化 mapping 到 evidence 字段。
2. **无 Finding 数据库**：当前 finding 模板是静态 Markdown 文件，没有 finding 数据库（SQLite 或其他），无法做 finding 跟踪和趋势分析。
3. **无 Dashboard severity 展示**：Dashboard 当前不显示 severity 分布（如 severity pie chart），需要 dashboard 增强才能展示。
4. **无 RoE 签署流程**：RoE 模板是静态文档，没有签署和版本管理流程。
5. **模板未接入现有评估系统**：当前 finding template、evidence guide 与现有 evidence 没有自动集成，需要人工使用。

## 后续建议

1. 若需要真正的 Finding 管理，建议为 finding 设计 SQLite 数据库 schema，替代静态 Markdown 模板。
2. Dashboard 增强：增加 severity 分布饼图、finding 列表、retest 状态。
3. 若启动真实红队评估，建议先完成 RoE 签署、测试账号隔离、数据脱敏策略和回滚计划。
4. Severity Model 未来可对接 Dashboard 的 test results 数据，实现自动 D1-D6 评分。
