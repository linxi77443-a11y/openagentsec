#!/usr/bin/env python3
"""Phase-92J Shared Asset Review Validator"""
import os, sys, yaml
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-92J Shared Asset Review ===")
check("review doc", os.path.exists(os.path.join(DOCS, "phase92j_shared_asset_review.md")))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase92j_shared_asset_review_result.yaml")))

result = yaml.safe_load(open(os.path.join(RESULTS, "phase92j_shared_asset_review_result.yaml")))
check("conclusion=approved", result["conclusion"] == "approved")
check("shared_files=3", result["shared_files"] == 3)
check("modified_files=0", result["modified_files"] == 0)
check("duplicate_ids=0", result["duplicate_ids"] == 0)
check("path_conflicts=0", result["path_conflicts"] == 0)
check("schema_conflicts=0", result["schema_conflicts"] == 0)
check("execution_performed=false", result["execution_performed"] is False)
check("capability_value=not_applicable", result["capability_value"] == "not_applicable")
check("risk_level=not_applicable", result["risk_level"] == "not_applicable")
check("coverage_credit_granted=false", result["coverage_credit_granted"] is False)
check("registered_module=false", result["registered_module"] is False)
check("coverage_change_claimed=false", result["coverage_change_claimed"] is False)
s = result["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)

print(f"\n{'='*40}\nPhase-92J: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F == 0 else 1)
