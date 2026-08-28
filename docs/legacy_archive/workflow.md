# 工作流

## 1. 选择测试范围

从 `knowledge/atlas_mapping.yaml` 中选择本次要验证的 technique，例如：

- LLM Prompt Injection
- Indirect Prompt Injection
- RAG Poisoning
- AI Agent Tool Invocation
- Extract LLM System Prompt

## 2. 确认目标

默认只允许：

- `sandbox/chatbot_demo`
- `sandbox/rag_demo`
- `sandbox/agent_demo`

非本地目标必须人工确认并记录授权范围。

## 3. 选择测试用例

从 `testcases/` 中选择对应用例目录，查看：

- `README.md`
- `examples.yaml`
- `expected_controls.md`

## 4. dry-run

先运行：

```bash
bash runners/run_all_dryrun.sh
```

确认将执行的目标、工具和测试范围。

## 5. 执行本地测试

第一阶段可以手工运行 sandbox demo 或后续接入 promptfoo。

## 6. 记录证据

证据保存到：

```text
reports/evidence/
```

证据应包含：输入、输出、工具调用、时间、目标、结果。

## 7. 生成报告

基于：

```text
reports/report_template.md
```

输出：

- ATLAS 映射
- OWASP 映射
- 风险等级
- 证据
- 修复建议
- 复测建议

## 8. 复测

修复后重复执行同一批测试用例，记录是否通过。
