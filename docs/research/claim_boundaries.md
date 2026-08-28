# Claim Boundaries (Frozen)

If language here conflicts with README badges, older technical reports, or `docs/research/*` historical pages, **this file plus** [openagentsec_current_research_state.md](openagentsec_current_research_state.md) **win**.

---

## Allowed claims

Use these when describing current OpenAgentSec v1.x:

- evidence-supported
- receipt-confirmed
- independently verified Evidence (not producer `verified=True`)
- integrity-verified reproduction
- decision-level consistency (distinct from integrity)
- controlled experiment
- current runtime / configuration
- no attack effect observed
- baseline behavior
- spontaneous workspace exploration
- partial observability
- UNKNOWN / INCONCLUSIVE / fail-closed
- pilot sample
- tool-boundary adjudication
- live Agent runtime (DeepSeek Harness, named profile)
- real framework runtime with controlled agent logic (LangGraph)
- controlled real protocol runtime (MCP stdio)
- External API: contract-level only

---

## Forbidden / unsupported claims

Do not use for current v1.x:

- Agent is safe
- attack-proof
- zero false positives
- zero false negatives
- production-grade
- production security scanner
- cryptographically trusted / cryptographic attestation
- all Agent attacks covered
- all Prompt Injection resisted
- fully deterministic Agent behavior
- DeepSeek Harness is secure
- tool/call equals execution
- majority voting as a finding rule
- copied artifacts as 5-run reproduction
- mock / simulation / planner tests as live Agent validation
- External / commercial cloud API as live validated
- Phase 23 rejected hypotheses as vulnerabilities
- “these attacks were all blocked”
- enterprise CI/CD platform as a current research claim
