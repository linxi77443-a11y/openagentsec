# Cross-Module Attack Pattern Index

> **Conceptual pattern index only** — not executable, not vulnerability evidence, not production risk taxonomy.

## Pattern Index

| # | Pattern ID | English Name | 中文名称 | Source Paths | Status |
|---|-----------|-------------|---------|-------------|--------|
| 1 | PATTERN-UPSTREAM-ENTRY-DEGRADATION-001 | Upstream Entry Degradation Pattern | 上游入口劣化模式 | PATH-SUPPLY-DEV-RAG-RUNTIME-001, PATH-DEV-CRED-RUNTIME-001, PATH-RAG-RUNTIME-001 | confirmed_across_3_paths |
| 2 | PATTERN-M50-AUDIT-CONFIRMATION-001 | M50 Audit Confirmation Pattern | M50 审计确认模式 | PATH-SUPPLY-DEV-RAG-RUNTIME-001, PATH-DEV-CRED-RUNTIME-001, PATH-RAG-RUNTIME-001 | confirmed_across_3_paths |
| 3 | PATTERN-M50-SANDBOX-BOUNDARY-001 | M50 Sandbox Execution Boundary Pattern | M50 沙箱执行边界模式 | PATH-SUPPLY-DEV-RAG-RUNTIME-001, PATH-RAG-RUNTIME-001 | confirmed_across_2_paths |
| 4 | PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001 | Credential Boundary Attenuation Pattern | 凭据边界衰减模式 | PATH-DEV-CRED-RUNTIME-001 | observed_in_1_path |
| 5 | PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001 | Permission Leakage Amplification Pattern | 权限泄漏放大模式 | PATH-RAG-RUNTIME-001, PATH-SUPPLY-DEV-RAG-RUNTIME-001 | observed_in_2_paths |
| 6 | PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001 | Repository Context to Runtime Pressure Pattern | 仓库上下文到运行时压力模式 | PATH-DEV-CRED-RUNTIME-001, PATH-SUPPLY-DEV-RAG-RUNTIME-001 | observed_in_2_paths |
| 7 | PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001 | RAG to Audit Chain Dependency Pattern | RAG 到审计链依赖模式 | PATH-RAG-RUNTIME-001, PATH-SUPPLY-DEV-RAG-RUNTIME-001 | observed_in_2_paths |
| 8 | PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | Human Review Breakpoint Pattern | 人工复核断点模式 | PATH-SUPPLY-DEV-RAG-RUNTIME-001, PATH-DEV-CRED-RUNTIME-001, PATH-RAG-RUNTIME-001 | confirmed_across_3_paths |

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total patterns | 8 |
| Source phases | 2 (79A, 80A) |
| Source paths | 3 |
| Covered modules | 6 (M43, M46, M47, M48, M49, M50) |
| Covered layers | 4 (supply_chain, development_environment, rag_data, runtime_sandbox) |
| confirmed_across_3_paths | 3 patterns |
| confirmed_across_2_paths | 1 pattern |
| observed_in_2_paths | 3 patterns |
| observed_in_1_path | 1 pattern |

## Pattern Category Summary

| Category | Patterns | Count |
|----------|----------|-------|
| Entry/Exit dynamics | PATTERN-UPSTREAM-ENTRY-DEGRADATION-001, PATTERN-M50-AUDIT-CONFIRMATION-001, PATTERN-M50-SANDBOX-BOUNDARY-001 | 3 |
| Intermediate attenuation | PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001 | 1 |
| Amplification | PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001 | 1 |
| Path-specific propagation | PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001, PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001 | 2 |
| Universal breakpoint | PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | 1 |

## Related Documents

| Document | Path |
|----------|------|
| Pattern Library Report | `reports/phase81a_cross_module_attack_pattern_library.md` |
| Path-Pattern Association Matrix | `docs/cross_module_path_pattern_association_matrix.md` |
| Module-Pattern Association Matrix | `docs/cross_module_module_pattern_association_matrix.md` |
| Phase 81A Notes | `docs/phase81a_cross_module_attack_pattern_library_notes.md` |
| Phase 81A Checklist | `docs/phase81a_cross_module_attack_pattern_library_checklist.md` |
| Phase 81A Result | `results/phase81a_cross_module_attack_pattern_library_result.yaml` |

---

*End of pattern index. All patterns are conceptual_only=true, executable=false.*
