# Phase 25 Generated Testcase Curation & Runner Binding — 复盘

## 概述

Phase 25 在 Phase 24 Corpus-to-Testcase Compiler 的基础上，建立 Generated Testcase Curation & Runner Binding 层。对 61 个 generated testcases 进行静态分类，分为 curated_candidate（32）和 manual_review_required（29），并建立 5 个 runner binding 草案。

## 阶段输出

| 产物 | 路径 | 状态 |
|---|---|---|
| Curation Schema | `curation/generated_testcase_curation_schema.md` | ✅ |
| Curation Result | `curation/generated_testcase_curation_result.yaml` | ✅（61 entries） |
| Curation Summary | `curation/curation_summary.md` | ✅ |
| Runner Binding Schema | `curation/runner_binding_schema.md` | ✅ |
| Runner Binding Index | `curation/runner_binding_index.yaml` | ✅（5 bindings） |
| Assertion Strategy Mapping | `curation/assertion_strategy_mapping.yaml` | ✅（16 risk types） |
| Manual Review Checklist | `curation/manual_review_checklist.md` | ✅ |
| Curation Script | `scripts/curate_generated_testcases.py` | ✅ |
| Generated Testcase 更新 | `generated_testcases/` | ✅ |
| Assessment Plan 更新 | `assessment_plans/generated/` | ✅ |
| Dashboard 更新 | `scripts/generate_atlas_dashboard.py` | ✅ |
| 企业报告更新 | `scripts/generate_enterprise_report.py` | ✅ |
| 发布文档更新 | `release/` 10 文件 | ✅ |
| 系统文档更新 | `docs/` 5 文件 | ✅ |
| 质量检查更新 | `runners/run_quality_check.sh` | ✅ |
| Phase 25 复盘 | 本文件 | ✅ |

## Curation 统计

| 指标 | 数值 |
|---|---|
| 总 generated testcases | 61 |
| curated_candidate | 32 |
| manual_review_required | 29 |
| planned_only | 0 |
| not_executable | 0 |
| duplicate_or_low_value | 0 |
| Runner binding 草案 | 5 |

### 分类规则

**curated_candidate（32）**：通过静态筛选的测试用例。特征：
- source corpus 是 active 或 regression
- 有 input_prompt、expected_behavior、risk_signals
- 有至少一个 OWASP 或 ATLAS 框架映射
- 不依赖真实 API、真实页面、真实工具
- 断言质量 clear，provider 兼容

**manual_review_required（29）**：需要人工复核的测试用例。特征：
- 缺少 assertion_strategy
- 缺少 fake_assets_required
- risk_signals 不完整
- runner_compatibility 不明确
- 预期行为缺少具体检查标志

## Runner Binding 草案

| Binding | Profile | Runner | Status |
|---|---|---|---|
| chatbot_generated_binding | chatbot | run_promptfoo.sh --profile chatbot | binding_draft |
| rag_generated_binding | rag | run_rag_promptfoo.sh --profile rag | binding_draft |
| agent_generated_binding | agent | run_agent_promptfoo.sh --profile agent | binding_draft |
| api_generated_binding | api | not_available | planned |
| regression_generated_binding | regression | run_promptfoo.sh --profile chatbot | binding_draft |

## Assertion Strategy Mapping

覆盖 16 种风险类型的断言策略映射：
- 7 种完全支持（local_sandbox）：prompt_injection、system_prompt_exposure、sensitive_disclosure、improper_output_handling、tool_misuse、memory_poisoning、skill_poisoning、exfiltration、resource_consumption
- 7 种部分支持（需人工复核）：misinformation、rag_poisoning、vector_embedding_weakness、fake_citation、stale_knowledge、unbounded_consumption、indirect_prompt_injection

## 架构说明

```
corpus/ (93 entries)
  ↓  compile_corpus_to_testcases.py (Phase 24)
generated_testcases/ (61 drafts)
  ↓  curate_generated_testcases.py (Phase 25)
curation/
  ├── curation_result.yaml (32 curated + 29 manual_review)
  ├── runner_binding_index.yaml (5 bindings)
  ├── assertion_strategy_mapping.yaml (16 risk types)
  └── manual_review_checklist.md
```

### 三层分离设计

1. **generated_testcases/** — 自动编译层（Phase 24，61 条草案）
2. **curation/** — 静态筛选层（Phase 25，本阶段产物）
3. **curated testcases** — 人工确认层（未来 Phase）

## 设计决策

### 为什么不做自动筛选到可执行？

- 保持 curation 层的纯净职责：只做静态分类，不做执行决策
- 29 条 manual_review_required 的测试用例需要人工判断，不能自动升级
- Runner binding 为草案建议，需要人工确认 provider 和 runner 配置

### 为什么有些测试用例是 manual_review_required？

主要原因：
1. **缺少 assertion_strategy**：编译器未自动生成断言策略，需要人工补充
2. **缺少 fake_assets_required**：agent 和部分 rag 测试需要指定 fake asset
3. **预期行为缺少具体检查标志**：部分 expected_behavior 是自由文本而非结构化字段
4. **runner_compatibility 不明确**：business 类型语料折叠到 chatbot，runner 选择不明确

### Runner binding 为什么 allowed_now=false？

- Provider 配置需要人工确认
- Fake assets 需要确认就绪
- Promptfoo 草稿需要验证
- 不跳过人工审核环节

## 安全与边界

- Curation 是静态分类，不运行任何测试
- Runner binding 是草案建议，不代表 runner 已验证通过
- 所有 curation 结果声明 executed=false、real_target_connected=false、usable_for_formal_finding=false
- 所有 runner binding 中 allowed_now=false
- Curation 脚本不访问网络、不读取环境变量、不加载凭证
- Curation 脚本不修改 corpus/、generated_testcases/、assessment_plans/ 下的原始文件
- 如需升级到可执行测试，需人工确认 target、runner、credential

## 后续建议

1. **人工复核工作流**：建立 manual_review_required 测试用例的复核流程，逐步升级为 curated_candidate
2. **Runner 验证**：为 binding_draft 状态的 runner binding 建立 dry-run 验证流程
3. **Assertion 补全**：自动生成默认 assertion 策略，减少 manual_review_required 数量
4. **Fake asset 管理**：建立 fake asset 目录，为每个 profile 提供标准 fake asset 集合
5. **Curation 自动回归**：每次 compile_corpus_to_testcases.py 运行后自动触发 curation
