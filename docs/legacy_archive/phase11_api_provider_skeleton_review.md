# Phase 11 API Provider Skeleton Review

## 本阶段目标

Phase 11 新增测试环境 API Provider Skeleton，为未来接入企业 AI 应用测试环境 Chatbot / RAG API 提供配置、provider、runner、mock response、文档、dashboard/report 展示和质量检查基础。

## 新增文件

- `targets/api/api_target_schema.md`
- `targets/api/chatbot_api_target_sample.yaml`
- `targets/api/rag_api_target_sample.yaml`
- `targets/api/mock_responses/chatbot_api_mock_response.json`
- `targets/api/mock_responses/rag_api_mock_response.json`
- `providers/api_provider_common.py`
- `providers/api_chatbot_provider.py`
- `providers/api_rag_provider.py`
- `runners/promptfoo.api_chatbot.yaml`
- `runners/promptfoo.api_rag.yaml`
- `runners/run_api_chatbot_provider.sh`
- `runners/run_api_rag_provider.sh`
- `docs/api_provider_onboarding.md`

## Provider 行为

- 默认只支持 dry-run readiness 检查。
- 只读取 `targets/api/*.yaml` 占位符配置。
- 不 import `requests`。
- 不 import `urllib`。
- 不执行真实 HTTP 请求。
- 不读取 `.env`。
- 不读取真实环境变量凭证。
- 输出统一 JSON，并接入 `utils.redaction`。
- 即使传入 `--execute`，本阶段也必须拒绝并报告 blocked reason。

## Target schema

Target schema 位于 `targets/api/api_target_schema.md`。样例 target 明确：

- `environment` 只能为 `test` 或 `staging`。
- `authorization_status` 当前为 `pending`。
- `execute_enabled: false`。
- endpoint 和 token 均为 placeholder。
- `write_actions_allowed: false`。
- `data_policy.redaction_required: true`。
- rate limit 为每分钟 5 次、单次运行最多 20 次。

## Runner 行为

- `bash runners/run_api_chatbot_provider.sh`
- `bash runners/run_api_rag_provider.sh`

两个 runner 默认 dry-run，生成 readiness evidence。若传入 `--execute`，runner 直接拒绝，不调用真实 API。

## 是否连接真实 API

否。Phase 11 未连接任何真实 API。

## 是否访问外部网络

否。Phase 11 provider 不包含网络调用逻辑。

## 是否读取真实凭证

否。Phase 11 target 只包含 placeholder，不读取 `.env` 或真实环境变量。

## 是否允许 execute

否。Phase 11 skeleton 不允许真实 API execute。

## Dry-run 输出

- `reports/evidence/api_chatbot_provider_dry_run.json`
- `reports/evidence/api_rag_provider_dry_run.json`

输出字段包括 provider 名称、模式、target、readiness 状态、blocked reasons、network / API / credential 标志和 redaction 状态。

## Dashboard / report 更新情况

Dashboard 和生成报告新增 API Provider Skeleton 区块。若只有 dry-run evidence，状态显示为 `dry_run_ready`；不会显示为真实 API tested / passed。

## 当前限制

- 不能评估真实 API。
- 不能加载真实凭证。
- 不能验证真实响应质量。
- 不能用于 production 或企业测试环境。
- 不能替代后续授权、账号隔离、日志、脱敏和回滚设计。

## 下一阶段建议

下一阶段应继续完善测试环境 API Provider 设计，重点是授权流程、测试账号、凭证加载边界、请求限速、日志脱敏、错误处理和人工确认流程，而不是直接启用真实 API execute。
