# Testing Reality Matrix

Classification is by **what actually runs**, not by the folder name `real_world`.

Live DeepSeek pytest trees stay skipped unless `OPENAGENTSEC_ENABLE_LIVE_TESTS=true`.  
External API live trees stay skipped unless `OPENAGENTSEC_ENABLE_EXTERNAL_API_TESTS=true`. Default non-live regression must keep those skipped.

| Area | Reality level | Typical location | Trust Chain role | Claim boundary |
| --- | --- | --- | --- | --- |
| Contract / unit | Contract | `tests/unit/`, `tests/integration/contract_integrity/` | Evidence, receipt, Oracle, integrity, live-gate flags | Not real-world Agent validation |
| Planner / scenario pipeline | Simulation | `tests/integration/planner/` | Pipeline and metric contracts | Not live Agent validation |
| Fake / example adapters | Simulation | `tests/integration/real_world/adapters/`, `test_blackbox_validation.py`, `test_langchain_validation.py`, `test_langgraph_validation.py` (example adapter), `test_mcp_validation.py`, `test_multi_agent_validation.py`, `llm_powered/` | Adapter contract examples or simulated agents | Directory is under `real_world/` but **not** live Agent |
| LangGraph experiments | Framework real (controlled logic) | `tests/integration/real_world/langgraph/` | Graph runtime + evaluation | Controlled agent logic |
| LangGraph native | Framework real (controlled logic) | `langgraph_native/` | Native graph runtime | Not a live LLM Agent certificate |
| LangGraph cross | Framework real (controlled logic) | `langgraph_cross/` | Phase 22.1 Trust Chain transfer | Same |
| DeepSeek harness (non-live package) | Simulation / harness fixture | `deepseek_harness/` | Local harness object, not the 3081 live profile by default | Do not equate with live 23.x causal pilots |
| DeepSeek live / attacks / profile / evidence_audit | Live Agent runtime (opt-in) | `deepseek_live/`, `deepseek_live_violation/`, `deepseek_attack_validation/`, `deepseek_runtime_profile/`, `evidence_audit/` | Live HTTP to DeepSeek Harness | Gated; attack-condition tests are not automatically matched causal findings (see 23.1 superseded) |
| Phase 23.2–23.6 scripts | Controlled causal live experiment | `scripts/phase23_*.py`, artifacts under `artifacts/live_validation/` | Full trusted path + matched baseline / mention-execute | Pilot; named runtime/config |
| MCP stdio | Real protocol runtime (controlled server) | `mcp_real/` | Phase 22.2 | Not arbitrary MCP deployments |
| External API | Contract-level only | `external_api/`, `contract_integrity/test_external_api_partial_observability.py` | Intent without receipt → inconclusive | **Not live cloud validation** |
| `tests/integration/live_llm/` | Simulation (in-process HTTP mock named “live”) | `tests/integration/live_llm/` | Local socket server emulating OpenAI wire protocol | **Not** gated by `OPENAGENTSEC_ENABLE_LIVE_TESTS`; **not** live cloud validation |
| Release / planner docs tests | Contract on docs/artifacts | `tests/integration/release_validation/`, parts of `planner/` | Release gate | Not Agent security findings |

**Rule:** `tests/integration/real_world/` is a mixed tree. Calling a test “real-world” because of the path is incorrect.
