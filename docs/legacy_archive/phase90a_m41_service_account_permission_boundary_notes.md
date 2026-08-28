# Phase 90A — M41 Agent Service Account Permission Boundary MVP Notes

## 范围
本阶段实现 M41 Agent Service Account Permission Boundary 的最小可执行模拟评估能力，验证 Agent 在面对 service account scope 不匹配、跨租户滥用、read-only 升级到 write、service account 替代用户授权等场景时，是否能保持权限边界。

## 场景覆盖
- read_only_to_write_escalation: read-only service account 尝试调用 write 工具
- scope_mismatch_tool_invocation: service account scope 与目标工具不匹配
- cross_tenant_service_account_abuse: 跨租户 service account 调用
- service_account_privilege_confusion: service account 权限混淆
- sa_as_user_authorization_substitute: service account 替代用户授权
- sa_scope_crep_multistep: 多步 scope creep
- sa_scope_via_parameter_pollution: 参数污染绕过 scope
- sa_expired_scope_token: 过期 scope token
- sa_impersonation_attempt: service account 冒充
- matched_scope_sa_invocation: 正常匹配 scope 调用（控制用例）
- sa_with_proper_authorization: 有授权的 SA 调用（控制用例）

## 评估模式
adversarial_validation

## 安全边界
- 不连接真实 IAM 系统
- 不访问真实 service account（no real service account）
- 不使用真实租户配置
- 不执行真实工具调用
- 不调用真实 API
- 所有数据使用 `<SIM_...>` 合成占位符

## 结果
- capability_value: high
- risk_level: low
- breakthrough_detected: 0
- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety_claimed: false

## 非目标
- 不是漏洞发现工具
- 不声称 production safety
- 不进入 controlled replay
- 所有发现为 candidate 级别
