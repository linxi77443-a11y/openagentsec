# Phase 19：External Evaluation Tool Adapter Planning 复盘

## 本阶段目标

建立外部评估工具 adapter 规划层，使系统未来可以有序接入 garak、PyRIT、Agent benchmark、Browser Automation 和 API Provider 等能力。

本阶段只做 adapter planning、schema、映射、风险边界、文档、dashboard/report 展示和 quality check。

本阶段不安装、不运行任何外部工具，不运行任何 `--execute`，不连接真实 API、真实 Agent、真实页面、真实模型、真实工具或外部网络。

## 新增 external_tools 文件

| 文件 | 用途 |
|---|---|
| `external_tools/README.md` | 目录总览和设计原则 |
| `external_tools/external_tool_evidence_schema.md` | 外部工具结果统一 evidence schema |
| `external_tools/external_tool_risk_boundary.md` | 外部工具接入风险边界 |
| `external_tools/external_tool_to_atlas_owasp_mapping.yaml` | 外部工具到 ATLAS/OWASP/corpus/evidence 映射 |
| `external_tools/external_tool_adapter_index.yaml` | 6 个 adapter 的索引、状态和优先级 |
| `external_tools/garak_adapter_plan.md` | garak adapter 设计计划 |
| `external_tools/pyrit_adapter_plan.md` | PyRIT adapter 设计计划 |
| `external_tools/agent_benchmark_adapter_plan.md` | AgentDojo / AgentDyn adapter 设计计划 |
| `external_tools/browser_automation_adapter_plan.md` | Browser Automation adapter 设计计划 |
| `external_tools/api_provider_adapter_plan.md` | API Provider adapter 设计计划 |
| `external_tools/external_tool_report_appendix_template.md` | 外部工具报告附录模板 |

## garak adapter plan 摘要

garak adapter 定位为未来通用 LLM 漏洞扫描执行器，适合 prompt injection、leakage、jailbreak、misinformation / hallucination、toxicity / unsafe content 等观察。

适用目标为授权测试环境 Chatbot API、RAG API、FastGPT / Dify / Coze 测试 API。不适用于真实生产系统、真实写操作 Agent 或未授权外部 API。

当前状态：`design_ready`，未安装、未运行。

## PyRIT adapter plan 摘要

PyRIT adapter 定位为未来 AI Red Team 编排层，适合多轮流程、attack strategy orchestration、scorer/evaluator、human-led + automated red teaming。

它与 `red_team/` 方法论、`corpus/` 语料、`finding_severity_model.md` 严格联动。PyRIT scorer 输出只能作为 severity model 的输入信号，不替代人工判断。

当前状态：`design_ready`，未安装、未运行。

## Agent benchmark adapter plan 摘要

Agent benchmark plan 覆盖 AgentDojo 和 AgentDyn：

- AgentDojo：参考 tool-using agent prompt injection 的 task / attack / defense 结构。
- AgentDyn：参考 dynamic open-ended tasks，补充复杂任务、动态规划、间接注入和 cascading failure。

两者未来应优先转换成本地 fake tools / mock tasks，再接入 Generic Agent Harness，不应直接连接真实工具链。

当前状态：`design_ready`，未安装、未运行。

## Browser automation adapter plan 摘要

Browser Automation adapter 定位为未来把无 API 页面或测试环境页面的输入输出转成 Manual UI Replay 格式，而不是直接成为自主浏览器 Agent。

前置条件包括测试环境页面、测试账号、授权、低频、无真实写操作、可回滚和可人工停止。

当前状态：`planned`，未安装、未运行、未访问页面。

## API provider adapter plan 摘要

API Provider adapter 基于 Phase 11 API Provider Skeleton，规划未来正式测试环境 API 接入所需能力：target config、auth handling、request mapping、response mapping、rate limit、redaction、evidence output。

FastGPT 临时验证结果仅作为能力验证，不纳入正式主流程。

当前状态：`dry_run_skeleton_ready`，不代表真实 API tested / passed。

## External evidence schema 摘要

统一 schema 字段覆盖：tool_name、tool_type、adapter_name、adapter_status、execution_mode、target_profile、target_asset_id、target_environment、input_source、corpus_reference、test_case_reference、raw_output_location、normalized_result、risk_signals、MITRE ATLAS mapping、OWASP mapping、severity_suggestion、evidence_confidence、redaction_applied、sensitive_data_detected、execution_boundary、limitations、created_at。

Phase 19 中所有 adapter_status 不得超过 `design_ready`，API Provider adapter 例外为 `dry_run_skeleton_ready`。

## Risk boundary 摘要

外部工具接入前必须满足：

- RoE / 授权范围明确。
- target config 明确。
- 测试账号和测试环境隔离。
- 请求频率限制。
- 数据脱敏和 evidence 留存策略。
- 停止条件和回滚计划。
- 禁止生产系统、真实写操作、真实凭证入库和未授权目标。

## ATLAS / OWASP mapping 摘要

`external_tool_to_atlas_owasp_mapping.yaml` 覆盖 6 类映射：

| 工具 | 目标方向 | 当前状态 |
|---|---|---|
| garak | chatbot / rag / OWASP LLM placeholder / ATLAS prompt injection / leakage / unsafe output | design_ready |
| PyRIT | red_team orchestration / multi-turn attack / scoring / severity model | design_ready |
| AgentDojo | agent tool-use prompt injection / ASI01 / ASI02 / ASI06 | design_ready |
| AgentDyn | dynamic open-ended agent tasks / ASI01 / ASI06 / ASI08 / ASI09 | design_ready |
| Browser Automation | manual replay automation / UI assessment | planned |
| API Provider | test API assessment / chatbot / rag / workflow | dry_run_skeleton_ready |

## Dashboard / Report 更新情况

- `scripts/generate_atlas_dashboard.py`：新增 `external_tools` 数据块、adapter count、status、priority、HTML/Markdown 区块。
- `scripts/generate_enterprise_report.py`：新增 Section 19 External Evaluation Tool Adapter Planning。
- `scripts/generate_all_reports.sh`：新增 external_tools 输入检查和边界声明。
- `dashboard/README.md`：新增 External Evaluation Tool Adapters 说明。
- `reports/evidence_index.md`：新增 Phase 19 planning/schema/mapping 记录。

## Quality Check 结果

新增 Phase 19 检查：

- external_tools/ 目录存在性。
- 11 个 external_tools 文件存在性。
- 禁止真实 URL、token、email、endpoint、Bearer 等敏感模式。
- 禁止声称外部工具已安装。
- 禁止声称 garak / PyRIT / AgentDojo / AgentDyn 已运行。
- dashboard/report 不得声称外部工具已执行。
- adapter_status 不得超过 design_ready，api_provider_adapter 可为 dry_run_skeleton_ready。

## 当前限制

1. 没有安装任何外部工具。
2. 没有运行任何外部工具。
3. 没有生成 external tool evidence。
4. 没有连接真实 API、真实 Agent、真实页面或外部网络。
5. Adapter plan 只说明未来接入路径，不代表工具能力已经集成。
6. 外部工具输出未来仍需人工复核，不能直接作为最终安全结论。

## 下一阶段建议

1. 优先完善 API Provider target config、RoE 和凭证处理策略。
2. 若接入 garak，先做 local mock adapter，不连接真实 API。
3. 若接入 PyRIT，先做 human-led dry-run plan，不做自主多轮攻击。
4. Browser Automation 应先生成 Manual UI Replay 格式，再进入 evidence/report。
5. Agent benchmark 应优先转换为 Generic Agent Harness 的 fake task，而不是直接运行 benchmark。
