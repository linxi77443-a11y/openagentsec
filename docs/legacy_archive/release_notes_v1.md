# Release Notes: AI Security Assessment & Governance Workbench v1.3

## 版本名称

**AI Security Assessment & Governance Workbench v1.3**

Phase 21 完成系统发布收口，版本从 v1.1 升级至 v1.3。

## 完成阶段

- Phase 7：ATLAS 驱动评估系统核心
- Phase 7.5：ATLAS 总控 runner execute 验证
- Phase 8：Dashboard 与报告生成器
- Phase 9：Manual UI Replay 页面评估框架
- Phase 9.5：Manual UI Replay 本地 fake execute 闭环
- Phase 10：v1 文档包、操作手册和路线图收尾
- Phase 11：测试环境 API Provider Skeleton dry-run readiness 框架
- Phase 12：Generic Agent ATLAS Assessment Pack 框架
- Phase 13：Generic Agent Mock Tool Harness（12 scenarios executable）
- Phase 14：OWASP Agentic Top 10 Crosswalk（mapping/documentation layer）
- Phase 15：Evaluation Corpus Architecture（49 entries, 7 profiles, unified schema）
- Phase 16：AI Red Teaming Playbook + Severity Model（execution methodology + 9 templates/guides）
- Phase 16.5：System Acceptance Regression Checkpoint（5 链路全量回归验证）
- Phase 17：AI Asset Inventory + NIST AI RMF Mapping（asset inventory schema + governance mapping layer）
- Phase 18：AI/ML-BOM + Supply Chain Mapping（AI/ML-BOM schema, 5 sample BOMs, 15 supply chain risk mappings）
- Phase 19：External Evaluation Tool Adapter Planning（6 adapters, unified evidence schema, risk boundary, no external execution）
- Phase 20：External Tool Mock Evidence Normalization（6 mock outputs, 6 normalized evidence entries, no external execution）
- **Phase 21：System Release Consolidation v1.3（release 目录，11 个发布收口文档）**
- **Phase 23：Assessment Plan Generator（assessment_plans/，schema、generator、5 sample plans、plan index，planning layer only）**
- **Phase 24：Corpus-to-Testcase Compiler（generated_testcases/，61 testcases，52 promptfoo drafts，compilation only）**
- **Phase 25：Generated Testcase Curation & Runner Binding（curation/，32 curated_candidate，29 manual_review_required，5 runner binding drafts，curation only）**
- **Phase 26：Curated Regression Suite Builder（regression_suites/，7 suites，65 selected，7 promptfoo drafts，static build only）**
- **Phase 26.5：Regression Suite Gap Triage（suite_gap_analysis.md，zero-selected suite root cause analysis，framework gap triage）**
- **Phase 27A：Corpus & Curation Backfill（fake_assets_required 修复、API corpus backfill、risk type 多值映射，zero-selected suites 3→0，curated_candidate 32→59，regression suite 65→104）**
- **Phase 27：Regression Suite Dry-Run Validator（7 suites validated，7 promptfoo drafts validated，static structure validation only，validation != evidence）**
- **Phase 28：Assertion & Risk Signal Rule Engine（rules/ directory，24 risk signal rules，15 expected behavior rules，OWASP LLM/Agentic/ATLAS assertion mappings，severity rule mapping，static rule validation only）**
- **Phase 30：Formal Report Package Builder（delivery_packages/ directory，schema，boundary doc，builder script，sample_enterprise_assessment_package with 13 sections，sample/mock only）**（commit b9756f2）
- **Phase 30.5：System Acceptance & Release Consolidation v1.4（release/ 目录新增 v1.4 发布文档，system acceptance，consolidation_only，无新增能力，无测试执行，无真实系统连接）**（commit pending）
- **Phase 31：Generic API Provider Formalization（api_provider/ 目录结构、provider schema（6 provider types）、target profile schema（5 environment types）、config template、normalization schema（6 redaction rules）、safety guardrails（G01-G16，3 层）、execution boundary、dry-run simulator、validation script（15 checks）、5 sample targets。所有 sample target 声明 real_target=false、dry_run_only=true、execution_allowed=false、usable_for_real_test=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试）**
- **Phase 31B：Authorized Test Target Onboarding（api_provider/onboarding/ 子目录，11 个核心文件，授权流程 5 步、环境隔离 3 类、凭证安全加载 6 项控制、速率限制 4 级、安全拆除流程、validation script 18 项检查。所有目标声明 authorized=true、approved_by=human、testing_period=timeboxed、data_scope=restricted。未连接真实目标、未加载真实凭证、未执行真实安全测试）**
- **Phase 31C：Local Mock API Execution Harness（api_provider/mock_harness/ 子目录，9 个核心文件，mock API target schema、mock request/response fixtures 8 请求/8 响应覆盖 5 种 provider 类型、mock execution trace、normalized response samples、execution boundary、run/validate 脚本。所有输出声明 mock_execution=true、external_network_called=false、credentials_loaded=false、real_target_connected=false、evidence_generated=false、usable_for_formal_finding=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint）**（commit pending）
- **Phase 31D：Limited Authorized API Dry-Run Plan（api_provider/authorized_dry_run_plan/ 目录，11 个文件，定义 dry-run plan schema、preflight checklist、test target readiness gate、credential readiness checklist、rate limit/request budget policy、allowed test bundle definition、rollback/stop condition policy、approval packet template。所有文件为 placeholder/模板/计划内容，不包含真实 URL/token/email/API key。所有标志声明：dry_run_plan_only=true、authorization_required=true、approval_status=not_approved、execution_allowed=false、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false、production_target_allowed=false。未连接真实目标、未加载真实凭证、未发起网络请求）**
	- **Phase 31E：Single Authorized API Smoke Test Design（api_provider/single_smoke_test_design/ 目录，11 个文件，smoke test schema、candidate target template、minimal request bundle（4 条低风险请求）、expected safe response contract、execution preflight gate（12 项）、abort condition checklist、operator runbook、evidence placeholder schema。所有标志声明：only_one_target_allowed=true、read_only_operations_only=true、no_adversarial_or_jailbreak_prompts=true、no_data_exfiltration_attempts=true、no_system_prompt_extraction=true、no_tool_abuse_attempts=true。所有文件为设计/占位内容，不包含真实 API target、不包含真实凭证、不连接真实系统）**（commit pending）
- **Phase 31F：Single Smoke Test Approval Packet & Go/No-Go Gate（api_provider/smoke_test_approval_packet/ 目录，10 个设计文件 + 验证脚本，定义 approval packet schema、go/no-go checklist（10 项）、approval packet template、pre-execution readiness summary、operator signoff placeholder、risk acceptance placeholder、execution hold statement。所有标志声明：approval_packet_ready=true、approval_status=not_approved、go_no_go_status=no_go、execution_allowed=false、human_approval_required=true、operator_signoff_required=true、risk_acceptance_required=true、execution_hold=true。所有文件为设计/审批/门禁内容，不包含真实 API target、不包含真实凭证、不连接真实系统）**（commit pending）
	- **Phase 32C：Full Authorized API Regression Execution（Execute full regression against authorized test API，evidence generation with redaction，finding candidates (needs_human_review)，no production access）**（commit pending）
	- **Phase 32D：Real API Regression Assessment Report Builder（Build complete assessment report from Phase 32C results，read-only report layer，redaction_applied=true，findings remain candidate status，not formal customer report）**（commit pending）
	- **Phase 33：Remediation & Retest Package Builder
		- **Phase 34A：DeepSeek Judge Provider Framework（tool_judge_providers/ directory with DeepSeek judge provider: template, schema, prompt templates for 8 use cases, mock results, adapter skeleton with 11 stub methods, build/validate scripts. All mock_only — no real API calls, no credentials, no network. All judge results declare network_called=false, credential_loaded=false, usable_for_formal_finding=false）**（5 remediation packages for 5 consolidated finding groups: system_prompt_leakage, sensitive_disclosure, rag_exposure, prompt_injection_bypass, api_boundary_weakness. remediation_task_board with 10 tasks (4 P0, 3 P1, 3 P2). 5 retest packages, execution plan, acceptance criteria, before/after comparison template. build_remediation_retest_packages.py and validate_remediation_retest_packages.py (87 checks). All remediation status: remediation_planned. All retest status: retest_not_executed. real_api_execution_allowed: false. No re-running tests, no connecting to APIs, no reading credentials. All findings remain candidate status, need human review）**（commit pending）
		- **Phase 34B：DeepSeek Judge Go/No-Go Packet（tool_judge_providers/deepseek/go_no_go/ directory with 8 packet files: approval packet, approval checklist, cost budget, execution plan, safety boundary, rollback plan, acceptance criteria, local config template. validation script with 6 sections, 18+ checks. All approval_status=not_approved, execution_allowed=false, network_allowed=false, credential_loaded=false, deepseek_api_called=false. No real API calls, no credentials, no network. Config template uses PLACEHOLDER only）**（commit pending）
		- **Phase 34C：Controlled DeepSeek Judge Execution（Real DeepSeek API (deepseek-v4-flash) called 21 times. 16 finding candidates judged (15 batch + 1 smoke), 5 consolidated groups reviewed. 0 errors, ~$0.01 cost. All security boundaries enforced: no target API calls, no new test generation, usable_for_formal_finding=false, manual_review_required=true, formal_finding=false. Approval: approval_status=approved, max_judge_calls=22. Output: tool_judge_providers/deepseek/executions/phase34c_controlled_judge/. All validation checks passed）**（commit pending）
		- **Phase 34D：DeepSeek Judge Result Integration & Review Report（Static integration of Phase 34C/34C.0/34C.1 results into structured review summary, human review handoff, dashboard/report/docs updates. No API re-call, no .local/ read, no target API connection, no test re-run. All judge results remain candidate status, require human review）**
		- **Phase 35：Promptfoo Integration Framework（tool_integrations/promptfoo/ directory with integration boundary, config index, result schema, mock results, evidence mapping, finding candidate mapping, DeepSeek judge handoff schema, adapter skeleton. No promptfoo eval, no target API connection, no DeepSeek API call. All execution_mode=mock/dry_run, all real_target_connected=false, all usable_for_formal_finding=false. Adapter real execution functions raise NotImplementedError until human Go/No-Go）**
		- **Phase 35B：Promptfoo Go/No-Go Packet（tool_integrations/promptfoo/go_no_go/ directory with 9 packet files: approval packet, approval checklist, execution scope, cost/request budget, preflight checklist, execution boundary, rollback plan, acceptance criteria, local config template. All approval_status=not_approved, execution_allowed=false, network_allowed=false, promptfoo_eval_allowed=false, target_api_call_allowed=false, deepseek_judge_allowed=false, credential_loaded=false, human_go_no_go_required=true, result_can_create_formal_finding=false. No promptfoo eval, no target API call, no DeepSeek API call, no .local/ read. Validate: 58 passed, 0 failed.）**
		- **Phase 35C.0：Promptfoo Execution Readiness Gate（tool_integrations/promptfoo/readiness/ directory with execution readiness gate document, validate script with 94 static checks. Verification dimensions: secret isolation, API isolation, network safety, command safety, adapter safety, Go/No-Go security flags. readiness_status=pass. No promptfoo eval, no target API, no DeepSeek API, no .local/ read, no formal finding. Does not replace Phase 35B Go/No-Go.）**

## 关键提交

- `bee7b3a phase7 add atlas-driven assessment system core`
- `0c70eb3 phase7.5 validate atlas assessment runner execution`
- `ba7a6c9 phase8 add atlas dashboard and report generator`
- `89e8a4d phase9 add manual ui replay assessment mode`
- `a48f1c1 phase9.5 execute manual ui replay workflow`
- `0431c1b phase10 finalize v1 documentation and operations guide`
- `c5c7474 phase11 add api provider skeleton`
- `a7d0e4b phase13 add generic agent mock tool harness`
- `b9756f2 phase30 add formal report package builder`
- `pending phase30.5 add system acceptance and release consolidation v1.4`

## 当前测试统计

| 链路 | Pass / Fail / Error |
|---|---|
| Chatbot | 9 / 0 / 0 |
| RAG | 12 / 0 / 0 |
| Agent | 10 / 0 / 0 |
| Manual UI Replay | 16 / 0 / 0 |
| Generic Agent Mock Tool Harness | 12 / 0 / 0 |
| API Provider Skeleton | dry-run readiness only |
| Generic Agent Assessment Pack | framework / methodology only |
| Evaluation Corpus | 67 entries / 7 profiles / corpus_ready |
| AI Red Teaming Playbook | methodology / template / 12-step standard process |
| Severity Model | methodology / 7-dimension scoring model |
| Finding Template | methodology / comprehensive finding template |
| Evidence Handling Guide | methodology / 9-section evidence guide |
| Mitigation & Retest Workflow | methodology / 9 control categories + retest process |
| Red Team Report Outline | methodology / 13-section report outline |
| System Acceptance Checkpoint | Phase 16.5 — all 5 chains passed |
| AI Asset Inventory | Phase 17 — schema, sample assets, intake form, risk register |
| NIST AI RMF Governance Mapping | Phase 17 — Govern/Map/Measure/Manage mapping |
| AI/ML-BOM + Supply Chain Mapping | Phase 18 — schema, 5 sample BOMs, 10 inventories, 15 risk mappings |
| External Evaluation Tool Adapter Planning | Phase 19 — 6 adapters, evidence schema, risk boundary, planning/design only |
| External Tool Mock Evidence Normalization | Phase 20 — 6 mock outputs, 6 normalized evidence entries, pipeline validation only |
| Assessment Plan Generator | Phase 23 — assessment_plans/ schema, generator script, 5 sample plans, plan index, planning layer only |
| Corpus-to-Testcase Compiler | Phase 24 — generated_testcases/ 61 testcases, 52 promptfoo drafts, compilation only |
| Generated Testcase Curation & Runner Binding | Phase 25 — curation/ 32 curated_candidate, 29 manual_review_required, 5 runner binding drafts, curation only |
| Curated Regression Suite Builder | Phase 26 — regression_suites/ 7 suites, 65 selected, 7 promptfoo drafts, static build only |
| Regression Suite Gap Triage | Phase 26.5 — suite_gap_analysis.md, zero-selected suite analysis, framework gap triage |
| Corpus & Curation Backfill | Phase 27A — fake_assets_required 修复, API corpus backfill, risk type 多值映射, zero-selected suites 3→0, LLM gaps 3→0, Agentic gaps 5→1, curated_candidate 32→59, manual_review_required 29→6, regression suite 65→104 |
| Regression Suite Dry-Run Validator | Phase 27 — regression_suites/validation/ 7 suites validated, 7 promptfoo drafts validated, static structure validation only, validation != evidence |
| Assertion & Risk Signal Rule Engine | Phase 28 — rules/ 24 risk signal rules, 15 expected behavior rules, OWASP LLM/Agentic/ATLAS assertion mappings, severity rule mapping, static rule validation only |
| Formal Report Package Builder | Phase 30 — delivery_packages/ schema, boundary doc, builder script, sample_enterprise_assessment_package with 13 sections, sample/mock only |
| System Acceptance & Release Consolidation v1.4 | Phase 30.5 — release/ v1.4 发布文档，system acceptance，consolidation_only，无新增能力，无测试执行，无真实系统连接 |
| Generic API Provider Formalization | Phase 31 — api_provider/ 目录结构、provider schema、target profile schema、config template、normalization schema、safety guardrails、execution boundary、dry-run simulator、validation script、5 sample targets。所有 sample target 声明 real_target=false、dry_run_only=true、execution_allowed=false、usable_for_real_test=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试 |
| Authorized Test Target Onboarding | Phase 31B — api_provider/onboarding/ 子目录，11 个核心文件，授权流程 5 步、环境隔离 3 类、凭证安全加载 6 项控制、速率限制 4 级、安全拆除流程、validation script 18 项检查。所有目标声明 authorized=true、approved_by=human、testing_period=timeboxed、data_scope=restricted。未连接真实目标、未加载真实凭证、未执行真实安全测试 |
| Local Mock API Execution Harness | Phase 31C — api_provider/mock_harness/ 子目录，9 个核心文件，mock API target schema、mock request/response fixtures（8 请求/8 响应，覆盖 5 种 provider 类型）、mock execution trace、normalized response samples、execution boundary、run/validate 脚本。所有输出声明 mock_execution=true、external_network_called=false、credentials_loaded=false、real_target_connected=false、evidence_generated=false、usable_for_formal_finding=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint |
| Limited Authorized API Dry-Run Plan | Phase 31D — api_provider/authorized_dry_run_plan/ 目录，11 个文件，dry-run plan schema、preflight checklist、test target readiness gate、credential readiness checklist、rate limit/request budget policy、allowed test bundle definition、rollback/stop condition policy、approval packet template。所有文件为 placeholder/模板/计划内容，不包含真实 URL/token/email/API key。所有标志声明：dry_run_plan_only=true、authorization_required=true、approval_status=not_approved、execution_allowed=false、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false、production_target_allowed=false。未连接真实目标、未加载真实凭证、未发起网络请求 |

## 当前 ATLAS coverage 状态

| 状态 | 数量 |
|---|---:|
| covered | 14 |
| partially_covered | 1 |
| planned | 4 |
| not_applicable | 1 |

Manual UI Replay 在 v1 中作为本地 fake replay 能力加入 coverage 来源，但不代表真实页面或企业系统覆盖。

## 当前主要限制

- 仅支持本地 sandbox、fake replay 和 API Provider Skeleton dry-run readiness。
- 不连接真实 API、真实模型、真实页面或企业系统。
- 不读取真实账号、密码、token、API key 或环境变量。
- 不执行浏览器自动化。
- 不安装 garak、PyRIT、AgentDojo、AgentDyn 或浏览器自动化工具。
- External Tool Adapter 当前只做规划/设计和 mock normalization，不运行任何真实外部工具，不生成真实 external tool evidence。
- Model extraction、membership inference、training data poisoning、AI supply chain 等仍为 planned 或 out-of-scope。

## 后续路线图

已完成：Phase 14 OWASP Agentic Top 10 Crosswalk（映射/文档层，无 execute）。
已完成：Phase 15 Evaluation Corpus Architecture（49 条语料、7 个 profile、统一 schema）。
已完成：Phase 16 AI Red Teaming Playbook + Severity Model（执行方法论层，9 个模板/指南/工作流文件，不执行测试）。
已完成：Phase 16.5 System Acceptance Regression Checkpoint（5 条评估链路全量回归验收，版本升级至 v1.1）。
已完成：Phase 17 AI Asset Inventory + NIST AI RMF Mapping（资产清单 schema + 治理映射层，不执行测试）。
已完成：Phase 18 AI/ML-BOM + Supply Chain Mapping（AI/ML-BOM schema、5 sample BOMs、15 条供应链风险映射，不执行测试）。
已完成：Phase 19 External Evaluation Tool Adapter Planning（garak/PyRIT/Agent benchmark/Browser/API adapter 规划层，不安装不运行外部工具）。
已完成：Phase 20 External Tool Mock Evidence Normalization（fake/mock outputs 到 normalized evidence 的 pipeline 验证，不运行真实外部工具）。
已完成：Phase 21 System Release Consolidation v1.3（release 目录，11 个发布收口文档，系统发布收口）。
已完成：Phase 23 Assessment Plan Generator（assessment_plans/，schema、generator、5 sample plans、plan index，planning layer only）。
已完成：Phase 24 Corpus-to-Testcase Compiler（generated_testcases/，61 testcases，52 promptfoo drafts，compilation only）。
已完成：Phase 25 Generated Testcase Curation & Runner Binding（curation/，32 curated_candidate，29 manual_review_required，5 runner binding drafts，curation only）。
已完成：Phase 26 Curated Regression Suite Builder（regression_suites/，7 suites，65 selected，7 promptfoo drafts，static build only）。
已完成：Phase 26.5 Regression Suite Gap Triage（suite_gap_analysis.md，zero-selected suite root cause analysis，framework gap triage）。
已完成：Phase 27A Corpus & Curation Backfill（fake_assets_required 修复、API corpus backfill、risk type 多值映射，zero-selected suites 3→0，curated_candidate 32→59，regression suite 65→104）。
已完成：Phase 27 Regression Suite Dry-Run Validator（7 suites validated，7 promptfoo drafts validated，static structure validation only，validation != evidence，ASI07 gap documented and accepted）。
已完成：Phase 28 Assertion & Risk Signal Rule Engine（rules/ directory，24 risk signal rules，15 expected behavior rules，OWASP LLM/Agentic/ATLAS assertion mappings，severity rule mapping，static rule validation only）。
已完成：Phase 30 Formal Report Package Builder（delivery_packages/ directory，schema，boundary doc，builder script，sample_enterprise_assessment_package with 13 sections，sample/mock only）。（commit b9756f2）
已完成：Phase 30.5 System Acceptance & Release Consolidation v1.4（release/ 目录新增 v1.4 发布文档，system acceptance，consolidation_only，无新增能力，无测试执行，无真实系统连接）。（commit pending）
已完成：Phase 31 Generic API Provider Formalization（api_provider/ 目录结构、provider schema、target profile schema、config template、normalization schema、safety guardrails、execution boundary、dry-run simulator、validation script、5 sample targets。所有 sample target 声明 real_target=false、dry_run_only=true、execution_allowed=false、usable_for_real_test=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试）。
已完成：Phase 31B Authorized Test Target Onboarding（api_provider/onboarding/ 子目录，11 个核心文件，授权流程 5 步、环境隔离 3 类、凭证安全加载 6 项控制、速率限制 4 级、安全拆除流程、validation script 18 项检查。所有目标声明 authorized=true、approved_by=human、testing_period=timeboxed、data_scope=restricted。未连接真实目标、未加载真实凭证、未执行真实安全测试）。
已完成：Phase 31C Local Mock API Execution Harness（api_provider/mock_harness/ 子目录，9 个核心文件，mock API target schema、mock request/response fixtures（8 请求/8 响应，覆盖 5 种 provider 类型）、mock execution trace、normalized response samples、execution boundary、run/validate 脚本。所有输出声明 mock_execution=true、external_network_called=false、credentials_loaded=false、real_target_connected=false、evidence_generated=false、usable_for_formal_finding=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint）。
已完成：Phase 31D Limited Authorized API Dry-Run Plan（api_provider/authorized_dry_run_plan/ 目录，11 个文件，dry-run plan schema、preflight checklist、test target readiness gate、credential readiness checklist、rate limit/request budget policy、allowed test bundle definition、rollback/stop condition policy、approval packet template。所有文件为 placeholder/模板/计划内容，不包含真实 URL/token/email/API key。所有标志声明：dry_run_plan_only=true、authorization_required=true、approval_status=not_approved、execution_allowed=false、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false、production_target_allowed=false。未连接真实目标、未加载真实凭证、未发起网络请求）。
已完成：Phase 31E Single Authorized API Smoke Test Design（api_provider/single_smoke_test_design/ 目录，11 个文件，smoke test schema、candidate target template、minimal request bundle（4 条低风险请求）、expected safe response contract、execution preflight gate（12 项）、abort condition checklist、operator runbook、evidence placeholder schema。所有标志声明：only_one_target_allowed=true、read_only_operations_only=true、no_adversarial_or_jailbreak_prompts=true、no_data_exfiltration_attempts=true、no_system_prompt_extraction=true、no_tool_abuse_attempts=true。所有文件为设计/占位内容，不包含真实 API target、不包含真实凭证、不连接真实系统）。
已完成：Phase 31F Single Smoke Test Approval Packet & Go/No-Go Gate（api_provider/smoke_test_approval_packet/ 目录，10 个设计文件 + 验证脚本，定义 approval packet schema、go/no-go checklist（10 项）、approval packet template、pre-execution readiness summary、operator signoff placeholder、risk acceptance placeholder、execution hold statement。所有标志声明：approval_packet_ready=true、approval_status=not_approved、go_no_go_status=no_go、execution_allowed=false、human_approval_required=true、operator_signoff_required=true、risk_acceptance_required=true、execution_hold=true。所有文件为设计/审批/门禁内容，不包含真实 API target、不包含真实凭证、不连接真实系统）。
已完成：Phase 32C Full Authorized API Regression Execution（Execute full regression against authorized test API，evidence generation with redaction，finding candidates (needs_human_review)，no production access）。
已完成：Phase 32D Real API Regression Assessment Report Builder（Build complete assessment report from Phase 32C results，read-only report layer，redaction_applied=true，findings remain candidate status，not formal customer report）。
已完成：Phase 33 Remediation & Retest Package Builder（5 remediation packages for 5 consolidated finding groups，remediation_task_board with 10 tasks (4 P0, 3 P1, 3 P2)，5 retest packages，execution plan，acceptance criteria，before/after comparison template，build/validate scripts (87 checks). All remediation status: remediation_planned. All retest status: retest_not_executed. real_api_execution_allowed: false. No re-running tests, no connecting to APIs, no reading credentials. All findings remain candidate status, need human review）。
已完成：Phase 34A DeepSeek Judge Provider Framework（tool_judge_providers/，通用判官模式、DeepSeek 提供者模板/提示模板/模式/模拟结果/适配器骨架，mock_only，不调用真实 DeepSeek API、不读取凭证、不发起网络请求）。
已完成：Phase 34B DeepSeek Judge Go/No-Go Packet（go_no_go/ 目录，8 个审批包文件，approval_status=not_approved，execution_allowed=false，network_allowed=false，credential_loaded=false，deepseek_api_called=false。不调用真实 DeepSeek API、不读取凭证、不发起网络请求）。
已完成：Phase 34C Controlled DeepSeek Judge Execution（21 次真实 DeepSeek API 调用，deepseek-v4-flash，16 个 finding candidates 研判，5 个合并组聚合，0 错误，~$0.01 成本。approval_status=approved，max_judge_calls=22，usable_for_formal_finding=false，manual_review_required=true，formal_finding=false。不涉及目标 API 调用，不生成新测试用例）。
2. Phase 17：garak 本地 mock 接入。
3. Phase 18：PyRIT 本地编排实验。
4. Phase 19：AgentDojo / Agent Benchmark 接入。

## v1 发布结论

当前系统可标记为 **AI Security Assessment & Governance Workbench v1.3**，用于本地学习、演示、方法论验证、evidence 管理、治理映射和报告生成。Phase 21 完成系统发布收口，将 Phase 1–20 全部能力整理为可理解的发布包（`release/`）。真实系统接入必须另行设计授权、账号、数据、日志、脱敏和回滚流程。
