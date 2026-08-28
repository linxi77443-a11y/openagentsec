# Phase 83A — Calibration Method Review Checklist

## 1. Purpose

This checklist provides structured review items for verifying the consistency of the 6 calibration targets from Phase 82A. Each target is reviewed for tabletop data alignment, trajectory field coverage, validation question adequacy, safety semantics, and human review requirement.

**Tabletop review checklist only** — not statistical validation, not production risk calibration.

## 2. Review Boundary

```yaml
review_boundary:
  conceptual_only: true
  executable: false
  human_review_required: true
  tabletop_review_checklist_only: true
  not_statistical_validation: true
  not_production_risk_calibration: true
```

## 3. Calibration Target Review Items

### 3.1 CAL-PROPAGATION-001: propagation_pressure_consistency

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Tabletop Data Alignment** | References Phase 79A edge propagation timeline (4 edges: permission_dependency, context_influence, runtime_dependency, audit_dependency); references Phase 80A both path reports for edge observations | `pending` |
| **Phase 79A Observation** | Propagation probability hints: permission_dependency=medium_to_high, context_influence=medium, runtime_dependency=medium, audit_dependency=low_to_medium | `pending` |
| **Phase 80A Observation** | DEV-CRED path: M46→M47 context_influence, M47→M50 audit_dependency; RAG path: M48→M49 permission_dependency, M49→M50 runtime_dependency | `pending` |
| **Trajectory Fields Covered** | defense_degradation_trajectory (edge propagation timeline), attack_evolution_trajectory (propagation ordering), node_state_timeline (per-edge D_target), evidence_reference_map (per-edge probability hints from Phase 79A/80A reports) | `pending` |
| **Validation Question Coverage** | VQ-001 (P_edge end-to-end explanation), VQ-004 (permission_leakage_amplification dual-boundary), VQ-007 (variable range consistency) | `pending` |
| **Expected Ordering** | permission_dependency (highest) > context_influence (medium) = runtime_dependency (medium) > audit_dependency (lowest); ordering matches Phase 79A probability hints | `pending` |
| **Safety Semantics** | tabletop_consistency_review_only: true, not_statistical_validation: true, not_production_risk_calibration: true, human_review_required: true | `pending` |
| **Reviewer Notes** | | |

### 3.2 CAL-ATTENUATION-001: attenuation_node_consistency

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Tabletop Data Alignment** | References Phase 80A multi-path comparison (M47 vs M49 attenuation comparison); references Phase 79A attenuation application per step | `pending` |
| **Phase 79A Observation** | Attenuation rules applied per module per step; M47 holds pressured with 3 rules; M50 remains pressured with 4 rules; attenuation ordering partially observable from node state transitions | `pending` |
| **Phase 80A Observation** | Cross-path comparison provides direct M47 vs M49 comparison: M47 (3 rules) ≥ M49 (2 rules) in attenuation strength; M46 vs M48 entry degradation speed comparison | `pending` |
| **Trajectory Fields Covered** | defense_degradation_trajectory (per-module attenuation impact), attack_evolution_trajectory (attenuation nodes as choke points), node_state_timeline (D_node evolution reveals attenuation effectiveness), evidence_reference_map (rule count per module from Phase 77A/79A/80A) | `pending` |
| **Validation Question Coverage** | VQ-002 (DEV-CRED vs RAG path discrimination), VQ-005 (credential_boundary_attenuation M47 > M49), VQ-007 (variable range consistency) | `pending` |
| **Expected Ranking** | M50 (4 rules, D_node≥0.7) > M47 (3 rules, held pressured) > M49 (2 rules, held pressured) > M48 (HRG + safe_summary) > M46 (HRG only) > M43 (no rules); ranking matches observed defense degradation speed | `pending` |
| **Safety Semantics** | tabletop_consistency_review_only: true, not_statistical_validation: true, not_production_risk_calibration: true, human_review_required: true | `pending` |
| **Reviewer Notes** | | |

### 3.3 CAL-M50-DAMPING-001: m50_damping_consistency

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Tabletop Data Alignment** | References Phase 79A M50 state (pressured at step 4-5); references Phase 80A both paths (M50 pressured); references all 3 path reports for M50 role comparison | `pending` |
| **Phase 79A Observation** | M50 starts at stable (step0), degrades to pressured (step2), remains pressured through step5; never reaches degraded; D_node ≈ 0.7-0.8 range | `pending` |
| **Phase 80A Observation** | Both DEV-CRED and RAG paths: M50 remains pressured; M50 role comparison shows consistent behavior across different entry paths | `pending` |
| **Trajectory Fields Covered** | defense_degradation_trajectory (M50 state trajectory), attack_evolution_trajectory (M50 as terminal node), node_state_timeline (M50 5-step timeline), evidence_reference_map (per-path M50 state data) | `pending` |
| **Validation Question Coverage** | VQ-003 (M50 damping across 3 paths), VQ-007 (variable range consistency) | `pending` |
| **Expected Result** | M50 D_node ≥ 0.7 in all 3 paths; consistent with observed M50 never degraded below pressured; W-M50-AUDIT-DAMP-001 (0.8) + W-M50-SB-BLOCK-001 (0.9) combination achieves this | `pending` |
| **Safety Semantics** | tabletop_consistency_review_only: true, not_statistical_validation: true, not_production_risk_calibration: true, human_review_required: true | `pending` |
| **Reviewer Notes** | | |

### 3.4 CAL-ENTRY-DEGRADATION-001: entry_degradation_consistency

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Tabletop Data Alignment** | References Phase 79A timeline (M43 step2 degraded, M46 step3 degraded, M48 step4 degraded); references Phase 80A M46 vs M48 entry degradation speed comparison | `pending` |
| **Phase 79A Observation** | 5-step full-lifecycle timeline: M43 degrades first (step2), M46 degrades second (step3), M48 degrades third (step4); M43 has no HRG, M46 has HRG only, M48 has HRG + safe_summary | `pending` |
| **Phase 80A Observation** | DEV-CRED path (M46 entry): M46 degrades at comparable speed to Phase 79A; RAG path (M48 entry): M48 degrades slower than M46, consistent with safe_summary protection | `pending` |
| **Trajectory Fields Covered** | defense_degradation_trajectory (entry module degradation ordering), attack_evolution_trajectory (entry as initial breach point), node_state_timeline (per-entry-module state transitions), evidence_reference_map (entry module HRG configuration from Phase 79A/80A) | `pending` |
| **Validation Question Coverage** | VQ-006 (H_review defense compensation), VQ-007 (variable range consistency) | `pending` |
| **Expected Ordering** | M43 degrades first (V_node=0.9, H_review=0.0) → M46 degrades second (V_node=0.7, H_review=0.3) → M48 degrades third (V_node=0.5, H_review=0.3 + safe_summary); ordering matches observed timeline | `pending` |
| **Safety Semantics** | tabletop_consistency_review_only: true, not_statistical_validation: true, not_production_risk_calibration: true, human_review_required: true | `pending` |
| **Reviewer Notes** | | |

### 3.5 CAL-FEEDBACK-001: feedback_loop_consistency

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Tabletop Data Alignment** | References Phase 77A feedback loop model (4 types); references Phase 79A/80A feedback loop observations across all paths | `pending` |
| **Phase 79A Observation** | runtime_control feedback active (negative): M50 runtime boundary enforcement reduces propagation pressure; permission_leakage feedback: potential but not triggered (M48→M49 chain reaches M50 before escalation) | `pending` |
| **Phase 80A Observation** | DEV-CRED: credential pressure feedback potentially active; RAG: permission leakage feedback potential; both paths: runtime_control feedback active (negative) | `pending` |
| **Trajectory Fields Covered** | defense_degradation_trajectory (feedback impact on degradation rate), attack_evolution_trajectory (feedback as propagation modifier), node_state_timeline (D_node recovery via feedback), evidence_reference_map (feedback sign observations from Phase 77A/79A/80A) | `pending` |
| **Validation Question Coverage** | VQ-007 (variable range consistency), VQ-008 (G_path partial_degradation classification) | `pending` |
| **Expected Behavior** | runtime_control active → F_feedback < 0 (observed in all 3 paths); permission_leakage triggered → F_feedback > 0 (potential, not observed); credential_pressure triggered → F_feedback > 0 (potential, not observed); negative feedback improves path containment in all observed cases | `pending` |
| **Safety Semantics** | tabletop_consistency_review_only: true, not_statistical_validation: true, not_production_risk_calibration: true, human_review_required: true | `pending` |
| **Reviewer Notes** | | |

### 3.6 CAL-CROSS-PATH-001: cross_path_discrimination

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Tabletop Data Alignment** | References Phase 80A multi-path comparison report (12 comparison dimensions); references all 3 path reports | `pending` |
| **Phase 79A Observation** | Full-lifecycle path (5 modules, 4 layers): complete degradation chain from M43 entry through M50 terminal; G_path = -2.8625 | `pending` |
| **Phase 80A Observation** | DEV-CRED path (3 modules, 2 layers): M46→M47→M50, strong M47 attenuation, G_path = -3.68; RAG path (3 modules, 2 layers): M48→M49→M50, slower M48 degradation, M49 moderate attenuation, G_path = -3.136 | `pending` |
| **Trajectory Fields Covered** | defense_degradation_trajectory (all 3 paths classified partial_degradation), attack_evolution_trajectory (path-specific attack progression), node_state_timeline (per-path per-module state differences), evidence_reference_map (12 cross-path comparison dimensions) | `pending` |
| **Validation Question Coverage** | VQ-002 (DEV-CRED vs RAG discrimination), VQ-004 (permission_leakage_amplification), VQ-008 (G_path partial_degradation) | `pending` |
| **Expected Differentiation** | DEV-CRED signature: strong M47 attenuation (0.9) dominates mid-chain → G_path = -3.68 (stronger containment); RAG signature: slower M48 degradation (V_node=0.5), M49 moderate attenuation (0.7) → G_path = -3.136 (weaker containment); full-lifecycle: 5-module chain → G_path = -2.8625 (weakest containment, more edges); all 3 paths are partial_degradation (not a ranking of "worse") | `pending` |
| **Safety Semantics** | tabletop_consistency_review_only: true, not_statistical_validation: true, not_production_risk_calibration: true, human_review_required: true | `pending` |
| **Reviewer Notes** | | |

## 4. Cross-Target Consistency Review

| Review Dimension | Expected Condition | Status |
|---|---|---|
| **Non-Overlapping Coverage** | Each target covers a distinct calibration aspect (propagation + attenuation + M50 + entry + feedback + cross-path); no two targets validate the same phenomenon | `pending` |
| **Trajectory Field Coverage Complete** | 4 trajectory fields (defense_degradation_trajectory, attack_evolution_trajectory, node_state_timeline, evidence_reference_map) are covered by at least 2 targets each; no trajectory field is uncovered | `pending` |
| **Validation Question Mapping** | All 8 VQs map to at least 1 target; each target has at least 2 VQs; VQ-006 and VQ-007 are shared across most targets (general consistency check) | `pending` |
| **Path Coverage Complete** | All 3 observed paths (full-lifecycle, DEV-CRED, RAG) are represented across targets; no path has zero coverage | `pending` |
| **Module Coverage Complete** | All 6 modules (M43, M46, M47, M48, M49, M50) are represented across targets; no module has zero coverage | `pending` |
| **Reviewer Notes** | | |

## 5. Document Metadata

```yaml
metadata:
  phase: "83A"
  document_type: "calibration_method_review_checklist"
  conceptual_only: true
  executable: false
  human_review_required: true
  tabletop_consistency_review_only: true
  not_statistical_validation: true
  not_production_risk_calibration: true
  calibration_targets_reviewed: 6
  review_dimensions_per_target: 8
  cross_target_review_items: 5
  review_status: "pending"
```
