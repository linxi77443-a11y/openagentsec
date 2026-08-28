# Phase 23 Review — Assessment Plan Generator

## 本阶段目标

建立 Assessment Plan Generator，使系统能够基于 AI Asset Inventory、Assessment Profile、Corpus、ATLAS、OWASP LLM、OWASP Agentic、Red Teaming Playbook 自动生成结构化评估计划。

## 新增文件

| 文件 | 说明 |
|------|------|
| `assessment_plans/README.md` | 评估计划目录说明 |
| `assessment_plans/assessment_plan_schema.md` | 11 字段组 Schema 定义 |
| `assessment_plans/assessment_plan_index.yaml` | 评估计划索引（by_asset / by_profile / by_framework 等 8 维度） |
| `assessment_plans/generated/README.md` | generated 目录说明 |
| `assessment_plans/generated/plan_sample_internal_chatbot.yaml` | Chatbot sample plan（YAML） |
| `assessment_plans/generated/plan_sample_internal_chatbot.md` | Chatbot sample plan（Markdown） |
| `assessment_plans/generated/plan_sample_policy_rag_assistant.yaml` | RAG sample plan（YAML） |
| `assessment_plans/generated/plan_sample_policy_rag_assistant.md` | RAG sample plan（Markdown） |
| `assessment_plans/generated/plan_sample_generic_agent.yaml` | Agent sample plan（YAML） |
| `assessment_plans/generated/plan_sample_generic_agent.md` | Agent sample plan（Markdown） |
| `assessment_plans/generated/plan_sample_fastgpt_workflow_api.yaml` | API/Workflow sample plan（YAML） |
| `assessment_plans/generated/plan_sample_fastgpt_workflow_api.md` | API/Workflow sample plan（Markdown） |
| `assessment_plans/generated/plan_sample_manual_ui_chatbot.yaml` | Manual UI sample plan（YAML） |
| `assessment_plans/generated/plan_sample_manual_ui_chatbot.md` | Manual UI sample plan（Markdown） |
| `docs/phase23_assessment_plan_generator_review.md` | 本文件 |

## 新增脚本

| 脚本 | 说明 |
|------|------|
| `scripts/generate_assessment_plans.py` | 评估计划生成器（Python，仅标准库 + PyYAML） |

## Assessment Plan Schema 摘要

每个评估计划包含 11 个字段组：

1. **Plan Metadata** — plan_id、plan_name、generated_at、plan_version、source_asset、plan_status、execution_boundary
2. **Target Summary** — target_type、profiles、environment、lifecycle、criticality、data_sensitivity、tooling/memory/external_channels/write_actions
3. **Framework Mapping** — MITRE ATLAS techniques、OWASP LLM risks、OWASP Agentic risks、NIST AI RMF functions、Supply Chain risks
4. **Recommended Assessment Scope** — in_scope、out_of_scope、assumptions、authorization、safety_boundary
5. **Recommended Corpus** — corpus_ids、corpus_files、status、priority、gaps
6. **Recommended Test Modes** — local_sandbox、manual_replay、mock_harness、api_provider、external_tool_mock、future_external_tools
7. **Recommended Runners** — runner_id、command、execution_mode、risk_level、allowed_now、reason
8. **Evidence Plan** — expected_evidence_files、evidence_type、redaction_required、usable_for_formal_finding、limitations
9. **Finding Plan** — potential_finding_categories、severity_model、finding_template、risk_register、retest_reference
10. **Report Plan** — dashboard_sections、report_sections、appendix_templates、limitations_to_include
11. **Current Limitations** — planned_only_items、mock_only_items、not_supported_items、missing_corpus、missing_evidence

## Generator Script 摘要

`scripts/generate_assessment_plans.py` 读取：
- `inventory/sample_ai_asset_inventory.yaml`
- `corpus/corpus_index.yaml`
- `owasp/llm_top10_2025.yaml`
- `owasp/agentic_top10_2026.yaml`
- `coverage/atlas_coverage_matrix.yaml`
- `external_tools/external_tool_adapter_index.yaml`
- `supply_chain/sample_ai_ml_bom.yaml`

生成 5 份 sample plans（每个 sample asset 一份），同时生成 plan index 和 Markdown 摘要。所有 `generated_at` 使用固定值 `2026-01-01T00:00:00Z`。

## 5 个 Sample Plan 摘要

| Plan | Asset | Type | Corpus Files | Corpus IDs | Runners |
|------|-------|------|-------------|-----------|---------|
| plan_sample_internal_chatbot | sample_internal_chatbot | chatbot | 6 文件 | 22 条 | run_atlas_assessment --profile chatbot |
| plan_sample_policy_rag_assistant | sample_policy_rag_assistant | rag | 6 文件 | 22 条 | run_atlas_assessment --profile rag |
| plan_sample_generic_agent | sample_generic_agent | agent | 5 文件 | 16 条 | run_generic_agent_harness + run_manual_ui |
| plan_sample_fastgpt_workflow_api | sample_fastgpt_workflow_api | api/workflow | 3 文件 | 10 条 | API Provider Skeleton only |
| plan_sample_manual_ui_chatbot | sample_manual_ui_chatbot | manual_ui_replay | 3 文件 | 10 条 | run_manual_ui_promptfoo |

## Assessment Plan Index 摘要

索引按 8 个维度组织：by_asset、by_profile、by_target_type、by_execution_mode、by_framework（mitre_atlas / owasp_llm / owasp_agentic / nist_ai_rmf）、by_status、by_risk_level、by_evidence_readiness。

## Dashboard / Report 更新

- Dashboard 新增 Assessment Plan Generator 区块（生成计划数、覆盖资产、Profiles、框架映射、executable_now=false、real_system_connected=false）
- Enterprise Report 新增 Phase 22 Assessment Plan Generator 章节
- Report 展示 5 个 sample plan 摘要和当前边界说明

## 更新文件列表

### 新增（16 文件）
- `assessment_plans/`（目录 + 14 文件 + review doc）

### 修改
- `scripts/generate_assessment_plans.py` — 新建生成器
- `scripts/generate_atlas_dashboard.py` — 新增 assessment_plans 数据 + 区块
- `scripts/generate_enterprise_report.py` — 新增 Assessment Plan Generator 章节
- `scripts/generate_all_reports.sh` — 新增 Phase 23 boundary 声明
- `runners/run_quality_check.sh` — 新增 Phase 23 检查
- `release/`（10 文件）— 更新为 Phase 23
- `docs/`（10 文件）— 更新为 Phase 23
- `README.md` — 新增 Phase 23

## Quality Check 结果

（待运行）

## 当前限制

- 所有 generated plans 均为 sample，不代表真实评估计划。
- 所有 allowed_now 均为 false — 本阶段不执行测试。
- 所有 real_endpoint 标记为 false — 未连接真实系统。
- 所有 usable_for_formal_finding 标记为 false — 仅用于方法论演示。
- 所有 plans 为 planning_only 状态。
- Generator 使用固定时间戳避免每次 diff。
- 未运行任何 execute。
- 未连接任何真实系统。
- 未安装外部工具。

## 下一阶段建议

- Phase 24：garak Local Adapter Prototype
- 将 Assessment Plan Generator 扩展为支持用户自定义资产
- 将 Corpus 缺口自动反馈到 Plan 的 missing_corpus 字段
- 在 Dashboard 中添加 plan 执行状态追踪
