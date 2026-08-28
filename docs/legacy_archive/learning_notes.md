# 学习笔记

## 学习目标

通过本地靶场理解 MITRE ATLAS 和 OWASP Agentic Applications Top 10 中与 LLM、RAG、Agent 工具调用相关的风险。

## 第一阶段重点

- Prompt Injection
- Direct Prompt Injection
- Indirect Prompt Injection
- LLM Jailbreak
- System Prompt Exposure
- LLM Data Leakage
- RAG Poisoning
- False RAG Entry Injection
- AI Agent Tool Invocation
- AI Agent Context Poisoning
- Credentials from AI Agent Configuration
- Cost Harvesting
- Agentic Resource Consumption
- Exfiltration via AI Agent Tool Invocation

## 学习方法

1. 先看风险定义。
2. 再看本地 demo 如何模拟。
3. 再写测试用例。
4. 最后写防守控制和报告。

## 关键判断

- prompt 风险不是只发生在用户输入，也会发生在网页、文档、邮件、RAG 内容和工具返回中。
- RAG 内容既是知识来源，也是攻击入口。
- Agent 工具调用会把语言攻击转化成真实系统动作。
- 凭证、工具、记忆、RAG、外联和成本限制是 Agent 安全的核心控制点。
