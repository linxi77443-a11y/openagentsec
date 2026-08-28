# Phase 52A.1 — Parser Regression Guard Notes

## Why

Phase 52A 修复了 `detect_m13_signals` 被 Phase 51A edit 挤掉的问题；此前也出现过 M15 parser 函数被误伤。`parse_capability_results.py` 已成为关键脆弱点，需要自动化完整性验证。

## Checks

- 12 detect functions (M04, M07, M08, M12, M13, M14, M15, M19, M38, M39, M41, xmodule + generic detect_signals)
- 11 refine functions (M04, M07, M08, M12, M13, M14, M15, M19, M38, M39, M41)
- 11 dispatch branches + generic fallback
- 11 refinement calls in parse()
- 9 field collection blocks
- assess_capability_value xmodule branch
- cross_module_result.yaml save name
- Structural integrity (no orphaned bodies)

## Result

- No missing functions found
- No fixes needed
- 39/39 checks passed

## Coverage

M04, M07, M08, M12, M13, M14, M15, M19, M38, M39, M41, xmodule
