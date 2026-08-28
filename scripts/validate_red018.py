#!/usr/bin/env python3
"""RED-018 Individual Review Validator"""
import os, sys, yaml, json
DIR = os.path.join(os.path.dirname(__file__), "..", "red_team", "red_018")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== RED-018 Review ===")
for f in ["red018_adversarial_playbook.yaml","red018_run_config.yaml","red018_execution_results.json","red018_result.yaml","red018_capability_scorecard.yaml","red_team_action_report.md"]:
    check(f"{f} exists", os.path.exists(os.path.join(DIR, f)))

with open(os.path.join(DIR, "red018_execution_results.json")) as er:
    e = json.load(er)
s = e["summary"]
check("total=25", s["total_entries"]==25)
check("blocked=20", s["blocked"]==20)
check("allowed=5", s["allowed"]==5)
check("breakthrough=0", s["breakthrough_count"]==0)
check("unsafe=0", s["unsafe_runtime_allowed_count"]==0)
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)

r = yaml.safe_load(open(os.path.join(DIR,"red018_result.yaml")))
check("report_id=RED018", r["report_id"]=="RED-018")
check("path_id correct", r["path_id"]=="PATH-SUPPLY-DEV-RAG-RUNTIME-001")
check("confirmed_vulnerability=false", r["safety"]["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", r["safety"]["formal_finding_allowed"] is False)
check("production_safety_claimed=false", r["safety"]["production_safety_claimed"] is False)
check("attack_execution_allowed=false", r["safety"]["attack_execution_allowed"] is False)
check("synthetic_only=true", r["safety"]["synthetic_only"] is True)

print(f"\n{'='*40}\nRED-018: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F==0 else 1)
