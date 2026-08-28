# Cross-Module Module-Pattern Association Matrix

> **Conceptual association matrix only** — not executable, not vulnerability evidence.

## Module Summary

| Module | Name | Phase | Layer | Pattern Count |
|--------|------|-------|-------|---------------|
| M43 | MCP Tool Descriptor Integrity | 66A | supply_chain | 1 |
| M46 | Coding Agent Repository Context Injection | 72A | development_environment | 3 |
| M47 | Coding Agent Command and Credential Boundary | 71A | development_environment | 2 |
| M48 | RAG Document Poisoning and Instruction Boundary | 67A | rag_data | 4 |
| M49 | RAG Permission Inheritance and Retrieval Audit | 69A | rag_data | 3 |
| M50 | Agent Runtime Sandbox and Audit Chain Integrity | 68A | runtime_sandbox | 5 |

## Matrix

| Module | PATTERN-UPSTREAM-ENTRY-DEGRADATION-001 | PATTERN-M50-AUDIT-CONFIRMATION-001 | PATTERN-M50-SANDBOX-BOUNDARY-001 | PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001 | PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001 | PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001 | PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001 | PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | Count |
|--------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| M43 | ● | — | — | — | — | — | — | — | 1 |
| M46 | ● | — | — | — | — | ● | — | ● | 3 |
| M47 | — | — | — | ● | — | ● | — | ● | 3 |
| M48 | ● | — | — | — | ● | — | ● | ● | 4 |
| M49 | — | — | — | — | ● | — | ● | ● | 3 |
| M50 | — | ● | ● | — | — | ● | ● | ● | 5 |

**Legend**: ● = pattern applies to this module; — = pattern does not apply

## Per-Module Pattern Details

### M43 — MCP Tool Descriptor Integrity
| Pattern | Role | Detail |
|---------|------|--------|
| PATTERN-UPSTREAM-ENTRY-DEGRADATION-001 | Primary entry | No attenuation rules — degrades fastest. Human review gate absent. |

### M46 — Coding Agent Repository Context Injection
| Pattern | Role | Detail |
|---------|------|--------|
| PATTERN-UPSTREAM-ENTRY-DEGRADATION-001 | Entry module | ATTEN-HRG-001 only — degrades at step 2-3. |
| PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001 | Context source | Provides context_influence edge to M47. |
| PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | Breakpoint | Human_review_gate available. |

### M47 — Coding Agent Command and Credential Boundary
| Pattern | Role | Detail |
|---------|------|--------|
| PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001 | Primary attenuation | 3 rules (ATTEN-HRG-001, ATTEN-BND-001, ATTEN-RED-001) — strongest intermediate node. |
| PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001 | Intermediate absorber | Absorbs M46 pressure, transfers to M50 via audit_dependency. |
| PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | Breakpoint | Human_review_gate available. |

### M48 — RAG Document Poisoning and Instruction Boundary
| Pattern | Role | Detail |
|---------|------|--------|
| PATTERN-UPSTREAM-ENTRY-DEGRADATION-001 | Entry module | ATTEN-HRG-001 + safe_summary — degrades slower than M43/M46. |
| PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001 | First boundary | safe_summary is first of dual boundaries in leakage scenario. |
| PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001 | Content source | Initiates retrieval-permission-audit sequence. |
| PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | Breakpoint | Human_review_gate available. |

### M49 — RAG Permission Inheritance and Retrieval Audit
| Pattern | Role | Detail |
|---------|------|--------|
| PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001 | Second boundary | permission_boundary_preserved is second of dual boundaries. |
| PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001 | Permission node | Evaluates content trust and transfers to M50. |
| PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | Breakpoint | Human_review_gate available. |

### M50 — Agent Runtime Sandbox and Audit Chain Integrity
| Pattern | Role | Detail |
|---------|------|--------|
| PATTERN-M50-AUDIT-CONFIRMATION-001 | Terminal audit | Audit chain confirmation for all upstream decisions. |
| PATTERN-M50-SANDBOX-BOUNDARY-001 | Execution boundary | Sandbox boundary and controlled replay gate as final barriers. |
| PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001 | Terminal node | Receives M47 credential signals via audit_dependency. |
| PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001 | Terminal node | Receives M49 permission signals via runtime_dependency. |
| PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | Breakpoint | Human_review_gate + REC-HRG-001 recovery available. |

## Module Coverage Summary

| Coverage Level | Count | Modules |
|---------------|-------|---------|
| 5 patterns | 1 | M50 |
| 4 patterns | 1 | M48 |
| 3 patterns | 3 | M46, M47, M49 |
| 1 pattern | 1 | M43 |

## Attenuation vs Pattern Count Comparison

| Module | Attenuation Rules | Pattern Count | Pattern Role |
|--------|------------------|---------------|-------------|
| M50 | 4 | 5 | Terminal node — most patterns, strongest attenuation |
| M48 | 1 (HRG) | 4 | Entry + dual-boundary participant |
| M46 | 1 (HRG) | 3 | Entry node |
| M47 | 3 | 3 | Strongest intermediate attenuation |
| M49 | 2 | 3 | Intermediate node |
| M43 | 0 | 1 | Weakest — no attenuation, fewest patterns |

---

*End of module-pattern association matrix. All patterns are conceptual_only=true, executable=false.*
