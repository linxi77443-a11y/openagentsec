# Attack Graph Feedback Loop Model — Design Gate

## 1. Purpose and Scope

This document defines a conceptual feedback loop model for the attack graph dynamics layer. Feedback loops describe how cross-module dependencies can create reinforcing or attenuating effects on propagation as signals travel across module and layer boundaries.

**This is a design gate artifact only** — no executable code, no scripts, no implementation, no simulation. Feedback loop concepts remain theoretical for future human review and planning.

## 2. Feedback Loop Boundary

```yaml
feedback_loop_boundary:
  conceptual_loop_only: true
  executable: false
  attack_execution_allowed: false
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  requires_human_review: true

  definition: >
    Feedback loops describe how the state of one module conceptually affects
    the propagation likelihood of adjacent modules in subsequent attack steps.
    All feedback loop concepts are theoretical and must not be interpreted as
    real system behavior.

  loop_properties:
    - "Directional — feedback flows from downstream to upstream (reverse of primary propagation)"
    - "State-dependent — feedback strength depends on module defense states"
    - "Cumulative — effects may compound across multiple attack steps"
    - "Review-gated — all feedback observations require human review"
```

## 3. Positive Feedback Concept

```yaml
positive_feedback:
  conceptual_loop_only: true
  executable: false
  not_exploit_chain: true
  requires_human_review: true

  definition: >
    A conceptual mechanism where degradation in a downstream module increases
    the propagation likelihood from upstream modules. Positive feedback
    conceptually amplifies risk by creating self-reinforcing degradation cycles.

  conceptual_mechanism: >
    When a downstream module's defense state degrades (e.g., M50 audit chain
    becomes inconsistent), the consequences conceptually flow upstream:
    upstream violations that would have been detected by the downstream module
    now have lower likelihood of detection, making upstream propagation more
    likely in subsequent attack steps.

  general_example: >
    If M50's audit chain is degraded (audit_chain_consistent: false),
    upstream violations from M49 (permission bypass) or M47 (credential
    exposure) are less likely to be detected. This conceptually increases
    the propagation likelihood from M49 → M50 and from M47 → M50, creating
    a positive feedback cycle: more upstream pressure → more downstream
    degradation → more upstream leakage.
```

## 4. Negative Feedback / Control Feedback Concept

```yaml
negative_feedback:
  conceptual_loop_only: true
  executable: false
  not_production_safety: true
  requires_human_review: true

  definition: >
    A conceptual mechanism where a downstream module's strong defense state
    reduces upstream propagation likelihood. Negative feedback conceptually
    attenuates risk by creating self-stabilizing control cycles.

  conceptual_mechanism: >
    When a downstream module's defense state is strong and consistent
    (e.g., M50 audit chain confirmed complete), the deterrence effect
    conceptually flows upstream: upstream modules that depend on the
    downstream module for accountability have stronger reason to maintain
    their own defensive posture.

  general_example: >
    If M50's audit chain is complete and consistent (audit_chain_consistent:
    true AND sandbox_boundary_preserved: true), upstream modules M47-M49
    are conceptually more likely to have their violations detected. This
    creates negative feedback: strong downstream controls reduce upstream
    propagation likelihood.
```

## 5. Audit Gap Feedback Loop

```yaml
audit_gap_feedback_loop:
  loop_id: "audit_gap_feedback_loop"
  conceptual_loop_only: true
  executable: false
  attack_execution_allowed: false
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  requires_human_review: true

  definition: >
    A feedback loop where gaps in the audit chain reduce visibility of
    upstream violations, conceptually increasing upstream propagation
    likelihood in subsequent attack steps.

  mechanism: >
    If M50's audit chain is incomplete or inconsistent
    (audit_chain_consistent: false, trace_integrity_failed: true),
    upstream violations from M49 (permission bypass), M48 (poisoned
    document), M47 (credential exposure) become harder to detect.
    Reduced detection likelihood conceptually amplifies propagation:
    attackers have less reason to avoid upstream boundaries if downstream
    detection is weakened.

  feedback_effect: "amplification — reduced audit integrity increases upstream propagation likelihood"

  conceptual_example_scenario:
    initial_state: "M50 audit_chain_consistent: false"
    step_1: "M49 permission boundary violation conceptually less detectable"
    step_2: "M48 poisoned document retrieval conceptually less detectable"
    step_3: "Reduced detection likelihood increases propagation probability from M48/M49 to M50"
    step_4: "M50 audit state further degraded by increased violations"
    result: "Positive feedback loop — audit gap widens over multiple attack steps"

  potential_breakpoints:
    - "Human review gate: M50 audit inconsistency triggers human investigation"
    - "Audit chain restoration: M50 recovers to audit_chain_consistent: true"
    - "Controlled replay gate: blocks execution before audit gap exploitation"
```

## 6. Permission Leakage Feedback Loop

```yaml
permission_leakage_feedback_loop:
  loop_id: "permission_leakage_feedback_loop"
  conceptual_loop_only: true
  executable: false
  attack_execution_allowed: false
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  requires_human_review: true

  definition: >
    A feedback loop where unclear or bypassed permission boundaries in the
    RAG layer conceptually amplify the degradation assumptions in the
    runtime sandbox layer.

  mechanism: >
    If M49's permission boundary is not preserved or the decision is not
    logged (permission_boundary_preserved: false OR permission_decision_logged: false),
    the consequence conceptually flows in two directions: (1) downstream to M50,
    where the runtime sandbox must handle potentially unauthorized content, and
    (2) upstream to M48, where poisoning signals may not be properly attributed
    to permission failures. This dual-direction ambiguity conceptually amplifies
    propagation uncertainty.

  feedback_effect: "amplification — permission ambiguity increases propagation uncertainty in both directions"

  conceptual_example_scenario:
    initial_state: "M49 permission_boundary_preserved: false"
    step_1: "Restricted content bypasses permission check into M50 runtime"
    step_2: "M50 must handle potentially unauthorized content without clear permission context"
    step_3: "M48 poisoning signals cannot be attributed to permission failure"
    step_4: "Propagation likelihood from M48 to M49 increases (bypass less detectable)"
    result: "Positive feedback loop — permission leakage expands over attack steps"

  potential_breakpoints:
    - "Human review gate: permission boundary gap flagged for investigation"
    - "Boundary restoration: M49 permission_boundary_preserved restored to true"
    - "Audit chain: M50 detects unauthorized content and triggers alert"
```

## 7. Credential Exposure Feedback Loop

```yaml
credential_pressure_feedback_loop:
  loop_id: "credential_pressure_feedback_loop"
  conceptual_loop_only: true
  executable: false
  attack_execution_allowed: false
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  requires_human_review: true

  definition: >
    A feedback loop where credential boundary pressure in the development
    environment conceptually increases the review burden on the runtime
    and audit layers.

  mechanism: >
    If M47's credential boundary is under pressure (credential_exposure_attempt
    detected but not fully blocked), the conceptual consequence flows downstream
    to M50: the runtime sandbox must be more vigilant about credential-related
    activity. This increased monitoring burden may conceptually strain M50's
    audit capacity, potentially reducing its ability to detect other violations.

  feedback_effect: "amplification via resource contention — credential pressure consumes downstream audit capacity"

  conceptual_example_scenario:
    initial_state: "M47 credential_exposure_attempt detected, partial block"
    step_1: "Credential pressure conceptually increases M50 audit workload"
    step_2: "M50 audit resources diverted to credential monitoring"
    step_3: "Other propagation pathways (M48→M49→M50) receive less audit attention"
    step_4: "Reduced audit coverage for non-credential pathways conceptually increases their propagation likelihood"
    result: "Positive feedback loop — credential pressure cascades into broader audit coverage gaps"

  potential_breakpoints:
    - "Human review gate: credential pressure triggers boundary review"
    - "Redaction: M47 redaction_or_placeholder_preservation reduces credential exposure"
    - "Audit chain: M50 maintains comprehensive audit despite increased load"
```

## 8. Runtime Policy Feedback Loop

```yaml
runtime_control_feedback_loop:
  loop_id: "runtime_control_feedback_loop"
  conceptual_loop_only: true
  executable: false
  attack_execution_allowed: false
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  requires_human_review: true

  definition: >
    A negative feedback loop where strong runtime sandbox controls conceptually
    attenuate upstream propagation. This is the only feedback loop that creates
    a stabilizing (negative feedback) effect.

  mechanism: >
    If M50's runtime controls are strong (sandbox_boundary_preserved: true,
    audit_chain_consistent: true, runtime_policy_enforced: true), the
    deterrence effect conceptually flows upstream. Modules M47-M49 that
    depend on M50 for accountability and detection have stronger reason to
    maintain defensive posture, conceptually reducing propagation likelihood
    from upstream modules.

  feedback_effect: "attenuation — strong runtime controls reduce upstream propagation likelihood"

  conceptual_example_scenario:
    initial_state: "M50 sandbox_boundary_preserved: true, audit_chain_consistent: true"
    step_1: "M47 command boundary block is reliably recorded in M50 audit"
    step_2: "M49 permission boundary decisions are verifiable through M50 audit chain"
    step_3: "Increased accountability conceptually reduces propagation attempts from M47 and M49"
    step_4: "Upstream modules maintain stronger posture due to accountability"
    result: "Negative feedback loop — runtime control stability propagates attenuation upstream"

  potential_breakpoints:
    - "M50 audit chain inconsistency breaks the feedback loop"
    - "M50 sandbox boundary escape nullifies the feedback effect"
    - "Human review gate: confirms runtime control integrity"
```

## 9. Human Review Breakpoint

```yaml
human_review_breakpoint:
  required: true
  purpose: >
    Every feedback loop observation requires human review before any
    downstream use. Feedback loops are theoretical modeling constructs —
    not confirmed system behaviors.
  breakpoint_triggers:
    - trigger: "feedback_loop_detected"
      description: "Any feedback loop mechanism is identified in the analysis"
      action: "Submit to human review for validation"

    - trigger: "positive_feedback_amplification"
      description: "Positive feedback is assessed to significantly amplify propagation"
      action: "Flag for human review with amplification assessment details"

    - trigger: "feedback_loop_uncertain"
      description: "Feedback direction or strength cannot be clearly determined"
      action: "Enter inconclusive state and route to human review"

    - trigger: "breakpoint_applied"
      description: "A potential breakpoint (human review, restoration, gate) is triggered"
      action: "Document breakpoint effect and confirm with human review"
```

## 10. Forbidden Uses

- Feedback loops must NOT be interpreted as real system causal relationships.
- Positive feedback amplification is NOT a vulnerability severity increase.
- Negative feedback attenuation is NOT a production safety guarantee.
- `audit_gap_feedback_loop` must NOT be used to justify reduced upstream defenses.
- `credential_pressure_feedback_loop` must NOT be used to justify audit capacity reduction.
- Feedback loop observations must NOT be treated as formal findings.
- This model must NOT be used as input to capability_engine execution.
- This model must NOT be used as input to controlled replay execution.
- All feedback loop concepts preserve `simulated_capability_signal_only` semantics.
