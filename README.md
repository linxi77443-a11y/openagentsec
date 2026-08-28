# OpenAgentSec

**A research framework for evidence-based and reproducible security evaluation of tool-using AI agents.**

[Research baseline](docs/research/README.md) · [Current state](docs/research/openagentsec_current_research_state.md) · [Validated results](docs/research/validated_results.md) · [Claim boundaries](docs/research/claim_boundaries.md) · [Quick start](docs/release/quick_start.md)

OpenAgentSec v1.x research baseline is **frozen** (Phase 24.1). See [OPENAGENTSEC_V1_RESEARCH_FREEZE.md](docs/research/OPENAGENTSEC_V1_RESEARCH_FREEZE.md).

---

## 🌟 Project Overview

OpenAgentSec is an **Agent Security Evaluation Research Framework**.

It observes a target agent, verifies Evidence independently, requires execution receipts before treating a tool as executed, adjudicates **tool-boundary** policy deterministically, and checks whether independent runs are integrity-verified reproductions — not copies of one run.

It is **not**:

- a production security scanner
- a production-grade security platform
- a universal Agent vulnerability detector
- a cryptographic attestation system
- a runtime security product or a replacement for runtime enforcement
- a claim that any evaluated agent is safe or attack-proof

Current maturity: **research framework**. Not a production system.

---

## ❓ Why OpenAgentSec?

Traditional Agent tests often mix layers that are not the same thing:

```text
model text
≠ tool intent (tool/call)
≠ actual execution (tool/result + receipt)
≠ policy deviation
≠ attack-caused deviation
```

OpenAgentSec uses a Trust Chain to keep those layers separate, and fail closed when a layer is missing.

`tool/call` is intent. Only a matching `tool/result` or runtime completion receipt can make an action execution-eligible.

---

## 🏛️ Architecture Overview

Trusted claiming uses `evaluate_verified()`. Legacy `evaluate()` still exists in code and is **not** the research claiming path.

```text
Runtime Observation
        ↓
Evidence Verification
        ↓
Execution Receipt
        ↓
Deterministic Oracle (evaluate_verified)
        ↓
Integrity-verified Reproduction
        ↓
Matched Baseline (for attack claims)
```

**Evidence Precedence Axiom:** independently verified Evidence and execution receipts outrank producer self-reports, model text, and `tool/call` intent. A producer field `verified=True` is not trusted Evidence.

Core capabilities of this research path:

- Evidence-admissible evaluation
- Intent vs execution separation
- Deterministic tool-boundary adjudication
- Integrity-verified reproduction
- Cross-runtime validation (classified by actual execution level)
- Attack-vs-baseline causal evaluation

---

## 🎯 Target & Benchmark Coverage

| Target | Reality level | Claim boundary |
| --- | --- | --- |
| DeepSeek Harness | **Live Agent runtime** | Current isolated runtime/config only |
| LangGraph (`TARGET-LANGGRAPH-MVP1` and related LangGraph targets) | **Real framework runtime with controlled agent logic** | Not a live general LLM Agent certificate |
| MCP stdio | **Controlled real protocol runtime** | Controlled test server |
| `TARGET-COMMERCIAL-LLM-AGENT` / external cloud API | **Contract-level only** | **Not live validated** |

Directory name `tests/integration/real_world/` does **not** mean every file is a live Agent experiment. See [testing_reality_matrix.md](docs/research/testing_reality_matrix.md).

Coverage is **not** “all Agent attacks.” The current Oracle is tool-boundary-focused. Benchmark registry targets remain historical contract artifacts; Phase 23 live claims are the DeepSeek Harness matched pilots below.

### Real Agent Experiments

Phase 23 ran matched, receipt-confirmed pilots on a clean DeepSeek Harness runtime. **No attack-associated effect was established under the tested controlled conditions.**

| Experiment | Result |
| --- | --- |
| Delayed Action Drift | **NO ATTACK EFFECT OBSERVED** |
| Authority Spoofing | **BASELINE RUNTIME BEHAVIOR** |
| Indirect Prompt Injection | **NO INDIRECT ATTACK EFFECT OBSERVED** |
| Delegation | **BASELINE DELEGATION BEHAVIOR** |
| Mention vs Execute | **MENTION/EXECUTE BOUNDARY PRESERVED** |

These results do **not** mean “all such attacks were blocked” or “the agent is secure.” They mean: under those templates, runtimes, and sample sizes, no attack-associated causal effect was established. Full table: [validated_results.md](docs/research/validated_results.md).

### Current Limitations

- One primary live Agent runtime (DeepSeek Harness)
- Oracle focus is **tool boundary**, not every `SecurityPolicy` dimension
- Phase 23 samples are pilots (5 vs 5 or 10 vs 10)
- Evidence is not cryptographic attestation
- External cloud APIs are not live validated
- Not a production platform
- Foreground subagent parent-view hides child tool traces unless a child session id is obtained

Allowed vs forbidden language: [claim_boundaries.md](docs/research/claim_boundaries.md).

---

## ⚡ Quick Example

```bash
git clone https://github.com/linxi77443-a11y/openagentsec.git
cd openagentsec
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install pytest pyyaml jsonschema

# Non-live regression (default). Live DeepSeek / paid API tests stay skipped.
pytest tests/unit tests/integration -v
bash scripts/verify_release.sh

python scripts/run_evaluation_pipeline.py --help
python -m openagentsec.cli --help
```

Live DeepSeek tests require `OPENAGENTSEC_ENABLE_LIVE_TESTS=true`.
External API live tests require `OPENAGENTSEC_ENABLE_EXTERNAL_API_TESTS=true` and are **not** a completed live validation.

More setup: [Quick Start](docs/release/quick_start.md).

---

## Documentation

Start here: **[docs/research/README.md](docs/research/README.md)** (research index).

| Document | Role |
| --- | --- |
| [Current research state](docs/research/openagentsec_current_research_state.md) | Source of truth for what was shown |
| [Phase status](docs/research/phase_status.md) | Phase 22–24 freeze table |
| [Validated results](docs/research/validated_results.md) | Final experimental table |
| [Claim boundaries](docs/research/claim_boundaries.md) | Allowed / forbidden claims |
| [Testing reality](docs/research/testing_reality_matrix.md) | Contract vs simulation vs live |
| [Technical debt](docs/research/technical_debt.md) | Known debt (not fixed in 24.1) |
| [Future work](docs/research/future_work.md) | Research directions, not a sprint plan |
| [v1 freeze](docs/research/OPENAGENTSEC_V1_RESEARCH_FREEZE.md) | Freeze statement |

Older reports under `docs/research/` may use pre-freeze language. Where they conflict with the documents above, **the freeze documents win**.

---

## License

Apache-2.0. See [LICENSE](LICENSE).
