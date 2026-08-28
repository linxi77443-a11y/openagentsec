# 《AI 攻击行为理论手册》— 术语表

## 使用说明

本术语表面向安全从业者、架构师、AI 治理负责人和决策者。每个术语用 1–2 段解释其含义、使用场景和级别限定。所有术语和结论均为 candidate-level，不得理解为 confirmed vulnerability 或 production risk 判定。

---

### authorized evaluation（授权评估）

一种受控安全评估方法，评估只在明确授权范围内对指定系统或模块进行，不连接真实系统、不访问真实数据、不执行真实工具。本项目中的所有评估均为 authorized evaluation，所有发现的"信号"均为 simulated signal。

### simulated signal（模拟信号）

在授权评估框架下，评估工具或方法论产生的行为观察结果。Simulated signal 表示在受控环境中观察到的潜在风险模式，但它不等于 confirmed vulnerability。一个 simulated signal 需要经过 human review 才能上升为 finding candidate。

### finding candidate（发现候选）

经过 human review 初筛后，被认为值得进一步确认的 simulated signal。Finding candidate 仍处于候选状态，不视为正式漏洞。多个 finding candidate 可以合并、降级或升级，取决于后续验证和 human review 结果。

### confirmed vulnerability（已确认漏洞）

本项目明确不产生 confirmed vulnerability。所有观察结果停留在 candidate 或 simulated 层级。Confirmed vulnerability 需要真实系统验证和生产环境证据，不在本项目的 defensive evaluation 范围内。

### formal finding（正式发现）

本项目明确不产生 formal finding。所有分析结论（包括 tabletop observation、theory model 输出、pattern candidate）仅供 human review 参考，不构成正式的漏洞报告或安全审计发现。

### tabletop exercise（桌面推演）

一种结构化的定性分析方法，在受控环境中模拟攻击路径的逐步展开。Tabletop exercise 基于假设场景和已知的模块行为边界，不连接真实系统、不执行真实攻击。本项目完成了三次 tabletop exercise：一次全生命周期路径和两次短路径批次。

### attack graph（攻击图）

跨模块攻击路径的图形化表示，包含节点（模块）、边（传播关系）、路径（攻击链）和层（供应链→开发环境→知识库→运行时）。攻击图是理论模型的结构骨架，不表示真实攻击网络。

### propagation dynamics（传播动力学）

描述攻击压力在攻击图各节点之间如何传播、衰减、放大、阻断和形成反馈循环的理论模型。传播动力学基于 Phase 77A 的 5 类衰减规则、3 类放大规则、4 类阻断规则和 4 类反馈循环，所有规则均为 conceptual 层级。

### defense degradation trajectory（防御降级轨迹）

描述被攻击模块的防御状态随时间变化的轨迹。每个模块的防御状态可经历：stable → pressured → degraded → blocked → recovering / isolated / compromised / bypassed。本项目通过 tabletop exercise 观察并记录了三组防御降级轨迹。

### attack evolution trajectory（攻击演化轨迹）

描述攻击压力从入口模块到终端模块的逐步推进过程，与 defense degradation trajectory 对应。攻击演化轨迹关注的是攻击如何穿越各层防御，而非防御如何失效。

### pattern library（模式库）

从多次 tabletop exercise 中沉淀的可复用攻击模式集合。本项目归纳了 8 个跨模块攻击模式，每个模式包含触发条件、行为表现、衰减节点、放大因子等结构化字段。Pattern 是 candidate 层级，不是检测规则。

### unified theory model（统一理论模型）

整合攻击图结构、传播动力学规则、tabletop 观察数据和模式权重的理论框架。核心产出为 3 个概念方程（P_edge、D_node、G_path）和 6 个权重因子。该模型是 conceptual 层级，不可执行，不产生风险评分。

### formal system（形式化系统）

统一理论模型的形式化数学表达的规划概念。将攻击图、传播动力学和理论模型映射为集合、关系、公理和定理候选的框架。本项目的形式化系统处于概念规划阶段（Phase 84A pending），尚未完成。

### human review gate（人工复核门控）

在评估流程中设计的人工审查节点。所有评估结果、模拟信号和理论模型输出必须经过人类审查员复核后才能进入下一阶段。Human review gate 不自动化，不替代安全专家判断。

### M50 audit confirmation（M50 审计确认）

Agent Runtime Sandbox（M50）作为审计确认节点的角色。M50 接收上游模块的审计信息并执行规则检查（审计依赖检查、权限验证、凭据压力检查、运行时资源检查）。在三次 tabletop exercise 中，M50 均维持在 pressured 状态，未被完全突破。

### M50 sandbox execution boundary（M50 沙箱执行边界）

Agent Runtime Sandbox（M50）作为执行阻断节点的角色。M50 通过沙箱机制阻断上游模块的工具调用和命令执行。在三次 tabletop exercise 中，M50 的沙箱边界均未失效。

### candidate-level conclusion（候选级结论）

本项目所有结论的共同限定层级。Candidate-level 含义包括：
- 未经过真实系统验证
- 不构成 confirmed vulnerability
- 不构成 formal finding
- 不构成 production risk 判定
- 仅供 human review 参考
- 可能因后续发现而被修正或废弃

### controlled replay（受控回放）

一种评估验证方法，在受控环境中重新执行先前记录的评估过程以验证结果一致性。本项目在设计层面考虑了 controlled replay 架构，但在所有已完成阶段中均未进入 controlled replay 执行。

### defense in depth for AI systems（AI 系统纵深防御）

本手册所描述的六模块防御架构体现的核心理念：AI 系统的安全性不依赖于单一防御点，而是通过多层防御（MCP 工具描述完整性 → 仓库上下文保护 → 命令/凭据边界 → RAG 文档安全 → 权限审计 → 运行时沙箱）实现纵深防御效果。
