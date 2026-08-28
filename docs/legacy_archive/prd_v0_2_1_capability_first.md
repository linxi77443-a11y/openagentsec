# 企业内部授权 AI 安全评估系统 PRD v0.2.1：能力验证与业务价值优先版

## 文档信息

| 字段 | 值 |
|---|---|
| 版本 | v0.2.1 |
| 状态 | Draft |
| 阶段 | Phase 35C |
| 优先级修订日期 | 2026-06-21 |
| 前序版本 | v0.2（Phase 34 系列） |

## 修订说明

v0.2.1 是一次**方向性调整**。v0.2 以合规流程、审批包、dashboard、静态规划为优先方向，经过 Phase 32C（授权 API 回归执行）、Phase 34C（DeepSeek Judge 执行）、Phase 35–35C.0（Promptfoo 集成框架与 Go/No-Go）等阶段的实践，项目已积累了可用的基础能力。但"合规优先"导致了大量重型文档投入，而核心问题尚未回答：

> **promptfoo 是否能跑通？输出是否可读？是否能辅助人工复核？是否相比现有工具有增量价值？**

v0.2.1 将优先级从"合规流程优先"调整为**"能力验证 + 业务价值优先"**。

## 核心理念

### 能力验证优先

- 每个模块必须先证明"能跑通、能出结果、结果可读"，才能进入合规化阶段。
- 先跑通，再优化；先有输出，再完善文档。
- 能力验证通过的标准：工具链运行成功、输出结构化可读、结果可映射到已有 finding candidates。

### 业务价值优先

- 每个模块必须回答：**对安全评估的实际价值是什么？**
- 优先投入高业务价值的模块：数据泄露发现、权限绕过验证、业务影响证据报告等。
- 低价值或不确定价值的模块后置：dashboard 美化、release notes 完善、roadmap 长文档更新等。

### 合规流程后置

- 合规流程（Go/No-Go、Readiness Gate、审批包）保留已构建的框架，但不再优先扩展。
- 新的评估模块先以最小配置跑通，再补充合规文档。
- 合规流程只对生产环境执行和 formal finding 输出是必须的；对本地 sandbox 测试和 assistant_review 输出可以简化。

### Dashboard / Release / Roadmap 暂不优先

- dashboard、release notes、roadmap、learning summary 等非必要文档暂停扩展。
- 这些文档在能力验证跑通后、系统进入稳定期后，按需补充。

### 多智能体后置

- 多 Agent（Multi-Agent）模拟、协调安全、跨 Agent 会话泄漏等场景归为 P2，当前不投入。
- 先聚焦单 Agent 和单 Chatbot 场景的能力验证。

### Agent 安全补强模块纳入

- 本版本将 Agent 安全（M38–M42）纳入 P0 和 P1 优先级。
- 包括：Agent 多源输入注入（M38）、Agent 行为审计与归因（M40）、Agent 服务账号权限边界（M41）、Agent 运行时状态污染（M39）、代码执行沙箱验证（M42）。

## 优先级定义

### P0：核心能力，必须优先验证

- 已有 finding candidates 支撑，且有对应工具链可执行。
- 未跑通则系统无法回答核心安全问题。
- 覆盖 Prompt Injection、System Prompt Leakage、RAG Boundary、Sensitive Data Leakage、Agent 安全等关键风险面。

### P1：重要能力，应在 P0 验证后按序投入

- 有明确业务价值，但依赖 P0 模块的基础能力。
- 覆盖权限边界验证、工具调用安全、修复效果对比、误报校准等。

### P2：增强能力，暂不投入

- 价值待验证，或依赖外部条件（如多 Agent 环境、生产流量）。
- 覆盖模型漂移监控、Shadow AI 发现、多模态安全等。

## 工具-模块适配原则

- 每个模块使用最合适的工具链，而不是所有工具跑所有模块。
- promptfoo 用于自动化断言和回归验证。
- garak 用于对抗性测试补充。
- DeepSeek judge 用于 AI-assisted 结果评审。
- 其他工具（PII detector、retrieval trace、code sandbox inspector 等）在各自领域做专项验证。
- 矩阵详见 `docs/tool_module_fit_matrix.md`。

## 当前代码处理原则

详见 `docs/phase35c_code_handling_note.md`。摘要：

- 保留 Phase 35C.0 及之前成果。
- 回滚旧 35C 未提交变更。
- 当前阶段只修 PRD 和 registry，不实现功能。
- 后续每个模块开发前必须先输出实现规格单。

## 模块一览

| 优先级 | 数量 | 模块 ID |
|---|---|---|
| P0 | 18 | M01, M02, M03, M04, M06, M07, M08, M09, M14, M15, M17, M18, M19, M21, M22, M38, M40, M41 |
| P1 | 15 | M05, M10, M11, M12, M13, M16, M20, M23, M24, M25, M27, M28, M29, M39, M42 |
| P2 | 9 | M26, M30, M31, M32, M33, M34, M35, M36, M37 |

完整定义见 `capability_modules/module_registry.yaml`。

## 后续路线图（精简版）

1. **Phase 35D+（短期）**：按 P0 优先级，每个模块输出实现规格单，选择工具链，在本地 sandbox 跑通最小验证。
2. **Phase 36+（中期）**：P1 模块验证 + 部分 P0 模块的正式化（formal finding allowed 评估）。
3. **Phase 37+（远期）**：P2 模块探索 + 系统化 dashboard / release 补充。

## 限制说明

- v0.2.1 是方向性 PRD，不是实现计划。具体实现规格在模块开发前独立输出。
- 工具链（promptfoo / garak 等）的安装和配置不在此 PRD 范围内，由各阶段自行处理。
- DeepSeek judge 保持当前状态，仅用于结果评审，不用于测试生成。
- 本版本不涉及生产环境部署、客户交付、formal finding 生成。
