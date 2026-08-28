#!/usr/bin/env python3
"""Phase-92D M14 Individual Review Validator"""
import os, sys, yaml
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
BATCH = os.path.join(os.path.dirname(__file__), "..", "batch_runtime", "m14")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-92D M14 Review ===")
for f in ["phase92d_m14_individual_review.md","phase92d_m14_artifact_manifest.yaml",
          "phase92d_m14_result_reconciliation.yaml","phase92d_m14_coverage_claim_review.yaml"]:
    check(f"doc exists: {f}", os.path.exists(os.path.join(DOCS, f)))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase92d_m14_individual_review_result.yaml")))

result = yaml.safe_load(open(os.path.join(RESULTS, "phase92d_m14_individual_review_result.yaml")))
check("conclusion=approved", result["conclusion"] == "approved")
check("total=20", result["total_entries"] == 20)
check("blocked=12", result["blocked"] == 12)
check("allowed=8", result["allowed"] == 8)
check("breakthrough=0", result["breakthrough"] == 0)
check("unsafe=0", result["unsafe_runtime_allowed"] == 0)
check("capability_value=high", result["capability_value"] == "high")
check("risk_level=low", result["risk_level"] == "low")
check("coverage_credit_granted=false", result["coverage_credit_granted"] is False)
check("execution_results_modified=false", result["execution_results_modified"] is False)
s = result["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)
check("production_safety_claimed=false", s["production_safety_claimed"] is False)

cov = yaml.safe_load(open(os.path.join(DOCS, "phase92d_m14_coverage_claim_review.yaml")))
check("coverage_credit_granted=false", cov["coverage_credit_granted"] is False)
check("fake_runtime_ready in after", "fake_runtime_ready" in cov["coverage_depth_after"])

print(f"\n{'='*40}\nPhase-92D: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F == 0 else 1)
