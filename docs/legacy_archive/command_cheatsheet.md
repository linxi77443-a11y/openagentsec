# 命令速查表

| 命令 | 用途 | 是否安全默认 | 是否生成 evidence | 是否修改文件 |
|---|---|---|---|---|
| `bash runners/run_quality_check.sh` | 运行安全门禁和 dry-run 检查 | 是 | 否 | 否 |
| `bash runners/run_atlas_assessment.sh --profile all` | 生成 ATLAS assessment plan | 是 | 是，plan | 是，更新 `atlas_assessment_plan.json` |
| `bash runners/run_atlas_assessment.sh --profile all --execute` | 执行 Chatbot / RAG / Agent 本地完整评估 | 需要人工确认 | 是 | 是 |
| `bash runners/run_promptfoo.sh` | Chatbot dry-run | 是 | 否 | 否 |
| `bash runners/run_promptfoo.sh --execute` | Chatbot 本地 execute | 需要人工确认 | 是 | 是 |
| `bash runners/run_rag_promptfoo.sh` | RAG dry-run | 是 | 否 | 否 |
| `bash runners/run_rag_promptfoo.sh --execute` | RAG 本地 execute | 需要人工确认 | 是 | 是 |
| `bash runners/run_agent_promptfoo.sh` | Agent dry-run | 是 | 否 | 否 |
| `bash runners/run_agent_promptfoo.sh --execute` | Agent 本地 execute | 需要人工确认 | 是 | 是 |
| `bash runners/run_manual_ui_promptfoo.sh` | Manual UI Replay dry-run | 是 | 否 | 否 |
| `bash runners/run_manual_ui_promptfoo.sh --execute` | Manual UI 本地 fake replay execute | 需要人工确认 | 是 | 是 |
| `python3 scripts/compile_corpus_to_testcases.py` | 编译语料到标准化测试用例 | 是 | 否 | 是，生成到 generated_testcases/ |
| `bash scripts/generate_all_reports.sh` | 生成 dashboard 和报告 | 是 | 否 | 是 |
| `git status --short` | 查看工作区变更 | 是 | 否 | 否 |
| `git add <files> && git commit -m "..."` | 提交阶段快照 | 取决于暂存内容 | 否 | 是，写入 Git 历史 |

## 推荐日常顺序

```bash
git status --short
bash runners/run_quality_check.sh
bash scripts/generate_all_reports.sh
git status --short
```

## Execute 前检查

运行任何 `--execute` 前确认：

- provider 仍然是本地 `exec:` provider。
- 目标是本地 sandbox 或 fake replay。
- 不访问真实页面、真实 API、真实模型或企业系统。
- 不读取真实账号、密码、token、API key 或环境变量。
- evidence 输出路径在 `reports/evidence/`。
- quality check 已通过。

## 不应直接运行的命令

不要在未确认范围时运行：

```bash
bash runners/run_atlas_assessment.sh --profile all --execute
bash runners/run_promptfoo.sh --execute
bash runners/run_rag_promptfoo.sh --execute
bash runners/run_agent_promptfoo.sh --execute
bash runners/run_manual_ui_promptfoo.sh --execute
```

如果要接入非本地目标，必须先完成 `docs/non_local_target_approval_checklist.md`。
