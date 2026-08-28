# Phase 96A — M11 Data Source Trust Boundary MVP Notes

## 范围
实现 M11 的最小可执行模拟评估能力，验证 RAG 系统在数据源信任边界场景中的安全能力。

## 评估模式
adversarial_validation

## 场景覆盖
- untrusted_source_injection: 不可信数据源注入
- source_identity_spoofing: 数据源身份伪造
- metadata_tampering: 数据源元数据篡改
- source_attribution_confusion: 数据源来源混淆
- cross_tenant_source_injection: 跨租户数据源注入
- source_priority_manipulation: 数据源优先级操纵
- expired_source_credential: 过期数据源凭证
- source_trust_escalation: 数据源信任提升
- trusted_source_normal_retrieval: 可信数据源正常检索（控制用例）
- same_tenant_source_access: 同租户数据源访问（控制用例）

## 安全边界
- 不连接真实数据源
- 不访问真实知识库
- 不使用真实外部服务
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

## 与 M48/M49/M10/M05 的关系
- M48: RAG 文档投毒与指令边界
- M49: RAG 权限继承与检索审计
- M10: 跨用户/跨会话泄漏
- M11: 数据源信任边界（本模块）
- M05: 输出边界控制

## 非目标
- 不是漏洞发现工具
- 不声称 production safety
- 不进入 controlled replay
- 所有发现为 candidate 级别
