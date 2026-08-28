# Phase 62A — Adversarial Validation Mode Schema Addendum Notes

## 任务性质

本任务是纯 schema / 字段定义 / 校验规则设计：
- 不是攻击剧本开发
- 未创建 corpus
- 未创建 run config
- 未生成 execution_results
- 未执行 capability_engine
- 未调用 API
- 未连接真实系统
- 未进入 adversarial_validation 测试
- 未进入 controlled replay

## 交付物

| 文件路径 | 状态 | 说明 |
|---------|------|------|
| `capability_modules/schemas/adversarial_validation_schema.yaml` | ✅ | 统一 schema，包含输入字段、结果字段、攻击成功信号、默认值 & 校验规则 |
| `scripts/validate_adversarial_validation_schema.py` | ✅ | 11 组校验规则，覆盖 AC-1 ~ AC-10 |
| `docs/phase62a_adversarial_validation_schema_addendum_notes.md` | ✅ | 本文件 |

## Schema 覆盖总结

### §5 输入字段（8/8）

| 字段 | 类型 | 必填 |
|------|------|------|
| `assessment_mode` | string | ✅ |
| `actor` | string | ✅ |
| `attacker_profile` | string | ✅ |
| `attacker_type` | string | ✅ |
| `adversarial_playbook_type`（§6） | string | ✅ |
| `attack_objective` | string | ✅ |
| `attack_chain` | list | ✅ |
| `expected_defensive_behavior` | string | ✅ |

### §7 结果字段（7/7）

| 字段 | 类型 | 默认值 |
|------|------|--------|
| `breakthrough_detected` | boolean | false |
| `breakthrough_type` | string | null |
| `exploit_chain_candidate` | list | — |
| `evidence_trace` | list | — |
| `confirmed_vulnerability` | boolean | false |
| `formal_finding_allowed` | boolean | false |
| `requires_human_review` | boolean | false |

### §8 攻击成功信号（3 级分类）

| 级别 | 自动升级限制 |
|------|-------------|
| `capability_signal` | 不得升级为 `confirmed_vulnerability` / `formal_finding` / `production_safety` / `controlled_replay` |
| `simulated_capability_signal` | 同上 |
| `requires_human_review` | 同上 |

### §9 约束规则（BRK-001）

| 条件 | 强制 | 禁止 |
|------|------|------|
| `breakthrough_detected == true` | `requires_human_review=true` | `confirmed_vulnerability=true`, `formal_finding_allowed=true` |

### 默认安全值

| 字段 | 默认值 |
|------|--------|
| `confirmed_vulnerability` | false |
| `formal_finding_allowed` | false |
| `production_safety_claimed` | false |
| `controlled_replay_claimed` | false |

### 校验规则（13 条）

| ID | 规则 |
|----|------|
| AV-SCHEMA-001 | `assessment_mode` 必须为 `adversarial_validation` |
| AV-SCHEMA-002 | `attacker_type` 必填 |
| AV-SCHEMA-003 | `attack_objective` 必填 |
| AV-SCHEMA-004 | `attack_objective` 必须属于 schema 枚举值 |
| AV-SCHEMA-005 | `confirmed_vulnerability` 必须为 false |
| AV-SCHEMA-006 | `formal_finding_allowed` 必须为 false |
| AV-SCHEMA-007 | `production_safety_claimed` 必须为 false |
| AV-SCHEMA-008 | `controlled_replay_claimed` 必须为 false |
| AV-SCHEMA-009 | 攻击成功信号不得自动升级为 confirmed vulnerability |
| AV-SCHEMA-010 | `evidence_trace` schema 定义不得缺失 |
| AV-SCHEMA-011 | `exploit_chain_candidate` schema 定义不得缺失 |
| AV-SCHEMA-012 | `adversarial_playbook_type` 必填且属于 §6 枚举值 |
| AV-SCHEMA-013 | `breakthrough_detected=true` 时强制 `requires_human_review=true`，且 `confirmed_vulnerability` 和 `formal_finding_allowed` 必须为 false |

## 约束遵守

| 约束 | 状态 |
|------|------|
| 未创建 corpus | ✅ |
| 未创建 run config | ✅ |
| 未生成 execution_results | ✅ |
| 未执行 capability_engine | ✅ |
| 未调用 API | ✅ |
| 未连接真实系统 | ✅ |
| 未开发攻击剧本 | ✅ |
| 未进入 controlled replay | ✅ |
| confirmed_vulnerability=false | ✅ |
| formal_finding_allowed=false | ✅ |
| assessment_mode=adversarial_validation | ✅（schema 定义，非本次执行） |
