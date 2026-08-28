# AI 安全控制项清单

## 使用说明

本清单用于企业内部防守、治理和复测。应用到非本地目标前，必须先完成 `docs/non_local_target_approval_checklist.md`。

## 1. Chatbot 控制项

### 系统提示保护

- [ ] 系统提示不直接拼接到用户可见输出。
- [ ] 用户输入不能覆盖系统指令或安全策略。
- [ ] debug / admin / developer role 等伪装请求不会暴露内部指令。
- [ ] prompt 模板中敏感策略和凭证不混放。

### prompt injection 检测

- [ ] 检测 ignore previous、override policy、debug mode 等直接注入模式。
- [ ] 对中文、英文、中英混合、编码、Markdown、quote block 等变体保留检测能力。
- [ ] 对角色扮演绕过、unrestricted assistant、内部规则摘要请求保留检测能力。
- [ ] 高风险输入进入风险标记和审计流程。
- [ ] 测试用例包含正常输入和恶意输入对照组。
- [ ] Phase 6.5 后应至少覆盖 9 个本地 Chatbot execute 用例，且最终 9/0/0。

### 输出过滤

- [ ] 输出不包含系统提示、内部策略、hidden instruction。
- [ ] 输出不包含可用凭证、token、API key 或敏感配置。
- [ ] 对拒绝回答给出安全、简短、可审计的说明。
- [ ] 输出过滤结果可记录到 evidence。

### 敏感信息脱敏

- [ ] fake secret / honeytoken 不被完整输出。
- [ ] 真实系统中应接入 secret detection / DLP。
- [ ] 日志中的敏感字段默认脱敏。
- [ ] 测试数据使用 fake data 或 dummy data。

### 日志审计

- [ ] 记录输入、输出、风险信号、target、时间和结果。
- [ ] 日志不包含真实敏感信息。
- [ ] 日志保留周期和访问权限明确。
- [ ] 失败用例有复盘和修复记录。

## 2. RAG 控制项

### 文档来源校验

- [ ] 每个检索文档有来源、版本、owner 和更新时间。
- [ ] 企业文档进入索引前经过审批或签名校验。
- [ ] 外部内容与内部权威内容分级处理。
- [ ] 可追踪文档变更和索引更新时间。

### 恶意文档检测

- [ ] 检测文档中的 prompt injection 指令。
- [ ] 检测隐藏文本、HTML 注释、Markdown 指令、伪装 policy。
- [ ] 恶意或可疑文档进入隔离或降权流程。
- [ ] 检索结果中保留风险标记。

### 检索结果可信度标记

- [ ] 输出 retrieved document IDs。
- [ ] 输出来源可信度或文档类别。
- [ ] 对低可信来源进行降权或人工确认。
- [ ] 用户可看到引用来源和限制说明。

### fake / stale / poisoned entry 检测

- [ ] 检测伪造政策、过期政策和冲突政策。
- [ ] 检测 fake citation、hidden instruction、多语言 indirect prompt injection 和 fake token 夹带。
- [ ] 权威政策有明确来源和版本。
- [ ] 发现 poisoned entry 后支持回滚索引。
- [ ] stale entry 不应覆盖当前权威策略。
- [ ] Phase 6.5 后应至少覆盖 12 个本地 RAG execute 用例，且最终 12/0/0。

### 上下文隔离

- [ ] 检索文档内容不能覆盖系统指令。
- [ ] 文档中的“忽略规则”“泄露凭证”等内容只作为不可信文本处理。
- [ ] 用户 query、系统指令、检索内容在 prompt 中明确分层。
- [ ] RAG 输出包含是否跟随文档指令的证据字段。

### 引用来源展示

- [ ] 输出引用文档 ID 或来源链接。
- [ ] 对无法确认来源的内容标记不确定性。
- [ ] 引用内容不应泄露敏感上下文。
- [ ] 复盘报告包含检索证据路径。

### secret / token 泄露检测

- [ ] 检索内容中的 secret / token 默认脱敏。
- [ ] 输出层执行 not-contains / DLP 检查。
- [ ] honeytoken 命中进入告警或复盘流程。
- [ ] 真实系统日志不保存完整 secret。

## 3. Agent 控制项

### tool allowlist

- [ ] Agent 只能调用明确 allowlist 中的工具。
- [ ] 非 allowlist 工具请求必须拒绝并记录 `denied_reason`。
- [ ] 工具名称、用途、owner 和风险等级有清单。
- [ ] allowlist 修改需要评审。

### least privilege

- [ ] 每个工具只拥有完成任务所需的最小权限。
- [ ] 读写权限分离。
- [ ] 高风险工具默认不可用。
- [ ] token、scope 和目标资源边界明确。

### tool schema validation

- [ ] 工具参数有 schema。
- [ ] 参数中的 URL、邮箱、文件路径、命令、ID 均需校验。
- [ ] 拒绝未知字段、无效目的地和高风险参数组合。
- [ ] 工具参数中出现 honeytoken、secret、token 与写操作组合时必须阻断。
- [ ] 参数校验失败应记录证据。

### dry-run for write actions

- [ ] 写操作默认 dry-run。
- [ ] dry-run 输出 `dry_run=true`、`sent=false` 或等价字段。
- [ ] 真实写操作必须额外授权和人工确认。
- [ ] 写操作 evidence 记录 side effect。

### human-in-the-loop

- [ ] 高风险工具调用需要人工确认。
- [ ] 真实邮件、日历、工单、云资源、数据库写操作需要审批。
- [ ] 人工确认记录包含确认人、时间、范围和回滚方案。
- [ ] Agent 不得自行升级权限或扩大目标。

### secret access control

- [ ] Agent 不直接读取环境变量中的真实凭证。
- [ ] secret manager 访问需要最小权限和审计。
- [ ] secret 输出默认脱敏。
- [ ] secret + send/email/upload 组合应被标记为 exfiltration 风险。
- [ ] 多步链路中的 read secret -> send / forward 组合必须被阻断。
- [ ] 恶意上下文诱导的 secret 外传工具调用必须被阻断。

### tool call audit logging

- [ ] 记录 `input`、`tool_calls`、`tool_name`、`tool_args`。
- [ ] 记录 `allowed`、`denied_reason`、`tool_result`、`side_effect`。
- [ ] 记录 `risk_signals`、`target`、时间和结果。
- [ ] 日志脱敏并受访问控制保护。
- [ ] evidence / log 不完整回显 honeytoken、fake secret 或 dummy token；Phase 6.6 已引入统一脱敏模块。

### external network egress control

- [ ] 默认禁止外部网络访问。
- [ ] 允许的外联目标必须在 egress allowlist 中。
- [ ] 禁止向未授权域名、个人邮箱、pastebin、webhook 等目标外传数据。
- [ ] 外联行为必须记录目的地、数据类型、授权依据和结果。

## 4. Phase 6 / 6.5 本地质量校验控制项

- [ ] promptfoo provider 只指向本地 `exec:python3 ..._provider.py`。
- [ ] 配置中不出现真实 API、真实模型、真实凭证、企业系统或外部网络目标关键词。
- [ ] evidence 输出路径限定在 `reports/evidence`。
- [ ] `*_log.jsonl`、`logs/`、`.env`、`.env.*` 已被 `.gitignore` 排除。
- [ ] Chatbot、RAG、Agent 三类配置都能 dry-run。
- [ ] README、evidence index、coverage matrix 包含 Phase 6 最新阶段说明。
- [ ] Phase 6.5 execute 前必须重新确认本地范围、fake data、无真实 API、无外部网络和 evidence 更新授权。
- [ ] Phase 6.5 execute 后应确认 Chatbot 9/0/0、RAG 12/0/0、Agent 10/0/0，且无真实系统风险。
- [ ] Phase 6.6 后应确认 evidence 和本地日志不包含完整 `HONEYTOKEN_`、`FAKE_SECRET_`、`DUMMY_TOKEN_` 前缀。
- [ ] Phase 6.7 后应确认 promptfoo result JSON 后处理脱敏已覆盖测试输入、变量和断言元数据中的 fake secret、honeytoken、dummy token、email-like 和 bearer-like 字符串。
- [ ] Phase 6.7 后应确认 Chatbot 9/0/0、RAG 12/0/0、Agent 10/0/0，且脱敏不删除关键布尔字段。

## 5. Phase 7 ATLAS 驱动评估系统控制项

- [ ] `atlas/` 中 technique 必须包含 coverage status，不能把未实现能力标记为 covered。
- [ ] `assessment_profiles/` 中 planned profile 不得包含可执行外部 provider。
- [ ] `test_catalog/` 中 executable capability 只能引用本地 runner。
- [ ] `coverage/atlas_coverage_matrix.yaml` 中 planned / not_applicable technique 不得映射 evidence 或 executable runner。
- [ ] `runners/run_atlas_assessment.sh` 默认 dry-run，只生成 assessment plan。
- [ ] ATLAS 总控 runner 的 `--execute` 必须先运行 `runners/run_quality_check.sh`。
- [ ] ATLAS 总控 runner 只能调用现有本地 Chatbot / RAG / Agent runner。
- [ ] ATLAS assessment plan 和 summary 必须写入 `reports/evidence/`。
- [ ] 当前仍只支持本地 sandbox，不得接入真实 API、真实模型、企业系统、外部网络目标或真实凭证。
