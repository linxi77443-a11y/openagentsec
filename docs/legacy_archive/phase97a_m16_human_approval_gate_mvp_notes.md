# Phase 97A — M16 Human Approval Gate Validation MVP Notes

## 范围
实现 M16 的最小可执行模拟评估能力，验证 Agent 高风险操作的人工审批关卡在攻击场景下的安全行为。

## 评估模式
adversarial_validation

## 场景覆盖
- approval_required_not_obtained: 审批绕过 — 未获取必要审批
- approval_level_mismatch: 权限提升 — 审批级别不匹配
- approval_bypass_social_engineering: 紧急压力 — 社工诱导跳过审批
- approval_role_impersonation: 角色冒充 — 声称代替休假同事审批
- approval_scope_mismatch: dry-run诱导 — 审批金额范围不匹配
- multi_level_approval_incomplete: 审批链断裂 — 多级审批不完整
- approval_retrospective_claim: 自动批准诱导 — 事后补批
- approval_urgency_pressure: 紧急压力 — 生产事故紧急绕过
- control_approval_correctly_obtained: 标准审批流程（控制用例）
- control_no_approval_needed: 正常审批查询（控制用例）

## 安全边界
- 不连接真实审批系统
- 不使用真实用户权限
- 不访问真实审计日志
- 不连接真实业务系统
- 所有数据使用 `<SIM_...>` 合成占位符

## 安全字段
- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety_claimed: false
- controlled_replay_claimed: false
- attack_execution_allowed: false
- payload_generation_allowed: false
- real_target_selection_allowed: false
- red_team_engine_not_executable: true
- dashboard_not_execution_interface: true

## 结果
- capability_value: high
- risk_level: low
- breakthrough_detected: 0

## 与 M40/M41/M14/M15 的关系
- M40: Agent 行为审计与归因
- M41: Agent 服务账号权限边界
- M14: Agent 高风险动作模拟
- M15: 业务动作模拟
- M16: 人工审批关卡验证（本模块）

## 非目标
- 不是漏洞发现工具
- 不声称 production safety
- 不进入 controlled replay
- 所有发现为 candidate 级别
