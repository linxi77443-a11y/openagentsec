# 通用 Agent 控制项清单

## 概述

本文档列出 Agentic AI 系统应具备的安全控制项，用于评估前控制基线检查和评估后控制项完整性审计。

## 控制项分类

### 1. Identity / Authorization

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 用户身份验证 | 每个 Agent 会话必须关联已验证用户身份 | 身份冒充、越权操作 | manual review, test instance |
| 会话隔离 | 不同用户会话上下文、记忆、工具权限严格隔离 | 跨用户信息泄露 | mock harness, test instance |
| 工具调用鉴权 | 每次工具调用必须验证当前用户权限 | 越权工具调用 | mock harness, test instance |
| 不可信来源标记 | 外部输入、工具返回、第三方数据必须标记来源 | 上下文投毒、间接注入 | local sandbox, mock harness |
| 权限分级 | 读/写/管理/外传四类权限分离 | 权限升级、破坏性操作 | mock harness, test instance |

### 2. Instruction Hierarchy

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 系统指令层级 | 安全指令不可被用户指令覆盖 | prompt injection | local sandbox |
| 最小安全规则集 | 无论用户指令无法绕过的最小安全规则 | 策略绕过 | local sandbox, mock harness |
| 指令执行后校验 | 工具调用前/回答生成后校验策略一致性 | 多轮绕过 | mock harness, test instance |
| 角色边界定义 | 明确哪些规则来自系统角色定义与权限边界 | 角色越权 | local sandbox |
| 策略变更审计 | 系统策略变更必须留痕并人工确认 | 策略篡改 | mock harness |

### 3. Planner Guardrails

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 任务目标不变性校验 | Planner 分解子任务不得偏离原始用户目标 | 目标劫持 | mock harness, test instance |
| 偏离阈值告警 | 子任务偏离原始目标超过阈值必须告警并停止 | 目标劫持 | mock harness, test instance |
| 恶意任务链回滚 | 检测到偏离后可以回滚到上一安全状态 | 链式攻击 | mock harness |
| 外部输入不可信标记 | Planner 输入必须标记为不可信 | 上下文投毒 | mock harness |
| 任务链长度限制 | 单会话任务链最大步数限制 | 资源消耗、循环攻击 | mock harness |

### 4. Memory Governance

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 记忆读写权限分离 | 写入记忆和读取记忆权限分离 | 记忆投毒、记忆泄露 | mock harness |
| 不可信记忆标记 | 外部来源写入的记忆必须标记不可信 | 记忆投毒 | mock harness |
| 敏感记忆脱敏 | 敏感信息写入记忆前必须脱敏 | 敏感数据泄露 | mock harness, test instance |
| 历史会话隔离 | 不同用户历史会话严格隔离 | 跨会话泄露 | test instance |
| 记忆完整性校验 | 关键系统记忆必须有完整性校验 | 记忆篡改 | mock harness |

### 5. Tool Registry Governance

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 工具注册鉴权 | 新增工具必须经过授权和鉴权 | 恶意工具注册 | mock harness |
| 工具来源白名单 | 只允许白名单来源的工具 | 第三方工具投毒 | mock harness |
| 工具元数据完整性校验 | 工具名称、描述、参数 schema 必须完整可校验 | 工具元数据投毒 | mock harness |
| 动态工具加载前确认 | 动态加载工具必须人工确认 | 恶意工具动态加载 | mock harness, test instance |
| 工具退役机制 | 不再使用的工具必须从注册表移除 | 残留工具风险 | review |

### 6. Tool Schema Validation

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 严格 schema 验证 | 所有工具调用参数必须严格符合 schema | 参数注入、类型混淆 | local sandbox, mock harness |
| 参数类型与范围校验 | 参数类型、范围、枚举值必须校验 | 参数越权 | local sandbox, mock harness |
| 未知参数拒绝 | 不在 schema 中的参数必须拒绝 | 隐藏参数注入 | local sandbox, mock harness |
| 敏感参数二次鉴权 | 标记为敏感的参数调用必须二次鉴权 | 敏感参数越权 | mock harness, test instance |
| 默认值安全校验 | 参数默认值必须安全，不得开启高权限 | 默认值越权 | mock harness |

### 7. Tool Invocation Allowlist

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 工具白名单 | 只允许调用白名单内工具 | 未授权工具调用 | local sandbox, mock harness |
| 最小权限原则 | 默认授予最少必要工具权限 | 权限过大 | review, mock harness |
| 每次调用鉴权 | 每次工具调用必须重新鉴权 | 会话内权限升级 | mock harness, test instance |
| 未知工具拒绝 | 不在白名单的工具必须拒绝调用 | 越权工具调用 | local sandbox, mock harness |
| 权限升级检测 | 同一会话内权限升级必须告警确认 | 权限升级攻击 | mock harness, test instance |

### 8. Tool Result Sanitization

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 工具返回数据 sanitization | 工具返回内容必须经过 sanitization | 工具返回注入 | mock harness |
| 不可信返回标记 | 外部工具返回必须标记为不可信 | 间接注入链式攻击 | mock harness |
| 敏感数据脱敏 | 工具返回中的敏感数据必须脱敏 | 数据泄露 | local sandbox, mock harness |
| 返回内容大小限制 | 工具返回内容大小必须限制 | 上下文窗口投毒 | mock harness |
| 返回内容注入检测 | 检测工具返回中检测 prompt injection 信号 | 间接注入 | mock harness |

### 9. Secret Access Control

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| Secret 读取授权 | 读取 secret 必须经过专门授权 | credential 泄露 | local sandbox, mock harness |
| Secret 值脱敏 | Secret 值在日志、evidence、输出中必须脱敏 | 泄露 | local sandbox, mock harness |
| Secret 外传阻断 | 禁止将 secret 通过任何通道外传 | exfiltration | local sandbox, mock harness |
| Secret 写入隔离 | 写入 secret 必须有独立授权 | 篡改 | mock harness, test instance |
| Fake secret / honeytoken 检测 | 检测到 honeytoken 访问必须告警 | 内部威胁 | local sandbox, mock harness |

### 10. External Channel Egress Control

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 外部通道白名单 | 只允许白名单内外部通道 | 未授权外传 | mock harness |
| 出站内容审计 | 所有出站内容必须审计留痕 | exfiltration | mock harness, test instance |
| 敏感数据外传阻断 | 检测到敏感数据外传必须阻断 | 数据泄露 | mock harness |
| 通道权限分级 | 不同通道有不同权限等级 | 高权限通道滥用 | mock harness |
| 出站频率限制 | 出站调用频率和数量限制 | 批量外传 | mock harness |

### 11. Write Action Human Confirmation

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 写操作默认 dry-run | 所有写操作默认 dry-run 模式 | 意外修改 | local sandbox, mock harness |
| 高风险写操作人工确认 | 删除、覆盖、批量写必须人工确认 | 数据破坏、篡改 | mock harness, test instance |
| 写操作可回滚 | 所有写操作必须支持回滚 | 不可逆破坏 | mock harness, test instance |
| 写操作权限分级 | 不同写操作类型有不同权限要求 | 越权修改 | mock harness |
| 确认旁路检测 | 检测人工确认机制不得被旁路 | 确认绕过攻击 | mock harness |

### 12. Skill / Plugin / MCP Governance

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 来源白名单 | Skill/Plugin/MCP 来源必须在白名单内 | 第三方代码投毒 | mock harness |
| 加载前签名校验 | 加载前必须校验代码/元数据签名 | 恶意代码加载 | mock harness |
| 工具描述 sanitization | 动态加载工具描述必须 sanitization | 工具描述投毒 | mock harness |
| 沙箱隔离执行 | 第三方代码必须在沙箱中隔离执行 | 插件越权 | mock harness |
| 返回数据 sanitization | Skill/Plugin/MCP 返回数据必须 sanitization | 返回注入 | mock harness |

### 13. Resource / Loop Control

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 工具调用频率限制 | 单位时间工具调用次数限制 | 资源消耗、成本收割 | mock harness |
| 单会话总调用限制 | 单会话工具调用总数限制 | 资源消耗、循环攻击 | mock harness |
| 无限循环检测 | 检测相似任务重复调用并告警停止 | 循环攻击、DoS | mock harness |
| 成本阈值告警 | 调用成本超过阈值必须告警停止 | cost harvesting | mock harness, test instance |
| 资源配额管理 | 按用户/会话/时间维度资源配额管理 | 资源滥用 | mock harness, test instance |

### 14. Audit Logging

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 所有工具调用审计 | 所有工具调用必须完整审计留痕 | 攻击无迹、隐匿攻击 | mock harness |
| 决策过程审计 | Planner 决策过程必须审计留痕 | 决策篡改 | mock harness |
| 策略变更审计 | 安全策略变更必须审计留痕 | 策略篡改 | mock harness |
| 用户操作审计 | 用户关键操作必须审计留痕 | 操作抵赖 | test instance |
| 审计日志完整性校验 | 审计日志必须有完整性校验 | 日志篡改 | mock harness |

### 15. Evidence / Log Redaction

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 结构化日志脱敏 | 结构化日志字段级脱敏 | 日志泄露 | local sandbox, mock harness |
| Secret / token / honeytoken 脱敏 | 敏感标识必须全链路脱敏 | 泄露 | local sandbox, mock harness |
| PII 脱敏 | 个人可识别信息必须脱敏 | 隐私合规 | mock harness |
| 日志写入权限分离 | 日志写入权限与其他操作分离 | 日志篡改 | mock harness |
| Evidence 完整性校验 | Evidence 文件必须有完整性校验 | evidence 篡改 | local sandbox |

### 16. Emergency Stop / Rollback

| 控制项 | 说明 | 风险 | 测试方式 |
|---|---|---|---|
| 紧急停止机制 | 存在紧急停止按钮/API，可立即停止所有执行 | 攻击扩散 | review, test instance |
| 会话级回滚 | 单会话所有写操作可整体回滚 | 不可逆破坏 | mock harness, test instance |
| 工具级回滚 | 单个工具写操作可单独回滚 | 局部破坏 | mock harness |
| 异常状态恢复 | 异常状态下可安全恢复到已知安全状态 | 死锁、僵死 | mock harness |
| 攻击后取证保留 | 攻击后保留完整证据不得被覆盖 | 证据销毁 | mock harness |

## OWASP Agentic Top 10 映射

每个控制分类对应 OWASP Agentic Top 10 风险。详见 `owasp/agentic_control_mapping.yaml`。

| ASI | 名称 | 对应控制分类 |
|---|---|---|
| ASI01 | Agent Goal Hijack | Planner Guardrails、Instruction Hierarchy |
| ASI02 | Tool Misuse and Exploitation | Tool Schema、Tool Invocation、Tool Result |
| ASI03 | Identity and Privilege Abuse | Identity、Secret Access、Audit |
| ASI04 | Agentic Supply Chain | Tool Registry、Skill/Plugin/MCP |
| ASI06 | Memory & Context Poisoning | Memory Governance、Tool Result |
| ASI08 | Cascading Failures | Resource / Loop Control |
| ASI09 | Human-Agent Trust Exploitation | Write Action、Identity |

## 控制项覆盖统计

| 分类 | 控制项数量 | 当前系统覆盖 |
|---|---|---|
| Identity / Authorization | 5 | 部分 |
| Instruction Hierarchy | 5 | 部分 |
| Planner Guardrails | 5 | mock harness 可测 |
| Memory Governance | 5 | mock harness 可测 |
| Tool Registry Governance | 5 | mock harness 可测 |
| Tool Schema Validation | 5 | 已覆盖 |
| Tool Invocation Allowlist | 5 | 已覆盖 |
| Tool Result Sanitization | 5 | mock harness 可测 |
| Secret Access Control | 5 | 已覆盖 |
| External Channel Egress Control | 5 | mock harness 可测 |
| Write Action Human Confirmation | 5 | mock harness 可测 |
| Skill / Plugin / MCP Governance | 5 | mock harness 可测（Skill） |
| Resource / Loop Control | 5 | mock harness 可测 |
| Audit Logging | 5 | 部分 |
| Evidence / Log Redaction | 5 | 已覆盖 |
| Emergency Stop / Rollback | 5 | planned |
| **总计** | **80** | **mock harness 可测 55 / 80** |
