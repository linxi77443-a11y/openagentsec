# Phase 87B.1 — Remaining Blockers
# Non-blocking items remaining after Phase 88A archive.
---
assessment_metadata:
  phase: phase87b1
  assessment_mode: defensive_evaluation
  synthetic_only: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  controlled_replay_claimed: false

remaining_items:

  - item_id: "REM-01"
    category: "governance"
    title: "human_review 标记样式设计"
    description: "仪表盘展示层面需设计 human_review 标记样式 (图标/颜色/位置) 和 inconclusive 状态展示策略。Phase 88A 已提供 7 条 human_review 样例和 1 条 inconclusive 样例作为输入, 但展示样式未定义。"
    severity: "low"
    blocking: false
    suggested_phase: "Phase 87C"
    estimated_effort: "0.5 天"

  - item_id: "REM-02"
    category: "field_semantics"
    title: "capability_value/risk_level 前端分离验证"
    description: "Phase 87A 设计已明确 capability_value 与 risk_level 分离展示, Module Registry 中 scorecard 均同时包含两者。但前端实现尚未开始, 需在实现阶段验证分离展示不回归为合并单一分数。"
    severity: "low"
    blocking: false
    suggested_phase: "Phase 87C 或 Phase 90A"
    estimated_effort: "0.5 天"

  - item_id: "REM-03"
    category: "validation"
    title: "Phase 88A schema 验证结果复检"
    description: "建议在 Phase 87C 中再次对 Phase 88A Mock Fixture 的 schema 字段命名与前端字段映射进行一致性检查, 确保链 ID、节点 ID、状态枚举在前端渲染层面一致。"
    severity: "low"
    blocking: false
    suggested_phase: "Phase 87C"
    estimated_effort: "0.5 天"

  - item_id: "REM-04"
    category: "risk_management"
    title: "R7 数据层断言实现"
    description: "严重风险 R7 (confirmed_vulnerability 误标) 需在仪表盘数据加载层实现防御断言: 如果检测到 confirmed_vulnerability=true, 拒绝加载并显示安全边界违反标记。该风险不阻塞启动, 但需在实现阶段处理。"
    severity: "critical"
    blocking: false  # design-level action, not a start blocker
    suggested_phase: "Phase 90A (Dashboard 实现)"
    estimated_effort: "1 天"

  - item_id: "REM-05"
    category: "governance"
    title: "Phase 87C 任务单确认"
    description: "当前启动条件重新评估完成后, 需由裁判审核 Phase 87C 任务单。Phase 87C 为静态实现准备 / Mock Fixture 输入门, 不写代码、不生成图表、不执行攻击。"
    severity: "low"
    blocking: true  # blocks Phase 87C start
    suggested_phase: "裁判审核后"
    estimated_effort: "审核流程"

summary:
  total_remaining: 5
  by_severity:
    critical: 1  # REM-04 (design-level action, not blocking)
    high: 0
    medium: 0
    low: 4
  blocking_phase_87c: 1  # REM-05 (judge review)
  non_blocking: 4
