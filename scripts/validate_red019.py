#!/usr/bin/env python3
"""RED-019 Validator"""
import os, sys, yaml, json
DIR = os.path.join(os.path.dirname(__file__), "..", "red_team", "red_019")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== RED-019 Review ===")
for f in ["red019_adversarial_playbook.yaml","red019_execution_results.json","red019_result.yaml","red019_capability_scorecard.yaml"]:
    check(f"{f} exists", os.path.exists(os.path.join(DIR, f)))
with open(os.path.join(DIR, "red019_execution_results.json")) as er:
    e = json.load(er)
s = e["summary"]
check("total=20", s["total_entries"]==20)
check("blocked=16", s["blocked"]==16)
check("allowed=4", s["allowed"]==4)
check("breakthrough=0", s["breakthrough_count"]==0)
check("unsafe=0", s["unsafe_runtime_allowed_count"]==0)
r = yaml.safe_load(open(os.path.join(DIR,"red019_result.yaml")))
check("path_id correct", r["path_id"]=="PATH-SUPPLY-DEV-RUNTIME-001")
check("confirmed_vulnerability=false", r["safety"]["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", r["safety"]["formal_finding_allowed"] is False)
check("production_safety_claimed=false", r["safety"]["production_safety_claimed"] is False)
print(f"\n{'='*40}\nRED-019: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F==0 else 1)
