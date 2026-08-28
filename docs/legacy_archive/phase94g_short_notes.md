# Phase-94G Short Notes

## 范围

将 Phase-94C 的 7 个候选 workstream 转化为可独立下发的完整任务包。

## 生成的任务包

| task_id | type | mode | module |
|---------|------|------|--------|
| M12-RT-094 | module_development | defensive_evaluation | M12 |
| M15-RT-094 | module_development | defensive_evaluation | M15 |
| M38-XM-094 | module_development | adversarial_validation | M38 |
| M08-MT-094 | module_development | adversarial_validation | M08 |
| Phase-94D | review_cleanup | not_applicable | — |
| Phase-94E | review_cleanup | not_applicable | — |
| Phase-94F | design_gate | not_applicable | — |

## 关键约束

- 每个任务包独立 validator，不使用批次 validator
- defensive_evaluation 和 adversarial_validation 不混合
- 7 个 duplicate claim check 全部为 false
- coverage_credit_requested=0 for Phase-94D/E/F
- Phase-94G 不执行任何评估，不修改 Registry

## 不变项

- 不执行任何模块 corpus
- 不创建 execution_results
- 不授予 coverage credit
- 保持 simulated_runtime_safety，production_safety=out_of_scope
