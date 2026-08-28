# Phase 36A.0: Reference Architecture Spike

## 1. Core Objects Capability Run Engine Should Have

| Object | Responsibility | Inspired By |
|--------|---------------|-------------|
| `RunConfig` | 描述一次完整评估：目标、模块、语料、执行参数 | promptfoo config |
| `CorpusLoader` | 加载语料，按模块划分，支持 budget 截断 | Inspect Dataset |
| `Provider` | 统一的 API 调用接口（fastgpt / openai / 后续补充） | promptfoo provider / Inspect solver |
| `ExecutionResult` | 单次请求的原始证据：prompt、response、signals、timing | Inspect TaskState |
| `SignalDetector` | 按模块规则检测响应中的安全信号 | Inspect scorer |
| `Scorer` | 综合多个 execution results 计算 capability value | Inspect scorer / AgentDojo utility+security |
| `Scorecard` | 结构化评估结果：per-module 统计 + overall value | Inspect Eval Log |
| `Trace` | 完整的调用轨迹：每个请求的前后状态、信号触发点 | AgentDojo tool call trajectory |

**当前状态**: Phase 36A 已实现 Provider（简化版）、SignalDetector、Scorer、Scorecard。缺少明确的 ExecutionResult 对象（目前用 dict）和 Trace。

## 2. `capability_run_config` 应该包含的字段

当前 schema 已覆盖基本需求。从参考框架看，需要补充：

| 新增字段 | 理由 | 参考来源 |
|---------|------|---------|
| `modules[n].techniques` | 可选的按模块细粒度选择 technique | Inspect Task 的 solver 列表 |
| `execution.concurrency` | 后续支持并发请求（当前顺序足够） | Inspect eval() 的并行能力 |
| `execution.retry` | 失败重试策略 | promptfoo 的 retries |
| `scoring` | 评分策略配置（metric、threshold） | Inspect scorer / AgentDojo dual score |
| `logging.detail` | trace / raw / summary 三级 | Inspect Eval Log |

**决策**: 以上字段 Phase 36A 不做，留到 Phase 36B+。当前 schema 足够 MVP。

## 3. Runner / Parser / Scorer 拆分职责

| 组件 | 职责 | 输出 |
|------|------|------|
| **Runner** (`run_capability_eval.py`) | 读 config → 加载语料 → 解析 env → 调用 API → 保存 raw | `execution_results.json` |
| **Parser** (`parse_capability_results.py`) | 读 raw → 检测信号 → 统计 per-module → 生成 module_result | `*_result.yaml`, `capability_scorecard.yaml` |
| **Scorer**（待分离） | 读 module_result → 计算 capability value → 生成 formal finding 决策 | 评分报告 |

**当前状态**: Parser 内部已经包含信号检测 + 评分逻辑。Phase 36B 应考虑将 scorer 独立为 `evaluate_capability.py`，使 parser 只负责信号提取。这样可以：
- 替换 scorer 策略不改 parser
- 对不同模块使用不同评分权重
- 支持 AgentDojo 式的 utility / security 双评分

## 4. Raw Evidence / Trace / Scorecard 保存策略

| 产物 | 内容 | 格式 | 保存位置 |
|------|------|------|---------|
| **Raw Evidence** | 原始请求/响应（含 API key 排除） | JSON | `executions/{run_id}/execution_results.json` |
| **Module Result** | 每个 module 的信号统计 + technique 分析 | YAML | `executions/{run_id}/{module_id}_result.yaml` |
| **Scorecard** | overall capability value + summary | YAML | `executions/{run_id}/capability_scorecard.yaml` |
| **Trace** (待加) | 按执行顺序排列的完整调用链 | JSON/JSONL | `executions/{run_id}/trace.jsonl` |

**原则**:
- Raw evidence 是唯一源头，module result 和 scorecard 可从中重建
- YAML 用于人工阅读，JSON 用于程序处理
- Trace 目前没有但应预留。Trace 与 raw evidence 不同：Trace 记录的是每个请求"为什么发、用什么 technique、收到什么信号、下一步决策"，而 raw evidence 只记录请求和响应。MVP 阶段 raw evidence 足够。

## 5. 借鉴 Inspect AI

1. **Solver chain 概念**: 当前 runner 只有 "send prompt → get response"。可以借鉴 Inspect 的 `chain(generate(), self_critique(), ...)` 实现多步评估流程，比如针对 M04 agent 场景需要 tool call 解析。

2. **Scorer 与 metric 分离**: Inspect 的 `@scorer(metrics=[accuracy()])` 模式好——score 是单次评价，metric 是整体聚合。当前实现混在一起（`assess_capability_value()` 同时负责评分和聚合）。

3. **Eval log 结构**: Inspect 保存每个 sample 的完整 state（input, output, score, metadata）。当前 `execution_results.json` 已经接近，但缺少标准化的 `TaskState` 对象。

## 6. 借鉴 AgentDojo

1. **Utility / Security 双评分**: 当前只计算 "capability value"（安全维度）。对于需要区分"模型能力"和"安全防护"的场景（如 M04 agent 场景），应该拆分为：
   - `utility_score`: 模型是否理解指令、能否执行任务
   - `security_score`: 安全防护是否生效
   - 当前 M01/M02/M03 场景 capability value 实际是 security_score，utility 隐含在 "error" 判断中

2. **Tool call trajectory 记录**: 当前只记录 prompt → response。对于 agent 场景（M04+），需要记录 tool 调用链、中间状态。Phase 36A 不涉及，但 runner 架构应预留 `tool_trajectory` 字段。

3. **Attack / Defense 分层**: AgentDojo 将 attack 和 defense 作为独立维度。当前我们按 module 区分攻击类型（M01 injection / M02 leak / M03 RAG），但没有显式的 attack-defender 模型。后续可考虑：`attack_surface`（哪个模块）+ `defense_boundary`（哪个防护层被绕过）的拆解。

## 7. 复用 promptfoo

1. **配置化执行**: 当前的 `capability_run.schema.yaml` 设计已经参考 promptfoo 的配置模式。promptfoo 的 `prompts` + `providers` + `tests` 三元组对应我们的 `corpus_reference` + `target_profile` + `modules`。

2. **Provider 抽象接口**: promptfoo 的 `ApiProvider` interface (id, callApi) 是好的参考。当前 runner 的 `call_api()` 函数已按 api_type 分支，但不够抽象——添加新 API 类型需要修改 if/else。可以提取 `BaseProvider` 类。

3. **Assertion 系统**: promptfoo 的 assertion 类型丰富（deterministic / model-graded / custom）。当前 `detect_signals()` 只做 keyword matching（等于 promptfoo 的 `contains`）。后续可扩展为：
   - `contains` = 当前 keyword 检测
   - `llm-rubric` = 用 judge model 评估（DeepSeek Judge）
   - `python` = 自定义信号检测函数

4. **Default test 机制**: promptfoo 的 `defaultTest` 可以统一设置 assertion / options。我们也可以引入 `module_defaults`，避免每个 module 重复配置。

## 8. 本阶段明确不做

1. **Trace / JSONL**: raw evidence 足够当前复用。Trace 格式待定。
2. **并发请求**: 当前顺序调用 + rate limiting 足够。后续需要时加 concurrency。
3. **Scorer 独立模块**: 当前 scorer 在 parser 内部。Phase 36B 分离。
4. **Utility / Security 双评分**: 当前只计算 capability value（安全维度）。后续 agent 场景引入。
5. **Provider 抽象类**: 当前 `if api_type == "fastgpt"` 分支足够。添加新类型时提取。
6. **LLM-assisted 评分**: 当前 keyword-based 信号检测足够准确。后续 M04+ 引入 DeepSeek Judge。
7. **失败重试**: 当前 120s timeout + 无重试。MVP 阶段 48/48 成功率证明不需要。
8. **Assertion 系统扩展**: 当前 module 特定 keyword 列表 + `detect_signals()` 函数足够。

## 决策记录

- **保留 Phase 36A 当前结构不变**。所有 MVP 文件已就位，架构设计经参考验证没有根本性问题。
- **Phase 36B** 主要做 scorer 独立 + trace 格式 + 单 module run config 支持。
- **Phase 36C** 扩展 provider 抽象 + 并发执行 + LLM-assisted 评分。
