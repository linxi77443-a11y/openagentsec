# Phase 83A — Unified Attack Intelligence Theory Model Review Checklist MVP

## 1. Purpose and Scope

This document defines a structured review checklist for the Phase 82A Unified Attack Intelligence Theory Model. The checklist covers four review dimensions:

1. **Equation Consistency Review** — verify 3 core conceptual equations (P_edge, D_node, G_path)
2. **Weight Factor Semantic Review** — verify 6 pattern-derived weight factors
3. **Calibration Method Review** — verify 5 calibration targets against Phase 79A/80A data
4. **Safety Semantics Review** — verify all conceptual_only, not_production_risk, not_vulnerability_severity, requires_human_review declarations

**This is a tabletop review checklist only** — not executable logic, not automated validation, not a model execution system. All review items are conceptual and require human review.

## 2. Tabletop Review Boundary

```yaml
tabletop_review_boundary:
  tabletop_review_checklist_only: true
  conceptual_only: true
  executable: false
  attack_execution_allowed: false
  controlled_replay_execution_allowed: false
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true

  review_scope:
    - "Equation variable completeness and source mapping"
    - "Weight factor semantic alignment with Phase 81A patterns"
    - "Calibration target alignment with Phase 79A/80A tabletop observations"
    - "Safety semantics presence and correctness"

  review_exclusions:
    - "NOT model execution or numerical computation"
    - "NOT automated validation"
    - "NOT vulnerability assessment"
    - "NOT production risk evaluation"
    - "NOT formal finding generation"
```

## 3. Source Artifacts

```yaml
source_artifacts:
  phase_82a_theory_model:
    documents:
      - "docs/unified_attack_intelligence_theory_model.md"
      - "docs/attack_intelligence_model_fusion_design.md"
      - "docs/attack_propagation_equation_design.md"
      - "docs/attack_intelligence_weight_factor_design.md"
      - "docs/tabletop_model_validation_calibration_method.md"
    provides_for_review:
      - "3 core equations with variable definitions"
      - "6 weight factors with source patterns"
      - "5 calibration targets with validation questions"
      - "4-layer fusion architecture"

  phase_74a_attack_graph:
    documents:
      - "docs/cross_module_attack_graph_schema.md"
      - "docs/risk_propagation_model.md"
    provides_for_review:
      - "Node/edge/path/layer definitions (structural alignment)"

  phase_77a_dynamics:
    documents:
      - "docs/attack_graph_dynamics_model.md"
      - "docs/node_defense_state_evolution_model.md"
      - "docs/attack_graph_feedback_loop_model.md"
    provides_for_review:
      - "Attenuation/amplification/blocking/recovery rules (dynamics alignment)"

  phase_79a_tabletop:
    documents:
      - "reports/phase79a_path_supply_dev_rag_runtime_tabletop_analysis.md"
      - "reports/phase79a_defense_degradation_trajectory_report.md"
    provides_for_review:
      - "Node state timeline (5 steps, 5 modules)"
      - "Edge propagation observations"
      - "Trajectory: partial_degradation"

  phase_80a_tabletop:
    documents:
      - "reports/phase80a_path_dev_cred_runtime_tabletop_analysis.md"
      - "reports/phase80a_path_rag_runtime_tabletop_analysis.md"
      - "reports/phase80a_multi_path_defense_degradation_comparison.md"
    provides_for_review:
      - "Two shorter path observations"
      - "Cross-path comparison (12 dimensions)"
      - "M47 vs M49 attenuation comparison"

  phase_81a_pattern_library:
    documents:
      - "reports/phase81a_cross_module_attack_pattern_library.md"
      - "docs/cross_module_attack_pattern_index.md"
      - "docs/cross_module_path_pattern_association_matrix.md"
      - "docs/cross_module_module_pattern_association_matrix.md"
    provides_for_review:
      - "8 patterns with lifecycle status"
      - "Pattern-to-path/module mapping"
```

## 4. Checklist Object Model

Each review item uses the following schema:

```yaml
checklist_item:
  item_id: "<CXX-XXX>"
  review_dimension: "equation_consistency | weight_factor_semantic | calibration_method | safety_semantics"
  source_reference: "<source document path>"
  expected_condition: "<what the reviewer should verify>"
  reviewer_observation: "<placeholder for reviewer notes>"
  review_status_placeholder: "pending | pass | needs_revision | not_applicable"
  human_review_required: true
  conceptual_only: true
  not_production_risk: true
  not_vulnerability_severity: true
```

## 5. Equation Consistency Review Overview

```yaml
equation_consistency_review_overview:
  description: >
    Verify that the 3 core conceptual equations have complete variable definitions,
    traceable source mappings, and logical consistency with the Phase 74A/77A/79A/
    80A/81A artifacts.
  total_equations: 3
  review_file: "docs/phase83a_equation_consistency_review_checklist.md"
  equations:
    - "EQ-EDGE-PROPAGATION-001: P_edge(t) = S_source(t) × W_edge × A_pattern × F_feedback × (1 - D_target)"
    - "EQ-NODE-STATE-001: D_node(t+1) = clamp(D_node(t) + R_control - P_in(t) × V_node + H_review)"
    - "EQ-PATH-DEGRADATION-001: G_path = Σ P_edge(t) × (1 + A_seq) - Σ A_attenuation + Σ A_amplification - Σ B_blocking"
```

## 6. Weight Factor Semantic Review Overview

```yaml
weight_factor_semantic_review_overview:
  description: >
    Verify that the 6 weight factors have correct source pattern mappings, complete
    field definitions, appropriate conceptual direction and range, and traceable
    calibration sources.
  total_weights: 6
  review_file: "docs/phase83a_weight_factor_semantic_review_checklist.md"
  weight_factors:
    - "W-ENTRY-VULN-001: upstream_entry_vulnerability_factor"
    - "W-M50-AUDIT-DAMP-001: m50_audit_damping_weight"
    - "W-M50-SB-BLOCK-001: m50_sandbox_boundary_weight"
    - "W-CRED-ATTEN-001: credential_boundary_attenuation_weight"
    - "W-PERM-AMPL-001: permission_leakage_amplification_weight"
    - "W-HRG-BREAK-001: human_review_breakpoint_weight"
```

## 7. Calibration Method Review Overview

```yaml
calibration_method_review_overview:
  description: >
    Verify that the 5 calibration targets reference correct Phase 79A/80A tabletop
    observations, cover the required trajectory fields, and include appropriate
    validation questions and human review gates.
  total_targets: 5
  review_file: "docs/phase83a_calibration_method_review_checklist.md"
  calibration_targets:
    - "CAL-PROPAGATION-001: propagation_pressure_consistency"
    - "CAL-ATTENUATION-001: attenuation_node_consistency"
    - "CAL-M50-DAMPING-001: m50_damping_consistency"
    - "CAL-ENTRY-DEGRADATION-001: entry_degradation_consistency"
    - "CAL-FEEDBACK-001: feedback_loop_consistency"
    - "CAL-CROSS-PATH-001: cross_path_discrimination"
```

## 8. Safety Semantics Review Overview

```yaml
safety_semantics_review_overview:
  description: >
    Verify that all 3 equations, 6 weight factors, and 5 calibration targets carry
    the required safety semantics declarations. This is a comprehensive sweep to
    prevent any conceptual model element from being misinterpreted as production
    risk, vulnerability severity, or formal finding.
  review_file: "docs/phase83a_safety_semantics_review_checklist.md"
  required_declarations:
    equations:
      - "conceptual_only: true"
      - "not_executable: true"
      - "not_production_risk: true"
      - "not_vulnerability_severity: true"
      - "not_exploitability_score: true"
      - "requires_human_review: true"
    weight_factors:
      - "conceptual_only: true"
      - "not_production_risk: true"
      - "not_vulnerability_severity: true"
      - "human_review_required: true"
    calibration_targets:
      - "tabletop_consistency_review_only: true"
      - "not_statistical_validation: true"
      - "not_production_risk_calibration: true"
      - "human_review_required: true"
```

## 9. Review Result Template

```yaml
review_result_template:
  conceptual_only: true
  human_review_required: true

  template_fields:
    - field: "review_session_id"
      type: "string"
      description: "Unique identifier for this review session"

    - field: "reviewer_name"
      type: "string"
      description: "Name of the human reviewer"

    - field: "review_date"
      type: "date"
      description: "Date of review"

    - field: "equation_review_results"
      type: "array"
      items:
        equation_id: "string"
        variable_completeness: "pass | needs_revision | not_applicable"
        source_mapping_consistency: "pass | needs_revision | not_applicable"
        safety_semantics_confirmed: "pass | needs_revision | not_applicable"
        reviewer_notes: "string"

    - field: "weight_factor_review_results"
      type: "array"
      items:
        weight_id: "string"
        source_pattern_alignment: "pass | needs_revision | not_applicable"
        direction_and_range_valid: "pass | needs_revision | not_applicable"
        calibration_source_traceable: "pass | needs_revision | not_applicable"
        safety_semantics_confirmed: "pass | needs_revision | not_applicable"
        reviewer_notes: "string"

    - field: "calibration_method_review_results"
      type: "array"
      items:
        target_id: "string"
        tabletop_data_alignment: "pass | needs_revision | not_applicable"
        trajectory_fields_covered: "pass | needs_revision | not_applicable"
        validation_questions_adequate: "pass | needs_revision | not_applicable"
        safety_semantics_confirmed: "pass | needs_revision | not_applicable"
        reviewer_notes: "string"

    - field: "safety_semantics_review_results"
      type: "object"
      properties:
        equations_all_declared: "pass | needs_revision"
        weight_factors_all_declared: "pass | needs_revision"
        calibration_targets_all_declared: "pass | needs_revision"
        global_safety_fields_correct: "pass | needs_revision"
        reviewer_notes: "string"

    - field: "overall_assessment"
      type: "string"
      options: ["approved", "approved_with_revisions", "needs_revision"]

    - field: "next_action"
      type: "string"
      description: "Recommended next step after review"
```

## 10. Human Review Requirements

```yaml
human_review_requirements:
  required: true
  purpose: >
    This checklist is a tabletop review aid for human reviewers. It does not
    replace human judgment, does not compute scores, and does not produce
    automated pass/fail decisions. Each item requires a human reviewer to
    examine the source documents and apply their judgment.

  reviewer_qualifications:
    - "Familiarity with Phase 74A attack graph schema and module definitions"
    - "Familiarity with Phase 77A dynamics model rules"
    - "Familiarity with Phase 79A/80A tabletop exercise results"
    - "Familiarity with Phase 81A pattern library"
    - "Understanding of conceptual_only, not_production_risk, not_vulnerability_severity semantics"

  review_process:
    - step: 1
      action: "Reviewer reads Equation Consistency checklist (4 sub-checklists)"
    - step: 2
      action: "Reviewer reads Weight Factor Semantic checklist"
    - step: 3
      action: "Reviewer reads Calibration Method checklist"
    - step: 4
      action: "Reviewer reads Safety Semantics checklist"
    - step: 5
      action: "Reviewer fills in review result template"
    - step: 6
      action: "Reviewer confirms all safety semantics declarations"
```

## 11. Forbidden Uses

```yaml
forbidden_uses:
  - "This checklist must NOT be executed as an automated validation system"
  - "Checklist items must NOT be treated as test cases"
  - "Review results must NOT be treated as vulnerability findings"
  - "Review gap items must NOT be treated as formal findings"
  - "Checklist pass/fail must NOT be treated as production readiness"
  - "Reviewer observations must NOT be treated as confirmed vulnerabilities"
  - "This checklist must NOT be used as input to capability_engine execution"
  - "This checklist must NOT be used as input to controlled replay execution"
  - "All review outputs are human-review-candidate only"
```

## 12. Document Metadata

```yaml
metadata:
  phase: "83A"
  document_type: "unified_theory_review_checklist"
  tabletop_review_checklist_only: true
  conceptual_only: true
  executable: false
  source_phase: "82A"
  total_sections: 12
  review_dimensions: 4
  equations_reviewed: 3
  weight_factors_reviewed: 6
  calibration_targets_reviewed: 6
  human_review_required: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
```
