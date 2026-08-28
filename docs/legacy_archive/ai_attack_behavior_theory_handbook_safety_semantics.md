# 《AI 攻击行为理论手册》— 安全语义声明

## 用途

本文件明确说明《AI 攻击行为理论手册》的类型、使用边界和结论级别。所有阅读者在使用手册中的内容之前，必须理解并接受以下声明。

---

## 1. 手册类型声明

```yaml
handbook_type_declaration:
  handbook_compilation_only: true
  documentation_only: true
  candidate_level_only: true
  is_not_vulnerability_report: true
  is_not_formal_finding_report: true
  is_not_attack_guide: true
  is_not_production_guidance: true
  is_human_review_reference_only: true
```

本手册是对项目 v1.0 至 v3.0 阶段性成果的理论性整理。它不是漏洞报告，不是正式安全审计发现，不是攻击操作指南，不是生产安全指南。

## 2. 核心声明

### 2.1 不声称 confirmed vulnerability

本手册中的任何内容均不构成已确认的安全漏洞。所有攻击路径描述为 conceptual path，所有模式描述为 tabletop pattern，所有理论模型描述为 theory model candidate，所有结论为 candidate-level conclusion。

### 2.2 不生成 formal finding

本手册不在任何法律、合规或审计框架下构成 formal finding。手册不替代正式的漏洞评估、渗透测试或安全合规审查流程。

### 2.3 不声明 production safety

本手册不评估、不保证、不声明任何 AI 系统或 Agent 系统的生产环境安全性。手册中的理论模型和 candidate-level 结论不得用于生产环境的风险判定。

### 2.4 不提供攻击执行指南

本手册描述的理论攻击路径和模式是为了帮助防御方理解攻击行为结构。手册内容不得被解释、复制或用于构建真实攻击。手册不包含可执行的攻击步骤、payload、命令或系统连接方式。

### 2.5 不包含真实 payload

本手册不包含可用于真实攻击的 prompt injection payload、shell 命令、API 调用参数或其他攻击载荷。手册中的示例使用模拟数据（dummy data）。

### 2.6 不连接真实系统

本手册所描述的所有评估均在授权受控环境中进行，不连接真实 MCP Server、不访问真实仓库、不读取真实文件、不执行真实命令、不读取真实凭据、不连接真实 RAG 系统、不调用真实 API。

### 2.7 不替代人工复核

本手册是 human review reference。手册中的任何分析结果、模式描述、理论模型输出均需要经过人类安全专家的审查和判断，不得用于自动化决策。

## 3. 结论层级声明

```yaml
conclusion_level_declaration:
  all_conclusions_are_candidate_level: true
  all_attack_paths_are_conceptual: true
  all_patterns_are_tabletop_patterns: true
  all_theorems_are_theorem_candidates: true
  all_equations_are_conceptual: true
  all_weight_factors_are_illustrative: true
  all_calibration_targets_are_tabletop_review_only: true
```

本手册中的所有结论均处于以下层级之一：
- **candidate-level** — 初步判断，待 human review 确认或修正
- **conceptual** — 理论概念，不代表真实系统行为
- **simulated** — 在受控环境中观察到的模拟信号
- **tabletop observation** — 在桌面推演中观察到的行为模式
- **theory model** — 理论模型输出，不可执行，不产生风险评分

没有结论处于 confirmed vulnerability 或 formal finding 层级。

## 4. 禁止用途

```yaml
forbidden_uses:
  - "不得将手册内容作为 confirmed vulnerability 的证据"
  - "不得将手册内容作为 formal finding 的依据"
  - "不得使用手册内容进行生产环境风险评分"
  - "不得将手册中的 conceptual equation 作为实际检测规则"
  - "不得将手册中的 weight factor 作为生产配置参数"
  - "不得将手册中的 tabletop observation 作为真实攻击复现结果"
  - "不得将手册中的 pattern library 作为实际检测规则库"
  - "不得将手册中的理论模型输出作为安全合规证据"
  - "不得使用手册构建真实攻击 payload"
  - "不得将手册作为自动化安全决策系统的输入"
```

## 5. 确认清单

- [x] 本手册不声称 confirmed vulnerability
- [x] 本手册不生成 formal finding
- [x] 本手册不声明 production safety
- [x] 本手册不提供攻击执行指南
- [x] 本手册不包含真实 payload
- [x] 本手册不连接真实系统
- [x] 本手册不替代人工复核
- [x] 本手册所有结论均为 candidate-level
- [x] 本手册仅用于 human review 参考

## 6. 文档元数据

```yaml
metadata:
  document_type: "handbook_safety_semantics_declaration"
  handbook_compilation_only: true
  documentation_only: true
  candidate_level_only: true
  confirmed_vulnerability: false
  formal_finding_allowed: false
  production_safety_claimed: false
  human_review_required: true
  handbook_is_not_attack_guide: true
  handbook_is_not_formal_finding_report: true
  handbook_is_human_review_reference_only: true
```
