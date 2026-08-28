# Phase 80A — 多路径跨模块攻击链桌面推演批次

## 范围

本阶段对 Phase 75A 路径目录中的两条路径进行批次桌面推演：

| 路径 | 模块 | 层 |
|------|------|-----|
| PATH-DEV-CRED-RUNTIME-001 | M46 → M47 → M50 | development_environment → runtime_sandbox |
| PATH-RAG-RUNTIME-001 | M48 → M49 → M50 | rag_data → runtime_sandbox |

只做 tabletop exercise，只做概念性传播分析。

## 交付物

| 文件 | 内容 |
|------|------|
| `reports/phase80a_path_dev_cred_runtime_tabletop_analysis.md` | PATH-DEV-CRED-RUNTIME-001 桌面推演分析 |
| `reports/phase80a_path_dev_cred_runtime_defense_degradation_trajectory_report.md` | PATH-DEV-CRED-RUNTIME-001 防御降级轨迹 |
| `reports/phase80a_path_dev_cred_runtime_attack_evolution_trajectory_report.md` | PATH-DEV-CRED-RUNTIME-001 攻击演化轨迹 |
| `reports/phase80a_path_rag_runtime_tabletop_analysis.md` | PATH-RAG-RUNTIME-001 桌面推演分析 |
| `reports/phase80a_path_rag_runtime_defense_degradation_trajectory_report.md` | PATH-RAG-RUNTIME-001 防御降级轨迹 |
| `reports/phase80a_path_rag_runtime_attack_evolution_trajectory_report.md` | PATH-RAG-RUNTIME-001 攻击演化轨迹 |
| `reports/phase80a_multi_path_defense_degradation_comparison.md` | 横向对比报告 |
| `docs/phase80a_multi_path_tabletop_batch_notes.md` | 本说明文件 |
| `docs/phase80a_multi_path_tabletop_batch_checklist.md` | 非可执行检查清单 |
| `results/phase80a_multi_path_tabletop_batch_result.yaml` | 批次结果 |

## 确认项

| 确认项 | 状态 |
|--------|------|
| tabletop_exercise_only | 通过 |
| conceptual_analysis_only | 通过 |
| executable_code_created=false | 通过 |
| script_created=false | 通过 |
| simulator_implemented=false | 通过 |
| dynamics_engine_implemented=false | 通过 |
| explorer_implemented=false | 通过 |
| workflow_engine_implemented=false | 通过 |
| new_corpus_created=false | 通过 |
| new_run_config_created=false | 通过 |
| capability_engine_executed=false | 通过 |
| execution_results_generated=false | 通过 |
| controlled_replay_executed=false | 通过 |
| confirmed_vulnerability=false | 通过 |
| formal_finding_allowed=false | 通过 |
| production_safety_claimed=false | 通过 |

## 推演结果摘要

### PATH-DEV-CRED-RUNTIME-001
| 指标 | 值 |
|------|-----|
| 初始状态 | M46/M47/M50: stable |
| 最终状态 | M46: degraded, M47: pressured, M50: pressured |
| 轨迹等级 | partial_degradation |
| 衰减计数 | M46: 1, M47: 3, M50: 4 |
| 边界阻断点 | 3 (M47 command, M50 sandbox, M50 replay gate) |
| 差异模块 | M47 — 3 项衰减规则，结构化数组证据 |

### PATH-RAG-RUNTIME-001
| 指标 | 值 |
|------|-----|
| 初始状态 | M48/M49/M50: stable |
| 最终状态 | M48: degraded, M49: pressured, M50: pressured |
| 轨迹等级 | partial_degradation |
| 衰减计数 | M48: 1, M49: 2, M50: 4 |
| 边界阻断点 | 3 (M49 permission, M50 sandbox, M50 replay gate) |
| 差异模块 | M48 safe_summary 提供额外内容保护层 |

### 横向对比要点
- 两条路径结构相同：层内传播 → 跨层传输到 runtime_sandbox
- M47（3 衰减）比 M49（2 衰减）更厚的中间衰减层
- M46 劣化比 M48 快（M48 有 safe_summary 保护）
- RAD 路径证据格式更统一（全 entry-level boolean）
- M50 在两条路径中角色不同：dev-cred 强调审计链，RAG 强调沙箱边界

## 非目标
- 不生成任何可执行代码
- 不生成任何脚本
- 不实现 simulator/explorer/workflow engine
- 不新增 corpus/run_config
- 不执行 capability_engine
- 不生成 execution_results
- 不进入 controlled replay
- 不连接真实系统
- 不生成真实 payload
- 不声明 confirmed vulnerability
- 不声明 formal finding
- 不声明 production safety
