# Phase 91A — M49 Permission-Aware Retrieval Hardening Notes

## 范围
本阶段作为 M49 RAG Permission Inheritance and Retrieval Audit 的回归/强化证据，验证 RAG 系统在权限感知检索场景中的边界保持能力。

## 任务类型
regression_hardening（回归强化）

## 评估模式
defensive_evaluation

## 场景覆盖
- low_priv_to_high_priv_retrieval: 低权限用户请求高权限文档检索
- cross_tenant_retrieval_attempt: 跨租户检索请求
- permission_inheritance_bypass: 权限继承绕过尝试
- missing_permission_annotation: 检索结果缺少权限标注
- role_escalation_via_retrieval: 通过检索上下文尝试角色提升
- multi_step_permission_erosion: 多步权限边界侵蚀
- source_attribution_confusion: 来源归因混淆
- expired_permission_token: 过期权限 token 检索
- standard_permission_retrieval: 标准权限检索（控制用例）
- same_tenant_intra_scope_retrieval: 同租户范围内检索（控制用例）

## 安全边界
- 不连接真实 RAG 系统
- 不访问真实权限系统
- 不使用真实知识库
- 不访问真实文档
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

## 与 M48/M49 的关系
- M48: RAG 文档投毒与指令边界
- M49: RAG 权限继承与检索审计（本模块为 M49 的回归强化）

## 非目标
- 不是漏洞发现工具
- 不声称 production safety
- 不进入 controlled replay
- 所有发现为 candidate 级别
- 不新增 M09 模块
- 不更新 PRD 外模块 coverage_depth
