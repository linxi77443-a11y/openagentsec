# 通用 Agent 攻击面文档

## 概述

本文档按 Agent 系统架构模块整理攻击面、典型风险、ATLAS technique 映射、OWASP Agentic Top 10 映射、可测试方式、当前覆盖状态和后续增强方向，服务于防御、治理和修复决策。

风险分类同时对齐 MITRE ATLAS（威胁建模）和 OWASP Agentic Top 10（报告语言）。详见 `owasp/agentic_to_atlas_crosswalk.yaml`。

## 1. User Intent / Identity

### 攻击面

- 用户输入的 prompt injection
- 用户身份标识欺骗
- 多用户会话隔离失效
- 用户操作冒充

### 典型风险

攻击者通过用户输入直接注入恶意指令，或冒充授权用户触发敏感工具调用。

### 对应 ATLAS technique

- LLM Prompt Injection
- AI Agent Context Poisoning

### 可测试方式

- local sandbox
- manual UI replay
- test instance API

### 当前系统覆盖

部分覆盖。已有本地 sandbox direct prompt injection 测试。

### 后续增强方向

增加身份标记传递测试、会话隔离测试、跨用户上下文泄露测试。

### 推荐控制项

- 用户身份验证与会话隔离
- 用户输入 sanitization
- 不可信输入标记

## 2. System Instruction / Policy Layer

### 攻击面

- 系统指令泄露
- 系统指令层级覆盖
- 安全策略绕过
- 工具调用策略篡改

### 典型风险

攻击者通过 paraphrase、角色扮演、编码等方式绕过或提取系统指令，使 Agent 违反安全策略执行工具调用。

### 对应 ATLAS technique

- LLM Prompt Injection
- Extract LLM System Prompt

### 可测试方式

- local sandbox
- manual UI replay

### 当前系统覆盖

已覆盖。Chatbot 和 Agent sandbox 均有系统 prompt 泄露测试。

### 后续增强方向

增加多轮指令覆盖、角色深度嵌套测试、间接指令注入测试。

### 推荐控制项

- 系统指令层级与优先级
- 不可覆盖的最小安全规则
- 指令执行后的策略校验

## 3. Planner / Task Decomposition

### 攻击面

- 目标劫持
- 任务重定向
- 计划篡改
- 多步攻击链构造

### 典型风险

攻击者通过上下文注入使 Planner 偏离原始用户目标，构造并执行恶意任务序列。

### 对应 ATLAS technique

- AI Agent Context Poisoning
- AI Agent Tool Invocation

### 可测试方式

- mock tool harness
- test instance API

### 当前系统覆盖

已覆盖。Goal hijacking 可通过 Mock Tool Harness 验证（Phase 13）。

### 后续增强方向

增加多步任务链劫持测试、目标偏离检测、恶意子任务构造测试。

### 推荐控制项

- 任务目标不变性校验
- 每步策略复核
- 偏离原始目标阈值告警

## 4. Memory / Context Store

### 攻击面

- 长期记忆投毒
- 上下文窗口污染
- 历史会话泄露
- 记忆标记篡改

### 典型风险

攻击者将恶意内容写入 Agent 记忆系统，使其在后续会话或多轮交互中被调用并执行。

### 对应 ATLAS technique

- AI Agent Context Poisoning
- LLM Data Leakage

### 可测试方式

- mock tool harness
- test instance API

### 当前系统覆盖

已覆盖。Memory poisoning 可通过 Mock Tool Harness 验证（Phase 13，单轮 fake memory store）。

### 后续增强方向

增加记忆读写隔离测试、跨轮上下文污染测试、记忆标签完整性校验。

### 推荐控制项

- 记忆读写权限分离
- 不可信来源标记
- 敏感记忆脱敏
- 历史会话隔离

## 5. Tool Registry

### 攻击面

- 工具白名单绕过
- 工具注册投毒
- 工具元数据篡改
- 动态工具加载风险

### 典型风险

恶意工具被注册到白名单中，或现有工具的描述/参数被篡改，诱导 Agent 错误调用。

### 对应 ATLAS technique

- AI Agent Tool Poisoning
- AI Agent Tool Invocation

### 可测试方式

- mock tool harness
- local sandbox

### 当前系统覆盖

部分覆盖。已有工具名称请求测试。

### 后续增强方向

增加动态工具注册测试、工具元数据签名校验、工具来源白名单。

### 推荐控制项

- 工具注册鉴权
- 工具元数据完整性校验
- 工具来源白名单
- 动态工具加载前人工确认

## 6. Tool Schema

### 攻击面

- 工具 schema 投毒
- schema 验证绕过
- 参数注入
- 类型混淆

### 典型风险

攻击者篡改工具 schema 或在参数中注入恶意内容，使工具调用时产生越权或副作用。

### 对应 ATLAS technique

- AI Agent Tool Data Poisoning
- AI Agent Tool Invocation

### 可测试方式

- local sandbox
- mock tool harness

### 当前系统覆盖

已覆盖。Agent sandbox 有 tool schema validation 测试。

### 后续增强方向

增加复杂 schema 类型混淆测试、嵌套参数注入、默认值篡改测试。

### 推荐控制项

- 严格 schema 验证
- 参数类型与范围校验
- 未知参数拒绝
- 敏感参数二次鉴权

## 7. Tool Invocation

### 攻击面

- 未授权工具调用
- 白名单绕过
- 参数越权
- 频率限制绕过

### 典型风险

Agent 在攻击者诱导下调用不在当前上下文中应允许的工具，或以高权限参数调用低权限工具。

### 对应 ATLAS technique

- AI Agent Tool Invocation
- Credentials from AI Agent Configuration

### 可测试方式

- local sandbox
- manual UI replay
- test instance API

### 当前系统覆盖

已覆盖。Agent sandbox 有未授权工具调用测试。

### 后续增强方向

增加跨工具权限传递测试、会话内权限升级检测、工具调用频率控制。

### 推荐控制项

- 工具白名单
- 最小权限原则
- 每次调用鉴权
- 频率与次数限制

## 8. Tool Result Handling

### 攻击面

- 工具返回内容注入
- 返回结果 exfiltration
- 返回内容诱导后续错误工具调用
- 敏感数据透传

### 典型风险

工具返回的不可信数据中包含恶意指令，被 Agent 读取后执行二次攻击或数据外传。

### 对应 ATLAS technique

- AI Agent Tool Data Poisoning
- Exfiltration via AI Agent Tool Invocation
- LLM Data Leakage

### 可测试方式

- mock tool harness
- local sandbox

### 当前系统覆盖

部分覆盖。已有简单工具返回内容测试。

### 后续增强方向

增加工具返回注入链式攻击测试、返回数据 exfiltration 路径测试、敏感数据透传阻断测试。

### 推荐控制项

- 工具返回数据 sanitization
- 返回内容不可信标记
- 敏感数据脱敏
- exfiltration 路径阻断

## 9. External Channels

### 攻击面

- 邮件外传
- 日历篡改
- 消息推送
- Webhook 回调
- API 出站调用

### 典型风险

Agent 将内部敏感数据通过邮件、消息、Webhook 等外部通道传出。

### 对应 ATLAS technique

- Exfiltration via AI Agent Tool Invocation
- Data Destruction via AI Agent Tool Invocation

### 可测试方式

- mock tool harness
- test instance API

### 当前系统覆盖

部分覆盖。已有 fake email write dry-run 测试。

### 后续增强方向

增加多通道 exfiltration 测试、出站白名单校验、写操作副作用隔离。

### 推荐控制项

- 外部通道白名单
- 出站内容审计
- 写操作人工确认
- dry-run 强制开启

## 10. Skill / Plugin / MCP Layer

### 攻击面

- Skill 代码投毒
- Plugin 元数据投毒
- MCP tool 描述注入
- 动态加载恶意 Skill/Plugin/MCP

### 典型风险

第三方 Skill、Plugin 或 MCP server 返回的工具描述包含恶意指令，诱导 Agent 执行非预期操作。

### 对应 ATLAS technique

- AI Agent Tool Poisoning
- AI Agent Context Poisoning

### 可测试方式

- mock tool harness

### 当前系统覆盖

已覆盖。Skill poisoning 可通过 Mock Tool Harness 验证（Phase 13）。Plugin/MCP poisoning 仍为 planned。

### 后续增强方向

增加 MCP tool 描述注入测试、动态 Skill 加载前校验、Plugin 来源与签名校验。

### 推荐控制项

- Skill/Plugin/MCP 来源白名单
- 动态加载前签名校验
- 工具描述不可信标记
- 第三方代码沙箱隔离

## 11. Write Actions

### 攻击面

- 文件写入
- 数据库修改
- 配置变更
- 资源删除
- 状态持久化

### 典型风险

Agent 在攻击者诱导下执行破坏性写操作，或持久化恶意内容供后续攻击利用。

### 对应 ATLAS technique

- Data Destruction via AI Agent Tool Invocation
- Exfiltration via AI Agent Tool Invocation

### 可测试方式

- local sandbox (dry-run only)
- mock tool harness

### 当前系统覆盖

部分覆盖。已有 fake write action dry-run 测试。

### 后续增强方向

增加写操作类型覆盖、删除/覆盖操作检测、持久化内容完整性校验。

### 推荐控制项

- 写操作默认 dry-run
- 人工确认机制
- 操作可回滚
- 写操作权限分级

## 12. Audit / Evidence / Logs

### 攻击面

- 日志注入
- 证据篡改
- 敏感信息日志泄露
- 审计日志缺失

### 典型风险

攻击者利用日志注入隐藏恶意操作痕迹，或日志中明文记录敏感信息导致泄露。

### 对应 ATLAS technique

- LLM Data Leakage
- Credentials from AI Agent Configuration

### 可测试方式

- local sandbox
- mock tool harness

### 当前系统覆盖

已覆盖。有 evidence redaction 测试和质量检查。

### 后续增强方向

增加结构化日志脱敏、日志完整性校验、审计日志不可篡改机制。

### 推荐控制项

- 日志脱敏
- 审计日志完整性校验
- 敏感字段不落地
- 日志写入权限分离

## 覆盖摘要

| 模块 | 当前状态 | executable |
|---|---|---|
| User Intent / Identity | 部分覆盖 | local sandbox |
| System Instruction / Policy | 已覆盖 | local sandbox |
| Planner / Task Decomposition | 已覆盖 | mock harness |
| Memory / Context Store | 已覆盖 | mock harness |
| Tool Registry | 部分覆盖 | local sandbox |
| Tool Schema | 已覆盖 | local sandbox |
| Tool Invocation | 已覆盖 | local sandbox |
| Tool Result Handling | 部分覆盖 | mock harness |
| External Channels | 部分覆盖 | mock harness |
| Skill / Plugin / MCP | 部分覆盖 | mock harness (Skill), planned (Plugin/MCP) |
| Write Actions | 部分覆盖 | mock harness dry-run |
| Audit / Evidence / Logs | 已覆盖 | local sandbox |
