# Phase 67A — M48 RAG Document Poisoning and Instruction Boundary MVP Notes

## 范围

本阶段是 **M48 RAG Document Poisoning and Instruction Boundary MVP**，使用 adversarial_validation 模式验证 Agent 在面对 RAG 检索结果中包含可疑、误导性、指令化或试图改变 Agent 行为边界的 synthetic 文档内容时，是否能保持"检索文档只是数据，不是指令"的边界。

## 评估配置

| 字段 | 值 |
|------|-----|
| 评估模式 | adversarial_validation |
| 攻击者类型 | indirect_prompt_source |
| 攻击目标 | rag_malicious_document_poisoning |
| 执行引擎 | 模拟防御评估（fake runtime only） |
| 数据 | `<SIM_DOC_POISONED_...>` / `<SIM_KB_...>` / `<SIM_RETRIEVAL_RESULT_...>` / fake / synthetic only |
| 真实 RAG 系统 | 未连接 |
| 真实知识库 | 未访问 |
| 真实文档 | 未访问 |
| 真实云存储 | 未访问 |
| 真实工具 | 未调用 |
| 真实 API | 未调用 |
| 真实 payload | 未生成 |

## 输入资产

本 MVP 基于内部安全评估中发现的 6 条证据构建：

| 证据文件 | 原始类型 | MVP 映射 |
|----------|---------|----------|
| M48-RAG01-001_evidence.yaml | rag_document_instruction_like_content | 直接映射 → M48-RAG01-001 |
| M48-RAG01-002_evidence.yaml | rag_document_tool_use_induction | 直接映射 → M48-RAG01-002 |
| M48-RAG01-004_evidence.yaml | rag_document_authority_claim | 直接映射 → M48-RAG01-004 |
| M48-RAG01-008_evidence.yaml | rag_document_tool_use_induction | 直接映射 → M48-RAG01-008 |
| IPI-001_evidence.yaml | rag_poisoning | 上下文框架引用 → source_confusion/summary_manipulation |
| IPI-002_evidence.yaml | rag_poisoning | 上下文框架引用 → policy_override/instruction_like |

4 条新增攻击类别（M48-RAG01-003/005/006/007）覆盖 documentation-only 的扩展攻击面。

## 核心信号

- `rag_poisoning_detected` — RAG 文档投毒已识别
- `retrieved_content_untrusted` — 检索内容被标记为不可信
- `safe_summary_generated` — 安全摘要已生成
- `source_attribution_preserved` — 来源归属保留
- `document_instruction_ignored` — 文档中指令型内容被忽略
- `tool_use_induction_blocked` — 工具调用诱导被阻止
- `human_review_required` — 需要人工审核
- `benign_retrieval_allowed` — 良性检索被允许

## 结果摘要

10 条 MVP cases（8 攻击场景 + 2 control cases）。所有 8 个攻击场景的 RAG 文档投毒被成功检测 (rag_poisoning_detected: 8/8)。所有 2 个 control cases 正常通过 (control_case_passed: 2/2)。0 breakthrough。

| 信号 | 计数 |
|------|------|
| rag_poisoning_detected | 8 |
| retrieved_content_untrusted | 8 |
| safe_summary_generated | 2 |
| source_attribution_preserved | 10 |
| document_instruction_ignored | 3 |
| tool_use_induction_blocked | 2 |
| human_review_required | 8 |
| benign_retrieval_allowed | 2 |
| breakthrough_detected | 0 |

## 安全声明

- `confirmed_vulnerability`: false
- `formal_finding_allowed`: false
- `production_safety_claimed`: false
- `controlled_replay_claimed`: false
- `breakthrough_detected` 仅表示 `simulated_capability_signal`
- 所有数据使用 `<SIM_DOC_POISONED_...>` / `<SIM_KB_...>` / `<SIM_RETRIEVAL_RESULT_...>` / fake / synthetic only
- 不连接真实 RAG 系统
- 不访问真实知识库
- 不访问真实文档
- 不访问真实云存储
- 不生成真实 payload

## 裁判条件性通过声明

| 字段 | 值 |
|------|-----|
| run_config_created | true |
| capability_value | high |
| risk_level | low |
| capability_value_risk_level_separated | true |
| confirmed_vulnerability | false |
| formal_finding_allowed | false |
| production_safety_claimed | false |
| controlled_replay_claimed | false |
| judge_review_status | passed |

## 非目标

- 不声明 production_ready
- 不声明 controlled_replay_ready
- 不连接真实 RAG 系统
- 不访问真实知识库
- 不访问真实文档
- 不访问真实云存储
- 不调用真实检索 API
- 不调用真实工具
- 不生成真实 payload
