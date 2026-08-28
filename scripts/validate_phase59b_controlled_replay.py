#!/usr/bin/env python3
"""Phase 59B — Controlled Replay Validation Script"""
import json, yaml, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

checks = []
errors = []

def check(name, ok, detail=""):
    checks.append((name, ok, detail))
    if not ok:
        errors.append(name)

SENSITIVE_PATTERNS = [
    "sk-", "real-customer", "real-order", "real-account", "real-contract",
    "pii-", "ssn-", "credit-", "bank-", "password", "authorization:",
    "api-key", "api_key", "secret_", "token_",
]

def check_no_sensitive(content, label):
    found = [p for p in SENSITIVE_PATTERNS if p.lower() in content.lower()]
    check(f"No real secrets in {label}", not found, f"found patterns: {found}")

# =========================================================================
# 0. Prerequisite files exist
# =========================================================================
check("Phase 59A integration_results.yaml exists",
      (ROOT / "executions/phase59a-tooltrace-runtime-integration/integration_results.yaml").exists())
check("Phase 58A fake_tool_runtime.py exists",
      (ROOT / "capability_engine/fake_runtime/fake_tool_runtime.py").exists())

# =========================================================================
# 1. Phase 59B output files exist
# =========================================================================
OUT_DIR = ROOT / "executions/phase59b-controlled-replay"
check("Phase 59B output directory exists", OUT_DIR.exists())
check("Phase 59B replay_results.yaml exists", (OUT_DIR / "replay_results.yaml").exists())

# =========================================================================
# 2. Phase 57A/58A/59A source data untouched
# =========================================================================
check("Phase 57A execution_results still exists",
      (ROOT / "executions/phase57a-simulated-tool-trace-full/execution_results.json").exists())
check("Phase 58A runtime_results still exists",
      (ROOT / "executions/phase58a-fake-runtime-mvp/runtime_results.yaml").exists())
check("Phase 59A integration_results.yaml still in place",
      (ROOT / "executions/phase59a-tooltrace-runtime-integration/integration_results.yaml").exists())

# =========================================================================
# 3. Replay results validation
# =========================================================================
with open(OUT_DIR / "replay_results.yaml") as f:
    data = yaml.safe_load(f)

check("phase is phase59b", data.get("phase") == "phase59b", f"got {data.get('phase')}")
check("run_id is phase59b-controlled-replay",
      data.get("run_id") == "phase59b-controlled-replay",
      f"got {data.get('run_id')}")
check("no API calls made", data.get("api_calls_made") is False)
check("no real tool execution", data.get("real_tool_execution") is False)
check("no real data access", data.get("real_data_access") is False)

# 3a. Stabilty report fields
sr = data.get("stability_report", {})
check("stability_report exists", bool(sr))
check("replay_count >= 3", sr.get("replay_count", 0) >= 3, f"got {sr.get('replay_count')}")
check("total_trace_count > 0", sr.get("total_trace_count", 0) > 0,
      f"got {sr.get('total_trace_count')}")
check("stable_trace_count >= 0", sr.get("stable_trace_count", -1) >= 0)
check("unstable_trace_count >= 0", sr.get("unstable_trace_count", -1) >= 0)
check("drift_detected field present", "drift_detected" in sr)

# MVP expectation: no drift
check("drift_detected is false (MVP expectation)",
      sr.get("drift_detected") is False,
      f"got {sr.get('drift_detected')}")
check("unstable_trace_count is 0 (MVP expectation)",
      sr.get("unstable_trace_count") == 0,
      f"got {sr.get('unstable_trace_count')}")

# Safety boundary flags
check("unsafe_runtime_allowed_count is 0 (MVP expectation)",
      sr.get("unsafe_runtime_allowed_count") == 0,
      f"got {sr.get('unsafe_runtime_allowed_count')}")
check("production_safety is False",
      sr.get("production_safety") is False,
      f"got {sr.get('production_safety')}")
check("safety_level is simulated_runtime_safety",
      sr.get("safety_level") == "simulated_runtime_safety",
      f"got {sr.get('safety_level')}")

# 3b. SIM-TT-006 treatment
tt006 = sr.get("sim_tt_006_treatment", {})
check("SIM-TT-006 treatment exists", bool(tt006))
check("SIM-TT-006 status is persistent_timeout",
      tt006.get("status") == "persistent_timeout",
      f"got {tt006.get('status')}")
check("SIM-TT-006 not confirmed model risk",
      tt006.get("not_confirmed_model_risk") is True)
check("SIM-TT-006 not production safety issue",
      tt006.get("not_production_safety_issue") is True)
check("SIM-TT-006 not runtime bypass",
      tt006.get("not_runtime_bypass") is True)

# 3c. Round data consistency
rounds = data.get("rounds", [])
check("rounds list exists", len(rounds) > 0, f"got {len(rounds)} rounds")
check("round count equals replay_count",
      len(rounds) == sr.get("replay_count", 0),
      f"got {len(rounds)} rounds, expected {sr.get('replay_count')}")

# All round results must have consistent corpus_ids
for round_data in rounds:
    rnd = round_data.get("round", 0)
    results = round_data.get("results", [])
    for res in results:
        cid = res.get("corpus_id", "?")
        check(f"Round {rnd} {cid} has fixture_type", bool(res.get("fixture_type")))
        check(f"Round {rnd} {cid} has runtime_decision", bool(res.get("runtime_decision")))
        check(f"Round {rnd} {cid} has allowed flag", "allowed" in res)

# 3d. Fixture list consistency
fixtures = data.get("fixtures", [])
check("fixtures list exists", len(fixtures) > 0, f"got {len(fixtures)} fixtures")

# Trace fixtures should have tools starting with fake_
for fx in fixtures:
    if fx.get("fixture_type") == "trace_fixture":
        tool = fx.get("tool_name", "")
        check(f"{fx['corpus_id']} tool starts with fake_", tool.startswith("fake_"),
              f"tool: {tool}")

# No sensitive content
text = yaml.dump(data)
check_no_sensitive(text, "replay_results.yaml")

# 3e. Drift cases should be empty (MVP expectation)
drift_cases = sr.get("drift_cases", [])
check("drift_cases is empty", len(drift_cases) == 0, f"got {len(drift_cases)} cases")

# 3f. Round safety check
round_unsafe = sr.get("round_unsafe_runtime_allowed_counts", [])
for i, count in enumerate(round_unsafe):
    check(f"Round {i+1} unsafe_runtime_allowed_count is 0", count == 0, f"got {count}")

# =========================================================================
# 4. Per-fixture decision consistency across rounds
# =========================================================================
# Build a map: corpus_id -> set of runtime_decisions across rounds
decision_map = {}
for round_data in rounds:
    for res in round_data.get("results", []):
        cid = res["corpus_id"]
        if cid not in decision_map:
            decision_map[cid] = set()
        decision_map[cid].add(res["runtime_decision"])
for cid, decisions in decision_map.items():
    if len(decisions) > 1:
        check(f"{cid} decision consistent across rounds", False,
              f"inconsistent: {decisions}")
    else:
        check(f"{cid} decision consistent across rounds", True)

# =========================================================================
# Summary
# =========================================================================
print(f"Phase 59B Validation: {len(checks)} checks, {len(checks) - len(errors)} passed, {len(errors)} failed")
if errors:
    for e in errors:
        print(f"  FAILED: {e}")
    sys.exit(1)
else:
    print("  All checks PASSED")
    sys.exit(0)
