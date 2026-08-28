# Phase 4：本地 Agent 工具调用安全测试 dry-run 工作流

## 目标

建立只面向 `sandbox/agent_demo` 的最小 Agent 工具调用安全测试 dry-run 工作流，用于学习和验证：

- AI Agent Tool Invocation
- Indirect Prompt Injection against Agent
- Agent Tool Misuse
- Agent Context Poisoning
- Credentials from AI Agent Configuration
- Exfiltration via AI Agent Tool Invocation
- Fake write-action abuse
- Tool allowlist / denylist 控制

本阶段只完成设计、配置和 dry-run，不执行真实 promptfoo Agent 测试，不进入 Phase 4.5。

## 范围

- 目标：`sandbox/agent_demo`
- Agent demo：`sandbox/agent_demo/agent.py`
- fake tools：`sandbox/agent_demo/fake_tools/tools.py`
- 直接调用 provider：`sandbox/agent_demo/agent_provider.py`
- Promptfoo provider：`runners/agent_provider.py`
- Promptfoo 配置：`runners/promptfoo.agent.yaml`
- Runner：`runners/run_agent_promptfoo.sh`
- 未来结果：`reports/evidence/promptfoo_agent_result.json`
- 本地日志：`sandbox/agent_demo/agent_log.jsonl`

## 安全边界

- 只允许测试本地 `sandbox/agent_demo`。
- 只允许调用 fake tools。
- 不访问外部网络。
- 不连接真实模型 API。
- 不读取真实环境变量、真实 API key 或真实凭证。
- 不访问真实邮件、真实日历、真实文件系统敏感路径。
- 不对真实系统执行写操作。
- fake write tools 必须默认 dry-run。
- 所有 secret 必须是假数据或 honeytoken。
- 所有工具调用输出 JSON 证据。
- 本阶段只做 dry-run。

## fake tool allowlist

仅允许：

- `search_fake_docs`
- `send_fake_email`
- `read_fake_calendar`
- `read_fake_secret`

工具约束：

- `search_fake_docs`：只能搜索内置 fake docs。
- `send_fake_email`：只能模拟发送，永远 `dry_run=true`、`sent=false`、`side_effect=dry_run_only`。
- `read_fake_calendar`：只能读取内置 fake calendar。
- `read_fake_secret`：只能返回 `REDACTED` 和 fake secret 访问说明，不输出完整 honeytoken。

## JSON 输出字段

Agent 输出至少包含：

- input
- agent_goal
- tool_calls
- tool_name
- tool_args
- allowed
- denied_reason
- tool_result
- side_effect
- risk_signals
- followed_malicious_instruction
- leaked_secret
- unauthorized_tool_call
- write_action_attempted
- target
- timestamp

## Promptfoo Agent 用例

`runners/promptfoo.agent.yaml` 覆盖：

1. 正常工具调用测试。
2. 非授权工具调用测试。
3. fake secret 读取测试。
4. indirect prompt injection against agent 测试。
5. fake email 写操作测试。
6. tool exfiltration simulation 测试。

每个测试包含 description、vars、assert、ATLAS technique、OWASP Agentic risk 和 expected behavior。

## dry-run

```bash
bash runners/run_agent_promptfoo.sh
```

预期只输出将要执行的命令、目标、provider 和结果路径，不执行测试。

## execute

Phase 4 不执行。Phase 4.5 已在人工确认后运行：

```bash
bash runners/run_agent_promptfoo.sh --execute
```

Phase 4.5 最终结果为 6 passed，0 failed，0 errors。执行复盘见 `docs/phase4_5_execution_review.md`。

## Phase 4.5 前置确认

进入真实本地执行前，需要确认：

1. 仍只测试 `sandbox/agent_demo`。
2. 仍只调用 fake tools。
3. 不新增外部 provider。
4. 不接入真实模型 API。
5. 不读取环境变量中的 API key 或真实凭证。
6. 不连接真实邮件、真实日历、真实文件系统敏感路径或企业系统。
7. 同意生成 `reports/evidence/promptfoo_agent_result.json` 和 `sandbox/agent_demo/agent_log.jsonl`。
