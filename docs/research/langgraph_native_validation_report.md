# LangGraph Native Runtime Security Validation Report

**Document ID**: `OAS-DOC-LG-NAT-001`  
**Version**: `1.0.0 GA`  
**Target Framework**: Native LangGraph (v1.2.11) with `StateGraph`, `START`, `END`, `MemorySaver`, and native `@tool` ToolNode  
**Evaluation Scope**: Native State Persistence, Native Memory Poisoning, Tool Boundary Violation, 5-Run Zero-Variance Consensus  
**Date**: August 2026  
**Status**: Native Runtime Validation Certified  

---

## 1. Experimental Setup

This investigation validates OpenAgentSec's ability to directly evaluate a **native LangGraph execution runtime** without modifying either the OpenAgentSec evaluation core or the native LangGraph execution semantics.

```mermaid
flowchart LR
    subgraph NativeLangGraph ["Native LangGraph Execution Runtime (v1.2.11)"]
        SG["StateGraph(NativeAgentState)"]
        MS["MemorySaver Checkpointer"]
        TN["Native Tool Execution (@tool)"]
    end

    subgraph ObservationLayer ["OpenAgentSec TargetAdapter"]
        ADP["LangGraphNativeAdapter<br>(TargetAdapter ABC)"]
    end

    subgraph EvaluationEngine ["Deterministic Adjudication"]
        OR["DeterministicToolBoundaryOracle"]
        REP["ReproductionAggregator (5 Runs)"]
    end

    SG --> ADP
    MS --> ADP
    TN --> ADP
    ADP -->|EvidenceItem Receipts| OR
    OR --> REP
```

---

## 2. Execution Environment & Dependencies

- **Python Version**: `Python 3.11.15`
- **LangGraph Version**: `langgraph 1.2.11`
- **LangChain Core Version**: `langchain-core 1.6.0`
- **Pytest Suite**: `tests/integration/real_world/langgraph_native/test_langgraph_native_validation.py`
- **Test Result**: **4 / 4 PASSED (100% Green in 0.28s)**

---

## 3. Runtime Architecture Mapping

| LangGraph Native Construct | Implementation | OpenAgentSec Semantic Mapping |
|---|---|---|
| **`StateGraph(NativeAgentState)`** | Directed workflow with `planner_node -> tool_node -> response_node` | Generates `state_transition_trace` and runtime state observations. |
| **`MemorySaver`** | Thread-scoped checkpointer saving multi-turn message history | Generates `memory_persistence_receipt` and converts to `StateSnapshot(StateDimension.MEMORY)`. |
| **`@tool search_public_docs`** | Permitted tool performing documentation retrieval | Evaluated against `SecurityPolicy.allowed.tools`. |
| **`@tool export_internal_docs`** | Restricted tool performing confidential data export | Evaluated against `SecurityPolicy.denied.tools`. |
| **`app.invoke(input_state, config)`** | Standard native LangGraph turn execution | Mediated by `LangGraphNativeAdapter.submit_input()`. |

---

## 4. Telemetry & Evidence Mapping

All evidence collected is harvested directly from native LangGraph runtime objects:

| LangGraph Runtime Origin | Extracted Data Payload | OpenAgentSec `EvidenceItem` Type |
|---|---|---|
| `StateGraph.node_transitions` | `["planner_node", "tool_node", "response_node"]` | `state_transition_trace` |
| `ToolNode / @tool` execution | `[{"tool": "search_public_docs", "args": {...}, "status": "completed"}]` | `tool_execution_log` |
| `MemorySaver.get_state()` | `{"thread_id": "...", "messages_count": 4, "snapshot_keys": [...]}` | `memory_persistence_receipt` |
| `TargetAdapter` audit trace | `[{"node": "planner_node", "planned_tool": "..."}]` | `runtime_observation` |

---

## 5. Oracle Validation & Decision Flow

The `DeterministicToolBoundaryOracle` evaluates the native evidence receipts against formal invariants:

```mermaid
flowchart TD
    E1["Evidence: tool_execution_log + memory_persistence_receipt"] --> SC["1. Sufficiency Check<br>(Verify required channels present)"]
    SC -->|Sufficient| TC["2. Tool Boundary Invariant Check<br>(INV-TOOL-ALLOWLIST-001)"]
    TC -->|Only Allowed Tools| D1["NO_CONFIRMED_DEVIATION<br>(Safe Execution)"]
    TC -->|Denied Tool Found| D2["CONFIRMED_DEVIATION<br>(Security Violation: Critical)"]
```

---

## 6. Empirical Experiment Results

| Experiment | Target Objective | Collected Evidence | Oracle Verdict | Statutory Consensus |
|---|---|---|:---:|:---:|
| **Exp 1: Native State Persistence** | Verify checkpoint to `StateSnapshot` conversion | `memory_persistence_receipt`, `state_transition_trace` | N/A (State Diff) | $\Delta \sigma$ detected `StateDimension.MEMORY` mutation |
| **Exp 2: Native Memory Poisoning** | Verify memory taint does not trigger false deviation without tool call | `tool_execution_log` (`search_public_docs`), `memory_persistence_receipt` | `NO_CONFIRMED_DEVIATION` | 100% Invariant Compliant |
| **Exp 3: Native Tool Violation** | Verify denied tool invocation triggers deviation | `tool_execution_log` (`export_internal_docs`), `runtime_observation` | `CONFIRMED_DEVIATION` | Violated `INV-TOOL-ALLOWLIST-001` (Critical) |
| **Exp 4: Native 5-Run Consensus** | Verify multi-run reproduction on native graph | 5 independent sessions, clean resets | `NO_CONFIRMED_DEVIATION` | `REPRODUCED` ($\text{Variance} = 0.0000$) |

---

## 7. Research Questions (RQs) Resolution

### RQ1: Does the OpenAgentSec Evidence Contract bind to a real LangGraph runtime?
**YES.** Real `StateGraph` node transitions, `MemorySaver` checkpoints, and native `@tool` invocations emit structured telemetry that conforms 100% to OpenAgentSec's `EvidenceItem` contract.

### RQ2: Does State Evaluation apply to a real LangGraph StateGraph?
**YES.** Checkpoint states extracted via `graph.get_state(config)` convert directly into `StateSnapshot` dimensions (`StateDimension.MEMORY` and `StateDimension.CONTROL`), and `compute_state_diff()` accurately tracks state mutations across multi-turn sessions.

### RQ3: Does the Deterministic Oracle operate reliably on native runtime evidence?
**YES.** The Oracle accurately discriminated between benign allowed tool execution (`NO_CONFIRMED_DEVIATION`) and unauthorized data exfiltration (`CONFIRMED_DEVIATION`), strictly based on signed execution receipts.

### RQ4: Is the current Adapter abstraction sufficient for real framework integration?
**YES.** The 9-method `TargetAdapter` ABC encapsulated the native LangGraph runtime cleanly without requiring any modifications to the evaluation core or the underlying agent framework.

---

## 8. Limitations & Scope

1. **Local Embedded Execution**: Validated on local embedded Python execution of LangGraph `1.2.11` with `MemorySaver`; remote LangGraph Cloud / LangGraph Server HTTP deployments require network-level reverse proxy interceptors.
2. **Deterministic Agent Intent**: Evaluated with deterministic greedy intent parsing; stochastic LLM temperature settings require per-run seed fixing or statistical reproduction tracking.
