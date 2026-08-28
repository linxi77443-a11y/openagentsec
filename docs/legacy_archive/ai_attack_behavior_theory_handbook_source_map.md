# 《AI 攻击行为理论手册》— 章节来源映射表

## 用途

此表将手册每章映射到对应的来源 Phase、模块和复用文档，用于可追溯性和一致性审查。

## 第一部分：基础框架与问题定义

| 章 | 标题 | 来源 Phase | 来源模块 | 复用文档 |
|----|------|-----------|---------|---------|
| 1 | 为什么需要 AI 攻击行为理论 | v0 PRD, v1.0 PRD, Phase 6–9 | 全局 | prd_v0_2_1_capability_first.md, prd_v2_extension_addendum.md, capability_matrix_v1.md, system_overview_v1.md, atlas_owasp_coverage_matrix.md |
| 2 | 授权 AI 安全评估的边界 | Phase 6–9, Phase 10–13 | 全局 | generic_agent_assessment_methodology.md, generic_agent_attack_surface.md, generic_agent_control_checklist.md, assessment_workflow_v1.md, non_local_target_approval_checklist.md, manual_ui_assessment_workflow.md, post_task_value_review.md, phase_p0_defensive_module_review_notes.md, phase_p0_review_retest_backlog.md |

## 第二部分：单模块风险与能力边界

| 章 | 标题 | 来源 Phase | 来源模块 | 复用文档 |
|----|------|-----------|---------|---------|
| 3 | AI 供应链与工具描述风险 | Phase 14–16, v2.0 Phase 43–45 | M43 | phase14_owasp_agentic_crosswalk_review.md, phase15_evaluation_corpus_architecture_review.md, phase16_5_system_acceptance_checkpoint.md, MCP Tool Descriptor Integrity 相关 notes |
| 4 | 开发环境与 Coding Agent 风险 | v2.0 Phase 46–47, Phase 71A–72A | M46, M47 | phase72a_m46_repo_context_injection_notes.md, phase71a_m47_coding_agent_command_credential_notes.md, 各 M46/M47 评估报告 |
| 5 | RAG 数据安全与权限继承风险 | v2.0 Phase 48–49, Phase 67A–68A | M48, M49 | phase67a_m48_rag_document_poisoning_notes.md, phase68a_m49_rag_permission_audit_notes.md, 各 M48/M49 评估报告 |
| 6 | 运行时沙箱与审计链路 | v2.0 Phase 50, Phase 69A | M50 | phase69a_m50_runtime_sandbox_audit_chain_notes.md, M50 评估报告、retest 报告 |

## 第三部分：跨模块攻击链与系统风险动力学

| 章 | 标题 | 来源 Phase | 来源模块 | 复用文档 |
|----|------|-----------|---------|---------|
| 7 | 从单点模块到跨模块攻击图 | v3.0 Phase 74A–75A, 76A | M43–M50 | cross_module_attack_graph_schema.md, risk_propagation_model.md, cross_module_attack_path_catalog.md, automated_cross_module_attack_chain_explorer_design.md, automated_attack_chain_discovery_framework_design.md, automated_attack_chain_workflow_engine_design.md |
| 8 | 攻击传播动力学与桌面推演 | v3.0 Phase 77A, 78A, 79A, 80A | M43–M50 | attack_graph_dynamics_model.md, node_defense_state_evolution_model.md, attack_graph_feedback_loop_model.md, Phase 79A/80A tabletop 分析报告和 trajectory 报告 |
| 9 | 攻击模式库与统一理论模型 | v3.0 Phase 81A, 82A, 83A | M43–M50 | phase81a_cross_module_attack_pattern_library.md, cross_module_attack_pattern_index.md, cross_module_path_pattern_association_matrix.md, cross_module_module_pattern_association_matrix.md, unified_attack_intelligence_theory_model.md, attack_intelligence_model_fusion_design.md, attack_propagation_equation_design.md, attack_intelligence_weight_factor_design.md, tabletop_model_validation_calibration_method.md, Phase 83A 复核清单系列 |

## 第四部分：形式化系统与实践使用

| 章 | 标题 | 来源 Phase | 来源模块 | 复用文档 |
|----|------|-----------|---------|---------|
| 10 | 形式化表达、使用边界与后续路线 | v3.0 Phase 82A–84A（部分规划中） | M43–M50 | unified_attack_intelligence_theory_model.md（扩展至形式化集合与公理体系），Phase 83A 复核清单，各 Phase notes |

## 来源阶段总览

```yaml
source_phases_coverage:
  v1.0:
    phase_range: "Phase 6–16"
    coverage_in_handbook: "第 1–2 章"
    reuse_type: "评价框架、方法论、评估原则"
  
  v2.0:
    phase_range: "Phase 43–50, Phase 66A–73A"
    coverage_in_handbook: "第 3–6 章"
    reuse_type: "单模块评估报告、行为描述、边界定义"
  
  v3.0:
    phase_range: "Phase 74A–83A"
    coverage_in_handbook: "第 7–10 章"
    reuse_type: "攻击图、动力学、tabletop、模式库、理论模型"
  
  planned:
    phase: "Phase 84A（形式化系统）"
    coverage_in_handbook: "第 10 章（概念引用）"
    status: "pending — 尚未完成，手册仅引用概念框架"
```

## 安全语义声明

```yaml
handbook_source_map_safety_semantics:
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  candidate_level_only: true
  source_materials_are_candidate_level: true
  handbook_is_not_formal_finding_report: true
```
