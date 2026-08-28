# ATLAS 驱动 AI 安全评估系统操作说明

## v1 文档入口

当前系统可标记为 **AI Security Assessment & Governance Workbench v1.3**。Phase 21 完成系统发布收口，发布文档位于 `release/`。日常使用建议优先阅读：

- 系统发布说明：`release/system_release_v1_3.md`
- 模块关系图：`release/module_map_v1_3.md`
- 能力矩阵：`release/capability_matrix_v1_3.md`
- 执行状态矩阵：`release/execution_status_matrix_v1_3.md`
- 已知限制：`release/known_limitations_v1_3.md`
- 后续路线图：`release/next_phase_roadmap_v1_3.md`
- 系统总览：`docs/system_overview_v1.md`

- 系统总览：`docs/system_overview_v1.md`
- 日常操作手册：`docs/daily_operation_guide.md`
- 评估流程说明：`docs/assessment_workflow_v1.md`
- 命令速查表：`docs/command_cheatsheet.md`
- 能力矩阵：`docs/capability_matrix_v1.md`
- Release notes：`docs/release_notes_v1.md`
- Roadmap：`docs/roadmap.md`

## 这个系统是什么

Phase 7 把项目从三套本地测试脚本升级为 ATLAS 驱动的 AI 安全评估系统骨架。

系统仍然只面向本地 sandbox：

- Chatbot：`sandbox/chatbot_demo`
- RAG：`sandbox/rag_demo`
- Agent：`sandbox/agent_demo`

它不是攻击工具，不连接真实 API、真实模型、企业系统、外部网络目标或真实凭证。

## 如何按 ATLAS 组织评估

系统用四层结构组织评估：

1. ATLAS 知识层：`atlas/`
2. 评估对象 profile：`assessment_profiles/`
3. 测试能力目录：`test_catalog/`
4. 覆盖矩阵：`coverage/`

此外，Phase 15 新增 Evaluation Corpus（`corpus/`）层，位于 test design 层，独立于 testcases（执行层）、replays（人工 replay 层）、evidence（结果层）。语料库按 profile 组织，提供测试意图、框架映射、输入数据和预期行为的结构化定义。

评估顺序建议：

```text
选择 profile -> 查看适用 technique -> [查 corpus 语料设计] -> 查 test capability -> 运行 dry-run -> 本地 execute（需确认） -> 查看 evidence -> 生成报告
```

## 如何选择 profile

当前支持：

- `chatbot`：本地 Chatbot prompt injection / system prompt exposure / data leakage。
- `rag`：本地 RAG poisoning / false entry / indirect prompt injection / dummy data leakage。
- `agent`：本地 Agent fake tool invocation / dry-run write / exfiltration blocking。
- `generic_agent`：Generic Agent 12 模块攻击面模型、80 项控制项、5 种评估模式（当前 framework / methodology only）。
- `all`：依次包含 chatbot、rag、agent。

`ai_gateway` 目前只是 planned profile，不执行测试。

## 如何查看 coverage matrix

覆盖矩阵：

```text
coverage/atlas_coverage_matrix.yaml
```

摘要：

```text
coverage/atlas_coverage_summary.md
coverage/coverage_gap_analysis.md
```

不要把 `planned` 或 `not_applicable` 项写成已覆盖能力。

## 如何运行 dry-run

默认 dry-run，只生成评估计划，不执行测试：

```bash
bash runners/run_atlas_assessment.sh --profile all
```

也可以选择单个 profile：

```bash
bash runners/run_atlas_assessment.sh --profile chatbot
bash runners/run_atlas_assessment.sh --profile rag
bash runners/run_atlas_assessment.sh --profile agent
```

Dry-run 输出：

```text
reports/evidence/atlas_assessment_plan.json
```

## 如何运行本地 execute

只有在人工明确确认后，才执行：

```bash
bash runners/run_atlas_assessment.sh --profile all --execute
```

执行模式会先运行：

```bash
bash runners/run_quality_check.sh
```

如果 quality check 失败，会停止，不继续执行测试。

Phase 7.5 已验证 `--profile all --execute` 的本地调度闭环：Chatbot 9/0/0、RAG 12/0/0、Agent 10/0/0，并生成 `reports/evidence/atlas_assessment_summary.json`。

`--execute` 只允许调用现有本地 runner：

- `runners/run_promptfoo.sh`
- `runners/run_rag_promptfoo.sh`
- `runners/run_agent_promptfoo.sh`

## 如何查看 evidence

ATLAS assessment plan：

```text
reports/evidence/atlas_assessment_plan.json
```

如果执行测试，会生成汇总：

```text
reports/evidence/atlas_assessment_summary.json
```

Summary 每个 profile 包含 `profile`、`runner`、`evidence_file`、`status`、`pass`、`fail`、`error`、`covered_atlas_techniques` 和 `timestamp`。

三类本地 evidence：

```text
reports/evidence/promptfoo_chatbot_result.json
reports/evidence/promptfoo_rag_result.json
reports/evidence/promptfoo_agent_result.json
```

Evidence 和 JSONL log 必须经过脱敏，不得包含完整 fake secret、honeytoken、dummy token、email-like 或 bearer-like 字符串。

## 如何生成报告

报告模板：

```text
reports/atlas_assessment_report_template.md
```

当前摘要：

```text
reports/atlas_assessment_summary.md
```

报告应按 ATLAS tactic / technique 组织，而不是只按脚本名称组织。

## 如何扩展新的 ATLAS technique

1. 在 `atlas/atlas_techniques.yaml` 增加 technique。
2. 设置正确的 `current_coverage_status`。
3. 如果没有本地测试能力，使用 `planned` 或 `not_applicable`。
4. 在 `coverage/atlas_coverage_matrix.yaml` 添加覆盖行。
5. 如有可执行测试，再新增 `test_catalog/` capability。
6. 更新报告模板或摘要。

## 如何新增测试能力

1. 在对应 promptfoo 配置中增加本地测试用例。
2. 不降低断言，不接入真实 provider。
3. 在 `test_catalog/` 中记录 capability。
4. 在 coverage matrix 中映射 technique。
5. 运行 quality check 和 dry-run。
6. 经人工确认后再执行本地 `--execute`。

## 如何接入未来的企业页面 / API / Agent

Phase 7 不实现真实接入。

未来如果要接入真实企业页面、API、模型或 Agent 工具链，必须先完成：

- 明确授权。
- 目标范围。
- 测试窗口。
- 数据分类和脱敏方案。
- 回滚方案。
- 日志访问控制。
- 人工确认流程。
- `docs/non_local_target_approval_checklist.md`。

在完成以上条件前，不允许把本系统用于非本地目标。

## Phase 8 Dashboard 与报告生成器

Phase 8 提供本地 dashboard 和企业评估报告生成器，仅读取本地 JSON、YAML、Markdown 文件，不访问网络，不执行测试，不修改 evidence。

### 运行

```bash
bash scripts/generate_all_reports.sh
```

### 输出

- `dashboard/dashboard_data.json`：dashboard 汇总数据
- `dashboard/index.md`：Markdown dashboard
- `dashboard/atlas_dashboard.html`：静态 HTML dashboard，使用内联 CSS，可直接在浏览器中打开
- `reports/generated_atlas_assessment_report.md`：基于 ATLAS 视角的本地评估报告

### 数据来源

- `reports/evidence/atlas_assessment_summary.json`
- `coverage/atlas_coverage_matrix.yaml`
- `coverage/atlas_coverage_summary.md`
- `coverage/coverage_gap_analysis.md`
- `assessment_profiles/*.yaml`
- `test_catalog/*.yaml`
- `docs/control_checklist.md`
- `reports/enterprise_ai_security_assessment_template.md`
- `reports/evidence_index.md`

## Phase 9 Manual UI Replay

Manual UI Replay 用于未来评估 Chatbot / RAG / Agent 页面：人工输入测试问题，复制页面输出，保存为本地 replay JSON，再由本地 provider 做风险信号分析、脱敏和 evidence 生成。

Phase 9 当前只使用 fake replay 样例：

- Sample：`replays/manual_ui_samples/`
- Schema：`replays/manual_ui_replay_schema.md`
- Provider：`providers/manual_replay_provider.py`
- Config：`runners/promptfoo.manual_ui.yaml`
- Runner：`runners/run_manual_ui_promptfoo.sh`
- Catalog：`test_catalog/manual_ui_test_catalog.yaml`
- Workflow：`docs/manual_ui_assessment_workflow.md`

Dry-run：

```bash
bash runners/run_manual_ui_promptfoo.sh
```

Phase 9.5 已在人工确认后执行本地 fake replay `--execute`，结果为 6 / 0 / 0，并生成 `reports/evidence/promptfoo_manual_ui_result.json`。真实页面接入前必须完成授权、测试账号隔离、数据范围确认、脱敏策略和人工复核流程。

## Phase 12.5 Generic Agent Manual Replay 验证

Phase 12.5 验证了 Generic Agent ATLAS Assessment Pack 的 10 个 fake manual replay 样例能进入现有 Manual UI Replay 评估闭环。Provider 新增了 Agent 专属风险信号分类和布尔字段。当前执行结果为 16 / 0 / 0（原 6 条 + 新增 10 条）。

复盘文档：`docs/phase12_5_generic_agent_manual_replay_review.md`。

## Phase 13 Generic Agent Mock Tool Harness

Phase 13 新增 Generic Agent Mock Tool Harness，用于在本地 fake sandbox 中验证 Agent 安全控制，包括 goal hijacking、memory poisoning、tool metadata/return injection、human confirmation bypass、resource consumption 等 12 个测试场景。

### 关键文件

- Harness：`sandbox/generic_agent_harness/`
- 测试用例：`testcases/generic_agent_mock_harness/examples.yaml`
- Runner：`runners/run_generic_agent_harness.sh`
- Evidence：`reports/evidence/promptfoo_generic_agent_harness_result.json`

### Dry-run

```bash
bash runners/run_generic_agent_harness.sh
```

### Execute

仅在人工确认后执行：

```bash
bash runners/run_generic_agent_harness.sh --execute
```

执行结果：12 / 0 / 0。

复盘文档：`docs/phase13_generic_agent_mock_harness_review.md`。

## Phase 14 OWASP Agentic Top 10 Crosswalk

Phase 14 新增 OWASP Agentic Top 10 Crosswalk，将 Agent 安全测试结果同时映射到 MITRE ATLAS technique、OWASP Agentic Top 10 risk、Generic Agent test capability、evidence、control recommendation 和 report finding language。

### 关键文件

- 风险定义：`owasp/agentic_top10_2026.yaml`
- OWASP → ATLAS 映射：`owasp/agentic_to_atlas_crosswalk.yaml`
- OWASP → Generic Agent 能力映射：`owasp/agentic_to_generic_agent_capabilities.yaml`
- 控制项映射：`owasp/agentic_control_mapping.yaml`
- 报告语言模板：`owasp/agentic_report_language.md`

### 覆盖状态

| 状态 | ASI |
|---|---|
| covered_by_local_harness | ASI01、ASI02、ASI03、ASI06、ASI08、ASI09 |
| partially_covered | ASI04 |
| planned | ASI07、ASI10 |
| not_supported_for_now | ASI05 |

### 与 ATLAS 的关系

OWASP Agentic Top 10 是风险分类层，不替代 MITRE ATLAS。ATLAS 用于"怎么测"，OWASP 用于"怎么报"。两者在 Dashboard 和 Report 中并列展示。

## Phase 16 AI Red Teaming Playbook + Severity Model

Phase 16 新增 AI Red Teaming 执行方法论层，位于 `/red_team/`。该层为执行方法论和模板层，不执行测试、不连接真实目标。

### AI Red Teaming Playbook

`red_team/ai_red_team_playbook.md` 定义了 12 步标准红队评估流程：

1. Scope Definition → Target Profiling → Threat Modeling → Corpus Selection → Test Planning → Execution → Evidence Collection → Finding Analysis → Severity Rating → Mitigation Recommendation → Retest → Final Report

Playbook 是执行方法论层，不替代现有的 ATLAS technique（知识层）、profile（评估对象）、corpus（语料设计）和 runner（执行层）。它回答的是"如何组织一次红队评估"的问题，而 ATLAS / profile / corpus / runner 回答的是"用什么技术、测什么对象、用什么数据、怎么执行"的问题。

### Severity Model

`red_team/finding_severity_model.md` 定义了 7 维度严重性评分模型（D1-D7），用于将 evidence 中观察到的安全行为转化为 finding 的严重性等级：

- **D1 Impact Scope**：从单轮输出影响（0.5）到外部系统影响（3.0）
- **D2 Data Sensitivity**：从无敏感数据（0）到客户/生产数据（3.0）
- **D3 Agentic Capability**：从无工具（0）到多 Agent/MCP 通信（2.5）
- **D4 Exploitability**：从需复杂条件（0.5）到可跨会话持久化（2.0）
- **D5 Control Failure**：从已阻断（0）到无人工确认（2.0）
- **D6 Persistence**：从不持久（0）到长期记忆/skill/plugin（2.0）
- **D7 Evidence Confidence**：low/medium/high（不贡献分数，影响降级）

Score = D1 + D2 + D3 + D4 + D5 + D6，映射为 5 个严重性等级（Informational / Low / Medium / High / Critical）。

Severity Model 连接 evidence → finding → report：evidence 中的布尔字段（如 `should_refuse=false`、`leaked_secret=true`）作为 D1-D6 的输入，计算出 base_score 后确定 severity，最终进入 finding 的 Detailed Findings 和 report 的 Findings Summary。

### Finding Template

`red_team/finding_template.md` 是完整的 finding 记录模板，包含 severity assessment（7 维度表）、MITRE ATLAS / OWASP Agentic / OWASP LLM 框架映射、evidence 引用、reproduction steps、root cause hypothesis、recommended controls、retest method 和 residual risk。

### Evidence Handling Guide

`red_team/evidence_handling_guide.md` 定义了 evidence 的类型、命名规则、脱敏规则和保留策略。它与 `utils/redaction.py` 和 quality check 中的脱敏扫描配合工作。

### Mitigation & Retest Workflow

`red_team/mitigation_retest_workflow.md` 定义了 9 类控制建议和修复后的复测流程：选择回归语料 → 执行复测 → 比较 before/after evidence → 更新 finding。

### Red Team Report Outline

`red_team/red_team_report_outline.md` 是正式红队评估报告的 13 节大纲，从 Executive Summary 到 Limitations + Appendix。

### 当前状态

- red_team/ 是方法论/模板层，所有文件均为模板和指南。
- **未执行真实红队项目**，未对任何真实系统执行红队评估。
- 所有模板均可在未来真实红队评估中复用。
- Severity Model 可以在现有 evidence 上打分验证，但当前不改变任何现有 finding 或 evidence 内容。


## Phase 17 AI Asset Inventory + NIST AI RMF Mapping

Phase 17 新增 AI 应用资产清单（`inventory/`）和 NIST AI RMF 治理映射层（`governance/`），将系统从"安全评估工作台"扩展为"评估 + 治理工作台"。

### AI Asset Inventory

`inventory/` 目录记录 AI 应用资产的 9 分类字段（Basic Info / AI System Type / Model / Data / RAG / Agent Tooling / Security Controls / Assessment Status / Governance），并提供接入登记表单和风险登记表模板。

当前所有资产为 sample/fake 数据。Inventory 是评估入口之一——通过资产类型、工具特征和数据敏感度确定适用的评估 profile。

### AI Application Intake Form

`inventory/ai_application_intake_form.md` 是 AI 应用接入评估流程的入口表单。根据表单结果选择 profile：

| 条件 | 推荐 Profile |
|---|---|
| 仅文本对话，无知识库、无工具 | Chatbot |
| 接入知识库，有检索增强生成 | RAG |
| 接入工具、有外部通道、有写操作 | Agent |
| 仅提供 API 接口调用 | API |
| 仅通过页面人工交互 | Manual UI Replay |

### NIST AI RMF Mapping

`governance/nist_ai_rmf_mapping.yaml` 将系统组件按 NIST AI RMF 的四个 function 映射：

| Function | Support Status | 关键组件 |
|---|---|---|
| Govern | partially_supported | inventory/, governance checklist, RoE, Severity Model |
| Map | supported | Asset Inventory, Profiles, Corpus, ATLAS, OWASP |
| Measure | supported | Runners, Sandboxes, Evidence, Dashboard |
| Manage | partially_supported | Mitigation & Retest, Quality Check |

**重要**：该映射是治理映射层，不代表已完成 NIST 合规认证。


## Phase 18 AI/ML-BOM + Supply Chain Mapping

Phase 18 新增 AI/ML-BOM + Supply Chain Mapping 层（`supply_chain/`），将系统从"评估 + 治理"扩展为"评估 + 治理 + 供应链追溯"。

### AI/ML-BOM Schema

`supply_chain/ai_ml_bom_schema.md` 定义了 9 类组件字段（BOM Metadata、Model、Dataset、Embedding、Tool/Plugin/MCP、Prompt、External API、Runtime/Infrastructure、Dependency Relationship）。每个 BOM 通过 `asset_id` 与 Inventory 中的资产记录关联。

### Sample BOM

`supply_chain/sample_ai_ml_bom.yaml` 包含 5 个样例 BOM，与 `inventory/sample_ai_asset_inventory.yaml` 中的 5 个资产一一对应。每个 BOM 包含完整的模型、数据集、工具、提示词、外部 API 和运行时组件列表，以及依赖关系图。

### Supply Chain Inventories

- **Model Provenance Checklist**：7 类检查（模型来源、许可证、微调、漏洞、供应链攻击防护、依赖审计、退役）
- **Dataset/KB Inventory**：记录数据集/知识库来源、敏感等级、更新频率和验证状态
- **Tool/Plugin/MCP Inventory**：记录工具权限等级、调用类型、写能力和外部网络访问
- **Prompt Template Inventory**：记录提示词模板版本、来源、安全相关性和变更历史
- **External API Dependency Inventory**：记录外部 API 端点、认证方式、数据处理位置和接入状态

### Supply Chain Risk Register

`supply_chain/supply_chain_risk_register_template.yaml` 包含 6 条 sample risk entries，覆盖外部工具提供商、数据溯源、外部 API、MCP/Plugin、模型提供商和提示词模板篡改风险。

### ATLAS/OWASP/NIST Mapping

`supply_chain/supply_chain_to_atlas_owasp_mapping.yaml` 定义了 15 条供应链风险到 ATLAS technique、OWASP Agentic、OWASP LLM 和 NIST AI RMF function 的映射，每条映射包含当前覆盖状态和评估缺口。

### 当前状态

- 所有 BOM 为 sample/fake 数据，不代表任何真实系统的组件依赖关系。
- 供应链风险映射为方法论参考，不构成完整供应链威胁模型。
- 本系统未连接真实模型仓库、真实供应商系统或真实依赖扫描工具。
- 本阶段不运行任何 --execute。

## Phase 19 External Evaluation Tool Adapter Planning

Phase 19 新增外部评估工具 adapter 规划层（`external_tools/`），将 garak、PyRIT、AgentDojo、AgentDyn、Browser Automation 和 API Provider 的未来接入方式统一到 schema、风险边界、ATLAS/OWASP 映射和 dashboard/report 展示中。

### 关键文件

| 文件 | 用途 |
|---|---|
| `external_tools/external_tool_evidence_schema.md` | 外部工具结果统一 evidence schema |
| `external_tools/external_tool_risk_boundary.md` | 外部工具接入风险边界 |
| `external_tools/external_tool_adapter_index.yaml` | 6 个 adapter 的状态和优先级 |
| `external_tools/external_tool_to_atlas_owasp_mapping.yaml` | 外部工具到 ATLAS/OWASP/corpus/evidence 的映射 |
| `external_tools/garak_adapter_plan.md` | garak adapter 设计计划 |
| `external_tools/pyrit_adapter_plan.md` | PyRIT adapter 设计计划 |
| `external_tools/agent_benchmark_adapter_plan.md` | AgentDojo / AgentDyn adapter 设计计划 |
| `external_tools/browser_automation_adapter_plan.md` | Browser Automation adapter 设计计划 |
| `external_tools/api_provider_adapter_plan.md` | API Provider adapter 设计计划 |

### 状态说明

- 本阶段只做 adapter planning / design layer。
- 本阶段不安装 garak、PyRIT、AgentDojo、AgentDyn 或浏览器自动化工具。
- 本阶段不运行任何外部工具，不运行任何 `--execute`。
- 本阶段不连接真实 API、真实 Agent、真实页面或外部网络。
- 外部工具不会替代现有 ATLAS / OWASP / corpus / evidence 体系，未来输出必须归一化到 `external_tool_evidence_schema.md`。

## Phase 20 External Tool Mock Evidence Normalization

Phase 20 使用 fake/mock 外部工具输出验证 `external_tools/` 定义的 evidence schema 和 adapter mapping。

| 文件 | 用途 |
|---|---|
| `external_tools/mock_outputs/` | 6 个 mock external tool raw outputs |
| `scripts/normalize_external_tool_mock_evidence.py` | 标准库 normalizer |
| `external_tools/mock_external_tool_evidence_mapping.yaml` | mock output 到 normalized evidence 映射 |
| `reports/evidence/external_tools/mock_external_tool_normalized_evidence.json` | mock normalized evidence |
| `reports/evidence/external_tools/mock_external_tool_evidence_index.json` | mock evidence index |

该阶段不安装、不运行任何外部工具，不连接真实系统。Normalized evidence 只能用于 adapter pipeline 验证，不可用于正式 finding。

## Phase 15 Evaluation Corpus Architecture

Phase 15 新增统一评估语料库目录 `corpus/`，覆盖 Chatbot、RAG、Agent、API、Business、Regression 六个 profile，共 49 条语料。语料库位于 test design 层，提供格式化的测试设计输入，独立于 testcases（执行层）、replays（人工 replay 层）和 evidence（结果层）。

### 目录结构

```text
corpus/
├── README.md              # 语料库概览与四层分离说明
├── corpus_schema.md       # 统一 schema 定义
├── corpus_index.yaml      # 按 profile / framework / mode / status / severity 索引
├── chatbot/               # 14 条语料（prompt injection / system prompt / sensitive / multilingual）
│   ├── README.md
│   ├── prompt_injection.yaml
│   ├── system_prompt_exposure.yaml
│   ├── sensitive_disclosure.yaml
│   └── multilingual_bypass.yaml
├── rag/                   # 14 条语料（indirect injection / poisoning / fake citation / over-disclosure）
│   ├── README.md
│   ├── indirect_prompt_injection.yaml
│   ├── rag_poisoning.yaml
│   ├── fake_citation.yaml
│   └── over_disclosure.yaml
├── agent/                 # 16 条语料（tool misuse / memory / skill / exfiltration / resource）
│   ├── README.md
│   ├── tool_misuse.yaml
│   ├── memory_poisoning.yaml
│   ├── skill_poisoning.yaml
│   ├── exfiltration.yaml
│   └── resource_consumption.yaml
├── api/                   # 6 条语料（smoke / security baseline）
│   ├── README.md
│   ├── fastgpt_api_smoke.yaml
│   └── api_security_baseline.yaml
├── business/              # 8 条语料（SOC / XDR / policy / project）
│   ├── README.md
│   ├── security_operations.yaml
│   ├── xdr_assistant.yaml
│   ├── policy_qa.yaml
│   └── project_management.yaml
└── regression/            # 9 条回归语料（通过 corpus_id 引用）
    ├── README.md
    ├── smoke_tests.yaml
    ├── core_security_regression.yaml
    └── generic_agent_regression.yaml
```

## Phase 11 API Provider Skeleton

Phase 11 新增测试环境 API Provider Skeleton，用于未来接入 Chatbot / RAG API 的前置框架。当前只支持 dry-run readiness，不连接真实 API、不访问外部网络、不读取真实凭证、不执行真实 HTTP 请求。

### 关键文件

- Target schema：`targets/api/api_target_schema.md`
- Chatbot target sample：`targets/api/chatbot_api_target_sample.yaml`
- RAG target sample：`targets/api/rag_api_target_sample.yaml`
- Provider：`providers/api_chatbot_provider.py`、`providers/api_rag_provider.py`
- Runner：`runners/run_api_chatbot_provider.sh`、`runners/run_api_rag_provider.sh`
- Onboarding：`docs/api_provider_onboarding.md`

### Dry-run

```bash
bash runners/run_api_chatbot_provider.sh
bash runners/run_api_rag_provider.sh
```

Dry-run evidence：

- `reports/evidence/api_chatbot_provider_dry_run.json`
- `reports/evidence/api_rag_provider_dry_run.json`

这些 evidence 只表示 skeleton readiness，不代表真实 API 测试通过。

## Phase 23 Assessment Plan Generator

Phase 23 新增 Assessment Plan Generator，一个独立的评估计划生成层。该层位于测试执行之前，用于根据评估目标、风险分类和可用测试能力自动生成评估计划（即测试设计方案）。

### 关键文件

- Schema：`assessment_plans/assessment_plan_schema.md`
- Generator 脚本：`scripts/generate_assessment_plans.py`
- 生成的计划：`assessment_plans/generated/`（5 个 sample plans）
- 计划索引：`assessment_plans/assessment_plan_index.yaml`

### 设计原则

- **Planning layer only**：评估计划是测试设计，不是证据，不是语料。
- **Corpus 是测试用例资产**：Plan 是针对特定资产的选择 + 执行推荐。
- **Evidence 是测试结果**：Plan 在执行之前，Evidence 在执行之后。
- 所有当前计划均为 `sample/planning_only`，`allowed_now=false`。
- 不执行测试、不连接真实系统、不安装外部工具。

### 运行方式

```bash
python3 scripts/generate_assessment_plans.py
```

### 与现有体系的关系

评估计划（Assessment Plan）位于评估流程中的 corpus（语料设计）之后、执行（execute）之前：

```text
Corpus（测试用例资产）→ Assessment Plan（选择 + 执行推荐）→ Execute（测试执行）→ Evidence（测试结果）
```

## Phase 24 Corpus-to-Testcase Compiler

Phase 24 新增 Corpus-to-Testcase Compiler（`scripts/compile_corpus_to_testcases.py`），将 corpus/ 下的 YAML 语料自动编译为标准化测试用例和 promptfoo 兼容的测试集草案。

- 输入：`corpus/` 下 status=active/regression 的 YAML 语料文件
- 输出：`generated_testcases/` 下的标准化 testcases YAML + promptfoo 草稿
- 状态：compilation only，不执行测试，不连接真实系统
- 覆盖 profile：chatbot（22）、rag（14）、agent（16）、api（10）、regression（9）
- 总计：61 个 generated testcases / 52 promptfoo drafts

## Phase 25 Generated Testcase Curation & Runner Binding

Phase 25 新增 Generated Testcase Curation & Runner Binding 层（`scripts/curate_generated_testcases.py`），对 Phase 24 生成的 61 个测试草案进行静态分类：32 curated_candidate、29 manual_review_required。建立 5 个 runner binding 草案。Curation 是静态分析，不运行测试，不连接真实系统。结果在 `curation/` 目录。

## Phase 27 Regression Suite Dry-Run Validator

Phase 27 新增 Regression Suite Dry-Run Validator（`scripts/validate_regression_suite_dry_run.py`），在 Phase 26/26.5/27A 构建的回归测试套件之上建立静态验证层。该层位于 suite build 和 future execution 之间，确保套件在进入实际运行时前已完成引用完整性、框架映射和边界合规检查。

### 关键文件

- Validator 脚本：`scripts/validate_regression_suite_dry_run.py`
- 验证输出：`regression_suites/validation/`
- 验证摘要：`regression_suites/validation/validation_summary.md`

### 验证范围

| 项目 | 结果 |
|---|---|
| Suites validated | 7（core_llm、chatbot、rag、agent、api、owasp_llm、owasp_agentic） |
| Promptfoo drafts validated | 7 |
| Reference integrity | PASS |
| Framework mapping | PASS |
| Boundary compliance | PASS |
| ASI07 gap | Documented and accepted |

### 设计原则

- **Validation mode**: `static_dry_run_only`
- **Validation != evidence**: 不执行测试、不执行 promptfoo、不连接真实系统、不生成 evidence。
- 验证结果只说明套件结构完整性，不代表测试执行通过。

### 与相邻阶段的关系

```text
Phase 26 Curated Regression Suite Builder
        ↓
Phase 26.5 Gap Triage
        ↓
Phase 27A Corpus & Curation Backfill
        ↓
Phase 27 Regression Suite Dry-Run Validator（← 当前阶段，验证层）
        ↓
未来：Regression Suite Execute（执行层）
```

## Phase 28 Assertion & Risk Signal Rule Engine

Phase 28 新增 Assertion & Risk Signal Rule Engine（`rules/` 目录），在回归套件 dry-run 验证之后增加"断言判断规则层"。该层定义了统一的规则体系，用于将测试结果中的 JSON 字段转换为可复制的断言判断。

### 关键文件

- 风险信号规则：`rules/risk_signal_rules.yaml`（24 条规则，覆盖 prompt injection、system prompt exposure、RAG poisoning、Agent tool misuse 等）
- 预期行为规则：`rules/expected_behavior_rules.yaml`（15 条规则，定义 AI 系统的期望安全行为）
- OWASP LLM 断言映射：`rules/owasp_llm_assertion_mapping.yaml`
- OWASP Agentic 断言映射：`rules/owasp_agentic_assertion_mapping.yaml`
- ATLAS 断言映射：`rules/atlas_assertion_mapping.yaml`
- Severity 规则映射：`rules/severity_rule_mapping.yaml`（规则违反到 severity 等级的自动对应）
- 规则索引：`rules/rule_index.yaml`
- 验证脚本：`scripts/validate_assertion_rules.py`

### 规则层的位置

```text
Corpus（语料）→ Testcases（测试用例）→ Curation（筛选）→ Regression Suites（回归套件）→ Validation（结构验证）→ Rules（断言规则）→ Evidence（测试证据）
```

规则层（Rules）位于验证层（Validation）与证据层（Evidence）之间——它为证据中的断言判断提供标准化依据。

### 设计原则

- **Static rule validation only**（`validation_mode: static_rule_validation`）：不对真实系统执行任何测试，不运行 promptfoo，不生成 evidence。
- **Rules != evidence**：规则是断言判断的参考依据，不是测试执行结果。
- **规则独立于执行层**：不依赖 sandbox、provider 或 runner，可以被任何评估链路引用。
- **三层断言体系**：每个规则可同时映射到 OWASP LLM、OWASP Agentic 和 MITRE ATLAS。

### 与相邻阶段的关系

```text
Phase 27 Regression Suite Dry-Run Validator
        ↓
Phase 28 Assertion & Risk Signal Rule Engine（← 当前阶段，规则定义层）
        ↓
未来：Assertion-Driven Execution（规则驱动测试执行）
```

### 运行方式

```bash
python3 scripts/validate_assertion_rules.py
```

## Phase 30 Formal Report Package Builder

Phase 30 新增 Formal Report Package Builder（`delivery_packages/` 目录），作为评估流程中的**正式报告交付包构建层**。该层从所有已完成的评估产物中自动组装标准化企业交付包。

### 关键文件

- 交付包 schema：`delivery_packages/delivery_package_schema.md`
- 边界声明：`delivery_packages/delivery_package_boundary.md`
- 构建脚本：`scripts/build_delivery_package.py`
- 样例交付包：`delivery_packages/generated/sample_enterprise_assessment_package/`（13 章节）

### 设计原则

- **Sample/mock delivery only**：所有内容为 sample/mock，不包含真实客户、真实目标或正式评估结论。
- **边界标志**：`real_customer=false`、`real_target_validated=false`、`formal_report=false`、`usable_for_customer_delivery=false`。
- **No tests executed**：不执行测试、不运行 promptfoo、不连接真实系统。
- **Package ID**：`PACKAGE-2026-001`。

### 运行方式

```bash
python3 scripts/build_delivery_package.py
```

## Phase 31 Generic API Provider Formalization

Phase 31 新增 Generic API Provider Formalization（`api_provider/` 目录），将 Phase 11 的 API Provider Skeleton 升级为形式化的 API Provider 定义层。该层定义了：

- **Provider schema**：6 provider types（chatbot、rag、agent、embedding、completion、multi-modal）
- **Target profile schema**：5 environment types（local、dev、staging、production、sandbox）
- **Config template**：标准化 API provider 配置文件
- **Normalization schema**：6 redaction rules（honeytoken、email、token、secret、path、credential）
- **Safety guardrails**：G01-G16，3 层（input validation、output redaction、execution control）
- **Execution boundary**：定义 API provider 的执行边界和限制
- **Dry-run simulator**：本地 dry-run 模拟器，验证 provider 配置
- **Validation script**：15 checks（schema validation、config integrity、guardrail compliance、dry-run execution）
- **5 sample targets**：覆盖不同 environment type 和 provider type

### 设计原则

- **Static definition only**：所有内容为静态定义和 dry-run 配置，不连接真实 API、不读取真实凭证、不访问真实 endpoint、不执行真实安全测试。
- **所有 sample target 声明**：`real_target=false`、`dry_run_only=true`、`execution_allowed=false`、`usable_for_real_test=false`。
- **未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试**。

### 关键文件

- Provider schema：`api_provider/provider_schema.md`
- Target profile schema：`api_provider/target_profile_schema.md`
- Config template：`api_provider/config_template.yaml`
- Normalization schema：`api_provider/normalization_schema.md`
- Safety guardrails：`api_provider/safety_guardrails.md`
- Execution boundary：`api_provider/execution_boundary.md`
- Dry-run simulator：`api_provider/dry_run_simulator.py`
- Validation script：`api_provider/validate_api_provider_config.py`
- Sample targets：`api_provider/sample_targets/`
