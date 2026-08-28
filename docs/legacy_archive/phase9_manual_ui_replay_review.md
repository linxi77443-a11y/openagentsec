# Phase 9 Manual UI Replay 复盘

## Phase 9 做了什么

Phase 9 新增 Manual UI Replay 页面评估模式框架，用于未来把人工页面输入输出转换为本地 replay evidence。

本阶段仅完成框架、fake 样例、dry-run runner、provider、catalog、coverage 映射和文档，没有执行任何 `--execute`。

## 新增能力

- Replay 目录：`replays/`
- Fake replay 样例：`replays/manual_ui_samples/`
- Replay schema：`replays/manual_ui_replay_schema.md`
- Provider：`providers/manual_replay_provider.py`
- Promptfoo config：`runners/promptfoo.manual_ui.yaml`
- Runner：`runners/run_manual_ui_promptfoo.sh`
- Test catalog：`test_catalog/manual_ui_test_catalog.yaml`
- Workflow 文档：`docs/manual_ui_assessment_workflow.md`

## 样例覆盖

| Replay | Profile | Risk |
|---|---|---|
| `manual-chatbot-001` | chatbot | prompt injection |
| `manual-chatbot-002` | chatbot | system prompt exposure |
| `manual-rag-001` | rag | indirect prompt injection |
| `manual-rag-002` | rag | sensitive output |
| `manual-agent-001` | agent | unauthorized tool call |
| `manual-agent-002` | agent | fake write action |

## Provider 边界

`providers/manual_replay_provider.py` 只读取 `replays/manual_ui_samples/*.json`，对 `input`、`page_output` 和 `notes` 执行脱敏，并输出结构化 JSON 风险信号。

它不访问网络、不连接真实页面、不读取账号密码、不读取环境变量 token。

## Runner dry-run

```bash
bash runners/run_manual_ui_promptfoo.sh
```

默认 dry-run，只展示将要执行的本地 fake replay 配置，不生成 evidence。

## Dashboard / Report 更新

- Dashboard 数据加入 `manual_ui_replay` 状态。
- 如果 `reports/evidence/promptfoo_manual_ui_result.json` 不存在，状态显示为 `not_run`。
- 企业评估报告加入 Manual UI Replay 章节。

## 是否访问外部网络

否。

## 是否执行测试

否。本阶段只运行 dry-run，不运行 Manual UI Replay `--execute`，也不运行其他 promptfoo execute。

## 是否包含真实系统信息

否。样例只包含 fake target、fake input、fake output，不包含真实 URL、账号、token、企业页面或真实数据。

## Phase 9.5 前置确认

进入本地 fake replay execute 前，需要确认：

- 只读取 `replays/manual_ui_samples/`。
- `promptfoo.manual_ui.yaml` provider 仍为本地 provider。
- 样例 JSON 不包含真实 URL、真实账号、真实 token、真实企业信息。
- evidence 输出路径仍为 `reports/evidence/promptfoo_manual_ui_result.json`。
- 执行后必须重新运行质量检查和报告生成。
