# Phase 57A.3 — Matrix Anchor & Coverage Semantics Addendum

## Why a Matrix Anchor?

Previously, each module referenced "matrix_area" as a free-text string (e.g., `"execution / prompt injection"`), with no canonical coordinate system. This led to:

- **No attack matrix denominator**: "覆盖攻击矩阵" was claimed without specifying which matrix, which techniques, or what fraction was tested.
- **Coverage theater risk**: `coverage_status: mvp_complete` conflated "MVP passed" with "module fully covered".
- **No safety level distinction**: All results implicitly claimed the same authority, even though the platform only verifies model text responses, not actual tool execution.

`attack_matrix_anchor.yaml` fixes this by establishing MITRE ATLAS as the primary coordinate system, with OWASP LLM Top 10 2025 and OWASP Agentic AI Threats as supplements, and defining explicit coverage depth and safety level enums.

## Why Not "Full Attack Matrix Coverage"?

The platform currently tests **proposal safety** — the model's text response proposing (or refusing) tool calls. This is not the same as:

- **Execution safety**: Whether the tool call actually executes safely against real systems.
- **Runtime safety**: Whether the sandbox, permission layer, or audit trail enforces the model's stated refusal.
- **Production safety**: Whether the full stack (model + middleware + runtime + controls) prevents real-world exploitation.

Claiming "full coverage" would be misleading without fake runtime, controlled replay, or production execution validation. All current modules are capped at **proposal_safety**.

## Proposal Safety vs Execution Safety

| Aspect | Proposal Safety (current) | Execution Safety (future) |
|--------|--------------------------|---------------------------|
| What is tested | Model text response | Tool call + runtime result |
| Tool calls | Simulated (text only) | Actual execution in mock env |
| Risk level | Theoretical | Operational |
| False negative risk | Model says no → safe | Model says no but runtime executes anyway |
| Current max level | proposal_safety | Not yet available |

The project's core finding — `confirmed vulnerability = 0, confirmed capability signal = 0` — is a **proposal safety** finding only.

## How coverage_depth Prevents Coverage Theater

Instead of a single `coverage_status` field (e.g., `complete`), each module now has a **ordered list** of depth levels it has reached:

```
coverage_depth: [mapped_only, reference_done, simulated_mvp, adversarial_ready, tool_trace_ready]
```

- **Additive**: Once a depth is reached, it is never removed. New depths are appended.
- **Non-linear**: Modules skip depths they haven't been tested for.
- **Gap visibility**: `next_depth_target` makes the next priority explicit.
- **Terminal depths**: `out_of_scope` is the only terminal depth — everything else is intermediate.

This makes it impossible to claim a module is "done" — it always has a next depth target unless explicitly out of scope.

## PRD Review Suggestions: Adopted vs Deferred

| Suggestion | Status |
|-----------|--------|
| Attack matrix must have explicit denominator | Adopted — `attack_matrix_anchor.yaml` |
| Platform tests proposal safety, not execution safety | Adopted — `safety_level` enum |
| coverage_status needs depth, not just complete/not_started | Adopted — `coverage_depth` list |
| MVP pass ≠ full coverage | Adopted — `next_depth_target` |
| Seeded known-bad meta-evaluation | Deferred — future phase |
| Repeat sampling / statistical significance | Deferred — future phase |
| Red/Blue/Purple methodology in results format | Deferred — methodology notes only |

## Current Principal Gaps

| Area | Status | Impact |
|------|--------|--------|
| Fake runtime execution | **not_started** | Cannot verify tool execution safety |
| Controlled replay | **not_started** | Cannot verify determinism |
| Seeded known-bad meta-evaluation | **not_started** | Cannot calibrate FP/FN rates |
| Statistical regression | **not_started** | Single-run results may be coincidental |
| Production safety | **out_of_scope** | Project does not verify production execution |

## Summary

Phase 57A.3 introduces no new tests, no API calls, no runner changes, no parser changes. It is a **semantic addendum**: establishing the matrix anchor, coverage depth ladder, and safety level taxonomy so that future phases and reporting have an honest, self-consistent frame of reference.
