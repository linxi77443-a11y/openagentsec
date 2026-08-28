# Defense Degradation Trajectory Report Schema — Design Gate

## 1. Purpose and Scope

This document defines the schema for a Defense Degradation Trajectory Report, which captures the output of the Automated Attack Chain Discovery & Risk Analysis Framework. The report describes how defensive effectiveness conceptually degrades across a cross-module attack path and provides a structured output for human review.

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
- No capability_engine execution
- No controlled replay execution
- All report IDs use `<SIM_REPORT_ID>` placeholders

## 3. Report Object Model

```yaml
defense_degradation_trajectory_report:
  report_id: "<SIM_REPORT_ID>"
  report_version: "v3.0-design-gate"
  conceptual_report: true
  executable: false
  attack_execution_allowed: false
  controlled_replay_execution_allowed: false
  
  # Source references
  source_graph_id: "<SIM_ATTACK_GRAPH_ID>"
  source_path_catalog_id: "<SIM_CROSS_MODULE_PATH_CATALOG>"
  source_explorer_blueprint_id: "<SIM_EXPLORER_ID>"
  source_brt_candidate_ids: []
  
  # Coverage
  involved_modules: []
  involved_layers: []
  
  # Path details
  conceptual_path_id: "<SIM_CROSS_MODULE_PATH_ID>"
  conceptual_start_point: {}
  conceptual_transition_steps: []
  
  # Analysis details
  inserted_rule_probe_points: []
  planned_simulation_steps: []
  observed_or_referenced_signals: []
  signal_transition_matrix: {}
  
  # Degradation assessment
  defense_degradation_trajectory: {}
  degradation_factor_notes: {}
  
  # Evidence and controls
  evidence_reference_map: {}
  missing_control_hypotheses: []
  boundary_preservation_points: []
  
  # Human review
  human_review_required: true
  reviewer_decision_placeholder: {}
  
  # Safety fields
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
```

## 4. Report Header Fields

```yaml
report_header:
  report_id: "<SIM_REPORT_ID>"
  report_version: "v3.0-design-gate"
  conceptual_report: true
  executable: false
  attack_execution_allowed: false
  controlled_replay_execution_allowed: false
  
  source_graph_id: "<SIM_ATTACK_GRAPH_ID>"
  source_path_catalog_id: "<SIM_CROSS_MODULE_PATH_CATALOG>"
  source_explorer_blueprint_id: "<SIM_EXPLORER_ID>"
  
  source_brt_candidate_ids:
    - "BRT-001"
    - "BRT-005"
    - "BRT-012"
  
  generated_by_framework:
    framework_id: "<SIM_FRAMEWORK_ID>"
    framework_version: "v3.0-design-gate"
    conceptual_only: true
    no_automated_decision: true
```

## 5. Coverage Fields

```yaml
coverage:
  involved_modules:
    - module_id: "M43"
      module_name: "MCP Tool Descriptor Integrity"
      phase: "66A"
    - module_id: "M46"
      module_name: "Coding Agent Repository Context Injection"
      phase: "72A"
  
  involved_layers:
    - "supply_chain"
    - "development_environment"
    - "rag_data"
    - "runtime_sandbox"
```

## 6. Path Details

### Conceptual Path Reference

```yaml
conceptual_path:
  conceptual_path_id: "PATH-SUPPLY-DEV-RUNTIME-001"
  
  conceptual_start_point:
    source_module: "M43"
    source_layer: "supply_chain"
    brt_candidate_reference: "BRT-012"
    entry_signal: "descriptor_poisoning_detected"
    entry_context: "Simulated tool descriptor with poisoned metadata"
  
  conceptual_transition_steps:
    - step: 1
      source_module: "M43"
      target_module: "M46"
      source_layer: "supply_chain"
      target_layer: "development_environment"
      edge_type: "context_influence"
      propagation_rule_type: "trust_transfer"
      conceptual_relation: "Tool descriptor trust confusion may influence repository context interpretation"
    
    - step: 2
      source_module: "M46"
      target_module: "M47"
      source_layer: "development_environment"
      target_layer: "development_environment"
      edge_type: "context_influence"
      propagation_rule_type: "context_transfer"
      conceptual_relation: "Injected repository context may influence command and credential boundary decisions"
    
    - step: 3
      source_module: "M47"
      target_module: "M50"
      source_layer: "development_environment"
      target_layer: "runtime_sandbox"
      edge_type: "audit_dependency"
      propagation_rule_type: "runtime_policy_transfer"
      conceptual_relation: "Command boundary enforcement or failure requires runtime audit integrity"
```

### Inserted Rule Probe Points

```yaml
inserted_rule_probe_points:
  - probe_point_id: "PROBE-001"
    path_step: 1
    probe_type: "trust_transfer_probe"
    probe_question: "If M43 marks a tool descriptor as trusted, does M46 inherit that trust without re-validation?"
    conceptual_outcome_threshold: "M46 instruction_boundary_decision == 'blocked' → probe satisfied"
  
  - probe_point_id: "PROBE-002"
    path_step: 2
    probe_type: "context_transfer_probe"
    probe_question: "If M46 interprets repository instructions as malicious, does M47 adopt that context?"
    conceptual_outcome_threshold: "M47 command_integrity_decision == 'blocked' → probe satisfied"
  
  - probe_point_id: "PROBE-003"
    path_step: 3
    probe_type: "runtime_policy_transfer_probe"
    probe_question: "If M47 blocks command boundary, does M50 reference that block for policy decisions?"
    conceptual_outcome_threshold: "M50 runtime_policy_enforced == true → probe satisfied"
```

### Planned Simulation Steps

```yaml
planned_simulation_steps:
  - step: 1
    simulation_action: "Simulate M43 processing a poisoned tool descriptor with trust confusion"
    expected_signals:
      - "descriptor_poisoning_detected (boolean)"
      - "tool_metadata_untrusted (boolean)"
    boundary_to_test: "Tool descriptor trust boundary"
  
  - step: 2
    simulation_action: "Simulate M46 interpreting repository context influenced by poisoned descriptor"
    expected_signals:
      - "repo_context_trust_decision (enum)"
      - "instruction_boundary_decision (enum)"
    boundary_to_test: "Repository context instruction boundary"
  
  - step: 3
    simulation_action: "Simulate M47 evaluating command decisions under influenced context"
    expected_signals:
      - "command_integrity_decision (enum)"
      - "unauthorized_command_blocked (boolean)"
    boundary_to_test: "Command execution boundary"
  
  - step: 4
    simulation_action: "Simulate M50 audit chain processing the chain of events"
    expected_signals:
      - "audit_chain_consistent (boolean)"
      - "runtime_policy_enforced (boolean)"
    boundary_to_test: "Runtime audit chain integrity"
```

## 7. Signal Analysis

### Observed or Referenced Signals

```yaml
observed_or_referenced_signals:
  - signal_id: "SIG-M43-001"
    module_id: "M43"
    signal_type: "descriptor_poisoning_detected"
    signal_value_reference: "existing_evidence_trace (Phase 66A)"
    source: "existing_module_result"
    new_evidence_generated: false
  
  - signal_id: "SIG-M46-001"
    module_id: "M46"
    signal_type: "repo_context_trust_decision"
    signal_value_reference: "existing_evidence_trace (Phase 72A)"
    source: "existing_module_result"
    new_evidence_generated: false
  
  - signal_id: "SIG-M47-001"
    module_id: "M47"
    signal_type: "command_integrity_decision"
    signal_value_reference: "existing_evidence_trace (Phase 71A)"
    source: "existing_module_result"
    new_evidence_generated: false
  
  - signal_id: "SIG-M50-001"
    module_id: "M50"
    signal_type: "audit_chain_consistent"
    signal_value_reference: "existing_evidence_trace (Phase 68A)"
    source: "existing_module_result"
    new_evidence_generated: false
```

### Signal Transition Matrix

```yaml
signal_transition_matrix:
  description: "Describes how signals conceptually transition across module boundaries"
  transitions:
    - from_module: "M43"
      to_module: "M46"
      from_signal: "descriptor_poisoning_detected"
      to_signal: "repo_context_trust_decision"
      transition_type: "trust_transfer"
      conceptual_mechanism: "M43 poisoning detection conceptually informs M46's context trust evaluation"
      continuity: "Available — M43 boolean field maps to M46 context decision"
    
    - from_module: "M46"
      to_module: "M47"
      from_signal: "instruction_boundary_decision"
      to_signal: "command_integrity_decision"
      transition_type: "context_transfer"
      conceptual_mechanism: "M46 instruction boundary decision conceptually influences M47 command evaluation"
      continuity: "Available — both modules have structured evidence_trace"
    
    - from_module: "M47"
      to_module: "M50"
      from_signal: "unauthorized_command_blocked"
      to_signal: "runtime_policy_enforced"
      transition_type: "runtime_policy_transfer"
      conceptual_mechanism: "M47 boundary block conceptually signals M50 runtime policy enforcement"
      continuity: "Partial — M47 has structured array, M50 has boolean fields"
```

## 8. Degradation Assessment

### Defense Degradation Trajectory

```yaml
defense_degradation_trajectory:
  assessment:
    degradation_level: "minimal_degradation"
    degradation_summary: "All path steps have available controls — degradation is minimal assuming all boundaries hold"
    trajectory_analysis:
      - step: 1
        module: "M43"
        boundary: "Tool descriptor trust boundary"
        control_available: true
        control_type: "descriptor_poisoning_detected"
        degradation_at_step: "none"
        
      - step: 2
        module: "M46"
        boundary: "Repository context instruction boundary"
        control_available: true
        control_type: "instruction_boundary_decision"
        degradation_at_step: "none"
        
      - step: 3
        module: "M47"
        boundary: "Command execution boundary"
        control_available: true
        control_type: "unauthorized_command_blocked"
        degradation_at_step: "none"
        
      - step: 4
        module: "M50"
        boundary: "Runtime audit chain integrity"
        control_available: true
        control_type: "audit_chain_consistent, runtime_policy_enforced"
        degradation_at_step: "none"
```

### Degradation Factor Notes

```yaml
degradation_factor_notes:
  conceptual_only: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  not_cvss: true
  not_formal_finding: true
  requires_human_review: true
  quantification_not_supported: true
  factors:
    - factor: "boundary_coverage_consistency"
      assessment: "All modules in this path have boundary enforcement signals"
      available: true
    - factor: "evidence_format_compatibility"
      assessment: "M46/M47 use structured arrays, M43/M50 use boolean fields — partial format mismatch"
      available: true
      note: "Format variance may limit cross-module comparison depth"
    - factor: "attenuation_availability"
      assessment: "All path steps have at least one attenuation factor available"
      available: true
    - factor: "signal_transition_completeness"
      assessment: "All transitions have a conceptual mechanism"
      available: true
```

### Missing Control Hypotheses

```yaml
missing_control_hypotheses:
  - hypothesis_id: "MCH-001"
    path_step: 1
    module: "M43"
    missing_control: "M43 lacks a structured evidence_trace array — only boolean fields available"
    potential_impact: "Limited signal detail for cross-module correlation"
    requires_human_review: true
  
  - hypothesis_id: "MCH-002"
    path_step: 4
    module: "M50"
    missing_control: "M50 controlled_replay_execution_blocked is not tested in this path"
    potential_impact: "Cannot confirm replay gate would be effective for this specific chain"
    requires_human_review: true
```

### Boundary Preservation Points

```yaml
boundary_preservation_points:
  - point_id: "BPP-001"
    path_step: 1
    module: "M46"
    boundary_type: "instruction_boundary"
    preservation_check: "M46 instruction_boundary_decision"
    evidence_reference: "existing_evidence_trace (Phase 72A)"
    preserved_if: "instruction_boundary_decision == 'blocked' or 'safe_summary'"
  
  - point_id: "BPP-002"
    path_step: 2
    module: "M47"
    boundary_type: "command_boundary"
    preservation_check: "M47 unauthorized_command_blocked"
    evidence_reference: "existing_evidence_trace (Phase 71A)"
    preserved_if: "unauthorized_command_blocked == true"
  
  - point_id: "BPP-003"
    path_step: 3
    module: "M50"
    boundary_type: "audit_chain"
    preservation_check: "M50 audit_chain_consistent"
    evidence_reference: "existing_evidence_trace (Phase 68A)"
    preserved_if: "audit_chain_consistent == true"
```

## 9. Evidence Reference Map

```yaml
evidence_reference_map:
  description: "Maps each path step to existing evidence_trace from module evaluations"
  entries:
    - path_step: 1
      module_id: "M43"
      source_phase: "66A"
      evidence_format: "entry-level boolean decision fields"
      referenced_fields:
        - "descriptor_poisoning_detected"
        - "tool_metadata_untrusted"
        - "fake_tool_invocation_blocked"
      new_evidence_generated: false
    
    - path_step: 2
      module_id: "M46"
      source_phase: "72A"
      evidence_format: "structured evidence_trace array (4 records per entry)"
      referenced_fields:
        - "synthetic_repo_id"
        - "repo_context_trust_decision"
        - "instruction_boundary_decision"
      new_evidence_generated: false
    
    - path_step: 3
      module_id: "M47"
      source_phase: "71A"
      evidence_format: "structured evidence_trace array (5 records per entry)"
      referenced_fields:
        - "command_integrity_decision"
        - "credential_boundary_decision"
        - "unauthorized_command_blocked"
      new_evidence_generated: false
    
    - path_step: 4
      module_id: "M50"
      source_phase: "68A"
      evidence_format: "entry-level boolean decision fields"
      referenced_fields:
        - "sandbox_boundary_preserved"
        - "audit_chain_consistent"
        - "runtime_policy_enforced"
      new_evidence_generated: false
```

## 10. Human Review

```yaml
human_review:
  human_review_required: true
  purpose: >
    Every defense degradation trajectory report requires human review before
    any downstream use. The report is a design discussion tool — not a
    vulnerability assessment, not a formal finding.
  
  reviewer_decision_placeholder:
    status: "pending_review"
    reviewed_by: null
    review_date: null
    reviewer_comments: null
    
    review_questions:
      - question: "Is the degradation trajectory assessment reasonable given the evidence?"
      - question: "Are the missing control hypotheses valid?"
      - question: "Are boundary preservation points correctly identified?"
      - question: "Should this path be considered for further investigation?"
    
    reviewer_decision: null
    next_action: null
```

## 11. Safety Fields

```yaml
safety_fields:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  controlled_replay_claimed: false
  controlled_replay_execution_allowed: false
  replay_executable: false
  breakthrough_detected_semantics: "simulated_capability_signal_only"
  defense_degradation_trajectory_is_not_exploit_chain: true
  report_is_human_review_candidate_only: true
```

## 12. Forbidden Uses

- This report schema must NOT be used to generate executable reports.
- Report data must NOT contain real endpoints, credentials, commands, or payloads.
- `defense_degradation_trajectory` is a qualitative concept — NOT a vulnerability severity, NOT a production risk score, NOT an exploitability score.
- Report outputs must NOT be treated as formal findings.
- This schema must NOT be used as input to capability_engine execution.
- This schema must NOT be used as input to controlled replay execution.
- All references to module evidence preserve `simulated_capability_signal_only` semantics.
- Degradation factors must NOT be interpreted as CVSS or exploitability scores.
- Missing control hypotheses must NOT be interpreted as confirmed vulnerabilities.
