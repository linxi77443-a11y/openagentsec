#!/usr/bin/env python3
"""
Phase 40A — M12 Tool Invocation Safety MVP Validation
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
    print("Phase 40A — M12 Tool Invocation Safety Validation")
    print("=" * 60)

    # File existence
    print("\n[1/8] File existence...")
    for p in [
        ROOT / "capability_modules/corpora/phase40a_m12_tool_invocation_safety/m12_corpus.yaml",
        ROOT / "capability_modules/corpora/phase40a_m12_tool_invocation_safety/m12_mvp_corpus.yaml",
        ROOT / "capability_engine/configs/phase40a_m12_mvp_run.yaml",
        ROOT / "executions/phase40a-m12-mvp/execution_results.json",
        ROOT / "executions/phase40a-m12-mvp/m12_result.yaml",
        ROOT / "executions/phase40a-m12-mvp/capability_scorecard.yaml",
    ]:
        check(p.exists(), f"Missing: {p.relative_to(ROOT)}")

    # Security: no secrets
    print("\n[2/8] Security: no secrets in outputs...")
    for f in [
        ROOT / "executions/phase40a-m12-mvp/m12_result.yaml",
        ROOT / "executions/phase40a-m12-mvp/capability_scorecard.yaml",
    ]:
        if f.exists():
            text = f.read_text()
            check("openapi-" not in text, f"API key in {f.name}")
            check("sk-" not in text, f"OpenAI key in {f.name}")
            check("Authorization" not in text, f"Auth header in {f.name}")

    # Full corpus
    print("\n[3/8] Full corpus structure...")
    with open(ROOT / "capability_modules/corpora/phase40a_m12_tool_invocation_safety/m12_corpus.yaml") as f:
        full = yaml.safe_load(f)
    check("m12" in full, "Full corpus missing top-level m12 key")
    full_entries = full.get("m12", [])
    check(len(full_entries) == 16, f"Full corpus expected 16 entries, got {len(full_entries)}")
    categories = set(e.get("category") for e in full_entries)
    expected_cats = {"read_only_scope", "single_tool_scope", "single_call_scope",
                     "missing_confirmation", "incomplete_arguments",
                     "high_impact_tool_boundary", "control_safe_invocation"}
    for cat in expected_cats:
        check(cat in categories, f"Full corpus missing category: {cat}")

    # MVP corpus
    print("\n[4/8] MVP corpus structure...")
    with open(ROOT / "capability_modules/corpora/phase40a_m12_tool_invocation_safety/m12_mvp_corpus.yaml") as f:
        mvp = yaml.safe_load(f)
    check("m12" in mvp, "MVP corpus missing top-level m12 key")
    mvp_entries = mvp.get("m12", [])
    check(len(mvp_entries) == 8, f"MVP corpus expected 8 entries, got {len(mvp_entries)}")

    # Check required M12 fields in corpus entries
    print("\n[5/8] Corpus field completeness...")
    required_fields = ["corpus_id", "module_id", "category", "technique_tag",
                       "user_goal", "authorized_tool_scope", "available_tools",
                       "task_context", "prompt_text", "expected_tool_behavior",
                       "expected_boundary_signal", "control_case"]
    for entry in mvp_entries:
        for field in required_fields:
            check(field in entry, f"{entry['corpus_id']} missing field: {field}")
        check(entry["module_id"] == "M12", f"{entry['corpus_id']} module_id != M12")

    # Run config check
    print("\n[6/8] Run config...")
    with open(ROOT / "capability_engine/configs/phase40a_m12_mvp_run.yaml") as f:
        config = yaml.safe_load(f)
    check("m12" in config.get("modules", []), "Run config modules missing m12")
    check("phase40a-m12-mvp" == config.get("run_id"), "run_id mismatch")
    check("fastgpt" == config.get("target_profile", {}).get("api_type"), "api_type mismatch")
    check(config.get("result", {}).get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")

    # Execution results
    print("\n[7/8] Execution results...")
    with open(ROOT / "executions/phase40a-m12-mvp/execution_results.json") as f:
        results = json.load(f)
    check(len(results) == 8, f"Expected 8 execution results, got {len(results)}")
    ok_count = sum(1 for r in results if r.get("api_response", {}).get("ok"))
    check(ok_count >= 6, f"Only {ok_count} OK responses")
    check(results[0].get("module_id") == "m12", "First entry should be m12 module")

    # M12 result YAML fields
    print("\n[8/8] m12_result.yaml fields...")
    with open(ROOT / "executions/phase40a-m12-mvp/m12_result.yaml") as f:
        m12_result = yaml.safe_load(f)
    expected_fields = [
        "module_id", "request_count", "ok_count", "error_count",
        "signal_count", "refusal_count", "inconclusive_count",
        "human_review_required_count", "strongest_techniques",
        "weakest_techniques", "technique_details",
        "capability_value", "assessment_reason",
        # M12-specific fields
        "tool_scope_preserved_count",
        "unauthorized_tool_suggested_count",
        "unrelated_tool_suggested_count",
        "excessive_tool_invocation_count",
        "read_to_write_tool_escalation_count",
        "missing_confirmation_tool_call_count",
        "incomplete_argument_tool_call_count",
        "high_impact_tool_suggested_count",
        "safe_tool_refusal_count",
        "likely_false_positive_count",
        "tool_invocation_risk_level",
    ]
    for field in expected_fields:
        check(field in m12_result, f"m12_result missing field: {field}")

    # Verify risk level and capability_value semantics
    cap_value = m12_result.get("capability_value", "")
    risk_level = m12_result.get("tool_invocation_risk_level", "")
    check(cap_value in ("high", "medium", "low"), f"Invalid capability_value: {cap_value}")
    check(risk_level in ("high", "medium", "low"), f"Invalid risk_level: {risk_level}")

    # Check scorecard
    with open(ROOT / "executions/phase40a-m12-mvp/capability_scorecard.yaml") as f:
        scorecard = yaml.safe_load(f)
    check("scorecard_metadata" in scorecard, "Scorecard missing metadata")
    check("modules" in scorecard, "Scorecard missing modules")
    check("m12" in scorecard.get("modules", {}), "Scorecard missing m12")
    check(scorecard["scorecard_metadata"].get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")
    sc_m12 = scorecard["modules"]["m12"]
    for field in expected_fields:
        check(field in sc_m12, f"Scorecard m12 missing field: {field}")

    # Check neutral assessment language
    reason = m12_result.get("assessment_reason", "")
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
