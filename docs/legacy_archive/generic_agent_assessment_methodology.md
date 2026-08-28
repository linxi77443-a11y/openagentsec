# 通用 Agent 评估方法论

## 评估目标

系统性评估 Agentic AI 系统的安全控制能力，覆盖从用户输入到工具执行到结果返回的全链路风险，输出可行动的修复建议和复测路径。

## 适用对象

### 可评估的 Agent 类型

- **Hermes / OpenClaw 类 Agent**：多步推理 + 工具调用型 Agent
- **Claude Code 类 Agent**：CLI / code interpreter 型 Agent
- **LangGraph Agent**：基于 LangGraph 的图结构 Agent
- **AutoGen / CrewAI 类 Agent**：多 Agent 协作系统
- **MCP Agent**：基于 Model Context Protocol 的 Agent
- **企业流程 Agent**：集成企业内部系统的流程自动化 Agent
- **自定义 Agent**：自研或二次开发的 Agent 系统

### 不适用对象

- 纯对话 Chatbot（无工具调用能力）→ 适用 Chatbot profile
- 纯 RAG 系统（无工具调用能力）→ 适用 RAG profile
- 纯 LLM API（无 Agent 编排层）→ 适用 LLM API profile

## Risk Classification

测试结果同时映射到：

- **MITRE ATLAS technique** — 威胁建模和测试用例基座
- **OWASP Agentic Top 10** — 风险分类和报告语言

详见 `owasp/agentic_to_atlas_crosswalk.yaml` 和 `owasp/agentic_report_language.md`。

## 评估前信息收集清单

评估前必须收集并确认以下信息：

1. **系统架构信息**
   - Agent 组件架构图
   - Planner / Memory / Tool Registry / Execution Layer 边界
   - 系统指令层级与优先级定义
   - 工具调用鉴权与授权流程

2. **工具清单**
   - 全部可用工具列表
   - 每个工具的功能描述
   - 每个工具的参数 schema
   - 每个工具的权限等级
   - 每个工具的副作用分类（读/写/外传/管理）

3. **权限边界**
   - 工具白名单定义
   - 用户权限等级划分
   - 跨用户/跨会话隔离机制
   - Secret / 凭证访问控制

4. **日志与审计**
   - 工具调用审计日志位置
   - 决策过程日志位置
   - 日志脱敏规则
   - 日志保留策略

5. **安全控制基线**
   - 已实现的安全控制列表
   - 控制项 owner 与联系方式
   - 已知安全限制与排除项
   - 人工确认流程定义

6. **测试环境授权**
   - 测试环境 API endpoint
   - 测试账号
   - 测试数据范围
   - 速率限制
   - 回滚流程

## Agent 架构画像

评估前必须完成 Agent 架构画像：

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
├─────────────────────────────────────────────────────────────┤
│             System Instruction / Policy Layer                │
├─────────────────────────────────────────────────────────────┤
│                   Planner / Task Decomposition               │
├─────────────────────────────────────────────────────────────┤
│              Memory / Context Store                          │
├─────────────────────────────────────────────────────────────┤
│              Tool Registry / Schema                          │
├─────────────────────────────────────────────────────────────┤
│              Tool Execution Layer                            │
├─────────────────────────────────────────────────────────────┤
│              Tool Result Handler                             │
├─────────────────────────────────────────────────────────────┤
│       Skill / Plugin / MCP Layer                             │
├─────────────────────────────────────────────────────────────┤
│       External Channel Connectors                            │
├─────────────────────────────────────────────────────────────┤
│       Audit / Logging / Evidence Layer                       │
└─────────────────────────────────────────────────────────────┘
```

对每个组件回答：
- 组件是否存在？
- 组件的输入输出边界？
- 组件的安全控制？
- 组件的攻击面？
- 组件是否可测试？

## ATLAS technique 映射流程

1. 从 `atlas/atlas_techniques.yaml` 中提取 Agent 相关 technique
2. 对照 Agent 架构画像，确认每个 technique 的适用场景
3. 对照 `generic_agent_test_catalog.yaml`，匹配测试能力
4. 对照 `generic_agent_control_checklist.md`，匹配控制项
5. 生成 coverage 矩阵与 gap 分析

## 测试模式选择

### 1. Local Sandbox

**适用场景**：基础 prompt injection、系统指令泄露、简单工具调用验证。

**特点**：
- 完全本地，无外部依赖
- 执行速度快
- 风险最低
- 覆盖范围有限

**测试能力**：
- direct prompt injection
- system prompt exposure
- simple tool schema validation
- basic tool allowlist check
- fake secret access control
- fake write action dry-run

### 2. Manual UI Replay

**适用场景**：已通过 UI 捕获真实交互，需要在本地分析和复测。

**特点**：
- 基于真实 UI 交互快照
- 不需要直接访问测试环境
- 可离线分析
- 可追溯原始操作

**测试能力**：
- 已发生的工具调用分析
- 已发生的 prompt injection 分析
- 已发生的 secret 泄露分析
- 控制项有效性验证
- 复测验证

### 3. Mock Tool Harness

**适用场景**：需要验证多步工具调用链、复杂工具返回注入、Planner 行为。

**特点**：
- 可控制工具返回内容
- 可模拟复杂工具交互
- 可注入恶意工具返回
- 可验证 Planner 决策逻辑
- 无真实副作用

**测试能力**：
- multi-step goal hijacking
- tool return data poisoning
- indirect injection chain reaction
- planner decision deviation
- memory poisoning
- loop / resource consumption
- human confirmation bypass

### 4. Test Instance API

**适用场景**：已有受控测试环境，可通过 API 调用真实 Agent（非生产）。

**特点**：
- 最接近真实环境
- 可验证真实控制项有效性
- 可发现集成层面风险
- 需要严格授权与隔离

**测试能力**：
- 全部 local sandbox 能力
- 全部 mock harness 能力
- 真实权限边界验证
- 真实 secret 访问控制验证
- 真实写操作 dry-run 验证
- 真实日志脱敏验证

### 5. Browser Automation in Test Env

**适用场景**：Agent 通过 Web UI 操作，需要浏览器自动化测试。

**特点**：
- 真实 UI 交互
- 需要浏览器隔离环境
- 需要测试账号隔离
- 需要明确的页面白名单

**测试能力**：
- UI 级 prompt injection
- UI 级工具调用验证
- UI 级人工确认机制验证
- UI 级 exfiltration 验证

## 测试优先级

**P0（必须）**：
- prompt injection
- system prompt exposure
- unauthorized tool invocation
- secret / credential access control
- write action dry-run enforcement
- basic exfiltration blocking

**P1（重要）**：
- indirect prompt injection
- tool schema validation
- tool result sanitization
- goal hijacking
- context poisoning
- human confirmation bypass

**P2（推荐）**：
- memory poisoning
- tool metadata poisoning
- skill / plugin / MCP poisoning
- resource consumption / loop abuse
- cross-session isolation
- audit log integrity

**P3（可选）**：
- cross-agent delegation
- multi-agent collusion
- advanced persistence
- supply chain attack

## Evidence 要求

所有测试必须生成可复核的 evidence：

1. **输入输出完整记录**：完整 prompt + 完整 response
2. **结构化 JSON 格式**：便于后续 dashboard 展示与报告生成
3. **风险信号标记**：检测到的风险必须明确标记
4. **决策过程记录**：Planner 决策过程必须记录
5. **工具调用记录**：实际调用的工具、参数、返回必须完整记录
6. **时间戳**：每个操作必须有精确时间戳
7. **来源标识**：测试来源（local sandbox / mock harness / test instance）必须明确

## 脱敏要求

所有 evidence、日志、报告必须脱敏：

1. **Secret / Token / API Key**：必须完全脱敏
2. **Honeytoken**：必须脱敏
3. **PII**：个人可识别信息必须脱敏
4. **企业内部信息**：非测试用内部信息必须脱敏
5. **真实 URL / Endpoint**：必须脱敏或替换为占位符
6. **真实账号**：必须脱敏

## 报告结构

评估报告必须包含：

1. **评估背景**：时间、范围、对象、授权方
2. **目标 Agent 架构画像**：组件图、边界说明
3. **评估范围**：已测/未测、测试模式、限制说明
4. **ATLAS 映射**：technique 覆盖矩阵
5. **测试用例**：全部测试用例列表与结果
6. **结果摘要**：P0/P1/P2/P3 风险分级
7. **风险信号**：检测到的风险信号详情
8. **控制项检查**：80 项控制项检查结果
9. **Evidence 索引**：全部 evidence 文件索引
10. **覆盖缺口**：未覆盖的技术与场景
11. **限制说明**：本次评估的已知限制
12. **修复建议**：按风险等级排序的修复建议
13. **复测建议**：复测范围、方法、通过标准

## 复测流程

修复后复测流程：

1. 确认修复已部署到测试环境
2. 重新运行原始测试用例
3. 新增针对修复机制的绕过测试用例
4. 生成复测报告
5. 对比原始报告与复测报告
6. 确认风险已缓解或降低到可接受水平
7. 若风险仍存在，返回修复流程
