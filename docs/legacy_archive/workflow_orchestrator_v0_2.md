# 工作流调度器 V0.2：单任务串行 Agent CLI Adapter

```yaml
document_version: v0.2
change_mode: minimal_adapter
no_state_machine_refactor: true
```

## 边界

V0.2 在 V0.1.5 状态机外增加 Agent 启动层。每次只允许当前状态对应的一个 Agent；用户必须显式提供 `--approve`。Agent 完成后可以自动 ingest 当前机器结果，但绝不自动启动下一 Agent、下一批次或下一轮规划。

```yaml
agent_execution_enabled: true
single_task_serial_execution: true
human_approval_before_each_agent: true
automatic_ingest_enabled: true
automatic_next_agent: false
parallel_agent_execution: false
automatic_next_batch: false
automatic_retry_agent: false
max_patch_cycles: 1
```

## 已核验的本机 CLI

```yaml
mimo:
  executable: /Users/linxi/.mimocode/bin/mimo
  version: 0.1.6
  invocation_template:
    - mimo
    - run
    - --dir
    - <repository_root>
    - --file
    - <handoff.md>
    - <short_instruction>
  permission_mode: default_cli_behavior

qoder:
  executable: /Users/linxi/.nvm/versions/node/v22.23.0/bin/qoderclicn
  version: 1.0.48
  invocation_template:
    - qoderclicn
    - --permission-mode
    - yolo
    - --print
    - --cwd
    - <repository_root>
    - --attachment
    - <handoff.md>
    - <short_instruction>
  permission_mode: yolo
```

本机 `qoderclicn --help` 当前列出的 permission mode 不包含 `yolo`。Adapter 因此把真实 Qoder 标记为 `required_permission_mode_unavailable`，真实 `--approve` 会在启动前停止并进入人工介入，不回退到 `auto`、`dont_ask`、`bypass_permissions` 或其他模式。`qoderclicn --permission-mode yolo --version` 虽返回版本，但不能证明实际 Agent 会接受该模式。

Mimo 只使用已核验的 `mimo run --file --dir`，不添加 `--never-ask`、`--dangerously-skip-permissions` 或其他未经授权的权限参数。

## 状态路由

| current_state | Agent | 预期结果 |
|---|---|---|
| `development_pending` | `mimo_development` | `development_result.yaml` |
| `review_pending` | `qoder_review` | `review_result.yaml` |
| `patch_pending` | `mimo_patch` | `patch_result.yaml` |
| `patch_review_pending` | `qoder_patch_review` | `review_result.yaml` |

用户不能指定 Agent。其他状态执行 `run-agent` 会返回 `agent_not_allowed_for_state`。

## CLI

```bash
python scripts/workflow.py agent-status

python scripts/workflow.py run-agent \
  --batch <batch_id> \
  --task <task_id> \
  --dry-run

python scripts/workflow.py run-agent \
  --batch <batch_id> \
  --task <task_id> \
  --approve

python scripts/workflow.py cancel-agent \
  --batch <batch_id> \
  --task <task_id>
```

`run-agent` 必须且只能选择 `--dry-run` 或 `--approve`。批准绑定 batch、task、当前状态、handoff SHA-256 和 Agent；状态或 handoff 变化会使本次批准失效。

## 运行记录

每次批准尝试写入：

```text
runtime/<batch_id>/agent_runs/<task_id>/<run_id>/
├── invocation.yaml
├── stdout.log
├── stderr.log
├── process.json
└── result.yaml
```

日志记录完整进程结果、前后 HEAD、工作区快照、新 Commit、修改文件、结果校验和最终状态。参数及 stdout/stderr 会遮蔽 Token、API Key、Cookie、Authorization、密码、Secret、Bearer 值和 URI userinfo。Agent 子进程只继承配置 allowlist 中的环境变量；日志从不记录环境变量值。

实际执行使用参数数组、`stdin=DEVNULL`、`shell=False` 和独立进程组。同一任务以 `.active.lock` 防止重复启动。超时或 `cancel-agent` 先发送 SIGTERM，15 秒宽限期后才发送 SIGKILL；部分结果不 ingest，且不自动重试。

## Git 与自动 ingest 门禁

调度器记录预存工作区文件的状态与 SHA-256，因此不会因为仓库本来不干净而误判，也能发现 Agent 改写已有未跟踪文件。它不会执行 reset、clean、stash、rebase、push 或自动回滚。

- Mimo development/patch 只允许冻结 `delivery_modification_scope` 和对应机器结果文件。
- Qoder review/patch review 只允许对应任务的 `review_result.yaml`。
- 发现范围越界会保留现场并进入 `human_intervention_required`。

自动 ingest 前必须同时满足：退出码 0、无超时/取消/交互审批、结果在本次运行中新建或更新、Schema 与身份有效、Commit 为完整 SHA、review Commit 匹配、Git Scope 有效、工作流状态未变化。Adapter不编辑结果、不补 Commit、不删除非法字段，也不调用 `retry-ingest` 掩盖错误。

## 配置

版本库提供 `config/agent_adapters.example.yaml`。本机可复制为被 Git 忽略的 `config/agent_adapters.local.yaml`；不得在配置中保存 Token、Cookie 或凭据。若 local 文件存在，CLI 优先读取它。

## 首次真实冒烟测试

基础设施开发期间不运行真实 Agent。首次 Mimo 测试由用户分两步执行：

```bash
python scripts/workflow.py run-agent --batch <synthetic_batch> --task <development_pending_task> --dry-run
python scripts/workflow.py run-agent --batch <synthetic_batch> --task <development_pending_task> --approve
```

确认自动 ingest 后停在 `review_pending`，不要继续启动 Qoder。第二次单独测试 Qoder：

```bash
python scripts/workflow.py run-agent --batch <synthetic_batch> --task <review_pending_task> --dry-run
python scripts/workflow.py run-agent --batch <synthetic_batch> --task <review_pending_task> --approve
```

只有 `agent-status` 和 dry-run 明确显示 `permission_mode_supported: true` 时才执行 Qoder `--approve`；当前本机版本不满足这一条件。
