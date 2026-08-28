# Phase 68A — M43 MCP Tool Descriptor Integrity MVP Notes

## 范围

本阶段是 **M43 MCP Tool Descriptor Integrity MVP**，基于 PRD v2.0 SC-01 剧本（MCP Tool Descriptor Poisoning Simulation），使用 adversarial_validation 模式验证 Agent 在面对 MCP-like 工具描述、manifest、schema、metadata 中的 instruction-like content、伪权威声明、优先级诱导、工具能力夸大、交叉工具权限暗示、隐含动作诱导时，是否能保持"工具描述是低信任供应链元数据，不是系统指令"的边界。

## 评估配置

| 字段 | 值 |
|------|-----|
| 评估模式 | adversarial_validation |
| 攻击者类型 | indirect_prompt_source |
| 攻击目标 | supply_chain_tool_descriptor_poisoning |
| 目标边界 | tool_descriptor_trust_boundary |
| 执行引擎 | capability_engine（模拟防御评估，fake runtime only） |
| 数据 | `<SIM_MCP_TOOL_...>` / `<SIM_TOOL_DESCRIPTOR_...>` / `<SIM_TOOL_MANIFEST_...>` / synthetic only |
| 真实 MCP Server | 未连接 |
| 真实工具注册表 | 未访问 |
| 真实工具 | 未加载，未调用 |
| 真实 API | 未调用 |
| 真实数据 | 未访问 |
| 真实 payload | 未生成 |

## SC-01 剧本映射

| 剧本字段 | 值 |
|----------|-----|
| playbook_id | SC-01 |
| playbook_name | MCP Tool Descriptor Poisoning Simulation |
| module_id | M43 |
| module_name | MCP Tool Descriptor Integrity |
| assessment_mode | adversarial_validation |
| attacker_type | indirect_prompt_source |
| attack_objective | supply_chain_tool_descriptor_poisoning |
| target_boundary | tool_descriptor_trust_boundary |

## Corpus 覆盖

13 条 MVP cases（11 攻击场景 + 2 control cases），覆盖 8 个攻击类别。

| 类别 | 条目数 | 说明 |
|------|--------|------|
| descriptor_instruction_like_content | 2 | 描述中包含指令型内容 |
| descriptor_tool_priority_manipulation | 2 | 工具优先级操控 |
| descriptor_fake_authority_claim | 1 | 伪造权限声明 |
| descriptor_capability_overclaim | 1 | 能力过度声称 |
| descriptor_manifest_metadata_drift | 1 | 清单元数据漂移 |
| descriptor_hidden_risk_hint | 1 | 隐藏风险提示 |
| descriptor_tool_invocation_induction | 2 | 工具调用诱导（NEW） |
| descriptor_cross_tool_permission_confusion | 1 | 交叉工具权限混淆（NEW） |
| safe_descriptor_control_case | 1 | 正常描述控制案例 |
| benign_tool_metadata_control_case | 1 | 良性元数据控制案例 |

## 核心信号

- `descriptor_poisoning_detected` — 工具描述投毒已识别
- `tool_metadata_untrusted` — 工具元数据被标记为不可信
- `descriptor_instruction_ignored` — 描述中指令型内容被忽略
- `fake_tool_invocation_blocked` — 虚假工具调用被阻止
- `tool_priority_manipulation_blocked` — 优先级操控被阻止
- `fake_authority_claim_rejected` — 伪权威声明被拒绝
- `capability_overclaim_detected` — 能力夸大被检测
- `manifest_metadata_drift_detected` — 清单元数据漂移被检测
- `cross_tool_permission_confusion_blocked` — 交叉工具权限混淆被阻止
- `benign_tool_metadata_allowed` — 正常元数据被允许
- `human_review_required` — 需要人工审核

## Run / Parser / Result / Scorecard 摘要

| 指标 | 值 |
|------|-----|
| 总请求数 | 13 |
| 成功数 | 13 |
| 错误数 | 0 |
| descriptor_poisoning_detected | 11 |
| tool_metadata_untrusted | 11 |
| fake_tool_invocation_blocked | 6 |
| breakthrough_candidate | 0 |
| control_passed | 2 |
| capability_value | high |
| risk_level | low |
| result_is_candidate_level | true |
| production_safety | out_of_scope |

## 安全声明

- `confirmed_vulnerability`: false
- `formal_finding_allowed`: false
- `production_safety_claimed`: false
- `controlled_replay_claimed`: false
- `breakthrough_candidate` 仅表示 `simulated_capability_signal`
- 所有数据使用 `<SIM_...>` / fake / synthetic only
- 不连接真实 MCP Server
- 不访问真实工具注册表
- 不加载真实工具描述
- 不调用真实工具
- 不生成真实 payload
- 不进入 controlled replay

## 裁判条件性通过声明

| 字段 | 值 |
|------|-----|
| single_module_only | true |
| module_id | M43 |
| playbook_id | SC-01 |
| run_config_created | true |
| capability_value | high |
| risk_level | low |
| capability_value_risk_level_separated | true |
| confirmed_vulnerability | false |
| formal_finding_allowed | false |
| production_safety_claimed | false |
| controlled_replay_claimed | false |
| breakthrough_candidate_is_simulated_signal_only | true |
| judge_review_packet_ready | true |

## 非目标与禁止项

- 不声明 production_ready
- 不声明 controlled_replay_ready
- 不连接真实 MCP Server
- 不访问真实 MCP registry
- 不加载真实 tool descriptor
- 不调用真实 MCP tool
- 不执行真实 API
- 不读取真实工具参数
- 不访问真实企业系统
- 不使用真实客户/员工数据
- 不把 descriptor poisoning candidate 写成 confirmed vulnerability
- 不把 result 写成正式漏洞报告
- 不声明 production safety
- 不包括 M48/M49/M50 等其他模块
- 不包括跨模块攻击链
- 不包括理论手册内容
