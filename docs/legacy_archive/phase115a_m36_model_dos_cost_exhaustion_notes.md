# Phase 115A — M36 Model DoS / Cost Exhaustion MVP Notes

## Summary

- Module: M36 — Model DoS / Cost Exhaustion
- Phase: 115A
- Assessment mode: adversarial_validation
- Total entries: 10 (8 attack + 2 control)
- Category coverage: 10 categories
- Breakthrough detected: 0
- Validation checks: passed

## Security Fields

- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety_claimed: false

## Attack Categories Covered

1. request_flooding_attack — 请求洪泛攻击，通过高频请求耗尽 API 配额和服务器资源
2. long_context_exhaustion — 长上下文耗尽，发送超长请求耗尽模型上下文窗口和内存资源
3. nested_call_loop — 嵌套调用循环，构造递归调用耗尽计算资源和 API 配额
4. resource_intensive_query — 资源密集型查询，构造计算密集型查询消耗大量 GPU/CPU 资源
5. cost_exhaustion_attack — 成本耗尽攻击，通过大量高成本请求耗尽组织 AI 预算
6. api_quota_exhaustion — API 配额耗尽，多账号配额滥用使合法用户无法使用服务
7. model_inference_overload — 模型推理过载，并发推理请求使模型服务性能严重下降
8. async_task_pileup — 异步任务堆积，堆积大量异步任务使任务队列溢出

## Control Cases

1. control_standard_request_handling — 标准推理请求处理
2. control_normal_resource_usage — 正常批量推理资源使用

## Notes

- All entries use `<SIM_...>` synthetic placeholders
- No real API gateway accessed
- No real billing system accessed
- No real model endpoint accessed
- No real quota system accessed
- Results are candidate-level, not production findings
- Requires human review for all attack cases
- Security fields: confirmed_vulnerability=false, formal_finding_allowed=false, production_safety_claimed=false
