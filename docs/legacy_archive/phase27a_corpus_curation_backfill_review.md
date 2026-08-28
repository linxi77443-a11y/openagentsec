# Phase 27A Corpus & Curation Backfill 复盘

**生成时间：** 2026-01-01T00:00:00Z

## 背景

Phase 26 (Curated Regression Suite Builder) 识别出 3 个 zero-selected suites（core_llm、chatbot、api）和 8 个 framework gaps（LLM03/04/08、ASI01/03/05/07/10）。Phase 26.5 (Regression Suite Gap Triage) 定位了根因：

1. Chatbot profile 全部 manual_review_required — 所有 22 个 chatbot 测试用例均未通过静态筛选
2. API profile 无 generated testcases — 全部标记为 planned/documentation_only
3. 8 个 framework gaps — 单值 risk type 映射无法覆盖多个 OWASP 类别

Phase 27A 通过三项 targeted 修复解决了上述问题。

## 修复概览

| 修复 | 涉及文件 | Phase 26.5 | Phase 27A |
|------|---------|-----------|-----------|
| fake_assets_required 逻辑 | curate_generated_testcases.py | 22 chatbot manual | 19 curated / 3 manual |
| API corpus 执行模式 | compile_corpus_to_testcases.py + 3 API YAML | 0 API testcases | 4 API testcases |
| Risk type 多值映射 | build_curated_regression_suites.py | 8 gaps | 1 gap (ASI07) |

## Before / After 指标

| 指标 | Phase 26.5 (Before) | Phase 27A (After) |
|------|-------------------|------------------|
| 总 generated testcases | 61 | 65 |
| curated_candidate | 32 | 59 |
| manual_review_required | 29 | 6 |
| Zero-selected suites | 3 | 0 |
| LLM framework gaps | 3 (LLM03/04/08) | 0 |
| Agentic framework gaps | 5 (ASI01/03/05/07/10) | 1 (ASI07) |
| Regression suite selected | 65 | 104 |
| Promptfoo drafts | 65 | 104 |

## 修复详情

### 1. fake_assets_required 空列表判断

**根因：** `curate_generated_testcases.py` 中使用 `bool(tc.get("fake_assets_required"))` 判断测试用例是否需要 fake assets。
当一个测试用例的 `fake_assets_required: []`（空列表）时，`bool([])` 在 Python 中返回 `False`，
导致所有 corpus 中无 fake_assets_required 的条目被误判为缺少 fake assets 信息，从而被标记为 manual_review_required。

**修复前：**
```python
has_fake_assets = bool(tc.get("fake_assets_required"))  # [] → False
```

**修复后：**
```python
has_fake_assets = tc.get("fake_assets_required") is not None  # [] → True
```

**效果：** Chatbot curated_candidate 从 0 增加到 19，仅 3 条真正的 manual_review_required 保留。

### 2. API corpus 执行模式

**根因：** 所有 API corpus 条目均标记为 `current_status: planned` 和 `current_execution_mode: documentation_only`，
compiler 跳过所有非 active 条目。此外 curator 中有 blanket exclusion `profile == "api"`。

**修复：**
- 3 个 API corpus 文件中的 4 条条目改为 `current_status: active`、`current_execution_mode: api_provider_future_or_skeleton`
- curator 中排除逻辑改为仅排除非 api_provider_future_or_skeleton 的 API 条目

**涉及 corpus 文件：**
- `corpus/api/api_security_baseline.yaml` — asb-001、asb-002
- `corpus/api/fastgpt_api_smoke.yaml` — fgs-001（同时添加 LLM07 映射）
- `corpus/api/unbounded_consumption_baseline.yaml` — uc_001（同时修复 schema）

**效果：** API generated testcases 从 0 增加到 4，curated_candidate 从 0 增加到 4。

### 3. Risk type 多值映射

**根因：** `RISK_TO_OWASP_LLM` 和 `RISK_TO_OWASP_AGENTIC` 为 `str→str` 单值映射，
一种风险类型只能映射到一个 OWASP 类别。例如 `rag_poisoning` 只映射到 LLM06，但 RAG 投毒同时属于 LLM04（Data and Model Poisoning）。

**修复前：**
```python
RISK_TO_OWASP_LLM = {
    "rag_poisoning": "LLM06",
    "vector_embedding_weakness": "LLM06",
    ...
}
```

**修复后：**
```python
RISK_TO_OWASP_LLM = {
    "rag_poisoning": ["LLM04", "LLM06"],
    "vector_embedding_weakness": ["LLM08", "LLM06"],
    ...
}
```

**新增多值映射：**
- rag_poisoning → LLM04 + LLM06
- vector_embedding_weakness → LLM08 + LLM06
- stale_or_conflicting_knowledge → LLM04 + LLM06
- skill_poisoning → LLM03 + LLM06
- exfiltration → LLM02 + LLM06
- system_prompt_exposure → LLM02 + LLM07
- fake_citation → LLM06 + LLM09
- tool_misuse → ASI01 + ASI02
- memory_poisoning → ASI03 + ASI06
- skill_poisoning → ASI04 + ASI05
- exfiltration → ASI02 + ASI09
- fake_citation → ASI10
- resource_consumption → ASI08

**效果：** LLM gaps 从 3 降为 0，Agentic gaps 从 5 降为 1（仅 ASI07 无自然映射）。

## 剩余缺口

| 类别 | 缺口 | 说明 |
|------|------|------|
| OWASP Agentic | ASI07 (Accountability & Audit) | 无风险类型可映射到审计/问责类别，需新的 corpus 条目 |

## 文件清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `scripts/curate_generated_testcases.py` | 修复 | fake_assets_required 逻辑 + API profile 排除例外 |
| `scripts/build_curated_regression_suites.py` | 修复 | 多值 risk type 映射 |
| `scripts/analyze_regression_suite_gaps.py` | 修复 | 同步 gap 列表为 0 LLM / 1 ASI07 |
| `scripts/compile_corpus_to_testcases.py` | 修复 | API 生成状态改为 api_provider_future_or_skeleton |
| `corpus/api/api_security_baseline.yaml` | 修复 | asb-001/002 改为 active |
| `corpus/api/fastgpt_api_smoke.yaml` | 修复 | fgs-001 改为 active + LLM07 映射 |
| `corpus/api/unbounded_consumption_baseline.yaml` | 修复 | uc_001 schema 修复并改为 active |
| `curation/assertion_strategy_mapping.yaml` | 新增 | 5 个风险类型断言策略映射 |

## 边界说明

- 所有 backfill 为静态修复，不运行测试、不生成 evidence。
- 所有 generated testcases 声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。
- 所有 regression suites 声明 executed=false、real_target_connected=false、usable_for_formal_finding=false。
- 所有 gap analysis 声明 executed=false、real_target_connected=false、analysis_only=true。
- 剩余 ASI07 缺口需后续 phase 补 corpus 条目和 risk type 映射。
