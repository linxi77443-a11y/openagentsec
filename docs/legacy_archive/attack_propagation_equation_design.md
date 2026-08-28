# Attack Propagation Equation Design — Conceptual

## 1. Purpose and Scope

This document defines three conceptual equations for the unified attack intelligence theory model. These equations describe how attack signals conceptually propagate across cross-module edges, how node defense states evolve over time steps, and how path-level degradation pressure is aggregated.

**All equations are conceptual only** — not executable code, not statistical models, not production risk calculators. They are theoretical modeling aids for human-guided tabletop analysis.

## 2. Equation Boundary

```yaml
equation_boundary:
  conceptual_only: true
  not_executable: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  not_cvss: true
  not_formal_finding: true
  requires_human_review: true

  equation_status:
    - "Equations are conceptual representations only"
    - "No numerical computation or code implementation"
    - "No statistical fitting or regression"
    - "No machine learning training"
    - "No production risk calibration"
    - "All variable values are qualitative modeling aids"
```

## 3. Edge Propagation Pressure Equation

```yaml
equation_1_edge_propagation_pressure:
  conceptual_only: true
  not_executable: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  requires_human_review: true

  equation_name: "Edge Propagation Pressure Equation"
  equation_purpose: >
    Describes the conceptual pressure on a single cross-module edge
    at a given time step. Higher P_edge indicates stronger conceptual
    likelihood that a signal propagates from source to target.

  equation_form:
    display: "P_edge(t) = S_source(t) × W_edge × A_pattern × F_feedback × (1 - D_target)"
    plain_text: >
      P_edge(t) = S_source(t) × W_edge × A_pattern × F_feedback × (1 - D_target)

    latex: |
      P_{\text{edge}}(t) = S_{\text{source}}(t) \cdot W_{\text{edge}} \cdot A_{\text{pattern}} \cdot F_{\text{feedback}} \cdot (1 - D_{\text{target}})

  variable_definitions:
    - variable: "P_edge(t)"
      definition: "Conceptual propagation pressure on the edge at time step t"
      conceptual_range: "[0.0, 1.0] as a conceptual modeling scale"
      interpretation:
        "0.0": "No propagation pressure — signal does not propagate"
        "0.0 - 0.3": "Low propagation pressure — unlikely propagation"
        "0.3 - 0.6": "Moderate propagation pressure — possible propagation"
        "0.6 - 1.0": "High propagation pressure — probable propagation"
      not_production_risk: true

    - variable: "S_source(t)"
      definition: "Attack signal strength at the source node at time step t"
      derivation: >
        Conceptually derived from D_source(t). As D_source decreases
        (defense weakens), S_source increases:
        S_source(t) ≈ 1 - D_source(t)
      conceptual_range: "[0.0, 1.0]"
      default_when_stable: "0.0 (D_source=1.0)"
      default_when_pressured: "0.3 (D_source=0.7)"
      default_when_degraded: "0.7 (D_source=0.3)"
      not_production_risk: true

    - variable: "W_edge"
      definition: "Edge-type weight factor reflecting conceptual propagation conductivity"
      conceptual_range: "Conceptual discrete values"
      values_by_type:
        context_influence: "0.6 (medium)"
        trust_boundary_transfer: "0.5 (medium_low)"
        permission_dependency: "0.8 (medium_to_high)"
        evidence_dependency: "0.3 (low)"
        audit_dependency: "0.4 (low_to_medium)"
        runtime_dependency: "0.6 (medium)"
      source: "Phase 74A edge taxonomy, Phase 77A propagation probability qualitative scale"
      not_production_risk: true

    - variable: "A_pattern"
      definition: "Pattern-based amplification/attenuation modifier derived from Phase 81A pattern library"
      conceptual_range: "[0.0, 2.0] where <1 = attenuating, >1 = amplifying, 1 = neutral"
      derivation: >
        Aggregated from all Phase 81A patterns applicable to the edge's
        source and target modules. Each pattern contributes a sub-weight.
        A_pattern = product or weighted sum of applicable pattern weights
        (human review determines aggregation method per case).
      not_production_risk: true

    - variable: "F_feedback"
      definition: "Feedback loop factor reflecting downstream-to-upstream influence"
      conceptual_range: "[-1.0, 1.0]"
      sign_convention:
        "negative (< 0)": "Attenuating feedback — reduces propagation (e.g., runtime_control negative feedback)"
        "zero (= 0)": "No active feedback"
        "positive (> 0)": "Amplifying feedback — increases propagation (e.g., permission_leakage, credential_pressure)"
      typical_values:
        "runtime_control_active": "-0.2 (moderate negative feedback)"
        "permission_leakage_triggered": "0.3 (moderate positive feedback)"
        "credential_pressure_triggered": "0.2 (mild positive feedback)"
        "no_active_feedback": "0.0"
      source: "Phase 77A feedback loop model"
      not_production_risk: true
      not_exploitability_score: true

    - variable: "D_target"
      definition: "Target node defense state strength"
      conceptual_range: "[0.0, 1.0] where 1.0 = fully stable, 0.0 = fully degraded"
      interpretation: >
        The (1 - D_target) term is the key attenuation mechanism in the equation.
        When D_target is high (strong defense), (1 - D_target) is small,
        significantly reducing P_edge. This represents the target module's
        ability to resist incoming pressure.
      not_production_risk: true

  boundary_conditions:
    - condition: "S_source = 0"
      result: "P_edge = 0 (no signal to propagate)"
    - condition: "D_target = 1.0"
      result: "(1 - D_target) = 0, P_edge = 0 (fully stable target blocks propagation)"
    - condition: "A_pattern = 0"
      result: "P_edge = 0 (perfect pattern-based attenuation)"
    - condition: "F_feedback = -1.0"
      result: "P_edge = 0 (maximum negative feedback)"
    - condition: "All factors at neutral"
      result: "P_edge = S_source × 0.6 × 1.0 × 1.0 × (1 - D_target)"

  example_calculations:
    - example: "M46 → M47 (context_influence) at t=1"
      values:
        S_source(t=1): "0.3 (M46 pressured)"
        W_edge: "0.6 (context_influence)"
        A_pattern: "0.8 (credential_boundary_attenuation_pattern active)"
        F_feedback: "-0.1 (mild runtime_control feedback)"
        D_target: "0.8 (M47 strong — 3 attenuation rules)"
      conceptual_result:
        P_edge: "0.3 × 0.6 × 0.8 × (-0.1) × (1-0.8)"
        note: "F_feedback is negative, so it reduces the product"
        computation: "0.3 × 0.6 × 0.8 × 0.9 × 0.2 = 0.0259"
        interpretation: "Very low — M47's strong defense and negative feedback suppress propagation"

    - example: "M48 → M49 (permission_dependency) at t=2"
      values:
        S_source(t=2): "0.5 (M48 approaching degraded)"
        W_edge: "0.8 (permission_dependency)"
        A_pattern: "1.2 (permission_leakage_amplification_pattern active)"
        F_feedback: "0.0 (no active feedback)"
        D_target: "0.7 (M49 moderate — 2 attenuation rules)"
      conceptual_result:
        P_edge: "0.5 × 0.8 × 1.2 × 1.0 × 0.3 = 0.144"
        interpretation: "Low-to-moderate — M49's 2 rules provide some defense but less than M47"

    - example: "M43 → M46 (context_influence) at t=1"
      values:
        S_source(t=1): "0.3 (M43 pressured)"
        W_edge: "0.6 (context_influence)"
        A_pattern: "1.3 (upstream_entry_degradation active)"
        F_feedback: "0.0 (no feedback yet)"
        D_target: "0.7 (M46 pressured — HRG only)"
      conceptual_result:
        P_edge: "0.3 × 0.6 × 1.3 × 1.0 × 0.3 = 0.0702"
        interpretation: "Low — but accumulates across steps as M43 degrades further"
```

## 4. Node Defense State Evolution Equation

```yaml
equation_2_node_defense_state_evolution:
  conceptual_only: true
  not_executable: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  requires_human_review: true

  equation_name: "Node Defense State Evolution Equation"
  equation_purpose: >
    Describes how a node's defense state conceptually evolves from one
    time step to the next. D_node(t+1) is computed from the current state,
    incoming pressure, control recovery, node vulnerability, and human review.

  equation_form:
    display: "D_node(t+1) = clamp(D_node(t) + R_control - P_in(t) × V_node + H_review)"
    plain_text: >
      D_node(t+1) = clamp(D_node(t) + R_control - P_in(t) × V_node + H_review)

    latex: |
      D_{\text{node}}(t+1) = \text{clamp}\big(D_{\text{node}}(t) + R_{\text{control}} - P_{\text{in}}(t) \cdot V_{\text{node}} + H_{\text{review}}\big)

  variable_definitions:
    - variable: "D_node(t+1)"
      definition: "Defense state strength at the next time step"
      conceptual_range: "[0.0, 1.0] (clamped)"
      not_production_risk: true

    - variable: "D_node(t)"
      definition: "Defense state strength at current time step"
      conceptual_range: "[0.0, 1.0]"
      initial_value: "1.0 (all modules start stable)"
      not_production_risk: true

    - variable: "R_control"
      definition: "Control recovery / boundary blocking factor"
      conceptual_range: "[0.0, 1.0]"
      values_by_scenario:
        no_recovery: "0.0"
        boundary_blocked: "0.3 (boundary successfully blocks propagation)"
        recovery_activated: "0.2 (control recovery mechanism engaged)"
        boundary_blocked_and_recovery: "0.4 (both blocking and recovery active)"
      source: "Phase 77A control recovery rules, boundary blocking rules"
      not_production_risk: true

    - variable: "P_in(t)"
      definition: "Incoming propagation pressure (aggregated from all inbound edges)"
      conceptual_range: "[0.0, 1.0]"
      derivation: >
        Sum of all P_edge(t) values from edges targeting this node,
        capped at 1.0:
        P_in(t) = clamp(Σ P_edge_inbound(t), 0.0, 1.0)
      not_production_risk: true

    - variable: "V_node"
      definition: "Node vulnerability or pressure sensitivity factor"
      conceptual_range: "[0.0, 1.0]"
      default_by_module:
        M43: "0.90 (most vulnerable — no attenuation rules)"
        M46: "0.70 (moderately vulnerable — only HRG)"
        M47: "0.40 (resilient — 3 attenuation rules)"
        M48: "0.50 (less vulnerable — HRG + safe_summary)"
        M49: "0.50 (moderately resilient — 2 attenuation rules)"
        M50: "0.20 (most resilient — 4 attenuation rules)"
      source: "Phase 81A upstream_entry_degradation_pattern, module-pattern association matrix"
      not_vulnerability_severity: true
      human_review_required: true

    - variable: "H_review"
      definition: "Human review gate compensation factor"
      conceptual_range: "[0.0, 0.5]"
      values:
        review_available_and_applied: "0.3 (moderate compensation)"
        review_available_not_applied: "0.0"
        review_not_available: "0.0 (M43 — no human review gate)"
      source: "Phase 81A human_review_breakpoint_pattern"
      not_production_risk: true

  clamp_function:
    definition: "Conceptually bounds D_node to [0.0, 1.0]"
    behavior:
      - condition: "D_node(t+1) > 1.0"
        result: "D_node(t+1) = 1.0 (fully stable)"
      - condition: "D_node(t+1) < 0.0"
        result: "D_node(t+1) = 0.0 (fully degraded)"
    note: "The clamp function is a conceptual modeling aid — not a code implementation"

  mapping_to_8_state_model:
    conceptual_mapping:
      D_node = 1.0: "stable"
      0.7 ≤ D_node < 1.0: "pressured"
      0.3 ≤ D_node < 0.7: "degraded"
      0.01 ≤ D_node < 0.3: "partially_blocked / blocked"
      D_node = 0.0: "fully_degraded"
      H_review > 0: "may transition to human_review_required or recovered"
    note: "Ranges are conceptual — not precise thresholds"

  example_calculations:
    - example: "M46 at t=1 (first pressure arrival)"
      values:
        D_node(t=1): "0.7 (pressured)"
        R_control: "0.0 (no immediate recovery)"
        P_in(t=1): "0.3 (propagation from M43)"
        V_node: "0.7 (M46 vulnerability)"
        H_review: "0.0 (review not yet applied)"
      conceptual_result:
        D_node(t=2): "clamp(0.7 + 0.0 - 0.3 × 0.7 + 0.0) = clamp(0.49) = 0.49"
        mapping: "degraded"
        interpretation: "M46 degrades from pressured to degraded after one step of pressure — consistent with Phase 80A observation (M46 degrades at step 2)"

    - example: "M47 at t=1 (pressure arrival with strong defense)"
      values:
        D_node(t=1): "0.9 (near stable)"
        R_control: "0.3 (command_boundary block active)"
        P_in(t=1): "0.07 (low incoming pressure — from M46→M47 edge)"
        V_node: "0.4 (M47 is resilient)"
        H_review: "0.0 (review not yet applied)"
      conceptual_result:
        D_node(t=2): "clamp(0.9 + 0.3 - 0.07 × 0.4 + 0.0) = clamp(1.172) = 1.0"
        mapping: "stable (held with boundary support)"
        interpretation: "M47 maintains strong defense — boundary block and low incoming pressure keep D_node at maximum — consistent with Phase 80A observation (M47 holds at pressured, does not degrade)"

    - example: "M50 at t=3 (final downstream node)"
      values:
        D_node(t=3): "0.8 (near stable)"
        R_control: "0.4 (sandbox_boundary + controlled_replay_block active)"
        P_in(t=3): "0.14 (moderate pressure from M49)"
        V_node: "0.2 (M50 most resilient)"
        H_review: "0.0 (review not yet applied)"
      conceptual_result:
        D_node(t=4): "clamp(0.8 + 0.4 - 0.14 × 0.2 + 0.0) = clamp(1.172) = 1.0"
        mapping: "stable (held with comprehensive defense)"
        interpretation: "M50 remains fully stable — strong R_control from dual blocking mechanisms and low V_node absorb the incoming pressure — consistent with Phase 79A/80A observations (M50 holds at pressured)"
```

## 5. Path-Level Propagation Pressure Model

```yaml
equation_3_path_level_degradation:
  conceptual_only: true
  not_executable: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  requires_human_review: true

  equation_name: "Path-Level Defense Degradation Model"
  equation_purpose: >
    Aggregates edge-level propagation pressures and node-level attenuation,
    amplification, and blocking into a path-level degradation intensity
    assessment. G_path represents the net conceptual pressure across the
    entire path.

  equation_form:
    display: "G_path = Σ P_edge(t) × (1 + A_seq) - Σ A_attenuation + Σ A_amplification - Σ B_blocking"
    plain_text: >
      G_path = Σ P_edge(t) × (1 + A_seq) - Σ A_attenuation + Σ A_amplification - Σ B_blocking

    latex: |
      G_{\text{path}} = \big(\Sigma P_{\text{edge}}(t)\big) \cdot (1 + A_{\text{seq}}) - \Sigma A_{\text{attenuation}} + \Sigma A_{\text{amplification}} - \Sigma B_{\text{blocking}}

  variable_definitions:
    - variable: "G_path"
      definition: "Path-level conceptual defense degradation intensity"
      conceptual_range: "Unbounded conceptual index — interpreted via trajectory mapping"
      mapping_to_trajectory:
        "G_path < 0": "stable_or_pressured — effective containment"
        "0 ≤ G_path < 0.5": "partial_pressure — some edges under mild pressure"
        "0.5 ≤ G_path < 1.0": "partial_degradation — entry/upstream modules degraded"
        "1.0 ≤ G_path < 2.0": "significant_degradation — multiple modules degraded"
        "G_path ≥ 2.0": "critical_degradation — widespread module degradation"
      note: "Phase 79A and Phase 80A both exhibited partial_degradation trajectories"
      not_production_risk: true

    - variable: "Σ P_edge(t)"
      definition: "Sum of conceptual propagation pressures across all edges at step t"
      derivation: >
        P_edge values are computed from Equation 1 for each edge in the path.
        Only edges that are active at step t contribute to the sum.
      not_production_risk: true

    - variable: "A_seq"
      definition: "Sequential amplification factor (AMPL-SEQ-001)"
      conceptual_range: "[0.0, 0.5]"
      values:
        "0_consecutive_weak_boundaries": "0.0"
        "1_consecutive_weak_boundary": "0.1"
        "2_consecutive_weak_boundaries": "0.25"
        "3_or_more_consecutive_weak_boundaries": "0.5"
      determination: >
        Count consecutive edges where D_target < 0.5 (target is degraded
        or approaching degraded) at the time of propagation.
      source: "Phase 77A AMPL-SEQ-001 rule"
      not_vulnerability_severity: true

    - variable: "Σ A_attenuation"
      definition: "Sum of attenuation factors applied across the path"
      derivation: >
        Sum of conceptual weights assigned to each activated attenuation rule.
        ATTEN-HRG-001: "0.3"
        ATTEN-BND-001: "0.4"
        ATTEN-RED-001: "0.2"
        ATTEN-AUD-001: "0.3"
        ATTEN-RPL-001: "0.5"
      per_module:
        M43: "0.0 (no attenuation)"
        M46: "0.3 (ATTEN-HRG-001 only)"
        M47: "0.9 (ATTEN-HRG + ATTEN-BND + ATTEN-RED)"
        M48: "0.3 (ATTEN-HRG-001 only; safe_summary not a formal attenuation rule)"
        M49: "0.7 (ATTEN-HRG-001 + ATTEN-BND-001)"
        M50: "1.5 (ATTEN-HRG + ATTEN-BND + ATTEN-AUD + ATTEN-RPL)"
      source: "Phase 77A attenuation rules, Phase 80A tabletop observations"
      not_production_risk: true

    - variable: "Σ A_amplification"
      definition: "Sum of amplification factors triggered across the path"
      derivation: >
        Sum of conceptual weights for triggered amplification rules.
        AMPL-SEQ-001: "accounted via A_seq term separately"
        AMPL-CROSS-001: "0.2 per layer crossing"
        AMPL-FEED-001: "0.3 if positive feedback triggered, -0.2 if negative feedback active"
      source: "Phase 77A amplification rules"
      not_vulnerability_severity: true

    - variable: "Σ B_blocking"
      definition: "Sum of boundary blocking events"
      derivation: >
        Each blocking event subtracts from G_path.
        BLOCK-CMD-001: "0.4 (M47 command boundary block)"
        BLOCK-PERM-001: "0.4 (M49 permission boundary block)"
        BLOCK-SB-001: "0.5 (M50 sandbox boundary block)"
        BLOCK-RPL-001: "0.5 (M50 controlled replay block)"
      source: "Phase 77A boundary blocking rules"
      not_production_risk: true

  path_calculations:

    path_dev_cred:
      path: "PATH-DEV-CRED-RUNTIME-001"
      modules: ["M46", "M47", "M50"]
      edges: 2
      steps: 4
      conceptual_values:
        Σ P_edge(t=4): "0.2 (cumulative across 2 edges × 4 steps)"
        A_seq: "0.1 (1 weak boundary at M46)"
        Σ A_attenuation: "0.3 (M46) + 0.9 (M47) + 1.5 (M50) = 2.7"
        Σ A_amplification: "0.0 (no cross-layer amplification within same initial layer; 0.2 for dev→runtime)"
        Σ B_blocking: "0.4 (BLOCK-CMD-001 at M47) + 0.5 (BLOCK-SB-001 at M50) + 0.5 (BLOCK-RPL-001 at M50) = 1.4"
        note: "B_blocking includes M50's sandbox block even when M50 role is primarily audit in this path"
      conceptual_result:
        G_path: "0.2 × 1.1 - 2.7 + 0.2 - 1.4 = 0.22 - 2.7 - 1.2 = -3.68"
        Note: "Strong negative G_path indicates effective containment"
        trajectory: "partial_degradation (entry degrades, intermediate and terminal hold)"
        interpretation: "Strong attenuation (2.7) and blocking (1.4) outweigh propagation pressure, consistent with observed pattern: M46 degraded, M47/M50 pressured, net partial_degradation"

    path_rag:
      path: "PATH-RAG-RUNTIME-001"
      modules: ["M48", "M49", "M50"]
      edges: 2
      steps: 4
      conceptual_values:
        Σ P_edge(t=4): "0.24 (slightly higher than dev-cred due to permission_dependency W_edge=0.8)"
        A_seq: "0.1 (1 weak boundary at M48)"
        Σ A_attenuation: "0.3 (M48) + 0.7 (M49) + 1.5 (M50) = 2.5"
        Σ A_amplification: "0.2 (cross_layer: rag→runtime) + 0.3 (permission_leakage potential) = 0.5"
        Σ B_blocking: "0.4 (BLOCK-PERM-001 at M49) + 0.5 (BLOCK-SB-001 at M50) + 0.5 (BLOCK-RPL-001 at M50) = 1.4"
      conceptual_result:
        G_path: "0.24 × 1.1 - 2.5 + 0.5 - 1.4 = 0.264 - 2.5 - 0.9 = -3.136"
        trajectory: "partial_degradation (entry degrades slower, intermediate and terminal hold)"
        interpretation: "Container but with less margin than dev-cred — M49 attenuation (0.7) is weaker than M47 (0.9), and permission_leakage amplification (0.3) adds pressure. Consistent with Phase 80A observation: M48 degraded slower, M49 more pressured relative to M47."

    full_lifecycle:
      path: "PATH-SUPPLY-DEV-RAG-RUNTIME-001"
      modules: ["M43", "M46", "M48", "M49", "M50"]
      edges: 4
      steps: 5
      conceptual_values:
        Σ P_edge(t=5): "0.35 (more edges and steps than shorter paths)"
        A_seq: "0.25 (2 consecutive weak boundaries: M43→M46, M46→M48)"
        Σ A_attenuation: "0.0 (M43) + 0.3 (M46) + 0.3 (M48) + 0.7 (M49) + 1.5 (M50) = 2.8"
        Σ A_amplification: "0.2 × 3 (3 layer crossings) + 0.3 (permission_leakage potential) = 0.9"
        Σ B_blocking: "0.4 (BLOCK-PERM-001 at M49) + 0.5 (BLOCK-SB-001 at M50) + 0.5 (BLOCK-RPL-001 at M50) = 1.4"
      conceptual_result:
        G_path: "0.35 × 1.25 - 2.8 + 0.9 - 1.4 = 0.4375 - 2.8 - 0.5 = -2.8625"
        trajectory: "partial_degradation (more upstream modules degraded due to longer chain)"
        interpretation: "Still contained overall, but more upstream degradation (M43, M46, M48 degraded). Higher A_seq (0.25 vs 0.1) reflects more consecutive weak boundaries. Consistent with Phase 79A observation: 3 upstream modules degraded, 2 downstream held."
```

## 6. Equation Safety Semantics

```yaml
equation_safety_semantics:
  conceptual_only: true
  not_executable: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false

  semantic_clarifications:
    - term: "P_edge"
      meaning: "Conceptual propagation pressure in a theoretical model — NOT an exploitability score"
    - term: "D_node"
      meaning: "Conceptual defense state in a theoretical model — NOT a confirmed system security state"
    - term: "G_path"
      meaning: "Conceptual path degradation index — NOT a production risk score"
    - term: "V_node"
      meaning: "Conceptual vulnerability factor from tabletop observations — NOT a vulnerability severity rating"
    - term: "W_edge"
      meaning: "Conceptual edge conductivity weight — NOT a detection rule weight"
    - term: "F_feedback"
      meaning: "Conceptual feedback factor — NOT a real system feedback measurement"
    - term: "H_review"
      meaning: "Conceptual human review compensation — NOT a guarantee of human review effectiveness"
    - term: "clamp"
      meaning: "Conceptual bounding operation — NOT a code function"
    - term: "computation"
      meaning: "Conceptual reasoning aid — NOT a numerical simulation result"

  downstream_use_restrictions:
    - "Equations must NOT be implemented as executable code"
    - "Equation values must NOT be treated as real measurements"
    - "Conceptual results must NOT be cited as vulnerability evidence"
    - "Variable ranges must NOT be interpreted as confidence intervals"
    - "Path calculations must NOT be treated as risk assessments"
    - "All equation output is human-review-candidate only"
```

## 7. Document Metadata

```yaml
metadata:
  phase: "82A"
  document_type: "attack_propagation_equation_design"
  conceptual_only: true
  not_executable: true
  total_equations: 3
  total_variables: 14
  path_calculations: 3
  example_calculations: 5
  human_review_required: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  propagation_equation_is_not_exploit_chain: true
  theory_model_is_not_detection_rule: true
```
