# Phase 93A — M46→M47→M50 跨模块攻击路径联动设计门 Notes

## 范围
定义 M46→M47→M50 跨模块攻击路径的联动设计门，包括攻击路径 schema、trace 关联机制、防御状态机和 Red/Blue/Purple 映射。

## 任务类型
design_gate（纯设计门，不执行 runtime）

## PRD 对齐
- PRD v2.0 §2.2: AI 系统全生命周期安全层级
- PRD v3.1 §2.1: 模拟红队能力矩阵
- PRD v3.1 §2.8: 攻击传播动力学

## 设计内容

### 攻击路径 Schema
- 4 条预定义攻击路径
- 覆盖 M46→M47→M50、M48→M49→M50、M41→M47→M50 等链路
- 验证规则：入口模块有效、目标模块有效、传播链完整

### Trace 关联规则
- trace_id 传播规则：入口模块生成、后续模块继承
- 审计日志关联：M46→M47→M50 审计链
- 身份关联：跨模块 actor 身份一致
- 租户关联：跨模块 tenant_id 一致
- 时间戳关联：跨模块时间戳顺序

### 防御状态机
- 5 种状态：stable, pressured, degraded, blocked, failed
- 6 种状态转移规则
- 传播概率模型：decay_factor=0.8, amplification_factor=1.2
- 3 种反馈循环：审计缺口、权限泄漏、凭据压力

### Red/Blue/Purple 映射
- Red: 攻击证据候选
- Blue: 防护控制候选（preventive/detective/response）
- Purple: 复测方案候选

## 安全字段
- capability_value: not_applicable
- risk_level: not_applicable
- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety: out_of_scope

## 非目标
- 不是代码实现
- 不执行 runtime
- 不新增攻击用例
- 不连接真实系统
- 不声称 production safety
