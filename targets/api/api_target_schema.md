# API Target Schema

Phase 11 API Provider Skeleton 使用本 schema 描述未来测试环境 API target。当前阶段仅支持 dry-run readiness 检查，不执行真实 HTTP 请求。

## 必填字段

| 字段 | 类型 | 要求 |
|---|---|---|
| `target_name` | string | 本地 target 名称，不得包含真实系统标识 |
| `target_type` | string | `chatbot_api` 或 `rag_api` |
| `environment` | string | 只能是 `test` 或 `staging`，禁止 `production` |
| `authorization_status` | string | 当前样例为 `pending`；未来 execute 必须为 `approved` |
| `execute_enabled` | boolean | Phase 11 必须为 `false` |
| `endpoint_placeholder` | string | 只能使用占位符，例如 `**TEST_CHATBOT_API_ENDPOINT**` |
| `request_method` | string | 当前样例使用 `POST` |
| `request_body_template` | object | 未来请求体模板，当前只用于 dry-run 文档化 |
| `response_mapping` | object | 未来响应字段映射，当前只用于 mock response 说明 |
| `auth` | object | 只能包含占位符 token，不得包含真实 token |
| `rate_limit` | object | 必须限制请求速率和单次总量 |
| `data_policy` | object | 必须禁止真实敏感数据并要求脱敏 |
| `write_actions_allowed` | boolean | 必须为 `false` |
| `forbidden_operations` | list | 必须列出 production、真实凭证、真实数据、写操作和批量测试禁令 |
| `evidence_output` | string | dry-run evidence 输出路径 |

## 安全约束

- 不允许真实 URL。
- 不允许真实 token、API key、账号或密码。
- 不允许 `environment: production`。
- 不允许 `execute_enabled: true`。
- 不允许 `write_actions_allowed: true`。
- `authorization_status` 不是 `approved` 时，未来 execute 必须拒绝。
- Phase 11 即使看到 `--execute` 也必须拒绝。
- 所有 evidence 必须进入 `reports/evidence/` 并经过脱敏检查。

## data_policy

```yaml
data_policy:
  use_real_sensitive_data: false
  use_fake_secret: true
  redaction_required: true
```

## rate_limit

```yaml
rate_limit:
  max_requests_per_minute: 5
  max_total_requests_per_run: 20
```
