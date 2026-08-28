# Mimo Code + Qoder/DeepSeek 分级审核工作流

## 当前范围与角色

本目录提供工作流角色指令、机器可读数据契约、状态模板和工作流调度器 V0.2。V0.2 保留 V0.1.5 的 1–10 项任务状态机、机器结果受控纠正和 Validator runner 缺陷重跑能力，并增加单任务串行 Agent CLI Adapter、日志捕获及成功后的自动 ingest。每次 Agent 启动仍要求用户显式 `--approve`，一次完成后停在下一 Agent 确认点；不实现自动下一轮循环。

```yaml
planner: mimo_code
developer: mimo_code
patch_executor: mimo_code
independent_reviewer: qoder_deepseek
orchestrator_developer: codex
```

Qoder 审核运行时固定为：

```yaml
runtime: qoderclicn
model: deepseek
```

`orchestrator_developer` 是调度器的开发归属。Codex 已实现 V0.2 基础设施，但仍不参与任务规划、开发、审核、裁定或修复；运行时任务分别由 Mimo Code 和 Qoder 承担。

## 完整流程

```text
Mimo 规划
→ 规划冻结与 Schema 校验
→ Mimo 开发
→ 专属 Validator
→ 读取 review_policy

validator_only
→ 确定性验收
→ accepted
→ 下一轮规划

lightweight_non_execution
→ Qoder + DeepSeek 轻量审核
→ passed 或 patch_required

full_execution
→ Qoder + DeepSeek 完整审核
→ passed 或 patch_required

patch_required
→ Mimo 定向修复
→ Qoder 补丁复审一次
→ passed 或人工介入
```

V0.2 先生成当前节点 handoff。用户执行 `run-agent --approve` 后，Adapter 只启动当前状态对应的一个 Agent；Agent 退出后通过安全门禁才自动 ingest，并停在下一 Agent 启动确认点。规划任务单默认不做模型审核；Qoder 从所有任务的固定必经节点调整为由风险驱动的审核节点。

Commit 契约明确区分 planning、delivery 与 metadata Commit。开发结果记录 planning Commit 和 delivery Commit，但不记录包含自身的 Commit；Qoder 只审核 delivery Commit。补丁复审分别核验 base delivery Commit 与 patch Commit。所有机器文件和 handoff 中的 Commit 必须是 40 位完整小写哈希。

批次任务数必须为 1–10；用户明确指定数量时必须保持原数量，未指定时规划建议默认 7 项。超过 10 项必须返回 `batch_split_required: true`，按每批最多 10 项给出保序、无丢失的拆批计划，不得填充或截断任务。

## Review Policy

规划阶段必须为每项任务冻结 `risk_level`、`review_profile`、`qoder_review_required` 和分类依据。开发阶段必须原样继承，只能申请升级，不能降级。

- `validator_only`：只用于低风险、非执行、机械性任务，且 `qoder_review_required: false`。
- `lightweight_non_execution`：用于涉及状态语义或跨文件一致性的非执行任务，且 `qoder_review_required: true`。
- `full_execution`：用于执行型任务、能力资产链、安全或 coverage 语义变更、共享逻辑及高影响工程资产，且 `qoder_review_required: true`。

所有任务都必须有专属 Validator。`validator_only` 不能用于执行型任务，不能修改或生成 `execution_results`，不能修改 runtime、parser、公共逻辑、Registry `coverage_depth` 或 `safety_level`。

## validator_only 确定性验收

`validator_only` 不等于无验收。最终接受前至少必须满足：

```yaml
task_specific_validator_passed: true
validator_failed_count: 0
git_diff_matches_frozen_scope: true
development_result_schema_valid: true
no_review_escalation_triggered: true
```

其最终接受状态使用：

```yaml
acceptance_mode: validator_only
final_status: accepted
qoder_review_required: false
```

不得写成 `review_status: passed`，因为该任务未经过 Qoder 审核。任何 Validator 失败、范围漂移、规划缺陷、意外 Registry 或 `execution_results` 修改、共享资产修改、安全字段变化、Git Diff 不一致或未解决错误都必须触发审核升级。

## Qoder 分级审核

### lightweight_non_execution

默认只核对冻结任务包、`development_result`、完整 delivery Commit、真实 Git Diff、实际修改文件、直接状态证据、专属 Validator、coverage 与安全字段。默认不扫描完整仓库、无关历史或无关模块；仅在 Commit 不一致、Validator 失败、范围漂移、语义冲突、duplicate claim 矛盾、安全变化、证据不足或共享资产受影响时扩大范围。

### full_execution

默认核对完整资产链：mapping → corpus/playbook → run config → capability engine → `execution_results` → parser/result → scorecard → Registry → 专属 Validator → coverage evidence。

### 补丁复审

补丁复审默认只检查原 `issue_id`、Patch Commit、Patch Diff、受影响文件、专属 Validator 和新高风险问题。仅在补丁影响共享 Runtime、公共 Parser、Registry Schema、`coverage_depth`、`safety_level`、多个模块或公共 Validator 时扩大范围。自动修复最多一次；复审再次为 `patch_required` 时停止并要求人工介入。

## 机器可读交接

- 规划方输出冻结任务包和通过 `agent_contracts/batch_manifest.schema.yaml` 校验的批次清单。
- 开发方输出通过 `agent_contracts/development_result.schema.yaml` 校验的 `development_result.yaml`，包含冻结策略及升级申请。
- 仅 `lightweight_non_execution` 与 `full_execution` 产生 Qoder `review_result.yaml`，并通过 `agent_contracts/review_result.schema.yaml` 校验。
- 补丁方输出通过 `agent_contracts/patch_result.schema.yaml` 校验的 `patch_result.yaml`，以 `fixed_issue_ids` 对账首次审核问题。
- 补丁复审继续使用 `review_result.schema.yaml`，通过审核轮次、完整 Commit 和原始 `issue_id` 建立追踪关系。

Agent 之间不直接通信。V0.2 Adapter 只把当前 handoff 作为附件交给对应 CLI，并以结果文件、Schema、Commit、Git Scope 和状态字段决定是否自动 ingest；不解析自然语言日志决定状态。自然语言日志、Markdown 摘要和对话内容均不是状态来源。

`development_result.yaml`、`review_result.yaml` 或 `patch_result.yaml` 因 Schema 错误进入 `workflow_error` 后，结果生产方仍负责依据对应现行 Schema 重新生成纠正文件；调度器不得自动编辑。恢复类型必须同时匹配文件名、Schema 和原错误记录。只有身份、完整 Commit、任务状态、冻结 Scope、安全边界及适用 Validator 全部通过时，`retry-ingest` 才可在一次持久化中追加错误解决记录并继续流转。其他业务错误、Commit/Scope 漂移、Validator 或安全错误必须继续停止。

新冻结任务包必须用 `validator_commands` 分别声明 development 和 patch 的 executable、repository-relative script、args 与 timeout。调度器只按数组并以 `shell=False` 执行冻结命令，记录完整 stdout/stderr 审计；Agent 结果文件不能覆盖参数。`rerun-validator` 仅可恢复已证明由旧 runner 丢失冻结参数造成的失败，不能恢复真实 Validator 失败。

## 冻结、Coverage 与失败处理

任务包在 `planning_status: frozen` 后不可由开发或补丁阶段改写。开发发现冻结目标、`assessment_mode`、`coverage_depth`、专属 Validator、安全边界或审核策略存在缺陷时，必须返回 `development_status: planning_defect` 或申请审核升级，不得自行重新规划。

Registry 字段同步不自动构成 coverage change。审核结果必须分别记录 Registry 同步、coverage change 和 coverage credit，不接受重复 coverage claim、跨任务共享 credit 或无新增证据的 coverage 升级。

Qoder 的正常审核结论只有 `passed` 和 `patch_required`。环境或流程异常仍写为 `patch_required`，并设置 `workflow_error: true`、`human_intervention_required: true` 和 `next_action: stop_for_human_intervention`。

## V0.2 Agent 执行边界

```yaml
agent_execution_enabled: true
single_task_serial_execution: true
human_approval_before_each_agent: true
automatic_ingest_enabled: true
automatic_next_agent: false
parallel_agent_execution: false
automatic_next_batch: false
automatic_retry_agent: false
```

Qoder 固定请求 `qoderclicn --permission-mode yolo`，不得回退其他 permission mode。Mimo 使用 `mimo run` 默认权限行为，不添加 `--never-ask` 或权限绕过参数。出现交互审批、TTY 等待、超时、取消、非零退出、缺失/非法结果、Commit 不一致或范围越界时，当前任务进入 `human_intervention_required`，保留日志且不自动 ingest。

## 状态模板与未实现事项

`planning/latest_project_state.yaml`、`planning/coverage_dashboard_snapshot.yaml` 和 `planning/registry_snapshot.yaml` 是模板，不得解释为真实项目状态。真实规划开始前，必须由人工或未来受控流程提供可验证快照。

- 已实现 V0.2 单任务串行 CLI Adapter；未实现并行 Agent 或自动循环。
- V0.2 开发和测试仅使用 fake CLI，未调用真实 Mimo Code 或 Qoder。
- 未实现审核或验收后的自动下一轮规划。
- 未生成或修改任何 `execution_results`、Registry、coverage 状态或裁定结果。
- 所有标记为 `draft` 的指令均未经过真实运行验证。
