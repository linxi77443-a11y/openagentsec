# 当前版本能力矩阵 v1

| 能力名称 | 对应目录 / 文件 | 当前状态 | 是否可执行 | 是否只限本地 | 是否有 evidence | 是否进入 dashboard | 是否进入报告 | 后续增强方向 |
|---|---|---|---|---|---|---|---|---|
| Testcase curation | `curation/`、`scripts/curate_generated_testcases.py` | planning | 否 | 是 | 否，curation only | 是 | 是 | 人工复核流程、runner binding 验证、fake asset 管理 |
| Chatbot assessment | `runners/run_promptfoo.sh`、`sandbox/chatbot_demo/` | covered | 是 | 是 | 是，`promptfoo_chatbot_result.json` | 是 | 是 | 增加更多本地 prompt 变体和 UI replay 对照 |
| RAG assessment | `runners/run_rag_promptfoo.sh`、`sandbox/rag_demo/` | covered | 是 | 是 | 是，`promptfoo_rag_result.json` | 是 | 是 | 多文档冲突、来源可信度评分、引用级脱敏 |
| Agent assessment | `runners/run_agent_promptfoo.sh`、`sandbox/agent_demo/` | covered / partially covered | 是 | 是 | 是，`promptfoo_agent_result.json` | 是 | 是 | human-in-the-loop、跨轮上下文、长期记忆模拟 |
| Manual UI Replay | `replays/`、`providers/manual_replay_provider.py`、`runners/run_manual_ui_promptfoo.sh` | covered for local fake replay | 是 | 是 | 是，`promptfoo_manual_ui_result.json` | 是 | 是 | 测试环境页面人工 replay，授权后再扩展 |
| API Provider Skeleton | `targets/api/`、`providers/api_*_provider.py`、`runners/run_api_*_provider.sh` | skeleton / dry-run only | 只支持 dry-run | 是 | 是，`api_*_provider_dry_run.json` | 是 | 是 | 授权后设计测试环境 API execute，不可直接接 production |
| ATLAS coverage | `coverage/atlas_coverage_matrix.yaml` | active | 不直接执行 | 是 | 间接引用 evidence | 是 | 是 | 增加更多 technique 和 gap traceability |
| AI Asset Inventory | `inventory/` | created | schema/methodology | 是 | N/A（sample 数据） | 是（Phase 17） | 是（Phase 17） | 增加真实资产接入流程 |
| NIST AI RMF Governance Mapping | `governance/` | created | mapping layer | 是 | N/A（治理映射层） | 是（Phase 17） | 是（Phase 17） | 扩展 GenAI Profile 映射，对接 Dashboard severity |
| Dashboard | `dashboard/` | active | 生成型 | 是 | 读取 evidence | 是 | 不适用 | 增加筛选、趋势和可视化导出 |
| Enterprise report | `reports/generated_atlas_assessment_report.md` | active | 生成型 | 是 | 读取 evidence | 不适用 | 是 | 增加更细控制项映射和复测差异 |
| Redaction | `utils/redaction.py`、各 runner 后处理 | active | 是 | 是 | 影响所有 evidence | 是 | 是 | 增强 fake PII、结构化 secret 字段覆盖 |

> Phase 21 v1.3 发布收口：详见 `release/capability_matrix_v1_3.md`（按能力分类的详细矩阵，含 execution_mode 和 limitation）。
| Quality check | `runners/run_quality_check.sh` | active | 是 | 是 | 否 | 否 | 否 | 持续纳入新增目录和输出校验 |
| Generic Agent Assessment Pack | `assessment_profiles/generic_agent_profile.yaml`、`docs/generic_agent_attack_surface.md`、`test_catalog/generic_agent_test_catalog.yaml` | framework / methodology | 否 | 是 | 无 evidence（framework only） | 是 | 是 | mock tool harness、test instance、真实 Agent 集成（需授权） |
| Generic Agent Mock Tool Harness | `sandbox/generic_agent_harness/`、`runners/run_generic_agent_harness.sh`、`testcases/generic_agent_mock_harness/examples.yaml` | executable | 是 | 是 | 是，`promptfoo_generic_agent_harness_result.json` | 是 | 是 | Plugin/MCP mock harness、多轮上下文模拟、test instance |
| OWASP Agentic Top 10 Crosswalk | `owasp/agentic_top10_2026.yaml`、`owasp/agentic_to_atlas_crosswalk.yaml` | active | 不直接执行（映射层） | 是 | 映射 evidence | 是 | 是 | ASI05/07/10 覆盖评估、真实 Agent 映射验证 |
| Test catalog | `test_catalog/` | active | 不直接执行 | 是 | 映射 evidence | 是 | 是 | 增加能力版本、owner 和风险等级 |
| Assessment profiles | `assessment_profiles/` | active | 不直接执行 | 是 | 映射 evidence | 是 | 是 | 支持测试环境 API Provider profile |
| Evaluation Corpus | `corpus/` | active | 不直接执行（test design 层） | 是 | 映射 evidence | 是 | 是 | 扩展更多语料、自动化语料验证、语料复用 |
| AI Red Teaming Playbook | `red_team/ai_red_team_playbook.md` | methodology / template | 否（方法论/模板层） | 是 | 映射 evidence | 否 | 否 | 真实红队评估时复用 playbook 和模板 |
| Severity Model | `red_team/finding_severity_model.md` | methodology / template | 否（评分模型） | 是 | 映射 evidence | 否 | 是 | 接入 Dashboard 展示 severity 分布 |
| Finding Template | `red_team/finding_template.md` | methodology / template | 否（模板） | 是 | 映射 evidence | 否 | 是 | 在报告生成时自动填充 finding |
| Evidence Handling Guide | `red_team/evidence_handling_guide.md` | methodology / template | 否（指南） | 是 | 映射 evidence | 否 | 否 | 与 quality check 脱敏扫描配合 |
| Mitigation & Retest Workflow | `red_team/mitigation_retest_workflow.md` | methodology / template | 否（工作流） | 是 | 映射 evidence | 否 | 是 | 对接 finding 的 retest 字段 |
| Red Team Report Outline | `red_team/red_team_report_outline.md` | methodology / template | 否（大纲） | 是 | 映射 evidence | 否 | 是 | 生成正式红队报告 |
| AI/ML-BOM + Supply Chain Mapping | `supply_chain/` | created | schema/methodology | 是 | N/A（sample 数据） | 是（Phase 18） | 是（Phase 18） | 增加真实供应链扫描接入 |
| External Evaluation Tool Adapter Planning | `external_tools/` | design layer | 否（规划/schema/映射层） | 是 | 无真实 external tool evidence | 是（Phase 19） | 是（Phase 19） | 未来按 RoE 接入 local mock / dry-run adapter |
| External Tool Mock Evidence Normalization | `external_tools/mock_outputs/`、`reports/evidence/external_tools/`、`scripts/normalize_external_tool_mock_evidence.py` | mock_normalization_ready | 是（仅 mock normalizer） | 是 | 是，mock normalized evidence | 是（Phase 20） | 是（Phase 20） | 未来接入真实工具前继续增强归一化规则 |
| Assessment Plan Generator | `assessment_plans/`、`scripts/generate_assessment_plans.py` | planning_layer | 是（生成计划） | 是 | 无（planning layer，不生成 evidence） | 否（Phase 23） | 否（Phase 23） | 对接实际 corpus 和执行计划，支持自定义目标 profile |
| Generated Testcase Curation & Runner Binding | `curation/`、`scripts/curate_generated_testcases.py` | curation_layer | 是（静态分类） | 是 | 无（curation layer，不生成 evidence） | 否（Phase 25） | 否（Phase 25） | 按 manual_review_required 条目进行人工审核后执行 |
| Regression Suite Dry-Run Validator | `regression_suites/validation/`、`scripts/validate_regression_suite_dry_run.py` | static_dry_run_only | 是（静态验证） | 是 | 无（validation layer，不生成 evidence） | 否（Phase 27） | 否（Phase 27） | 验证结果为结构检查，不替代实际执行验证；未来可扩展为动态验证 |
| Assertion & Risk Signal Rule Engine | `rules/`、`scripts/validate_assertion_rules.py` | static_rule_validation | 是（静态规则验证） | 是 | 无（rule layer，不生成 evidence） | 否（Phase 28） | 否（Phase 28） | 规则层为断言判断提供标准化依据，不替代测试执行验证；未来可扩展为 assertion-driven execution |
| Formal Report Package Builder | `delivery_packages/`、`scripts/build_delivery_package.py` | sample_delivery_build | 是（构建交付包） | 是 | 无（delivery package layer，不生成 evidence） | 否（Phase 30） | 否（Phase 30） | 所有交付包为 sample/mock，不包含真实客户或正式评估结论 |
| Generic API Provider Formalization | `api_provider/` | provider schema, target profile schema, config template, normalization schema, safety guardrails, execution boundary, 5 sample targets, dry-run simulator, validation script | sample/dry-run | false | false | false | false | false |

## v1 状态说明

v1 已具备本地自动评估、人工 replay、coverage、dashboard、报告生成和质量门禁。所有可执行能力均限制在本地 sandbox 或本地 fake replay，不代表真实企业系统覆盖。
