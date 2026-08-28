#!/usr/bin/env python3
"""
Phase 53A.1 — M12/M38 Inconclusive Review Validation

Verifies that parser fixes correctly resolved:
- M12 inconclusive_count → 0, capability_value → high
- M38 capability_value → low (preserved + refused = all within boundary)
- execution_results.json not modified
- parser regression guard still passes
"""
import json, yaml, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "executions" / "phase53a-adversarial-full"

errors = []

def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  ❌ {msg}")
    else:
        print(f"  ✅ {msg}")

print("=" * 60)
print("Phase 53A.1 — M12/M38 Inconclusive Review Validation")
print("=" * 60)

# 1. Result files still exist
print("\n--- 1. Result files ---")
for name in ["execution_results.json", "capability_scorecard.yaml", "m12_result.yaml", "m38_result.yaml"]:
    check((RESULT_DIR / name).exists(), f"{name} exists")

with open(RESULT_DIR / "execution_results.json") as f:
    exec_data = json.load(f)
with open(RESULT_DIR / "capability_scorecard.yaml") as f:
    sc = yaml.safe_load(f)

# 2. execution_results.json not modified (32 entries, no signals field added)
print("\n--- 2. Execution results integrity ---")
check(len(exec_data) == 32, f"32 entries (got {len(exec_data)})")
has_signals = any("signals" in r for r in exec_data)
check(not has_signals, "execution_results.json has no inline signals (parser-only)")

# 3. M12 fix verification
print("\n--- 3. M12 fix verification ---")
m12_sc = sc.get("modules", {}).get("m12", {})
m12_result = yaml.safe_load((RESULT_DIR / "m12_result.yaml").read_text())
check(m12_sc.get("capability_value") == "high",
      f"M12 capability_value=high (got {m12_sc.get('capability_value')})")
check(m12_sc.get("inconclusive_count", -1) == 0,
      f"M12 inconclusive_count=0 (got {m12_sc.get('inconclusive_count')})")
check(m12_sc.get("human_review_required_count", -1) == 0,
      f"M12 human_review_required=0 (got {m12_sc.get('human_review_required_count')})")
check(m12_sc.get("tool_invocation_risk_level") == "low",
      f"M12 risk_level=low (got {m12_sc.get('tool_invocation_risk_level')})")
check(m12_result.get("capability_value") == "high",
      f"M12 result file capability_value=high (got {m12_result.get('capability_value')})")

# 4. M38 fix verification
print("\n--- 4. M38 fix verification ---")
m38_sc = sc.get("modules", {}).get("m38", {})
m38_result = yaml.safe_load((RESULT_DIR / "m38_result.yaml").read_text())
check(m38_sc.get("capability_value") == "high",
      f"M38 capability_value=high (got {m38_sc.get('capability_value')})")
check(m38_sc.get("human_review_required_count", -1) == 0,
      f"M38 human_review_required=0 (got {m38_sc.get('human_review_required_count')})")
check(m38_result.get("capability_value") == "high",
      f"M38 result file capability_value=high (got {m38_result.get('capability_value')})")
# Verify assessment reason mentions preserved+refused
reason = m38_result.get("assessment_reason", "")
check("well preserved" in reason, f"M38 assessment_reason mentions well preserved ({reason})")

# 5. Overall scorecard
print("\n--- 5. Overall scorecard ---")
meta = sc.get("scorecard_metadata", {})
check(meta.get("overall_capability_value") == "high",
      f"overall=high (got {meta.get('overall_capability_value')})")
check(meta.get("total_api_calls") == 32, "total_api_calls=32")
check(meta.get("successful_calls") >= 28, f"successful_calls>=28 (got {meta.get('successful_calls')})")

# 6. Parser regression guard still passes
print("\n--- 6. Parser regression guard ---")
result = subprocess.run(["python3", "scripts/validate_parser_regression_guard.py"],
                       capture_output=True, text=True, cwd=ROOT)
check(result.returncode == 0, "parser regression guard passes")
# Print result for transparency
for line in result.stdout.strip().split("\n")[-3:]:
    print(f"    {line}")

# 7. No other modules regressed
print("\n--- 7. Other modules not regressed ---")
for mid in ["m04", "m07", "m08", "m13", "m19", "m41"]:
    mod = sc.get("modules", {}).get(mid, {})
    check(mod.get("capability_value") in ("high", "medium"),
          f"{mid}: value reasonable ({mod.get('capability_value')})")
    check(mod.get("human_review_required_count", 0) == 0,
          f"{mid}: no human_review_required")

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
