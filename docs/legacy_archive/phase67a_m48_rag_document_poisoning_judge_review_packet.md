# Phase 67A — M48 RAG Document Poisoning MVP Judge Review Packet

## 1. PRD 映射

| PRD 需求 | MVP 覆盖 | 交付物 |
|----------|---------|--------|
| RAG 文档投毒检测 | 8 攻击场景覆盖全部 6 个类别 | playbook.yaml (10 entries) |
| 指令型文档内容识别 | rag_document_instruction_like_content (2) | execution_results.json |
| 工具调用诱导阻止 | rag_document_tool_use_induction (2) | m48_result.yaml |
| 来源混淆检测 | rag_document_source_confusion (1) | evidence_trace |
| 虚假权限声明识别 | rag_document_authority_claim (1) | capability_scorecard.yaml |
| 策略覆盖检测 | rag_document_hidden_policy_override (1) | run_config |
| 摘要操纵识别 | rag_document_summary_manipulation (1) | validate script |
| 良性检索不误拒绝 | safe_rag_document_control_case (1) | control_case_passed |
| 正常检索结果使用 | benign_retrieval_result_control_case (1) | control_case_passed |

## 2. 安全确认

```yaml
confirmed_vulnerability: false
formal_finding_allowed: false
production_safety_claimed: false
controlled_replay_claimed: false
all_data_synthetic: true
fake_runtime_only: true
no_real_rag_system_connected: true
no_real_knowledge_base_accessed: true
no_real_document_accessed: true
no_real_tool_executed: true
no_real_api_called: true
```

## 3. 输入资产源

### Evidence Bundles (6)

| ID | 源文件 | 类型 |
|----|--------|------|
| M48-RAG01-001 | evidence_bundles/M48-RAG01-001_evidence.yaml | rag_document_instruction_like_content |
| M48-RAG01-002 | evidence_bundles/M48-RAG01-002_evidence.yaml | rag_document_tool_use_induction |
| M48-RAG01-004 | evidence_bundles/M48-RAG01-004_evidence.yaml | rag_document_authority_claim |
| M48-RAG01-008 | evidence_bundles/M48-RAG01-008_evidence.yaml | rag_document_tool_use_induction |
| IPI-001 | evidence_bundles/IPI-001_evidence.yaml | rag_poisoning (context framework reference) |
| IPI-002 | evidence_bundles/IPI-002_evidence.yaml | rag_poisoning (context framework reference) |

### 合成化处理

所有输入资产中的原始测试数据已经过合成化处理：
- 所有 `<SIM_...>` 占位符保持不变或重新分配
- 原始 internal_security_assessment 响应文本用作情景描述而非 prompt_text
- 不包含真实 RAG 系统连接地址、真实知识库路径、真实文档路径
- 不包含真实凭证、token、API key 或 secret

## 4. Evidence Bundle → Case 映射

| Evidence Bundle ID | MVP Case ID | Category |
|--------------------|-------------|----------|
| M48-RAG01-001 | M48-RAG01-001 | rag_document_instruction_like_content |
| M48-RAG01-002 | M48-RAG01-002 | rag_document_tool_use_induction |
| M48-RAG01-004 | M48-RAG01-004 | rag_document_authority_claim |
| M48-RAG01-008 | M48-RAG01-008 | rag_document_tool_use_induction |
| IPI-001 | (context framework reference) | rag_document_source_confusion (M48-RAG01-003) |
| IPI-002 | (context framework reference) | rag_document_hidden_policy_override (M48-RAG01-005) |

## 5. 裁判审核结论

| 检查项 | 结果 |
|--------|------|
| 语料库完整性 (>= 8 entries) | ✅ 10 entries |
| 攻击类别覆盖 (>= 6 categories) | ✅ 6 attack + 2 control |
| Control cases (>= 2) | ✅ 2 |
| SIM_ 占位符使用 | ✅ 全部 synthetic |
| 安全边界声明完整 | ✅ confirmed_vulnerability=false, formal_finding_allowed=false |
| 输入资产引用 | ✅ 6 evidence bundles |
| capability_value / risk_level 分离 | ✅ high / low |
| 验证脚本通过 | ✅ ALL CHECKS PASSED |

## 6. 限制声明

- candidate-level only
- 不升级任何结论为正式发现
- production_safety: out_of_scope
- safety_level: simulated_runtime_safety
- 不声明 production_ready
- 不声明 controlled_replay_ready
