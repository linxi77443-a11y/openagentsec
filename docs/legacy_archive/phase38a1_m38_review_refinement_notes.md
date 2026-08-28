# Phase 38A.1: M38 Review Refinement & False Positive Guard

## What was done
- Analyzed Phase 38A M38 MVP results for false positive patterns
- Identified two root causes of keyword-based false positives:
  1. Model quoting tool return content to explain why it's **rejecting** the instruction (TOOL002)
  2. Model quoting low-priority source in credibility table to dismiss it (PRI001)
- Added `M38_REJECTION_CONTEXT` markers and `refine_m38_signals()` post-hoc refinement pass
- Kept original Phase 38A signals unchanged, added refinement signals on top

## Why distinguish legitimate source update from boundary breach
- Model frequently uses tool return / external source content as factual reference material while maintaining user goal — this is correct behavior, not a boundary breach
- Model generates credibility-assessment tables that quote low-priority sources alongside dismissals — keyword markers match the quotes, not the model's intent
- Without refinement, every credibility analysis that mentions the source content looks like a breach

## New/refined fields in m38_result.yaml and capability_scorecard.yaml
- `parser_flagged_boundary_issue_count` — total entries with any boundary signal
- `confirmed_by_parser_boundary_issue_count` — entries with clear evidence of following
- `legitimate_source_update_count` — entries using source info as factual reference
- `likely_false_positive_count` — flagged entries classified as false positive
- `review_note` — per-entry note for human reviewers (stored in results)
- `assessment_reason` uses neutral language, avoids "breached"

## API re-call
No. Re-ran parser only on existing execution_results.json.

## Original execution_results.json
Preserved in full at `executions/phase38a_m38_mvp/execution_results.json`.

## M38 capability_value
Unchanged: high. Reason: parser still flags 2 entries; refinement downgrades 0 confirmed. Capability_value reflects the conservative "high" from Phase 38A.

## Next step
Full corpus regression (24 entries) recommended to validate refinement stability across more techniques.
