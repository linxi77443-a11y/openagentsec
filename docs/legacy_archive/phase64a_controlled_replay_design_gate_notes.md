# Phase 64A — Controlled Scenario Replay Design Gate 说明

## 阶段性质

Phase 64A 是 **controlled replay design gate**（受控场景复测设计门），**不是 replay 执行**。

## 当前状态

| 检查项 | 值 |
|--------|-----|
| 阶段 | 设计门，非执行 |
| replay_executable | false |
| controlled_replay_execution_allowed | false |
| 是否执行 replay | 否 |
| 是否连接真实系统 | 否 |
| 是否使用真实账号 | 否 |
| 是否使用真实数据 | 否 |
| 是否执行真实攻击 | 否 |
| 是否产生 confirmed vulnerability | 否 |
| 是否声明 production safety | 否 |
| 是否新增攻击剧本 | 否 |
| 是否新增 corpus | 否 |
| 是否新增 run config | 否 |
| 是否生成 execution_results | 否 |
| 是否执行 capability_engine | 否 |
| 是否调用 API | 否 |

## 交付物说明

| 交付物 | 内容 |
|--------|------|
| controlled_scenario_replay_design_gate.md | 主设计门文档：准入标准、授权清单要求、环境要求、账号数据要求、回滚计划、人工复核门、日志要求、安全字段等 |
| controlled_replay_authorization_checklist.yaml | 授权清单：所有字段使用 `<SIM_...>` 占位符 |
| controlled_replay_environment_requirements.yaml | 环境要求 + 测试账号/数据要求 |
| controlled_replay_rollback_plan.yaml | 回滚计划：快照、步骤、中止条件、验证要求 |
| controlled_replay_logging_requirements.yaml | 日志 schema：字段定义、日志要求、禁止行为 |
| scripts/validate_phase64a_design_gate.py | 验证脚本：检查安全字段、文件完整性、禁止项 |

## 下一步（如需执行 replay）

1. 从设计门中筛选满足准入条件的候选项
2. 通过 **controlled replay readiness review** 确认授权、环境、账号、数据、回滚、日志与复核门均已满足
3. 生成独立的 **controlled replay execution 任务单**
4. 通过人工审批
5. 在新的任务单中执行 replay

**注意**：以上步骤均未执行。当前仅完成设计门阶段。
