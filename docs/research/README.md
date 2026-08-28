# OpenAgentSec Research Index

**Read this first.** It is the entry point for the frozen v1.x research baseline.

Claim source of truth: [`openagentsec_current_research_state.md`](openagentsec_current_research_state.md)

---

## Current baseline (start here)

| Document | What it answers |
| --- | --- |
| [openagentsec_current_research_state.md](openagentsec_current_research_state.md) | What was shown, rejected, and limited |
| [OPENAGENTSEC_V1_RESEARCH_FREEZE.md](OPENAGENTSEC_V1_RESEARCH_FREEZE.md) | Formal freeze statement |
| [phase_status.md](phase_status.md) | Phase 22–24 status |
| [validated_results.md](validated_results.md) | Final experimental table only |
| [claim_boundaries.md](claim_boundaries.md) | Allowed vs forbidden claims |
| [testing_reality_matrix.md](testing_reality_matrix.md) | Contract / simulation / live classification |
| [technical_debt.md](technical_debt.md) | Known debt; not a fix list |
| [future_work.md](future_work.md) | High-value directions, not Phase 23 continuation |

---

## How to read the rest of this folder

Many files in `docs/research/` predate Phase 22–23. They remain as historical reports.

If an older page says any of the following, treat it as **superseded**:

- zero false positives / zero false negatives
- cryptographically trusted evidence
- production-grade / enterprise platform
- all attacks covered / Prompt Injection resisted
- mock or planner tests as live Agent validation
- External / commercial API as live validated
- Phase 23 rejected hypotheses as vulnerabilities
- `tool/call` as execution
- 5-run decision consistency as fully deterministic Agent behavior
- stale test counts (e.g. 498/498)

---

## Project positioning

**Maturity:** research framework  
**Not:** production system
