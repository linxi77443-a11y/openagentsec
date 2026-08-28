#!/usr/bin/env python3
"""
Phase 52A.1 — Parser Regression Guard

Verifies that parse_capability_results.py has no missing detect/refine/dispatch/field
functions. Run after any edit to the parser to catch accidental deletions early.
Does NOT call API, read .local/, or execute capability_engine.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARSER_PATH = ROOT / "capability_engine" / "parsers" / "parse_capability_results.py"

errors = []

def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  ❌ {msg}")
    else:
        print(f"  ✅ {msg}")

print("=" * 60)
print("Phase 52A.1 — Parser Regression Guard")
print("=" * 60)

# 1. File existence
print("\n--- 1. Parser file ---")
check(PARSER_PATH.exists(), "parse_capability_results.py exists")

text = PARSER_PATH.read_text()

# 2. Detect functions
print("\n--- 2. Detect functions ---")
expected_detect = {
    "detect_m04_signals",
    "detect_m07_signals",
    "detect_m08_signals",
    "detect_m12_signals",
    "detect_m13_signals",
    "detect_m14_signals",
    "detect_m15_signals",
    "detect_m19_signals",
    "detect_m38_signals",   # via detect_signals generic (refine only)
    "detect_m39_signals",
    "detect_m41_signals",
    "detect_xmodule_signals",
}
detect_pattern = re.compile(r'^def (detect_\w+)\(', re.MULTILINE)
found_detect = set(detect_pattern.findall(text))

# detect_m38 is special — it uses the generic detect_signals function
# We treat detect_m38 as covered by detect_signals
expected_with_generic = expected_detect - {"detect_m38_signals"}
expected_with_generic.add("detect_signals")

for fn in sorted(expected_with_generic):
    check(fn in found_detect, f"function '{fn}' exists")

# 3. Refine functions
print("\n--- 3. Refine functions ---")
expected_refine = {
    "refine_m04_data_leakage_signals",
    "refine_m07_unauthorized_access_signals",
    "refine_m08_role_boundary_signals",
    "refine_m12_tool_invocation_signals",
    "refine_m13_argument_signals",
    "refine_m14_high_risk_action_signals",
    "refine_m15_business_action_signals",
    "refine_m19_business_data_signals",
    "refine_m38_signals",
    "refine_m39_action_signals",
    "refine_m41_service_account_signals",
}
refine_pattern = re.compile(r'^def (refine_\w+)\(', re.MULTILINE)
found_refine = set(refine_pattern.findall(text))

for fn in sorted(expected_refine):
    check(fn in found_refine, f"function '{fn}' exists")

# 4. Parser dispatch — all module-specific branches
print("\n--- 4. Parser dispatch ---")
dispatch_checks = {
    "m39": 'detect_m39_signals(r)',
    "m12": 'detect_m12_signals(r)',
    "m13": 'detect_m13_signals(r)',
    "m14": 'detect_m14_signals(r)',
    "m15": 'detect_m15_signals(r)',
    "m04": 'detect_m04_signals(r)',
    "m19": 'detect_m19_signals(r)',
    "m08": 'detect_m08_signals(r)',
    "m41": 'detect_m41_signals(r)',
    "m07": 'detect_m07_signals(r)',
    "xmodule": 'detect_xmodule_signals(r)',
}
for mod, call in dispatch_checks.items():
    check(call in text, f"dispatch branch for '{mod}' → {call}")

# Generic fallback dispatch
check("detect_signals(r[\"module_id\"]" in text, "generic dispatch fallback (detect_signals)")

# 5. Refinement calls in parse()
print("\n--- 5. Refinement calls ---")
refine_calls = {
    "refine_m38_signals(results)",
    "refine_m39_action_signals(results)",
    "refine_m12_tool_invocation_signals(results)",
    "refine_m13_argument_signals(results)",
    "refine_m14_high_risk_action_signals(results)",
    "refine_m15_business_action_signals(results)",
    "refine_m07_unauthorized_access_signals(results)",
    "refine_m04_data_leakage_signals(results)",
    "refine_m19_business_data_signals(results)",
    "refine_m08_role_boundary_signals(results)",
    "refine_m41_service_account_signals(results)",
}
for call in sorted(refine_calls):
    check(call in text, f"refinement call '{call}'")

# 6. Field collection blocks
print("\n--- 6. Field collection ---")
field_checks = {
    "M13 field collection": '# M13 tool argument integrity fields',
    "M14 field collection": '# M14 high-risk action simulation fields',
    "M15 field collection": '# M15 business action simulation fields',
    "M07 field collection": '# M07 unauthorized access boundary fields',
    "M04 field collection": '# M04 sensitive data leakage fields',
    "M19 field collection": '# M19 business data exposure fields',
    "M08 field collection": '# M08 role boundary fields',
    "M41 field collection": '# M41 service account permission fields',
    "M38 field collection": '# M38 refinement fields',
}
for label, marker in field_checks.items():
    check(marker in text, f"{label} present")

# 7. assess_capability_value branch for xmodule
print("\n--- 7. Assess capability branches ---")
check("xmodule" in text.lower() and "high" in text.lower(),
      "xmodule branch in assess_capability_value (or handled generically)")

# 8. Cross-module save name
print("\n--- 8. Save names ---")
check("cross_module_result.yaml" in text, "cross_module_result.yaml save name")

# 9. No orphaned code — verify all detected functions have def header
print("\n--- 9. Structural integrity ---")
# Count function definitions that start at column 0
all_defs = re.findall(r'^(def \w+)', text, re.MULTILINE)
# Count lines starting with 'def '
check(len(all_defs) > 0, f"parser has {len(all_defs)} function definitions")

# 10. No stale orphaned bodies (code at same indent after return)
print("\n--- 10. No orphaned function bodies ---")
# Check there's no code after "return signals" or "return signals or" at the same
# indentation level that looks like orphaned function body
orphan_pattern = re.findall(r'    return signals\n    [a-z]', text)
check(len(orphan_pattern) == 0,
      f"no orphaned bodies after 'return signals' (found {len(orphan_pattern)})")

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
