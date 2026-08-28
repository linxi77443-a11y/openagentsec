# Cross-Module Attack Graph Schema — Design Gate

## 1. Purpose and Scope

This document defines a conceptual schema for cross-module attack graphs within the AI system lifecycle attack matrix. It is a **design gate artifact only** — not an executable attack chain, not a vulnerability assessment, and not a production safety model.

The schema models how simulated signals detected by individual v2.0 modules (M43, M46, M47, M48, M49, M50) may conceptually propagate across module and layer boundaries. The schema is intended for **human review, planning, and design discussion only**.

## 2. Non-Execution Boundary

- `executable: false` for all graph elements
- No real payloads, commands, endpoints, credentials, or system references
- No capability_engine execution
- No execution_results generation
- No controlled replay
- All graph IDs use `<SIM_ATTACK_GRAPH_ID>` placeholders

## 3. Graph Object Model

```yaml
graph_schema:
  graph_id: "<SIM_ATTACK_GRAPH_ID>"
  version: "v3.0-design-gate"
  design_gate_only: true
  executable: false
  nodes: []
  edges: []
  paths: []
```

## 4. Node Definition

```yaml
node_types:
  - module_node:    "A v2.0 assessment module with defined attack objectives and simulated signals."
  - boundary_node:  "A security boundary (command boundary, permission boundary, sandbox boundary, etc.)"
  - artifact_node:  "A synthetic artifact (tool descriptor, repo file, config, secret placeholder, document, trace)"
  - signal_node:    "A simulated defensive signal (injection detected, exposure blocked, boundary preserved)"
  - control_node:   "A control mechanism (human review gate, redaction, audit log, policy enforcement)"
  - evidence_node:  "A reference to stored evidence_trace from module execution"
  - layer_node:     "A system layer (supply_chain, development_environment, rag_data, runtime_sandbox)"
```

## 5. Edge Definition

```yaml
edge_types:
  - context_influence:           "Conceptual flow of context/trust from one node to another"
  - trust_boundary_transfer:     "Trust crossing a defined security boundary"
  - permission_dependency:       "Permission or authorization dependency between modules"
  - evidence_dependency:         "Evidence or signal output consumed by another module"
  - audit_dependency:            "Audit chain integrity dependency"
  - runtime_dependency:          "Runtime sandbox or execution environment dependency"
  - amplification_edge:          "Risk amplification when multiple boundaries are weakened"
  - mitigation_edge:             "Control or human review gate that reduces risk"
  - review_gate_edge:            "Human review or design gate dependency"
```

All edges carry `executable: false`.

## 6. Path Representation

```yaml
path_schema:
  path_id: "<SIM_PATH_ID>"
  source_layer: "<layer>"
  target_layer: "<layer>"
  modules: ["<MXX>", ...]
  relation: "<conceptual description of cross-module relation>"
  executable: false
  requires_human_review: true
  evidence_refs: []
```

## 7. Layer Definition

```yaml
layers:
  - layer_id: "supply_chain"
    description: "AI supply chain including tool descriptors, package manifests, and third-party integrations"
    modules: ["M43"]
  - layer_id: "development_environment"
    description: "AI-augmented development environment including repo context and command execution"
    modules: ["M46", "M47"]
  - layer_id: "rag_data"
    description: "RAG data pipeline including document retrieval, permission inheritance, and audit"
    modules: ["M48", "M49"]
  - layer_id: "runtime_sandbox"
    description: "Agent runtime sandbox including trace integrity, audit chain, and policy enforcement"
    modules: ["M50"]
```

## 8. Module Node Mapping

```yaml
module_nodes:
  M43:
    name: "MCP Tool Descriptor Integrity"
    layer: "supply_chain"
    primary_attack_objective: "supply_chain_tool_descriptor_poisoning"
  M46:
    name: "Coding Agent Repository Context Injection"
    layer: "development_environment"
    primary_attack_objectives:
      - "dev_environment_repository_context_injection"
      - "dev_environment_code_review_bypass"
  M47:
    name: "Coding Agent Command and Credential Boundary"
    layer: "development_environment"
    primary_attack_objectives:
      - "dev_environment_unauthorized_command_induction"
      - "dev_environment_credential_exposure_attempt"
      - "dev_environment_agent_permission_confusion"
  M48:
    name: "RAG Document Poisoning and Instruction Boundary"
    layer: "rag_data"
    primary_attack_objective: "rag_malicious_document_poisoning"
  M49:
    name: "RAG Permission Inheritance and Retrieval Audit"
    layer: "rag_data"
    primary_attack_objectives:
      - "rag_permission_inheritance_bypass"
      - "rag_cross_tenant_retrieval_attempt"
      - "rag_retrieval_audit_gap_detection"
  M50:
    name: "Agent Runtime Sandbox and Audit Chain Integrity"
    layer: "runtime_sandbox"
    primary_attack_objectives:
      - "runtime_sandbox_escape_signal"
      - "runtime_fake_tool_boundary_violation"
      - "runtime_audit_chain_tampering_signal"
      - "runtime_trace_integrity_gap_detection"
      - "runtime_policy_enforcement_bypass"
```

## 9. Cross-Module Edge Taxonomy

```yaml
cross_module_edges:
  - edge_type: "context_influence"
    source_layer: "supply_chain"
    target_layer: "development_environment"
    source_modules: ["M43"]
    target_modules: ["M46", "M47"]
    description: "A poisoned tool descriptor in the supply chain may influence how code context is interpreted in the development environment."
    executable: false

  - edge_type: "context_influence"
    source_layer: "development_environment"
    target_layer: "rag_data"
    source_modules: ["M46", "M47"]
    target_modules: ["M48", "M49"]
    description: "Repository context injection or command boundary bypass may influence the content or permissions of data fed into RAG pipelines."
    executable: false

  - edge_type: "runtime_dependency"
    source_layer: "rag_data"
    target_layer: "runtime_sandbox"
    source_modules: ["M48", "M49"]
    target_modules: ["M50"]
    description: "RAG document retrieval and permission boundary decisions depend on runtime audit chain integrity for non-repudiation."
    executable: false

  - edge_type: "trust_boundary_transfer"
    source_layer: "development_environment"
    target_layer: "runtime_sandbox"
    source_modules: ["M47"]
    target_modules: ["M50"]
    description: "Command and credential boundary violations may transfer into runtime sandbox policy enforcement decisions."
    executable: false
```

## 10. Attack Path Schema

```yaml
conceptual_paths:
  - path_id: "PATH-SUPPLY-DEV-001"
    source_layer: "supply_chain"
    target_layer: "development_environment"
    modules: ["M43", "M46"]
    relation: "tool descriptor trust confusion may influence repository context interpretation"
    executable: false

  - path_id: "PATH-DEV-CRED-RUNTIME-001"
    source_layer: "development_environment"
    target_layer: "runtime_sandbox"
    modules: ["M46", "M47", "M50"]
    relation: "repository context confusion may increase pressure on command or credential boundary and require runtime/audit controls"
    executable: false

  - path_id: "PATH-RAG-RUNTIME-001"
    source_layer: "rag_data"
    target_layer: "runtime_sandbox"
    modules: ["M48", "M49", "M50"]
    relation: "retrieved content and permission boundary decisions depend on audit chain integrity"
    executable: false

  - path_id: "PATH-FULL-LIFECYCLE-001"
    source_layer: "supply_chain"
    target_layer: "runtime_sandbox"
    modules: ["M43", "M46", "M47", "M48", "M49", "M50"]
    relation: "conceptual end-to-end path across supply chain, development environment, RAG, and runtime layers"
    executable: false
```

## 11. Evidence Reference Schema

```yaml
evidence_reference:
  module_id: "<MXX>"
  phase: "<Phase XX>"
  evidence_trace_source: "per_entry_results[].evidence_trace[] or entry-level decision booleans"
  referenced_signals: []
  synthetic_ids:
    - "<SIM_...>"
  cross_module_relevance: "<description of how this evidence relates to adjacent modules>"
  requires_human_review: true
```

## 12. Safety Field Requirements

```yaml
safety_fields:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  controlled_replay_claimed: false
  controlled_replay_execution_allowed: false
  replay_executable: false
  breakthrough_detected_semantics: "simulated_capability_signal_only"
```

## 13. Forbidden Uses

- This schema must NOT be used to construct executable attack chains.
- Paths defined herein are conceptual only and must carry `executable: false`.
- Graph elements must NOT contain real endpoints, credentials, commands, or payloads.
- `risk_amplification_factor` is a conceptual modeling aid only — NOT a vulnerability severity, NOT a production risk score, NOT an exploitability score.
- Cross-module paths must NOT be treated as formal findings.
- This schema must NOT be used as input to capability_engine execution.
- This schema must NOT be used as input to controlled replay execution.
- All references to v2.0 module results preserve the original `breakthrough_detected` semantics as `simulated_capability_signal_only`.
