#!/usr/bin/env python3
"""Phase 58A — Fake Runtime MVP Execution Runner.

Loads corpus, evaluates each entry through fake runtime, saves results + scorecard.
No real system access, no real data, no real tool execution.
"""
import json, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from capability_engine.fake_runtime.fake_tool_runtime import run_corpus, build_scorecard

CORPUS_PATH = ROOT / "capability_modules/corpora/phase58a_fake_runtime/fake_runtime_mvp_corpus.yaml"
OUT_DIR = ROOT / "executions/phase58a-fake-runtime-mvp"

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load corpus
    with open(CORPUS_PATH) as f:
        corpus = yaml.safe_load(f)
    entries = corpus.get("runtime_cases", [])
    print(f"Loaded {len(entries)} corpus entries")

    # Run fake runtime
    results = run_corpus(entries)

    # Build scorecard
    scorecard = build_scorecard(results)

    # Save per-entry results
    runtime_results = []
    for entry, result in zip(entries, results):
        row = {
            "corpus_id": result.get("corpus_id", entry.get("corpus_id", "?")),
            "category": entry.get("category", ""),
            "modules_under_test": entry.get("modules_under_test", []),
            "technique_tag": entry.get("technique_tag", ""),
            "runtime_decision": result.get("runtime_decision"),
            "allowed": result.get("allowed"),
            "block_reason": result.get("block_reason", ""),
            "tool_name": result.get("tool_name", ""),
            "action_type": result.get("action_type", ""),
            "tenant_boundary_status": result.get("tenant_boundary_status", ""),
            "role_boundary_status": result.get("role_boundary_status", ""),
            "service_account_scope_status": result.get("service_account_scope_status", ""),
            "argument_integrity_status": result.get("argument_integrity_status", ""),
            "approval_status": result.get("approval_status", ""),
            "safety_level": result.get("safety_level", ""),
            "production_safety_claimed": result.get("production_safety_claimed", False),
            "expected_runtime_decision": entry.get("expected_runtime_decision", ""),
            "matches_expected": result.get("runtime_decision") == entry.get("expected_runtime_decision"),
        }
        runtime_results.append(row)

    # Write runtime_results.yaml
    out_results = OUT_DIR / "runtime_results.yaml"
    with open(out_results, "w") as f:
        yaml.dump({"phase": "phase58a", "run_id": "phase58a-fake-runtime-mvp", "runtime_results": runtime_results}, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Wrote {out_results}")

    # Write scorecard
    out_sc = OUT_DIR / "capability_scorecard.yaml"
    with open(out_sc, "w") as f:
        yaml.dump(scorecard, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Wrote {out_sc}")

    # Print summary
    print(f"\n=== Phase 58A Fake Runtime Results ===")
    print(f"Total cases: {scorecard['total_runtime_cases']}")
    print(f"Allowed: {scorecard['allowed_control_count']}")
    print(f"Blocked: {scorecard['runtime_blocked_count']}")
    print(f"  blocked_by_scope:  {scorecard['blocked_by_scope_count']}")
    print(f"  blocked_by_role:   {scorecard['blocked_by_role_count']}")
    print(f"  blocked_by_tenant: {scorecard['blocked_by_tenant_count']}")
    print(f"  blocked_by_untrusted_argument: {scorecard['blocked_by_untrusted_argument_count']}")
    print(f"  approval_required: {scorecard['approval_required_count']}")
    print(f"  invalid_tool:      {scorecard['invalid_tool_blocked_count']}")
    print(f"Unsafe allowed:      {scorecard['unsafe_runtime_allowed_count']}")
    print(f"Capability value:    {scorecard['capability_value']}")
    print(f"Risk level:          {scorecard['fake_runtime_risk_level']}")
    print(f"Safety level:        {scorecard['safety_level']}")
    print(f"Production claimed:  {scorecard['production_safety_claimed']}")

    ok = scorecard['unsafe_runtime_allowed_count'] == 0
    if not ok:
        print("\n⚠️  WARNING: unsafe_runtime_allowed_count > 0 — this is a capability signal, not a vulnerability")
        print("   No formal finding generated. No production safety claimed.")
        sys.exit(0)  # Don't fail — signals are valid outputs
    else:
        print("\n✅ All unsafe cases blocked as expected.")
        print("   This is a simulated_runtime_safety result, not production_safety.")
        sys.exit(0)


if __name__ == "__main__":
    main()
