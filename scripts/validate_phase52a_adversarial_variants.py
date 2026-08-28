#!/usr/bin/env python3
"""
Phase 52A — Adversarial Variant Corpus Sprint MVP Validation
Validates: corpus, MVP corpus, execution results, per-module results,
adversarial variant-specific metrics, security boundaries.
"""
import json, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "executions" / "phase52a-adversarial-variants"

errors = []

def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  ❌ {msg}")
    else:
        print(f"  ✅ {msg}")

print("=" * 60)
print("Phase 52A — Adversarial Variant Corpus Sprint Validation")
print("=" * 60)

# 1. File existence
print("\n--- 1. Required files ---")
corpus_dir = ROOT / "capability_modules" / "corpora" / "phase52a_adversarial_variants"
check(corpus_dir.exists(), "corpus directory exists")
check((corpus_dir / "adversarial_variant_corpus.yaml").exists(), "full corpus exists")
check((corpus_dir / "adversarial_variant_mvp_corpus.yaml").exists(), "MVP corpus exists")
check((ROOT / "capability_engine" / "configs" / "phase52a_adversarial_variants_run.yaml").exists(), "run config exists")

# 2. Result files
print("\n--- 2. Result files ---")
for name in ["execution_results.json", "capability_scorecard.yaml"]:
    check((RESULT_DIR / name).exists(), f"{name} exists")
for m in ["m04", "m07", "m08", "m12", "m13", "m19", "m38", "m41"]:
    check((RESULT_DIR / f"{m}_result.yaml").exists(), f"{m}_result.yaml exists")

with open(RESULT_DIR / "execution_results.json") as f:
    exec_data = json.load(f)
with open(RESULT_DIR / "capability_scorecard.yaml") as f:
    sc = yaml.safe_load(f)

# 3. Execution size
print("\n--- 3. Execution size ---")
check(len(exec_data) == 16, f"16 execution entries (got {len(exec_data)})")
ok_count = sum(1 for r in exec_data if r["api_response"].get("ok"))
check(ok_count == 16, f"16 successful API calls (got {ok_count})")

# 4. Module coverage — from corpus
print("\n--- 4. Module coverage ---")
expected_modules = {"m04", "m07", "m19", "m08", "m41", "m38", "m12", "m13"}
with open(corpus_dir / "adversarial_variant_mvp_corpus.yaml") as f:
    mvp = yaml.safe_load(f)
present_modules = set(k for k in mvp if k in expected_modules)
for m in sorted(expected_modules):
    check(m in present_modules, f"module '{m}' in MVP corpus")
    entries = mvp.get(m, [])
    check(len(entries) == 2, f"module '{m}' has 2 entries (got {len(entries)})")

# 5. Scorecard module coverage
print("\n--- 5. Scorecard module coverage ---")
scorecard_modules = set(sc.get("modules", {}).keys())
for m in sorted(expected_modules):
    check(m in scorecard_modules, f"scorecard has '{m}'")

# 6. Adversarial variant metrics
print("\n--- 6. Adversarial variant metrics ---")
for m in sorted(expected_modules):
    mod = sc.get("modules", {}).get(m, {})
    # Check each module has technique_details for its adversarial variant
    details = mod.get("technique_details", {})
    check(len(details) == 2, f"{m}: 2 techniques in scorecard (got {len(details)})")

# 7. Module-level results
print("\n--- 7. Module-level results ---")
for m in sorted(expected_modules):
    result_path = RESULT_DIR / f"{m}_result.yaml"
    with open(result_path) as f:
        result = yaml.safe_load(f)
    check(result is not None, f"{m}_result.yaml is parseable")
    entries_count = result.get("entries_count", 0)
    check(entries_count == 2, f"{m}: 2 entries (got {entries_count})")

# 8. Security boundaries — no real data in corpus
print("\n--- 8. Security boundaries ---")
for r in exec_data:
    check(r["api_response"].get("ok") == True, f"{r['corpus_id']}: API call succeeded")

corpus_text = (corpus_dir / "adversarial_variant_mvp_corpus.yaml").read_text()
check("<SIM_" in corpus_text or "<FAKE_" in corpus_text, "SIM_/FAKE_ placeholders in corpus")
check("sk-" not in corpus_text.lower(), "No sk- secret pattern")
check("real_token" not in corpus_text.lower(), "No real_token pattern")

# 9. Overall scorecard metadata
print("\n--- 9. Scorecard metadata ---")
meta = sc.get("scorecard_metadata", {})
check(meta.get("run_id") == "phase52a-adversarial-variants", "run_id correct")
check(meta.get("phase") == "phase52a", "phase correct")
check(meta.get("overall_capability_value") in ("high", "medium"), "overall capability reasonable")
check(meta.get("successful_calls") == 16, "successful_calls=16")

# Summary
print("\n" + "=" * 60)
if errors:
    print(f"❌ FAILED: {len(errors)} error(s)")
    for e in errors:
        print(f"  - {e}")
    import sys; sys.exit(1)
else:
    print(f"✅ ALL CHECKS PASSED")
    import sys; sys.exit(0)
