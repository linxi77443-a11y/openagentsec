# Attack Evolution Trajectory Report Schema — Design Gate

## 1. Purpose and Scope

This document defines the schema for an Attack Evolution Trajectory Report, which captures the output of the attack graph dynamics simulation layer. The report describes how attack signals conceptually propagate across the graph over time, how node defense states evolve, and how feedback loops influence propagation.

**This is a design gate artifact only** — no executable code, no scripts, no implementation. The report schema is a conceptual template for future human review and planning.

## 2. Non-Execution Boundary

- `conceptual_report: true` for all reports
- `executable: false` for all reports
- `attack_execution_allowed: false` for all reports
- `controlled_replay_execution_allowed: false` for all reports
- `confirmed_vulnerability: false` for all reports
- `formal_finding_allowed: false` for all reports
- `production_safety_claimed: false` for all reports
- `human_review_required: true` for all reports
- No real payloads, commands, endpoints, credentials, or system references
- All report IDs use `<SIM_EVOLUTION_REPORT_ID>` placeholders

## 3. Report Object Model

```yaml
attack_evolution_trajectory_report:
  report_id: "<SIM_EVOLUTION_REPORT_ID>"
  report_version: "v3.0-design-gate"
  conceptual_report: true
  executable: false
  attack_execution_allowed: false
  controlled_replay_execution_allowed: false

  source_attack_graph_id: "<SIM_ATTACK_GRAPH_ID>"
  source_path_catalog_id: "<SIM_CROSS_MODULE_PATH_CATALOG>"
  source_framework_design_id: "<SIM_FRAMEWORK_ID>"

  involved_modules: []
  involved_layers: []
  conceptual_path_id: "<SIM_CROSS_MODULE_PATH_ID>"

  simulation_scope: {}
  time_step_model: {}
  attack_step_sequence: []
  node_state_timeline: {}
  edge_propagation_timeline: []

  propagation_probability_notes: {}
  attenuation_factor_notes: {}
  amplification_factor_notes: {}
  feedback_loop_observations: []

  defense_state_evolution: {}
  boundary_blocking_points: []
  recovery_points: []

  evidence_reference_map: {}

  human_review_required: true
  reviewer_decision_placeholder: {}

  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
```

## 4. Report Header Fields

```yaml
report_header:
  report_id: "<SIM_EVOLUTION_REPORT_ID>"
  report_version: "v3.0-design-gate"
  conceptual_report: true
  executable: false
  attack_execution_allowed: false
  controlled_replay_execution_allowed: false

  source_attack_graph_id: "<SIM_ATTACK_GRAPH_ID>"
  source_path_catalog_id: "<SIM_CROSS_MODULE_PATH_CATALOG>"
  source_framework_design_id: "<SIM_FRAMEWORK_ID>"
```

## 5. Coverage Fields

```yaml
coverage:
  involved_modules:
    - module_id: "M43"
      module_name: "MCP Tool Descriptor Integrity"
    - module_id: "M46"
      module_name: "Coding Agent Repository Context Injection"
    - module_id: "M47"
      module_name: "Coding Agent Command and Credential Boundary"
    - module_id: "M48"
      module_name: "RAG Document Poisoning and Instruction Boundary"
    - module_id: "M49"
      module_name: "RAG Permission Inheritance and Retrieval Audit"
    - module_id: "M50"
      module_name: "Agent Runtime Sandbox and Audit Chain Integrity"

  involved_layers:
    - "supply_chain"
    - "development_environment"
    - "rag_data"
    - "runtime_sandbox"

  conceptual_path_id: "PATH-SUPPLY-DEV-RUNTIME-001"
```

## 6. Simulation Scope

```yaml
simulation_scope:
  conceptual_only: true
  executable: false
  description: >
    Conceptual description of what the dynamics simulation would cover
    if executed in a future phase.
  conceptual_paths_covered:
    - "PATH-SUPPLY-DEV-001"
    - "PATH-DEV-CMD-001"
    - "PATH-DEV-RUNTIME-001"
  modules_simulated:
    - "M43"
    - "M46"
    - "M47"
    - "M50"
  layers_simulated:
    - "supply_chain"
    - "development_environment"
    - "runtime_sandbox"
  conceptual_time_steps: 4
  dynamics_rules_applied:
    - "propagation_probability"
    - "attenuation_rules"
    - "amplification_rules"
    - "boundary_blocking_rules"
    - "control_recovery_rules"
    - "feedback_loop_mechanisms"
```

## 7. Time Step Model

```yaml
time_step_model:
  conceptual_only: true
  executable: false
  definition: "Conceptual discrete time steps for the dynamics simulation"
  step_types:
    - "attack_step — signal propagation attempt"
    - "defense_response_step — defensive evaluation"
    - "state_transition_step — node state update"
    - "feedback_step — feedback loop evaluation"
  total_conceptual_steps: 4
```

## 8. Attack Step Sequence

```yaml
attack_step_sequence:
  - step: 1
    step_type: "attack_step"
    action: "M43 → M46 propagation attempt (context_influence edge)"
    propagation_rule: "trust_transfer"
    conceptual_description: "Tool descriptor trust signal attempts to transfer to repository context"

  - step: 2
    step_type: "attack_step"
    action: "M46 → M47 propagation attempt (context_influence edge)"
    propagation_rule: "context_transfer"
    conceptual_description: "Injected repository context attempts to influence command boundary"

  - step: 3
    step_type: "attack_step"
    action: "M47 → M50 propagation attempt (audit_dependency edge)"
    propagation_rule: "runtime_policy_transfer"
    conceptual_description: "Command boundary signal attempts to reach runtime policy enforcement"

  - step: 4
    step_type: "feedback_step"
    action: "Feedback loop evaluation across all involved modules"
    feedback_loops_evaluated:
      - "audit_gap_feedback_loop"
      - "runtime_control_feedback_loop"
    conceptual_description: "Evaluate how downstream states affect upstream propagation"
```

## 9. Node State Timeline

```yaml
node_state_timeline:
  conceptual_only: true
  not_execution_result: true
  requires_human_review: true

  timeline:
    - step: 0
      description: "Initial state before simulation"
      node_states:
        M43: "stable"
        M46: "stable"
        M47: "stable"
        M50: "stable"

    - step: 1
      description: "After M43 → M46 propagation attempt"
      node_states:
        M43: "pressured"
        M46: "pressured"
        M47: "stable"
        M50: "stable"

    - step: 2
      description: "After M46 → M47 propagation attempt"
      node_states:
        M43: "degraded"
        M46: "pressured"
        M47: "pressured"
        M50: "stable"

    - step: 3
      description: "After M47 → M50 propagation attempt"
      node_states:
        M43: "degraded"
        M46: "degraded"
        M47: "pressured"
        M50: "pressured"

    - step: 4
      description: "After feedback loop evaluation"
      node_states:
        M43: "degraded"
        M46: "degraded"
        M47: "pressured"
        M50: "pressured"
```

## 10. Edge Propagation Timeline

```yaml
edge_propagation_timeline:
  conceptual_only: true
  not_exploit_chain: true
  requires_human_review: true

  propagations:
    - step: 1
      edge: "M43 → M46"
      edge_type: "context_influence"
      propagation_probability_hint: "medium"
      attenuation_applied: "human_review_gate (M46)"
      propagation_outcome: "probable — M46 enters pressured state"
      conceptual_basis: "M43 and M46 both have available evidence_trace"

    - step: 2
      edge: "M46 → M47"
      edge_type: "context_influence"
      propagation_probability_hint: "medium"
      attenuation_applied: "human_review_gate (M47), command_boundary_preserved (M47)"
      propagation_outcome: "possible — M47 enters pressured state with boundary available"
      conceptual_basis: "Both modules have structured evidence_trace arrays"

    - step: 3
      edge: "M47 → M50"
      edge_type: "audit_dependency"
      propagation_probability_hint: "medium"
      attenuation_applied: "audit_chain_completeness (M50), controlled_replay_gate (M50)"
      propagation_outcome: "possible — M50 enters pressured state with multiple attenuations"
      conceptual_basis: "M47 has structured array, M50 has boolean fields — partial format mismatch"
```

## 11. Dynamics Factor Notes

```yaml
propagation_probability_notes:
  conceptual_only: true
  not_production_risk: true
  not_exploitability_score: true
  requires_human_review: true
  notes:
    - "All probabilities are qualitative hints, not quantitative metrics"
    - "Propagation likelihood is assessed per-edge, per-step"
    - "Evidence format variance introduces uncertainty in cross-module comparison"

attenuation_factor_notes:
  conceptual_only: true
  not_production_risk: true
  requires_human_review: true
  notes:
    - "Attenuation factors applied per edge based on propagation model"
    - "M47 has strongest attenuation profile (command_boundary + redaction + review)"
    - "M50 has comprehensive attenuation (audit_chain + controlled_replay_gate)"
    - "M43 has limited attenuation options — only evidence_trace fields available"

amplification_factor_notes:
  conceptual_only: true
  not_vulnerability_severity: true
  not_cvss: true
  requires_human_review: true
  notes:
    - "Amplification assessed per the dynamics model rules (AMPL-SEQ, AMPL-CROSS, AMPL-FEED)"
    - "Cross-layer propagation (supply_chain → development_environment → runtime_sandbox) applies stepwise amplification"
    - "Sequential weakening: 3 consecutive steps without complete blocking"
    - "Feedback loop assessment: audit_gap_feedback_loop may amplify if M50 degrades"
```

## 12. Feedback Loop Observations

```yaml
feedback_loop_observations:
  conceptual_loop_only: true
  requires_human_review: true
  observations:
    - loop_id: "runtime_control_feedback_loop"
      observed: true
      effect: "negative_feedback — attenuation upstream"
      strength_hint: "moderate"
      description: "M50 runtime controls conceptually attenuate upstream propagation"
      requires_human_review: true

    - loop_id: "audit_gap_feedback_loop"
      observed: false
      effect: "not_triggered"
      condition: "M50 audit_chain_consistent would need to be false"
      requires_human_review: true
```

## 13. Defense State Evolution

```yaml
defense_state_evolution:
  conceptual_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true
  evolution_summary: >
    All four modules show progressive state change across the attack steps.
    M43 degrades earliest (supply_chain is the entry point). M50 remains
    pressured but has strong attenuation controls. The progression is
    conceptual and depends on the specific attack path simulated.

  by_module:
    M43:
      initial: "stable"
      final: "degraded"
      transitions:
        - step: 1
          to: "pressured"
          trigger: "Upstream propagation from path entry"
        - step: 2
          to: "degraded"
          trigger: "No recovery mechanism — limited attenuation options"

    M46:
      initial: "stable"
      final: "degraded"
      transitions:
        - step: 1
          to: "pressured"
          trigger: "Propagation from M43"
        - step: 3
          to: "degraded"
          trigger: "Sustained propagation pressure without complete block"

    M47:
      initial: "stable"
      final: "pressured"
      transitions:
        - step: 2
          to: "pressured"
          trigger: "Propagation from M46"
        - step: 2-4
          status: "held — boundary preservation available"

    M50:
      initial: "stable"
      final: "pressured"
      transitions:
        - step: 3
          to: "pressured"
          trigger: "Propagation from M47"
        - step: 3-4
          status: "held — comprehensive attenuation available"
```

## 14. Boundary Blocking and Recovery Points

```yaml
boundary_blocking_points:
  - point_id: "BLOCK-PATH-001"
    step: 2
    module: "M47"
    boundary_type: "command_boundary"
    blocking_condition: "M47 command_boundary_preserved: true"
    status: "available — boundary present but not activated in this simulation"

  - point_id: "BLOCK-PATH-002"
    step: 3
    module: "M50"
    boundary_type: "sandbox_boundary"
    blocking_condition: "M50 sandbox_boundary_preserved: true"
    status: "available — boundary present but not activated in this simulation"

recovery_points:
  - point_id: "REC-PATH-001"
    step: 4
    module: "M50"
    recovery_type: "audit_chain_restoration"
    recovery_condition: "M50 audit_chain_consistent: true"
    status: "available — audit chain intact, can support recovery assessment"
```

## 15. Evidence Reference Map

```yaml
evidence_reference_map:
  description: "Maps each simulation step to existing module evidence_trace"
  entries:
    - step: 1
      module_id: "M43"
      source_phase: "66A"
      referenced_fields:
        - "descriptor_poisoning_detected"
        - "tool_metadata_untrusted"
      new_evidence_generated: false
    - step: 1
      module_id: "M46"
      source_phase: "72A"
      referenced_fields:
        - "repo_context_trust_decision"
      new_evidence_generated: false
    - step: 2
      module_id: "M46"
      source_phase: "72A"
      referenced_fields:
        - "instruction_like_content_identified"
      new_evidence_generated: false
    - step: 2
      module_id: "M47"
      source_phase: "71A"
      referenced_fields:
        - "command_integrity_decision"
        - "unauthorized_command_blocked"
      new_evidence_generated: false
    - step: 3
      module_id: "M47"
      source_phase: "71A"
      referenced_fields:
        - "credential_boundary_decision"
      new_evidence_generated: false
    - step: 3
      module_id: "M50"
      source_phase: "68A"
      referenced_fields:
        - "sandbox_boundary_preserved"
        - "audit_chain_consistent"
      new_evidence_generated: false
```

## 16. Human Review

```yaml
human_review:
  human_review_required: true
  purpose: >
    Every attack evolution trajectory report requires human review before any
    downstream use. The report is a conceptual modeling output — not a
    vulnerability assessment, not a formal finding.

  reviewer_decision_placeholder:
    status: "pending_review"
    reviewed_by: null
    review_date: null
    reviewer_comments: null
    review_questions:
      - question: "Are the node state transitions consistent with available evidence?"
      - question: "Are propagation probability hints reasonable given module evidence?"
      - question: "Are feedback loop observations valid?"
      - question: "Are boundary blocking points correctly identified?"
      - question: "Should this evolution trajectory be considered for further analysis?"
    reviewer_decision: null
    next_action: null
```

## 17. Safety Fields

```yaml
safety_fields:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  controlled_replay_claimed: false
  controlled_replay_execution_allowed: false
  replay_executable: false
  attack_evolution_trajectory_is_conceptual_only: true
  dynamics_model_output_is_not_exploit_chain: true
  report_is_human_review_candidate_only: true
```

## 18. Forbidden Uses

- This report schema must NOT be used to generate executable simulation reports.
- Report data must NOT contain real endpoints, credentials, commands, or payloads.
- `propagation_probability_notes` are qualitative planning aids — NOT exploitability scores.
- `amplification_factor_notes` are NOT vulnerability severity or CVSS assessments.
- Node state timelines must NOT be interpreted as confirmed exploit progressions.
- Feedback loop observations must NOT be interpreted as confirmed system behaviors.
- Report must NOT be treated as formal findings.
- This schema must NOT be used as input to capability_engine execution.
- This schema must NOT be used as input to controlled replay execution.
