# Phase 17：AI Asset Inventory + NIST AI RMF Mapping 复盘

## 本阶段目标

建立 AI 应用资产清单与 NIST AI RMF 治理映射层，将系统从"安全测试工作台"扩展为"AI 安全评估 + AI 风险治理工作台"。

本阶段不新增攻击测试能力，不运行任何 `--execute`，不连接真实 API、真实 Agent、真实页面或真实工具。

## 新增 inventory 文件（6 个）

| 文件 | 用途 |
|---|---|
| `inventory/README.md` | 目录总览和系统组件关系 |
| `inventory/ai_asset_inventory_schema.md` | 9 分类资产字段定义（Basic Info / AI System Type / Model / Data / RAG / Agent Tooling / Security Controls / Assessment Status / Governance） |
| `inventory/sample_ai_asset_inventory.yaml` | 5 个样例资产（全部 fake 数据） |
| `inventory/ai_application_intake_form.md` | AI 应用接入登记表单（17 个字段 + profile 选择指引） |
| `inventory/ai_asset_risk_register_template.yaml` | 风险登记表模板（5 条 sample risk entries） |
| `inventory/ai_asset_inventory_index.yaml` | 资产索引（按类型/profile/环境/风险/NIST function 分类） |

## 新增 governance 文件（6 个）

| 文件 | 用途 |
|---|---|
| `governance/README.md` | 目录总览和重要说明 |
| `governance/nist_ai_rmf_mapping.yaml` | NIST AI RMF 四个 function 映射（Govern/Map/Measure/Manage） |
| `governance/nist_genai_profile_mapping.yaml` | NIST GenAI Profile 风险类别映射占位（10 类 GenAI 风险） |
| `governance/ai_risk_governance_checklist.md` | 12 类治理检查清单（60+ 检查项） |
| `governance/governance_to_security_assessment_crosswalk.md` | 治理框架到安全评估组件的交叉映射 |
| `governance/governance_report_appendix_template.md` | 治理报告附录模板 |

## AI Asset Inventory Schema 摘要

9 分类字段体系：

1. **Basic Information**：asset_id, asset_name, asset_type, owner, business_unit, environment, lifecycle_stage, criticality
2. **AI System Type**：chatbot/rag/agent/workflow/api/multimodal/other
3. **Model Information**：provider, name, version, deployment_mode, fine_tuned, access_control
4. **Data / Knowledge Base**：knowledge_base, data_sources, sensitivity, personal/customer data, update_frequency
5. **RAG / Retrieval**：vector_store, embedding_model, retrieval_scope, citation, filtering, stale document handling
6. **Agent / Tooling**：tools, registry, allowlist, write_actions, external_channels, memory, skill/plugin, MCP, human_confirmation
7. **Security Controls**：system_prompt_protection, input/output filtering, redaction, rate_limit, audit_logging, egress_control, secret_management, access_control
8. **Assessment Status**：ATLAS/OWASP/Corpus/Red Team status, evidence_files, last_assessment_date, residual_risk
9. **Governance**：risk_owner, approval_status, policy_exception, incident_response_owner, retest_frequency, decommission_plan

## Sample Assets 摘要

5 个样例资产，均为 fake 数据：

| Asset ID | Type | Environment | Criticality | Profile |
|---|---|---|---|---|
| sample_internal_chatbot | chatbot | local_sandbox | medium | chatbot |
| sample_policy_rag_assistant | rag | local_sandbox | medium | rag |
| sample_generic_agent | agent | local_sandbox | high | agent/generic_agent |
| sample_fastgpt_workflow_api | workflow_api | local_sandbox | low | api |
| sample_manual_ui_chatbot | manual_ui_replay | local_sandbox | low | chatbot/manual_ui |

每个资产包含 `related_profiles`、`related_corpus`、`related_evidence`、`related_atlas_techniques`、`related_owasp_agentic_risks`、`related_red_team_templates` 和 `current_assessment_status`。

## AI Application Intake Form 摘要

- 5 个字段分类：应用基本信息、AI 能力特征、数据合规、安全控制现状、测试环境
- 17+ 个字段，涵盖是否接入模型/知识库/工具、是否涉及个人/客户数据、审计日志、人工确认等
- 根据表单结果自动选择评估 profile（Chatbot/RAG/Agent/API/Manual UI Replay）

## Risk Register 模板摘要

每个 risk entry 包含 19 个字段：

- risk_id, asset_id, risk_title, risk_description, affected_component
- mitre_atlas_mapping, owasp_llm_mapping, owasp_agentic_mapping, nist_ai_rmf_function
- severity, likelihood, impact, evidence_reference, control_gap
- mitigation_plan, risk_owner, due_date, residual_risk, retest_plan, status

5 条 sample entries 覆盖 prompt injection、RAG poisoning、Agent tool misuse、API unassessed、Manual replay limited coverage。

## NIST AI RMF Mapping 摘要

| Function | Support Status | 关键组件 |
|---|---|---|
| Govern | partially_supported | inventory/, governance checklist, RoE, Severity Model |
| Map | supported | Asset Inventory, Profiles, Corpus, ATLAS, OWASP |
| Measure | supported | Runners, Sandboxes, Evidence, Dashboard |
| Manage | partially_supported | Mitigation & Retest, Quality Check |

每个 function 包含 `related_system_artifacts`、`related_inventory_fields`、`related_security_assessment_components`、`related_evidence`、`gaps` 和 `next_steps`。

## NIST GenAI Profile Mapping 摘要

10 类 GenAI 风险覆盖状态：

| 风险类别 | 状态 | 主要缺口 |
|---|---|---|
| Prompt Injection | covered | 跨轮上下文注入未覆盖 |
| Sensitive Information Disclosure | covered | 结构化 API 脱敏未验证 |
| Hallucination / Inaccurate Output | partially_covered | 无事实性验证 |
| Harmful Content | not_supported | 未覆盖 |
| Data Provenance | partially_covered | 无数据溯源 |
| Model / Tool Supply Chain | partially_covered | Plugin/MCP 未实现 |
| Privacy | not_supported | 无成员推断测试 |
| Cybersecurity | partially_covered | API baseline 为 doc only |
| Human Oversight | partially_covered | 无真实 HITL 流程 |
| Monitoring | not_supported | 无实时监控 |

## Governance Checklist 摘要

12 类共 60+ 检查项：Ownership & Accountability、AI Asset Inventory、Data Classification、Model/Provider Risk、RAG/Knowledge Base Governance、Agent/Tool Governance、Human Oversight、Logging & Monitoring、Security Testing、Evidence & Reporting、Incident Response、Retest & Continuous Improvement。

## Dashboard / Report 更新情况

- `scripts/generate_atlas_dashboard.py`：新增 AI Asset Inventory 和 NIST AI RMF Governance 数据块、Markdown 和 HTML 展示区
- `scripts/generate_enterprise_report.py`：新增 Inventory 和 Governance 章节、更新附录
- `scripts/generate_all_reports.sh`：新增 inventory/ 和 governance/ 输入文件检查
- Dashboard HTML 导航栏新增 Inventory 和 Governance 链接

## Quality Check 结果

新增 8 项 Phase 17 检查：

- inventory/ 和 governance/ 目录文件存在性：通过
- inventory/ 文件禁止模式扫描（URL/token/email/endpoint）：通过
- governance/ 文件禁止模式扫描（token/email）：通过
- sample_fastgpt_workflow_api 不包含真实 endpoint/API key：通过
- inventory index 引用 sample assets：通过
- NIST mapping 包含 Govern/Map/Measure/Manage：通过
- Dashboard/Report 不声称 NIST 合规认证：通过
- README.md 提及 Phase 17：通过

## 当前限制

1. **资产为 sample/fake 数据**：当前所有资产记录为样例数据，不代表任何真实系统。
2. **无自动化资产发现**：资产信息需要人工填写，没有自动化扫描或导入机制。
3. **NIST AI RMF 映射非认证**：映射是项目内部的治理映射层，不代表已完成 NIST 合规认证。
4. **无 Finding 数据库**：Risk register 为模板级别，未关联 finding 数据库。
5. **Dashboard 不显示 governance 状态图**：当前只在文字区块展示，没有 severity 分布或治理进度可视化。
6. **GenAI Profile 映射不完整**：10 类风险中有 3 类（Harmful Content、Privacy、Monitoring）未被覆盖。

## 下一阶段建议

1. 继续增强 AI Asset Inventory 覆盖更多资产类型和真实数据接入流程。
2. 设计 Finding 数据库 schema（SQLite），替代静态 Markdown 模板。
3. Dashboard 增加 Governance 状态可视化（severity 分布、修复进度、NIST function 覆盖）。
4. 若需要正式合规评估，建议引入外部审计，本系统仅提供技术层面的治理映射参考。
5. 考虑为 inventory 设计自动化资产信息导入接口。
