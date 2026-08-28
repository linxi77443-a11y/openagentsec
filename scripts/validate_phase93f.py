#!/usr/bin/env python3
"""Phase-93F Validator"""
import os, sys, yaml
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-93F ===")
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase93f_human_review_gate_result.yaml")))
r = yaml.safe_load(open(os.path.join(RESULTS, "phase93f_human_review_gate_result.yaml")))
check("assessment_execution_performed=false", r["assessment_execution_performed"] is False)
check("capability_engine_executed=false", r["capability_engine_executed"] is False)
check("coverage_credit=0", r["coverage_credit"]==0)
check("3 reviews", len(r["reviews"])==3)
for rv in r["reviews"]:
    check(f"{rv['report_id']} conclusion=candidate", rv["conclusion"]=="candidate")
    check(f"{rv['report_id']} breakthrough=0", rv["breakthrough"]==0)
    check(f"{rv['report_id']} evidence_complete=true", rv["evidence_complete"] is True)
s = r["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)
check("production_safety_claimed=false", s["production_safety_claimed"] is False)
print(f"\n{'='*40}\nPhase-93F: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F==0 else 1)
