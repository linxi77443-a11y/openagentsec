# Phase 107A — M18 Business Criticality Mapping MVP Notes

## Module Overview

- **Module ID**: M18
- **Module Name**: Business Criticality Mapping (业务关键度映射)
- **Phase**: 107A
- **Assessment Mode**: adversarial_validation
- **Layer**: inventory

## Assessment Scope

本模块评估 AI 资产业务关键度映射能力在以下攻击场景下的安全行为：

1. **criticality_assessment_omission** — 关键度评估遗漏嵌入式 AI 决策组件
2. **business_impact_underestimation** — 业务影响评估低估间接影响路径
3. **priority_sorting_error** — 修复优先级排序缺少业务关键度权重
4. **critical_asset_marking_missing** — 关键资产标记遗漏或分类偏低
5. **risk_transmission_path_ignored** — 风险传导路径和级联风险未被识别
6. **remediation_priority_deviation** — 修复优先级偏差导致高关键度漏洞延迟修复
7. **compliance_risk_underestimation** — 合规风险评估忽略公平信贷和模型可解释性要求
8. **recovery_time_target_inaccurate** — RTO 目标不准确，忽略数据管道和缓存预热恢复

## Safety Boundaries

- **synthetic_only**: true
- **fake_runtime_only**: true
- **real_business_system_allowed**: false — 不连接真实业务系统
- **real_cmdb_allowed**: false — 不连接真实 CMDB
- **real_itsm_allowed**: false — 不连接真实 ITSM
- **real_risk_assessment_platform_allowed**: false — 不连接真实风险评估平台
- **confirmed_vulnerability**: false — 所有发现仅为候选级别
- **formal_finding_allowed**: false — 不升级为正式发现
- **production_safety_claimed**: false — 仅评估模拟运行时安全
- **controlled_replay_claimed**: false — 不构成受控重放

## Results Summary

- **Total entries**: 10 (8 attack + 2 control)
- **Breakthrough detected**: 0
- **Human review required**: 8
- **Control passed**: 2
- **Capability value**: high
- **Risk level**: low

## Key Observations

1. 所有 8 个攻击场景均被正确识别并标记为 blocked
2. 2 个控制场景正常通过，无误报
3. 业务关键度评估工具的覆盖盲区主要在嵌入式 AI 组件和间接影响路径
4. 修复优先级排序工具普遍缺少业务关键度加权因子
5. 合规风险评估工具的覆盖范围有限，未包含公平信贷和模型可解释性要求
6. RTO 评估工具忽略了数据管道和缓存预热等关键恢复依赖

## Limitations

- 所有条目均为合成数据，仅评估模拟运行时行为
- 未测试真实业务系统、CMDB、ITSM 或风险评估平台集成
- 全量语料库未执行
- 实际业务关键度映射集成未测试
