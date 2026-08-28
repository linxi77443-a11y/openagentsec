# v5.2.0 Release Notes

## 英文总结 (English Summary)
Welcome to Enterprise AI Security Platform v5.2.0! This release delivers advanced evaluation tools, interactive visualization, and comprehensive regression baselines:
- **COT Reasoning Abnormality Analysis (COT-012)**:
  - Deep inspection of reasoning chains (`<think>` tags)
  - Detection for premise tampering, logic jumps, reasoning loops, and token exhaustion
  - Evaluated on 30+ adversarial COT samples with automated precision/recall scoring
- **Interactive HTML Report Viewer (VIEW-013)**:
  - Responsive standalone HTML report generation for executive and technical review
  - Visual summary of security invariants, residual risk declarations, and candidate findings
- **Shadow AI Discovery (M32)**:
  - Identification and mapping of unauthorized model endpoints and agent pipelines
- **Comprehensive Benchmarks & Test Harness (Phase 113B)**:
  - Standardized benchmark presets and full-corpus execution harness
- **Security & Safety Invariants**:
  - Maintained strict isolation: `synthetic_only: true`, `production_safety: out_of_scope`

## 中文总结 (Chinese Summary)
欢迎使用企业级 AI 安全评估平台 v5.2.0！本次更新带来高级分析套件、可视化与基准测试能力：
- **思维链 (COT) 异常推理分析 (COT-012)**：
  - 针对大模型思考链 (`<think>` 标签) 进行深度语义与结构分析
  - 支持前提篡改、逻辑跳跃、死循环推理及 Token 耗尽等异常模式检测
  - 在 30+ 条对抗样本上完成验证并输出精确率/召回率报告
- **交互式 HTML 安全报告生成器 (VIEW-013)**：
  - 支持将结构化评估结果渲染为独立交互式 HTML 报告
  - 清晰呈现安全不变式、自适应残留风险声明与候选发现项
- **影子 AI 发现模块 (M32)**：
  - 自动化探测企业内部未受管控的模型接入点与 Agent 链路
- **标准化基准评测与测试框架 (Phase 113B)**：
  - 预设基准排行榜数据集与全量语料回归测试脚手架
- **安全边界合规**：
  - 严格保持 `synthetic_only: true` 本地合成运行规范，不连接生产业务系统。
