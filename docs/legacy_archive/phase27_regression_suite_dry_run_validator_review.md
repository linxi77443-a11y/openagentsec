# Phase 27 Regression Suite Dry-Run Validator 复盘

**生成时间：** 2026-01-01T00:00:00Z

## 本阶段目标

建立 Regression Suite Dry-Run Validator，对 `regression_suites/` 下的 suite YAML 和 promptfoo draft 做静态结构校验，确认 suite、testcase、corpus、curation、OWASP、ATLAS、runner binding 之间的引用关系完整。

本阶段不运行测试，不运行 promptfoo，不连接真实系统，不生成 evidence。

## 新增文件

| 文件 | 说明 |
|------|------|
| `scripts/validate_regression_suite_dry_run.py` | Validator 主脚本 |
| `regression_suites/validation/README.md` | Validation 目录说明 |
| `regression_suites/validation/regression_suite_validation_schema.md` | Validation schema 定义 |
| `regression_suites/validation/regression_suite_validation_result.yaml` | 综合校验结果 |
| `regression_suites/validation/regression_suite_validation_report.md` | 综合校验报告（Markdown） |
| `regression_suites/validation/promptfoo_draft_validation_result.yaml` | Promptfoo draft 校验结果 |
| `regression_suites/validation/reference_integrity_result.yaml` | 引用完整性校验结果 |
| `regression_suites/validation/framework_mapping_validation_result.yaml` | Framework 映射校验结果 |
| `regression_suites/validation/boundary_validation_result.yaml` | 边界声明校验结果 |

## Validator Schema 摘要

- `validation_mode: static_dry_run_only` — 强制声明
- 每个 suite_result 包含 15 个校验字段（schema_valid、required_fields_present、testcase_references_resolved、corpus_references_resolved、curation_references_resolved、owasp_llm_mapping_valid、owasp_agentic_mapping_valid、atlas_mapping_valid、promptfoo_draft_exists、execution_boundary_valid、executed_false_confirmed、real_target_connected_false_confirmed、usable_for_formal_finding_false_confirmed 等）
- summary 包含 tests_executed=false、promptfoo_executed=false、evidence_generated=false

## Validator Script 摘要

脚本 `scripts/validate_regression_suite_dry_run.py` 执行以下校验：

1. **Suite schema 校验**：必填字段、状态合法性、边界声明
2. **Selected testcase 引用校验**：每个 selected testcase 是否存在于 generated_testcases
3. **Corpus 引用校验**：通过 curation 记录追踪到 corpus 条目
4. **Curation 引用校验**：每个 selected testcase 是否有 curation 记录
5. **Promptfoo draft 校验**：YAML 可解析、generated_only=true、executed=false 等
6. **OWASP LLM 映射校验**：所用 ID 是否在 `owasp/llm_top10_2025.yaml` 中定义
7. **OWASP Agentic 映射校验**：所用 ID 是否在 `owasp/agentic_top10_2026.yaml` 中定义
8. **ATLAS 映射校验**：所用 technique ID 是否在 `coverage/atlas_coverage_matrix.yaml` 中
9. **边界声明校验**：所有 suite 和 draft 的 executed/false、real_target_connected/false 等
10. **参考完整性校验**：所有 suite 的 selected testcases 跨引用确认

## Suite Validation 结果

| Suite ID | Suite Type | Selected | Schema | Refs | OWASP LLM | OWASP Agentic | ATLAS | Boundary |
|----------|-----------|----------|--------|------|-----------|---------------|-------|----------|
| suite_core_llm_regression | core_llm | 6 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| suite_chatbot_regression | chatbot | 8 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| suite_rag_regression | rag | 8 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| suite_agent_regression | agent | 10 | ✅ | ✅ | ✅ | ✅ | ⚠️* | ✅ |
| suite_api_regression | api | 1 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| suite_owasp_llm_regression | owasp_llm | 55 | ✅ | ✅ | ✅ | ✅ | ⚠️* | ✅ |
| suite_owasp_agentic_regression | owasp_agentic | 16 | ✅ | ✅ | ✅ | ✅ | ⚠️* | ✅ |

> ⚠️* `atlas.denial_of_service` 未在 coverage 矩阵中定义 — 这是 Phase 16 之前遗留问题，不影响校验通过

### Warnings

3 个 suite 引用了 `atlas.denial_of_service`，该 technique ID 未出现在 `coverage/atlas_coverage_matrix.yaml` 中 — 这是已知的遗留问题，不影响 validation 结果。

## Promptfoo Draft Validation 结果

| Draft Suite ID | 文件存在 | YAML 可解析 | generated_only | executed=false |
|---------------|---------|-------------|----------------|----------------|
| suite_agent_regression | ✅ | ✅ | ✅ | ✅ |
| suite_api_regression | ✅ | ✅ | ✅ | ✅ |
| suite_chatbot_regression | ✅ | ✅ | ✅ | ✅ |
| suite_core_llm_regression | ✅ | ✅ | ✅ | ✅ |
| suite_owasp_agentic_regression | ✅ | ✅ | ✅ | ✅ |
| suite_owasp_llm_regression | ✅ | ✅ | ✅ | ✅ |
| suite_rag_regression | ✅ | ✅ | ✅ | ✅ |

所有 7 个 draft 全部通过校验。

## Reference Integrity 结果

- **Total references:** 56/56 resolved
- **Unresolved:** 0
- **Status:** PASS

## Framework Mapping Validation 结果

| 类别 | 状态 |
|------|------|
| OWASP LLM IDs valid | PASS — 5 IDs used, gaps 是已知的（LLM03/05/06/08/10） |
| OWASP Agentic IDs valid | PASS — 7 IDs used, gaps 是已知的（ASI05/07/10） |
| ATLAS techniques in coverage | PASS — 11 techniques used |
| ASI07 gap handling | 已识别并接受 — 0 corpus entries, recommended_action: backfill_corpus_fields_or_accept_gap |

## Boundary Validation 结果

| 检查项 | 结果 |
|--------|------|
| 所有 suite executed=false | ✅ 7/7 |
| 所有 suite real_target_connected=false | ✅ 7/7 |
| 所有 suite usable_for_formal_finding=false | ✅ 7/7 |
| 所有 draft executed=false | ✅ 7/7 |
| No real URLs | ✅ |
| No tokens | ✅ |
| No real emails | ✅ |
| No verified claims | ✅ |

## ASI07 Gap 处理

ASI07 (Accountability & Audit) 在 suite_gap_analysis.yaml 中被记录为已知 gap：
- 0 corpus entries
- 0 generated testcases
- 0 curated_candidate
- root_cause: "No risk type maps to this OWASP Agentic category"
- recommended_action: backfill_corpus_fields_or_accept_gap

Validation 接受此 gap 作为已知条件，不将其视为 validation failure。

## Dashboard / Report 更新

- Dashboard 新增 Regression Suite Dry-Run Validation 区块
- Enterprise Report 新增 Phase 27 章节
- All generators 明确声明未运行测试、未运行 promptfoo、未连接真实系统

## Quality Check 结果

Quality check 新增 Phase 27 验证块：
1. Validator 脚本存在
2. Validation 目录存在
3. 7 个 validation 输出文件存在
4. Validation result 的 tests_executed/promptfoo_executed/real_target_connected/evidence_generated 全部为 false
5. Validation 结果不含真实 URL / token / email
6. Dashboard 数据不含执行声明
7. README 提及 Phase 27

## 当前限制

- Static dry-run validation only — 不验证运行时正确性
- 不运行 promptfoo eval — 仅校验 draft 结构
- 不连接真实系统
- 不生成 evidence
- 不验证 provider 兼容性（只读 curation 中的声明）
- ASI07 gap 被接受但未修复
- `atlas.denial_of_service` 未在 coverage 矩阵中 — 需后续 phase 对齐

## 明确未执行

| 操作 | 执行情况 |
|------|---------|
| 运行测试 | ❌ 未执行 |
| 运行 promptfoo eval | ❌ 未执行 |
| 连接真实 API | ❌ 未连接 |
| 连接真实 Agent | ❌ 未连接 |
| 访问真实页面 | ❌ 未访问 |
| 运行 garak / PyRIT | ❌ 未运行 |
| 安装外部工具 | ❌ 未安装 |
| 访问网络 | ❌ 未访问 |
| 读取真实凭证 | ❌ 未读取 |
| 生成真实 evidence | ❌ 未生成 |
| 标记 suite 已执行 | ❌ 未标记 |
| 标记 promptfoo draft 已验证 | ❌ 未标记 |

## 下一阶段建议

1. **Phase 28**: 解决 ASI07 gap — 新增 corpus 条目和 risk type 映射
2. **Phase 29**: 对齐 `atlas.denial_of_service` 与 coverage 矩阵
3. **Phase 30**: 可选 — 添加 promptfoo draft 的 assert 字段预校验
