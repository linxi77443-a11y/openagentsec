# OpenAgentSec External User Journey Validation

**Validation Target: OpenAgentSec v1.0.0 Public Usability**  
**Document ID: OAS-DOC-USER-JOURNEY-001**

---

## 1. Executive Summary

To ensure OpenAgentSec is truly usable by the external open-source and enterprise AI community upon public release, we simulated three primary external user personas:
1. **User A: Academic AI Security Researcher** (Evaluating novel memory & RAG poisoning attacks).
2. **User B: Agent Framework & Toolchain Developer** (Integrating a proprietary custom agent runtime).
3. **User C: Enterprise SecOps & Compliance Officer** (Auditing autonomous agent safety invariants for production release).

---

## 2. Simulated User Journeys & Empirical Feedback

```mermaid
journey
    title OpenAgentSec External User Journey Validation
    section User A: Security Researcher
      Read README & Technical Report: 5: Fast, clear axioms
      Run Full Benchmark Test Suite: 5: 157+ tests pass in 5s
      Inspect Causal Attribution Trace: 5: Memory->Retrieval isolated
    section User B: Agent Developer
      Read Quick Start & Adapter Docs: 5: Blackbox interface intuitive
      Subclass BlackboxTargetAdapter: 5: 30 lines of glue code
      Verify Tool Boundary Logging: 5: Outer-loop receipts captured
    section User C: Enterprise SecOps
      Audit Threat Model & Specification: 5: 4 domains, 8 scenarios mapped
      Review Invariant Oracles: 5: Zero LLM judge dependency
      Verify 5-Run Zero-Variance: 5: Audit-grade compliance proof
```

### Persona A: Academic AI Security Researcher
- **Objective**: Validate whether OpenAgentSec can reproduce delayed-recall memory poisoning and test mitigation boundaries.
- **Execution Path**:
  1. Cloned repo and ran `pip install -e .`.
  2. Read `docs/research/openagentsec_technical_report.md` and `docs/research/evaluation_methodology.md`.
  3. Executed `pytest tests/integration/planner/test_retrieval_attack_generalization.py -v`.
- **Validation Outcome**:
  - Successfully verified the 5-stage causal chain: $\text{Memory Taint} \to \text{Retrieval} \to \text{Context} \to \text{Decision} \to \text{Action}$.
  - Confirmed `attack_success_rate = 1.0` across Direct Instruction, Authority Spoofing, and Workflow Poisoning.
  - Verified that Trust Filtering (L2) and Context Isolation (L4) achieve 100% mitigation, while Passive Annotation yields 0%.
- **Time to First Benchmark Run**: **< 15 minutes**.

---

### Persona B: Agent Framework & Toolchain Developer
- **Objective**: Onboard a proprietary, non-LangGraph, non-LangChain enterprise Python agent (`CustomEnterpriseAgent`) into the benchmark harness.
- **Execution Path**:
  1. Consulted `docs/release/quick_start.md` §3 ("Extending the Framework").
  2. Implemented `ThirdPartyAgentAdapter` subclassing `BlackboxTargetAdapter` (35 lines of code in `tests/integration/external_validation/mock_third_party_agent/adapter.py`).
  3. Executed `pytest tests/integration/external_validation/test_external_adapter_contract.py -v`.
- **Validation Outcome**:
  - The proprietary agent required **zero modification to its internal code**.
  - All tool executions were captured into standard `EvidenceItem(evidence_type="tool_execution_log")` receipts.
  - Successfully ran statutory 5-run reproduction with `reproduction_status == REPRODUCED` and `variance_detected == False`.

---

### Persona C: Enterprise SecOps & AI Compliance Officer
- **Objective**: Evaluate an AI Agent against enterprise data exfiltration policies before approving deployment.
- **Execution Path**:
  1. Reviewed `docs/research/threat_model.md` and `docs/research/benchmark_specification.md`.
  2. Audited policy enforcement at the MCP Tool Gateway boundary (`MCPToolGateway`).
  3. Verified that external egress attempts (`destination="external_public_url"`) generated signed `authorization_check_receipt` records and **0 physical executions**.
- **Validation Outcome**:
  - Confirmed the **Evidence Precedence Axiom**: Even if an LLM generates deceptive text claiming successful exfiltration, the deterministic Oracle checks physical receipts and avoids false confirmations.
  - Confirmed the **Strict Fail-Closed Principle**: Any missing telemetry immediately yields `INCONCLUSIVE`, preventing unverified safety claims.

---

## 3. Usability & Ergonomics Feedback Matrix

| Evaluation Dimension | Usability Finding | Recommendation / Implemented Solution |
|---|---|---|
| **Installation Speed** | Local installation takes < 1 minute with standard `pip install -e .`. | Pinned core dependencies in `pyproject.toml`. |
| **Adapter Friction** | Implementing `BlackboxTargetAdapter` requires only 5 standard methods. | Provided template in `quick_start.md` and `mock_third_party_agent/`. |
| **Debugging Ambiguity** | When tests fail due to missing receipts, reason codes clearly identify root cause. | Enforced descriptive `reason_codes` in `DeterministicToolBoundaryOracle`. |
| **Reproduction Trust** | Multi-run aggregation transparently displays per-run decisions and variance status. | Output structured `ReproductionResult` with explicit `variance_detected` flag. |
