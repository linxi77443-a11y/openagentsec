# OpenAgentSec Phase Status (Frozen)

**Source of truth for narrative:** [openagentsec_current_research_state.md](openagentsec_current_research_state.md)

| Phase | Status | Main result |
| --- | --- | --- |
| 22.0A Evidence Trust Boundary | COMPLETE | Producer `verified=True` is not trusted Evidence |
| 22.0B Execution Truth Boundary | COMPLETE | `tool/call` ≠ execution; receipt gate |
| 22.0C Reproduction Integrity | COMPLETE | Copied 5-run fakes rejected; no majority vote |
| 22.0D Cross-runtime + live safety / API contract | COMPLETE | Live Agent, framework, protocol; API contract-only |
| 22.1 LangGraph cross + strict Trust Chain helpers | COMPLETE | Trust Chain transfers to real LangGraph runtime |
| 22.2 MCP stdio protocol runtime | COMPLETE | Real stdio MCP; intent ≠ execution |
| 22.3 External cloud API live validation | OPTIONAL / NOT LIVE VALIDATED | Contract-level partial observability only |
| 23.1 Real-world Agent attack evaluation | SUPERSEDED BY CAUSAL FOLLOW-UP | Attack-condition observations only; not matched causal findings |
| 23.2 Delayed Action Drift | COMPLETE | NO ATTACK EFFECT OBSERVED |
| 23.3 Authority Spoofing | COMPLETE | BASELINE RUNTIME BEHAVIOR |
| 23.3R Live adapter `turn_captures` repair | COMPLETE | Adapter lifecycle fix; Trust Chain untouched |
| 23.4 Indirect Prompt Injection causal | COMPLETE | NO INDIRECT ATTACK EFFECT OBSERVED |
| 23.5 Delegation (foreground-heavy) | SUPERSEDED / PARTIAL OBSERVABILITY | Unobserved child traces must not be encoded as 0 |
| 23.5R Observable delegation re-validation | COMPLETE | BASELINE DELEGATION BEHAVIOR |
| 23.6 Mention vs Execute | COMPLETE | MENTION/EXECUTE BOUNDARY PRESERVED |
| 24.0 Research consolidation | COMPLETE | Claim baseline written |
| 24.1 Final documentation closure | FINAL CLOSURE | README and freeze docs aligned |

Phase 22 and Phase 23 are closed. Further work requires a **new** research phase, not Phase 23.7+.
