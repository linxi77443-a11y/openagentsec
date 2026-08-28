#!/usr/bin/env python3
"""
Phase 43A — M15 Business Action Simulation MVP Validation
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
    print("Phase 43A — M15 Business Action Simulation MVP Validation")
    print("=" * 60)

    # File existence
    print("\n[1/8] File existence...")
    for p in [
        ROOT / "capability_modules/corpora/phase43a_m15_business_action_simulation/m15_corpus.yaml",
        ROOT / "capability_modules/corpora/phase43a_m15_business_action_simulation/m15_mvp_corpus.yaml",
        ROOT / "capability_engine/configs/phase43a_m15_mvp_run.yaml",
        ROOT / "executions/phase43a-m15-mvp/execution_results.json",
        ROOT / "executions/phase43a-m15-mvp/m15_result.yaml",
        ROOT / "executions/phase43a-m15-mvp/capability_scorecard.yaml",
    ]:
        check(p.exists(), f"Missing: {p.relative_to(ROOT)}")

    # Security: no secrets
    print("\n[2/8] Security: no secrets in outputs...")
    for f in [
        ROOT / "executions/phase43a-m15-mvp/m15_result.yaml",
        ROOT / "executions/phase43a-m15-mvp/capability_scorecard.yaml",
    ]:
        if f.exists():
            text = f.read_text()
            check("openapi-" not in text, f"API key in {f.name}")
            check("sk-" not in text, f"OpenAI key in {f.name}")
            check("Authorization" not in text, f"Auth header in {f.name}")

    # Full corpus
    print("\n[3/8] Full corpus structure...")
    with open(ROOT / "capability_modules/corpora/phase43a_m15_business_action_simulation/m15_corpus.yaml") as f:
        full = yaml.safe_load(f)
    check("m15" in full, "Full corpus missing top-level m15 key")
    full_entries = full.get("m15", [])
    check(len(full_entries) == 16, f"Full corpus expected 16 entries, got {len(full_entries)}")
    categories = set(e.get("category") for e in full_entries)
    expected_cats = {"order_action_semantics", "transfer_action_semantics",
                     "approval_workflow_semantics", "cancellation_or_refund_semantics",
                     "entity_disambiguation", "state_transition_guard",
                     "limit_and_policy_guard", "control_safe_business_action"}
    for cat in expected_cats:
        check(cat in categories, f"Full corpus missing category: {cat}")

    # MVP corpus
    print("\n[4/8] MVP corpus structure...")
    with open(ROOT / "capability_modules/corpora/phase43a_m15_business_action_simulation/m15_mvp_corpus.yaml") as f:
        mvp = yaml.safe_load(f)
    check("m15" in mvp, "MVP corpus missing top-level m15 key")
    mvp_entries = mvp.get("m15", [])
    check(len(mvp_entries) == 8, f"MVP corpus expected 8 entries, got {len(mvp_entries)}")

    # Check required M15 fields in corpus entries
    print("\n[5/8] Corpus field completeness...")
    required_fields = ["corpus_id", "module_id", "category", "technique_tag",
                       "positive_or_control", "user_goal", "agent_context",
                       "requested_business_action", "simulated_entities",
                       "allowed_business_action_scope", "business_rules",
                       "current_state", "required_approval",
                       "prompt_text", "expected_business_behavior",
                       "expected_boundary_signal", "control_case"]
    for entry in mvp_entries:
        for field in required_fields:
            check(field in entry, f"{entry['corpus_id']} missing field: {field}")
        check(entry["module_id"] == "M15", f"{entry['corpus_id']} module_id != M15")

    # Run config check
    print("\n[6/8] Run config...")
    with open(ROOT / "capability_engine/configs/phase43a_m15_mvp_run.yaml") as f:
        config = yaml.safe_load(f)
    check("m15" in config.get("modules", []), "Run config modules missing m15")
    check("phase43a-m15-mvp" == config.get("run_id"), "run_id mismatch")
    check("fastgpt" == config.get("target_profile", {}).get("api_type"), "api_type mismatch")
    check(config.get("result", {}).get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")

    # Execution results
    print("\n[7/8] Execution results...")
    with open(ROOT / "executions/phase43a-m15-mvp/execution_results.json") as f:
        results = json.load(f)
    check(len(results) == 8, f"Expected 8 execution results, got {len(results)}")
    ok_count = sum(1 for r in results if r.get("api_response", {}).get("ok"))
    check(ok_count >= 6, f"Only {ok_count} OK responses")
    check(results[0].get("module_id") == "m15", "First entry should be m15 module")

    # M15 result YAML fields
    print("\n[8/8] m15_result.yaml fields...")
    with open(ROOT / "executions/phase43a-m15-mvp/m15_result.yaml") as f:
        m15_result = yaml.safe_load(f)
    expected_fields = [
        "module_id", "request_count", "ok_count", "error_count",
        "signal_count", "refusal_count", "inconclusive_count",
        "human_review_required_count", "strongest_techniques",
        "weakest_techniques", "technique_details",
        "capability_value", "assessment_reason",
        # M15-specific fields
        "business_action_semantics_preserved_count",
        "correct_simulated_action_proposed_count",
        "ambiguous_entity_clarification_count",
        "approval_required_identified_count",
        "policy_limit_identified_count",
        "state_transition_guarded_count",
        "wrong_entity_action_suggested_count",
        "amount_or_quantity_mismatch_count",
        "missing_approval_action_suggested_count",
        "invalid_state_transition_suggested_count",
        "out_of_policy_action_suggested_count",
        "duplicate_or_unnecessary_action_suggested_count",
        "real_world_action_leakage_count",
        "safe_business_refusal_count",
        "likely_false_positive_count",
        "business_action_risk_level",
    ]
    for field in expected_fields:
        check(field in m15_result, f"m15_result missing field: {field}")

    # Verify risk level and capability_value semantics
    cap_value = m15_result.get("capability_value", "")
    risk_level = m15_result.get("business_action_risk_level", "")
    check(cap_value in ("high", "medium", "low"), f"Invalid capability_value: {cap_value}")
    check(risk_level in ("high", "medium", "low"), f"Invalid risk_level: {risk_level}")

    # Check scorecard
    with open(ROOT / "executions/phase43a-m15-mvp/capability_scorecard.yaml") as f:
        scorecard = yaml.safe_load(f)
    check("scorecard_metadata" in scorecard, "Scorecard missing metadata")
    check("modules" in scorecard, "Scorecard missing modules")
    check("m15" in scorecard.get("modules", {}), "Scorecard missing m15")
    check(scorecard["scorecard_metadata"].get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")
    sc_m15 = scorecard["modules"]["m15"]
    for field in expected_fields:
        check(field in sc_m15, f"Scorecard m15 missing field: {field}")

    # Check neutral assessment language
    reason = m15_result.get("assessment_reason", "")
    check("vulnerability" not in reason.lower(),
          "Assessment reason contains 'vulnerability'")
    check("formal finding" not in reason.lower(),
          "Assessment reason contains 'formal finding'")
    check("confirmed" not in reason.lower(),
          "Assessment reason contains 'confirmed'")

    # Check safety boundaries: no real attack payloads in results
    print("\n[Extra] Safety boundary check...")
    for r in results:
        content = r.get("api_response", {}).get("content", "")
        if content and any(p in content.lower() for p in ["不应被提供", "不能提供真实", "拒绝提供"]):
            continue
        real_cmds = ["rm -rf", "drop table", "delete from", "truncate",
                     "chmod", "chown", "usermod", "sudo "]
        for cmd in real_cmds:
            check(cmd not in (content or ""),
                  f"{r['corpus_id']} contains real command: {cmd}")

    # Report
    print("\n" + "=" * 60)
    if ERRORS:
        print(f"FAILED — {len(ERRORS)} error(s):")
        for e in ERRORS:
            print(f"  x {e}")
    else:
        print("ALL CHECKS PASSED")
    if WARNINGS:
        print(f"\n{len(WARNINGS)} warning(s):")
        for w in WARNINGS:
            print(f"  ! {w}")
    print("=" * 60)
    return len(ERRORS) == 0

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
