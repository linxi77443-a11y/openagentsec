#!/usr/bin/env python3
"""
Phase 39A — M39 Tool Invocation / Action Boundary MVP Validation
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
    print("Phase 39A — M39 Tool Invocation / Action Boundary Validation")
    print("=" * 60)

    # File existence
    print("\n[1/8] File existence...")
    for p in [
        ROOT / "capability_modules/corpora/phase39a_m39_action_boundary/m39_corpus.yaml",
        ROOT / "capability_modules/corpora/phase39a_m39_action_boundary/m39_mvp_corpus.yaml",
        ROOT / "capability_engine/configs/phase39a_m39_mvp_run.yaml",
        ROOT / "executions/phase39a-m39-mvp/execution_results.json",
        ROOT / "executions/phase39a-m39-mvp/m39_result.yaml",
        ROOT / "executions/phase39a-m39-mvp/capability_scorecard.yaml",
    ]:
        check(p.exists(), f"Missing: {p.relative_to(ROOT)}")

    # Security: no secrets
    print("\n[2/8] Security: no secrets in outputs...")
    for f in [
        ROOT / "executions/phase39a-m39-mvp/m39_result.yaml",
        ROOT / "executions/phase39a-m39-mvp/capability_scorecard.yaml",
    ]:
        if f.exists():
            text = f.read_text()
            check("openapi-" not in text, f"API key in {f.name}")
            check("sk-" not in text, f"OpenAI key in {f.name}")
            check("Authorization" not in text, f"Auth header in {f.name}")

    # Full corpus
    print("\n[3/8] Full corpus structure...")
    with open(ROOT / "capability_modules/corpora/phase39a_m39_action_boundary/m39_corpus.yaml") as f:
        full = yaml.safe_load(f)
    check("m39" in full, "Full corpus missing top-level m39 key")
    full_entries = full.get("m39", [])
    check(len(full_entries) == 16, f"Full corpus expected 16 entries, got {len(full_entries)}")

    # MVP corpus
    print("\n[4/8] MVP corpus structure...")
    with open(ROOT / "capability_modules/corpora/phase39a_m39_action_boundary/m39_mvp_corpus.yaml") as f:
        mvp = yaml.safe_load(f)
    check("m39" in mvp, "MVP corpus missing top-level m39 key")
    mvp_entries = mvp.get("m39", [])
    check(len(mvp_entries) == 8, f"MVP corpus expected 8 entries, got {len(mvp_entries)}")

    # Check required M39 fields in corpus entries
    print("\n[5/8] Corpus field completeness...")
    required_fields = ["corpus_id", "module_id", "category", "technique_tag",
                       "user_goal", "trusted_context", "tool_return_content",
                       "embedded_action", "authorized_action_scope",
                       "expected_behavior", "boundary_signal", "control_case",
                       "prompt_text"]
    for entry in mvp_entries:
        for field in required_fields:
            check(field in entry, f"{entry['corpus_id']} missing field: {field}")
        check(entry["module_id"] == "M39", f"{entry['corpus_id']} module_id != M39")
        check(entry["authorized_action_scope"] in ("read_only", "analysis_only", "read_only_analysis"),
              f"{entry['corpus_id']} invalid authorized_action_scope: {entry['authorized_action_scope']}")
        if not entry["control_case"]:
            check(entry.get("embedded_action", ""), f"{entry['corpus_id']} missing embedded_action")

    # Run config check
    print("\n[6/8] Run config...")
    with open(ROOT / "capability_engine/configs/phase39a_m39_mvp_run.yaml") as f:
        config = yaml.safe_load(f)
    check("m39" in config.get("modules", []), "Run config modules missing m39")
    check("phase39a-m39-mvp" == config.get("run_id"), "run_id mismatch")
    check("fastgpt" == config.get("target_profile", {}).get("api_type"), "api_type mismatch")
    check(config.get("result", {}).get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")

    # Execution results
    print("\n[7/8] Execution results...")
    with open(ROOT / "executions/phase39a-m39-mvp/execution_results.json") as f:
        results = json.load(f)
    check(len(results) == 8, f"Expected 8 execution results, got {len(results)}")
    ok_count = sum(1 for r in results if r.get("api_response", {}).get("ok"))
    check(ok_count >= 6, f"Only {ok_count} OK responses")
    check(results[0].get("module_id") == "m39", "First entry should be m39 module")

    # M39 result YAML fields
    print("\n[8/8] m39_result.yaml fields...")
    with open(ROOT / "executions/phase39a-m39-mvp/m39_result.yaml") as f:
        m39_result = yaml.safe_load(f)
    expected_fields = [
        "module_id", "request_count", "ok_count", "error_count",
        "signal_count", "refusal_count", "inconclusive_count",
        "human_review_required_count", "strongest_techniques",
        "weakest_techniques", "technique_details",
        "capability_value", "assessment_reason",
        # M39-specific fields
        "action_boundary_preserved_count",
        "unauthorized_action_suggested_count",
        "low_priority_action_followed_count",
        "tool_instruction_followed_count",
        "citation_action_followed_count",
        "source_redirect_followed_count",
        "read_only_to_write_escalation_count",
        "action_refusal_count",
        "likely_false_positive_count",
        "action_boundary_risk_level",
    ]
    for field in expected_fields:
        check(field in m39_result, f"m39_result missing field: {field}")

    # Verify risk level and capability_value semantics
    cap_value = m39_result.get("capability_value", "")
    risk_level = m39_result.get("action_boundary_risk_level", "")
    check(cap_value in ("high", "medium", "low"), f"Invalid capability_value: {cap_value}")
    check(risk_level in ("high", "medium", "low"), f"Invalid risk_level: {risk_level}")

    # Check scorecard
    with open(ROOT / "executions/phase39a-m39-mvp/capability_scorecard.yaml") as f:
        scorecard = yaml.safe_load(f)
    check("scorecard_metadata" in scorecard, "Scorecard missing metadata")
    check("modules" in scorecard, "Scorecard missing modules")
    check("m39" in scorecard.get("modules", {}), "Scorecard missing m39")
    check(scorecard["scorecard_metadata"].get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")
    sc_m39 = scorecard["modules"]["m39"]
    for field in expected_fields:
        check(field in sc_m39, f"Scorecard m39 missing field: {field}")

    # Check neutral assessment language
    reason = m39_result.get("assessment_reason", "")
    check("breached" not in reason.lower(),
          f"Assessment reason uses 'breached': {reason}")
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
