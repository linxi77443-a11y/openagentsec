# Manual UI Replay 评估流程

Manual UI Replay 是一种人工页面评估模式：测试人员在页面中输入测试问题，复制页面输出，保存为本地 replay JSON，再由本地 provider 做风险信号分析、脱敏和 evidence 生成。

## 为什么先做人工 replay

相比浏览器自动化，人工 replay 的边界更清晰：

- 不需要登录真实账号。
- 不需要浏览器自动化权限。
- 不会误触真实页面按钮或写操作。
- 可以先验证 evidence schema、脱敏、报告和 dashboard 流水线。
- 真实页面接入前可以先沉淀审批和复核流程。

## Phase 9 当前边界

- 只使用 `replays/manual_ui_samples/` 中的 fake replay。
- 不访问真实页面。
- 不连接真实 API 或真实模型。
- 不读取真实账号、密码、token 或环境变量。
- 不访问外部网络。
- 不执行 promptfoo `--execute`。

## 如何填写 replay JSON

参考：`replays/manual_ui_replay_schema.md`。

最小字段包括：

- `replay_id`
- `target_name`
- `target_type`
- `assessment_mode`
- `profile`
- `test_case_id`
- `atlas_technique`
- `test_category`
- `input`
- `page_output`
- `copied_by`
- `copied_at`
- `redaction_applied`
- `expected_behavior`
- `notes`

## dry-run

```bash
bash runners/run_manual_ui_promptfoo.sh
```

输出将显示本地 provider、replay source 和 evidence 路径，但不会执行测试，也不会生成 evidence。

## 本地 fake replay execute

Phase 9.5 已在人工确认后执行本地 fake replay。执行前确认只读取 `replays/manual_ui_samples/`，且样例不包含真实页面、账号、token 或企业数据。

执行命令：

```bash
bash runners/run_manual_ui_promptfoo.sh --execute
```

## Evidence

本地 fake replay execute 后会写入：

```text
reports/evidence/promptfoo_manual_ui_result.json
```

Phase 9.5 后该文件已生成，dashboard 和报告显示 Manual UI Replay 为 `available`。

## 未来企业页面接入

真实页面接入前必须完成：

- 明确书面授权。
- 测试页面、账号、时间窗口和数据范围确认。
- 禁止生产数据和真实客户数据进入 replay JSON。
- 输出复制后先脱敏，再进入 evidence。
- 写操作和高风险页面必须 human-in-the-loop。
- 需要回滚和审计记录。
