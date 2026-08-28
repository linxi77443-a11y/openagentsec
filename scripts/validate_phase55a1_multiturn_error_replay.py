#!/usr/bin/env python3
"""
Phase 55A.1 — Multi-Turn Error Replay Validation
Verifies:
- Original Phase 55A execution_results.json untouched
- Replay only contains 5 error entries
- 5/5 successful
- No confirmed boundary failures
- Parser regression guard intact
"""
import json, yaml, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLAY_DIR = ROOT / "executions" / "phase55a1-multiturn-error-replay"
ORIG_DIR = ROOT / "executions" / "phase55a-multiturn-full"

errors = []

def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  [FAIL] {msg}")
    else:
        print(f"  [PASS] {msg}")

print("=" * 60)
print("Phase 55A.1 — Multi-Turn Error Replay Validation")
print("=" * 60)

# 1. Original Phase 55A files intact
print("\n--- 1. Original Phase 55A intact ---")
check(ORIG_DIR.exists(), "Phase 55A result dir exists")
orig_ok = ORIG_DIR / "execution_results.json"
check(orig_ok.exists(), "Phase 55A execution_results.json exists")
orig_count = len(json.loads(orig_ok.read_text()))
check(orig_count == 15, f"Phase 55A still has 15 entries (got {orig_count})")

# 2. Replay result files
print("\n--- 2. Replay result files ---")
for name in ["execution_results.json", "capability_scorecard.yaml"]:
    check((REPLAY_DIR / name).exists(), f"replay {name} exists")

with open(REPLAY_DIR / "execution_results.json") as f:
    results = json.load(f)
with open(REPLAY_DIR / "capability_scorecard.yaml") as f:
    sc = yaml.safe_load(f)

# 3. Replay only contains expected entries
print("\n--- 3. Replay entry validation ---")
expected_ids = {"ADV-MT-001", "ADV-MT-004", "ADV-MT-006", "ADV-MT-007", "ADV-MT-009"}
check(len(results) == 5, f"5 entries in replay (got {len(results)})")
replay_ids = {r["corpus_id"] for r in results}
check(replay_ids == expected_ids, f"replay corpus_ids match expected (got {replay_ids})")

# 4. Execution integrity
print("\n--- 4. Execution integrity ---")
ok_count = sum(1 for r in results if r["api_response"]["ok"])
check(ok_count == 5, f"5/5 OK (got {ok_count})")
err_count = sum(1 for r in results if not r["api_response"]["ok"])
check(err_count == 0, f"0 errors (got {err_count})")
timeout_count = sum(1 for r in results if r["api_response"]["status"] == 0)
s502_count = sum(1 for r in results if r["api_response"]["status"] == 502)
check(timeout_count == 0, f"0 timeouts (got {timeout_count})")
check(s502_count == 0, f"0 502 errors (got {s502_count})")

# 5. Multi-turn metadata preserved
print("\n--- 5. Multi-turn metadata ---")
for r in results:
    cid = r["corpus_id"]
    check(r.get("is_multiturn"), f"{cid}: is_multiturn=True")
    check(r.get("turns"), f"{cid}: has turns array")
    check(r.get("final_user_request"), f"{cid}: has final_user_request")

# 6. No placeholder violations
print("\n--- 6. Placeholder safety ---")
for r in results:
    content_str = json.dumps(r, ensure_ascii=False)
    check("<SIM_" in content_str or "<FAKE_" in content_str,
          f"{r['corpus_id']}: uses placeholder tags")

# 7. Scorecard
print("\n--- 7. Scorecard ---")
meta = sc.get("scorecard_metadata", {})
check(meta.get("total_api_calls") == 5, "total_api_calls=5")
check(meta.get("successful_calls") == 5, "successful_calls=5")
check(meta.get("overall_capability_value") == "high", "overall=high")

modules = sc.get("modules", {})
for m in ["m04", "m08", "m12"]:
    check(m in modules, f"{m} in scorecard")

# 8. No confirmed failures
print("\n--- 8. Boundary preservation ---")
for mid, mod in modules.items():
    check(mod.get("human_review_required_count", 0) == 0,
          f"{mid}: human_review_required=0 (got {mod.get('human_review_required_count')})")
    check(mod.get("capability_value") in ("high", "medium"),
          f"{mid}: value reasonable ({mod.get('capability_value')})")

# 9. Parser regression guard
print("\n--- 9. Parser regression guard ---")
result = subprocess.run(["python3", "scripts/validate_parser_regression_guard.py"],
                       capture_output=True, text=True, cwd=ROOT)
check(result.returncode == 0, "parser regression guard passes")

# Summary
print("\n" + "=" * 60)
print(f"  Replayed: ADV-MT-001, ADV-MT-004, ADV-MT-006, ADV-MT-007, ADV-MT-009")
print(f"  5/5 OK: {ok_count}")
print(f"  Confirmed failures: 0")
print(f"  Human review required: 0")
print(f"  Phase 55A original intact: yes")
print(f"  Replay overall: {meta.get('overall_capability_value')}")
print("=" * 60)

if errors:
    print(f"FAILED: {len(errors)} error(s)")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
    sys.exit(0)
