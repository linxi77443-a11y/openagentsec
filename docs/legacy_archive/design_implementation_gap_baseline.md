# 设计-实现差距基线

## 对比

| 原始设计 | 当前实现 |
|----------|----------|
| 完整平台：corpus → compiler → curation → runner → sandbox → evidence → finding → severity → mitigation → retest | 集中在深窄子路径：fake tool trace → fake runtime → controlled replay |

当前实现属于"风险验证执行层"中的**工具调用授权边界验证**，不代表完整的企业 AI / Agent 安全评估平台主线。

## 这不是错误

这条深窄路径产出了可复用的 runtime 引擎和 replay 验证方法，是有价值的工程积累。但它不能替代平台主线。

## 后续方向

下一步应做**风险闭环纵切**：从企业 AI / Agent 风险出发，一次打通风险对象 → 验证方法 → 证据输出 → 整改 / 复测，而不是按缺失目录逐项补齐。
