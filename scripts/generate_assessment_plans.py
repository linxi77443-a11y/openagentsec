#!/usr/bin/env python3
"""Assessment Plan Generator — Phase 23.

Reads AI Asset Inventory, Corpus Index, ATLAS, OWASP LLM, OWASP Agentic,
NIST AI RMF, Supply Chain, and External Tools data, then generates structured
assessment plans for each sample asset.

All generated_at values use fixed timestamp 2026-01-01T00:00:00Z.
All plans are sample/planning_only — no tests executed, no real systems connected.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required for local YAML parsing") from exc

ROOT = Path(__file__).resolve().parents[1]
PLANS_DIR = ROOT / "assessment_plans"
GENERATED_DIR = PLANS_DIR / "generated"
INDEX_PATH = PLANS_DIR / "assessment_plan_index.yaml"

FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"
PLAN_VERSION = "1.0"

INVENTORY_PATH = ROOT / "inventory/sample_ai_asset_inventory.yaml"
INVENTORY_INDEX_PATH = ROOT / "inventory/ai_asset_inventory_index.yaml"
CORPUS_INDEX_PATH = ROOT / "corpus/corpus_index.yaml"
LLM_PATH = ROOT / "owasp/llm_top10_2025.yaml"
AGENTIC_PATH = ROOT / "owasp/agentic_top10_2026.yaml"
ATLAS_PATH = ROOT / "coverage/atlas_coverage_matrix.yaml"
EXTERNAL_TOOLS_PATH = ROOT / "external_tools/external_tool_adapter_index.yaml"
BOM_PATH = ROOT / "supply_chain/sample_ai_ml_bom.yaml"
NIST_RMF_PATH = ROOT / "governance/nist_ai_rmf_mapping.yaml"


def read_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Plan templates per asset type
# ---------------------------------------------------------------------------


def build_plan_metadata(asset: dict, plan_suffix: str) -> dict:
    return {
        "plan_id": f"plan_{asset['asset_id']}",
        "plan_name": f"评估计划 — {asset['asset_name']}",
        "generated_at": FIXED_TIMESTAMP,
        "plan_version": PLAN_VERSION,
        "source_asset_id": asset["asset_id"],
        "source_asset_name": asset["asset_name"],
        "plan_status": "generated_sample",
        "execution_boundary": "本地 sandbox / fake data / fake tools only. No real API, real model, or real system.",
    }


def build_target_summary(asset: dict) -> dict:
    ai_type = asset.get("ai_system_type", {})
    target_types = [k for k, v in ai_type.items() if v]
    return {
        "target_type": target_types[0] if target_types else "unknown",
        "target_profiles": asset.get("related_profiles", []),
        "environment": asset.get("environment", "local_sandbox"),
        "lifecycle_stage": asset.get("lifecycle_stage", "testing"),
        "criticality": asset.get("criticality", "low"),
        "data_sensitivity": asset.get("data_knowledge_base", {}).get("data_sensitivity", "public"),
        "tooling_enabled": bool(asset.get("agent_tooling", {}).get("tools_enabled", [])),
        "memory_enabled": asset.get("agent_tooling", {}).get("memory_enabled", False),
        "external_channels": asset.get("agent_tooling", {}).get("external_channels", []),
        "write_actions_allowed": asset.get("agent_tooling", {}).get("write_actions_allowed", False),
    }


def build_chatbot_framework() -> dict:
    return {
        "mitre_atlas_techniques": [
            {"technique_id": "atlas.llm_prompt_injection", "coverage_status": "covered"},
            {"technique_id": "atlas.extract_llm_system_prompt", "coverage_status": "covered"},
            {"technique_id": "atlas.llm_data_leakage", "coverage_status": "covered"},
            {"technique_id": "atlas.llm_prompt_obfuscation", "coverage_status": "covered"},
        ],
        "owasp_llm_risks": [
            {"risk_id": "LLM01", "name": "Prompt Injection", "status": "covered_by_local_tests"},
            {"risk_id": "LLM02", "name": "Sensitive Information Disclosure", "status": "covered_by_local_tests"},
            {"risk_id": "LLM05", "name": "Improper Output Handling", "status": "partially_covered"},
            {"risk_id": "LLM07", "name": "System Prompt Leakage", "status": "covered_by_local_tests"},
            {"risk_id": "LLM09", "name": "Misinformation", "status": "partially_covered"},
        ],
        "owasp_agentic_risks": [],
        "nist_ai_rmf_functions": ["Govern", "Map", "Measure"],
        "supply_chain_risks": [
            {"component": "prompt_template_inventory", "risk": "low"},
            {"component": "external_api_dependency_inventory", "risk": "low"},
        ],
    }


def build_rag_framework() -> dict:
    return {
        "mitre_atlas_techniques": [
            {"technique_id": "atlas.indirect_prompt_injection", "coverage_status": "covered"},
            {"technique_id": "atlas.rag_poisoning", "coverage_status": "covered"},
            {"technique_id": "atlas.llm_data_leakage", "coverage_status": "covered"},
            {"technique_id": "atlas.data_poisoning", "coverage_status": "partially_covered"},
        ],
        "owasp_llm_risks": [
            {"risk_id": "LLM01", "name": "Prompt Injection", "status": "covered_by_local_tests"},
            {"risk_id": "LLM02", "name": "Sensitive Information Disclosure", "status": "covered_by_local_tests"},
            {"risk_id": "LLM04", "name": "Data and Model Poisoning", "status": "partially_covered"},
            {"risk_id": "LLM08", "name": "Vector and Embedding Weaknesses", "status": "partially_covered"},
            {"risk_id": "LLM09", "name": "Misinformation", "status": "partially_covered"},
        ],
        "owasp_agentic_risks": [],
        "nist_ai_rmf_functions": ["Govern", "Map", "Measure", "Manage"],
        "supply_chain_risks": [
            {"component": "dataset_knowledge_base_inventory", "risk": "medium"},
            {"component": "external_api_dependency_inventory", "risk": "low"},
        ],
    }


def build_agent_framework() -> dict:
    return {
        "mitre_atlas_techniques": [
            {"technique_id": "atlas.ai_agent_tool_invocation", "coverage_status": "covered"},
            {"technique_id": "atlas.ai_agent_context_poisoning", "coverage_status": "covered"},
            {"technique_id": "atlas.exfiltration_via_ai_agent_tool_invocation", "coverage_status": "covered"},
            {"technique_id": "atlas.credentials_from_ai_agent_configuration", "coverage_status": "covered"},
            {"technique_id": "atlas.denial_of_service", "coverage_status": "covered"},
        ],
        "owasp_llm_risks": [
            {"risk_id": "LLM06", "name": "Excessive Agency", "status": "covered_by_local_tests"},
            {"risk_id": "LLM10", "name": "Unbounded Consumption", "status": "partially_covered"},
        ],
        "owasp_agentic_risks": [
            {"risk_id": "ASI01", "name": "Agent Goal Hijack", "status": "covered_by_local_harness"},
            {"risk_id": "ASI02", "name": "Tool Misuse and Exploitation", "status": "covered_by_local_harness"},
            {"risk_id": "ASI03", "name": "Identity and Privilege Abuse", "status": "covered_by_local_harness"},
            {"risk_id": "ASI06", "name": "Memory & Context Poisoning", "status": "covered_by_local_harness"},
            {"risk_id": "ASI08", "name": "Cascading Failures", "status": "covered_by_local_harness"},
            {"risk_id": "ASI09", "name": "Human-Agent Trust Exploitation", "status": "covered_by_local_harness"},
        ],
        "nist_ai_rmf_functions": ["Govern", "Map", "Measure", "Manage"],
        "supply_chain_risks": [
            {"component": "tool_plugin_mcp_inventory", "risk": "medium"},
            {"component": "external_api_dependency_inventory", "risk": "low"},
        ],
    }


def build_api_framework() -> dict:
    return {
        "mitre_atlas_techniques": [
            {"technique_id": "atlas.llm_data_leakage", "coverage_status": "partially_covered"},
            {"technique_id": "atlas.llm_prompt_injection", "coverage_status": "covered"},
            {"technique_id": "atlas.denial_of_service", "coverage_status": "partially_covered"},
        ],
        "owasp_llm_risks": [
            {"risk_id": "LLM01", "name": "Prompt Injection", "status": "covered_by_local_tests"},
            {"risk_id": "LLM02", "name": "Sensitive Information Disclosure", "status": "covered_by_local_tests"},
            {"risk_id": "LLM10", "name": "Unbounded Consumption", "status": "partially_covered"},
        ],
        "owasp_agentic_risks": [],
        "nist_ai_rmf_functions": ["Govern", "Map", "Measure"],
        "supply_chain_risks": [
            {"component": "external_api_dependency_inventory", "risk": "medium"},
        ],
    }


def build_manual_ui_framework() -> dict:
    return {
        "mitre_atlas_techniques": [
            {"technique_id": "atlas.llm_prompt_injection", "coverage_status": "covered"},
            {"technique_id": "atlas.direct_prompt_injection", "coverage_status": "covered"},
        ],
        "owasp_llm_risks": [
            {"risk_id": "LLM01", "name": "Prompt Injection", "status": "covered_by_local_tests"},
            {"risk_id": "LLM02", "name": "Sensitive Information Disclosure", "status": "covered_by_local_tests"},
            {"risk_id": "LLM07", "name": "System Prompt Leakage", "status": "covered_by_local_tests"},
        ],
        "owasp_agentic_risks": [],
        "nist_ai_rmf_functions": ["Map", "Measure"],
        "supply_chain_risks": [],
    }


def build_chatbot_scope() -> dict:
    return {
        "in_scope": [
            "Direct prompt injection testing",
            "System prompt extraction attempts",
            "Sensitive information disclosure testing",
            "Multilingual bypass testing",
            "Improper output handling testing",
            "Misinformation / hallucination testing",
        ],
        "out_of_scope": [
            "Real API endpoint testing",
            "Real model testing",
            "Real user data access",
            "Production system testing",
            "Browser automation",
        ],
        "assumptions": [
            "All tests run against local sandbox chatbot provider",
            "All input/output data is fake/public",
            "No real credentials or secrets involved",
            "No external network access required",
        ],
        "required_authorization": ["Local sandbox access only"],
        "safety_boundary": "Local sandbox / fake data only. No real system connection.",
    }


def build_rag_scope() -> dict:
    return {
        "in_scope": [
            "Indirect prompt injection via retrieved documents",
            "RAG knowledge base poisoning testing",
            "Fake citation / hallucination detection",
            "Over-disclosure of retrieved content",
            "Vector embedding weakness testing",
            "Stale or conflicting knowledge detection",
        ],
        "out_of_scope": [
            "Real knowledge base connection",
            "Real enterprise document access",
            "Real user PII in retrieval",
            "Production RAG system testing",
        ],
        "assumptions": [
            "All tests use fake documents in sandbox/rag_demo/",
            "Vector store is local_fake only",
            "Embedding model is mock_embedding_v1",
            "No real enterprise data accessed",
        ],
        "required_authorization": ["Local sandbox access only"],
        "safety_boundary": "Local sandbox / fake documents only. No real knowledge base connection.",
    }


def build_agent_scope() -> dict:
    return {
        "in_scope": [
            "Agent tool misuse testing",
            "Agent memory poisoning testing",
            "Agent skill poisoning testing",
            "Agent exfiltration testing",
            "Agent resource consumption testing",
            "OWASP Agentic ASI01-ASI10 mapping verification",
        ],
        "out_of_scope": [
            "Real Agent API integration",
            "Real email/calendar/slack connection",
            "Real secret management system",
            "Real MCP server testing",
            "Production agent system testing",
        ],
        "assumptions": [
            "All tests use Generic Agent Mock Tool Harness",
            "All tools are fake (search_fake_docs, send_fake_email, read_fake_calendar, read_fake_secret)",
            "All write actions are dry-run only",
            "No real external channels accessed",
        ],
        "required_authorization": ["Local sandbox access only", "Mock tool harness approval"],
        "safety_boundary": "Local sandbox / fake tools only. No real agent connection.",
    }


def build_api_scope() -> dict:
    return {
        "in_scope": [
            "API security baseline testing (auth, input validation, error handling)",
            "FastGPT API smoke testing (connectivity, response format, error codes)",
            "Unbounded consumption baseline testing (token limits, rate limiting, recursive loops)",
        ],
        "out_of_scope": [
            "Real API endpoint testing",
            "Real API key usage",
            "Production API load testing",
            "DoS / stress testing",
            "Real credential testing",
        ],
        "assumptions": [
            "API Provider Skeleton is dry-run readiness only",
            "No real endpoint is included in the plan",
            "All tests are documentation_only or planned",
            "No network access required",
        ],
        "required_authorization": ["N/A — all tests are planning/design only"],
        "safety_boundary": "Planning layer only. No real API connection. No real endpoint.",
    }


def build_manual_ui_scope() -> dict:
    return {
        "in_scope": [
            "Manual UI prompt injection replay",
            "Manual UI system prompt exposure replay",
            "Manual UI over-disclosure observation",
        ],
        "out_of_scope": [
            "Real page access",
            "Real browser automation",
            "Real user session testing",
            "Production UI testing",
        ],
        "assumptions": [
            "All replays use local fake replay samples",
            "Manual UI review only — no automated browser testing",
            "No real pages or URLs are accessed",
        ],
        "required_authorization": ["Local sandbox access only"],
        "safety_boundary": "Local fake replay only. No real page access.",
    }


def build_chatbot_corpus() -> dict:
    return {
        "corpus_ids": [
            "chatbot-pi-001", "chatbot-pi-002", "chatbot-pi-003", "chatbot-pi-004",
            "chatbot-spe-001", "chatbot-spe-002", "chatbot-spe-003",
            "chatbot-sd-001", "chatbot-sd-002", "chatbot-sd-003", "chatbot-sd-004",
            "chatbot-mb-001", "chatbot-mb-002", "chatbot-mb-003",
            "chatbot_improper_output_001", "chatbot_improper_output_002",
            "chatbot_improper_output_003", "chatbot_improper_output_004",
            "chatbot_misinfo_001", "chatbot_misinfo_002",
            "chatbot_misinfo_003", "chatbot_misinfo_004",
        ],
        "corpus_files": [
            "corpus/chatbot/prompt_injection.yaml",
            "corpus/chatbot/system_prompt_exposure.yaml",
            "corpus/chatbot/sensitive_disclosure.yaml",
            "corpus/chatbot/multilingual_bypass.yaml",
            "corpus/chatbot/improper_output_handling.yaml",
            "corpus/chatbot/misinformation.yaml",
        ],
        "corpus_status": "mixed (active + planned)",
        "corpus_priority": "high",
        "corpus_gaps": ["多轮注入尚未覆盖", "PII 泄露检测语料不足"],
    }


def build_rag_corpus() -> dict:
    return {
        "corpus_ids": [
            "rag-ipi-001", "rag-ipi-002", "rag-ipi-003", "rag-ipi-004",
            "rag-rp-001", "rag-rp-002", "rag-rp-003", "rag-rp-004",
            "rag-fc-001", "rag-fc-002", "rag-fc-003",
            "rag-od-001", "rag-od-002", "rag-od-003",
            "rag_vector_001", "rag_vector_002", "rag_vector_003", "rag_vector_004",
            "rag_stale_001", "rag_stale_002", "rag_stale_003", "rag_stale_004",
        ],
        "corpus_files": [
            "corpus/rag/indirect_prompt_injection.yaml",
            "corpus/rag/rag_poisoning.yaml",
            "corpus/rag/fake_citation.yaml",
            "corpus/rag/over_disclosure.yaml",
            "corpus/rag/vector_embedding_weaknesses.yaml",
            "corpus/rag/stale_or_conflicting_knowledge.yaml",
        ],
        "corpus_status": "mixed (active + planned)",
        "corpus_priority": "high",
        "corpus_gaps": ["微调投毒未覆盖", "训练数据投毒不在本地 sandbox 范围内"],
    }


def build_agent_corpus() -> dict:
    return {
        "corpus_ids": [
            "agent-tmu-001", "agent-tmu-002", "agent-tmu-003", "agent-tmu-004",
            "agent-mp-001", "agent-mp-002", "agent-mp-003",
            "agent-sp-001", "agent-sp-002", "agent-sp-003",
            "agent-exf-001", "agent-exf-002", "agent-exf-003",
            "agent-rc-001", "agent-rc-002", "agent-rc-003",
        ],
        "corpus_files": [
            "corpus/agent/tool_misuse.yaml",
            "corpus/agent/memory_poisoning.yaml",
            "corpus/agent/skill_poisoning.yaml",
            "corpus/agent/exfiltration.yaml",
            "corpus/agent/resource_consumption.yaml",
        ],
        "corpus_status": "active",
        "corpus_priority": "high",
        "corpus_gaps": ["MCP 投毒测试尚未实现 mock harness", "跨 Agent 通信权限控制未覆盖"],
    }


def build_api_corpus() -> dict:
    return {
        "corpus_ids": [
            "api-fgs-001", "api-fgs-002", "api-fgs-003",
            "api-asb-001", "api-asb-002", "api-asb-003",
            "api_uc_001", "api_uc_002", "api_uc_003", "api_uc_004",
        ],
        "corpus_files": [
            "corpus/api/fastgpt_api_smoke.yaml",
            "corpus/api/api_security_baseline.yaml",
            "corpus/api/unbounded_consumption_baseline.yaml",
        ],
        "corpus_status": "documentation_only + planned",
        "corpus_priority": "medium",
        "corpus_gaps": ["API 速率限制测试未覆盖", "循环检测未覆盖"],
    }


def build_manual_ui_corpus() -> dict:
    return {
        "corpus_ids": [
            "chatbot-pi-001", "chatbot-pi-002", "chatbot-pi-003", "chatbot-pi-004",
            "chatbot-spe-001", "chatbot-spe-002", "chatbot-spe-003",
            "rag-od-001", "rag-od-002", "rag-od-003",
        ],
        "corpus_files": [
            "corpus/chatbot/prompt_injection.yaml",
            "corpus/chatbot/system_prompt_exposure.yaml",
            "corpus/rag/over_disclosure.yaml",
        ],
        "corpus_status": "active",
        "corpus_priority": "medium",
        "corpus_gaps": ["手动 replay 效率低，未来考虑 browser automation"],
    }


def build_chatbot_test_modes() -> dict:
    return {
        "local_sandbox": True,
        "manual_replay": True,
        "mock_harness": False,
        "api_provider": {"status": "skeleton_ready", "real_endpoint": False},
        "external_tool_mock": True,
        "future_external_tools": ["garak", "PyRIT"],
    }


def build_rag_test_modes() -> dict:
    return {
        "local_sandbox": True,
        "manual_replay": True,
        "mock_harness": False,
        "api_provider": {"status": "skeleton_ready", "real_endpoint": False},
        "external_tool_mock": True,
        "future_external_tools": ["garak"],
    }


def build_agent_test_modes() -> dict:
    return {
        "local_sandbox": True,
        "manual_replay": True,
        "mock_harness": True,
        "api_provider": {"status": "not_applicable", "real_endpoint": False},
        "external_tool_mock": True,
        "future_external_tools": ["AgentDojo"],
    }


def build_api_test_modes() -> dict:
    return {
        "local_sandbox": False,
        "manual_replay": False,
        "mock_harness": False,
        "api_provider": {
            "status": "skeleton_or_planning",
            "real_endpoint_required": False,
            "usable_for_formal_finding": False,
            "production_testing_allowed": False,
        },
        "external_tool_mock": False,
        "future_external_tools": [],
    }


def build_manual_ui_test_modes() -> dict:
    return {
        "local_sandbox": False,
        "manual_replay": True,
        "mock_harness": False,
        "api_provider": {"status": "not_applicable", "real_endpoint": False},
        "external_tool_mock": False,
        "future_external_tools": ["Browser Automation (future)"],
    }


def build_chatbot_runners() -> list:
    return [
        {
            "runner_id": "run_atlas_assessment_chatbot",
            "command": "bash runners/run_atlas_assessment.sh --profile chatbot --execute",
            "execution_mode": "local_sandbox",
            "risk_level": "medium",
            "allowed_now": False,
            "reason": "Phase 23 does not execute tests. Execute in a future phase after plan approval.",
        },
    ]


def build_rag_runners() -> list:
    return [
        {
            "runner_id": "run_atlas_assessment_rag",
            "command": "bash runners/run_atlas_assessment.sh --profile rag --execute",
            "execution_mode": "local_sandbox",
            "risk_level": "medium",
            "allowed_now": False,
            "reason": "Phase 23 does not execute tests. Execute in a future phase after plan approval.",
        },
    ]


def build_agent_runners() -> list:
    return [
        {
            "runner_id": "run_generic_agent_harness",
            "command": "bash runners/run_generic_agent_harness.sh --execute",
            "execution_mode": "mock_harness",
            "risk_level": "high",
            "allowed_now": False,
            "reason": "Phase 23 does not execute tests. Execute in a future phase after plan approval.",
        },
        {
            "runner_id": "run_manual_ui_agent",
            "command": "bash runners/run_manual_ui_promptfoo.sh --execute",
            "execution_mode": "manual_replay",
            "risk_level": "medium",
            "allowed_now": False,
            "reason": "Phase 23 does not execute tests. Execute in a future phase after plan approval.",
        },
    ]


def build_api_runners() -> list:
    return [
        {
            "runner_id": "api_provider_skeleton",
            "command": "API Provider Skeleton only — no executable runner available",
            "execution_mode": "api_provider",
            "risk_level": "low",
            "allowed_now": False,
            "reason": "API Provider Skeleton is dry-run readiness only. No real endpoint included.",
        },
    ]


def build_manual_ui_runners() -> list:
    return [
        {
            "runner_id": "run_manual_ui_promptfoo",
            "command": "bash runners/run_manual_ui_promptfoo.sh --execute",
            "execution_mode": "manual_replay",
            "risk_level": "low",
            "allowed_now": False,
            "reason": "Phase 23 does not execute tests. Execute in a future phase after plan approval.",
        },
    ]


def build_chatbot_evidence() -> dict:
    return {
        "expected_evidence_files": [
            "reports/evidence/promptfoo_chatbot_result.json",
            "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json",
        ],
        "evidence_type": "local_sandbox_test_result",
        "redaction_required": True,
        "usable_for_formal_finding": False,
        "limitations": [
            "Evidence from local sandbox only — does not represent real system behavior",
            "External tool evidence is mock normalization only",
            "No real API or model tested",
        ],
    }


def build_rag_evidence() -> dict:
    return {
        "expected_evidence_files": [
            "reports/evidence/promptfoo_rag_result.json",
            "reports/evidence/external_tools/mock_external_tool_normalized_evidence.json",
        ],
        "evidence_type": "local_sandbox_test_result",
        "redaction_required": True,
        "usable_for_formal_finding": False,
        "limitations": [
            "Evidence from local sandbox with fake documents only",
            "No real knowledge base or enterprise data accessed",
        ],
    }


def build_agent_evidence() -> dict:
    return {
        "expected_evidence_files": [
            "reports/evidence/promptfoo_agent_result.json",
            "reports/evidence/promptfoo_generic_agent_harness_result.json",
        ],
        "evidence_type": "local_sandbox_test_result + mock_harness_result",
        "redaction_required": True,
        "usable_for_formal_finding": False,
        "limitations": [
            "Evidence from mock tool harness only — no real agent tools",
            "All tools are fake with fake data",
            "No real email, calendar, or secret accessed",
        ],
    }


def build_api_evidence() -> dict:
    return {
        "expected_evidence_files": [
            "reports/evidence/api_chatbot_provider_dry_run.json",
            "reports/evidence/api_rag_provider_dry_run.json",
        ],
        "evidence_type": "dry_run_skeleton",
        "redaction_required": False,
        "usable_for_formal_finding": False,
        "limitations": [
            "No real endpoint included — all tests are dry-run/planning only",
            "No formal finding can be derived from skeleton evidence",
            "Production testing not allowed",
        ],
    }


def build_manual_ui_evidence() -> dict:
    return {
        "expected_evidence_files": [
            "reports/evidence/promptfoo_manual_ui_result.json",
        ],
        "evidence_type": "manual_replay_result",
        "redaction_required": True,
        "usable_for_formal_finding": False,
        "limitations": [
            "Manual UI replay only — no automated browser testing",
            "Replay samples are local fake data only",
            "No real pages or URLs accessed",
        ],
    }


def build_chatbot_finding() -> dict:
    return {
        "potential_finding_categories": [
            "Prompt Injection",
            "System Prompt Leakage",
            "Sensitive Information Disclosure",
            "Improper Output Handling",
            "Misinformation / Hallucination",
        ],
        "severity_model_reference": "red_team/finding_severity_model.md",
        "finding_template_reference": "red_team/finding_template.md",
        "risk_register_reference": "inventory/ai_asset_risk_register_template.yaml",
        "retest_reference": "red_team/mitigation_retest_workflow.md",
    }


def build_rag_finding() -> dict:
    return {
        "potential_finding_categories": [
            "Indirect Prompt Injection",
            "RAG Poisoning",
            "Fake Citation / Hallucination",
            "Over-Disclosure",
            "Vector Embedding Weakness",
            "Stale / Conflicting Knowledge",
        ],
        "severity_model_reference": "red_team/finding_severity_model.md",
        "finding_template_reference": "red_team/finding_template.md",
        "risk_register_reference": "inventory/ai_asset_risk_register_template.yaml",
        "retest_reference": "red_team/mitigation_retest_workflow.md",
    }


def build_agent_finding() -> dict:
    return {
        "potential_finding_categories": [
            "Tool Misuse",
            "Memory Poisoning",
            "Skill Poisoning",
            "Exfiltration",
            "Resource Consumption",
            "Agent Goal Hijack (OWASP ASI01)",
            "Human-Agent Trust Exploitation (OWASP ASI09)",
        ],
        "severity_model_reference": "red_team/finding_severity_model.md",
        "finding_template_reference": "red_team/finding_template.md",
        "risk_register_reference": "inventory/ai_asset_risk_register_template.yaml",
        "retest_reference": "red_team/mitigation_retest_workflow.md",
    }


def build_api_finding() -> dict:
    return {
        "potential_finding_categories": [
            "API Authentication Weakness",
            "API Input Validation",
            "API Error Information Leakage",
            "Unbounded Resource Consumption",
        ],
        "severity_model_reference": "red_team/finding_severity_model.md",
        "finding_template_reference": "red_team/finding_template.md",
        "risk_register_reference": "inventory/ai_asset_risk_register_template.yaml",
        "retest_reference": "red_team/mitigation_retest_workflow.md",
    }


def build_manual_ui_finding() -> dict:
    return {
        "potential_finding_categories": [
            "Prompt Injection (manual observation)",
            "System Prompt Leakage (manual observation)",
            "Over-Disclosure (manual observation)",
        ],
        "severity_model_reference": "red_team/finding_severity_model.md",
        "finding_template_reference": "red_team/finding_template.md",
        "risk_register_reference": "inventory/ai_asset_risk_register_template.yaml",
        "retest_reference": "red_team/mitigation_retest_workflow.md",
    }


def build_chatbot_report() -> dict:
    return {
        "dashboard_sections": ["测试结果总览", "OWASP LLM 覆盖", "ATLAS 覆盖概览", "Profile 视图"],
        "report_sections": ["执行摘要", "评估范围", "发现与风险", "控制项评估", "修复建议"],
        "appendix_templates": ["red_team/red_team_report_outline.md", "governance/governance_report_appendix_template.md"],
        "limitations_to_include": [
            "仅使用本地 sandbox / fake data",
            "未执行真实 API 测试",
            "未访问外部网络",
        ],
    }


def build_rag_report() -> dict:
    return {
        "dashboard_sections": ["测试结果总览", "OWASP LLM 覆盖", "RAG 覆盖详情", "ATLAS 覆盖概览"],
        "report_sections": ["执行摘要", "RAG 评估范围", "检索安全发现", "知识库投毒风险", "修复建议"],
        "appendix_templates": ["red_team/red_team_report_outline.md", "supply_chain/supply_chain_report_appendix_template.md"],
        "limitations_to_include": [
            "仅使用本地 sandbox / fake documents",
            "未连接真实知识库",
            "未访问企业数据",
        ],
    }


def build_agent_report() -> dict:
    return {
        "dashboard_sections": ["测试结果总览", "OWASP Agentic 覆盖", "OWASP LLM 覆盖", "ATLAS 覆盖概览"],
        "report_sections": ["执行摘要", "Agent 评估范围", "工具滥用发现", "记忆投毒发现", "外传风险", "OWASP Agentic 映射", "修复建议"],
        "appendix_templates": ["red_team/red_team_report_outline.md", "governance/governance_report_appendix_template.md"],
        "limitations_to_include": [
            "仅使用 mock tool harness",
            "未连接真实 Agent 系统",
            "所有工具均为 fake",
        ],
    }


def build_api_report() -> dict:
    return {
        "dashboard_sections": ["测试结果总览", "API 覆盖详情", "OWASP LLM 覆盖"],
        "report_sections": ["执行摘要", "API 评估范围", "安全基线发现", "资源消耗风险", "限制说明"],
        "appendix_templates": ["governance/governance_report_appendix_template.md"],
        "limitations_to_include": [
            "所有测试均为 documentation_only / planned",
            "API Provider Skeleton 为 dry-run 就绪",
            "未包含真实 endpoint",
        ],
    }


def build_manual_ui_report() -> dict:
    return {
        "dashboard_sections": ["Manual UI Replay 状态", "测试结果总览"],
        "report_sections": ["执行摘要", "Manual Replay 结果", "观察发现", "限制说明"],
        "appendix_templates": ["red_team/red_team_report_outline.md"],
        "limitations_to_include": [
            "Manual replay 仅覆盖有限样本",
            "未使用 browser automation",
            "未访问真实页面",
        ],
    }


def build_chatbot_limitations() -> dict:
    return {
        "planned_only_items": [
            "improper_output_handling 语料（4 条 planned）",
            "misinformation 语料（4 条 planned）",
        ],
        "mock_only_items": ["external_tool_mock (garak/PyRIT mock normalization only)"],
        "not_supported_items": ["真实模型测试", "真实 API 测试", "浏览器自动化"],
        "missing_corpus": ["多轮注入语料", "PII 泄露检测语料"],
        "missing_evidence": ["无真实模型测试结果", "无真实 API 测试结果"],
    }


def build_rag_limitations() -> dict:
    return {
        "planned_only_items": [
            "vector_embedding_weaknesses 语料（4 条 planned）",
            "stale_or_conflicting_knowledge 语料（4 条 planned）",
        ],
        "mock_only_items": ["external_tool_mock (garak mock normalization only)"],
        "not_supported_items": ["真实知识库连接", "真实 embedding 模型评估", "训练数据投毒"],
        "missing_corpus": ["微调投毒语料", "训练数据投毒语料"],
        "missing_evidence": ["无真实 RAG 系统测试结果"],
    }


def build_agent_limitations() -> dict:
    return {
        "planned_only_items": [],
        "mock_only_items": ["mock harness (fake tools only)"],
        "not_supported_items": ["真实 Agent 连接", "真实 MCP 服务器", "真实工具链"],
        "missing_corpus": ["MCP 投毒语料", "跨 Agent 通信语料"],
        "missing_evidence": ["无真实 Agent 测试结果", "无真实工具调用 evidence"],
    }


def build_api_limitations() -> dict:
    return {
        "planned_only_items": [
            "fastgpt_api_smoke（3 条 documentation_only）",
            "api_security_baseline（3 条 documentation_only）",
            "unbounded_consumption_baseline（4 条 planned）",
        ],
        "mock_only_items": [],
        "not_supported_items": ["真实 API 测试", "生产系统测试", "DoS / load testing"],
        "missing_corpus": ["API 速率限制语料", "API 认证绕过语料"],
        "missing_evidence": ["无 API 执行结果 — 所有语料均为 documentation_only / planned"],
    }


def build_manual_ui_limitations() -> dict:
    return {
        "planned_only_items": [],
        "mock_only_items": [],
        "not_supported_items": ["浏览器自动化", "真实页面访问"],
        "missing_corpus": ["UI 特定语料"],
        "missing_evidence": ["manual replay 证据有限 — 仅覆盖少数样本"],
    }


# ---------------------------------------------------------------------------
# Builder dispatch
# ---------------------------------------------------------------------------

ASSET_TYPE_BUILDERS = {
    "sample_internal_chatbot": {
        "framework": build_chatbot_framework,
        "scope": build_chatbot_scope,
        "corpus": build_chatbot_corpus,
        "test_modes": build_chatbot_test_modes,
        "runners": build_chatbot_runners,
        "evidence": build_chatbot_evidence,
        "finding": build_chatbot_finding,
        "report": build_chatbot_report,
        "limitations": build_chatbot_limitations,
    },
    "sample_policy_rag_assistant": {
        "framework": build_rag_framework,
        "scope": build_rag_scope,
        "corpus": build_rag_corpus,
        "test_modes": build_rag_test_modes,
        "runners": build_rag_runners,
        "evidence": build_rag_evidence,
        "finding": build_rag_finding,
        "report": build_rag_report,
        "limitations": build_rag_limitations,
    },
    "sample_generic_agent": {
        "framework": build_agent_framework,
        "scope": build_agent_scope,
        "corpus": build_agent_corpus,
        "test_modes": build_agent_test_modes,
        "runners": build_agent_runners,
        "evidence": build_agent_evidence,
        "finding": build_agent_finding,
        "report": build_agent_report,
        "limitations": build_agent_limitations,
    },
    "sample_fastgpt_workflow_api": {
        "framework": build_api_framework,
        "scope": build_api_scope,
        "corpus": build_api_corpus,
        "test_modes": build_api_test_modes,
        "runners": build_api_runners,
        "evidence": build_api_evidence,
        "finding": build_api_finding,
        "report": build_api_report,
        "limitations": build_api_limitations,
    },
    "sample_manual_ui_chatbot": {
        "framework": build_manual_ui_framework,
        "scope": build_manual_ui_scope,
        "corpus": build_manual_ui_corpus,
        "test_modes": build_manual_ui_test_modes,
        "runners": build_manual_ui_runners,
        "evidence": build_manual_ui_evidence,
        "finding": build_manual_ui_finding,
        "report": build_manual_ui_report,
        "limitations": build_manual_ui_limitations,
    },
}


def build_plan(asset: dict, asset_id: str) -> dict:
    builders = ASSET_TYPE_BUILDERS.get(asset_id)
    if not builders:
        raise ValueError(f"No builder for asset_id: {asset_id}")
    return {
        "plan_metadata": build_plan_metadata(asset, asset_id),
        "target_summary": build_target_summary(asset),
        "framework_mapping": builders["framework"](),
        "recommended_assessment_scope": builders["scope"](),
        "recommended_corpus": builders["corpus"](),
        "recommended_test_modes": builders["test_modes"](),
        "recommended_runners": builders["runners"](),
        "evidence_plan": builders["evidence"](),
        "finding_plan": builders["finding"](),
        "report_plan": builders["report"](),
        "current_limitations": builders["limitations"](),
    }


# ---------------------------------------------------------------------------
# Markdown summary generation
# ---------------------------------------------------------------------------


def render_markdown(plan: dict, asset_id: str) -> str:
    meta = plan["plan_metadata"]
    target = plan["target_summary"]
    framework = plan["framework_mapping"]
    scope = plan["recommended_assessment_scope"]
    corpus = plan["recommended_corpus"]
    modes = plan["recommended_test_modes"]
    runners = plan["recommended_runners"]
    evidence = plan["evidence_plan"]
    finding = plan["finding_plan"]
    report = plan["report_plan"]
    limitations = plan["current_limitations"]

    lines = [
        f"# {meta['plan_name']}",
        "",
        f"**Plan ID:** `{meta['plan_id']}`",
        f"**Asset:** `{meta['source_asset_id']}` — {meta['source_asset_name']}",
        f"**Generated:** {meta['generated_at']}",
        f"**Status:** {meta['plan_status']}",
        f"**Boundary:** {meta['execution_boundary']}",
        "",
        "## Target Summary",
        "",
        f"- Type: {target['target_type']}",
        f"- Profiles: {', '.join(target['target_profiles'])}",
        f"- Environment: {target['environment']}",
        f"- Lifecycle: {target['lifecycle_stage']}",
        f"- Criticality: {target['criticality']}",
        f"- Data Sensitivity: {target['data_sensitivity']}",
        f"- Tooling Enabled: {target['tooling_enabled']}",
        f"- Memory Enabled: {target['memory_enabled']}",
        f"- Write Actions Allowed: {target['write_actions_allowed']}",
        "",
        "## Framework Mapping",
        "",
    ]
    lines.append("### MITRE ATLAS")
    for t in framework["mitre_atlas_techniques"]:
        lines.append(f"- `{t['technique_id']}` ({t['coverage_status']})")
    lines.append("")
    lines.append("### OWASP LLM")
    for r in framework["owasp_llm_risks"]:
        lines.append(f"- {r['risk_id']}: {r['name']} ({r['status']})")
    lines.append("")
    if framework["owasp_agentic_risks"]:
        lines.append("### OWASP Agentic")
        for r in framework["owasp_agentic_risks"]:
            lines.append(f"- {r['risk_id']}: {r['name']} ({r['status']})")
        lines.append("")
    lines.append("### NIST AI RMF")
    lines.append(f"- Functions: {', '.join(framework['nist_ai_rmf_functions'])}")
    lines.append("")
    if framework["supply_chain_risks"]:
        lines.append("### Supply Chain")
        for r in framework["supply_chain_risks"]:
            lines.append(f"- {r['component']}: {r['risk']}")
        lines.append("")

    lines.extend([
        "## Assessment Scope",
        "",
        "### In Scope",
        *[f"- {item}" for item in scope["in_scope"]],
        "",
        "### Out of Scope",
        *[f"- {item}" for item in scope["out_of_scope"]],
        "",
        f"### Safety Boundary",
        f"- {scope['safety_boundary']}",
        "",
        "## Recommended Corpus",
        "",
        f"- Corpus files: {len(corpus['corpus_files'])}",
        f"- Corpus IDs: {len(corpus['corpus_ids'])}",
        f"- Status: {corpus['corpus_status']}",
        f"- Priority: {corpus['corpus_priority']}",
        "",
    ])
    for f in corpus["corpus_files"]:
        lines.append(f"- `{f}`")
    if corpus["corpus_gaps"]:
        lines.append("")
        lines.append("### Corpus Gaps")
        for g in corpus["corpus_gaps"]:
            lines.append(f"- {g}")

    lines.extend([
        "",
        "## Test Modes",
        "",
        f"- Local Sandbox: {modes['local_sandbox']}",
        f"- Manual Replay: {modes['manual_replay']}",
        f"- Mock Harness: {modes['mock_harness']}",
        f"- External Tool Mock: {modes['external_tool_mock']}",
        "",
        "## Recommended Runners",
        "",
    ])
    for runner in runners:
        lines.extend([
            f"- **{runner['runner_id']}**",
            f"  - Command: `{runner['command']}`",
            f"  - Mode: {runner['execution_mode']}",
            f"  - Risk: {runner['risk_level']}",
            f"  - Allowed Now: {runner['allowed_now']}",
            f"  - Reason: {runner['reason']}",
            "",
        ])

    lines.extend([
        "## Evidence Plan",
        "",
        f"- Usable for Formal Finding: {evidence['usable_for_formal_finding']}",
        f"- Redaction Required: {evidence['redaction_required']}",
        "",
    ])
    for ef in evidence["expected_evidence_files"]:
        lines.append(f"- `{ef}`")
    lines.append("")
    for lim in evidence["limitations"]:
        lines.append(f"- *{lim}*")

    lines.extend([
        "",
        "## Finding Plan",
        "",
    ])
    for cat in finding["potential_finding_categories"]:
        lines.append(f"- {cat}")
    lines.extend([
        "",
        f"- Severity Model: `{finding['severity_model_reference']}`",
        f"- Finding Template: `{finding['finding_template_reference']}`",
        f"- Risk Register: `{finding['risk_register_reference']}`",
        f"- Retest Workflow: `{finding['retest_reference']}`",
        "",
        "## Current Limitations",
        "",
    ])
    if limitations["planned_only_items"]:
        lines.append("### Planned Only")
        for item in limitations["planned_only_items"]:
            lines.append(f"- {item}")
    if limitations["mock_only_items"]:
        lines.append("### Mock Only")
        for item in limitations["mock_only_items"]:
            lines.append(f"- {item}")
    if limitations["not_supported_items"]:
        lines.append("### Not Supported")
        for item in limitations["not_supported_items"]:
            lines.append(f"- {item}")
    if limitations["missing_corpus"]:
        lines.append("### Missing Corpus")
        for item in limitations["missing_corpus"]:
            lines.append(f"- {item}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Index builder
# ---------------------------------------------------------------------------


def build_index(plans: dict[str, dict]) -> dict:
    index: dict[str, Any] = {
        "assessment_plan_index": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_plans": len(plans),
            "by_asset": {},
            "by_profile": {},
            "by_target_type": {},
            "by_execution_mode": {},
            "by_framework": {"mitre_atlas": [], "owasp_llm": [], "owasp_agentic": [], "nist_ai_rmf": []},
            "by_status": {"generated_sample": [], "planning_only": [], "executable_later": []},
            "by_risk_level": {"low": [], "medium": [], "high": []},
            "by_evidence_readiness": {"evidence_exists": [], "evidence_planned": [], "no_evidence": []},
        }
    }
    idx = index["assessment_plan_index"]

    for asset_id, plan in plans.items():
        meta = plan["plan_metadata"]
        target = plan["target_summary"]
        framework = plan["framework_mapping"]

        plan_ref = {"plan_id": meta["plan_id"], "asset_id": asset_id}

        # by_asset
        idx["by_asset"].setdefault(asset_id, []).append(meta["plan_id"])

        # by_profile
        for profile in target["target_profiles"]:
            idx["by_profile"].setdefault(profile, []).append(meta["plan_id"])

        # by_target_type
        idx["by_target_type"].setdefault(target["target_type"], []).append(meta["plan_id"])

        # by_execution_mode
        for runner in plan["recommended_runners"]:
            mode = runner["execution_mode"]
            idx["by_execution_mode"].setdefault(mode, []).append(meta["plan_id"])

        # by_framework
        for t in framework["mitre_atlas_techniques"]:
            ref = {"plan_id": meta["plan_id"], "technique_id": t["technique_id"]}
            if ref not in idx["by_framework"]["mitre_atlas"]:
                idx["by_framework"]["mitre_atlas"].append(ref)
        for r in framework["owasp_llm_risks"]:
            ref = {"plan_id": meta["plan_id"], "risk_id": r["risk_id"]}
            if ref not in idx["by_framework"]["owasp_llm"]:
                idx["by_framework"]["owasp_llm"].append(ref)
        for r in framework["owasp_agentic_risks"]:
            ref = {"plan_id": meta["plan_id"], "risk_id": r["risk_id"]}
            if ref not in idx["by_framework"]["owasp_agentic"]:
                idx["by_framework"]["owasp_agentic"].append(ref)
        for func in framework["nist_ai_rmf_functions"]:
            ref = {"plan_id": meta["plan_id"], "function": func}
            if ref not in idx["by_framework"]["nist_ai_rmf"]:
                idx["by_framework"]["nist_ai_rmf"].append(ref)

        # by_status
        idx["by_status"]["generated_sample"].append(meta["plan_id"])

        # by_risk_level
        idx["by_risk_level"].setdefault(target["criticality"], []).append(meta["plan_id"])

        # by_evidence_readiness
        idx["by_evidence_readiness"]["evidence_planned"].append(meta["plan_id"])

    return index


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    inventory = read_yaml(INVENTORY_PATH)
    assets = inventory.get("assets", [])

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    asset_map = {}
    for asset in assets:
        aid = asset.get("asset_id", "")
        if aid in ASSET_TYPE_BUILDERS:
            asset_map[aid] = asset

    plans: dict[str, dict] = {}
    for asset_id, asset in asset_map.items():
        plan = build_plan(asset, asset_id)
        plans[asset_id] = plan

        yaml_path = GENERATED_DIR / f"plan_{asset_id}.yaml"
        yaml_path.write_text(
            yaml.dump(plan, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        print(f"Generated: {yaml_path.relative_to(ROOT)}")

        md_path = GENERATED_DIR / f"plan_{asset_id}.md"
        md_path.write_text(render_markdown(plan, asset_id), encoding="utf-8")
        print(f"Generated: {md_path.relative_to(ROOT)}")

    index = build_index(plans)
    INDEX_PATH.write_text(
        yaml.dump(index, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Generated: {INDEX_PATH.relative_to(ROOT)}")

    print(f"\nTotal plans generated: {len(plans)}")
    for aid in sorted(plans):
        print(f"  - {aid}")
    print("\nAll plans are sample/planning_only. No tests executed. No real systems connected.")


if __name__ == "__main__":
    main()
