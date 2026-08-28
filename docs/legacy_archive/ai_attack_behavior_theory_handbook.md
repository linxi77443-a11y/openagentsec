# AI 攻击行为理论手册

**Candidate-Level Reference — Human Review Required**

## 手册概述

本手册是项目 v1.0 至 v3.0 全部阶段性成果的理论性整理。它将分散在数十个阶段文档中的基础框架、单模块评估、跨模块攻击图、传播动力学、桌面推演、模式库、统一理论模型和形式化系统概念进行提取、重组和降噪，形成一份可供安全从业者、架构师、AI 治理负责人和决策者阅读的理论型资料。

**核心主线**：AI / Agent 攻击行为如何从单点模块风险演化为跨模块系统性风险。

**结论层级**：所有判断处于 candidate、conceptual、simulated、tabletop 或 theory model 层级。不声称真实漏洞、正式 finding 或生产安全结论。

---

# 第一部分：基础框架与问题定义

---

## 第 1 章：为什么需要 AI 攻击行为理论

### Purpose

说明 AI / Agent 安全评估从单轮提示词问题扩展为系统性行为问题的背景，解释为什么需要一套统一的攻击行为理论来组织跨模块风险分析。

### Key Ideas

**从提示词注入到行为链。** 早期的 AI 安全讨论集中于单轮 prompt injection——攻击者能否通过一条精心构造的文本让模型输出有害内容。但在 Agent 架构下，问题已经发生了质变：一个 Agent 可能通过多个步骤、调用多种工具、访问多个数据源来完成一个任务。攻击不再是一次性的输入污染，而是一条跨越多个系统模块的行为链。

**六个核心模块就是六个防御层。** 本手册所研究的 AI / Agent 系统由六个核心模块构成：MCP 工具描述完整性（M43）、仓库上下文注入（M46）、命令与凭据边界（M47）、RAG 文档投毒（M48）、RAG 权限继承（M49）和运行时沙箱审计链（M50）。每个模块既是攻击的潜在入口，也是防御的一个环节。

**单模块评估不够，需要跨模块视角。** 我们进行过单模块的深度评估（v2.0），发现了一些重要的行为模式——例如 M50 的运行时沙箱对上游攻击有显著的阻断效果，M48 的 safe_summary 机制能延缓文档投毒的攻击速度。但要理解攻击行为如何系统性地展开，必须在模块之间的连接上做文章。这就是 v3.0 跨模块攻击链研究的起点。

**理论手册的目标。** 本手册不是漏洞报告（不是），不是攻击指南（不是），不是生产安全评估（不是）。它的作用是让安全从业者和决策者能够：

1. 理解 AI / Agent 攻击行为的基本结构——从哪个模块进来、经过哪些模块、最终影响到哪里
2. 知道哪些防御点最有效——例如 M50 沙箱和 M47 凭据边界的实际阻断效果
3. 对"攻击压力如何在系统中传播"形成直觉——而不仅仅是看静态的漏洞列表
4. 在规划安全架构时，有一个理论框架参考——而不是靠猜测

### Source Phases

v0 PRD, v1.0 PRD, Phase 6–9 (基础评估框架), Phase 10–13 (评估方法论验证)

### Security Semantics

```yaml
chapter_1_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  chapter_type: "foundation_and_context"
```

### Candidate-Level Conclusion

AI / Agent 安全评估需要从单模块走向跨模块系统性分析。本手册提供了一套理论框架来组织这种分析，但框架本身处于 candidate 层级，未经生产环境验证。

### Human Review Note

本章是背景说明，不包含评估结果或风险判断。读者应理解本手册的 candidate-level 属性后方可继续阅读。

---

## 第 2 章：授权 AI 安全评估的边界

### Purpose

说明本手册所依据的评估方法是在什么边界条件下进行的——不连接真实系统、不执行真实攻击、不以发现漏洞为唯一目标。

### Key Ideas

**授权评估（Authorized Evaluation）。** 本项目中的所有评估均在明确授权范围内进行。评估目标不是真实的生产系统，而是模拟环境（sandbox）、本地靶场（test harness）和受控的框架执行。没有一次评估连接过真实 MCP Server、真实仓库、真实 RAG 系统或真实运行时环境。

**模拟信号（Simulated Signal）。** 评估产出的不是"漏洞"，而是"模拟信号"——在受控环境中观察到的行为模式。一个 simulated signal 表示"如果在真实系统中出现类似条件，可能产生类似行为"，但不等于"真实系统中存在这个漏洞"。

**Finding Candidate。** 经过人工初筛的 simulated signal 可以上升为 finding candidate。但 finding candidate 仍处于候选状态。本项目的所有输出都停留在 candidate 层级——包括本手册中的任何结论。

**Human Review Gate。** 所有评估结果必须经过人类安全专家审查。没有 automated pipeline 可以直接将 simulated signal 转换为 actionable finding。这是底线。

**不是传统渗透测试。** 本项目的方法论不同于传统的渗透测试或红队评估。我们不追求"攻破"某个系统，而是系统地理解攻击行为如何在不同模块之间传播和演化，以及现有防御机制在理论层面上能起到多大的阻断效果。

### Source Phases

Phase 6–9 (评估框架), Phase 10–13 (方法论), generic_agent_assessment_methodology.md, assessment_workflow_v1.md

### Security Semantics

```yaml
chapter_2_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  chapter_type: "methodology_boundary"
```

### Candidate-Level Conclusion

本手册的所有内容受限于授权评估的边界条件。没有结论经过真实系统验证。所有结论仅供 human review 参考，不构成安全审计发现。

### Human Review Note

读者应理解授权评估与真实渗透测试的区别。本手册中的攻击路径描述是 conceptual path，不代表在真实系统中可复现。

---

# 第二部分：单模块风险与能力边界

---

## 第 3 章：AI 供应链与工具描述风险

### Purpose

描述 MCP（Model Context Protocol）Tool Descriptor Integrity 模块（M43）的风险——当 AI 系统从不可信来源加载工具描述时，可能发生什么。

### Key Ideas

**MCP 工具描述就是攻击面。** MCP 工具描述是 AI 模型理解外部工具接口的方式。如果攻击者能够篡改工具描述（例如注册一个名称合法但行为恶意的工具），就可以在不直接控制模型的情况下影响模型的行为决策。

**供应链信任边界。** M43 的核心问题是供应链信任——AI 系统如何知道它加载的工具描述是可信的？如果工具市场、插件源或配置文件被污染，攻击者可以在工具描述层注入恶意元数据，诱导模型执行非预期的操作。

**在跨模块攻击链中的位置。** M43 是攻击链的入口层（供应链层）。在 Phase 79A 的 tabletop 推演中，攻击从 M43 开始，通过污染的工具描述诱导模型加载恶意上下文，进而影响后续的 M46（仓库上下文）和 M48（RAG 文档）处理。M43 本身防御手段有限（基本没有内置保护），在三次 tabletop 推演中都是最早降级的模块。

**已验证不适用于本模块。** M43 的防御主要依赖于外部供应链安全措施（工具市场审核、签名验证、策略配置），不在本手册所描述的 AI 系统内置防御范围内。注意：not_vulnerability_severity — 这描述的是一个理论上的攻击入口，不是评估出一个"高严重性漏洞"。

### Source Phases

Phase 14–16, v2.0 Phase 43–45, Phase 66A, 各 M43 评估报告

### Security Semantics

```yaml
chapter_3_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  module: "M43"
  module_role: "supply_chain_entry"
```

### Candidate-Level Conclusion

M43 是跨模块攻击链的典型入口，自身防御薄弱。在理论模型中，M43 的脆弱性因子最高（V_node=0.9），且在三次 tabletop 推演中均最早出现防御降级。但这不意味着每个使用 MCP 的系统都有这个漏洞——这是 candidate-level 的理论判断。

### Human Review Note

第 3–6 章描述的是六个模块各自的风险轮廓。每个模块的评估结果均来自受控环境的 simulated signal 和 tabletop observation。不得将单模块的描述理解为独立漏洞报告。

---

## 第 4 章：开发环境与 Coding Agent 风险

### Purpose

描述编程 Agent 在访问仓库上下文和执行命令时面临的两个核心风险——仓库上下文注入（M46）和命令/凭据边界突破（M47）。

### Key Ideas

**M46：仓库上下文注入。** Coding Agent 在分析代码仓库时，会读取仓库中的文件作为上下文。如果攻击者能够在仓库中植入包含恶意指令的文件（例如 README.md 中的隐藏指令、代码注释中的 prompt injection），Agent 可能将这些恶意内容解释为有效指令并执行。M46 的攻击不需要攻破任何认证机制，只需要向仓库中写入内容（在协作场景下这是常态）。

**M47：命令与凭据边界。** Coding Agent 能够执行 shell 命令和访问凭据（如 API key、SSH 密钥）。M47 的关键问题是：Agent 如何在"执行合法命令"和"防止命令被恶意操控"之间划清边界？在跨模块攻击链中，M47 是凭据保护的核心节点——它通过三条规则（命令边界、凭据边界、网络边界）来阻断攻击。

**M47 的衰减效果。** 在 Phase 80A 的 DEV-CRED 路径 tabletop 推演中，M47 的凭据边界衰减权重为 0.85（在 0–1 尺度上），是三个中链模块中衰减最强的一个（M47 3 条规则 > M49 2 条规则）。M47 成功将入口模块的传播压力降低，使得终端模块 M50 保持 pressured 状态而非 degraded。

**M46 vs M47 的对比。** M46 负责识别仓库上下文中的恶意指令，但它不是边界执行模块。M47 才是实际的执行边界。跨模块攻击链的关键路径之一就是"从 M46 的上下文污染过渡到 M47 的边界突破"——如果 M46 没有检测到仓库注入，它就会将恶意内容传递到 M47，由 M47 决定是否执行。

### Source Phases

v2.0 Phase 46–47, Phase 71A–72A, 各 M46/M47 评估报告, Phase 79A/80A tabletop 报告

### Security Semantics

```yaml
chapter_4_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  modules: ["M46", "M47"]
  module_roles: ["context_injection", "credential_boundary"]
```

### Candidate-Level Conclusion

M46 和 M47 构成了一条关键的风险链：仓库上下文注入 → 命令/凭据边界突破。M47 的凭据边界在三层防御规则支持下表现出较强的衰减效果（candidate 层级判断），但任何单一模块都不构成完整防御。纵深防御才是有效的策略。

### Human Review Note

M46 和 M47 的评估基于受控环境和 simulated signal。M47 的衰减因子（0.85）是 theory model 中的概念值，不是生产环境中的真实防御评分。

---

## 第 5 章：RAG 数据安全与权限继承风险

### Purpose

描述 RAG（Retrieval-Augmented Generation）系统中的数据安全和权限继承风险，覆盖文档投毒（M48）和权限继承漏洞（M49）。

### Key Ideas

**M48：RAG 文档投毒。** RAG 系统从外部知识库检索文档来增强模型回答。如果攻击者能够在知识库中植入包含恶意内容的文档（文档投毒），当模型检索到这些文档时，可能被诱导执行非预期的操作。M48 的独特之处在于它可以通过 safe_summary 机制延缓降级——在 Phase 79A 推演中，M48 的降级速度比 M46 慢，因为它除了 HRG（Human Review Gate）外还多了一层 safe_summary 保护。

**M49：RAG 权限继承。** 当 RAG 系统检索文档时，它可能会继承文档中的权限设置——如果一个低权限用户上传的文档被高权限的 Agent 检索并执行其中的指令，就发生了权限继承攻击。M49 的核心问题是"检索到的内容应该有多少执行权限"。在 Phase 79A 推演中，M48→M49 的 permission_dependency 边是传播概率最高的边（medium_to_high）。

**M48 与 M49 的权限链。** RAG 系统的核心风险链是：文档投毒（M48）→ 权限继承（M49）→ 工具调用（M50）。M48 负责让恶意内容进入检索结果，M49 负责让该内容获得足够的执行权限，M50 负责执行——如果任何一层防御生效，链条就断了。

**safe_summary 机制的效果。** 在 Phase 79A 推演中，M48 的 safe_summary 将 V_node（脆弱性因子）降低到 0.5（M46 为 0.7，M43 为 0.9），使 M48 成为入口模块中降解最慢的一个。Safe_summary 不是完整的解决方案——它只能延缓不能阻止——但它在纵深防御中是有价值的单层。

### Source Phases

v2.0 Phase 48–49, Phase 67A–68A, 各 M48/M49 评估报告, Phase 79A/80A tabletop 报告

### Security Semantics

```yaml
chapter_5_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  modules: ["M48", "M49"]
  module_roles: ["document_poisoning", "permission_inheritance"]
```

### Candidate-Level Conclusion

RAG 系统的权限链（M48 → M49）是跨模块攻击传播的关键通道。permission_dependency 边在所有观察到的攻击路径中都具有最高的传播概率（candidate 层级）。Safe_summary 机制延缓了 M48 的降解，但无法独立阻止权限继承攻击。

### Human Review Note

M48→M49 的传播概率（medium_to_high）来自 tabletop 推演中的定性观察，不是真实系统中的测量值。RAG 系统的实际安全表现取决于具体实现，不能直接从本手册的 candidate 级结论推断。

---

## 第 6 章：运行时沙箱与审计链路

### Purpose

描述 Agent 运行时沙箱（M50）作为终端防御层的双重角色——既是审计确认节点，也是执行阻断节点。

### Key Ideas

**M50 的双重角色。** M50（Agent Runtime Sandbox）是跨模块攻击链的终端模块，位于运行时层。它承担两个角色：

1. **审计确认（Audit Confirmation）**——接收上游模块的审计信息，检查是否满足审计依赖、权限验证、凭据压力和运行时资源约束
2. **沙箱执行边界（Sandbox Execution Boundary）**——阻断非授权的工具调用和命令执行

**四层防御规则。** M50 有四条防御规则：审计依赖压力检查、权限验证器泄漏检测、凭据压力检查和运行时资源压力检查。这使得 M50 是所有模块中规则最多的（M47 有 3 条，M49 有 2 条），对应最高的衰减效果。

**Tabletop 推演中的 M50。** 在全部三次 tabletop 推演中（Phase 79A 全生命周期路径、Phase 80A DEV-CRED 路径、Phase 80A RAG 路径），M50 均保持 pressured 状态（D_node ≥ 0.7），从未 degraded。这是所有模块中唯一的——所有其他模块都在某些推演中达到了 degraded 或 blocked 状态。这使 M50 被视为纵深防御中最可靠的单层（但仍然是 candidate 层级判断，不是生产保证）。

**M50 的两种权重。** 在统一理论模型中，M50 有两个独立权重：
- 审计衰减权重（W-M50-AUDIT-DAMP-001）：0.5–1.0，默认 0.8
- 沙箱阻断权重（W-M50-SB-BLOCK-001）：0.0–1.0，默认 0.9

高默认值反映了 M50 在所有观察到的攻击场景中均未失效。

**M50 不是银弹。** 尽管在推演中表现最强，M50 仍然是有限度的。理论模型假设沙箱逃逸是可能的（因此阻断权重不是 1.0）。在真实系统中，M50 依赖于正确的配置、及时的安全更新和完善的审计覆盖。这些超出了本手册的讨论范围。

### Source Phases

v2.0 Phase 50, Phase 69A, M50 评估与 retest 报告, Phase 79A/80A tabletop 报告, Phase 81A pattern library (M50 相关模式)

### Security Semantics

```yaml
chapter_6_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  module: "M50"
  module_role: "runtime_sandbox_terminal"
```

### Candidate-Level Conclusion

M50 在理论层面表现出最强的防御韧性——在所有 tabletop 推演中维持 pressured 状态。但这是 candidate-level 观察，不代表 M50 在任何真实实现中都能达到同等效果。M50 的有效性取决于具体实现和配置。

### Human Review Note

M50 的 tabletop 观察结果（未 degraded）不应被误解为"M50 总是安全的"。沙箱逃逸在理论上是可能的，且未被纳入推演范围。人力资源安全的最终评估需要结合具体实现信息。

---

# 第三部分：跨模块攻击链与系统风险动力学

---

## 第 7 章：从单点模块到跨模块攻击图

### Purpose

描述如何将六个独立模块组织为一个跨模块攻击图（Attack Graph），并定义节点、边、路径、层四种结构元素。

### Key Ideas

**攻击图结构。** 跨模块攻击图由以下元素构成：

- **节点（Node）**——七个节点类型：supply_chain_node（M43）、context_injection_node（M46）、credential_boundary_node（M47）、document_poisoning_node（M48）、permission_inheritance_node（M49）、runtime_sandbox_node（M50）、audit_log_node（审计日志，跨模块）
- **边（Edge）**——九种边类型：permission_dependency、context_influence、runtime_dependency、audit_dependency、supply_chain、api_injection、credential_access、repo_impact、tool_call_chain
- **路径（Path）**——跨模块攻击链路径：从入口模块出发，经过若干中间模块，到达终端模块
- **层（Layer）**——四层结构：供应链层（M43）→ 开发环境层（M46/M47）→ 知识库层（M48/M49）→ 运行时层（M50）

**三条观察到的攻击路径。** 通过 Phase 79A 和 Phase 80A 的 tabletop 推演，我们观察并记录了三组具体的攻击路径：

1. **PATH-SUPPLY-DEV-RAG-RUNTIME-001**（全生命周期路径）：M43 → M46 → M48 → M49 → M50（5 模块，4 层）
2. **PATH-DEV-CRED-RUNTIME-001**（开发凭据路径）：M46 → M47 → M50（3 模块，2 层）
3. **PATH-RAG-RUNTIME-001**（RAG 运行时路径）：M48 → M49 → M50（3 模块，2 层）

**攻击路径目录。** 除了观察到的三条路径，Phase 75A 还定义了一个更大的跨模块攻击路径目录，包含更多理论上的路径变体。目录中的路径按入口模块分类，并基于攻击图拓扑的可能组合。目录条目处于 conceptual 层级——它们描述了攻击在理论上可以如何展开，但尚未经过 tabletop 推演验证。

**层间传播规则。** 攻击如何在层之间传播由七类传播规则定义。这些规则考虑了：同一层内的模块间传播、向上游传播、向下游传播、跨层传播等场景。规则是 conceptual 层级，不模拟真实网络传播。

### Source Phases

Phase 74A (cross_module_attack_graph_schema.md), Phase 75A (cross_module_attack_path_catalog.md), Phase 76A (explorer design gate), risk_propagation_model.md

### Security Semantics

```yaml
chapter_7_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  chapter_type: "cross_module_structural"
```

### Candidate-Level Conclusion

跨模块攻击图提供了组织 AI / Agent 攻击行为分析的结构框架。三条观察到的攻击路径展示了攻击如何从供应链层逐步推进到运行时层。攻击路径目录中的其他路径为 conceptual 层级，未经推演验证。

### Human Review Note

攻击图中的节点和边是 conceptual 模型，不代表真实网络拓扑或系统架构。观察到的攻击路径在受控的 tabletop 环境中推演，不代表在真实系统中可复现。

---

## 第 8 章：攻击传播动力学与桌面推演

### Purpose

描述攻击压力如何在攻击图中传播、衰减、放大和形成反馈循环（Phase 77A 动力学模型），以及如何通过桌面推演（Phase 79A/80A）验证理论模型与观察的一致性。

### Key Ideas

**八种防御状态。** 每个模块的防御状态可以处于以下八种状态之一：stable → pressured → degraded → blocked → recovering → isolated → compromised → bypassed。攻击传播动力学描述的是这些状态之间的转变过程。

**五种衰减规则。** 攻击压力在通过某些模块时会衰减。衰减的来源包括：命令边界阻断、凭据边界阻断、网络边界阻断、审计确认检查和运行时沙箱阻断。M50（4 条衰减规则）> M47（3 条）> M49（2 条）> 其他模块。

**三种放大规则。** 攻击压力在某些条件下会放大：权限泄漏放大、凭据压力放大和上下文污染放大。放大规则与特定模块和边类型关联，例如 M48→M49 的 permission_dependency 边在双边界失效时产生最大放大效果。

**四种反馈循环。** 攻击传播过程中存在反馈机制：运行时控制反馈（负反馈，降低传播压力）、权限泄漏反馈（正反馈，增加传播压力）、凭据压力反馈（正反馈，潜在）、审计确认反馈（负反馈，降低传播压力）。在三次 tabletop 推演中，运行时控制负反馈始终活跃，而正反馈循环未被触发。

**第一次桌面推演（Phase 79A）。** 针对全生命周期路径 PATH-SUPPLY-DEV-RAG-RUNTIME-001 的五步推演，覆盖 5 个模块、4 层、5 个时间步。关键观察：
- M43 在第 2 步降级（无 HRG，最快）
- M46 在第 3 步降级（有 HRG，中等速度）
- M48 在第 4 步降级（有 HRG + safe_summary，最慢）
- M50 在所有步骤中维持 pressured（从未 degraded）
- 整体轨迹等级：partial_degradation

**第二次桌面推演批次（Phase 80A）。** 针对两条短路径的并行推演：
- DEV-CRED 路径（M46→M47→M50）：M47 的 3 条衰减规则有效控制传播；G_path = -3.68（理论计算值）
- RAG 路径（M48→M49→M50）：M48 的 safe_summary 延缓入口降级，但权限链传播压力较高；G_path = -3.136（理论计算值）
- 交叉对比显示两条路径表现出不同的衰减模式（M47 强衰减 vs M49 中等衰减），但最终都归为 partial_degradation

### Source Phases

Phase 77A (dynamics model, node defense state evolution, feedback loop), Phase 78A (discovery framework), Phase 79A (first tabletop), Phase 80A (multi-path batch)

### Security Semantics

```yaml
chapter_8_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  chapter_type: "dynamics_and_tabletop"
```

### Candidate-Level Conclusion

攻击传播动力学是理解跨模块攻击行为的关键理论工具。衰减规则、放大规则和反馈循环共同构成了攻击压力在系统中如何演化的定性模型。三次桌面推演的结果与理论模型定性一致（所有路径归为 partial_degradation），但这是 tabletop observation 级别的结论，不是定量验证。

### Human Review Note

本章中的传播概率（medium_to_high、medium、low_to_medium）是定性标签，不是统计学概率。G_path 值（-3.68、-3.136）是 conceptual 计算示例，不是真实的防御评分或风险分数。

---

## 第 9 章：攻击模式库与统一理论模型

### Purpose

描述如何从多次桌面推演中沉淀出可复用的攻击模式（Phase 81A），并将所有观察整合为一个统一的理论模型（Phase 82A），以及如何对该模型进行结构化复核（Phase 83A）。

### Key Ideas

**八个攻击模式。** 从三次 tabletop 推演中，我们提取了八个跨模块攻击模式。每个模式是一种可复用的攻击行为描述，包括触发条件、行为表现、衰减节点、放大因子等结构化字段。模式按生命周期状态分类：

- **confirmed_across_3_paths（4 个模式）**：在全部三次推演中均被观察到
  - upstream_entry_degradation：入口模块降级模式
  - m50_audit_confirmation：M50 审计确认模式
  - m50_sandbox_execution_boundary：M50 沙箱边界模式
  - human_review_breakpoint：人工审查断点模式

- **observed_in_2_paths（2 个模式）**：在两次推演中被观察到
  - credential_boundary_attenuation：凭据边界衰减模式
  - permission_leakage_amplification：权限泄漏放大模式

- **observed_in_1_path（2 个模式）**：在一次推演中被观察到
  - repo_context_to_runtime_pressure：仓库上下文到运行时压力模式
  - rag_to_audit_chain_dependency：RAG 到审计链依赖模式

**统一理论模型。** Phase 82A 将攻击图结构、传播动力学规则、tabletop 观察数据和模式库整合为一个统一的理论框架，产出三个核心概念方程和六个权重因子：

- **边传播压力方程（P_edge）**：`P_edge(t) = S_source(t) × W_edge × A_pattern × F_feedback × (1 - D_target)`
  - 描述攻击压力在一条边上的传播强度
- **节点防御状态演化方程（D_node）**：`D_node(t+1) = clamp(D_node(t) + R_control - P_in(t) × V_node + H_review)`
  - 描述一个模块的防御状态随时间的演变
- **路径级防御降级模型（G_path）**：`G_path = Σ P_edge(t) × (1 + A_seq) - Σ A_attenuation + Σ A_amplification - Σ B_blocking`
  - 描述整条攻击路径的总体防御降级情况

**六个权重因子。** 权重因子从模式库中推导，每个权重有一个概念值范围：
| 权重 | 方向 | 范围 | 覆盖模块 |
|------|------|------|---------|
| upstream_entry_vulnerability | 放大 | 0.0–1.0 | M43, M46, M48 |
| m50_audit_damping | 衰减 | 0.5–1.0 | M50 |
| m50_sandbox_boundary | 阻断 | 0.0–1.0 | M50 |
| credential_boundary_attenuation | 衰减 | 0.0–1.0 | M46, M47, M50 |
| permission_leakage_amplification | 放大 | 0.0–2.0 | M48, M49, M50 |
| human_review_breakpoint | 审查门 | 0.0–0.5 | 全部模块 |

**模型校准。** 六个校准目标用于验证理论模型与 tabletop 观察的一致性，包括传播压力一致性、衰减节点一致性、M50 阻尼一致性、入口降级一致性、反馈循环一致性和跨路径区分能力。校准方法是定性比较，不是统计拟合。

**结构化复核。** Phase 83A 创建了覆盖四个维度（方程一致性、权重因子语义、校准方法、安全语义）的复核检查清单，全部为 human review 性质。

### Source Phases

Phase 81A (pattern library, pattern index, matrices), Phase 82A (unified theory model, weight factors, calibration method), Phase 83A (review checklists)

### Security Semantics

```yaml
chapter_9_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  chapter_type: "pattern_and_theory"
```

### Candidate-Level Conclusion

模式库和统一理论模型是项目 v3.0 的核心理论成果。八个模式描述了可复用的攻击行为结构，三个概念方程将传播动力学形式化，六个权重因子将模式库与理论模型连接。但所有这些仍然是 theory model candidate 层级——概念方程不可执行，权重因子是 illustrative 值，模式是 tabletop pattern。

### Human Review Note

概念方程是定性分析工具，不是可执行模型。权重因子是 tabletop 观察推导的概念值，不是生产配置参数。模式库不是检测规则库。所有内容仅供 human review 参考。

---

# 第四部分：形式化系统与实践使用

---

## 第 10 章：形式化表达、使用边界与后续路线

### Purpose

描述统一理论模型向形式化系统（集合、关系、公理、定理候选）扩展的概念框架，以及本手册在 human review、方案沟通和研究规划中的使用方法和边界。

### Key Ideas

**形式化系统的概念。** 形式化系统（Formal System）是统一理论模型向数学表达方向的概念扩展。它将攻击图元素映射为集合，传播关系映射为关系，动力学规则映射为公理，模型预测映射为定理候选。形式化系统不是形式化验证——它不证明任何系统是安全的，而是为攻击行为分析提供一种严谨的推理结构。

**形式化系统的构成要素（概念规划）：**
- **集合**：节点集合（N）、边集合（E）、路径集合（P）、状态集合（S）
- **关系**：传播关系（R_prop）、衰减关系（R_atten）、放大关系（R_ampl）
- **公理**：传播方向公理、衰减/放大公理、阻断公理、反馈公理、入口脆弱性公理
- **定理候选**：路径分类定理、衰减排序定理、M50 稳定性定理

**注意：Phase 84A（形式化系统）尚未完成。** 本章引用的形式化系统概念来自统一理论模型的规划扩展。目前只有概念框架，没有完整的集合定义、公理体系和定理推导。在 Phase 84A 完成后，本章内容需要更新。

**手册使用指南。** 本手册可以在以下场景中使用：

1. **Human Review 参考**——作为安全评估人员理解 AI / Agent 攻击行为结构的参考资料。手册中的理论和模式可以帮助评估人员更快地识别潜在的攻击模式，但所有判断仍需人工审查。
2. **方案沟通**——作为安全团队与产品团队、架构师和决策者沟通风险轮廓的框架性文档。手册的四部分十章结构提供了从基础概念到高级理论的递进式叙述。
3. **研究规划**——作为后续安全研究的理论基线。手册中标记为 candidate 的结论可以指导后续研究的优先级，pending 的领域（如 Phase 84A 形式化系统）标识了待推进的方向。

**禁止用途。** 本手册不得用于以下场景：
- 作为已确认漏洞的证据
- 作为正式安全审计发现的依据
- 作为生产环境风险评分的输入
- 作为构建真实攻击的参考
- 作为自动化安全决策系统的输入

**后续路线（建议）。** Phase 85A 完成后，建议的后续方向包括：
- **Phase 85B**：手册结构与语言精修（如果四部分十章结构需要调整，或技术表达过重）
- **Phase 86A**：Executive Summary MVP（面向高层决策者的精简摘要）
- **Phase 84A 补充**：完成形式化系统的集合定义、公理体系和定理推导（取决于项目优先级）

**不建议下一步直接做的事：**
- 自动化手册生成器（当前是文档整理阶段，不是能力实现）
- 攻击模拟器实现（理论模型仍处于 candidate 层级）
- 形式化验证实现（需要在 Phase 84A 完成后才有基础）
- Pattern detector 实现（模式不是检测规则）
- Controlled replay 执行（受控回放仍不得进入执行）
- 生产安全验证（理论模型不适合用于生产安全判定）

### Source Phases

Phase 82A (unified theory model), Phase 83A (review checklists), Phase 84A (concept — pending)

### Security Semantics

```yaml
chapter_10_safety:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  chapter_type: "formal_system_and_usage"
  phase_84A_status: "pending"
```

### Candidate-Level Conclusion

形式化系统是统一理论模型的数学扩展概念，目前处于规划阶段（Phase 84A pending）。本手册作为 human review 参考、方案沟通工具和研究基线，具有理论和结构价值，但不适用于生产安全评估、形式化验证或漏洞确认。

### Human Review Note

第 10 章引用了尚未完成的 Phase 84A 形式化系统概念。该概念在 Phase 84A 完成之前不应被视为有效理论框架。手册的使用边界和禁止用途必须被所有读者理解和遵守。

---

# 附录

## A. 结论层级汇总

| 层级 | 含义 | 在手册中的应用 |
|------|------|---------------|
| candidate-level | 初步判断，待 human review 确认或修正 | 所有章节的结论 |
| conceptual | 理论概念，不代表真实系统行为 | 攻击图节点、边、传播规则 |
| simulated | 在受控环境中观察到的模拟信号 | 模块评估行为描述 |
| tabletop observation | 在桌面推演中观察到的行为模式 | 传播概率、衰减效果、轨迹 |
| theory model | 理论模型输出，不可执行 | P_edge/D_node/G_path 方程 |
| pattern candidate | 跨推演观察的可复用模式 | 八个攻击模式 |

## B. 来源 Phase 索引

| Phase | 内容 | 在手册中的章节 |
|-------|------|---------------|
| v1.0 (Phase 6–16) | 评估框架和方法论 | 第 1–2 章 |
| v2.0 Phase 43–45 | M43 MCP 工具描述 | 第 3 章 |
| v2.0 Phase 46–47 | M46/M47 仓库上下文、命令边界 | 第 4 章 |
| v2.0 Phase 48–49 | M48/M49 RAG 文档投毒、权限继承 | 第 5 章 |
| v2.0 Phase 50 | M50 运行时沙箱 | 第 6 章 |
| Phase 74A | 跨模块攻击图 | 第 7 章 |
| Phase 75A | 攻击路径目录 | 第 7 章 |
| Phase 76A | 自动化探索器设计 | 第 7 章 |
| Phase 77A | 攻击图动力学 | 第 8 章 |
| Phase 78A | 攻击链发现框架 | 第 8 章 |
| Phase 79A | 第一次 tabletop 推演 | 第 8 章 |
| Phase 80A | 多路径 tabletop 批次 | 第 8 章 |
| Phase 81A | 攻击模式库 | 第 9 章 |
| Phase 82A | 统一理论模型 | 第 9 章 |
| Phase 83A | 理论模型复核清单 | 第 9 章 |
| Phase 84A (pending) | 形式化系统 | 第 10 章 |

## C. 安全语义声明全文

参见独立文档 `docs/ai_attack_behavior_theory_handbook_safety_semantics.md`。

核心声明摘要：
- 本手册所有结论为 candidate-level
- 不声称 confirmed vulnerability
- 不生成 formal finding
- 不声明 production safety
- 不提供攻击执行指南
- 不替代人工复核

## D. 手册元数据

```yaml
metadata:
  handbook_name: "AI 攻击行为理论手册"
  version: "85A"
  handbook_compilation_only: true
  documentation_only: true
  candidate_level_only: true
  structure: "four_parts_ten_chapters"
  total_chapters: 10
  total_appendices: 4
  source_phases:
    - "v1.0 (Phase 6–16)"
    - "v2.0 (Phase 43–50, Phase 66A–73A)"
    - "v3.0 (Phase 74A–83A)"
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  handbook_is_not_attack_guide: true
  handbook_is_not_formal_finding_report: true
  handbook_is_human_review_reference_only: true
```
