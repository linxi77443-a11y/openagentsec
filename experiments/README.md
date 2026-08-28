# OpenAgentSec Empirical Experiments & Verification Archive

**Directory Baseline**: `OpenAgentSec v1.x`  
**Status**: Governed Experiment Catalog  

---

## 1. Directory Structure

```text
experiments/
├── benchmark/      # Statutory Benchmark Execution Traces & Metrics (v1.0.0)
├── empirical/      # Hypothesis Validation Experiments (H1 Baseline, H2 Memory, H3 Multi-Agent, H4 Adaptive)
├── real_world/     # Real-World Agent Runtime Traces (LangGraph, MCP, LangChain, Commercial APIs)
└── archived/       # Historical Phase Experiment Runs (Phase 6–13 Archive)
```

---

## 2. Experiment Catalog & Research Matrix

| Subdirectory | Experiment Suite | Target Runtimes | Key Invariants Verified | Statutory Reproduction |
|---|---|---|---|---|
| **`benchmark/`** | `Benchmark Suite v1.0.0` | Whitebox, Framework Hook, Protocol Gateway, Blackbox API | `INV-TOOL-ALLOWLIST-001`<br>`INV-TOOL-PARAMETER-SCOPE-001` | $\text{Variance} = 0.0000$ ($5/5$) |
| **`empirical/`** | `EXP-H1` to `EXP-H4` | Synthetic & Stateful Multi-Turn Agents | `Delta State Evaluation`<br>`Privilege Monotonicity` | $\text{Variance} = 0.0000$ ($5/5$) |
| **`real_world/`** | `EXP-REAL-001` to `005` | LangGraph, MCP Gateway, LangChain RAG, OpenAI, Claude, DeepSeek | `StateGraph PEP`<br>`Fail-Closed Tool Gateway` | $\text{Variance} = 0.0000$ ($5/5$) |
| **`archived/`** | Historical Logs | Prototype Runtimes (Phases 6–13) | Development & Regression Traces | Historical Baseline |

---

## 3. Reproduction Command

To reproduce all canonical benchmark and real-world experiments:
```bash
# 1. Run all empirical & real-world integration tests
PYTHONPATH=src pytest tests/integration/ -v

# 2. Verify statutory release criteria
bash scripts/verify_release.sh
```
