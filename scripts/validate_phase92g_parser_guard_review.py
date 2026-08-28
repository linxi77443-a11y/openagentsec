#!/usr/bin/env python3
"""Phase-92G Parser Guard Review Validator"""
import os, sys, yaml
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-92G Parser Guard Review ===")
check("review doc", os.path.exists(os.path.join(DOCS, "phase92g_parser_guard_review.md")))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase92g_parser_guard_review_result.yaml")))

result = yaml.safe_load(open(os.path.join(RESULTS, "phase92g_parser_guard_review_result.yaml")))
check("conclusion=approved", result["conclusion"] == "approved")
check("modules_checked=11", result["modules_checked"] == 11)
check("modules_passed=11", result["modules_passed"] == 11)
check("modules_failed=0", result["modules_failed"] == 0)
check("blocking_items=0", result["blocking_items"] == 0)
check("coverage_credit_granted=false", result["coverage_credit_granted"] is False)
check("execution_results_modified=false", result["execution_results_modified"] is False)
s = result["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)

print(f"\n{'='*40}\nPhase-92G: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F == 0 else 1)
