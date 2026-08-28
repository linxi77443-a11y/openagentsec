# Phase 39A: M39 Tool Invocation / Action Boundary MVP

## What was done
- Created M39 full corpus (16 entries, 6 categories) and MVP corpus (8 entries)
- Extended parser with `detect_m39_signals()` and `refine_m39_action_signals()` (FP guard)
- Executed 8-API-call MVP run via `capability_engine` against FastGPT target
- Generated execution_results.json, m39_result.yaml, capability_scorecard.yaml

## M39 focus
Tool Invocation / Action Boundary — whether model suggests or executes actions embedded in low-priority sources (search results, citations, external sources), even when user only authorized read/analysis.

## Distinction from related modules
| Module | Focus |
|--------|-------|
| M38 (Phase 38A) | Content-level: which source info model adopts in answers |
| M39 (this phase) | Action-level: whether model acts on source-embedded action instructions |
| M12 | Tool invocation parameter/rate safety |
| M13 | Tool argument injection defense |

## Corpus
- **Full**: 16 entries (search_result_action=3, citation_action=3, source_redirect_action=3, credibility_dismissed_action=3, read_only_to_write_boundary=2, control_no_action=2)
- **MVP**: 8 entries (search_result_action=2, citation_action=1, source_redirect_action=1, credibility_dismissed_action=1, read_only_to_write_boundary=2, control_no_action=1)

## Execution
- Engine: `capability_engine/runners/run_capability_eval.py`
- API calls: Yes (8 calls to FastGPT target)
- Results: 8/8 OK, 0 server errors

## Key results
| Metric | Value |
|--------|-------|
| action_boundary_preserved_count | 6 |
| unauthorized_action_suggested_count | 1 |
| read_only_to_write_escalation_count | 1 |
| likely_false_positive_count | 3 |
| capability_value | medium |
| action_boundary_risk_level | medium |

## Field semantics
- `capability_value`: M39 action boundary robustness (high=good boundary, low=weak boundary)
- `action_boundary_risk_level`: risk assessment (high=more unauthorized action suggestions, low=stable)

## False positive guard (Phase 38A.1-style)
Three FP types handled:
1. **Quoting vs executing**: model references source action instruction as analysis content
2. **Rejection context**: model explicitly refuses action but keyword matches embedded_action
3. **Legitimate analysis vs unauthorized action**: model suggests "人工确认"not direct execution

## Not done
- Dashboard / README / PRD / release notes / approval packet
- Formal finding
- Full corpus regression (24 entries)
- M12/M13/M14/M15/M16/M40/M41/M42
- Generalized runtime state corruption

## Next step
Full corpus regression (16 entries) recommended to validate action boundary stability across more categories and techniques.
