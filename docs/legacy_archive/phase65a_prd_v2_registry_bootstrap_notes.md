# Phase 65A — PRD v2.0 Extension Addendum and Registry Bootstrap Notes

## 范围

本阶段是 **PRD v2.0 addendum 编写 + registry bootstrap**，仅建立 v2.0 生命周期攻击矩阵覆盖评估的规划基础。

## 本阶段完成的内容

- PRD v2.0 扩展章节：`docs/prd_v2_extension_addendum.md`
- attack_objective 枚举新增 20 个 v2.0 枚举值（supply_chain / dev_environment / rag / runtime）
- M43–M50 registry 条目（8 个新增模块）

## M43–M50 初始状态

所有 v2.0 新增模块初始 coverage_status 统一为 `v2_planned`。

| 模块 | 名称 | Domain | 初始状态 |
|------|------|--------|---------|
| M43 | MCP Tool Descriptor Integrity | ai_supply_chain_security | v2_planned |
| M44 | A2A Agent Identity Trust Boundary | ai_supply_chain_security | v2_planned |
| M45 | AI Dependency Integrity | ai_supply_chain_security | v2_planned |
| M46 | Coding Agent Repository Context Injection | development_environment_security | v2_planned |
| M47 | Coding Agent Command and Credential Boundary | development_environment_security | v2_planned |
| M48 | RAG Document Poisoning and Instruction Boundary | rag_data_security | v2_planned |
| M49 | RAG Permission Inheritance and Retrieval Audit | rag_data_security | v2_planned |
| M50 | Agent Runtime Sandbox and Audit Chain Integrity | runtime_sandbox_security | v2_planned |

## 本阶段不执行

- 不新增 corpus
- 不新增 run_config
- 不执行 capability_engine
- 不生成 execution_results
- 不生成 M43–M50 result.yaml
- 不声明 capability_value / risk_level
- 不声明 mvp_complete
- 不声明 controlled_replay_ready
- 不声明 execution_complete
- 不声明 production_ready

## 安全声明

- `confirmed_vulnerability_allowed`: false
- `formal_finding_allowed`: false
- `production_safety`: out_of_scope
- `synthetic_only`: true
- `controlled_replay_claimed`: false
- 所有数据使用 `<SIM_...>` / fake / synthetic only
- 不连接真实系统，不使用真实凭证，不执行真实工具调用

## 设计/bootstrap only (design/bootstrap only)

本阶段所有产出仅为设计规划，不产生任何可执行的评估结果。
