# Phase 24 Corpus-to-Testcase Compiler — 复盘

## 概述

Phase 24 在 Phase 23 Assessment Plan Generator 的基础上，进一步补齐"语料 → 可执行测试集"的工具链。Corpus-to-Testcase Compiler 将 `corpus/` 下的 YAML 语料自动编译为标准化测试用例和 promptfoo 兼容的测试集草案。

## 阶段输出

| 产物 | 路径 | 状态 |
|---|---|---|
| 编译器脚本 | `scripts/compile_corpus_to_testcases.py` | ✅ |
| 测试用例 Schema | `generated_testcases/generated_testcase_schema.md` | ✅ |
| Chatbot 测试用例 | `generated_testcases/chatbot/generated_chatbot_testcases.yaml` | 14 testcases / 14 promptfoo |
| RAG 测试用例 | `generated_testcases/rag/generated_rag_testcases.yaml` | 14 testcases / 14 promptfoo |
| Agent 测试用例 | `generated_testcases/agent/generated_agent_testcases.yaml` | 16 testcases / 16 promptfoo |
| API 测试用例 | `generated_testcases/api/generated_api_testcases.yaml` | 10 testcases / 0 promptfoo（not_executable） |
| Regression 测试用例 | `generated_testcases/regression/generated_regression_testcases.yaml` | 9 testcases / 9 promptfoo |
| 多维索引 | `generated_testcases/generated_testcase_index.yaml` | ✅ |
| 覆盖摘要 | `generated_testcases/generated_testcase_summary.md` | ✅ |
| Dashboard 更新 | `scripts/generate_atlas_dashboard.py` | ✅ |
| 企业报告更新 | `scripts/generate_enterprise_report.py` | ✅ |
| 发布文档更新 | `release/` 10 文件 | ✅ |
| 系统文档更新 | `docs/` 5 文件 | ✅ |
| 质量检查更新 | `runners/run_quality_check.sh` | ✅ |
| 评估计划关联 | `assessment_plans/generated/` | ✅ |
| 测试目录关联 | `test_catalog/` | ✅ |

## 编译统计

| 指标 | 数值 |
|---|---|
| 总语料数 | 93 |
| 可编译语料（active/regression） | 61 |
| 已生成测试用例 | 61 |
| Promptfoo 草稿 | 52 |
| 需人工审核 | 0 |
| 覆盖 Profile | chatbot/rag/agent/api/regression |

### 生成状态分布

- generated_draft（本地沙箱，需手动执行）：9
- promptfoo_ready（可直接导入 promptfoo）：52

## 架构说明

```
corpus/ (93 entries)
  ↓  compile_corpus_to_testcases.py
generated_testcases/
  ├── chatbot/  (14 testcases)
  ├── rag/      (14 testcases)
  ├── agent/    (16 testcases)
  ├── api/      (10 testcases, not_executable)
  ├── regression/ (9 testcases)
  ├── generated_testcase_index.yaml
  └── generated_testcase_summary.md
```

### 四层分离设计

1. **corpus/** — 原始语料层（93 条，不变）
2. **generated_testcases/** — 自动编译层（61 条，本阶段产物）
3. **curated testcases** — 人工筛选层（未来 Phase，可执行版本）
4. **evidence** — 测试证据层（未来 Phase，执行结果）

## 设计决策

### 为什么不做直接执行？

- 保持 compilation layer 的纯净职责：只编译，不执行
- 避免在未确认 target/runner/credential 的情况下自动产生误导性 evidence
- 与 Phase 23 Assessment Plan Generator 保持一致的 planning/compilation 层定位

### Profile 折叠策略

- Business 类型语料 → 折叠入 chatbot profile（业务场景本质是 chatbot 交互）
- Generic Agent 类型语料 → 保留为 agent profile（保持 agent 测试完整性）
- Workflow 类型语料 → 映射为 api profile（workflow 通常通过 API 暴露）

### 不可编译条目处理

- status=planned → 跳过（尚未准备好的语料）
- status=reference_only → 跳过（仅参考，非可执行条目）
- status=documentation_only → 跳过（仅文档说明）
- API 类型 → 标记为 not_executable（无 runner 可用）
- 缺失必要字段 → 标记 manual_review_required（本阶段为 0）

## 生成测试用例 Schema

每个 generated testcase 包含 23 个字段：

| 字段 | 说明 |
|---|---|
| generated_testcase_id | 自动生成的唯一 ID |
| source_corpus_id | 来源 corpus entry ID |
| source_corpus_file | 来源 corpus YAML 文件路径 |
| target_profile | 目标评估 profile |
| target_type | 目标类型 |
| owasp_llm_mapping | OWASP LLM Top 10 映射 |
| owasp_agentic_mapping | OWASP Agentic Top 10 映射 |
| mitre_atlas_mapping | MITRE ATLAS 映射 |
| test_intent | 测试意图 |
| input_prompt | 输入 prompt |
| context_required | 所需上下文 |
| fake_assets_required | 所需 fake 资源 |
| expected_behavior | 预期行为 |
| risk_signals | 风险信号 |
| assertion_strategy | 断言策略 |
| severity_if_failed | 失败严重性 |
| execution_mode | 执行模式 |
| runner_compatibility | 兼容 runner |
| promptfoo_compatible | 是否兼容 promptfoo |
| generated_status | 生成状态 |
| executable_now | 是否立即可执行 |
| evidence_expected | 预期证据类型 |
| limitations | 当前限制 |

## 与已有系统的关系

| 组件 | 关系 |
|---|---|
| Assessment Plan Generator | 互补：plan generator 生成评估计划，testcase compiler 生成测试用例 |
| Corpus | 上游：compiler 读取 corpus YAML 作为输入 |
| Test Catalog | 下游：generated testcases 可补充 test catalog 的测试能力 |
| Runners | 下游：generated testcases 的 promptfoo 草稿可导入 runner 执行 |

## 安全与边界

- 所有 generated testcases 声明 executed=false、real_target_connected=false、usable_for_formal_finding=false
- API 类型测试标记为 not_executable（无可用的 runner）
- 编译器不访问网络、不读取环境变量、不加载凭证
- 编译器不修改 corpus/ 下的原始语料
- Business 类型语料折叠入 chatbot Profile
- 如需从草稿升级为可执行测试，需人工确认 target、runner、credential

## 后续建议

1. **与 Runner 打通**：将 promptfoo 草稿自动导入 runner 配置，实现一键执行
2. **人工筛选工作流**：支持从 generated testcases 中人工筛选、编辑、升级为 curated testcases
3. **多语种语料编译**：支持从多语种 corpus 编译多语种 testcases
4. **智能 testcase 组合**：根据风险矩阵自动组合 testcase suite
5. **Compiler 自检**：增加 compiler 自身的完整性验证（验证输入输出一致性）
