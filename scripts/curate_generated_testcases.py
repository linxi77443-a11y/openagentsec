#!/usr/bin/env python3
"""Phase 25: Generated Testcase Curation & Runner Binding.

Reads generated testcases and performs static classification:
- curated_candidate: passes static filters, ready for next phase
- manual_review_required: needs human review
- planned_only: planned corpus entries
- not_executable: requires real system/tools
- duplicate_or_low_value: duplicate or low-value

Outputs:
- curation/generated_testcase_curation_result.yaml
- curation/curation_summary.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CURATION_DIR = ROOT / "curation"
GENERATED_DIR = ROOT / "generated_testcases"
CORPUS_INDEX = ROOT / "corpus" / "corpus_index.yaml"

FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"

# Risk types that require real external systems or tools
REAL_SYSTEM_RISKS = {
    "browser_automation",
    "real_api_access",
    "real_credential_access",
    "external_network_access",
}

# Risk types that are currently not executable
NOT_EXECUTABLE_TYPES = {
    "api",
    "workflow",
    "real_external_tool",
}

# Corpus statuses
PLANNED_STATUSES = {"planned", "reference_only", "documentation_only"}

# Assertion strategy quality: risk types that need custom assertions
PARTIAL_ASSERTION_RISKS = {
    "misinformation",
    "rag_poisoning",
    "vector_embedding_weakness",
    "fake_citation",
    "stale_knowledge",
    "unbounded_consumption",
}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        print(f"Warning: {path} not found, returning empty dict")
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def collect_generated_testcases() -> list[dict]:
    """Collect all generated testcases from profile directories."""
    profiles = ["chatbot", "rag", "agent", "api", "regression"]
    all_testcases = []
    for profile in profiles:
        path = GENERATED_DIR / profile / f"generated_{profile}_testcases.yaml"
        if not path.exists():
            continue
        data = load_yaml(path)
        key = f"generated_{profile}_testcases"
        entries = data.get(key, [])
        for entry in entries:
            entry["_source_file"] = str(path.relative_to(ROOT))
            entry["_source_profile"] = profile
        all_testcases.extend(entries)
    return all_testcases


def load_corpus_index() -> dict:
    """Load corpus index to check entry statuses."""
    return load_yaml(CORPUS_INDEX)


def get_corpus_status(corpus_id: str, corpus_index: dict) -> str:
    """Look up a corpus entry's current_status from the corpus index."""
    by_profile = corpus_index.get("corpus_index", {}).get("by_profile", {})
    for _profile, entries in by_profile.items():
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, dict) and entry.get("corpus_id") == corpus_id:
                    return entry.get("current_status", "unknown")
    return "unknown"


def curate_testcase(tc: dict, corpus_index: dict) -> dict:
    """Perform static curation on a single generated testcase.

    Classification rules:
    - curated_candidate: active/regression corpus, has input_prompt,
      expected_behavior, risk_signals, at least one framework mapping,
      does not require real system
    - manual_review_required: missing assertion_strategy, missing
      fake_assets_required, incomplete risk_signals, partial assertion quality
    - planned_only: source corpus is planned/reference/documentation
    - not_executable: requires real external system/tools/browser
    - duplicate_or_low_value: generic warning without clear expected behavior
    """
    gtc_id = tc.get("generated_testcase_id", "unknown")
    profile = tc.get("_source_profile", "unknown")
    corpus_id = tc.get("source_corpus_id", "")
    target_type = tc.get("target_type", "")
    execution_mode = tc.get("execution_mode", "")
    runner_compat = tc.get("runner_compatibility", [])

    # Get corpus entry status
    corpus_status = get_corpus_status(corpus_id, corpus_index)

    # Basic field checks
    has_input = bool(tc.get("input_prompt"))
    has_expected = bool(tc.get("expected_behavior"))
    has_risk_signals = bool(tc.get("risk_signals"))
    has_framework = bool(
        tc.get("owasp_llm_mapping")
        or tc.get("owasp_agentic_mapping")
        or tc.get("mitre_atlas_mapping")
    )
    has_assertion = bool(tc.get("assertion_strategy"))
    has_fake_assets = tc.get("fake_assets_required") is not None
    promptfoo_ready = tc.get("promptfoo_compatible", False)

    # Determine assertion quality
    risk_signals = tc.get("risk_signals", [])
    assertion_quality = "clear"
    missing_reqs = []

    if not has_assertion:
        assertion_quality = "missing"
        missing_reqs.append("assertion_strategy")
    elif any(risk in str(risk_signals) for risk in PARTIAL_ASSERTION_RISKS):
        if not has_assertion:
            assertion_quality = "partial"
            missing_reqs.append("partial_assertion_coverage")

    if not has_fake_assets:
        missing_reqs.append("fake_assets_required")

    # Check if requires real system
    requires_real_system = False
    for risk in REAL_SYSTEM_RISKS:
        if risk in str(runner_compat).lower() or risk in execution_mode.lower():
            requires_real_system = True
            break

    # Check if target type is not_executable
    is_not_executable = target_type in NOT_EXECUTABLE_TYPES or (profile == "api" and execution_mode != "api_provider_future_or_skeleton")

    # Determine curation status
    curation_status = "curated_candidate"
    reason = "Passes static filters"
    recommended_action = "Add to runner binding draft"

    if requires_real_system or is_not_executable:
        curation_status = "not_executable"
        reason = "Requires real external system or API"
        recommended_action = "Wait for API provider or external tool integration"

    elif corpus_status in PLANNED_STATUSES:
        curation_status = "planned_only"
        reason = f"Source corpus status is '{corpus_status}'"
        recommended_action = "Wait until corpus entry is active"

    elif not has_input or not has_expected:
        curation_status = "manual_review_required"
        reason = "Missing input_prompt or expected_behavior"
        recommended_action = "Review and complete required fields"

    elif not has_risk_signals:
        curation_status = "manual_review_required"
        reason = "Missing risk_signals"
        recommended_action = "Review and define risk signals"

    elif not has_framework:
        curation_status = "manual_review_required"
        reason = "Missing framework mapping (OWASP/ATLAS)"
        recommended_action = "Review and add framework mapping"

    elif assertion_quality in ("partial", "missing"):
        curation_status = "manual_review_required"
        reason = f"Assertion quality is '{assertion_quality}'"
        recommended_action = "Review assertion strategy"

    elif not has_fake_assets:
        curation_status = "manual_review_required"
        reason = "Missing fake_assets_required"
        recommended_action = "Review and define required fake assets"

    # Check for duplicates/low value: generic warning without clear expected behavior
    expected = tc.get("expected_behavior", {})
    if isinstance(expected, dict):
        has_specific_check = any(
            key in expected
            for key in [
                "should_refuse",
                "should_block",
                "should_not_reveal_system_prompt",
                "should_not_leak_sensitive_data",
                "should_not_call_unauthorized_tool",
            ]
        )
        if not has_specific_check and curation_status == "curated_candidate":
            curation_status = "manual_review_required"
            reason = "Expected behavior lacks specific check flags"
            recommended_action = "Review expected behavior detail"

    # Provider compatibility
    if promptfoo_ready and profile in ("chatbot", "rag", "agent"):
        provider_compat = "compatible"
    elif profile == "api":
        provider_compat = "incompatible"
    else:
        provider_compat = "partial"

    # Runner binding status
    if promptfoo_ready and profile in ("chatbot", "rag", "agent", "regression"):
        binding_status = "bound"
    elif profile == "api":
        binding_status = "unbound"
    else:
        binding_status = "partial"

    # Fake asset dependency
    if profile == "agent":
        fake_dep = "required"
    elif profile == "rag":
        fake_dep = "partial"
    else:
        fake_dep = "none"

    return {
        "generated_testcase_id": gtc_id,
        "source_corpus_id": corpus_id,
        "source_profile": tc.get("_source_profile", ""),
        "source_file": tc.get("_source_file", ""),
        "target_profile": tc.get("target_profile", ""),
        "owasp_llm_mapping": tc.get("owasp_llm_mapping", []),
        "owasp_agentic_mapping": tc.get("owasp_agentic_mapping", []),
        "mitre_atlas_mapping": tc.get("mitre_atlas_mapping", []),
        "curation_status": curation_status,
        "reason": reason,
        "missing_requirements": missing_reqs,
        "assertion_quality": assertion_quality,
        "provider_compatibility": provider_compat,
        "fake_asset_dependency": fake_dep,
        "runner_binding_status": binding_status,
        "recommended_next_action": recommended_action,
        "usable_for_formal_finding": False,
        "executed": False,
        "real_target_connected": False,
    }


def build_summary(curation_results: list[dict]) -> str:
    """Build curation summary markdown."""
    status_counts: dict[str, int] = {}
    profile_counts: dict[str, dict[str, int]] = {}

    for cr in curation_results:
        status = cr["curation_status"]
        status_counts[status] = status_counts.get(status, 0) + 1

        profile = cr["source_profile"]
        if profile not in profile_counts:
            profile_counts[profile] = {}
        profile_counts[profile][status] = profile_counts[profile].get(status, 0) + 1

    by_profile_lines = []
    for profile in sorted(profile_counts.keys()):
        parts = [f"  - {profile}:"]
        for status in ["curated_candidate", "manual_review_required", "planned_only", "not_executable", "duplicate_or_low_value"]:
            count = profile_counts[profile].get(status, 0)
            if count > 0:
                parts.append(f"    - {status}: {count}")
        by_profile_lines.append("\n".join(parts))

    lines = [
        f"# Generated Testcase Curation Summary",
        "",
        f"**Generated at:** {FIXED_TIMESTAMP}",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total curated testcases | {len(curation_results)} |",
        f"| curated_candidate | {status_counts.get('curated_candidate', 0)} |",
        f"| manual_review_required | {status_counts.get('manual_review_required', 0)} |",
        f"| planned_only | {status_counts.get('planned_only', 0)} |",
        f"| not_executable | {status_counts.get('not_executable', 0)} |",
        f"| duplicate_or_low_value | {status_counts.get('duplicate_or_low_value', 0)} |",
        "",
        "## By Profile",
        "",
        *by_profile_lines,
        "",
        "## Important Notes",
        "",
        "- **Curation is static classification only** — no tests executed.",
        "- **All entries declare executed=false, real_target_connected=false, usable_for_formal_finding=false.**",
        "- **curated_candidate** means the testcase passes static filters but still requires manual runner binding review before execution.",
        "- **manual_review_required** means the testcase has incomplete fields or ambiguous semantics.",
        "- **not_executable** means the testcase requires a real external system, API, or tool that is not available.",
        "- **Runner binding is a draft recommendation** — not a validated runner configuration.",
    ]
    return "\n".join(lines)


def main():
    print("Phase 25: Generated Testcase Curation & Runner Binding")
    print(f"Reading generated testcases from {GENERATED_DIR}")
    print()

    # Load inputs
    all_testcases = collect_generated_testcases()
    corpus_index = load_corpus_index()

    print(f"Collected {len(all_testcases)} generated testcases")
    print()

    # Curate each testcase
    curation_results = []
    for tc in all_testcases:
        cr = curate_testcase(tc, corpus_index)
        curation_results.append(cr)

    # Build output structure
    output = {
        "curation_generated_at": FIXED_TIMESTAMP,
        "curation_only": True,
        "executed": False,
        "real_target_connected": False,
        "usable_for_formal_finding": False,
        "total_curated": len(curation_results),
        "curation_results": curation_results,
    }

    # Write curation result
    result_path = CURATION_DIR / "generated_testcase_curation_result.yaml"
    CURATION_DIR.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        yaml.dump(output, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Written: {result_path}")

    # Write summary
    summary = build_summary(curation_results)
    summary_path = CURATION_DIR / "curation_summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"Written: {summary_path}")

    # Print stats
    status_counts: dict[str, int] = {}
    for cr in curation_results:
        status = cr["curation_status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    print()
    print("Curation Results:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print(f"  Total: {len(curation_results)}")

    print()
    print("Phase 25 curation complete. No tests executed, no real systems connected.")


if __name__ == "__main__":
    main()
