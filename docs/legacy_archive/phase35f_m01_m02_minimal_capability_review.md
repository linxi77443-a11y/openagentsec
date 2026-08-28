# Phase 35F: M01 / M02 Minimal Capability Implementation — Review Document

## 概述

Phase 35F 基于 Phase 35D 输出的 M01 / M02 模块实现规格单，为两个 P0 基础能力模块（提示注入与绕过、系统提示词泄露）构建最小能力框架。本阶段不运行 promptfoo eval，不连接目标 API，不调用 DeepSeek API，不生成 formal finding。

参考 Phase 35E M03 的实现结构，但未抽象公共框架——每个模块保持独立的 schema、sample、review 文件，便于独立审查和维护。

## 交付物

| # | 文件 | 用途 |
|---|---|---|
| 1 | `capability_modules/implementations/M01_prompt_injection_bypass/module_input_schema.yaml` | M01 输入 schema，20 个必需字段 |
| 2 | `capability_modules/implementations/M01_prompt_injection_bypass/sample_module_input.yaml` | 基于 FC-32C-gtc_chatbot-mb-001 的样本输入 |
| 3 | `capability_modules/implementations/M01_prompt_injection_bypass/review_output_schema.yaml` | M01 评审输出 schema，含 M21/M22/M25 映射 |
| 4 | `capability_modules/implementations/M01_prompt_injection_bypass/sample_capability_review.md` | M01 人工可读评审样本 |
| 5 | `capability_modules/implementations/M02_system_prompt_leakage/module_input_schema.yaml` | M02 输入 schema，21 个必需字段 |
| 6 | `capability_modules/implementations/M02_system_prompt_leakage/sample_module_input.yaml` | 基于 FC-32C-gtc_chatbot-spe-001 的样本输入 |
| 7 | `capability_modules/implementations/M02_system_prompt_leakage/review_output_schema.yaml` | M02 评审输出 schema，含 M21/M22/M25 映射 |
| 8 | `capability_modules/implementations/M02_system_prompt_leakage/sample_capability_review.md` | M02 人工可读评审样本 |
| 9 | `scripts/validate_m01_m02_minimal_capabilities.py` | 静态验证脚本 |
| 10 | `docs/phase35f_m01_m02_minimal_capability_review.md` | 本文件：阶段评审文档 |

## M01 最小能力实现摘要

- **module_input_schema.yaml**: 20 个必需字段，包括 prompt_injection_variant、bypass_language、encoding_or_transformation_used、target_policy_or_guardrail
- **sample_module_input.yaml**: 基于 FC-32C-gtc_chatbot-mb-001（法语注入绕过），formal_finding_allowed: false，human_review_required: true
- **review_output_schema.yaml**: 输出结构包含 prompt_injection_bypass_observed、multilingual_bypass_likelihood、encoding_or_transformation_bypass_likelihood、guardrail_bypass_likelihood、mapping_to_M21/M22/M25
- **sample_capability_review.md**: 评审模板含注入风险判断、多语言绕过评估、能力缺失清单、不构成 formal finding 声明

## M02 最小能力实现摘要

- **module_input_schema.yaml**: 21 个必需字段，包括 leakage_target、leakage_method、encoding_or_transformation_used、possible_system_prompt_exposure、possible_developer_instruction_exposure、possible_internal_policy_exposure
- **sample_module_input.yaml**: 基于 FC-32C-gtc_chatbot-spe-001（Base64 解码提取完整系统提示词），formal_finding_allowed: false，human_review_required: true
- **review_output_schema.yaml**: 输出结构包含 system_prompt_leakage_observed、developer_instruction_leakage_likelihood、internal_policy_leakage_likelihood、encoding_based_leakage_likelihood、mapping_to_M21/M22/M25
- **sample_capability_review.md**: 评审模板含泄露风险判断、编码提取评估、能力缺失清单、不构成 formal finding 声明

## 安全边界确认

| 边界 | 值 |
|---|---|
| promptfoo_eval_run | false |
| target_api_connected | false |
| deepseek_api_called | false |
| local_config_read | false |
| formal_finding_generated | false |
| test_cases_added | false |
| promptfoo_runner_implemented | false |
| static_analysis_only | true |
| human_review_required | true |
| formal_finding_allowed | false |

## 能力缺口

1. M01/M02 当前只有结构框架，未关联 promptfoo 配置的实际执行
2. 缺少自动化输出解析器（需后续阶段实现）
3. 缺少与已有 finding candidates 的结构化关联验证
4. 未实现跨模块的 review 汇总机制

## 下一步建议

1. 运行验证脚本确认所有文件合规
2. 提交当前阶段成果
3. 考虑为 M01/M02/M03 实现统一的 review queue 入口
4. 后续阶段可在最小能力框架基础上，逐步接入 promptfoo 执行和输出解析
