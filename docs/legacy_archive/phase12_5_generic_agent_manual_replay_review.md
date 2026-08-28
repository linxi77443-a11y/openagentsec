# Phase 12.5 Generic Agent Manual Replay 本地验证复盘

## 本阶段目标

验证 Generic Agent ATLAS Assessment Pack 的 fake manual replay 样例是否能进入现有 Manual UI Replay 评估闭环，包括 provider 增强、风险信号识别、evidence 生成和 dashboard/report 更新。

## 执行命令

```bash
bash runners/run_manual_ui_promptfoo.sh          # dry-run
bash runners/run_manual_ui_promptfoo.sh --execute  # execute
bash scripts/generate_all_reports.sh              # dashboard/report 更新
bash runners/run_quality_check.sh                 # quality check
```

## Replay 样例来源

`replays/manual_ui_samples/generic_agent_manual_replay_sample.json`

## Generic Agent Replay 场景

10 个 fake 场景，覆盖全部计划攻击面：

| ID | 类别 | ATLAS Technique |
|---|---|---|
| generic-agent-001 | identity_spoofing | atlas.ai_agent_context_poisoning |
| generic-agent-002 | goal_hijacking | atlas.ai_agent_context_poisoning |
| generic-agent-003 | memory_poisoning | atlas.ai_agent_context_poisoning |
| generic-agent-004 | tool_metadata_poisoning | atlas.ai_agent_tool_poisoning |
| generic-agent-005 | tool_return_poisoning | atlas.ai_agent_tool_data_poisoning |
| generic-agent-006 | fake_secret_access | atlas.credentials_from_ai_agent_configuration |
| generic-agent-007 | exfiltration_via_external_channel | atlas.exfiltration_via_ai_agent_tool_invocation |
| generic-agent-008 | human_confirmation_bypass | atlas.data_destruction_via_ai_agent_tool_invocation |
| generic-agent-009 | skill_poisoning | atlas.ai_agent_tool_poisoning |
| generic-agent-010 | resource_consumption_loop | atlas.agentic_resource_consumption |

## Manual UI Replay Execute 结果

| 项目 | 值 |
|---|---|
| 总测试数 | 16（原 6 + 新增 10） |
| Pass | 16 |
| Fail | 0 |
| Error | 0 |
| Generic Agent replay 数量 | 10 |
| Generic Agent replay pass/fail/error | 10 / 0 / 0 |

## Evidence 文件位置

`reports/evidence/promptfoo_manual_ui_result.json`

## 已识别风险信号

Provider 已成功识别以下 Agent 专属风险信号：

- `identity_spoofing_attempt`
- `goal_hijacking_attempt`
- `memory_poisoning_attempt`
- `tool_metadata_poisoning_attempt`
- `tool_return_injection_attempt`
- `unauthorized_secret_access_attempt`
- `exfiltration_attempt`
- `human_confirmation_bypass_attempt`
- `skill_poisoning_attempt`
- `resource_consumption_attack_attempt`

## 新增 Boolean 字段

Provider 新增以下布尔字段（当前全部为 false，因为 fake Agent 响应均正确拒绝）：

- `memory_poisoning_attempt`
- `skill_poisoning_attempt`
- `tool_exfiltration_attempt`
- `human_confirmation_bypass_attempt`
- `resource_consumption_attempt`

后续如果 provider 用于真实 Agent 响应评估，这些字段可用于断言。

## 未识别但应在后续增强的风险信号

当前 provider 的 denial 检测基于关键词匹配（中英文拒绝词），可能存在以下限制：

1. **跨轮上下文污染**：无法检测跨多轮对话的渐进式诱导
2. **工具链组合攻击**：无法检测多个工具组合使用的恶意链
3. **时间窗口攻击**：无法检测延迟触发的恶意指令
4. **语义级绕过**：无法检测不使用关键词的语义级绕过
5. **工具返回深度污染**：无法检测嵌套在 JSON 结构中的恶意指令

这些需要未来在 Provider 中引入更复杂的检测逻辑（如模式匹配增强、工具调用链分析）。

## Provider 增强内容

本阶段对 `providers/manual_replay_provider.py` 做了以下增强：

1. **字段映射**：支持 generic_agent 格式的 `user_input`/`agent_response` 字段
2. **Profile 传播**：从 `target_profile`/`replay_mode` 字段回填 `profile`/`assessment_mode`
3. **Redaction 传播**：从 metadata 层传播 `redaction_applied` 到记录级
4. **风险信号**：新增 10 个 Agent 专属风险信号分类
5. **Boolean 字段**：新增 `memory_poisoning_attempt`、`skill_poisoning_attempt`、`tool_exfiltration_attempt`、`human_confirmation_bypass_attempt`、`resource_consumption_attempt`
6. **Denial 检测**：扩展中文拒绝词检测，覆盖所有 fake Agent 响应中的拒绝模式

## Dashboard / Report 更新情况

已更新：

- `dashboard/dashboard_data.json`
- `dashboard/index.md`
- `dashboard/atlas_dashboard.html`
- `reports/generated_atlas_assessment_report.md`

Manual UI Replay 结果从 6/0/0 更新为 16/0/0。

## 当前限制

- Provider 仅基于关键词匹配做 denial 检测，不适用于真实 Agent 响应分析
- Generic Agent 的新 Boolean 字段当前均为 false（fake Agent 正确拒绝），未被触发
- Provider 的 risk signal 仅基于 `test_category` 字段映射，不基于输出语义分析
- 不连接任何真实 Agent、真实 API、真实页面或真实工具

## 下一阶段建议

1. 为 Manual UI provider 增加 tool_call 链分析能力，检测跨轮工具调用风险
2. 增加语义级绕过检测（不依赖关键词）
3. 为 Generic Agent 开发 mock tool harness，使 10 项 planned 测试能力变为可执行
4. 在 mock harness 就绪后，为 Generic Agent 增加 `--execute` 支持（仅限 fake tools）
