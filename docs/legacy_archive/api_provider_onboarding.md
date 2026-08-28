# API Provider Onboarding

## API Provider 是什么

API Provider 是未来把 ATLAS AI Security Assessment System 从本地 sandbox 扩展到受控测试环境 API 的接入层。Phase 11 只提供 skeleton 和 dry-run readiness 检查，不执行真实 HTTP 请求。

## 适用对象

- Chatbot API
- RAG API
- 后续 Agent API

## Phase 11 当前支持什么

- `targets/api/` target schema 和占位符样例。
- Chatbot API / RAG API provider skeleton。
- mock response / fake response 样例。
- dry-run runner。
- dashboard / report 中展示 API Provider Skeleton 状态。
- quality check 中检查 API target 和 provider 安全边界。

## Phase 11 当前不支持什么

- 不连接真实 API。
- 不访问外部网络。
- 不读取真实 token、API key、账号或密码。
- 不读取 `.env` 或环境变量中的真实凭证。
- 不访问生产系统或企业测试环境。
- 不执行真实 HTTP 请求。
- 不支持任何真实 API execute。
- 不做 Agent 通用评估包。
- 不引入浏览器自动化。

## 接入真实测试环境 API 前需要准备的信息

| 信息 | 要求 |
|---|---|
| API 类型 | Chatbot API、RAG API 或后续 Agent API |
| endpoint | 只能在后续已批准阶段填入测试环境地址 |
| request method | 例如 POST |
| request body | 字段名、模板、固定测试参数 |
| response mapping | 输出字段、上下文字段、错误字段 |
| auth method | 测试账号或测试 token 的安全加载方式 |
| rate limit | 每分钟请求数、单次运行最大请求数 |
| test account | 独立测试账号，不使用个人账号 |
| test data | fake / synthetic / test fixture，不使用真实客户数据 |
| authorization approval | 审批记录、范围、窗口、责任人 |
| rollback plan | 出错时停止、回滚、通知和 evidence 处理方式 |

## 禁止事项

- 禁止 production。
- 禁止真实客户数据。
- 禁止真实 secret 进入仓库、配置或 evidence。
- 禁止真实写操作。
- 禁止 uncontrolled batch testing。
- 禁止在未批准阶段启用 execute。

## Dry-run 流程

```bash
bash runners/run_api_chatbot_provider.sh
bash runners/run_api_rag_provider.sh
```

Dry-run 只读取 `targets/api/*.yaml` 占位符配置，输出 readiness evidence：

- `reports/evidence/api_chatbot_provider_dry_run.json`
- `reports/evidence/api_rag_provider_dry_run.json`

## 未来 execute 流程草案

未来如需接入测试环境 API，应先完成：

1. 审批测试范围和窗口。
2. 配置测试环境 endpoint。
3. 设计安全的测试凭证加载方式。
4. 确认 rate limit 和请求总量。
5. 确认 test account / test data 隔离。
6. 确认日志、脱敏、evidence 保留策略。
7. 更新 quality check。
8. 人工确认后再启用 execute。

Phase 11 不实现上述 execute。

## Evidence 位置

- Chatbot API skeleton dry-run：`reports/evidence/api_chatbot_provider_dry_run.json`
- RAG API skeleton dry-run：`reports/evidence/api_rag_provider_dry_run.json`

## Dashboard / Report 更新方式

运行：

```bash
bash scripts/generate_all_reports.sh
```

Dashboard 和报告会展示 API Provider Skeleton 状态，但不会把 dry-run readiness 伪装成真实 API 测试通过。
