#!/usr/bin/env python3
"""Phase 57A.1 — Tool Trace Error Replay Validation"""
import json, yaml, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASE57A_DIR = ROOT / "executions/phase57a-simulated-tool-trace-full"
OUT_DIR = ROOT / "executions/phase57a1-tooltrace-error-replay"

checks = []
errors = []

def check(name, ok, detail=""):
    checks.append((name, ok, detail))
    if not ok:
        errors.append(name)

# === Phase 57A original results preserved ===
for fname in ["execution_results.json", "execution_results_raw_16.json",
              "execution_results_fanout_36.json", "tool_trace_result.yaml",
              "capability_scorecard.yaml"]:
    check(f"Phase 57A {fname} still exists", (PHASE57A_DIR / fname).exists())

if (PHASE57A_DIR / "execution_results.json").exists():
    with open(PHASE57A_DIR / "execution_results.json") as f:
        p57a_raw = json.load(f)
    check("Phase 57A raw still has 16 entries", len(p57a_raw) == 16, f"got {len(p57a_raw)}")

# === Phase 57A M38 parser FP resolved in Phase 57A.2 ===
if (PHASE57A_DIR / "tool_trace_result.yaml").exists():
    with open(PHASE57A_DIR / "tool_trace_result.yaml") as f:
        p57a_tt = yaml.safe_load(f)
    m38 = p57a_tt.get("m38", {})
    check("Phase 57A M38 unsafe == 0 (parser FP resolved)",
          m38.get("unsafe_tool_trace_proposed_count", 0) == 0,
          f"got {m38.get('unsafe_tool_trace_proposed_count')}")
    check("Phase 57A M38 risk_level == low (FP corrected)",
          m38.get("tool_trace_risk_level") == "low",
          f"got {m38.get('tool_trace_risk_level')}")

# === Replay output files exist ===
for fname in ["execution_results.json", "execution_results_fanout.json",
              "tool_trace_result.yaml", "capability_scorecard.yaml"]:
    check(f"Replay {fname} exists", (OUT_DIR / fname).exists())

# === Replay only contains the 5 error entries ===
REPLAY_IDS = {"SIM-TT-002", "SIM-TT-004", "SIM-TT-006", "SIM-TT-007b", "SIM-TT-008"}
if (OUT_DIR / "execution_results.json").exists():
    with open(OUT_DIR / "execution_results.json") as f:
        replay_raw = json.load(f)
    check("Replay has 5 entries", len(replay_raw) == 5, f"got {len(replay_raw)}")
    replay_ids = {r["corpus_id"] for r in replay_raw}
    check("Replay only contains SIM-TT-002/004/006/007b/008",
          replay_ids == REPLAY_IDS, f"got {replay_ids}")

# === No real secrets/tokens/PII/customer/order/contract/account ===
SENSITIVE_PATTERNS = [
    "sk-", "real-customer", "real-order", "real-account", "real-contract",
    "pii-", "ssn-", "credit-", "bank-",
]
def check_no_sensitive(content, label):
    found = [p for p in SENSITIVE_PATTERNS if p.lower() in content.lower()]
    check(f"No real secrets in {label}", not found,
          f"found patterns: {found}")

if (OUT_DIR / "execution_results.json").exists():
    with open(OUT_DIR / "execution_results.json") as f:
        text = f.read()
    check_no_sensitive(text, "replay execution_results.json")
if (OUT_DIR / "execution_results_fanout.json").exists():
    with open(OUT_DIR / "execution_results_fanout.json") as f:
        text = f.read()
    check_no_sensitive(text, "replay execution_results_fanout.json")

# === All tool names start with fake_ ===
if (OUT_DIR / "execution_results.json").exists():
    with open(OUT_DIR / "execution_results.json") as f:
        data = json.load(f)
    tool_actions = set()
    for r in data:
        ta = r.get("requested_tool_action", "")
        if ta:
            tool_actions.add(ta)
    non_fake = [t for t in tool_actions if not t.startswith("fake_")]
    check("All tool names start with fake_", not non_fake,
          f"non-fake tools: {non_fake}")

# === All resources use <SIM_...> placeholders ===
if (OUT_DIR / "execution_results.json").exists():
    with open(OUT_DIR / "execution_results.json") as f:
        data = json.load(f)
    for r in data:
        resource = r.get("requested_resource", "")
        if resource:
            check(f"{r['corpus_id']} resource uses SIM_ placeholder",
                  "SIM_" in resource or not resource,
                  f"resource: {resource[:100]}")

# === Replay tool_trace_result has all expected modules ===
EXPECTED_MODULES = {"m07", "m08", "m12", "m13", "m15", "m41"}
if (OUT_DIR / "tool_trace_result.yaml").exists():
    with open(OUT_DIR / "tool_trace_result.yaml") as f:
        tt = yaml.safe_load(f)
    present = set(tt.keys()) & EXPECTED_MODULES
    check(f"Replay tool_trace_result has all modules (got {present})",
          present == EXPECTED_MODULES)

# === Replay results document the error ===
if (OUT_DIR / "execution_results.json").exists():
    with open(OUT_DIR / "execution_results.json") as f:
        data = json.load(f)
    for r in data:
        resp = r.get("api_response", {})
        if not resp.get("ok"):
            check(f"{r['corpus_id']} error documented (status={resp.get('status')})",
                  resp.get("status") in (0, 404, 502),
                  f"unexpected status: {resp.get('status')}")

# === All replay entries are marked is_tooltrace ===
if (OUT_DIR / "execution_results.json").exists():
    with open(OUT_DIR / "execution_results.json") as f:
        data = json.load(f)
    all_tt = all(r.get("is_tooltrace", False) for r in data)
    check("All replay entries marked is_tooltrace", all_tt)

# Summary
print(f"Phase 57A.1 Validation: {len(checks)} checks, {len(checks) - len(errors)} passed, {len(errors)} failed")
if errors:
    for e in errors:
        print(f"  FAILED: {e}")
    sys.exit(1)
else:
    print("  All checks PASSED")
    sys.exit(0)
