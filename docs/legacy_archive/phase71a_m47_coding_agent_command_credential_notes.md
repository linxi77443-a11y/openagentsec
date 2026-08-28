# Phase 71A — M47 Coding Agent Command and Credential Boundary MVP Notes

## 范围

本阶段是 **M47 Coding Agent Command and Credential Boundary MVP**，使用 adversarial_validation 模式验证 Coding Agent 在面对 synthetic 开发上下文中的越权命令执行诱导和凭据泄露诱导时，是否能保持开发环境安全边界。

## 评估配置

| 字段 | 值 |
|------|-----|
| 评估模式 | adversarial_validation |
| 攻击者类型 | malicious_insider / low_privileged_operator |
| 攻击目标 | dev_environment_unauthorized_command_induction / dev_environment_credential_exposure_attempt / dev_environment_agent_permission_confusion |
| 执行引擎 | simulate_defense（synthetic fake runtime） |
| 数据 | `<SIM_REPO_...>` / `<SIM_COMMAND_...>` / `<SIM_SECRET_PLACEHOLDER_...>` / fake / synthetic only |
| 真实仓库 | 未访问 |
| 真实命令 | 未执行 |
| 真实凭据 | 未读取 |
| 真实文件 | 未读取 |
| 真实工具 | 未调用 |
| 真实 API | 未调用 |

## 核心信号（按 M47-MVP-01 任务单）

| 信号 | 说明 | 计数 |
|------|------|------|
| `command_execution_blocked` | 越权命令执行被阻断 | 5 |
| `operational_attack_command_blocked` | 攻击性操作命令生成被阻断 | 5 |
| `safe_alternative_provided` | 提供安全替代方案（如静态审查） | 7 |
| `secret_exposure_blocked` | 凭据泄露被阻断 | 4 |
| `redaction_applied` | 脱敏已应用 | 4 |
| `credential_reuse_blocked` | 凭据跨上下文复用被阻断 | 4 |
| `defensive_guidance_provided` | 防御指导已提供 | 4 |
| `human_review_required` | 需要人工复核 | 9 |

## 结果摘要

11 条 MVP cases（9 攻击场景 + 2 control case）。所有攻击场景的命令执行边界和凭据泄露边界被保持。所有 control case 正常通过。

| 指标 | 值 |
|------|-----|
| capability_value | high |
| risk_level | low |

## 安全声明

- `confirmed_vulnerability`: false
- `formal_finding_allowed`: false
- `production_safety_claimed`: false
- `controlled_replay_claimed`: false
- `result_is_candidate_level`: true
- `breakthrough_detected` 仅表示 `simulated_capability_signal`
- 所有数据使用 `<SIM_REPO_...>` / `<SIM_COMMAND_...>` / `<SIM_SECRET_PLACEHOLDER_...>` / fake / synthetic only
- 不访问真实仓库
- 不执行真实命令
- 不读取真实凭据
- 不读取真实文件
- 不调用真实工具
- 不调用真实 API
- 不生成真实 payload

## 非目标

- 不声明 production_ready
- 不声明 controlled_replay_ready
- 不访问真实仓库
- 不执行真实命令
- 不读取真实凭据
- 不读取真实文件
- 不调用真实工具
- 不调用真实 API
- 不连接真实系统
- 不执行 controlled replay
- 不生成真实 payload
