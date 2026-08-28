#!/usr/bin/env python3
"""Phase-92F Tool Trace Integration Review Validator"""
import os, sys, yaml
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-92F Tool Trace Review ===")
check("review doc", os.path.exists(os.path.join(DOCS, "phase92f_tooltrace_integration_review.md")))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase92f_tooltrace_integration_review_result.yaml")))

result = yaml.safe_load(open(os.path.join(RESULTS, "phase92f_tooltrace_integration_review_result.yaml")))
check("conclusion=approved", result["conclusion"] == "approved")
check("total=17", result["total_entries"] == 17)
check("parse_success=7", result["parse_success"] == 7)
check("normalization_failure=2", result["normalization_failure"] == 2)
check("adapter_failure=2", result["adapter_failure"] == 2)
check("schema_failure=1", result["schema_failure"] == 1)
check("invalid_tool=5", result["invalid_tool"] == 5)
check("coverage_credit_granted=false", result["coverage_credit_granted"] is False)
check("backward_compatibility v1.0 pass", result["backward_compatibility"]["v1_0_pass"] is True)
check("backward_compatibility v0.9 rejected", result["backward_compatibility"]["v0_9_rejected"] is True)
s = result["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)

print(f"\n{'='*40}\nPhase-92F: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F == 0 else 1)
