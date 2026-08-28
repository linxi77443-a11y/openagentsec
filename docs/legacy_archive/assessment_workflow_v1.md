# 评估流程说明 v1

## 评估流程总图

```text
AI Red Teaming Playbook（red_team/ai_red_team_playbook.md）
AI Asset Inventory（inventory/）→ AI/ML-BOM（supply_chain/）→ External Tool Adapter Planning（external_tools/）→ 选择评估 profile
	        ↓
AI Red Teaming Playbook（red_team/ai_red_team_playbook.md）
Scope → Target Profile → Threat Model → Corpus → Test Plan → Execute → Evidence → Finding → Severity → Mitigation → Retest → Report
        ↓
ATLAS technique / OWASP risk
        ↓
Assessment profile 选择
        ↓
Corpus 语料检索（corpus/corpus_index.yaml）
        ↓
Corpus-to-Testcase Compiler 编译（generated_testcases/）
        ↓
Generated Testcase Curation（curation/）
        ↓
Curated Regression Suite Build（regression_suites/）
        ↓
Regression Suite Dry-Run Validation（regression_suites/validation/）
        ↓
Assertion & Risk Signal Rule Engine（rules/）
        ↓
Test catalog capability 映射
        ↓
Runner dry-run / execute
        ↓
本地 provider / sandbox / fake replay / API skeleton dry-run
        ↓
Promptfoo result JSON evidence
        ↓
Finding 分析 + Severity 评分（red_team/finding_severity_model.md）
        ↓
Finding Generator 生成 finding drafts（findings/）
        ↓
Formal Report Package Builder 构建交付包（delivery_packages/）
        ↓
Redaction 后处理与 quality check
        ↓
Coverage matrix / evidence index
        ↓
Dashboard / Enterprise report
        ↓
复盘、修复建议、路线图
```

## ATLAS technique 到测试能力的映射流程

1. 在 `atlas/atlas_techniques.yaml` 中确认 technique。
2. 在 `coverage/atlas_coverage_matrix.yaml` 中查看覆盖状态。
3. 在 `corpus/corpus_index.yaml` 中按 profile / framework 检索对应语料。
4. 在 `test_catalog/test_capability_index.yaml` 中找到对应 capability。
5. 根据 capability 定位 runner、promptfoo config 和 evidence。
6. 如果 technique 是 `planned` 或 `not_applicable`，不得映射 executable runner 或 evidence。

## Profile 选择流程

```text
目标系统类型
  ├─ Chatbot → assessment_profiles/chatbot_profile.yaml
  ├─ RAG → assessment_profiles/rag_profile.yaml
  ├─ Agent → assessment_profiles/agent_profile.yaml
  ├─ AI Gateway → assessment_profiles/ai_gateway_profile.yaml（planned）
  └─ Generic Agent → assessment_profiles/generic_agent_profile.yaml
```

Profile 决定适用的 ATLAS technique、runner、evidence、控制项和不支持的测试类型。

## Runner 执行流程

Runner 默认 dry-run。execute 需要人工确认本地范围。

```text
run_quality_check.sh
        ↓
run_*_promptfoo.sh dry-run
        ↓
人工确认本地 fake scope
        ↓
run_*_promptfoo.sh --execute
        ↓
promptfoo result JSON
        ↓
redaction 后处理
```

## Evidence 生成流程

自动化链路：

```text
promptfoo config
        ↓
exec provider
        ↓
sandbox / fake tools
        ↓
JSON output
        ↓
promptfoo evidence file
```

Manual UI Replay 链路：

```text
manual replay JSON
        ↓
manual_replay_provider.py
        ↓
risk signal analysis
        ↓
promptfoo evidence file
```

## Redaction 脱敏流程

脱敏覆盖：

- provider 输出
- sandbox 日志
- promptfoo result JSON
- Manual UI replay provider 输出
- dashboard_data 和 generated report 的质量扫描

统一脱敏逻辑位于：`utils/redaction.py`。

quality check 会扫描：

- `reports/evidence/*.json`
- `sandbox/**/*_log.jsonl`
- `dashboard/dashboard_data.json`
- `reports/generated_atlas_assessment_report.md`
- `reports/evidence/promptfoo_manual_ui_result.json`

## External Tool Adapter Planning 流程

```text
external_tools/external_tool_adapter_index.yaml
        ↓
选择未来 adapter（garak / PyRIT / Agent benchmark / Browser / API Provider）
        ↓
读取 risk boundary + evidence schema
        ↓
映射 ATLAS / OWASP / corpus
        ↓
未来 external tool raw output
        ↓
normalized external tool evidence
        ↓
dashboard / report
```

Phase 19 只建立规划和 schema，不安装、不运行任何外部工具，不生成 external tool evidence。外部工具不会替代现有 ATLAS / OWASP / corpus / evidence 体系，只能作为未来受控执行器或编排器。

## External Tool Mock Evidence Normalization 流程

```text
external_tools/mock_outputs/*.json
        ↓
scripts/normalize_external_tool_mock_evidence.py
        ↓
reports/evidence/external_tools/mock_external_tool_normalized_evidence.json
        ↓
reports/evidence/external_tools/mock_external_tool_evidence_index.json
        ↓
dashboard / report
```

该流程只处理 fake/mock outputs，`external_tool_executed=false`、`real_target_connected=false`，不可用于正式 finding。

## Dashboard / Report 生成流程

```text
evidence + coverage + profiles + catalog + docs
        ↓
scripts/generate_all_reports.sh
        ↓
dashboard/dashboard_data.json
        ↓
dashboard/index.md + dashboard/atlas_dashboard.html
        ↓
reports/generated_atlas_assessment_report.md
```

生成脚本只读取本地 JSON / YAML / Markdown 文件，不执行测试，不访问网络。

## API Provider Skeleton 流程

```text
API target placeholder YAML
        ↓
api_*_provider.py dry-run readiness check
        ↓
blocked reasons + safety flags
        ↓
api_*_provider_dry_run.json
        ↓
dashboard / report 显示 skeleton 状态
```

Phase 11 不执行真实 HTTP 请求，不读取真实 token，不访问企业测试环境。dry-run evidence 只能表示 skeleton readiness，不能表示真实 API 已测试通过。

## Manual UI Replay 流程

```text
系统生成测试用例
        ↓
人工在页面输入测试问题
        ↓
人工复制页面输出
        ↓
保存为 replay JSON
        ↓
manual_replay_provider.py 读取本地 replay
        ↓
风险信号分析 + 脱敏
        ↓
promptfoo_manual_ui_result.json
        ↓
dashboard / report 更新
```

v1 当前只执行本地 fake replay 样例。真实页面接入前必须完成授权、账号隔离、数据范围和脱敏流程确认。

## Phase 21 System Release Consolidation v1.3

Phase 21 完成系统发布收口，将 Phase 1–20 成果整理为 v1.3 release package。

详见 `release/` 目录：

- 系统发布说明：`release/system_release_v1_3.md`
- 模块关系图：`release/module_map_v1_3.md`
- 能力矩阵：`release/capability_matrix_v1_3.md`
- 执行状态矩阵：`release/execution_status_matrix_v1_3.md`
- 使用路径：`release/user_journey_v1_3.md`
- 命令速查：`release/operator_quickstart_v1_3.md`
- 已知限制：`release/known_limitations_v1_3.md`
- 后续路线图：`release/next_phase_roadmap_v1_3.md`
- 交付清单：`release/delivery_package_checklist_v1_3.md`

该阶段不新增测试能力、不新增治理框架、不安装外部工具、不运行任何 `--execute`、不连接真实系统。

## Phase 23 Assessment Plan Generator

Phase 23 新增 Assessment Plan Generator，在评估流程中增加"生成评估计划"步骤。

### 评估流程中的位置

评估计划生成位于 Corpus（语料检索）之后、Runner execute（测试执行）之前：

```text
Corpus 语料检索（corpus/corpus_index.yaml）
        ↓
Assessment Plan 生成（assessment_plans/）
        ↓
Test catalog capability 映射
        ↓
Runner dry-run / execute
```

- Schema：`assessment_plans/assessment_plan_schema.md`
- Generator 脚本：`scripts/generate_assessment_plans.py`
- 生成的计划：`assessment_plans/generated/`（5 个 sample plans）
- 计划索引：`assessment_plans/assessment_plan_index.yaml`

### 设计原则

- **Planning layer only**：评估计划是测试设计，不是证据，不是语料。
- 所有当前计划均为 `sample/planning_only`，`allowed_now=false`。
- 不执行测试、不连接真实系统。

### 运行方式

```bash
python3 scripts/generate_assessment_plans.py
```

## Phase 24 Corpus-to-Testcase Compiler

Phase 24 新增 Corpus-to-Testcase Compiler，在评估流程中增加"语料到测试用例编译"步骤。

### 评估流程中的位置

语料编译位于 Corpus（语料检索）之后、Test catalog capability 映射之前：

```text
Corpus 语料检索（corpus/corpus_index.yaml）
        ↓
Corpus-to-Testcase Compiler 编译（generated_testcases/）
        ↓
Generated Testcase Curation（curation/）
        ↓
Curated Regression Suite Build（regression_suites/）
        ↓
Regression Suite Dry-Run Validation（regression_suites/validation/）
        ↓
Test catalog capability 映射
        ↓
Runner dry-run / execute
```

### 关键文件

- 编译脚本：`scripts/compile_corpus_to_testcases.py`
- 生成的 testcases：`generated_testcases/<profile>/generated_<profile>_testcases.yaml`
- promptfoo 草稿：`generated_testcases/<profile>/promptfoo_<profile>_generated.yaml`
- 多维索引：`generated_testcases/generated_testcase_index.yaml`
- 覆盖摘要：`generated_testcases/generated_testcase_summary.md`

## Phase 25 Generated Testcase Curation & Runner Binding

Phase 25 新增 Generated Testcase Curation & Runner Binding 层，在 compilation 之后增加"静态筛选"步骤。对 61 个 generated testcases 进行静态分类（32 curated_candidate、29 manual_review_required），建立 5 个 runner binding 草案。

### 评估流程中的位置

Curation 位于 compilation 之后、Test catalog 之前：

```text
Corpus-to-Testcase Compiler 编译（generated_testcases/）
        ↓
Generated Testcase Curation（curation/）
        ↓
Curated Regression Suite Build（regression_suites/）
        ↓
Regression Suite Dry-Run Validation（regression_suites/validation/）
        ↓
Test catalog capability 映射
```

### 关键文件

- Curation 脚本：`scripts/curate_generated_testcases.py`
- Curation schema：`curation/generated_testcase_curation_schema.md`
- Curation 结果：`curation/generated_testcase_curation_result.yaml`
- Runner binding 索引：`curation/runner_binding_index.yaml`
- Assertion 策略映射：`curation/assertion_strategy_mapping.yaml`
- 人工复核清单：`curation/manual_review_checklist.md`

### 设计原则

- **Static curation only**：不运行测试，不连接真实系统。
- **三层分离**：generated_testcases → curation → curated testcases（未来）。
- **Runner binding 为草案**：所有 binding allowed_now=false。
- 所有 generated testcases 声明 `executed=false`、`real_target_connected=false`、`usable_for_formal_finding=false`。
- 覆盖 profile：chatbot（22）、rag（14）、agent（16）、api（10）、regression（9），总计 61 个 generated testcases / 52 promptfoo drafts。

### 运行方式

```bash
python3 scripts/compile_corpus_to_testcases.py
```

## Phase 27 Regression Suite Dry-Run Validator

Phase 27 新增 Regression Suite Dry-Run Validator，在评估流程中增加"回归套件 dry-run 验证"步骤。

### 评估流程中的位置

Dry-run 验证位于 Curated Regression Suite Build 之后、Test catalog capability 映射之前：

```text
Curated Regression Suite Build（regression_suites/generated/）
        ↓
Regression Suite Dry-Run Validation（regression_suites/validation/）
        ↓
Test catalog capability 映射
```

### 验证范围

- 7 个回归套件（core_llm、chatbot、rag、agent、api、owasp_llm、owasp_agentic）
- 7 个 promptfoo 草稿
- 验证维度：reference integrity、framework mapping、boundary compliance
- ASI07 gap：documented and accepted

### 设计原则

- **Static dry-run only**：不执行测试、不执行 promptfoo。
- **Validation != evidence**：不连接真实系统、不生成 evidence。
- 验证结果只说明套件结构完整性，不代表测试执行通过。

### 运行方式

```bash
python3 scripts/validate_regression_suite_dry_run.py
```

## Phase 28 Assertion & Risk Signal Rule Engine

Phase 28 新增 Assertion & Risk Signal Rule Engine，在评估流程中增加"断言规则引擎"步骤。

### 评估流程中的位置

规则引擎位于 Regression Suite Dry-Run Validation 之后、Test catalog capability 映射之前：

```text
Regression Suite Dry-Run Validation（regression_suites/validation/）
        ↓
Assertion & Risk Signal Rule Engine（rules/）
        ↓
Test catalog capability 映射
```

### 层关系

规则引擎与评估流程中其他层的关系：

```text
rules（断言规则层，定义"如何判断"）
        ↓
corpus（语料设计层，定义"测什么"）
        ↓
generated_testcases（测试用例编译层）
        ↓
curation（测试用例筛选层）
        ↓
regression_suites（回归套件构建层）
        ↓
validation（结构验证层）
        ↓
evidence（测试结果层）
        ↓
findings（finding 生成层）
        ↓
delivery_packages（交付包构建层）
```

### 关键文件

- 风险信号规则：`rules/risk_signal_rules.yaml`（24 条）
- 预期行为规则：`rules/expected_behavior_rules.yaml`（15 条）
- OWASP LLM 断言映射：`rules/owasp_llm_assertion_mapping.yaml`
- OWASP Agentic 断言映射：`rules/owasp_agentic_assertion_mapping.yaml`
- ATLAS 断言映射：`rules/atlas_assertion_mapping.yaml`
- Severity 规则映射：`rules/severity_rule_mapping.yaml`
- 规则索引：`rules/rule_index.yaml`
- 验证脚本：`scripts/validate_assertion_rules.py`

### 设计原则

- **Static rule validation only**（`validation_mode: static_rule_validation`）：不对真实系统执行任何测试。
- **Rules != evidence**：规则是断言判断的参考依据，不是测试执行结果。
- **三层断言体系**：每个规则可同时映射到 OWASP LLM、OWASP Agentic 和 MITRE ATLAS。

### 运行方式

```bash
python3 scripts/validate_assertion_rules.py
```

## Phase 30 Formal Report Package Builder

Phase 30 新增 Formal Report Package Builder，在评估流程最后增加"交付包构建"步骤。

### 评估流程中的位置

交付包构建位于 Finding 生成之后，是评估流程的最后一步：

```text
Finding 分析 + Severity 评分（red_team/finding_severity_model.md）
        ↓
Delivery Package 构建（delivery_packages/）
```

### 关键文件

- 交付包 schema：`delivery_packages/delivery_package_schema.md`
- 边界声明：`delivery_packages/delivery_package_boundary.md`
- 构建脚本：`scripts/build_delivery_package.py`
- 样例交付包：`delivery_packages/generated/sample_enterprise_assessment_package/`（13 章节）

### 设计原则

- **Sample/mock delivery only**：所有内容为 sample/mock，不包含真实客户、真实目标或正式评估结论。
- 边界标志：real_customer=false、real_target_validated=false、formal_report=false、usable_for_customer_delivery=false。
- Package ID：PACKAGE-2026-001。
- 不执行测试、不运行 promptfoo、不连接真实系统。

### 运行方式

```bash
python3 scripts/build_delivery_package.py
```

## Phase 31 Generic API Provider Formalization

Phase 31 新增 Generic API Provider Formalization（`api_provider/`），在交付包构建之后增加"API Provider 形式化定义"步骤。

### 评估流程中的位置

API Provider 形式化定义位于 Formal Report Package Builder 之后，是评估系统的静态 provider 定义层：

```text
Delivery Package 构建（delivery_packages/）
        ↓
API Provider Formalization（api_provider/）
```

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
- 未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试。不运行任何 --execute。

### 运行方式

```bash
python3 api_provider/validate_api_provider_config.py
python3 api_provider/dry_run_simulator.py
```
