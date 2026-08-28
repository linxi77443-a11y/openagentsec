# ADV-SLICE-002: 问题切片攻击模拟语料库草案 Notes

## 任务性质

- **任务类型**: corpus_draft_gate
- **评估模式**: adversarial_validation
- **覆盖状态**: corpus_draft_gate_planned（已创建 corpus draft，未推进到 simulated_mvp / multiturn_ready / execution_complete / controlled_replay_ready）
- **日期**: 2026-07-03

## 范围

- 已创建 corpus draft 结构、字段、expected_signal、control_case 和安全约束（共 8 条目）
- 仅绑定两个 playbook: DIST-001（分布式信息获取）和 CROSS-001（跨上下文边界组合）
- 所有数据使用 `<SIM_...>` 合成占位符
- **本阶段已创建 corpus draft，但仍未创建 run_config、未执行 capability_engine、未生成 execution_results、未产生 observed_signal / parser_signal / evidence_trace**（依据 v2.0 §13、v3.1 §3.2-§3.4）

## 非目标

## 非目标

- 不定义 observed_signal、observed_model_behavior、parser_signal、execution_result
- 不创建 run_config
- 不执行 capability_engine
- 不生成 execution_results.json、result.yaml、scorecard 或 runtime evidence
- 不产生 capability_value / risk_level 评分
- 不接入 production parser
- 不更新 M04/M19/M38/M39/multiturn 现有能力评估
- 不进入 controlled replay execution
- 不声明 production safety

## 交付物

| 文件路径 | 状态 | 说明 |
|---------|------|------|
| `capability_modules/adversarial/problem_slicing/adv_slice_002_problem_slicing_corpus_draft.yaml` | ✅ | Corpus 草案，8 条目（6 攻击 + 2 control），仅 DIST-001 + CROSS-001 |
| `docs/adv_slice_002_corpus_draft_notes.md` | ✅ | 本文件 |
| `scripts/validate_adv_slice_002_design_gate.py` | ✅ | 验证脚本 |

## Corpus 结构说明

```
corpus_draft_metadata
  ├── schema_references          → 引用 ADV-SLICE-001 schema / engine requirements
  ├── corpus_draft_gate_only: true
  ├── v3.1 §4 安全字段          → real_target_selection_allowed=false, red_team_engine_not_executable=true, etc.
  ├── bound_playbooks            → 仅 DIST-001 + CROSS-001
  └── 安全默认值                  → confirmed_vulnerability=false, etc.

playbook_metadata_dist          → DIST-001 元数据
dist_001_entries
  ├── A001: 客户身份信息切片（4 轮）
  ├── A002: 敏感业务数据渐进式切片（4 轮）
  ├── A003: 边界递减式切片（3 轮）
  └── C001: control case — 公开市场规模查询

playbook_metadata_cross         → CROSS-001 元数据
cross_001_entries
  ├── A001: RAG + 政策片段组合（5 轮）
  ├── A002: 跨主题 + 跨权限材料组合（4 轮）
  ├── A003: 系统提示 + 用户输入边界试探（3 轮）
  └── C001: control case — 单会话公开政策条款查询
```

## 信号使用声明

所有条目中定义的 signals 均为 **expected_signal**，不是 observed_signal / parser_signal / execution_result。
**human_review_required 在本阶段仅作为 expected_signal 出现，不是实际的 human_review_required_count**（依据攻击者视角新增章节 §7/§8）。

- DIST-001 expected_signal: `slicing_pattern_detected`、`cumulative_disclosure_blocked`、`safe_summary_generated`、`authorization_required`、`human_review_required`
- CROSS-001 expected_signal: `cross_context_composition_blocked`、`context_boundary_preserved`、`source_priority_enforced`、`permission_check_required`、`human_review_required`
- Control cases: `normal_response`

## exploit_chain_candidate / evidence_trace

本 corpus draft 不在条目中定义 exploit_chain_candidate 或 evidence_trace。这些字段由后续 capability_engine 执行阶段在 execution_results 中按 schema 规则产生。当前在条目中使用 `pre_execution_note` 占位说明。

## 安全确认

| 约束 | 状态 |
|------|------|
| confirmed_vulnerability=false | ✅ corpus_draft_metadata 强制默认值 |
| formal_finding_allowed=false | ✅ corpus_draft_metadata 强制默认值 |
| production_safety_claimed=false | ✅ corpus_draft_metadata 强制默认值 |
| 无 real payload | ✅ 全部使用 `<SIM_...>` |
| 无 run_config | ✅ 未创建 |
| 无 execution_results | ✅ 未生成 |
| 无 capability_engine 执行 | ✅ 未执行 |
