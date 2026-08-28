# Phase 26 Curated Regression Suite Builder Review

## 概述

Phase 26 建立 Curated Regression Suite Builder，从 Phase 25 筛选出的 32 个 curated_candidate 中构建 7 个回归测试套件草案。

## 构建结果

| 指标 | 数值 |
|---|---|
| 总 suites | 7 |
| 总 selected testcases | 65 |
| 总 excluded | 17 |
| 总 gaps | 8 |
| Promptfoo 草稿 | 65 |

## Suite 清单

| Suite | Suite Type | Selected | Excluded | Gaps |
|---|---|---|---|---|
| suite_core_llm_regression | core_llm | 0 | 3 | 0 |
| suite_chatbot_regression | chatbot | 0 | 3 | 0 |
| suite_rag_regression | rag | 8 | 6 | 0 |
| suite_agent_regression | agent | 10 | 5 | 0 |
| suite_api_regression | api | 0 | 0 | 0 |
| suite_owasp_llm_regression | owasp_llm | 32 | 0 | 3 |
| suite_owasp_agentic_regression | owasp_agentic | 15 | 0 | 5 |

## 已知 Gaps

### OWASP LLM
- LLM03 (Model Theft): No curated_candidate with matching risk type
- LLM04 (Denial of Service): No curated_candidate with matching risk type
- LLM08 (Vector & Embedding Weaknesses): No curated_candidate with matching risk type

### OWASP Agentic
- ASI01 (Unauthorized Tool/Service Access): No curated_candidate with matching risk type
- ASI03 (Excessive Agency): No curated_candidate with matching risk type
- ASI05 (Insufficient Audit Trail): No curated_candidate with matching risk type
- ASI07 (Supply Chain Vulnerabilities): No curated_candidate with matching risk type
- ASI10 (Insecure Recovery): No curated_candidate with matching risk type

## 设计原则

- **Static suite build only**: 不运行测试，不连接真实系统。
- **仅从 curated_candidate 选择**: 不包含 manual_review_required 条目。
- **所有 suite 声明**: executed=false、real_target_connected=false、usable_for_formal_finding=false。
- **所有 promptfoo suite draft 声明**: generated_only=true、curated_from_static_analysis=true。
- **Profile 折叠**: business→chatbot、generic_agent→agent、workflow→api。
- **固定时间戳**: 2026-01-01T00:00:00Z。

## 安全边界

- Builder 不访问网络、不连接 API、不执行测试。
- 所有生成的 YAML 文件不包含真实 URL、token、email 或凭证。
- Builder 脚本只读取本地 YAML 文件，不引入外部依赖。

## 已更新的文件

- `regression_suites/` — 7 个 suite 草案 + 7 个 promptfoo 草稿 + schema + 索引 + 摘要
- `curation/` — 更新 curation_summary.md 和 runner_binding_index.yaml
- `README.md` — 添加 Phase 26 描述
- `scripts/` — 更新 dashboard/report 生成器和脚本
- `release/` — 更新所有发布文档
- `runners/run_quality_check.sh` — 添加 Phase 26 检查
- `docs/` — 本文件

## 后续步骤

1. 人工复核后，可将 curated_draft 升级为 ready_for_dry_run_later
2. 配置 runner 后执行 dry-run
3. 确认稳定后升级为 formal regression execution
4. 补充 LLM03、LLM04、LLM08、ASI01、ASI03、ASI05、ASI07、ASI10 的 curated_candidate
