# Phase 97A — Dynamic Propagation & Cross-Module Integration Design

**Document ID:** `DOC-ARCH-PHASE97A-GATE-003`  
**Phase:** Phase 97A (Gate 003)  
**Task:** `Phase-97A-GATE-003`  
**Evaluation Mode:** `defensive_evaluation`  
**PRD Alignment:** PRD v3.1 §2.4, §2.8 & §4; PRD v1.0 §4, §10; Phase 96C; Phase 97A Tasks 1 & 2  
**Status:** Approved / Frozen Architecture Design  

---

## 1. Executive Summary & Safety Invariants

This document specifies the integrated architecture connecting the **Cross-Module Propagation Dynamics Engine** (`PropagationDynamicsEngine`) and the **Cross-Module Long Chain Injection Engine** (`CrossModuleInjectionEngine`). The unified engine suite enables end-to-end multi-layer attack propagation modeling, Markov state distribution convergence tracking, edge conductivity pressure calculation, and standardized candidate exploit chain synthesis across attack paths **PATH-001** through **PATH-008**.

### Non-Negotiable Safety Boundaries

```yaml
safety_boundaries:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  synthetic_only: true
  dashboard_not_execution_interface: true
  red_team_engine_not_executable: true
  propagation_equation_is_not_exploit_chain: true
  theory_model_is_not_detection_rule: true
  requires_human_review: true
  all_findings_are_candidate: true
  evidence_mode: synthetic_only
```

---

## 2. Integrated System Architecture

The Phase 97A integration brings together two tightly coupled layers:

1. **Analytical / Theoretical Core (`PropagationDynamicsEngine`)**:
   - Maintains continuous equations for edge propagation pressure ($P_{\text{edge}}$), node defense state evolution ($D_{\text{node}}$), and cumulative path degradation ($G_{\text{path}}$).
   - Enforces a 5-state Markov stochastic process with strict mathematical invariance ($\sum_{j=1}^5 T_{ij} = 1.00$).
   - Models domain-specific attenuation rules (HRG, Boundary Preservation, Redaction, Audit Damping, Replay Gate) and amplification mechanisms (Sequential Weak Boundary, Cross-Layer Crossing, Feedback Loops).

2. **Operational Injection Core (`CrossModuleInjectionEngine`)**:
   - Ingests structured scenario playbooks (`playbooks/cross_module/path_001_to_008_scenarios.yaml`) encompassing 34 steps and 8 attack objectives.
   - Drives step-by-step injection sessions, computing real-time pressure transfer across module boundaries.
   - Generates standardized `<SIM_TRACE_...>` evidence traces and candidate exploit chain dossiers (`<SIM_EXPLOIT_CHAIN_...>`).

```
+---------------------------------------------------------------------------------------------------+
|                                  PHASE 97A INTEGRATED ENGINE SUITE                                |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   +---------------------------------------+       +-------------------------------------------+   |
|   |       Playbook Scenario Catalog       | ----> |       CrossModuleInjectionEngine          |   |
|   |      (PATH-001 .. PATH-008, 34 Steps) |       |  (Step Injection & Trajectory Orchestr.)  |   |
|   +---------------------------------------+       +-------------------------------------------+   |
|                                                                 |                 ^               |
|                                                     Trigger Step|                 | Pressure, D_t |
|                                                     Parameters  |                 | Markov Dist.  |
|                                                                 v                 |               |
|                                                   +-------------------------------------------+   |
|                                                   |        PropagationDynamicsEngine          |   |
|                                                   | (P_edge, D_node, G_path, Markov Transition|   |
|                                                   +-------------------------------------------+   |
|                                                                 |                                 |
|                                                                 v                                 |
|                 +-----------------------------------------------------------------+               |
|                 |                   Unified Output Artifacts                      |               |
|                 |  1. Step Evidence Traces (<SIM_TRACE_...>)                      |               |
|                 |  2. Exploit Chain Candidates (<SIM_EXPLOIT_CHAIN_...>)          |               |
|                 |  3. Markov 5-State Trajectory Distributions (Sum=1.0)           |               |
|                 |  4. Path Degradation Classifications (G_path)                   |               |
|                 |  5. Phase Checkpoint Snapshot (phase97a_checkpoint.json)       |               |
|                 +-----------------------------------------------------------------+               |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Mathematical Foundations & Propagation Equations

### 3.1 Edge Propagation Pressure ($P_{\text{edge}}$)

At simulation time $t$, when signal traverses from source node to target node across edge $e$:
$$P_{\text{edge}}(t) = \text{clamp}\Big( S_{\text{source}}(t) \cdot W_{\text{edge}} \cdot A_{\text{pattern}} \cdot (1.0 + F_{\text{feedback}}) \cdot (1.0 - D_{\text{target}}(t)), 0.0, 1.0 \Big)$$

- $S_{\text{source}}(t) \in [0.0, 1.0]$: Inbound signal intensity.
- $W_{\text{edge}} \in [0.0, 1.0]$: Conductivity weight of the edge type.
- $A_{\text{pattern}} \ge 0.0$: Modifying factor based on attack pattern matching.
- $F_{\text{feedback}} \in [-1.0, 1.0]$: Active feedback factor (positive/negative reinforcement).
- $D_{\text{target}}(t) \in [0.0, 1.0]$: Current defense strength of the target node.

### 3.2 Target Node Defense State Evolution ($D_{\text{node}}$)

$$D_{\text{node}}(t+1) = \text{clamp}\Big( D_{\text{node}}(t) + R_{\text{control}} - P_{\text{in}}(t) \cdot V_{\text{node}} + H_{\text{review}}, 0.0, 1.0 \Big)$$

- $R_{\text{control}} \in [0.0, 1.0]$: Internal control recovery rate.
- $P_{\text{in}}(t) = \sum_{e \in \text{InEdges}} P_{\text{edge}, e}(t)$: Aggregated inbound edge pressure.
- $V_{\text{node}} \in [0.0, 1.0]$: Layer/Module vulnerability factor.
- $H_{\text{review}} \in [0.0, 0.5]$: Human Review Gate recovery credit.

### 3.3 Markov 5-State Transition & Convergence

The node defense state is modeled as a 5-state Markov stochastic process $\mathcal{S} = \{\text{stable}, \text{pressured}, \text{degraded}, \text{blocked}, \text{failed}\}$.

For state distribution $\vec{\pi}(t) = [\pi_1, \pi_2, \pi_3, \pi_4, \pi_5]$:
$$\vec{\pi}(t+1) = \vec{\pi}(t) \cdot \mathbf{T}_{\text{dynamic}}(P_{\text{in}}, R_{\text{ctrl}}, H_{\text{rev}})$$

Under perturbation, transition probabilities are adjusted dynamically and re-normalized:
$$\mathbf{T}_{ij}^{\text{dyn}} = \frac{\mathbf{T}_{ij}^{\text{base}} + \Delta_{ij}(P_{\text{in}}, R, H)}{\sum_{k=1}^5 \big(\mathbf{T}_{ik}^{\text{base}} + \Delta_{ik}(P_{\text{in}}, R, H)\big)}$$
This guarantees the fundamental invariant:
$$\sum_{j=1}^5 \mathbf{T}_{ij}^{\text{dyn}} = 1.000000 \quad \forall i \in \{1..5\}$$

### 3.4 Path Degradation Model ($G_{\text{path}}$)

$$G_{\text{path}} = \sum_{e \in \mathcal{E}} P_{\text{edge}, e} \cdot (1 + A_{\text{seq}}) - \sum_{r \in \mathcal{R}_{\text{atten}}} A_r + \sum_{m \in \mathcal{M}_{\text{ampl}}} A_m - \sum_{b \in \mathcal{B}_{\text{block}}} B_b$$

Trajectory mapping:
- $G_{\text{path}} < 0.0 \implies \text{stable\_or\_pressured}$ (Effective containment)
- $0.0 \le G_{\text{path}} < 0.5 \implies \text{partial\_pressure}$
- $0.5 \le G_{\text{path}} < 1.0 \implies \text{partial\_degradation}$
- $1.0 \le G_{\text{path}} < 2.0 \implies \text{significant\_degradation}$
- $G_{\text{path}} \ge 2.0 \implies \text{critical\_degradation}$

---

## 4. Scenario Catalog Coverage (PATH-001 .. PATH-008)

| Path ID | Alias ID | Modules Involved | Layers Involved | Steps | Primary Attacker Objective |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **PATH-001** | `PATH-SUPPLY-DEV-RAG-RUNTIME-001` | M43, M46, M48, M49, M50 | 4 layers (L1..L4) | 5 | Multi-stage lifecycle breach |
| **PATH-002** | `PATH-SUPPLY-A2A-DEP-RUNTIME-001` | M44, M45, M46, M47, M50 | 3 layers (L1, L2, L4) | 5 | Dev/Identity credential abuse |
| **PATH-003** | `PATH-RAG-RUNTIME-001` | M48, M49, M50 | 2 layers (L3, L4) | 3 | RAG poisoning & permission elevation |
| **PATH-004** | `PATH-CHATBOT-AGENT-001` | M01, M38, M16 | 3 layers (Chatbot, Agent, L4) | 3 | Prompt injection & HRG bypass |
| **PATH-005** | `PATH-AGENT-SUPPLY-CHAIN-001` | M38, M43, M44, M50 | 3 layers (Agent, L1, L4) | 4 | MCP descriptor tampering & A2A spoofing |
| **PATH-006** | `PATH-RAG-DATA-EXFIL-001` | M06, M34, M20, M50 | 3 layers (RAG, Exfil, L4) | 4 | Indirect prompt injection & data exfiltration |
| **PATH-007** | `PATH-IDENTITY-PERMISSION-001` | M10, M11, M08, M41 | 4 layers (Chatbot, RAG, Agent, L4) | 4 | Cross-session token leak & role escalation |
| **PATH-008** | `PATH-MULTI-AGENT-IMPACT-001` | M37, M21, M22, M50 | 3 layers (Agent, Report, L4) | 4 | Multi-agent state conflict & audit evasion |

---

## 5. Multi-Scenario State Permutations & Integration Verification

The integration test suite (`tests/test_phase97a_integration_suite.py`) and validator (`scripts/validate_phase97a_gate_suite.py`) systematically evaluate the joint engines across three operational modes:

1. **Baseline Contained Mode (Standard Operating Conditions)**:
   - Initial defense scores: $D_{\text{init}} = 0.85$ (or module baseline).
   - Inbound edge pressures are attenuated by active boundary controls.
   - Outcome: $0/8$ breakthrough detections, $8/8$ contained paths, $G_{\text{path}} < 0.0$ (`stable_or_pressured`).
   - Markov distributions maintain dominant probability in `stable` or `pressured`.

2. **Perturbation Stress Mode (Weakened Initial Defense)**:
   - Initial defense degraded to $D_{\text{init}} \in [0.40, 0.60]$.
   - Evaluates resilience, control recovery ($R_{\text{ctrl}}$), and Human Review Gate ($H_{\text{rev}}$) stabilization.
   - Markov distributions reflect progressive recovery or controlled pressure absorption.

3. **Adversarial Breach Mode (Simulated Control Failure)**:
   - Injection steps simulate failure of boundary checks (e.g. descriptor poisoning, permission boundary leakage, sandbox evasion).
   - Evaluates breakthrough detection criteria:
     - `breakthrough_detected = true`
     - `severity_tier` escalation: `candidate_medium` $\to$ `candidate_high` $\to$ `candidate_critical`
     - Correct construction of `ExploitChainCandidate` dossiers containing synthetic findings `<SIM_FINDING_...>` and safety flags.

---

## 6. Phase Checkpoint Snapshot Architecture

The integration suite generates `artifacts/batch_checkpoints/phase97a_checkpoint.json` capturing the complete state snapshot of the Phase 97A execution:

```json
{
  "checkpoint_version": "1.0",
  "session_id": "phase97a_gate003_integration_session_001",
  "phase": "Phase-97A",
  "task_id": "Phase-97A-GATE-003",
  "status": "completed",
  "total_scenarios": 8,
  "total_steps_executed": 34,
  "total_evidence_traces": 34,
  "safety_boundaries": {
    "confirmed_vulnerability": false,
    "formal_finding_allowed": false,
    "production_safety_claimed": false,
    "synthetic_only": true,
    "dashboard_not_execution_interface": true,
    "red_team_engine_not_executable": true
  },
  "summary_metrics": { ... },
  "paths": { ... },
  "adversarial_stress_scenarios": { ... }
}
```

---

## 7. Deliverables & Acceptance Checklist

| Item | File Path | Status |
| :--- | :--- | :--- |
| **Integrated Design Document** | `docs/phase97a_dynamic_propagation_and_cross_module_integration_design.md` | Verified |
| **Integration Test Suite** | `tests/test_phase97a_integration_suite.py` | Verified (100% Pass) |
| **Standalone Validator** | `scripts/validate_phase97a_gate_suite.py` | Verified (100% Pass) |
| **Integration Validation Report** | `reports/phase97a_integration_suite_validation_report.md` | Verified |
| **Phase Checkpoint Snapshot** | `artifacts/batch_checkpoints/phase97a_checkpoint.json` | Generated & Verified |
| **Task Execution Summary** | `phase97a_gate003_execution_summary.yaml` | Verified |
| **Delivery Manifest** | `delivery.json` | Updated |
