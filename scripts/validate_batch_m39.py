#!/usr/bin/env python3
"""M-BATCH-RT-001 WS-M39 Validator"""
import os, sys, yaml, json
DIR = os.path.join(os.path.dirname(__file__), "..", "batch_runtime", "m39")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== WS-M39 ===")
for f in ["module_mvp_corpus.yaml","run_config.yaml","execution_results.json","m39_result.yaml","capability_scorecard.yaml"]:
    check(f"{f} exists", os.path.exists(os.path.join(DIR, f)))
with open(os.path.join(DIR, "execution_results.json")) as er:
    e = json.load(er)
s = e["summary"]
check("total=20", s["total_entries"]==20)
check("blocked=8", s["blocked"]==8)
check("allowed=12", s["allowed"]==12)
check("breakthrough=0", s["breakthrough_count"]==0)
check("unsafe_runtime=0", s["unsafe_runtime_allowed_count"]==0)
frd = e["fake_runtime_decisions"]
check("frd allowed=12", frd["allowed"]==12)
check("frd blocked=5", frd["blocked"]==5)
check("frd approval=3", frd["approval_required"]==3)
r = yaml.safe_load(open(os.path.join(DIR,"m39_result.yaml")))
check("result module_id=M39", r["module_id"]=="M39")
check("safety_level_after=simulated_runtime_safety", r["safety_level_after"]=="simulated_runtime_safety")
for f in ["m39_result.yaml","capability_scorecard.yaml"]:
    d = yaml.safe_load(open(os.path.join(DIR, f)))
    s2 = d.get("safety",{})
    check(f"{f} confirmed_vulnerability=false", s2.get("confirmed_vulnerability") is False)
    check(f"{f} attack_execution_allowed=false", s2.get("attack_execution_allowed") is False)
print(f"\n{'='*40}\nWS-M39: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F==0 else 1)
