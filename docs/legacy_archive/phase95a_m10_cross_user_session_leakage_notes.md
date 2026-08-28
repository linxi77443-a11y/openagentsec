# Phase 95A — M10 Cross-User / Cross-Session Leakage MVP Notes

## 范围
实现 M10 的最小可执行模拟评估能力，验证 RAG 系统在跨用户/跨会话场景中的数据隔离能力。

## 评估模式
adversarial_validation

## 场景覆盖
- cross_user_data_access: 跨用户数据访问
- cross_session_context_leakage: 跨会话上下文泄漏
- user_identity_spoofing: 用户身份伪造
- session_hijacking_attempt: 会话劫持尝试
- cross_tenant_data_isolation: 跨租户数据隔离
- multi_turn_identity_escalation: 多轮身份提升
- context_pollution_leakage: 上下文污染泄漏
- data_aggregation_leakage: 数据聚合泄漏
- same_user_same_session_access: 同用户同会话访问（控制用例）
- same_tenant_authorized_access: 同租户授权访问（控制用例）

## 安全边界
- 不连接真实用户系统
- 不访问真实会话存储
- 不使用真实租户数据库
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

## 与 M07/M08/M49 的关系
- M07: 未授权数据访问
- M08: 角色边界验证
- M10: 跨用户/跨会话泄漏（本模块）
- M49: RAG 权限继承与检索审计

## 非目标
- 不是漏洞发现工具
- 不声称 production safety
- 不进入 controlled replay
- 所有发现为 candidate 级别
