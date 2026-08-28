# Phase 75A — Cross-Module Attack Path Catalog MVP

## 范围

本阶段是 v3.0 cross-module attack path catalog MVP。只做概念性路径目录，所有路径均为 conceptual_path，不执行攻击，不开发新模块，不新增 corpus，不新增 run_config，不执行 capability_engine。

## 设计交付物

| 文件 | 内容 |
|------|------|
| `docs/cross_module_attack_path_catalog.md` | 跨模块攻击路径目录（10 章节，8 条概念路径） |
| `docs/phase75a_cross_module_attack_path_catalog_notes.md` | 本说明文件 |
| `results/phase75a_cross_module_attack_path_catalog_result.yaml` | 目录结果 |
| `scripts/validate_phase75a_cross_module_attack_path_catalog.py` | 文档完整性验证脚本 |

## 确认项

| 确认项 | 状态 |
|--------|------|
| catalog_only | 通过 — catalog_only=true |
| conceptual_paths_only | 通过 — 所有路径 conceptual_path=true |
| executable_paths=false | 通过 — 所有路径 executable=false |
| attack_execution_allowed=false | 通过 — 所有路径 attack_execution_allowed=false |
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
| evidence_trace 只引用不生成 | 通过 — 所有引用标记 new_evidence_generated=false |
| 每条路径需人工审核 | 通过 — 所有路径 human_review_required=true |

## 路径目录摘要

| 指标 | 值 |
|------|-----|
| 路径总数 | 8 |
| 覆盖模块 | M43, M46, M47, M48, M49, M50 |
| 覆盖层级 | supply_chain, development_environment, rag_data, runtime_sandbox |
| evidence_trace 引用总数 | 18 个模块引用 |
| conceptual_risk_amplification_notes | 概念模型，非生产风险/非漏洞严重性 |

## 非目标

- 不执行攻击路径
- 不生成可执行攻击链
- 不开发新模块
- 不新增 corpus / adversarial_playbook
- 不新增 run_config
- 不执行 capability_engine
- 不生成 execution_results.json
- 不执行 parser
- 不生成 capability_scorecard
- 不进入 controlled replay
- 不连接真实系统
- 不生成真实 payload / 真实命令
- 不把 conceptual path 解释为漏洞确认
- 不把 path catalog 解释为 production risk model
