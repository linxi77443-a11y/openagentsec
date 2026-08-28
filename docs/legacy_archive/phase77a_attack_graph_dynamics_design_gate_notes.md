# Phase 77A — Attack Graph Dynamics Simulation Layer Design Gate

## 范围

本阶段是 Attack Graph Dynamics Simulation Layer 的理论设计门。只做传播动力学概念设计、节点防御状态演化模型设计、反馈循环机制设计、Attack Evolution Trajectory Report Schema 设计。不生成可执行代码，不生成脚本，不实现 simulator。

## 设计交付物

| 文件 | 内容 |
|------|------|
| `docs/attack_graph_dynamics_model.md` | 攻击图动态传播模型（12 章节） |
| `docs/node_defense_state_evolution_model.md` | 节点防御状态演化模型（11 章节，8 状态） |
| `docs/attack_graph_feedback_loop_model.md` | 反馈循环机制（10 章节，4 反馈循环） |
| `docs/attack_evolution_trajectory_report_schema.md` | 攻击演化轨迹报告 Schema（18 章节） |
| `docs/phase77a_attack_graph_dynamics_design_gate_notes.md` | 本说明文件 |
| `docs/phase77a_attack_graph_dynamics_design_gate_checklist.md` | 非可执行 Markdown 检查清单 |
| `results/phase77a_attack_graph_dynamics_design_gate_result.yaml` | 设计门结果 |

## 确认项

| 确认项 | 状态 |
|--------|------|
| design_gate_only | 通过 |
| theory_model_only | 通过 |
| dynamics_model_only | 通过 |
| report_schema_only | 通过 |
| executable_code_created=false | 通过 |
| script_created=false | 通过 |
| simulator_implemented=false | 通过 |
| 不新增 corpus | 通过 |
| 不新增 run_config | 通过 |
| 不执行 capability_engine | 通过 |
| 不生成 execution_results | 通过 |
| 不进入 controlled replay | 通过 |
| 不连接真实系统 | 通过 |
| 不声明 confirmed vulnerability | 通过 |
| 不声明 formal finding | 通过 |
| 不声明 production safety | 通过 |

## 设计摘要

| 指标 | 值 |
|------|-----|
| 动态传播模型章节 | 12 |
| 节点防御状态 | 8（stable/pressured/degraded/partially_blocked/blocked/recovered/inconclusive/human_review_required） |
| 反馈循环 | 4（audit_gap/permission_leakage/credential_pressure/runtime_control） |
| 报告 Schema 字段 | 25+ |
| 所有概念标记 conceptual_only/not_execution_result/conceptual_loop_only | 通过 |

## 非目标

- 不生成任何可执行代码、脚本
- 不实现 dynamics simulator
- 不新增 corpus / run_config
- 不执行 capability_engine
- 不进入 controlled replay
- 不连接真实系统
- 不把 propagation probability 解释为真实攻击概率
- 不把 amplification factor 解释为漏洞严重性
- 不把 defense state 解释为漏洞确认
- 不把 feedback loop 解释为真实系统因果关系
