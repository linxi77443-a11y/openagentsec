#!/usr/bin/env python3
"""Update generated testcases YAML files with curation_status and runner_binding_status."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "generated_testcases"
CURATION_RESULT = ROOT / "curation" / "generated_testcase_curation_result.yaml"

profiles = ["chatbot", "rag", "agent", "api", "regression"]

# Load curation result
curation = yaml.safe_load(CURATION_RESULT.read_text(encoding="utf-8"))
curation_map = {}
for c in curation.get("curation_results", []):
    gtc_id = c.get("generated_testcase_id")
    if gtc_id:
        curation_map[gtc_id] = c

print(f"Loaded {len(curation_map)} curation results")

for profile in profiles:
    path = GENERATED_DIR / profile / f"generated_{profile}_testcases.yaml"
    if not path.exists():
        print(f"  SKIP {path} (not found)")
        continue

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    key = f"generated_{profile}_testcases"
    entries = data.get(key, [])

    updated = 0
    for entry in entries:
        gtc_id = entry.get("generated_testcase_id", "")
        cr = curation_map.get(gtc_id)
        if cr:
            entry["curation_status"] = cr.get("curation_status", "manual_review_required")
            entry["runner_binding_status"] = cr.get("runner_binding_status", "unbound")
            entry["usable_for_formal_finding"] = False
            updated += 1

    path.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"  {path.name}: {updated}/{len(entries)} entries updated")

print("\nDone.")
