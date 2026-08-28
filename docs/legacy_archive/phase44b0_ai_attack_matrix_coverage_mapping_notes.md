# Phase 44B.0 — AI Attack Matrix Coverage Mapping Notes

## Scope

本阶段只做覆盖映射，不开发新模块。目标是基于 module_registry 和已完成模块，
建立从完成模块到 AI 攻击矩阵 / Agent 攻击链的映射关系，明确覆盖范围、空白区域、
后续优先级，防止继续按模块编号开发而偏离矩阵覆盖策略。

本阶段基于项目内 registry 与已完成模块做初版映射，不声称完整覆盖。

## Current Capability Chain

已完成或预研的能力链（按评估粒度递进）：

```
基础模型行为 ─→ 外部内容边界 ─→ 多源上下文 ─→ 动作决策
  (M01/M02/M03)     (M06)          (M38)        (M39)

动作决策 ─→ 工具调用安全 ─→ 工具参数注入 ─→ 高风险动作 ─→ 业务动作语义
             (M12)             (M13)         (M14)        (M15)

后续链路（参考级别）：
  └→ 人工审批关卡 (M16, reference only)
```

## Current Module Coverage Table

| Module | Name | Layer | ATLAS Area | Coverage | Evidence |
|--------|------|-------|------------|----------|----------|
| M01 | Prompt Injection / Bypass | chatbot | Execution / LLM Prompt Injection | candidate available | promptfoo corpus |
| M02 | System Prompt Leakage | chatbot | Execution / Extract LLM System Prompt | candidate available | promptfoo corpus |
| M03 | RAG Boundary Exposure | rag | Execution / RAG Poisoning | candidate available | promptfoo corpus |
| M06 | Indirect Prompt Injection | rag | Execution / Indirect Prompt Injection | **MVP done** | corpus, run, result, scorecard |
| M38 | Agent Multi-Source Input Injection | agent | Execution / Agent Context Poisoning | **MVP done** | corpus, run, result, scorecard |
| M39 | Agent Runtime State Corruption | agent | Execution / AI Agent Tool Poisoning | **MVP done** | corpus, run, result, scorecard, refinement |
| M12 | Agent Tool Invocation Safety | agent | Tool Execution / Tool Misuse | **MVP done** | corpus, run, result, scorecard |
| M13 | Agent Tool Argument Injection | agent | Tool Execution / Tool Argument Pollution | **MVP done** | corpus, run, result, scorecard |
| M14 | Agent High-Risk Action Simulation | agent | Action Execution / Destructive Action | **MVP done** | corpus, run, result, scorecard |
| M15 | Business Action Simulation | agent | Action Execution / Business Logic Error | **MVP done** | corpus, run, result, scorecard |
| M16 | Human Approval Gate Validation | agent | Action Execution / Approval Bypass | **reference only** | boundary notes |
| M40 | Agent Action Audit & Attribution | agent | Defense / Audit Trail | **defined, not started** | — |
| M41 | Agent Service Account Permission Boundary | agent | Privilege / Service Account | **defined, not started** | — |
| M42 | Code Execution Sandbox Validation | agent | Execution / Code Sandbox | **defined, not started** | — |
| M07 | Unauthorized Data Access Simulation | agent | Data Access / Unauthorized Access | **defined, not started** | — |
| M08 | Authorization / Role Boundary Validation | agent | Privilege / Role Boundary | **defined, not started** | — |
| M09 | RAG Permission-Aware Retrieval | rag | Data Access / Permission Filter | **defined, not started** | — |
| M04 | Sensitive Data Leakage | chatbot | Data / Data Leakage | candidate available | promptfoo corpus |
| M17 | AI Asset & Exposure Surface Mapping | inventory | Recon / Asset Discovery | **defined, not started** | — |
| M19 | Business Data Exposure Validation | rag | Data / Business Data Leakage | **defined, not started** | — |
| M20 | Mock Data Exfiltration Path Validation | agent | Exfiltration / Tool Exfiltration | **defined, not started** | — |
| M27 | File Upload / Document Ingestion Safety | rag | Supply Chain / File Ingestion | **defined, not started** | — |
| M28 | Connector / SaaS Boundary Validation | agent | Privilege / Connector Scope | **defined, not started** | — |
| M34 | RAG / Knowledge Base Poisoning | rag | Data / Knowledge Base Poisoning | **defined, not started** | — |
| M35 | MCP / Tool Descriptor Poisoning | agent | Supply Chain / Tool Descriptor | **defined, not started** | — |
| M36 | Model DoS / Cost Exhaustion | chatbot | Resource / Cost Consumption | **defined, not started** | — |
| M42 | Code Execution Sandbox Validation | agent | Execution / Sandbox Escape | **defined, not started** | — |

## Agent Attack Chain vs Coverage

基于 MITRE ATLAS 战术阶段和项目实际模块映射：

```
┌──────────────────────────────────────────────────────────────────┐
│                       AI ATTACK CHAIN                            │
├──────────────────────────────────────────────────────────────────┤
│ Recon / Discovery          │ M17 (defined)  ── NOT STARTED       │
│ Initial Access             │ M01/M02/M03/M06/M38 ── COVERED      │
│ Resource Development       │ M35 (defined)  ── NOT STARTED       │
│ Execution (Prompt Inj.)    │ M01/M02/M03/M06 ── COVERED           │
│ Execution (Tool Call)      │ M12/M13/M14 ── COVERED               │
│ Execution (Business)       │ M15 ── COVERED, M16 (reference)     │
│ Execution (Code)           │ M42 (defined)  ── NOT STARTED       │
│ Persistence                │ undefined      ── NOT COVERED       │
│ Privilege Escalation       │ M08/M41 (defined) ── NOT STARTED    │
│ Defense Evasion            │ M01 obfuscation ── PARTIAL           │
│ Credential Access          │ M04/M07 (defined) ── PARTIAL/NOT    │
│ Discovery (internal)       │ undefined      ── NOT COVERED       │
│ Collection / Data Access   │ M07/M09/M19 ── NOT STARTED          │
│ Exfiltration               │ M20 (defined)  ── NOT STARTED       │
│ Impact                     │ M14/M15/M21/M22 ── PARTIAL/NOT      │
│ Cost / Resource            │ M36 (defined)  ── NOT STARTED       │
│ Audit / Log Evasion        │ M40 (defined)  ── NOT STARTED       │
└──────────────────────────────────────────────────────────────────┘
```

Key: **COVERED** = MVP or equivalent done; PARTIAL = only basic coverage;
NOT STARTED = defined in registry but no implementation.

## Covered Areas

以下区域当前已有实际评估能力：

1. **Prompt / External Content Manipulation** (ATLAS: LLM Prompt Injection, RAG Poisoning, Indirect Prompt Injection) — M01/M02/M03/M06
   - 覆盖多层：直接注入、间接注入、编码绕过、系统提示词提取
   - 工具：promptfoo + capability_engine
   - 局限性：需增强多语言、隐藏指令、跨轮注入变体

2. **Multi-Source Context Manipulation** (ATLAS: Agent Context Poisoning) — M38
   - 覆盖：用户输入 + 工具返回 + 系统状态联合注入
   - capability_engine MVP 完成

3. **Agent Action Manipulation** (ATLAS: AI Agent Tool Poisoning) — M39
   - 覆盖：运行时状态污染导致动作决策异常
   - 工具：capability_engine + mock Agent tools

4. **Tool Invocation Abuse** (ATLAS: AI Agent Tool Invocation) — M12
   - 覆盖：未授权工具、超频调用、高频、高影响工具
   - 工具：capability_engine + mock tools

5. **Tool Argument Pollution** (ATLAS: AI Agent Tool Data Poisoning) — M13
   - 覆盖：参数注入、参数篡改、schema 验证

6. **High-Risk Action Handling** (ATLAS: 无直接映射 — 对应"拒绝直接执行高风险操作")
   - M14：删除、覆盖、提权动作拒绝

7. **Business Action Semantics** (ATLAS: 无直接映射 — 对应"业务操作逻辑错误")
   - M15：SKU、金额、账户、审批链、状态跳转验证

8. **Approval Gate** (ATLAS: 部分覆盖 — 对应"审批绕过") — M16
   - 仅 reference notes，未执行

## Missing or Weakly Covered Areas

以下区域当前覆盖不足或完全空白（按优先级排列）：

1. **Data Poisoning / RAG Poisoning** — M34 (P2)
   - 知识库投毒是真实企业场景的核心攻击面
   - 当前 M03/M06 覆盖了"注入"，但未覆盖"投毒/篡改既有知识"
   - 建议：至少做 reference spike

2. **Exfiltration / Data Leakage** — M20 (P1), M04 (P0), M19 (P0)
   - 数据外泄是 Agent 安全最高风险场景之一
   - 当前只有 promptfoo 级别的基础覆盖（M04）
   - 建议：M20 可做模拟外泄路径验证

3. **Credential Access / Unauthorized Data Access** — M07 (P0)
   - 未授权数据访问是 P0 模块但完全未开始
   - 建议：至少做 boundary reference spike

4. **Authorization / Permission Boundary** — M08 (P0), M41 (P0), M09 (P0), M28 (P1)
   - 权限边界是 P0 级别但完全空白
   - 角色权限、服务账号权限、RAG 权限感知检索、连接器权限
   - 最大的战略空白之一

5. **Code Execution / Sandbox Boundary** — M42 (P1)
   - 代码执行沙箱验证完全未开始
   - 需要模拟环境，不能使用真实沙箱

6. **Audit Trail Validation** — M40 (P0)
   - 审计日志完整性验证是 P0 但完全未开始
   - 需要 M40 审计框架 + 模拟审计日志

7. **Persistence / Memory Corruption**
   - 项目内无对应模块定义
   - Agent 持久化记忆污染是新型攻击面
   - 建议：如果项目内无定义，先不做

8. **Defense Evasion** — 仅有 M01 编码绕过基础覆盖
   - 无专门对抗检测/对抗混淆模块

9. **Cost Harvesting / Resource Consumption** — M36 (P2)
   - 成本耗尽是 P2，可暂缓

10. **Recon / Discovery** — M17 (P0)
    - AI 资产发现是 P0 但需要企业环境配合

11. **Supply Chain / Tool Descriptor Poisoning** — M35 (P2)
    - MCP 协议投毒值得关注但优先级低

## Agent Runtime Subchain Assessment

### 当前强项

项目当前已形成完整的 **Agent Runtime / Tool / Action Safety** 子链路：

```
                                  ┌─ M06: External Content
                                  │   (indirect injection into agent context)
     M01/M02/M03 ─→ M38 ─→ M39 ──┼─ M12: Tool Invocation Safety
     (base model)   (multi-   (action  ├─ M13: Tool Argument Integrity
                     source)   decision)├─ M14: High-Risk Action Simulation
                                        ├─ M15: Business Action Simulation
                                        └─ M16: Approval Gate (reference)
```

这是完整 AI 安全评估中的一个重要子集，覆盖了从"输入污染"到"工具滥用"到"高风险动作"
到"业务逻辑错误"的完整链条。capability_engine 使该子链可执行、可复用、可评分。

### 明确限制

1. **这只是完整 AI attack matrix 的子集**。Agent runtime 覆盖不代表 full matrix。
2. **缺少数据层覆盖**：外泄、投毒、未授权访问均未覆盖。
3. **缺少权限层覆盖**：角色、服务账号、连接器权限均未覆盖。
4. **缺少审计层覆盖**：审计日志验证未开始。
5. **缺少持久化覆盖**：跨会话记忆污染未定义。
6. **不能声称 full matrix coverage**。

## Recommended Next Priorities

基于 module_registry 优先级和当前覆盖空白：

### Phase 44B.1 (immediate, 1-2 days): Matrix Coverage Registry Alignment

```
Goal:   将 module_registry.yaml 与 coverage mapping 对齐
Action: 在 module_registry.yaml 每个模块中新增 coverage_status 字段
        更新 per_module_summary 或类似结构以包含覆盖阶段信息
Deliverable: 更新 registry + 短 notes
Priority: HIGH — 防止后续开发继续偏离矩阵覆盖
```

### Phase 45A (next, 2-3 days): P0 Gap — Data / Access Layer Reference Spike

```
Target: M07 (Unauthorized Data Access, P0) + M04 (Sensitive Data Leakage, P0)
        同时评估 M19 (Business Data Exposure, P0) 边界
Rationale: P0 模块中最大覆盖空白，数据泄露是最高风险场景之一
Method: 只做 reference spike，查 registry 确认正式定义
        不做 MVP，不做 API 调用
        评估是否可以通过 capability_engine 模拟
Priority: HIGH
```

### Phase 46A (next, 2-3 days): P0 Gap — Permission Boundary Reference Spike

```
Target: M08 (Authorization/Role Boundary, P0) + M41 (Service Account, P0)
Rationale: P0 模块权限边界完全空白
Method: 只做 reference spike
        评估是否可以合并评估
Priority: HIGH
```

### Phase 47A (next, 3-5 days): M20 Exfiltration Simulation MVP (P1)

```
Target: M20 (Mock Data Exfiltration Path Validation, P1)
Rationale: 数据外泄是 Agent 安全最高风险场景，M20 是 P1 中最重要的模块
Method: capability_engine MVP (模拟外泄路径，不做真实外传)
        8 条 MVP corpus + 完整 corpus + parser 扩展
Priority: MEDIUM (P1, 但外泄风险高)
```

### After filling P0 gaps: Reassess

```
恢复 M16 MVP 或开始 M40/M41/M42 reference spike
具体方向取决于 Phase 44B.1 coverage registry alignment 的结果
```

## Decision Recommendation

### 是否继续 M16 MVP？

**不建议现在继续 M16 MVP。**

理由：
1. M16 是 P1，但 P0 模块中 M07/M08/M41/M19/M17/M18/M40 未开始。
2. M16 与 M14 有重叠（都涉及高风险操作），M14 已覆盖"风险感知"，M16 的增量
   "流程合规"是增强而非补白。
3. 当前更大的空白在数据层（M07/M04/M19）和权限层（M08/M41），这些是 P0。

建议：**先补 P0 空白 → 再做 M16 reference → 决定是否 MVP**。

### Coverage Registry Alignment

**建议立即执行。**

当前 module_registry 只有 current_status（defined/candidate_available），
没有 coverage_status（covered/mvp/reference/not_started）字段。
补充此字段可以：
- 防止开发跑偏
- 帮助排期决策
- 向 stakeholders 展示真实进展

### 下一最合理开发方向

**Phase 44B.1 → Phase 45A (M07+M04 reference) → Phase 46A (M08+M41 reference)
→ 然后根据 alignment 结果决策**

### 哪些方向只适合 reference spike

- **M34 RAG/KB Poisoning** (P2) — 知识库投毒评估需要真实业务知识库或高仿真 mock，
  当前阶段只能做 reference，不能做 MVP。
- **M35 MCP/Tool Descriptor Poisoning** (P2) — 需要 MCP 协议深度调研，只能 reference。
- **M36 Cost Exhaustion** (P2) — 成本耗尽评估需要配额监控机制，只能 reference。
- **M42 Code Execution Sandbox** (P1) — 沙箱评估需要真实或高仿真沙箱环境，
  当前只能做 reference + 架构评估。
- **M40 Agent Action Audit** (P0) — 审计日志验证需要审计框架运行数据，
  reference 阶段可做 schema 和边界定义。

## Non-Goals

本次覆盖映射不做：
- 不开发新模块
- 不跑 API
- 不生成 corpus
- 不新增 run config
- 不修改 parser
- 不执行 capability_engine
- 不连接业务系统
- 不做真实攻击
- 不做真实漏洞验证
- 不生成 confirmed vulnerability
- 不生成 formal finding
- 不做外传、凭证访问、攻击 payload
- 不读取 .local/
- 不提交 API key 或 Authorization header
- 不研究 M40/M41/M42 的实现细节
