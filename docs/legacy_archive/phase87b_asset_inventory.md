# Phase 87B — AI安全评估可视化实施准备评估
# 资产盘点清单 — Phase 87A 12 设计交付物

## 盘点范围

Phase 87A 全部 12 个设计交付物 + validate 检查结果。

## 资产清单

| # | 资产类型 | 文件路径 | 核心内容 | 数据量 | 状态 |
|---|---------|---------|---------|-------|------|
| 1 | 设计文档 | `docs/phase87a_ai_security_assessment_dashboard_design.md` | 概述、设计约束、11 设计信号、8 数据来源、4 视图概要、安全边界 | ~80 行 | ✅ |
| 2 | 布局蓝图 | `executions/phase87a_dashboard_design/dashboard_layout_blueprint.yaml` | 4 Tab 布局、导航栏、颜色语义(7+5 色)、4 角色权限、4 筛选维度、5 交互模式 | ~213 行 | ✅ |
| 3 | 数据契约 | `executions/phase87a_dashboard_design/dashboard_data_contract.yaml` | 11 数据源注册、6 字段映射分类、5 契约规则 | ~180 行 | ✅ |
| 4 | 可视化输入 Schema | `executions/phase87a_dashboard_design/visualization_input_schema.yaml` | 4 视图输入 required_fields、aggregation/visualization 规则、5 通用规则 | ~250 行 | ✅ |
| 5 | 覆盖热力图视图规范 | `executions/phase87a_dashboard_design/coverage_heatmap_view_spec.yaml` | 9 矩阵锚点 × 11 层、7 级色图、4 交互(7 字段 tooltip)、6 图例项、4 安全断言 | ~170 行 | ✅ |
| 6 | 攻击链传播视图规范 | `executions/phase87a_dashboard_design/attack_chain_propagation_view_spec.yaml` | 节点模式P01-P10、5 态颜色语义、有向边、4 交互、4 安全断言 | ~130 行 | ✅ |
| 7 | 防御降级轨迹视图规范 | `executions/phase87a_dashboard_design/defense_degradation_timeline_view_spec.yaml` | 水平状态条、5 态色图、6 汇总指标、4 交互、4 安全断言 | ~120 行 | ✅ |
| 8 | 红队引擎操作面板规范 | `executions/phase87a_dashboard_design/red_team_engine_panel_spec.yaml` | 5 攻击者类型、9 攻击目标、3 运行模式、突破信号查看器、3 方输出、6 安全断言 | ~250 行 | ✅ |
| 9 | 结果 Schema | `executions/phase87a_dashboard_design/phase87a_result_schema.yaml` | 11 设计信号、6 设计模块计数、5 设计门状态字段、8 数据来源映射、11 字段安全边界 | ~103 行 | ✅ |
| 10 | Validator 检查清单 | `executions/phase87a_dashboard_design/validator_checklist.yaml` | 7 类别 43 检查规则、设计门标志12+安全边界10+禁止代码6+禁止图表4+禁止执行5+禁止payload3+合成数据3 | ~203 行 | ✅ |
| 11 | 设计笔记 | `docs/phase87a_ai_security_assessment_dashboard_design_notes.md` | 11 信号表、安全声明、7 类别 validator、非目标清单 | ~60 行 | ✅ |
| 12 | Run Config | `run_configs/phase87a_ai_security_assessment_dashboard_design_run_config.yaml` | 引擎配置、路径配置、安全约束 | ~58 行 | ✅ |
| — | Validator 执行结果 | `executions/phase87a_dashboard_design/validate_summary.json` | 169/169 passed, 16 categories | — | ✅ |
| — | Validator 脚本 | `scripts/validate_phase87a_ai_security_assessment_dashboard_design.py` | 16 检查类别, ~580 行 Python | ~580 行 | ✅ |

## 资产统计

- 设计文档: 2 个(.md)
- YAML Schema: 9 个
- Validate 脚本: 1 个(.py)
- Run Config: 1 个(.yaml)
- 总计文件: 14 个（含 validator 结果）
- 总计有效行数: ~2000 行
