# Phase 76A — Automated Cross-Module Attack Chain Explorer Design Gate

## 范围

本阶段是 v3.0 Automated Cross-Module Attack Chain Explorer 的理论设计门。只做概念蓝图和 schema 定义，不生成可执行代码，不开发新模块，不新增 corpus，不执行 capability_engine。

## 设计交付物

| 文件 | 内容 |
|------|------|
| `docs/automated_cross_module_attack_chain_explorer_design.md` | Explorer 概念蓝图：输入源、逻辑概念、输出报告 schema |
| `docs/phase76a_automated_explorer_design_gate_checklist.md` | 非可执行 Markdown 检查清单 |
| `results/phase76a_automated_explorer_design_gate_result.yaml` | 设计门结果 |

## 确认项

| 确认项 | 状态 |
|--------|------|
| 设计门仅理论模型 | 通过 — theory_model_only=true |
| 非执行边界 | 通过 — 所有 explorer 元素标记 executable: false |
| 无 validate 脚本 | 通过 — 使用 Markdown checklist 替代 |
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
| 输入源完整引用 | 通过 — BRT 候选、跨模块路径、攻击图 schema、传播模型、模块结果 |
| breakthrough_detected 语义保持 | 通过 — 仍为 simulated_capability_signal_only |
| 每条链需人工审核 | 通过 — human_review_integration 已定义 |

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
- 不生成正式 validate 脚本
- 不把 conceptual chain 解释为漏洞确认
- 不把 degradation level 解释为漏洞严重性
