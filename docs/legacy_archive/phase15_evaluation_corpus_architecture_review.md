# Phase 15 Evaluation Corpus Architecture 复盘

## 目标

Phase 15 的目标是建立统一评估语料库目录 `corpus/`，覆盖 Chatbot、RAG、Agent、API、Business、Regression 六个 profile，使用统一 schema 定义语料结构，实现 test design 层与 testcases（执行层）、replays（人工 replay 层）、evidence（结果层）的四层分离。

## 交付清单

| 交付物 | 路径 | 状态 |
|---|---|---|
| Corpus 目录结构 | `corpus/` | ✅ |
| Schema 定义 | `corpus/corpus_schema.md` | ✅ |
| 总索引 | `corpus/corpus_index.yaml` | ✅ |
| Chatbot 语料（4 文件，14 条） | `corpus/chatbot/` | ✅ |
| RAG 语料（4 文件，14 条） | `corpus/rag/` | ✅ |
| Agent 语料（5 文件，16 条） | `corpus/agent/` | ✅ |
| API 语料（2 文件，6 条） | `corpus/api/` | ✅ |
| Business 语料（4 文件，8 条） | `corpus/business/` | ✅ |
| Regression 语料（3 文件，9 条引用） | `corpus/regression/` | ✅ |
| 文档更新 | `README.md` 等 10 文件 | ✅ |
| Generator 更新 | `generate_atlas_dashboard.py`、`generate_enterprise_report.py` | ✅ |
| Quality check 更新 | `runners/run_quality_check.sh` | ✅ |

## Corpus 统计

| Profile | 语料数 | corpus_id 前缀 | 执行模式 | 主要风险类别 |
|---|---|---|---|---|
| Chatbot | 14 | chatbot-pi/spe/sd/mb | local_sandbox | prompt injection、system prompt exposure、sensitive disclosure、multilingual bypass |
| RAG | 14 | rag-ipi/rp/fc/od | local_sandbox | indirect injection、RAG poisoning、fake citation、over-disclosure |
| Agent | 16 | agent-tmu/mp/sp/exf/rc | manual_replay | tool misuse、memory poisoning、skill poisoning、exfiltration、resource consumption |
| API | 6 | api-fgs/asb | documentation_only | smoke、auth、authorization、rate limiting |
| Business | 8 | business-so/xdr/pq/pm | manual_replay | SOC、XDR、policy QA、project management |
| Regression | 9 | regression-smoke/cs/ga | local_sandbox | core security regression、smoke tests |
| **合计** | **67（49 独立 + 9 引用）** | | | |

## 四层分离

```
┌─────────────────────────────────────────────┐
│  Corpus (test design)    ← Phase 15 新增    │
│  统一 schema、corpus_id、框架映射、预期行为    │
├─────────────────────────────────────────────┤
│  Testcases (execution)                       │
│  promptfoo 配置、provider、断言               │
├─────────────────────────────────────────────┤
│  Replays (manual observation)                │
│  Manual UI replay JSON 文件                   │
├─────────────────────────────────────────────┤
│  Evidence (results)                          │
│  promptfoo result JSON、脱敏后日志            │
└─────────────────────────────────────────────┘
```

## Schema 关键字段

- `corpus_id`：全局唯一 ID（如 `chatbot-pi-001`）
- `target_profile`：chatbot / rag / agent / api / business / regression
- `risk_category`：prompt_injection / system_prompt_exposure / sensitive_disclosure / multilingual_bypass / indirect_prompt_injection / rag_poisoning / fake_citation / over_disclosure / tool_misuse / memory_poisoning / skill_poisoning / exfiltration / resource_consumption / api_smoke / api_security_baseline / security_operations / xdr_assistant / policy_qa / project_management / regression / api_security_baseline
- `framework_mapping`：mitre_atlas / owasp_agentic / owasp_llm / red_team_phase
- `test_intent`：一句话描述测试目标
- `expected_behavior`：7 个布尔字段（should_refuse, should_block, should_not_reveal_system_prompt, should_not_leak_sensitive_data, should_not_call_unauthorized_tool, should_not_write_memory, should_not_execute_write_action）
- `risk_signals`：风险信号标签
- `severity_if_failed`：critical / high / medium / low
- `current_execution_mode`：local_sandbox / manual_replay / mock_harness / api_provider / browser_future / documentation_only
- `current_status`：active / regression / planned / deprecated / reference_only
- `refs`：regression 语料通过 corpus_id 引用原始条目

## 框架映射覆盖

| 框架 | 覆盖语料数 |
|---|---|
| MITRE ATLAS | 44 条（17 个 technique） |
| OWASP Agentic Top 10 | 15 条（6 个 ASI） |
| OWASP LLM | 15 条（1 个 placeholder） |

## 执行模式分布

| 模式 | 语料数 | 说明 |
|---|---|---|
| local_sandbox | 27 | 可本地执行 |
| manual_replay | 27 | 需人工 replay |
| documentation_only | 6 | 仅语料设计，无可执行 runner |

## 已知限制

- API 和 Business 语料暂无自动执行 runner，仅作语料设计。
- 部分 Agent 语料（tool misuse、exfiltration）仍为 manual_replay 模式，未接入现有 local_sandbox。
- Regression 语料通过 `corpus_id` 引用，不独立存在，自动化引用解析尚待实现。
- Corpus 与 testcases 之间的双向追踪尚未建立。

## 下一步建议

1. 为 API 语料创建可执行 runner（基于现有 API Provider Skeleton）。
2. 为 Business 语料接入手动 replay 评估流水线。
3. 实现 corpus → testcase 自动映射工具。
4. 扩展 Business 语料到更多企业场景（合规检查、DevSecOps、告警分析）。
