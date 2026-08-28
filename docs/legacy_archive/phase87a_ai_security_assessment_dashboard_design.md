# Phase 87A — AI安全评估可视化仪表盘设计门

## 1. 概述

Phase 87A 以纯设计门方式定义 AI 安全评估可视化仪表盘蓝图，整合 v1.0-v2.0 全部模块资产、Phase 86B 冻结 schema、攻击路径目录、节点防御状态演化模型、防御降级轨迹报告和红队攻击链自动化引擎流程。

仪表盘定义四类核心视图：
1. **攻击面覆盖热力图 (Coverage Heatmap)** — 矩阵锚点 × 模块的覆盖深度着色
2. **攻击链传播视图 (Attack Chain Propagation View)** — 链级多节点传播与防御状态演化
3. **防御降级轨迹图 (Defense Degradation Timeline)** — 节点防御状态随时间演化轨迹
4. **红队引擎操作面板 (Red Team Engine Panel)** — 模拟运行、突破信号查看、证据浏览

## 2. 设计约束

| 控制项 | 值 |
|-------|-----|
| design_gate_only | true |
| synthetic_only | true |
| no_code_implementation | true |
| no_chart_generation | true |
| no_real_execution | true |
| no_real_payload | true |
| confirmed_vulnerability | false |
| formal_finding_allowed | false |
| production_safety_claimed | false |
| controlled_replay_claimed | false |
| controlled_replay_execution_allowed | false |
| capability_value | not_applicable (设计门) |
| risk_level | not_applicable (设计门) |

## 3. 设计信号

| 信号 | 含义 | 值 |
|------|------|-----|
| coverage_heatmap_design_defined | 攻击面覆盖热力图设计已定义 | true |
| attack_chain_graph_design_defined | 攻击链传播视图设计已定义 | true |
| defense_degradation_timeline_defined | 防御降级轨迹图设计已定义 | true |
| red_team_engine_panel_defined | 红队引擎面板设计已定义 | true |
| data_source_mapping_defined | 数据源映射已定义 | true |
| interaction_logic_defined | 交互逻辑已定义 | true |
| safety_boundary_assertions_defined | 安全边界断言已定义 | true |
| no_code_implementation_asserted | 禁止代码实现已断言 | true |
| no_real_execution_asserted | 禁止真实执行已断言 | true |
| human_review_required | 人工复核计数 | {case_level=0, design_gate=true, judge=true} |
| inconclusive_count | 未决计数 | 0 |

## 4. 数据来源

| 数据源 | 来源 Phase | 用途 |
|--------|-----------|------|
| module_registry.yaml | Phase 35C | 模块清单、coverage_status、priority、layer |
| capability_scorecard.yaml | 各模块 MVP | capability_value、risk_level、验证计数 |
| result.yaml | 各模块 MVP | 控制用例表现、信号分布 |
| phase86b_result_schema.yaml | Phase 86B | 结果 schema、freeze signals |
| phase86b_capability_scorecard_schema.yaml | Phase 86B | 计分卡 schema |
| phase86b_attack_chain_schema.yaml | Phase 86B | 攻击链/节点 schema |
| phase86b_state_machine.yaml | Phase 86B | 5 态防御状态机 |
| phase86b_safety_assertions.yaml | Phase 86B | 安全边界断言 |
| Phase 75A 攻击路径目录 | Phase 75A | 路径-模式关联 |
| Phase 77A 节点防御状态演化模型 | Phase 77A | 防御演化状态 |
| Phase 78A 防御降级轨迹报告 Schema | Phase 78A | 降级轨迹格式 |

## 5. 视图概要

| 视图 | 文件 | 用途 |
|------|------|------|
| 覆盖热力图 | coverage_heatmap_view_spec.yaml | 矩阵锚点 × 模块覆盖深度 |
| 攻击链传播 | attack_chain_propagation_view_spec.yaml | 链级攻击流与防御状态 |
| 防御降级轨迹 | defense_degradation_timeline_view_spec.yaml | 节点防御状态时间线 |
| 红队引擎面板 | red_team_engine_panel_spec.yaml | 模拟运行与突破信号 |

## 6. 安全边界

- `breakthrough_detected` = simulated capability signal only，不等于 confirmed vulnerability
- `exploit_chain_candidate` = simulated attack path，不等于真实 exploit
- `evidence_trace` = 模拟证据链，不等于真实审计证据
- 所有数据使用 `<SIM_...>` synthetic placeholders
- 不包含代码实现、图表组件、API 服务
- 不连接真实系统，不调用真实 API
- hot 颜色 (红色/橙色) 仅表示覆盖缺口或模拟突破信号，不表示真实漏洞
