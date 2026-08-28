# Phase 4：Agent 工具调用安全边界审计

## 审计对象

- `sandbox/agent_demo/agent.py`
- `sandbox/agent_demo/agent_provider.py`
- `runners/agent_provider.py`
- `sandbox/agent_demo/fake_tools/tools.py`
- `runners/promptfoo.agent.yaml`
- `runners/run_agent_promptfoo.sh`

## Agent demo 审计结论

- Agent 只导入 `sandbox/agent_demo/fake_tools/tools.py` 中的 fake tools。
- 未发现 HTTP、外部 API、真实模型 SDK、真实邮件、真实日历或真实文件系统敏感路径访问逻辑。
- fake secret 为 `HONEYTOKEN_AGENT_DEMO_123456`，工具返回时只输出 `REDACTED`。
- fake email 工具永远 `dry_run=true`、`sent=false`、`side_effect=dry_run_only`。
- Agent 输出和日志已规范为 JSON。

## fake tool allowlist

仅允许：

- `search_fake_docs`
- `send_fake_email`
- `read_fake_calendar`
- `read_fake_secret`

未授权工具请求会被拒绝，例如：

- `run_shell`
- `read_env`
- `delete_file`
- `curl`

## 外部请求检查

未发现外部请求逻辑：

- 无 HTTP URL provider。
- 无 OpenAI / Anthropic / 真实模型 API provider。
- 无 SMTP / IMAP / Gmail / Slack 等真实集成。
- 无企业系统地址。
- 无网络扫描逻辑。
- 无外部数据上传逻辑。

`run_agent_promptfoo.sh` 会拒绝包含外部 API、真实模型、企业目标、凭证或真实集成关键词的有效 promptfoo 配置。

## 凭证与敏感数据检查

- 未读取环境变量。
- 未读取真实 credential store。
- 未包含真实 API key、token、cookie 或客户数据。
- `HONEYTOKEN_AGENT_DEMO_123456` 是本地 fake honeytoken，仅用于测试输出防泄露。
- `read_fake_secret` 只返回 `REDACTED`。

## 命令行调用

Agent demo 可直接调用：

```bash
python3 sandbox/agent_demo/agent.py "Search fake docs for policy"
```

直接 provider 可调用：

```bash
python3 sandbox/agent_demo/agent_provider.py "{{prompt}}"
```

promptfoo provider 通过 `runners` basePath 调用：

```bash
python3 runners/agent_provider.py "{{prompt}}"
```

## JSON 证据字段

Agent 输出和日志包含：

- `timestamp`
- `input`
- `agent_goal`
- `tool_calls`
- `tool_name`
- `tool_args`
- `allowed`
- `denied_reason`
- `tool_result`
- `side_effect`
- `risk_signals`
- `followed_malicious_instruction`
- `leaked_secret`
- `unauthorized_tool_call`
- `write_action_attempted`
- `target`
- `result`

## dry-run 与 Phase 4.5 执行结果

Phase 4 只允许执行：

```bash
bash runners/run_agent_promptfoo.sh
```

Phase 4.5 已在人工确认后执行：

```bash
bash runners/run_agent_promptfoo.sh --execute
```

最终结果：6 passed，0 failed，0 errors。执行复盘见 `docs/phase4_5_execution_review.md`。

## 日志提交规则

已提交的历史 fake log 可作为本地学习证据保留。未来真实测试日志、环境文件、API key、真实 token 或企业数据不得直接提交 Git。

## 风险与限制

- 当前 demo 使用规则选择工具，不代表真实 Agent 规划系统风险覆盖完整性。
- 当前所有工具都是 fake tools，不评估真实邮件、日历、文件系统、云资源或数据库风险。
- Phase 4.5 执行前必须再次确认安全边界。

## 结论

Phase 4 设计仍限制在本地 `sandbox/agent_demo` 和 fake tools 范围内。未发现外部请求或真实凭证风险。本阶段可以执行 dry-run，但不应执行真实 Agent promptfoo 测试，除非进入 Phase 4.5 并获得人工确认。
