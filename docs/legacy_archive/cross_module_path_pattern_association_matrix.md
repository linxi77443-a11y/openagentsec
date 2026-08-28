# Cross-Module Path-Pattern Association Matrix

> **Conceptual association matrix only** — not executable, not vulnerability evidence.

## Matrix

| Path ID | Path Name | Modules | Layers | Patterns | Count |
|---------|-----------|---------|--------|----------|-------|
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | Full Lifecycle — Supply Chain through Runtime Sandbox | M43 → M46 → M48 → M49 → M50 | supply_chain, development_environment, rag_data, runtime_sandbox | PATTERN-UPSTREAM-ENTRY-DEGRADATION-001, PATTERN-M50-AUDIT-CONFIRMATION-001, PATTERN-M50-SANDBOX-BOUNDARY-001, PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001, PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001, PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001, PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | 7 |
| PATH-DEV-CRED-RUNTIME-001 | Development Environment — Repository Context to Command/Credential Boundary to Runtime Audit | M46 → M47 → M50 | development_environment, runtime_sandbox | PATTERN-UPSTREAM-ENTRY-DEGRADATION-001, PATTERN-M50-AUDIT-CONFIRMATION-001, PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001, PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001, PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | 5 |
| PATH-RAG-RUNTIME-001 | RAG Data Pipeline to Runtime Sandbox — Content Trust and Audit Dependency | M48 → M49 → M50 | rag_data, runtime_sandbox | PATTERN-UPSTREAM-ENTRY-DEGRADATION-001, PATTERN-M50-AUDIT-CONFIRMATION-001, PATTERN-M50-SANDBOX-BOUNDARY-001, PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001, PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001, PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | 6 |

## Pattern-to-Path Detailed Mapping

### PATTERN-UPSTREAM-ENTRY-DEGRADATION-001
| Path | Entry Module | Degradation Step | Basis |
|------|-------------|-----------------|-------|
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | M43, M46, M48 | M43: step 2, M46: step 3, M48: step 4 | M43: no attenuation; M46: HRG only; M48: HRG + safe_summary |
| PATH-DEV-CRED-RUNTIME-001 | M46 | step 2 | M46: HRG only, no boundary preservation |
| PATH-RAG-RUNTIME-001 | M48 | step 3 | M48: HRG + safe_summary slows degradation |

### PATTERN-M50-AUDIT-CONFIRMATION-001
| Path | M50 Input | Audit Role | Evidence |
|------|----------|------------|----------|
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | M49 permission decision | Verify full retrieval-permission-audit sequence | audit_chain_consistent: true |
| PATH-DEV-CRED-RUNTIME-001 | M47 credential decision | Non-repudiation of M47 boundary enforcement | audit_chain_consistent: true |
| PATH-RAG-RUNTIME-001 | M49 permission decision | Audit trail for content trust propagation | audit_chain_consistent: true |

### PATTERN-M50-SANDBOX-BOUNDARY-001
| Path | Activation Condition | Blocking Mechanism |
|------|---------------------|-------------------|
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | Cross-layer propagation reaches runtime | sandbox_boundary_preserved + controlled_replay_execution_blocked |
| PATH-RAG-RUNTIME-001 | RAG content reaches runtime | sandbox_boundary_preserved as primary barrier |

### PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001
| Path | Primary Node | Attenuation Rules | Outcome |
|------|-------------|------------------|---------|
| PATH-DEV-CRED-RUNTIME-001 | M47 | 3 (HRG, command_boundary, redaction) | M47 holds at pressured — strongest intermediate attenuation |

### PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001
| Path | Dual Boundaries | Amplification Concern |
|------|----------------|----------------------|
| PATH-RAG-RUNTIME-001 | M48 safe_summary + M49 permission | Higher amplification — 2 rules vs M47's 3 |
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | M48 safe_summary + M49 permission | Additional upstream pressure from M46/M43 degradation |

### PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001
| Path | Edge Sequence | Attenuation Gradient |
|------|-------------|---------------------|
| PATH-DEV-CRED-RUNTIME-001 | M46→M47→M50 | High (M46 degrades) → Moderate (M47 holds: 3 rules) → Low (M50 holds: 4 rules) |
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | M46→M47→(M48→M49→M50) | Extended chain — M46→M47 dev segment feeds into RAG segment |

### PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001
| Path | Edge Sequence | Evidence Format |
|------|-------------|----------------|
| PATH-RAG-RUNTIME-001 | M48→M49→M50 | Uniform entry-level boolean across all 3 modules |
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | M48→M49→M50 (as suffix of full chain) | Uniform boolean format, but upstream M43/M46 use structured arrays |

### PATTERN-HUMAN-REVIEW-BREAKPOINT-001
| Path | Modules with HRG | Module without HRG |
|------|-----------------|-------------------|
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | M46, M48, M49, M50 | M43 |
| PATH-DEV-CRED-RUNTIME-001 | M46, M47, M50 | — |
| PATH-RAG-RUNTIME-001 | M48, M49, M50 | — |

---

*End of path-pattern association matrix. All patterns are conceptual_only=true, executable=false.*
