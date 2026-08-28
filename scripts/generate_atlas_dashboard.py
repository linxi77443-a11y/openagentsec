#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required for local YAML parsing") from exc

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "dashboard"
SUMMARY_PATH = ROOT / "reports/evidence/atlas_assessment_summary.json"
COVERAGE_PATH = ROOT / "coverage/atlas_coverage_matrix.yaml"
PROFILES_DIR = ROOT / "assessment_profiles"
CATALOG_DIR = ROOT / "test_catalog"

PROJECT_NAME = "AI 安全评估探索"
CURRENT_PHASE = "Phase 35C.0 Promptfoo Execution Readiness Gate"
SCOPE = "本地 sandbox：Chatbot、RAG、Agent；Manual UI fake replay；API Provider Skeleton dry-run only；Generic Agent Mock Tool Harness executable；OWASP Agentic Top 10 Crosswalk mapping layer；OWASP LLM Top 10 Crosswalk mapping layer；Evaluation Corpus 97 entries / 7 profiles；AI Red Teaming Methodology 9 templates/guides；AI Asset Inventory 5 sample assets；NIST AI RMF Mapping Govern/Map/Measure/Manage；AI/ML-BOM + Supply Chain Mapping 11 files / 5 sample BOMs；External Evaluation Tool Adapter Planning 10 files / 6 adapters；External Tool Mock Evidence Normalization 6 mock outputs / 6 normalized evidence entries；Assessment Plan Generator 5 sample plans / 5 assets；Corpus-to-Testcase Compiler 65 generated testcases / 52 promptfoo drafts；Generated Testcase Curation & Runner Binding 65 curated / 59 curated_candidate / 6 manual_review / 5 runner bindings；Curated Regression Suite Builder 7 suites / 104 selected testcases / 7 promptfoo drafts；Regression Suite Gap Triage 0 zero-selected suites / 1 remaining gap (ASI07)；Phase 27A Corpus & Curation Backfill：fix fake_assets_required logic、multi-map risk types、API corpus backfill、assertion strategy补齐；Phase 27 Regression Suite Dry-Run Validator：static dry-run validation of regression suites and promptfoo drafts；Phase 28 Assertion & Risk Signal Rule Engine：static rule layer for 24 risk signal rules, 15 expected behavior rules, OWASP/ATLAS assertion coverage mapping, severity mapping, and manual review rules；Phase 29 Finding Generator Prototype：findings directory schema, generator script, 6 sample/mock finding drafts, finding index, risk register mapping, mitigation/retest mapping；Phase 30 Formal Report Package Builder：delivery_packages directory, delivery package schema, package generation boundary, package builder script, sample enterprise assessment package with 13 sections, package manifest, risk register export, mitigation roadmap；Phase 31 Generic API Provider Formalization：api_provider directory, provider schema, target profile schema, config template, normalization schema, safety guardrails (G01-G16), execution boundary, dry-run simulator, validation script, 5 sample targets (openai_compatible_chat, rag_qa_api, agent_api, workflow_api, fastgpt_compatible), provider_validation_result.yaml, provider_validation_report.md；Phase 31B Authorized Test Target Onboarding：onboarding/ 目录结构、authorized target onboarding schema、RoE checklist、credential isolation policy、test scope definition、allowed/prohibited operations matrix、rate limit and safety window policy、approval gate checklist、onboarding validation script（18 checks）。所有 target 声明 authorization_required=true、approval_status=not_approved、execution_allowed=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint。；Phase 31C: Local Mock API Execution Harness — 本地 mock API 执行框架；Phase 31D: Limited Authorized API Dry-Run Plan — 有限授权 API 干运行计划。；Phase 31E: Single Authorized API Smoke Test Design — 单次授权 API 冒烟测试设计。；Phase 31F: Single Smoke Test Approval Packet & Go/No-Go Gate — 单次冒烟测试审批包与执行/不执行门禁。；Phase 32C: Full Authorized API Regression Execution — execute full regression against authorized test API, generate evidence, generate finding candidates；Phase 32D: Real API Regression Assessment Report Builder — build complete assessment report from Phase 32C results；Phase 32D.1: Chinese Report Localization — preserve English as _en.md, Chinese as default .md, generate bilingual index；Phase 32E: Finding Triage & Report Hardening — generate finding triage materials (16 candidates → 5 groups) and final hardened reports (management brief, final exec summary, final findings, remediation action plan, retest plan)；Phase 33: Remediation & Retest Package Builder — generate 5 remediation packages, 5 retest packages, remediation task board (10 tasks), build/validate scripts, execution plan, acceptance criteria；Phase 34A: DeepSeek Judge Provider Framework — build tool_judge_providers/ directory, DeepSeek judge provider with template, schema, prompt templates, mock results, adapter skeleton, build/validate scripts. All mock — no real API calls, no credentials.；Phase 34B: DeepSeek Judge Go/No-Go Packet — build go_no_go/ directory with approval packet, approval checklist, cost budget, execution plan, safety boundary, rollback plan, acceptance criteria, local config template. All approval_status=not_approved, execution_allowed=false, network_allowed=false, credential_loaded=false. No real API calls, no credentials, no network.；Phase 34C: Controlled DeepSeek Judge Execution — execute 21 real DeepSeek API calls (1 smoke + 15 batch + 5 consolidated groups) against 16 existing finding candidates. No target API calls, no new test generation. All outputs: usable_for_formal_finding=false, manual_review_required=true, formal_finding=false. ~$0.01 cost.；Phase 34C.0: DeepSeek API Call Authenticity Verification — static analysis concluded probable_real_call. reasoning_tokens + prompt_cache fields present (strong evidence), but response_id not saved (cannot correlate in DeepSeek backend). requires_manual_billing_verification=true.；Phase 34C.1: DeepSeek Judge Call Budget Reconciliation — added 4 budget fields (max_candidate_judge_calls=16, max_consolidated_group_judge_calls=5, max_smoke_calls=1, max_total_deepseek_api_calls=22). actual_total=21 <= max_total=22.；Phase 34D: DeepSeek Judge Result Integration & Review Report — integrate Phase 34C/34C.0/34C.1 results into structured review summary, human review handoff, dashboard/report/docs updates. Static integration only — no API re-call, no .local/ read, no target API connection.;Phase 35: Promptfoo Integration Framework — build tool_integrations/promptfoo/ directory with config index, result schema, mock results, evidence mapping, finding candidate mapping, DeepSeek judge handoff schema, adapter skeleton. All mock/dry_run only — no promptfoo eval, no target API connection, no DeepSeek API call, no .local/ read, no original draft modification.;Phase 35B: Promptfoo Go/No-Go Packet — build tool_integrations/promptfoo/go_no_go/ directory with approval packet, approval checklist, execution scope, cost/request budget, preflight checklist, execution boundary, rollback plan, result acceptance criteria, local config template. All approval_status=not_approved, execution_allowed=false, network_allowed=false, promptfoo_eval_allowed=false, target_api_call_allowed=false, deepseek_judge_allowed=false, credential_loaded=false. No promptfoo eval, no target API call, no DeepSeek API call, no .local/ read.;Phase 35C.0: Promptfoo Execution Readiness Gate — build tool_integrations/promptfoo/readiness/ directory with execution readiness gate document, validate script (94 checks). Static verification only — secret isolation, API isolation, network safety, command safety, adapter safety. readiness_status=pass. No promptfoo eval, no target API, no DeepSeek API, no .local/ read, no formal finding. Does not replace Phase 35B Go/No-Go."

RISK_SIGNALS = [
    "prompt injection",
    "system prompt exposure",
    "RAG poisoning",
    "indirect prompt injection",
    "data leakage",
    "agent tool invocation",
    "tool exfiltration",
    "fake write action",
]

CONTROL_SUMMARY = {
    "Chatbot 控制项": [
        "系统提示隔离",
        "prompt injection 风险信号记录",
        "输出过滤与敏感信息脱敏",
        "本地 evidence 审计",
    ],
    "RAG 控制项": [
        "文档来源和版本标记",
        "恶意文档与 hidden instruction 检测",
        "检索上下文隔离",
        "引用和 dummy data 脱敏",
    ],
    "Agent 控制项": [
        "tool allowlist",
        "tool schema validation",
        "fake write action dry-run",
        "secret + send / exfiltration 阻断",
    ],
}

OWASP_LLM_COVERAGE = [
    {"llm": "LLM01", "name": "Prompt Injection", "status": "covered_by_local_tests"},
    {"llm": "LLM02", "name": "Sensitive Information Disclosure", "status": "covered_by_local_tests"},
    {"llm": "LLM03", "name": "Supply Chain", "status": "partially_covered"},
    {"llm": "LLM04", "name": "Data and Model Poisoning", "status": "partially_covered"},
    {"llm": "LLM05", "name": "Improper Output Handling", "status": "partially_covered"},
    {"llm": "LLM06", "name": "Excessive Agency", "status": "covered_by_local_tests"},
    {"llm": "LLM07", "name": "System Prompt Leakage", "status": "covered_by_local_tests"},
    {"llm": "LLM08", "name": "Vector and Embedding Weaknesses", "status": "partially_covered"},
    {"llm": "LLM09", "name": "Misinformation", "status": "partially_covered"},
    {"llm": "LLM10", "name": "Unbounded Consumption", "status": "partially_covered"},
]

OWASP_AGENTIC_COVERAGE = [
    {"asi": "ASI01", "name": "Agent Goal Hijack", "status": "covered_by_local_harness"},
    {"asi": "ASI02", "name": "Tool Misuse and Exploitation", "status": "covered_by_local_harness"},
    {"asi": "ASI03", "name": "Identity and Privilege Abuse", "status": "covered_by_local_harness"},
    {"asi": "ASI04", "name": "Agentic Supply Chain Vulnerabilities", "status": "partially_covered"},
    {"asi": "ASI05", "name": "Unexpected Code Execution", "status": "not_supported_for_now"},
    {"asi": "ASI06", "name": "Memory & Context Poisoning", "status": "covered_by_local_harness"},
    {"asi": "ASI07", "name": "Insecure Inter-Agent Communication", "status": "planned"},
    {"asi": "ASI08", "name": "Cascading Failures", "status": "covered_by_local_harness"},
    {"asi": "ASI09", "name": "Human-Agent Trust Exploitation", "status": "covered_by_local_harness"},
    {"asi": "ASI10", "name": "Rogue Agents", "status": "planned"},
]

KNOWN_GAPS = [
    "模型抽取暂未覆盖",
    "成员推断暂未覆盖",
    "训练数据投毒暂未覆盖",
    "AI 供应链攻击暂未覆盖 — 已建立 AI/ML-BOM 和映射模板（supply_chain/）",
    "Agent 长期记忆和跨轮上下文污染部分覆盖",
    "真实工具链攻击不在本地 sandbox 范围内",
    "Generic Agent Plugin / MCP 投毒测试尚未实现 mock harness",
    "API 语料仅 documentation_only 状态，无可执行 runner",
    "Business 语料仅 manual_replay 状态，无自动执行",
    "AI Red Teaming Methodology 是方法论/模板层，未执行真实红队项目",
    "AI Asset Inventory 使用 sample/fake 资产，不代表真实系统",
    "NIST AI RMF Mapping 是治理映射层，不代表已完成 NIST 合规认证",
    "Governance checklist 为通用模板，不适用于所有组织场景",
    "外部评估工具 adapter 已完成 mock evidence normalization pipeline 验证，但未安装、未运行任何真实外部工具",
    "Curated Regression Suite Builder 经 Phase 27A backfill 后：0 zero-selected suites、0 LLM gaps、1 ASI07 gap（Accountability & Audit）",
    "Regression Suite Dry-Run Validation 经 Phase 27 静态验证：7/7 suites validated、7/7 promptfoo drafts validated、reference integrity PASS、framework mapping PASS、boundary validation PASS、ASI07 gap documented and accepted。No tests executed、no promptfoo executed、no real systems connected、no evidence generated。",
    "Phase 28 Assertion & Risk Signal Rule Engine 是静态规则层：24 条风险信号规则、15 条预期行为规则、OWASP LLM/Agentic/ATLAS assertion 覆盖映射、24 条 severity mapping、8 条 manual review 规则。未执行测试、未运行 promptfoo、未连接真实系统、未生成 evidence。规则目录 rules/。",
    "Phase 29 Finding Generator Prototype 是 sample/mock finding draft 生成层：findings/ 目录结构、32 字段 finding schema、生成器脚本、6 个 sample/mock finding drafts、多维 finding index、risk register mapping、mitigation/retest mapping。不生成真实 finding。未执行测试、未运行 promptfoo、未连接真实系统、未生成真实 evidence。",
    "Phase 30 Formal Report Package Builder 是 sample delivery package 构建层：delivery_packages/ 目录结构、delivery package schema、package generation boundary、package builder 脚本、sample enterprise assessment package（13 sections）、package manifest、risk register export、mitigation roadmap、retest plan、governance appendix、supply chain appendix、external tool appendix。所有 package 内容为 sample/mock，不包含真实客户信息，不用于正式客户交付。未执行测试、未运行 promptfoo、未连接真实系统、未生成真实 evidence、未生成真实 finding。",
    "Phase 31 Generic API Provider Formalization 是 API Provider 规范化层：api_provider/ 目录结构、provider schema（6 provider types）、target profile schema（5 environment types）、config template（placeholder only）、request/response normalization schema（6 redaction rules）、provider safety guardrails（16 guardrails across 3 layers）、provider execution boundary、dry-run simulator、validation script（15 checks）、5 sample targets（openai_compatible_chat/rag_qa_api/agent_api/workflow_api/fastgpt_compatible）。所有 sample target 声明 real_target=false、dry_run_only=true、execution_allowed=false、usable_for_real_test=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试。",
    "Phase 31B Authorized Test Target Onboarding 是授权评估目标接入层：onboarding/ 目录结构、authorized target onboarding schema、RoE checklist、credential isolation policy、test scope definition template、allowed/prohibited operations matrix、rate limit and safety window policy、approval gate checklist。所有 target 声明 authorization_required=true、approval_status=not_approved、execution_allowed=false、real_target_connected=false、credentials_loaded=false、production_target_allowed=false。未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试。",
    "Phase 31C Local Mock API Execution Harness 是本地 mock API 执行层：api_provider/mock_harness/ 目录结构、mock API target schema、mock request/response fixtures（8 请求/8 响应，覆盖 5 种 provider 类型）、mock execution trace、normalized response samples、execution boundary、run/validate 脚本。所有输出声明 mock_execution=true、external_network_called=false、credentials_loaded=false、real_target_connected=false、evidence_generated=false、usable_for_formal_finding=false。Mock harness 只使用本地 fixture，不发起网络请求、不读取真实凭证。",
    "Phase 31D Limited Authorized API Dry-Run Plan 是有限授权 API 干运行计划定义层：authorized_dry_run_plan/ 目录结构、dry_run_plan schema、rate limit and request budget policy、rollback and stop conditions plan、human approval gate checklist、allowed test bundle definition、preflight readiness checklist、credential isolation checklist、validation script（19 checks）。所有计划文件声明 placeholder markers only、no real URLs、no real tokens、no real credentials、no real emails、no real API keys、no network calls。未连接真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求。",
    "Phase 31E Single Authorized API Smoke Test Design 是单次授权 API 冒烟测试设计层：api_provider/single_smoke_test_design/ 目录结构、11 个设计文件、single smoke test schema、candidate target template、minimal request bundle、expected safe response contract、execution preflight gate、abort condition checklist、operator runbook template、evidence placeholder schema、validation script（20 checks）。所有设计文件声明 smoke_test_design_ready=true、only_one_target_allowed=true、read_only_operations_only=true、approval_status=not_approved、execution_allowed=false、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false、no_adversarial_prompts=true。未使用真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求、未使用对抗性提示。",
    "Phase 31F Single Smoke Test Approval Packet & Go/No-Go Gate 是单次冒烟测试审批包与执行/不执行门禁层：api_provider/smoke_test_approval_packet/ 目录结构、10 个设计文件、approval packet schema、go/no-go gate checklist、risk acceptance form、operator signoff template、credential readiness verification、real target connection verification、rollback plan template、communication plan template、approval packet validation script（20 checks）。所有审批文件声明 approval_packet_ready=true、approval_status=not_approved、go_no_go_status=no_go、execution_allowed=false、human_approval_required=true、operator_signoff_required=true、risk_acceptance_required=true、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false、production_target_allowed=false、execution_hold=true。未使用真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求、未使用对抗性提示。",
    "Phase 32C Full Authorized API Regression Execution 是全量回归测试授权 API 层：执行全量回归测试，生成 evidence 和 finding candidates。所有 output 声明 execution_mode=full_authorized_api_regression、target_environment=test、provider_type=fastgpt_compatible、redaction_applied=true、api_key_logged=false、authorization_header_logged=false、production_target=false。测试仅针对已授权的 test API，不针对生产环境。所有 finding 为 candidate 状态，需人工审核后方可成为正式 finding。未生成正式客户报告。",
    "Phase 32D Real API Regression Assessment Report Builder 是基于 Phase 32C 结果的完整评估报告构建层：生成 10 份报告文件（完整评估报告、执行摘要、技术发现摘要、覆盖矩阵、风险摘要、修复建议、复测建议、证据索引、生成结果、README）。不重新运行测试、不连接 API、不读取凭证。所有 finding 保持 candidate 状态。",
    "Phase 32D.1 Chinese Report Localization 是在 Phase 32D 基础上新增中文报告本地化层：保留英文报告为 _en.md，中文报告为默认 .md。生成 report_language_index.md 双语索引。README 更新为双语目录概览。所有报告保持脱敏状态。",
    "Phase 32E Finding Triage & Report Hardening 是基于 Phase 32D 的发现研判与报告加固层：生成 finding_triage/ 目录（5 份文件），将 16 个候选发现合并为 5 个主问题组。生成 final_hardened/ 目录（6 份文件），包括管理层简报、最终执行摘要、最终发现摘要、修复行动计划、最终复测计划。所有发现保持 needs_human_review 状态。",
    "Phase 33 Remediation & Retest Package Builder 是整改与复测包构建层：基于 Phase 32C/32D/32E 结果，生成 remediation_packages/（5 个整改包、remediation_task_board 含 10 个 P0/P1/P2 任务）和 retest_packages/（5 个复测包、执行计划、验收标准、修复前后对比模板）。构建脚本 build_remediation_retest_packages.py、验证脚本 validate_remediation_retest_packages.py（87 项检查）。所有整改状态为 remediation_planned，所有复测状态为 retest_not_executed。不重新运行测试、不连接 API、不读取凭证。",
    "Phase 34A DeepSeek Judge Provider Framework 是 DeepSeek 判官提供者框架层：tool_judge_providers/ 目录结构，包含 DeepSeek 判官提供者（模板、模式、提示模板、模拟结果、适配器骨架）、构建/验证脚本。所有输出为模拟模式——不调用真实 API、不读取凭证、不发起网络请求。",
    "Phase 34B DeepSeek Judge Go/No-Go Packet 是 DeepSeek 判官执行/不执行审批包层：go_no_go/ 目录结构，包含审批包、审批清单、成本预算、执行计划、安全边界、回滚计划、验收标准、本地配置模板。所有审批状态为 not_approved，execution_allowed=false，network_allowed=false，credential_loaded=false。不调用真实 API、不读取凭证、不发起网络请求。",
    "Phase 34C Controlled DeepSeek Judge Execution 是受控的 DeepSeek 真实 API 判官执行：21 次 API 调用（1 smoke + 15 batch + 5 合并组），评估 16 个现有候选发现。不调用目标 API、不生成新测试。所有输出标记 usable_for_formal_finding=false、manual_review_required=true、formal_finding=false。成本约 $0.01。",
]

ROADMAP = [
    "Manual UI Replay",
    "API Provider Skeleton dry-run readiness",
    "浏览器自动化，只限测试环境",
    "garak 本地 mock 接入",
    "PyRIT 本地 mock 接入",
    "AgentDojo 本地 fake tools 接入",
    "Generic Agent mock tool harness — 已完成 Phase 13",
    "Generic Agent Plugin / MCP mock harness",
    "Generic Agent test instance API",
    "OWASP Agentic Top 10 Crosswalk — 已完成 Phase 14",
    "OWASP LLM Top 10 Crosswalk — 已完成 Phase 22",
    "Evaluation Corpus Architecture — 已完成 Phase 15",
    "AI Red Teaming Playbook + Severity Model — 已完成 Phase 16",
    "AI Asset Inventory + NIST AI RMF Mapping — 已完成 Phase 17",
    "AI/ML-BOM + Supply Chain Mapping — 已完成 Phase 18",
    "External Evaluation Tool Adapter Planning — 已完成 Phase 19",
    "External Tool Mock Evidence Normalization — 已完成 Phase 20",
    "System Release Consolidation v1.3 — 已完成 Phase 21",
    "OWASP LLM Top 10 Crosswalk + Core LLM Corpus Hardening — 已完成 Phase 22",
    "Assessment Plan Generator — 已完成 Phase 23",
    "Corpus-to-Testcase Compiler — 已完成 Phase 24",
    "Generated Testcase Curation & Runner Binding — 已完成 Phase 25",
    "Curated Regression Suite Builder — 已完成 Phase 26",
    "Regression Suite Gap Triage — 已完成 Phase 26.5",
    "Corpus & Curation Backfill — 已完成 Phase 27A",
    "Regression Suite Dry-Run Validation — 已完成 Phase 27",
    "Assertion & Risk Signal Rule Engine — 已完成 Phase 28",
    "Finding Generator Prototype — 已完成 Phase 29",
    "Formal Report Package Builder — 已完成 Phase 30",
    "Generic API Provider Formalization — 已完成 Phase 31",
    "Authorized Test Target Onboarding — 已完成 Phase 31B",
    "Local Mock API Execution Harness — 已完成 Phase 31C",
    "Limited Authorized API Dry-Run Plan — 已完成 Phase 31D",
    "Single Authorized API Smoke Test Design — 已完成 Phase 31E",
    "Single Smoke Test Approval Packet & Go/No-Go Gate — 已完成 Phase 31F",
    "Full Authorized API Regression Execution — 已完成 Phase 32C",
    "Real API Regression Assessment Report — 已完成 Phase 32D",
    "Chinese Report Localization — 已完成 Phase 32D.1",
    "Finding Triage & Report Hardening — 已完成 Phase 32E",
    "Remediation & Retest Package Builder — 已完成 Phase 33",
    "DeepSeek Judge Provider Framework — 已完成 Phase 34A",
    "DeepSeek Judge Go/No-Go Packet — 已完成 Phase 34B",
    "Controlled DeepSeek Judge Execution — 已完成 Phase 34C",
]

MANUAL_UI_EVIDENCE = ROOT / "reports/evidence/promptfoo_manual_ui_result.json"
API_CHATBOT_DRY_RUN_EVIDENCE = ROOT / "reports/evidence/api_chatbot_provider_dry_run.json"
API_RAG_DRY_RUN_EVIDENCE = ROOT / "reports/evidence/api_rag_provider_dry_run.json"
GENERIC_AGENT_PROFILE_PATH = ROOT / "assessment_profiles/generic_agent_profile.yaml"
GENERIC_AGENT_CATALOG_PATH = ROOT / "test_catalog/generic_agent_test_catalog.yaml"

EVIDENCE_INDEX = [
    "reports/evidence/atlas_assessment_summary.json",
    "reports/evidence/promptfoo_chatbot_result.json",
    "reports/evidence/promptfoo_rag_result.json",
    "reports/evidence/promptfoo_agent_result.json",
    "reports/evidence/promptfoo_manual_ui_result.json",
    "reports/evidence/promptfoo_generic_agent_harness_result.json",
    "reports/evidence/api_chatbot_provider_dry_run.json",
    "reports/evidence/api_rag_provider_dry_run.json",
    "corpus/corpus_index.yaml",
    "corpus/corpus_schema.md",
    "red_team/ai_red_team_playbook.md",
    "red_team/finding_severity_model.md",
    "red_team/finding_template.md",
    "red_team/evidence_handling_guide.md",
    "red_team/mitigation_retest_workflow.md",
    "red_team/red_team_report_outline.md",
    "inventory/ai_asset_inventory_schema.md",
    "inventory/sample_ai_asset_inventory.yaml",
    "inventory/ai_asset_inventory_index.yaml",
    "governance/nist_ai_rmf_mapping.yaml",
    "governance/nist_genai_profile_mapping.yaml",
    "governance/ai_risk_governance_checklist.md",
    "supply_chain/ai_ml_bom_schema.md",
    "supply_chain/sample_ai_ml_bom.yaml",
    "supply_chain/model_provenance_checklist.md",
    "supply_chain/supply_chain_risk_register_template.yaml",
    "supply_chain/supply_chain_to_atlas_owasp_mapping.yaml",
    "external_tools/external_tool_evidence_schema.md",
    "external_tools/external_tool_adapter_index.yaml",
    "external_tools/external_tool_to_atlas_owasp_mapping.yaml",
    "external_tools/external_tool_risk_boundary.md",
    "external_tools/external_tool_report_appendix_template.md",
    "external_tools/mock_external_tool_evidence_mapping.yaml",
    "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json",
    "reports/evidence/external_tools/mock_external_tool_evidence_index.json",
    "owasp/llm_top10_2025.yaml",
    "owasp/llm_to_atlas_crosswalk.yaml",
    "owasp/llm_to_corpus_mapping.yaml",
    "owasp/llm_to_controls_mapping.yaml",
    "owasp/llm_to_supply_chain_mapping.yaml",
    "owasp/llm_report_language.md",
    "curation/curation_schema.md",
    "curation/curation_result.yaml",
    "curation/runner_binding_index.yaml",
    "curation/assertion_strategy_mapping.yaml",
    "curation/manual_review_checklist.md",
    "curation/curation_summary.md",
    "scripts/curate_generated_testcases.py",
    "regression_suites/suite_gap_analysis.yaml",
    "regression_suites/suite_gap_analysis.md",
    "docs/phase26_5_regression_suite_gap_triage.md",
    "docs/phase27a_corpus_curation_backfill_review.md",
    "scripts/analyze_regression_suite_gaps.py",
    "regression_suites/validation/regression_suite_validation_report.md",
    "rules/rule_coverage_report.md",
    "findings/README.md",
    "findings/finding_schema.md",
    "findings/finding_generation_boundary.md",
    "findings/finding_index.yaml",
    "findings/finding_to_risk_register_mapping.yaml",
    "findings/finding_to_mitigation_retest_mapping.yaml",
    "findings/sample_findings/sample_finding_drafts.yaml",
    "delivery_packages/delivery_package_schema.md",
    "delivery_packages/package_generation_boundary.md",
    "delivery_packages/sample_enterprise_assessment_package/package_manifest.yaml",
    "delivery_packages/sample_enterprise_assessment_package/executive_summary.md",
    "delivery_packages/sample_enterprise_assessment_package/finding_summary.md",
    "delivery_packages/sample_enterprise_assessment_package/risk_register_export.yaml",
    "delivery_packages/sample_enterprise_assessment_package/mitigation_roadmap.md",
    "scripts/build_formal_report_package.py",
    "api_provider/api_provider_schema.md",
    "api_provider/target_profile_schema.md",
    "api_provider/provider_config_template.local.example.yaml",
    "api_provider/request_response_normalization_schema.md",
    "api_provider/provider_safety_guardrails.md",
    "api_provider/provider_execution_boundary.md",
    "api_provider/provider_validation_result.yaml",
    "api_provider/provider_validation_report.md",
    "scripts/api_provider_dry_run_simulator.py",
    "scripts/validate_api_provider_formalization.py",
    "api_provider/onboarding/README.md",
    "api_provider/onboarding/authorized_target_onboarding_schema.md",
    "api_provider/onboarding/target_intake_template.yaml",
    "api_provider/onboarding/roe_checklist.md",
    "api_provider/onboarding/credential_isolation_policy.md",
    "api_provider/onboarding/test_scope_definition_template.yaml",
    "api_provider/onboarding/allowed_prohibited_operations_matrix.yaml",
    "api_provider/onboarding/rate_limit_and_safety_window_policy.md",
    "api_provider/onboarding/approval_gate_checklist.md",
    "api_provider/onboarding/onboarding_validation_result.yaml",
    "api_provider/onboarding/onboarding_validation_report.md",
    "scripts/validate_authorized_target_onboarding.py",
    "api_provider/mock_harness/README.md",
    "api_provider/mock_harness/mock_api_target_schema.md",
    "api_provider/mock_harness/mock_execution_boundary.md",
    "api_provider/mock_harness/mock_request_fixtures.yaml",
    "api_provider/mock_harness/mock_response_fixtures.yaml",
    "api_provider/mock_harness/mock_execution_trace.yaml",
    "api_provider/mock_harness/mock_normalized_response_samples.yaml",
    "api_provider/mock_harness/mock_harness_validation_result.yaml",
    "api_provider/mock_harness/mock_harness_validation_report.md",
    "scripts/run_local_mock_api_harness.py",
    "scripts/validate_local_mock_api_harness.py",
    "scripts/run_full_authorized_api_regression.py",
    "scripts/validate_full_authorized_api_regression_result.py",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"covered": 0, "partially_covered": 0, "planned": 0, "not_applicable": 0}
    for row in rows:
        status = row.get("coverage_status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def load_profiles() -> list[dict[str, Any]]:
    profiles = []
    for path in sorted(PROFILES_DIR.glob("*.yaml")):
        if path.name == "profile_schema.md":
            continue
        data = read_yaml(path) or {}
        profile_name = data.get("profile_name") or path.stem.replace("_profile", "")
        profiles.append({
            "profile": profile_name,
            "file": rel(path),
            "status": data.get("status") or data.get("coverage_status") or ("planned" if profile_name == "ai_gateway" else "covered"),
            "system_type": data.get("system_type") or data.get("profile_type") or "local_sandbox",
            "runner": data.get("runner") or data.get("existing_test_runner") or data.get("existing_test_runners") or "N/A",
            "evidence_files": listify(data.get("evidence_file") or data.get("evidence_files")),
            "techniques": listify(data.get("techniques") or data.get("applicable_techniques") or data.get("mapped_atlas_techniques")),
        })
    order = {"chatbot": 0, "rag": 1, "agent": 2, "ai_gateway": 3}
    return sorted(profiles, key=lambda item: order.get(item["profile"], 99))


def load_catalog_summary() -> dict[str, Any]:
    files = []
    capability_count = 0
    for path in sorted(CATALOG_DIR.glob("*.yaml")):
        data = read_yaml(path) or {}
        text = path.read_text(encoding="utf-8")
        capability_count += len(re.findall(r"capability_id:", text))
        files.append({"file": rel(path), "top_level_keys": sorted(data.keys()) if isinstance(data, dict) else []})
    return {"files": files, "capability_count_hint": capability_count}


def _load_full_regression_execution() -> dict[str, Any]:
    """Load actual execution results from result YAML and finding candidates."""
    result_path = ROOT / "api_provider/full_regression_execution/full_regression_execution_result.yaml"
    finding_path = ROOT / "api_provider/full_regression_execution/finding_candidates.yaml"
    default = {
        "execution_mode": "full_authorized_api_regression",
        "target_environment": "test",
        "provider_type": "fastgpt_compatible",
        "total_requests_attempted": 0,
        "total_requests_completed": 0,
        "total_pass": 0,
        "total_fail": 0,
        "total_skipped": 0,
        "finding_candidates": 0,
        "redaction_applied": True,
        "api_key_logged": False,
        "authorization_header_logged": False,
        "production_target": False,
    }
    if not result_path.exists():
        return default
    try:
        result = yaml.safe_load(result_path.read_text(encoding="utf-8"))
        if not isinstance(result, dict):
            return default
        candidates = 0
        if finding_path.exists():
            try:
                fc = yaml.safe_load(finding_path.read_text(encoding="utf-8"))
                if isinstance(fc, dict) and isinstance(fc.get("candidates"), list):
                    candidates = len(fc["candidates"])
            except Exception:
                pass
        return {
            "execution_mode": "full_authorized_api_regression",
            "target_environment": result.get("environment", "test"),
            "provider_type": result.get("provider_type", "fastgpt_compatible"),
            "total_requests_attempted": result.get("total_requests_attempted", 0),
            "total_requests_completed": result.get("total_requests_completed", 0),
            "total_pass": result.get("total_pass", 0),
            "total_fail": result.get("total_fail", 0),
            "total_skipped": result.get("total_skipped", 0),
            "finding_candidates": candidates,
            "redaction_applied": result.get("redaction_applied", True),
            "api_key_logged": result.get("api_key_logged", False),
            "authorization_header_logged": result.get("authorization_header_logged", False),
            "production_target": result.get("production_target", False),
        }
    except Exception:
        return default


def _load_real_api_regression_report() -> dict[str, Any]:
    """Load report generation result from Phase 32D/32D.1/32E Real API Regression Assessment Report."""
    report_path = ROOT / "reports/real_api_regression_assessment/report_generation_result.yaml"
    default = {
        "report_generated": False,
        "source_phase": "Phase 32C",
        "total_requests_attempted": 0,
        "total_requests_completed": 0,
        "total_pass": 0,
        "total_fail": 0,
        "total_skipped": 0,
        "finding_candidates": 0,
        "redaction_applied": True,
        "formal_finding": False,
        "formal_customer_report": False,
        "manual_review_required": True,
        "chinese_report_generated": False,
        "english_report_preserved": False,
        "finding_triage_generated": False,
        "final_hardened_generated": False,
        "bilingual_index_generated": False,
    }
    if not report_path.exists():
        return default
    try:
        result = yaml.safe_load(report_path.read_text(encoding="utf-8"))
        if not isinstance(result, dict):
            return default
        return {
            "report_generated": result.get("report_generated", False),
            "source_phase": result.get("source_phase", "Phase 32C"),
            "total_requests_attempted": result.get("total_requests_attempted", 0),
            "total_requests_completed": result.get("total_requests_completed", 0),
            "total_pass": result.get("total_pass", 0),
            "total_fail": result.get("total_fail", 0),
            "total_skipped": result.get("total_skipped", 0),
            "finding_candidates": result.get("finding_candidates", 0),
            "redaction_applied": result.get("redaction_applied", True),
            "formal_finding": result.get("formal_finding", False),
            "formal_customer_report": result.get("formal_customer_report", False),
            "manual_review_required": result.get("manual_review_required", True),
            "chinese_report_generated": result.get("chinese_report_generated", False),
            "english_report_preserved": result.get("english_report_preserved", False),
            "finding_triage_generated": result.get("finding_triage_generated", False),
            "final_hardened_generated": result.get("final_hardened_generated", False),
            "bilingual_index_generated": result.get("bilingual_index_generated", False),
        }
    except Exception:
        return default


def _load_promptfoo_go_no_go_packet() -> dict[str, Any]:
    """Load Phase 35B Promptfoo Go/No-Go Packet status."""
    go_no_go_dir = ROOT / "tool_integrations" / "promptfoo" / "go_no_go"
    default = {
        "packet_complete": True,
        "directory": "tool_integrations/promptfoo/go_no_go/",
        "packet_files": 9,
        "approval_status": "not_approved",
        "execution_allowed": False,
        "network_allowed": False,
        "promptfoo_eval_allowed": False,
        "target_api_call_allowed": False,
        "deepseek_judge_allowed": False,
        "credential_loaded": False,
        "human_go_no_go_required": True,
        "result_can_create_formal_finding": False,
        "validate_script": "scripts/validate_promptfoo_go_no_go.py",
        "validate_passed": 58,
        "validate_total": 58,
        "note": "Phase 35B: Go/No-Go packet only. No promptfoo eval, no target API, no DeepSeek API, no .local/ read.",
    }
    return default


def _load_promptfoo_execution_readiness() -> dict[str, Any]:
    """Load Phase 35C.0 Promptfoo Execution Readiness Gate status."""
    readiness_dir = ROOT / "tool_integrations" / "promptfoo" / "readiness"
    default = {
        "readiness_gate_complete": True,
        "directory": "tool_integrations/promptfoo/readiness/",
        "readiness_files": 1,
        "validate_script": "scripts/validate_promptfoo_readiness_gate.py",
        "validate_passed": 94,
        "validate_total": 94,
        "readiness_status": "pass",
        "promptfoo_eval_run": False,
        "target_api_connected": False,
        "deepseek_api_called": False,
        "local_config_read": False,
        "formal_finding_generated": False,
        "note": "Phase 35C.0: Execution readiness gate. Static verification only. No promptfoo eval, no target API, no DeepSeek API, no .local/ read.",
    }
    return default


def _load_promptfoo_integration_framework() -> dict[str, Any]:
    """Load Phase 35 Promptfoo Integration Framework status."""
    integration_dir = ROOT / "tool_integrations" / "promptfoo"
    default = {
        "framework_complete": True,
        "directory": "tool_integrations/promptfoo/",
        "profiles_indexed": 12,
        "result_schema_defined": True,
        "mock_results_generated": True,
        "evidence_mapping_defined": True,
        "finding_candidate_mapping_defined": True,
        "judge_handoff_schema_defined": True,
        "adapter_skeleton_created": True,
        "build_script": "scripts/build_promptfoo_integration_framework.py",
        "validate_script": "scripts/validate_promptfoo_integration_framework.py",
        "execution_mode": "mock",
        "real_target_connected": False,
        "usable_for_formal_finding": False,
        "promptfoo_eval_run": False,
        "deepseek_api_called": False,
        "note": "Phase 35: schema/config/mock/adapter only. No promptfoo eval, no target API, no DeepSeek API.",
    }
    return default


def _load_deepseek_judge_result_integration() -> dict[str, Any]:
    """Load Phase 34D DeepSeek Judge result integration status."""
    summary_path = ROOT / "tool_judge_providers" / "deepseek" / "executions" / "phase34c_controlled_judge" / "deepseek_judge_review_summary.yaml"
    default = {
        "integration_complete": False,
        "source_phase": "phase34c_controlled_deepseek_judge_execution",
        "total_api_calls": 21,
        "authenticity_verdict": "probable_real_call",
        "requires_manual_billing_verification": True,
        "all_require_human_review": True,
        "no_formal_findings": True,
        "budget_reconciled": True,
    }
    if not summary_path.exists():
        return default
    try:
        data = yaml.safe_load(summary_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return default
        overview = data.get("execution_overview", {})
        budget = data.get("budget_summary", {})
        return {
            "integration_complete": True,
            "source_phase": data.get("source_phase", default["source_phase"]),
            "total_api_calls": overview.get("total_api_calls", 21),
            "authenticity_verdict": overview.get("authenticity_verdict", "probable_real_call"),
            "requires_manual_billing_verification": overview.get("requires_manual_billing_verification", True),
            "all_require_human_review": data.get("all_require_human_review", True),
            "no_formal_findings": data.get("no_formal_findings", True),
            "budget_reconciled": budget.get("within_budget", True),
            "total_finding_candidates": overview.get("total_finding_candidates", 16),
            "smoke_reviewed_candidates": overview.get("smoke_reviewed_candidates", 1),
            "batch_reviewed_candidates": overview.get("batch_reviewed_candidates", 15),
            "total_candidate_coverage": overview.get("total_candidate_coverage", "16/16"),
            "groups_reviewed": overview.get("consolidated_group_reviews", 5),
            "total_tokens": overview.get("total_tokens_used", 0),
            "estimated_cost": overview.get("estimated_cost_usd", 0),
        }
    except Exception:
        return default


def build_data() -> dict[str, Any]:
    summary = read_json(SUMMARY_PATH)
    coverage = read_yaml(COVERAGE_PATH) or {}
    techniques = coverage.get("coverage_matrix", [])
    results = summary.get("results", [])

    RED_TEAM_DIR = ROOT / "red_team"
    red_team_playbook_path = RED_TEAM_DIR / "ai_red_team_playbook.md"
    red_team_severity_path = RED_TEAM_DIR / "finding_severity_model.md"
    test_results = []
    for item in results:
        total = item.get("pass", 0) + item.get("fail", 0) + item.get("error", 0)
        test_results.append({
            "profile": item.get("profile"),
            "runner": item.get("runner"),
            "evidence_file": item.get("evidence_file"),
            "total": total,
            "pass": item.get("pass", 0),
            "fail": item.get("fail", 0),
            "error": item.get("error", 0),
            "status": item.get("status"),
            "timestamp": item.get("timestamp"),
        })
    covered_techniques = sorted({tech for item in results for tech in item.get("covered_atlas_techniques", [])})
    manual_ui_replay = {
        "status": "available" if MANUAL_UI_EVIDENCE.exists() else "not_run",
        "evidence_file": rel(MANUAL_UI_EVIDENCE),
        "sample_source": "replays/manual_ui_samples/",
        "runner": "runners/run_manual_ui_promptfoo.sh",
        "mode": "local_fake_replay_only",
        "note": "Manual UI Replay uses local fake replay evidence only.",
    }
    api_provider_skeleton = {
        "status": "dry_run_ready" if API_CHATBOT_DRY_RUN_EVIDENCE.exists() and API_RAG_DRY_RUN_EVIDENCE.exists() else "not_run",
        "mode": "skeleton_dry_run_only",
        "chatbot_evidence_file": rel(API_CHATBOT_DRY_RUN_EVIDENCE),
        "rag_evidence_file": rel(API_RAG_DRY_RUN_EVIDENCE),
        "chatbot_runner": "runners/run_api_chatbot_provider.sh",
        "rag_runner": "runners/run_api_rag_provider.sh",
        "target_schema": "targets/api/api_target_schema.md",
        "real_api_tested": False,
        "network_access": False,
        "credentials_loaded": False,
        "note": "Dry-run readiness only; do not interpret as real API tested or passed.",
    }
    generic_agent_assessment_pack = {
        "status": "framework_ready" if GENERIC_AGENT_PROFILE_PATH.exists() else "not_created",
        "profile_file": rel(GENERIC_AGENT_PROFILE_PATH),
        "catalog_file": rel(GENERIC_AGENT_CATALOG_PATH),
        "methodology_doc": "docs/generic_agent_assessment_methodology.md",
        "attack_surface_doc": "docs/generic_agent_attack_surface.md",
        "control_checklist": "docs/generic_agent_control_checklist.md",
        "manual_replay_sample": "replays/manual_ui_samples/generic_agent_manual_replay_sample.json",
        "report_template": "reports/generic_agent_assessment_template.md",
        "local_sandbox_executable": True,
        "mock_harness_ready": True,
        "test_instance_ready": False,
        "real_agent_integrated": False,
        "note": "Framework, methodology, and mock tool harness ready. No real Agent connections. No real API calls.",
    }
    owasp_data = {"coverage": OWASP_AGENTIC_COVERAGE, "source": "owasp/agentic_top10_2026.yaml"}
    red_team_data = {
        "status": "methodology_ready" if red_team_playbook_path.exists() else "not_created",
        "playbook": "red_team/ai_red_team_playbook.md",
        "severity_model": "red_team/finding_severity_model.md",
        "finding_template": "red_team/finding_template.md",
        "evidence_guide": "red_team/evidence_handling_guide.md",
        "retest_workflow": "red_team/mitigation_retest_workflow.md",
        "report_outline": "red_team/red_team_report_outline.md",
        "real_red_team_executed": False,
        "note": "Methodology/template layer only. No real red team project has been executed.",
    }
    INVENTORY_DIR = ROOT / "inventory"
    GOVERNANCE_DIR = ROOT / "governance"
    SUPPLY_CHAIN_DIR = ROOT / "supply_chain"
    EXTERNAL_TOOLS_DIR = ROOT / "external_tools"
    sample_inventory_path = INVENTORY_DIR / "sample_ai_asset_inventory.yaml"
    nist_mapping_path = GOVERNANCE_DIR / "nist_ai_rmf_mapping.yaml"
    bom_schema_path = SUPPLY_CHAIN_DIR / "ai_ml_bom_schema.md"
    adapter_index_path = EXTERNAL_TOOLS_DIR / "external_tool_adapter_index.yaml"
    external_mock_index_path = ROOT / "reports/evidence/external_tools/mock_external_tool_evidence_index.json"
    inventory_data = {
        "status": "created" if sample_inventory_path.exists() else "not_created",
        "sample_asset_count": 5,
        "asset_types": ["chatbot", "rag", "agent", "workflow_api", "manual_ui_replay"],
        "profiles_covered": ["chatbot", "rag", "agent", "generic_agent", "api", "manual_ui"],
        "schema_file": "inventory/ai_asset_inventory_schema.md",
        "sample_inventory_file": "inventory/sample_ai_asset_inventory.yaml",
        "intake_form": "inventory/ai_application_intake_form.md",
        "risk_register": "inventory/ai_asset_risk_register_template.yaml",
        "inventory_index": "inventory/ai_asset_inventory_index.yaml",
        "note": "Sample/fake assets only. Does not represent any real system.",
    }
    governance_data = {
        "status": "created" if nist_mapping_path.exists() else "not_created",
        "nist_ai_rmf_mapping": "governance/nist_ai_rmf_mapping.yaml",
        "nist_genai_mapping": "governance/nist_genai_profile_mapping.yaml",
        "governance_checklist": "governance/ai_risk_governance_checklist.md",
        "crosswalk": "governance/governance_to_security_assessment_crosswalk.md",
        "report_appendix": "governance/governance_report_appendix_template.md",
        "govern_support": "partially_supported",
        "map_support": "supported",
        "measure_support": "supported",
        "manage_support": "partially_supported",
        "note": "Governance mapping layer. Does not represent NIST compliance certification.",
    }
    supply_chain_data = {
        "status": "created" if bom_schema_path.exists() else "not_created",
        "bom_schema": "supply_chain/ai_ml_bom_schema.md",
        "sample_bom": "supply_chain/sample_ai_ml_bom.yaml",
        "model_provenance_checklist": "supply_chain/model_provenance_checklist.md",
        "dataset_kb_inventory": "supply_chain/dataset_knowledge_base_inventory.md",
        "tool_plugin_mcp_inventory": "supply_chain/tool_plugin_mcp_inventory.yaml",
        "prompt_template_inventory": "supply_chain/prompt_template_inventory.yaml",
        "external_api_dependency_inventory": "supply_chain/external_api_dependency_inventory.yaml",
        "risk_register": "supply_chain/supply_chain_risk_register_template.yaml",
        "atlas_owasp_mapping": "supply_chain/supply_chain_to_atlas_owasp_mapping.yaml",
        "report_appendix": "supply_chain/supply_chain_report_appendix_template.md",
        "sample_bom_count": 5,
        "supply_chain_mapping_count": 15,
        "note": "Sample/fake BOM data only. No real model repositories or vendor systems connected.",
    }
    adapter_index = read_yaml(adapter_index_path) if adapter_index_path.exists() else {}
    adapters = adapter_index.get("adapter_index", []) if isinstance(adapter_index, dict) else []
    external_mock_index = read_json(external_mock_index_path) if external_mock_index_path.exists() else {}
    external_tools_data = {
        "status": "mock_normalization_ready" if external_mock_index_path.exists() else ("design_layer_created" if adapter_index_path.exists() else "not_created"),
        "adapter_count": len(adapters),
        "adapters": [
            {
                "adapter_id": adapter.get("adapter_id"),
                "tool_name": adapter.get("tool_name"),
                "current_status": adapter.get("current_status"),
                "integration_priority": adapter.get("integration_priority"),
            }
            for adapter in adapters
        ],
        "evidence_schema": "external_tools/external_tool_evidence_schema.md",
        "adapter_index": "external_tools/external_tool_adapter_index.yaml",
        "risk_boundary": "external_tools/external_tool_risk_boundary.md",
        "atlas_owasp_mapping": "external_tools/external_tool_to_atlas_owasp_mapping.yaml",
        "report_appendix": "external_tools/external_tool_report_appendix_template.md",
        "mock_evidence_mapping": "external_tools/mock_external_tool_evidence_mapping.yaml",
        "mock_outputs_dir": "external_tools/mock_outputs/",
        "mock_output_count": external_mock_index.get("mock_output_count", 0),
        "normalized_evidence_count": external_mock_index.get("normalized_evidence_count", 0),
        "tools_represented": external_mock_index.get("tools_represented", []),
        "normalized_evidence_file": external_mock_index.get("normalized_evidence_file"),
        "normalized_evidence_index": "reports/evidence/external_tools/mock_external_tool_evidence_index.json",
        "external_tools_installed": False,
        "external_tools_executed": False,
        "external_tool_evidence_exists": external_mock_index_path.exists(),
        "real_target_connected": False,
        "usable_for_formal_finding": False,
        "note": "Mock normalization pipeline only. No external evaluation tools installed or executed.",
    }
    ASSESSMENT_PLANS_DIR = ROOT / "assessment_plans"
    GENERATED_PLANS_DIR = ASSESSMENT_PLANS_DIR / "generated"
    assessment_plan_data = {
        "status": "generated" if GENERATED_PLANS_DIR.exists() else "not_created",
        "generated_plan_count": len(list(GENERATED_PLANS_DIR.glob("plan_*.yaml"))) if GENERATED_PLANS_DIR.exists() else 0,
        "assets_covered": [
            "sample_internal_chatbot",
            "sample_policy_rag_assistant",
            "sample_generic_agent",
            "sample_fastgpt_workflow_api",
            "sample_manual_ui_chatbot",
        ],
        "profiles_covered": ["chatbot", "rag", "agent", "generic_agent", "api", "manual_ui"],
        "framework_mappings_covered": ["mitre_atlas", "owasp_llm", "owasp_agentic", "nist_ai_rmf"],
        "executable_now": False,
        "real_system_connected": False,
        "note": "Sample plan generation only. No tests executed. No real systems connected.",
    }
    COMPILER_GENERATED_DIR = ROOT / "generated_testcases"
    compiler_data = {
        "status": "generated" if COMPILER_GENERATED_DIR.exists() else "not_created",
        "total_corpus": 93,
        "compilable_corpus": 65,
        "generated_testcase_count": 65,
        "promptfoo_draft_count": 52,
        "manual_review_required_count": 0,
        "profiles_covered": ["chatbot", "rag", "agent", "api", "regression"],
        "executed": False,
        "real_target_connected": False,
        "note": "Generated testcases are drafts. No tests executed. No real systems connected.",
    }
    CURATION_DIR = ROOT / "curation"
    curation_data = {
        "status": "static_analysis_complete",
        "total_generated_testcases": 65,
        "curated_candidate": 59,
        "manual_review_required": 6,
        "planned_only": 0,
        "not_executable": 0,
        "duplicate_or_low_value": 0,
        "runner_binding_count": 5,
        "allowed_now": False,
        "executed": False,
        "real_target_connected": False,
        "usable_for_formal_finding": False,
        "note": "Static curation only. Phase 27A backfill: curated_candidate 32→59, manual_review_required 29→6. No tests executed. No real systems connected.",
    }
    RELEASE_DIR = ROOT / "release"
    release_data = {
        "release_version": "v1.4",
        "release_package_ready": RELEASE_DIR.exists(),
        "module_count": 10,
        "capability_group_count": 12,
        "executed_local_count": 5,
        "mock_only_count": 2,
        "planning_only_count": 5,
        "methodology_ready_count": 6,
        "governance_mapping_count": 5,
    }
    return {
        "regression_suite_gap_triage": {
            "status": "static_analysis_complete",
            "zero_selected_suites": 0,
            "framework_gaps_llm": 0,
            "framework_gaps_agentic": 1,
            "gap_analysis_yaml": "regression_suites/suite_gap_analysis.yaml",
            "gap_analysis_md": "regression_suites/suite_gap_analysis.md",
            "triage_doc": "docs/phase26_5_regression_suite_gap_triage.md",
            "analysis_script": "scripts/analyze_regression_suite_gaps.py",
            "executed": False,
            "real_target_connected": False,
            "usable_for_formal_finding": False,
            "analysis_only": True,
            "note": "Static analysis only. Phase 27A backfill: zero_selected 3→0, LLM gaps 3→0, Agentic gaps 5→1. No tests executed. No real systems connected.",
        },
        "regression_suite_validation": {
            "status": "static_dry_run_complete",
            "suite_validation_count": 7,
            "promptfoo_draft_validation_count": 7,
            "reference_integrity_pass": True,
            "framework_mapping_pass": True,
            "boundary_validation_pass": True,
            "tests_executed": False,
            "promptfoo_executed": False,
            "real_target_connected": False,
            "evidence_generated": False,
            "validation_mode": "static_dry_run_only",
            "note": "Static dry-run validation only. No tests executed. No promptfoo executed. No real systems connected. No evidence generated.",
        },
        "rule_engine": {
            "risk_signal_rule_count": 24,
            "expected_behavior_rule_count": 15,
            "owasp_llm_assertion_coverage": 10,
            "owasp_agentic_assertion_coverage": 10,
            "atlas_assertion_coverage": 21,
            "severity_mapping_count": 24,
            "manual_review_required_rule_count": 8,
            "tests_executed": False,
            "real_target_connected": False,
            "evidence_generated": False,
            "rule_validation_pass": True,
            "asi07_gap_handled": True,
        },
        "finding_generator": {
            "status": "sample_generation_complete",
            "finding_schema": "findings/finding_schema.md",
            "generator_script": "scripts/generate_finding_drafts.py",
            "sample_finding_count": 6,
            "finding_types": ["sample_draft", "mock_draft", "governance_gap"],
            "profiles_covered": ["chatbot", "agent", "rag"],
            "output_files": [
                "findings/sample_findings/sample_finding_drafts.yaml",
                "findings/sample_findings/sample_finding_drafts.md",
                "findings/finding_index.yaml",
            ],
            "risk_register_mapping": "findings/finding_to_risk_register_mapping.yaml",
            "mitigation_retest_mapping": "findings/finding_to_mitigation_retest_mapping.yaml",
            "finding_boundary_doc": "findings/finding_generation_boundary.md",
            "tests_executed": False,
            "promptfoo_executed": False,
            "real_target_connected": False,
            "real_evidence_generated": False,
            "real_finding_generated": False,
            "usable_for_formal_report": False,
            "all_findings_real_target_validated": False,
            "generation_mode": "sample_generation_only",
        },
        "delivery_package": {
            "status": "sample_package_ready",
            "package_schema": "delivery_packages/delivery_package_schema.md",
            "package_boundary": "delivery_packages/package_generation_boundary.md",
            "builder_script": "scripts/build_formal_report_package.py",
            "package_id": "PACKAGE-2026-001",
            "package_type": "sample_delivery_package",
            "package_sections_count": 13,
            "sample_finding_count": 6,
            "risk_register_entries": 6,
            "included_sections": [
                "executive_summary", "assessment_scope", "methodology",
                "asset_inventory_summary", "test_coverage_summary", "finding_summary",
                "risk_register_export", "mitigation_roadmap", "retest_plan",
                "governance_appendix", "supply_chain_appendix", "external_tool_appendix",
                "limitations",
            ],
            "real_customer": False,
            "real_target_validated": False,
            "formal_report": False,
            "usable_for_customer_delivery": False,
            "manual_review_required": True,
            "roe_required": True,
            "real_execution_required": True,
        },
        "api_provider_formalization": {
            "status": "provider_formalization_complete",
            "mode": "dry_run_only",
            "dry_run_only": True,
            "network_called": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "tests_executed": False,
            "evidence_generated": False,
            "usable_for_formal_finding": False,
            "provider_schema_ready": True,
            "target_profile_schema_ready": True,
            "sample_target_count": 5,
            "total_simulated_operations": 6,
            "all_targets_dry_run_only": True,
            "all_targets_no_real_target": True,
            "all_targets_no_execution": True,
            "targets": [
                {"target_id": "sample_openai_chat", "target_type": "openai_compatible_chat", "source_file": "api_provider/sample_targets/openai_compatible_chat_sample.yaml", "simulated_operations": 1},
                {"target_id": "sample_rag_qa_api", "target_type": "rag_qa_api", "source_file": "api_provider/sample_targets/rag_qa_api_sample.yaml", "simulated_operations": 1},
                {"target_id": "sample_agent_api", "target_type": "agent_api", "source_file": "api_provider/sample_targets/agent_api_sample.yaml", "simulated_operations": 1},
                {"target_id": "sample_workflow_api", "target_type": "workflow_api", "source_file": "api_provider/sample_targets/workflow_api_sample.yaml", "simulated_operations": 1},
                {"target_id": "sample_fastgpt_compatible", "target_type": "fastgpt_compatible", "source_file": "api_provider/sample_targets/fastgpt_compatible_sample.yaml", "simulated_operations": 2},
            ],
            "safety_guardrails": {
                "config_layer_checks": 6,
                "execution_layer_checks": 6,
                "credential_layer_checks": 4,
                "total_guardrails": 16,
                "all_checks_passed": True,
                "guardrails_source": "api_provider/provider_safety_guardrails.md",
            },
            "validation_checks_total": 15,
            "validation_checks_passed": 15,
            "validation_script": "scripts/validate_api_provider_formalization.py",
            "simulator_script": "scripts/api_provider_dry_run_simulator.py",
            "provider_schema": "api_provider/api_provider_schema.md",
            "target_profile_schema": "api_provider/target_profile_schema.md",
            "config_template": "api_provider/provider_config_template.local.example.yaml",
            "normalization_schema": "api_provider/request_response_normalization_schema.md",
            "safety_guardrails_doc": "api_provider/provider_safety_guardrails.md",
            "execution_boundary_doc": "api_provider/provider_execution_boundary.md",
            "validation_result": "api_provider/provider_validation_result.yaml",
            "validation_report": "api_provider/provider_validation_report.md",
            "note": "API provider formalization layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. The provider schema is for auditability and safety guardrails, not for connecting real API targets.",
        },
        "authorized_target_onboarding": {
            "status": "onboarding_complete",
            "mode": "schema_formalization_only",
            "approval_status": "not_approved",
            "authorization_required": True,
            "execution_allowed": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "production_target_allowed": False,
            "dry_run_only": True,
            "human_approval_obtained": False,
            "network_called": False,
            "tests_executed": False,
            "evidence_generated": False,
            "usable_for_formal_finding": False,
            "onboarding_files": [
                "api_provider/onboarding/README.md",
                "api_provider/onboarding/authorized_target_onboarding_schema.md",
                "api_provider/onboarding/target_intake_template.yaml",
                "api_provider/onboarding/roe_checklist.md",
                "api_provider/onboarding/credential_isolation_policy.md",
                "api_provider/onboarding/test_scope_definition_template.yaml",
                "api_provider/onboarding/allowed_prohibited_operations_matrix.yaml",
                "api_provider/onboarding/rate_limit_and_safety_window_policy.md",
                "api_provider/onboarding/approval_gate_checklist.md",
                "api_provider/onboarding/onboarding_validation_result.yaml",
                "api_provider/onboarding/onboarding_validation_report.md",
            ],
            "validation_checks_total": 18,
            "validation_checks_passed": 18,
            "validation_script": "scripts/validate_authorized_target_onboarding.py",
            "onboarding_schema": "api_provider/onboarding/authorized_target_onboarding_schema.md",
            "intake_template": "api_provider/onboarding/target_intake_template.yaml",
            "roe_checklist": "api_provider/onboarding/roe_checklist.md",
            "credential_isolation_policy": "api_provider/onboarding/credential_isolation_policy.md",
            "allowed_prohibited_matrix": "api_provider/onboarding/allowed_prohibited_operations_matrix.yaml",
            "rate_limit_policy": "api_provider/onboarding/rate_limit_and_safety_window_policy.md",
            "approval_gate_checklist": "api_provider/onboarding/approval_gate_checklist.md",
            "guardrails_extended": {
                "total_guardrails": 24,
                "phase31_guardrails": 16,
                "onboarding_guardrails": 8,
                "guardrails_source": "api_provider/provider_safety_guardrails.md",
            },
            "note": "Authorized test target onboarding layer. All targets declare authorization_required=true, approval_status=not_approved, execution_allowed=false. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. Onboarding is for structured authorization before any real API testing.",
        },
        "mock_harness": {
            "status": "mock_execution_complete",
            "mode": "local_mock_execution_only",
            "mock_execution": True,
            "external_network_called": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "tests_executed": False,
            "evidence_generated": False,
            "usable_for_formal_finding": False,
            "target_types_simulated": 5,
            "request_fixtures": 8,
            "response_fixtures": 8,
            "execution_trace_operations": 8,
            "normalized_samples": 8,
            "validation_checks_total": 21,
            "validation_checks_passed": 21,
            "target_types": ["openai_compatible_chat", "rag_qa_api", "agent_api", "workflow_api", "fastgpt_compatible"],
            "harness_directory": "api_provider/mock_harness/",
            "run_script": "scripts/run_local_mock_api_harness.py",
            "validate_script": "scripts/validate_local_mock_api_harness.py",
            "note": "Local mock API execution harness only. All outputs are mock data. No network calls. No real credentials. No real endpoints accessed. No evidence generated.",
        },
        "dry_run_plan": {
            "dry_run_plan_ready": True,
            "authorization_required": True,
            "approval_status": "not_approved",
            "execution_allowed": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "network_called": False,
            "evidence_generated": False,
            "production_target_allowed": False,
            "dry_run_plan_only": True,
            "plan_files": 11,
            "validation_checks": 19,
            "validation_passed": 0,
            "preflight_items": 20,
            "readiness_checks": 10,
            "credential_checks": 14,
            "allowed_bundles": 4,
            "stop_conditions": 10,
            "rollback_steps": 18,
        },
        "smoke_test_design": {
            "smoke_test_design_ready": True,
            "only_one_target_allowed": True,
            "read_only_operations_only": True,
            "approval_status": "not_approved",
            "execution_allowed": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "network_called": False,
            "evidence_generated": False,
            "production_target_allowed": False,
            "smoke_test_design_only": True,
            "design_files": 11,
            "validation_checks": 20,
            "validation_passed": 0,
            "minimal_requests": 4,
            "preflight_checks": 12,
            "abort_conditions": 13,
        },
        "approval_packet": {
            "approval_packet_ready": True,
            "approval_status": "not_approved",
            "go_no_go_status": "no_go",
            "execution_allowed": False,
            "human_approval_required": True,
            "operator_signoff_required": True,
            "risk_acceptance_required": True,
            "credentials_loaded": False,
            "real_target_connected": False,
            "network_called": False,
            "evidence_generated": False,
            "production_target_allowed": False,
            "execution_hold": True,
            "design_files": 10,
            "validation_checks": 20,
            "validation_passed": 0,
        },
        "full_regression_execution": _load_full_regression_execution(),
        "deepseek_judge_result_integration": _load_deepseek_judge_result_integration(),
        "promptfoo_integration_framework": _load_promptfoo_integration_framework(),
        "promptfoo_go_no_go_packet": _load_promptfoo_go_no_go_packet(),
        "promptfoo_execution_readiness": _load_promptfoo_execution_readiness(),
        "real_api_regression_report": _load_real_api_regression_report(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_status": release_data,
        "owasp_agentic": owasp_data,
        "owasp_llm": {"coverage": OWASP_LLM_COVERAGE, "source": "owasp/llm_top10_2025.yaml"},
        "red_team_methodology": red_team_data,
        "ai_asset_inventory": inventory_data,
        "nist_ai_rmf_governance": governance_data,
        "supply_chain": supply_chain_data,
        "external_tools": external_tools_data,
        "assessment_plans": assessment_plan_data,
        "corpus_compiler": compiler_data,
        "generated_testcase_curation": curation_data,
        "project_name": PROJECT_NAME,
        "current_phase": CURRENT_PHASE,
        "assessment_time": summary.get("generated_at"),
        "assessment_scope": SCOPE,
        "local_sandbox_only": summary.get("local_sandbox_only", True),
        "requested_profile": summary.get("requested_profile", "all"),
        "test_results": test_results,
        "manual_ui_replay": manual_ui_replay,
        "api_provider_skeleton": api_provider_skeleton,
        "generic_agent_assessment_pack": generic_agent_assessment_pack,
        "coverage_counts": status_counts(techniques),
        "covered_technique_count": len(covered_techniques),
        "covered_techniques": covered_techniques,
        "profiles": load_profiles(),
        "catalog_summary": load_catalog_summary(),
        "technique_coverage": techniques,
        "evidence_index": EVIDENCE_INDEX,
        "risk_signals": RISK_SIGNALS,
        "control_summary": CONTROL_SUMMARY,
        "known_gaps": KNOWN_GAPS,
        "roadmap": ROADMAP,
        "limitations": [
            "仅使用本地 sandbox / fake data / fake tools。",
            "API Provider Skeleton 只做 dry-run readiness，不代表真实 API 已测试。",
            "未执行新的真实 API 测试，未运行任何 API --execute。",
            "未访问外部网络、真实 API、真实模型或企业系统。",
            "Phase 31C Local Mock API Execution Harness 是本地 mock 执行层，不发起网络请求、不读取真实凭证。",
            "Phase 31E Single Authorized API Smoke Test Design 是单次授权 API 冒烟测试设计层：仅定义设计，不执行测试。不使用真实 API、不读取真实凭证、不发起网络请求、不使用对抗性提示。",
            "Phase 31F Single Smoke Test Approval Packet & Go/No-Go Gate 是单次冒烟测试审批包与执行/不执行门禁层：仅定义审批包和门禁条件，不执行测试。不使用真实 API、不读取真实凭证、不发起网络请求、不使用对抗性提示。",
            "Phase 32C Full Authorized API Regression Execution 是全量回归测试执行层：执行全量回归测试，生成 evidence 和 finding candidates。测试仅针对授权 test API，不针对生产环境。所有 finding 为 candidate 状态，需人工审核后方可成为正式 finding。未生成正式客户报告。",
            "Phase 34D DeepSeek Judge Result Integration & Review Report 是结果整合与报告更新层：对 Phase 34C/34C.0/34C.1 的结果进行整合，生成判官评审摘要、人工审核交接文档。不重新调用 DeepSeek API、不读取 .local/、不连接被测 API、不重新运行测试。所有结果仍为 candidate 状态，需人工审核后方可用于任何决策。",
            "Phase 35 Promptfoo Integration Framework 是 promptfoo 接入框架层：仅定义 schema、config、mock、adapter，不安装或运行 promptfoo CLI、不连接任何真实目标、不执行 promptfoo eval、不输出真实评估结果。所有 execution_mode=mock/dry_run、所有 real_target_connected=false、所有 usable_for_formal_finding=false。真实执行函数 stub 均 raise NotImplementedError。",
            "Phase 35B Promptfoo Go/No-Go Packet 是 promptfoo 执行审批包层：仅生成审批、范围、预算、执行边界、回滚计划和验收标准，不运行 promptfoo eval、不连接被测 API、不调用 DeepSeek API、不读取 .local/。所有 approval_status=not_approved、execution_allowed=false、network_allowed=false、promptfoo_eval_allowed=false、target_api_call_allowed=false、deepseek_judge_allowed=false、credential_loaded=false。所有文件为审批/占位内容。",
        ],
    }


def md_list(items: list[Any]) -> str:
    if not items:
        return "- N/A"
    return "\n".join(f"- `{item}`" if isinstance(item, str) and item.startswith("atlas.") else f"- {item}" for item in items)


def pipe(value: Any) -> str:
    if isinstance(value, list):
        return "<br>".join(html.escape(str(v)) for v in value) or "N/A"
    return html.escape(str(value)) if value not in (None, "") else "N/A"


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# ATLAS 评估 Dashboard",
        "",
        "## 系统概览",
        "",
        f"- 项目名称：{data['project_name']}",
        f"- 评估时间：{data['assessment_time']}",
        f"- 当前阶段：{data['current_phase']}",
        f"- 评估对象范围：{data['assessment_scope']}",
        f"- 是否仅本地 sandbox：{data['local_sandbox_only']}",
        "",
        "## Release Status",
        "",
        f"- Release version：{data['release_status']['release_version']}",
        f"- Release package ready：{data['release_status']['release_package_ready']}",
        f"- Module count：{data['release_status']['module_count']}",
        f"- Capability group count：{data['release_status']['capability_group_count']}",
        f"- Executed local chains：{data['release_status']['executed_local_count']}",
        f"- Mock-only chains：{data['release_status']['mock_only_count']}",
        f"- Planning-only adapters：{data['release_status']['planning_only_count']}",
        f"- Methodology ready：{data['release_status']['methodology_ready_count']}",
        f"- Governance mapping：{data['release_status']['governance_mapping_count']}",
        "",
        "## 测试结果总览",
        "",
        "| Profile | Total | Pass | Fail | Error | Status | Evidence |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in data["test_results"]:
        lines.append(f"| {row['profile']} | {row['total']} | {row['pass']} | {row['fail']} | {row['error']} | {row['status']} | `{row['evidence_file']}` |")
    manual = data["manual_ui_replay"]
    api_provider = data["api_provider_skeleton"]
    gen_agent = data["generic_agent_assessment_pack"]
    red_team = data["red_team_methodology"]
    ai_inv = data.get("ai_asset_inventory", {})
    gov = data.get("nist_ai_rmf_governance", {})
    mh = data.get("mock_harness", {})
    drp = data.get("dry_run_plan", {})
    std = data.get("smoke_test_design", {})
    ap = data.get("approval_packet", {})
    ap = data.get("approval_packet", {})
    fre = data.get("full_regression_execution", {})
    dji = data.get("deepseek_judge_result_integration", {})
    pfi = data.get("promptfoo_integration_framework", {})
    pfgn = data.get("promptfoo_go_no_go_packet", {})
    pfer = data.get("promptfoo_execution_readiness", {})
    owasp_coverage = data.get("owasp_agentic", {}).get("coverage", [])
    counts = data["coverage_counts"]
    lines.extend([
        "",
        "## Manual UI Replay",
        "",
        f"- 状态：{manual['status']}",
        f"- Runner：`{manual['runner']}`",
        f"- Sample source：`{manual['sample_source']}`",
        f"- Evidence：`{manual['evidence_file']}`",
        f"- 说明：{manual['note']}",
        "",
        "## API Provider Skeleton",
        "",
        f"- 状态：{api_provider['status']}",
        f"- 模式：{api_provider['mode']}",
        f"- Chatbot runner：`{api_provider['chatbot_runner']}`",
        f"- RAG runner：`{api_provider['rag_runner']}`",
        f"- Target schema：`{api_provider['target_schema']}`",
        f"- Chatbot evidence：`{api_provider['chatbot_evidence_file']}`",
        f"- RAG evidence：`{api_provider['rag_evidence_file']}`",
        f"- 是否真实 API tested：{api_provider['real_api_tested']}",
        f"- 说明：{api_provider['note']}",
        "",
        "## Generic Agent Assessment Pack",
        "",
        f"- 状态：{gen_agent['status']}",
        f"- Profile：`{gen_agent['profile_file']}`",
        f"- 测试能力目录：`{gen_agent['catalog_file']}`",
        f"- 攻击面文档：`{gen_agent['attack_surface_doc']}`",
        f"- 评估方法论：`{gen_agent['methodology_doc']}`",
        f"- 控制项清单：`{gen_agent['control_checklist']}`",
        f"- Manual replay 样例：`{gen_agent['manual_replay_sample']}`",
        f"- 报告模板：`{gen_agent['report_template']}`",
        f"- Local sandbox 可执行：{gen_agent['local_sandbox_executable']}",
        f"- Mock harness 就绪：{gen_agent['mock_harness_ready']}",
        f"- Test instance 就绪：{gen_agent['test_instance_ready']}",
        f"- 真实 Agent 集成：{gen_agent['real_agent_integrated']}",
        f"- 说明：{gen_agent['note']}",
        "",
        "## AI Red Teaming Methodology",
        "",
        f"- 状态：{red_team['status']}",
        f"- Playbook：`{red_team['playbook']}`",
        f"- Severity Model：`{red_team['severity_model']}`",
        f"- Finding Template：`{red_team['finding_template']}`",
        f"- Evidence Guide：`{red_team['evidence_guide']}`",
        f"- Retest Workflow：`{red_team['retest_workflow']}`",
        f"- Report Outline：`{red_team['report_outline']}`",
        f"- 是否执行真实红队项目：{red_team['real_red_team_executed']}",
        f"- 说明：{red_team['note']}",
        "",
        "## OWASP Agentic Top 10 覆盖",
        "",
        "| ASI | 名称 | 状态 |",
        "|---|---|---|",
    ])
    for item in owasp_coverage:
        lines.append(f"| {item['asi']} | {item['name']} | {item['status']} |")
    lines.extend([
        "",
        "## ATLAS 覆盖概览",
        "",
        f"- covered：{counts.get('covered', 0)}",
        f"- partially_covered：{counts.get('partially_covered', 0)}",
        f"- planned：{counts.get('planned', 0)}",
        f"- not_applicable：{counts.get('not_applicable', 0)}",
        f"- covered techniques 去重数量：{data['covered_technique_count']}",
        "",
        "## Profile 视图",
        "",
        "| Profile | Status | System Type | Runner | Evidence | Techniques |",
        "|---|---|---|---|---|---|",
    ])
    for profile in data["profiles"]:
        lines.append(f"| {profile['profile']} | {profile['status']} | {profile['system_type']} | `{profile['runner']}` | {', '.join(profile['evidence_files']) or 'N/A'} | {', '.join(profile['techniques']) or 'N/A'} |")
    lines.extend([
        "",
        "## Technique 覆盖表",
        "",
        "| Tactic | Technique ID | Technique Name | Coverage | Profiles | Test Capabilities | Evidence | Gaps | Next Steps |",
        "|---|---|---|---|---|---|---|---|---|",
    ])
    for row in data["technique_coverage"]:
        lines.append("| " + " | ".join([
            str(row.get("tactic", "")),
            f"`{row.get('technique_id', '')}`",
            str(row.get("technique_name", "")),
            str(row.get("coverage_status", "")),
            "<br>".join(listify(row.get("applicable_profiles"))) or "N/A",
            "<br>".join(listify(row.get("mapped_test_capabilities"))) or "N/A",
            "<br>".join(listify(row.get("evidence_files"))) or "N/A",
            "<br>".join(listify(row.get("gaps"))) or "N/A",
            "<br>".join(listify(row.get("next_steps"))) or "N/A",
        ]) + " |")
    lines.extend([
        "",
        "## AI Asset Inventory",
        "",
    ])
    ai_inv = data.get("ai_asset_inventory", {})
    lines.extend([
        f"- 状态：{ai_inv.get('status')}",
        f"- Sample 资产数：{ai_inv.get('sample_asset_count')}",
        f"- 资产类型：{', '.join(ai_inv.get('asset_types', []))}",
        f"- 覆盖 Profile：{', '.join(ai_inv.get('profiles_covered', []))}",
        f"- Schema：`{ai_inv.get('schema_file')}`",
        f"- Sample Inventory：`{ai_inv.get('sample_inventory_file')}`",
        f"- Intake Form：`{ai_inv.get('intake_form')}`",
        f"- Risk Register：`{ai_inv.get('risk_register')}`",
        f"- Inventory Index：`{ai_inv.get('inventory_index')}`",
        f"- 说明：{ai_inv.get('note')}",
        "",
        "## NIST AI RMF Governance Mapping",
        "",
    ])
    gov = data.get("nist_ai_rmf_governance", {})
    lines.extend([
        f"- 状态：{gov.get('status')}",
        f"- NIST AI RMF Mapping：`{gov.get('nist_ai_rmf_mapping')}`",
        f"- NIST GenAI Profile Mapping：`{gov.get('nist_genai_mapping')}`",
        f"- Governance Checklist：`{gov.get('governance_checklist')}`",
        f"- Crosswalk：`{gov.get('crosswalk')}`",
        f"- Report Appendix：`{gov.get('report_appendix')}`",
        "",
        "| NIST Function | Support Status |",
        "|---|---|",
        f"| Govern | {gov.get('govern_support')} |",
        f"| Map | {gov.get('map_support')} |",
        f"| Measure | {gov.get('measure_support')} |",
        f"| Manage | {gov.get('manage_support')} |",
        "",
        f"- 说明：{gov.get('note')}",
        "",
        "## AI/ML-BOM + Supply Chain Mapping",
        "",
    ])
    sc = data.get("supply_chain", {})
    lines.extend([
        f"- 状态：{sc.get('status')}",
        f"- BOM Schema：`{sc.get('bom_schema')}`",
        f"- Sample BOM：`{sc.get('sample_bom')}`",
        f"- Sample BOM 数量：{sc.get('sample_bom_count')}",
        f"- 供应链风险映射数：{sc.get('supply_chain_mapping_count')}",
        f"- Model Provenance Checklist：`{sc.get('model_provenance_checklist')}`",
        f"- Dataset/KB Inventory：`{sc.get('dataset_kb_inventory')}`",
        f"- Tool/Plugin/MCP Inventory：`{sc.get('tool_plugin_mcp_inventory')}`",
        f"- Prompt Template Inventory：`{sc.get('prompt_template_inventory')}`",
        f"- External API Dependency Inventory：`{sc.get('external_api_dependency_inventory')}`",
        f"- Supply Chain Risk Register：`{sc.get('risk_register')}`",
        f"- ATLAS/OWASP Mapping：`{sc.get('atlas_owasp_mapping')}`",
        f"- 说明：{sc.get('note')}",
        "",
        "## External Evaluation Tool Adapters",
        "",
    ])
    ext = data.get("external_tools", {})
    lines.extend([
        f"- 状态：{ext.get('status')}",
        f"- Adapter count：{ext.get('adapter_count')}",
        f"- Evidence schema：`{ext.get('evidence_schema')}`",
        f"- Adapter index：`{ext.get('adapter_index')}`",
        f"- Risk boundary：`{ext.get('risk_boundary')}`",
        f"- ATLAS/OWASP Mapping：`{ext.get('atlas_owasp_mapping')}`",
        f"- Report appendix：`{ext.get('report_appendix')}`",
        f"- 外部工具已安装：{ext.get('external_tools_installed')}",
        f"- 外部工具已运行：{ext.get('external_tools_executed')}",
        f"- External tool evidence exists：{ext.get('external_tool_evidence_exists')}",
        f"- Mock output count：{ext.get('mock_output_count')}",
        f"- Normalized evidence count：{ext.get('normalized_evidence_count')}",
        f"- Tools represented：{', '.join(ext.get('tools_represented', []))}",
        f"- Real target connected：{ext.get('real_target_connected')}",
        f"- Usable for formal finding：{ext.get('usable_for_formal_finding')}",
        f"- Normalized evidence：`{ext.get('normalized_evidence_file')}`",
        f"- Normalized evidence index：`{ext.get('normalized_evidence_index')}`",
        "",
        "| Adapter | Tool | Status | Priority |",
        "|---|---|---|---|",
    ])
    for adapter in ext.get("adapters", []):
        lines.append(f"| {adapter.get('adapter_id')} | {adapter.get('tool_name')} | {adapter.get('current_status')} | {adapter.get('integration_priority')} |")
    lines.extend([
        "",
        f"- 说明：{ext.get('note')}",
        "",
        "## Assessment Plan Generator",
        "",
    ])
    plans = data.get("assessment_plans", {})
    lines.extend([
        f"- 状态：{plans.get('status')}",
        f"- 生成的计划数：{plans.get('generated_plan_count')}",
        f"- 覆盖资产：{', '.join(plans.get('assets_covered', []))}",
        f"- 覆盖 Profile：{', '.join(plans.get('profiles_covered', []))}",
        f"- 框架映射覆盖：{', '.join(plans.get('framework_mappings_covered', []))}",
        f"- 当前可执行：{plans.get('executable_now')}",
        f"- 连接真实系统：{plans.get('real_system_connected')}",
        f"- 说明：{plans.get('note')}",
        "",
        "## Corpus-to-Testcase Compiler",
        "",
    ])
    comp = data.get("corpus_compiler", {})
    lines.extend([
        f"- 状态：{comp.get('status')}",
        f"- 总语料数：{comp.get('total_corpus')}",
        f"- 可编译语料：{comp.get('compilable_corpus')}",
        f"- 生成测试用例：{comp.get('generated_testcase_count')}",
        f"- Promptfoo 草案：{comp.get('promptfoo_draft_count')}",
        f"- 需人工审查：{comp.get('manual_review_required_count')}",
        f"- 覆盖 Profile：{', '.join(comp.get('profiles_covered', []))}",
        f"- 已执行：{comp.get('executed')}",
        f"- 连接真实系统：{comp.get('real_target_connected')}",
        f"- 说明：{comp.get('note')}",
        "",
        "## Generated Testcase Curation & Runner Binding",
        "",
    ])
    cur = data.get("generated_testcase_curation", {})
    lines.extend([
        f"- 状态：{cur.get('status')}",
        f"- 总 generated testcases：{cur.get('total_generated_testcases')}",
        f"- curated_candidate：{cur.get('curated_candidate')}",
        f"- manual_review_required：{cur.get('manual_review_required')}",
        f"- planned_only：{cur.get('planned_only')}",
        f"- not_executable：{cur.get('not_executable')}",
        f"- duplicate_or_low_value：{cur.get('duplicate_or_low_value')}",
        f"- runner_binding_count：{cur.get('runner_binding_count')}",
        f"- allowed_now：{cur.get('allowed_now')}",
        f"- executed：{cur.get('executed')}",
        f"- real_target_connected：{cur.get('real_target_connected')}",
        f"- usable_for_formal_finding：{cur.get('usable_for_formal_finding')}",
        f"- 说明：{cur.get('note')}",
        "",
        "## Regression Suite Dry-Run Validation",
        "",
    ])
    reg_val = data.get("regression_suite_validation", {})
    lines.extend([
        f"- Status: {reg_val.get('status', 'N/A')}",
        f"- Suites validated: {reg_val.get('suite_validation_count', 'N/A')}",
        f"- Promptfoo drafts validated: {reg_val.get('promptfoo_draft_validation_count', 'N/A')}",
        f"- Reference integrity: {reg_val.get('reference_integrity_pass', 'N/A')}",
        f"- Framework mapping: {reg_val.get('framework_mapping_pass', 'N/A')}",
        f"- Boundary validation: {reg_val.get('boundary_validation_pass', 'N/A')}",
        f"- Tests executed: {reg_val.get('tests_executed', 'N/A')}",
        f"- Promptfoo executed: {reg_val.get('promptfoo_executed', 'N/A')}",
        f"- Real target connected: {reg_val.get('real_target_connected', 'N/A')}",
        f"- Evidence generated: {reg_val.get('evidence_generated', 'N/A')}",
        f"- Validation mode: {reg_val.get('validation_mode', 'N/A')}",
        f"- 说明：{reg_val.get('note', 'N/A')}",
        "",
        "## Assertion & Risk Signal Rule Engine",
        "",
    ])
    re_data = data.get("rule_engine", {})
    lines.extend([
        f"- 风险信号规则数：{re_data.get('risk_signal_rule_count', 'N/A')}",
        f"- 预期行为规则数：{re_data.get('expected_behavior_rule_count', 'N/A')}",
        f"- OWASP LLM assertion 覆盖：{re_data.get('owasp_llm_assertion_coverage', 'N/A')}",
        f"- OWASP Agentic assertion 覆盖：{re_data.get('owasp_agentic_assertion_coverage', 'N/A')}",
        f"- ATLAS assertion 覆盖：{re_data.get('atlas_assertion_coverage', 'N/A')}",
        f"- Severity mapping 数：{re_data.get('severity_mapping_count', 'N/A')}",
        f"- 需人工审查规则数：{re_data.get('manual_review_required_rule_count', 'N/A')}",
        f"- Tests executed：{re_data.get('tests_executed', 'N/A')}",
        f"- Real target connected：{re_data.get('real_target_connected', 'N/A')}",
        f"- Evidence generated：{re_data.get('evidence_generated', 'N/A')}",
        f"- Rule validation pass：{re_data.get('rule_validation_pass', 'N/A')}",
        f"- ASI07 gap handled：{re_data.get('asi07_gap_handled', 'N/A')}",
        "",
        "## Finding Generator Prototype",
        "",
    ])
    fg = data.get("finding_generator", {})
    lines.extend([
        f"- Status: {fg.get('status', 'N/A')}",
        f"- Finding schema: `{fg.get('finding_schema', 'N/A')}`",
        f"- Generator script: `{fg.get('generator_script', 'N/A')}`",
        f"- Sample finding count: {fg.get('sample_finding_count', 'N/A')}",
        f"- Finding types: {', '.join(fg.get('finding_types', []))}",
        f"- Profiles covered: {', '.join(fg.get('profiles_covered', []))}",
        f"- Risk register mapping: `{fg.get('risk_register_mapping', 'N/A')}`",
        f"- Mitigation/retest mapping: `{fg.get('mitigation_retest_mapping', 'N/A')}`",
        f"- Generation mode: {fg.get('generation_mode', 'N/A')}",
        f"- Tests executed: {fg.get('tests_executed', 'N/A')}",
        f"- Promptfoo executed: {fg.get('promptfoo_executed', 'N/A')}",
        f"- Real target connected: {fg.get('real_target_connected', 'N/A')}",
        f"- Real evidence generated: {fg.get('real_evidence_generated', 'N/A')}",
        f"- Real finding generated: {fg.get('real_finding_generated', 'N/A')}",
        f"- Usable for formal report: {fg.get('usable_for_formal_report', 'N/A')}",
        "",
        "## Formal Report Package Builder",
        "",
    ])
    dp = data.get("delivery_package", {})
    lines.extend([
        f"- Status: {dp.get('status', 'N/A')}",
        f"- Package ID: {dp.get('package_id', 'N/A')}",
        f"- Package type: {dp.get('package_type', 'N/A')}",
        f"- Package sections: {dp.get('package_sections_count', 'N/A')}",
        f"- Sample finding count: {dp.get('sample_finding_count', 'N/A')}",
        f"- Risk register entries: {dp.get('risk_register_entries', 'N/A')}",
        f"- Real customer: {dp.get('real_customer', 'N/A')}",
        f"- Real target validated: {dp.get('real_target_validated', 'N/A')}",
        f"- Formal report: {dp.get('formal_report', 'N/A')}",
        f"- Usable for customer delivery: {dp.get('usable_for_customer_delivery', 'N/A')}",
        f"- Manual review required: {dp.get('manual_review_required', 'N/A')}",
        f"- Package schema: `{dp.get('package_schema', 'N/A')}`",
        f"- Builder script: `{dp.get('builder_script', 'N/A')}`",
        "",
        "Phase 30 is a sample delivery package build layer only. No tests executed. No promptfoo executed. No real systems connected. No real evidence generated. No real findings generated. The sample package is not usable for customer delivery.",
        "",
        "## Generic API Provider Formalization",
        "",
        f"- 状态：完成",
        f"- 模式：dry_run_only（模拟运行，未发起网络请求）",
        f"- Provider schema：`api_provider/api_provider_schema.md`",
        f"- Target profile schema：`api_provider/target_profile_schema.md`",
        f"- Config template：`api_provider/provider_config_template.local.example.yaml`",
        f"- Normalization schema：`api_provider/request_response_normalization_schema.md`",
        f"- Safety guardrails：`api_provider/provider_safety_guardrails.md`（G01-G16，3 层）",
        f"- Execution boundary：`api_provider/provider_execution_boundary.md`",
        f"- Sample targets：5（openai_compatible_chat、rag_qa_api、agent_api、workflow_api、fastgpt_compatible）",
        f"- Dry-run simulator：`scripts/api_provider_dry_run_simulator.py`",
        f"- Validation script：`scripts/validate_api_provider_formalization.py`",
        f"- Validation checks：15/15 passed",
        f"- Simulated operations：6（所有 target）",
        f"- Network called：False",
        f"- Credentials loaded：False",
        f"- Real target connected：False",
        f"- Tests executed：False",
        f"- Evidence generated：False",
        f"- Usable for formal finding：False",
        "",
        "Phase 31 is an API provider formalization layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. The provider schema is for auditability and safety guardrails, not for connecting real API targets.",
        "",
        "## Authorized Test Target Onboarding",
        "",
        f"- 状态：完成",
        f"- 模式：schema_formalization_only（未发起网络请求）",
        f"- Onboarding schema：`api_provider/onboarding/authorized_target_onboarding_schema.md`",
        f"- Target intake template：`api_provider/onboarding/target_intake_template.yaml`",
        f"- RoE checklist：`api_provider/onboarding/roe_checklist.md`",
        f"- Credential isolation policy：`api_provider/onboarding/credential_isolation_policy.md`",
        f"- Test scope template：`api_provider/onboarding/test_scope_definition_template.yaml`",
        f"- Allowed/prohibited matrix：`api_provider/onboarding/allowed_prohibited_operations_matrix.yaml`",
        f"- Rate limit policy：`api_provider/onboarding/rate_limit_and_safety_window_policy.md`",
        f"- Approval gate checklist：`api_provider/onboarding/approval_gate_checklist.md`",
        f"- Validation script：`scripts/validate_authorized_target_onboarding.py`",
        f"- Validation checks：18/18 passed",
        f"- Onboarding files：11",
        f"- Guardrails extended：G01-G24（G17-G24 新增）",
        f"- authorization_required：True",
        f"- approval_status：not_approved",
        f"- execution_allowed：False",
        f"- credentials_loaded：False",
        f"- real_target_connected：False",
        f"- production_target_allowed：False",
        f"- dry_run_only：True",
        f"- human_approval_obtained：False",
        f"- network_called：False",
        f"- tests_executed：False",
        f"- evidence_generated：False",
        f"- usable_for_formal_finding：False",
        "",
        "Phase 31B is an authorized test target onboarding layer only. All targets declare authorization_required=true, approval_status=not_approved, execution_allowed=false. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. Onboarding is for structured authorization before any real API testing.",
        "",
        "## Local Mock API Execution Harness",
        "",
        f"- 状态：完成",
        f"- 模式：{mh.get('mode')}（本地 mock 执行，无网络请求）",
        f"- Mock API target schema：`api_provider/mock_harness/mock_api_target_schema.md`",
        f"- Mock request fixtures：{mh.get('request_fixtures')}（覆盖 5 种 provider 类型）",
        f"- Mock response fixtures：{mh.get('response_fixtures')}（含 risk signal 响应）",
        f"- Execution trace operations：{mh.get('execution_trace_operations')}",
        f"- Normalized response samples：{mh.get('normalized_samples')}",
        f"- Execution boundary：`api_provider/mock_harness/mock_execution_boundary.md`",
        f"- Run script：`{mh.get('run_script')}`",
        f"- Validate script：`{mh.get('validate_script')}`",
        f"- Validation checks：{mh.get('validation_checks_passed')}/{mh.get('validation_checks_total')} passed",
        f"- Target types：{', '.join(mh.get('target_types', []))}",
        f"- mock_execution：{mh.get('mock_execution')}",
        f"- external_network_called：{mh.get('external_network_called')}",
        f"- credentials_loaded：{mh.get('credentials_loaded')}",
        f"- real_target_connected：{mh.get('real_target_connected')}",
        f"- evidence_generated：{mh.get('evidence_generated')}",
        f"- usable_for_formal_finding：{mh.get('usable_for_formal_finding')}",
        "",
        "Phase 31C is a local mock API execution harness layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. The mock harness uses local fixtures only to simulate API request/response flows.",
        "",
        "### Limited Authorized API Dry-Run Plan",
        "",
        f"- dry_run_plan_ready: {drp.get('dry_run_plan_ready')}",
        f"- authorization_required: {drp.get('authorization_required')}",
        f"- approval_status: {drp.get('approval_status')}",
        f"- execution_allowed: {drp.get('execution_allowed')}",
        f"- credentials_loaded: {drp.get('credentials_loaded')}",
        f"- real_target_connected: {drp.get('real_target_connected')}",
        f"- network_called: {drp.get('network_called')}",
        f"- evidence_generated: {drp.get('evidence_generated')}",
        f"- production_target_allowed: {drp.get('production_target_allowed')}",
        f"- dry_run_plan_only: {drp.get('dry_run_plan_only')}",
        f"- plan_files: {drp.get('plan_files')}",
        f"- validation_checks: {drp.get('validation_checks')}",
        f"- validation_passed: {drp.get('validation_passed')}",
        f"- preflight_items: {drp.get('preflight_items')}",
        f"- readiness_checks: {drp.get('readiness_checks')}",
        f"- credential_checks: {drp.get('credential_checks')}",
        f"- allowed_bundles: {drp.get('allowed_bundles')}",
        f"- stop_conditions: {drp.get('stop_conditions')}",
        f"- rollback_steps: {drp.get('rollback_steps')}",
        "",
        "Phase 31D is a limited authorized API dry-run plan definition layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. All plan files declare placeholder markers only, no real URLs, tokens, credentials, or production targets.",
        "",
        "### Single Authorized API Smoke Test Design",
        "",
        f"- smoke_test_design_ready: {std.get('smoke_test_design_ready')}",
        f"- only_one_target_allowed: {std.get('only_one_target_allowed')}",
        f"- read_only_operations_only: {std.get('read_only_operations_only')}",
        f"- approval_status: {std.get('approval_status')}",
        f"- execution_allowed: {std.get('execution_allowed')}",
        f"- credentials_loaded: {std.get('credentials_loaded')}",
        f"- real_target_connected: {std.get('real_target_connected')}",
        f"- network_called: {std.get('network_called')}",
        f"- evidence_generated: {std.get('evidence_generated')}",
        f"- production_target_allowed: {std.get('production_target_allowed')}",
        f"- smoke_test_design_only: {std.get('smoke_test_design_only')}",
        f"- design_files: {std.get('design_files')}",
        f"- validation_checks: {std.get('validation_checks')}",
        f"- validation_passed: {std.get('validation_passed')}",
        f"- minimal_requests: {std.get('minimal_requests')}",
        f"- preflight_checks: {std.get('preflight_checks')}",
        f"- abort_conditions: {std.get('abort_conditions')}",
        "",
        "Phase 31E is a single authorized API smoke test design layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. No adversarial prompts. No network calls. No real credentials. The smoke test design is a static design definition only — not an execution plan.",
        "",
        "### Single Smoke Test Approval Packet",
        "",
        f"- approval_packet_ready: {ap.get('approval_packet_ready')}",
        f"- approval_status: {ap.get('approval_status')}",
        f"- go_no_go_status: {ap.get('go_no_go_status')}",
        f"- execution_allowed: {ap.get('execution_allowed')}",
        f"- human_approval_required: {ap.get('human_approval_required')}",
        f"- operator_signoff_required: {ap.get('operator_signoff_required')}",
        f"- risk_acceptance_required: {ap.get('risk_acceptance_required')}",
        f"- credentials_loaded: {ap.get('credentials_loaded')}",
        f"- real_target_connected: {ap.get('real_target_connected')}",
        f"- network_called: {ap.get('network_called')}",
        f"- evidence_generated: {ap.get('evidence_generated')}",
        f"- production_target_allowed: {ap.get('production_target_allowed')}",
        f"- execution_hold: {ap.get('execution_hold')}",
        f"- design_files: {ap.get('design_files')}",
        f"- validation_checks: {ap.get('validation_checks')}",
        f"- validation_passed: {ap.get('validation_passed')}",
        "",
        "Phase 31F is a single smoke test approval packet and go/no-go gate layer only. All approval packet files declare approval_packet_ready=true, approval_status=not_approved, go_no_go_status=no_go, execution_allowed=false, human_approval_required=true, operator_signoff_required=true, risk_acceptance_required=true, execution_hold=true. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. No adversarial prompts. No network calls. The approval packet is a static approval packet definition only — not an execution gate.",
        "",
        "### Full Authorized API Regression Execution",
        "",
        f"- execution_mode: {fre.get('execution_mode')}",
        f"- target_environment: {fre.get('target_environment')}",
        f"- provider_type: {fre.get('provider_type')}",
        f"- total_requests_attempted: {fre.get('total_requests_attempted')}",
        f"- total_requests_completed: {fre.get('total_requests_completed')}",
        f"- total_pass: {fre.get('total_pass')}",
        f"- total_fail: {fre.get('total_fail')}",
        f"- total_skipped: {fre.get('total_skipped')}",
        f"- finding_candidates: {fre.get('finding_candidates')}",
        f"- redaction_applied: {fre.get('redaction_applied')}",
        f"- api_key_logged: {fre.get('api_key_logged')}",
        f"- authorization_header_logged: {fre.get('authorization_header_logged')}",
        f"- production_target: {fre.get('production_target')}",
        "",
        "Phase 32C is a full authorized API regression execution layer. Regression executed against authorized test API only, not production. All findings are candidates only and require human review before formal finding status. No formal customer report generated.",
        "### DeepSeek Judge Result Integration",
        "",
        f"- integration_complete: {dji.get('integration_complete')}",
        f"- source_phase: {dji.get('source_phase')}",
        f"- total_api_calls: {dji.get('total_api_calls')}",
        f"- total_tokens: {dji.get('total_tokens')}",
        f"- estimated_cost: ${dji.get('estimated_cost')}",
        f"- authenticity_verdict: {dji.get('authenticity_verdict')}",
        f"- requires_manual_billing_verification: {dji.get('requires_manual_billing_verification')}",
        f"- total_finding_candidates: {dji.get('total_finding_candidates')}",
        f"- smoke_reviewed_candidates: {dji.get('smoke_reviewed_candidates')}",
        f"- batch_reviewed_candidates: {dji.get('batch_reviewed_candidates')}",
        f"- candidate_coverage: {dji.get('total_candidate_coverage')}",
        f"- groups_reviewed: {dji.get('groups_reviewed')}",
        f"- all_require_human_review: {dji.get('all_require_human_review')}",
        f"- no_formal_findings: {dji.get('no_formal_findings')}",
        f"- budget_reconciled: {dji.get('budget_reconciled')}",
        "",
        "Phase 34D is a static result integration & review report layer. No DeepSeek API re-call, no .local/ read, no target API connection, no test re-run. All judge results remain candidate status and require human review before any decision-making. No formal findings generated.",
        "### Promptfoo Integration Framework",
        "",
        f'- framework_complete: {pfi.get("framework_complete")}',
        f'- directory: {pfi.get("directory")}',
        f'- profiles_indexed: {pfi.get("profiles_indexed")}',
        f'- result_schema_defined: {pfi.get("result_schema_defined")}',
        f'- mock_results_generated: {pfi.get("mock_results_generated")}',
        f'- evidence_mapping_defined: {pfi.get("evidence_mapping_defined")}',
        f'- finding_candidate_mapping_defined: {pfi.get("finding_candidate_mapping_defined")}',
        f'- judge_handoff_schema_defined: {pfi.get("judge_handoff_schema_defined")}',
        f'- adapter_skeleton_created: {pfi.get("adapter_skeleton_created")}',
        f'- execution_mode: {pfi.get("execution_mode")}',
        f'- real_target_connected: {pfi.get("real_target_connected")}',
        f'- usable_for_formal_finding: {pfi.get("usable_for_formal_finding")}',
        f'- promptfoo_eval_run: {pfi.get("promptfoo_eval_run")}',
        f'- deepseek_api_called: {pfi.get("deepseek_api_called")}',
        f'- note: {pfi.get("note")}',
        "",
        "Phase 35 is a schema/config/mock/adapter layer only. No promptfoo CLI installed or executed. No real targets connected. No DeepSeek API called. No .local/ read. No original drafts modified. All results remain candidate status and require human Go/No-Go before real execution.",
        "### Promptfoo Go/No-Go Packet",
        "",
        f'- packet_complete: {pfgn.get("packet_complete")}',
        f'- directory: {pfgn.get("directory")}',
        f'- packet_files: {pfgn.get("packet_files")}',
        f'- approval_status: {pfgn.get("approval_status")}',
        f'- execution_allowed: {pfgn.get("execution_allowed")}',
        f'- network_allowed: {pfgn.get("network_allowed")}',
        f'- promptfoo_eval_allowed: {pfgn.get("promptfoo_eval_allowed")}',
        f'- target_api_call_allowed: {pfgn.get("target_api_call_allowed")}',
        f'- deepseek_judge_allowed: {pfgn.get("deepseek_judge_allowed")}',
        f'- credential_loaded: {pfgn.get("credential_loaded")}',
        f'- human_go_no_go_required: {pfgn.get("human_go_no_go_required")}',
        f'- result_can_create_formal_finding: {pfgn.get("result_can_create_formal_finding")}',
        f'- validate_passed: {pfgn.get("validate_passed")}/{pfgn.get("validate_total")}',
        "",
        "Phase 35B is a Go/No-Go packet layer only. No promptfoo eval, no target API call, no DeepSeek API call, no .local/ read. All files declare approval_status=not_approved and execution_allowed=false. Human Go/No-Go required before any real execution.",
        "",
        "### Promptfoo Execution Readiness Gate",
        "",
        f'- readiness_status: {pfer.get("readiness_status")}',
        f'- directory: {pfer.get("directory")}',
        f'- readiness_files: {pfer.get("readiness_files")}',
        f'- validate_passed: {pfer.get("validate_passed")}/{pfer.get("validate_total")}',
        f'- promptfoo_eval_run: {pfer.get("promptfoo_eval_run")}',
        f'- target_api_connected: {pfer.get("target_api_connected")}',
        f'- deepseek_api_called: {pfer.get("deepseek_api_called")}',
        f'- formal_finding_generated: {pfer.get("formal_finding_generated")}',
        "",
        "Phase 35C.0 is an execution readiness gate layer. Static verification only — no promptfoo eval, no target API connection, no DeepSeek API call, no .local/ read. Must pass before any controlled promptfoo execution. Does not replace Phase 35B Go/No-Go.",
        "## Evidence 索引",
        "",
        *[f"- `{item}`" for item in data["evidence_index"]],
        "",
        "## 风险信号摘要",
        "",
        *[f"- {item}" for item in data["risk_signals"]],
        "",
        "## 控制项摘要",
        "",
    ])
    for title, items in data["control_summary"].items():
        lines.append(f"### {title}")
        lines.append("")
        lines.extend(f"- {item}" for item in items)
        lines.append("")
    lines.extend([
        "## 当前覆盖缺口",
        "",
        *[f"- {item}" for item in data["known_gaps"]],
        "",
        "## 后续路线图",
        "",
        *[f"- {item}" for item in data["roadmap"]],
        "",
        "## 限制说明",
        "",
        *[f"- {item}" for item in data["limitations"]],
        "",
    ])
    return "\n".join(lines)


def render_html(data: dict[str, Any]) -> str:
    counts = data["coverage_counts"]
    result_rows = "".join(
        f"<tr><td>{html.escape(str(row['profile']))}</td><td>{row['total']}</td><td>{row['pass']}</td><td>{row['fail']}</td><td>{row['error']}</td><td>{html.escape(str(row['status']))}</td><td><code>{html.escape(str(row['evidence_file']))}</code></td></tr>"
        for row in data["test_results"]
    )
    technique_rows = "".join(
        "<tr>" + "".join([
            f"<td>{pipe(row.get('tactic'))}</td>",
            f"<td><code>{pipe(row.get('technique_id'))}</code></td>",
            f"<td>{pipe(row.get('technique_name'))}</td>",
            f"<td><span class='badge {html.escape(str(row.get('coverage_status')))}'>{pipe(row.get('coverage_status'))}</span></td>",
            f"<td>{pipe(row.get('applicable_profiles'))}</td>",
            f"<td>{pipe(row.get('mapped_test_capabilities'))}</td>",
            f"<td>{pipe(row.get('evidence_files'))}</td>",
            f"<td>{pipe(row.get('gaps'))}</td>",
            f"<td>{pipe(row.get('next_steps'))}</td>",
        ]) + "</tr>"
        for row in data["technique_coverage"]
    )
    profile_cards = "".join(
        f"<div class='profile'><h3>{html.escape(str(p['profile']))}</h3><p>Status: <strong>{html.escape(str(p['status']))}</strong></p><p>Runner: <code>{html.escape(str(p['runner']))}</code></p><p>Evidence: {pipe(p['evidence_files'])}</p></div>"
        for p in data["profiles"]
    )
    controls = "".join(
        f"<section class='control'><h3>{html.escape(title)}</h3><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in items)}</ul></section>"
        for title, items in data["control_summary"].items()
    )
    manual = data["manual_ui_replay"]
    api_provider = data["api_provider_skeleton"]
    gen_agent = data["generic_agent_assessment_pack"]
    red_team = data["red_team_methodology"]
    ai_inv = data.get("ai_asset_inventory", {})
    gov = data.get("nist_ai_rmf_governance", {})
    sc = data.get("supply_chain", {})
    ext = data.get("external_tools", {})
    plans = data.get("assessment_plans", {})
    comp = data.get("corpus_compiler", {})
    cur = data.get("generated_testcase_curation", {})
    regression_validation = data.get("regression_suite_validation", {})
    rule_engine = data.get("rule_engine", {})
    fg = data.get("finding_generator", {})
    dp = data.get("delivery_package", {})
    apf = data.get("api_provider_formalization", {})
    ato = data.get("authorized_target_onboarding", {})
    mh = data.get("mock_harness", {})
    drp = data.get("dry_run_plan", {})
    std = data.get("smoke_test_design", {})
    ap = data.get("approval_packet", {})
    fre = data.get("full_regression_execution", {})
    dji = data.get("deepseek_judge_result_integration", {})
    pfi = data.get("promptfoo_integration_framework", {})
    pfgn = data.get("promptfoo_go_no_go_packet", {})
    pfer = data.get("promptfoo_execution_readiness", {})
    ext_rows = "".join(
        f"<tr><td>{html.escape(str(adapter.get('adapter_id')))}</td><td>{html.escape(str(adapter.get('tool_name')))}</td><td><span class='badge {html.escape(str(adapter.get('current_status')))}'>{html.escape(str(adapter.get('current_status')))}</span></td><td>{html.escape(str(adapter.get('integration_priority')))}</td></tr>"
        for adapter in ext.get("adapters", [])
    )
    owasp = data.get("owasp_agentic", {}).get("coverage", [])
    owasp_rows = "".join(
        f"<tr><td>{html.escape(str(item['asi']))}</td><td>{html.escape(str(item['name']))}</td><td><span class='badge {html.escape(str(item['status']))}'>{html.escape(str(item['status']))}</span></td></tr>"
        for item in owasp
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ATLAS 评估 Dashboard</title>
<style>
:root {{ --bg:#f6f7f9; --card:#ffffff; --text:#17202a; --muted:#667085; --line:#d9dee7; --blue:#2454d6; --green:#0f7b4f; --amber:#a15c00; --gray:#5d6675; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); line-height:1.55; }}
header {{ background:linear-gradient(135deg,#111827,#1f3b73); color:white; padding:40px 48px; }}
header p {{ color:#dbe5ff; max-width:960px; }}
nav {{ padding:14px 48px; background:#fff; border-bottom:1px solid var(--line); position:sticky; top:0; z-index:1; }}
nav a {{ margin-right:18px; color:var(--blue); text-decoration:none; font-weight:600; }}
main {{ padding:28px 48px 56px; }}
section {{ margin-bottom:28px; }}
.card-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; }}
.card,.profile,.control {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; box-shadow:0 6px 18px rgba(16,24,40,.04); }}
.card .value {{ font-size:30px; font-weight:750; margin-top:6px; }}
.card .label {{ color:var(--muted); font-size:14px; }}
table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; }}
th,td {{ padding:11px 12px; border-bottom:1px solid var(--line); vertical-align:top; text-align:left; font-size:14px; }}
th {{ background:#eef2f8; color:#263244; }}
tr:last-child td {{ border-bottom:none; }}
code {{ background:#eef2f8; padding:2px 5px; border-radius:5px; }}
.badge {{ display:inline-block; border-radius:999px; padding:3px 9px; font-weight:700; font-size:12px; }}
.covered {{ background:#e8f7ef; color:var(--green); }}
.partially_covered {{ background:#fff4df; color:var(--amber); }}
.planned {{ background:#eef2f8; color:var(--gray); }}
.not_applicable {{ background:#f1f1f1; color:#555; }}
.profile-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; }}
.notice {{ background:#fff8e7; border:1px solid #f2d28a; border-radius:12px; padding:16px; }}
footer {{ color:var(--muted); padding:24px 48px; border-top:1px solid var(--line); background:#fff; }}
</style>
</head>
<body>
<header>
  <h1>ATLAS 评估 Dashboard</h1>
  <p>{html.escape(data['project_name'])} · {html.escape(data['current_phase'])}</p>
  <p>评估时间：{html.escape(str(data['assessment_time']))} · 仅本地 sandbox：{html.escape(str(data['local_sandbox_only']))}</p>
</header>
<nav>
  <a href="#overview">概览</a><a href="#results">测试结果</a><a href="#manual-ui">Manual UI</a><a href="#api-provider">API Skeleton</a><a href="#generic-agent">Generic Agent</a><a href="#red-team">Red Teaming</a><a href="#owasp">OWASP</a><a href="#inventory">Inventory</a><a href="#governance">Governance</a><a href="#supply-chain">Supply Chain</a><a href="#external-tools">External Tools</a><a href="#assessment-plans">Plans</a><a href="#corpus-compiler">Compiler</a><a href="#curation">Curation</a><a href="#regression-validation">Regression</a><a href="#rule-engine">Rule Engine</a><a href="#finding-generator">Findings</a><a href="#delivery-package">Delivery</a><a href="#api-provider-formalization">API Prov</a><a href="#authorized-target-onboarding">Onboard</a><a href="#mock-harness">Mock</a><a href="#dry-run-plan">Dry-Run</a><a href="#smoke-test-design">Smoke Test</a><a href="#approval-packet">Approval</a><a href="#full-regression-execution">Regression</a><a href="#coverage">覆盖表</a><a href="#profiles">Profiles</a><a href="#gaps">缺口</a><a href="#roadmap">路线图</a>
</nav>
<main>
<section id="overview">
  <h2>系统概览</h2>
  <div class="card-grid">
    <div class="card"><div class="label">Covered</div><div class="value">{counts.get('covered', 0)}</div></div>
    <div class="card"><div class="label">Partially Covered</div><div class="value">{counts.get('partially_covered', 0)}</div></div>
    <div class="card"><div class="label">Planned</div><div class="value">{counts.get('planned', 0)}</div></div>
    <div class="card"><div class="label">Not Applicable</div><div class="value">{counts.get('not_applicable', 0)}</div></div>
    <div class="card"><div class="label">Covered Techniques</div><div class="value">{data['covered_technique_count']}</div></div>
  </div>
  <p class="notice">评估对象范围：{html.escape(data['assessment_scope'])}。本 dashboard 仅使用本地 sandbox 数据，不加载远程资源，不包含任何企业身份信息。</p>
</section>
<section id="release">
  <h2>Release Status</h2>
  <div class="card">
    <p>Release version: <strong>v1.3</strong></p>
    <p>Release package ready: <strong>{html.escape(str(data['release_status']['release_package_ready']))}</strong></p>
    <p>Module count: <strong>{data['release_status']['module_count']}</strong></p>
    <p>Capability group count: <strong>{data['release_status']['capability_group_count']}</strong></p>
    <p>Executed local chains: <strong>{data['release_status']['executed_local_count']}</strong></p>
    <p>Mock-only chains: <strong>{data['release_status']['mock_only_count']}</strong></p>
    <p>Planning-only adapters: <strong>{data['release_status']['planning_only_count']}</strong></p>
    <p>Methodology ready: <strong>{data['release_status']['methodology_ready_count']}</strong></p>
    <p>Governance mapping: <strong>{data['release_status']['governance_mapping_count']}</strong></p>
    <p>详见 <code>release/</code> 目录。</p>
  </div>
</section>
<section id="results">
  <h2>测试结果总览</h2>
  <table><thead><tr><th>Profile</th><th>Total</th><th>Pass</th><th>Fail</th><th>Error</th><th>Status</th><th>Evidence</th></tr></thead><tbody>{result_rows}</tbody></table>
</section>
<section id="manual-ui">
  <h2>Manual UI Replay</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(manual['status']))}</strong></p>
    <p>Runner: <code>{html.escape(str(manual['runner']))}</code></p>
    <p>Sample source: <code>{html.escape(str(manual['sample_source']))}</code></p>
    <p>Evidence: <code>{html.escape(str(manual['evidence_file']))}</code></p>
    <p>{html.escape(str(manual['note']))}</p>
  </div>
</section>
<section id="api-provider">
  <h2>API Provider Skeleton</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(api_provider['status']))}</strong></p>
    <p>Mode: <code>{html.escape(str(api_provider['mode']))}</code></p>
    <p>Chatbot runner: <code>{html.escape(str(api_provider['chatbot_runner']))}</code></p>
    <p>RAG runner: <code>{html.escape(str(api_provider['rag_runner']))}</code></p>
    <p>Target schema: <code>{html.escape(str(api_provider['target_schema']))}</code></p>
    <p>Chatbot evidence: <code>{html.escape(str(api_provider['chatbot_evidence_file']))}</code></p>
    <p>RAG evidence: <code>{html.escape(str(api_provider['rag_evidence_file']))}</code></p>
    <p>Real API tested: <strong>{html.escape(str(api_provider['real_api_tested']))}</strong></p>
    <p>Network access: <strong>{html.escape(str(api_provider['network_access']))}</strong></p>
    <p>Credentials loaded: <strong>{html.escape(str(api_provider['credentials_loaded']))}</strong></p>
    <p>{html.escape(str(api_provider['note']))}</p>
  </div>
</section>
<section id="generic-agent">
  <h2>Generic Agent Assessment Pack</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(gen_agent['status']))}</strong></p>
    <p>Profile: <code>{html.escape(str(gen_agent['profile_file']))}</code></p>
    <p>Catalog: <code>{html.escape(str(gen_agent['catalog_file']))}</code></p>
    <p>Attack surface doc: <code>{html.escape(str(gen_agent['attack_surface_doc']))}</code></p>
    <p>Methodology doc: <code>{html.escape(str(gen_agent['methodology_doc']))}</code></p>
    <p>Control checklist: <code>{html.escape(str(gen_agent['control_checklist']))}</code></p>
    <p>Manual replay sample: <code>{html.escape(str(gen_agent['manual_replay_sample']))}</code></p>
    <p>Report template: <code>{html.escape(str(gen_agent['report_template']))}</code></p>
    <p>Local sandbox executable: <strong>{html.escape(str(gen_agent['local_sandbox_executable']))}</strong></p>
    <p>Mock harness ready: <strong>{html.escape(str(gen_agent['mock_harness_ready']))}</strong></p>
    <p>Test instance ready: <strong>{html.escape(str(gen_agent['test_instance_ready']))}</strong></p>
    <p>Real agent integrated: <strong>{html.escape(str(gen_agent['real_agent_integrated']))}</strong></p>
    <p>{html.escape(str(gen_agent['note']))}</p>
  </div>
</section>
<section id="red-team">
  <h2>AI Red Teaming Methodology</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(red_team['status']))}</strong></p>
    <p>Playbook: <code>{html.escape(str(red_team['playbook']))}</code></p>
    <p>Severity Model: <code>{html.escape(str(red_team['severity_model']))}</code></p>
    <p>Finding Template: <code>{html.escape(str(red_team['finding_template']))}</code></p>
    <p>Evidence Guide: <code>{html.escape(str(red_team['evidence_guide']))}</code></p>
    <p>Retest Workflow: <code>{html.escape(str(red_team['retest_workflow']))}</code></p>
    <p>Report Outline: <code>{html.escape(str(red_team['report_outline']))}</code></p>
    <p>Real red team project executed: <strong>{html.escape(str(red_team['real_red_team_executed']))}</strong></p>
    <p>{html.escape(str(red_team['note']))}</p>
  </div>
</section>
<section id="owasp">
  <h2>OWASP Agentic Top 10 覆盖</h2>
  <table><thead><tr><th>ASI</th><th>Name</th><th>Status</th></tr></thead><tbody>{owasp_rows}</tbody></table>
</section>
<section id="profiles">
  <h2>Profile 视图</h2>
  <div class="profile-grid">{profile_cards}</div>
</section>
<section id="supply-chain">
  <h2>AI/ML-BOM + Supply Chain Mapping</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(sc['status']))}</strong></p>
    <p>BOM Schema: <code>{html.escape(str(sc['bom_schema']))}</code></p>
    <p>Sample BOM: <code>{html.escape(str(sc['sample_bom']))}</code></p>
    <p>Sample BOM 数量: <strong>{html.escape(str(sc['sample_bom_count']))}</strong></p>
    <p>供应链风险映射数: <strong>{html.escape(str(sc['supply_chain_mapping_count']))}</strong></p>
    <p>Model Provenance Checklist: <code>{html.escape(str(sc['model_provenance_checklist']))}</code></p>
    <p>Dataset/KB Inventory: <code>{html.escape(str(sc['dataset_kb_inventory']))}</code></p>
    <p>Tool/Plugin/MCP Inventory: <code>{html.escape(str(sc['tool_plugin_mcp_inventory']))}</code></p>
    <p>Prompt Template Inventory: <code>{html.escape(str(sc['prompt_template_inventory']))}</code></p>
    <p>External API Inventory: <code>{html.escape(str(sc['external_api_dependency_inventory']))}</code></p>
    <p>Supply Chain Risk Register: <code>{html.escape(str(sc['risk_register']))}</code></p>
    <p>ATLAS/OWASP Mapping: <code>{html.escape(str(sc['atlas_owasp_mapping']))}</code></p>
    <p>{html.escape(str(sc['note']))}</p>
  </div>
</section>
<section id="external-tools">
  <h2>External Evaluation Tool Adapters</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(ext.get('status')))}</strong></p>
    <p>Adapter count: <strong>{html.escape(str(ext.get('adapter_count')))}</strong></p>
    <p>Evidence schema: <code>{html.escape(str(ext.get('evidence_schema')))}</code></p>
    <p>Adapter index: <code>{html.escape(str(ext.get('adapter_index')))}</code></p>
    <p>Risk boundary: <code>{html.escape(str(ext.get('risk_boundary')))}</code></p>
    <p>ATLAS/OWASP Mapping: <code>{html.escape(str(ext.get('atlas_owasp_mapping')))}</code></p>
    <p>External tools installed: <strong>{html.escape(str(ext.get('external_tools_installed')))}</strong></p>
    <p>External tools executed: <strong>{html.escape(str(ext.get('external_tools_executed')))}</strong></p>
    <p>External tool evidence exists: <strong>{html.escape(str(ext.get('external_tool_evidence_exists')))}</strong></p>
    <p>Mock output count: <strong>{html.escape(str(ext.get('mock_output_count')))}</strong></p>
    <p>Normalized evidence count: <strong>{html.escape(str(ext.get('normalized_evidence_count')))}</strong></p>
    <p>Tools represented: <strong>{html.escape(str(', '.join(ext.get('tools_represented', []))))}</strong></p>
    <p>Real target connected: <strong>{html.escape(str(ext.get('real_target_connected')))}</strong></p>
    <p>Usable for formal finding: <strong>{html.escape(str(ext.get('usable_for_formal_finding')))}</strong></p>
    <p>Normalized evidence: <code>{html.escape(str(ext.get('normalized_evidence_file')))}</code></p>
    <p>Normalized evidence index: <code>{html.escape(str(ext.get('normalized_evidence_index')))}</code></p>
    <p>{html.escape(str(ext.get('note')))}</p>
  </div>
  <table><thead><tr><th>Adapter</th><th>Tool</th><th>Status</th><th>Priority</th></tr></thead><tbody>{ext_rows}</tbody></table>
<section id="assessment-plans">
  <h2>Assessment Plan Generator</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(plans.get("status")))}</strong></p>
    <p>Generated plans: <strong>{html.escape(str(plans.get("generated_plan_count")))}</strong></p>
    <p>Assets covered: <strong>{html.escape(str(", ".join(plans.get("assets_covered", []))))}</strong></p>
    <p>Profiles covered: <strong>{html.escape(str(", ".join(plans.get("profiles_covered", []))))}</strong></p>
    <p>Framework mappings covered: <strong>{html.escape(str(", ".join(plans.get("framework_mappings_covered", []))))}</strong></p>
    <p>Executable now: <strong>{html.escape(str(plans.get("executable_now")))}</strong></p>
    <p>Real system connected: <strong>{html.escape(str(plans.get("real_system_connected")))}</strong></p>
    <p>{html.escape(str(plans.get("note")))}</p>
  </div>
</section>
	<section id="corpus-compiler">
	  <h2>Corpus-to-Testcase Compiler</h2>
	  <div class="card">
	    <p>Status: <strong>{html.escape(str(comp.get("status")))}</strong></p>
	    <p>Total corpus: <strong>{html.escape(str(comp.get("total_corpus")))}</strong></p>
	    <p>Compilable corpus: <strong>{html.escape(str(comp.get("compilable_corpus")))}</strong></p>
	    <p>Generated testcases: <strong>{html.escape(str(comp.get("generated_testcase_count")))}</strong></p>
	    <p>Promptfoo drafts: <strong>{html.escape(str(comp.get("promptfoo_draft_count")))}</strong></p>
	    <p>Manual review required: <strong>{html.escape(str(comp.get("manual_review_required_count")))}</strong></p>
	    <p>Profiles covered: <strong>{html.escape(str(", ".join(comp.get("profiles_covered", []))))}</strong></p>
	    <p>Executed: <strong>{html.escape(str(comp.get("executed")))}</strong></p>
	    <p>Real target connected: <strong>{html.escape(str(comp.get("real_target_connected")))}</strong></p>
	    <p>{html.escape(str(comp.get("note")))}</p>
	  </div>
	</section>
</section>
<section id="curation">
  <h2>Generated Testcase Curation & Runner Binding</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(cur.get("status")))}</strong></p>
    <p>Total generated testcases: <strong>{html.escape(str(cur.get("total_generated_testcases")))}</strong></p>
    <p>Curated candidate: <strong>{html.escape(str(cur.get("curated_candidate")))}</strong></p>
    <p>Manual review required: <strong>{html.escape(str(cur.get("manual_review_required")))}</strong></p>
    <p>Planned only: <strong>{html.escape(str(cur.get("planned_only")))}</strong></p>
    <p>Not executable: <strong>{html.escape(str(cur.get("not_executable")))}</strong></p>
    <p>Duplicate or low value: <strong>{html.escape(str(cur.get("duplicate_or_low_value")))}</strong></p>
    <p>Runner binding count: <strong>{html.escape(str(cur.get("runner_binding_count")))}</strong></p>
    <p>Allowed now: <strong>{html.escape(str(cur.get("allowed_now")))}</strong></p>
    <p>Executed: <strong>{html.escape(str(cur.get("executed")))}</strong></p>
    <p>Real target connected: <strong>{html.escape(str(cur.get("real_target_connected")))}</strong></p>
    <p>Usable for formal finding: <strong>{html.escape(str(cur.get("usable_for_formal_finding")))}</strong></p>
    <p>{html.escape(str(cur.get("note")))}</p>
  </div>
</section>
<section id="regression-validation">
  <h2>Regression Suite Dry-Run Validation</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(regression_validation.get("status")))}</strong></p>
    <p>Suites validated: <strong>{html.escape(str(regression_validation.get("suite_validation_count")))}</strong></p>
    <p>Promptfoo drafts validated: <strong>{html.escape(str(regression_validation.get("promptfoo_draft_validation_count")))}</strong></p>
    <p>Reference integrity: <strong>{html.escape(str(regression_validation.get("reference_integrity_pass")))}</strong></p>
    <p>Framework mapping: <strong>{html.escape(str(regression_validation.get("framework_mapping_pass")))}</strong></p>
    <p>Boundary validation: <strong>{html.escape(str(regression_validation.get("boundary_validation_pass")))}</strong></p>
    <p>Tests executed: <strong>{html.escape(str(regression_validation.get("tests_executed")))}</strong></p>
    <p>Promptfoo executed: <strong>{html.escape(str(regression_validation.get("promptfoo_executed")))}</strong></p>
    <p>Real target connected: <strong>{html.escape(str(regression_validation.get("real_target_connected")))}</strong></p>
    <p>Evidence generated: <strong>{html.escape(str(regression_validation.get("evidence_generated")))}</strong></p>
    <p>Validation mode: <strong>{html.escape(str(regression_validation.get("validation_mode")))}</strong></p>
    <p>{html.escape(str(regression_validation.get("note")))}</p>
  </div>
</section>
<section id="rule-engine">
  <h2>Assertion & Risk Signal Rule Engine</h2>
  <div class="card">
    <p>Risk signal rules: <strong>{html.escape(str(rule_engine.get("risk_signal_rule_count")))}</strong></p>
    <p>Expected behavior rules: <strong>{html.escape(str(rule_engine.get("expected_behavior_rule_count")))}</strong></p>
    <p>OWASP LLM assertion coverage: <strong>{html.escape(str(rule_engine.get("owasp_llm_assertion_coverage")))}</strong></p>
    <p>OWASP Agentic assertion coverage: <strong>{html.escape(str(rule_engine.get("owasp_agentic_assertion_coverage")))}</strong></p>
    <p>ATLAS assertion coverage: <strong>{html.escape(str(rule_engine.get("atlas_assertion_coverage")))}</strong></p>
    <p>Severity mapping count: <strong>{html.escape(str(rule_engine.get("severity_mapping_count")))}</strong></p>
    <p>Manual review required rules: <strong>{html.escape(str(rule_engine.get("manual_review_required_rule_count")))}</strong></p>
    <p>Tests executed: <strong>{html.escape(str(rule_engine.get("tests_executed")))}</strong></p>
    <p>Real target connected: <strong>{html.escape(str(rule_engine.get("real_target_connected")))}</strong></p>
    <p>Evidence generated: <strong>{html.escape(str(rule_engine.get("evidence_generated")))}</strong></p>
    <p>Rule validation pass: <strong>{html.escape(str(rule_engine.get("rule_validation_pass")))}</strong></p>
    <p>ASI07 gap handled: <strong>{html.escape(str(rule_engine.get("asi07_gap_handled")))}</strong></p>
    <p>Phase 28 is a static rule layer only. No tests executed. No promptfoo executed. No real systems connected. No evidence generated. Rules directory: <code>rules/</code>.</p>
  </div>
</section>
<section id="finding-generator">
  <h2>Finding Generator Prototype</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(fg.get("status")))}</strong></p>
    <p>Finding schema: <code>{html.escape(str(fg.get("finding_schema")))}</code></p>
    <p>Generator script: <code>{html.escape(str(fg.get("generator_script")))}</code></p>
    <p>Sample finding count: <strong>{html.escape(str(fg.get("sample_finding_count")))}</strong></p>
    <p>Finding types: <strong>{html.escape(str(", ".join(fg.get("finding_types", []))))}</strong></p>
    <p>Profiles covered: <strong>{html.escape(str(", ".join(fg.get("profiles_covered", []))))}</strong></p>
    <p>Risk register mapping: <code>{html.escape(str(fg.get("risk_register_mapping")))}</code></p>
    <p>Mitigation/retest mapping: <code>{html.escape(str(fg.get("mitigation_retest_mapping")))}</code></p>
    <p>Generation mode: <strong>{html.escape(str(fg.get("generation_mode")))}</strong></p>
    <p>Tests executed: <strong>{html.escape(str(fg.get("tests_executed")))}</strong></p>
    <p>Promptfoo executed: <strong>{html.escape(str(fg.get("promptfoo_executed")))}</strong></p>
    <p>Real target connected: <strong>{html.escape(str(fg.get("real_target_connected")))}</strong></p>
    <p>Real evidence generated: <strong>{html.escape(str(fg.get("real_evidence_generated")))}</strong></p>
    <p>Real finding generated: <strong>{html.escape(str(fg.get("real_finding_generated")))}</strong></p>
    <p>Usable for formal report: <strong>{html.escape(str(fg.get("usable_for_formal_report")))}</strong></p>
    <p>Phase 29 is a sample finding draft generation layer only. No tests executed. No promptfoo executed. No real systems connected. No real evidence generated. No real findings generated. All findings are sample/mock drafts with real_target_validated=false, usable_for_formal_report=false.</p>
  </div>
</section>
<section id="delivery-package">
  <h2>Formal Report Package Builder</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(dp.get("status")))}</strong></p>
    <p>Package ID: <strong>{html.escape(str(dp.get("package_id")))}</strong></p>
    <p>Package type: <strong>{html.escape(str(dp.get("package_type")))}</strong></p>
    <p>Package sections: <strong>{html.escape(str(dp.get("package_sections_count")))}</strong></p>
    <p>Sample finding count: <strong>{html.escape(str(dp.get("sample_finding_count")))}</strong></p>
    <p>Risk register entries: <strong>{html.escape(str(dp.get("risk_register_entries")))}</strong></p>
    <p>Real customer: <strong>{html.escape(str(dp.get("real_customer")))}</strong></p>
    <p>Real target validated: <strong>{html.escape(str(dp.get("real_target_validated")))}</strong></p>
    <p>Formal report: <strong>{html.escape(str(dp.get("formal_report")))}</strong></p>
    <p>Usable for customer delivery: <strong>{html.escape(str(dp.get("usable_for_customer_delivery")))}</strong></p>
    <p>Manual review required: <strong>{html.escape(str(dp.get("manual_review_required")))}</strong></p>
    <p>Package schema: <code>{html.escape(str(dp.get("package_schema")))}</code></p>
    <p>Builder script: <code>{html.escape(str(dp.get("builder_script")))}</code></p>
    <p>Phase 30 is a sample delivery package build layer only. No tests executed. No promptfoo executed. No real systems connected. No real evidence generated. No real findings generated. The sample package is not usable for customer delivery.</p>
  </div>
</section>
<section id="api-provider-formalization">
  <h2>Generic API Provider Formalization</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(apf.get("status")))}</strong></p>
    <p>Mode: <strong>{html.escape(str(apf.get("mode")))}</strong> (simulated, no network requests)</p>
    <p>Provider schema: <code>{html.escape(str(apf.get("provider_schema")))}</code></p>
    <p>Target profile schema: <code>{html.escape(str(apf.get("target_profile_schema")))}</code></p>
    <p>Config template: <code>{html.escape(str(apf.get("config_template")))}</code></p>
    <p>Normalization schema: <code>{html.escape(str(apf.get("normalization_schema")))}</code></p>
    <p>Safety guardrails: <code>{html.escape(str(apf.get("safety_guardrails_doc")))}</code> (G01-G16, 3 layers)</p>
    <p>Execution boundary: <code>{html.escape(str(apf.get("execution_boundary_doc")))}</code></p>
    <p>Sample targets: <strong>{html.escape(str(apf.get("sample_target_count")))}</strong> (openai_compatible_chat, rag_qa_api, agent_api, workflow_api, fastgpt_compatible)</p>
    <p>Dry-run simulator: <code>{html.escape(str(apf.get("simulator_script")))}</code></p>
    <p>Validation script: <code>{html.escape(str(apf.get("validation_script")))}</code></p>
    <p>Validation checks: <strong>{html.escape(str(apf.get("validation_checks_passed")))}/{html.escape(str(apf.get("validation_checks_total")))} passed</strong></p>
    <p>Simulated operations: <strong>{html.escape(str(apf.get("total_simulated_operations")))}</strong> (all targets)</p>
    <p>Network called: <strong>{html.escape(str(apf.get("network_called")))}</strong></p>
    <p>Credentials loaded: <strong>{html.escape(str(apf.get("credentials_loaded")))}</strong></p>
    <p>Real target connected: <strong>{html.escape(str(apf.get("real_target_connected")))}</strong></p>
    <p>Tests executed: <strong>{html.escape(str(apf.get("tests_executed")))}</strong></p>
    <p>Evidence generated: <strong>{html.escape(str(apf.get("evidence_generated")))}</strong></p>
    <p>Usable for formal finding: <strong>{html.escape(str(apf.get("usable_for_formal_finding")))}</strong></p>
    <p>Phase 31 is an API provider formalization layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. The provider schema is for auditability and safety guardrails, not for connecting real API targets.</p>
  </div>
</section>
<section id="authorized-target-onboarding">
  <h2>Authorized Test Target Onboarding</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(ato.get("status")))}</strong></p>
    <p>Mode: <strong>{html.escape(str(ato.get("mode")))}</strong> (no network requests)</p>
    <p>Onboarding schema: <code>{html.escape(str(ato.get("onboarding_schema")))}</code></p>
    <p>Intake template: <code>{html.escape(str(ato.get("intake_template")))}</code></p>
    <p>RoE checklist: <code>{html.escape(str(ato.get("roe_checklist")))}</code></p>
    <p>Credential isolation policy: <code>{html.escape(str(ato.get("credential_isolation_policy")))}</code></p>
    <p>Allowed/prohibited matrix: <code>{html.escape(str(ato.get("allowed_prohibited_matrix")))}</code></p>
    <p>Rate limit policy: <code>{html.escape(str(ato.get("rate_limit_policy")))}</code></p>
    <p>Approval gate checklist: <code>{html.escape(str(ato.get("approval_gate_checklist")))}</code></p>
    <p>Validation script: <code>{html.escape(str(ato.get("validation_script")))}</code></p>
    <p>Validation checks: <strong>{html.escape(str(ato.get("validation_checks_passed")))}/{html.escape(str(ato.get("validation_checks_total")))} passed</strong></p>
    <p>Guardrails extended: <strong>G01-G24</strong> (G17-G24 onboarding)</p>
    <p>authorization_required: <strong>{html.escape(str(ato.get("authorization_required")))}</strong></p>
    <p>approval_status: <strong>{html.escape(str(ato.get("approval_status")))}</strong></p>
    <p>execution_allowed: <strong>{html.escape(str(ato.get("execution_allowed")))}</strong></p>
    <p>credentials_loaded: <strong>{html.escape(str(ato.get("credentials_loaded")))}</strong></p>
    <p>real_target_connected: <strong>{html.escape(str(ato.get("real_target_connected")))}</strong></p>
    <p>production_target_allowed: <strong>{html.escape(str(ato.get("production_target_allowed")))}</strong></p>
    <p>dry_run_only: <strong>{html.escape(str(ato.get("dry_run_only")))}</strong></p>
    <p>human_approval_obtained: <strong>{html.escape(str(ato.get("human_approval_obtained")))}</strong></p>
    <p>network_called: <strong>{html.escape(str(ato.get("network_called")))}</strong></p>
    <p>tests_executed: <strong>{html.escape(str(ato.get("tests_executed")))}</strong></p>
    <p>evidence_generated: <strong>{html.escape(str(ato.get("evidence_generated")))}</strong></p>
    <p>usable_for_formal_finding: <strong>{html.escape(str(ato.get("usable_for_formal_finding")))}</strong></p>
    <p>Phase 31B is an authorized test target onboarding layer only. All targets declare authorization_required=true, approval_status=not_approved, execution_allowed=false. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. Onboarding is for structured authorization before any real API testing.</p>
  </div>
</section>
<section id="mock-harness">
  <h2>Local Mock API Execution Harness</h2>
  <div class="card">
    <p>Status: <strong>{html.escape(str(mh.get("status")))}</strong></p>
    <p>Mode: <strong>{html.escape(str(mh.get("mode")))}</strong> (local mock execution, no network requests)</p>
    <p>Mock API target schema: <code>{html.escape(str(mh.get("harness_directory")))}mock_api_target_schema.md</code></p>
    <p>Request fixtures: <strong>{html.escape(str(mh.get("request_fixtures")))}</strong> (5 target types)</p>
    <p>Response fixtures: <strong>{html.escape(str(mh.get("response_fixtures")))}</strong> (includes risk signal responses)</p>
    <p>Execution trace operations: <strong>{html.escape(str(mh.get("execution_trace_operations")))}</strong></p>
    <p>Normalized samples: <strong>{html.escape(str(mh.get("normalized_samples")))}</strong></p>
    <p>Run script: <code>{html.escape(str(mh.get("run_script")))}</code></p>
    <p>Validate script: <code>{html.escape(str(mh.get("validate_script")))}</code></p>
    <p>Validation checks: <strong>{html.escape(str(mh.get("validation_checks_passed")))}/{html.escape(str(mh.get("validation_checks_total")))} passed</strong></p>
    <p>Target types: <strong>{html.escape(str(", ".join(mh.get("target_types", []))))}</strong></p>
    <p>mock_execution: <strong>{html.escape(str(mh.get("mock_execution")))}</strong></p>
    <p>external_network_called: <strong>{html.escape(str(mh.get("external_network_called")))}</strong></p>
    <p>credentials_loaded: <strong>{html.escape(str(mh.get("credentials_loaded")))}</strong></p>
    <p>real_target_connected: <strong>{html.escape(str(mh.get("real_target_connected")))}</strong></p>
    <p>evidence_generated: <strong>{html.escape(str(mh.get("evidence_generated")))}</strong></p>
    <p>usable_for_formal_finding: <strong>{html.escape(str(mh.get("usable_for_formal_finding")))}</strong></p>
    <p>Phase 31C is a local mock API execution harness layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. The mock harness uses local fixtures only to simulate API request/response flows.</p>
  </div>
</section>
<section id="dry-run-plan">
  <h2>Limited Authorized API Dry-Run Plan</h2>
  <div class="card">
    <p>dry_run_plan_ready: <strong>{html.escape(str(drp.get("dry_run_plan_ready")))}</strong></p>
    <p>authorization_required: <strong>{html.escape(str(drp.get("authorization_required")))}</strong></p>
    <p>approval_status: <strong>{html.escape(str(drp.get("approval_status")))}</strong></p>
    <p>execution_allowed: <strong>{html.escape(str(drp.get("execution_allowed")))}</strong></p>
    <p>credentials_loaded: <strong>{html.escape(str(drp.get("credentials_loaded")))}</strong></p>
    <p>real_target_connected: <strong>{html.escape(str(drp.get("real_target_connected")))}</strong></p>
    <p>network_called: <strong>{html.escape(str(drp.get("network_called")))}</strong></p>
    <p>evidence_generated: <strong>{html.escape(str(drp.get("evidence_generated")))}</strong></p>
    <p>production_target_allowed: <strong>{html.escape(str(drp.get("production_target_allowed")))}</strong></p>
    <p>dry_run_plan_only: <strong>{html.escape(str(drp.get("dry_run_plan_only")))}</strong></p>
    <p>plan_files: <strong>{html.escape(str(drp.get("plan_files")))}</strong></p>
    <p>validation_checks: <strong>{html.escape(str(drp.get("validation_checks")))}</strong></p>
    <p>validation_passed: <strong>{html.escape(str(drp.get("validation_passed")))}</strong></p>
    <p>preflight_items: <strong>{html.escape(str(drp.get("preflight_items")))}</strong></p>
    <p>readiness_checks: <strong>{html.escape(str(drp.get("readiness_checks")))}</strong></p>
    <p>credential_checks: <strong>{html.escape(str(drp.get("credential_checks")))}</strong></p>
    <p>allowed_bundles: <strong>{html.escape(str(drp.get("allowed_bundles")))}</strong></p>
    <p>stop_conditions: <strong>{html.escape(str(drp.get("stop_conditions")))}</strong></p>
    <p>rollback_steps: <strong>{html.escape(str(drp.get("rollback_steps")))}</strong></p>
    <p>Phase 31D is a limited authorized API dry-run plan definition layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. All plan files declare placeholder markers only, no real URLs, tokens, credentials, or production targets.</p>
  </div>
</section>
<section id="smoke-test-design">
  <h2>Single Authorized API Smoke Test Design</h2>
  <div class="card">
    <p>smoke_test_design_ready: <strong>{html.escape(str(std.get("smoke_test_design_ready")))}</strong></p>
    <p>only_one_target_allowed: <strong>{html.escape(str(std.get("only_one_target_allowed")))}</strong></p>
    <p>read_only_operations_only: <strong>{html.escape(str(std.get("read_only_operations_only")))}</strong></p>
    <p>approval_status: <strong>{html.escape(str(std.get("approval_status")))}</strong></p>
    <p>execution_allowed: <strong>{html.escape(str(std.get("execution_allowed")))}</strong></p>
    <p>credentials_loaded: <strong>{html.escape(str(std.get("credentials_loaded")))}</strong></p>
    <p>real_target_connected: <strong>{html.escape(str(std.get("real_target_connected")))}</strong></p>
    <p>network_called: <strong>{html.escape(str(std.get("network_called")))}</strong></p>
    <p>evidence_generated: <strong>{html.escape(str(std.get("evidence_generated")))}</strong></p>
    <p>production_target_allowed: <strong>{html.escape(str(std.get("production_target_allowed")))}</strong></p>
    <p>smoke_test_design_only: <strong>{html.escape(str(std.get("smoke_test_design_only")))}</strong></p>
    <p>design_files: <strong>{html.escape(str(std.get("design_files")))}</strong></p>
    <p>validation_checks: <strong>{html.escape(str(std.get("validation_checks")))}</strong></p>
    <p>validation_passed: <strong>{html.escape(str(std.get("validation_passed")))}</strong></p>
    <p>minimal_requests: <strong>{html.escape(str(std.get("minimal_requests")))}</strong></p>
    <p>preflight_checks: <strong>{html.escape(str(std.get("preflight_checks")))}</strong></p>
    <p>abort_conditions: <strong>{html.escape(str(std.get("abort_conditions")))}</strong></p>
    <p>Phase 31E is a single authorized API smoke test design layer only. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. No adversarial prompts. No network calls. No real credentials. The smoke test design is a static design definition only — not an execution plan.</p>
  </div>
</section>
<section id="approval-packet">
  <h2>Single Smoke Test Approval Packet</h2>
  <div class="card">
    <p>approval_packet_ready: <strong>{html.escape(str(ap.get("approval_packet_ready")))}</strong></p>
    <p>approval_status: <strong>{html.escape(str(ap.get("approval_status")))}</strong></p>
    <p>go_no_go_status: <strong>{html.escape(str(ap.get("go_no_go_status")))}</strong></p>
    <p>execution_allowed: <strong>{html.escape(str(ap.get("execution_allowed")))}</strong></p>
    <p>human_approval_required: <strong>{html.escape(str(ap.get("human_approval_required")))}</strong></p>
    <p>operator_signoff_required: <strong>{html.escape(str(ap.get("operator_signoff_required")))}</strong></p>
    <p>risk_acceptance_required: <strong>{html.escape(str(ap.get("risk_acceptance_required")))}</strong></p>
    <p>credentials_loaded: <strong>{html.escape(str(ap.get("credentials_loaded")))}</strong></p>
    <p>real_target_connected: <strong>{html.escape(str(ap.get("real_target_connected")))}</strong></p>
    <p>network_called: <strong>{html.escape(str(ap.get("network_called")))}</strong></p>
    <p>evidence_generated: <strong>{html.escape(str(ap.get("evidence_generated")))}</strong></p>
    <p>production_target_allowed: <strong>{html.escape(str(ap.get("production_target_allowed")))}</strong></p>
    <p>execution_hold: <strong>{html.escape(str(ap.get("execution_hold")))}</strong></p>
    <p>design_files: <strong>{html.escape(str(ap.get("design_files")))}</strong></p>
    <p>validation_checks: <strong>{html.escape(str(ap.get("validation_checks")))}</strong></p>
    <p>validation_passed: <strong>{html.escape(str(ap.get("validation_passed")))}</strong></p>
    <p>Phase 31F is a single smoke test approval packet and go/no-go gate layer only. All approval packet files declare approval_packet_ready=true, approval_status=not_approved, go_no_go_status=no_go, execution_allowed=false, human_approval_required=true, operator_signoff_required=true, risk_acceptance_required=true, execution_hold=true. No real APIs connected. No real credentials loaded. No real endpoints accessed. No real security tests executed. No adversarial prompts. No network calls. The approval packet is a static approval packet definition only — not an execution gate.</p>
  </div>
</section>
<section id="full-regression-execution">
  <h2>Full Authorized API Regression Execution</h2>
  <div class="card">
    <p>execution_mode: <strong>{html.escape(str(fre.get("execution_mode")))}</strong></p>
    <p>target_environment: <strong>{html.escape(str(fre.get("target_environment")))}</strong></p>
    <p>provider_type: <strong>{html.escape(str(fre.get("provider_type")))}</strong></p>
    <p>total_requests_attempted: <strong>{html.escape(str(fre.get("total_requests_attempted")))}</strong></p>
    <p>total_requests_completed: <strong>{html.escape(str(fre.get("total_requests_completed")))}</strong></p>
    <p>total_pass: <strong>{html.escape(str(fre.get("total_pass")))}</strong></p>
    <p>total_fail: <strong>{html.escape(str(fre.get("total_fail")))}</strong></p>
    <p>total_skipped: <strong>{html.escape(str(fre.get("total_skipped")))}</strong></p>
    <p>finding_candidates: <strong>{html.escape(str(fre.get("finding_candidates")))}</strong></p>
    <p>redaction_applied: <strong>{html.escape(str(fre.get("redaction_applied")))}</strong></p>
    <p>api_key_logged: <strong>{html.escape(str(fre.get("api_key_logged")))}</strong></p>
    <p>authorization_header_logged: <strong>{html.escape(str(fre.get("authorization_header_logged")))}</strong></p>
    <p>production_target: <strong>{html.escape(str(fre.get("production_target")))}</strong></p>
    <p>Phase 32C is a full authorized API regression execution layer. Regression executed against authorized test API only, not production. All findings are candidates only and require human review before formal finding status. No formal customer report generated.</p>
  </div>
</section>
<section id="deepseek-judge-result-integration">
  <h2>DeepSeek Judge Result Integration</h2>
  <div class="card">
    <p>integration_complete: <strong>{html.escape(str(dji.get("integration_complete")))}</strong></p>
    <p>source_phase: <strong>{html.escape(str(dji.get("source_phase")))}</strong></p>
    <p>total_api_calls: <strong>{html.escape(str(dji.get("total_api_calls")))}</strong></p>
    <p>total_tokens: <strong>{html.escape(str(dji.get("total_tokens")))}</strong></p>
    <p>estimated_cost: <strong>${html.escape(str(dji.get("estimated_cost")))}</strong></p>
    <p>authenticity_verdict: <strong>{html.escape(str(dji.get("authenticity_verdict")))}</strong></p>
    <p>requires_manual_billing_verification: <strong>{html.escape(str(dji.get("requires_manual_billing_verification")))}</strong></p>
    <p>total_finding_candidates: <strong>{html.escape(str(dji.get("total_finding_candidates")))}</strong></p>
    <p>smoke_reviewed_candidates: <strong>{html.escape(str(dji.get("smoke_reviewed_candidates")))}</strong></p>
    <p>batch_reviewed_candidates: <strong>{html.escape(str(dji.get("batch_reviewed_candidates")))}</strong></p>
    <p>candidate_coverage: <strong>{html.escape(str(dji.get("total_candidate_coverage")))}</strong></p>
    <p>groups_reviewed: <strong>{html.escape(str(dji.get("groups_reviewed")))}</strong></p>
    <p>all_require_human_review: <strong>{html.escape(str(dji.get("all_require_human_review")))}</strong></p>
    <p>no_formal_findings: <strong>{html.escape(str(dji.get("no_formal_findings")))}</strong></p>
    <p>budget_reconciled: <strong>{html.escape(str(dji.get("budget_reconciled")))}</strong></p>
    <p>Phase 34D is a static result integration & review report layer. No DeepSeek API re-call, no .local/ read, no target API connection, no test re-run. All judge results remain candidate status and require human review before any decision-making. No formal findings generated.</p>
  </div>
</section>
<section>
  <h2>Promptfoo Integration Framework</h2>
  <div class="card-grid">
    <div class="card"><div class="label">Framework Complete</div><div class="value">{html.escape(str(pfi.get("framework_complete")))}</div></div>
    <div class="card"><div class="label">Profiles Indexed</div><div class="value">{pfi.get("profiles_indexed")}</div></div>
    <div class="card"><div class="label">Execution Mode</div><div class="value">{pfi.get("execution_mode")}</div></div>
  </div>
  <p>directory: <code>{pfi.get("directory")}</code></p>
  <p>result_schema_defined: <strong>{html.escape(str(pfi.get("result_schema_defined")))}</strong></p>
  <p>mock_results_generated: <strong>{html.escape(str(pfi.get("mock_results_generated")))}</strong></p>
  <p>evidence_mapping_defined: <strong>{html.escape(str(pfi.get("evidence_mapping_defined")))}</strong></p>
  <p>finding_candidate_mapping_defined: <strong>{html.escape(str(pfi.get("finding_candidate_mapping_defined")))}</strong></p>
  <p>judge_handoff_schema_defined: <strong>{html.escape(str(pfi.get("judge_handoff_schema_defined")))}</strong></p>
  <p>adapter_skeleton_created: <strong>{html.escape(str(pfi.get("adapter_skeleton_created")))}</strong></p>
  <p>real_target_connected: <strong>{html.escape(str(pfi.get("real_target_connected")))}</strong></p>
  <p>usable_for_formal_finding: <strong>{html.escape(str(pfi.get("usable_for_formal_finding")))}</strong></p>
  <p>promptfoo_eval_run: <strong>{html.escape(str(pfi.get("promptfoo_eval_run")))}</strong></p>
  <p>deepseek_api_called: <strong>{html.escape(str(pfi.get("deepseek_api_called")))}</strong></p>
  <p>Phase 35 is a schema/config/mock/adapter layer only. No promptfoo CLI installed or executed. No real targets connected. No DeepSeek API called. No .local/ read. No original drafts modified. All results remain candidate status and require human Go/No-Go before real execution.</p>
</section>
<section>
  <h2>Promptfoo Go/No-Go Packet</h2>
  <div class="card-grid">
    <div class="card"><div class="label">Approval Status</div><div class="value">{html.escape(str(pfgn.get("approval_status")))}</div></div>
    <div class="card"><div class="label">Execution Allowed</div><div class="value">{html.escape(str(pfgn.get("execution_allowed")))}</div></div>
    <div class="card"><div class="label">Validate Passed</div><div class="value">{pfgn.get("validate_passed")}/{pfgn.get("validate_total")}</div></div>
  </div>
  <p>packet_files: <strong>{pfgn.get("packet_files")}</strong> | directory: <code>{pfgn.get("directory")}</code></p>
  <p>network_allowed: <strong>{html.escape(str(pfgn.get("network_allowed")))}</strong> | promptfoo_eval_allowed: <strong>{html.escape(str(pfgn.get("promptfoo_eval_allowed")))}</strong> | target_api_call_allowed: <strong>{html.escape(str(pfgn.get("target_api_call_allowed")))}</strong></p>
  <p>deepseek_judge_allowed: <strong>{html.escape(str(pfgn.get("deepseek_judge_allowed")))}</strong> | credential_loaded: <strong>{html.escape(str(pfgn.get("credential_loaded")))}</strong> | human_go_no_go_required: <strong>{html.escape(str(pfgn.get("human_go_no_go_required")))}</strong></p>
  <p>Phase 35B is a Go/No-Go packet layer only. No promptfoo eval, no target API call, no DeepSeek API call, no .local/ read. All files declare approval_status=not_approved and execution_allowed=false. Human Go/No-Go required before any real execution.</p>
</section>
<section>
  <h2>Promptfoo Execution Readiness Gate</h2>
  <div class="card-grid">
    <div class="card"><div class="label">Readiness Status</div><div class="value">{html.escape(str(pfer.get("readiness_status")))}</div></div>
    <div class="card"><div class="label">Validate Passed</div><div class="value">{pfer.get("validate_passed")}/{pfer.get("validate_total")}</div></div>
  </div>
  <p>readiness_files: <strong>{pfer.get("readiness_files")}</strong> | directory: <code>{pfer.get("directory")}</code></p>
  <p>promptfoo_eval_run: <strong>{html.escape(str(pfer.get("promptfoo_eval_run")))}</strong> | target_api_connected: <strong>{html.escape(str(pfer.get("target_api_connected")))}</strong> | deepseek_api_called: <strong>{html.escape(str(pfer.get("deepseek_api_called")))}</strong></p>
  <p>local_config_read: <strong>{html.escape(str(pfer.get("local_config_read")))}</strong> | formal_finding_generated: <strong>{html.escape(str(pfer.get("formal_finding_generated")))}</strong></p>
  <p>Phase 35C.0 is an execution readiness gate layer. Static verification only — no promptfoo eval, no target API connection, no DeepSeek API call, no .local/ read. Must pass before any controlled promptfoo execution. Does not replace Phase 35B Go/No-Go.</p>
</section>
<section id="coverage">
  <h2>Technique 覆盖表</h2>
  <table><thead><tr><th>Tactic</th><th>Technique ID</th><th>Name</th><th>Status</th><th>Profiles</th><th>Capabilities</th><th>Evidence</th><th>Gaps</th><th>Next Steps</th></tr></thead><tbody>{technique_rows}</tbody></table>
</section>
<section>
  <h2>Evidence 索引</h2>
  <ul>{''.join(f'<li><code>{html.escape(item)}</code></li>' for item in data['evidence_index'])}</ul>
</section>
<section>
  <h2>风险信号摘要</h2>
  <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in data['risk_signals'])}</ul>
</section>
<section>
  <h2>控制项摘要</h2>
  <div class="profile-grid">{controls}</div>
</section>
<section id="gaps">
  <h2>当前覆盖缺口</h2>
  <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in data['known_gaps'])}</ul>
</section>
<section id="roadmap">
  <h2>后续路线图</h2>
  <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in data['roadmap'])}</ul>
</section>
</main>
<footer>Generated at {html.escape(data['generated_at'])}. Local static HTML only.</footer>
</body>
</html>
"""


def main() -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    data = build_data()
    (DASHBOARD_DIR / "dashboard_data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DASHBOARD_DIR / "index.md").write_text(render_markdown(data), encoding="utf-8")
    (DASHBOARD_DIR / "atlas_dashboard.html").write_text(render_html(data), encoding="utf-8")
    print("Generated dashboard/dashboard_data.json")
    print("Generated dashboard/index.md")
    print("Generated dashboard/atlas_dashboard.html")


if __name__ == "__main__":
    main()
