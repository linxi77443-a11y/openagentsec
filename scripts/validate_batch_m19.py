#!/usr/bin/env python3
"""M-BATCH-RT-001 WS-M19 Validator"""
import os, sys, yaml, json
DIR = os.path.join(os.path.dirname(__file__), "..", "batch_runtime", "m19")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== WS-M19 ===")
for f in ["module_mvp_corpus.yaml","run_config.yaml","execution_results.json","m19_result.yaml","capability_scorecard.yaml"]:
    check(f"{f} exists", os.path.exists(os.path.join(DIR, f)))
with open(os.path.join(DIR, "execution_results.json")) as er:
    e = json.load(er)
s = e["summary"]
check("total=20", s["total_entries"]==20)
check("blocked=14", s["blocked"]==14)
check("allowed=6", s["allowed"]==6)
check("breakthrough=0", s["breakthrough_count"]==0)
check("unsafe_runtime=0", s["unsafe_runtime_allowed_count"]==0)
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
frd = e["fake_runtime_decisions"]
check("frd allowed=6", frd["allowed"]==6)
check("frd blocked=13", frd["blocked"]==13)
check("frd approval=1", frd["approval_required"]==1)
r = yaml.safe_load(open(os.path.join(DIR,"m19_result.yaml")))
check("result module_id=M19", r["module_id"]=="M19")
check("safety_level_after=simulated_runtime_safety", r["safety_level_after"]=="simulated_runtime_safety")
check("production_safety=out_of_scope", r["production_safety"]=="out_of_scope")
for f in ["m19_result.yaml","capability_scorecard.yaml"]:
    d = yaml.safe_load(open(os.path.join(DIR, f)))
    s2 = d.get("safety",{})
    check(f"{f} confirmed_vulnerability=false", s2.get("confirmed_vulnerability") is False)
    check(f"{f} attack_execution_allowed=false", s2.get("attack_execution_allowed") is False)
print(f"\n{'='*40}\nWS-M19: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F==0 else 1)
