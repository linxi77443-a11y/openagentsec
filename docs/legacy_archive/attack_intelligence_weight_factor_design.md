# Attack Intelligence Weight Factor Design — Conceptual

## 1. Purpose and Scope

This document defines six conceptual weight factors derived from the Phase 81A attack pattern library. These weights serve as modifiers in the unified theory model's equations, providing pattern-based attenuation, amplification, blocking, and review gate adjustments.

**Conceptual weights only** — not detection rules, not risk scores, not vulnerability severity ratings.

## 2. Weight Factor Boundary

```yaml
weight_factor_boundary:
  conceptual_only: true
  not_production_risk: true
  not_vulnerability_severity: true
  not_exploitability_score: true
  not_detection_rule: true
  requires_human_review: true

  weight_status:
    - "Weights are conceptual modeling aids derived from tabletop exercise observations"
    - "No numerical fitting, statistical calibration, or machine learning training"
    - "Weight values are qualitative and subject to human review adjustment"
    - "Weights must NOT be interpreted as detection rule coefficients"
    - "Weights must NOT be interpreted as production risk factors"
```

## 3. Weight Factor Definitions

### upstream_entry_vulnerability_factor

```yaml
weight_id: "W-ENTRY-VULN-001"
weight_name: "upstream_entry_vulnerability_factor"
conceptual_meaning: >
  A factor representing the conceptual vulnerability of upstream entry modules
  (M43, M46, M48) to early degradation under sustained attack pressure. Higher
  values indicate modules that degrade faster with less incoming pressure.
source_pattern: "PATTERN-UPSTREAM-ENTRY-DEGRADATION-001"
source_pattern_lifecycle: "confirmed_across_3_paths"
related_paths:
  - "PATH-SUPPLY-DEV-RAG-RUNTIME-001"
  - "PATH-DEV-CRED-RUNTIME-001"
  - "PATH-RAG-RUNTIME-001"
related_modules: ["M43", "M46", "M48"]
conceptual_direction: "amplification (increases degradation sensitivity)"
suggested_range: "0.0 - 1.0 as conceptual scale"
default_values_by_module:
  M43: "0.90"
    reasoning: "No attenuation rules, no human review gate — degrades fastest"
    tabletop_evidence: "Phase 79A: M43 degrades at step 2 (earliest of all modules)"
  M46: "0.70"
    reasoning: "Only ATTEN-HRG-001, no boundary_preservation attenuation"
    tabletop_evidence: "Phase 80A DEV-CRED: M46 degrades at step 2; Phase 79A: M46 degrades at step 3"
  M48: "0.50"
    reasoning: "Has ATTEN-HRG-001 + safe_summary content protection — slower degradation"
    tabletop_evidence: "Phase 80A RAG: M48 degrades at step 3 (slower than M46's step 2)"
equation_application:
  primary: "V_node (node vulnerability factor in D_node equation)"
  secondary: "S_source derivation (higher V_node → higher S_source at same D_node level)"
calibration_source: "Phase 79A/80A node state timeline observations"
not_production_risk: true
not_vulnerability_severity: true
human_review_required: true
```

### m50_audit_damping_weight

```yaml
weight_id: "W-M50-AUDIT-DAMP-001"
weight_name: "m50_audit_damping_weight"
conceptual_meaning: >
  A damping factor representing M50's audit chain confirmation effect on overall
  path propagation. M50's audit_chain_consistent field provides a conceptual
  damping effect by ensuring upstream decisions are recorded and non-repudiable,
  which deters undetected propagation.
source_pattern: "PATTERN-M50-AUDIT-CONFIRMATION-001"
source_pattern_lifecycle: "confirmed_across_3_paths"
related_paths:
  - "PATH-SUPPLY-DEV-RAG-RUNTIME-001"
  - "PATH-DEV-CRED-RUNTIME-001"
  - "PATH-RAG-RUNTIME-001"
related_modules: ["M50"]
conceptual_direction: "attenuation (reduces propagation pressure)"
suggested_range: "0.5 - 1.0 as conceptual scale"
default_value: "0.8"
reasoning: >
  M50 has 4 attenuation rules (strongest profile). The audit chain provides
  both detective (ATTEN-AUD-001) and preventive (ATTEN-RPL-001) controls.
  The value 0.8 reflects strong but not absolute damping — M50 can still be
  pressured even if it does not degrade.
tabletop_evidence:
  - "Phase 79A: M50 pressured but not degraded across 5 steps in full-lifecycle path"
  - "Phase 80A DEV-CRED: M50 pressured but not degraded (audit chain for M47)"
  - "Phase 80A RAG: M50 pressured but not degraded (sandbox boundary for M49)"
equation_application:
  primary: "D_target in P_edge equation (M50's high D_target gives (1-D_target)=0.2)"
  secondary: "Σ A_attenuation in G_path equation (M50 contributes 1.5 total attenuation)"
feedback_loop_relationship: >
  runtime_control_feedback_loop (negative feedback) activates when M50 D_node is high.
  This produces F_feedback < 0 which reduces P_edge for upstream edges.
calibration_source: "Phase 79A/80A M50 node state consistency across all 3 paths"
not_production_risk: true
not_vulnerability_severity: true
human_review_required: true
```

### m50_sandbox_boundary_weight

```yaml
weight_id: "W-M50-SB-BLOCK-001"
weight_name: "m50_sandbox_boundary_weight"
conceptual_meaning: >
  A blocking factor representing M50's sandbox boundary and controlled replay gate
  effectiveness. Unlike the audit damping weight (which is attenuating), this weight
  is blocking — it can reduce propagation pressure to zero if the boundary holds.
source_pattern: "PATTERN-M50-SANDBOX-BOUNDARY-001"
source_pattern_lifecycle: "confirmed_across_2_paths"
related_paths:
  - "PATH-SUPPLY-DEV-RAG-RUNTIME-001"
  - "PATH-RAG-RUNTIME-001"
related_modules: ["M50"]
conceptual_direction: "blocking (can eliminate propagation at boundary)"
suggested_range: "0.0 - 1.0 as conceptual scale"
default_value: "0.9"
reasoning: >
  M50's sandbox boundary (BLOCK-SB-001) and controlled replay gate (BLOCK-RPL-001)
  are the strongest blocking mechanisms across all modules. If the sandbox boundary
  is preserved, propagation is blocked at the runtime entry point.
tabletop_evidence:
  - "Phase 80A RAG: M50 sandbox_boundary_preserved=true prevents content execution"
  - "Phase 79A: M50 sandbox boundary holds across all 5 steps"
  - "M50 role in RAG path emphasizes sandbox enforcement over audit"
equation_application:
  primary: "Σ B_blocking in G_path equation (BLOCK-SB-001: 0.5, BLOCK-RPL-001: 0.5)"
  secondary: "R_control in D_node equation (provides recovery when boundary is triggered)"
functional_distinction_from_audit_damping: >
  The sandbox boundary weight is PREVENTIVE (blocks before execution).
  The audit damping weight is DETECTIVE (confirms after the fact).
  Both contribute to M50's overall defense, but through different mechanisms.
  In DEV-CRED path, audit damping dominates. In RAG path, sandbox boundary dominates.
calibration_source: "Phase 79A/80A M50 sandbox boundary observations"
not_production_risk: true
not_vulnerability_severity: true
human_review_required: true
```

### credential_boundary_attenuation_weight

```yaml
weight_id: "W-CRED-ATTEN-001"
weight_name: "credential_boundary_attenuation_weight"
conceptual_meaning: >
  A weight representing M47's credential boundary attenuation effectiveness. M47 has
  3 attenuation rules (the most of any intermediate module), providing strong
  resistance to upstream propagation from M46's repository context injection.
source_pattern: "PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001"
source_pattern_lifecycle: "observed_in_1_path"
related_paths:
  - "PATH-DEV-CRED-RUNTIME-001"
related_modules: ["M46", "M47", "M50"]
conceptual_direction: "attenuation (reduces propagation pressure through M47)"
suggested_range: "0.0 - 1.0 as conceptual scale"
default_value: "0.85"
reasoning: >
  M47 has 3 attenuation rules: ATTEN-HRG-001 (human review), ATTEN-BND-001
  (command boundary), ATTEN-RED-001 (redaction). This is the strongest intermediate
  attenuation profile — stronger than M49 (2 rules). The weight 0.85 reflects:
  - 3 rules vs M49's 2 rules → proportionally stronger
  - But not absolute (M47 can still transition to pressured)
  - Redaction (ATTEN-RED-001) is unique to M47 — no other module has it
equation_application:
  primary: "A_pattern in P_edge equation (applied to M46→M47 and M47→M50 edges)"
  secondary: "V_node default (M47=0.4 — low vulnerability reflects strong attenuation)"
module_context:
  M46: "Source of context injection that M47's credential boundary must evaluate"
  M47: "Primary attenuation node with 3 rules"
  M50: "Receives M47's enforcement decision via audit_dependency edge"
calibration_source: "Phase 80A comparison report: M47 (3 rules) > M49 (2 rules)"
not_production_risk: true
not_vulnerability_severity: true
human_review_required: true
```

### permission_leakage_amplification_weight

```yaml
weight_id: "W-PERM-AMPL-001"
weight_name: "permission_leakage_amplification_weight"
conceptual_meaning: >
  A weight representing the amplification risk when both M48's safe_summary content
  protection and M49's permission boundary fail simultaneously. This dual-boundary
  failure creates a higher amplification scenario than single-boundary paths.
source_pattern: "PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001"
source_pattern_lifecycle: "observed_in_2_paths"
related_paths:
  - "PATH-RAG-RUNTIME-001"
  - "PATH-SUPPLY-DEV-RAG-RUNTIME-001"
related_modules: ["M48", "M49", "M50"]
conceptual_direction: "amplification (increases propagation pressure when dual boundaries fail)"
suggested_range: "0.0 - 2.0 as conceptual scale (1.0 = neutral)"
default_value: "1.3"
reasoning: >
  The dual-boundary structure (M48 safe_summary + M49 permission_boundary) means
  both must fail for full propagation. This creates:
  - Higher amplification than single-boundary paths if both fail (hence > 1.0)
  - But also two independent opportunities for containment
  The value 1.3 reflects moderate amplification — significant but not extreme.
tabletop_evidence:
  - "Phase 80A RAG: M48 safe_summary delays degradation; M49 2 rules provide moderate attenuation"
  - "Phase 80A comparison: RAG path has higher amplification potential than DEV-CRED"
  - "Phase 79A: Permission leakage feedback loop is potential (not triggered) — weight reflects conditional nature"
equation_application:
  primary: "A_pattern in P_edge equation (for M48→M49 and M49→M50 edges)"
  secondary: "Σ A_amplification in G_path equation (adds to amplification sum)"
trigger_condition: >
  This weight only activates when BOTH M48 safe_summary fails AND M49 permission
  boundary fails. If either holds, the weight defaults to 1.0 (neutral).
  If both hold, the weight is not applied (no leakage scenario).
related_feedback_loop: >
  permission_leakage_feedback_loop activates when M49 permission_boundary_preserved
  becomes false. When triggered, F_feedback > 0, which compounds the amplification.
calibration_source: "Phase 80A multi-path comparison (RAG vs DEV-CRED amplification difference), Phase 81A pattern library"
not_production_risk: true
not_vulnerability_severity: true
human_review_required: true
```

### human_review_breakpoint_weight

```yaml
weight_id: "W-HRG-BREAK-001"
weight_name: "human_review_breakpoint_weight"
conceptual_meaning: >
  A weight representing the compensating effect of human review gates on module
  defense states. Modules with available and activated human review gates receive
  a defense compensation that slows degradation. M43 has no human review gate
  and thus receives zero compensation.
source_pattern: "PATTERN-HUMAN-REVIEW-BREAKPOINT-001"
source_pattern_lifecycle: "confirmed_across_3_paths"
related_paths:
  - "PATH-SUPPLY-DEV-RAG-RUNTIME-001"
  - "PATH-DEV-CRED-RUNTIME-001"
  - "PATH-RAG-RUNTIME-001"
related_modules: ["M43", "M46", "M47", "M48", "M49", "M50"]
conceptual_direction: "review_gate (provides defense compensation)"
suggested_range: "0.0 - 0.5 as conceptual scale"
default_values_by_module:
  M43: "0.0 (no human review gate available)"
    reasoning: "M43's evidence structure has no human_review_gate field — weakest module"
    tabletop_evidence: "Phase 79A: M43 degrades fastest with no recovery within module"
  M46: "0.3"
    reasoning: "Human review gate available — moderate compensation"
    tabletop_evidence: "Phase 80A DEV-CRED: M46 degrades but human review could intervene"
  M47: "0.3"
    reasoning: "Human review gate available as part of 3-rule attenuation"
    tabletop_evidence: "Phase 80A DEV-CRED: M47 holds — review gate contributes"
  M48: "0.3"
    reasoning: "Human review gate available — additional safe_summary protection"
    tabletop_evidence: "Phase 80A RAG: M48 degrades slower than M46"
  M49: "0.3"
    reasoning: "Human review gate available as part of 2-rule attenuation"
    tabletop_evidence: "Phase 80A RAG: M49 holds with permission boundary"
  M50: "0.3"
    reasoning: "Human review gate available — also has REC-HRG-001 recovery"
    tabletop_evidence: "Phase 79A/80A: M50 consistently holds across all paths"
equation_application:
  primary: "H_review in D_node equation (added to defense state computation)"
  secondary: "R_control recovery contribution when REC-HRG-001 is activated"
activation_condition: >
  H_review > 0 only when:
  1. The module has human_review_gate available (ATTEN-HRG-001 in evidence)
  2. The human review is conceptually applied (not bypassed)
  3. For M43: H_review is always 0 — no human review gate
note: >
  The human review breakpoint weight is the only weight that applies across
  all modules (except M43) and acts as a universal defense compensation mechanism.
  It is also the only weight that interacts with control recovery (REC-HRG-001).
calibration_source: "Phase 81A human_review_breakpoint_pattern (confirmed_across_3_paths)"
not_production_risk: true
not_vulnerability_severity: true
human_review_required: true
```

## 4. Weight Factor Summary

```yaml
weight_factor_summary:
  conceptual_only: true
  requires_human_review: true

  weights:
    - weight_id: "W-ENTRY-VULN-001"
      name: "upstream_entry_vulnerability_factor"
      direction: "amplification"
      range: "0.0 - 1.0"
      primary_modules: ["M43", "M46", "M48"]
      primary_equation: "V_node (D_node equation)"

    - weight_id: "W-M50-AUDIT-DAMP-001"
      name: "m50_audit_damping_weight"
      direction: "attenuation"
      range: "0.5 - 1.0"
      primary_modules: ["M50"]
      primary_equation: "D_target (P_edge equation), Σ A_attenuation (G_path equation)"

    - weight_id: "W-M50-SB-BLOCK-001"
      name: "m50_sandbox_boundary_weight"
      direction: "blocking"
      range: "0.0 - 1.0"
      primary_modules: ["M50"]
      primary_equation: "Σ B_blocking (G_path equation)"

    - weight_id: "W-CRED-ATTEN-001"
      name: "credential_boundary_attenuation_weight"
      direction: "attenuation"
      range: "0.0 - 1.0"
      primary_modules: ["M46", "M47", "M50"]
      primary_equation: "A_pattern (P_edge equation)"

    - weight_id: "W-PERM-AMPL-001"
      name: "permission_leakage_amplification_weight"
      direction: "amplification"
      range: "0.0 - 2.0"
      primary_modules: ["M48", "M49", "M50"]
      primary_equation: "A_pattern (P_edge equation), Σ A_amplification (G_path equation)"

    - weight_id: "W-HRG-BREAK-001"
      name: "human_review_breakpoint_weight"
      direction: "review_gate"
      range: "0.0 - 0.5"
      primary_modules: ["M43", "M46", "M47", "M48", "M49", "M50"]
      primary_equation: "H_review (D_node equation)"

  direction_summary:
    amplification: ["W-ENTRY-VULN-001", "W-PERM-AMPL-001"]
    attenuation: ["W-M50-AUDIT-DAMP-001", "W-CRED-ATTEN-001"]
    blocking: ["W-M50-SB-BLOCK-001"]
    review_gate: ["W-HRG-BREAK-001"]

  equation_coverage:
    p_edge_equation_variables:
      - "A_pattern (W-CRED-ATTEN-001, W-PERM-AMPL-001)"
      - "D_target (W-M50-AUDIT-DAMP-001)"
    d_node_equation_variables:
      - "V_node (W-ENTRY-VULN-001)"
      - "H_review (W-HRG-BREAK-001)"
    g_path_equation_variables:
      - "Σ A_attenuation (W-M50-AUDIT-DAMP-001, W-CRED-ATTEN-001)"
      - "Σ A_amplification (W-PERM-AMPL-001)"
      - "Σ B_blocking (W-M50-SB-BLOCK-001)"
```

## 5. Weight Safety Semantics

```yaml
weight_safety_semantics:
  conceptual_only: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false

  semantic_clarifications:
    - term: "weight"
      meaning: "Conceptual modifier derived from tabletop pattern observations — NOT a regression coefficient"
    - term: "default_value"
      meaning: "Starting point for human review discussion — NOT a calibrated parameter"
    - term: "suggested_range"
      meaning: "Conceptual boundary for the weight — NOT a statistical confidence interval"
    - term: "direction"
      meaning: "Conceptual effect direction — NOT a guaranteed causal relationship"
    - term: "calibration_source"
      meaning: "Source of qualitative evidence — NOT a training dataset"

  downstream_use_restrictions:
    - "Weights must NOT be used as detection rule coefficients"
    - "Weights must NOT be interpreted as vulnerability severity scores"
    - "Weights must NOT be used as input to automated decision systems"
    - "Weight default values require human review confirmation"
    - "All weight applications are human-review-candidate only"
```

## 6. Document Metadata

```yaml
metadata:
  phase: "82A"
  document_type: "attack_intelligence_weight_factor_design"
  conceptual_only: true
  executable: false
  total_weights: 6
  source_patterns: 6
  covered_modules: 6 (M43-M50)
  weight_directions:
    amplification: 2
    attenuation: 2
    blocking: 1
    review_gate: 1
  human_review_required: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
```
