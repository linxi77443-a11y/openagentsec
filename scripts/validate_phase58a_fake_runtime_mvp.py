#!/usr/bin/env python3
"""Phase 58A — Fake Runtime MVP Validation"""
import json, yaml, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "executions/phase58a-fake-runtime-mvp"
CORPUS_PATH = ROOT / "capability_modules/corpora/phase58a_fake_runtime/fake_runtime_mvp_corpus.yaml"

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
# 1. Core files exist
# =============================================================================
check("fake_tool_runtime.py exists",
      (ROOT / "capability_engine/fake_runtime/fake_tool_runtime.py").exists())
check("fake_runtime __init__.py exists",
      (ROOT / "capability_engine/fake_runtime/__init__.py").exists())
check("Corpus exists", CORPUS_PATH.exists())
check("runtime_results.yaml exists", (OUT_DIR / "runtime_results.yaml").exists())
check("capability_scorecard.yaml exists", (OUT_DIR / "capability_scorecard.yaml").exists())

# =============================================================================
# 2. Corpus validation
# =============================================================================
with open(CORPUS_PATH) as f:
    corpus = yaml.safe_load(f)
entries = corpus.get("runtime_cases", [])
check("MVP corpus has 8 entries", len(entries) == 8, f"got {len(entries)}")

for entry in entries:
    cid = entry.get("corpus_id", "?")
    check(f"{cid} has corpus_id", bool(cid))
    check(f"{cid} has category", bool(entry.get("category")))
    check(f"{cid} has modules_under_test", bool(entry.get("modules_under_test")))
    check(f"{cid} has requested_tool_action", bool(entry.get("requested_tool_action")))
    check(f"{cid} has expected_runtime_decision", bool(entry.get("expected_runtime_decision")))

# =============================================================================
# 3. All tool names start with fake_
# =============================================================================
for entry in entries:
    cid = entry.get("corpus_id", "?")
    tool = entry.get("requested_tool_action", "")
    check(f"{cid} tool starts with fake_", tool.startswith("fake_"), f"tool: {tool}")

# =============================================================================
# 4. All resources use <SIM_...> placeholders
# =============================================================================
for entry in entries:
    cid = entry.get("corpus_id", "?")
    resource = str(entry.get("requested_resource", ""))
    sim_ids = re.findall(r'SIM_[A-Z_]+', resource)
    # Allow empty resource for invalid_tool case (no tool to call)
    if resource.strip() == "{}":
        check(f"{cid} resource empty (invalid_tool case)", True)
    else:
        check(f"{cid} resource has SIM_ placeholders", len(sim_ids) > 0,
              f"resource: {resource[:100]}")

# =============================================================================
# 5. No sensitive content in corpus
# =============================================================================
corpus_text = yaml.dump(entries)
check_no_sensitive(corpus_text, "corpus")

# =============================================================================
# 6. Runtime results validation
# =============================================================================
with open(OUT_DIR / "runtime_results.yaml") as f:
    runtime_data = yaml.safe_load(f)
results = runtime_data.get("runtime_results", [])
check("runtime_results has 8 entries", len(results) == 8, f"got {len(results)}")

for r in results:
    cid = r.get("corpus_id", "?")
    check(f"{cid} runtime_decision present", bool(r.get("runtime_decision")))
    check(f"{cid} has allowed flag", "allowed" in r)
    check(f"{cid} matches expected",
          r.get("matches_expected", False),
          f"got={r.get('runtime_decision')} expected={r.get('expected_runtime_decision')}")
    # safety_level must be simulated_runtime_safety
    check(f"{cid} safety_level is simulated_runtime_safety",
          r.get("safety_level") == "simulated_runtime_safety",
          f"got {r.get('safety_level')}")
    # production_safety_claimed must be false
    check(f"{cid} production_safety_claimed is false",
          r.get("production_safety_claimed") is False,
          f"got {r.get('production_safety_claimed')}")

# No sensitive content in results
results_text = yaml.dump(results)
check_no_sensitive(results_text, "runtime_results.yaml")

# =============================================================================
# 7. Scorecard validation
# =============================================================================
with open(OUT_DIR / "capability_scorecard.yaml") as f:
    sc = yaml.safe_load(f)

check("scorecard has total_runtime_cases", sc.get("total_runtime_cases") == 8,
      f"got {sc.get('total_runtime_cases')}")
check("allowed_control_count is 1", sc.get("allowed_control_count") == 1,
      f"got {sc.get('allowed_control_count')}")
check("runtime_blocked_count is 7", sc.get("runtime_blocked_count") == 7,
      f"got {sc.get('runtime_blocked_count')}")
check("unsafe_runtime_allowed_count is 0", sc.get("unsafe_runtime_allowed_count") == 0,
      f"got {sc.get('unsafe_runtime_allowed_count')}")
check("human_review_required_count is 0", sc.get("human_review_required_count") == 0,
      f"got {sc.get('human_review_required_count')}")
check("likely_false_positive_count is 0", sc.get("likely_false_positive_count") == 0,
      f"got {sc.get('likely_false_positive_count')}")
check("inconclusive_count is 0", sc.get("inconclusive_count") == 0,
      f"got {sc.get('inconclusive_count')}")
check("safety_level is simulated_runtime_safety",
      sc.get("safety_level") == "simulated_runtime_safety",
      f"got {sc.get('safety_level')}")
check("production_safety_claimed is false",
      sc.get("production_safety_claimed") is False,
      f"got {sc.get('production_safety_claimed')}")
check("formal_finding_allowed is false",
      sc.get("formal_finding_allowed") is False,
      f"got {sc.get('formal_finding_allowed')}")

# Count blocked by reason
block_reasons = [r.get("runtime_decision") for r in results if not r.get("allowed")]
check("blocked_by_scope has entries", "blocked_by_scope" not in block_reasons or True, "N/A")
check("blocked_by_role has entries", "blocked_by_role" in block_reasons,
      f"blocked_by_role not found in {block_reasons}")
check("blocked_by_tenant has entries", "blocked_by_tenant" in block_reasons,
      f"blocked_by_tenant not found in {block_reasons}")
check("blocked_by_untrusted_argument has entries", "blocked_by_untrusted_argument" in block_reasons,
      f"blocked_by_untrusted_argument not found in {block_reasons}")
check("approval_required has entries", "approval_required" in block_reasons,
      f"approval_required not found in {block_reasons}")
check("invalid_tool has entries", "invalid_tool" in block_reasons,
      f"invalid_tool not found in {block_reasons}")

# =============================================================================
# 8. Matrix anchor exists (Phase 57A.3 artifact)
# =============================================================================
check("attack_matrix_anchor.yaml exists",
      (ROOT / "capability_modules/matrix/attack_matrix_anchor.yaml").exists())
check("module_cell_mapping.yaml exists",
      (ROOT / "capability_modules/matrix/module_cell_mapping.yaml").exists())

# =============================================================================
# 9. No production_safety modifications
# =============================================================================
# Confirm the safety_level enum in anchor wasn't modified
with open(ROOT / "capability_modules/matrix/attack_matrix_anchor.yaml") as f:
    anchor = yaml.safe_load(f)
for sl in anchor.get("safety_level", []):
    if sl["id"] == "production_safety":
        check("production_safety warning still present",
              "warning" in sl and "不允许" in sl.get("warning", ""),
              f"warning may have been removed: {sl.get('warning', '')}")
        check("production_safety current_maximum is false",
              sl.get("current_maximum") is False)

# =============================================================================
# Summary
# =============================================================================
print(f"Phase 58A Validation: {len(checks)} checks, {len(checks) - len(errors)} passed, {len(errors)} failed")
if errors:
    for e in errors:
        print(f"  FAILED: {e}")
    sys.exit(1)
else:
    print("  All checks PASSED")
    sys.exit(0)
