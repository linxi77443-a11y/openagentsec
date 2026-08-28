# Automated Attack Chain Discovery & Risk Analysis Framework — Design Gate

## 1. Purpose and Scope

This document defines a conceptual blueprint for an Automated Attack Chain Discovery & Risk Analysis Framework. The framework would integrate inputs from Phase 74A (attack graph schema, risk propagation model), Phase 75A (cross-module path catalog), Phase 76A (automated explorer blueprint), and Phase 63A (20 BRT candidates) to form a cohesive "path generation → simulation planning → signal collection design → defense degradation analysis → report generation" conceptual workflow.

**This is a design gate artifact only** — no executable code, no scripts, no implementation, no execution. The framework remains a conceptual blueprint for future human review and planning.

## 2. Non-Execution Boundary

- `executable: false` for all framework components
- `conceptual_component: true` for all framework components
- `implementation_allowed_in_phase78a: false` for all framework components
- No implementation code, no scripts, no executable automation
- No real endpoints, credentials, commands, or payloads
- No capability_engine execution
- No controlled replay execution
- All framework IDs use `<SIM_FRAMEWORK_ID>` placeholders
- All component schemas are conceptual only — not executable configurations

## 3. Framework Conceptual Architecture

```yaml
framework_architecture:
  framework_id: "<SIM_FRAMEWORK_ID>"
  version: "v3.0-design-gate"
  design_gate_only: true
  framework_blueprint_only: true
  executable: false
  components:
    - Attack Graph Schema Provider
    - Risk Propagation Model Provider
    - Path Catalog Provider
    - BRT Candidate Provider
    - Explorer Planner
    - Workflow Planner
    - Simulation Plan Builder
    - Signal Collection Planner
    - Defense Degradation Analyzer
    - Report Schema Generator
    - Human Review Gate
  input_sources: []
  workflow_stages: []
```

## 4. Input Sources and Read-Only References

```yaml
input_sources:
  - source_id: "phase74a_attack_graph_schema"
    path: "docs/cross_module_attack_graph_schema.md"
    provides:
      - "7 node types (module_node, boundary_node, artifact_node, signal_node, control_node, evidence_node, layer_node)"
      - "9 edge types (context_influence, trust_boundary_transfer, permission_dependency, evidence_dependency, audit_dependency, runtime_dependency, amplification_edge, mitigation_edge, review_gate_edge)"
      - "4 layers (supply_chain, development_environment, rag_data, runtime_sandbox)"
      - "Safety field requirements"
    read_only: true

  - source_id: "phase74a_risk_propagation_model"
    path: "docs/risk_propagation_model.md"
    provides:
      - "4 propagation layers with module mapping"
      - "7 propagation rule types (trust_transfer, context_transfer, permission_transfer, credential_exposure_transfer, retrieval_transfer, audit_trace_transfer, runtime_policy_transfer)"
      - "Risk amplification factor concept (conceptual_only, not_production_risk, not_vulnerability_severity)"
      - "5 attenuation factors"
      - "4 boundary preservation rules"
      - "3 conceptual propagation patterns"
    read_only: true

  - source_id: "phase75a_cross_module_path_catalog"
    path: "docs/cross_module_attack_path_catalog.md"
    provides:
      - "8 conceptual paths with path_id, edge_sequence, involved_modules, involved_layers"
      - "Evidence trace reference design for each path"
      - "Conceptual risk amplification notes per path"
      - "Attenuation factors per path"
    read_only: true

  - source_id: "phase76a_explorer_blueprint"
    path: "docs/automated_cross_module_attack_chain_explorer_design.md"
    provides:
      - "Explorer logic concepts (start_point_selection, path_composition, rule_probe_insertion, defense_degradation_assessment)"
      - "Output report schema (defense_degradation_trajectory_report)"
      - "Human review integration checkpoints"
    read_only: true

  - source_id: "phase63a_brt_candidates"
    path: "red_blue_purple_retest_mapping.yaml"
    provides:
      - "20 breakthrough candidates (BRT-001 to BRT-020)"
      - "Per-candidate: breakthrough_type, affected_boundary, evidence_trace_ref, exploit_chain_steps"
      - "10 source playbooks across multiple attacker profiles"
    read_only: true

  - source_id: "existing_module_results"
    modules:
      - "M43 — MCP Tool Descriptor Integrity (Phase 66A, mvp_complete)"
      - "M46 — Coding Agent Repository Context Injection (Phase 72A, mvp_complete)"
      - "M47 — Coding Agent Command and Credential Boundary (Phase 71A, mvp_complete)"
      - "M48 — RAG Document Poisoning and Instruction Boundary (Phase 67A, mvp_complete)"
      - "M49 — RAG Permission Inheritance and Retrieval Audit (Phase 69A, mvp_complete)"
      - "M50 — Agent Runtime Sandbox and Audit Chain Integrity (Phase 68A, mvp_complete)"
    provides:
      - "Per-module evidence_trace (boolean decision fields or structured arrays)"
      - "Per-module scorecard (capability_value, risk_level — simulated only)"
      - "Per-module safety field declarations"
    read_only: true
```

## 5. Component Interaction Model

```yaml
components:

  - component_id: "attack_graph_schema_provider"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Provides the attack graph type system (nodes, edges, layers) to other components"
    input_references:
      - "docs/cross_module_attack_graph_schema.md"
    output_concept: "Typed graph schema with node/edge/layer definitions"
    connected_to:
      - "Workflow Planner"
      - "Path Generation Stage"

  - component_id: "risk_propagation_model_provider"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Provides the risk propagation rule types, amplification factor concept, and attenuation factors"
    input_references:
      - "docs/risk_propagation_model.md"
    output_concept: "Propagation rule catalog with layer ordering"
    connected_to:
      - "Workflow Planner"
      - "Defense Degradation Analyzer"

  - component_id: "path_catalog_provider"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Provides the pre-defined conceptual cross-module paths as composition templates"
    input_references:
      - "docs/cross_module_attack_path_catalog.md"
    output_concept: "Path catalog with 8 conceptual path entries"
    connected_to:
      - "Workflow Planner"
      - "Path Generation Stage"

  - component_id: "brt_candidate_provider"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Provides the 20 BRT candidates as read-only entry point candidates"
    input_references:
      - "red_blue_purple_retest_mapping.yaml"
    output_concept: "BRT candidate list with breakthrough signals and evidence trace refs"
    connected_to:
      - "Explorer Planner"
      - "Path Generation Stage"

  - component_id: "explorer_planner"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Provides explorer logic concepts (start point selection, path composition, rule probe insertion)"
    input_references:
      - "docs/automated_cross_module_attack_chain_explorer_design.md"
    output_concept: "Exploration plan concept with selection criteria and composition rules"
    connected_to:
      - "Workflow Planner"
      - "Path Generation Stage"

  - component_id: "workflow_planner"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Orchestrates the overall workflow by coordinating all other components"
    input_references:
      - "All provider components"
    output_concept: "Orchestrated workflow plan across path generation, simulation planning, signal collection, degradation analysis, and report generation"
    connected_to:
      - "All components"

  - component_id: "simulation_plan_builder"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Designs a future simulation plan that describes what simulated execution would look like — does not execute anything"
    input_references:
      - "Path Catalog Provider"
      - "Explorer Planner"
    output_concept: "Conceptual simulation plan describing future execution scope, parameters, and expected signals"
    connected_to:
      - "Workflow Planner"
      - "Signal Collection Planner"

  - component_id: "signal_collection_planner"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Defines what signals would need to be collected during future simulated execution"
    input_references:
      - "Risk Propagation Model Provider"
      - "Existing module evidence_trace"
    output_concept: "Signal collection specification — describes signal types, sources, and collection points for future phases"
    connected_to:
      - "Workflow Planner"
      - "Defense Degradation Analyzer"

  - component_id: "defense_degradation_analyzer"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Analyzes how defensive effectiveness degrades across module boundaries in a conceptual chain"
    input_references:
      - "Risk Propagation Model Provider"
      - "Signal Collection Planner"
      - "Existing module evidence_trace"
    output_concept: "Defense degradation trajectory assessment with degradation factors and boundary preservation points"
    connected_to:
      - "Workflow Planner"
      - "Report Schema Generator"

  - component_id: "report_schema_generator"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Generates the defense degradation trajectory report schema (conceptual output only)"
    input_references:
      - "Defense Degradation Analyzer"
    output_concept: "Defense degradation trajectory report with all required fields"
    connected_to:
      - "Workflow Planner"
      - "Human Review Gate"

  - component_id: "human_review_gate"
    conceptual_component: true
    executable: false
    implementation_allowed_in_phase78a: false
    purpose: "Ensures all framework outputs pass through human review before any downstream use"
    input_references:
      - "Report Schema Generator"
    output_concept: "Human review decision record with reviewer_decision_placeholder"
    connected_to:
      - "Workflow Planner"
```

## 6. Workflow Engine Conceptual Design

See `docs/automated_attack_chain_workflow_engine_design.md` for the complete workflow engine conceptual design.

Workflow stages overview:

| Stage | Stage ID | Purpose | Execution in Phase 78A |
|-------|----------|---------|------------------------|
| 1 | Input Loading | Load all input sources and read-only references | false |
| 2 | Path Generation | Compose conceptual paths from catalog and graph | false |
| 3 | Simulation Planning | Design future simulation plan (no execution) | false |
| 4 | Rule Probe Insertion | Insert boundary-check and rule-probe concepts | false |
| 5 | Signal Collection Design | Define signals to collect in future execution | false |
| 6 | Defense Degradation Analysis | Assess control effectiveness across boundaries | false |
| 7 | Report Generation | Output defense degradation trajectory report | false |
| 8 | Human Review Gate | All candidates enter human review | false |

## 7. Path Generation Stage

```yaml
path_generation_stage:
  stage_id: "path_generation"
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false
  purpose: >
    Combine the Phase 75A path catalog with the Phase 74A attack graph schema
    and BRT candidate entry points to generate conceptual cross-module paths
    for further analysis.
  input_references:
    - "docs/cross_module_attack_path_catalog.md (8 conceptual paths)"
    - "docs/cross_module_attack_graph_schema.md (7 node types, 9 edge types)"
    - "red_blue_purple_retest_mapping.yaml (20 BRT candidates as entry points)"
  output_concept: "Expanded set of conceptual paths with BRT candidate entry point annotations"
  examples_of_conceptual_generation:
    - "Select BRT candidate → match against path catalog entry point module → annotate path with candidate_id"
    - "Select path from catalog → verify edge types against graph schema → confirm edge compatibility"
    - "Annotate each path step with expected evidence_trace reference from existing module results"
```

## 8. Simulation Planning Stage

```yaml
simulation_planning_stage:
  stage_id: "simulation_planning"
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false
  purpose: >
    Design a conceptual simulation plan that describes what a future simulated
    execution would look like. This is not an execution plan — it is a planning
    artifact for future human review.
  input_references:
    - "Phase 76A explorer blueprint (start_point_selection, path_composition concepts)"
    - "Path generation stage output (conceptual paths with BRT annotations)"
  output_concept: "Simulation plan concept with scope, parameters, and expected signal descriptions"
  conceptual_plan_elements:
    - "Simulation scope description (which path segments would be executed conceptually)"
    - "Expected signal descriptions per path step"
    - "Boundary conditions to test"
    - "Control case descriptions for comparison"
  non_execution_confirmations:
    - "No actual simulation is executed in Phase 78A"
    - "No capability_engine invocation"
    - "No execution_results generation"
    - "No corpus creation"
```

## 9. Signal Collection Design

```yaml
signal_collection_design:
  stage_id: "signal_collection_design"
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false
  purpose: >
    Define what simulated signals would need to be collected during a future
    execution of the conceptual path. This is a design for future signal
    collection, not an actual collection plan.
  input_references:
    - "Existing module evidence_trace (M43/M46/M47/M48/M49/M50)"
    - "Risk propagation model (7 rule types)"
  output_concept: "Signal collection specification describing signal types, sources, and collection points"
  signal_types_to_design:
    - "Boundary enforcement signals (blocked/allowed per module)"
    - "Evidence trace signals (boolean decision fields, structured trace records)"
    - "Propagation signals (signal transition across module boundaries)"
    - "Attenuation signals (control effectiveness indicators)"
  collection_design_elements:
    - "Per-module signal mapping (which signals each module can produce)"
    - "Cross-module signal transition design (how signals conceptually transfer)"
    - "Missing signal gap analysis (which signals are not available)"
```

## 10. Defense Degradation Analysis Model

```yaml
defense_degradation_analysis:
  stage_id: "defense_degradation_analysis"
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false
  purpose: >
    Analyze how defensive effectiveness degrades as a hypothetical attack
    chain progresses across module boundaries. This is a conceptual analysis
    model, not a quantitative scoring system.
  input_references:
    - "Risk propagation model (amplification factor concept, attenuation factors)"
    - "Signal collection design output"
    - "Existing module evidence_trace"
  output_concept: "Defense degradation trajectory with degradation factors, boundary preservation points, and missing control hypotheses"
  analysis_dimensions:
    - dimension: "boundary_coverage_consistency"
      description: "Whether each module in the path has a defensive boundary that was tested"
      evaluation_concept: "Compare per-module evidence_trace against expected signals for the path"
    - dimension: "signal_transition_integrity"
      description: "Whether signals from upstream modules are preserved in downstream modules"
      evaluation_concept: "Examine signal continuity across edge_sequence transitions"
    - dimension: "attenuation_availability"
      description: "Whether control mechanisms exist at critical boundary crossings"
      evaluation_concept: "Map attenuation factors from propagation model to each path step"
    - dimension: "missing_control_identification"
      description: "Identify path steps where no control mechanism is available"
      evaluation_concept: "Gap analysis between required controls and available attenuation factors"
  degradation_trajectory_levels:
    - level: "minimal_degradation"
      description: "All boundaries have available controls, signal continuity is complete"
    - level: "partial_degradation"
      description: "Some boundaries lack controls or signal gaps exist"
    - level: "significant_degradation"
      description: "Multiple consecutive boundaries without controls, signal chain broken"
```

## 11. Report Generation Stage

```yaml
report_generation_stage:
  stage_id: "report_generation"
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false
  purpose: >
    Generate the defense degradation trajectory report schema. The report
    captures the full analysis output including path details, degradation
    assessment, and human review placeholders.
  input_references:
    - "Defense degradation analysis output"
    - "Path generation stage output"
  output_concept: "Defense degradation trajectory report with all required fields"
  output_schema_reference: "docs/defense_degradation_trajectory_report_schema.md"
```

## 12. Human Review Gate

```yaml
human_review_gate:
  required: true
  purpose: >
    Every framework output requires human review before any downstream use.
    The framework is a design discussion tool — not an automated decision system.
  what_human_review_covers:
    - "Path plausibility assessment — does the conceptual path make sense?"
    - "Simulation plan review — is the future execution scope appropriate?"
    - "Signal collection design review — are the right signals being targeted?"
    - "Defense degradation assessment review — is the trajectory analysis reasonable?"
    - "Report accuracy review — does the report correctly reflect the analysis?"
    - "Safety field confirmation — all security fields confirmed false"
    - "Non-execution boundary confirmation — framework remains conceptual only"
  human_review_checkpoints:
    - checkpoint: "after_path_generation"
      description: "Human reviews generated paths before simulation planning"
    - checkpoint: "after_simulation_planning"
      description: "Human reviews simulation plan before signal collection design"
    - checkpoint: "after_degradation_analysis"
      description: "Human reviews degradation assessment before report generation"
    - checkpoint: "after_report_generation"
      description: "Human reviews final report before any downstream use"
```

## 13. Evidence Reference Model

```yaml
evidence_reference_model:
  principle: "All framework components reference existing evidence_trace from individual module evaluations. No new evidence is generated."
  existing_evidence_trace:
    M43:
      format: "entry-level boolean decision fields"
      phase: "66A"
      key_fields: ["descriptor_poisoning_detected", "tool_metadata_untrusted", "fake_tool_invocation_blocked"]
    M46:
      format: "structured evidence_trace array (4 records per entry)"
      phase: "72A"
      key_fields: ["synthetic_repo_id", "repo_context_trust_decision", "instruction_boundary_decision"]
    M47:
      format: "structured evidence_trace array (5 records per entry)"
      phase: "71A"
      key_fields: ["command_integrity_decision", "credential_boundary_decision", "permission_confusion_decision"]
    M48:
      format: "entry-level boolean decision fields"
      phase: "67A"
      key_fields: ["rag_poisoning_detected", "retrieved_content_untrusted", "safe_summary_generated"]
    M49:
      format: "entry-level boolean decision fields"
      phase: "69A"
      key_fields: ["permission_boundary_preserved", "restricted_retrieval_blocked", "permission_decision_logged"]
    M50:
      format: "entry-level boolean decision fields"
      phase: "68A"
      key_fields: ["sandbox_boundary_preserved", "audit_chain_consistent", "controlled_replay_execution_blocked"]
  brt_candidate_evidence:
    source: "red_blue_purple_retest_mapping.yaml"
    format: "20 breakthrough candidates with evidence_trace_ref and exploit_chain_steps"
  no_new_evidence_generated: true
```

## 14. Safety Field Requirements

```yaml
safety_fields:
  framework_design:
    confirmed_vulnerability: false
    formal_finding_allowed: false
    production_safety_claimed: false
    controlled_replay_claimed: false
    controlled_replay_execution_allowed: false
    replay_executable: false
  workflow_design:
    confirmed_vulnerability: false
    formal_finding_allowed: false
    production_safety_claimed: false
  report_schema:
    confirmed_vulnerability: false
    formal_finding_allowed: false
    production_safety_claimed: false
  breakthrough_detected_semantics: "simulated_capability_signal_only"
  defense_degradation_trajectory_is_not_exploit_chain: true
  framework_output_is_human_review_candidate_only: true
```

## 15. Forbidden Uses

- This framework blueprint must NOT be used to construct executable attack chains.
- All framework components remain conceptual only — no implementation is permitted in this phase.
- Framework components must NOT contain real endpoints, credentials, commands, or payloads.
- `defense_degradation_trajectory` is a qualitative design concept — NOT a vulnerability severity, NOT a production risk score, NOT an exploitability score.
- Framework outputs must NOT be treated as formal findings.
- This blueprint must NOT be used as input to capability_engine execution.
- This blueprint must NOT be used as input to controlled replay execution.
- All references to v2.0 module results preserve `simulated_capability_signal_only` semantics.
- Component interaction descriptions must NOT be interpreted as executable architecture.
- Workflow stage descriptions must NOT be interpreted as implementation specifications.
- The framework must NOT be used to automate vulnerability discovery without human review.

## 16. Future Phase Boundary

```yaml
future_phase_boundary:
  phase78a_deliverables:
    - "Framework blueprint design (this document)"
    - "Workflow engine conceptual design"
    - "Defense degradation trajectory report schema"
    - "Design gate notes"
    - "Non-executable markdown checklist"
    - "Design gate result"
  what_phase78a_does_not_include:
    - "No executable code or scripts"
    - "No framework implementation"
    - "No explorer implementation"
    - "No workflow engine implementation"
    - "No corpus or run_config creation"
    - "No capability_engine execution"
    - "No execution_results generation"
    - "No controlled replay"
    - "No real system connection"
  recommended_next_phase: "Phase 78B — Framework Blueprint Refinement"
  next_execution_phase: "Requires separate task card and human approval"
  controlled_replay_requires_separate_approval: true
```
