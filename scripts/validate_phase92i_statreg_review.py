#!/usr/bin/env python3
"""Phase-92I Statistical Regression Review Validator"""
import os, sys, yaml
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-92I StatReg Review ===")
check("review doc", os.path.exists(os.path.join(DOCS, "phase92i_statreg_review.md")))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase92i_statreg_review_result.yaml")))

result = yaml.safe_load(open(os.path.join(RESULTS, "phase92i_statreg_review_result.yaml")))
check("conclusion=approved", result["conclusion"] == "approved")
check("total=5", result["total_entries"] == 5)
check("baseline_match=5", result["baseline_match"] == 5)
check("max_delta=0.0", result["max_delta"] == 0.0)
check("threshold=0.05", result["threshold"] == 0.05)
check("regression_detected=false", result["regression_detected"] is False)
check("coverage_credit_granted=false", result["coverage_credit_granted"] is False)
s = result["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)

print(f"\n{'='*40}\nPhase-92I: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F == 0 else 1)
