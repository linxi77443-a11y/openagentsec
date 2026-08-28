#!/usr/bin/env python3
"""Update generated_testcase_index.yaml and summary with curation data."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "generated_testcases" / "generated_testcase_index.yaml"
SUMMARY_PATH = ROOT / "generated_testcases" / "generated_testcase_summary.md"
CURATION_RESULT = ROOT / "curation" / "generated_testcase_curation_result.yaml"

# Load curation result
curation = yaml.safe_load(CURATION_RESULT.read_text(encoding="utf-8"))
curation_results = curation.get("curation_results", [])

# Build curation stats
status_counts: dict[str, int] = {}
by_profile: dict[str, dict[str, int]] = {}
for cr in curation_results:
    status = cr["curation_status"]
    status_counts[status] = status_counts.get(status, 0) + 1
    profile = cr["source_profile"]
    if profile not in by_profile:
        by_profile[profile] = {}
    by_profile[profile][status] = by_profile[profile].get(status, 0) + 1

# Update index
index = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8"))
gti = index.get("generated_testcase_index", index)
gti["curation_status"] = "completed"
gti["curation_stats"] = {
    "total_curated": len(curation_results),
    "curated_candidate": status_counts.get("curated_candidate", 0),
    "manual_review_required": status_counts.get("manual_review_required", 0),
    "planned_only": status_counts.get("planned_only", 0),
    "not_executable": status_counts.get("not_executable", 0),
    "duplicate_or_low_value": status_counts.get("duplicate_or_low_value", 0),
    "runner_binding_drafts": 5,
    "curation_only": True,
    "executed": False,
}

INDEX_PATH.write_text(
    yaml.dump(index, default_flow_style=False, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
)
print(f"Updated: {INDEX_PATH}")

# Update summary
summary_lines = [
    "# Generated Testcase Summary",
    "",
    "## Curation Status",
    "",
    f"Phase 25 curation completed: {len(curation_results)} testcases classified.",
    "",
    "| Status | Count |",
    "|---|---|",
    f"| curated_candidate | {status_counts.get('curated_candidate', 0)} |",
    f"| manual_review_required | {status_counts.get('manual_review_required', 0)} |",
    f"| planned_only | {status_counts.get('planned_only', 0)} |",
    f"| not_executable | {status_counts.get('not_executable', 0)} |",
    f"| duplicate_or_low_value | {status_counts.get('duplicate_or_low_value', 0)} |",
    "",
    "## By Profile",
    "",
]

for profile in ["chatbot", "rag", "agent", "api", "regression"]:
    summary_lines.append(f"### {profile}")
    counts = by_profile.get(profile, {})
    summary_lines.append(f"- curated_candidate: {counts.get('curated_candidate', 0)}")
    summary_lines.append(f"- manual_review_required: {counts.get('manual_review_required', 0)}")

summary_lines.extend([
    "",
    "## Runner Binding",
    "",
    "5 runner binding drafts created:",
    "- chatbot_generated_binding",
    "- rag_generated_binding",
    "- agent_generated_binding",
    "- api_generated_binding",
    "- regression_generated_binding",
    "",
    "All bindings: allowed_now=false (binding_draft only)",
    "",
    "## Important Notes",
    "",
    "- **Curation is static classification only** — no tests executed.",
    "- **All entries declare executed=false, real_target_connected=false, usable_for_formal_finding=false.**",
    "- **curated_candidate** passes static filters but still requires manual runner binding review.",
    "- **manual_review_required** has incomplete fields or ambiguous semantics.",
    "- **Runner binding is a draft recommendation** — not a validated runner configuration.",
])

summary = "\n".join(summary_lines)
SUMMARY_PATH.write_text(summary, encoding="utf-8")
print(f"Updated: {SUMMARY_PATH}")

print("Done.")
