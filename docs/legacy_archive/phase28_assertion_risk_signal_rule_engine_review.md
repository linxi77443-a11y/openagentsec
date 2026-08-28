# Phase 28 Assertion & Risk Signal Rule Engine 复盘

**生成时间：** 2026-01-01T00:00:00Z

## 本阶段目标

建立 Assertion & Risk Signal Rule Engine，把 corpus、generated_testcases、curation、regression_suites 中分散的 risk_signals、expected_behavior、assertion_strategy、severity_if_failed 统一到 `rules/` 规则库，并提供静态规则校验脚本。

本阶段不运行测试，不运行 promptfoo，不连接真实系统，不生成 evidence。

## 新增文件

| 文件 | 说明 |
|------|------|
| `rules/README.md` | rules 目录说明 |
| `rules/assertion_rule_schema.md` | Assertion rule schema 定义 |
| `rules/risk_signal_rule_catalog.yaml` | 风险信号规则目录（24 种 risk_type） |
| `rules/expected_behavior_rule_catalog.yaml` | 预期行为规则目录（15 种 behavior） |
| `rules/owasp_llm_assertion_mapping.yaml` | OWASP LLM Top 10 → assertion rules |
| `rules/owasp_agentic_assertion_mapping.yaml` | OWASP Agentic Top 10 → assertion rules |
| `rules/atlas_assertion_mapping.yaml` | MITRE ATLAS → assertion rules（21 techniques） |
| `rules/severity_rule_mapping.yaml` | 规则失败 → 严重性建议 |
| `rules/rule_engine_boundary.md` | 规则引擎边界声明 |
| `rules/rule_coverage_report.yaml` | 规则覆盖报告 |
| `rules/rule_coverage_report.md` | 规则覆盖报告 Markdown |
| `scripts/validate_assertion_rules.py` | 规则校验脚本 |
| `docs/phase28_assertion_risk_signal_rule_engine_review.md` | 本复盘文档 |

## Assertion Rule Schema 摘要

- rule_type 可取 9 种：refusal_check / leakage_check / tool_use_check / memory_write_check / citation_check / output_safety_check / resource_use_check / schema_check / manual_review_only
- current_support 可取 5 种：supported_static_rule / supported_pattern_rule / manual_review_required / planned / not_supported_for_now
- 每个 rule 包含 20+ 字段覆盖风险信号、预期行为、framework 映射、严重性、误报/漏报风险

## Risk Signal Rule Catalog 摘要

- **24 种 risk_type** 全部覆盖
- 每项包含 common_signals、safe_indicators、risky_indicators、automation_feasibility、framework 映射、建议断言策略
- ASI07 accountability_audit_gap 标记为 planned
- misinformation / hallucination / fake_citation 标记为 manual_review_required

## Expected Behavior Rule Catalog 摘要

- **15 种预期行为**：
  should_refuse / should_answer_safely / should_not_reveal_system_prompt / should_not_leak_sensitive_data / should_not_follow_document_instruction / should_not_call_unauthorized_tool / should_not_execute_write_action / should_require_human_confirmation / should_not_write_memory / should_not_modify_skill / should_not_exfiltrate / should_cite_sources / should_flag_uncertainty / should_limit_resource_usage / should_log_or_audit_action
- 每项包含 applicable_profiles、assertion_strategy、automation_feasibility、current_support

## OWASP LLM Assertion Mapping 摘要

| Risk ID | current_support | manual_review |
|---------|----------------|---------------|
| LLM01 | supported_static_rule | false |
| LLM02 | supported_static_rule | false |
| LLM03 | manual_review_required | true |
| LLM04 | supported_pattern_rule | true |
| LLM05 | manual_review_required | false |
| LLM06 | supported_static_rule | false |
| LLM07 | supported_static_rule | false |
| LLM08 | manual_review_required | true |
| LLM09 | manual_review_required | true |
| LLM10 | manual_review_required | true |

## OWASP Agentic Assertion Mapping 摘要

| Risk ID | current_support | rules | manual_review |
|---------|----------------|-------|---------------|
| ASI01 | supported_static_rule | ✅ | false |
| ASI02 | supported_static_rule | ✅ | false |
| ASI03 | supported_static_rule | ✅ | false |
| ASI04 | supported_pattern_rule | ✅ | true |
| ASI05 | not_supported_for_now | ❌ | true |
| ASI06 | supported_pattern_rule | ✅ | false |
| ASI07 | planned | ❌ | true |
| ASI08 | supported_pattern_rule | ✅ | false |
| ASI09 | supported_static_rule | ✅ | false |
| ASI10 | planned | ❌ | true |

## ATLAS Assertion Mapping 摘要

- 21 个 ATLAS techniques mapped
- 覆盖 Execution / Defense Evasion / Exfiltration / Persistence / Credential Access / Collection / Impact 战术
- atlas.denial_of_service 包含在映射中（已知的不在 coverage 矩阵中的遗留问题）
- atlas.real_toolchain_attack / model_extraction / membership_inference / training_data_poisoning 标记为 not_supported_for_now / planned

## Severity Rule Mapping 摘要

- 24 种 risk_type 全部有 severity mapping
- 默认严重性范围：Informational ~ Critical
- 包含 escalation / reduction factors
- 与 red_team/finding_severity_model.md 对齐

## ASI07 Gap 处理

- 在 owasp_agentic_assertion_mapping.yaml 中明确记录
- current_support: planned
- 对应的 risk_type: accountability_audit_gap 标记为 planned
- 对应的 expected behavior: should_log_or_audit_action 标记为 planned
- 与 Phase 27 一致，不作为 gap failure

## Rule Validation Script 摘要

脚本 `scripts/validate_assertion_rules.py` 执行：

1. OWASP LLM 映射校验：10/10 risks mapped
2. OWASP Agentic 映射校验：10/10 risks mapped（ASI05/ASI07/ASI10 标记 gap）
3. Severity 映射校验：24/24 risk types mapped
4. Risk type coverage 校验：全部有 expected behavior 或 manual_review_required
5. Regression suite 引用校验
6. ATLAS mapping 校验
7. Automation claim 校验：不把 manual_review_required 误标为 fully automated

## Rule Coverage Report 结果

| 检查项 | 结果 |
|--------|------|
| OWASP LLM assertion mapping | ✅ PASS |
| OWASP Agentic assertion mapping | ✅ PASS |
| Severity mapping | ✅ PASS |
| Risk type coverage | ✅ PASS |
| Suite references | ✅ PASS |
| ATLAS mapping | ✅ PASS |
| ASI07 gap 处理 | ✅ Documented |
| False automation claims | ✅ None detected |

## Dashboard / Report 更新

- Dashboard 新增 Assertion & Risk Signal Rule Engine 区块
- Enterprise Report 新增 Phase 28 章节
- 明确声明 tests_executed=false、real_target_connected=false、evidence_generated=false

## Quality Check 结果

Phase 28 新增 20 项检查：

1. rules/ 目录存在
2-9. 所有 rules/ 核心文件存在
10. scripts/validate_assertion_rules.py 存在
11-12. rule_coverage_report.yaml / .md 存在
13-15. coverage report 声明 tests_executed/promptfoo_executed/real_target_connected=false
16-18. rules 不含真实 URL / token / email
19-20. dashboard/report 不声称 rule engine 执行了测试或生成真实 finding

## 当前限制

- 规则引擎是静态规则层，不执行判断
- Pattern-based assertion 可能误报或漏报
- Semantic review 需要人工复核
- ASI05 not_supported_for_now（需要真实代码执行环境）
- ASI07 planned（需要多 Agent 编排模拟）
- ASI10 planned（需要自主 Agent 漂移模拟）
- misinformation / hallucination / fake_citation 主要依赖人工复核

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
| 生成 real finding | ❌ 未生成 |
| 修改 Phase 16.5 执行统计 | ❌ 未修改 |

## 下一阶段建议

1. **Phase 29**: Rule Engine Runner Integration — 将 assertion rules 集成到 promptfoo assert 配置
2. **Phase 30**: ASI05 Code Execution Mock Environment — 建立安全的 mock 代码执行测试环境
3. **Phase 31**: ASI07 Multi-Agent Simulation — 多 Agent 编排模拟
4. **Phase 32**: Automated Severity Assessment — 基于 severity mapping 实现自动严重性建议
