# 架构说明

## 定位

本项目是本地受控 AI 安全评估工作台，用于把 MITRE ATLAS 和 OWASP Agentic Applications Top 10 转换为可执行、可记录、可复盘的安全测试流程。

## 架构

```text
knowledge/ 映射知识
  ↓
corpus/ 评估语料
  ↓
generated_testcases/ 编译测试用例
  ↓
testcases/ 测试用例
  ↓
runners/ 测试编排
  ↓
sandbox/ 本地靶场
  ↓
reports/ 证据与报告
```

## 组件

### knowledge

存放 ATLAS technique、OWASP Agentic Top 10、风险分类和防守控制映射。

### testcases

按风险类型组织测试用例。第一阶段使用 YAML 和 Markdown 管理，便于后续接入 promptfoo、PyRIT、garak。

### generated_testcases

由 Corpus-to-Testcase Compiler（Phase 24）从 `corpus/` YAML 语料自动编译生成的标准化测试用例。按 profile 组织，包含 61 个 generated testcases 和 52 个 promptfoo 草稿。所有 testcases 为 draft 状态，未执行，未连接真实系统。

### sandbox

本地靶场，只处理假数据：

- `chatbot_demo`：模拟聊天机器人。
- `rag_demo`：模拟 RAG 检索和恶意文档注入。
- `agent_demo`：模拟 Agent 工具调用。

### runners

执行 dry-run、调用本地 demo、预留开源工具接入。

### reports

记录测试时间、目标、范围、工具、ATLAS 映射、OWASP 映射、结果、证据和修复建议。

## 安全设计

- 默认 dry-run。
- 默认本地靶场。
- 所有 secret 使用 fake secret。
- 高风险测试只生成说明。
- 不自动连接生产系统。
