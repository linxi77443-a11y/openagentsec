# Phase 85A — 《AI攻击行为理论手册》整理任务

## 范围

本阶段将项目 v1.0 到 v3.0 的全部阶段性成果整理为一份结构化理论手册《AI 攻击行为理论手册》。手册面向安全从业者、架构师、AI 治理负责人、产品安全负责人和决策者。

**仅做文档整理** — 不新增理论模型，不新增测试，不新增 corpus，不新增 run_config，不生成代码。

## 交付物

| 文件 | 内容 |
|------|------|
| `docs/ai_attack_behavior_theory_handbook.md` | 手册主文档（四部分十章） |
| `docs/ai_attack_behavior_theory_handbook_source_map.md` | 章节来源映射表 |
| `docs/ai_attack_behavior_theory_handbook_glossary.md` | 术语表（17 个核心术语） |
| `docs/ai_attack_behavior_theory_handbook_safety_semantics.md` | 安全语义声明 |
| `docs/phase85a_ai_attack_behavior_theory_handbook_notes.md` | 本说明文件 |
| `docs/phase85a_ai_attack_behavior_theory_handbook_checklist.md` | 非执行型检查清单 |
| `results/phase85a_ai_attack_behavior_theory_handbook_result.yaml` | 手册整理结果 |

## 手册结构

```
第一部分：基础框架与问题定义
  第 1 章：为什么需要 AI 攻击行为理论
  第 2 章：授权 AI 安全评估的边界

第二部分：单模块风险与能力边界
  第 3 章：AI 供应链与工具描述风险（M43）
  第 4 章：开发环境与 Coding Agent 风险（M46/M47）
  第 5 章：RAG 数据安全与权限继承风险（M48/M49）
  第 6 章：运行时沙箱与审计链路（M50）

第三部分：跨模块攻击链与系统风险动力学
  第 7 章：从单点模块到跨模块攻击图（Phase 74A/75A）
  第 8 章：攻击传播动力学与桌面推演（Phase 77A/79A/80A）
  第 9 章：攻击模式库与统一理论模型（Phase 81A/82A/83A）

第四部分：形式化系统与实践使用
  第 10 章：形式化表达、使用边界与后续路线
```

## 来源阶段

| 来源 | 覆盖 |
|------|------|
| v1.0 | Phase 6–16（评估框架与方法论） |
| v2.0 | Phase 43–50, Phase 66A–73A（六大核心模块闭环） |
| v3.0 | Phase 74A–83A（攻击图、动力学、tabletop、模式库、理论模型） |

## 确认项

| 确认项 | 状态 |
|--------|------|
| handbook_compilation_only | 通过 |
| documentation_only | 通过 |
| candidate_level_only | 通过 |
| 未新增代码 | 通过 |
| 未新增脚本 | 通过 |
| 未新增 corpus | 通过 |
| 未新增 run_config | 通过 |
| 未新增测试 | 通过 |
| 未执行 capability_engine | 通过 |
| 未生成 execution_results | 通过 |
| 未进入 controlled replay | 通过 |
| 未连接真实系统 | 通过 |
| 未声明 confirmed vulnerability | 通过 |
| 未声明 formal finding | 通过 |
| 未声明 production safety | 通过 |
| 四部分十章结构 | 通过 |
| 每章含来源映射 | 通过 |
| 每章含安全声明 | 通过 |
| 术语表存在 | 通过 |
| 安全语义声明存在 | 通过 |

## 非目标

- 不新增任何可执行代码
- 不新增任何脚本
- 不新增 Python / shell / JS / TS 脚本
- 不新增 validate 脚本
- 不新增 corpus
- 不新增 adversarial_playbook
- 不新增 run_config
- 不新增测试
- 不新增评估模块
- 不新增理论模型
- 不执行 capability_engine
- 不生成 execution_results.json
- 不执行 parser
- 不生成 capability_scorecard
- 不进入 controlled replay
- 不连接真实 MCP Server
- 不访问真实仓库
- 不读取真实文件
- 不执行真实命令
- 不读取真实凭据
- 不连接真实 RAG 系统
- 不连接真实 runtime
- 不调用真实 API
- 不生成真实 payload
- 不声明 confirmed vulnerability
- 不声明 formal finding
- 不声明 production safety

---

*Phase 85A 手册整理说明文件末端。*
