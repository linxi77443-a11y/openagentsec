# Phase 106A — M17 AI Asset & Exposure Surface Mapping MVP Notes

## Overview

M17 AI Asset & Exposure Surface Mapping 验证 AI 资产发现与暴露面映射能力，确保企业能够完整识别 AI 资产、准确评估暴露面、检测影子 AI、维护完整模型清单。

## Assessment Mode

- **Mode**: adversarial_validation
- **Phase**: 106A
- **Module**: M17 — AI Asset & Exposure Surface Mapping
- **Actor**: simulated_adversary

## Safety Boundaries

- 不连接真实资产管理系统、不连接真实CMDB、不连接真实云平台、不连接真实网络扫描器（real_asset_management_allowed=false, real_cmdb_allowed=false, real_cloud_platform_allowed=false, real_network_scanner_allowed=false）。
- 所有数据使用 `<SIM_...>` 合成占位符。
- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety_claimed: false
- controlled_replay_claimed: false

## Attack Categories (8 attack + 2 control = 10 entries)

1. **asset_discovery_omission** — 资产扫描遗漏影子 AI 模型端点
2. **exposure_surface_underestimation** — 暴露面评估低估间接输入向量
3. **shadow_ai_detection_failure** — 影子 AI 检测未能识别未授权外部 AI 服务
4. **model_inventory_incomplete** — 模型清单遗漏第三方预训练模型依赖
5. **api_endpoint_exposure** — AI 推理 API 端点公网暴露且缺乏认证
6. **training_data_leakage_path** — 训练数据存储暴露，可通过模型 API 间接提取
7. **deployment_config_misconfiguration** — 部署配置错误，调试模式暴露敏感信息
8. **third_party_ai_component_risk** — 第三方 AI 组件存在已知漏洞但未纳入清单

## Control Cases

1. **standard_asset_scan** — 标准资产扫描覆盖已知 AI 资产，与 CMDB 一致
2. **normal_exposure_assessment** — 标准暴露面评估确认端点认证和网络隔离正确

## Signals

- `asset_discovery_gap_detected` — 资产发现盲区检测
- `shadow_ai_risk_identified` — 影子 AI 风险识别
- `scan_coverage_incomplete` — 扫描覆盖不完整
- `exposure_underestimation_detected` — 暴露面低估检测
- `indirect_input_vectors_identified` — 间接输入向量识别
- `assessment_scope_incomplete` — 评估范围不完整
- `shadow_ai_detection_gap` — 影子 AI 检测盲区
- `vpn_proxy_bypass_risk` — VPN/代理绕过风险
- `detection_coverage_incomplete` — 检测覆盖不完整
- `model_inventory_gap` — 模型清单盲区
- `third_party_model_dependency_missing` — 第三方模型依赖缺失
- `supply_chain_risk_undetected` — 供应链风险未检测
- `api_endpoint_publicly_exposed` — API 端点公网暴露
- `authentication_missing` — 认证缺失
- `network_segmentation_violation` — 网络隔离违规
- `training_data_exposure_risk` — 训练数据暴露风险
- `data_lineage_incomplete` — 数据血缘不完整
- `model_api_data_leakage_path` — 模型 API 数据泄露路径
- `debug_mode_exposure` — 调试模式暴露
- `credential_in_deployment_config` — 部署配置中的凭据
- `config_misconfiguration_detected` — 配置错误检测
- `third_party_vulnerability_detected` — 第三方组件漏洞检测
- `component_not_in_inventory` — 组件未纳入清单
- `supply_chain_security_gap` — 供应链安全盲区

## Results Summary

- Total entries: 10 (8 attack + 2 control)
- Breakthrough detected: 0
- All 8 attack categories covered
- Validation checks passed

## Capability & Risk

- capability_value: high (evaluation effectiveness)
- risk_level: low (simulated residual risk)
- result_is_candidate_level: true
