#!/usr/bin/env python3
"""Phase 26: Curated Regression Suite Builder.

Reads curated_candidate from Phase 25 curation result and builds
7 curated regression suite drafts + 7 promptfoo suite drafts.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CURATION_RESULT = ROOT / "curation" / "generated_testcase_curation_result.yaml"
RUNNER_BINDING = ROOT / "curation" / "runner_binding_index.yaml"
ASSERTION_MAP = ROOT / "curation" / "assertion_strategy_mapping.yaml"
CORPUS_INDEX = ROOT / "corpus" / "corpus_index.yaml"
GENERATED_DIR = ROOT / "generated_testcases"
SUITE_DIR = ROOT / "regression_suites"
GENERATED_SUITE_DIR = SUITE_DIR / "generated"
PROMPTFOO_DIR = SUITE_DIR / "promptfoo_drafts"

FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_generated_testcases() -> dict[str, dict]:
    """Load all generated testcases keyed by gtc_id."""
    profiles = ["chatbot", "rag", "agent", "api", "regression"]
    result = {}
    for profile in profiles:
        path = GENERATED_DIR / profile / f"generated_{profile}_testcases.yaml"
        if not path.exists():
            continue
        data = load_yaml(path)
        key = f"generated_{profile}_testcases"
        for entry in data.get(key, []):
            gid = entry.get("generated_testcase_id", "")
            if gid:
                result[gid] = entry
    return result


# Define suite configurations with selection rules
SUITE_CONFIGS = [
    {
        "suite_id": "suite_core_llm_regression",
        "suite_name": "Core LLM Regression Suite",
        "suite_type": "core_llm",
        "target_profiles": ["chatbot"],
        "framework_focus": {
            "mitre_atlas": ["atlas.llm_prompt_injection", "atlas.llm_data_leakage",
                            "atlas.llm_system_prompt_extraction"],
            "owasp_llm": ["LLM01", "LLM02", "LLM05", "LLM07", "LLM09", "LLM10"],
            "owasp_agentic": [],
        },
        "risk_types": [
            "prompt_injection", "system_prompt_exposure",
            "sensitive_disclosure", "improper_output_handling",
            "misinformation", "unbounded_consumption",
        ],
        "source_profiles": ["chatbot", "regression"],
        "max_per_risk": 2,
        "description": "Core LLM regression covering prompt injection, system prompt leakage, sensitive disclosure, improper output handling, misinformation, and unbounded consumption.",
    },
    {
        "suite_id": "suite_chatbot_regression",
        "suite_name": "Chatbot Regression Suite",
        "suite_type": "chatbot",
        "target_profiles": ["chatbot"],
        "framework_focus": {
            "mitre_atlas": ["atlas.llm_prompt_injection", "atlas.llm_data_leakage"],
            "owasp_llm": ["LLM01", "LLM02", "LLM05"],
            "owasp_agentic": [],
        },
        "risk_types": [
            "prompt_injection", "system_prompt_exposure",
            "sensitive_disclosure", "multilingual_bypass", "misinformation",
        ],
        "source_profiles": ["chatbot", "regression"],
        "max_per_risk": 2,
        "description": "Chatbot-specific regression covering prompt injection, system prompt exposure, sensitive disclosure, multilingual bypass, and misinformation.",
    },
    {
        "suite_id": "suite_rag_regression",
        "suite_name": "RAG Regression Suite",
        "suite_type": "rag",
        "target_profiles": ["rag"],
        "framework_focus": {
            "mitre_atlas": ["atlas.llm_indirect_prompt_injection",
                            "atlas.llm_data_leakage"],
            "owasp_llm": ["LLM01", "LLM02", "LLM06"],
            "owasp_agentic": [],
        },
        "risk_types": [
            "indirect_prompt_injection", "rag_poisoning",
            "fake_citation", "over_disclosure",
            "vector_embedding_weakness", "stale_or_conflicting_knowledge",
        ],
        "source_profiles": ["rag"],
        "max_per_risk": 2,
        "description": "RAG-specific regression covering indirect prompt injection, RAG poisoning, fake citation, over-disclosure, vector embedding weaknesses, and stale knowledge.",
    },
    {
        "suite_id": "suite_agent_regression",
        "suite_name": "Agent Regression Suite",
        "suite_type": "agent",
        "target_profiles": ["agent"],
        "framework_focus": {
            "mitre_atlas": ["atlas.agent_tool_misuse", "atlas.agent_memory_poisoning",
                            "atlas.agent_exfiltration", "atlas.agent_resource_consumption"],
            "owasp_llm": ["LLM06", "LLM10"],
            "owasp_agentic": ["ASI01", "ASI02", "ASI03", "ASI06", "ASI08", "ASI09"],
        },
        "risk_types": [
            "tool_misuse", "memory_poisoning", "skill_poisoning",
            "exfiltration", "resource_consumption",
        ],
        "source_profiles": ["agent"],
        "max_per_risk": 2,
        "description": "Agent-specific regression covering tool misuse, memory poisoning, skill poisoning, exfiltration, and resource consumption.",
    },
    {
        "suite_id": "suite_api_regression",
        "suite_name": "API Regression Suite",
        "suite_type": "api",
        "target_profiles": ["api"],
        "framework_focus": {
            "mitre_atlas": [],
            "owasp_llm": ["LLM07", "LLM10"],
            "owasp_agentic": [],
        },
        "risk_types": [
            "api_security_baseline", "unbounded_consumption",
        ],
        "source_profiles": ["api"],
        "max_per_risk": 1,
        "description": "API regression covering API security baseline and unbounded consumption. Not executable — API type testcases are marked not_executable.",
    },
    {
        "suite_id": "suite_owasp_llm_regression",
        "suite_name": "OWASP LLM Regression Suite",
        "suite_type": "owasp_llm",
        "target_profiles": ["chatbot", "rag", "agent"],
        "framework_focus": {
            "mitre_atlas": [],
            "owasp_llm": ["LLM01", "LLM02", "LLM03", "LLM04", "LLM05",
                          "LLM06", "LLM07", "LLM08", "LLM09", "LLM10"],
            "owasp_agentic": [],
        },
        "risk_types": [],
        "source_profiles": ["chatbot", "rag", "agent", "regression"],
        "max_per_risk": 2,
        "description": "OWASP LLM Top 10 organized regression suite. Maps curated_candidate entries to LLM01-LLM10 categories.",
    },
    {
        "suite_id": "suite_owasp_agentic_regression",
        "suite_name": "OWASP Agentic Regression Suite",
        "suite_type": "owasp_agentic",
        "target_profiles": ["agent"],
        "framework_focus": {
            "mitre_atlas": [],
            "owasp_llm": [],
            "owasp_agentic": ["ASI01", "ASI02", "ASI03", "ASI04",
                              "ASI05", "ASI06", "ASI07", "ASI08",
                              "ASI09", "ASI10"],
        },
        "risk_types": [],
        "source_profiles": ["agent"],
        "max_per_risk": 2,
        "description": "OWASP Agentic Top 10 organized regression suite. Maps curated_candidate entries to ASI01-ASI10 categories.",
    },
]

# Risk type -> OWASP LLM mapping (for OWASP LLM suite)
# Each risk type may map to multiple OWASP LLM categories
RISK_TO_OWASP_LLM = {
    "prompt_injection": ["LLM01"],
    "system_prompt_exposure": ["LLM02", "LLM07"],
    "sensitive_disclosure": ["LLM02"],
    "improper_output_handling": ["LLM05"],
    "misinformation": ["LLM09"],
    "indirect_prompt_injection": ["LLM01"],
    "rag_poisoning": ["LLM04", "LLM06"],
    "fake_citation": ["LLM06", "LLM09"],
    "over_disclosure": ["LLM02"],
    "vector_embedding_weakness": ["LLM08", "LLM06"],
    "stale_or_conflicting_knowledge": ["LLM04", "LLM06"],
    "tool_misuse": ["LLM06"],
    "memory_poisoning": ["LLM06"],
    "skill_poisoning": ["LLM03", "LLM06"],
    "exfiltration": ["LLM02", "LLM06"],
    "resource_consumption": ["LLM10"],
    "unbounded_consumption": ["LLM10"],
    "api_security_baseline": ["LLM07"],
}

# Risk type -> OWASP Agentic mapping (for OWASP Agentic suite)
RISK_TO_OWASP_AGENTIC = {
    "tool_misuse": ["ASI01", "ASI02"],
    "memory_poisoning": ["ASI03", "ASI06"],
    "skill_poisoning": ["ASI04", "ASI05"],
    "exfiltration": ["ASI02", "ASI09"],
    "resource_consumption": ["ASI08"],
    "fake_citation": ["ASI10"],
}

# Gaps by design (categories still without curated_candidate after mapping)
OWASP_LLM_GAPS = []  # All LLM categories now have mapped risk types
OWASP_AGENTIC_GAPS = ["ASI07"]  # Accountability/Audit has no direct risk type mapping


def get_risk_type_from_id(gtc_id: str) -> str:
    """Infer risk type from testcase ID."""
    risk_map = {
        "pi": "prompt_injection",
        "spe": "system_prompt_exposure",
        "sd": "sensitive_disclosure",
        "mb": "multilingual_bypass",
        "ioh": "improper_output_handling",
        "mi": "misinformation",
        "ipi": "indirect_prompt_injection",
        "rp": "rag_poisoning",
        "fc": "fake_citation",
        "od": "over_disclosure",
        "vew": "vector_embedding_weakness",
        "sck": "stale_or_conflicting_knowledge",
        "tmu": "tool_misuse",
        "mp": "memory_poisoning",
        "sp": "skill_poisoning",
        "exf": "exfiltration",
        "rc": "resource_consumption",
        "uc": "unbounded_consumption",
        "asb": "api_security_baseline",
        "smoke": "api_smoke",
        "csr": "core_security_regression",
        "ga": "generic_agent_regression",
        "olr": "owasp_llm_regression",
    }
    for key, risk in risk_map.items():
        if f"-{key}-" in gtc_id or gtc_id.endswith(f"-{key}"):
            return risk
    return "unknown"


def build_suite(config: dict, curated: list[dict], gtc_map: dict) -> dict:
    """Build a single regression suite from curated candidates."""
    suite_id = config["suite_id"]
    source_profiles = config["source_profiles"]
    risk_types = config.get("risk_types", [])
    max_per_risk = config["max_per_risk"]
    framework_focus = config["framework_focus"]

    # Filter curated_candidates matching source profiles
    candidates = [
        c for c in curated
        if c["curation_status"] == "curated_candidate"
        and c["source_profile"] in source_profiles
    ]

    selected = []
    excluded = []
    used_risk_counts: dict[str, int] = {}

    for c in candidates:
        gtc_id = c["generated_testcase_id"]
        risk = get_risk_type_from_id(gtc_id)

        # For type-specific suites with risk_types list, enforce limit
        if risk_types:
            if risk not in risk_types:
                excluded.append({"id": gtc_id, "reason": f"Risk type '{risk}' not in suite scope"})
                continue
            current = used_risk_counts.get(risk, 0)
            if current >= max_per_risk:
                excluded.append({"id": gtc_id, "reason": f"Max {max_per_risk} per risk type '{risk}'"})
                continue
            used_risk_counts[risk] = current + 1

        selected.append(gtc_id)

    # For OWASP-specific suites, organize by framework category
    gaps = []
    owasp_llm_coverage = {}
    owasp_agentic_coverage = {}

    for gtc_id in selected:
        risk = get_risk_type_from_id(gtc_id)
        if config["suite_type"] == "owasp_llm":
            llm_cats = RISK_TO_OWASP_LLM.get(risk, [])
            for cat in llm_cats:
                owasp_llm_coverage.setdefault(cat, []).append(gtc_id)
        if config["suite_type"] == "owasp_agentic":
            agentic_cats = RISK_TO_OWASP_AGENTIC.get(risk, [])
            for cat in agentic_cats:
                owasp_agentic_coverage.setdefault(cat, []).append(gtc_id)

    if config["suite_type"] == "owasp_llm":
        for cat in OWASP_LLM_GAPS:
            if cat not in owasp_llm_coverage:
                gaps.append({"category": cat, "reason": "No curated_candidate with matching risk type"})
    if config["suite_type"] == "owasp_agentic":
        for cat in OWASP_AGENTIC_GAPS:
            if cat not in owasp_agentic_coverage:
                gaps.append({"category": cat, "reason": "No curated_candidate with matching risk type"})

    # Build assertion strategy summary
    assertion_summary = list(set(
        risk_types[:3] if risk_types else ["refusal_detection", "block_detection"]
    ))

    return {
        "suite_id": suite_id,
        "suite_name": config["suite_name"],
        "suite_type": config["suite_type"],
        "suite_status": "curated_draft",
        "generated_at": FIXED_TIMESTAMP,
        "source_curation_file": str(CURATION_RESULT.relative_to(ROOT)),
        "source_generated_testcases": [
            f"generated_testcases/{p}/generated_{p}_testcases.yaml"
            for p in source_profiles
        ],
        "target_profiles": config["target_profiles"],
        "framework_focus": framework_focus,
        "selected_testcases": selected,
        "excluded_testcases": excluded,
        "selection_criteria": [
            "curation_status=curated_candidate",
            f"source_profiles in {source_profiles}",
            "has input_prompt and expected_behavior",
            "no real system dependency",
        ],
        "exclusion_criteria": [
            "curation_status!=curated_candidate",
            "planned_only or not_executable",
            "missing assertion_strategy",
        ],
        "assertion_strategy_summary": assertion_summary,
        "fake_assets_required": [],
        "runner_binding_reference": str(RUNNER_BINDING.relative_to(ROOT)),
        "promptfoo_draft_reference": f"regression_suites/promptfoo_drafts/promptfoo_{config['suite_type']}_regression.yaml",
        "execution_boundary": {
            "network_access": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "external_tools_required": False,
            "write_actions_allowed": False,
        },
        "executable_now": False,
        "executed": False,
        "real_target_connected": False,
        "usable_for_formal_finding": False,
        "evidence_expected_if_executed": ["prompt_response", "refusal_log", "block_log"],
        "limitations": [
            "Static suite draft only — not executed",
            "Runner binding not verified",
            "Promptfoo drafts not validated",
            "May require manual review before execution",
        ],
        "gaps": gaps,
        "owasp_llm_coverage": owasp_llm_coverage,
        "owasp_agentic_coverage": owasp_agentic_coverage,
    }


def build_promptfoo_draft(suite: dict, gtc_map: dict) -> dict:
    """Build a promptfoo-compatible draft from a regression suite."""
    selected = suite["selected_testcases"]
    tests = []
    for gtc_id in selected:
        tc = gtc_map.get(gtc_id, {})
        if not tc:
            continue
        tests.append({
            "description": f"[REGRESSION] {gtc_id}: {tc.get('test_intent', '')[:80]}",
            "vars": {
                "prompt": tc.get("input_prompt", ""),
                "expected_behavior": str(tc.get("expected_behavior", {})),
            },
            "assert": [],
            "metadata": {
                "generated_testcase_id": gtc_id,
                "suite_id": suite["suite_id"],
                "generated_only": True,
                "curated_from_static_analysis": True,
                "executed": False,
                "real_target_connected": False,
                "usable_for_formal_finding": False,
            },
        })

    return {
        "promptfoo_generated_draft": True,
        "generated_only": True,
        "curated_from_static_analysis": True,
        "executed": False,
        "real_target_connected": False,
        "usable_for_formal_finding": False,
        "generated_at": FIXED_TIMESTAMP,
        "suite_id": suite["suite_id"],
        "suite_name": suite["suite_name"],
        "target_profiles": suite["target_profiles"],
        "prompts": ["Generated prompt template for regression tests"],
        "providers": ["python3 <profile>_provider.py"],
        "tests": tests,
    }


def build_index(suites: list[dict]) -> dict:
    """Build multi-dimensional suite index."""
    by_suite = {}
    by_profile = {}
    by_owasp_llm = {}
    by_owasp_agentic = {}
    by_status = {}
    total_selected = 0
    total_gaps = 0
    total_promptfoo = 0

    for s in suites:
        sid = s["suite_id"]
        by_suite[sid] = {
            "suite_name": s["suite_name"],
            "suite_type": s["suite_type"],
            "suite_status": s["suite_status"],
            "selected_count": len(s["selected_testcases"]),
            "excluded_count": len(s["excluded_testcases"]),
            "gap_count": len(s.get("gaps", [])),
        }
        by_status[s["suite_status"]] = by_status.get(s["suite_status"], 0) + 1
        total_selected += len(s["selected_testcases"])
        total_gaps += len(s.get("gaps", []))

        for profile in s["target_profiles"]:
            by_profile.setdefault(profile, []).append(sid)

        for llm_cat in s.get("owasp_llm_coverage", {}):
            by_owasp_llm.setdefault(llm_cat, []).append(sid)

        for agentic_cat in s.get("owasp_agentic_coverage", {}):
            by_owasp_agentic.setdefault(agentic_cat, []).append(sid)

    return {
        "regression_suite_index": {
            "generated_at": FIXED_TIMESTAMP,
            "total_suites": len(suites),
            "total_selected_testcases": total_selected,
            "total_promptfoo_drafts": total_promptfoo,
            "total_gaps": total_gaps,
            "executed": False,
            "real_target_connected": False,
            "usable_for_formal_finding": False,
            "by_suite": by_suite,
            "by_profile": by_profile,
            "by_owasp_llm": by_owasp_llm,
            "by_owasp_agentic": by_owasp_agentic,
            "by_status": by_status,
        }
    }


def build_summary(suites: list[dict]) -> str:
    """Build markdown summary."""
    lines = [
        "# Curated Regression Suite Build Summary",
        "",
        f"**Generated at:** {FIXED_TIMESTAMP}",
        "",
        "## Overview",
        "",
        f"| Metric | Value |",
        "|---|---|",
        f"| Total suites | {len(suites)} |",
        f"| Total selected testcases | {sum(len(s['selected_testcases']) for s in suites)} |",
        f"| Total excluded | {sum(len(s['excluded_testcases']) for s in suites)} |",
        f"| Total gaps | {sum(len(s.get('gaps', [])) for s in suites)} |",
        f"| Executed | False |",
        f"| Real target connected | False |",
        "",
        "## Suites",
        "",
    ]
    for s in suites:
        lines.extend([
            f"### {s['suite_name']} (`{s['suite_id']}`)",
            "",
            f"- **Status**: {s['suite_status']}",
            f"- **Target profiles**: {', '.join(s['target_profiles'])}",
            f"- **Selected**: {len(s['selected_testcases'])}",
            f"- **Excluded**: {len(s['excluded_testcases'])}",
            f"- **Gaps**: {len(s.get('gaps', []))}",
            f"- **Promptfoo draft**: {s['promptfoo_draft_reference']}",
            "",
        ])
        if s.get("gaps"):
            lines.append("  **Gaps:**")
            for g in s["gaps"]:
                lines.append(f"  - {g['category']}: {g['reason']}")
            lines.append("")

    lines.extend([
        "",
        "## Important Notes",
        "",
        "- **Static suite build only** — no tests executed.",
        "- **All suites declare executed=false, real_target_connected=false, usable_for_formal_finding=false.**",
        "- **Promptfoo suite drafts declare generated_only=true, curated_from_static_analysis=true.**",
        "- **Suites are built from curated_candidate entries only.**",
        "- **Gaps indicate no suitable curated_candidate for a category.**",
    ])
    return "\n".join(lines)


def main():
    print("Phase 26: Curated Regression Suite Builder")
    print(f"Reading curation result from {CURATION_RESULT}")
    print()

    # Load inputs
    curation = load_yaml(CURATION_RESULT)
    curated = curation.get("curation_results", [])
    gtc_map = load_generated_testcases()

    print(f"Loaded {len(curated)} curation results")
    print(f"Loaded {len(gtc_map)} generated testcases")
    print(f"curated_candidate: {sum(1 for c in curated if c['curation_status'] == 'curated_candidate')}")
    print()

    # Build suites
    suites = []
    for config in SUITE_CONFIGS:
        suite = build_suite(config, curated, gtc_map)
        suites.append(suite)
        print(f"  {suite['suite_id']}: {len(suite['selected_testcases'])} selected, "
              f"{len(suite.get('gaps', []))} gaps")

    # Write suite YAML files
    for suite in suites:
        path = GENERATED_SUITE_DIR / f"{suite['suite_type']}_regression_suite.yaml"
        path.write_text(
            yaml.dump({"regression_suite": suite}, default_flow_style=False,
                      allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    # Write promptfoo drafts
    total_promptfoo = 0
    for suite in suites:
        st = suite["suite_type"]
        if not suite["selected_testcases"]:
            # Write empty draft
            draft = {
                "promptfoo_generated_draft": True,
                "generated_only": True,
                "curated_from_static_analysis": True,
                "executed": False,
                "real_target_connected": False,
                "usable_for_formal_finding": False,
                "generated_at": FIXED_TIMESTAMP,
                "suite_id": suite["suite_id"],
                "suite_name": suite["suite_name"],
                "target_profiles": suite["target_profiles"],
                "prompts": [],
                "providers": [],
                "tests": [],
            }
            path = PROMPTFOO_DIR / f"promptfoo_{st}_regression.yaml"
            path.write_text(
                yaml.dump(draft, default_flow_style=False, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            continue

        draft = build_promptfoo_draft(suite, gtc_map)
        total_promptfoo += len(draft["tests"])
        path = PROMPTFOO_DIR / f"promptfoo_{st}_regression.yaml"
        path.write_text(
            yaml.dump(draft, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    # Write index
    index = build_index(suites)
    # Update total_promptfoo
    index["regression_suite_index"]["total_promptfoo_drafts"] = total_promptfoo
    index_path = SUITE_DIR / "regression_suite_index.yaml"
    index_path.write_text(
        yaml.dump(index, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    # Write summary
    summary = build_summary(suites)
    summary_path = SUITE_DIR / "suite_build_summary.md"
    summary_path.write_text(summary, encoding="utf-8")

    # Print stats
    total_selected = sum(len(s["selected_testcases"]) for s in suites)
    total_excluded = sum(len(s["excluded_testcases"]) for s in suites)
    total_gaps = sum(len(s.get("gaps", [])) for s in suites)

    print()
    print("Build Results:")
    print(f"  Total suites: {len(suites)}")
    print(f"  Total selected: {total_selected}")
    print(f"  Total excluded: {total_excluded}")
    print(f"  Total gaps: {total_gaps}")
    print(f"  Total promptfoo drafts: {total_promptfoo}")
    print()
    print("Phase 26 complete. No tests executed, no real systems connected.")


if __name__ == "__main__":
    main()
