# Phase 21 System Release Consolidation v1.3 Review

## 本阶段目标

做一次系统级发布收口，把 Phase 1–20 的成果整理成清晰的 v1.3 release package，使项目从"持续迭代工程"变成"可理解、可使用、可交付、可继续扩展的 AI 安全评估工作台"。

本阶段不新增测试能力、不新增治理框架、不安装外部工具、不运行任何 `--execute`、不连接真实系统。

## 新增 release 文件

- `release/README.md` — release 目录入口
- `release/system_release_v1_3.md` — 系统发布说明
- `release/release_manifest_v1_3.yaml` — 发布清单
- `release/module_map_v1_3.md` — 模块关系图（含 Mermaid）
- `release/capability_matrix_v1_3.md` — 按能力分类的详细矩阵（12 组，50+ 项）
- `release/execution_status_matrix_v1_3.md` — 执行状态矩阵（6 类执行状态）
- `release/user_journey_v1_3.md` — 5 条典型使用路径
- `release/operator_quickstart_v1_3.md` — 常用命令速查与风险等级
- `release/delivery_package_checklist_v1_3.md` — 交付包检查清单
- `release/known_limitations_v1_3.md` — 已知限制（16 条）
- `release/next_phase_roadmap_v1_3.md` — 后续路线图（Phase 22–30）

## System Release v1.3 摘要

- **系统名称**：AI Security Assessment & Governance Workbench v1.3
- **定位**：以 MITRE ATLAS 为攻击技术底座、以 OWASP Agentic Top 10 为 Agent 风险分类、以 AI Red Teaming 为执行方法、并扩展到 NIST AI RMF、AI Asset Inventory、AI/ML-BOM 与外部工具 Adapter 的本地 AI 安全评估与治理工作台。
- **6 条能力主线**：安全测试、红队交付、治理管理、供应链、外部工具接入、报告与质量
- **6 种执行模式**：local_sandbox_execute、manual_ui_replay、dry_run_only、mock_normalization_only、methodology_template、governance_mapping、planning_layer

## Release Manifest 摘要

- Release version: v1.3
- Baseline commits: phase16_5–phase21
- Core directories: 20 个
- Supported execution modes: 7 种
- Current limitations: 11 条
- Next phase candidates: 9 个

## Module Map 摘要

- 10 个模块，覆盖框架层、方法层、治理层、执行层、数据层、展示层、规划层、验证层、质量层
- 6 条数据流路径
- 使用 Mermaid flowchart 展示模块关系

## Capability Matrix 摘要

- 12 个能力组，50+ 项具体能力
- 每个能力标注 current_status、execution_mode、evidence、dashboard/report 支持情况、限制和下一步
- Status 取值：executed_local、mock_normalization_ready、dry_run_skeleton_ready、methodology_ready、governance_mapping_ready、planning_ready、planned

## Execution Status Matrix 摘要

| 分类 | 数量 | 可作 evidence | 可作正式 finding |
|---|---|---|---|
| 已真实本地执行 | 5 | ✓ 本地沙箱 | 仅限沙箱环境 |
| 已 mock 归一化 | 1 | pipeline 验证 only | ❌ |
| 已 dry-run skeleton | 1 | dry-run 状态 only | ❌ |
| 已方法论 ready | 4 | ❌ | ❌ |
| 已治理映射 ready | 5 | ❌ sample 数据 | ❌ |
| 仅 planning | 5 | ❌ | ❌ |

## User Journey 摘要

5 条典型使用路径：

1. 评估一个普通 Chatbot
2. 评估一个 RAG 知识库助手
3. 评估一个 Agent 工具调用系统
4. 评估一个只有页面没有 API 的 AI 应用
5. 做一次企业 AI 应用治理评估

每条路径包含从入口到 dashboard/report 再到 finding/retest 的完整流程。

## Operator Quickstart 摘要

8 个常用命令，标注 4 种风险等级：

- safe_dry_run: quality check
- report_generation: generate_all_reports
- local_execute_only: ATLAS assessment、Manual UI Replay、Generic Agent Harness
- mock_only: normalize external tool mock evidence

## Delivery Package Checklist 摘要

21 个文件，分为用户可读交付物和内部工程文件。明确标注哪些是 sample/fake/mock，哪些不能作为真实评估结论。

## Known Limitations 摘要

16 条已知限制，涵盖评估范围、框架映射、数据、展示层、流程和安全边界。

## Next Phase Roadmap 摘要

9 个后续阶段（Phase 22–30），每个阶段包含目标、为什么做、输入、输出、风险边界、是否需要真实系统、是否允许 execute。

## Dashboard / Report 更新情况

- Dashboard 新增 Release Status 区块（release version、module count、executed/mock/planning 分类统计）
- Report 新增 Section 21：System Release Consolidation v1.3（release status 表格、发布文档列表、版本说明）
- Report 限制说明更新：标注 release consolidation 不改变评估结果
- Dashboard 和 Report 均不声明 certification achieved、external tools integrated 或 production system tested

## Quality Check 结果

Phase 21 质量检查验证：

- release/ 目录和 11 个发布文档必须存在
- release/ 文件不得包含真实 URL、token、email、endpoint
- release/ 不得声明 certification achieved、external tools integrated、production system tested
- execution_status_matrix 必须区分 executed_local / mock_only / planning
- release manifest 必须包含 current_limitations
- Dashboard 必须显示 release version v1.3 和 release package ready
- Report 不得声明 certification achieved、external tools integrated、production system tested

## 当前限制

- Release consolidation 不改变 Phase 16.5 的测试统计。
- 所有发布文档为静态 Markdown/YAML，不包含实时数据。
- 发布包不包含自动部署脚本或 CI 配置。

## 下一阶段建议

详见 `release/next_phase_roadmap_v1_3.md`。

建议优先关注 Phase 22：正式 API Provider Integration（FastGPT 测试环境）。
