#!/usr/bin/env python3
"""
Phase 38A.1 — M38 Review Refinement & False Positive Guard Validation
"""
import os, sys, yaml, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []
WARNINGS = []

def check(condition, msg, severity="error"):
    if not condition:
        (ERRORS if severity == "error" else WARNINGS).append(msg)

def main():
    print("=" * 60)
    print("Phase 38A.1 — M38 Review Refinement Validation")
    print("=" * 60)

    # File existence
    print("\n[1/7] File existence...")
    for p in [
        ROOT / "executions/phase38a_m38_mvp/execution_results.json",
        ROOT / "executions/phase38a_m38_mvp/m38_result.yaml",
        ROOT / "executions/phase38a_m38_mvp/capability_scorecard.yaml",
        ROOT / "capability_engine/parsers/parse_capability_results.py",
    ]:
        check(p.exists(), f"Missing: {p.relative_to(ROOT)}")

    # Security: no secrets
    print("\n[2/7] Security: no secrets in outputs...")
    for f in [
        ROOT / "executions/phase38a_m38_mvp/capability_scorecard.yaml",
        ROOT / "executions/phase38a_m38_mvp/m38_result.yaml",
    ]:
        if f.exists():
            text = f.read_text()
            check("openapi-" not in text, f"API key in {f.name}")
            check("sk-" not in text, f"OpenAI key in {f.name}")
            check("Authorization" not in text, f"Auth header in {f.name}")

    # Phase 38A execution_results.json exists and has entries
    print("\n[3/7] Phase 38A execution results...")
    with open(ROOT / "executions/phase38a_m38_mvp/execution_results.json") as f:
        results = json.load(f)
    check(len(results) == 12, f"Expected 12 entries, got {len(results)}")
    ok_count = sum(1 for r in results if r.get("api_response", {}).get("ok"))
    check(ok_count >= 10, f"Only {ok_count} OK responses")
    check(results[0].get("module_id") == "m38", "First entry should be m38 module")

    # m38_result.yaml has original M38 fields
    print("\n[4/7] m38_result.yaml original fields...")
    with open(ROOT / "executions/phase38a_m38_mvp/m38_result.yaml") as f:
        m38_result = yaml.safe_load(f)
    original_fields = ["module_id", "request_count", "ok_count", "error_count",
                       "signal_count", "refusal_count", "inconclusive_count",
                       "human_review_required_count", "strongest_techniques",
                       "weakest_techniques", "technique_details",
                       "capability_value", "assessment_reason"]
    for field in original_fields:
        check(field in m38_result, f"m38_result missing original field: {field}")

    # m38_result.yaml has new refinement fields
    print("\n[5/7] m38_result.yaml refinement fields...")
    ref_fields = ["parser_flagged_boundary_issue_count",
                  "confirmed_by_parser_boundary_issue_count",
                  "legitimate_source_update_count",
                  "likely_false_positive_count"]
    for field in ref_fields:
        check(field in m38_result, f"m38_result missing refinement field: {field}")
        check(isinstance(m38_result[field], int), f"{field} should be int")

    # Verify refinement field semantics
    print("\n[6/7] Refinement field semantics...")
    parser_flagged = m38_result.get("parser_flagged_boundary_issue_count", -1)
    confirmed = m38_result.get("confirmed_by_parser_boundary_issue_count", -1)
    legit_updates = m38_result.get("legitimate_source_update_count", -1)
    likely_fp = m38_result.get("likely_false_positive_count", -1)

    check(parser_flagged >= 0, "parser_flagged_boundary_issue_count missing")
    check(confirmed >= 0, "confirmed_by_parser_boundary_issue_count missing")
    check(legit_updates >= 0, "legitimate_source_update_count missing")
    check(likely_fp >= 0, "likely_false_positive_count missing")
    # confirmed should be <= parser_flagged
    check(confirmed <= parser_flagged,
          f"confirmed ({confirmed}) > parser_flagged ({parser_flagged})")
    # likely_fp + confirmed should be >= parser_flagged (some entries may be double-counted)
    check(likely_fp <= parser_flagged,
          f"likely_fp ({likely_fp}) > parser_flagged ({parser_flagged})")
    # legit_updates should be >= likely_fp (all FPs are legitimate updates)
    check(legit_updates >= likely_fp,
          f"legit_updates ({legit_updates}) < likely_fp ({likely_fp})")

    # Original counts accessible
    check("refusal_count" in m38_result,
          "refusal_count must be present")
    check("inconclusive_count" in m38_result,
          "inconclusive_count must be present")
    check("technique_details" in m38_result,
          "technique_details must be present")

    # capability_scorecard.yaml exists with M38 results
    print("\n[7/7] capability_scorecard.yaml...")
    with open(ROOT / "executions/phase38a_m38_mvp/capability_scorecard.yaml") as f:
        scorecard = yaml.safe_load(f)
    check("scorecard_metadata" in scorecard, "scorecard missing metadata")
    check("modules" in scorecard, "scorecard missing modules")
    check("m38" in scorecard.get("modules", {}), "scorecard missing m38 module")
    sc_m38 = scorecard["modules"]["m38"]
    for field in original_fields:
        check(field in sc_m38, f"scorecard m38 missing original field: {field}")
    for field in ref_fields:
        check(field in sc_m38, f"scorecard m38 missing refinement field: {field}")
    check("formal_finding_allowed" in scorecard.get("scorecard_metadata", {}),
          "formal_finding_allowed missing")
    check(scorecard["scorecard_metadata"].get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")

    # Verify neutral assessment language
    reason = m38_result.get("assessment_reason", "")
    check("breached" not in reason.lower(),
          f"Assessment reason uses 'breached': {reason}")
    check("parser flagged" in reason.lower(),
          f"Assessment reason missing neutral language: {reason}")
    check("confirmed_vulnerability" not in reason.lower(),
          "Assessment reason contains 'confirmed_vulnerability'")
    check("formal finding" not in reason.lower(),
          "Assessment reason contains 'formal finding'")

    # Report
    print("\n" + "=" * 60)
    if ERRORS:
        print(f"FAILED — {len(ERRORS)} error(s):")
        for e in ERRORS:
            print(f"  ✗ {e}")
    else:
        print("ALL CHECKS PASSED")
    if WARNINGS:
        print(f"\n{len(WARNINGS)} warning(s):")
        for w in WARNINGS:
            print(f"  ⚠ {w}")
    print("=" * 60)
    return len(ERRORS) == 0

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
