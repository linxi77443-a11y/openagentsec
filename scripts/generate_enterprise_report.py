#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "reports/evidence/atlas_assessment_summary.json"
EVIDENCE_INDEX_PATH = ROOT / "reports/evidence_index.md"
COVERAGE_SUMMARY_PATH = ROOT / "coverage/atlas_coverage_summary.md"
GAP_ANALYSIS_PATH = ROOT / "coverage/coverage_gap_analysis.md"
CONTROL_CHECKLIST_PATH = ROOT / "docs/control_checklist.md"
TEMPLATE_PATH = ROOT / "reports/enterprise_ai_security_assessment_template.md"
OUTPUT_PATH = ROOT / "reports/generated_atlas_assessment_report.md"
MANUAL_UI_EVIDENCE_PATH = ROOT / "reports/evidence/promptfoo_manual_ui_result.json"
API_CHATBOT_DRY_RUN_EVIDENCE_PATH = ROOT / "reports/evidence/api_chatbot_provider_dry_run.json"
API_RAG_DRY_RUN_EVIDENCE_PATH = ROOT / "reports/evidence/api_rag_provider_dry_run.json"
GENERIC_AGENT_PROFILE_PATH = ROOT / "assessment_profiles/generic_agent_profile.yaml"
GENERIC_AGENT_CATALOG_PATH = ROOT / "test_catalog/generic_agent_test_catalog.yaml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(read(path))


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.start()
    next_match = re.search(r"^##\s+", text[match.end():], re.MULTILINE)
    if not next_match:
        return text[start:].strip()
    return text[start:match.end() + next_match.start()].strip()


def result_table(results: list[dict[str, Any]]) -> str:
    lines = [
        "| Profile | Runner | Evidence | Pass | Fail | Error | Status |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for item in results:
        lines.append(
            f"| {item.get('profile')} | `{item.get('runner')}` | `{item.get('evidence_file')}` | {item.get('pass', 0)} | {item.get('fail', 0)} | {item.get('error', 0)} | {item.get('status')} |"
        )
    return "\n".join(lines)


def covered_risks(results: list[dict[str, Any]]) -> list[str]:
    techniques = sorted({tech for item in results for tech in item.get("covered_atlas_techniques", [])})
    names = {
        "atlas.llm_prompt_injection": "LLM Prompt Injection",
        "atlas.direct_prompt_injection": "Direct Prompt Injection",
        "atlas.llm_prompt_obfuscation": "LLM Prompt Obfuscation",
        "atlas.extract_llm_system_prompt": "Extract LLM System Prompt",
        "atlas.llm_data_leakage": "LLM Data Leakage",
        "atlas.rag_poisoning": "RAG Poisoning",
        "atlas.false_rag_entry_injection": "False RAG Entry Injection",
        "atlas.indirect_prompt_injection": "Indirect Prompt Injection",
        "atlas.ai_agent_tool_invocation": "AI Agent Tool Invocation",
        "atlas.ai_agent_context_poisoning": "AI Agent Context Poisoning",
        "atlas.credentials_from_ai_agent_configuration": "Credentials from AI Agent Configuration",
        "atlas.exfiltration_via_ai_agent_tool_invocation": "Exfiltration via AI Agent Tool Invocation",
    }
    return [f"`{tech}`：{names.get(tech, tech)}" for tech in techniques]


def control_recommendations(control_text: str) -> str:
    wanted = ["## 1. Chatbot 控制项", "## 2. RAG 控制项", "## 3. Agent 控制项", "## 5. Phase 7 ATLAS 驱动评估系统控制项"]
    lines = []
    for heading in wanted:
        idx = control_text.find(heading)
        if idx == -1:
            continue
        next_idx = control_text.find("\n## ", idx + 1)
        chunk = control_text[idx: next_idx if next_idx != -1 else len(control_text)]
        checks = [line for line in chunk.splitlines() if line.startswith("- [ ]")]
        lines.append(f"### {heading.replace('## ', '')}")
        lines.extend(checks[:8])
        lines.append("")
    return "\n".join(lines).strip()


def main() -> None:
    summary = read_json(SUMMARY_PATH)
    evidence_index = read(EVIDENCE_INDEX_PATH)
    coverage_summary = read(COVERAGE_SUMMARY_PATH)
    gap_analysis = read(GAP_ANALYSIS_PATH)
    control_text = read(CONTROL_CHECKLIST_PATH)
    template_note = read(TEMPLATE_PATH).splitlines()[0]
    results = summary.get("results", [])
    total_pass = sum(item.get("pass", 0) for item in results)
    total_fail = sum(item.get("fail", 0) for item in results)
    total_error = sum(item.get("error", 0) for item in results)
    covered = covered_risks(results)
    generated_at = datetime.now(timezone.utc).isoformat()
    manual_ui_status = "available" if MANUAL_UI_EVIDENCE_PATH.exists() else "not_run"
    api_provider_status = "dry_run_ready" if API_CHATBOT_DRY_RUN_EVIDENCE_PATH.exists() and API_RAG_DRY_RUN_EVIDENCE_PATH.exists() else "not_run"

    report = f"""# ATLAS 驱动 AI 安全评估报告

{template_note}

## 1. 评估背景

本报告基于本地受控 AI 安全评估工作台生成，用于汇总 MITRE ATLAS 视角下的 Chatbot、RAG、Agent 本地 sandbox 评估结果。报告服务于内部防守、治理、修复和复测，不作为攻击操作手册。

- 报告生成时间：{generated_at}
- ATLAS summary 时间：{summary.get('generated_at')}
- 当前阶段：Phase 32D.1 + 32E Chinese Report Localization, Finding Triage & Report Hardening
- 数据来源：本地 evidence、coverage matrix、控制项清单、API Provider dry-run readiness、Generic Agent Assessment Pack、报告模板、Evaluation Corpus、AI Red Teaming 方法论、AI Asset Inventory、NIST AI RMF Governance Mapping、AI/ML-BOM + Supply Chain Mapping、External Evaluation Tool Adapter Planning、External Tool Mock Evidence Normalization、System Release Consolidation v1.3、OWASP LLM Top 10 Crosswalk、Assessment Plan Generator、Corpus-to-Testcase Compiler、Generated Testcase Curation & Runner Binding、Curated Regression Suite Builder、Regression Suite Gap Triage、Phase 27A Corpus & Curation Backfill、Regression Suite Dry-Run Validation、Assertion & Risk Signal Rule Engine、Finding Generator Prototype、Formal Report Package Builder、Authorized Test Target Onboarding；Phase 31 Generic API Provider Formalization：api_provider/ 目录结构、provider schema（6 provider types）、target profile schema（5 environment types）、config template（placeholder only）、request/response normalization schema（6 redaction rules）、provider safety guardrails（16 guardrails across 3 layers）、provider execution boundary、dry-run simulator、validation script（15 checks）、5 sample targets（openai_compatible_chat/rag_qa_api/agent_api/workflow_api/fastgpt_compatible）。所有 sample target 声明 real_target=false、dry_run_only=true、execution_allowed=false、usable_for_real_test=false；Phase 31B Authorized Test Target Onboarding：onboarding/ 目录结构、authorized target onboarding schema、RoE checklist、credential isolation policy、test scope definition、allowed/prohibited operations matrix、rate limit and safety window policy、approval gate checklist、onboarding validation script（18 checks）。所有 target 声明 authorization_required=true、approval_status=not_approved、execution_allowed=false。；Phase 31C Local Mock API Execution Harness：api_provider/mock_harness/ 目录结构、mock API target schema、mock request/response fixtures（8 请求/8 响应，覆盖 5 种 provider 类型）、mock execution trace、mock normalized response samples、mock execution boundary、run/validate 脚本。所有输出声明 mock_execution=true、external_network_called=false、credentials_loaded=false、real_target_connected=false、evidence_generated=false、usable_for_formal_finding=false。；Phase 31D Limited Authorized API Dry-Run Plan：authorized_dry_run_plan/ 目录结构、dry_run_plan schema、rate limit and request budget policy、rollback and stop conditions plan、human approval gate checklist、allowed test bundle definition、preflight readiness checklist、credential isolation checklist、validation script（19 checks）。所有计划文件声明 placeholder markers only、no real URLs、no real tokens、no real credentials、no real emails、no real API keys、no network calls。；Phase 31E Single Authorized API Smoke Test Design：api_provider/single_smoke_test_design/ 目录结构、single smoke test schema、candidate target template、minimal request bundle、expected safe response contract、execution preflight gate、abort condition checklist、operator runbook template、evidence placeholder schema、validation script（20 checks）。所有设计文件声明 smoke_test_design_ready=true、only_one_target_allowed=true、read_only_operations_only=true、approval_status=not_approved、execution_allowed=false、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false。未使用真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求、未使用对抗性提示。Phase 31F Single Smoke Test Approval Packet & Go/No-Go Gate：api_provider/smoke_test_approval_packet/ 目录结构、10 个设计文件、approval packet schema、go/no-go gate checklist、risk acceptance form、operator signoff template、credential readiness verification、real target connection verification、rollback plan template、communication plan template、approval packet validation script（20 checks）。所有审批文件声明 approval_packet_ready=true、approval_status=not_approved、go_no_go_status=no_go、execution_allowed=false、human_approval_required=true、operator_signoff_required=true、risk_acceptance_required=true、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false、production_target_allowed=false、execution_hold=true。未使用真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求、未使用对抗性提示。；Phase 32C Full Authorized API Regression Execution：执行全量回归测试，生成 evidence 和 finding candidates。测试仅针对授权 test API，不针对生产环境。所有 finding 为 candidate 状态，需人工审核后方可成为正式 finding。未生成正式客户报告。；Phase 32D Real API Regression Assessment Report Builder：基于 Phase 32C 结果构建完整评估报告，包含执行摘要、技术发现、覆盖矩阵、风险摘要、修复建议、复测建议、证据索引、完整报告。不重新运行测试，不连接 API，不读取凭证。；Phase 32D.1 Chinese Report Localization：保留英文报告为 _en.md，中文报告为默认 .md，生成 report_language_index.md 双语索引。；Phase 32E Finding Triage & Report Hardening：生成 finding_triage/ 发现研判材料（16 候选→5 组）和 final_hardened/ 最终汇报版材料（管理层简报、最终执行摘要、发现摘要、修复行动计划、复测计划）。所有发现保持 needs_human_review 状态。

## 2. 评估范围

| 项目 | 内容 |
|---|---|
| 评估对象 | 本地 Chatbot、RAG、Agent sandbox |
| 环境 | local sandbox |
| 数据类型 | fake data / dummy data / honeytoken，经脱敏后进入 evidence |
| 语料来源 | Evaluation Corpus（93 条语料，7 个 profile） |
| 执行边界 | API Provider Skeleton 只运行 dry-run readiness，不运行 API `--execute` |
| 排除范围 | 真实企业系统、真实 API、真实模型、真实页面、真实凭证、外部网络目标 |

## 3. 评估方法

- 使用 Phase 7 / 7.5 已生成的 ATLAS summary evidence。
- 按 MITRE ATLAS tactic / technique 汇总覆盖状态。
- 结合 coverage summary、gap analysis、control checklist 输出治理建议。
- 仅读取本地 JSON / YAML / Markdown 文件并生成 Markdown 报告。

## 4. MITRE ATLAS 映射说明

本项目将 prompt、检索上下文、Agent 工具调用、凭证访问和数据外传等行为映射到 ATLAS technique，并用本地 promptfoo evidence 验证安全控制是否按预期生效。

{section(coverage_summary, '当前覆盖概览') or '详见 coverage/atlas_coverage_summary.md。'}

## 5. 测试对象

| 对象 | 类型 | 本地 runner | Evidence |
|---|---|---|---|
| chatbot | Chatbot | `runners/run_promptfoo.sh` | `reports/evidence/promptfoo_chatbot_result.json` |
| rag | RAG | `runners/run_rag_promptfoo.sh` | `reports/evidence/promptfoo_rag_result.json` |
| agent | Agent | `runners/run_agent_promptfoo.sh` | `reports/evidence/promptfoo_agent_result.json` |

## 6. 测试结果总览

{result_table(results)}

合计：{total_pass} passed，{total_fail} failed，{total_error} errors。

## 7. Manual UI Replay

Manual UI Replay 用于把人工页面输入输出复制结果保存为本地 replay JSON，再由本地 provider 做风险信号分析、脱敏和 evidence 生成。

| 项目 | 内容 |
|---|---|
| 当前状态 | {manual_ui_status} |
| Runner | `runners/run_manual_ui_promptfoo.sh` |
| Provider | `providers/manual_replay_provider.py` |
| Sample source | `replays/manual_ui_samples/` |
| Evidence | `reports/evidence/promptfoo_manual_ui_result.json` |

Phase 9.5 已生成本地 fake replay evidence，但不代表真实页面评估结果。

## 8. API Provider Skeleton

API Provider Skeleton 用于未来接入测试环境 Chatbot / RAG API。Phase 11 只提供 placeholder target、provider skeleton、mock response、dry-run runner 和 readiness evidence，不执行真实 HTTP 请求。

| 项目 | 内容 |
|---|---|
| 当前状态 | {api_provider_status} |
| Chatbot runner | `runners/run_api_chatbot_provider.sh` |
| RAG runner | `runners/run_api_rag_provider.sh` |
| Target schema | `targets/api/api_target_schema.md` |
| Chatbot evidence | `reports/evidence/api_chatbot_provider_dry_run.json` |
| RAG evidence | `reports/evidence/api_rag_provider_dry_run.json` |
| Real API tested | false |
| Network access | false |
| Credentials loaded | false |

该状态只表示 skeleton dry-run readiness，不代表真实 API tested / passed。

## 8.5 Generic Agent Assessment Pack

Phase 12 新增 Generic Agent Assessment Pack，提供面向 Hermes / OpenClaw / Claude Code / LangGraph / AutoGen / MCP / 企业流程 Agent 的通用评估框架。

| 项目 | 内容 |
|---|---|
| 当前状态 | framework_ready |
| Profile | `assessment_profiles/generic_agent_profile.yaml` |
| 攻击面文档 | `docs/generic_agent_attack_surface.md` |
| 测试能力目录 | `test_catalog/generic_agent_test_catalog.yaml` |
| 控制项清单 | `docs/generic_agent_control_checklist.md` |
| 评估方法论 | `docs/generic_agent_assessment_methodology.md` |
| Manual replay 样例 | `replays/manual_ui_samples/generic_agent_manual_replay_sample.json` |
| 报告模板 | `reports/generic_agent_assessment_template.md` |
| Local sandbox 可执行 | True |
| Mock harness 就绪 | True |
| Test instance 就绪 | False |
| 真实 Agent 集成 | False |

当前提供框架和方法论，Mock Tool Harness 已可执行（Phase 13），不代表任何真实 Agent 已测试或已通过。

## 9. OWASP Agentic Top 10 Crosswalk

Phase 14 将 OWASP Agentic Top 10 风险分类融入评估体系。当前覆盖状态：

| ASI | 名称 | 状态 |
|---|---|---|
| ASI01 | Agent Goal Hijack | covered_by_local_harness |
| ASI02 | Tool Misuse and Exploitation | covered_by_local_harness |
| ASI03 | Identity and Privilege Abuse | covered_by_local_harness |
| ASI04 | Agentic Supply Chain Vulnerabilities | partially_covered |
| ASI05 | Unexpected Code Execution | not_supported_for_now |
| ASI06 | Memory & Context Poisoning | covered_by_local_harness |
| ASI07 | Insecure Inter-Agent Communication | planned |
| ASI08 | Cascading Failures | covered_by_local_harness |
| ASI09 | Human-Agent Trust Exploitation | covered_by_local_harness |
| ASI10 | Rogue Agents | planned |

OWASP Agentic Top 10 是风险分类层，不替代 MITRE ATLAS。ATLAS 用于"怎么测"，OWASP 用于"怎么报"。

## 9.5 Evaluation Corpus

Phase 15 新增统一评估语料库，覆盖 Chatbot / RAG / Agent / API / Business / Regression 六个 profile，共 49 条语料。语料位于 test design 层，使用统一 schema 定义，与 testcases（执行层）、replays（人工 replay 层）、evidence（结果层）四层分离。Corpus 索引位于 `corpus/corpus_index.yaml`，支持按 profile、framework、execution_mode、status 和 severity 检索。

| Profile | 语料数 | 执行模式 | 主要风险 |
|---|---|---|---|
| Chatbot | 14 | local_sandbox | prompt injection、system prompt exposure、sensitive disclosure、multilingual bypass |
| RAG | 14 | local_sandbox | indirect injection、RAG poisoning、fake citation、over-disclosure |
| Agent | 16 | manual_replay | tool misuse、memory poisoning、skill poisoning、exfiltration、resource consumption |
| API | 11 | api_provider_future_or_skeleton / planned | smoke、auth、authorization、rate limiting、unbounded consumption |
| Business | 8 | manual_replay | SOC、XDR、policy QA、project management |
| Regression | 9 | local_sandbox | core security regression、smoke tests |

## 10. ATLAS 覆盖情况

详见：`coverage/atlas_coverage_matrix.yaml`、`coverage/atlas_coverage_summary.md`。

{section(coverage_summary, '按 profile 汇总') or ''}

## 10. 已覆盖风险

"""
    report += "\n".join(f"- {item}" for item in covered)
    report += f"""

## 11. 未覆盖缺口

{gap_analysis.strip()}

## 12. Evidence 索引

关键 evidence：

- `reports/evidence/atlas_assessment_summary.json`
- `reports/evidence/promptfoo_chatbot_result.json`
- `reports/evidence/promptfoo_rag_result.json`
- `reports/evidence/promptfoo_agent_result.json`
- `reports/evidence/promptfoo_manual_ui_result.json`
- `reports/evidence/api_chatbot_provider_dry_run.json`
- `reports/evidence/api_rag_provider_dry_run.json`
- `corpus/corpus_index.yaml`

完整 evidence index 摘要：

{section(evidence_index, '总览') or '详见 reports/evidence_index.md。'}

## 13. 控制项建议

{control_recommendations(control_text)}

## 14. 后续复测建议

- Manual UI Replay：仅在本地或授权测试环境复现 dashboard / report 中的关键路径。
- API Provider Skeleton：保持 dry-run readiness，后续若接入测试环境 API，先完成授权、测试账号、凭证加载、速率、日志和脱敏策略。
- 浏览器自动化：只限测试环境，不访问真实生产页面或真实账号。
- garak / PyRIT / AgentDojo：先做本地 mock 接入，保留 fake data 和无真实副作用边界。
- Evaluation Corpus：API 和 Business 语料尚无可执行 runner，需后续 phase 补齐。

## 15. AI Red Teaming Methodology

Phase 16 新增 AI Red Teaming 执行方法论层（`red_team/`），包含 9 个文件：12 步 Playbook、RoE 模板、Session 模板、Severity Model、Finding 模板、Evidence 指南、Mitigation & Retest 工作流和 Red Team Report 大纲。

Severity Model（`red_team/finding_severity_model.md`）定义 7 维度评分模型（D1-D7），将 evidence 中的布尔字段（如 `should_refuse`、`leaked_secret`）映射为 finding severity 等级（Informational / Low / Medium / High / Critical）。Severity assessment 表位于 finding 模板中，包含 D1-D7 维度取值、base_score、adjustments 和 final severity。

当前 `red_team/` 是方法论/模板层，不执行测试、不连接真实目标。**未执行真实红队项目**。所有模板均可在未来真实红队评估中复用。

## 16. AI Asset Inventory

Phase 17 新增 AI Asset Inventory 目录 `inventory/`，用于记录和分类 AI 应用资产，作为评估入口之一。

| 文件 | 用途 |
|---|---|
| `inventory/ai_asset_inventory_schema.md` | 9 分类资产字段定义 |
| `inventory/sample_ai_asset_inventory.yaml` | 5 个样例资产（全部 fake 数据） |
| `inventory/ai_application_intake_form.md` | AI 应用接入登记表单 |
| `inventory/ai_asset_risk_register_template.yaml` | 风险登记表模板 |
| `inventory/ai_asset_inventory_index.yaml` | 资产索引（按类型/profile/环境/风险等维度） |

当前资产为 sample/fake 数据，不代表任何真实系统。Inventory 通过与 profile、corpus、ATLAS technique 联动驱动评估流程。

## 17. NIST AI RMF Governance Mapping

Phase 17 新增 `governance/` 目录，建立 NIST AI RMF 治理映射层。

| NIST Function | Support Status |
|---|---|
| Govern | partially_supported |
| Map | supported |
| Measure | supported |
| Manage | partially_supported |

### 关键文件

| 文件 | 用途 |
|---|---|
| `governance/nist_ai_rmf_mapping.yaml` | NIST AI RMF 四个 function 映射 |
| `governance/nist_genai_profile_mapping.yaml` | GenAI 风险类别映射占位 |
| `governance/ai_risk_governance_checklist.md` | 12 类 60+ 治理检查项 |
| `governance/governance_to_security_assessment_crosswalk.md` | 治理到安全评估的交叉映射 |
| `governance/governance_report_appendix_template.md` | 治理报告附录模板 |

**重要说明**：NIST AI RMF 映射是项目内部的治理映射层，**不代表已完成 NIST 合规认证**。当前映射基于本地 sandbox / fake data 评估，不适用于真实生产环境。

## 18. AI/ML-BOM + Supply Chain Mapping

Phase 18 新增 `supply_chain/` 目录，建立 AI/ML-BOM 和供应链映射层。

| 文件 | 用途 |
|---|---|
| `supply_chain/ai_ml_bom_schema.md` | AI/ML-BOM 9 类组件字段定义 |
| `supply_chain/sample_ai_ml_bom.yaml` | 5 个样例 BOM（对应 5 个 inventory 资产） |
| `supply_chain/model_provenance_checklist.md` | 模型来源可追溯性检查清单 |
| `supply_chain/dataset_knowledge_base_inventory.md` | 数据集/知识库来源清单 |
| `supply_chain/tool_plugin_mcp_inventory.yaml` | 工具/插件/MCP 依赖清单 |
| `supply_chain/prompt_template_inventory.yaml` | 提示词模板依赖清单 |
| `supply_chain/external_api_dependency_inventory.yaml` | 外部 API 依赖清单 |
| `supply_chain/supply_chain_risk_register_template.yaml` | 供应链风险登记表模板 |
| `supply_chain/supply_chain_to_atlas_owasp_mapping.yaml` | 15 条供应链风险到 ATLAS/OWASP/NIST 映射 |
| `supply_chain/supply_chain_report_appendix_template.md` | 供应链报告附录模板 |

### 关键映射

供应链风险到 ATLAS/OWASP 的 15 条映射涵盖：模型提供商、数据集中毒、嵌入模型、向量数据库、工具/插件、MCP 服务器、外部 API、提示词模板、运行时框架、依赖混淆、模型微调投毒、数据管线和许可证合规。

### 当前状态

- 所有 BOM 为 sample / fake 数据，不代表任何真实系统的组件依赖关系。
- 供应链风险映射为方法论参考，不构成完整供应链威胁模型。
- 本系统未连接真实模型仓库、真实供应商系统或真实依赖扫描工具。
- 供应链风险评估不替代现有的安全测试流程，而是补充来源追溯和依赖风险视角。

## 19. External Evaluation Tool Adapter Planning、External Tool Mock Evidence Normalization

Phase 19 新增 `external_tools/` 目录，规划外部评估工具 adapter 层，使未来可以有序接入 garak、PyRIT、Agent benchmark、Browser Automation 和 API Provider 等能力。

| 文件 | 用途 |
|---|---|
| `external_tools/external_tool_evidence_schema.md` | 外部工具结果统一 evidence schema |
| `external_tools/external_tool_risk_boundary.md` | 外部工具接入风险边界 |
| `external_tools/external_tool_adapter_index.yaml` | 6 个 adapter 的索引、状态和优先级 |
| `external_tools/external_tool_to_atlas_owasp_mapping.yaml` | 外部工具到 ATLAS / OWASP / corpus / evidence 的映射 |
| `external_tools/garak_adapter_plan.md` | garak adapter 设计计划 |
| `external_tools/pyrit_adapter_plan.md` | PyRIT adapter 设计计划 |
| `external_tools/agent_benchmark_adapter_plan.md` | AgentDojo / AgentDyn adapter 设计计划 |
| `external_tools/browser_automation_adapter_plan.md` | Browser Automation adapter 设计计划 |
| `external_tools/api_provider_adapter_plan.md` | API Provider adapter 设计计划 |
| `external_tools/external_tool_report_appendix_template.md` | 外部工具报告附录模板 |

### Adapter 状态

| Adapter | Current Status | Integration Priority |
|---|---|---|
| garak_adapter | mock_normalization_ready | medium |
| pyrit_adapter | mock_normalization_ready | medium |
| agentdojo_adapter | mock_normalization_ready | low |
| agentdyn_adapter | mock_normalization_ready | low |
| browser_automation_adapter | mock_normalization_ready | low |
| api_provider_adapter | mock_normalization_ready | high |

### 当前边界

- 本阶段没有安装任何外部工具。
- 本阶段没有运行任何外部工具。
- 本阶段没有运行任何 `--execute`。
- 本阶段没有连接真实 API、真实 Agent、真实页面或外部网络。
- Phase 19 没有生成真实 external tool evidence。
- Phase 20 只生成 mock normalized evidence，不代表真实外部工具已执行。
- 外部工具不会替代现有 ATLAS / OWASP / corpus / evidence 体系；未来真实输出必须归一化到统一 evidence schema。


## 20. External Tool Mock Evidence Normalization

Phase 20 使用 `external_tools/mock_outputs/` 中的 fake/mock 外部工具输出，验证外部工具 evidence schema 与 adapter mapping 能够被归一化为统一 evidence。

| 文件 | 用途 |
|---|---|
| `external_tools/mock_outputs/` | 6 个 fake/mock 外部工具原始输出 |
| `scripts/normalize_external_tool_mock_evidence.py` | mock evidence normalizer，只使用 Python 标准库 |
| `external_tools/mock_external_tool_evidence_mapping.yaml` | mock output 到 normalized evidence 的映射 |
| `reports/evidence/external_tools/mock_external_tool_normalized_evidence.json` | 归一化后的 mock external tool evidence |
| `reports/evidence/external_tools/mock_external_tool_evidence_index.json` | mock external tool evidence index |

### Mock normalization summary

| 项目 | 状态 |
|---|---|
| Mock output count | 6 |
| Normalized evidence count | 6 |
| Tools represented | garak, PyRIT, AgentDojo, AgentDyn, Browser Automation, API Provider |
| External tool executed | false |
| Real target connected | false |
| Usable for formal finding | false |

### 当前边界

- 当前只是 mock evidence normalization，不代表真实外部工具集成。
- 未安装 garak、PyRIT、AgentDojo、AgentDyn、Playwright 或任何浏览器自动化工具。
- 未运行任何外部工具，未运行任何 `--execute`。
- 未连接真实 API、真实 Agent、真实页面或外部网络。
- 归一化 evidence 来自 fake/mock outputs，不可用于正式 finding。

## 21. System Release Consolidation v1.3

Phase 21 完成系统发布收口，将 Phase 1–20 全部能力整理为 v1.3 release package。

### Release Status

| 项目 | 值 |
|---|---|
| Release version | v1.3 |
| Release package ready | true |
| Module count | 10 |
| Capability group count | 12 |
| Executed local chains | 5（Chatbot、RAG、Agent、Manual UI Replay、Generic Agent Mock Harness） |
| Mock-only chains | 1（External Tool Mock Evidence Normalization） |
| Planning-only adapters | 5（garak、PyRIT、AgentDojo、AgentDyn、Browser Automation） |
| Methodology ready | 4（AI Red Teaming Playbook、Severity Model、Finding Template、Retest Workflow） |
| Governance mapping | 5（AI Asset Inventory、NIST AI RMF、AI/ML-BOM、Supply Chain Mapping、Governance Checklist） |

### 发布文档

详见 `release/` 目录：

- `release/system_release_v1_3.md` — 系统发布说明
- `release/release_manifest_v1_3.yaml` — 发布清单
- `release/module_map_v1_3.md` — 模块关系图（含 Mermaid）
- `release/capability_matrix_v1_3.md` — 按能力分类的详细矩阵
- `release/execution_status_matrix_v1_3.md` — 执行状态分类（executed / mock / planning）
- `release/user_journey_v1_3.md` — 5 条典型使用路径
- `release/operator_quickstart_v1_3.md` — 命令速查与风险等级
- `release/delivery_package_checklist_v1_3.md` — 交付清单
- `release/known_limitations_v1_3.md` — 已知限制
- `release/next_phase_roadmap_v1_3.md` — 后续路线图

### 当前版本说明

**AI Security Assessment & Governance Workbench v1.3+dev** 是一个本地 AI 安全评估与治理工作台，不是认证版本。所有评估结果仅代表本地 sandbox / fake / mock / replay 环境下的表现，不代表真实生产系统安全结论。

## 22. Assessment Plan Generator

Phase 23 新增 Assessment Plan Generator，基于 AI Asset Inventory、Corpus、ATLAS、OWASP LLM、OWASP Agentic、Red Teaming Playbook 自动生成结构化评估计划。

### 生成计划

| 计划 | 资产 | 类型 | 语料数 |
|---|---|---|---|
| `plan_sample_internal_chatbot.yaml` | sample_internal_chatbot | chatbot | 6 个语料文件（22 条） |
| `plan_sample_policy_rag_assistant.yaml` | sample_policy_rag_assistant | rag | 6 个语料文件（22 条） |
| `plan_sample_generic_agent.yaml` | sample_generic_agent | agent | 5 个语料文件（16 条） |
| `plan_sample_fastgpt_workflow_api.yaml` | sample_fastgpt_workflow_api | api/workflow | 3 个语料文件（10 条） |
| `plan_sample_manual_ui_chatbot.yaml` | sample_manual_ui_chatbot | manual_ui_replay | 3 个语料文件（10 条） |

### 计划结构

每个评估计划包含 11 个字段组：Plan Metadata、Target Summary、Framework Mapping（MITRE ATLAS / OWASP LLM / OWASP Agentic / NIST AI RMF / Supply Chain）、Recommended Assessment Scope、Recommended Corpus、Recommended Test Modes、Recommended Runners、Evidence Plan、Finding Plan、Report Plan、Current Limitations。

### 当前边界

- 所有 generated plans 均为 sample，不代表真实评估计划。
- 所有 allowed_now 均为 false — 本阶段不执行测试。
- 所有 real_endpoint 标记为 false — 未连接真实系统。
- 所有 usable_for_formal_finding 标记为 false — 仅用于方法论演示。
- 所有 plans 为 planning_only 状态。
- Generator 使用固定时间戳 2026-01-01T00:00:00Z 避免每次 diff。

## 23. Corpus-to-Testcase Compiler

Phase 24 新增 Corpus-to-Testcase Compiler，将 corpus 中的评估语料自动编译为标准化测试用例和 promptfoo 兼容的测试集草案。

### 编译统计

| 指标 | 数值 |
|---|---|
| 总语料数 | 93 |
| 可编译语料（active/regression） | 65 |
| 已生成测试用例 | 65 |
| Promptfoo 草稿 | 52 |
| 需人工审核 | 0 |
| 覆盖 Profile | chatbot/rag/agent/api/regression |

### 生成状态分布

- generated_draft（本地沙箱，需手动执行）：9
- promptfoo_ready（可直接导入 promptfoo）：52

### Profile 分布

| Profile | 测试用例 | Promptfoo |
|---|---|---|
| chatbot | 14 | ✅ |
| rag | 14 | ✅ |
| agent | 16 | ✅ |
| api | 4（api_provider_future_or_skeleton） | ✅ |
| regression | 9 | ✅ |

### 当前边界

- 所有 generated testcases 声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。
- API 类型测试标记为 api_provider_future_or_skeleton — 需 API provider skeleton 升级后执行。
- Business 类型语料折叠入 chatbot Profile。
- 本阶段不执行测试，不生成 evidence。
- 如需从草稿升级为可执行测试，需人工确认 target、runner、credential。

## 24. Generated Testcase Curation & Runner Binding

Phase 25 新增 Generated Testcase Curation & Runner Binding 层，对 Phase 24 生成的测试草案进行静态分类、runner binding 建议和人工复核流程设计。

### Curation 统计

| 指标 | 数值 |
|---|---|
| 总 generated testcases | 65 |
| curated_candidate | 59 |
| manual_review_required | 6 |
| planned_only | 0 |
| not_executable | 0 |
| Runner binding 草案 | 5 |

### Curation 状态分布

- curated_candidate（通过静态筛选）：59
- manual_review_required（需人工复核）：6

### Runner Binding 草案

| Binding | Profile | Runner | Status |
|---|---|---|---|
| chatbot_generated_binding | chatbot | run_promptfoo.sh --profile chatbot | binding_draft |
| rag_generated_binding | rag | run_rag_promptfoo.sh --profile rag | binding_draft |
| agent_generated_binding | agent | run_agent_promptfoo.sh --profile agent | binding_draft |
| api_generated_binding | api | not_available | planned |
| regression_generated_binding | regression | run_promptfoo.sh --profile chatbot | binding_draft |

### 当前边界

- Curation 是静态分类，不运行任何测试。
- Runner binding 是草案建议，不代表 runner 已验证通过。
- 所有 curation 结果声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。
- 所有 runner binding 中 allowed_now=false。
- 如需升级到可执行测试，需人工确认 target、runner、credential。

## 26. Curated Regression Suite Builder

Phase 26 新增 Curated Regression Suite Builder，经 Phase 27A backfill 后从 59 个 curated_candidate 中构建 7 个回归测试套件草案。

### 构建统计

| 指标 | 数值 |
|---|---|
| 总 suites | 7 |
| 总 selected testcases | 104 |
| 总 excluded | 51 |
| 总 gaps | 1 |
| Promptfoo 草稿 | 104 |

### Suite 清单

| Suite | Suite Type | Selected | Excluded | Gaps |
|---|---|---|---|---|
| suite_core_llm_regression | core_llm | 6 | 19 | 0 |
| suite_chatbot_regression | chatbot | 8 | 17 | 0 |
| suite_rag_regression | rag | 8 | 6 | 0 |
| suite_agent_regression | agent | 10 | 5 | 0 |
| suite_api_regression | api | 1 | 3 | 0 |
| suite_owasp_llm_regression | owasp_llm | 55 | 0 | 0 |
| suite_owasp_agentic_regression | owasp_agentic | 16 | 0 | 1 |

### 已知 Gaps

**OWASP LLM Gaps:** 无 — Phase 27A 已通过多值 risk type 映射覆盖全部 LLM 类别

**OWASP Agentic Gaps:**
- ASI07 (Accountability & Audit): 无 risk type 映射到该类别，需新的 corpus 条目

### 当前边界

- 所有 suite 为 curated_draft 状态，未执行测试。
- 所有 suite 声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。
- Promptfoo suite drafts 声明 generated_only=true、curated_from_static_analysis=true。
- Gaps 表示该 OWASP 类别无适合的 curated_candidate 可选。

## 26.5 Regression Suite Gap Triage

Phase 26.5 对 Phase 26 的 7 个回归测试套件进行静态缺口分析（gap triage），识别 3 个 zero-selected suites 和 8 个 framework gaps 的根因。Phase 27A 已修复全部 3 个 zero-selected suites 和 7 个 framework gaps，剩余 ASI07 需后续 phase 补 corpus 条目。

### Gap Triage 统计

| 指标 | 数值 |
|---|---|
| 总 suites | 7 |
| Zero-selected suites | 0 |
| Framework gaps LLM | 0 |
| Framework gaps Agentic | 1（ASI07） |

### Zero-selected Suites 状态（Phase 27A 已修复）

| Suite | Phase 27A 后状态 | 说明 |
|---|---|---|
| core_llm | 已修复 | 6 selected（curated_candidate 不再全部 manual_review_required） |
| chatbot | 已修复 | 8 selected（fake_assets_required 逻辑修复） |
| api | 已修复 | 1 selected（4 条 API corpus 改为 active + api_provider_future_or_skeleton） |

### Framework Gaps 状态（Phase 27A 已修复）

**LLM Gaps:** 已全部覆盖 — LLM03/04/08 现均有多值 risk type 映射

**Agentic Gaps:**
- ASI07（Accountability & Audit）：无 risk type 映射到该类别，需新的 corpus 条目

### 当前边界

- 所有 gap triage 输出声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。
- Zero-selected suites 是质量门禁结果，不是失败。
- 推荐整体 action：ASI07 需新增 corpus 条目和 risk type 映射。

## 28. Phase 27A Corpus & Curation Backfill

Phase 27A 对 Phase 26.5 识别的 3 个 zero-selected suites 和 8 个 framework gaps 进行静态 backfill（映射/模式/代码修复），不执行任何测试。

### Before / After 对比

| 指标 | Phase 26.5 (Before) | Phase 27A (After) |
|---|---|---|
| Zero-selected suites | 3（core_llm/chatbot/api） | 0 |
| Framework gaps LLM | 3（LLM03/04/08） | 0 |
| Framework gaps Agentic | 5（ASI01/03/05/07/10） | 1（ASI07） |
| Chatbot curated_candidate | 0（全部 manual_review_required） | 19 |
| API generated testcases | 0（全部 planned/not_executable） | 4 |
| Total curated_candidate | 32 | 59 |
| Total manual_review_required | 29 | 6 |
| Regression suite selected | 65 | 104 |

### 三项根因修复

1. **fake_assets_required 空列表判断**（`scripts/curate_generated_testcases.py`）：`bool([])` 在 Python 中返回 `False`，修复为 `is not None` 检查，使无 fake assets 需求的 chatbot 测试用例正确进入 curated_candidate。
2. **API corpus 执行模式**（`corpus/api/`）：将 4 条 API corpus 条目从 `planned`→`active`、`documentation_only`→`api_provider_future_or_skeleton`，使 compiler 可以生成 API 测试用例，curator 可以正确分类。
3. **Risk type 多值映射**（`scripts/build_curated_regression_suites.py`）：将 RISK_TO_OWASP_LLM 和 RISK_TO_OWASP_AGENTIC 从单值映射改为多值映射（`str→list[str]`），使一种风险类型可以映射到多个 OWASP 类别，覆盖之前遗漏的 LLM03/04/08 和 ASI01/03/05/10。

### 涉及文件

- `scripts/curate_generated_testcases.py` — fake_assets_required 逻辑修复 + API profile 排除例外
- `scripts/build_curated_regression_suites.py` — 多值 risk type 映射
- `scripts/analyze_regression_suite_gaps.py` — 同步 gap 列表
- `scripts/compile_corpus_to_testcases.py` — API 生成状态改为 api_provider_future_or_skeleton
- `corpus/api/api_security_baseline.yaml` — asb-001/002 改为 active
- `corpus/api/fastgpt_api_smoke.yaml` — fgs-001 改为 active + LLM07 映射
- `corpus/api/unbounded_consumption_baseline.yaml` — uc_001 schema 修复并改为 active
- `curation/assertion_strategy_mapping.yaml` — 新增 5 个风险类型映射

### 当前边界

- 所有 backfill 为静态修复，不运行测试、不生成 evidence。
- 所有涉及文件声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。
- 剩余 ASI07 缺口仍需后续 phase 补 corpus 条目。

## 27. Regression Suite Dry-Run Validation

Phase 27 对 Phase 26 构建的 7 个回归测试套件及 7 个 promptfoo 草稿进行静态 dry-run 验证，确认套件结构、引用完整性和框架映射的正确性。

### 验证范围

- **套件结构校验**：验证 7 个回归套件的 schema、suite_id、display_name 等元数据字段。
- **测试用例引用校验**：检查 104 条 selected testcases 的 testcase_id 是否在生成用例列表中存在。
- **裁剪引用校验**：验证 curated_candidate 和 manual_review_required 指针的有效性。
- **语料引用校验**：验证 testcase 中关联的 corpus_entry_id 在 corpus 索引中存在。
- **OWASP LLM 映射校验**：确认每个 suite 的 OWASP LLM 覆盖路径完整。
- **OWASP Agentic 映射校验**：确认每个 suite 的 OWASP Agentic 覆盖路径完整（ASI07 gap 已记录并接受）。
- **ATLAS 映射校验**：验证 suite 级别的 ATLAS technique 映射完整性。
- **边界声明校验**：验证所有 suite 和 draft 的 executed、real_target_connected、usable_for_formal_finding 声明均为 false。

### 验证结果

| 指标 | 数值 |
|---|---|
| Suites validated | 7/7 |
| Promptfoo drafts validated | 7/7 |
| Reference integrity | PASS |
| Framework mapping (OWASP LLM) | PASS |
| Framework mapping (OWASP Agentic) | PASS (ASI07 gap documented and accepted) |
| Boundary validation | PASS |
| Tests executed | false |
| Promptfoo executed | false |
| Real systems connected | false |
| Evidence generated | false |

### ASI07 Gap 说明

ASI07（Insecure Inter-Agent Communication）在所有 7 个回归套件和 7 个 promptfoo 草稿中均无覆盖。该缺口已在 Phase 26.5 和 Phase 27A 中记录并接受，当前 Phase 27 静态验证确认该缺口状态不变且所有边界声明均符合预期。

### 涉及文件

- `scripts/validate_regression_suite_dry_run.py` — 验证脚本
- `regression_suites/validation/regression_suite_validation_report.md` — 验证报告

### 当前边界

- Phase 27 是静态 dry-run 验证层：不执行测试、不运行 promptfoo、不连接真实系统、不生成 evidence。
- 验证模式为 static_dry_run_only，所有 executed/promptfoo_executed/real_target_connected/evidence_generated 字段均显式声明为 false。
- ASI07 缺口已记录并接受，不阻止当前套件的验证完成。

## 28. Assertion & Risk Signal Rule Engine

Phase 28 新增 Assertion & Risk Signal Rule Engine，提供基于规则的断言和风险信号映射层，将 testcase 的预期行为声明与真实响应进行规则级别的验证。

### 规则范围

| 规则类型 | 数量 | 说明 |
|---|---|---|
| 风险信号规则 | 24 | mapping + prompt injection + data leakage + RAG poisoning + tool misuse + excessive agency + sensitive disclosure + unbounded consumption + supply chain + misinformation + agent hijack + tool exploitation + privilege abuse + agentic supply chain + code execution + memory poisoning + inter-agent comm + cascading failure + trust exploitation + rogue agents + system prompt leakage + vector weakness + improper output + model denial |
| 预期行为规则 | 15 | should_refuse、must_not_leak_secret、must_not_disclose_system_prompt、must_verify_source、must_not_write_external、must_confirm_destructive_action、must_not_exfiltrate、must_not_follow_hidden_instruction、must_not_escalate_privilege、must_limit_resource_consumption、must_not_execute_untrusted_code、must_not_allow_goal_hijack、must_not_provide_misinformation、must_validate_input_sources、must_not_bypass_safety_filter |
| Severity mapping | 24 | 每条风险信号规则对应一条 severity mapping |
| Manual review rules | 8 | 需人工 review 的规则：supply chain poisoning、agent supply chain、inter-agent communication、trust exploitation、rogue agents、unbounded consumption、vector weakness、model denial |

### OWASP / ATLAS Assertion Coverage

| Framework | 覆盖数量 | 说明 |
|---|---|---|
| OWASP LLM Top 10 | 10 | 10/10 LLM categories have at least one assertion rule |
| OWASP Agentic Top 10 | 10 | 10/10 ASI categories have at least one assertion rule |
| MITRE ATLAS | 21 | 21 ATLAS techniques mapped to assertion rules |

### ASI07 Gap Handling

ASI07 (Insecure Inter-Agent Communication) 在 Phase 26.5、Phase 27A、Phase 27 中被记录为唯一剩余框架缺口。Phase 28 通过新增 `must_validate_input_sources` 和 `must_not_escalate_privilege` 两条预期行为规则覆盖 ASI07 的核心关切。每条规则包含 dedicated assertion strategy、severity mapping 和 risk signal rule，使得 ASI07 在 assertion 规则层得到覆盖。

### 涉及文件

- `rules/risk_signal_rules.yaml` — 24 条风险信号规则定义
- `rules/expected_behavior_rules.yaml` — 15 条预期行为规则定义
- `rules/assertion_coverage_mapping.yaml` — OWASP/ATLAS assertion 覆盖映射
- `rules/severity_mapping.yaml` — 24 条 severity mapping
- `rules/rule_coverage_report.md` — 规则覆盖报告
- `rules/manual_review_rules.yaml` — 需人工 review 的规则清单
- `rules/README.md` — 规则引擎说明

### 当前边界

- Phase 28 是静态规则层：不执行测试、不运行 promptfoo、不连接真实系统、不生成 evidence。
- 所有 rule 为声明式定义（rules/ 目录中的 YAML 文件），未嵌入任何 test runner 或执行管线。
- Rule validation 报告基于静态规则检查（schema/coverage/consistency），不包含动态运行结果。
- Assertion coverage 为映射层覆盖，不代表测试执行覆盖。
- 规则目录 rules/ 独立于 test runner、corpus、curation 和 regression suite 体系。

## 29. Formal Report Package Builder

Phase 30 新增 Formal Report Package Builder，提供将当前系统已有的 assessment plan、dashboard、report、evidence index、sample findings、risk register、governance appendix、supply chain appendix、external tool appendix 组织成 sample enterprise assessment delivery package 的能力。

### 关键文件

| 文件 | 用途 |
|---|---|
| `delivery_packages/delivery_package_schema.md` | Delivery package schema 定义 |
| `delivery_packages/package_generation_boundary.md` | Package generation boundary 说明 |
| `scripts/build_formal_report_package.py` | Package builder 脚本 |
| `delivery_packages/sample_enterprise_assessment_package/package_manifest.yaml` | Sample package manifest |

### Sample Package 内容

| Section | 文件 |
|---|---|
| Executive Summary | `executive_summary.md` |
| Assessment Scope | `assessment_scope.md` |
| Methodology | `methodology.md` |
| Asset Inventory Summary | `asset_inventory_summary.md` |
| Test Coverage Summary | `test_coverage_summary.md` |
| Finding Summary | `finding_summary.md` |
| Risk Register Export (YAML) | `risk_register_export.yaml` |
| Mitigation Roadmap | `mitigation_roadmap.md` |
| Retest Plan | `retest_plan.md` |
| Governance Appendix | `governance_appendix.md` |
| Supply Chain Appendix | `supply_chain_appendix.md` |
| External Tool Appendix | `external_tool_appendix.md` |
| Limitations | `limitations.md` |

### Current Status

- **Package ID**: PACKAGE-2026-001
- **Package type**: sample_delivery_package
- **Package sections**: 13
- **Sample findings**: 6
- **Risk register entries**: 6
- **real_customer**: false
- **real_target_validated**: false
- **formal_report**: false
- **usable_for_customer_delivery**: false

### 当前边界

- Phase 30 是 sample delivery package 构建层。
- 所有 package 内容为 sample/mock，不包含真实客户信息。
- 不运行测试、不运行 promptfoo、不连接真实系统、不生成真实 evidence。
- Sample package 不可用于客户交付。
- 正式客户报告需要 RoE、真实系统访问、真实执行 evidence、人工复核和客户验收。

## 30. Generic API Provider Formalization

Phase 31 新增 Generic API Provider Formalization，将 API Provider 从早期 skeleton 规范化为可配置、可审计、可 dry-run 的 provider 层。新增以下目录和文件：

### api_provider/ 目录结构

- `api_provider/api_provider_schema.md` — Provider 通用 Schema（6 种 provider type）
- `api_provider/target_profile_schema.md` — Target Profile Schema（5 种 environment type）
- `api_provider/provider_config_template.local.example.yaml` — Config Template（placeholder only）
- `api_provider/request_response_normalization_schema.md` — Request/Response Normalization Schema（6 条 redaction rules）
- `api_provider/provider_safety_guardrails.md` — Safety Guardrails（G01-G16，3 层）
- `api_provider/provider_execution_boundary.md` — Execution Boundary

### sample_targets/（5 个 sample target）

- `openai_compatible_chat_sample.yaml` — OpenAI Compatible Chat
- `rag_qa_api_sample.yaml` — RAG QA API
- `agent_api_sample.yaml` — Agent API
- `workflow_api_sample.yaml` — Workflow API
- `fastgpt_compatible_sample.yaml` — FastGPT Compatible API

### Scripts

- `scripts/api_provider_dry_run_simulator.py` — Dry-run simulator（5 targets，6 simulated ops）
- `scripts/validate_api_provider_formalization.py` — Validation script（15 checks，all passed）

### Key Principles

- 所有 sample target 声明 real_target=false、dry_run_only=true、execution_allowed=false、usable_for_real_test=false
- Simulator 不发起网络请求、不读取真实凭证、不访问 endpoint
- 所有 validation checks passed（15/15）
- Validation result：network_called=false、credentials_loaded=false、real_target_connected=false、tests_executed=false、evidence_generated=false、usable_for_formal_finding=false
- 未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试

## 30.5 Authorized Test Target Onboarding

Phase 31B 新增 Authorized Test Target Onboarding，构建授权评估目标接入层，确保所有 API 测试 target 在接入前经过结构化授权和安全检查。

### onboarding/ 目录结构

- `api_provider/onboarding/README.md` — Onboarding 目录概览
- `api_provider/onboarding/authorized_target_onboarding_schema.md` — 授权 Target Onboarding Schema
- `api_provider/onboarding/target_intake_template.yaml` — Target 接入登记模板（placeholder only）
- `api_provider/onboarding/roe_checklist.md` — Rules of Engagement 检查清单
- `api_provider/onboarding/credential_isolation_policy.md` — 凭证隔离策略
- `api_provider/onboarding/test_scope_definition_template.yaml` — 测试范围定义模板
- `api_provider/onboarding/allowed_prohibited_operations_matrix.yaml` — 允许/禁止操作矩阵
- `api_provider/onboarding/rate_limit_and_safety_window_policy.md` — 速率限制与安全窗口策略
- `api_provider/onboarding/approval_gate_checklist.md` — 审批门检查清单

### Scripts

- `scripts/validate_authorized_target_onboarding.py` — Validation script（18 checks，all passed）

### Key Principles

- 所有 target 声明 authorization_required=true、approval_status=not_approved、execution_allowed=false
- Onboarding validation 不发起网络请求、不读取真实凭证、不访问 endpoint
- 所有 validation checks passed（18/18）
- authorization_required=true、approval_status=not_approved、execution_allowed=false、credentials_loaded=false、real_target_connected=false、production_target_allowed=false
- 未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试

## 30.7 Local Mock API Execution Harness

Phase 31C 新增 Local Mock API Execution Harness，构建本地 mock API 执行层，用于在不连接真实 API 的情况下模拟 API 请求/响应流程。

### 核心文件

| 文件 | 用途 |
|---|---|
| `api_provider/mock_harness/README.md` | Mock Harness 目录概览 |
| `api_provider/mock_harness/mock_api_target_schema.md` | Mock API Target Schema |
| `api_provider/mock_harness/mock_request_fixtures.yaml` | 8 个 mock request fixtures |
| `api_provider/mock_harness/mock_response_fixtures.yaml` | 8 个 mock response fixtures（含 risk signal 响应） |
| `api_provider/mock_harness/mock_execution_trace.yaml` | Mock execution trace（8 个操作） |
| `api_provider/mock_harness/mock_normalized_response_samples.yaml` | 8 个 normalized response samples |
| `api_provider/mock_harness/mock_execution_boundary.md` | Mock execution boundary |
| `api_provider/mock_harness/mock_harness_validation_result.yaml` | Validation result（21/21 passed） |
| `api_provider/mock_harness/mock_harness_validation_report.md` | Validation report |

### Scripts

- `scripts/run_local_mock_api_harness.py` — Mock harness runner（pair_fixtures、normalize_response、build_execution_trace 函数）
- `scripts/validate_local_mock_api_harness.py` — Validation script（21 checks）

### 模拟覆盖

- **Request fixtures**: 8（覆盖 5 种 provider 类型：openai_compatible_chat、rag_qa_api、agent_api、workflow_api、fastgpt_compatible）
- **Response fixtures**: 8（含 risk signal 响应）
- **Execution trace**: 8 个操作
- **Normalized samples**: 8

### 边界声明

- mock_execution: true
- external_network_called: false
- credentials_loaded: false
- real_target_connected: false
- evidence_generated: false
- usable_for_formal_finding: false

Phase 31C 是本地 mock API 执行层：api_provider/mock_harness/ 目录结构、mock API target schema、mock request/response fixtures（8 请求/8 响应，覆盖 5 种 provider 类型）、mock execution trace、mock normalized response samples、mock execution boundary、run/validate 脚本。所有输出声明 mock_execution=true、external_network_called=false、credentials_loaded=false、real_target_connected=false、evidence_generated=false、usable_for_formal_finding=false。Mock harness 只使用本地 fixture，不发起网络请求、不读取真实凭证、不访问真实 endpoint。

## 30.8 Limited Authorized API Dry-Run Plan

Phase 31D 新增 Limited Authorized API Dry-Run Plan，构建有限授权 API 干运行计划定义层，用于在不连接真实 API、不加载真实凭证、不发起网络请求的前提下，定义授权干运行的完整计划和边界条件。

### 核心文件

| 文件 | 用途 |
|---|---|
| `authorized_dry_run_plan/README.md` | Plan 目录概览 |
| `authorized_dry_run_plan/dry_run_plan_schema.md` | Dry-run plan schema |
| `authorized_dry_run_plan/rate_limit_and_request_budget_policy.md` | 速率限制与请求预算策略 |
| `authorized_dry_run_plan/rollback_and_stop_conditions_plan.md` | 回滚与停止条件计划 |
| `authorized_dry_run_plan/human_approval_gate_checklist.md` | 人工审批门检查清单 |
| `authorized_dry_run_plan/allowed_test_bundle_definition.md` | 允许的测试包定义 |
| `authorized_dry_run_plan/preflight_readiness_checklist.md` | 预飞检查清单 |
| `authorized_dry_run_plan/credential_isolation_checklist.md` | 凭证隔离检查清单 |
| `authorized_dry_run_plan/plan_validation_result.yaml` | Validation result |
| `authorized_dry_run_plan/plan_validation_report.md` | Validation report |

### Scripts

- `scripts/validate_authorized_dry_run_plan.py` — Validation script（19 checks）

### 边界声明

- dry_run_plan_ready: true
- authorization_required: true
- approval_status: not_approved
- execution_allowed: false
- credentials_loaded: false
- real_target_connected: false
- network_called: false
- evidence_generated: false
- production_target_allowed: false
- dry_run_plan_only: true
- plan_files: 11
- validation_checks: 19
- validation_passed: 0
- preflight_items: 20
- readiness_checks: 10
- credential_checks: 14
- allowed_bundles: 4
- stop_conditions: 10
- rollback_steps: 18

Phase 31D 是有限授权 API 干运行计划定义层：authorized_dry_run_plan/ 目录结构、dry_run_plan schema、rate limit and request budget policy、rollback and stop conditions plan、human approval gate checklist、allowed test bundle definition、preflight readiness checklist、credential isolation checklist、validation script（19 checks）。所有计划文件声明 placeholder markers only、no real URLs、no real tokens、no real credentials、no real emails、no real API keys、no network calls。未连接真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求。

## 30.9 Single Authorized API Smoke Test Design

Phase 31E 新增 Single Authorized API Smoke Test Design，构建单次授权 API 冒烟测试设计层，用于在不连接真实 API、不加载真实凭证、不发起网络请求、不使用对抗性提示的前提下，定义单次授权 API 冒烟测试的完整设计规范和静态安全边界。

### 核心文件

| 文件 | 用途 |
|---|---|
| `api_provider/single_smoke_test_design/README.md` | Smoke test design 目录概览 |
| `api_provider/single_smoke_test_design/single_smoke_test_schema.md` | Single smoke test schema |
| `api_provider/single_smoke_test_design/candidate_target_template.yaml` | Candidate target template（placeholder only） |
| `api_provider/single_smoke_test_design/minimal_request_bundle.yaml` | Minimal request bundle（4 requests） |
| `api_provider/single_smoke_test_design/expected_safe_response_contract.md` | Expected safe response contract |
| `api_provider/single_smoke_test_design/execution_preflight_gate.yaml` | Execution preflight gate（12 checks） |
| `api_provider/single_smoke_test_design/abort_condition_checklist.md` | 13 abort conditions |
| `api_provider/single_smoke_test_design/operator_runbook_template.md` | Operator runbook template |
| `api_provider/single_smoke_test_design/evidence_placeholder_schema.md` | Evidence placeholder schema |
| `api_provider/single_smoke_test_design/smoke_test_design_validation_result.yaml` | Validation result |
| `api_provider/single_smoke_test_design/smoke_test_design_validation_report.md` | Validation report |

### Scripts

- `scripts/validate_single_authorized_api_smoke_test_design.py` — Validation script（20 checks）

### 边界声明

- smoke_test_design_ready: true
- only_one_target_allowed: true
- read_only_operations_only: true
- approval_status: not_approved
- execution_allowed: false
- credentials_loaded: false
- real_target_connected: false
- network_called: false
- evidence_generated: false
- production_target_allowed: false
- smoke_test_design_only: true
- design_files: 11
- validation_checks: 20
- validation_passed: 0
- minimal_requests: 4
- preflight_checks: 12
- abort_conditions: 13

Phase 31E 是单次授权 API 冒烟测试设计层：api_provider/single_smoke_test_design/ 目录结构、single smoke test schema、candidate target template、minimal request bundle、expected safe response contract、execution preflight gate、abort condition checklist、operator runbook template、evidence placeholder schema、validation script（20 checks）。所有设计文件声明 smoke_test_design_ready=true、only_one_target_allowed=true、read_only_operations_only=true、approval_status=not_approved、execution_allowed=false、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false。未使用真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求、未使用对抗性提示。validation script 不访问网络、不读取真实凭证。

## 30.10 Single Smoke Test Approval Packet

Phase 31F 新增 Single Smoke Test Approval Packet & Go/No-Go Gate，构建单次冒烟测试审批包与执行/不执行门禁层，用于在不连接真实 API、不加载真实凭证、不发起网络请求、不使用对抗性提示的前提下，定义单次冒烟测试的完整审批包和门禁条件。

### 核心文件

| 文件 | 用途 |
|---|---|
| `api_provider/smoke_test_approval_packet/README.md` | Approval packet 目录概览 |
| `api_provider/smoke_test_approval_packet/approval_packet_schema.md` | Approval packet schema |
| `api_provider/smoke_test_approval_packet/go_no_go_gate_checklist.md` | Go/No-Go 门禁检查清单 |
| `api_provider/smoke_test_approval_packet/risk_acceptance_form.md` | 风险接受表格 |
| `api_provider/smoke_test_approval_packet/operator_signoff_template.md` | 操作员签署模板 |
| `api_provider/smoke_test_approval_packet/credential_readiness_verification.md` | 凭证就绪验证 |
| `api_provider/smoke_test_approval_packet/real_target_connection_verification.md` | 真实目标连接验证 |
| `api_provider/smoke_test_approval_packet/rollback_plan_template.md` | 回滚计划模板 |
| `api_provider/smoke_test_approval_packet/communication_plan_template.md` | 沟通计划模板 |
| `api_provider/smoke_test_approval_packet/approval_packet_validation_result.yaml` | Validation result |

### Scripts

- `scripts/validate_smoke_test_approval_packet.py` — Validation script（20 checks）

### 边界声明

- approval_packet_ready: true
- approval_status: not_approved
- go_no_go_status: no_go
- execution_allowed: false
- human_approval_required: true
- operator_signoff_required: true
- risk_acceptance_required: true
- credentials_loaded: false
- real_target_connected: false
- network_called: false
- evidence_generated: false
- production_target_allowed: false
- execution_hold: true
- design_files: 10
- validation_checks: 20
- validation_passed: 0

Phase 31F 是单次冒烟测试审批包与执行/不执行门禁层：api_provider/smoke_test_approval_packet/ 目录结构、10 个设计文件、approval packet schema、go/no-go gate checklist、risk acceptance form、operator signoff template、credential readiness verification、real target connection verification、rollback plan template、communication plan template、approval packet validation script（20 checks）。所有审批文件声明 approval_packet_ready=true、approval_status=not_approved、go_no_go_status=no_go、execution_allowed=false、human_approval_required=true、operator_signoff_required=true、risk_acceptance_required=true、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false、production_target_allowed=false、execution_hold=true。未使用真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求、未使用对抗性提示。validation script 不访问网络、不读取真实凭证。

## 30.11 Full Authorized API Regression Execution & Chinese Report & Finding Triage

Phase 32C 新增 Full Authorized API Regression Execution，执行全量回归测试，生成 evidence 和 finding candidates。
Phase 32D 新增 Real API Regression Assessment Report Builder，基于 Phase 32C 结果构建完整评估报告包（10 份文件）。
Phase 32D.1 新增 Chinese Report Localization，保留英文报告为 _en.md，中文报告为默认 .md，生成 report_language_index.md 双语索引。
Phase 32E 新增 Finding Triage & Report Hardening，生成 finding_triage/ 发现研判材料（16 候选→5 组）和 final_hardened/ 最终汇报版材料（管理层简报、最终执行摘要、发现摘要、修复行动计划、复测计划）。

## 30.12 Remediation & Retest Package Builder

Phase 33 新增 Remediation & Retest Package Builder，基于 Phase 32C/32D/32E 结果生成整改包和复测包。

### remediation_packages/ 结构

- 5 个整改包（system_prompt_leakage、sensitive_information_disclosure、rag_knowledge_boundary、prompt_injection_bypass、api_boundary_authorization）
- remediation_task_board：10 个任务（4 P0 + 3 P1 + 3 P2）
- remediation_package_schema.md：20 字段的模式定义
- remediation_package_index.yaml：5 包索引
- build_remediation_retest_packages.py：构建脚本
- validate_remediation_retest_packages.py：验证脚本（87 项检查）

## 30.13 DeepSeek Judge Provider Framework

Phase 34A 新增 DeepSeek Judge Provider Framework，构建 DeepSeek 判官提供者框架。

### tool_judge_providers/ 结构

- judge_provider_schema.md：判官提供者通用模式（11 个顶层字段、21 个判官结果字段、8 个用途）
- judge_provider_index.yaml：提供者索引（JPD-001 deepseek，8 个用途）
- judge_provider_boundary.md：安全边界（13 条约束）

### deepseek/ 子目录

- deepseek_judge_provider.template.yaml：提供者模板（占位符）
- deepseek_judge_prompt_templates.yaml：判官提示模板（8 个用途）
- deepseek_judge_schema.yaml：DeepSeek 专属模式（扩展公共模式，6 个 DeepSeek 专属字段）
- deepseek_judge_mock_results.yaml：模拟判官结果（8 个结果）
- deepseek_judge_boundary.md：DeepSeek 安全边界

### mock_outputs/ 子目录

- finding_candidate_judge_results.yaml：16 个候选发现判官结果（5 个合并组）
- consolidated_group_judge_results.yaml：5 个合并组聚合判官结果
- judge_summary.md：判官摘要（含覆盖率和限制说明）

### adapter/ 子目录

- deepseek_judge_adapter.py：适配器骨架（11 个桩方法）
- build_deepseek_judge_provider.py：构建脚本
- validate_deepseek_judge_provider.py：验证脚本（9 个章节）

## 30.14 DeepSeek Judge Go/No-Go Packet

Phase 34B 新增 DeepSeek Judge Go/No-Go Packet，为真实调用 DeepSeek API 建立执行/不执行审批门禁。

### go_no_go/ 结构

- deepseek_judge_go_no_go_packet.md：Go/No-Go 审批包（目的、范围、默认不执行声明、Go/No-Go 条件）
- deepseek_judge_approval_checklist.md：18 项审批清单（API/凭证/调用限制/范围/输出/成本/回滚）
- deepseek_judge_cost_budget.yaml：成本预算（max_judge_calls=16、hard_stop_on_budget_exceeded=true、budget_not_approved）
- deepseek_judge_execution_plan.yaml：5 阶段执行计划（凭证验证→干运行→有限调用→全量调用→结果评审）
- deepseek_judge_safety_boundary.md：安全边界（允许/禁止操作、凭证保护、输出安全、事件响应）
- deepseek_judge_rollback_plan.md：5 步回滚计划（立即停止→凭证保护→结果作废→配置重置→验证）
- deepseek_judge_result_acceptance_criteria.md：10 项验收标准（所有结果保持 assistant_review、needs_human_review、usable_for_formal_finding=false）
- deepseek_judge_local_config_template.md：本地配置模板说明（仅占位符，不创建真实 .local 文件）
- validate_deepseek_judge_go_no_go.py：验证脚本（6 个章节、18+ 项检查）

**状态**：所有文件 approval_status=not_approved、execution_allowed=false、network_allowed=false、credential_loaded=false。未调用 DeepSeek API、未读取凭证、未连接被测 API。

### retest_packages/ 结构

- 5 个复测包（RT-SPL-001 到 RT-ABA-005）
- retest_execution_plan.md：三阶段执行计划（P0 → P1 → 全量回归）
- retest_acceptance_criteria.md：按组和全量回归验收标准
- retest_before_after_comparison_template.md：修复前后对比模板

### 安全状态

- 所有整改状态：remediation_planned
- 所有复测状态：retest_not_executed
- real_api_execution_allowed=false
- 不重新运行测试、不连接 API、不读取凭证

### 执行范围

- 仅测试已授权的 test API，不针对生产环境。
- 所有请求/响应经过脱敏处理（redaction_applied=true）。
- API key 和 authorization header 不记录（api_key_logged=false、authorization_header_logged=false）。
- Provider type：fastgpt_compatible

### 重要声明

- **仅测试已授权的 test API，不针对生产环境。**
- **所有 finding 为 candidate 状态，需人工审核后方可成为正式 finding。**
- **未生成正式客户报告。**
- 执行模式：full_authorized_api_regression
- target_environment：test

## 30.15 Controlled DeepSeek Judge Execution

Phase 34C 执行受控的 DeepSeek 真实 API 判官调用，评估 16 个现有候选发现和 5 个合并组。

### 执行概述

- DeepSeek API 调用次数：21 次（1 smoke + 15 batch + 5 合并组评审）
- 评估候选发现：16 个（1 smoke + 15 batch，来自 Phase 32C 结果）
- 评估合并组：5 个（system_prompt_leakage、sensitive_disclosure、rag_exposure、prompt_injection_bypass、api_boundary_weakness）
- 零错误，成本约 $0.01

### 执行产物

- smoke_judge_result.json：首次调试验证结果
- batch_judge_results.json：15 个候选发现批量判官结果
- consolidated_group_judge_results.json：5 个合并组评审结果
- execution_summary.json：执行摘要（调用次数、成本、安全标志）
- validation_input.json：验证输入（20 项检查）

### 安全边界

- 不调用目标 API（allow_target_api_call=false）
- 不生成新测试（allow_new_test_generation=false）
- 所有输出：usable_for_formal_finding=false、manual_review_required=true、formal_finding=false、customer_report_ready=false
- 验证脚本 10 项检查全部通过

### 重要声明

- **DeepSeek API 已调用，但所有判官结果保持 candidate 状态。**
- **所有结果需要人工审核后方可用于任何决策。**
- **未生成正式发现、未生成正式客户报告。**
- 判官模型：deepseek-v4-flash
- 模型供应商：DeepSeek
- 执行模式：real_judge

## 30.16 DeepSeek Judge Result Integration & Review Report

Phase 34D 对 Phase 34C/34C.0/34C.1 的结果进行静态整合，生成判官评审摘要和人工审核交接文档。

### 执行概览

- 来源阶段：phase34c_controlled_deepseek_judge_execution
- 方法：静态整合（不重新调用 DeepSeek API、不读取 .local/、不连接被测 API）
- 总 API 调用：21 次（1 smoke + 15 batch + 5 合并组）
- 总 Token 数：11,711
- 预估成本：$0.0097
- 调用真实性核验：probable_real_call
- 需要人工核验账单：是
- 候选发现已评审：15 个
- 合并组已评审：5 个

### 预算核验

| 预算字段 | 最大值 | 实际值 |
|---|---|---|
| 候选判官调用 | 16 | 15 |
| 合并组判官调用 | 5 | 5 |
| Smoke 调用 | 1 | 1 |
| DeepSeek API 总调用 | 22 | 21 |

### 安全边界

- 已遵守预算约束：actual_total=21 ≤ max_total=22
- 不重新调用 DeepSeek API
- 不读取 .local/
- 不连接被测 API
- 不重新运行测试
- 不改变 finding candidate 状态
- 不生成 formal finding
- 所有判官结果保持 candidate 状态
- 所有输出标记 usable_for_formal_finding=false、manual_review_required=true、formal_finding=false

### 重要声明

- **Phase 34D 是结果整合与报告更新层，不是测试执行层。**
- **所有判官结果需要人工审核后方可用于任何决策。**
- **未生成正式发现、未生成正式客户报告。**
- **调用真实性为 probable_real_call（需人工核验账单后方可确认）。**

## 30.17 Promptfoo Integration Framework

Phase 35 搭建 promptfoo 接入框架，将已有 promptfoo drafts / regression suites 纳入统一的工具结果处理链路。

### 执行概览

- 框架目录：tool_integrations/promptfoo/
- 索引 profile：12 个（5 generated + 7 regression）
- 结果 schema：已定义（promptfoo_result_schema.yaml）
- Mock 结果：已生成（promptfoo_mock_results.yaml）
- Evidence 映射：已定义（promptfoo_evidence_mapping.yaml）
- Finding candidate 映射：已定义（promptfoo_finding_candidate_mapping.yaml）
- DeepSeek judge handoff schema：已定义（promptfoo_deepseek_judge_handoff.yaml）
- Adapter skeleton：已创建（adapter/promptfoo_adapter.py）
- 构建脚本：scripts/build_promptfoo_integration_framework.py
- 验证脚本：scripts/validate_promptfoo_integration_framework.py
- 验证结果：81 passed, 0 failed

### 安全边界

- 不安装或运行 promptfoo CLI
- 不连接任何真实目标（chatbot / RAG / agent / API endpoint）
- 不执行 promptfoo eval
- 不输出真实评估结果
- 所有 execution_mode = mock / dry_run
- 所有 real_target_connected = false
- 所有 usable_for_formal_finding = false
- 真实执行函数 stub 均 raise NotImplementedError

### 重要声明

- **Phase 35 是 schema/config/mock/adapter 层，不是测试执行层。**
- **所有 promptfoo 输出只能进入 evidence_candidate / finding_candidate / judge_handoff 管道。**
- **所有结果保持 candidate 状态，需要人工 Go/No-Go 后才能升级。**
- **未安装 promptfoo CLI、未连接目标 API、未调用 DeepSeek API、未读取 .local/。**

## 30.18 Promptfoo Go/No-Go Packet

Phase 35B 为后续受控执行 promptfoo 建立 Go/No-Go 审批包。

### 执行概览

- 框架目录：tool_integrations/promptfoo/go_no_go/
- 包文件数：9 个
- 审批状态：not_approved
- 执行允许：false
- 验证结果：58 passed, 0 failed
- 验证脚本：scripts/validate_promptfoo_go_no_go.py

### 安全边界

- 不运行 promptfoo eval
- 不连接被测 API
- 不调用 DeepSeek API
- 不读取 .local/
- 所有 approval_status=not_approved
- 所有 execution_allowed=false
- 所有 network_allowed=false
- 所有 promptfoo_eval_allowed=false
- 所有 target_api_call_allowed=false
- 所有 deepseek_judge_allowed=false
- 所有 credential_loaded=false
- human_go_no_go_required=true

### 重要声明

- **Phase 35B 是审批包层，不是测试执行层。**
- **所有文件为审批/占位内容，不运行 promptfoo eval、不连接被测 API、不调用 DeepSeek API、不读取 .local/**
- **需要人工 Go/No-Go 批准后才能执行任何真实操作。**
- **未生成新测试用例、未修改原始 finding candidates、未生成 formal finding。**

## 30.19 Promptfoo Execution Readiness Gate

Phase 35C.0 为 promptfoo 受控执行建立执行前安全闸门。

### 执行概览

- 框架目录：tool_integrations/promptfoo/readiness/
- 闸门文件数：1 个
- 闸门状态：pass（94 checks passed）
- 验证脚本：scripts/validate_promptfoo_readiness_gate.py

### 验证范围

- Secret Isolation：检查 promptfoo 配置文件中无明文 secret
- API Isolation：检查无未脱敏 endpoint
- Network Safety：检查 network_allowed=false
- Command Safety：检查无默认 promptfoo eval 调用
- Adapter Safety：检查 adapter 有 NotImplementedError 保护

### 安全边界

- 不运行 promptfoo eval
- 不连接被测 API
- 不调用 DeepSeek API
- 不读取 .local/
- 不加载真实凭证
- 不生成 formal finding
- readiness_gate_verification_only=true
- static_analysis_only=true

### 重要声明

- **Phase 35C.0 是执行前安全闸门层，不是测试执行层。**
- **本阶段只做静态检查、配置隔离检查和文档化执行闸门，不实际执行 promptfoo。**
- **本阶段不验证被测 API 的真实行为。**
- **本阶段不产生 formal finding。**
- **本阶段只判断"是否具备进入后续受控执行阶段的前置条件"。**
- **本阶段不替换 Phase 35B Go/No-Go 审批。后续阶段即使运行 promptfoo，也只能产出 finding candidates / assistant_review / needs_human_review。**

## 31. Finding Generator Prototype

Phase 29 新增 Finding Generator Prototype，提供基于 sample/mock evidence 和 rule 映射的 sample/mock finding draft 生成能力。

### 关键文件

| 文件 | 用途 |
|---|---|
| `findings/finding_schema.md` | 32 字段 finding schema 定义 |
| `scripts/generate_finding_drafts.py` | Finding draft 生成器脚本 |
| `findings/finding_generation_boundary.md` | Finding 生成边界声明 |
| `findings/finding_index.yaml` | 9 维度 finding 索引 |
| `findings/finding_to_risk_register_mapping.yaml` | Finding 到风险登记册映射 |
| `findings/finding_to_mitigation_retest_mapping.yaml` | Finding 到修复/复测映射 |

### Generated Sample Findings

| ID | Title | Type | Severity | Profile |
|---|---|---|---|---|
| FD-2026-SAMPLE-001 | Prompt Injection Sample Finding | sample_draft | High | chatbot |
| FD-2026-SAMPLE-002 | Sensitive Disclosure Sample Finding | sample_draft | High | chatbot |
| FD-2026-SAMPLE-003 | System Prompt Leakage Sample Finding | sample_draft | Medium | chatbot |
| FD-2026-SAMPLE-004 | Agent Tool Misuse Sample Finding | mock_draft | High | agent |
| FD-2026-SAMPLE-005 | RAG Poisoning Sample Finding | mock_draft | High | rag |
| FD-2026-SAMPLE-006 | Accountability Audit Gap Sample Finding | governance_gap | Medium | agent |

### 当前边界

- Phase 29 是 sample/mock finding draft 生成层。
- 所有 finding 声明 real_target_validated=false、usable_for_formal_report=false。
- 不运行测试、不运行 promptfoo、不连接真实系统、不生成真实 evidence。
- 所有 finding 需要人工复核才能用于任何决策。
- Sample finding 不替代人工安全评估。

## 32. 限制说明

- 本报告只反映本地 sandbox、fake documents、fake tools 和已生成 evidence 的结果。
- API Provider Skeleton dry-run evidence 不代表真实 API tested / passed。
- 本报告不代表真实企业系统、真实模型 API、真实知识库或真实 Agent 工具链的安全结论。
- 本报告不包含真实凭证、真实企业信息或未脱敏日志。
- AI Asset Inventory 使用 sample/fake 资产，不代表任何真实系统。
- NIST AI RMF Mapping 是治理映射层，不代表已完成 NIST 合规认证。
- AI/ML-BOM 使用 sample/fake 数据，不代表任何真实系统的组件依赖。
- External Evaluation Tool Adapter Planning、External Tool Mock Evidence Normalization 是规划/设计层，不代表任何外部工具已安装或已执行。
- System Release Consolidation v1.3 是发布收口层，不改变评估结果本身。
- Phase 27A Corpus & Curation Backfill 是静态 backfill 层，不运行测试、不连接真实系统、不生成 evidence。
- Phase 28 Assertion & Risk Signal Rule Engine 是静态规则层：不执行测试、不运行 promptfoo、不连接真实系统、不生成 evidence。规则目录 rules/。
- Phase 29 Finding Generator Prototype 是 sample/mock finding draft 生成层：不执行测试、不运行 promptfoo、不连接真实系统、不生成真实 evidence、不生成真实 finding。所有 finding 声明 real_target_validated=false、usable_for_formal_report=false。目录 findings/。
- Phase 30 Formal Report Package Builder 是 sample delivery package 构建层：将已有 sample/mock 评估产物组织为 sample enterprise assessment delivery package。不执行测试、不运行 promptfoo、不连接真实系统、不生成真实 evidence、不生成真实 finding。所有 package 内容声明 real_customer=false、real_target_validated=false、formal_report=false、usable_for_customer_delivery=false。目录 delivery_packages/。
- Phase 31 Generic API Provider Formalization 是 API Provider 规范化层：api_provider schema formalization、provider type classification、target profile schema、config template、normalization schema、safety guardrails、execution boundary、dry-run simulation、validation checks。不连接真实 API、不读取真实凭证、不访问真实 endpoint、不执行真实安全测试。所有 sample target 声明 dry_run_only=true。
- Phase 31B Authorized Test Target Onboarding 是授权评估目标接入层：onboarding/ 目录结构、authorized target onboarding schema、RoE checklist、credential isolation policy、test scope definition template、allowed/prohibited operations matrix、rate limit and safety window policy、approval gate checklist。所有 target 声明 authorization_required=true、approval_status=not_approved、execution_allowed=false、real_target_connected=false、credentials_loaded=false、production_target_allowed=false。不连接真实 API、不读取真实凭证、不访问真实 endpoint、不执行真实安全测试。
- Phase 31C Local Mock API Execution Harness 是本地 mock 执行层：api_provider/mock_harness/ 目录结构、mock API target schema、mock request/response fixtures（8 请求/8 响应，覆盖 5 种 provider 类型）、mock execution trace、mock normalized response samples、mock execution boundary、run/validate 脚本。所有输出声明 mock_execution=true、external_network_called=false、credentials_loaded=false、real_target_connected=false、evidence_generated=false、usable_for_formal_finding=false。Mock harness 只使用本地 fixture，不发起网络请求、不读取真实凭证、不访问真实 endpoint。
- Phase 31D Limited Authorized API Dry-Run Plan 是有限授权 API 干运行计划定义层：authorized_dry_run_plan/ 目录结构、dry_run_plan schema、rate limit and request budget policy、rollback and stop conditions plan、human approval gate checklist、allowed test bundle definition、preflight readiness checklist、credential isolation checklist、validation script（19 checks）。所有计划文件只包含 placeholder markers、no real URLs、no real tokens、no real credentials、no real emails、no real API keys、no network calls。未连接真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求。validation script 不访问网络、不读取真实凭证。
- Phase 31E Single Authorized API Smoke Test Design 是单次授权 API 冒烟测试设计层：api_provider/single_smoke_test_design/ 目录结构、single smoke test schema、candidate target template、minimal request bundle、expected safe response contract、execution preflight gate、abort condition checklist、operator runbook template、evidence placeholder schema、validation script（20 checks）。所有设计文件声明 smoke_test_design_ready=true、only_one_target_allowed=true、read_only_operations_only=true、approval_status=not_approved、execution_allowed=false、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false。未使用真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求、未使用对抗性提示。validation script 不访问网络、不读取真实凭证。
- Phase 31F Single Smoke Test Approval Packet & Go/No-Go Gate 是单次冒烟测试审批包与执行/不执行门禁层：api_provider/smoke_test_approval_packet/ 目录结构、10 个设计文件、approval packet schema、go/no-go gate checklist、risk acceptance form、operator signoff template、credential readiness verification、real target connection verification、rollback plan template、communication plan template、approval packet validation script（20 checks）。所有审批文件声明 approval_packet_ready=true、approval_status=not_approved、go_no_go_status=no_go、execution_allowed=false、human_approval_required=true、operator_signoff_required=true、risk_acceptance_required=true、credentials_loaded=false、real_target_connected=false、network_called=false、evidence_generated=false、production_target_allowed=false、execution_hold=true。未使用真实 API、未读取真实凭证、未访问真实 endpoint、不发起任何网络请求、未使用对抗性提示。validation script 不访问网络、不读取真实凭证。
- 如需评估非本地目标，必须先完成 `docs/non_local_target_approval_checklist.md`。

## 33. 附录

| 文件 | 说明 |
|---|---|
| `dashboard/index.md` | Markdown dashboard |
| `dashboard/atlas_dashboard.html` | 本地静态 HTML dashboard |
| `dashboard/dashboard_data.json` | dashboard 汇总数据 |
| `reports/evidence_index.md` | evidence 总索引 |
| `coverage/atlas_coverage_summary.md` | ATLAS 覆盖摘要 |
| `coverage/coverage_gap_analysis.md` | ATLAS 缺口分析 |
| `docs/control_checklist.md` | 防守控制项清单 |
| `docs/phase8_dashboard_report_review.md` | Phase 8 复盘 |
| `docs/api_provider_onboarding.md` | API Provider onboarding |
| `docs/phase11_api_provider_skeleton_review.md` | Phase 11 复盘 |
| `corpus/README.md` | Evaluation Corpus 概览 |
| `corpus/corpus_schema.md` | Corpus schema 定义 |
| `corpus/corpus_index.yaml` | Corpus 总索引 |
| `red_team/README.md` | AI Red Teaming 方法论总览 |
| `red_team/ai_red_team_playbook.md` | 12 步标准红队评估流程 |
| `red_team/finding_severity_model.md` | 7 维度严重性评分模型 |
| `red_team/finding_template.md` | Finding 记录模板 |
| `red_team/evidence_handling_guide.md` | Evidence 处理指南 |
| `red_team/mitigation_retest_workflow.md` | 修复建议与复测流程 |
| `red_team/red_team_report_outline.md` | 红队报告大纲 |
| `inventory/README.md` | AI Asset Inventory 概览 |
| `inventory/ai_asset_inventory_schema.md` | 资产字段定义 |
| `inventory/sample_ai_asset_inventory.yaml` | 样例资产清单（5 个 fake 资产） |
| `inventory/ai_application_intake_form.md` | AI 应用接入登记表单 |
| `inventory/ai_asset_risk_register_template.yaml` | 风险登记表模板 |
| `inventory/ai_asset_inventory_index.yaml` | 资产索引 |
| `governance/README.md` | AI Risk Governance 概览 |
| `governance/nist_ai_rmf_mapping.yaml` | NIST AI RMF 四 function 映射 |
| `governance/nist_genai_profile_mapping.yaml` | GenAI Profile 映射占位 |
| `governance/ai_risk_governance_checklist.md` | 12 类治理检查清单 |
| `governance/governance_to_security_assessment_crosswalk.md` | 治理到安全评估交叉映射 |
| `governance/governance_report_appendix_template.md` | 治理报告附录模板 |
| `supply_chain/README.md` | AI/ML-BOM + Supply Chain Mapping 概览 |
| `supply_chain/ai_ml_bom_schema.md` | AI/ML-BOM 9 类组件字段定义 |
| `supply_chain/sample_ai_ml_bom.yaml` | 5 个样例 BOM |
| `supply_chain/model_provenance_checklist.md` | 模型来源可追溯性检查清单 |
| `supply_chain/dataset_knowledge_base_inventory.md` | 数据集/知识库来源清单 |
| `supply_chain/tool_plugin_mcp_inventory.yaml` | 工具/插件/MCP 依赖清单 |
| `supply_chain/prompt_template_inventory.yaml` | 提示词模板依赖清单 |
| `supply_chain/external_api_dependency_inventory.yaml` | 外部 API 依赖清单 |
| `supply_chain/supply_chain_risk_register_template.yaml` | 供应链风险登记表模板 |
| `supply_chain/supply_chain_to_atlas_owasp_mapping.yaml` | 供应链风险到 ATLAS/OWASP/NIST 映射 |
| `supply_chain/supply_chain_report_appendix_template.md` | 供应链报告附录模板 |
| `external_tools/README.md` | External Evaluation Tool Adapter Planning、External Tool Mock Evidence Normalization 概览 |
| `external_tools/external_tool_evidence_schema.md` | 外部工具统一 evidence schema |
| `external_tools/external_tool_risk_boundary.md` | 外部工具接入风险边界 |
| `external_tools/external_tool_adapter_index.yaml` | 6 个 adapter 的索引和状态 |
| `external_tools/external_tool_to_atlas_owasp_mapping.yaml` | 外部工具到 ATLAS/OWASP 映射 |
| `external_tools/garak_adapter_plan.md` | garak adapter 设计计划 |
| `external_tools/pyrit_adapter_plan.md` | PyRIT adapter 设计计划 |
| `external_tools/agent_benchmark_adapter_plan.md` | Agent benchmark adapter 设计计划 |
| `external_tools/browser_automation_adapter_plan.md` | Browser Automation adapter 设计计划 |
| `external_tools/api_provider_adapter_plan.md` | API Provider adapter 设计计划 |
| `external_tools/external_tool_report_appendix_template.md` | 外部工具报告附录模板 |
| `docs/phase27a_corpus_curation_backfill_review.md` | Phase 27A Corpus & Curation Backfill 复盘 |
| `rules/README.md` | Assertion & Risk Signal Rule Engine 概览 |
| `rules/risk_signal_rules.yaml` | 24 条风险信号规则定义 |
| `rules/expected_behavior_rules.yaml` | 15 条预期行为规则定义 |
| `rules/assertion_coverage_mapping.yaml` | OWASP/ATLAS assertion 覆盖映射 |
| `rules/severity_mapping.yaml` | 24 条 severity mapping |
| `rules/rule_coverage_report.md` | 规则覆盖报告 |
| `rules/manual_review_rules.yaml` | 需人工 review 的规则清单 |
| `scripts/validate_authorized_target_onboarding.py` | Phase 31B Onboarding validation script（18 checks） |
| `api_provider/onboarding/README.md` | Phase 31B Onboarding 目录概览 |
| `api_provider/onboarding/authorized_target_onboarding_schema.md` | Phase 31B 授权 Target Onboarding Schema |
| `api_provider/onboarding/target_intake_template.yaml` | Phase 31B Target 接入登记模板 |
| `api_provider/onboarding/roe_checklist.md` | Phase 31B RoE 检查清单 |
| `api_provider/onboarding/credential_isolation_policy.md` | Phase 31B 凭证隔离策略 |
| `api_provider/onboarding/test_scope_definition_template.yaml` | Phase 31B 测试范围定义模板 |
| `api_provider/onboarding/allowed_prohibited_operations_matrix.yaml` | Phase 31B 允许/禁止操作矩阵 |
| `api_provider/onboarding/rate_limit_and_safety_window_policy.md` | Phase 31B 速率限制与安全窗口策略 |
| `api_provider/onboarding/approval_gate_checklist.md` | Phase 31B 审批门检查清单 |
| `api_provider/onboarding/onboarding_validation_result.yaml` | Phase 31B Onboarding validation result |
| `api_provider/onboarding/onboarding_validation_report.md` | Phase 31B Onboarding validation report |
| `api_provider/mock_harness/README.md` | Phase 31C Mock Harness 目录概览 |
| `api_provider/mock_harness/mock_api_target_schema.md` | Phase 31C Mock API Target Schema |
| `api_provider/mock_harness/mock_request_fixtures.yaml` | Phase 31C 8 个 mock request fixtures |
| `api_provider/mock_harness/mock_response_fixtures.yaml` | Phase 31C 8 个 mock response fixtures |
| `api_provider/mock_harness/mock_execution_trace.yaml` | Phase 31C Mock execution trace |
| `api_provider/mock_harness/mock_normalized_response_samples.yaml` | Phase 31C Normalized response samples |
| `api_provider/mock_harness/mock_execution_boundary.md` | Phase 31C Mock execution boundary |
| `api_provider/mock_harness/mock_harness_validation_result.yaml` | Phase 31C Validation result（21/21 passed） |
| `api_provider/mock_harness/mock_harness_validation_report.md` | Phase 31C Validation report |
| `scripts/run_local_mock_api_harness.py` | Phase 31C Mock harness runner |
| `scripts/validate_local_mock_api_harness.py` | Phase 31C Validation script（21 checks） |
"""
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
