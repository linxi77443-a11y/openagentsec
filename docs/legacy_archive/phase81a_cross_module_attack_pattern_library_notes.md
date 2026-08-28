# Phase 81A — 跨模块攻击模式库 MVP

## 范围

本阶段基于 Phase 79A 和 Phase 80A 的 tabletop 推演结果，建立跨模块攻击模式库 MVP。模式库将三条推演路径中重复出现的传播结构、边界压力、衰减节点、放大因素、审计确认、权限泄漏、凭据边界压力和 M50 最终防线作用抽象为 8 个可复用模式。

## 来源路径

| 路径 | 来源阶段 | 模块 | 层 |
|------|---------|------|-----|
| PATH-SUPPLY-DEV-RAG-RUNTIME-001 | 79A | M43 → M46 → M48 → M49 → M50 | supply_chain → development_environment → rag_data → runtime_sandbox |
| PATH-DEV-CRED-RUNTIME-001 | 80A | M46 → M47 → M50 | development_environment → runtime_sandbox |
| PATH-RAG-RUNTIME-001 | 80A | M48 → M49 → M50 | rag_data → runtime_sandbox |

## 交付物

| 文件 | 内容 |
|------|------|
| `reports/phase81a_cross_module_attack_pattern_library.md` | 模式库主文档（11 节，8 模式） |
| `docs/cross_module_attack_pattern_index.md` | 模式索引（含中文名称） |
| `docs/cross_module_path_pattern_association_matrix.md` | 路径-模式关联矩阵（3 路径） |
| `docs/cross_module_module_pattern_association_matrix.md` | 模块-模式关联矩阵（6 模块） |
| `docs/phase81a_cross_module_attack_pattern_library_notes.md` | 本说明文件 |
| `docs/phase81a_cross_module_attack_pattern_library_checklist.md` | 非可执行检查清单 |
| `results/phase81a_cross_module_attack_pattern_library_result.yaml` | 模式库结果 |

## 模式列表

| # | 模式 ID | 英文名 | 中文名 |
|---|---------|--------|--------|
| 1 | PATTERN-UPSTREAM-ENTRY-DEGRADATION-001 | Upstream Entry Degradation Pattern | 上游入口劣化模式 |
| 2 | PATTERN-M50-AUDIT-CONFIRMATION-001 | M50 Audit Confirmation Pattern | M50 审计确认模式 |
| 3 | PATTERN-M50-SANDBOX-BOUNDARY-001 | M50 Sandbox Execution Boundary Pattern | M50 沙箱执行边界模式 |
| 4 | PATTERN-CREDENTIAL-BOUNDARY-ATTENUATION-001 | Credential Boundary Attenuation Pattern | 凭据边界衰减模式 |
| 5 | PATTERN-PERMISSION-LEAKAGE-AMPLIFICATION-001 | Permission Leakage Amplification Pattern | 权限泄漏放大模式 |
| 6 | PATTERN-REPO-CONTEXT-TO-RUNTIME-PRESSURE-001 | Repository Context to Runtime Pressure Pattern | 仓库上下文到运行时压力模式 |
| 7 | PATTERN-RAG-TO-AUDIT-CHAIN-DEPENDENCY-001 | RAG to Audit Chain Dependency Pattern | RAG 到审计链依赖模式 |
| 8 | PATTERN-HUMAN-REVIEW-BREAKPOINT-001 | Human Review Breakpoint Pattern | 人工复核断点模式 |

## 模式来源分析

### 从 PATH-SUPPLY-DEV-RAG-RUNTIME-001（Phase 79A）提取
- 上游入口劣化：M43 无衰减 → M46 仅 HRG → M48 有 safe_summary
- 全链路 M50 审计确认：5 模块 4 层的最终汇聚点
- 权限泄漏放大：M48 + M49 双边界串联
- 仓库上下文到运行时压力：M46 → M47 → (RAG chain)
- RAG 到审计链依赖：M48 → M49 → M50
- 人工复核断点：M46/M48/M49/M50 有 HRG，M43 无

### 从 PATH-DEV-CRED-RUNTIME-001（Phase 80A）提取
- 上游入口劣化：M46 快速劣化（仅 HRG）
- 凭据边界衰减：M47 3 条衰减规则（最强中间节点）
- 仓库上下文到运行时压力：M46 → M47 → M50
- M50 审计确认：审计链确认 M47 边界决策
- 人工复核断点：M46/M47/M50 有 HRG

### 从 PATH-RAG-RUNTIME-001（Phase 80A）提取
- 上游入口劣化：M48 慢速劣化（safe_summary 保护）
- RAG 到审计链依赖：M48 → M49 → M50
- 权限泄漏放大：M48 safe_summary + M49 permission 双边界
- M50 沙箱执行边界：沙箱边界作为最终执行屏障
- M50 审计确认：完整 retrieval-permission-audit 序列审计
- 人工复核断点：M48/M49/M50 有 HRG

## 模式覆盖统计

| 指标 | 值 |
|------|-----|
| 总模式数 | 8 |
| 来源路径数 | 3 |
| 覆盖模块数 | 6（M43, M46, M47, M48, M49, M50） |
| 覆盖层数 | 4（supply_chain, development_environment, rag_data, runtime_sandbox） |
| 3 路径确认模式 | 3（入口劣化、M50审计确认、人工复核断点） |
| 2 路径确认模式 | 1（M50沙箱边界） |
| 2 路径观察模式 | 3（权限泄漏放大、仓库上下文到运行时压力、RAG到审计链依赖） |
| 1 路径观察模式 | 1（凭据边界衰减） |

## 确认项

| 确认项 | 状态 |
|--------|------|
| tabletop_pattern=true 全部模式 | 通过 |
| conceptual_only=true 全部模式 | 通过 |
| executable=false 全部模式 | 通过 |
| new_evidence_generated=false | 通过 |
| human_review_required=true 全部模式 | 通过 |
| 8 个模式均已定义 | 通过 |
| 所有 pattern schema 字段完整 | 通过 |
| 路径-模式矩阵包含 ≥2 模式/路径 | 通过 |
| 模块-模式矩阵包含 ≥1 模式/模块 | 通过 |
| Safety Semantics Declaration 已添加 | 通过 |
| Forbidden Uses 已定义 | 通过 |

---

*Phase 81A 模式库说明文档末端。*
