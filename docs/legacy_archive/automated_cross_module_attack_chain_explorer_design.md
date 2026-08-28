# Automated Cross-Module Attack Chain Explorer — Design Gate

## 1. Purpose and Scope

This document defines a conceptual design blueprint for an Automated Cross-Module Attack Chain Explorer. The explorer would systematically combine signals from individual v2.0 module evaluations (M43, M46, M47, M48, M49, M50) into cross-module attack chains, using the Phase 74A attack graph schema and risk propagation model as its logical foundation.

**This is a design gate artifact only** — no executable code, no implementation, no execution. The explorer remains a conceptual blueprint for future human review and planning.

## 2. Non-Execution Boundary

- `executable: false` for all explorer logic concepts
- No implementation code, no scripts, no executable automation
- No real endpoints, credentials, commands, or payloads
- No capability_engine execution
- No controlled replay execution
- All explorer IDs use `<SIM_EXPLORER_ID>` placeholders
- All output report schemas are conceptual only

## 3. Explorer Object Model

```yaml
explorer_schema:
  explorer_id: "<SIM_EXPLORER_ID>"
  version: "v3.0-design-gate"
  design_gate_only: true
  executable: false
  input_sources: []
  explorer_logic: {}
  output_schema: {}
  safety_fields:
    confirmed_vulnerability: false
    formal_finding_allowed: false
    production_safety_claimed: false
    controlled_replay_claimed: false
    controlled_replay_execution_allowed: false
    replay_executable: false
```

## 4. Input Sources

### 4.1 Breakthrough Candidate Catalog (Phase 63A)

```yaml
input_brt_candidates:
  source_phase: "63A"
  total_candidates: 20
  candidate_ids: ["BRT-001" .. "BRT-020"]
  source_playbooks: 10
  mapping_type: "red_blue_purple_retest_mapping"
  available_fields_per_candidate:
    - breakthrough_detected
    - breakthrough_type
    - capability_signal
    - affected_boundary
    - evidence_trace_ref
    - exploit_chain_steps
    - attacker_type
    - attack_objective
  purpose: >
    Each BRT candidate provides a validated breakthrough signal with evidence trace
    reference and exploit chain steps. The explorer would use these as candidate
    attack chain building blocks.
```

### 4.2 Cross-Module Path Catalog (Phase 74A)

```yaml
input_cross_module_path_catalog:
  source_phase: "74A"
  total_conceptual_paths: 4
  path_ids:
    - "PATH-SUPPLY-DEV-001": "M43 → M46 (supply_chain → development_environment)"
    - "PATH-DEV-CRED-RUNTIME-001": "M46 → M47 → M50 (development_environment → runtime_sandbox)"
    - "PATH-RAG-RUNTIME-001": "M48 → M49 → M50 (rag_data → runtime_sandbox)"
    - "PATH-FULL-LIFECYCLE-001": "M43 → M46 → M47 → M48 → M49 → M50 (end-to-end)"
  purpose: >
    Each conceptual path defines a module-pair or module-chain relationship with
    contextual description. The explorer would use these as path templates for
    chain composition.
```

### 4.3 Attack Graph Schema (Phase 74A)

```yaml
input_attack_graph_schema:
  source_phase: "74A"
  node_types_available: 7
    - module_node
    - boundary_node
    - artifact_node
    - signal_node
    - control_node
    - evidence_node
    - layer_node
  edge_types_available: 9
    - context_influence
    - trust_boundary_transfer
    - permission_dependency
    - evidence_dependency
    - audit_dependency
    - runtime_dependency
    - amplification_edge
    - mitigation_edge
    - review_gate_edge
  layers_defined: 4
    - supply_chain
    - development_environment
    - rag_data
    - runtime_sandbox
  purpose: >
    The attack graph schema provides the type system for nodes, edges, and paths.
    The explorer would instantiate nodes and edges from these type definitions
    when composing attack chains.
```

### 4.4 Risk Propagation Model (Phase 74A)

```yaml
input_risk_propagation_model:
  source_phase: "74A"
  propagation_layers: 4
  propagation_rule_types: 7
    - trust_transfer
    - context_transfer
    - permission_transfer
    - credential_exposure_transfer
    - retrieval_transfer
    - audit_trace_transfer
    - runtime_policy_transfer
  conceptual_propagation_patterns: 3
    - "PATTERN-SUPPLY-DEV-001": "M43 → M46 → M47"
    - "PATTERN-DEV-RAG-001": "M46 → M47 → M48 → M49"
    - "PATTERN-RAG-RUNTIME-001": "M48 → M49 → M50"
  purpose: >
    The propagation model defines how signals conceptually transfer between modules
    and layers. The explorer would use propagation rule types to assess whether
    a composed chain is conceptually plausible.
```

### 4.5 Existing Module Results (v2.0 MVP Complete)

```yaml
input_existing_module_results:
  modules:
    M43:
      status: "mvp_complete"
      phase: "66A"
      primary_objective: "supply_chain_tool_descriptor_poisoning"
      evidence_format: "entry-level boolean decision fields"
      breakthrough_detected: 0
    M46:
      status: "mvp_complete"
      phase: "72A"
      primary_objectives:
        - "dev_environment_repository_context_injection"
        - "dev_environment_code_review_bypass"
      evidence_format: "structured evidence_trace array (4 records per entry)"
      breakthrough_detected: 0
    M47:
      status: "mvp_complete"
      phase: "71A"
      primary_objectives:
        - "dev_environment_unauthorized_command_induction"
        - "dev_environment_credential_exposure_attempt"
        - "dev_environment_agent_permission_confusion"
      evidence_format: "structured evidence_trace array (5 records per entry)"
      breakthrough_detected: 0
    M48:
      status: "mvp_complete"
      phase: "67A"
      primary_objective: "rag_malicious_document_poisoning"
      evidence_format: "entry-level boolean decision fields"
      breakthrough_detected: 0
    M49:
      status: "mvp_complete"
      phase: "69A"
      primary_objectives:
        - "rag_permission_inheritance_bypass"
        - "rag_cross_tenant_retrieval_attempt"
        - "rag_retrieval_audit_gap_detection"
      evidence_format: "entry-level boolean decision fields"
      breakthrough_detected: 0
    M50:
      status: "mvp_complete"
      phase: "68A"
      primary_objectives:
        - "runtime_sandbox_escape_signal"
        - "runtime_fake_tool_boundary_violation"
        - "runtime_audit_chain_tampering_signal"
        - "runtime_trace_integrity_gap_detection"
        - "runtime_policy_enforcement_bypass"
      evidence_format: "entry-level boolean decision fields"
      breakthrough_detected: 0
  purpose: >
    Each module's MVP results contain actual evaluation data (evidence_trace, signals,
    decision booleans) that the explorer would reference when composing specific
    attack chain instances.
```

## 5. Explorer Logic Concepts

### 5.1 Start Point Selection

```yaml
start_point_selection:
  description: >
    Select one or more entries from BRT candidates or module MVP results as the
    starting point for attack chain composition.
  logic_concept: "entry_selection"
  selection_criteria:
    - criterion: "brt_candidate_with_breakthrough"
      description: "Select a BRT candidate where breakthrough_detected is true"
      source: "BRT-001 .. BRT-020"
    - criterion: "module_entry_with_weakest_defense"
      description: "Select module evaluation entries where defensive signals are weakest or absent"
      source: "per-entry execution results across M43/M46/M47/M48/M49/M50"
    - criterion: "boundary_weakening_detected"
      description: "Select entries where a boundary-level defense was triggered but incomplete"
      source: "boundary_node type from attack graph schema"
  conceptual_only: true
  executable: false
```

### 5.2 Path Composition

```yaml
path_composition:
  description: >
    Compose a cross-module attack chain by linking the start point through
    intermediate modules toward a target module, using the conceptual path
    catalog as a template.
  logic_concept: "chain_composition"
  composition_rules:
    - rule: "path_template_match"
      description: >
        Match the selected start point's module against conceptual path catalog
        entry points, then traverse along the path template.
      example: >
        Start point from M43 (supply_chain) matches PATH-SUPPLY-DEV-001
        entry point → traverse M43 → M46
    - rule: "edge_type_validation"
      description: >
        For each step in the composed chain, validate that a compatible edge
        type exists in the attack graph schema between source and target modules.
      example: >
        M43 → M46 uses context_influence edge type (defined in cross_module_edges)
    - rule: "layered_sequence_enforcement"
      description: >
        Ensure the chain respects layer ordering: supply_chain → development_environment
        → rag_data → runtime_sandbox. Reverse propagation is conceptually possible
        but requires explicit justification.
    - rule: "evidence_trace_link"
      description: >
        Each step should reference existing evidence_trace from the source module's
        MVP results. No new evidence is generated.
  chain_depth:
    min_modules: 2
    max_modules: 6
    conceptual_only: true
  executable: false
```

### 5.3 Rule Probe Insertion

```yaml
rule_probe_insertion:
  description: >
    For each step in the composed chain, identify which propagation rule type
    would be probed and what defensive condition would need to fail for the
    chain to progress.
  logic_concept: "rule_probe"
  probe_types:
    - probe_type: "trust_transfer_probe"
      description: "Assess whether trust decisions from source module could transfer to target"
      example_condition: "If M43 marks a tool descriptor as trusted, does M46 inherit that trust without re-validation?"
    - probe_type: "context_transfer_probe"
      description: "Assess whether context interpretation from source influences target"
      example_condition: "If M46 interprets repository instructions as malicious, does M47 adopt that context for command decisions?"
    - probe_type: "permission_transfer_probe"
      description: "Assess whether permission boundary decisions cascade"
      example_condition: "If M49 bypasses permission boundary, does M50 accept the bypassed context?"
    - probe_type: "credential_exposure_transfer_probe"
      description: "Assess whether credential exposure in one module increases downstream risk"
      example_condition: "If M47 exposes credential placeholder, does that secret reach M50 runtime?"
    - probe_type: "retrieval_transfer_probe"
      description: "Assess whether poisoned RAG content reaches development or runtime"
      example_condition: "If M48 retrieves poisoned document, does M46 incorporate it into code context?"
    - probe_type: "audit_trace_transfer_probe"
      description: "Assess whether audit chain integrity affects cross-module accountability"
      example_condition: "If M50 audit chain is tampered, are upstream violations (M49 permission bypass) obscured?"
    - probe_type: "runtime_policy_transfer_probe"
      description: "Assess whether upstream boundary signals affect runtime enforcement decisions"
      example_condition: "If M47 blocks command boundary, does M50 reference that block for policy decisions?"
  probe_result_concept:
    - result: "probe_satisfied"
      meaning: "The propagation rule is conceptually plausible for this chain step"
    - result: "probe_unsatisfied"
      meaning: "The propagation rule is blocked by existing defense or missing precondition"
    - result: "probe_inconclusive"
      meaning: "Insufficient evidence_trace to determine — requires human review"
  conceptual_only: true
  executable: false
```

### 5.4 Defense Degradation Assessment

```yaml
defense_degradation_assessment:
  description: >
    Assess how multiple boundary weakenings across modules compound into a
    degraded overall defense posture. This is the exploratory analog of the
    risk_amplification_factor from the propagation model.
  logic_concept: "degradation_assessment"
  assessment_dimensions:
    - dimension: "boundary_coverage_gap"
      description: "Number of consecutive module boundaries without a confirmed defensive block"
      example: "M43 boundary triggered, M46 boundary missing, M47 boundary triggered → gap at M46"
    - dimension: "evidence_chain_integrity"
      description: "Whether evidence_trace from each module forms a complete chain"
      example: "M46 has structured evidence_trace, but M48 only has boolean fields — potential gap in detail"
    - dimension: "amplification_accumulation"
      description: "Number of unmitigated propagation steps in sequence"
      example: "trust_transfer (unmitigated) + context_transfer (unmitigated) → 2-step amplification"
    - dimension: "attenuation_availability"
      description: "Whether control nodes (human_review_gate, boundary_preservation, etc.) exist for each step"
      example: "M47 has command_boundary_preserved attenuation available, but M43 has no equivalent control"
  degradation_levels:
    - level: "low"
      description: "0-1 consecutive boundary gaps, strong attenuation availability"
    - level: "medium"
      description: "2-3 consecutive boundary gaps, partial attenuation"
    - level: "high"
      description: "4+ consecutive boundary gaps, no effective attenuation"
  conceptual_only: true
  executable: false
```

## 6. Output Report Schema

### 6.1 Defense Degradation Trajectory Report

```yaml
defense_degradation_trajectory_report:
  report_id: "<SIM_REPORT_ID>"
  explorer_version: "v3.0-design-gate"
  conceptual_only: true
  executable: false
  contains_no_real_data: true
  requires_human_review: true

  composed_chain:
    chain_id: "<SIM_CHAIN_ID>"
    entry_point:
      source_module: "<MXX>"
      brt_reference: "BRT-XXX"
      entry_id: "<entry_id>"
    propagation_steps:
      - step: 1
        source_module: "<MXX>"
        target_module: "<MXX>"
        edge_type: "<edge_type_from_schema>"
        rule_probe_applied: "<probe_type>"
        probe_result: "<satisfied | unsatisfied | inconclusive>"
        evidence_trace_ref: "<module execution evidence reference>"
      - step: 2
        ...
    target_module: "<MXX>"

  degradation_assessment:
    boundary_coverage_gaps: <count>
    evidence_chain_gaps: <count>
    amplification_accumulation: <count>
    attenuation_available: <count>
    overall_degradation_level: "<low | medium | high>"

  human_review_notes:
    - "<human review finding 1>"
    - "<human review finding 2>"

  safety_fields:
    confirmed_vulnerability: false
    formal_finding_allowed: false
    production_safety_claimed: false
    controlled_replay_claimed: false
    controlled_replay_execution_allowed: false
    replay_executable: false
```

## 7. Conceptual Chain Examples

### 7.1 Supply Chain → Dev Environment Chain

```
Conceptual chain composed from:
  Entry point: M43 tool descriptor poisoning (BRT candidate reference)
  Step 1: M43 → M46 via context_influence edge
    Rule probe: trust_transfer_probe — Does poisoned descriptor trust carry to repo context?
  Step 2: M46 → M47 via context_influence edge
    Rule probe: context_transfer_probe — Does injected repo context influence command decisions?
  Attenuation available at M47: command_boundary_preserved
  Overall degradation: depends on whether M46/M47 boundary defenses held in execution
```

### 7.2 RAG → Runtime Chain

```
Conceptual chain composed from:
  Entry point: M48 RAG poisoned document (BRT candidate reference)
  Step 1: M48 → M49 via permission_dependency edge
    Rule probe: permission_transfer_probe — Does poisoned content bypass permission check?
  Step 2: M49 → M50 via runtime_dependency edge
    Rule probe: retrieval_transfer_probe — Does bypassed RAG content reach runtime?
  Attenuation available at M50: audit_chain_complete, controlled_replay_gate
  Overall degradation: depends on M49 permission boundary and M50 audit integrity
```

## 8. Human Review Integration

```yaml
human_review_integration:
  required: true
  purpose: >
    Every composed attack chain requires human review before any further action.
    The explorer is a design discussion tool that surfaces candidate chains for
    human evaluation — not an automated decision system.
  human_review_checkpoints:
    - checkpoint: "start_point_selection"
      description: "Human confirms the BRT candidate or module entry as a valid starting point"
    - checkpoint: "chain_composition"
      description: "Human reviews the composed module sequence for plausibility"
    - checkpoint: "probe_results"
      description: "Human evaluates each rule probe result for correctness"
    - checkpoint: "degradation_assessment"
      description: "Human validates the overall degradation level assessment"
    - checkpoint: "report_output"
      description: "Human reviews the final trajectory report before any downstream use"
```

## 9. Evidence Trace Dependency

```yaml
evidence_trace_dependency:
  principle: >
    All composed chains reference existing evidence_trace from individual module
    evaluations. The explorer generates no new evidence and requires no new
    module execution.
  evidence_sources:
    M43: "entry-level boolean decision fields (descriptor_poisoning_detected, tool_metadata_untrusted, fake_tool_invocation_blocked)"
    M46: "structured evidence_trace arrays (4 records per entry with source/signal_type/content)"
    M47: "structured evidence_trace arrays (5 records per entry with source/signal_type/content)"
    M48: "entry-level boolean decision fields (rag_poisoning_detected, retrieved_content_untrusted, safe_summary_generated)"
    M49: "entry-level boolean decision fields (permission_boundary_preserved, restricted_retrieval_blocked, permission_decision_logged)"
    M50: "entry-level boolean decision fields (sandbox_boundary_preserved, audit_chain_consistent, controlled_replay_execution_blocked)"
  brt_candidate_evidence: "red_blue_purple_retest_mapping.yaml — 20 candidates with evidence_trace_ref and exploit_chain_steps"
  no_new_evidence_generated: true
  no_execution_required: true
```

## 10. Safety Field Requirements

```yaml
safety_fields:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  controlled_replay_claimed: false
  controlled_replay_execution_allowed: false
  replay_executable: false
  breakthrough_detected_semantics: "simulated_capability_signal_only"
  chain_plausibility_not_vulnerability: true
  degradation_level_not_severity: true
  composed_chain_not_attack_procedure: true
  requires_human_review_for_every_chain: true
```

## 11. Limitation Acknowledgment

```yaml
limitations:
  - limitation: "All chains are conceptual — no module execution was performed"
  - limitation: "BRT candidates are simulated candidates, not confirmed vulnerabilities"
  - limitation: "Evidence trace format variance (arrays vs boolean fields) limits cross-module comparison depth"
  - limitation: "Propagation rules are hypothetical — no empirical validation was performed"
  - limitation: "Degradation levels are qualitative concepts without quantitative calibration"
  - limitation: "The explorer does not replace per-module deep-dive evaluation"
  - limitation: "Attack chains must not be interpreted as exploit procedures"
```

## 12. Forbidden Uses

- This blueprint must NOT be used to construct executable attack chains.
- Composed chains are conceptual only and must carry `executable: false`.
- Explorer logic must NOT contain real endpoints, credentials, commands, or payloads.
- Degradation levels must NOT be interpreted as vulnerability severity scores.
- Composed chains must NOT be treated as formal findings.
- This blueprint must NOT be used as input to capability_engine execution.
- This blueprint must NOT be used as input to controlled replay execution.
- All references to module results preserve `simulated_capability_signal_only` semantics.
- The explorer must NOT be used to automate vulnerability discovery without human review.
- Composed chains must NOT be used for production risk quantification.
