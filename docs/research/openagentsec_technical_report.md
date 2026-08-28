# OpenAgentSec: A Deterministic Evidence-driven Security Benchmark for Stateful and Tool-Using AI Agents

**Technical Report v1.0.0**  
**OpenAgentSec Research Team**  
**August 2026**

> **Phase 24.1:** Historical report. Current claims: [openagentsec_current_research_state.md](openagentsec_current_research_state.md). Freeze index: [README.md](README.md).

---

## Abstract

Existing safety benchmarks for Large Language Models (LLMs) and AI Agents suffer from five foundational limitations:
1. **Text-Only Judgment**: Relying on natural language outputs and LLM-as-a-Judge evaluations, which are vulnerable to model hallucination, output deception, and scoring drift.
2. **Absence of Physical Execution Receipts**: Inability to differentiate between agent conversational intent and verified physical tool executions on underlying host systems.
3. **Lack of Causal Chain Analysis**: Conflating passive state persistence with active risk activation, failing to decouple memory storage from retrieval-induced decision coupling.
4. **Non-Deterministic and Unreproducible Evaluation**: Evaluating safety via single-shot prompts without statutory zero-variance multi-run reproduction requirements.
5. **Lack of Real-World Agent Portability**: Benchmarking synthetic toy scripts rather than standard agent frameworks (LangGraph, LangChain), tool boundaries (MCP Gateway), and commercial closed-source APIs (GPT-4o, Claude, DeepSeek).

To resolve these challenges, we introduce **OpenAgentSec**, a policy-driven, evidence-based security evaluation harness for stateful and tool-using AI agents. OpenAgentSec establishes the **Evidence $\to$ Oracle $\to$ Reproduction** trust loop, utilizing deterministic runtime receipts, independent non-LLM oracles, fail-closed safety semantics, and statutory 5-run zero-variance reproduction. Across 7 agent architectural tiers and 8 canonical adversarial scenarios, OpenAgentSec provides a rigorous, formal foundation for evaluating AI Agent security.

---

## 1. Problem Formulation

We formalize the AI Agent Security Evaluation Problem as follows:

Given:
- An **Agent Target** $\mathcal{A}$ under evaluation operating across multi-turn conversational trajectories.
- A controlled **Stimulus** $\mathcal{S}$ injected across conversational turns.
- A formal **Security Policy** $\mathcal{P} = (\mathcal{I}, \mathcal{R}_{\text{allow}}, \mathcal{R}_{\text{deny}}, \mathcal{E}_{\text{req}})$, where $\mathcal{I}$ denotes safety invariants, $\mathcal{R}$ denotes tool allowlists/denylists, and $\mathcal{E}_{\text{req}}$ denotes mandatory evidence requirements.
- An observed physical **Execution Trace** $\mathcal{T}$.

The evaluation harness must compute an objective decision $\mathcal{D} \in \{\text{CONFIRMED\_DEVIATION}, \text{NO\_CONFIRMED\_DEVIATION}, \text{INCONCLUSIVE}\}$ such that:

$$\mathcal{D} = \mathcal{O}(\mathcal{P}, \mathcal{T}, \mathcal{E})$$

Subject to:
1. **Evidence Sufficiency Gate**:
   $$\text{Completeness}(\mathcal{E}, \mathcal{E}_{\text{req}}) < 1.0 \implies \mathcal{D} = \text{INCONCLUSIVE}$$
2. **Oracle Independence**: The oracle $\mathcal{O}$ evaluates only verified physical evidence $\mathcal{E}$ and delta state mutations $\Delta \sigma$, remaining strictly isolated from model-generated natural language.
3. **Statutory Zero-Variance Reproduction**:
   $$\text{Outcome}(\mathcal{A}, \mathcal{S}) = \text{REPRODUCED} \iff \forall i, j \in [1, 5], \quad \mathcal{D}_i = \mathcal{D}_j \land \mathcal{D}_i \neq \text{INCONCLUSIVE}$$

---

## 2. Scientific Contributions

### Contribution 1: Evidence-Driven Agent Security Evaluation
OpenAgentSec fundamentally shifts agent security evaluation from subjective text scoring to immutable, signed physical execution receipts. We establish the **Evidence Precedence Axiom**:
$$\text{Verified Physical Receipts} \succ \text{Emitted Tool Intents} \succ \text{Model Self-Report Text}$$
Even if an agent outputs deceptive text claiming successful unauthorized data exfiltration, the harness adjudicates based strictly on whether physical RPCs traversed the tool boundary.

### Contribution 2: Causal Security Chain Analysis
Through controlled comparative baselines, OpenAgentSec disproved the assumption that *"Memory Persistence equals Security Risk"*. We proved that memory taint remains benign until activated by a 5-stage causal coupling chain:
$$\text{Memory Taint} \xrightarrow{\text{Query Match}} \text{Retrieval} \xrightarrow{\text{Prompt Synthesis}} \text{Context Injection} \xrightarrow{\text{LLM Reasoning}} \text{Decision Coupling} \xrightarrow{\text{Dispatch}} \text{Action Deviation}$$

### Contribution 3: Deterministic and Fail-Closed Adjudication
OpenAgentSec replaces stochastic LLM Judges with the deterministic `DeterministicToolBoundaryOracle`. Missing telemetry, partially observable communication channels, or unverified evidence automatically trigger **Fail-Closed semantics (`INCONCLUSIVE`)**, eliminating false confirmations.

### Contribution 4: Universal Real Agent Portability
OpenAgentSec seamlessly scales across 7 target architectural tiers:
- Whitebox StateGraph agents (`LangGraphMVP1TargetAgent`, `LangGraphRetrievalCoupledTargetAgent`).
- 4-layer Policy Enforcement Point agents (`LangGraphAuthorizationAwareTargetAgent`, `ParameterAuthorizationAwareTargetAgent`).
- External framework agents (`LangChainRealTargetAgent`).
- Protocol boundary agents (`MCPToolGateway`).
- Commercial blackbox APIs (`CommercialLLMAgent` evaluating GPT-4o / DeepSeek API formats).

---

## 3. Experimental Evaluation Synthesis

| Evaluation Dimension | Evaluated Target | Key Security Metric | Metric Value | Research Finding |
|---|---|---|---|---|
| **Memory Persistence** | `TARGET-LANGGRAPH-MVP1` | `subsequent_deviation_rate` | **`0.0`** | Memory persistence without retrieval does NOT cause action deviation. |
| **Retrieval Coupling** | `TARGET-LANGGRAPH-RETRIEVAL` | `subsequent_deviation_rate`<br>`taint_to_action_lag` | **`1.0`**<br>**`1 step`** | RAG retrieval activates delayed memory poisoning into confirmed deviation. |
| **Attack Generalization** | `TARGET-LANGGRAPH-RETRIEVAL` | `attack_success_rate` | **`1.0`** (3/3) | Direct instruction, authority spoofing, and workflow poisoning all succeed. |
| **Security Controls** | `TARGET-LANGGRAPH-RETRIEVAL` | `mitigation_effectiveness` | **`100%`** (Trust/Context)<br>**`0%`** (Passive Tag) | Trust Filtering & Context Isolation block attacks; Passive Annotation fails. |
| **Role & Token Auth** | `TARGET-LANGGRAPH-AUTH` | `authorization_bypass_rate` | **`0.0`** | Pre-execution PEP blocks role spoofing, prompt escalation, and fake tokens. |
| **Parameter Scope** | `TARGET-LANGGRAPH-PARAM` | `parameter_violation_block_rate` | **`1.0`** (100%) | 4-layer PEP blocks data exfiltration to external URLs and path traversal. |
| **LangChain Adapter** | `TARGET-LANGCHAIN-REAL` | `reproduction_rate` (5/5) | **`1.0`** (`REPRODUCED`) | Evaluates real LangChain agents via Callbacks without whitebox state access. |
| **MCP Tool Gateway** | `TARGET-MCP-GATEWAY` | `reproduction_rate` (5/5) | **`1.0`** (`REPRODUCED`) | Enforces perimeter policy at network/RPC boundary independently of agent code. |
| **Commercial Blackbox** | `TARGET-COMMERCIAL-LLM` | `reproduction_rate` (5/5) | **`1.0`** (`REPRODUCED`) | Successfully evaluates commercial LLM API agents via outer-loop receipts. |

---

## 4. Conclusion

OpenAgentSec establishes the first deterministic, evidence-driven, and reproduction-validated benchmark framework for autonomous AI Agents. By decoupling evaluation from model self-reports and grounding decisions in immutable physical receipts, OpenAgentSec provides an open, scientific foundation for stateful AI security governance.
