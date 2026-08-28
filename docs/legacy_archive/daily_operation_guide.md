# 日常操作手册

本手册说明如何日常使用当前本地 ATLAS AI 安全评估系统 v1。所有操作默认只面向本地 sandbox 和 fake data。

## 如何查阅 AI Asset Inventory

AI Asset Inventory（`inventory/`）记录 AI 应用资产信息，用于确定评估 profile：

```bash
# 查看资产 schema
cat inventory/ai_asset_inventory_schema.md

# 查看样例资产
cat inventory/sample_ai_asset_inventory.yaml

# 查看资产索引
cat inventory/ai_asset_inventory_index.yaml
```

当前资产为 sample/fake 数据，不代表任何真实系统。Inventory 是评估入口之一，与 profile、corpus、评估流程联动。

## 如何查阅 NIST AI RMF Governance Mapping

NIST AI RMF Mapping（`governance/`）将系统组件映射到 NIST AI RMF 的四个 function：

```bash
# 查看 NIST AI RMF 映射
cat governance/nist_ai_rmf_mapping.yaml

# 查看治理检查清单
cat governance/ai_risk_governance_checklist.md

# 查看治理报告附录模板
cat governance/governance_report_appendix_template.md
```

**重要**：NIST AI RMF Mapping 是项目内部治理映射层，不代表已完成 NIST 合规认证。

## 如何查阅 AI/ML-BOM + Supply Chain Mapping

AI/ML-BOM（`supply_chain/`）记录 AI 系统的组件依赖关系和供应链风险：

```bash
# 查看 BOM schema
cat supply_chain/ai_ml_bom_schema.md

# 查看样例 BOM
cat supply_chain/sample_ai_ml_bom.yaml

# 查看供应链风险登记表
cat supply_chain/supply_chain_risk_register_template.yaml

# 查看供应链风险到 ATLAS/OWASP 映射
cat supply_chain/supply_chain_to_atlas_owasp_mapping.yaml

# 查看模型来源检查清单
cat supply_chain/model_provenance_checklist.md
```

当前所有 BOM 为 sample/fake 数据，不代表任何真实系统的组件依赖关系。

## 如何查阅 External Evaluation Tool Adapter Planning

External Tool Adapter Planning（`external_tools/`）记录未来接入 garak、PyRIT、Agent benchmark、Browser Automation 和 API Provider 的规划：

```bash
# 查看统一 evidence schema
cat external_tools/external_tool_evidence_schema.md

# 查看 adapter index
cat external_tools/external_tool_adapter_index.yaml

# 查看风险边界
cat external_tools/external_tool_risk_boundary.md

# 查看外部工具到 ATLAS/OWASP 映射
cat external_tools/external_tool_to_atlas_owasp_mapping.yaml
```

当前 external_tools 只是 planning/design layer：不要安装或运行 garak、PyRIT、AgentDojo、AgentDyn、Playwright、Selenium 或任何浏览器自动化工具。不要连接真实 API、真实 Agent、真实页面或外部网络。

## 如何检查系统状态

开始任何操作前，先查看 Git 工作区是否干净：

```bash
git status --short
```

如果有源码、配置、文档变更，应先确认这些变更是否属于当前任务。如果只是 `.gitignore` 覆盖的运行时产物，通常不需要提交；如果是未提交的业务文件，应先停止并判断是否需要提交或回滚。

## 如何执行 quality check

quality check 是进入任何执行步骤前的安全门禁：

```bash
bash runners/run_quality_check.sh
```

它会检查 provider 是否仍然指向本地、evidence/log 是否脱敏、ATLAS / dashboard / manual replay 结构是否完整，并运行 Chatbot / RAG / Agent dry-run。它不会执行 `--execute`。

## 如何运行 ATLAS dry-run

ATLAS dry-run 只生成评估计划，不执行测试：

```bash
bash runners/run_atlas_assessment.sh --profile all
```

适合用于确认 profile、runner、evidence 路径和 ATLAS technique 映射是否正确。

## 如何运行本地完整 execute

本地完整 execute 会运行 Chatbot、RAG、Agent 三条自动评估链路，并更新 evidence：

```bash
bash runners/run_atlas_assessment.sh --profile all --execute
```

只有在人工明确确认本地范围后才运行。运行前必须先通过 quality check。不要把该命令用于真实 API、真实模型、真实页面或企业系统。

## 如何单独运行 Chatbot / RAG / Agent

### Chatbot

Dry-run：

```bash
bash runners/run_promptfoo.sh
```

Execute：

```bash
bash runners/run_promptfoo.sh --execute
```

### RAG

Dry-run：

```bash
bash runners/run_rag_promptfoo.sh
```

Execute：

```bash
bash runners/run_rag_promptfoo.sh --execute
```

### Agent

Dry-run：

```bash
bash runners/run_agent_promptfoo.sh
```

Execute：

```bash
bash runners/run_agent_promptfoo.sh --execute
```

单独 execute 同样只限本地 sandbox / fake tools，并应在 quality check 通过后运行。

## 如何运行 Manual UI Replay

Manual UI Replay 默认 dry-run：

```bash
bash runners/run_manual_ui_promptfoo.sh
```

本地 fake replay execute：

```bash
bash runners/run_manual_ui_promptfoo.sh --execute
```

当前只允许读取 `replays/manual_ui_samples/`。不要把真实页面输出、真实账号、真实 token 或企业数据写入 replay JSON。

## 如何运行 API Provider Skeleton dry-run

Phase 11 API Provider Skeleton 只做 readiness 检查，不连接真实 API：

```bash
bash runners/run_api_chatbot_provider.sh
bash runners/run_api_rag_provider.sh
```

输出：

- `reports/evidence/api_chatbot_provider_dry_run.json`
- `reports/evidence/api_rag_provider_dry_run.json`

不要运行 API Provider `--execute`。本阶段即使传入 `--execute` 也必须拒绝。

## 如何生成 External Tool Mock Normalized Evidence

Phase 20 允许运行本地 normalizer：

```bash
python3 scripts/normalize_external_tool_mock_evidence.py
```

输入来自 `external_tools/mock_outputs/`，输出到 `reports/evidence/external_tools/`。该命令不安装、不运行外部工具，不访问网络，不连接真实系统。

## 如何生成评估计划（Assessment Plan）

Phase 23 新增 Assessment Plan Generator，用于根据评估目标、风险分类和可用测试能力自动生成评估计划：

```bash
python3 scripts/generate_assessment_plans.py
```

该命令生成 5 个 sample 评估计划到 `assessment_plans/generated/`，并更新 `assessment_plans/assessment_plan_index.yaml`。

### 输出文件

- `assessment_plans/assessment_plan_index.yaml`：计划索引
- `assessment_plans/generated/`：5 个 sample 评估计划

### 设计原则

- **Planning layer only**：不执行测试、不连接真实系统、不安装外部工具。
- 所有计划均为 `sample/planning_only`，`allowed_now=false`。
- 评估计划是测试设计（选择 + 执行推荐），不是 evidence，不是 corpus。

## 如何执行生成测试用例筛选

Phase 25 新增 Generated Testcase Curation，对 Phase 24 编译的 61 个测试草案进行静态分类和 runner 绑定：

```bash
python3 scripts/curate_generated_testcases.py
```

执行后输出到 `curation/`，包括分类结果（32 curated_candidate、29 manual_review_required）、5 个 runner binding 草案和断言策略映射。Curation 只做静态分析，不执行任何测试。

## 如何编译语料到测试用例

Corpus-to-Testcase Compiler（Phase 24）将 `corpus/` 下的评估语料自动编译为标准化测试用例：

```bash
python3 scripts/compile_corpus_to_testcases.py
```

执行后输出到 `generated_testcases/`：
- `generated_testcases/<profile>/generated_<profile>_testcases.yaml` — 标准化 testcase
- `generated_testcases/<profile>/promptfoo_<profile>_generated.yaml` — promptfoo 草稿
- `generated_testcases/generated_testcase_index.yaml` — 多维索引
- `generated_testcases/generated_testcase_summary.md` — 覆盖摘要

**重要**：编译为 draft only，不执行任何测试。所有 generated testcases 声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。

## 如何执行语料筛选

Generated Testcase Curation（Phase 25）对编译后的测试用例进行静态分类：

```bash
python3 scripts/curate_generated_testcases.py
```

执行后输出到 `curation/`：
- `curation/generated_testcase_curation_result.yaml` — 61 条分类结果
- `curation/curation_summary.md` — 分类摘要
- `curation/runner_binding_index.yaml` — 5 个 runner binding 草案
- `curation/assertion_strategy_mapping.yaml` — 16 种风险类型的断言策略映射
- `curation/manual_review_checklist.md` — 人工复核清单

**重要**：Curation 是静态分类，不执行任何测试。所有 curation 结果声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。所有 runner binding 的 allowed_now=false。

## 如何重新生成 Dashboard / Report

当 evidence、coverage 或文档索引更新后，运行：

```bash
bash scripts/generate_all_reports.sh
```

输出包括：

- `dashboard/dashboard_data.json`
- `dashboard/index.md`
- `dashboard/atlas_dashboard.html`
- `reports/generated_atlas_assessment_report.md`

该命令只读取本地文件，不执行测试，不安装或运行任何外部评估工具。

## 如何运行回归套件 Dry-Run 验证

Phase 27 新增 Regression Suite Dry-Run Validator，用于在回归套件进入实际执行前验证套件结构完整性：

```bash
python3 scripts/validate_regression_suite_dry_run.py
```

输出写入 `regression_suites/validation/`。该命令只做静态结构验证，不执行测试、不执行 promptfoo、不连接真实系统、不生成 evidence。

验证维度：
- **Reference integrity**：确保套件引用的 testcase 和 runner 存在且可解析
- **Framework mapping**：确保 ATLAS/OWASP 映射一致且无缺失
- **Boundary compliance**：确保没有意外标记为 executable 或 real_target_connected

验证结果位于 `regression_suites/validation/validation_summary.md`。

## 如何运行规则验证

Phase 28 新增 Assertion & Risk Signal Rule Engine，用于验证断言规则文件的结构完整性、引用一致性和框架映射正确性：

```bash
python3 scripts/validate_assertion_rules.py
```

该命令读取 `rules/` 目录下的规则定义文件，进行静态结构验证，不执行测试、不执行 promptfoo、不连接真实系统、不生成 evidence。

验证维度：
- **Rule structural integrity**：确保每条规则具有完整的字段和有效值
- **Mapping consistency**：确保 OWASP LLM / OWASP Agentic / ATLAS 映射一致且引用有效
- **Severity mapping**：确保 severity 规则映射覆盖了所有定义的规则

验证结果输出到标准输出（控制台），包含每条规则的验证状态和任何发现的错误。

## 如何查看 evidence

核心 evidence 位于：

- `reports/evidence/promptfoo_chatbot_result.json`
- `reports/evidence/promptfoo_rag_result.json`
- `reports/evidence/promptfoo_agent_result.json`
- `reports/evidence/promptfoo_manual_ui_result.json`
- `reports/evidence/atlas_assessment_summary.json`
- `reports/evidence/api_chatbot_provider_dry_run.json`
- `reports/evidence/api_rag_provider_dry_run.json`
- Generic Agent Assessment Pack（framework/methodology only，无 evidence 文件）

索引文档：`reports/evidence_index.md`。

## 如何查阅 AI Red Teaming 方法论

Phase 16 新增 AI Red Teaming 方法论层，位于 `red_team/`。该层提供红队评估的执行流程、模板、指南和报告大纲，但**不执行任何测试**。

推荐阅读顺序：

```bash
# 先读 playbook 了解红队评估 12 步流程
cat red_team/ai_red_team_playbook.md

# 再看 finding severity model 了解如何给发现项定级
cat red_team/finding_severity_model.md

# 然后在需要时查阅具体模板
cat red_team/finding_template.md
cat red_team/evidence_handling_guide.md
cat red_team/mitigation_retest_workflow.md
cat red_team/red_team_report_outline.md
```

当需要正式授权一次红队评估时，使用 `red_team/rules_of_engagement_template.md`；当需要记录一次测试 session 时，使用 `red_team/test_session_template.md`。

所有模板均为方法论/模板层，**不代表已对任何真实系统执行了红队评估**。

## 如何查看 corpus

Evaluation Corpus 位于 `corpus/`，提供按 profile 组织的结构化语料：

```bash
# 查看语料库概览
cat corpus/README.md

# 查看 corpus 总索引（按 profile / framework / mode / status / severity）
cat corpus/corpus_index.yaml

# 查看特定 profile 语料
cat corpus/chatbot/prompt_injection.yaml
cat corpus/rag/indirect_prompt_injection.yaml
cat corpus/agent/tool_misuse.yaml
cat corpus/api/fastgpt_api_smoke.yaml
cat corpus/business/security_operations.yaml
cat corpus/regression/core_security_regression.yaml
```

Corpus 是 test design 层，位于 testcases（执行层）之上。新增测试用例前，建议先在 corpus 中完成语料设计。

## 如何查看 coverage

主要看：

- `coverage/atlas_coverage_matrix.yaml`
- `coverage/atlas_coverage_summary.md`
- `coverage/coverage_gap_analysis.md`

Dashboard 也会展示覆盖情况：`dashboard/atlas_dashboard.html`。

## 如何提交 Git 快照

完成一个阶段后：

```bash
git status
git add <相关文件>
git commit -m "阶段性提交信息"
```

提交前建议运行：

```bash
bash runners/run_quality_check.sh
bash scripts/generate_all_reports.sh
```

## 常见问题与处理方式

### quality check 失败

先读失败信息，不要绕过检查。常见原因包括新增文件缺失、provider 指向错误、evidence 中出现未脱敏 marker、dashboard 引入外部资源等。

### promptfoo evidence 中出现未脱敏内容

检查对应 runner 是否在执行后调用 redaction 后处理。不要手工编辑 evidence 逃避问题，应修复生成路径。

### dashboard 显示 not_run

通常是对应 evidence 不存在。例如 Manual UI Replay 在未 execute 前显示 `not_run`。如果已经 execute，重新运行 `bash scripts/generate_all_reports.sh`。

### runner 找不到 provider

promptfoo config 中的 provider 路径以 config 所在目录为 basePath。确认 provider 路径是否相对于 `runners/` 正确。

### 不确定是否可以运行 execute

默认不要运行。先确认：目标是否本地、数据是否 fake、provider 是否本地、是否会访问网络、是否有真实凭证风险、是否已通过 quality check。

## Phase 31 Generic API Provider Formalization

Phase 31 新增 Generic API Provider Formalization 层，位于 `api_provider/`。该层将 Phase 11 的 API Provider Skeleton 升级为形式化定义的 API Provider 配置模板、schema、safety guardrails 和 dry-run 验证体系。

### 关键文件

- Provider schema：`api_provider/provider_schema.md`（6 provider types）
- Target profile schema：`api_provider/target_profile_schema.md`（5 environment types）
- Config template：`api_provider/config_template.yaml`
- Normalization schema：`api_provider/normalization_schema.md`（6 redaction rules）
- Safety guardrails：`api_provider/safety_guardrails.md`（G01-G16，3 层）
- Execution boundary：`api_provider/execution_boundary.md`
- Dry-run simulator：`api_provider/dry_run_simulator.py`
- Validation script：`api_provider/validate_api_provider_config.py`
- Sample targets：`api_provider/sample_targets/`（5 个）

### 设计原则

- **Static definition only**：所有内容为静态定义和 dry-run 配置。
- 所有 sample target 声明：`real_target=false`、`dry_run_only=true`、`execution_allowed=false`、`usable_for_real_test=false`。
- 未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试。

### 如何运行验证和 dry-run

验证 API Provider 配置：

```bash
python3 api_provider/validate_api_provider_config.py
```

运行 dry-run 模拟器：

```bash
python3 api_provider/dry_run_simulator.py
```

## Phase 21 v1.3 发布收口

Phase 21 完成系统发布收口。新增 `release/` 目录，包含 11 个发布收口文档。

详见 `release/README.md`。
