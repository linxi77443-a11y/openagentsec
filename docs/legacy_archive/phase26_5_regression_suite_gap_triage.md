# Phase 26.5 Regression Suite Gap Triage

## 1. 本阶段目标

对 Phase 26 Curated Regression Suite Builder 中 core_llm、chatbot、api 三个 suite 为 0 selected 的原因做静态排查，并输出 gap triage 结果。

## 2. Phase 26 Suite 结果摘要

| Suite | Suite Type | Selected | Excluded | Gaps |
|---|---|---|---|---|
| suite_core_llm_regression | core_llm | 0 | 3 | 0 |
| suite_chatbot_regression | chatbot | 0 | 3 | 0 |
| suite_rag_regression | rag | 8 | 6 | 0 |
| suite_agent_regression | agent | 10 | 5 | 0 |
| suite_api_regression | api | 0 | 0 | 0 |
| suite_owasp_llm_regression | owasp_llm | 32 | 0 | 3 |
| suite_owasp_agentic_regression | owasp_agentic | 15 | 0 | 5 |

## 3. 0 Selected Suite 分析

### 3.1 core_llm_regression_suite

**Source profiles**: chatbot, regression
**Required risk types**: prompt_injection, system_prompt_exposure, sensitive_disclosure, improper_output_handling, misinformation, unbounded_consumption

**排查结果**:
- Chatbot profile 有 22 个 generated testcases，但全部是 `manual_review_required`（0 个 curated_candidate）
- Regression profile 有 3 个 curated_candidate 和 6 个 manual_review_required，但 regression testcases 的 risk type（core_security_regression, generic_agent_regression, api_smoke）不匹配 core_llm 所需的 risk types
- **根因**: Chatbot profile 的 generated testcases 缺少 `fake_assets_required` 和 `assertion_strategy` 字段，导致 Phase 25 curation 标记为 manual_review_required。没有 curated_candidate 可用。

**推荐动作**: improve_assertion_strategy

### 3.2 chatbot_regression_suite

**Source profiles**: chatbot, regression
**Required risk types**: prompt_injection, system_prompt_exposure, sensitive_disclosure, multilingual_bypass, misinformation

**排查结果**:
- 与 core_llm_regression_suite 相同的根因：chatbot profile 全部 22 个 testcases 为 manual_review_required
- Regression profile 的 testcases 不匹配 chatbot 所需 risk types
- **根因**: 同上 — chatbot generated testcases 缺少 fake_assets_required 和 assertion_strategy

**推荐动作**: improve_assertion_strategy

### 3.3 api_regression_suite

**Source profiles**: api
**Required risk types**: api_security_baseline, unbounded_consumption

**排查结果**:
- API profile 在 Phase 24 生成了 0 个 testcases（`generated_api_testcases: []`）
- API 类型 corpus 在编译时被标记为 `not_executable`，因为无可用的 runner
- 即使生成了 testcases，API corpus 中有 4 条是 planned 状态（unbounded_consumption_baseline.yaml），未编译
- **根因**: API corpus 为 planned 状态且无 runner，Phase 24 编译器跳过了 API 类型

**推荐动作**: backfill_corpus_fields（先确保 API corpus 就绪，再更新 compiler）

## 4. 已知 Framework Gap 解释

### 4.1 LLM03 (Model Theft)

**排查**:
- Corpus 中 LLM03 相关条目：0 条专门针对 model theft 的语料
- RISK_TO_OWASP_LLM 映射表中没有风险类型映射到 LLM03
- **结论**: 设计上未覆盖 model theft 风险，需要新增 corpus 和 risk type 映射

**推荐动作**: accept_gap（当前无 model theft 相关语料，需从零构建）

### 4.2 LLM04 (Denial of Service)

**排查**:
- Corpus 中 resource_consumption (agent-rc-*) 和 unbounded_consumption (api-uc-*) 条目存在，但这些被映射到 LLM10
- 没有风险类型映射到 LLM04
- **结论**: DoS 相关 corpus 被归类到 LLM10 而非 LLM04

**推荐动作**: accept_gap（现有 resource_consumption 映射到 LLM10，语义更接近）

### 4.3 LLM08 (Vector & Embedding Weaknesses)

**排查**:
- Corpus 中有 vector_embedding_weaknesses 条目（4 条 planned 状态）
- Risk type `vector_embedding_weakness` 映射到 LLM06（Sensitive Information Disclosure）而非 LLM08
- **结论**: 映射表设计将 vector embedding 相关风险归入 LLM06

**推荐动作**: backfill_corpus_fields（待 vector_embedding_weaknesses 语料执行后，可调整映射或新增 LLM08 专用条目）

### 4.4 ASI01 (Unauthorized Tool/Service Access)

**排查**:
- Corpus 中 business 和 agent profile 有相关条目，但 business 条目折叠到 chatbot profile
- Agent profile 的 tool_misuse 条目映射到 ASI02，memory_poisoning 映射到 ASI06
- RISK_TO_OWASP_AGENTIC 中无映射到 ASI01 的风险类型
- **结论**: 现有 risk type 映射覆盖了 ASI02/04/06/08/09，但 ASI01 无对应

**推荐动作**: accept_gap（需要新增针对 unauthorized tool access 的 corpus 和 risk type）

### 4.5 ASI03 (Excessive Agency)

**排查**:
- Corpus 和 curation 中无专门针对 excessive agency 的条目
- RISK_TO_OWASP_AGENTIC 中无映射到 ASI03 的风险类型
- **结论**: 未覆盖 excessive agency 风险

**推荐动作**: accept_gap（需要新增 excessive agency 专项 corpus）

### 4.6 ASI05 (Insufficient Audit Trail)

**排查**:
- Corpus 和 curation 中无专门针对 audit trail 的条目
- RISK_TO_OWASP_AGENTIC 中无映射到 ASI05 的风险类型
- **结论**: 未覆盖 audit trail 风险

**推荐动作**: accept_gap（需要新增 audit trail 专项 corpus）

### 4.7 ASI07 (Supply Chain Vulnerabilities)

**排查**:
- Corpus 和 curation 中无专门针对 supply chain 的条目
- RISK_TO_OWASP_AGENTIC 中无映射到 ASI07 的风险类型
- Supply chain 相关文档在 `supply_chain/` 目录，但未被 corpus 覆盖
- **结论**: 未覆盖 supply chain 风险

**推荐动作**: accept_gap（需要新增 supply chain vulnerability 专项 corpus）

### 4.8 ASI10 (Insecure Recovery)

**排查**:
- Corpus 和 curation 中无专门针对 insecure recovery 的条目
- RISK_TO_OWASP_AGENTIC 中无映射到 ASI10 的风险类型
- **结论**: 未覆盖 insecure recovery 风险

**推荐动作**: accept_gap（需要新增 insecure recovery 专项 corpus）

## 5. 建议下一步

| 类别 | 推荐动作 | 优先级 |
|---|---|---|
| core_llm / chatbot 0 selected | Phase 27A: backfill chatbot assertion_strategy 和 fake_assets_required | 高 |
| api 0 selected | Phase 27A: 先确保 API corpus 和 runner 就绪 | 中 |
| LLM03 / LLM04 / LLM08 | accept_gap（设计上未覆盖或映射到其他类别） | 低 |
| ASI01 / ASI03 / ASI05 / ASI07 / ASI10 | accept_gap（需新增专项 corpus） | 低 |

**总体建议**: 优先进入 Phase 27A (corpus/curation backfill)，而不是 Phase 27 (validator)。在 curated_candidate 覆盖度提升后再运行 validator 更有意义。
