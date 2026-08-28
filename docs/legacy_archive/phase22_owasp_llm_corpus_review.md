# Phase 22: OWASP LLM Top 10 Crosswalk + Core LLM Corpus Hardening

## 目标

1. 将 OWASP LLM Top 10 placeholder 替换为完整的映射层（数据文件、到 ATLAS/Corpus/Controls/Supply Chain 的交叉映射、报告语言模板）
2. 强化核心 LLM 语料覆盖（6 个新语料文件，26 条 planned 条目）
3. 更新现有 corpus 文件的 OWASP LLM 映射

## 关键约束

- 不执行任何测试（--execute）
- 不连接真实 API/Agent/页面
- 不安装 garak / PyRIT / Browser Automation
- 不声称 OWASP 认证
- 所有新 corpus 条目标记为 `planned`，不误标为 `active` 或 `executed`

## 交付物

### OWASP LLM 映射层（6 个文件）

| 文件 | 用途 |
|---|---|
| `owasp/llm_top10_2025.yaml` | LLM01–LLM10 风险定义，含 coverage 校准 |
| `owasp/llm_to_atlas_crosswalk.yaml` | LLM → ATLAS technique 交叉映射 |
| `owasp/llm_to_corpus_mapping.yaml` | LLM → Corpus 映射与缺口分析 |
| `owasp/llm_to_controls_mapping.yaml` | LLM 控制项映射 |
| `owasp/llm_to_supply_chain_mapping.yaml` | LLM → 供应链映射 |
| `owasp/llm_report_language.md` | 报告语言模板 |

### 新增语料（6 个文件，26 条条目，全部 planned）

| 文件 | 条目数 | 对应 LLM |
|---|---|---|
| `corpus/chatbot/improper_output_handling.yaml` | 4 | LLM05 |
| `corpus/chatbot/misinformation.yaml` | 4 | LLM09 |
| `corpus/rag/vector_embedding_weaknesses.yaml` | 4 | LLM08 |
| `corpus/rag/stale_or_conflicting_knowledge.yaml` | 4 | LLM04 |
| `corpus/api/unbounded_consumption_baseline.yaml` | 4 | LLM10 |
| `corpus/regression/owasp_llm_regression.yaml` | 6 | LLM01/02/05/06/07/09 |

### 更新文件

- 10 个现有 corpus 文件的 `owasp_llm` 字段：`OWASP_LLM_PLACEHOLDER` → 正确 LLM ID
- `corpus/corpus_index.yaml`：增加 `by_owasp_llm`、新增 corpus 条目、总条目数 49 → 75
- `owasp/README.md`：增加 OWASP LLM 章节和文件结构
- `corpus/README.md`：更新 corpus 总数
- `release/release_manifest_v1_3.yaml`：更新 limitation 和 next_phase
- `release/capability_matrix_v1_3.md`：OWASP LLM 和 Corpus 行更新
- `release/known_limitations_v1_3.md`：OWASP LLM limitation 更新
- `release/system_release_v1_3.md`：一句话定位、能力主线、框架映射层、下一阶段建议
- `release/execution_status_matrix_v1_3.md`：增加 OWASP LLM 方法论行
- `release/next_phase_roadmap_v1_3.md`：Phase 22 标记完成，Phase 24→Phase 23 重排

## 覆盖状态校准

| LLM | 状态 | 说明 |
|---|---|---|
| LLM01 Prompt Injection | covered_by_local_tests | Chatbot/RAG/Agent 本地测试 |
| LLM02 Sensitive Information Disclosure | covered_by_local_tests | Chatbot/RAG/API 本地测试 |
| LLM03 Supply Chain | partially_covered | BOM 和映射层，无测试执行 |
| LLM04 Data and Model Poisoning | partially_covered | RAG 投毒已测，stale/conflict 未执行 |
| LLM05 Improper Output Handling | partially_covered | 4 条语料 planned |
| LLM06 Excessive Agency | covered_by_local_tests | Agent 工具滥用本地测试 |
| LLM07 System Prompt Leakage | covered_by_local_tests | Chatbot 本地测试 |
| LLM08 Vector and Embedding Weaknesses | partially_covered | 4 条语料 planned |
| LLM09 Misinformation | partially_covered | Fake citation 已测，misinfo 未执行 |
| LLM10 Unbounded Consumption | partially_covered | Agent 资源消耗已测，API 未执行 |

## 风险与限制

- 所有新语料为 planned 状态，未执行测试
- OWASP LLM 映射为内部映射参考，不构成认证或合规声明
- LLM08 和 LLM10 的测试需外部工具（向量数据库、速率限制）支持
- 语料使用 fake/safe/low-risk 数据，无真实 URL/token/email/endpoint
