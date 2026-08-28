#!/usr/bin/env python3
"""
Phase 39A.1 — M39 Action Boundary Review Refinement & False Positive Guard Validation
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
    print("Phase 39A.1 — M39 Review Refinement Validation")
    print("=" * 60)

    # File existence
    print("\n[1/7] File existence...")
    for p in [
        ROOT / "executions/phase39a-m39-mvp/execution_results.json",
        ROOT / "executions/phase39a-m39-mvp/m39_result.yaml",
        ROOT / "executions/phase39a-m39-mvp/capability_scorecard.yaml",
        ROOT / "capability_engine/parsers/parse_capability_results.py",
    ]:
        check(p.exists(), f"Missing: {p.relative_to(ROOT)}")

    # Security: no secrets
    print("\n[2/7] Security: no secrets in outputs...")
    for f in [
        ROOT / "executions/phase39a-m39-mvp/capability_scorecard.yaml",
        ROOT / "executions/phase39a-m39-mvp/m39_result.yaml",
    ]:
        if f.exists():
            text = f.read_text()
            check("openapi-" not in text, f"API key in {f.name}")
            check("sk-" not in text, f"OpenAI key in {f.name}")
            check("Authorization" not in text, f"Auth header in {f.name}")

    # Phase 39A execution_results.json exists and is unchanged
    print("\n[3/7] Phase 39A execution results preserved...")
    with open(ROOT / "executions/phase39a-m39-mvp/execution_results.json") as f:
        results = json.load(f)
    check(len(results) == 8, f"Expected 8 entries, got {len(results)}")
    ok_count = sum(1 for r in results if r.get("api_response", {}).get("ok"))
    check(ok_count == 8, f"Expected 8 OK, got {ok_count}")
    check(results[0].get("module_id") == "m39", "First entry should be m39 module")

    # m39_result.yaml has original M39 fields
    print("\n[4/7] m39_result.yaml original fields...")
    with open(ROOT / "executions/phase39a-m39-mvp/m39_result.yaml") as f:
        m39_result = yaml.safe_load(f)
    original_fields = ["module_id", "request_count", "ok_count", "error_count",
                       "signal_count", "refusal_count", "inconclusive_count",
                       "human_review_required_count", "strongest_techniques",
                       "weakest_techniques", "technique_details",
                       "capability_value", "assessment_reason",
                       "action_boundary_preserved_count",
                       "unauthorized_action_suggested_count",
                       "low_priority_action_followed_count",
                       "tool_instruction_followed_count",
                       "citation_action_followed_count",
                       "source_redirect_followed_count",
                       "read_only_to_write_escalation_count",
                       "action_refusal_count",
                       "likely_false_positive_count",
                       "action_boundary_risk_level"]
    for field in original_fields:
        check(field in m39_result, f"m39_result missing original field: {field}")

    # m39_result.yaml has new refinement fields
    print("\n[5/7] m39_result.yaml refinement fields...")
    ref_fields = ["parser_flagged_action_issue_count",
                  "confirmed_by_parser_action_issue_count",
                  "parser_flagged_read_only_to_write_count",
                  "confirmed_read_only_to_write_count",
                  "action_keyword_only_match_count",
                  "review_required_action_issue_count"]
    for field in ref_fields:
        check(field in m39_result, f"m39_result missing refinement field: {field}")
        check(isinstance(m39_result[field], int), f"{field} should be int")

    # Verify refinement field semantics
    print("\n[6/7] Refinement field semantics...")
    parser_flagged = m39_result["parser_flagged_action_issue_count"]
    confirmed = m39_result["confirmed_by_parser_action_issue_count"]
    rw_flagged = m39_result["parser_flagged_read_only_to_write_count"]
    rw_confirmed = m39_result["confirmed_read_only_to_write_count"]
    keyword_only = m39_result["action_keyword_only_match_count"]
    review_required = m39_result["review_required_action_issue_count"]

    check(parser_flagged >= 0, "parser_flagged_action_issue_count missing")
    check(confirmed >= 0, "confirmed_by_parser_action_issue_count missing")
    check(confirmed <= parser_flagged,
          f"confirmed ({confirmed}) > parser_flagged ({parser_flagged})")
    check(rw_confirmed <= rw_flagged,
          f"rw_confirmed ({rw_confirmed}) > rw_flagged ({rw_flagged})")
    check(keyword_only <= parser_flagged + 4,
          f"keyword_only ({keyword_only}) too large")
    check(review_required >= 0, "review_required_action_issue_count missing")

    # Verify neutral assessment language
    reason = m39_result.get("assessment_reason", "")
    check("breached" not in reason.lower(),
          f"Assessment reason uses 'breached': {reason}")
    check("confirmed_vulnerability" not in reason.lower(),
          "Assessment reason contains 'confirmed_vulnerability'")
    check("formal finding" not in reason.lower(),
          "Assessment reason contains 'formal finding'")

    # Verify capability_value and risk_level semantics
    cap_value = m39_result.get("capability_value", "")
    risk_level = m39_result.get("action_boundary_risk_level", "")
    check(cap_value in ("high", "medium", "low"), f"Invalid capability_value: {cap_value}")
    check(risk_level in ("high", "medium", "low"), f"Invalid risk_level: {risk_level}")

    # scorecard check
    print("\n[7/7] capability_scorecard.yaml...")
    with open(ROOT / "executions/phase39a-m39-mvp/capability_scorecard.yaml") as f:
        scorecard = yaml.safe_load(f)
    check("scorecard_metadata" in scorecard, "scorecard missing metadata")
    check("modules" in scorecard, "scorecard missing modules")
    check("m39" in scorecard.get("modules", {}), "scorecard missing m39 module")
    sc_m39 = scorecard["modules"]["m39"]
    for field in original_fields:
        check(field in sc_m39, f"scorecard m39 missing original field: {field}")
    for field in ref_fields:
        check(field in sc_m39, f"scorecard m39 missing refinement field: {field}")
    check("formal_finding_allowed" in scorecard.get("scorecard_metadata", {}),
          "formal_finding_allowed missing")
    check(scorecard["scorecard_metadata"].get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")

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
