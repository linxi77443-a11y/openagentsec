# 后续路线图

## 推荐优先级

1. Phase 27A：Corpus/Curation Backfill ✅ — 补齐 chatbot assertion_strategy 和 fake_assets_required，解决 API profile testcases 生成问题（已完成）
2. Phase 27：Regression Suite Dry-Run Validator ✅ — 在 curated_candidate 覆盖度提升后执行 dry-run 结构验证（已完成）
3. Phase 28：Assertion & Risk Signal Rule Engine ✅（已完成）
4. 未来：Assertion-Driven Execution（规则驱动测试执行，需先完成运行时 assertion 引擎）
5. 未来：External Tool Integration（garak / PyRIT / Browser Automation，需先完成授权和 adapter 验证）

## 已完成阶段

### Phase 16.5：System Acceptance Regression Checkpoint

已完成。Phase 16.5 对当前 ATLAS AI Security Assessment System（Phase 6–16）做了一次全量系统回归验收，确认所有 5 条评估链路（Chatbot、RAG、Agent、Manual UI Replay、Generic Agent Mock Harness）在本地 sandbox 环境下完整可运行。

- **Chatbot**：9 passed，0 failed，0 errors
- **RAG**：12 passed，0 failed，0 errors
- **Agent**：10 passed，0 failed，0 errors
- **Manual UI Replay**：16 passed，0 failed，0 errors
- **Generic Agent Mock Harness**：12 passed，0 failed，0 errors
- **Quality Check**：2 次（执行前/执行后），均通过
- **脱敏检查**：reports/evidence/、dashboard/、corpus/、owasp/ 等 9 个目录，均通过
- **Evidence 文件**：7 个文件，全部存在
- **Dashboard / Report**：已重新生成
- **Checkpoint 文档**：`docs/phase16_5_system_acceptance_checkpoint.md`

版本从 v1 升级至 v1.1。所有测试结果均为本地 sandbox / fake replay / mock harness 数据，不代表真实企业系统、真实模型 API、真实知识库或真实 Agent 工具链的安全结论。

### Phase 11：测试环境 API Provider Skeleton

已完成。Phase 11 提供 placeholder target schema、Chatbot / RAG provider skeleton、mock response、dry-run runner、readiness evidence、dashboard/report 展示和 quality check。当前仍不连接真实 API。

后续如进入真实测试环境 API execute，需要另设批准阶段，补齐授权、测试账号、凭证加载、日志脱敏和回滚流程。

### Phase 12：Generic Agent ATLAS Assessment Pack

已完成。Phase 12 把 Agent 评估从本地 sandbox 升级为通用 Agent ATLAS Assessment Pack，覆盖 Hermes / OpenClaw / Claude Code / LangGraph / AutoGen / MCP / 企业流程 Agent。提供 12 模块攻击面模型、80 项控制项清单、18 项测试能力、5 种评估模式、架构画像方法和完整 dashboard/report 集成。

当前框架不连接任何真实 Agent，不支持真实 API 调用，不支持 `--execute`。

### Phase 13：Generic Agent Mock Tool Harness

已完成。Phase 13 构建了 Generic Agent Mock Tool Harness，提供 6 个 fake 工具、fake memory store、fake skill store、fake external channel、8 项策略检查、12 个本地可执行的 mock 测试场景，覆盖 goal hijacking、identity spoofing、memory poisoning、context poisoning、tool allowlist/schema/metadata/return injection、secret access、exfiltration、human confirmation bypass、skill poisoning、resource consumption 和 audit log redaction。

- Harness：`sandbox/generic_agent_harness/`
- 测试用例：`testcases/generic_agent_mock_harness/examples.yaml`
- Runner：`runners/run_generic_agent_harness.sh`
- Evidence：`reports/evidence/promptfoo_generic_agent_harness_result.json`
- 结果：12 / 0 / 0

### Phase 14：OWASP Agentic Top 10 Crosswalk

已完成。Phase 14 将 OWASP Agentic Top 10 风险分类融入现有 Generic Agent 评估体系，形成风险分类与报告映射层。新增 `owasp/` 目录和 6 个文件，覆盖 ASI01-ASI10 的映射、控制项、报告语言。不连接真实 Agent，不执行任何测试。

覆盖状态：

- covered_by_local_harness：ASI01（Goal Hijack）、ASI02（Tool Misuse）、ASI03（Identity Abuse）、ASI06（Memory Poisoning）、ASI08（Cascading Failures）、ASI09（Trust Exploitation）
- partially_covered：ASI04（Supply Chain — Skill poisoning covered, Plugin/MCP planned）
- planned：ASI07（Inter-Agent Communication）、ASI10（Rogue Agents）
- not_supported_for_now：ASI05（Code Execution）

与 MITRE ATLAS 互补：ATLAS 用于威胁建模和测试设计，OWASP 用于风险分类和报告语言。

### Phase 15：Evaluation Corpus Architecture

已完成。Phase 15 新增统一评估语料库目录 `corpus/`，覆盖 Chatbot、RAG、Agent、API、Business、Regression 六个 profile，共 49 条语料。语料库位于 test design 层，使用统一 schema 定义，独立于 testcases（执行层）、replays（人工 replay 层）、evidence（结果层）。

关键交付：
- Corpus 目录结构：7 个子目录，每个包含 README.md 和 YAML 语料文件
- Schema 定义：`corpus/corpus_schema.md`
- 总索引：`corpus/corpus_index.yaml`（按 profile / framework / execution_mode / status / severity 索引）
- 49 条语料覆盖：chatbot 14 + rag 14 + agent 16 + api 6 + business 8 条实际语料，regression 9 条引用语料
- 回归引用机制：regression 语料通过 corpus_id 引用原始条目，不重复复制

### Phase 16：AI Red Teaming Playbook + Severity Model

已完成。Phase 16 新增 AI Red Teaming 执行方法论层，位于 `red_team/`。包含 9 个文件：

- **Playbook**（`red_team/ai_red_team_playbook.md`）：12 步标准红队评估流程，说明位置、适用对象、不适用对象和系统组件关系
- **Rules of Engagement 模板**（`red_team/rules_of_engagement_template.md`）：15 节正式授权模板
- **Test Session 模板**（`red_team/test_session_template.md`）：9 节 session 记录模板
- **Severity Model**（`red_team/finding_severity_model.md`）：7 维度严重性评分模型
- **Finding Template**（`red_team/finding_template.md`）：完整 finding 记录模板
- **Evidence 处理指南**（`red_team/evidence_handling_guide.md`）：evidence 类型、命名、脱敏和保留规则
- **修复建议与复测流程**（`red_team/mitigation_retest_workflow.md`）：9 类控制建议 + 复测流程
- **红队报告大纲**（`red_team/red_team_report_outline.md`）：13 节正式报告结构
- **REDAME**（`red_team/README.md`）：目录总览和系统关系图

**状态说明**：
- 所有文件均为方法论/模板层，不执行任何测试。
- **未执行真实红队项目**，未对任何真实系统执行红队评估。
- Severity Model 可在现有 evidence 上打分验证，但不改变现有 finding 或 evidence 内容。
- 真实红队评估时需补充授权、RoE 签署、测试账号、数据脱敏和回滚计划。

### Phase 17：AI Asset Inventory + NIST AI RMF Mapping

已完成。Phase 17 新增 AI 应用资产清单（`inventory/`）和 NIST AI RMF 治理映射层（`governance/`）。

**Inventory 关键交付**：
- Schema：`inventory/ai_asset_inventory_schema.md`（9 分类资产字段定义）
- 样例资产：`inventory/sample_ai_asset_inventory.yaml`（5 个 fake 资产，覆盖 chatbot/rag/agent/workflow_api/manual_ui_replay）
- 登记表单：`inventory/ai_application_intake_form.md`
- 风险登记表：`inventory/ai_asset_risk_register_template.yaml`
- 资产索引：`inventory/ai_asset_inventory_index.yaml`

**Governance 关键交付**：
- NIST AI RMF Mapping：`governance/nist_ai_rmf_mapping.yaml`（Govern/Map/Measure/Manage）
- GenAI Profile 映射：`governance/nist_genai_profile_mapping.yaml`（10 类 GenAI 风险）
- 治理检查清单：`governance/ai_risk_governance_checklist.md`（12 类 60+ 检查项）
- 治理到安全评估交叉映射：`governance/governance_to_security_assessment_crosswalk.md`
- 治理报告附录模板：`governance/governance_report_appendix_template.md`

**状态说明**：
- 当前资产为 sample/fake 数据，不代表任何真实系统。
- NIST AI RMF 映射是治理映射层，**不代表已完成 NIST 合规认证**。
- 不连接真实 API、真实 Agent、真实页面或真实工具。
- 本阶段不运行任何 --execute。

### Phase 18：AI/ML-BOM + Supply Chain Mapping

已完成。Phase 18 新增 AI/ML-BOM 和供应链映射层（`supply_chain/`）。

**关键交付**：
- BOM Schema：`supply_chain/ai_ml_bom_schema.md`（9 类组件字段定义）
- 5 个样例 BOM：`supply_chain/sample_ai_ml_bom.yaml`（与 5 个 inventory 资产一一对应）
- 模型来源检查清单：`supply_chain/model_provenance_checklist.md`（7 类检查）
- 数据集/知识库来源清单：`supply_chain/dataset_knowledge_base_inventory.md`
- 工具/插件/MCP 依赖清单：`supply_chain/tool_plugin_mcp_inventory.yaml`
- 提示词模板依赖清单：`supply_chain/prompt_template_inventory.yaml`
- 外部 API 依赖清单：`supply_chain/external_api_dependency_inventory.yaml`
- 供应链风险登记表：`supply_chain/supply_chain_risk_register_template.yaml`（6 条 sample risk entries）
- ATLAS/OWASP/NIST 映射：`supply_chain/supply_chain_to_atlas_owasp_mapping.yaml`（15 条映射）
- 供应链报告附录模板：`supply_chain/supply_chain_report_appendix_template.md`

**状态说明**：
- 所有 BOM 为 sample/fake 数据，不代表任何真实系统的组件依赖关系。
- 供应链风险映射为方法论参考，不构成完整供应链威胁模型。
- 本系统未连接真实模型仓库、真实供应商系统或真实依赖扫描工具。
- 本阶段不运行任何 --execute。

### Phase 19：External Evaluation Tool Adapter Planning

已完成。Phase 19 新增外部评估工具 adapter 规划层（`external_tools/`），用于未来有序接入 garak、PyRIT、AgentDojo、AgentDyn、Browser Automation 和 API Provider。

**关键交付**：
- 统一 evidence schema：`external_tools/external_tool_evidence_schema.md`
- 风险边界：`external_tools/external_tool_risk_boundary.md`
- Adapter index：`external_tools/external_tool_adapter_index.yaml`（6 个 adapter）
- ATLAS/OWASP 映射：`external_tools/external_tool_to_atlas_owasp_mapping.yaml`
- Adapter plans：garak、PyRIT、Agent benchmark、Browser Automation、API Provider
- 报告附录模板：`external_tools/external_tool_report_appendix_template.md`

**状态说明**：
- 当前为 planning/design layer only。
- 未安装 garak、PyRIT、AgentDojo、AgentDyn 或浏览器自动化工具。
- 未运行任何外部工具，未运行任何 `--execute`。
- 未连接真实 API、真实 Agent、真实页面或外部网络。
- 未来外部工具输出必须归一化到统一 evidence schema。

### Phase 20：External Tool Mock Evidence Normalization

已完成。Phase 20 使用 fake/mock 外部工具输出验证 `external_tools/` evidence schema 和 adapter mapping 可以归一化为统一 evidence，并展示到 dashboard/report。

**关键交付**：
- 6 个 mock raw outputs：`external_tools/mock_outputs/`
- Normalizer：`scripts/normalize_external_tool_mock_evidence.py`
- Normalized evidence：`reports/evidence/external_tools/mock_external_tool_normalized_evidence.json`
- Evidence index：`reports/evidence/external_tools/mock_external_tool_evidence_index.json`
- Mock evidence mapping：`external_tools/mock_external_tool_evidence_mapping.yaml`

**状态说明**：
- 仅 fake/mock outputs，未安装或运行真实外部工具。
- `external_tool_executed=false`，`real_target_connected=false`。
- `adapter_status=mock_normalization_ready`，不代表 integrated。
- Mock evidence 不能用于 formal finding，只能用于 pipeline validation。

### Phase 21：System Release Consolidation v1.3

已完成。Phase 21 做系统级发布收口，把 Phase 1–20 的成果整理成 v1.3 release package。

**关键交付**：
- `release/` 目录（11 个发布收口文档）
- `release/system_release_v1_3.md` — 系统发布说明
- `release/release_manifest_v1_3.yaml` — 发布清单
- `release/module_map_v1_3.md` — 模块关系图
- `release/capability_matrix_v1_3.md` — 能力矩阵
- `release/execution_status_matrix_v1_3.md` — 执行状态矩阵
- `release/user_journey_v1_3.md` — 5 条使用路径
- `release/operator_quickstart_v1_3.md` — 命令速查
- `release/delivery_package_checklist_v1_3.md` — 交付清单
- `release/known_limitations_v1_3.md` — 已知限制
- `release/next_phase_roadmap_v1_3.md` — 后续路线图

**状态说明**：
- 不新增测试能力、不新增治理框架、不安装外部工具、不运行任何 `--execute`、不连接真实系统。

### Phase 23：Assessment Plan Generator

已完成。Phase 23 新增 Assessment Plan Generator，一个独立的评估计划生成层。

**关键交付**：
- Schema：`assessment_plans/assessment_plan_schema.md`
- Generator 脚本：`scripts/generate_assessment_plans.py`
- 5 个 sample 评估计划：`assessment_plans/generated/`
- 计划索引：`assessment_plans/assessment_plan_index.yaml`

**设计原则**：
- **Planning layer only**：评估计划是测试设计（test design），不是 evidence，不是 corpus。
- Corpus 是测试用例资产；Plan 是针对特定资产的选择 + 执行推荐。
- Evidence 是测试结果；Plan 在执行之前，Evidence 在执行之后。
- 所有当前计划均为 `sample/planning_only`，`allowed_now=false`。
- 不执行测试、不连接真实系统、不安装外部工具。

**运行方式**：
```bash
python3 scripts/generate_assessment_plans.py
```

## Phase 25：Generated Testcase Curation & Runner Binding

已完成。Phase 25 新增 Generated Testcase Curation & Runner Binding 层（`curation/`），对 Phase 24 生成的 61 个测试草案进行静态分类：32 curated_candidate、29 manual_review_required。建立 5 个 runner binding 草案。Curation 只做静态分析，不运行任何测试。结果位于 `curation/` 目录。

## Phase 22：Browser Automation Test Env Design

### 目标

设计浏览器自动化在测试环境中的安全边界、账号隔离、页面 allowlist、截图脱敏和人机确认流程。

### 前置条件

- 已有测试环境授权。
- 测试账号独立。
- 页面 allowlist 明确。
- 禁止生产数据。
- 高风险按钮和写操作需要人工确认。

### 风险边界

- 只限测试环境页面。
- 不自动操作真实生产页面。
- 不自动提交真实写操作。

### 不做什么

- 不爬取外部网站。
- 不使用真实个人账号。
- 不做绕过登录或权限边界的操作。

### 推荐优先级

中高。应在 API Provider 边界稳定后推进。

## Phase 23：garak 本地 mock 接入

### 目标

学习 garak 的 LLM vulnerability probing 思路，并将其限制在本地 mock provider。

### 前置条件

- 本地 mock provider 可用。
- 输出脱敏和 evidence 转换流程明确。
- 不连接真实模型 API。

### 风险边界

- 只跑本地 mock。
- 不跑高频真实模型探测。
- 不接外部 endpoint。

### 不做什么

- 不对真实模型服务做 probing。
- 不运行未审查的大规模 probe 集。

### 推荐优先级

中。适合作为工具学习阶段。

## Phase 24：Corpus-to-Testcase Compiler ✅

Phase 24 已完成。详见 Phase 24 复盘文档 `docs/phase24_corpus_to_testcase_compiler_review.md`。

## Phase 25：Generated Testcase Curation & Runner Binding ✅

Phase 25 已完成。详见 Phase 25 复盘文档 `docs/phase25_generated_testcase_curation_runner_binding_review.md`。

## Phase 26：garak / PyRIT / Browser Automation 接入（规划中）

### 目标

研究 Agent 任务注入、工具调用和 benchmark 评估方式，并将其迁移为本地 fake tool / mock environment。

### 前置条件

- Generic Agent Assessment Pack 已稳定。
- fake tools 和 side-effect 分类明确。
- benchmark 输出可转为本地 evidence。

### 风险边界

- 只使用 fake tools。
- 不连接真实邮件、日历、云资源或企业工具。
- 写操作 dry-run。

### 不做什么

- 不让 Agent 自主访问真实系统。
- 不执行真实副作用动作。

### 推荐优先级

中低。建议在 Agent 本地评估包稳定后推进。

## Phase 27A：Corpus & Curation Backfill ✅

已完成。Phase 27A 对 Phase 26.5 识别出的三个根因问题做了 backfill 修复：

1. **fake_assets_required 修复**：为 chatbot 等 profile 的 generated testcases 补齐 assertion_strategy 和 fake_assets_required 字段，使其可通过 curation 进入 curated_candidate。
2. **API corpus backfill**：补齐 API 类型的 corpus 条目和 runner 定义，使 compiler 可以生成 API testcases，消除 api suite zero-selected。
3. **Risk type 多值映射**：修复 RISK_TO_OWASP 映射表，使 risk type 可以映射到多个 OWASP ASI，消除 LLM03/04/08 和 ASI01/03/05/10 的 framework gap。

**关键指标变化：**
- Zero-selected suites：3→0（core_llm、chatbot、api 全部补齐）
- LLM gaps：3→0（LLM03/04/08 覆盖）
- Agentic gaps：5→1（ASI07 仍为 gap，为 design gap）
- curated_candidate：32→59
- manual_review_required：29→6
- Regression suite selected：65→104

## Phase 27：Regression Suite Dry-Run Validator ✅

已完成。Phase 27 在 Phase 26/26.5/27A 构建的 7 个回归测试套件和 7 个 promptfoo 草稿之上，新增 Regression Suite Dry-Run Validator。该阶段做静态结构验证，确保套件在进入实际执行前具备引用完整性、框架映射一致性和边界合规性。

**验证结果：**

| 验证维度 | 结果 |
|---|---|
| Suites validated | 7（core_llm、chatbot、rag、agent、api、owasp_llm、owasp_agentic） |
| Promptfoo drafts validated | 7 |
| Reference integrity | PASS |
| Framework mapping | PASS |
| Boundary compliance | PASS |
| ASI07 gap | Documented and accepted |

**设计原则：**
- **Static dry-run only**：不执行测试、不执行 promptfoo、不连接真实系统、不生成 evidence。
- **Validation != evidence**：验证结果只证明套件结构完整性，不代表套件已执行或测试通过。
- 验证模式为 `static_dry_run_only`，不做运行时验证。

**关键交付：**
- Validator 脚本：`scripts/validate_regression_suite_dry_run.py`
- 验证输出：`regression_suites/validation/`（validation_summary.md 等）
- 验证模式：`static_dry_run_only`

**运行方式：**
```bash
python3 scripts/validate_regression_suite_dry_run.py
```

## Phase 28：Assertion & Risk Signal Rule Engine ✅

已完成。Phase 28 新增 Assertion & Risk Signal Rule Engine（`rules/` 目录），建立评估流程中的断言判断规则层。

**关键交付：**
- 风险信号规则：`rules/risk_signal_rules.yaml`（24 条，覆盖 prompt injection、system prompt exposure、RAG poisoning、Agent tool misuse 等）
- 预期行为规则：`rules/expected_behavior_rules.yaml`（15 条，定义 AI 系统期望安全行为）
- OWASP LLM 断言映射：`rules/owasp_llm_assertion_mapping.yaml`
- OWASP Agentic 断言映射：`rules/owasp_agentic_assertion_mapping.yaml`
- ATLAS 断言映射：`rules/atlas_assertion_mapping.yaml`
- Severity 规则映射：`rules/severity_rule_mapping.yaml`
- 规则索引：`rules/rule_index.yaml`
- 验证脚本：`scripts/validate_assertion_rules.py`

**设计原则：**
- **Static rule validation only**（`validation_mode: static_rule_validation`）：不对真实系统执行任何测试，不运行 promptfoo，不生成 evidence。
- **Rules != evidence**：规则是断言判断的参考依据，不是测试执行结果。
- **三层断言体系**：每个规则可同时映射到 OWASP LLM、OWASP Agentic 和 MITRE ATLAS。
- 规则层独立于执行层：不依赖 sandbox、provider 或 runner，可被任何评估链路引用。

**运行方式：**
```bash
python3 scripts/validate_assertion_rules.py
```

**后续阶段建议：**

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| Phase 29 | Assertion-Driven Execution（规则驱动测试执行，将规则引擎集成到评估运行时可自动评估断言） | 中 |
| Phase 30 | Formal Report Package Builder ✅（delivery_packages/） | 已完成 |
| Phase 30.5 | System Acceptance & Release Consolidation v1.4 ✅（release/ v1.4 发布文档，consolidation_only） | 已完成 |
| Phase 31 | Generic API Provider Formalization ✅（api_provider/ 目录结构、provider schema、target profile schema、config template、normalization schema、safety guardrails、execution boundary、dry-run simulator、validation script、5 sample targets。所有 sample target 声明 real_target=false、dry_run_only=true、execution_allowed=false、usable_for_real_test=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试） | 已完成 |
| Phase 31B | Authorized Test Target Onboarding ✅（api_provider/onboarding/ 子目录，11 个核心文件，授权流程 5 步、环境隔离 3 类、凭证安全加载 6 项控制、速率限制策略 4 级、安全拆除流程、validation script 18 项检查。所有目标声明 authorized=true、approved_by=human、testing_period=timeboxed、data_scope=restricted。未连接真实目标、未加载真实凭证、未执行真实安全测试） | 已完成 |
| Phase 31C | Local Mock API Execution Harness ✅（api_provider/mock_harness/ 子目录，9 个核心文件，mock API target schema、mock request/response fixtures（8 请求/8 响应，覆盖 5 种 provider 类型）、mock execution trace、normalized response samples、execution boundary、run/validate 脚本。Mock harness 只使用本地 fixture，不发起网络请求，不读取真实凭证。所有输出声明 mock_execution=true、external_network_called=false、credentials_loaded=false、real_target_connected=false） | 已完成 |
| Phase 31D | Limited Authorized API Dry-Run Plan | 已完成 |
| Phase 31E | Single Authorized API Smoke Test Design | 已完成 |
| Phase 31F | Single Smoke Test Approval Packet & Go/No-Go Gate | 已完成 |
| Phase 32C | Full Authorized API Regression Execution | ✅ |
| Phase 32D | Real API Regression Assessment Report Builder | ✅ |
| Phase 33 | Remediation & Retest Package Builder | ✅ |
| Phase 34A | DeepSeek Judge Provider Framework | ✅ |
| Phase 34B | DeepSeek Judge Go/No-Go Packet | ✅ |
| Phase 34C | Controlled DeepSeek Judge Execution | ✅ |
| Phase 34D | DeepSeek Judge Result Integration & Review Report | ✅ |
| Phase 35 | Promptfoo Integration Framework — 搭建 promptfoo 接入框架，配置归一化、dry-run 校验、结果 schema、结果归一化、evidence/finding/judge handoff。不运行 promptfoo eval、不连接被测 API、不调用 DeepSeek。所有 mock/dry-run。 | ✅ |
| Phase 35B | Promptfoo Go/No-Go Packet — 为后续受控执行 promptfoo 建立 Go/No-Go 审批包。9 个文件：approval packet、approval checklist、execution scope、cost/request budget、preflight checklist、execution boundary、rollback plan、acceptance criteria、local config template。所有 approval_status=not_approved、execution_allowed=false。不运行 promptfoo eval、不连接被测 API、不调用 DeepSeek。 | ✅ |
| Phase 35C.0 | Promptfoo Execution Readiness Gate — 建立执行前安全闸门，验证 secret isolation、API isolation、network safety、command safety。静态检查 only。不运行 promptfoo eval、不连接被测 API、不调用 DeepSeek、不读取 .local/、不生成 formal finding。Validate 94/94 passed，readiness_status=pass。不替换 Phase 35B Go/No-Go。 | ✅ |

Phase 31D 已完成的后续真实 API 测试前置条件见 release/system_release_v1_4.md
| Phase 32 | External Tool Integration - garak 本地 mock 接入 | 中 |
| Phase 33 | Remediation & Retest Package Builder | ✅ 已完成 |
