# Phase-91A — RED-015 行动报告索引与元数据一致性清理

## 任务信息

| 字段 | 值 |
|------|-----|
| 任务编号 | Phase-91A |
| 任务类型 | registry_review_cleanup |
| 评估模式 | defensive_evaluation |
| 日期 | 2026-07-18 |

### PRD v2.0 §13 执行状态声明

| 字段 | 值 |
|------|-----|
| assessment_execution_performed | false |
| capability_engine_executed | false |
| execution_results_generated | false |
| corpus_added | false |
| run_config_added | false |

## 1. 清理范围

对 RED-015 既有行动报告资产进行只读核对，补齐 `red_team_report_index.yaml` 中缺失的索引条目。

## 2. RED-015 资产清单与核对结果

### 2.1 文件完整性

| 文件 | 存在 | 大小 | 核对 |
|------|------|------|------|
| `red_team/red_015/adversarial_playbook.yaml` | ✅ | 31872B | 36 entries (三阶段), category/expected_behavior/expected_signal/control_case 齐全 |
| `red_team/red_015/run_config.yaml` | ✅ | 2880B | chain_id=ADV-CHAIN-001, 3 stages, playbook/fixture/result 引用一致 |
| `red_team/red_015/execution_results.json` | ✅ | 31541B | 47 entries, summary 统计一致, 所有 safety 字段正确 |
| `red_team/red_015/red_015_result.yaml` | ✅ | 2073B | report_id=RED-015, chain_id=ADV-CHAIN-001, 统计与 execution_results 一致 |
| `red_team/red_015/capability_scorecard.yaml` | ✅ | 1031B | chain_level 统计一致, per_phase 3 阶段覆盖 |
| `red_team/red_015/red_team_evidence_candidates.yaml` | ✅ | 4956B | 6 evidence candidates, all finding_type=negative |
| `red_team/red_015/blue_control_candidates.yaml` | ✅ | 2843B | 4 control candidates |
| `red_team/red_015/purple_retest_candidates.yaml` | ✅ | 2115B | 4 retest candidates |
| `red_team/red_015/reused_baseline_index.yaml` | ✅ | 2393B | 5 reused baselines |
| `red_team/red_015/short_notes.md` | ✅ | 978B | 概要与统计一致 |

### 2.2 统计一致性核对

| 指标 | result.yaml | scorecard | execution_results.json | 一致性 |
|------|-------------|-----------|----------------------|--------|
| total_entries | 47 | 47 | 47 | ✅ |
| attack_entries | 29 | 29 (12+9+8) | 29 | ✅ |
| control_entries | 18 | 18 (6+6+6) | 18 | ✅ |
| blocked | 29 | 29 | 29 | ✅ |
| allowed | 18 | 18 | 18 | ✅ |
| breakthroughs | 0 | 0 | 0 | ✅ |
| errors | 0 | 0 | 0 | ✅ |

### 2.3 安全字段核对

| 字段 | 值 | 来源 | 一致 |
|------|-----|------|------|
| confirmed_vulnerability | false | result.yaml, scorecard, execution_results | ✅ |
| formal_finding_allowed | false | result.yaml, scorecard, execution_results | ✅ |
| production_safety_claimed | false | result.yaml, execution_results | ✅ |
| all_findings_are_candidate_level | true | result.yaml, scorecard, execution_results | ✅ |
| attack_execution_allowed | false | run_config, execution_results | ✅ |
| payload_generation_allowed | false | run_config, execution_results | ✅ |
| breakthrough_detected | false | result.yaml, scorecard, execution_results | ✅ |

### 2.4 路径与模块引用

RED-015 是链级评估（ADV-CHAIN-001），非单模块评估。涉及的攻击面和模块通过 reused_red_reports 引用 RED-001 至 RED-014，不独立映射到 M43-M50 的单模块 coverage。

- chain_id: ADV-CHAIN-001
- chain_stages: stage_1_reconnaissance, stage_2_exfiltration, stage_3_persistence
- reused_red_reports: RED-001 至 RED-014
- 无独立 selected_paths（链级评估不适用单路径映射）

## 3. 索引修复

### 3.1 修复前状态

- RED-015 在 `red_team_report_index.yaml` 中：**不存在**（缺失索引）
- red_team/red_015/ 目录：已存在，10 个文件完整

### 3.2 修复后状态

- RED-015 已添加到 `red_team_report_index.yaml`
- status: closed/judge_approved（原始报告已通过裁判审核）
- 14 个已有索引条目未被修改

## 4. 保持不变项

- RED-015 原始 execution_results.json 未修改
- RED-015 原始 red_015_result.yaml 未修改
- RED-015 原始 capability_scorecard.yaml 未修改
- RED-015 原始 adversarial_playbook.yaml 未修改
- RED-015 原始 red_team_evidence_candidates.yaml 未修改
- RED-015 原始 blue_control_candidates.yaml 未修改
- RED-015 原始 purple_retest_candidates.yaml 未修改
- RED-015 原始 run_config.yaml 未修改
- RED-016、RED-017 索引和资产未修改
- M43-M50 registry coverage_status 未修改
- v1.0 十类攻击剧本覆盖分母未变化

## 5. 来源报告原始值（不重评分）

> 引用来源：攻击者视角新增章节 §7、PRD v2.0 §13、PRD v3.1 §8。

| 字段 | 值 | 说明 |
|------|-----|------|
| source_report_capability_value_raw | very_strong | 历史 raw legacy value，当前四份 PRD 未注册该枚举 |
| source_report_risk_level_raw | low | 历史 raw legacy value |
| source_report_breakthrough_detected | false | 原始值保持不变 |
| source_report_results_unchanged | true | 47 条原始结果未修改 |
| capability_value_declared_by_phase | false | Phase-91A 不做重评分 |
| risk_level_declared_by_phase | false | Phase-91A 不做重评分 |
| normalization_performed | false | 不规范化 very_strong 为 high/medium/low |

## 6. 模拟红队专项安全字段

> 引用来源：原 PRD §4/§12/§16、攻击者视角新增章节 §3/§11、PRD v2.0 §4、PRD v3.1 §4/§6。

| 字段 | 值 |
|------|-----|
| attack_execution_allowed | false |
| payload_generation_allowed | false |
| real_target_selection_allowed | false |
| red_team_engine_not_executable | true |
| dashboard_not_execution_interface | true |
| confirmed_vulnerability | false |
| formal_finding_allowed | false |
| production_safety_claimed | false |
| controlled_replay_execution_allowed | false |

## 7. 非目标

- 不重新执行 capability_engine
- 不修改 RED-015 原始统计值
- 不新增红队路径或攻击剧本
- 不处理 canonical capability/risk mapping 文档债务
- 不修改 M04/M19 的 fake-runtime 深度空间描述
