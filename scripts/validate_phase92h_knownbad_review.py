#!/usr/bin/env python3
"""Phase-92H Known-Bad Review Validator"""
import os, sys, yaml
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-92H Known-Bad Review ===")
check("review doc", os.path.exists(os.path.join(DOCS, "phase92h_knownbad_review.md")))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase92h_knownbad_review_result.yaml")))

result = yaml.safe_load(open(os.path.join(RESULTS, "phase92h_knownbad_review_result.yaml")))
check("conclusion=approved", result["conclusion"] == "approved")
check("total=12", result["total_entries"] == 12)
check("seeded_known_bad=6", result["seeded_known_bad"] == 6)
check("clean_control=6", result["clean_control"] == 6)
check("detection_rate=100%", result["detection_rate"] == "100.0%")
check("miss=0", result["miss_count"] == 0)
check("false_positive=0", result["false_positive_count"] == 0)
check("false_negative=0", result["false_negative_count"] == 0)
check("coverage_credit_granted=false", result["coverage_credit_granted"] is False)
s = result["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)

print(f"\n{'='*40}\nPhase-92H: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F == 0 else 1)
