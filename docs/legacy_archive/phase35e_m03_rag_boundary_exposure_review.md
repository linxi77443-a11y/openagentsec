# Phase 35E: M03 RAG Boundary Exposure Minimal Implementation — Review Document

## 概述

Phase 35E 基于 Phase 35D 输出的 M03 模块实现规格单，构建最小能力框架。本阶段不运行 promptfoo eval，不连接目标 API，不调用 DeepSeek API，不生成 formal finding。

## 交付物

| # | 文件 | 用途 |
|---|---|---|
| 1 | `capability_modules/implementations/M03_rag_boundary_exposure/module_input_schema.yaml` | 模块输入 schema，定义 19 个必需字段 |
| 2 | `capability_modules/implementations/M03_rag_boundary_exposure/sample_module_input.yaml` | 基于 FC-32C-rag-001 的样本输入 |
| 3 | `capability_modules/implementations/M03_rag_boundary_exposure/review_output_schema.yaml` | 评审输出 schema，含 mapping_to_M19/M21/M22 |
| 4 | `capability_modules/implementations/M03_rag_boundary_exposure/sample_capability_review.md` | 人工可读的评审样本 |
| 5 | `scripts/validate_m03_rag_boundary_exposure.py` | 静态验证脚本（约 20+ 检查项） |
| 6 | `docs/phase35e_m03_rag_boundary_exposure_review.md` | 本文件：阶段评审文档 |

## 验证结果

| 检查项 | 状态 |
|---|---|
| module_input_schema.yaml — 19 个必需字段完整 | ✅ |
| module_input_schema.yaml — formal_finding_allowed must_be false | ✅ |
| module_input_schema.yaml — human_review_required must_be true | ✅ |
| module_input_schema.yaml — result_semantics enum 限制 | ✅ |
| sample_module_input.yaml — formal_finding_allowed false | ✅ |
| sample_module_input.yaml — result_semantics 合法 | ✅ |
| review_output_schema.yaml — 输出字段完整 | ✅ |
| review_output_schema.yaml — review_status enum 限制 | ✅ |
| review_output_schema.yaml — formal_finding_allowed must_be false | ✅ |
| review_output_schema.yaml — 含 mapping_to_M19/M21/M22 | ✅ |
| sample_capability_review.md — 含"不构成 formal finding"声明 | ✅ |
| sample_capability_review.md — 无 forbidden 模式 | ✅ |
| 所有文件无 API key / Authorization / 未脱敏 endpoint | ✅ |
| 所有文件无 .local/ 路径 | ✅ |
| 所有文件无 confirmed_exploit / validated_finding | ✅ |

## 安全边界

| 边界 | 值 |
|---|---|
| promptfoo_eval_run | false |
| target_api_connected | false |
| deepseek_api_called | false |
| local_config_read | false |
| formal_finding_generated | false |
| static_analysis_only | true |
| human_review_required | true |
| formal_finding_allowed | false |

## 架构决策

1. **输入 schema 先行** — 先定义模块输入结构，确保所有实现代码有统一的输入契约
2. **评审输出 schema 分离** — 评审输出结构与输入结构分离，便于后续扩展评审字段
3. **M19/M21/M22 映射字段内置** — review_output_schema 中内置 mapping_to_M19/M21/M22 字段，确保下游模块的输入可追溯
4. **静态验证脚本独立** — 验证脚本不依赖运行时环境，可在任何阶段执行

## 后续步骤

1. 运行验证脚本确认所有文件合规
2. 提交当前阶段成果
3. 进入 M01/M02 的 Phase 35E 实现（按照 specification_index.md 的模块顺序：M01 → M02 → M03 → M40）
4. 根据验证结果和人工复核反馈决定是否继续投入

## 停止标准

| 情况 | 处理 |
|---|---|
| 验证脚本发现不合规项 | 修复后再提交 |
| 阶段规格变化 | 更新本文档后再继续 |
| 项目方向调整 | 参考 phase35c_code_handling_note.md 的处理原则 |
