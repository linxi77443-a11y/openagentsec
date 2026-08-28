# Risk Propagation Model — Design Gate

## 1. Purpose and Scope

This document defines a conceptual risk propagation model for the cross-module attack graph. It describes how simulated signals detected across v2.0 modules may conceptually influence each other across layers. **This is a theoretical model only** — it does not quantify production risk, does not assign vulnerability severity, and must not be used for formal findings.

## 2. Conceptual Risk Propagation Only

```yaml
risk_propagation_model:
  model_id: "<SIM_RISK_PROPAGATION_MODEL>"
  version: "v3.0-design-gate"
  conceptual_only: true
  not_production_risk: true
  not_vulnerability_severity: true
```

The model describes conceptual risk propagation paths. All relationships are hypothetical and intended for human review and design discussion only.

## 3. Propagation Layers

```yaml
propagation_layers:
  - layer_id: "supply_chain"
    order: 1
    description: "AI supply chain — tool descriptors, third-party metadata, package manifests"
    modules: ["M43"]

  - layer_id: "development_environment"
    order: 2
    description: "AI-augmented development environment — repository context, command execution, credential handling"
    modules: ["M46", "M47"]

  - layer_id: "rag_data"
    order: 3
    description: "RAG data pipeline — document retrieval, permission boundary, retrieval audit"
    modules: ["M48", "M49"]

  - layer_id: "runtime_sandbox"
    order: 4
    description: "Agent runtime sandbox — trace integrity, audit chain, policy enforcement, controlled replay gate"
    modules: ["M50"]
```

Layers are ordered conceptually from upstream (supply chain) to downstream (runtime). Propagation can occur in both directions, though forward propagation (upstream → downstream) is the primary focus.

## 4. Propagation Rule Types

```yaml
propagation_rule_types:
  - rule_type: "trust_transfer"
    description: "Trust decisions in one module may transfer to adjacent modules when shared context exists."
    conceptual_example: "If M43 accepts a poisoned tool descriptor, M46 may interpret repository instructions with misplaced trust."

  - rule_type: "context_transfer"
    description: "Context interpretation from one module may influence context in connected modules."
    conceptual_example: "Repository context injection (M46) may carry fabricated context into command decisions (M47)."

  - rule_type: "permission_transfer"
    description: "Permission boundary decisions may cascade when modules share authorization context."
    conceptual_example: "Permission boundary bypass in RAG (M49) may influence which documents reach runtime execution (M50)."

  - rule_type: "credential_exposure_transfer"
    description: "Credential exposure in one module may increase exposure pressure in downstream modules."
    conceptual_example: "Credential boundary bypass (M47) may expose secrets consumed at runtime (M50)."

  - rule_type: "retrieval_transfer"
    description: "Retrieved content from RAG may influence development context or runtime decisions."
    conceptual_example: "Poisoned retrieved document (M48) may feed into development context (M46) or runtime tool invocation (M50)."

  - rule_type: "audit_trace_transfer"
    description: "Audit chain integrity in one module may affect accountability in connected modules."
    conceptual_example: "Audit chain tampering (M50) may obscure violations originating from RAG permission bypass (M49)."

  - rule_type: "runtime_policy_transfer"
    description: "Runtime policy enforcement decisions may depend on boundary signals from upstream modules."
    conceptual_example: "Command boundary block (M47) provides a signal that runtime policy (M50) may reference for enforcement decisions."
```

## 5. Risk Amplification Factor Concept

```yaml
risk_amplification_factor:
  definition: >
    A conceptual multiplier describing how a simulated signal may become more
    systemically significant when it crosses module or layer boundaries. Multiple
    weakly-defended boundaries crossed in sequence may produce a compounding effect
    that is greater than any single boundary violation.
  conceptual_only: true
  not_vulnerability_severity: true
  not_production_risk: true
  not_exploitability_score: true
  not_cvss: true
  not_formal_finding: true
  requires_human_review: true
  quantification_not_supported: true
```

The risk amplification factor is **not** a numeric score. It is a qualitative design concept to highlight areas where multiple defensive layers may need strengthening. It must not be used to assign CVSS scores, vulnerability severity ratings, or exploitability scores.

## 6. Risk Attenuation / Control Factors

```yaml
risk_attenuation_factors:
  - factor: "human_review_gate"
    description: "Human review requirements can attenuate risk amplification by introducing manual verification."
    applicable_modules: ["M46", "M47", "M48", "M49", "M50"]

  - factor: "boundary_preservation"
    description: "Strong boundary enforcement in one module may attenuate propagation from adjacent modules."
    conceptual_example: "Command boundary preservation (M47) attenuates credential exposure transfer to runtime (M50)."

  - factor: "redaction_or_placeholder_preservation"
    description: "Secret placeholder preservation attenuates credential exposure propagation."
    applicable_modules: ["M47"]

  - factor: "audit_chain_completeness"
    description: "Complete audit chain in runtime (M50) provides detection and non-repudiation for upstream violations."
    applicable_modules: ["M50"]

  - factor: "controlled_replay_gate"
    description: "Controlled replay gate prevents execution of untrusted replay sequences."
    applicable_modules: ["M50"]
```

## 7. Boundary Preservation Rules

```yaml
boundary_preservation_rules:
  - rule: "command_boundary_preserved"
    description: "If command execution boundary is preserved in M47, credential exposure from command context is conceptually attenuated."
    prerequisite_signal: "command_execution_blocked"

  - rule: "permission_boundary_preserved"
    description: "If permission boundary is preserved in M49, cross-tenant retrieval is conceptually blocked."
    prerequisite_signal: "restricted_retrieval_blocked"

  - rule: "sandbox_boundary_preserved"
    description: "If sandbox boundary is preserved in M50, runtime escape is conceptually blocked."
    prerequisite_signal: "runtime_escape_blocked"

  - rule: "audit_chain_complete"
    description: "If audit chain is complete in M50, tampering signals are conceptually preserved for review."
    prerequisite_signal: "audit_chain_consistent"
```

## 8. Example Conceptual Propagation Patterns

```yaml
conceptual_propagation_patterns:
  - pattern_id: "PATTERN-SUPPLY-DEV-001"
    entry_point: "M43"
    propagation: "M43 → M46 → M47"
    description: "A poisoned tool descriptor (M43) introduces misleading context into repository interpretation (M46), which may increase pressure on command boundary (M47)."
    amplification_factors: ["context compounding across layers 1→2"]
    attenuation_factors: ["human_review_gate (M46)", "command_boundary_preserved (M47)"]

  - pattern_id: "PATTERN-DEV-RAG-001"
    entry_point: "M46"
    propagation: "M46 → M47 → M48 → M49"
    description: "Repository context injection (M46) leads to credential exposure (M47), which could contaminate RAG documents (M48) and bypass permission boundaries (M49)."
    amplification_factors: ["credential_exposure cross-layer propagation"]
    attenuation_factors: ["redaction (M47)", "safe_summary (M48)", "permission_boundary_preserved (M49)"]

  - pattern_id: "PATTERN-RAG-RUNTIME-001"
    entry_point: "M48"
    propagation: "M48 → M49 → M50"
    description: "Poisoned RAG document (M48) bypasses permission boundary (M49) and reaches runtime (M50) where audit integrity is required to detect the violation."
    amplification_factors: ["retrieval_transfer without permission check"]
    attenuation_factors: ["audit_chain_complete (M50)", "controlled_replay_gate (M50)"]
```

## 9. Evidence Trace Dependency

```yaml
evidence_trace_dependency:
  principle: >
    Any conceptual cross-module path must reference existing evidence_trace from
    the individual module evaluations. No new evidence is generated by the
    propagation model.
  sources:
    M43: "entry-level boolean decision fields (descriptor_poisoning_detected, tool_metadata_untrusted, fake_tool_invocation_blocked)"
    M46: "structured evidence_trace arrays (4 records per entry with source/signal_type/content)"
    M47: "structured evidence_trace arrays (5 records per entry with source/signal_type/content)"
    M48: "entry-level boolean decision fields (rag_poisoning_detected, retrieved_content_untrusted, safe_summary_generated)"
    M49: "entry-level boolean decision fields (permission_boundary_preserved, restricted_retrieval_blocked, permission_decision_logged)"
    M50: "entry-level boolean decision fields (sandbox_boundary_preserved, audit_chain_consistent, controlled_replay_execution_blocked)"
  no_new_evidence_generated: true
  no_execution_required: true
```

## 10. Human Review Gate

```yaml
human_review_gate:
  required: true
  purpose: >
    All conceptual cross-module paths require human review before any
    implementation or cataloging. The attack graph model is a design discussion
    tool, not an automated decision system.
  what_human_review_covers:
    - "Path plausibility assessment"
    - "Evidence trace completeness check"
    - "Amplification factor qualitative evaluation"
    - "Attenuation factor adequacy check"
    - "Safety field confirmation"
```

## 11. Forbidden Uses

- This model must NOT be used to quantify production risk.
- `risk_amplification_factor` must NOT be interpreted as CVSS, vulnerability severity, or exploitability score.
- Propagation rules must NOT be used as input to automated risk scoring systems.
- Conceptual propagation patterns must NOT be treated as confirmed attack chains.
- This model must NOT be used as input to capability_engine execution.
- This model must NOT be used as input to controlled replay execution.
- All propagation concepts remain `conceptual_only: true` and `not_production_risk: true`.
- The model generates NO new evidence traces and requires NO new module execution.
- Cross-module propagation must NOT be cited as a formal finding.
- Boundary preservation must be confirmed through existing module results, not assumed by the model.
