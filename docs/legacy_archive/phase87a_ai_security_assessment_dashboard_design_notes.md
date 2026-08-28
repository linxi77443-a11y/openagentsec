# Phase 87A — AI安全评估可视化仪表盘设计门

## 范围

Phase 87A 以纯设计门方式定义 AI 安全评估可视化仪表盘蓝图，整合 v1.0-v2.0 全部模块资产、Phase 86B 冻结 schema、攻击路径目录（Phase 75A）、节点防御状态演化模型（Phase 77A）、防御降级轨迹报告 Schema（Phase 78A）和攻击链生成流程（Phase 86A）。

仪表盘定义四类核心视图：覆盖热力图、攻击链传播视图、防御降级轨迹图、红队引擎操作面板。

## 设计信号（11 个）

| 信号 | 值 |
|------|-----|
| coverage_heatmap_design_defined | true |
| attack_chain_graph_design_defined | true |
| defense_degradation_timeline_defined | true |
| red_team_engine_panel_defined | true |
| data_source_mapping_defined | true |
| interaction_logic_defined | true |
| safety_boundary_assertions_defined | true |
| no_code_implementation_asserted | true |
| no_real_execution_asserted | true |
| human_review_required | {case_level=0, design_gate=true, judge=true} |
| inconclusive_count | 0 |

## 安全声明

- `design_gate_only`: true — 纯设计门，不包含可执行代码、不生成图表
- `no_chart_generation`: true — 不生成实际图表、图片、UI 组件
- `synthetic_only`: true — 所有数据使用 `<SIM_...>` 占位符
- `confirmed_vulnerability`: false — 未声明真实漏洞
- `formal_finding_allowed`: false — 不作正式发现
- `production_safety_claimed`: false — 不声明生产安全
- `controlled_replay_claimed`: false — 不声明受控回放
- `capability_value`: not_applicable — 设计门不声明能力值
- `risk_level`: not_applicable — 设计门不声明风险等级
- `breakthrough_detected` 语义: simulated capability signal only
- `exploit_chain_candidate` 语义: simulated attack path
- 所有 `real_*` 连接字段: false
- hot 颜色（红色/橙色）仅表示覆盖缺口或模拟突破信号，不表示真实漏洞

## Validator 检查项

7 个检查类别，43 条检查规则：
- design_gate_flags (12) — 设计门标志一致性
- security_boundary (10) — 安全边界断言
- no_code_implementation (6) — 禁止代码实现
- no_chart_generation (4) — 禁止图表生成
- no_real_execution (5) — 禁止真实执行
- no_real_payload (3) — 禁止真实 payload
- synthetic_only (3) — 仅合成数据

## 非目标

- 不实现前端代码、后端代码、图表组件、API 服务
- 不生成实际图片、图表、UI 截图或可执行原型
- 不连接真实系统、不调用真实 API
- 不执行攻击链、不启动模拟执行
- 不修改 module_registry.yaml 的业务结论
- 不更新任何模块 coverage_status
- 不声明 production_safety / controlled_replay_safety
