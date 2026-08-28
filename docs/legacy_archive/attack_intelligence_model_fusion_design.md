# Attack Intelligence Model Fusion Design

## 1. Purpose and Scope

This document defines how five prior phases (74A, 77A, 79A, 80A, 81A) are fused into the unified attack intelligence theory model. Each phase provides a distinct input layer, and the fusion design specifies how those layers interact within the unified model.

**Conceptual fusion only** — not an implementation, not automated integration.

## 2. Phase 74A: Attack Graph Structure

```yaml
phase_74a_input:
  phase: "74A"
  source_documents:
    - "docs/cross_module_attack_graph_schema.md"
    - "docs/risk_propagation_model.md"

  provided_elements:

    nodes:
      type: "module_node"
      modules: ["M43", "M46", "M47", "M48", "M49", "M50"]
      attributes_per_node:
        - "module_id"
        - "module_name"
        - "layer_id"
        - "primary_attack_objective"
      usage_in_unified_model: >
        Nodes become the entities whose defense states (D_node) evolve over time.
        Each node's layer and attack objective inform its vulnerability factor (V_node).

    edges:
      types:
        - "context_influence"
        - "trust_boundary_transfer"
        - "permission_dependency"
        - "evidence_dependency"
        - "audit_dependency"
        - "runtime_dependency"
        - "amplification_edge"
        - "mitigation_edge"
        - "review_gate_edge"
      attributes_per_edge:
        - "source_layer"
        - "target_layer"
        - "propagation_rule_type"
      usage_in_unified_model: >
        Edges become propagation channels with weight factors (W_edge). The edge type
        determines the baseline conductivity of the conceptual propagation channel.

    layers:
      layer_ids: ["supply_chain", "development_environment", "rag_data", "runtime_sandbox"]
      ordering: [1, 2, 3, 4]
      module_mapping:
        supply_chain: ["M43"]
        development_environment: ["M46", "M47"]
        rag_data: ["M48", "M49"]
        runtime_sandbox: ["M50"]
      usage_in_unified_model: >
        Layer boundaries introduce cross-layer amplification (AMPL-CROSS-001).
        Adjacent layer crossings add less amplification than skip-layer crossings.

    paths:
      path_ids:
        - "PATH-SUPPLY-DEV-001"
        - "PATH-DEV-CMD-001"
        - "PATH-RAG-PERMISSION-001"
        - "PATH-CRED-RUNTIME-AUDIT-001"
        - "PATH-RAG-RUNTIME-001"
        - "PATH-DEV-RUNTIME-001"
        - "PATH-SUPPLY-DEV-RUNTIME-001"
        - "PATH-SUPPLY-DEV-RAG-RUNTIME-001"
      usage_in_unified_model: >
        Paths define the ordered module sequences over which G_path (path-level degradation)
        is computed. Each path is a test case for the unified model's consistency.

  mapping_to_unified_model_variables:
    - graph_element: "Node"
      unified_variable: "D_node(t), V_node, R_control"
    - graph_element: "Edge"
      unified_variable: "W_edge, P_edge(t)"
    - graph_element: "Layer"
      unified_variable: "A_seq (cross_layer_amplification)"
    - graph_element: "Path"
      unified_variable: "G_path"
    - graph_element: "Node.layer_id"
      unified_variable: "V_node.default_by_module"
```

## 3. Phase 77A: Dynamics Evolution Rules

```yaml
phase_77a_input:
  phase: "77A"
  source_documents:
    - "docs/attack_graph_dynamics_model.md"
    - "docs/node_defense_state_evolution_model.md"
    - "docs/attack_graph_feedback_loop_model.md"

  provided_elements:

    propagation_probability_factors:
      factors:
        - "edge_type_influence"
        - "source_defense_state"
        - "layer_boundary_crossing"
        - "attenuation_availability"
      usage_in_unified_model: >
        These factors define how W_edge varies by context. Edge_type_influence
        provides the baseline; source_defense_state and layer_boundary_crossing
        provide situational modifiers.

    attenuation_rules:
      rules:
        - "ATTEN-HRG-001 (human_review_gate)"
        - "ATTEN-BND-001 (boundary_preservation)"
        - "ATTEN-RED-001 (redaction)"
        - "ATTEN-AUD-001 (audit_chain)"
        - "ATTEN-RPL-001 (controlled_replay_gate)"
      usage_in_unified_model: >
        Attenuation rules contribute to Σ A_attenuation in the G_path equation.
        Each rule has a conceptual weight based on its effect
        (blocking > significant_reduction > moderate_reduction).

    amplification_rules:
      rules:
        - "AMPL-SEQ-001 (sequential_boundary_weakening)"
        - "AMPL-CROSS-001 (cross_layer_amplification)"
        - "AMPL-FEED-001 (feedback_loop_amplification)"
      usage_in_unified_model: >
        Amplification rules contribute to Σ A_amplification in G_path and to
        the A_seq term. Each rule has a conceptual weight based on the
        number of weak boundaries or layer crossings.

    boundary_blocking_rules:
      rules:
        - "BLOCK-CMD-001 (command_boundary)"
        - "BLOCK-PERM-001 (permission_boundary)"
        - "BLOCK-SB-001 (sandbox_boundary)"
        - "BLOCK-RPL-001 (controlled_replay_gate)"
      usage_in_unified_model: >
        Boundary blocking contributes to Σ B_blocking in G_path. Each block
        event subtracts from net path degradation.

    control_recovery_rules:
      rules:
        - "REC-HRG-001 (human_review_recovery)"
        - "REC-AUD-001 (audit_chain_restoration)"
        - "REC-BND-001 (boundary_recovery)"
        - "REC-TIME-001 (time_based_attenuation)"
      usage_in_unified_model: >
        Recovery rules contribute to R_control in the D_node equation. They
        provide positive restoration force when activated.

    node_defense_states:
      states: ["stable", "pressured", "degraded", "partially_blocked", "blocked", "recovered", "inconclusive", "human_review_required"]
      usage_in_unified_model: >
        The 8-state model maps to D_node value ranges. This mapping enables
        translating tabletop observations (state labels) into conceptual
        equation variables.

    feedback_loops:
      loops:
        - "audit_gap_feedback_loop"
        - "permission_leakage_feedback_loop"
        - "credential_pressure_feedback_loop"
        - "runtime_control_feedback_loop"
      usage_in_unified_model: >
        Feedback loops determine F_feedback sign and magnitude. Active negative
        feedback (runtime_control) produces F_feedback < 0. Potential positive
        feedback (permission_leakage, credential_pressure) can produce F_feedback > 0.

    time_step_model:
      step_types:
        - "attack_step"
        - "defense_response_step"
        - "recovery_step"
        - "feedback_step"
      usage_in_unified_model: >
        Time steps provide the temporal dimension (t) for all equations.
        Each time step in the conceptual model corresponds to one logical
        step in the attack/defense sequence.

  mapping_to_unified_model_variables:
    - dynamics_element: "Propagation probability"
      unified_variable: "Base for W_edge assignment"
    - dynamics_element: "Attenuation rules"
      unified_variable: "Σ A_attenuation (G_path)"
    - dynamics_element: "Amplification rules"
      unified_variable: "A_seq, Σ A_amplification (G_path)"
    - dynamics_element: "Boundary blocking rules"
      unified_variable: "Σ B_blocking (G_path)"
    - dynamics_element: "Control recovery rules"
      unified_variable: "R_control (D_node equation)"
    - dynamics_element: "Node defense states"
      unified_variable: "D_node range mapping"
    - dynamics_element: "Feedback loops"
      unified_variable: "F_feedback (P_edge equation)"
    - dynamics_element: "Time step model"
      unified_variable: "t parameter in all equations"
```

## 4. Phase 79A: Full-Lifecycle Tabletop Observation

```yaml
phase_79a_input:
  phase: "79A"
  source_documents:
    - "reports/phase79a_path_supply_dev_rag_runtime_tabletop_analysis.md"
    - "reports/phase79a_defense_degradation_trajectory_report.md"
    - "reports/phase79a_attack_evolution_trajectory_report.md"

  provided_elements:

    node_state_timeline:
      path: "PATH-SUPPLY-DEV-RAG-RUNTIME-001"
      steps: 5
      observed_transitions:
        - "M43: stable → pressured → degraded (step 2)"
        - "M46: stable → pressured → degraded (step 3)"
        - "M48: stable → pressured → degraded (step 4)"
        - "M49: stable → pressured → pressured (held, step 1-5)"
        - "M50: stable → pressured → pressured (held, step 4-5)"
      usage_in_unified_model: >
        Provides observed D_node transitions for the longest path. M43 degrades
        first (step 2), M46 second (step 3), M48 third (step 4). M49 and M50 hold.
        This pattern validates V_node ordering: M43 > M46 > M48 > M49 ≈ M50.

    edge_propagation_timeline:
      observed_propagations:
        - "M43 → M46: probable (context_influence, adjacent_layer)"
        - "M46 → M48: medium (context_influence, adjacent_layer)"
        - "M48 → M49: medium_to_high (permission_dependency, same_layer)"
        - "M49 → M50: medium (runtime_dependency, adjacent_layer)"
      usage_in_unified_model: >
        Provides observed P_edge calibration. Same-layer propagation (M48→M49)
        has highest probability hint. Cross-layer edges have medium probability.
        This validates W_edge ordering: permission_dependency > context_influence ≈ runtime_dependency.

    attenuation_application:
      observed_attenuation:
        - "M46: ATTEN-HRG-001 only"
        - "M48: ATTEN-HRG-001 + safe_summary content protection"
        - "M49: ATTEN-HRG-001 + ATTEN-BND-001"
        - "M50: ATTEN-HRG-001 + ATTEN-BND-001 + ATTEN-AUD-001 + ATTEN-RPL-001"
      usage_in_unified_model: >
        Provides observed Σ A_attenuation for each module. M50 has the strongest
        attenuation (4 rules). M46 has the weakest among non-M43 modules (1 rule).
        This validates A_attenuation assignments.

    amplification_application:
      observed_amplification:
        - "AMPL-SEQ-001: moderate (2 consecutive weak boundaries: M43-M46, M46-M48)"
        - "AMPL-CROSS-001: moderate (4 layer crossings)"
        - "AMPL-FEED-001: feedback_dependent (runtime_control negative active)"
      usage_in_unified_model: >
        Provides observed Σ A_amplification. The 4-layer path has moderate
        cross-layer amplification. Sequential amplification is moderate due to
        multiple weak-entry boundaries.

    feedback_loop_evaluation:
      observed_loops:
        - "runtime_control_feedback_loop: active_negative_feedback (moderate strength)"
        - "permission_leakage_feedback_loop: potential (not triggered)"
        - "audit_gap_feedback_loop: not_triggered"
        - "credential_pressure_feedback_loop: not_applicable (no M47 in path)"
      usage_in_unified_model: >
        Provides observed F_feedback values. runtime_control produces negative
        feedback (F_feedback < 0). permission_leakage and audit_gap are
        condition-dependent.

    trajectory_level:
      observed: "partial_degradation"
      usage_in_unified_model: >
        Maps to G_path in the moderate range (0.4-0.7). Provides a reference
        point for interpreting G_path values.

  mapping_to_unified_model_variables:
    - tabletop_element: "Node state timeline"
      unified_variable: "D_node(t) progression patterns"
    - tabletop_element: "Edge propagation timeline"
      unified_variable: "P_edge conceptual validation"
    - tabletop_element: "Attenuation application"
      unified_variable: "Σ A_attenuation calibration"
    - tabletop_element: "Amplification application"
      unified_variable: "A_seq, Σ A_amplification calibration"
    - tabletop_element: "Feedback loop evaluation"
      unified_variable: "F_feedback sign and magnitude"
    - tabletop_element: "Trajectory level"
      unified_variable: "G_path range mapping"
```

## 5. Phase 80A: Multi-Path Tabletop Comparison

```yaml
phase_80a_input:
  phase: "80A"
  source_documents:
    - "reports/phase80a_path_dev_cred_runtime_tabletop_analysis.md"
    - "reports/phase80a_path_rag_runtime_tabletop_analysis.md"
    - "reports/phase80a_multi_path_defense_degradation_comparison.md"
    - "reports/phase80a_path_dev_cred_runtime_defense_degradation_trajectory_report.md"
    - "reports/phase80a_path_rag_runtime_defense_degradation_trajectory_report.md"

  provided_elements:

    dev_cred_path_observations:
      path: "PATH-DEV-CRED-RUNTIME-001"
      modules: ["M46", "M47", "M50"]
      node_state_timeline:
        - "M46: degraded (step 2)"
        - "M47: pressured (held, 3 attenuation rules)"
        - "M50: pressured (held, 4 attenuation rules)"
      attenuation_at_M47:
        rules: 3
        rules_list: ["ATTEN-HRG-001", "ATTEN-BND-001", "ATTEN-RED-001"]
        assessment: "strong attenuation node"
      usage_in_unified_model: >
        Validates M47 as the strongest intermediate attenuation node.
        M47 V_node=0.4 is appropriate (3 rules absorb pressure).
        M46 degrades fast (step 2) — consistent with V_node=0.7.

    rag_path_observations:
      path: "PATH-RAG-RUNTIME-001"
      modules: ["M48", "M49", "M50"]
      node_state_timeline:
        - "M48: degraded (step 3) — slower than M46"
        - "M49: pressured (held, 2 attenuation rules)"
        - "M50: pressured (held, 4 attenuation rules)"
      attenuation_at_M49:
        rules: 2
        rules_list: ["ATTEN-HRG-001", "ATTEN-BND-001"]
        assessment: "moderate_to_strong attenuation node"
      usage_in_unified_model: >
        Validates M48 degrades slower than M46 (safe_summary protection).
        M49 with 2 rules is weaker than M47 with 3 — consistent with
        V_node=0.5 for M49 vs V_node=0.4 for M47.

    cross_path_comparison:
      comparison_dimensions: 12
      key_differences:
        - "M46 degrades faster than M48 (no safe_summary equivalent)"
        - "M47 (3 rules) is stronger than M49 (2 rules)"
        - "DEV-CRED emphasizes M50 audit role; RAG emphasizes M50 sandbox role"
        - "RAG path has more uniform evidence format (all boolean)"
      usage_in_unified_model: >
        Enables cross-path calibration. The unified model must produce
        different G_path profiles for each path while maintaining
        consistent variable definitions.

    m50_role_comparison:
      dev_cred_role: "Audit chain confirmation for M47 credential decisions"
      rag_role: "Sandbox boundary enforcer and audit chain for M49 permission decisions"
      usage_in_unified_model: >
        Informs the M50 damping coefficient's dual nature. The coefficient
        is the same value (0.8) but applies differently: more on A_attenuation
        (audit) for dev-cred, more on B_blocking (sandbox) for RAG.

  mapping_to_unified_model_variables:
    - tabletop_element: "M46 vs M48 degradation speed"
      unified_variable: "V_node difference: M46=0.7, M48=0.5"
    - tabletop_element: "M47 vs M49 attenuation comparison"
      unified_variable: "Σ A_attenuation: M47=3 rules, M49=2 rules"
    - tabletop_element: "M50 role comparison"
      unified_variable: "M50 damping coefficient (0.8) with dual role"
    - tabletop_element: "Cross-path trajectory comparison"
      unified_variable: "G_path differentiation: both partial_degradation but different patterns"
    - tabletop_element: "Evidence format comparison"
      unified_variable: "Not directly in equations, but affects human review confidence"
```

## 6. Phase 81A: Pattern Library Weights

```yaml
phase_81a_input:
  phase: "81A"
  source_documents:
    - "reports/phase81a_cross_module_attack_pattern_library.md"
    - "docs/cross_module_attack_pattern_index.md"
    - "docs/cross_module_path_pattern_association_matrix.md"
    - "docs/cross_module_module_pattern_association_matrix.md"

  provided_elements:

    upstream_entry_degradation_pattern:
      pattern_id: "PATTERN-UPSTREAM-ENTRY-DEGRADATION-001"
      lifecycle_status: "confirmed_across_3_paths"
      observed_modules: ["M43", "M46", "M48"]
      usage_in_unified_model: >
        Directly informs V_node values for entry modules. The pattern
        confirms that entry modules degrade first, with M43 fastest
        (no attenuation) and M48 slowest (safe_summary).

    m50_audit_confirmation_pattern:
      pattern_id: "PATTERN-M50-AUDIT-CONFIRMATION-001"
      lifecycle_status: "confirmed_across_3_paths"
      observed_modules: ["M50"]
      usage_in_unified_model: >
        Informs M50's audit-related A_attenuation contribution.
        Confirms M50's audit chain role across all paths.

    m50_sandbox_execution_boundary_pattern:
      pattern_id: "PATTERN-M50-SANDBOX-BOUNDARY-001"
      lifecycle_status: "confirmed_across_2_paths"
      observed_modules: ["M50"]
      usage_in_unified_model: >
        Informs M50's sandbox-related B_blocking contribution.
        Confirms M50's sandbox boundary role in RAG-involved paths.

    credential_boundary_attenuation_pattern:
      pattern_id: "PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001"
      lifecycle_status: "observed_in_1_path"
      observed_modules: ["M47"]
      usage_in_unified_model: >
        Informs M47's A_attenuation contribution. The pattern confirms
        M47's 3 attenuation rules make it the strongest intermediate node.

    permission_leakage_amplification_pattern:
      pattern_id: "PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001"
      lifecycle_status: "observed_in_2_paths"
      observed_modules: ["M48", "M49"]
      usage_in_unified_model: >
        Informs A_amplification for M48-M49 segments. The dual-boundary
        failure mechanism increases amplification risk.

    human_review_breakpoint_pattern:
      pattern_id: "PATTERN-HUMAN-REVIEW-BREAKPOINT-001"
      lifecycle_status: "confirmed_across_3_paths"
      observed_modules: ["M46", "M47", "M48", "M49", "M50"]
      usage_in_unified_model: >
        Informs H_review compensation factor. Modules with human review gate
        can receive H_review > 0. M43 has no human review gate.

    path_pattern_association_matrix:
      provided_data:
        - "PATH-SUPPLY-DEV-RAG-RUNTIME-001: 7 patterns"
        - "PATH-DEV-CRED-RUNTIME-001: 5 patterns"
        - "PATH-RAG-RUNTIME-001: 6 patterns"
      usage_in_unified_model: >
        Determines which A_pattern values apply to which path segments.
        A_pattern aggregates the weights of all patterns applicable to a given edge.

    module_pattern_association_matrix:
      provided_data:
        - "M50: 5 patterns (most covered)"
        - "M48: 4 patterns"
        - "M46/M47/M49: 3 patterns each"
        - "M43: 1 pattern (least covered)"
      usage_in_unified_model: >
        Determines A_pattern weight aggregation per module. More patterns
        per module means more weight factors potentially affecting that module's behavior.
        M43's single pattern reflects its uniquely weak attenuation profile.

  mapping_to_unified_model_variables:
    - pattern_element: "Upstream entry degradation pattern"
      unified_variable: "V_node defaults (M43=0.9, M46=0.7, M48=0.5)"
    - pattern_element: "M50 audit confirmation pattern"
      unified_variable: "M50 damping coefficient, A_attenuation"
    - pattern_element: "M50 sandbox boundary pattern"
      unified_variable: "M50 B_blocking contribution"
    - pattern_element: "Credential boundary attenuation pattern"
      unified_variable: "M47 A_attenuation weight"
    - pattern_element: "Permission leakage amplification pattern"
      unified_variable: "M48-M49 A_amplification weight"
    - pattern_element: "Human review breakpoint pattern"
      unified_variable: "H_review compensation factor"
    - pattern_element: "Path-pattern matrix"
      unified_variable: "A_pattern aggregation per path"
    - pattern_element: "Module-pattern matrix"
      unified_variable: "Per-module A_pattern components"
```

## 7. Fusion Architecture Diagram

```text
Phase 74A (Graph)          Phase 77A (Dynamics)
      |                          |
      v                          v
  Nodes + Edges             Evolution Rules
  + Layers                  + Feedback Loops
  + Paths                   + Time Steps
      |                          |
      +--------------------------+
                 |
                 v
     Unified Theory Model
     Core Variables + Equations
                 |
      +----------+-----------+
      |                      |
      v                      v
Phase 79A/80A           Phase 81A
(Calibration)           (Weights)
      |                      |
      v                      v
  Node State             Pattern Weights
  Timelines              + Association
  + Trajectories         Matrices
  + Comparisons               |
      |                      |
      +----------+-----------+
                 |
                 v
     Calibrated Conceptual Model
     (Human Review Required)
```

## 8. Fusion Safety Semantics

```yaml
fusion_safety_semantics:
  conceptual_only: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true

  fusion_boundary:
    - "Phase 74A graph elements remain conceptual_only — no executable paths"
    - "Phase 77A dynamics rules remain conceptual_only — no executable simulation"
    - "Phase 79A/80A tabletop observations remain conceptual_only — no confirmed vulnerabilities"
    - "Phase 81A pattern library remains conceptual_only — no detection rules"
    - "The fusion of these layers does not change their individual conceptual_only status"
    - "Fused model output is human-review-candidate only"

  per_phase_preservation:
    phase_74A: "graph schema still conceptual_only=true"
    phase_77A: "dynamics model still conceptual_only=true"
    phase_79A: "tabletop reports still conceptual_only=true, not_confirmed_vulnerability=true"
    phase_80A: "tabletop comparisons still conceptual_only=true"
    phase_81A: "pattern library still tabletop_pattern=true, conceptual_only=true"
```

## 9. Document Metadata

```yaml
metadata:
  phase: "82A"
  document_type: "attack_intelligence_model_fusion_design"
  conceptual_only: true
  executable: false
  fused_phases:
    - "74A (attack graph structure)"
    - "77A (dynamics evolution rules)"
    - "79A (full-lifecycle tabletop)"
    - "80A (multi-path comparison)"
    - "81A (pattern library weights)"
  total_fusion_mappings: 5
  human_review_required: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
```
