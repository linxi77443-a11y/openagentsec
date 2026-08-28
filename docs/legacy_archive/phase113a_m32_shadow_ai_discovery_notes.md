# Phase 113A — M32 Shadow AI / Unauthorized AI Usage Discovery MVP Notes

## Summary

- Module: M32 — Shadow AI / Unauthorized AI Usage Discovery
- Phase: 113A
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

1. unauthorized_ai_tool_access — 未经授权的 AI 工具私自接入企业环境
2. shadow_model_deployment — 私自部署未经安全评估的 AI 模型
3. shadow_data_storage — 影子数据存储，AI 模型数据存储在未授权位置
4. ai_service_bypass_approval — AI 服务绕过审批流程直接使用
5. unauthorized_api_call — 未授权的 AI API 调用绕过安全监控
6. ai_asset_concealment — AI 资产隐瞒，隐藏已部署的 AI 资产信息
7. shadow_ai_risk_accumulation — 影子 AI 风险累积，未授权 AI 使用的风险逐渐积累
8. shadow_ai_data_exfiltration — 影子 AI 数据外泄，通过未授权 AI 服务外泄敏感数据

## Control Cases

1. control_standard_ai_usage_approval — 标准 AI 使用审批流程
2. control_normal_asset_registration — 标准 AI 资产登记流程

## Notes

- All entries use `<SIM_...>` synthetic placeholders
- No real AI asset management, shadow IT detection, or model deployment system accessed
- Results are candidate-level, not production findings
- Requires human review for all attack cases
