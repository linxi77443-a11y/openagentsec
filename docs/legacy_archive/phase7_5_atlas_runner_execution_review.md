# Phase 7.5 ATLAS 总控 Runner 执行复盘

## 执行范围

Phase 7.5 验证 `runners/run_atlas_assessment.sh` 能否在本地 sandbox 范围内串联 Chatbot、RAG、Agent 三类已有 runner，并生成 ATLAS summary evidence。

本阶段没有新增攻击能力，没有接入真实 API、真实模型、企业系统、外部网络目标或真实凭证，也没有安装 garak、PyRIT 或 AgentDojo。

## 执行前检查

- 工作区状态：执行前 `git status --short` 无输出。
- 质量检查：`bash runners/run_quality_check.sh` 通过。
- ATLAS dry-run：`bash runners/run_atlas_assessment.sh --profile all` 通过，并生成 `reports/evidence/atlas_assessment_plan.json`。

## 本地 execute 命令

```bash
bash runners/run_atlas_assessment.sh --profile all --execute
```

执行模式先运行 `runners/run_quality_check.sh`，通过后依次调用：

- `runners/run_promptfoo.sh --execute`
- `runners/run_rag_promptfoo.sh --execute`
- `runners/run_agent_promptfoo.sh --execute`

## 执行结果

| Profile | Runner | Evidence | Pass | Fail | Error | Status |
|---|---|---|---:|---:|---:|---|
| chatbot | `runners/run_promptfoo.sh` | `reports/evidence/promptfoo_chatbot_result.json` | 9 | 0 | 0 | passed |
| rag | `runners/run_rag_promptfoo.sh` | `reports/evidence/promptfoo_rag_result.json` | 12 | 0 | 0 | passed |
| agent | `runners/run_agent_promptfoo.sh` | `reports/evidence/promptfoo_agent_result.json` | 10 | 0 | 0 | passed |

ATLAS summary evidence：`reports/evidence/atlas_assessment_summary.json`。

## Summary schema 验证

`atlas_assessment_summary.json` 已包含每个 profile 的以下字段：

- `profile`
- `runner`
- `evidence_file`
- `status`
- `pass`
- `fail`
- `error`
- `covered_atlas_techniques`
- `timestamp`
- `assertion_pass`
- `assertion_fail`

## ATLAS coverage 统计

Phase 7.5 summary 中去重后的 covered technique 数量：12。

Coverage matrix 状态统计：

- `covered`：11
- `partially_covered`：1
- `planned`：4
- `not_applicable`：1

## 边界验证

- Evidence 中未发现完整 `HONEYTOKEN_`、`FAKE_SECRET_`、`DUMMY_TOKEN_` 前缀。
- Evidence 和 JSONL log 中未发现未脱敏 email-like 或 bearer-like 字符串。
- Agent fake write action 保持 `dry_run=true`、`sent=false`、`side_effect=dry_run_only`。
- 未发现外部请求、真实 API、真实模型、真实凭证或企业系统访问痕迹。

## 结论

Phase 7.5 验证通过：ATLAS 总控 runner 可以在本地 sandbox 内先执行质量检查，再调度现有 Chatbot、RAG、Agent runner，并生成结构化 summary evidence。

当前结论只适用于本地 sandbox、fake data、fake documents 和 fake tools，不代表真实企业系统、真实模型 API、真实知识库或真实 Agent 工具链的安全结论。
