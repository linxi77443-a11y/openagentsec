# PRD v2.0 Extension Addendum

## 文档信息

| 字段 | 值 |
|---|---|
| 版本 | v2.0-addendum |
| 状态 | Draft |
| 阶段 | Phase 65A |
| 创建日期 | 2026-06-25 |
| 前序版本 | PRD v0.2.1 (Phase 35C) |

## 定位升级

v1.0 基线（Phase 64A 完成）将评估范围锁定在 **Agent 行为安全评估**，覆盖 10 类攻击剧本的 MVP 验证和 P0 防守模块的能力评估。

v2.0 将评估定位升级为 **AI 系统全生命周期攻击矩阵覆盖评估**，在 v1.0 的 Agent 行为安全基础上，扩展至以下新增攻击阶段：

- **AI 供应链安全** — MCP 工具描述完整性、A2A Agent 身份信任、AI 依赖完整性
- **开发环境安全** — Coding Agent 仓库上下文注入、命令与凭据边界
- **RAG 数据安全** — RAG 文档投毒与指令边界、权限继承与检索审计
- **运行时沙箱与审计链路** — Agent 运行时沙箱逃逸、审计链完整性

## v1.0 已完成部分与 v2.0 新增部分关系

| 维度 | v1.0 (基线冻结) | v2.0 (扩展规划) |
|---|---|---|
| 范围 | Agent 行为安全 (10 类攻击剧本 + P0 防守模块) | 全生命周期攻击矩阵覆盖 |
| 模块 | M01–M42（MVP 完成或已定义） | M43–M50（v2_planned） |
| 评估模式 | defensive_evaluation + adversarial_validation | 同上，双模设计保持不变 |
| corpus | 已生成各模块 MVP/full corpus | 本阶段不新增 corpus |
| 执行状态 | 已执行 capability_engine | 本阶段不执行 |
| production_safety | 全部 out_of_scope | 全部 out_of_scope |

v1.0 所有模块保持原 coverage_status，不回退、不重开。v2.0 仅新增 M43–M50 规划条目，不修改 v1.0 已完成模块的状态。

## 双模设计

两阶段评估模式保持不变，v2.0 新增模块同样支持：

- **defensive_evaluation** — 验证模型/Agent 是否按设计规则拒绝越权行为
- **adversarial_validation** — 使用攻击者视角 prompt 模拟攻击者的诱导和技术手法

选择哪种模式由评估任务在任务单中指定，双模设计服务于不同的评估目标。

## 统一安全边界

v2.0 所有模块统一遵循以下安全边界：

| 字段 | 值 |
|---|---|
| production_safety | out_of_scope |
| synthetic_only | true |
| confirmed_vulnerability_allowed | false |
| formal_finding_allowed | false |
| controlled_replay_claimed | false |
| controlled_replay_execution_allowed | false |

## 新增 attack_objective 分类

v2.0 在现有 attack_objective 枚举（data_exposure, unauthorized_access, tool_misuse, role_escalation, service_account_abuse, approval_bypass, business_action_induction, context_poisoning, exfiltration_simulation）基础上新增以下枚举：

**AI 供应链安全：**
- `supply_chain_tool_descriptor_poisoning` — MCP 工具描述中毒
- `supply_chain_agent_identity_spoofing` — A2A Agent 身份伪造
- `supply_chain_malicious_dependency_injection` — 恶意依赖注入
- `supply_chain_tool_manifest_drift` — 工具清单漂移
- `supply_chain_trust_boundary_confusion` — 信任边界混淆

**开发环境安全：**
- `dev_environment_repository_context_injection` — 仓库上下文注入
- `dev_environment_unauthorized_command_induction` — 未授权命令诱导
- `dev_environment_credential_exposure_attempt` — 凭据暴露尝试
- `dev_environment_agent_permission_confusion` — Agent 权限混淆
- `dev_environment_code_review_bypass` — 代码审查绕过

**RAG 数据安全：**
- `rag_malicious_document_poisoning` — 恶意文档投毒
- `rag_permission_inheritance_bypass` — 权限继承绕过
- `rag_cross_tenant_retrieval_attempt` — 跨租户检索尝试
- `rag_retrieval_audit_gap_detection` — 检索审计缺口检测
- `rag_source_attribution_confusion` — 来源归因混淆

**运行时沙箱与审计链路：**
- `runtime_sandbox_escape_signal` — 沙箱逃逸信号
- `runtime_fake_tool_boundary_violation` — 虚假工具边界违反
- `runtime_audit_chain_tampering_signal` — 审计链篡改信号
- `runtime_trace_integrity_gap_detection` — 追踪完整性缺口检测
- `runtime_policy_enforcement_bypass` — 策略执行绕过

## 新增攻击阶段

### AI 供应链安全 (M43–M45)

AI 供应链安全涵盖 MCP（Model Context Protocol）工具描述、A2A Agent 身份信任、以及 AI 依赖完整性的安全验证。这些模块针对 AI 系统在集成外部工具、Agent 和服务时的供应链攻击面。

| 模块 | 名称 | 核心关注点 |
|---|---|---|
| M43 | MCP Tool Descriptor Integrity | MCP 工具描述被篡改或注入恶意指令 |
| M44 | A2A Agent Identity Trust Boundary | Agent 间身份伪造和信任边界混淆 |
| M45 | AI Dependency Integrity | 恶意依赖注入和工具清单漂移 |

### 开发环境安全 (M46–M47)

开发环境安全覆盖 Coding Agent 在仓库上下文、命令执行和凭据管理中的安全风险。这些模块针对 AI 辅助编程场景中的特有攻击面。

| 模块 | 名称 | 核心关注点 |
|---|---|---|
| M46 | Coding Agent Repository Context Injection | 仓库上下文中的恶意指令注入 |
| M47 | Coding Agent Command and Credential Boundary | 未授权命令执行和凭据泄露 |

### RAG 数据安全 (M48–M49)

RAG 数据安全扩展 v1.0 中 M03/M07/M19 的数据安全能力，聚焦文档投毒、权限继承和检索审计领域。

| 模块 | 名称 | 核心关注点 |
|---|---|---|
| M48 | RAG Document Poisoning and Instruction Boundary | 恶意文档投毒导致的指令边界违反 |
| M49 | RAG Permission Inheritance and Retrieval Audit | 跨租户检索和检索审计完整性 |

### 运行时沙箱与审计链路 (M50)

运行时沙箱与审计链路针对 Agent 运行时的沙箱逃逸、审计链篡改和策略执行绕过等高风险场景。

| 模块 | 名称 | 核心关注点 |
|---|---|---|
| M50 | Agent Runtime Sandbox and Audit Chain Integrity | 沙箱逃逸、审计链篡改、策略绕过 |

## M43–M50 Registry 对应关系

M43–M50 新增模块的完整 registry 条目见 `capability_modules/module_registry.yaml`，初始 coverage_status 统一为 `v2_planned`。

所有 M43–M50 模块在本阶段满足以下条件：

- 覆盖状态: `v2_planned`
- 安全级别: `simulated_runtime_safety`
- 使用合成数据: `true`
- 正式发现: `false`
- 生产环境安全: `out_of_scope`
- 受控重放: `false`
- MVP 完成: `false`
- 能力执行: `false`

## Phase 65A 范围限定

Phase 65A 仅为 **PRD v2.0 addendum 编写 + registry bootstrap**，不做以下任何事项：

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
- 不连接真实系统
- 不使用真实凭证
- 不执行真实工具调用

所有 v2.0 新增内容保持 `<SIM_...>` / fake / synthetic only。

## 下一步建议

Phase 65A 完成后，建议优先进入 **Phase 66A — M43 MCP Tool Descriptor Integrity MVP**，理由：

- M43 与现有 Tool Invocation Safety (M12)、Tool Argument Integrity (M13)、Indirect Prompt Injection (M06)、Multi-Source Context Boundary (M38) 关联最强
- 可完全使用 `<SIM_MCP_TOOL_DESCRIPTOR_...>`、`<SIM_TOOL_MANIFEST_...>`、fake runtime 和 synthetic corpus
- 不需要连接真实 MCP Server
- 适合作为 v2.0 新增生命周期模块的第一个 MVP

备选：**Phase 66A — M48 RAG Document Poisoning and Instruction Boundary MVP**，如果优先扩展 RAG 数据安全层。
