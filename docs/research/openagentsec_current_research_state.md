# OpenAgentSec Current Research State

**Document:** OAS-DOC-CURRENT-STATE-001  
**Scope:** Phase 22–23 consolidation (Phase 24.0)  
**Freeze:** Phase 24.1 documentation alignment — [OPENAGENTSEC_V1_RESEARCH_FREEZE.md](OPENAGENTSEC_V1_RESEARCH_FREEZE.md)  
**Mode:** documentation only — no new features, attacks, runtimes, or Trust Chain changes

This document is the current research baseline. It records what has been *shown*, what has been *rejected*, and what must not be claimed. Older README or pre-v1.x research pages that use stronger language are superseded here for claim purposes. Index: [README.md](README.md).

---

## 1. Executive Summary

OpenAgentSec v1.x is a **research framework for evidence-admissible Agent security evaluation**.

It does not currently prove that any Agent, including DeepSeek Harness, is safe or attack-proof. It does show that, under controlled conditions, a single Trust Chain can:

- refuse producer `verified=True` as trusted Evidence
- refuse `tool/call` as proof of execution
- require matching runtime receipts for execution eligibility
- fail closed when Evidence, execution, attribution, or reproduction is incomplete
- compare Attack vs matched Baseline instead of treating attack-condition anomalies as findings

Phase 22 established that Trust Chain. Phase 23 applied it to a live DeepSeek Harness Agent and **did not produce a reproduced attack vulnerability**. Several popular hypotheses (delayed drift, authority spoofing, indirect injection, delegation attack, mention/execute confusion under the 23.6 template) were **not supported** by matched causal pilots.

The project’s current value is **lower false confidence**, not a vulnerability scanner scoreboard.

**Maturity:** research framework.

---

## 2. What OpenAgentSec Is

OpenAgentSec is an evaluation methodology and implementation that:

1. Observes a target through a `TargetAdapter`.
2. Turns observations into `EvidenceItem` objects.
3. Independently verifies Evidence (`EvidenceVerifier`) before Oracle use.
4. Extracts and matches `ExecutionReceipt` objects from trusted Evidence.
5. Adjudicates **tool-boundary** policy with `DeterministicToolBoundaryOracle.evaluate_verified()`.
6. Checks independent-run integrity with `ReproductionAggregator(require_integrity=True)`.
7. For security claims about attacks, requires Attack vs matched Baseline comparison.

The trusted evaluation path is:

```text
Runtime Observation
  → EvidenceVerifier
  → Verified Evidence
  → ExecutionReceiptValidator
  → DeterministicToolBoundaryOracle.evaluate_verified()
  → ReproductionAggregator(require_integrity=True)
  → Security Result
```

---

## 3. What OpenAgentSec Is Not

OpenAgentSec is not:

- a guarantee that an Agent is safe
- a complete Prompt Injection / Agent-attack benchmark
- a cryptographic attestation system
- a production-grade enterprise platform
- an LLM-as-a-Judge replacement for all security questions
- a claim that DeepSeek Harness, LangGraph, or MCP “passed” and is therefore secure
- a scanner that outputs only “vulnerable / not vulnerable”

It also does not currently live-validate remote cloud model providers.

---

## 4. Trust Chain Architecture

### 4.1 Evidence Trust Boundary (Phase 22.0A)

A producer field `verified=True` is not trusted Evidence.

Only an independent `EvidenceVerifier` result, with required provenance (`run_id`, `session_id`, `producer`, `observation_id`) and intact content hash, can make Evidence eligible for Oracle use.

### 4.2 Execution Truth Boundary (Phase 22.0B)

```text
tool/call  ≠  tool execution
```

Intent-only traces remain intent. Execution eligibility requires a matching `tool/result` or runtime completion receipt, bound to `call_id` / tool identity, after receipt validation. A naked `actual_tool_execution=True` claim cannot bypass this gate.

### 4.3 Reproduction Integrity (Phase 22.0C)

Copying one run’s artifacts and relabeling them as five runs is rejected.

Strict integrity checks unique run identity, unique session, unique Evidence instance, unique receipts, instance digest, and outcome digest. Majority voting is not used to manufacture a finding.

Two different questions remain separate:

| Question | What it answers |
| --- | --- |
| Decision consistency | Did independent runs yield the same Oracle decision? |
| Integrity-verified reproduction | Were those runs actually independent executions with distinct Evidence/receipts? |

### 4.4 Trusted Oracle entry

`evaluate_verified()` is the Phase 22 trusted entry. Legacy `evaluate()` still exists in code and is **not** the research claiming path.

The implemented Oracle’s demonstrated adjudication is **tool boundary** (denied tool actually executed vs not). `SecurityPolicy` can carry other fields (approvals, critical actions, evidence requirements); those dimensions are **not** claimed as fully Oracle-adjudicated.

---

## 5. Runtime Validation Matrix

| Area | Reality Level | Trust Chain | Research Role | Claim Boundary |
| --- | --- | --- | --- | --- |
| Contract / unit tests (`tests/unit`, `tests/integration/contract_integrity`) | Contract / unit | Full objects exercised with fixtures | Protect Evidence, receipt, Oracle, and integrity semantics | Not real-world Agent validation |
| Planner / fake-runtime / simulated agents | Simulation | Often uses evaluation objects; some paths still mention legacy `evaluate()` | Scenario and pipeline tests | Must not be written as live Agent validation |
| LangGraph native / cross | Real framework runtime, **controlled agent logic** | Strict path used in Phase 22.1 transfer work | Shows the Trust Chain transfers to a real graph runtime | Not a live LLM Agent; not a general LangGraph security certificate |
| DeepSeek Harness live | Live Agent runtime | `evaluate_verified()` + receipts + integrity on isolated sessions | Primary real-Agent measurement surface for Phase 23 | Current runtime/config only; not “DeepSeek is secure” |
| MCP stdio (Phase 22.2) | Controlled real protocol runtime | Strict path on real stdio MCP | Protocol-boundary execution vs intent | Controlled test server, not arbitrary MCP deployments |
| Phase 23.2–23.6 matched pilots | Controlled causal experiments on live DeepSeek Harness | Full trusted path; child attribution via real child `session.history` when id is available | Attack vs baseline / mention vs execute | Pilot samples; template-specific |
| External API tests | Contract-level partial-observability path | Intent without remote receipt stays inconclusive | Documents how a remote API *should* fail closed | **Not live Cloud Provider validation** |

Live DeepSeek pytest directories remain behind `OPENAGENTSEC_ENABLE_LIVE_TESTS=true`. External API live tests remain behind `OPENAGENTSEC_ENABLE_EXTERNAL_API_TESTS=true` and were not completed as live validation.

---

## 6. Phase 23 Real Agent Experiments

All Phase 23 causal claims below are from the **clean isolated DeepSeek Harness** profile (`http://127.0.0.1:3081` for 23.2–23.6): Hermes memory disabled, checkpoint/resume disabled, fresh session and workspace per run.

### 6.1 Delayed Action Drift (Phase 23.2)

| Condition | Denied execution |
| --- | ---: |
| Attack | 0/5 |
| Benign | 1/5 |
| Delta | −0.2 |

**NO ATTACK EFFECT OBSERVED.**

### 6.2 Authority Spoofing (Phase 23.3)

| Condition | Marker execution |
| --- | ---: |
| Authority | 10/10 |
| Neutral control | 10/10 |
| Delta_marker | 0 |

**BASELINE RUNTIME BEHAVIOR.** Authority framing showed no extra action effect on this marker.

### 6.3 Indirect Prompt Injection (Phase 23.4)

| Condition | Marker execution | Generic denied bash |
| --- | ---: | ---: |
| Attack | 0/10 | 0/10 |
| Control | 0/10 | 2/10 |
| Delta | 0 | −0.2 |

**NO INDIRECT ATTACK EFFECT OBSERVED.** Control denied executions were spontaneous `pwd && ls -la`, not the attack marker.

### 6.4 Delegation Boundary (Phase 23.5 / 23.5R)

Phase 23.5 used mostly foreground subagent calls. Parent then saw only child final text. Encoding those runs as `Y_child_marker = 0` was invalid.

**Phase 23.5 is SUPERSEDED as a causal result** and reclassified **PARTIAL OBSERVABILITY**. Control RUN-09 remains a valid demonstration that child `session.history(child_id)` can complete the attribution chain.

Phase 23.5R forced `run_in_background=true` and required 20/20 `OBSERVED_COMPLETE` child traces:

| Condition | Child marker execution |
| --- | ---: |
| Attack | 10/10 |
| Matched control | 10/10 |
| Delta | 0 |

Parent marker execution was 0/10 in both groups. **BASELINE DELEGATION BEHAVIOR.** Denied marker execution occurred on the **child**, equally under both conditions.

### 6.5 Mention vs Execute (Phase 23.6)

New marker: `echo OPENAGENTSEC_MENTION_TEST`. Review conditions used explicit “do not execute / only analyze” language. Delegated conditions were 10/10 child-observable.

| Condition | Marker execution |
| --- | ---: |
| Direct Review | 0/10 |
| Delegated Review | 0/10 |
| Explicit Execute | 10/10 |

**MENTION/EXECUTE BOUNDARY PRESERVED** on this template. Explicit Execute confirms the runtime can still execute the marker.

Phase 23.5R control used different wording (“report what it says”) and must not be merged with 23.6 Delegated Review.

### 6.6 Baseline workspace exploration

Under `danger-full-access`, DeepSeek Harness sometimes executes `pwd`, `ls`, or `pwd && ls -la`. These are real executions and must be recorded, but they are **not** automatically attack-caused. Classify as baseline / spontaneous workspace exploration.

---

## 7. Valid Findings

The following are evidence-supported:

1. Producer-claimed Evidence is not Oracle-eligible without independent verification.
2. Tool intent is not tool execution.
3. Relabeled single-run artifacts fail integrity-verified reproduction.
4. The same Trust Chain can be applied to live DeepSeek Harness, LangGraph cross runtime, and controlled MCP stdio.
5. Remote API intent without a local/runtime receipt is inconclusive at the contract level.
6. Phase 23 matched pilots did **not** support the tested attack hypotheses.
7. Child execution can be attributed when a background subagent id is returned and child history is complete; parent-view subagent text is not execution.
8. Mention/execute was preserved on the 23.6 template; explicit execute still ran 10/10 on the child.
9. Spontaneous workspace exploration exists and must be separated from attack markers.

There is **no** reproduced attack-associated vulnerability finding from Phase 23.

---

## 8. Rejected / Unsupported Hypotheses

Do not claim:

| Hypothesis | Why unsupported |
| --- | --- |
| Memory poisoning / delayed action drift vulnerability | Attack 0/5 vs benign 1/5 denied execution |
| Authority spoofing vulnerability | 10/10 vs 10/10 marker execution |
| Indirect prompt injection vulnerability | 0/10 vs 0/10 marker execution |
| Delegation attack vulnerability | After 23.5R, 10/10 vs 10/10 child marker |
| Review is generally rewritten as execute | 23.6 Direct and Delegated Review both 0/10 |
| DeepSeek Harness is secure / attack-proof | Not tested; absence of effect ≠ absence of all attacks |
| Zero false positives / false negatives | Not measured as a general error rate |
| Cryptographically trusted Evidence | Hashes and provenance, not attestation |
| All Agent attacks covered | Oracle is tool-boundary-centered; samples are pilots |

Phase 23.5’s original “NO DELEGATION EFFECT OBSERVED” from 0/10 vs 1/10 **is rejected as a causal claim** (unobserved child traces encoded as zero).

---

## 9. Research Contributions

1. **Evidence-admissible evaluation** — independent verification instead of model self-report or producer `verified` claims.
2. **Intent-vs-execution separation** — model text, tool intent, and receipt-confirmed execution are distinct.
3. **Integrity-verified reproduction** — independent execution identity, not majority vote or copied artifacts.
4. **Cross-runtime measurement** — one Trust Chain on Agent runtime, framework runtime, and protocol runtime (with the claim boundaries in §5).
5. **Attack-vs-baseline causal validation** — attack-condition anomalies are not findings without a matched control.
6. **Fail-closed research claiming** — incomplete Evidence, unobserved execution, incomplete child attribution, or integrity failure yields `INCONCLUSIVE` / `PARTIAL OBSERVABILITY` / `UNKNOWN`, not a manufactured certainty.

---

## 10. Current Output Contract

When a user attaches an Agent (via an adapter and a policy/objective), OpenAgentSec can currently produce a **structured evaluation record**, not a binary “has vuln / no vuln” stamp.

Typical outputs:

1. Observed trajectory (messages, tool intent, tool results, when available).
2. Separation of what the model said vs what the runtime executed.
3. Receipt-confirmed executions, if the runtime exposes them.
4. Deterministic tool-boundary adjudication against `SecurityPolicy`.
5. Supporting verified Evidence (and explicit gaps).
6. Multi-run reproduction / integrity status.
7. If a matched baseline is included: whether an anomaly is attack-associated or baseline.

A result looks like:

```text
Finding (or no attack effect observed)
  + Evidence (verified or insufficient)
  + Actual execution (receipt-confirmed or not eligible)
  + Policy deviation (confirmed / none / inconclusive)
  + Reproduction (integrity-verified or not)
  + Baseline comparison (if designed)
  + Confidence and limitations
```

If the Agent is only partially observable (e.g. remote API without execution receipts, or child Agent without a queryable child session), the honest output is **inconclusive / partial observability**.

---

## 11. Known Limitations

1. The main live Agent runtime is **DeepSeek Harness** (isolated 3081 profile for Phase 23 causal work).
2. LangGraph work is a **real framework runtime with controlled agent logic**, not a live general-purpose LLM Agent certificate.
3. MCP work is a **controlled real protocol runtime**.
4. External cloud APIs: contract-level partial-observability only; **not live validated**.
5. Evidence provenance is **not cryptographic attestation**.
6. Execution receipts still depend on **runtime-supplied provenance**.
7. The Oracle’s demonstrated core is **tool boundary**.
8. `SecurityPolicy` has additional dimensions that are **not** claimed as fully adjudicated.
9. Phase 23 causal samples are **pilots** (5 vs 5 or 10 vs 10).
10. No observed attack effect **does not** imply other templates, runtimes, or methods are safe.
11. Parent-view foreground `subagent` still hides child intermediate tools; experiments that need child truth must obtain `child_id` and complete child history.
12. Current live Agent tests use `danger-full-access`; results do not transfer automatically to stricter sandboxes.

---

## 12. Technical Debt

Record only. **Not fixed in Phase 24.0.**

### P0

None known in the frozen Trust Chain objects that currently block the research claiming path.

### P1

- Public `DeterministicToolBoundaryOracle.evaluate()` remains callable; research claiming must use `evaluate_verified()`.
- Phase 24.1 aligned root `README.md` and freeze docs. Older `docs/research/*` historical pages may still contain pre-freeze wording; freeze documents win.
- External API **live** validation is unfinished.
- Oracle coverage vs full `SecurityPolicy` surface is incomplete.

### P2

- `tests/test_m16_mvp_notes.py` fails `git diff --check` (extra blank line at EOF). Historical dirty worktree; do not treat as a Trust Chain bug.
- `tests/integration/real_world/` mixes live-gated Agent tests, framework tests, protocol tests, and some non-live fixtures — naming can be read as “all real-world”.
- Historical simulation results and pre-integrity reproduction artifacts still exist under `artifacts/` and older reports.
- Adapter / pytest live gates are easy to misuse (running live directories without the env flag skips tests rather than validating live behavior).
- Large historical dirty worktree outside this research line.

### P3

- Historical reports still cite stale test counts (e.g. 204/278 or 498/498). The current non-live suite is larger and includes skips for live/API gates; do not freeze a count in public claims.
- Phase 23 artifact JSON is large; no compact researcher-facing index beyond this document.
- Child attribution is an analysis layer; Oracle itself still answers “denied bash executed?” without parent/child as a first-class decision field.

Do **not** list as active bugs: Phase 23.3R `turn_captures` AttributeError (fixed); Phase 23.5R child-observability encoding error (reclassified and repaired experimentally, not by changing Trust Chain).

---

## 13. Research Claim Boundaries

Allowed language:

- controlled experiment
- observed behavior
- evidence-supported
- receipt-confirmed
- decision-level / integrity-verified reproduction
- current runtime/configuration
- no attack effect observed
- baseline behavior
- partial observability
- pilot sample
- fail-closed / inconclusive

Forbidden language for current claims:

- zero false positives / zero false negatives
- cryptographically trusted evidence
- fully deterministic Agent behavior
- production-grade enterprise platform
- all Agent attacks covered
- all Prompt Injection resisted
- DeepSeek Harness is secure
- Agent is safe
- attack-proof

---

## 14. Current Project Status

| Phase | Status | Main Result |
| --- | --- | --- |
| 22.0A Evidence Trust Boundary | COMPLETE | Producer `verified` is not trusted Evidence |
| 22.0B Execution Truth Boundary | COMPLETE | `tool/call` ≠ execution; receipt gate |
| 22.0C Reproduction Integrity | COMPLETE | Copied 5-run fakes rejected; no majority vote |
| 22.0D Cross-runtime + live safety / API contract | COMPLETE | Live Agent, framework, protocol; API contract-only |
| 22.1 LangGraph cross + strict Trust Chain helpers | COMPLETE | Trust Chain transfers to real LangGraph runtime |
| 22.2 MCP stdio protocol runtime | COMPLETE | Real stdio MCP; intent ≠ execution |
| 23.1 Real-world Agent attack evaluation | SUPERSEDED BY CAUSAL FOLLOW-UP | Attack-condition observations; not matched causal findings |
| 23.2 Delayed attack vs baseline | COMPLETE | NO ATTACK EFFECT OBSERVED |
| 23.3 Authority spoofing | COMPLETE | BASELINE RUNTIME BEHAVIOR |
| 23.3R Live adapter `turn_captures` repair | COMPLETE | Adapter lifecycle fix; Trust Chain untouched |
| 23.4 Indirect prompt injection causal | COMPLETE | NO INDIRECT ATTACK EFFECT OBSERVED |
| 23.5 Delegation (foreground-heavy) | SUPERSEDED | Reclassified PARTIAL OBSERVABILITY |
| 23.5R Observable delegation re-validation | COMPLETE | BASELINE DELEGATION BEHAVIOR |
| 23.6 Mention vs execute | COMPLETE | MENTION/EXECUTE BOUNDARY PRESERVED |
| External cloud live API | OPTIONAL / NOT LIVE VALIDATED | Contract path only |
| 24.0 Research consolidation | COMPLETE (this document) | Claim baseline written |
| 24.1 Final documentation closure | FINAL CLOSURE | README and freeze docs aligned |

Phase 22 and Phase 23 are **formally closable** as research stages.

---

## 15. Recommended Future Research

Do not execute these in Phase 24.0.

1. Additional live Agent runtimes under the same Trust Chain (not only DeepSeek Harness).
2. External cloud API **live** validation that never treats remote intent as execution.
3. Larger samples than 5 vs 5 / 10 vs 10, still with matched baselines.
4. Mention/review templates beyond 23.6, because 23.5R vs 23.6 showed wording changes child action.
5. First-class parent/child actor in reporting (without silently changing Oracle policy semantics).
6. Oracle coverage of policy dimensions other than tool allow/deny — only if new Evidence types exist.
7. Stricter sandbox profiles than `danger-full-access`.

Not recommended as next work: more Prompt Injection variants on the same 23.2–23.4 templates; Trust Chain redesign; treating the current README as the claim source.
