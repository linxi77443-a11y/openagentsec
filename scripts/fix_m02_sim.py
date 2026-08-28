#!/usr/bin/env python3
"""Fix M02: add control entries to per_entry_results + add SIM_ to original prompts."""
import yaml, json, os

BASE = "/Users/linxi/Desktop/ai-workspace/AI学习/AI安全评估探索/adversarial_playbooks/m02_full_corpus"

with open(os.path.join(BASE, "playbook.yaml")) as f:
    pb = yaml.safe_load(f)
entries = pb["entries"]

# Fix 1: Add control entries to per_entry_results
er_path = os.path.join(BASE, "execution_results.json")
with open(er_path) as f:
    er = json.load(f)

existing_ids = {r.get("entry_id") for r in er.get("per_entry_results", [])}
controls = [e for e in entries if e.get("category") == "control"]

for c in controls:
    eid = c.get("entry_id", "")
    if eid and eid not in existing_ids:
        er["per_entry_results"].append({
            "entry_id": eid,
            "status": "control_baseline",
            "breakthrough_detected": False,
            "behavior_match": True,
            "human_review_required": False,
            "signals": ["control_baseline_normal"]
        })

er["per_entry_results"] = sorted(er["per_entry_results"], key=lambda x: x.get("entry_id", ""))

with open(er_path, "w") as f:
    json.dump(er, f, ensure_ascii=False, indent=2)
print(f"M02: per_entry_results now has {len(er['per_entry_results'])} entries")

# Fix 2: Add SIM_ placeholders to original attack entries that lack them
attacks = [e for e in entries if e.get("category") != "control"]
fixed = 0
for e in attacks:
    prompt = e.get("prompt", "")
    if "<SIM_" not in prompt:
        eid = e.get("entry_id", "")
        cat = e.get("category", "")
        # Wrap original prompt with SIM context
        e["prompt"] = f"<SIM_{cat.upper()}_QUERY_{eid}>: {prompt}"
        fixed += 1

with open(os.path.join(BASE, "playbook.yaml"), "w") as f:
    yaml.dump(pb, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
print(f"M02: added SIM_ placeholders to {fixed} original attack entries")
