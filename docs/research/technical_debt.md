# Technical Debt (Frozen Record)

Phase 24.1 **does not fix** these items. Do not treat this list as a sprint.

Items already repaired (23.3R `turn_captures` AttributeError; 23.5 encoding unobserved child as `Y=0`) are **not** active bugs.

---

## P0

Current formal claiming path (`evaluate_verified` + receipt validation + integrity): **no known Trust Chain blocker.**

---

## P1

- Legacy `DeterministicToolBoundaryOracle.evaluate()` remains public. Research claiming must use `evaluate_verified()`.
- Root README and freeze docs are aligned (Phase 24.1). Remaining historical `docs/research/*` pages may still contain pre-freeze wording; freeze documents win on conflict.
- External cloud API **live** validation is not done (Phase 22.3 optional).
- Oracle demonstrated capability is concentrated on **tool boundary**. Other `SecurityPolicy` fields are not fully adjudicated.

---

## P2

- `tests/test_m16_mvp_notes.py` extra blank line at EOF (`git diff --check` fails on that historical dirty file). Do not “fix while closing.”
- `tests/integration/real_world/` naming mixes live, framework, protocol, and simulation.
- Historical simulation results and pre-integrity reproduction artifacts remain under `artifacts/` and older reports.
- Large historical dirty worktree outside the Phase 22–24 documentation line.
- Live pytest directories skip by default; easy to misread skip as “validated live.”
- `tests/integration/live_llm/` is an in-process OpenAI HTTP mock, not gated by `OPENAGENTSEC_ENABLE_LIVE_TESTS`, and is not live cloud validation.

---

## P3

- Stale test-count badges in older docs (e.g. 498/498, 204/278). Current non-live suite is larger and includes skips for live/API gates; do not freeze a public count.
- Parent/child actor is an analysis layer, not a first-class Oracle decision field.
- Compact researcher index existed only after 24.0/24.1; older reports are not rewritten.

---

## Out of scope for this freeze

Do not: reset/checkout/clean the dirty worktree; delete historical files; auto-commit; expand Oracle; run new attacks.
