# Tabletop Model Validation and Calibration Method — Conceptual

## 1. Purpose and Scope

This document defines a conceptual method for validating and calibrating the unified attack intelligence theory model against existing tabletop exercise observations. The method is qualitative and human-review-based — not statistical, not automated, not production-oriented.

**Conceptual calibration only** — no model execution, no numerical fitting, no production risk calibration.

## 2. Calibration Boundary

```yaml
calibration_boundary:
  conceptual_only: true
  not_statistical_validation: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_automated_calibration: true
  requires_human_review: true

  calibration_scope:
    - "Qualitative consistency between theoretical model and tabletop observations"
    - "Human review of whether conceptual equations reproduce observed degradation patterns"
    - "Adjustment of conceptual variable ranges based on observed state transitions"
    - "Cross-path consistency verification across multiple tabletop exercises"

  calibration_exclusions:
    - "NOT statistical fitting or regression analysis"
    - "NOT machine learning model training"
    - "NOT automated parameter optimization"
    - "NOT production risk calibration"
    - "NOT vulnerability severity validation"
    - "NOT controlled replay validation"
    - "NOT capability_engine calibration"
```

## 3. Validation Source Artifacts

```yaml
validation_source_artifacts:
  conceptual_only: true
  requires_human_review: true

  phase_79a_reports:
    documents:
      - "reports/phase79a_path_supply_dev_rag_runtime_tabletop_analysis.md"
      - "reports/phase79a_defense_degradation_trajectory_report.md"
      - "reports/phase79a_attack_evolution_trajectory_report.md"
    provides_for_calibration:
      - "Node state timeline (5 steps, 5 modules)"
      - "Edge propagation timeline (4 edges, probability hints)"
      - "Attenuation application per step"
      - "Amplification assessment"
      - "Feedback loop evaluation"
      - "Trajectory level: partial_degradation"

  phase_80a_reports:
    documents:
      - "reports/phase80a_path_dev_cred_runtime_tabletop_analysis.md"
      - "reports/phase80a_path_rag_runtime_tabletop_analysis.md"
      - "reports/phase80a_multi_path_defense_degradation_comparison.md"
      - "reports/phase80a_path_dev_cred_runtime_defense_degradation_trajectory_report.md"
      - "reports/phase80a_path_rag_runtime_defense_degradation_trajectory_report.md"
    provides_for_calibration:
      - "Two shorter path observations (3 modules each)"
      - "Cross-path comparison (12 dimensions)"
      - "M47 vs M49 attenuation comparison"
      - "M46 vs M48 entry degradation speed comparison"
      - "M50 role comparison across paths"

  phase_81a_pattern_library:
    documents:
      - "reports/phase81a_cross_module_attack_pattern_library.md"
      - "docs/cross_module_attack_pattern_index.md"
      - "docs/cross_module_path_pattern_association_matrix.md"
      - "docs/cross_module_module_pattern_association_matrix.md"
    provides_for_calibration:
      - "8 pattern definitions with lifecycle status"
      - "Pattern-to-path mapping for calibration targeting"
      - "Pattern-to-module mapping for per-module weight calibration"

  evidence_reference_maps:
    documents:
      - "All Phase 79A and Phase 80A reports (evidence_reference_map sections)"
    provides_for_calibration:
      - "Per-step evidence field references"
      - "Module evidence format information (structured arrays vs boolean fields)"
      - "Source phase mapping for each evidence field"

  human_review_observations:
    documents:
      - "Phase 79A and Phase 80A report human_review sections"
      - "Checklist items from Phase 79A and Phase 80A checklists"
    provides_for_calibration:
      - "Review questions that identify calibration concerns"
      - "Pending review items that indicate uncertainty"
      - "Safety field confirmations"
```

## 4. Calibration Targets

```yaml
calibration_targets:
  conceptual_only: true
  requires_human_review: true

  targets:
    - target_id: "CAL-PROPAGATION-001"
      target_name: "propagation_pressure_consistency"
      description: "Verify that conceptual P_edge values align with observed propagation outcomes"
      validation_question: "Does the P_edge equation produce higher values for edges observed as 'probable' and lower values for edges observed as 'possible'?"
      source_evidence: "Phase 79A edge propagation timeline, Phase 80A path reports"
      calibration_method: >
        For each edge in the three observed paths, compute conceptual P_edge
        using Equation 1 and compare the relative ordering to the observed
        propagation probability hints (medium_to_high > medium > low_to_medium).
        Adjust W_edge defaults if ordering is inconsistent.
      expected_ordering:
        highest: "permission_dependency (M48→M49) — observed medium_to_high"
        medium: "context_influence (M46→M47, M43→M46) — observed medium"
        medium: "runtime_dependency (M49→M50) — observed medium"
        lowest: "audit_dependency (M47→M50) — observed low_to_medium"
      human_review_required: true

    - target_id: "CAL-ATTENUATION-001"
      target_name: "attenuation_node_consistency"
      description: "Verify that model-predicted attenuation ordering matches observed patterns"
      validation_question: "Does the model correctly rank M47 > M49 > M46 > M48 > M43 in attenuation strength?"
      source_evidence: "Phase 80A multi-path comparison (M47 vs M49), Phase 79A attenuation application"
      calibration_method: >
        Compare Σ A_attenuation values per module from the G_path equation
        to observed defense states. M47 (3 rules) should have higher
        A_attenuation than M49 (2 rules). M50 (4 rules) should have highest.
      expected_ranking:
        1st: "M50 (4 rules) — consistently pressured"
        2nd: "M47 (3 rules) — held at pressured"
        3rd: "M49 (2 rules) — held at pressured"
        4th: "M48 (HRG + safe_summary) — degrades slower"
        5th: "M46 (HRG only) — degrades faster"
        6th: "M43 (no rules) — degrades fastest"
      human_review_required: true

    - target_id: "CAL-M50-DAMPING-001"
      target_name: "m50_damping_consistency"
      description: "Verify that M50 remains pressured (D_node ≈ 0.7-0.8) across all three paths"
      validation_question: "Does the D_node equation produce consistent M50 defense states across different path configurations?"
      source_evidence: "Phase 79A M50 state (pressured at step 4-5), Phase 80A both paths (pressured)"
      calibration_method: >
        Apply the D_node equation to M50 in all three path scenarios.
        Verify that M50's D_node stays above 0.7 in all cases.
        If D_node drops below 0.5 in any scenario, adjust M50 V_node
        (currently 0.2) or R_control defaults.
      expected_result: "M50 D_node ≥ 0.7 in all three paths"
      human_review_required: true

    - target_id: "CAL-ENTRY-DEGRADATION-001"
      target_name: "entry_degradation_consistency"
      description: "Verify that entry modules degrade in the correct order: M43 < M46 < M48"
      validation_question: "Does the model produce the observed degradation ordering: M43 first, then M46, then M48?"
      source_evidence: "Phase 79A timeline (M43 step 2, M46 step 3, M48 step 4), Phase 80A comparison"
      calibration_method: >
        Apply the D_node equation to M43, M46, and M48 under equivalent
        path conditions. Verify that D_node drops below 0.7 (degraded
        threshold) in the correct order. Adjust V_node values if ordering
        is incorrect.
      expected_ordering:
        first_to_degrade: "M43 (V_node=0.9, no HRG)"
        second_to_degrade: "M46 (V_node=0.7, HRG only)"
        third_to_degrade: "M48 (V_node=0.5, HRG + safe_summary)"
      human_review_required: true

    - target_id: "CAL-FEEDBACK-001"
      target_name: "feedback_loop_consistency"
      description: "Verify that feedback loop sign and magnitude align with tabletop observations"
      validation_question: "Does the F_feedback term produce negative values when runtime_control is active and positive values when permission_leakage would trigger?"
      source_evidence: "Phase 77A feedback loop model, Phase 79A/80A feedback loop observations"
      calibration_method: >
        For each path, determine which feedback loops are active from
        tabletop observations. Set F_feedback accordingly:
        - runtime_control active → F_feedback < 0 (observed in all 3 paths)
        - permission_leakage triggered → F_feedback > 0 (potential, not observed)
        - credential_pressure triggered → F_feedback > 0 (potential, not observed)
        Verify that negative feedback improves path containment.
      human_review_required: true

    - target_id: "CAL-CROSS-PATH-001"
      target_name: "cross_path_discrimination"
      description: "Verify that the model produces different G_path profiles for DEV-CRED vs RAG paths"
      validation_question: "Can the model distinguish between DEV-CRED (M47 strong attenuation) and RAG (M48 slow degradation, M49 moderate attenuation) patterns?"
      source_evidence: "Phase 80A multi-path comparison report"
      calibration_method: >
        Compute G_path for both paths and verify:
        1. Both show partial_degradation trajectory
        2. DEV-CRED has stronger attenuation contribution from M47
        3. RAG has slower entry degradation from M48 safe_summary
        4. The difference is qualitative, not a ranking of which path is 'worse'
      expected_differentiation:
        dev_cred_signature: "Strong M47 attenuation (0.9) dominates mid-chain"
        rag_signature: "Slower M48 degradation (V_node=0.5), M49 moderate attenuation (0.7)"
      human_review_required: true
```

## 5. Calibration Procedure

```yaml
calibration_procedure:
  conceptual_only: true
  requires_human_review: true

  steps:
    - step: 1
      action: "Select calibration path"
      description: "Choose one of the three observed paths for calibration"
      options:
        - "PATH-SUPPLY-DEV-RAG-RUNTIME-001 (5 modules, 4 layers)"
        - "PATH-DEV-CRED-RUNTIME-001 (3 modules, 2 layers)"
        - "PATH-RAG-RUNTIME-001 (3 modules, 2 layers)"

    - step: 2
      action: "Extract observed node state timeline"
      description: "From the selected path's tabletop report, extract the node state transitions per step"
      output: "List of (module, step, state) tuples for all steps"
      example: "[(M46, step0, stable), (M46, step1, pressured), (M46, step2, degraded), ...]"

    - step: 3
      action: "Map state labels to conceptual D_node ranges"
      description: "Convert observed state labels to conceptual D_node ranges"
      mapping:
        stable: "0.9 - 1.0"
        pressured: "0.7 - 0.89"
        degraded: "0.3 - 0.69"
        blocked: "0.01 - 0.29"
      note: "Ranges are conceptual aids — exact mapping requires human review"

    - step: 4
      action: "Apply conceptual equations to the path"
      description: >
        Compute P_edge for each edge at each relevant time step using
        Equation 1. Compute D_node evolution using Equation 2. Compute
        G_path using Equation 3. All computations are conceptual — use
        the example calculation format from the equation design document.
      note: "No actual code execution — all computation is human reasoning with conceptual values"

    - step: 5
      action: "Compare model output to observed trajectory"
      description: >
        Check whether the conceptual equation outputs align with the
        observed tabletop trajectory:
        - Does degradation ordering match?
        - Do attenuation nodes hold at correct states?
        - Does M50 remain pressured?
        - Does G_path range map to partial_degradation?
      assessment: "consistent, partially_consistent, or inconsistent"

    - step: 6
      action: "Adjust variable defaults if needed"
      description: >
        If the model output is inconsistent with observations, adjust
        conceptual variable defaults within their defined ranges:
        - V_node: adjust within [0.0, 1.0]
        - W_edge: adjust within defined discrete values
        - A_attenuation weights: adjust within pattern-based defaults
        - A_amplification weights: adjust within defined ranges
      constraint: "Adjustments must be documented and require human review sign-off"

    - step: 7
      action: "Cross-validate with other paths"
      description: >
        After calibrating on one path, apply the same variable values
        to the other two paths. Verify that the same variable set
        produces consistent results across all paths.
      requirement: "Variable values should be path-independent — same values work for all paths"

    - step: 8
      action: "Human review calibration results"
      description: >
        Present calibration results for human review. The reviewer
        must confirm that:
        - Conceptual equations align with observed patterns
        - Variable defaults are reasonable
        - Cross-path consistency is achieved
        - No variable values are misinterpreted as risk scores
      outcome: "calibration_confirmed, calibration_needs_refinement, or calibration_invalid"
```

## 6. Validation Questions

```yaml
validation_questions:
  conceptual_only: true
  requires_human_review: true

  questions:
    - question_id: "VQ-001"
      question: "Can the P_edge equation conceptually explain the end-to-end propagation in Phase 79A's full-lifecycle path?"
      targets: ["CAL-PROPAGATION-001", "CAL-CROSS-PATH-001"]
      expected_answer: "Yes, with permission_dependency edges showing highest P_edge and audit_dependency edges showing lowest"

    - question_id: "VQ-002"
      question: "Can the equations distinguish between DEV-CRED-RUNTIME and RAG-RUNTIME degradation patterns?"
      targets: ["CAL-CROSS-PATH-001", "CAL-ATTENUATION-001"]
      expected_answer: "Yes, DEV-CRED should show stronger M47 attenuation; RAG should show slower M48 degradation and M49 moderate attenuation"

    - question_id: "VQ-003"
      question: "Does M50 consistently behave as a damping/audit confirmation factor across all three paths?"
      targets: ["CAL-M50-DAMPING-001"]
      expected_answer: "Yes, M50 D_node should remain ≥ 0.7 in all paths with appropriate combination of audit damping and sandbox blocking"

    - question_id: "VQ-004"
      question: "Can the permission_leakage_amplification_weight conceptually express the dual-boundary failure scenario?"
      targets: ["CAL-PROPAGATION-001", "CAL-CROSS-PATH-001"]
      expected_answer: "Yes, A_pattern=1.3 for M48-M49 edges when both boundaries fail; A_pattern=1.0 when either holds"

    - question_id: "VQ-005"
      question: "Can the credential_boundary_attenuation_weight conceptually express M47's stronger defense relative to M49?"
      targets: ["CAL-ATTENUATION-001"]
      expected_answer: "Yes, M47 A_attenuation (0.85) > M49 A_attenuation (0.7), reflecting 3 rules vs 2 rules"

    - question_id: "VQ-006"
      question: "Does the H_review factor provide meaningful defense compensation without being overstated?"
      targets: [All targets]
      expected_answer: "Yes, H_review=0.3 provides moderate compensation — enough to slow degradation but not prevent it entirely"

    - question_id: "VQ-007"
      question: "Are the conceptual variable ranges consistent with observed behavior across all paths?"
      targets: [All targets]
      expected_answer: "Yes, the same variable ranges produce consistent results across all three observed paths"

    - question_id: "VQ-008"
      question: "Does the G_path model correctly classify all three paths as 'partial_degradation'?"
      targets: ["CAL-CROSS-PATH-001"]
      expected_answer: "Yes, all three paths produce G_path values in the range corresponding to partial_degradation trajectory"
```

## 7. Calibration Recording

```yaml
calibration_recording:
  conceptual_only: true
  requires_human_review: true

  recording_format: >
    Each calibration exercise should be recorded in a human-readable format
    (Markdown or YAML) documenting:
    1. Which path was used for calibration
    2. What variable defaults were used
    3. What the conceptual equation outputs were
    4. Whether outputs were consistent with observations
    5. What adjustments were made (if any)
    6. Human review decision

  example_entry:
    calibration_session:
      date: "conceptual_date_placeholder"
      path: "PATH-DEV-CRED-RUNTIME-001"
      human_reviewer: null
      variables_used:
        V_node: {M46: 0.7, M47: 0.4, M50: 0.2}
        W_edge: {context_influence: 0.6, audit_dependency: 0.4}
        A_pattern: {credential_boundary: 0.85}
        F_feedback: -0.1
      conceptual_output:
        D_node_final: {M46: 0.49, M47: 0.9, M50: 0.9}
        G_path: -3.68
        trajectory: "partial_degradation"
      consistency_assessment: "consistent"
      adjustments_made: null
      human_review_decision: null
```

## 8. Calibration Safety Semantics

```yaml
calibration_safety_semantics:
  conceptual_only: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false

  semantic_clarifications:
    - term: "calibration"
      meaning: "Qualitative consistency checking against tabletop observations — NOT parameter optimization"
    - term: "validation"
      meaning: "Human review of conceptual alignment — NOT empirical validation"
    - term: "adjustment"
      meaning: "Human-guided refinement of conceptual ranges — NOT statistical fitting"
    - term: "consistent"
      meaning: "Conceptual alignment with observed patterns — NOT statistically significant agreement"
    - term: "expected_ordering"
      meaning: "Predicted relative ranking from theory — NOT empirically confirmed ordering"

  downstream_use_restrictions:
    - "Calibration results must NOT be treated as empirically validated parameters"
    - "Calibration must NOT be used as evidence of production readiness"
    - "Calibration does NOT replace controlled replay or real-system testing"
    - "Calibrated values must NOT be used as inputs to automated decision systems"
    - "All calibration outputs are human-review-candidate only"
```

## 9. Document Metadata

```yaml
metadata:
  phase: "82A"
  document_type: "tabletop_model_validation_calibration_method"
  conceptual_only: true
  executable: false
  total_calibration_targets: 6
  total_validation_questions: 8
  calibration_procedure_steps: 8
  source_phases_referenced:
    - "79A"
    - "80A"
    - "81A"
  human_review_required: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  statistical_validation_not_performed: true
  automated_calibration_not_performed: true
```
