# 任务工作流调度器 V0.1.5

```yaml
document_version: v0.1.5
```

## 定位

```yaml
orchestrator_version: v0.1.5
orchestrator_type: deterministic_multi_task_state_machine
single_task_supported: true
multi_task_supported: true
agent_execution_enabled: false
automatic_next_round_enabled: false
human_handoff_enabled: true
max_automatic_patch_cycles: 1
```

V0.1.5 不包含 Mimo Code 或 Qoder 调用能力。它只读取机器文件、运行冻结的专属 Validator、核验 Git Commit 与修改范围、持久化每项任务的独立状态，并生成供人复制执行的 handoff。

## 批次数量规则

```yaml
minimum_tasks_per_batch: 1
maximum_tasks_per_batch: 10
default_tasks_when_unspecified: 7
user_specified_count_must_be_respected: true
```

新批次必须包含 1–10 项任务，单任务和多任务使用同一状态机。用户明确指定数量时按该数量规划，不填充、不截断；未指定时，规划层建议默认 7 项。调度器只校验冻结清单，不调用规划 Agent。

超过 10 项时，严格 Schema 拒绝原批次并返回 `state: workflow_error`、`batch_split_required: true` 和确定性 `batches` 拆分计划。拆分计划以每批最多 10 项保留完整任务对象、原始顺序和全部 `task_id`，不改写源 manifest，也不自动创建或启动子批次。可使用：

```bash
python scripts/workflow.py split --batch <batch_id>
```

## 文件

- CLI：`scripts/workflow.py`
- 状态机：`workflow_orchestrator/engine.py`
- 状态：`runtime/<batch_id>/workflow_state.yaml`
- 事件：`runtime/<batch_id>/workflow_events.jsonl`
- 汇总：`runtime/<batch_id>/batch_summary.yaml`
- Handoff：`runtime/<batch_id>/handoffs/<task_id>/`

每个 handoff 目录始终只保留当前状态需要的一个请求文件。重复执行 `next` 或 `resume` 会生成相同内容，不启动 Agent。

## CLI

```bash
python scripts/workflow.py init --batch <batch_id> --planning-commit <40位完整哈希>
python scripts/workflow.py status --batch <batch_id>
python scripts/workflow.py validate --batch <batch_id>
python scripts/workflow.py next --batch <batch_id>
python scripts/workflow.py ingest --batch <batch_id> --task <task_id> --file <result_file>
python scripts/workflow.py retry-ingest --batch <batch_id> --task <task_id> --file <corrected_result_file>
python scripts/workflow.py retry-ingest --batch <batch_id> --task <task_id> --file <corrected_result_file> --dry-run
python scripts/workflow.py rerun-validator --batch <batch_id> --task <task_id>
python scripts/workflow.py summary --batch <batch_id>
python scripts/workflow.py resume --batch <batch_id>
python scripts/workflow.py replay --batch <historical_batch_id>
python scripts/workflow.py split --batch <batch_id>
```

`init` 只接受符合当前 `batch_manifest.schema.yaml`、包含 1–10 项且任务间无依赖的新批次，并要求显式提供完整 planning Commit。`ingest` 与 `retry-ingest` 只接受文件名严格为 `development_result.yaml`、`review_result.yaml` 或 `patch_result.yaml` 的机器结果。恢复类型由文件名、对应 Schema 和原始错误事件中的 `failed_result_type` 共同确定，三者不一致即拒绝；`--dry-run` 会执行同样的 Schema、Commit、Scope 和 Validator 校验，但不写状态、事件、汇总、结果副本或 handoff。

## 状态与路由

每项任务独立保存 `review_profile`、当前状态、planning/delivery/metadata/patch Commit、Validator 状态、审核状态、补丁次数、最终状态、warnings 和 errors。

- `validator_only`：Schema、完整 Commit、Git Diff、冻结范围和专属 Validator 全部通过，且未触发升级时，使用 `acceptance_mode: validator_only` 接受；不写 `review_status: passed`。
- `lightweight_non_execution`：Validator 通过后生成 Qoder 轻量审核 handoff。
- `full_execution`：Validator 通过后生成 Qoder 完整资产链审核 handoff。
- `patch_required`：只允许一次 Mimo 补丁和一次 Qoder 补丁复审；再次失败后进入人工介入。

一个任务失败不会改变其他任务状态。批次只有在所有任务分别为 `accepted` 时才设置 `batch_ready_for_next_round: true`，但 V0.1.5 不会据此自动启动下一轮。

## Commit 模型与范围核验

```yaml
planning_commit:
  purpose: 冻结 task package、batch manifest、planning freeze、Validator 和只读输入 Fixture
delivery_commit:
  purpose: 仅包含 delivery_modification_scope 内的开发交付
metadata_commit:
  purpose: 可选保存 development_result、workflow state 或 handoff，不是审核对象
```

planning Commit 在创建后通过 `init --planning-commit` 传入，不写入自身。`development_result.yaml` 只记录完整 `planning_commit` 与 `delivery_commit`，因此不存在结果文件要求包含自身的自引用。

新 ingest 要求严格匹配 `^[0-9a-f]{40}$` 的 Commit。调度器实际解析 Git 对象，并检查：

1. planning Commit 的真实 Diff 与 `planning_assets` 完全一致；
2. delivery Commit 是 planning Commit 的后代但不是同一 Commit；
3. delivery Commit 的单次真实 Diff 与 `modified_files` 一致；
4. delivery 文件全部位于冻结任务包的 `delivery_modification_scope`；
5. runtime 结果、workflow state、handoff 和后续 metadata Commit 不计入 delivery Scope；
6. Qoder `reviewed_commit` 必须严格等于 delivery Commit；
7. 专属 Validator 名称与冻结任务包一致。

新冻结任务包必须为 planning、development 与 patch 分别提供结构化命令：

```yaml
delivery_modification_scope:
  - repository/relative/path/or/directory/
validator_commands:
  planning:
    executable: python
    script: scripts/validate_task.py
    args: ["--phase", "planning"]
    timeout_seconds: 120
  development:
    executable: python
    script: scripts/validate_task.py
    args: ["--phase", "development"]
    timeout_seconds: 120
  patch:
    executable: python
    script: scripts/validate_task.py
    args: ["--phase", "patch"]
    timeout_seconds: 120
```

调度器不会解析自然语言目标来猜测可写范围，也不接受 Agent 在结果文件中覆盖 Validator 参数。实际执行始终使用参数数组和 `shell=False`；`&&`、`;`、管道、重定向、命令替换、仓库外脚本及未冻结阶段命令都会被拒绝。

每次执行会在状态与事件中记录 `phase`、声明的 executable/script/args、实际 `resolved_command`、timeout、exit code、stdout、stderr 与超时标记。development result 只运行 development 命令，patch result 只运行 patch 命令。

已初始化的旧状态仍可运行无参数的历史命令数组；历史只读回放保持原兼容规则。仅 `rerun-validator` 可为已冻结且已证明由旧 runner 丢参造成失败的任务，从 planning Commit 中的旧 phase command 安全解析参数，解析后仍以数组执行而不启动 shell。新任务不得使用字符串命令契约。

## 幂等与恢复

- 每个 ingest 结果按 SHA-256 去重；重复 ingest 不追加事件或重复流转。
- `workflow_state.yaml` 使用原子替换写入。
- `workflow_events.jsonl` 保存单调递增事件序号。
- `resume` 验证状态并重建当前 handoff，不重开 accepted 任务。
- 已进入 `ready_for_next_round` 的批次不能通过 `init` 自动重开。

### 机器结果纠正后的受控重试

普通 `resume` 只恢复落盘状态，不清除错误。只有任务当前为 `workflow_error`、可追溯根因是三类已登记机器结果之一的 `schema_validation_failed`，且纠正文件通过对应现行严格 Schema 时，才允许使用 `retry-ingest`。调度器不编辑结果文件；结果生产方必须依据现行 Schema 重新生成文件。

重试在内存副本中一次完成全部检查和状态投影，全部成功后才进行一次持久化：读取原错误 → 对账结果类型 → 校验纠正文件 → 核验 batch/task 身份 → 核验适用 Commit、Scope、安全及 Validator 条件 → 追加 `workflow_error_resolved` → ingest 结果 → 进入该结果对应的下一状态。任何检查失败都不清空原错误，也不写入半恢复状态。

允许恢复的根因仅为：

```yaml
recoverable_errors:
  - schema_validation_failed
supported_result_types:
  - development_result
  - review_result
  - patch_result
```

以下错误不能通过 `retry-ingest` 自动恢复：

```yaml
non_recoverable_errors:
  - planning_commit_mismatch
  - delivery_commit_mismatch
  - delivery_scope_mismatch
  - patch_scope_mismatch
  - planning_asset_modified
  - validator_failed
  - review_commit_mismatch
  - patch_commit_mismatch
  - patch_cycle_limit_exceeded
  - safety_boundary_violation
  - task_id_mismatch
  - batch_id_mismatch
  - result_type_mismatch
```

原错误事件不会删除或重写。成功后任务状态中的当前 `errors` 被清空，并新增：

```yaml
resolved_errors:
  - code: schema_validation_failed
    result_type: review_result
    original_event_sequence: 1
    original_file_sha256: 64位SHA-256
    resolved_at: ISO-8601时间
    corrected_file_sha256: 64位SHA-256
    resolution: corrected_machine_result_reingested
    related_event_sequences: []
```

`development_result` 继续核验原 planning/delivery Commit 与冻结范围；初次 `review_result` 要求完整 `reviewed_commit` 严格等于任务的 delivery Commit，并按 `passed → accepted`、`patch_required → patch_pending` 流转；`patch_result` 要求 base delivery Commit、原 patch Commit、issue ID、Patch Scope 和专属 Validator 全部匹配，并进入 `patch_review_pending`。未知文件、结果类型错配、Commit/Scope 漂移、安全字段或 Validator 失败均拒绝恢复。

JSONL 追加 `workflow_error_resolved` 及正常 ingest 事件；已有行保持逐字不变。审计记录同时保存 `result_type`。汇总中的当前 `workflow_error` 数量不再包含已解决错误，并单独报告 `resolved_error_count`。同一结果类型、同一纠正文件再次提交返回幂等结果，不追加事件；已恢复任务不能用不同文件再次恢复同一个错误。

### Validator runner 缺陷受控重跑

`rerun-validator` 仅处理 `current_state: validator_failed` 且最新事件为 `task_validator_failed` 的 runner 调用缺陷。调度器重新核验 planning assets、delivery Commit 与 Scope，从冻结任务包恢复完整 development 命令，并证明原执行命令与冻结命令不同后才允许运行。完整冻结命令本身失败、Validator 真实失败、Commit/Scope 漂移或存在其他活动错误时拒绝恢复。

成功后追加 `validator_runner_defect_resolved`，在 `resolved_errors` 中记录 `orchestrator_validator_invocation_defect` 和完整 `validator_execution`，保留所有原 JSONL 行，并按原审核策略进入 `review_pending` 或适用的 `validator_only` 接受状态。

## 新运行严格模式与历史只读回放

```yaml
new_runs:
  require_batch_id: true
  require_full_commit: true
```

新运行始终使用当前 Schema；格式错误返回 `state: workflow_error`。历史兼容仅允许五个明确登记的 2026-07-20 批次，不能被任意新 batch_id 调用，也不能放宽新任务结果中的 `batch_id` 或完整 Commit 要求。

`replay` 为 2026-07-20 的历史批次提供只读 compatibility。BATCH-001 至 004 保留原结论；BATCH-005 固定作为 Commit 契约负面案例，输出 `final_state: workflow_error`，不生成 patch handoff，不改写任何历史文件或 Commit。

历史结果中的短哈希或 `pending` 仅在回放适配器中通过现有 Git/审核证据解析；新 ingest 不接受这些值。`BATCH-2026-07-20-004` 的旧 manifest 存在两行 list/mapping 缩进错误，回放器只在内存中忽略这两行无关 dependency 元数据并输出兼容警告。

每次历史回放明确输出：

```yaml
compatibility_mode_recorded: true
historical_files_modified: false
historical_results_overwritten: false
```

BATCH-2026-07-20-004 的解析恢复还会记录 `category: historical_manifest_parse_recovery`、`recovery_applied: true`、`source_modified: false`、源文件路径、恢复原因及被忽略的原始行。相同错误若出现在新运行中会被拒绝，绝不调用历史 adapter。

## 已知既存测试基线

```yaml
known_preexisting_test_failures:
  duplicate_test_module_collection:
    affected_backup_directories: 2
  m16_interface_assertion_drift:
    failure_count: 33
  introduced_by_orchestrator: false
```

这些问题不属于调度器补丁范围；V0.1.5 不修改相关业务测试或备份目录。

## V0.2 前置条件

V0.2 若要自动调用 Agent，仍需人工确认或实现：

- Mimo Code 与 Qoder 的受控调用接口、认证方式和超时/取消语义；
- Agent 运行目录、并发隔离和资源上限；
- Commit 签名或调用身份与任务身份的强绑定；
- 真实 `patch_required` 分支的一次人工端到端验证；
- 网络、凭据、日志脱敏和失败重试策略；
- 自动下一轮规划的显式人工授权门。
