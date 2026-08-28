# Phase 83A — Equation Consistency Review Checklist

## 1. Purpose

This checklist provides structured review items for verifying the consistency of the 3 core conceptual equations from Phase 82A. Each equation is reviewed across 8 dimensions: variable completeness, variable source mapping, graph schema alignment, dynamics model alignment, tabletop report alignment, pattern library alignment, safety semantics presence, and human review requirement.

**Tabletop review checklist only** — not executable logic, not automated validation.

## 2. Review Boundary

```yaml
review_boundary:
  conceptual_only: true
  executable: false
  human_review_required: true
  tabletop_review_checklist_only: true
```

## 3. Equation Review Items

### 3.1 EQ-EDGE-PROPAGATION-001: P_edge(t)

**Equation:** `P_edge(t) = S_source(t) × W_edge × A_pattern × F_feedback × (1 - D_target)`

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Variable Completeness** | All 5 variables (S_source, D_target, W_edge, A_pattern, F_feedback) are defined with name, symbol, type, range, and description | `pending` |
| **Variable Source Mapping** | S_source ← Phase 74A source node; D_target ← Phase 74A target node defense state; W_edge ← Phase 74A edge type weight; A_pattern ← Phase 81A pattern amplification; F_feedback ← Phase 77A feedback loop | `pending` |
| **Graph Schema Alignment (74A)** | Edge types (permission_dependency, context_influence, runtime_dependency, audit_dependency, supply_chain, api_injection, credential_access, repo_impact, tool_call_chain) map to W_edge discrete values; source/target node types align with 7-node-type schema | `pending` |
| **Dynamics Model Alignment (77A)** | F_feedback term aligns with 4 feedback loop types (runtime_control_feedback, permission_leakage_feedback, credential_pressure_feedback, audit_confirmation_feedback); propagation direction matches edge-type attenuation rules | `pending` |
| **Tabletop Report Alignment (79A/80A)** | P_edge values for edges observed in Phase 79A (M43→M46→M48→M49→M50) and Phase 80A (DEV-CRED, RAG) produce consistent relative ordering matching observed probability hints (medium_to_high > medium > low_to_medium) | `pending` |
| **Pattern Library Alignment (81A)** | A_pattern values map to 6 pattern-derived weights (W-ENTRY-VULN-001 through W-HRG-BREAK-001); per-edge A_pattern aggregation follows path-to-pattern associations | `pending` |
| **Safety Semantics Present** | conceptual_only: true, not_executable: true, not_production_risk: true, not_vulnerability_severity: true, not_exploitability_score: true, requires_human_review: true | `pending` |
| **Human Review Required** | All 7 dimensions above require human reviewer judgment; no automated pass/fail | `pending` |
| **Reviewer Notes** | | |

### 3.2 EQ-NODE-STATE-001: D_node(t+1)

**Equation:** `D_node(t+1) = clamp(D_node(t) + R_control - P_in(t) × V_node + H_review)`

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Variable Completeness** | All 5 variables (D_node, R_control, P_in, V_node, H_review) plus clamp() function are defined with name, symbol, type, range, and description; clamp bounds [0, 1] specified | `pending` |
| **Variable Source Mapping** | D_node ← Phase 74A node defense state (8-state model: stable/pressured/degraded/blocked/recovering/isolated/compromised/bypassed); R_control ← Phase 77A control recovery rules; P_in ← Phase 74A incoming propagation sum; V_node ← Phase 74A node vulnerability; H_review ← Phase 81A human_review_breakpoint weight | `pending` |
| **Graph Schema Alignment (74A)** | D_node uses 8-state model from Phase 74A dynamics schema; V_node values align with node-type vulnerability ranges; clamp [0,1] preserves D_node as probability-like measure | `pending` |
| **Dynamics Model Alignment (77A)** | R_control maps to 4 control recovery rules (control_restore, containment_initiate, credential_rotate, review_override); P_in × V_node matches attack propagation impact formula; D_node(t) → D_node(t+1) transition respects state machine constraints | `pending` |
| **Tabletop Report Alignment (79A/80A)** | D_node evolution for M43 (step2 degraded), M46 (step3 degraded), M48 (step4 degraded) matches observed timeline; M50 holds ≥ 0.7 across all paths; entry module degradation ordering (M43 < M46 < M48) reproduces observed pattern | `pending` |
| **Pattern Library Alignment (81A)** | H_review factor derives from HRG-BREAK-001 pattern; V_node values align with upstream_entry_vulnerability weight (W-ENTRY-VULN-001); per-module R_control availability maps to pattern lifecycle status | `pending` |
| **Safety Semantics Present** | conceptual_only: true, not_executable: true, not_production_risk: true, not_vulnerability_severity: true, not_exploitability_score: true, requires_human_review: true | `pending` |
| **Human Review Required** | All 7 dimensions above require human reviewer judgment; no automated pass/fail | `pending` |
| **Reviewer Notes** | | |

### 3.3 EQ-PATH-DEGRADATION-001: G_path

**Equation:** `G_path = Σ P_edge(t) × (1 + A_seq) - Σ A_attenuation + Σ A_amplification - Σ B_blocking`

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Variable Completeness** | All 5 components (P_edge, A_seq, A_attenuation, A_amplification, B_blocking) are defined with name, symbol, type, range, and description; summation notation explained | `pending` |
| **Variable Source Mapping** | P_edge(t) ← EQ-EDGE-PROPAGATION-001 output; A_seq ← Phase 74A sequence amplification effect; A_attenuation ← Phase 77A attenuation rules (5 types); A_amplification ← Phase 77A amplification rules (3 types); B_blocking ← Phase 77A boundary blocking rules (4 types) | `pending` |
| **Graph Schema Alignment (74A)** | Path structure aligns with Phase 74A cross-module path schema; edge sequence ordering respects layer ordering (supply → credential/rag → runtime); A_seq captures sequence-dependent amplification from path topology | `pending` |
| **Dynamics Model Alignment (77A)** | Σ A_attenuation sums per-module attenuation values (M50=4 rules > M47=3 rules > M49=2 rules); Σ A_amplification captures 3 amplification types (permission_leakage, credential_pressure, context_contamination); Σ B_blocking captures 4 boundary blocking types (sandbox_execution, credential, audit, network) | `pending` |
| **Tabletop Report Alignment (79A/80A)** | DEV-CRED G_path = -3.68 matches observed partial_degradation trajectory; RAG G_path = -3.136 matches observed partial_degradation trajectory; full-lifecycle G_path = -2.8625 matches longer path; all 3 paths classify as partial_degradation | `pending` |
| **Pattern Library Alignment (81A)** | A_attenuation values map to credential_boundary_attenuation (W-CRED-ATTEN-001) and m50_audit_damping (W-M50-AUDIT-DAMP-001); A_amplification values map to permission_leakage_amplification (W-PERM-AMPL-001) and upstream_entry_vulnerability (W-ENTRY-VULN-001); B_blocking values map to m50_sandbox_boundary (W-M50-SB-BLOCK-001) | `pending` |
| **Safety Semantics Present** | conceptual_only: true, not_executable: true, not_production_risk: true, not_vulnerability_severity: true, not_exploitability_score: true, requires_human_review: true | `pending` |
| **Human Review Required** | All 7 dimensions above require human reviewer judgment; no automated pass/fail | `pending` |
| **Reviewer Notes** | | |

## 4. Cross-Equation Consistency Review

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **P_edge → D_node Coupling** | P_edge(t) feeds as P_in(t) into D_node(t+1); higher P_edge → lower D_node(t+1); consistent variable naming across equations | `pending` |
| **P_edge → G_path Coupling** | P_edge(t) appears in G_path summation; aggregated edge propagation drives path-level degradation | `pending` |
| **D_node → P_edge Feedback** | D_target in P_edge equation = D_node(t) of target node; degraded target → higher P_edge (positive feedback); consistent with Phase 77A feedback loop model | `pending` |
| **Variable Name Consistency** | No duplicate variable names with different meanings; same symbol = same meaning across all 3 equations; all 10 core conceptual variables appear in at least one equation | `pending` |
| **Example Calculation Reproducibility** | Phase 82A example calculations (DEV-CRED: -3.68, RAG: -3.136, full-lifecycle: -2.8625) use consistent variable values; intermediate values are traceable; no arithmetic contradictions | `pending` |
| **Reviewer Notes** | | |

## 5. Document Metadata

```yaml
metadata:
  phase: "83A"
  document_type: "equation_consistency_review_checklist"
  conceptual_only: true
  executable: false
  human_review_required: true
  equations_reviewed: 3
  review_dimensions_per_equation: 8
  cross_equation_review_items: 5
  review_status: "pending"
```
