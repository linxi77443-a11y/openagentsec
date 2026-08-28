# Unified Attack Intelligence Theory Model — Design Gate

## 1. Purpose and Scope

This document defines a unified conceptual theory model that fuses four prior design gates and two tabletop exercise phases into a single theoretical framework for cross-module attack intelligence:

- **Phase 74A** — Cross-Module Attack Graph Schema & Risk Propagation Model (structural foundation)
- **Phase 77A** — Attack Graph Dynamics Simulation Layer (evolution rules)
- **Phase 79A / 80A** — Tabletop Exercise Phases (observation samples)
- **Phase 81A** — Cross-Module Attack Pattern Library (reusable pattern weights)

The unified model provides:
1. A formalized conceptual language (variables, equations, parameters) for describing attack signal propagation
2. A theoretical basis for interpreting tabletop exercise observations as model calibration samples
3. A framework for integrating pattern-level weights into path-level propagation analysis
4. A human-review-gated structure that prevents misinterpretation as production risk or vulnerability assessment

**This is a theory model design gate only** — not an implementation, not a simulator, not an automated detection system. All equations, parameters, and weights are conceptual and must not be interpreted as real attack probabilities, production risk scores, vulnerability severity ratings, or formal findings.

## 2. Theory Model Boundary

```yaml
theory_model_boundary:
  theory_model_design_gate_only: true
  unified_model_blueprint_only: true
  conceptual_equations_only: true
  executable: false
  attack_execution_allowed: false
  controlled_replay_execution_allowed: false
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true

  model_scope:
    - "Conceptual propagation dynamics across module and layer boundaries"
    - "Defense state evolution under sustained attack pressure"
    - "Pattern-weighted amplification and attenuation"
    - "M50 audit confirmation and sandbox boundary damping"
    - "Human review gate as universal breakpoint"

  model_boundary_limitations:
    - "Does NOT predict real attack outcomes"
    - "Does NOT assign vulnerability severity"
    - "Does NOT compute production risk scores"
    - "Does NOT generate executable attack chains"
    - "Does NOT implement automated detection"
    - "Does NOT replace human review"
```

## 3. Source Artifacts

```yaml
source_artifacts:
  phase_74a:
    documents:
      - "docs/cross_module_attack_graph_schema.md"
      - "docs/risk_propagation_model.md"
    provides:
      - "7 node types, 9 edge types, 4 layers"
      - "7 propagation rule types"
      - "Module-to-layer mapping (M43-M50)"
      - "Cross-module edge taxonomy"
    usage_in_unified_model: "Structural skeleton — defines the graph topology upon which dynamics and patterns operate"

  phase_77a:
    documents:
      - "docs/attack_graph_dynamics_model.md"
      - "docs/node_defense_state_evolution_model.md"
      - "docs/attack_graph_feedback_loop_model.md"
    provides:
      - "5 attenuation rules, 3 amplification rules"
      - "4 boundary blocking rules, 4 control recovery rules"
      - "8 node defense states"
      - "4 feedback loops"
      - "Time step / attack step conceptual model"
    usage_in_unified_model: "Evolution engine — defines how node states change and how signals propagate across time steps"

  phase_79a:
    documents:
      - "reports/phase79a_path_supply_dev_rag_runtime_tabletop_analysis.md"
      - "reports/phase79a_defense_degradation_trajectory_report.md"
      - "reports/phase79a_attack_evolution_trajectory_report.md"
    provides:
      - "First 5-module, 4-layer tabletop exercise data"
      - "Node state timeline (5 steps)"
      - "Edge propagation timeline (4 edges)"
      - "Attenuation/amplification application observations"
      - "Feedback loop evaluation"
      - "Evidence reference map"
    usage_in_unified_model: "Calibration sample — provides empirical observation of the full-lifecycle path dynamics"

  phase_80a:
    documents:
      - "reports/phase80a_path_dev_cred_runtime_tabletop_analysis.md"
      - "reports/phase80a_path_rag_runtime_tabletop_analysis.md"
      - "reports/phase80a_multi_path_defense_degradation_comparison.md"
      - "reports/phase80a_path_dev_cred_runtime_defense_degradation_trajectory_report.md"
      - "reports/phase80a_path_rag_runtime_defense_degradation_trajectory_report.md"
    provides:
      - "Two shorter path tabletop exercises (3 modules each)"
      - "Cross-path comparison: DEV-CRED vs RAG degradation patterns"
      - "M47 (3 attenuation rules) vs M49 (2 rules) comparison"
      - "M46 vs M48 entry degradation speed comparison"
      - "M50 role comparison across paths"
    usage_in_unified_model: "Comparative calibration — enables cross-path model consistency checks"

  phase_81a:
    documents:
      - "reports/phase81a_cross_module_attack_pattern_library.md"
      - "docs/cross_module_attack_pattern_index.md"
      - "docs/cross_module_path_pattern_association_matrix.md"
      - "docs/cross_module_module_pattern_association_matrix.md"
    provides:
      - "8 reusable attack patterns with lifecycle status"
      - "Path-pattern and module-pattern association matrices"
      - "Pattern-specific attenuation/amplification insights"
    usage_in_unified_model: "Weight source — patterns provide conceptual weight factors for the equations"
```

## 4. Unified Model Architecture

The unified model has four conceptual layers:

```yaml
unified_model_architecture:
  layer_1_graph_structure:
    source: "Phase 74A"
    components:
      - "Nodes (modules)"
      - "Edges (cross-module relationships)"
      - "Paths (ordered node sequences)"
      - "Layers (system layers with ordering)"
    role: "Provide the structural skeleton — defines what exists and how elements connect"

  layer_2_dynamics_evolution:
    source: "Phase 77A"
    components:
      - "Propagation probability factors"
      - "Attenuation / amplification / blocking / recovery rules"
      - "Node defense state definitions and transitions"
      - "Feedback loop mechanisms"
      - "Time step progression model"
    role: "Provide the evolution rules — defines how states change over conceptual time steps"

  layer_3_tabletop_observations:
    source: "Phase 79A / 80A"
    components:
      - "Node state timelines"
      - "Edge propagation timelines"
      - "Defense degradation trajectories"
      - "Attack evolution trajectories"
      - "Evidence reference maps"
      - "Cross-path comparisons"
    role: "Provide calibration samples — observed state transitions used to refine model parameters"

  layer_4_pattern_weights:
    source: "Phase 81A"
    components:
      - "8 attack patterns with lifecycle status"
      - "Pattern-to-path mapping"
      - "Pattern-to-module mapping"
    role: "Provide weight factors — reusable pattern insights as conceptual equation coefficients"
```

The four layers interact as follows:

```text
Layer 1 (Graph)     defines the topology
       ↓
Layer 2 (Dynamics)  defines how signals move across the topology
       ↓
Layer 3 (Tabletop)  provides observed samples of the dynamics in action
       ↓
Layer 4 (Patterns)  provides reusable weights derived from observed samples
       ↓
Back to Layer 2     weights refine dynamics parameters for future analysis
```

This is a **conceptual feedback loop** in the model architecture itself: patterns observed in tabletop exercises feed back into refined understanding of propagation dynamics.

## 5. Graph-Dynamics-Tabletop-Pattern Fusion

```yaml
graph_dynamics_tabletop_pattern_fusion:
  conceptual_only: true
  requires_human_review: true

  fusion_mapping:
    - graph_element: "Node (module_node)"
      dynamics_element: "Node defense state (8 states)"
      tabletop_element: "Per-module node state in timeline"
      pattern_element: "Module-pattern association (which patterns apply to this module)"
      fusion_description: "A node in the graph carries a defense state that evolves via dynamics. Tabletop exercises observe this evolution. Patterns provide context-dependent weight adjustments."

    - graph_element: "Edge (context_influence, permission_dependency, etc.)"
      dynamics_element: "Propagation probability, edge type influence factor"
      tabletop_element: "Edge propagation timeline observation"
      pattern_element: "Pattern-related amplification/attenuation factors"
      fusion_description: "An edge in the graph has a conceptual propagation channel defined by dynamics. Tabletop exercises observe whether propagation occurred. Patterns adjust the channel's effective weight."

    - graph_element: "Path (ordered module sequence)"
      dynamics_element: "Sequential propagation, cumulative amplification"
      tabletop_element: "Path-level degradation trajectory"
      pattern_element: "Path-pattern association matrix entries"
      fusion_description: "A path is a sequence of nodes and edges. Dynamics define how pressure accumulates along the sequence. Tabletop exercises observe the net trajectory. Patterns provide segment-level weight adjustments."

    - graph_element: "Layer boundary"
      dynamics_element: "Cross-layer amplification (AMPL-CROSS-001)"
      tabletop_element: "Layer crossing observations in node state timeline"
      pattern_element: "Pattern layer coverage (which layers a pattern spans)"
      fusion_description: "Layer boundaries introduce cross-layer amplification. Tabletop exercises observe whether layer crossings increase propagation likelihood. Patterns identify which layer-crossing structures recur."

  fusion_feedback_cycle:
    - step: 1
      action: "Graph structure defines possible paths"
    - step: 2
      action: "Dynamics rules define expected behavior along paths"
    - step: 3
      action: "Tabletop exercises produce observed behavior samples"
    - step: 4
      action: "Pattern library abstracts recurring observed behaviors into weights"
    - step: 5
      action: "Weights refine dynamics parameters for next iteration"
    - step: 6
      action: "Human review gates every step of the cycle"
```

## 6. Core Conceptual Variables

```yaml
core_conceptual_variables:
  conceptual_only: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  requires_human_review: true

  variables:
    - variable: "S_source(t)"
      conceptual_meaning: "Attack signal strength at the source node at time step t"
      conceptual_range: "[0, 1] as a conceptual modeling scale only"
      source_reference: "Phase 77A propagation probability concept, Phase 79A/80A node state observations"
      initial_default: "0.0 (no pressure) at t=0"
      not_production_risk: true
      human_review_required: true

    - variable: "D_node(t)"
      conceptual_meaning: "Defense state strength of a node at time step t"
      conceptual_range: "[0, 1] where 1 = fully stable, 0 = fully degraded"
      source_reference: "Phase 77A 8-state defense model, Phase 79A/80A node state timelines"
      initial_default: "1.0 (stable) at t=0"
      not_production_risk: true
      human_review_required: true

    - variable: "P_edge(t)"
      conceptual_meaning: "Conceptual propagation pressure on an edge at time step t"
      conceptual_range: "[0, 1] as a conceptual modeling aid"
      source_reference: "Phase 74A edge type definitions, Phase 77A propagation probability factors"
      initial_default: "0.0 at t=0"
      not_production_risk: true
      human_review_required: true

    - variable: "W_edge"
      conceptual_meaning: "Edge-type weight factor indicating conceptual propagation conductivity"
      conceptual_range: "{low, medium, high} or [0.0, 1.0]"
      source_reference: "Phase 74A edge taxonomy, Phase 77A qualitative propagation scale"
      default_by_type:
        context_influence: "medium"
        permission_dependency: "medium_to_high"
        audit_dependency: "low_to_medium"
        runtime_dependency: "medium"
      not_production_risk: true
      human_review_required: true

    - variable: "A_pattern"
      conceptual_meaning: "Pattern-based amplification/attenuation modifier derived from Phase 81A pattern library"
      conceptual_range: "[0.0, 2.0] where <1 = attenuating, >1 = amplifying, 1 = neutral"
      source_reference: "Phase 81A pattern library, path-pattern association matrix"
      not_production_risk: true
      human_review_required: true

    - variable: "F_feedback"
      conceptual_meaning: "Feedback loop factor reflecting downstream-to-upstream influence"
      conceptual_range: "[-1.0, 1.0] where negative = attenuating feedback, positive = amplifying feedback"
      source_reference: "Phase 77A feedback loop model (4 loops)"
      not_production_risk: true
      human_review_required: true

    - variable: "R_control"
      conceptual_meaning: "Control recovery / boundary blocking factor"
      conceptual_range: "[0.0, 1.0] where higher = stronger recovery or blocking"
      source_reference: "Phase 77A boundary blocking rules, control recovery rules"
      not_production_risk: true
      human_review_required: true

    - variable: "V_node"
      conceptual_meaning: "Node vulnerability or pressure sensitivity factor"
      conceptual_range: "[0.0, 1.0] where higher = more sensitive to pressure"
      source_reference: "Phase 81A upstream_entry_degradation_pattern, module-pattern matrix"
      default_by_module:
        M43: "0.9 (most vulnerable — no attenuation)"
        M46: "0.7 (moderately vulnerable — HRG only)"
        M48: "0.5 (less vulnerable — HRG + safe_summary)"
        M47: "0.4 (resilient — 3 attenuation rules)"
        M49: "0.5 (moderately resilient — 2 rules)"
        M50: "0.2 (most resilient — 4 rules)"
      not_production_risk: true
      human_review_required: true

    - variable: "H_review"
      conceptual_meaning: "Human review gate compensation factor"
      conceptual_range: "[0.0, 0.5] where higher = stronger compensation"
      source_reference: "Phase 77A human review gate, Phase 81A human_review_breakpoint_pattern"
      default: "0.3 (conceptual moderate compensation)"
      not_production_risk: true
      human_review_required: true

    - variable: "G_path"
      conceptual_meaning: "Path-level conceptual defense degradation intensity"
      conceptual_range: "Conceptual ordinal: stable < pressured < degraded < blocked"
      source_reference: "Phase 79A/80A trajectory_level observations (partial_degradation)"
      not_production_risk: true
      human_review_required: true
```

## 7. Attack Propagation Equation

```yaml
attack_propagation_equation:
  conceptual_only: true
  not_executable: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  requires_human_review: true

  equation_form: |
    P_edge(t) = S_source(t) × W_edge × A_pattern × F_feedback × (1 - D_target)

  equation_description: >
    This conceptual equation describes the propagation pressure on a single edge
    at a given time step. The pressure is a function of source signal strength,
    edge conductivity, pattern-based modifiers, feedback effects, and target
    defense strength. Higher P_edge indicates stronger conceptual propagation
    pressure. When D_target approaches 1 (fully stable), the (1 - D_target)
    term approaches 0, significantly attenuating propagation.

  variable_explanations:
    - variable: "P_edge(t)"
      meaning: "Conceptual propagation pressure on the edge at time step t"
      interpretation: "Higher values indicate stronger conceptual likelihood of signal propagation"

    - variable: "S_source(t)"
      meaning: "Attack signal strength at the source node at time step t"
      interpretation: "Derived from the source module's defense state — degraded modules produce stronger signals"
      proxy_from_tabletop: "When D_source < 0.5 (degraded), S_source increases proportionally"

    - variable: "W_edge"
      meaning: "Edge-type weight factor"
      interpretation: "Constant for the edge type — reflects how conductive the relationship is"

    - variable: "A_pattern"
      meaning: "Pattern-based amplification/attenuation modifier"
      interpretation: "Aggregated from applicable Phase 81A patterns for this path segment"

    - variable: "F_feedback"
      meaning: "Feedback loop factor"
      interpretation: "Negative feedback (from M50 strong state) reduces P_edge; positive feedback (from degraded downstream) increases it"

    - variable: "D_target"
      meaning: "Target node defense state strength"
      interpretation: "Stronger defense at the target node reduces propagation pressure — this is the primary attenuation mechanism"

  example_application:
    path_segment: "M46 → M47 (context_influence)"
    conceptual_values:
      S_source(t=1): "0.3 (M46 just pressured, not yet degraded)"
      W_edge: "medium (~0.6 on [0,1] scale)"
      A_pattern: "credential_boundary_attenuation_weight (~0.5 — attenuating)"
      F_feedback: "-0.2 (runtime_control negative feedback from M50)"
      D_target: "0.8 (M47 with 3 attenuation rules, relatively strong)"
    conceptual_result:
      P_edge: "0.3 × 0.6 × 0.5 × 0.8 × (1 - 0.8) = 0.0144"
      interpretation: "Low propagation pressure — M47's strong attenuation and M50 feedback effectively suppress the signal"

  boundary_conditions:
    - "P_edge = 0 when S_source = 0 (no signal to propagate)"
    - "P_edge → 0 when D_target → 1 (target fully stable blocks propagation)"
    - "P_edge is amplified when A_pattern > 1 (amplifying patterns active)"
    - "P_edge is attenuated when F_feedback < 0 (negative feedback active)"
```

## 8. Node Defense State Equation

```yaml
node_defense_state_equation:
  conceptual_only: true
  not_executable: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  requires_human_review: true

  equation_form: |
    D_node(t+1) = clamp(D_node(t) + R_control - P_in(t) × V_node + H_review)

  equation_description: >
    This conceptual equation describes how a node's defense state evolves from one
    time step to the next. The defense state changes based on: control recovery
    (positive), incoming propagation pressure weighted by node vulnerability
    (negative), and human review gate compensation (positive). The clamp
    function conceptually bounds D_node to [0, 1].

  variable_explanations:
    - variable: "D_node(t+1)"
      meaning: "Defense state strength at the next time step"
      interpretation: "1.0 = fully stable, 0.0 = fully degraded"

    - variable: "D_node(t)"
      meaning: "Defense state strength at current time step"
      interpretation: "Starting point for the state transition"

    - variable: "R_control"
      meaning: "Control recovery / boundary blocking factor"
      interpretation: "Positive value represents boundary enforcement or recovery mechanisms activating"
      values_by_scenario:
        boundary_blocked: "0.3 (boundary successfully blocks propagation)"
        recovery_activated: "0.2 (control recovery mechanism engaged)"
        no_control: "0.0 (no recovery or blocking)"

    - variable: "P_in(t)"
      meaning: "Incoming propagation pressure (aggregated from all inbound edges)"
      interpretation: "Sum of P_edge values from all upstream edges targeting this node"

    - variable: "V_node"
      meaning: "Node vulnerability/pressure sensitivity factor"
      interpretation: "Higher values make the node more sensitive to incoming pressure"

    - variable: "H_review"
      meaning: "Human review gate compensation"
      interpretation: "Applied when human review gate is available and conceptually activated"

  clamp_behavior:
    - condition: "D_node(t+1) > 1.0"
      result: "D_node(t+1) = 1.0 (fully stable — defense cannot exceed maximum)"
    - condition: "D_node(t+1) < 0.0"
      result: "D_node(t+1) = 0.0 (fully degraded — defense cannot go below zero)"

  example_application:
    node: "M46 (development_environment)"
    conceptual_values_at_t=1:
      D_node(t=1): "0.7 (transitioning from stable to pressured)"
      R_control: "0.0 (no immediate control recovery)"
      P_in(t=1): "0.3 (propagation pressure from M43)"
      V_node: "0.7 (M46 vulnerability factor — only HRG)"
      H_review: "0.0 (review not yet applied)"
    conceptual_result:
      D_node(t=2): "clamp(0.7 + 0.0 - 0.3 × 0.7 + 0.0) = clamp(0.49) = 0.49"
      interpretation: "M46 degrades from pressured toward degraded — consistent with Phase 79A/80A observations"

  mapping_to_8_state_model:
    D_node_range:
      "1.0": "stable"
      "0.7 - 0.99": "pressured"
      "0.3 - 0.69": "degraded"
      "0.01 - 0.29": "partially_blocked / blocked"
      "0.0": "fully_degraded"
    note: "These ranges are conceptual mapping aids, not precise thresholds"
```

## 9. Path-Level Propagation Pressure Model

```yaml
path_level_propagation_pressure_model:
  conceptual_only: true
  not_executable: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  requires_human_review: true

  equation_form: |
    G_path = Σ P_edge(t) × (1 + A_seq) - Σ A_attenuation + Σ A_amplification - Σ B_blocking

  equation_description: >
    This conceptual equation aggregates edge-level propagation pressures into a
    path-level degradation assessment. G_path represents the net conceptual
    degradation intensity for the entire path. The equation accounts for:
    sequential amplification (A_seq accumulates across consecutive edges),
    per-edge attenuation, per-edge amplification, and boundary blocking events.

  variable_explanations:
    - variable: "G_path"
      meaning: "Path-level conceptual defense degradation intensity"
      interpretation: "Higher values indicate stronger net degradation pressure across the entire path"

    - variable: "Σ P_edge(t)"
      meaning: "Sum of conceptual propagation pressures across all edges at step t"
      interpretation: "Aggregate pressure from all edge segments"

    - variable: "A_seq"
      meaning: "Sequential amplification factor (AMPL-SEQ-001)"
      interpretation: "Increases with the number of consecutive weakly-defended boundaries"
      values:
        1_consecutive_weak: "0.1"
        2_consecutive_weak: "0.25"
        3_or_more: "0.5"

    - variable: "Σ A_attenuation"
      meaning: "Sum of attenuation factors applied across the path"
      interpretation: "Reduces G_path — higher attenuation means stronger defense"
      sources: "ATTEN-HRG-001, ATTEN-BND-001, ATTEN-RED-001, ATTEN-AUD-001, ATTEN-RPL-001"

    - variable: "Σ A_amplification"
      meaning: "Sum of amplification factors triggered across the path"
      interpretation: "Increases G_path — triggered by boundary weakening or cross-layer effects"
      sources: "AMPL-SEQ-001, AMPL-CROSS-001, AMPL-FEED-001"

    - variable: "Σ B_blocking"
      meaning: "Sum of boundary blocking events"
      interpretation: "Reduces G_path — each blocking event subtracts from net pressure"
      sources: "BLOCK-CMD-001, BLOCK-PERM-001, BLOCK-SB-001, BLOCK-RPL-001"

  mapping_to_trajectory_levels:
    G_path_range:
      "very_low (< 0.2)": "stable — no significant degradation pressure"
      "low (0.2 - 0.4)": "partial_pressure — some edges under pressure"
      "moderate (0.4 - 0.7)": "partial_degradation — entry/upstream modules degraded"
      "high (0.7 - 1.0)": "significant_degradation — multiple modules degraded"
      "very_high (> 1.0)": "critical_degradation — widespread module degradation"
    note: "These ranges are conceptual mapping aids. Phase 79A/80A both exhibited partial_degradation trajectories."

  cross_path_comparison:
    path_dev_cred:
      G_path_assessment: "moderate (partial_degradation)"
      key_factors:
        - "M46 V_node=0.7 causes early entry degradation"
        - "M47 3 attenuation rules (A_attenuation=0.6) contain mid-chain pressure"
        - "M50 4 rules (A_attenuation=0.8) provide strong terminal damping"
      note: "Consistent with Phase 80A observation: M46 degraded, M47 pressured, M50 pressured"

    path_rag:
      G_path_assessment: "moderate (partial_degradation)"
      key_factors:
        - "M48 V_node=0.5 (safe_summary protection) delays entry degradation"
        - "M49 2 attenuation rules (A_attenuation=0.4) — weaker than M47"
        - "M50 4 rules (A_attenuation=0.8) provides strong terminal damping"
      note: "Consistent with Phase 80A observation: M48 degraded (slower), M49 pressured, M50 pressured"

    full_lifecycle:
      G_path_assessment: "moderate_to_high (partial_degradation)"
      key_factors:
        - "M43 V_node=0.9 (no attenuation) causes earliest degradation"
        - "4 layer crossings → higher A_seq amplification"
        - "Longer path → more edges contributing to Σ P_edge"
      note: "Consistent with Phase 79A observation: M43/M46/M48 degraded, M49/M50 pressured"
```

## 10. Pattern Weight Integration

```yaml
pattern_weight_integration:
  conceptual_only: true
  requires_human_review: true

  integration_concept: >
    Each Phase 81A pattern provides a conceptual weight factor that modifies
    how the unified model interprets propagation dynamics for a given path
    segment. Weights are integrated at two levels:
    1. Edge-level: A_pattern in P_edge equation is derived from patterns
       applicable to the specific edge's source and target modules.
    2. Path-level: Pattern weights adjust G_path by modifying A_attenuation
       or A_amplification terms.

  pattern_to_equation_mapping:
    - pattern: "PATTERN-UPSTREAM-ENTRY-DEGRADATION-001"
      equation_impact: "Increases V_node for M43, M46, M48"
      conceptual_rationale: "Entry modules consistently degrade first — higher V_node reflects this observation"
      impact_direction: "amplification (increases degradation pressure)"

    - pattern: "PATTERN-M50-AUDIT-CONFIRMATION-001"
      equation_impact: "Adds to A_attenuation for M50 audit chain terms"
      conceptual_rationale: "M50 audit chain provides consistent confirmation across all paths"
      impact_direction: "attenuation (reduces degradation pressure)"

    - pattern: "PATTERN-M50-SANDBOX-BOUNDARY-001"
      equation_impact: "Adds to B_blocking for M50 sandbox boundary terms"
      conceptual_rationale: "M50 sandbox boundary is a structural blocking mechanism"
      impact_direction: "blocking (eliminates propagation at boundary)"

    - pattern: "PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001"
      equation_impact: "Adds to A_attenuation for M47 path segments"
      conceptual_rationale: "M47's 3 attenuation rules provide strong intermediate defense"
      impact_direction: "attenuation (reduces degradation pressure)"

    - pattern: "PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001"
      equation_impact: "Adds to A_amplification for M48-M49 segments"
      conceptual_rationale: "Dual-boundary failure (safe_summary + permission) creates amplification risk"
      impact_direction: "amplification (increases degradation pressure)"

    - pattern: "PATTERN-HUMAN-REVIEW-BREAKPOINT-001"
      equation_impact: "Enables H_review compensation for applicable modules"
      conceptual_rationale: "Human review gate is a universal breakpoint available to all modules except M43"
      impact_direction: "attenuation / recovery (reduces degradation pressure)"
```

## 11. M50 Damping / Audit Confirmation Role

```yaml
m50_damping_and_audit_confirmation:
  conceptual_only: true
  requires_human_review: true

  m50_damping_coefficient:
    conceptual_meaning: >
      A conceptual term representing M50's attenuating effect on upstream
      propagation pressure. M50 acts as a damper in the system — its strong
      defense posture (4 attenuation rules) conceptually absorbs pressure
      and prevents it from reflecting back upstream.
    conceptual_range: "[0.5, 1.0] where higher = stronger damping"
    derived_from:
      - "M50 4 attenuation rules (strongest profile)"
      - "M50 sandbox_boundary_preserved (hard boundary)"
      - "M50 audit_chain_consistent (detective control)"
      - "M50 controlled_replay_gate (preventive control)"
    default_value: "0.8 (conceptual strong damping)"
    not_production_risk: true
    human_review_required: true

  m50_role_in_equations:
    - equation: "P_edge (for edges targeting M50)"
      role: "D_target = 0.8 (high defense strength) — (1-D_target)=0.2 significantly reduces P_edge"
      effect: "Strong attenuation at M50 entry point"

    - equation: "D_node (for M50 itself)"
      role: "V_node = 0.2 (low vulnerability) — M50 degrades very slowly under pressure"
      effect: "M50 remains pressured, never degrades in observed tabletop exercises"

    - equation: "G_path (path-level)"
      role: "A_attenuation from M50 contributes strongly to Σ A_attenuation"
      effect: "M50's comprehensive attenuation reduces overall path degradation intensity"

  m50_dual_role:
    role_audit_confirmation:
      description: "M50 confirms upstream decisions are properly audited"
      primary_pattern: "PATTERN-M50-AUDIT-CONFIRMATION-001"
      primary_path: "PATH-DEV-CRED-RUNTIME-001 (audit chain for M47 credential decisions)"
      equation_contribution: "A_attenuation via ATTEN-AUD-001"

    role_sandbox_boundary:
      description: "M50 enforces sandbox boundary as final execution barrier"
      primary_pattern: "PATTERN-M50-SANDBOX-BOUNDARY-001"
      primary_path: "PATH-RAG-RUNTIME-001 (sandbox boundary for M49 permission decisions)"
      equation_contribution: "B_blocking via BLOCK-SB-001 and BLOCK-RPL-001"

  feedback_loop_contribution:
    loop: "runtime_control_feedback_loop"
    effect: "negative_feedback (attenuating)"
    strength: "moderate"
    equation_impact: "F_feedback < 0 when M50 D_node is high — reduces P_edge for upstream edges"
    observed_in: "All three tabletop exercises (Phase 79A and Phase 80A both paths)"
```

## 12. Tabletop Calibration Method

```yaml
tabletop_calibration_method:
  conceptual_only: true
  not_production_risk: true
  not_statistical_validation: true
  requires_human_review: true

  calibration_approach: >
    The unified model is calibrated against tabletop exercise observations
    through qualitative consistency checks rather than numerical fitting.
    Each tabletop exercise provides a set of observed node state transitions
    that the model should conceptually reproduce. Calibration adjusts the
    conceptual ranges and default values of model parameters, not by
    computing statistical fits, but by ensuring the model's conceptual
    behavior aligns with human-reviewed observations.

  calibration_targets:
    - target: "propagation_pressure_consistency"
      description: "Model-predicted P_edge should align with observed propagation outcomes"
      source: "Phase 79A/80A edge propagation timelines"
      method: "Compare conceptual P_edge values to observed 'propagation probable/possible' assessments"

    - target: "attenuation_node_consistency"
      description: "Model-predicted D_node for attenuation nodes should reflect observed defense states"
      source: "Phase 80A comparison report (M47 vs M49 attenuation comparison)"
      method: "Verify M47 D_node remains higher than M49 D_node under equivalent pressure"

    - target: "m50_damping_consistency"
      description: "M50 should remain 'pressured' (D_node ≈ 0.7-0.8) across all paths"
      source: "Phase 79A and Phase 80A all three path reports"
      method: "Verify M50 D_node does not degrade below 0.5 under any path scenario"

    - target: "entry_degradation_consistency"
      description: "Entry modules should degrade before intermediate and terminal modules"
      source: "Phase 81A upstream_entry_degradation_pattern"
      method: "Verify D_node rates: M43 < M46 < M48 < M49 ≈ M47 < M50"

    - target: "feedback_loop_consistency"
      description: "Runtime_control_feedback_loop should produce negative F_feedback when M50 is strong"
      source: "Phase 77A feedback loop model, Phase 79A/80A loop observations"
      method: "Verify F_feedback < 0 aligns with observed M50 strong state"

    - target: "cross_path_discrimination"
      description: "Model should produce different G_path profiles for DEV-CRED vs RAG paths"
      source: "Phase 80A multi-path comparison report"
      method: "Verify DEV-CRED has stronger M47 attenuation; RAG has stronger M48 safe_summary delay"

  calibration_procedure:
    - step: 1
      action: "Select a tabletop exercise path"
      input: "Phase 79A or Phase 80A path report"
    - step: 2
      action: "Map observed node state transitions to D_node values"
      method: "Convert state labels (stable/pressured/degraded) to conceptual D_node ranges"
    - step: 3
      action: "Apply the three conceptual equations to the path"
      method: "Compute conceptual P_edge, D_node evolution, and G_path"
    - step: 4
      action: "Compare model output to observed trajectory"
      method: "Check consistency of degradation order, attenuation nodes, and final states"
    - step: 5
      action: "Adjust variable defaults if inconsistency found"
      method: "Refine conceptual ranges for V_node, W_edge, or A_pattern within their defined bounds"
    - step: 6
      action: "Human review calibration adjustment"
      requirement: "All calibration adjustments require human review and sign-off"

  calibration_not:
    - "NOT statistical fitting or regression"
    - "NOT machine learning training"
    - "NOT production risk calibration"
    - "NOT automated parameter tuning"
    - "NOT vulnerability severity scoring"
```

## 13. Human Review Gate

```yaml
human_review_gate:
  required: true
  purpose: >
    Every component of the unified model requires human review before any
    conceptual downstream use. The model is a theoretical framework for
    human-guided analysis — not an automated system, not a detection tool,
    not a risk calculator.

  review_scope:
    - "Variable definitions — are the conceptual meanings clear and not misleading?"
    - "Equation forms — do the conceptual equations reflect observed tabletop patterns?"
    - "Parameter ranges — are the conceptual ranges appropriate?"
    - "Pattern weights — are the pattern-to-equation mappings reasonable?"
    - "Calibration method — is the tabletop consistency check approach sound?"
    - "Safety field confirmation — all security fields confirmed false"

  what_human_review_prevents:
    - "Misinterpretation of P_edge as exploitability score"
    - "Misinterpretation of G_path as production risk rating"
    - "Misinterpretation of V_node as confirmed vulnerability severity"
    - "Misinterpretation of conceptual equations as executable simulation code"
    - "Misinterpretation of pattern weights as detection rules"
    - "Misuse of calibration method as production validation"

  gate_structure:
    - stage: "Variable Review"
      reviews: "All core conceptual variables"
    - stage: "Equation Review"
      reviews: "P_edge, D_node, G_path equations"
    - stage: "Parameter Review"
      reviews: "All default values and ranges"
    - stage: "Pattern Integration Review"
      reviews: "Pattern-to-equation mappings"
    - stage: "Calibration Method Review"
      reviews: "Calibration targets and procedure"
    - stage: "Safety Field Confirmation"
      reviews: "All false declarations verified"
```

## 14. Forbidden Uses

```yaml
forbidden_uses:
  - "Must NOT be interpreted as an executable attack simulation model"
  - "Must NOT be used to compute production risk scores"
  - "Must NOT be used to assign vulnerability severity ratings"
  - "Must NOT be used as input to capability_engine execution"
  - "Must NOT be used as input to controlled replay execution"
  - "Must NOT be interpreted as formal security findings"
  - "Must NOT be interpreted as confirmed vulnerability evidence"
  - "Propagation equation (P_edge) must NOT be treated as exploitability score"
  - "Node state equation (D_node) must NOT be treated as real system state"
  - "Path degradation model (G_path) must NOT be treated as risk level"
  - "Pattern weights must NOT be treated as detection rules"
  - "M50 damping coefficient must NOT be treated as production safety guarantee"
  - "Tabletop calibration method must NOT be treated as statistical validation"
  - "All conceptual equations preserve conceptual_only semantics"
  - "All model outputs are human-review-candidates only"

## 15. Document Metadata

```yaml
metadata:
  phase: "82A"
  document_type: "unified_attack_intelligence_theory_model"
  theory_model_design_gate_only: true
  unified_model_blueprint_only: true
  conceptual_equations_only: true
  executable: false
  source_phases:
    - "74A (attack graph schema)"
    - "77A (dynamics model)"
    - "79A (first tabletop)"
    - "80A (multi-path tabletop)"
    - "81A (pattern library)"
  total_sections: 15
  core_variables: 10
  conceptual_equations: 3
  pattern_weights_integrated: 6
  calibration_targets: 6
  human_review_required: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
```
