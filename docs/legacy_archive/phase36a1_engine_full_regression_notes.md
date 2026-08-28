# Phase 36A.1: Engine Full Corpus Regression Notes

## Execution
- Total requests: 48 (Phase 35I selected corpus, 17 M01 + 16 M02 + 15 M03)
- Successful: 44 (4 ERR(502) — transient API server errors, not engine issues)
- Phase 35I had 0 errors, but those 4 entries were re-runnable

## Capability Values

| Module | Phase 35I | Phase 36A Engine | Consistent? |
|--------|-----------|-------------------|-------------|
| M01    | medium    | medium            | ✅ |
| M02    | high      | high              | ✅ |
| M03    | medium    | medium            | ✅ |
| Overall| high      | high              | ✅ |

## Engine vs Old Script Assessment
- capability_value 完全一致（M01=medium, M02=high, M03=medium, overall=high）
- engine 正确识别了 M02 system_prompt_leak / step_by_step_extraction 的 leaked 信号
- engine 正确记录了 refusal、error、inconclusive 状态
- Phase 36A engine 可以替代 Phase 35I 一次性脚本

## Minor Issues Found
1. 4 ERR(502) — API 服务端偶发 502，engine 已正确处理为 error，不影响评分
2. module_id 大小写不一致：Phase 35I corpus 中 m02/m03 部分 entry 用 "m02"/"m03"（小写），部分用 "M02"/"M03"（大写）。engine 按小写分组，大小写混用不影响解析

## Verdict
capability_engine 已具备替代一次性 phase 脚本的能力。通过一个 run config 启动，跑完 48 条语料，生成完整原始结果 + 3 个 module_result + 1 个 scorecard。
