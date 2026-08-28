#!/usr/bin/env python3
"""Phase 26.5: Regression Suite Gap Triage — Static Analysis.

Reads corpus, generated_testcases, curation, and regression_suite data
to trace why certain suites have 0 selected and why framework gaps exist.

Outputs:
  regression_suites/suite_gap_analysis.yaml
  regression_suites/suite_gap_analysis.md
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORPUS_INDEX = ROOT / "corpus" / "corpus_index.yaml"
GTC_INDEX = ROOT / "generated_testcases" / "generated_testcase_index.yaml"
CURATION_RESULT = ROOT / "curation" / "generated_testcase_curation_result.yaml"
SUITE_INDEX = ROOT / "regression_suites" / "regression_suite_index.yaml"
SUITE_BUILD_SUMMARY = ROOT / "regression_suites" / "suite_build_summary.md"

FIXED_TIMESTAMP = "2026-01-01T00:00:00Z"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> None:
    corpus = load_yaml(CORPUS_INDEX)
    gtc_idx = load_yaml(GTC_INDEX)
    curation = load_yaml(CURATION_RESULT)
    suite_idx = load_yaml(SUITE_INDEX)

    idx = gtc_idx.get("generated_testcase_index", gtc_idx)
    si = suite_idx.get("regression_suite_index", suite_idx)
    ci = corpus.get("corpus_index", corpus)

    # --- 1. Corpus profile counts ---
    corpus_by_profile = ci.get("by_profile", {})
    corpus_counts = {p: d.get("total", 0) for p, d in corpus_by_profile.items()}

    # --- 2. Generated testcase profile counts ---
    gtc_by_profile = idx.get("by_profile", {})
    gtc_counts = {p: len(v) for p, v in gtc_by_profile.items()}

    # --- 3. Curation profile x status ---
    curation_results = curation.get("curation_results", [])
    profile_status = {}  # profile -> {status: count}
    for c in curation_results:
        p = c.get("source_profile", "unknown")
        s = c.get("curation_status", "unknown")
        if p not in profile_status:
            profile_status[p] = {}
        profile_status[p][s] = profile_status[p].get(s, 0) + 1

    # --- 4. Suite summary ---
    by_suite = si.get("by_suite", {})

    # --- 5. Identify zero-selected suites ---
    zero_selected = {}
    for sid, sinfo in by_suite.items():
        if sinfo.get("selected_count", 0) == 0:
            zero_selected[sid] = sinfo

    # --- 6. Trace each zero-selected suite ---
    suite_configs = _get_suite_configs()

    zero_selected_analysis = {}
    for sid, sinfo in zero_selected.items():
        config = suite_configs.get(sid, {})
        src_profiles = config.get("source_profiles", [])
        risk_types = config.get("risk_types", [])

        # Check each source profile
        profile_analysis = {}
        for sp in src_profiles:
            curated = profile_status.get(sp, {}).get("curated_candidate", 0)
            manual = profile_status.get(sp, {}).get("manual_review_required", 0)
            total_gtc = gtc_counts.get(sp, 0)
            total_corpus = corpus_counts.get(sp, 0)

            # Check if any curated_candidate matches risk types
            matching_risk = 0
            for c in curation_results:
                if c.get("source_profile") != sp:
                    continue
                if c.get("curation_status") != "curated_candidate":
                    continue
                gid = c.get("generated_testcase_id", "")
                gid_risk = _risk_from_id(gid)
                if gid_risk in risk_types:
                    matching_risk += 1

            profile_analysis[sp] = {
                "corpus_entries": total_corpus,
                "generated_testcases": total_gtc,
                "curated_candidate": curated,
                "manual_review_required": manual,
                "matching_risk_type_curated_candidate": matching_risk,
            }

        root_causes = _determine_root_causes(sid, src_profiles, profile_analysis, risk_types)

        zero_selected_analysis[sid] = {
            "suite_name": sinfo.get("suite_name", sid),
            "suite_type": sinfo.get("suite_type", ""),
            "source_profiles": src_profiles,
            "risk_types_required": risk_types,
            "profile_analysis": profile_analysis,
            "root_causes": root_causes,
            "recommended_action": _recommend_action(root_causes),
        }

    # --- 7. Framework gap analysis ---
    owasp_llm_gaps = _analyze_owasp_llm_gaps(corpus, curation_results, gtc_counts)
    owasp_agentic_gaps = _analyze_owasp_agentic_gaps(corpus, curation_results, gtc_counts)

    # --- 8. Build output ---
    analysis = {
        "analysis_generated_at": FIXED_TIMESTAMP,
        "executed": False,
        "real_target_connected": False,
        "usable_for_formal_finding": False,
        "analysis_only": True,
        "summary": {
            "total_suites": len(by_suite),
            "zero_selected_suites": len(zero_selected),
            "zero_selected_suite_ids": sorted(zero_selected.keys()),
            "framework_gaps_llm": len(owasp_llm_gaps),
            "framework_gaps_agentic": len(owasp_agentic_gaps),
        },
        "profile_status_summary": {
            p: {"curated_candidate": d.get("curated_candidate", 0),
                "manual_review_required": d.get("manual_review_required", 0),
                "generated_testcases": gtc_counts.get(p, 0),
                "corpus_entries": corpus_counts.get(p, 0)}
            for p, d in sorted(profile_status.items())
        },
        "zero_selected_suite_analysis": zero_selected_analysis,
        "owasp_llm_gap_analysis": owasp_llm_gaps,
        "owasp_agentic_gap_analysis": owasp_agentic_gaps,
        "recommended_overall_action": "Proceed to Phase 27A: corpus/curation backfill for zero-selected suites and framework gaps; defer Phase 27 validator until curated_candidate coverage improves.",
    }

    # Write YAML
    yaml_path = ROOT / "regression_suites" / "suite_gap_analysis.yaml"
    _write_safe_yaml(yaml_path, analysis)

    # Write Markdown
    md_path = ROOT / "regression_suites" / "suite_gap_analysis.md"
    _write_markdown(md_path, analysis, by_suite, owasp_llm_gaps, owasp_agentic_gaps)

    print(f"Gap analysis written to:\n  {yaml_path}\n  {md_path}")
    print(f"\nZero-selected suites: {len(zero_selected)}")
    for sid in sorted(zero_selected):
        print(f"  {sid}")
    print(f"\nOWASP LLM gaps: {len(owasp_llm_gaps)}")
    for g in owasp_llm_gaps:
        print(f"  {g['gap_id']}: {g['root_cause']}")
    print(f"\nOWASP Agentic gaps: {len(owasp_agentic_gaps)}")
    for g in owasp_agentic_gaps:
        print(f"  {g['gap_id']}: {g['root_cause']}")


def _get_suite_configs() -> dict:
    """Return suite configs as a dict keyed by suite_id."""
    return {
        "suite_core_llm_regression": {
            "source_profiles": ["chatbot", "regression"],
            "risk_types": [
                "prompt_injection", "system_prompt_exposure",
                "sensitive_disclosure", "improper_output_handling",
                "misinformation", "unbounded_consumption",
            ],
        },
        "suite_chatbot_regression": {
            "source_profiles": ["chatbot", "regression"],
            "risk_types": [
                "prompt_injection", "system_prompt_exposure",
                "sensitive_disclosure", "multilingual_bypass", "misinformation",
            ],
        },
        "suite_api_regression": {
            "source_profiles": ["api"],
            "risk_types": ["api_security_baseline", "unbounded_consumption"],
        },
    }


def _risk_from_id(gtc_id: str) -> str:
    risk_map = {
        "pi": "prompt_injection", "spe": "system_prompt_exposure",
        "sd": "sensitive_disclosure", "mb": "multilingual_bypass",
        "ioh": "improper_output_handling", "mi": "misinformation",
        "ipi": "indirect_prompt_injection", "rp": "rag_poisoning",
        "fc": "fake_citation", "od": "over_disclosure",
        "vew": "vector_embedding_weakness", "sck": "stale_or_conflicting_knowledge",
        "tmu": "tool_misuse", "mp": "memory_poisoning",
        "sp": "skill_poisoning", "exf": "exfiltration",
        "rc": "resource_consumption", "uc": "unbounded_consumption",
        "asb": "api_security_baseline", "smoke": "api_smoke",
        "cs": "core_security_regression", "ga": "generic_agent_regression",
    }
    parts = gtc_id.split("-")
    for p in parts:
        if p in risk_map:
            return risk_map[p]
    return "unknown"


def _determine_root_causes(suite_id: str, src_profiles: list[str],
                           profile_analysis: dict, risk_types: list[str]) -> list[str]:
    causes = []
    for sp in src_profiles:
        pa = profile_analysis.get(sp, {})
        if pa.get("curated_candidate", 0) == 0:
            if pa.get("manual_review_required", 0) > 0:
                causes.append(f"Profile '{sp}': all {pa['manual_review_required']} generated testcases are manual_review_required — none passed curation filter")
            else:
                causes.append(f"Profile '{sp}': no generated testcases at all")
        else:
            mc = pa.get("matching_risk_type_curated_candidate", 0)
            if mc == 0:
                causes.append(f"Profile '{sp}': {pa['curated_candidate']} curated_candidate(s) exist but none match required risk types {risk_types}")

    if suite_id == "suite_api_regression":
        candidate_count = profile_analysis.get("api", {}).get("curated_candidate", 0)
        if candidate_count == 0:
            cause = profile_analysis.get("api", {}).get("manual_review_required", 0)
            if cause > 0:
                causes.append(f"Profile 'api': all {cause} generated testcases are manual_review_required — need field completion")
            else:
                causes.append("Profile 'api': no generated testcases or API entries still not compilable")

    if not causes:
        causes.append("Unknown — requires deeper investigation")

    return causes


def _recommend_action(causes: list[str]) -> str:
    combined = " ".join(causes).lower()
    if "no generated testcases" in combined or "nothing to curate" in combined:
        return "backfill_corpus_fields"
    if "manual_review_required" in combined:
        return "improve_assertion_strategy"
    if "none match" in combined:
        return "relax_curation_rule_or_backfill"
    return "accept_gap_or_backfill"


def _analyze_owasp_llm_gaps(corpus: dict, curation_results: list[dict],
                            gtc_counts: dict) -> list[dict]:
    gap_ids = []  # All LLM categories now have mapped risk types (Phase 27A backfill)
    gaps = []
    owasp = corpus.get("corpus_index", {}).get("by_framework", {}).get("owasp_llm", [])

    owasp_data = {}
    for entry in owasp:
        owasp_data[entry["risk"].split(" ")[0]] = {
            "name": entry["risk"],
            "corpus_ids": entry.get("corpus_ids", []),
        }

    for gid in gap_ids:
        info = owasp_data.get(gid, {})
        corpus_ids = info.get("corpus_ids", [])
        # Trace to generated testcases
        matching_gtc = []
        for c in curation_results:
            if c.get("source_corpus_id") in corpus_ids:
                matching_gtc.append(c["generated_testcase_id"])
        curated = sum(1 for c in curation_results
                      if c["generated_testcase_id"] in matching_gtc
                      and c.get("curation_status") == "curated_candidate")

        gaps.append({
            "gap_id": gid,
            "name": info.get("name", gid),
            "corpus_entries": len(corpus_ids),
            "corpus_entry_ids": corpus_ids,
            "generated_testcases_from_corpus": len(matching_gtc),
            "curated_candidate_from_corpus": curated,
            "root_cause": "Risk type mapping exists (Phase 27A backfill) but corpus entries "
                          "may be planned or no curated_candidate produced for this category.",
            "recommended_action": "backfill_corpus_fields",
        })
    return gaps


def _analyze_owasp_agentic_gaps(corpus: dict, curation_results: list[dict],
                                gtc_counts: dict) -> list[dict]:
    gap_ids = ["ASI07"]  # ASI07 (Accountability & Audit) has no direct risk type mapping
    gaps = []
    owasp = corpus.get("corpus_index", {}).get("by_framework", {}).get("owasp_agentic", [])

    owasp_data = {}
    for entry in owasp:
        owasp_data[entry["risk"].split(" ")[0]] = {
            "name": entry["risk"],
            "corpus_ids": entry.get("corpus_ids", []),
        }

    for gid in gap_ids:
        info = owasp_data.get(gid, {})
        corpus_ids = info.get("corpus_ids", [])
        matching_gtc = []
        for c in curation_results:
            if c.get("source_corpus_id") in corpus_ids:
                matching_gtc.append(c["generated_testcase_id"])
        curated = sum(1 for c in curation_results
                      if c["generated_testcase_id"] in matching_gtc
                      and c.get("curation_status") == "curated_candidate")

        gaps.append({
            "gap_id": gid,
            "name": info.get("name", gid),
            "corpus_entries": len(corpus_ids),
            "corpus_entry_ids": corpus_ids,
            "generated_testcases_from_corpus": len(matching_gtc),
            "curated_candidate_from_corpus": curated,
            "root_cause": "No risk type maps to this OWASP Agentic category in RISK_TO_OWASP_AGENTIC. "
                          "ASI07 (Accountability & Audit) lacks a direct risk type and may require "
                          "new corpus entries.",
            "recommended_action": "backfill_corpus_fields_or_accept_gap",
        })
    return gaps


def _write_safe_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write YAML manually to avoid PyYAML round-trip issues
    lines = _dict_to_yaml_lines(data, 0)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _needs_quoting(value: str) -> bool:
    """Check if a string value needs YAML quoting for safety."""
    if not value:
        return True
    # Colons, brackets, braces, commas, #, >, |, !, &, *, ?, etc.
    special = {":", "[", "]", "{", "}", ",", "#", ">", "|", "!", "&", "*", "?"}
    for ch in value:
        if ch in special:
            return True
    if value.startswith("- "):
        return True
    return False


def _dict_to_yaml_lines(data, indent: int) -> list[str]:
    """Simple dict-to-YAML converter to avoid round-trip issues."""
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                lines.append(f"{prefix}{k}:")
                lines.extend(_dict_to_yaml_lines(v, indent + 1))
            elif isinstance(v, list):
                if not v:
                    lines.append(f"{prefix}{k}: []")
                else:
                    lines.append(f"{prefix}{k}:")
                    for item in v:
                        if isinstance(item, dict):
                            lines.append(f"{prefix}-")
                            lines.extend(_dict_to_yaml_lines(item, indent + 2))
                        elif isinstance(item, list):
                            lines.append(f"{prefix}  - {item}")
                        else:
                            s = str(item)
                            if _needs_quoting(s):
                                s = s.replace("'", "''")
                                lines.append(f"{prefix}- '{s}'")
                            else:
                                lines.append(f"{prefix}- {item}")
            elif isinstance(v, bool):
                lines.append(f"{prefix}{k}: {'true' if v else 'false'}")
            elif v is None:
                lines.append(f"{prefix}{k}: null")
            else:
                s = str(v)
                if _needs_quoting(s):
                    s = s.replace("'", "''")
                    lines.append(f"{prefix}{k}: '{s}'")
                else:
                    lines.append(f"{prefix}{k}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(f"{prefix}-")
                lines.extend(_dict_to_yaml_lines(item, indent + 1))
            else:
                s = str(item)
                if _needs_quoting(s):
                    s = s.replace("'", "''")
                    lines.append(f"{prefix}- '{s}'")
                else:
                    lines.append(f"{prefix}- {item}")
    else:
        s = str(data)
        if _needs_quoting(s):
            s = s.replace("'", "''")
            lines.append(f"{prefix}'{s}'")
        else:
            lines.append(f"{prefix}{data}")
    return lines


def _write_markdown(path: Path, analysis: dict, by_suite: dict,
                    owasp_llm_gaps: list, owasp_agentic_gaps: list) -> None:
    lines = [
        "# Suite Gap Analysis",
        "",
        f"**Generated at:** {FIXED_TIMESTAMP}",
        "",
        "## Overview",
        "",
        f"| Metric | Value |",
        "|---|---|",
        f"| Total suites | {analysis['summary']['total_suites']} |",
        f"| Zero-selected suites | {analysis['summary']['zero_selected_suites']} |",
        f"| OWASP LLM gaps | {analysis['summary']['framework_gaps_llm']} |",
        f"| OWASP Agentic gaps | {analysis['summary']['framework_gaps_agentic']} |",
        f"| Analysis only | True |",
        "",
        "## Profile Status Summary",
        "",
        "| Profile | Corpus | Generated Testcases | Curated Candidate | Manual Review Required |",
        "|---|---|---|---|---|",
    ]
    for p, d in sorted(analysis["profile_status_summary"].items()):
        lines.append(
            f"| {p} | {d['corpus_entries']} | {d['generated_testcases']} | "
            f"{d['curated_candidate']} | {d['manual_review_required']} |"
        )

    lines.extend([
        "",
        "## Zero-Selected Suite Analysis",
        "",
    ])
    for sid, sdata in sorted(analysis["zero_selected_suite_analysis"].items()):
        lines.extend([
            f"### {sid} (`{sdata['suite_name']}`)",
            "",
            f"- **Suite type:** {sdata['suite_type']}",
            f"- **Source profiles:** {', '.join(sdata['source_profiles'])}",
            f"- **Required risk types:** {', '.join(sdata['risk_types_required'])}",
            "",
            "**Root causes:**",
        ])
        for cause in sdata["root_causes"]:
            lines.append(f"- {cause}")
        lines.append(f"- **Recommended action:** {sdata['recommended_action']}")
        lines.append("")

    lines.extend([
        "## OWASP LLM Gap Analysis",
        "",
    ])
    for g in owasp_llm_gaps:
        lines.extend([
            f"### {g['gap_id']}: {g['name']}",
            "",
            f"- **Corpus entries:** {g['corpus_entries']}",
            f"- **Generated testcases:** {g['generated_testcases_from_corpus']}",
            f"- **Curated candidates:** {g['curated_candidate_from_corpus']}",
            f"- **Root cause:** {g['root_cause']}",
            f"- **Recommended action:** {g['recommended_action']}",
            "",
        ])

    lines.extend([
        "## OWASP Agentic Gap Analysis",
        "",
    ])
    for g in owasp_agentic_gaps:
        lines.extend([
            f"### {g['gap_id']}: {g['name']}",
            "",
            f"- **Corpus entries:** {g['corpus_entries']}",
            f"- **Generated testcases:** {g['generated_testcases_from_corpus']}",
            f"- **Curated candidates:** {g['curated_candidate_from_corpus']}",
            f"- **Root cause:** {g['root_cause']}",
            f"- **Recommended action:** {g['recommended_action']}",
            "",
        ])

    lines.extend([
        "## Recommended Overall Action",
        "",
        analysis["recommended_overall_action"],
        "",
        "## Important Notes",
        "",
        "- **Static analysis only** — no tests executed.",
        "- **All outputs declare executed=false, real_target_connected=false, usable_for_formal_finding=false.**",
        "- **Zero-selected suites are a quality gate result, not a failure.**",
        "- **Framework gaps indicate missing risk type mappings, not missing functionality.**",
    ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
