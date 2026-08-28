# Phase 63A — Red/Blue/Purple Retest Mapping 说明

## 映射性质

- **模拟评估**: 本映射文件是 adversarial_validation 模式下的红蓝紫复测对照表，所有数据基于模拟测试结果
- **非 controlled_replay**: 本映射不控制任何生产系统、不触发真实告警、不连接真实外部服务
- **非 production_safety**: 本映射不声明任何生产安全性
- **非 confirmed_vulnerability**: 所有 breakthrough 候选均为 exploitable_behavior_observed，需人工审查确认
- **非 formal_finding**: 本映射不产生正式发现报告

## 结构说明

- 20 个 breakthrough 候选 (BRT-001 ~ BRT-020)，覆盖 10 个 playbook
- 每个候选含 Red（攻击端证据）、Blue（防守端建议）、Purple（复测设计）三部分
- Red: 记录攻击过程、突破信号、受影响边界
- Blue: 预防/检测/响应三层控制建议
- Purple: 复测用例设计，包含通过/失败条件和人工审查要求

## 防御视角

- 所有候选标注 `requires_human_review: true`，确保人工介入
- 4 个安全字段全部为 false，防止自动升级
- 10 个 distinct affected_boundary 标记了本次评估覆盖的防守边界
- Purple 部分的 pass/fail condition 为复测提供了明确的判定标准

## 关键限制

1. 映射基于模拟数据，不代表真实系统行为
2. 复测用例 (retest_case_id: RTC-001 ~ RTC-020) 尚未在真实环境中执行
3. Blue 部分的防守建议未经验证
4. 所有 exploit_chain_steps 为模拟推演，非真实攻击记录
5. 未覆盖 playbook control_case 对应的防守边界
