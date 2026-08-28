#!/usr/bin/env python3
"""Corpus-to-Testcase Compiler — Phase 24.

Reads corpus/ YAML files, selects active/regression entries, and generates:
1. Standardized testcases per profile (YAML)
2. Promptfoo-compatible draft test sets (YAML)
3. Generated testcase index (YAML)
4. Corpus compile coverage summary (Markdown)

All generated files declare:
  generated_only: true
  executed: false
  real_target_connected: false
  usable_for_formal_finding: false
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required for local YAML parsing") from exc

ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "generated_testcases"
CORPUS_DIR = ROOT / "corpus"
CORPUS_INDEX_PATH = ROOT / "corpus/corpus_index.yaml"

# Statuses that are compilable
COMPILABLE_STATUSES = {"active", "regression", "regression_candidate"}

# Statuses that are NOT compilable
PLANNED_STATUSES = {"planned", "reference_only", "documentation_only"}

FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"

PROFILE_DIR_MAP = {
    "chatbot": "chatbot",
    "rag": "rag",
    "agent": "agent",
    "generic_agent": "agent",
    "api": "api",
    "workflow": "api",
    "regression": "regression",
}

PROMPTFOO_PROVIDER_MAP = {
    "chatbot": "python3 chatbot_provider.py",
    "rag": "python3 rag_provider.py",
    "agent": "python3 agent_provider.py",
    "api": "python3 api_provider.py",
    "regression": "python3 chatbot_provider.py",
}


def read_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def infer_target_type(profile: str) -> str:
    mapping = {
        "chatbot": "chat",
        "rag": "rag_retrieval",
        "agent": "agent_tool",
        "generic_agent": "agent_tool",
        "api": "api_endpoint",
        "workflow": "api_workflow",
        "regression": "chat",
        "business": "chat",
    }
    return mapping.get(profile, "unknown")


def map_assertion_strategy(expected: dict[str, Any]) -> str:
    """Map expected_behavior fields to assertion strategy."""
    if not expected:
        return "manual_review"
    strategies = []
    if expected.get("should_refuse"):
        strategies.append("refusal_detection")
    if expected.get("should_block"):
        strategies.append("block_detection")
    if expected.get("should_not_reveal_system_prompt"):
        strategies.append("system_prompt_protection")
    if expected.get("should_not_leak_sensitive_data"):
        strategies.append("data_leakage_detection")
    if expected.get("should_not_call_unauthorized_tool"):
        strategies.append("tool_authorization_check")
    if expected.get("should_not_write_memory"):
        strategies.append("memory_write_block")
    if expected.get("should_detect_conflict"):
        strategies.append("conflict_detection")
    if expected.get("should_flag_outdated"):
        strategies.append("staleness_detection")
    if expected.get("should_not_fabricate"):
        strategies.append("hallucination_detection")
    if expected.get("should_not_follow_hidden"):
        strategies.append("hidden_instruction_detection")
    if expected.get("should_not_exceed_quota"):
        strategies.append("quota_enforcement_check")
    if expected.get("should_limit_tokens"):
        strategies.append("token_limit_check")
    return ", ".join(strategies) if strategies else "manual_review"


def infer_runner_compatibility(profile: str, execution_mode: str) -> list[str]:
    runners = []
    if profile == "chatbot":
        runners.append("runners/run_promptfoo.sh --profile chatbot")
    elif profile == "rag":
        runners.append("runners/run_rag_promptfoo.sh --profile rag")
    elif profile == "agent" or profile == "generic_agent":
        runners.append("runners/run_agent_promptfoo.sh --profile agent")
        runners.append("runners/run_generic_agent_harness.sh")
    elif profile == "api":
        runners.append("API Provider Skeleton (dry-run only)")
    elif profile == "regression":
        runners.append("runners/run_promptfoo.sh --profile chatbot")
    if execution_mode == "manual_replay":
        runners.append("runners/run_manual_ui_promptfoo.sh")
    return runners


def extract_context_required(entry: dict) -> str:
    inp = entry.get("input", {})
    if inp.get("document_context_optional"):
        return "document_context"
    if inp.get("tool_context_optional"):
        return "tool_context"
    if inp.get("system_context_optional"):
        return "system_context"
    return "none"


def extract_fake_assets(entry: dict) -> list[str]:
    assets = entry.get("test_assets", {})
    result = []
    if assets.get("fake_documents"):
        result.append("fake_documents")
    if assets.get("fake_tools"):
        result.append("fake_tools")
    if assets.get("fake_memory"):
        result.append("fake_memory")
    if assets.get("fake_secret"):
        result.append("fake_secret")
    if assets.get("fake_external_channel"):
        result.append("fake_external_channel")
    return result


def extract_owasp_llm(entry: dict) -> list[str]:
    fm = entry.get("framework_mapping", {})
    val = fm.get("owasp_llm")
    if val:
        return [val]
    return []


def extract_owasp_agentic(entry: dict) -> list[str]:
    fm = entry.get("framework_mapping", {})
    val = fm.get("owasp_agentic")
    if val:
        return [val]
    return []


def extract_atlas(entry: dict) -> list[str]:
    fm = entry.get("framework_mapping", {})
    return listify(fm.get("mitre_atlas"))


# ---------------------------------------------------------------------------
# Collect all corpus entries
# ---------------------------------------------------------------------------


def collect_corpus_entries() -> tuple[list[dict], list[dict], list[dict], dict[str, Any]]:
    """Returns (compilable_entries, planned_entries, all_entries, stats)."""
    corpus_index = read_yaml(CORPUS_INDEX_PATH) or {}
    profile_data = corpus_index.get("corpus_index", {}).get("by_profile", {})

    all_entries: list[dict] = []
    compilable_entries: list[dict] = []
    planned_entries: list[dict] = []
    missing_field_entries: list[dict] = []

    for profile_name, data in profile_data.items():
        for file_info in data.get("files", []):
            path = CORPUS_DIR.parent / file_info["path"]
            if not path.exists():
                continue
            yaml_data = read_yaml(path)
            for entry in yaml_data.get("corpus", yaml_data.get("entries", [])):
                entry["_source_file"] = file_info["path"]
                entry["_profile"] = profile_name
                all_entries.append(entry)

                status = entry.get("current_status", entry.get("status", "unknown"))

                if status in COMPILABLE_STATUSES:
                    # Check for required fields
                    missing = []
                    for field in ["corpus_id", "test_intent", "expected_behavior"]:
                        if field not in entry or entry.get(field) is None:
                            missing.append(field)
                    # input might be nested or string
                    inp = entry.get("input", {})
                    if isinstance(inp, dict) and not inp.get("user_prompt"):
                        if not entry.get("input"):
                            missing.append("input")
                    elif isinstance(inp, str) and not inp:
                        missing.append("input")

                    if missing:
                        entry["_missing_fields"] = missing
                        missing_field_entries.append(entry)
                    else:
                        compilable_entries.append(entry)
                elif status in PLANNED_STATUSES:
                    planned_entries.append(entry)
                else:
                    planned_entries.append(entry)

    all_count = len(all_entries)
    compilable_count = len(compilable_entries)
    planned_count = len(planned_entries)
    missing_count = len(missing_field_entries)
    manual_review_count = missing_count

    stats = {
        "total_corpus": all_count,
        "compilable_corpus": compilable_count,
        "planned_corpus": planned_count,
        "missing_field_corpus": missing_count,
        "manual_review_required": manual_review_count,
    }

    return compilable_entries, planned_entries, missing_field_entries, stats


# ---------------------------------------------------------------------------
# Generate testcase for one corpus entry
# ---------------------------------------------------------------------------


def generate_testcase(entry: dict) -> dict:
    profile = entry.get("target_profile") or entry.get("_profile", "unknown")
    execution_mode = entry.get("current_execution_mode", "planned")
    inp = entry.get("input", {})
    if isinstance(inp, str):
        user_prompt = inp
    else:
        user_prompt = inp.get("user_prompt", "")

    expected = entry.get("expected_behavior", {})
    if isinstance(expected, str):
        expected = {"should_refuse": True}

    corpus_id = entry.get("corpus_id", entry.get("id", "unknown"))

    testcase = {
        "generated_testcase_id": f"gtc_{corpus_id}",
        "source_corpus_id": corpus_id,
        "source_corpus_file": entry.get("_source_file", ""),
        "target_profile": profile,
        "target_type": infer_target_type(profile),
        "owasp_llm_mapping": extract_owasp_llm(entry),
        "owasp_agentic_mapping": extract_owasp_agentic(entry),
        "mitre_atlas_mapping": extract_atlas(entry),
        "test_intent": entry.get("test_intent", ""),
        "input_prompt": user_prompt,
        "context_required": extract_context_required(entry),
        "fake_assets_required": extract_fake_assets(entry),
        "expected_behavior": entry.get("expected_behavior", ""),
        "risk_signals": listify(entry.get("risk_signals", [])),
        "assertion_strategy": map_assertion_strategy(expected),
        "severity_if_failed": entry.get("severity_if_failed", "medium"),
        "execution_mode": execution_mode,
        "runner_compatibility": infer_runner_compatibility(profile, execution_mode),
        "promptfoo_compatible": execution_mode == "local_sandbox",
        "generated_status": "generated_draft",
        "executable_now": False,
        "evidence_expected": listify(entry.get("evidence_mapping", "")),
        "limitations": [
            "Generated testcase — not executed",
            "No real target connected",
            "Not usable for formal finding without execution",
        ],
        "generated_only": True,
        "executed": False,
        "real_target_connected": False,
        "usable_for_formal_finding": False,
    }

    # Mark as promptfoo_ready if execution_mode is local_sandbox
    if execution_mode == "local_sandbox" and profile != "api":
        testcase["generated_status"] = "promptfoo_ready"

    # Mark API entries as future/skeleton (not real executable)
    if profile == "api":
        testcase["generated_status"] = "api_provider_future_or_skeleton"
        testcase["execution_mode"] = "api_provider_future_or_skeleton"

    return testcase


def generate_promptfoo_entry(testcase: dict) -> dict:
    """Generate a promptfoo-compatible test entry."""
    description = f"[GENERATED] {testcase['source_corpus_id']}: {testcase['test_intent'][:80]}"
    return {
        "description": description,
        "vars": {
            "prompt": testcase["input_prompt"],
            "expected_behavior": testcase["expected_behavior"] if isinstance(testcase["expected_behavior"], str) else str(testcase["expected_behavior"]),
        },
        "assert": [],
        "metadata": {
            "generated_testcase_id": testcase["generated_testcase_id"],
            "source_corpus_id": testcase["source_corpus_id"],
            "generated_only": True,
            "executed": False,
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    compilable_entries, planned_entries, missing_field_entries, stats = collect_corpus_entries()

    # Group by profile
    profile_groups: dict[str, list[dict]] = {}
    for entry in compilable_entries:
        profile = entry.get("target_profile") or entry.get("_profile", "unknown")
        mapped_profile = PROFILE_DIR_MAP.get(profile, profile)
        profile_groups.setdefault(mapped_profile, []).append(entry)

    # Also add business entries to chatbot since there's no business dir
    for entry in compilable_entries:
        profile = entry.get("target_profile") or entry.get("_profile", "unknown")
        if profile == "business":
            profile_groups.setdefault("chatbot", []).append(entry)

    # Generate testcases and promptfoo drafts per profile
    generated_testcases: list[dict] = []
    promptfoo_drafts: list[dict] = []

    for profile_dir in ["chatbot", "rag", "agent", "api", "regression"]:
        entries = profile_groups.get(profile_dir, [])
        testcases = [generate_testcase(e) for e in entries]
        generated_testcases.extend(testcases)

        # Write generated testcases YAML
        testcase_path = GENERATED_DIR / profile_dir / f"generated_{profile_dir}_testcases.yaml"
        testcase_data = {
            "generated_only": True,
            "executed": False,
            "real_target_connected": False,
            "usable_for_formal_finding": False,
            "generated_at": FIXED_TIMESTAMP,
            "source_profiles": [profile_dir],
            f"generated_{profile_dir}_testcases": testcases,
        }
        testcase_path.write_text(
            yaml.dump(testcase_data, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        print(f"Generated: {testcase_path.relative_to(ROOT)}")

        # Generate promptfoo-compatible draft
        pf_entries = []
        for tc in testcases:
            if tc.get("promptfoo_compatible") and tc["generated_status"] != "not_executable":
                pf_entries.append(generate_promptfoo_entry(tc))

        pf_path = GENERATED_DIR / profile_dir / f"promptfoo_{profile_dir}_generated.yaml"
        provider = PROMPTFOO_PROVIDER_MAP.get(profile_dir, "python3 default_provider.py")
        pf_data = {
            "promptfoo_generated_draft": True,
            "generated_only": True,
            "executed": False,
            "real_target_connected": False,
            "usable_for_formal_finding": False,
            "generated_at": FIXED_TIMESTAMP,
            "target": f"local_{profile_dir}",
            "prompts": [f"Generated prompt template for {profile_dir} tests"],
            "providers": [provider],
            "tests": pf_entries,
        }
        pf_path.write_text(
            yaml.dump(pf_data, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        print(f"Generated: {pf_path.relative_to(ROOT)}")
        promptfoo_drafts.extend(pf_entries)

    # Generate index
    index = build_index(generated_testcases, stats, promptfoo_drafts)
    index_path = GENERATED_DIR / "generated_testcase_index.yaml"
    index_path.write_text(
        yaml.dump(index, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Generated: {index_path.relative_to(ROOT)}")

    # Generate summary
    summary = build_summary(generated_testcases, stats, promptfoo_drafts)
    summary_path = GENERATED_DIR / "generated_testcase_summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"Generated: {summary_path.relative_to(ROOT)}")

    print(f"\nTotal: {len(generated_testcases)} generated testcases, {len(promptfoo_drafts)} promptfoo drafts")
    print(f"Manual review required: {stats['manual_review_required']}")
    print("All files are generated drafts. No tests executed. No real systems connected.")


# ---------------------------------------------------------------------------
# Index builder
# ---------------------------------------------------------------------------


def build_index(
    testcases: list[dict],
    stats: dict[str, int],
    promptfoo_drafts: list[dict],
) -> dict:
    index: dict[str, Any] = {
        "generated_testcase_index": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_generated_testcases": len(testcases),
            "total_promptfoo_drafts": len(promptfoo_drafts),
            "stats": stats,
            "by_profile": {},
            "by_owasp_llm": {},
            "by_owasp_agentic": {},
            "by_atlas_technique": {},
            "by_execution_mode": {},
            "by_runner_compatibility": {},
            "by_generated_status": {},
            "by_manual_review_required": [],
            "by_gap": [],
        }
    }
    idx = index["generated_testcase_index"]

    for tc in testcases:
        pid = tc["generated_testcase_id"]
        profile = tc["target_profile"]

        # by_profile
        idx["by_profile"].setdefault(profile, []).append(pid)

        # by_owasp_llm
        for llm in tc.get("owasp_llm_mapping", []):
            idx["by_owasp_llm"].setdefault(llm, []).append(pid)

        # by_owasp_agentic
        for ag in tc.get("owasp_agentic_mapping", []):
            idx["by_owasp_agentic"].setdefault(ag, []).append(pid)

        # by_atlas_technique
        for atlas in tc.get("mitre_atlas_mapping", []):
            idx["by_atlas_technique"].setdefault(atlas, []).append(pid)

        # by_execution_mode
        mode = tc.get("execution_mode", "unknown")
        idx["by_execution_mode"].setdefault(mode, []).append(pid)

        # by_runner_compatibility
        for runner in tc.get("runner_compatibility", []):
            idx["by_runner_compatibility"].setdefault(runner, []).append(pid)

        # by_generated_status
        status = tc.get("generated_status", "generated_draft")
        idx["by_generated_status"].setdefault(status, []).append(pid)

        # by_manual_review_required
        if tc.get("generated_status") == "manual_review_required":
            idx["by_manual_review_required"].append(pid)

    idx["by_gap"] = [
        f"Planned corpus not compiled: {stats['planned_corpus']} entries",
        f"Missing field entries: {stats['missing_field_corpus']}",
    ]

    return index


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------


def build_summary(
    testcases: list[dict],
    stats: dict[str, int],
    promptfoo_drafts: list[dict],
) -> str:
    # Count per profile
    profile_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    llm_counts: dict[str, int] = {}
    agentic_counts: dict[str, int] = {}
    mode_counts: dict[str, int] = {}

    for tc in testcases:
        profile = tc["target_profile"]
        profile_counts[profile] = profile_counts.get(profile, 0) + 1

        status = tc.get("generated_status", "generated_draft")
        status_counts[status] = status_counts.get(status, 0) + 1

        for llm in tc.get("owasp_llm_mapping", []):
            llm_counts[llm] = llm_counts.get(llm, 0) + 1

        for ag in tc.get("owasp_agentic_mapping", []):
            agentic_counts[ag] = agentic_counts.get(ag, 0) + 1

        mode = tc.get("execution_mode", "unknown")
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    lines = [
        "# Corpus Compile Coverage Summary",
        "",
        f"**Generated at:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Overview",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total corpus entries | {stats['total_corpus']} |",
        f"| Compilable corpus entries (active/regression) | {stats['compilable_corpus']} |",
        f"| Planned corpus entries (skipped) | {stats['planned_corpus']} |",
        f"| Missing field entries (manual review) | {stats['missing_field_corpus']} |",
        f"| Generated testcases | {len(testcases)} |",
        f"| Promptfoo draft entries | {len(promptfoo_drafts)} |",
        "",
        "## By Profile",
        "",
    ]
    for prof, cnt in sorted(profile_counts.items()):
        lines.append(f"- {prof}: {cnt}")
    lines.append("")

    # Profile breakdown with file paths
    lines.extend([
        "| Profile | Generated File | Promptfoo Draft |",
        "|---|---|---|",
    ])
    for prof in ["chatbot", "rag", "agent", "api", "regression"]:
        cnt = profile_counts.get(prof, 0)
        lines.append(f"| {prof} | `generated_testcases/{prof}/generated_{prof}_testcases.yaml` ({cnt}) | `generated_testcases/{prof}/promptfoo_{prof}_generated.yaml` |")

    lines.extend([
        "",
        "## By Generated Status",
        "",
    ])
    for status, cnt in sorted(status_counts.items()):
        lines.append(f"- {status}: {cnt}")

    lines.extend([
        "",
        "## By OWASP LLM",
        "",
    ])
    for llm, cnt in sorted(llm_counts.items()):
        lines.append(f"- {llm}: {cnt}")

    lines.extend([
        "",
        "## By OWASP Agentic",
        "",
    ])
    for ag, cnt in sorted(agentic_counts.items()):
        lines.append(f"- {ag}: {cnt}")

    lines.extend([
        "",
        "## By Execution Mode",
        "",
    ])
    for mode, cnt in sorted(mode_counts.items()):
        lines.append(f"- {mode}: {cnt}")

    lines.extend([
        "",
        "## Gaps",
        "",
        f"- Planned corpus entries not compiled: {stats['planned_corpus']}",
        f"- Missing field entries requiring manual review: {stats['missing_field_corpus']}",
        "- API corpus entries marked as not_executable (no runner available)",
        "- Business corpus entries not profiled (folded into chatbot)",
        "",
        "## Important Notes",
        "",
        "- **Generated testcases do not equal executed testcases**.",
        "- **Promptfoo drafts do not equal validated runners**.",
        "- **This phase does not produce real evidence**.",
        "- All files declare: executed=false, real_target_connected=false, usable_for_formal_finding=false.",
        "",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    main()
