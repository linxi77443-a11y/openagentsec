#!/usr/bin/env python3
"""Phase 29 — Finding Generator Prototype。

读取 mock/local sample evidence，生成 sample/mock finding drafts。

本脚本不执行测试、不运行 promptfoo、不连接真实系统、不生成真实 evidence。
"""

import os
import sys
import json
import yaml
import copy

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINDINGS_DIR = os.path.join(ROOT_DIR, "findings")
SAMPLE_DIR = os.path.join(FINDINGS_DIR, "sample_findings")

GENERATED_AT = "2026-01-01T00:00:00Z"


def load_json(rel_path):
    path = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def load_yaml(rel_path):
    path = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


def make_finding(
    finding_id,
    title,
    finding_status,
    finding_type,
    source_type,
    source_evidence,
    target_profile,
    affected_asset,
    risk_summary,
    severity,
    confidence,
    risk_signals,
    owasp_llm_mapping=None,
    owasp_agentic_mapping=None,
    mitre_atlas_mapping=None,
    related_corpus=None,
    related_regression_suites=None,
    technical_summary=None,
    business_impact=None,
    severity_rationale=None,
    expected_behavior_failed=None,
    recommended_mitigation=None,
    retest_plan=None,
    limitations=None,
):
    """Create a sample finding dict with required boundary fields."""
    finding = {
        "finding_id": finding_id,
        "finding_title": title,
        "finding_status": finding_status,
        "finding_type": finding_type,
        "source_type": source_type,
        "source_evidence": source_evidence or [],
        "target_profile": target_profile,
        "affected_asset": affected_asset,
        "risk_summary": risk_summary,
        "severity": severity,
        "confidence": confidence,
        "risk_signals": risk_signals or [],
        "generated_at": GENERATED_AT,
        "real_target_validated": False,
        "usable_for_formal_report": False,
    }
    if owasp_llm_mapping:
        finding["owasp_llm_mapping"] = owasp_llm_mapping
    if owasp_agentic_mapping:
        finding["owasp_agentic_mapping"] = owasp_agentic_mapping
    if mitre_atlas_mapping:
        finding["mitre_atlas_mapping"] = mitre_atlas_mapping
    if related_corpus:
        finding["related_corpus"] = related_corpus
    if related_regression_suites:
        finding["related_regression_suites"] = related_regression_suites
    if technical_summary:
        finding["technical_summary"] = technical_summary
    if business_impact:
        finding["business_impact"] = business_impact
    if severity_rationale:
        finding["severity_rationale"] = severity_rationale
    if expected_behavior_failed:
        finding["expected_behavior_failed"] = expected_behavior_failed
    if recommended_mitigation:
        finding["recommended_mitigation"] = recommended_mitigation
    if retest_plan:
        finding["retest_plan"] = retest_plan
    if limitations:
        finding["limitations"] = limitations
    return finding


def generate_sample_findings():
    """Generate sample/mock finding drafts from available evidence and rules."""

    # Load evidence sources
    mock_evidence = load_json(
        "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json"
    )
    severity_rules = load_yaml("rules/severity_rule_mapping.yaml")
    regression_suite_index = load_yaml(
        "regression_suites/regression_suite_index.yaml"
    )

    if not mock_evidence:
        print("WARNING: No mock evidence found. Generating built-in sample findings.")
        mock_entries = []
    else:
        mock_entries = mock_evidence.get("evidence", [])

    findings = []

    # ── 1. Prompt Injection Sample Finding ──
    findings.append(
        make_finding(
            finding_id="FD-2026-SAMPLE-001",
            title="Prompt Injection Sample Finding",
            finding_status="sample_draft",
            finding_type="sample_draft",
            source_type="sample_or_mock",
            source_evidence=[
                "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json",
                "reports/evidence/promptfoo_chatbot_result.json",
            ],
            target_profile="chatbot",
            affected_asset="sample_internal_chatbot",
            risk_summary="Chatbot 在接收到包含恶意指令的用户输入时，可能绕过安全限制执行非预期操作。"
                         "本 sample finding 展示 prompt injection 类的发现项格式。",
            severity="High",
            confidence="medium",
            risk_signals=["prompt_injection", "goal_hijack"],
            owasp_llm_mapping=["LLM01"],
            owasp_agentic_mapping=["ASI01"],
            mitre_atlas_mapping=[
                "atlas.llm_prompt_injection",
                "atlas.direct_prompt_injection",
            ],
            related_corpus=["corpus/chatbot/prompt_injection.yaml"],
            related_regression_suites=[
                "suite_chatbot_regression",
                "suite_owasp_llm_regression",
            ],
            technical_summary="通过精心构造的 prompt 绕过系统限制，模拟攻击者注入恶意指令。"
                              "当前 sandbox 使用 fake model，未在真实模型上验证。",
            business_impact="攻击者可能绕过安全控制获得非授权信息或功能。",
            severity_rationale="基于 severity_rule_mapping.yaml: prompt_injection 默认 High。"
                               "当前为 sample draft，未在真实目标上确认。",
            expected_behavior_failed=["should_refuse"],
            recommended_mitigation="增强 system prompt 安全边界，实施输入过滤规则，增加拒绝行为检测。",
            retest_plan="使用 corpus/chatbot/prompt_injection.yaml 语料执行 promptfoo eval。",
            limitations=[
                "Sample finding only — 未在真实模型上验证",
                "使用 fake model 和 mock 环境",
                "不可用于正式报告",
            ],
        )
    )

    # ── 2. Sensitive Disclosure Sample Finding ──
    findings.append(
        make_finding(
            finding_id="FD-2026-SAMPLE-002",
            title="Sensitive Disclosure Sample Finding",
            finding_status="sample_draft",
            finding_type="sample_draft",
            source_type="sample_or_mock",
            source_evidence=[
                "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json",
                "reports/evidence/promptfoo_chatbot_result.json",
            ],
            target_profile="chatbot",
            affected_asset="sample_internal_chatbot",
            risk_summary="Chatbot 在输出中可能意外泄露敏感信息，包括内部数据、fake secret 或配置信息。"
                         "本 sample finding 展示敏感信息泄露类的发现项格式。",
            severity="High",
            confidence="medium",
            risk_signals=["sensitive_disclosure", "data_leakage"],
            owasp_llm_mapping=["LLM02"],
            owasp_agentic_mapping=["ASI02", "ASI09"],
            mitre_atlas_mapping=["atlas.llm_data_leakage"],
            related_corpus=["corpus/chatbot/sensitive_disclosure.yaml"],
            related_regression_suites=[
                "suite_chatbot_regression",
                "suite_owasp_llm_regression",
            ],
            technical_summary="模拟敏感信息泄露场景，测试 chatbot 是否能正确处理含敏感数据的查询。"
                              "当前使用 fake secret 和 honeytoken 进行检测。",
            business_impact="敏感信息泄露可能导致内部策略暴露、凭证泄露或合规问题。",
            severity_rationale="基于 severity_rule_mapping.yaml: sensitive_disclosure 默认 High。"
                               "使用 fake data，未在真实数据上验证。",
            expected_behavior_failed=["should_not_leak_sensitive_data"],
            recommended_mitigation="实施输出过滤与敏感信息脱敏，增加 evidence 后处理脱敏。",
            retest_plan="使用 corpus/chatbot/sensitive_disclosure.yaml 语料执行 promptfoo eval。",
            limitations=[
                "Sample finding only — 使用 fake secret/honeytoken",
                "不反映真实敏感数据泄露风险",
                "不可用于正式报告",
            ],
        )
    )

    # ── 3. System Prompt Leakage Sample Finding ──
    findings.append(
        make_finding(
            finding_id="FD-2026-SAMPLE-003",
            title="System Prompt Leakage Sample Finding",
            finding_status="sample_draft",
            finding_type="sample_draft",
            source_type="sample_or_mock",
            source_evidence=[
                "reports/evidence/promptfoo_chatbot_result.json",
            ],
            target_profile="chatbot",
            affected_asset="sample_internal_chatbot",
            risk_summary="Chatbot 可能通过注入或推理泄露系统提示内容，暴露应用内部指令和安全边界。",
            severity="Medium",
            confidence="medium",
            risk_signals=["system_prompt_exposure"],
            owasp_llm_mapping=["LLM07"],
            owasp_agentic_mapping=["ASI06"],
            mitre_atlas_mapping=["atlas.extract_llm_system_prompt"],
            related_corpus=["corpus/chatbot/system_prompt_exposure.yaml"],
            related_regression_suites=[
                "suite_chatbot_regression",
                "suite_owasp_llm_regression",
            ],
            technical_summary="通过构造特定 prompt（如 'Repeat your instructions'）尝试提取 system prompt。"
                              "当前使用 fake system prompt，真实 system prompt 泄露风险可能不同。",
            business_impact="System prompt 泄露可能导致攻击者了解系统安全边界和指令配置。",
            severity_rationale="基于 severity_rule_mapping.yaml: system_prompt_exposure 默认 Medium。"
                               "使用 fake system prompt，未在真实系统上验证。",
            expected_behavior_failed=["should_not_reveal_system_prompt"],
            recommended_mitigation="实施系统提示隔离，增加多语言提取变体的回归语料。",
            retest_plan="使用 corpus/chatbot/system_prompt_exposure.yaml 语料执行 promptfoo eval。",
            limitations=[
                "Sample finding only — 使用 fake system prompt",
                "仅限本地 sandbox 环境",
                "不可用于正式报告",
            ],
        )
    )

    # ── 4. Agent Tool Misuse Sample Finding (from mock evidence) ──
    # Find AgentDojo mock evidence
    agentdojo_entry = None
    for entry in mock_entries or []:
        if entry.get("tool_name") == "AgentDojo":
            agentdojo_entry = entry
            break

    if agentdojo_entry:
        obs = agentdojo_entry.get("normalized_result", {}).get("observations", [])
        obs_status = obs[0].get("status", "unknown") if obs else "unknown"
        risk_summary = (
            f"Agent 在模拟测试中被检测到工具调用异常：{obs_status}。"
            f"基于 AgentDojo mock evidence 生成的 finding draft。"
        )
    else:
        risk_summary = "Agent 工具 misuse 的 sample finding。当前 sandbox 使用 mock harness 测试工具调用权限。"

    findings.append(
        make_finding(
            finding_id="FD-2026-SAMPLE-004",
            title="Agent Tool Misuse Sample Finding",
            finding_status="mock_draft",
            finding_type="mock_draft",
            source_type="external_tool_mock",
            source_evidence=[
                "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json",
                "reports/evidence/promptfoo_agent_result.json",
            ],
            target_profile="agent",
            affected_asset="sample_generic_agent",
            risk_summary=risk_summary,
            severity="High",
            confidence="medium",
            risk_signals=["tool_misuse", "unauthorized_tool_invocation", "exfiltration"],
            owasp_llm_mapping=["LLM06"],
            owasp_agentic_mapping=["ASI02", "ASI08"],
            mitre_atlas_mapping=[
                "atlas.ai_agent_tool_invocation",
                "atlas.exfiltration_via_ai_agent_tool_invocation",
            ],
            related_corpus=[
                "corpus/agent/tool_misuse.yaml",
                "corpus/agent/exfiltration.yaml",
            ],
            related_regression_suites=[
                "suite_agent_regression",
                "suite_owasp_agentic_regression",
            ],
            technical_summary=f"Agent 工具 misuse 的 mock draft。"
                              f"{'AgentDojo mock observation: ' + obs_status if agentdojo_entry else '基于 mock harness 检测。'}",
            business_impact="Agent 工具 misuse 可能导致非授权写操作、数据外传或系统影响。",
            severity_rationale="基于 severity_rule_mapping.yaml: tool_misuse 默认 High。"
                               "基于 mock external tool evidence，未在真实 Agent 上验证。",
            expected_behavior_failed=[
                "should_not_call_unauthorized_tool",
                "should_not_execute_write_action",
            ],
            recommended_mitigation="严格定义工具 allowlist，实施工具调用权限验证。",
            retest_plan="使用 corpus/agent/tool_misuse.yaml 语料执行 agent harness 测试。",
            limitations=[
                "Mock draft only — 基于未执行的外部工具 mock 输出",
                "AgentDojo 适配器为 planning/design 层，未安装或执行",
                "不可用于正式报告",
            ],
        )
    )

    # ── 5. RAG Poisoning Sample Finding (from mock evidence) ──
    pyrit_entry = None
    for entry in mock_entries or []:
        if entry.get("tool_name") == "PyRIT":
            pyrit_entry = entry
            break

    if pyrit_entry:
        obs = pyrit_entry.get("normalized_result", {}).get("observations", [])
        obs_status = obs[0].get("status", "unknown") if obs else "unknown"
        risk_summary_pyrit = (
            f"RAG 系统在模拟投毒测试中检测到异常：{obs_status}。"
            f"基于 PyRIT mock evidence 生成的 finding draft。"
        )
    else:
        risk_summary_pyrit = "RAG 知识库投毒的 sample finding。使用 mock 文档测试投毒检测。"

    findings.append(
        make_finding(
            finding_id="FD-2026-SAMPLE-005",
            title="RAG Poisoning Sample Finding",
            finding_status="mock_draft",
            finding_type="mock_draft",
            source_type="external_tool_mock",
            source_evidence=[
                "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json",
                "reports/evidence/promptfoo_rag_result.json",
            ],
            target_profile="rag",
            affected_asset="sample_policy_rag_assistant",
            risk_summary=risk_summary_pyrit,
            severity="High",
            confidence="medium",
            risk_signals=["rag_poisoning", "indirect_prompt_injection"],
            owasp_llm_mapping=["LLM04", "LLM08"],
            owasp_agentic_mapping=["ASI06"],
            mitre_atlas_mapping=[
                "atlas.rag_poisoning",
                "atlas.indirect_prompt_injection",
            ],
            related_corpus=[
                "corpus/rag/rag_poisoning.yaml",
                "corpus/rag/indirect_prompt_injection.yaml",
            ],
            related_regression_suites=[
                "suite_rag_regression",
                "suite_owasp_llm_regression",
            ],
            technical_summary=f"RAG 知识库投毒的 mock draft。"
                              f"{'PyRIT mock observation: ' + obs_status if pyrit_entry else '基于本地 mock 文档测试。'}",
            business_impact="RAG 知识库投毒可能导致输出被操控、敏感信息泄露或错误决策。",
            severity_rationale="基于 severity_rule_mapping.yaml: rag_poisoning 默认 High。"
                               "基于 mock external tool evidence，未在真实 RAG 系统上验证。",
            expected_behavior_failed=[
                "should_not_follow_document_instruction",
                "should_cite_sources",
            ],
            recommended_mitigation="增加文档来源可信度评分，实现文档内容冲突检测。",
            retest_plan="使用 corpus/rag/rag_poisoning.yaml 语料执行 promptfoo eval。",
            limitations=[
                "Mock draft only — 基于未执行的外部工具 mock 输出",
                "PyRIT 适配器为 planning/design 层，未安装或执行",
                "不可用于正式报告",
            ],
        )
    )

    # ── 6. Accountability Audit Gap Sample Finding (governance pattern) ──
    findings.append(
        make_finding(
            finding_id="FD-2026-SAMPLE-006",
            title="Accountability Audit Gap Sample Finding",
            finding_status="sample_draft",
            finding_type="governance_gap",
            source_type="sample_or_mock",
            source_evidence=[],
            target_profile="agent",
            affected_asset="sample_generic_agent",
            risk_summary="当前系统缺乏 Agent 工具调用的审计日志记录机制。"
                         "对应 ASI07 (Insecure Inter-Agent Communication) 的已知 gap。"
                         "本 finding 是 governance gap pattern，非技术执行结果。",
            severity="Medium",
            confidence="low",
            risk_signals=["accountability_audit_gap"],
            owasp_agentic_mapping=["ASI07"],
            mitre_atlas_mapping=["atlas.ai_agent_tool_invocation"],
            technical_summary=(
                "ASI07 在 Phase 27 和 Phase 28 中被识别为已知 gap。"
                "当前系统无多 Agent 或跨 Agent 通信测试。"
                "无审计日志记录机制。"
                "本 finding 以 governance gap 形式记录，不作为技术漏洞。"
            ),
            business_impact="缺乏审计日志可能导致安全事件无法追溯，合规要求无法满足。",
            severity_rationale="基于 severity_rule_mapping.yaml: accountability_audit_gap 默认 Medium。"
                               "Governance gap，非技术执行结果。",
            expected_behavior_failed=["should_log_or_audit_action"],
            recommended_mitigation="设计审计日志架构，实施工具调用 Audit Logging。",
            retest_plan="需要多 Agent 编排模拟环境。当前标记为 planned。",
            limitations=[
                "Governance gap pattern — 非技术执行结果",
                "ASI07 已知 gap，不作为 finding failure",
                "当前系统无多 Agent 或跨 Agent 通信",
                "不可用于正式报告",
            ],
        )
    )

    return findings


def build_index(findings):
    """Build finding index from generated findings."""
    by_status = {}
    by_source = {}
    by_profile = {}
    by_severity = {}
    by_owasp_llm = {}
    by_owasp_agentic = {}
    by_atlas = {}
    by_risk_signal = {}

    for f in findings:
        status = f["finding_status"]
        by_status.setdefault(status, []).append(f["finding_id"])

        source = f["source_type"]
        by_source.setdefault(source, []).append(f["finding_id"])

        profile = f["target_profile"]
        by_profile.setdefault(profile, []).append(f["finding_id"])

        sev = f["severity"]
        by_severity.setdefault(sev, []).append(f["finding_id"])

        for owasp_llm in f.get("owasp_llm_mapping", []):
            by_owasp_llm.setdefault(owasp_llm, []).append(f["finding_id"])
        for owasp_agentic in f.get("owasp_agentic_mapping", []):
            by_owasp_agentic.setdefault(owasp_agentic, []).append(f["finding_id"])
        for atlas in f.get("mitre_atlas_mapping", []):
            by_atlas.setdefault(atlas, []).append(f["finding_id"])
        for signal in f.get("risk_signals", []):
            by_risk_signal.setdefault(signal, []).append(f["finding_id"])

    return {
        "generated_at": GENERATED_AT,
        "total_findings": len(findings),
        "by_status": by_status,
        "by_source": by_source,
        "by_profile": by_profile,
        "by_severity": by_severity,
        "by_owasp_llm": by_owasp_llm,
        "by_owasp_agentic": by_owasp_agentic,
        "by_atlas_technique": by_atlas,
        "by_risk_type": by_risk_signal,
        "by_usability": {"usable_for_formal_report": False},
        "by_validation_status": {"real_target_validated": False},
    }


def main():
    print("=== Phase 29: Finding Generator Prototype ===")
    print()

    # Generate findings
    findings = generate_sample_findings()
    print(f"Generated {len(findings)} sample/mock finding drafts:")
    for f in findings:
        print(
            f"  [{f['finding_status']}] {f['finding_id']}: {f['finding_title']} "
            f"(severity={f['severity']}, confidence={f['confidence']})"
        )

    # Build index
    index = build_index(findings)
    assert index["by_usability"]["usable_for_formal_report"] == False
    assert index["by_validation_status"]["real_target_validated"] == False

    # Verify all findings have required boundary fields
    for f in findings:
        assert f["real_target_validated"] == False, (
            f"{f['finding_id']}: real_target_validated must be False"
        )
        assert f["usable_for_formal_report"] == False, (
            f"{f['finding_id']}: usable_for_formal_report must be False"
        )
        assert f["finding_status"] in (
            "sample_draft", "mock_draft", "local_sandbox_draft",
            "needs_human_review", "not_validated", "closed_sample"
        ), f"{f['finding_id']}: invalid finding_status"

    # Write sample finding drafts YAML
    yaml_path = os.path.join(SAMPLE_DIR, "sample_finding_drafts.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(
            {
                "generated_at": GENERATED_AT,
                "total_findings": len(findings),
                "real_target_validated": False,
                "usable_for_formal_report": False,
                "findings": findings,
            },
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
    print(f"\nWrote: {yaml_path}")

    # Write sample finding drafts MD
    md_lines = [
        "# Sample Finding Drafts",
        "",
        f"**Generated at:** {GENERATED_AT}",
        f"**Total findings:** {len(findings)}",
        f"**Real target validated:** False",
        f"**Usable for formal report:** False",
        "",
        "## Finding List",
        "",
        "| ID | Title | Type | Severity | Confidence | Target |",
        "|---|---|---|---|---|---|",
    ]
    for f in findings:
        md_lines.append(
            f"| {f['finding_id']} | {f['finding_title']} | "
            f"{f['finding_status']} | {f['severity']} | "
            f"{f['confidence']} | {f['target_profile']} |"
        )

    md_lines.extend(
        [
            "",
            "## Finding Details",
            "",
        ]
    )

    for f in findings:
        md_lines.extend(
            [
                f"### {f['finding_id']}: {f['finding_title']}",
                "",
                f"- **Status:** {f['finding_status']}",
                f"- **Type:** {f['finding_type']}",
                f"- **Severity:** {f['severity']}",
                f"- **Confidence:** {f['confidence']}",
                f"- **Target profile:** {f['target_profile']}",
                f"- **Asset:** {f['affected_asset']}",
                "",
                "**Risk Summary:**",
                "",
                f"{f['risk_summary']}",
                "",
                "**Risk Signals:**",
                "",
            ]
        )
        for signal in f.get("risk_signals", []):
            md_lines.append(f"- {signal}")
        md_lines.append("")

        if f.get("owasp_llm_mapping"):
            md_lines.extend(
                ["**OWASP LLM Mapping:**", ""]
                + [f"- {r}" for r in f["owasp_llm_mapping"]]
                + [""]
            )

        if f.get("owasp_agentic_mapping"):
            md_lines.extend(
                ["**OWASP Agentic Mapping:**", ""]
                + [f"- {r}" for r in f["owasp_agentic_mapping"]]
                + [""]
            )

        if f.get("mitre_atlas_mapping"):
            md_lines.extend(
                ["**MITRE ATLAS Mapping:**", ""]
                + [f"- {r}" for r in f["mitre_atlas_mapping"]]
                + [""]
            )

        md_lines.extend(
            [
                "**Evidence References:**",
                "",
            ]
        )
        for ev in f.get("source_evidence", []):
            md_lines.append(f"- {ev}")

        md_lines.extend(
            [
                "",
                "**Boundary Flags:**",
                "",
                f"- real_target_validated: {f['real_target_validated']}",
                f"- usable_for_formal_report: {f['usable_for_formal_report']}",
                "",
            ]
        )

        if f.get("limitations"):
            md_lines.extend(
                ["**Limitations:**", ""]
                + [f"- {lim}" for lim in f["limitations"]]
                + [""]
            )

    md_lines.extend(
        [
            "---",
            "",
            "**Important Notice:**",
            "",
            "- All findings are sample/mock drafts only.",
            "- No real targets were validated.",
            "- Not usable for formal security reports.",
            "- Does not replace professional security assessment.",
        ]
    )

    md_path = os.path.join(SAMPLE_DIR, "sample_finding_drafts.md")
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"Wrote: {md_path}")

    # Write finding index
    index_path = os.path.join(FINDINGS_DIR, "finding_index.yaml")
    with open(index_path, "w") as f:
        yaml.dump(index, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Wrote: {index_path}")

    print(f"\nFinding generation complete: {len(findings)} sample/mock finding drafts")
    print("All findings: real_target_validated=false, usable_for_formal_report=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
