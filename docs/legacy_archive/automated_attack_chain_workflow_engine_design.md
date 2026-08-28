# Automated Attack Chain Workflow Engine — Conceptual Design

## 1. Purpose and Scope

This document defines a conceptual workflow engine design for the Automated Attack Chain Discovery & Risk Analysis Framework. The workflow engine describes how input sources, components, and analysis stages would conceptually interact to produce a defense degradation trajectory report.

**This is a design gate artifact only** — no executable code, no scripts, no implementation, no execution. The workflow engine remains a conceptual blueprint for future human review and planning.

## 2. Non-Execution Boundary

- All workflow stages: `executable: false`, `code_generated: false`, `payload_generated: false`, `real_system_connection: false`
- No workflow engine implementation
- No explorer implementation
- No capability_engine execution
- No execution_results generation
- No controlled replay

## 3. Workflow Engine Conceptual Architecture

```yaml
workflow_engine:
  engine_id: "<SIM_WORKFLOW_ENGINE_ID>"
  version: "v3.0-design-gate"
  design_gate_only: true
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false
  workflow_stages: []
```

## 4. Workflow Stages

### Stage 1: Input Loading

```yaml
stage:
  stage_id: "input_loading"
  order: 1
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false

  purpose: >
    Load all input sources and read-only references into the workflow context.
    This stage establishes the knowledge base that all subsequent stages reference.

  input_references:
    - "docs/cross_module_attack_graph_schema.md — 7 node types, 9 edge types, 4 layers"
    - "docs/risk_propagation_model.md — 4 layers, 7 rule types, amplification/attenuation concepts"
    - "docs/cross_module_attack_path_catalog.md — 8 conceptual paths"
    - "docs/automated_cross_module_attack_chain_explorer_design.md — explorer logic concepts"
    - "red_blue_purple_retest_mapping.yaml — 20 BRT candidates"
    - "Per-module execution results and evidence_trace (M43/M46/M47/M48/M49/M50)"

  output_concept: >
    Workflow context initialized with all input sources loaded as read-only references.

  conceptual_actions:
    - action: "load_graph_schema"
      description: "Load the attack graph node types, edge types, and layer definitions"
    - action: "load_propagation_model"
      description: "Load propagation rule types, amplification factor concept, attenuation factors"
    - action: "load_path_catalog"
      description: "Load all 8 conceptual paths with edge sequences and evidence references"
    - action: "load_explorer_blueprint"
      description: "Load explorer logic concepts (start_point_selection, path_composition, rule_probe_insertion)"
    - action: "load_brt_candidates"
      description: "Load all 20 BRT candidates as conceptual entry points"
    - action: "load_module_evidence"
      description: "Load existing evidence_trace from all 6 v2.0 modules"
```

### Stage 2: Path Generation

```yaml
stage:
  stage_id: "path_generation"
  order: 2
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false

  purpose: >
    Generate conceptual cross-module paths by combining the path catalog,
    BRT candidate entry points, and attack graph schema validation.

  input_references:
    - "Path catalog (8 conceptual paths — Phase 75A)"
    - "BRT candidates (20 entry points — Phase 63A)"
    - "Attack graph schema (edge type validation — Phase 74A)"

  output_concept: >
    Annotated path list — each path enriched with BRT candidate entry point
    references and edge type compatibility confirmation.

  conceptual_actions:
    - action: "select_entry_point"
      description: "Select a BRT candidate or path from catalog as the starting point"
      example: "BRT-001 (direct prompt injection) maps to M46 as entry point"
    - action: "match_path_template"
      description: "Match the entry point module against path catalog entry points"
      example: "M46 entry matches PATH-DEV-CMD-001 (M46 → M47)"
    - action: "validate_edge_sequence"
      description: "For each step, confirm the edge type exists in the attack graph schema"
      example: "M46 → M47 uses context_influence edge — valid per schema"
    - action: "annotate_with_brt"
      description: "Annotate the generated path with the BRT candidate_id for traceability"
      example: "PATH-DEV-CMD-001 + BRT-001 annotation"
```

### Stage 3: Simulation Planning

```yaml
stage:
  stage_id: "simulation_planning"
  order: 3
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false

  purpose: >
    Design a conceptual simulation plan that describes what a future execution
    of the generated path would involve. This stage does not execute anything —
    it produces a planning artifact for future human review.

  input_references:
    - "Annotated path list from path generation stage"
    - "Explorer blueprint (start_point_selection, path_composition logic concepts)"

  output_concept: >
    Conceptual simulation plan describing future execution scope, parameters,
    expected signals, and boundary conditions.

  conceptual_actions:
    - action: "define_simulation_scope"
      description: "Describe which path segments would be executed in a future simulation"
    - action: "identify_boundary_conditions"
      description: "Identify which security boundaries each path step would test"
    - action: "describe_expected_signals"
      description: "Describe what signals each path step would be expected to produce"
    - action: "define_control_cases"
      description: "Describe control cases for comparison — what a benign path would look like"
```

### Stage 4: Rule Probe Insertion

```yaml
stage:
  stage_id: "rule_probe_insertion"
  order: 4
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false

  purpose: >
    Insert conceptual boundary-check and rule-probe points at each step of
    the generated path. Each probe assesses what propagation rule type would
    be tested and what defensive condition would need to be evaluated.

  input_references:
    - "Risk propagation model (7 rule types — Phase 74A)"
    - "Attack graph schema (edge types — Phase 74A)"
    - "Annotated path list from path generation stage"

  output_concept: >
    Path with rule probe annotations — each step has a probe type, conceptual
    evaluation question, and expected defensive condition.

  conceptual_actions:
    - action: "assign_probe_type"
      description: "For each edge in the path, assign the relevant propagation rule type as probe"
      example: "M43 → M46 (context_influence edge) → probe: trust_transfer"
    - action: "formulate_probe_question"
      description: "Formulate a conceptual question the probe would evaluate"
      example: "If M43 marks a tool descriptor as trusted, does M46 inherit that trust without re-validation?"
    - action: "identify_evaluation_condition"
      description: "Identify the defensive condition that would determine probe outcome"
      example: "M46 instruction_boundary_decision == 'blocked' means probe is satisfied (boundary holds)"
```

### Stage 5: Signal Collection Design

```yaml
stage:
  stage_id: "signal_collection_design"
  order: 5
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false

  purpose: >
    Define what simulated signals would need to be collected during a future
    execution of the path. This is a design for future collection —
    no actual signal collection occurs in this phase.

  input_references:
    - "Existing module evidence_trace (M43/M46/M47/M48/M49/M50)"
    - "Rule probe annotations from rule probe insertion stage"
    - "Risk propagation model (7 rule types)"

  output_concept: >
    Signal collection specification describing what signals to collect,
    from which module sources, and at which path steps.

  conceptual_actions:
    - action: "map_signals_to_modules"
      description: "For each module in the path, list the available evidence_trace signals"
    - action: "design_signal_transition"
      description: "Describe how a signal from one module conceptually transitions to the next"
    - action: "identify_signal_gaps"
      description: "Identify path steps where expected signals are not available from existing evidence_trace"
    - action: "specify_collection_points"
      description: "Define at which path steps signal collection would occur in future execution"
```

### Stage 6: Defense Degradation Analysis

```yaml
stage:
  stage_id: "defense_degradation_analysis"
  order: 6
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false

  purpose: >
    Analyze how defensive effectiveness degrades across the generated path.
    Assess boundary coverage consistency, signal transition integrity,
    attenuation availability, and missing control hypotheses.

  input_references:
    - "Signal collection design output"
    - "Risk propagation model (amplification factor concept, attenuation factors)"
    - "Existing module evidence_trace"

  output_concept: >
    Defense degradation trajectory assessment with degradation factors,
    boundary preservation points, and missing control hypotheses.

  conceptual_actions:
    - action: "assess_boundary_coverage"
      description: "For each path step, check whether a boundary enforcement signal exists"
      evaluation: "M46 instruction_boundary_decision available — coverage confirmed"
    - action: "trace_signal_integrity"
      description: "Trace each signal across path steps — is the signal chain complete?"
      evaluation: "M43 → M46 signal available, M46 → M47 signal available — chain intact"
    - action: "evaluate_attenuation"
      description: "Map available attenuation factors to each path step"
      evaluation: "M47 has command_boundary_preserved — attenuation available"
    - action: "identify_missing_controls"
      description: "Identify path steps where no control or attenuation is available"
      evaluation: "M43 has no equivalent boundary preservation control — potential gap"
    - action: "assign_degradation_level"
      description: "Assign a conceptual degradation level based on the assessment"
      evaluation: "minimal_degradation — all boundaries have controls"
```

### Stage 7: Report Generation

```yaml
stage:
  stage_id: "report_generation"
  order: 7
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false

  purpose: >
    Generate the defense degradation trajectory report based on the analysis
    from all previous stages. The report captures the full analysis output
    in a structured schema.

  input_references:
    - "Defense degradation analysis output"
    - "Annotated path list"
    - "Signal collection design"
    - "Rule probe annotations"
    - "Simulation plan"

  output_concept: >
    Defense degradation trajectory report with all required fields
    (see docs/defense_degradation_trajectory_report_schema.md).

  conceptual_actions:
    - action: "compile_path_information"
      description: "Aggregate all path details (path_id, modules, layers, edge_sequence)"
    - action: "compile_analysis_results"
      description: "Aggregate degradation analysis (degradation factors, boundary points, missing controls)"
    - action: "compile_evidence_references"
      description: "Aggregate evidence reference map with per-module signal references"
    - action: "generate_report_document"
      description: "Assemble all components into the final report structure"
```

### Stage 8: Human Review Gate

```yaml
stage:
  stage_id: "human_review_gate"
  order: 8
  phase78a_execution_allowed: false
  executable: false
  code_generated: false
  payload_generated: false
  real_system_connection: false

  purpose: >
    All workflow outputs must pass through human review before any downstream
    use. The human review gate ensures that conceptual analysis is not
    mistaken for confirmed findings.

  input_references:
    - "Defense degradation trajectory report from report generation stage"

  output_concept: >
    Human review decision record with reviewer decision, comments, and
    next-action recommendations.

  conceptual_actions:
    - action: "submit_for_review"
      description: "Submit the generated report for human review"
    - action: "record_reviewer_decision"
      description: "Record the human reviewer's decision (approve/reject/amend)"
    - action: "check_safety_fields"
      description: "Confirm all safety fields remain false after review"
    - action: "determine_next_action"
      description: "Based on review, determine next action (archive, refine, proceed to next phase)"

  reviewer_decision_placeholder:
    status: "pending_review"
    reviewed_by: null
    review_date: null
    reviewer_comments: null
    next_action: null
```

## 5. Workflow State Diagram (Conceptual)

```text
[Input Loading] → [Path Generation] → [Simulation Planning]
                                              ↓
[Report Generation] ← [Degradation Analysis] ← [Signal Collection Design]
        ↓                                       ↑
        ↓                              [Rule Probe Insertion]
        ↓
[Human Review Gate] → [Output: Defense Degradation Trajectory Report]
```

All stages are conceptual only. No execution, no implementation, no code generation.

## 6. Data Flow Concept

```yaml
data_flow_concepts:
  - flow: "input_loading → path_generation"
    data: "Loaded input sources (graph schema, path catalog, BRT candidates, evidence_trace)"
    transformation: "Input sources are combined into annotated path list"

  - flow: "path_generation → simulation_planning"
    data: "Annotated path list with BRT candidate references"
    transformation: "Path list informs simulation scope and boundary conditions"

  - flow: "simulation_planning → rule_probe_insertion"
    data: "Simulation plan with scope and boundary conditions"
    transformation: "Boundary conditions inform rule probe type assignment"

  - flow: "rule_probe_insertion → signal_collection_design"
    data: "Path with rule probe annotations"
    transformation: "Probe types inform what signals should be collected"

  - flow: "signal_collection_design → defense_degradation_analysis"
    data: "Signal collection specification"
    transformation: "Collected signal design informs degradation assessment"

  - flow: "defense_degradation_analysis → report_generation"
    data: "Degradation assessment with factors and boundary points"
    transformation: "Assessment data populates report fields"

  - flow: "report_generation → human_review_gate"
    data: "Complete defense degradation trajectory report"
    transformation: "Report is submitted for human review"
```

## 7. Safety Field Assertions

```yaml
safety_field_assertions:
  all_stages:
    phase78a_execution_allowed: false
    executable: false
    code_generated: false
    payload_generated: false
    real_system_connection: false
  workflow_engine:
    confirmed_vulnerability: false
    formal_finding_allowed: false
    production_safety_claimed: false
    controlled_replay_claimed: false
    controlled_replay_execution_allowed: false
    replay_executable: false
  breakthrough_detected_semantics: "simulated_capability_signal_only"
  conceptual_path_not_exploit_chain: true
  workflow_output_is_human_review_candidate_only: true
```

## 8. Forbidden Uses

- This workflow engine design must NOT be used to construct executable workflow implementations.
- All workflow stages remain conceptual — no implementation is permitted in this phase.
- Workflow stage descriptions must NOT be interpreted as executable algorithms.
- Data flow descriptions must NOT be interpreted as implementation specifications.
- This design must NOT be used as input to capability_engine execution.
- This design must NOT be used as input to controlled replay execution.
- Workflow outputs must NOT be treated as formal findings.
- All references to module evidence preserve `simulated_capability_signal_only` semantics.
