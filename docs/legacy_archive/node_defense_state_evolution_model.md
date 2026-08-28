# Node Defense State Evolution Model — Design Gate

## 1. Purpose and Scope

This document defines a conceptual model for how a module node's defense state evolves across conceptual attack steps in the attack graph dynamics layer. Each module (M43, M46, M47, M48, M49, M50) in the attack graph may occupy a defense state that changes as attack signals propagate across edges.

**This is a design gate artifact only** — no executable code, no scripts, no implementation, no simulation. The node state model remains a conceptual theory model for future human review and planning.

## 2. Non-Execution Boundary

- `conceptual_state_only: true` for all defense states
- `not_execution_result: true` — states are not actual evaluation results
- `not_confirmed_vulnerability: true` — degraded states are not vulnerabilities
- `requires_human_review: true` for all state transitions
- No real module execution, no capability_engine invocation
- All state IDs use `<SIM_DEFENSE_STATE_ID>` placeholders

## 3. Node Defense State Definition

```yaml
node_defense_state:
  definition: >
    A conceptual representation of a module node's defensive posture at a given
    point in a conceptual attack sequence. The state is derived from the module's
    existing evidence_trace and the dynamics model's propagation rules.

  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  applicable_modules:
    - "M43 — MCP Tool Descriptor Integrity"
    - "M46 — Coding Agent Repository Context Injection"
    - "M47 — Coding Agent Command and Credential Boundary"
    - "M48 — RAG Document Poisoning and Instruction Boundary"
    - "M49 — RAG Permission Inheritance and Retrieval Audit"
    - "M50 — Agent Runtime Sandbox and Audit Chain Integrity"
```

## 4. Defense State Definitions

### Stable

```yaml
defense_state:
  state_id: "stable"
  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  description: >
    The module node's defenses are conceptually intact. All available defensive
    signals indicate normal operation. No propagation pressure has been applied
    to this node in the current conceptual attack sequence.

  characteristics:
    - "All available boundary signals: true or blocked"
    - "No upstream propagation has reached this node"
    - "Normal defensive posture maintained"
    - "Conceptually represents a well-defended state"

  typical_evidence_trace_indicators:
    - "descriptor_poisoning_detected: true (M43)"
    - "repo_context_injection_detected: true (M46)"
    - "unauthorized_command_blocked: true (M47)"
    - "rag_poisoning_detected: true (M48)"
    - "permission_boundary_preserved: true (M49)"
    - "sandbox_boundary_preserved: true (M50)"
```

### Pressured

```yaml
defense_state:
  state_id: "pressured"
  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  description: >
    The module node has received upstream propagation pressure but its primary
    defensive boundaries remain intact. The node is conceptually aware of
    potential threats but has not yet degraded.

  characteristics:
    - "Primary boundary signals still true or blocked"
    - "Upstream propagation pressure detected"
    - "Defensive posture remains intact but under observation"
    - "Some auxiliary signals may show partial triggers"

  typical_evidence_trace_indicators:
    - "Primary boundary: preserved"
    - "Auxiliary signals: partial trigger or inconclusive"
```

### Degraded

```yaml
defense_state:
  state_id: "degraded"
  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  description: >
    The module node's defenses have experienced some degradation. One or more
    secondary defensive signals have weakened, though primary boundaries may
    still hold. The node is conceptually in a weakened but not fully broken state.

  characteristics:
    - "Primary boundary: holding but under significant pressure"
    - "Secondary signals: degraded or incomplete"
    - "Evidence trace may show gaps or inconsistencies"
    - "Human review recommended to assess boundary integrity"

  typical_evidence_trace_indicators:
    - "Primary boundary: preserved but with noted gaps"
    - "Secondary signals: partially triggered or missing"
    - "Evidence trace format variance may obscure signal detail"
```

### Partially Blocked

```yaml
defense_state:
  state_id: "partially_blocked"
  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  description: >
    The module node's primary boundary has conceptually blocked propagation
    through one pathway, but other pathways may remain unblocked. The node
    has partially but not completely defended against the conceptual chain.

  characteristics:
    - "Primary boundary blocked one propagation pathway"
    - "Alternative pathways remain conceptually open"
    - "Attenuation applied but not complete blocking"
    - "Human review needed to assess remaining pathways"

  typical_evidence_trace_indicators:
    - "Primary boundary: blocked for one signal type"
    - "Other signal types: not evaluated or partially triggered"
```

### Blocked

```yaml
defense_state:
  state_id: "blocked"
  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  description: >
    The module node has conceptually blocked all known propagation pathways.
    Propagation through this node is considered conceptually blocked for the
    current attack sequence.

  characteristics:
    - "All relevant boundaries: confirmed blocked"
    - "No propagation pathways remain conceptually open"
    - "Evidence trace supports complete blocking assessment"
    - "Human review should confirm blocking assessment"

  typical_evidence_trace_indicators:
    - "All boundary signals: true or blocked"
    - "Consistent evidence across all signal types"
    - "No indication of bypass or partial trigger"
```

### Recovered

```yaml
defense_state:
  state_id: "recovered"
  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  description: >
    A previously degraded or blocked node has conceptually recovered its
    defensive posture. Recovery may be through human review intervention,
    audit chain restoration, or boundary re-establishment.

  characteristics:
    - "Previously degraded state: resolved"
    - "Recovery mechanism identified (human review, audit, boundary reset)"
    - "Defensive posture: restored to stable or near-stable"
    - "Evidence of recovery action should be documented"

  recovery_triggers:
    - "Human review gate approval"
    - "Audit chain consistency confirmed"
    - "Boundary re-established"
    - "Control mechanism restored"
```

### Inconclusive

```yaml
defense_state:
  state_id: "inconclusive"
  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  description: >
    The module node's defense state cannot be conceptually determined from
    available evidence. This may be due to insufficient evidence_trace,
    ambiguous signals, or format variance that prevents assessment.

  characteristics:
    - "Available evidence: insufficient or ambiguous"
    - "Clear state determination: not possible without human review"
    - "May be due to evidence format variance (boolean fields vs structured arrays)"
    - "Human review mandatory for resolution"

  common_causes:
    - "Evidence trace format not unified across modules"
    - "Key signals missing from module results"
    - "Contradictory signals within same module"
    - "Cross-module signal comparison not possible"
```

### Human Review Required

```yaml
defense_state:
  state_id: "human_review_required"
  conceptual_state_only: true
  not_execution_result: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  description: >
    A state flag indicating that human review is mandatory before any further
    conceptual assessment or downstream use. This state may apply alongside
    any other state to indicate that automated assessment is insufficient.

  characteristics:
    - "Automated conceptual assessment: insufficient"
    - "Human review: mandatory"
    - "This state is additive — it qualifies another defense state"
    - "No automated decision or propagation should occur past this state"
```

## 5. State Lifecycle

```yaml
state_lifecycle:
  conceptual_only: true
  not_execution_result: true
  requires_human_review: true

  lifecycle_stages:
    - stage: "initial"
      description: "Node begins in stable state before any attack steps"
      entry_state: "stable"

    - stage: "under_pressure"
      description: "Upstream propagation reaches the node"
      possible_states: ["pressured", "stable"]

    - stage: "boundary_evaluation"
      description: "Node boundaries are evaluated against the propagation attempt"
      possible_states:
        - "stable (boundary holds effectively)"
        - "pressured (boundary holds but under pressure)"
        - "degraded (boundary partially weakened)"
        - "partially_blocked (some pathways blocked, others open)"
        - "blocked (all pathways blocked)"

    - stage: "recovery_or_blocked"
      description: "Node either recovers or remains in blocked/degraded state"
      possible_states:
        - "recovered (intervention restored defenses)"
        - "blocked (all pathways blocked and confirmed)"
        - "degraded (no recovery applied yet)"

    - stage: "inconclusive"
      description: "Unable to determine state — enters human review"
      possible_states: ["inconclusive"]
```

## 6. State Transition Triggers

```yaml
state_transition_triggers:
  conceptual_only: true
  not_execution_result: true
  requires_human_review: true

  triggers:
    - from_state: "stable"
      to_state: "pressured"
      trigger: "Upstream propagation signal reaches node boundary"
      condition: "Propagation probability assessment indicates medium or higher"

    - from_state: "stable"
      to_state: "blocked"
      trigger: "Direct boundary enforcement without upstream pressure"
      condition: "Boundary signal is actively blocking (e.g., unauthorized_command_blocked: true)"

    - from_state: "pressured"
      to_state: "degraded"
      trigger: "Sustained propagation pressure weakens secondary signals"
      condition: "Multiple attack steps without effective attenuation"

    - from_state: "pressured"
      to_state: "stable"
      trigger: "Effective attenuation or no further propagation"
      condition: "Attenuation rules applied successfully"

    - from_state: "degraded"
      to_state: "partially_blocked"
      trigger: "Boundary enforcement partially effective"
      condition: "One propagation pathway blocked but others remain open"

    - from_state: "degraded"
      to_state: "blocked"
      trigger: "Complete boundary enforcement"
      condition: "All propagation pathways blocked"

    - from_state: "degraded"
      to_state: "recovered"
      trigger: "Human review or audit chain restoration"
      condition: "Human review gate approves recovery or audit chain confirmed complete"

    - from_state: "blocked"
      to_state: "recovered"
      trigger: "Boundary re-established or human review intervention"
      condition: "Human review determines recovery appropriate"

    - from_state: "any"
      to_state: "inconclusive"
      trigger: "Insufficient evidence or ambiguous signals"
      condition: "Evidence_trace does not support clear state determination"
```

## 7. Degradation Conditions

```yaml
degradation_conditions:
  conceptual_only: true
  not_confirmed_vulnerability: true
  requires_human_review: true

  conditions:
    - condition_id: "DEG-MULTI-001"
      description: "Multiple consecutive attack steps without effective boundary blocking"
      conceptual_effect: "Node state degrades from pressured to degraded after N steps"
      threshold: "3+ consecutive attack steps without boundary confirmation"

    - condition_id: "DEG-SIG-001"
      description: "Key signals missing or incomplete in module evidence_trace"
      conceptual_effect: "Unable to confirm boundary effectiveness → potential degradation"
      examples:
        - "M43: only 3 boolean fields, no structured trace"
        - "M48/M49/M50: only entry-level booleans, no structured arrays"

    - condition_id: "DEG-AMP-001"
      description: "Amplification from upstream reduces boundary effectiveness"
      conceptual_effect: "Propagation likelihood increased → node more likely to degrade"
      trigger: "Amplification rules applied (AMPL-SEQ-001, AMPL-CROSS-001, AMPL-FEED-001)"

    - condition_id: "DEG-FEED-001"
      description: "Feedback loop from downstream reduces effectiveness"
      conceptual_effect: "Negative feedback increases state degradation"
      trigger: "Feedback loop mechanism activated (e.g., audit_gap_feedback_loop)"
```

## 8. Recovery Conditions

```yaml
recovery_conditions:
  conceptual_only: true
  not_production_safety: true
  requires_human_review: true

  conditions:
    - condition_id: "REC-HRG-001"
      description: "Human review gate intervenes and validates defensive posture"
      conceptual_effect: "Node restored to stable or recovered state"
      trigger: "Human reviewer confirms defense integrity"
      applicable_to: ["pressured", "degraded", "partially_blocked", "inconclusive"]

    - condition_id: "REC-AUD-001"
      description: "Audit chain confirms consistency — no undetected propagation occurred"
      conceptual_effect: "Node can be restored from degraded or inconclusive"
      trigger: "M50 audit_chain_consistent == true AND no contradictory evidence"
      applicable_to: ["degraded", "inconclusive"]

    - condition_id: "REC-BND-001"
      description: "Boundary re-established after being partially weakened"
      conceptual_effect: "Partially_blocked node returns to stable"
      trigger: "Boundary signals restored to blocked or preserved"
      applicable_to: ["partially_blocked"]

    - condition_id: "REC-ATTN-001"
      description: "Attenuation factors naturally reduce propagation pressure"
      conceptual_effect: "Pressured node returns to stable without active intervention"
      trigger: "Attenuation rules applied successfully over multiple time steps"
      applicable_to: ["pressured"]
```

## 9. Evidence Trace Reference

```yaml
evidence_trace_reference:
  principle: "Node defense state assessment references existing module evidence_trace. No new evidence is generated."
  reference_by_module:
    M43:
      state_determination_fields:
        - "descriptor_poisoning_detected"
        - "tool_metadata_untrusted"
        - "fake_tool_invocation_blocked"
      state_correlation:
        stable: "All three signals true"
        degraded: "One or more signals false"
        inconclusive: "Signals missing or contradictory"

    M46:
      state_determination_fields:
        - "repo_context_injection_detected"
        - "instruction_like_content_identified"
        - "code_review_bypass_blocked"
      state_correlation:
        stable: "Injection detected and blocked"
        pressured: "Injection detected but auxiliary signals partial"
        degraded: "Injection not detected or boundary uncertain"

    M47:
      state_determination_fields:
        - "command_integrity_decision"
        - "credential_boundary_decision"
        - "unauthorized_command_blocked"
      state_correlation:
        stable: "Command integrity confirmed, unauthorized blocked"
        blocked: "Command blocked, boundary preserved"
        degraded: "Command integrity uncertain or partial block"

    M48:
      state_determination_fields:
        - "rag_poisoning_detected"
        - "retrieved_content_untrusted"
        - "safe_summary_generated"
      state_correlation:
        stable: "Poisoning detected, safe summary generated"
        degraded: "Poisoning detected but no safe summary"
        partially_blocked: "Safe summary generated but content still reached downstream"

    M49:
      state_determination_fields:
        - "permission_boundary_preserved"
        - "restricted_retrieval_blocked"
        - "permission_decision_logged"
      state_correlation:
        stable: "Boundary preserved, retrieval blocked, decision logged"
        partially_blocked: "One pathway blocked but others uncertain"
        degraded: "Boundary not preserved or decision not logged"

    M50:
      state_determination_fields:
        - "sandbox_boundary_preserved"
        - "audit_chain_consistent"
        - "controlled_replay_execution_blocked"
      state_correlation:
        stable: "All three signals true"
        blocked: "Sandbox boundary preserved and replay blocked"
        degraded: "Audit chain inconsistent or boundary uncertain"
  new_evidence_generated: false
```

## 10. Human Review Gate

```yaml
human_review_gate:
  required: true
  purpose: >
    All node defense state assessments and transitions require human review.
    State evolution is a conceptual modeling tool, not an automated assessment.
  what_human_review_covers:
    - "State assignment plausibility — does the state match available evidence?"
    - "Transition trigger validation — was the transition reasonably triggered?"
    - "Degradation condition assessment — is degradation justified?"
    - "Recovery condition assessment — is recovery realistic?"
    - "Inconclusive state resolution — human resolves ambiguity"
```

## 11. Forbidden Uses

- Node defense states must NOT be interpreted as real vulnerability assessments.
- A "degraded" state is NOT a confirmed vulnerability — it is a conceptual modeling construct.
- A "blocked" state is NOT a production safety guarantee.
- A "recovered" state is NOT a production recovery confirmation.
- "inconclusive" must trigger human review, not automated escalation.
- State transitions must NOT be automated without human review.
- This model must NOT be used as input to capability_engine execution.
- This model must NOT be used as input to controlled replay execution.
- All state references preserve `simulated_capability_signal_only` semantics.
