# Phase 18：AI/ML-BOM + Supply Chain Mapping 复盘

## 本阶段目标

建立 AI/ML-BOM（Bill of Materials）清单和供应链风险映射层，将系统从"安全评估 + 治理工作台"扩展为"评估 + 治理 + 供应链追溯工作台"。

本阶段不新增攻击测试能力，不运行任何 `--execute`，不连接真实模型仓库、真实供应商系统或真实依赖扫描工具。

## 新增 supply_chain 文件（11 个）

| 文件 | 用途 |
|---|---|
| `supply_chain/README.md` | 目录总览和系统组件关系 |
| `supply_chain/ai_ml_bom_schema.md` | 9 类组件字段定义（BOM Metadata / Model / Dataset / Embedding / Tool / Prompt / External API / Runtime / Dependency） |
| `supply_chain/sample_ai_ml_bom.yaml` | 5 个样例 BOM（与 5 个 inventory 资产一一对应） |
| `supply_chain/model_provenance_checklist.md` | 模型来源可追溯性检查清单（7 类检查） |
| `supply_chain/dataset_knowledge_base_inventory.md` | 数据集/知识库来源清单（5 个样例） |
| `supply_chain/tool_plugin_mcp_inventory.yaml` | 工具/插件/MCP 依赖清单（4 个 fake 工具 + 占位符） |
| `supply_chain/prompt_template_inventory.yaml` | 提示词模板依赖清单（8 个模板记录） |
| `supply_chain/external_api_dependency_inventory.yaml` | 外部 API 依赖清单（3 个 mock 服务 + 占位符） |
| `supply_chain/supply_chain_risk_register_template.yaml` | 供应链风险登记表模板（6 条 sample risk entries） |
| `supply_chain/supply_chain_to_atlas_owasp_mapping.yaml` | 15 条供应链风险到 ATLAS/OWASP/NIST 映射 |
| `supply_chain/supply_chain_report_appendix_template.md` | 供应链报告附录模板 |

## AI/ML-BOM Schema 摘要

9 类组件字段体系：

1. **BOM Metadata**：bom_id, asset_id, bom_version, created_date, last_reviewed_date, review_frequency
2. **Model Component**：model_id, provider, name, version, deployment_mode, fine_tuned, base_model, license_type, supply_chain_risk
3. **Dataset / KB Component**：dataset_id, name, data_source, data_type, sensitivity, update_frequency, provenance_verified
4. **Embedding / Vector Component**：embedding_model, vector_store, version, dimension
5. **Tool / Plugin / MCP Component**：tool_id, name, type, provider, version, permission_level
6. **Prompt / Policy Component**：prompt_id, name, type, version, source
7. **External API / Service Component**：service_id, name, provider, endpoint_type, authentication, data_processing_location
8. **Runtime / Infrastructure Component**：runtime_id, name, type, version, provider
9. **Dependency Relationship**：dependency_id, from_component, to_component, relationship_type, critical_path

## Sample BOM 摘要

5 个样例 BOM，与 inventory 中的 5 个资产一一对应：

| BOM ID | Asset ID | 模型组件 | 数据集组件 | 工具组件 | 外部 API | 依赖关系 |
|---|---|---|---|---|---|---|
| bom_sample_internal_chatbot | sample_internal_chatbot | mock_chatbot_v1 | 1 | 0 | 0 | 2 |
| bom_sample_policy_rag_assistant | sample_policy_rag_assistant | mock_rag_v1 | 1 | 0 | 0 | 3 |
| bom_sample_generic_agent | sample_generic_agent | mock_agent_v1 | 0 | 4 | 2 | 5 |
| bom_sample_fastgpt_workflow_api | sample_fastgpt_workflow_api | mock_workflow_v1 | 1 | 0 | 1 | 2 |
| bom_sample_manual_ui_chatbot | sample_manual_ui_chatbot | null | 0 | 0 | 0 | 1 |

## Supply Chain Risk Register 摘要

6 条 sample risk entries：

| Risk ID | Asset | 风险描述 | Severity | 依赖类型 |
|---|---|---|---|---|
| SCRISK-001 | sample_generic_agent | 外部工具提供商供应链风险 | medium | external_api |
| SCRISK-002 | sample_policy_rag_assistant | 数据来源未验证 | high | dataset |
| SCRISK-003 | sample_fastgpt_workflow_api | 外部 API 依赖未评估 | medium | external_api |
| SCRISK-004 | sample_generic_agent | MCP/Plugin 供应链未评估 | high | plugin_mcp |
| SCRISK-005 | sample_internal_chatbot | 模型提供商依赖风险 | medium | model |
| SCRISK-006 | sample_generic_agent | 提示词模板篡改风险 | critical | prompt_template |

## ATLAS/OWASP/NIST Mapping 摘要

15 条供应链风险映射，覆盖：

| 供应链风险类别 | 覆盖状态 |
|---|---|
| Model Provider Compromise | not_assessed |
| Dataset / KB Poisoning | partially_assessed |
| Embedding Model Dependency | not_assessed |
| Vector Store Dependency | not_assessed |
| Tool / Plugin Provider Compromise | not_assessed |
| MCP Server Compromise | not_assessed |
| External API / Service Provider Compromise | not_assessed |
| Prompt Template Tampering | partially_assessed |
| Runtime / Framework Dependency Vulnerability | not_assessed |
| Supply Chain Dependency Confusion | not_assessed |
| Model Malicious Fine-Tuning | not_assessed |
| Data Pipeline Supply Chain Attack | not_assessed |
| Third-Party Inference API Data Leakage | not_assessed |
| Open Source Component License Violation | not_assessed |
| Dependency Deprecation / End-of-Life | not_assessed |

## 更新文件

### inventory/ 更新

- `inventory/sample_ai_asset_inventory.yaml`：5 个资产各新增 `related_bom` 字段
- `inventory/ai_asset_inventory_schema.md`：新增第 10 类 Supply Chain References 字段定义
- `inventory/ai_asset_inventory_index.yaml`：新增 `by_bom_status` 维度

### governance/ 更新

- `governance/governance_to_security_assessment_crosswalk.md`：新增 BOM → Supply Chain Risk 映射表
- `governance/ai_risk_governance_checklist.md`：新增第 13 类 Supply Chain & BOM Governance（9 项检查）
- `governance/governance_report_appendix_template.md`：Governance Scope 新增 supply_chain/
- `governance/README.md`：新增 supply_chain/ 关联说明

### Dashboard / Report 生成器更新

- `scripts/generate_atlas_dashboard.py`：
  - CURRENT_PHASE → Phase 18
  - SCOPE 新增 supply chain 描述
  - SUPPLY_CHAIN_DIR 检测
  - supply_chain_data 数据块
  - EVIDENCE_INDEX 新增 5 个 supply_chain 路径
  - KNOWN_GAPS 更新 AI 供应链描述
  - ROADMAP 新增 Phase 18
  - Markdown 新增 AI/ML-BOM + Supply Chain Mapping 区块
  - HTML 新增 supply-chain nav 和 section
- `scripts/generate_enterprise_report.py`：
  - Phase → Phase 18
  - 新增 Section 18：AI/ML-BOM + Supply Chain Mapping（10 个文件 + 关键映射 + 当前状态）
  - 附录新增 11 个 supply_chain 文件
  - 限制列表新增 AI/ML-BOM sample 声明
- `scripts/generate_all_reports.sh`：
  - REQUIRED_INPUTS 新增 5 个 supply_chain 文件
  - 新增 2 条 boundary 声明

## 文档更新情况

共更新 12 份文档：

- `README.md`：新增 Phase 18 阶段状态行和 supply_chain/ 目录说明
- `docs/atlas_assessment_system_guide.md`：新增 Phase 18 完整说明章节
- `docs/assessment_workflow_v1.md`：评估流程总图新增 AI/ML-BOM 步骤
- `docs/daily_operation_guide.md`：新增查阅 AI/ML-BOM 操作说明
- `docs/capability_matrix_v1.md`：新增 AI/ML-BOM 能力行
- `docs/release_notes_v1.md`：新增 Phase 18 完成状态
- `docs/roadmap.md`：Phase 18 标记为已完成，后续编号推移
- `docs/learning_summary.md`：新增 Phase 18 关键经验
- `reports/evidence_index.md`：新增 6 条 supply_chain evidence 记录
- `inventory/README.md`：新增 BOM 关联说明
- `governance/README.md`：新增 supply_chain/ 关联说明
- `dashboard/README.md`：新增 AI/ML-BOM + Supply Chain Mapping 说明

## Quality Check 结果

新增 Phase 18 检查：

- supply_chain/ 文件存在性（11 个文件）：通过
- supply_chain/ 文件禁止模式扫描（URL/token/email/endpoint）：通过
- Sample BOM 不包含真实 endpoint/API key：通过
- Sample BOM 条目数（5）：通过
- 供应链映射条目数（15）：通过
- README.md 提及 Phase 18：通过
- Inventory sample assets 引用 supply_chain：通过
- Dashboard 数据包含 supply_chain 区块：通过

## 当前限制

1. **BOM 为 sample/fake 数据**：所有 BOM 记录为样例数据，不代表任何真实系统的组件依赖关系。
2. **无自动化组件扫描**：BOM 信息需要人工填写，没有自动化的 SBOM 生成或依赖扫描工具接入。
3. **供应链风险映射非认证**：映射是项目内部参考，不代表已完成供应链安全审计或合规认证。
4. **无运行时供应链攻击检测**：BOM 和映射是静态的，没有实时的依赖漏洞监控或供应链攻击检测。
5. **MCP/Plugin 依赖清单为空**：当前没有启用 MCP 或外部插件，相关条目仅为占位符。
6. **无外部供应商评估流程**：外部提供商安全评估当前为 not_assessed 状态，需要真实供应商对接才能执行。
7. **15 条映射中 12 条为 not_assessed**：供应链安全评估是当前系统最大的缺口之一。

## 下一阶段建议

1. 继续增强 Inventory/BOM 覆盖更多资产类型，考虑自动化资产信息导入接口。
2. 设计 Finding 数据库 schema（SQLite），替代静态 Markdown 模板。
3. Dashboard 增加供应链风险分布可视化（风险类别、依赖类型、severity 分布）。
4. 若需要正式供应链安全审计，建议引入外部工具（如 SBOM 生成器、依赖扫描器）。
5. 在启用 MCP/Plugin 前，先完成 MCP 服务器安全评估框架和供应商评估流程。
6. 考虑将 BOM 组件状态跟踪集成到 governance checklist 的定期复核流程中。
