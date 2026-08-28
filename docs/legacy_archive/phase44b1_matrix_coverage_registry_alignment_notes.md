# Phase 44B.1 — Matrix Coverage Registry Alignment Notes

## What Phase 44B.1 Did

Updated `capability_modules/module_registry.yaml` to add a `coverage:` block
to all 42 module entries, aligning the registry with the Phase 44B.0 AI attack
matrix coverage mapping.

## New Registry Field

Each module entry now includes a `coverage:` block with:

- **matrix_area**: AI attack matrix / Agent attack chain area
- **coverage_status**: mvp_complete / partial / reference_only / not_started
- **implementation_status**: candidate_available / mvp_done / refined / replay_done / reference_done / not_started
- **evidence**: list of completed artifacts (commits, results, scorecards, notes)
- **gaps**: current gaps and limitations
- **next_action**: recommended next step

## Modules Marked Complete

| Module | Coverage Status | Implementation Status |
|--------|----------------|----------------------|
| M01 | mvp_complete | candidate_available |
| M02 | mvp_complete | candidate_available |
| M03 | mvp_complete | candidate_available |
| M06 | mvp_complete | mvp_done |
| M38 | mvp_complete | refined |
| M39 | mvp_complete | refined |
| M12 | mvp_complete | mvp_done |
| M13 | mvp_complete | mvp_done |
| M14 | mvp_complete | replay_done |
| M15 | mvp_complete | mvp_done |

## Modules Reference Only

| Module | Coverage Status | Next Action |
|--------|----------------|-------------|
| M16 | reference_only | defer until P0 data/permission gaps addressed |

## Current P0 Blank Modules

| Module | Area | Next Action |
|--------|------|-------------|
| M04 | data / sensitive data leakage | reference spike before MVP |
| M07 | data access / unauthorized access | reference spike (high priority) |
| M08 | privilege / role boundary | reference spike (high priority) |
| M19 | data / business data leakage | reference spike before MVP |
| M41 | privilege / service account permission | reference spike (high priority) |

## Why M16 MVP Is Deferred

M16 (Human Approval Gate Validation, P1) is marked `reference_only` with
next_action `defer until P0 data/permission gaps addressed`. This is based on
Phase 44B.0 coverage mapping which identified P0 data layer (M04/M07/M19)
and P0 permission layer (M08/M41) as larger coverage gaps.

## Recommended Next Phase

**Phase 45A.0**: M07 + M04 Data / Access Layer Reference Spike — P0 data layer gap.

## Non-Goals

- No new module development
- No API calls
- No new corpus
- No new run config
- No parser modification
- No capability_engine execution
