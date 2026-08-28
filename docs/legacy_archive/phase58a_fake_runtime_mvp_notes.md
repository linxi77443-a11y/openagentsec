# Phase 58A — Fake Tool Runtime MVP

## Summary

Phase 58A introduces a minimal fake tool runtime for simulating tool execution security boundary enforcement. No real system access, no real data, no real tool execution. All tools/accounts/resources use `fake_` / `<SIM_...>` placeholders.

## What Changed

- **New**: `capability_engine/fake_runtime/` — fake runtime engine package
- **New**: `capability_engine/fake_runtime/fake_tool_runtime.py` — runtime with 6 boundary checks (tool existence, tenant, role, SA scope, untrusted params, approval)
- **New**: `capability_modules/corpora/phase58a_fake_runtime/fake_runtime_mvp_corpus.yaml` — 8-entry MVP corpus
- **New**: `executions/phase58a-fake-runtime-mvp/runtime_results.yaml` — per-entry results
- **New**: `executions/phase58a-fake-runtime-mvp/capability_scorecard.yaml` — aggregate scorecard
- **New**: `capability_engine/configs/phase58a_fake_runtime_mvp.yaml` — run config

## Results

| Metric | Value |
|--------|-------|
| Total cases | 8 |
| Allowed (control) | 1 |
| Blocked | 7 |
| blocked_by_role | 3 |
| blocked_by_tenant | 1 |
| blocked_by_untrusted_argument | 1 |
| approval_required | 1 |
| invalid_tool | 1 |
| unsafe_runtime_allowed | 0 |
| human_review_required | 0 |
| likely_false_positive | 0 |
| inconclusive | 0 |
| Capability value | high |
| Risk level | low |
| Safety level | simulated_runtime_safety |
| Production claimed | false |

## Boundary Checks

The runtime enforces 6 security boundaries in priority order:

1. **Tool existence**: non-fake_ or unknown tool → `invalid_tool`
2. **Tenant boundary**: resource tenant ≠ current tenant → `blocked_by_tenant`
3. **Role boundary**: role not in tool's allowed_roles → `blocked_by_role`
4. **Service account scope**: SA not permitted or scope insufficient → `blocked_by_scope`
5. **Untrusted parameter**: SIM_ entity overlap between untrusted context and resource → `blocked_by_untrusted_argument`
6. **Approval gate**: high-impact + approval_required tool → `approval_required`

## Constraints

- No real system access
- No real data
- No real tool execution
- No API calls made
- No formal finding generated
- No vulnerability claimed
- No production safety claimed
- `production_safety_claimed: false` on all entries
- `safety_level: simulated_runtime_safety` — one level above proposal_safety

## Mapped to Phase 57A.3 Matrix Anchor

| Module | Coverage depth advance |
|--------|----------------------|
| M07 | Now has tool_trace_ready via Phase 57A; fake_runtime_ready begins here |
| M08 | tool_trace_ready extended with runtime role boundary enforcement |
| M12 | tool_trace_ready → tool calls verified at runtime |
| M13 | untrusted_argument validation now at runtime level |
| M15 | high_impact approval gate enforced at runtime |
| M38 | multi-source context boundary enforced with untrusted parameter detection |
| M41 | SA scope enforced at runtime (beyond proposal-level refusal) |

## Next Steps

- Expand corpus beyond 8 entries
- Add `blocked_by_scope` test case (requires role + scope both satisfied but scope fails first)
- Add cross-module runtime scenarios
- Add multiturn runtime scenarios
- Integrate with Phase 57A tool trace corpus for end-to-end proposal→runtime pipeline
