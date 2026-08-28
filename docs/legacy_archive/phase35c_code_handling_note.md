# Phase 35C：代码处理原则

## 背景

Phase 35C（PRD v0.2.1 Capability-First Revision）是一次方向性调整，将项目重心从"合规流程 / 审批包 / dashboard / 静态规划优先"调整为"能力验证 + 业务价值优先"。本文记录当前代码处理原则，供后续阶段参考。

## 已保留内容

- **Phase 35C.0 及之前所有已提交成果**：包括 Phase 35 Promptfoo Integration Framework、Phase 35B Go/No-Go Packet、Phase 35C.0 Execution Readiness Gate 等。这些文件是合规体系的基础资产，保留不动。
- **已提交的 dashboard / release / roadmap 内容**：保留已提交版本，本阶段不扩展。

## 已回滚内容

- **Phase 35C "Controlled Promptfoo Dry Run / Static Execution Plan" 未提交变更**：包括重型 dry-run 规划文档、validate 脚本、dashboard 扩展等。这些属于合规优先方向的过度投入，不符合新方向，已删除。
- **Phase 35C "Minimum Visible Demo" 未提交变更**：包括 demo 配置、runbook、结果模板等。该方向已被 PRD 修订取代，已删除。

## 当前阶段原则

1. **只修 PRD 和 registry**：本阶段只新增 PRD 文档、module registry、工具-模块适配矩阵、代码处理说明。不实现新功能。
2. **不运行 promptfoo eval**：本阶段不做任何评估执行。
3. **不连接被测 API**：本阶段不触发任何外部 API。
4. **不调用 DeepSeek API**：DeepSeek judge 保持当前状态，不动。
5. **不读取 .local/**：不访问本地 secret 存储。
6. **不重新运行 Phase 32C 测试**：已有授权 API 回归结果保持原样。
7. **不修改原始 finding candidates**：已有 finding candidates 保持 candidate 状态。
8. **不新增测试用例**：不扩展评估语料。
9. **不实现新的评估模块**：当前只登记模块定义，不实现。
10. **不扩展 dashboard / release notes / roadmap 长文档**：这些暂不优先，后续按需补充。
11. **不生成 formal finding**：所有输出保持 assistant_review / needs_human_review。
12. **不提交 API key / Authorization header / 未脱敏 endpoint**：安全底线不变。

## 后续开发前提

**每个模块开发前，必须先输出实现规格单（implementation specification）**。规格单至少包含：

- 模块目标与业务价值
- 使用的工具链（promptfoo / garak / DeepSeek judge / 其他）
- 测试用例设计思路
- 预期输出格式
- 人工审核要求
- 安全边界

未输出规格单的模块不得进入开发阶段。

## 文件清单

| 文件 | 说明 |
|---|---|
| `docs/prd_v0_2_1_capability_first.md` | PRD v0.2.1：能力验证与业务价值优先版 |
| `capability_modules/module_registry.yaml` | 模块注册表 M01–M42 |
| `docs/tool_module_fit_matrix.md` | 工具-模块适配矩阵 |
| `docs/phase35c_code_handling_note.md` | 本文件：代码处理原则 |
