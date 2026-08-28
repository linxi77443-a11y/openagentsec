#!/usr/bin/env python3
"""Phase 30 — Formal Report Package Builder。

读取本地 sample/mock 评估数据，生成 sample enterprise assessment delivery package。

本脚本不执行测试、不运行 promptfoo、不连接真实系统、不生成真实 evidence。
"""

import os
import sys
import yaml
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
PACKAGE_DIR = BASE_DIR / "delivery_packages" / "sample_enterprise_assessment_package"
GENERATED_AT = "2026-01-01T00:00:00Z"
PACKAGE_ID = "PACKAGE-2026-001"

SOURCE_FILES = {
    "release_manifest": BASE_DIR / "release" / "release_manifest_v1_3.yaml",
    "assessment_plan_index": BASE_DIR / "assessment_plans" / "assessment_plan_index.yaml",
    "report": BASE_DIR / "reports" / "generated_atlas_assessment_report.md",
    "evidence_index": BASE_DIR / "reports" / "evidence_index.md",
    "finding_index": BASE_DIR / "findings" / "finding_index.yaml",
    "sample_findings": BASE_DIR / "findings" / "sample_findings" / "sample_finding_drafts.yaml",
    "risk_register_mapping": BASE_DIR / "findings" / "finding_to_risk_register_mapping.yaml",
    "mitigation_retest_mapping": BASE_DIR / "findings" / "finding_to_mitigation_retest_mapping.yaml",
    "asset_inventory": BASE_DIR / "inventory" / "sample_ai_asset_inventory.yaml",
    "governance_mapping": BASE_DIR / "governance" / "nist_ai_rmf_mapping.yaml",
    "supply_chain_bom": BASE_DIR / "supply_chain" / "sample_ai_ml_bom.yaml",
    "dashboard_data": BASE_DIR / "dashboard" / "dashboard_data.json",
}

INCLUDED_SECTIONS = [
    "executive_summary",
    "assessment_scope",
    "methodology",
    "asset_inventory_summary",
    "test_coverage_summary",
    "finding_summary",
    "risk_register_export",
    "mitigation_roadmap",
    "retest_plan",
    "governance_appendix",
    "supply_chain_appendix",
    "external_tool_appendix",
    "limitations",
]

EXCLUDED_SECTIONS = [
    "raw_evidence_dump",
    "customer_confidential_data",
    "real_credentials",
    "real_endpoints",
    "production_system_data",
]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_yaml(path):
    if not path.exists():
        print(f"  [WARN] File not found: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json(path):
    if not path.exists():
        print(f"  [WARN] File not found: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        import json
        return json.load(f)


def load_text(path):
    if not path.exists():
        print(f"  [WARN] File not found: {path}")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Wrote: {path.relative_to(BASE_DIR)}")


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Wrote: {path.relative_to(BASE_DIR)}")


# ─── Package Manifest ────────────────────────────────────────────────────────

def build_manifest(data):
    """Build package_manifest.yaml."""
    finding_index = data["finding_index"]
    risk_mappings = data["risk_register_mapping"].get("mappings", [])
    mitigation_mappings = data["mitigation_retest_mapping"].get("mappings", [])

    findings = data["sample_findings"].get("findings", [])
    severity_counts = {}
    status_counts = {}
    for f in findings:
        sev = f.get("severity", "Unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        st = f.get("finding_status", "unknown")
        status_counts[st] = status_counts.get(st, 0) + 1

    risk_count = len(risk_mappings)
    mitigation_count = len(mitigation_mappings)
    retest_count = sum(1 for m in mitigation_mappings if m.get("current_status") == "not_retested")

    return {
        "package_id": PACKAGE_ID,
        "package_name": "Sample Enterprise AI Security Assessment Package",
        "package_type": "sample_delivery_package",
        "generated_at": GENERATED_AT,
        "source_release": "v1.3",
        "source_assessment_plans": [
            "assessment_plans/assessment_plan_index.yaml",
            "assessment_plans/generated/",
        ],
        "source_findings": "findings/finding_index.yaml",
        "source_evidence_index": "reports/evidence_index.md",
        "source_dashboard": "dashboard/dashboard_data.json",
        "source_governance_mapping": "governance/nist_ai_rmf_mapping.yaml",
        "source_supply_chain_mapping": "supply_chain/sample_ai_ml_bom.yaml",
        "included_sections": INCLUDED_SECTIONS,
        "excluded_sections": EXCLUDED_SECTIONS,
        "finding_summary": {
            "total_findings": len(findings),
            "by_severity": severity_counts,
            "by_status": status_counts,
        },
        "risk_register_summary": {
            "total_risk_entries": risk_count,
            "status": "planned",
        },
        "mitigation_summary": {
            "total_mitigation_plans": mitigation_count,
            "covered_findings": [m["finding_id"] for m in risk_mappings],
        },
        "retest_summary": {
            "total_retest_plans": retest_count,
            "retest_status": "not_retested",
        },
        "limitations": [
            "Sample delivery package — not a formal customer report",
            "All findings are sample/mock drafts (real_target_validated=false)",
            "No real test execution performed",
            "No real evidence generated",
            "No real systems connected",
            "No real credentials, endpoints, or customer data included",
            "External tools (garak, PyRIT, AgentDojo, AgentDyn) not installed or executed",
            "Browser automation not connected",
            "Governance mapping is project-internal, not NIST compliance certification",
            "Supply chain BOM uses sample/fake data only",
        ],
        "validation_status": {
            "real_customer": False,
            "real_target_validated": False,
            "formal_report": False,
            "usable_for_customer_delivery": False,
            "manual_review_required": True,
            "roe_required": True,
            "real_execution_required": True,
        },
        "real_customer": False,
        "real_target_validated": False,
        "formal_report": False,
        "usable_for_customer_delivery": False,
    }


# ─── Section Builders ────────────────────────────────────────────────────────

def build_executive_summary(data):
    """Build executive_summary.md."""
    findings = data["sample_findings"].get("findings", [])
    severity_counts = {}
    for f in findings:
        sev = f.get("severity", "Unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    severity_line = ", ".join(f"{k}: {v}" for k, v in sorted(severity_counts.items()))

    return f"""# Executive Summary

**Sample Delivery Package — Not a Formal Customer Report**

## Overview

This document is a **sample enterprise AI security assessment delivery package** generated by the AI Security Assessment & Governance Workbench (v1.3). It demonstrates the delivery package structure for an enterprise AI security assessment.

## Package Information

- **Package ID**: {PACKAGE_ID}
- **Generated At**: {GENERATED_AT}
- **Package Type**: sample_delivery_package
- **Source Release**: v1.3

## Assessment Scope

The sample assessment covers 5 assessment plans targeting chatbot, RAG, agent, API, and manual UI profiles. All assessments were executed in local sandbox / mock / replay environments. No real systems were tested.

## Key Findings

- **Total Sample Findings**: {len(findings)}
- **Severity Distribution**: {severity_line}
- **Finding Types**: sample_draft, mock_draft, governance_gap

## Important Notice

This is a **SAMPLE DELIVERY PACKAGE** only. It does NOT represent:

- A real customer assessment
- Real security vulnerabilities in any production system
- A completed compliance certification
- A formal security audit report

All findings are sample/mock drafts (real_target_validated=false, usable_for_formal_report=false). No real test execution was performed. No real evidence was generated. No real systems were connected.

A real customer delivery package requires: RoE, real system access, real test execution, real evidence generation, manual review of all findings, and customer acceptance.
"""


def build_assessment_scope(data):
    """Build assessment_scope.md."""
    plan_index = data["assessment_plan_index"]
    plans = plan_index.get("assessment_plan_index", plan_index)
    total_plans = plans.get("total_plans", 0)
    by_profile = plans.get("by_profile", {})

    profiles = list(by_profile.keys())
    plan_names = []
    for p_list in by_profile.values():
        plan_names.extend(p_list)

    return f"""# Assessment Scope

## Sample Assessment Scope

- **Total Assessment Plans**: {total_plans}
- **Profiles Covered**: {', '.join(sorted(profiles))}
- **Plan Names**:
{chr(10).join(f'  - {p}' for p in sorted(set(plan_names)))}

## Assessment Boundaries

All assessments in this sample package were conducted within the following boundaries:

- **Execution Mode**: local_sandbox, manual_ui_replay, dry_run, mock_only
- **Real Systems**: Not connected
- **Real APIs**: Not called
- **Real Models**: Not accessed
- **Real Data**: Not used
- **External Tools**: Not installed or executed (garak, PyRIT, AgentDojo, AgentDyn)
- **Browser Automation**: Not connected

## Sample Assets Assessed

The sample assessment covers 5 sample assets (internal_chatbot, policy_rag_assistant, generic_agent, fastgpt_workflow_api, manual_ui_chatbot). All assets are sample/fake assets only and do not represent any real system.
"""


def build_methodology(data):
    """Build methodology.md."""
    return f"""# Assessment Methodology

## Approach

The AI Security Assessment & Governance Workbench follows a structured methodology:

1. **Planning Layer**: Define assessment scope, risk categories, and corpus selection
2. **Compilation Layer**: Compile corpus entries into standardized testcases
3. **Curation Layer**: Classify and bind testcases to appropriate runners
4. **Execution Layer**: Execute tests via local sandbox, manual replay, or API providers
5. **Analysis Layer**: Apply assertion rules and risk signal detection
6. **Reporting Layer**: Generate findings, dashboard, and delivery package

## Methodologies Referenced

- **MITRE ATLAS**: Adversarial Threat Landscape for AI Systems
- **OWASP LLM Top 10**: Security risks in LLM applications
- **OWASP Agentic Top 10**: Security risks in autonomous AI agents
- **NIST AI RMF**: AI Risk Management Framework (governance mapping only)

## Testing Methods

| Method | Status | Real System Connected |
|---|---|---|
| Local Sandbox Assessment | Executed (fake/mock) | No |
| Manual UI Replay | Executed (fake samples) | No |
| API Provider Skeleton | Dry-run only | No |
| Generic Agent Mock Harness | Executed (mock tools) | No |

## Important

The methodology described here is a **framework and approach** used within this sample package. It does not represent completed testing against any real system. All findings are sample/mock drafts only.
"""


def build_asset_inventory_summary(data):
    """Build asset_inventory_summary.md."""
    inventory = data["asset_inventory"]
    assets = inventory.get("assets", [])
    asset_types = {}
    for a in assets:
        ai_type = a.get("ai_system_type", {})
        for k, v in ai_type.items():
            if v:
                asset_types[k] = asset_types.get(k, 0) + 1

    type_lines = ", ".join(f"{k}: {v}" for k, v in sorted(asset_types.items()))

    return f"""# Asset Inventory Summary

## Sample AI Asset Inventory

- **Total Sample Assets**: {len(assets)}
- **Asset Types**: {type_lines}
- **Environment**: local_sandbox (all assets)
- **Data Sensitivity**: public / fake data only

## Asset Details

| Asset ID | Name | Type | Environment |
|---|---|---|---|
{chr(10).join(f"| {a.get('asset_id', '')} | {a.get('asset_name', '')} | {', '.join(k for k, v in a.get('ai_system_type', {}).items() if v) or 'N/A'} | {a.get('environment', '')} |" for a in assets)}

## Important

All assets listed above are **sample/fake assets** only. They do not represent any real system, real company, or real deployment. No real endpoints, credentials, or customer data are included.
"""


def build_test_coverage_summary(data):
    """Build test_coverage_summary.md."""
    dashboard = data.get("dashboard_data", {})
    profiles = dashboard.get("assessment_profiles", {})
    exec_status = dashboard.get("execution_status", {})

    profile_lines = []
    if isinstance(profiles, dict):
        for pname, pinfo in profiles.items():
            if isinstance(pinfo, dict):
                total = pinfo.get("total_tests", pinfo.get("total_testcases", 0))
                passed = pinfo.get("passed", 0)
                profile_lines.append(f"- **{pname}**: {total} tests ({passed} passed)")
    elif isinstance(exec_status, dict):
        for pname, status in exec_status.items():
            profile_lines.append(f"- **{pname}**: {status}")

    if not profile_lines:
        profile_lines = ["- Chatbot: 9 tests (sandbox local execute)", "- RAG: 12 tests (sandbox local execute)", "- Agent: 10 tests (sandbox local execute)", "- Manual UI Replay: 16 tests (fake replay)", "- Generic Agent Mock Harness: 12 tests (mock tools)"]

    return f"""# Test Coverage Summary

## Execution Status

| Capability | Status | Evidence Available |
|---|---|---|
| Chatbot Local Assessment | Executed (local sandbox) | Yes |
| RAG Local Assessment | Executed (local sandbox) | Yes |
| Agent Local Assessment | Executed (local sandbox) | Yes |
| Manual UI Replay | Executed (fake samples) | Yes |
| Generic Agent Mock Harness | Executed (mock tools) | Yes |
| API Provider Skeleton | Dry-run only | No |
| External Tool Mock Normalization | Mock pipeline only | Yes |
| AI Asset Inventory | Sample data only | N/A |
| Governance Mapping | Governance layer | N/A |

## Test Results

{chr(10).join(f"  {l}" for l in profile_lines) if any(profile_lines) else ""}

## Important

All test results are from **local sandbox / fake / mock / replay** environments only. No real systems were tested. No real evidence was generated. Test results are not indicative of real-world security posture.
"""


def build_finding_summary(data):
    """Build finding_summary.md."""
    findings = data["sample_findings"].get("findings", [])
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    sorted_findings = sorted(findings, key=lambda f: severity_order.get(f.get("severity", "Low"), 99))

    finding_lines = []
    for f in sorted_findings:
        finding_lines.append(f"""### {f.get('finding_id', '')}: {f.get('finding_title', '')}

- **Status**: {f.get('finding_status', '')}
- **Severity**: {f.get('severity', '')}
- **Confidence**: {f.get('confidence', '')}
- **Profile**: {f.get('target_profile', '')}
- **Asset**: {f.get('affected_asset', '')}
- **Risk Summary**: {f.get('risk_summary', '')}
- **OWASP LLM**: {', '.join(f.get('owasp_llm_mapping', [])) or 'N/A'}
- **OWASP Agentic**: {', '.join(f.get('owasp_agentic_mapping', [])) or 'N/A'}
- **MITRE ATLAS**: {', '.join(f.get('mitre_atlas_mapping', [])) or 'N/A'}
- **Real Target Validated**: {f.get('real_target_validated', False)}
- **Usable for Formal Report**: {f.get('usable_for_formal_report', False)}

""")

    return f"""# Finding Summary

## Sample Finding Summary

**Total Sample Findings**: {len(findings)}

## Important Notice

All findings listed below are **SAMPLE/MOCK DRAFTS** only:

- real_target_validated=false
- usable_for_formal_report=false
- source_type=sample_or_mock (or external_tool_mock)
- No real test execution was performed
- No real evidence was generated
- Findings do not represent real vulnerabilities in any system

## Findings

{chr(10).join(finding_lines)}

## Severity Distribution

| Severity | Count |
|---|---|
{f"| Critical | {sum(1 for f in findings if f.get('severity') == 'Critical')} |"}
| High | {sum(1 for f in findings if f.get('severity') == 'High')} |
| Medium | {sum(1 for f in findings if f.get('severity') == 'Medium')} |
| Low | {sum(1 for f in findings if f.get('severity') == 'Low')} |
"""


def build_risk_register_export(data):
    """Build risk_register_export.yaml."""
    risk_mappings = data["risk_register_mapping"].get("mappings", [])
    findings = data["sample_findings"].get("findings", [])

    finding_map = {f["finding_id"]: f for f in findings}

    export_entries = []
    for rm in risk_mappings:
        fid = rm["finding_id"]
        finding = finding_map.get(fid, {})
        export_entries.append({
            "risk_id": f"RISK-{fid.replace('FD-', '')}",
            "finding_id": fid,
            "finding_title": rm.get("finding_title", ""),
            "finding_severity": finding.get("severity", "Unknown"),
            "related_asset_id": rm.get("related_asset_id", ""),
            "risk_register_template": rm.get("related_risk_register_template", ""),
            "risk_title": rm.get("risk_register_fields", {}).get("risk_title", ""),
            "affected_component": rm.get("risk_register_fields", {}).get("affected_component", ""),
            "severity": rm.get("risk_register_fields", {}).get("severity", ""),
            "control_gap": rm.get("risk_register_fields", {}).get("control_gap", ""),
            "suggested_risk_owner_placeholder": rm.get("suggested_risk_owner_placeholder", ""),
            "status": rm.get("status", "planned"),
        })

    return {
        "risk_register_export": {
            "generated_at": GENERATED_AT,
            "package_id": PACKAGE_ID,
            "package_type": "sample_delivery_package",
            "real_target_validated": False,
            "usable_for_formal_report": False,
            "total_risk_entries": len(export_entries),
            "entries": export_entries,
        }
    }


def build_mitigation_roadmap(data):
    """Build mitigation_roadmap.md."""
    mitigations = data["mitigation_retest_mapping"].get("mappings", [])

    sections = []
    for m in mitigations:
        sections.append(f"""### {m.get('finding_id', '')}: {m.get('finding_title', '')}

- **Finding Type**: {m.get('finding_type', '')}
- **Target Profile**: {m.get('target_profile', '')}
- **Current Status**: {m.get('current_status', '')}

**Recommended Controls:**
{chr(10).join(f'  - {c}' for c in m.get('recommended_controls', []))}

**Mitigation Plan:**
{m.get('mitigation_plan', 'N/A')}

""")

    return f"""# Mitigation Roadmap

## Sample Mitigation Roadmap

**Total Mitigation Plans**: {len(mitigations)}
**Status**: All mitigations are planned / not_retested

## Important Notice

All mitigation plans listed below are **SAMPLE RECOMMENDATIONS** based on sample findings. They do not represent verified remediation steps for any real system. Real mitigations require real test execution and manual review.

## Mitigation Details

{chr(10).join(sections)}

## Summary

| Finding ID | Profile | Status | Retest Boundary |
|---|---|---|---|
{chr(10).join(f"| {m.get('finding_id', '')} | {m.get('target_profile', '')} | {m.get('current_status', '')} | {m.get('retest_boundary', '')} |" for m in mitigations)}
"""


def build_retest_plan(data):
    """Build retest_plan.md."""
    mitigations = data["mitigation_retest_mapping"].get("mappings", [])

    sections = []
    for m in mitigations:
        suites = m.get("related_regression_suite", [])
        rules = m.get("related_rules", [])
        sections.append(f"""### {m.get('finding_id', '')}: {m.get('finding_title', '')}

- **Retest Boundary**: {m.get('retest_boundary', '')}
- **Current Status**: {m.get('current_status', '')}

**Retest Method:**
{m.get('retest_method', 'N/A')}

**Related Regression Suites:**
{chr(10).join(f'  - {s}' for s in suites) if suites else '  (none)'}

**Related Rules:**
{chr(10).join(f'  - {r}' for r in rules) if rules else '  (none)'}

**Notes:**
{m.get('notes', 'N/A')}

""")

    return f"""# Retest Plan

## Sample Retest Plan

**Total Retest Plans**: {len(mitigations)}
**Status**: All retests are not_retested (planned)

## Important Notice

All retest plans listed below are **SAMPLE PLANS** based on sample findings. They do not represent verified retest results. Real retests require:

1. Mitigation implementation
2. Test execution against real targets
3. Evidence collection and validation
4. Manual review of retest results

## Retest Details

{chr(10).join(sections)}
"""


def build_governance_appendix(data):
    """Build governance_appendix.md."""
    gov = data["governance_mapping"]
    functions = ["govern", "map", "measure", "manage"]
    func_lines = []
    for fn in functions:
        fn_data = gov.get(fn, {})
        support = fn_data.get("current_system_support", "not_mapped")
        gaps = fn_data.get("gaps", [])
        func_lines.append(f"""### {fn_data.get('function_name', fn)} ({fn})

- **Purpose**: {fn_data.get('purpose', 'N/A')}
- **Current Support**: {support}
- **Gaps**:
{chr(10).join(f'  - {g}' for g in gaps) if gaps else '  (none)'}

""")

    return f"""# Governance Appendix

## NIST AI RMF Governance Mapping

This appendix maps the current system components to the NIST AI RMF framework.

**Important**: This mapping is a **project-internal governance layer**. It does NOT represent NIST compliance certification. The system has NOT been audited or certified against NIST AI RMF.

## RMF Function Coverage

{chr(10).join(func_lines)}

## Usage Notes

- All governance mappings are based on sample/fake assets
- No real system has been assessed against NIST AI RMF
- The governance checklist (governance/ai_risk_governance_checklist.md) is a generic template that requires organizational adaptation
- Formal NIST AI RMF assessment requires: authorized assessor, scope definition, evidence collection, and independent validation
"""


def build_supply_chain_appendix(data):
    """Build supply_chain_appendix.md."""
    bom = data["supply_chain_bom"]
    entries = bom.get("bom_entries", [])

    entry_lines = []
    for e in entries:
        models = e.get("model_components", [])
        datasets = e.get("dataset_components", [])
        tools = e.get("tool_components", [])
        entry_lines.append(f"""### {e.get('bom_id', '')} (Asset: {e.get('asset_id', '')})

- **BOM Version**: {e.get('bom_version', '')}
- **Review Frequency**: {e.get('review_frequency', '')}
- **Models**: {len(models)} component(s)
- **Datasets**: {len(datasets)} component(s)
- **Tools**: {len(tools)} component(s)
""")

    return f"""# Supply Chain Appendix

## AI/ML-BOM Summary

**Total Sample BOM Entries**: {len(entries)}

## Important

All BOM entries listed below are **SAMPLE/FAKE** data only. They do not represent any real system's component dependencies. No real model providers, dataset sources, or tool dependencies are included.

## BOM Entries

{chr(10).join(entry_lines)}

## Supply Chain Risk Mapping

The supply chain risk mapping (supply_chain/supply_chain_to_atlas_owasp_mapping.yaml) provides a methodology reference for mapping AI supply chain components to MITRE ATLAS techniques and OWASP risks. This is a methodology reference, not a complete supply chain threat model.
"""


def build_external_tool_appendix(data):
    """Build external_tool_appendix.md."""
    return f"""# External Tool Appendix

## External Evaluation Tool Adapters

The following external tool adapters are in planning/design phase:

| Adapter | Status | Installed | Executed | Real Target Connected |
|---|---|---|---|---|
| garak | planning | No | No | No |
| PyRIT | planning | No | No | No |
| AgentDojo | planning | No | No | No |
| AgentDyn | planning | No | No | No |
| Browser Automation | planning | No | No | No |

## Current External Tool Status

- **No external tools are installed**
- **No external tools have been executed**
- **No external tool evidence has been generated from real execution**
- **Mock normalization pipeline** has been verified using fake/mock outputs only
- **All external tool adapters** are at planning/design stage only

## Future Integration Roadmap

When external tools are integrated, their outputs must be:
1. Collected from each tool's native output format
2. Normalized to external_tool_evidence_schema
3. Validated against assertion rules
4. Incorporated into findings and this delivery package
"""


def build_limitations(data):
    """Build limitations.md."""
    return f"""# Limitations

## Current Limitations

This sample enterprise assessment package has the following limitations:

### Execution Limitations

1. **Local sandbox only**: All assessments were executed in local sandbox / fake / mock / replay environments. No real systems were tested.
2. **No real API connection**: API Provider Skeleton is dry-run only. No real API was called.
3. **No external tools**: garak, PyRIT, AgentDojo, AgentDyn, and Browser Automation are not installed or executed.
4. **No real evidence**: All evidence is from local sandbox execution, mock normalization, or fake replay.
5. **No real findings**: All findings are sample/mock drafts (real_target_validated=false).

### Data Limitations

6. **Sample assets only**: All assets in the inventory are sample/fake assets.
7. **Sample BOM**: AI/ML-BOM entries are sample/fake data only.
8. **Fake data**: All test data uses fake secrets, fake documents, and honeytokens.
9. **No customer data**: No real customer data, credentials, or endpoints are included.

### Methodology Limitations

10. **NIST AI RMF mapping**: Project-internal governance layer only. Not compliance certification.
11. **Severity model**: Not calibrated against real projects.
12. **Corpus coverage**: Still requires business-specific corpus enrichment.
13. **Dashboard**: Static HTML display, not a web console with real-time updates.

### Governance Limitations

14. **No audit trail**: No real audit log for assessment execution.
15. **No approval workflow**: No automated approval or review chain.
16. **No compliance certification**: Package is not a substitute for formal compliance assessment.

### Package Limitations

17. **Sample delivery package only**: This package is NOT a formal customer report.
18. **Not validated against real targets**: All findings have real_target_validated=false.
19. **Not usable for customer delivery**: This package is a structure/template demonstration only.
20. **Manual review required**: All contents require manual review before any decision-making.
"""


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=== Phase 30: Formal Report Package Builder ===\n")

    # 1. Load all source data
    print("Loading source data...")
    data = {}
    for key, path in SOURCE_FILES.items():
        if path.suffix in (".yaml", ".yml"):
            data[key] = load_yaml(path)
        elif path.suffix == ".json":
            data[key] = load_json(path)
        elif path.suffix == ".md":
            data[key] = load_text(path)
        else:
            print(f"  [WARN] Unknown file type: {path}")
            data[key] = {}
    print(f"  Loaded {len(SOURCE_FILES)} source files\n")

    # 2. Build manifest
    print("Building package manifest...")
    manifest = build_manifest(data)
    write_yaml(PACKAGE_DIR / "package_manifest.yaml", manifest)

    # 3. Build sections
    print("\nBuilding package sections...")

    sections = [
        ("executive_summary.md", build_executive_summary(data)),
        ("assessment_scope.md", build_assessment_scope(data)),
        ("methodology.md", build_methodology(data)),
        ("asset_inventory_summary.md", build_asset_inventory_summary(data)),
        ("test_coverage_summary.md", build_test_coverage_summary(data)),
        ("finding_summary.md", build_finding_summary(data)),
        ("mitigation_roadmap.md", build_mitigation_roadmap(data)),
        ("retest_plan.md", build_retest_plan(data)),
        ("governance_appendix.md", build_governance_appendix(data)),
        ("supply_chain_appendix.md", build_supply_chain_appendix(data)),
        ("external_tool_appendix.md", build_external_tool_appendix(data)),
        ("limitations.md", build_limitations(data)),
    ]

    for filename, content in sections:
        write_text(PACKAGE_DIR / filename, content)

    # 4. Build risk register export (YAML)
    print("\nBuilding risk register export...")
    risk_export = build_risk_register_export(data)
    write_yaml(PACKAGE_DIR / "risk_register_export.yaml", risk_export)

    # 5. Build sample package README
    print("\nBuilding sample package README...")
    readme_content = f"""# Sample Enterprise AI Security Assessment Package

## Package Information

- **Package ID**: {PACKAGE_ID}
- **Package Name**: Sample Enterprise AI Security Assessment Package
- **Package Type**: sample_delivery_package
- **Generated At**: {GENERATED_AT}
- **Source Release**: v1.3

## Validation Status

| Field | Value |
|---|---|
| real_customer | false |
| real_target_validated | false |
| formal_report | false |
| usable_for_customer_delivery | false |
| manual_review_required | true |

## Sections

{chr(10).join(f"- {s}" for s in INCLUDED_SECTIONS)}

## Important

This is a **SAMPLE DELIVERY PACKAGE** only. It is NOT a formal customer report, NOT a compliance certification, and NOT a substitute for a real security assessment.
"""
    write_text(PACKAGE_DIR / "README.md", readme_content)

    print(f"\n=== Package build complete ===")
    print(f"Package ID: {PACKAGE_ID}")
    print(f"Package path: {PACKAGE_DIR.relative_to(BASE_DIR)}")
    print(f"Sections: {len(INCLUDED_SECTIONS)}")
    print(f"All sections: sample/mock only, not for customer delivery")


if __name__ == "__main__":
    main()
