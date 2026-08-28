# Phase 74A — Cross-Module Attack Graph & Propagation Model Design Gate

## 范围

本阶段是 v3.0 跨模块攻击图与风险传播模型的理论设计门。只做理论模型和 schema 定义，不做新模块开发，不新增 corpus，不执行 capability_engine。

## 设计交付物

| 文件 | 内容 |
|------|------|
| `docs/cross_module_attack_graph_schema.md` | 攻击图节点、边、路径、层级、模块映射、evidence 引用 schema |
| `docs/risk_propagation_model.md` | 风险传播规则类型、放大因子、衰减因子、边界保持规则、human review gate |

## 确认项

| 确认项 | 状态 |
|--------|------|
| 设计门仅理论模型 | 通过 — theory_model_only=true |
| 非执行边界 | 通过 — 所有 graph element 标记 executable: false |
| 不开发新模块 | 通过 — 未新增 |
| 不新增 corpus | 通过 — 未新增 |
| 不新增 run_config | 通过 — 未新增 |
| 不执行 capability_engine | 通过 — 未执行 |
| 不生成 execution_results | 通过 — 未生成 |
| 不进入 controlled replay | 通过 — 未进入 |
| 不连接真实系统 | 通过 — 未连接 |
| 不生成真实 payload | 通过 — 未生成 |
| 不声明 confirmed vulnerability | 通过 — 未声明 |
| 不声明 formal finding | 通过 — 未声明 |
| 不声明 production safety | 通过 — 未声明 |
| risk_amplification_factor 为概念模型 | 通过 — 已明确 not_production_risk / not_vulnerability_severity |
| breakthrough_detected 语义保持 | 通过 — 仍为 simulated_capability_signal_only |

## 非目标

- 不开发新模块
- 不新增 corpus / adversarial_playbook
- 不新增 run_config
- 不执行 capability_engine
- 不生成 execution_results
- 不执行 parser
- 不生成 capability_scorecard
- 不进入 controlled replay
- 不连接真实系统
- 不生成真实 payload
- 不生成可执行攻击链
- 不把 conceptual path 解释为漏洞确认
- 不把 propagation model 解释为生产风险模型
- 不把 risk amplification factor 解释为 CVSS 或漏洞严重性
