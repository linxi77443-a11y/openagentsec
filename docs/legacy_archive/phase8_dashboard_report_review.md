# Phase 8 Dashboard / 报告生成器复盘

## Phase 8 做了什么

Phase 8 把现有 ATLAS 评估结果整理为可读 dashboard 和可交付的企业评估报告，未新增攻击能力，未运行任何 `--execute`。

新增内容：

- `dashboard/`：本地 dashboard 输出目录
  - `dashboard/index.md`：Markdown dashboard
  - `dashboard/atlas_dashboard.html`：单文件静态 HTML dashboard，使用内联 CSS
  - `dashboard/dashboard_data.json`：从本地 evidence、coverage、profiles、catalog 汇总的结构化数据
  - `dashboard/README.md`：查看说明
- `scripts/generate_atlas_dashboard.py`：dashboard 生成脚本
- `scripts/generate_enterprise_report.py`：企业评估报告生成脚本
- `scripts/generate_all_reports.sh`：统一生成命令
- `reports/generated_atlas_assessment_report.md`：基于 ATLAS 视角的本地报告

## Dashboard 数据来源

`dashboard/dashboard_data.json` 由 `scripts/generate_atlas_dashboard.py` 读取以下本地文件后汇总生成：

- `reports/evidence/atlas_assessment_summary.json`
- `coverage/atlas_coverage_matrix.yaml`
- `assessment_profiles/*.yaml`
- `test_catalog/*.yaml`

## Dashboard 生成方式

```bash
bash scripts/generate_all_reports.sh
```

该命令先校验输入文件是否存在，再依次执行 dashboard 与报告生成脚本。

## 企业报告生成方式

```bash
python3 scripts/generate_enterprise_report.py
```

读取本地 evidence、coverage 摘要、缺口分析、控制项清单和企业评估报告模板，生成 `reports/generated_atlas_assessment_report.md`。

## 是否访问外部网络

否。所有脚本仅读取本地文件并写出本地文件。

## 是否执行测试

否。Phase 8 没有运行任何 `--execute`，也没有触发 promptfoo 实测，仅基于已有 evidence 汇总。

## 是否包含真实系统信息

否。所有内容仍然限制在本地 sandbox、fake data、fake documents 和 fake tools。

## 如何查看 dashboard

- Markdown：阅读 `dashboard/index.md`
- HTML：在浏览器中打开 `dashboard/atlas_dashboard.html`（单文件、内联 CSS、无外部依赖）

## 如何使用 generated report

`reports/generated_atlas_assessment_report.md` 是结构化 Markdown 报告，可直接用于内部评审、复测计划或修复跟踪。该报告不替代企业评估模板 `reports/enterprise_ai_security_assessment_template.md`，而是其本地数据填充版本。

## 后续建议

- Manual UI Replay：基于 dashboard 视图复现 Chatbot / RAG / Agent 关键路径，记录视觉证据。
- 测试环境 API Provider：使用 mock / staging API 接入 promptfoo，仍保留 fake credentials。
- garak / PyRIT / AgentDojo 本地 mock：先做 dry-run 与样本生成，再考虑接入 evidence 流水线。
