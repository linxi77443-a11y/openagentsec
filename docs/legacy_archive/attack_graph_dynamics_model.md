# Attack Graph Dynamics Model — Design Gate

## 1. Purpose and Scope

This document defines a conceptual dynamics model for the cross-module attack graph. It describes how attack signals may dynamically propagate across the graph over conceptual attack steps, how propagation probability, attenuation, amplification, boundary blocking, and control recovery conceptually interact, and how node defense states evolve over time.

**This is a design gate artifact only** — no executable code, no scripts, no implementation, no simulation. The dynamics model remains a conceptual theory model for future human review and planning.

## 2. Non-Execution Boundary

- `conceptual_only: true` for all dynamics concepts
- `executable: false` for all dynamics rules
- No implementation code, no scripts, no executable automation
- No real endpoints, credentials, commands, or payloads
- No capability_engine execution
- No controlled replay execution
- All dynamics element IDs use `<SIM_DYNAMICS_ID>` placeholders
- All concept schemas are documentation-only — not executable configurations

## 3. Relationship to Phase 74A / 75A / 76A / 78A

```yaml
phase_relationships:
  phase74a:
    schema: "docs/cross_module_attack_graph_schema.md"
    model: "docs/risk_propagation_model.md"
    provides:
      - "7 node types, 9 edge types, 4 layers"
      - "7 propagation rule types"
      - "Amplification factor, attenuation factors, boundary preservation rules"
    role_in_dynamics: "Foundation type system — dynamics model operates on the same node/edge/layer types"

  phase75a:
    path_catalog: "docs/cross_module_attack_path_catalog.md"
    provides:
      - "8 conceptual paths with edge sequences and module coverage"
    role_in_dynamics: "Path templates — dynamics model applies propagation rules along these path templates"

  phase76a:
    explorer_blueprint: "docs/automated_cross_module_attack_chain_explorer_design.md"
    provides:
      - "Explorer logic concepts (probe insertion, degradation assessment)"
    role_in_dynamics: "Probe concepts — dynamics model defines probe outcomes as state transitions"

  phase78a:
    framework_blueprint: "docs/automated_attack_chain_discovery_framework_design.md"
    workflow_engine: "docs/automated_attack_chain_workflow_engine_design.md"
    provides:
      - "Framework component interaction model"
      - "Workflow engine stage definitions"
    role_in_dynamics: "Execution context — dynamics model feeds into the simulation planning and degradation analysis stages"
```

## 4. Dynamics Layer Conceptual Architecture

```yaml
dynamics_layer:
  layer_id: "<SIM_DYNAMICS_LAYER_ID>"
  conceptual_only: true
  executable: false
  description: >
    A conceptual layer that sits atop the static attack graph schema. While the
    schema defines what nodes, edges, and paths exist statically, the dynamics
    layer defines how signals conceptually propagate across them over time.

  dynamics_elements:
    - propagation_probability
    - attenuation_factor
    - amplification_factor
    - boundary_blocking_factor
    - control_recovery_factor
    - time_step_concept
    - node_state_evolution
    - feedback_loop_mechanism

  interaction_with_static_layers:
    - "Nodes from the static graph become stateful entities in the dynamics layer"
    - "Edges from the static graph become propagation channels in the dynamics layer"
    - "Edge types (context_influence, trust_boundary_transfer, etc.) influence propagation probabilities"
    - "Layer boundaries (supply_chain → development_environment → rag_data → runtime_sandbox) introduce attenuation"
    - "Attenuation factors from the propagation model become state recovery mechanisms"
    - "Amplification factor concept becomes a dynamics variable that changes with attack steps"
```

## 5. Propagation Probability Concept

```yaml
propagation_probability:
  conceptual_only: true
  not_production_risk: true
  not_exploitability_score: true
  not_cvss: true
  requires_human_review: true

  definition: >
    A conceptual indicator describing the theoretical likelihood that a signal
    from one module would propagate to an adjacent module across a specific
    edge type, given the source module's defensive state and the edge's
    characteristics. This is NOT a real probability — it is a qualitative
    planning aid for human review.

  conceptual_factors:
    - factor: "edge_type_influence"
      description: "Different edge types may conceptually influence propagation differently"
      qualitative_scale:
        context_influence: "medium_conceptual_propagation"
        trust_boundary_transfer: "medium_conceptual_propagation"
        permission_dependency: "medium_to_high_conceptual_propagation"
        evidence_dependency: "low_conceptual_propagation"
        audit_dependency: "low_to_medium_conceptual_propagation"
        runtime_dependency: "medium_conceptual_propagation"

    - factor: "source_defense_state"
      description: "The defense state of the source module influences propagation likelihood"
      qualitative_scale:
        stable: "low_propagation"
        pressured: "medium_propagation"
        degraded: "medium_to_high_propagation"
        partially_blocked: "low_to_medium_propagation"
        blocked: "very_low_propagation"

    - factor: "layer_boundary_crossing"
      description: "Crossing layer boundaries introduces conceptual propagation resistance"
      qualitative_scale:
        same_layer: "medium_to_high_propagation"
        adjacent_layer: "medium_propagation"
        skip_layer: "low_propagation"

    - factor: "attenuation_availability"
      description: "Available attenuation factors reduce conceptual propagation likelihood"
      qualitative_scale:
        attenuation_available: "reduced_propagation"
        no_attenuation: "increased_propagation"

  conceptual_confidence_hint:
    definition: "A qualitative hint about how confident a reviewer might be in the propagation assessment"
    levels:
      - "high_confidence — strong evidence_trace available for both source and target modules"
      - "medium_confidence — evidence available but format variance or gaps exist"
      - "low_confidence — limited evidence or missing signals"
      - "inconclusive — cannot assess without human review"
```

## 6. Attenuation Rules

```yaml
attenuation_rules:
  conceptual_only: true
  not_production_risk: true
  not_vulnerability_severity: true
  requires_human_review: true

  definition: >
    Conceptual rules that describe how propagation likelihood is reduced when
    defensive controls are present at a boundary crossing.

  rules:
    - rule_id: "ATTEN-HRG-001"
      rule_type: "human_review_gate_attenuation"
      description: "Human review gate at a module reduces propagation likelihood conceptually"
      conceptual_mechanism: "Human review introduces manual verification that interrupts automated signal propagation"
      applicable_modules: ["M46", "M47", "M48", "M49", "M50"]
      attenuation_effect: "significant_reduction"

    - rule_id: "ATTEN-BND-001"
      rule_type: "boundary_preservation_attenuation"
      description: "Preserved boundary in a module blocks or reduces propagation through that boundary"
      conceptual_mechanism: "Boundary enforcement (command, permission, sandbox) blocks signal transfer"
      applicable_boundaries:
        - "M47 command_boundary_preserved"
        - "M49 permission_boundary_preserved"
        - "M50 sandbox_boundary_preserved"
      attenuation_effect: "blocking_or_significant_reduction"

    - rule_id: "ATTEN-RED-001"
      rule_type: "redaction_attenuation"
      description: "Redaction or placeholder preservation reduces credential exposure propagation"
      conceptual_mechanism: "Secrets are replaced with placeholders, preventing meaningful credential transfer"
      applicable_modules: ["M47"]
      attenuation_effect: "moderate_reduction"

    - rule_id: "ATTEN-AUD-001"
      rule_type: "audit_chain_attenuation"
      description: "Complete audit chain enables detection and non-repudiation, conceptually deterring propagation"
      conceptual_mechanism: "Audit trace creates accountability that conceptually reduces undetected propagation"
      applicable_modules: ["M50"]
      attenuation_effect: "moderate_reduction"

    - rule_id: "ATTEN-RPL-001"
      rule_type: "controlled_replay_gate_attenuation"
      description: "Controlled replay gate prevents execution of untrusted sequences"
      conceptual_mechanism: "Replay gate blocks execution of simulated attack sequences"
      applicable_modules: ["M50"]
      attenuation_effect: "blocking"
```

## 7. Amplification Rules

```yaml
amplification_rules:
  conceptual_only: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  requires_human_review: true

  definition: >
    Conceptual rules that describe how propagation likelihood may increase when
    multiple weakly-defended boundaries are crossed in sequence.

  rules:
    - rule_id: "AMPL-SEQ-001"
      rule_type: "sequential_boundary_weakening"
      description: "Multiple consecutive boundaries without effective defense amplify propagation"
      conceptual_mechanism: "Each undefended or weakly-defended boundary crossing compounds the next"
      amplification_effect: "cumulative_increase"
      qualitative_scale:
        1_consecutive_weak: "minor_amplification"
        2_consecutive_weak: "moderate_amplification"
        3_or_more_consecutive_weak: "significant_amplification"

    - rule_id: "AMPL-CROSS-001"
      rule_type: "cross_layer_amplification"
      description: "Signals propagating across multiple layers may gain conceptual influence"
      conceptual_mechanism: "Crossing from supply_chain to runtime_sandbox accumulates contextual weight"
      amplification_effect: "stepwise_increase"
      per_layer_crossing: "minor_to_moderate_amplification"

    - rule_id: "AMPL-FEED-001"
      rule_type: "feedback_loop_amplification"
      description: "Feedback loops can amplify propagation when degradation signals feed back upstream"
      conceptual_mechanism: "Degraded downstream state conceptually increases upstream propagation likelihood"
      amplification_effect: "feedback_dependent"
```

## 8. Boundary Blocking Rules

```yaml
boundary_blocking_rules:
  conceptual_only: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  definition: >
    Conceptual rules that describe when propagation is blocked entirely at a
    security boundary.

  rules:
    - rule_id: "BLOCK-CMD-001"
      rule_type: "command_boundary_block"
      description: "Command boundary preservation blocks command-related propagation"
      trigger_condition: "M47 command_boundary_preserved == true AND unauthorized_command_blocked == true"
      blocking_effect: "propagation_blocked_at_boundary"

    - rule_id: "BLOCK-PERM-001"
      rule_type: "permission_boundary_block"
      description: "Permission boundary preservation blocks retrieval-related propagation"
      trigger_condition: "M49 permission_boundary_preserved == true AND restricted_retrieval_blocked == true"
      blocking_effect: "propagation_blocked_at_boundary"

    - rule_id: "BLOCK-SB-001"
      rule_type: "sandbox_boundary_block"
      description: "Sandbox boundary preservation blocks runtime escape propagation"
      trigger_condition: "M50 sandbox_boundary_preserved == true AND runtime_escape_blocked == true"
      blocking_effect: "propagation_blocked_at_boundary"

    - rule_id: "BLOCK-RPL-001"
      rule_type: "controlled_replay_block"
      description: "Controlled replay gate blocks execution of untrusted sequences"
      trigger_condition: "M50 controlled_replay_execution_blocked == true"
      blocking_effect: "propagation_blocked_at_gate"
```

## 9. Control Recovery Rules

```yaml
control_recovery_rules:
  conceptual_only: true
  not_production_safety: true
  requires_human_review: true

  definition: >
    Conceptual rules that describe how a node's defense state may recover from
    degradation over conceptual time steps, either autonomously or through
    human intervention.

  rules:
    - rule_id: "REC-HRG-001"
      rule_type: "human_review_recovery"
      description: "Human review can restore a degraded defense state to stable"
      conceptual_mechanism: "Manual verification identifies and corrects defensive gaps"
      recovery_effect: "restore_to_stable"
      requires_human_intervention: true

    - rule_id: "REC-AUD-001"
      rule_type: "audit_chain_restoration"
      description: "A complete audit chain allows trace-based recovery"
      conceptual_mechanism: "Audit logs enable reconstruction of events and identification of breach points"
      recovery_effect: "partial_to_full_recovery"
      requires_human_intervention: true

    - rule_id: "REC-BND-001"
      rule_type: "boundary_recovery"
      description: "Re-establishing a boundary can recover blocked state to partially_blocked"
      conceptual_mechanism: "Closing a breached or weakened boundary resumes enforcement"
      recovery_effect: "boundary_restored"
      requires_human_intervention: true

    - rule_id: "REC-TIME-001"
      rule_type: "time_based_attenuation"
      description: "Over multiple attack steps without reinforcement, propagation likelihood may naturally attenuate"
      conceptual_mechanism: "Signal strength decays without active reinforcement"
      recovery_effect: "gradual_attenuation"
      requires_human_intervention: false
```

## 10. Time Step / Attack Step Concept

```yaml
time_step_model:
  conceptual_only: true
  executable: false
  requires_human_review: true

  definition: >
    A conceptual time dimension for the dynamics model. Attack steps represent
    discrete conceptual steps in a hypothetical attack progression, not real
    time or real attack execution.

  time_step_types:
    - step_type: "attack_step"
      description: "A conceptual step where an attack signal attempts to propagate from one module to another"
      conceptual_duration: "One logical step in the attack chain"
      state_transition: "Source module defense state may degrade; target module may be pressured"

    - step_type: "defense_response_step"
      description: "A conceptual step where defensive controls respond to propagation attempts"
      conceptual_duration: "One logical evaluation step"
      state_transition: "Defensive signals evaluated; blocking/attenuation may occur"

    - step_type: "recovery_step"
      description: "A conceptual step where defensive controls may recover from degradation"
      conceptual_duration: "One logical recovery cycle"
      state_transition: "Degraded states may recover if recovery conditions are met"

    - step_type: "feedback_step"
      description: "A conceptual step where feedback loops influence upstream or downstream propagation"
      conceptual_duration: "One logical feedback evaluation"
      state_transition: "Feedback strength calculated; propagation probabilities adjusted"

  attack_step_sequence_concept:
    - step: 1
      action: "attack_step — signal attempts to propagate from source to target"
      evaluation: "propagation_probability assessed based on source state and edge type"
    - step: 2
      action: "defense_response_step — target module evaluates defensive signals"
      evaluation: "boundary blocking, attenuation, and amplification rules applied"
    - step: 3
      action: "state_transition_step — source and target defense states updated"
      evaluation: "degradation or recovery conditions evaluated"
    - step: 4
      action: "feedback_step — feedback loops evaluated for cross-step influence"
      evaluation: "feedback loop mechanisms calculated for next attack step"
```

## 11. Human Review Gate

```yaml
human_review_gate:
  required: true
  purpose: >
    Every dynamics model assessment requires human review before any downstream
    use. The dynamics model is a design discussion and theory modeling tool —
    not an automated simulation system.
  what_human_review_covers:
    - "Propagation probability assessment — is the qualitative scale reasonable?"
    - "Attenuation and amplification rule application — are the right rules applied?"
    - "Boundary blocking conditions — are blocking triggers correctly identified?"
    - "Control recovery assessment — are recovery conditions realistic?"
    - "Node state evolution — do state transitions reflect the evidence?"
    - "Feedback loop evaluation — are feedback mechanisms appropriately characterized?"
    - "Safety field confirmation — all security fields confirmed false"
```

## 12. Forbidden Uses

- This dynamics model must NOT be used to construct executable attack simulations.
- `propagation_probability` is a qualitative planning aid — NOT a real probability, NOT an exploitability score.
- `amplification_factor` is a conceptual design concept — NOT a vulnerability severity, NOT a CVSS score.
- `attenuation_factor` is NOT a guarantee of production safety.
- `boundary_blocking_factor` is NOT a confirmed vulnerability block.
- `control_recovery_factor` is NOT a production recovery guarantee.
- Dynamics model outputs must NOT be treated as formal findings.
- This model must NOT be used as input to capability_engine execution.
- This model must NOT be used as input to controlled replay execution.
- All references to module evidence preserve `simulated_capability_signal_only` semantics.
- Time step concepts must NOT be interpreted as real attack execution timelines.
