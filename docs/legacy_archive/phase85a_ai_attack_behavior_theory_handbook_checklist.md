# Phase 85A — 《AI 攻击行为理论手册》非执行型检查清单

> **非执行型检查清单** — 本 checklist 用于人工复核手册整理交付物。
> 不得包含可执行代码块。

## 1. 手册主文档存在性

- [ ] `docs/ai_attack_behavior_theory_handbook.md` 已创建
  - [ ] 第一部分：基础框架与问题定义（第 1–2 章）
  - [ ] 第二部分：单模块风险与能力边界（第 3–6 章）
  - [ ] 第三部分：跨模块攻击链与系统风险动力学（第 7–9 章）
  - [ ] 第四部分：形式化系统与实践使用（第 10 章）
  - [ ] 每章包含 chapter purpose
  - [ ] 每章包含 key ideas
  - [ ] 每章包含 source phases
  - [ ] 每章包含 security semantics
  - [ ] 每章包含 candidate-level conclusion
  - [ ] 每章包含 human review note

## 2. 章节来源映射表存在性

- [ ] `docs/ai_attack_behavior_theory_handbook_source_map.md` 已创建
  - [ ] 每章映射到来源 Phase
  - [ ] 每章映射到来源模块
  - [ ] 每章列出复用文档
  - [ ] 来源阶段总览表存在
  - [ ] 安全语义声明存在

## 3. 术语表存在性

- [ ] `docs/ai_attack_behavior_theory_handbook_glossary.md` 已创建
  - [ ] authorized evaluation 已定义
  - [ ] simulated signal 已定义
  - [ ] finding candidate 已定义
  - [ ] confirmed vulnerability 已定义
  - [ ] formal finding 已定义
  - [ ] tabletop exercise 已定义
  - [ ] attack graph 已定义
  - [ ] propagation dynamics 已定义
  - [ ] defense degradation trajectory 已定义
  - [ ] attack evolution trajectory 已定义
  - [ ] pattern library 已定义
  - [ ] unified theory model 已定义
  - [ ] formal system 已定义
  - [ ] human review gate 已定义
  - [ ] M50 audit confirmation 已定义
  - [ ] M50 sandbox execution boundary 已定义
  - [ ] candidate-level conclusion 已定义

## 4. 安全语义声明存在性

- [ ] `docs/ai_attack_behavior_theory_handbook_safety_semantics.md` 已创建
  - [ ] 不声称 confirmed vulnerability
  - [ ] 不生成 formal finding
  - [ ] 不声明 production safety
  - [ ] 不提供攻击执行指南
  - [ ] 不包含真实 payload
  - [ ] 不连接真实系统
  - [ ] 不替代人工复核
  - [ ] 所有结论均為 candidate-level
  - [ ] 结论层级声明（candidate / conceptual / simulated / tabletop / theory model）
  - [ ] 禁止用途列表

## 5. Notes 存在性

- [ ] `docs/phase85a_ai_attack_behavior_theory_handbook_notes.md` 已创建
  - [ ] 说明仅做文档整理
  - [ ] 说明未新增代码
  - [ ] 说明未新增 corpus
  - [ ] 说明未新增 run_config
  - [ ] 说明未新增测试
  - [ ] 说明未执行 capability_engine
  - [ ] 说明未连接真实系统
  - [ ] 说明非目标列表

## 6. v1.0 内容覆盖

- [ ] v1.0 授权评估原则已纳入（第 2 章）
- [ ] v1.0 评估框架已纳入（第 1–2 章）
- [ ] v1.0 capability matrix 已引用
- [ ] v1.0 ATLAS/OWASP 映射已引用

## 7. v2.0 六大模块覆盖

- [ ] M43（MCP Tool Descriptor Integrity）已纳入（第 3 章）
- [ ] M46（Repository Context Injection）已纳入（第 4 章）
- [ ] M47（Command and Credential Boundary）已纳入（第 4 章）
- [ ] M48（RAG Document Poisoning）已纳入（第 5 章）
- [ ] M49（RAG Permission Inheritance）已纳入（第 5 章）
- [ ] M50（Agent Runtime Sandbox）已纳入（第 6 章）

## 8. v3.0 理论栈覆盖

- [ ] 攻击图内容已纳入（第 7 章）
- [ ] 攻击路径目录已纳入（第 7 章）
- [ ] 动力学模型内容已纳入（第 8 章）
- [ ] tabletop 推演内容已纳入（第 8 章）
- [ ] 模式库内容已纳入（第 9 章）
- [ ] 统一理论模型内容已纳入（第 9 章）
- [ ] 复核检查清单内容已纳入（第 9 章）
- [ ] 形式化系统概念已纳入（第 10 章）

## 9. 安全声明检查

- [ ] no confirmed vulnerability 声明在所有交付物中存在
- [ ] no formal finding 声明在所有交付物中存在
- [ ] no production safety claim 声明在所有交付物中存在
- [ ] handbook_compilation_only 声明在所有交付物中存在
- [ ] documentation_only 声明在所有交付物中存在
- [ ] candidate_level_only 声明在所有交付物中存在
- [ ] human_review_required 声明在所有交付物中存在

## 10. 非执行确认

- [ ] 未生成可执行代码
- [ ] 未生成脚本
- [ ] 未生成 validate 脚本
- [ ] 未新增 corpus
- [ ] 未新增 adversarial_playbook
- [ ] 未新增 run_config
- [ ] 未新增测试
- [ ] 未新增评估模块
- [ ] 未新增理论模型
- [ ] 未执行 capability_engine
- [ ] 未生成 execution_results
- [ ] 未执行 parser
- [ ] 未生成 capability_scorecard
- [ ] 未进入 controlled replay
- [ ] 未连接真实系统
- [ ] 未生成真实 payload
- [ ] 未声明 confirmed vulnerability
- [ ] 未声明 formal finding
- [ ] 未声明 production safety

## 11. 交付物清单

- [ ] `docs/ai_attack_behavior_theory_handbook.md`
- [ ] `docs/ai_attack_behavior_theory_handbook_source_map.md`
- [ ] `docs/ai_attack_behavior_theory_handbook_glossary.md`
- [ ] `docs/ai_attack_behavior_theory_handbook_safety_semantics.md`
- [ ] `docs/phase85a_ai_attack_behavior_theory_handbook_notes.md`
- [ ] `docs/phase85a_ai_attack_behavior_theory_handbook_checklist.md`
- [ ] `results/phase85a_ai_attack_behavior_theory_handbook_result.yaml`

## 12. 人工复核

- [ ] 手册主文档已人工审阅
- [ ] 章节来源映射表已人工审阅
- [ ] 术语表已人工审阅
- [ ] 安全语义声明已人工审阅
- [ ] notes 已人工审阅
- [ ] 四部分十章结构确认完整
- [ ] 所有章节安全语义声明确认正确
- [ ] candidate-level 语义一致
- [ ] 非执行边界确认无违规
- [ ] 手册未被误解为漏洞报告或攻击指南

---

*检查清单末端。所有 [ ] 项需人工确认。*
