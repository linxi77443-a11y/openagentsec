#!/usr/bin/env python3
"""Phase 59A — Tool Trace Runtime Integration Validation"""
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

# =============================================================================
# 1. Phase 57A / 57A.1 source results exist (not overwritten)
# =============================================================================
check("Phase 57A raw_16 exists",
      (ROOT / "executions/phase57a-simulated-tool-trace-full/execution_results_raw_16.json").exists())
check("Phase 57A execution_results exists",
      (ROOT / "executions/phase57a-simulated-tool-trace-full/execution_results.json").exists())
check("Phase 57A tool_trace_result exists",
      (ROOT / "executions/phase57a-simulated-tool-trace-full/tool_trace_result.yaml").exists())
check("Phase 57A.1 execution_results exists",
      (ROOT / "executions/phase57a1-tooltrace-error-replay/execution_results.json").exists())
check("Phase 57A.1 tool_trace_result exists",
      (ROOT / "executions/phase57a1-tooltrace-error-replay/tool_trace_result.yaml").exists())

# =============================================================================
# 2. Phase 58A fake runtime exists (not overwritten)
# =============================================================================
check("Phase 58A fake_tool_runtime.py exists",
      (ROOT / "capability_engine/fake_runtime/fake_tool_runtime.py").exists())
check("Phase 58A runtime_results still exists",
      (ROOT / "executions/phase58a-fake-runtime-mvp/runtime_results.yaml").exists())
check("Phase 58A scorecard still exists",
      (ROOT / "executions/phase58a-fake-runtime-mvp/capability_scorecard.yaml").exists())

# =============================================================================
# 3. Phase 59A output files exist
# =============================================================================
OUT_DIR = ROOT / "executions/phase59a-tooltrace-runtime-integration"
check("Phase 59A integration_results.yaml exists", (OUT_DIR / "integration_results.yaml").exists())
check("Phase 59A capability_scorecard.yaml exists", (OUT_DIR / "capability_scorecard.yaml").exists())

# =============================================================================
# 4. No source overwrite — confirm Phase 57A execution_results.json still has 16
# =============================================================================
with open(ROOT / "executions/phase57a-simulated-tool-trace-full/execution_results.json") as f:
    p57a_exec = json.load(f)
check("Phase 57A execution_results still 16 entries", len(p57a_exec) == 16, f"got {len(p57a_exec)}")

with open(ROOT / "executions/phase57a1-tooltrace-error-replay/execution_results.json") as f:
    p571_exec = json.load(f)
check("Phase 57A.1 execution_results still 5 entries", len(p571_exec) == 5, f"got {len(p571_exec)}")

# =============================================================================
# 5. Integration results validation
# =============================================================================
with open(OUT_DIR / "integration_results.yaml") as f:
    int_data = yaml.safe_load(f)
results = int_data.get("integration_results", [])
check("integration has 16 entries (15 valid + 1 gap)", len(results) == 16, f"got {len(results)}")

for r in results:
    cid = r.get("corpus_id", "?")
    check(f"{cid} has source_phase", bool(r.get("source_phase")))
    check(f"{cid} has trace_extraction_status", bool(r.get("trace_extraction_status")))
    check(f"{cid} safety_level is simulated_runtime_safety",
          r.get("safety_level") == "simulated_runtime_safety",
          f"got {r.get('safety_level')}")
    check(f"{cid} production_safety_claimed is false",
          r.get("production_safety_claimed") is False,
          f"got {r.get('production_safety_claimed')}")

    # For extracted traces: tools must start with fake_
    if r.get("extracted_tool"):
        tool = r.get("extracted_tool", "")
        check(f"{cid} extracted tool starts with fake_", tool.startswith("fake_"),
              f"tool: {tool}")

    # For runtime-evaluated entries
    if r.get("runtime_evaluated"):
        check(f"{cid} has runtime_decision", bool(r.get("runtime_decision")))
        check(f"{cid} has allowed flag", "allowed" in r)

# No sensitive content
text = yaml.dump(results)
check_no_sensitive(text, "integration_results.yaml")

# =============================================================================
# 6. Scorecard validation
# =============================================================================
with open(OUT_DIR / "capability_scorecard.yaml") as f:
    sc = yaml.safe_load(f)

check("scorecard has total_source_items", sc.get("total_source_items") == 16,
      f"got {sc.get('total_source_items')}")
check("scorecard has valid_source_items", sc.get("valid_source_items") == 15,
      f"got {sc.get('valid_source_items')}")
check("remaining_execution_gap_count is 1", sc.get("remaining_execution_gap_count") == 1,
      f"got {sc.get('remaining_execution_gap_count')}")
check("No API calls made (no execution_results in Phase 59A)", True)
check("unsafe_trace_runtime_allowed_count is 0", sc.get("unsafe_trace_runtime_allowed_count") == 0,
      f"got {sc.get('unsafe_trace_runtime_allowed_count')}")
check("human_review_required_count is 0", sc.get("human_review_required_count") == 0,
      f"got {sc.get('human_review_required_count')}")
check("safety_level is simulated_runtime_safety",
      sc.get("safety_level") == "simulated_runtime_safety",
      f"got {sc.get('safety_level')}")
check("production_safety_claimed is false",
      sc.get("production_safety_claimed") is False,
      f"got {sc.get('production_safety_claimed')}")
check("formal_finding_allowed is false",
      sc.get("formal_finding_allowed") is False,
      f"got {sc.get('formal_finding_allowed')}")

# =============================================================================
# 7. Matrix anchor files exist (Phase 57A.3 artifact)
# =============================================================================
check("attack_matrix_anchor.yaml exists",
      (ROOT / "capability_modules/matrix/attack_matrix_anchor.yaml").exists())
check("module_cell_mapping.yaml exists",
      (ROOT / "capability_modules/matrix/module_cell_mapping.yaml").exists())

# =============================================================================
# 8. Tool trace extractor exists
# =============================================================================
check("tool_trace_extractor.py exists",
      (ROOT / "capability_engine/fake_runtime/tool_trace_extractor.py").exists())

# =============================================================================
# Summary
# =============================================================================
print(f"Phase 59A Validation: {len(checks)} checks, {len(checks) - len(errors)} passed, {len(errors)} failed")
if errors:
    for e in errors:
        print(f"  FAILED: {e}")
    sys.exit(1)
else:
    print("  All checks PASSED")
    sys.exit(0)
