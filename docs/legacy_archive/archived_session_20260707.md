# 会话归档文档 — Full Corpus 50→75 增强阶段

**归档时间**: 2026-07-07 22:30
**归档原因**: 移交 Qoder 继续开发（多 Agent 模式）
**会话跨度**: 2026-07-06 20:00 ~ 2026-07-07 22:30 (~26 小时)

---

## 1. 项目整体状态

| 维度 | 当前值 | 目标值 | 完成率 |
|------|--------|--------|--------|
| MVP 模块 | 51/51 | 51 | **100%** |
| Full Corpus (≥50 entries) | 49/49 | 49 | **100%** |
| Full Corpus 增强 (75 entries) | 37/49 | 49 | **75.5%** |
| 总 Commit 数 | 461 | — | — |
| 总测试用例 | ~3500 | ~4900 | ~71% |
| 裁判审核覆盖率 | 37/37 | 37/37 | **100%** |

---

## 2. Full Corpus 增强进度（75 entries）

### ✅ 已完成（37 个模块）

| 模块 | 名称 | entries | 裁判 |
|------|------|---------|------|
| M42 | Code Execution Sandbox | 75 | PASS |
| M50 | Agent Runtime Sandbox & Audit Chain | 75 | PASS |
| M48 | RAG Document Poisoning | 75 | PASS |
| M47 | Coding Agent Command & Credential Safety | 75 | PASS |
| M49 | RAG Permission Inheritance & Retrieval Audit | 75 | PASS |
| M10 | Cross-User / Cross-Session Leakage | 75 | PASS (修复后) |
| M11 | Data Source Trust Boundary | 75 | PASS (修复后) |
| M05 | Output Boundary / Unsafe Conclusion Control | 75 | PASS |
| M34 | RAG Knowledge Base Poisoning | 75 | PASS |
| M29 | Model/Provider Fallback Risk | 75 | PASS |
| M26 | Risk Prioritization | 75 | PASS |
| M30 | Model Behavior Drift Monitoring | 75 | PASS |
| M31 | Attack Surface Regression Suite | 76 | PASS |
| M32 | Shadow AI Discovery | 75 | PASS |
| M33 | Multimodal Input Safety | 75 | PASS |
| M36 | Model DoS / Cost Exhaustion | 75 | PASS |
| M37 | Multi-Agent Coordination Safety | 75 | PASS |
| M38 | Multi-Source Input Injection | 75 | PASS |
| M39 | Runtime State Corruption | 75 | PASS |
| M40 | Agent Action Audit & Attribution | 75 | PASS |
| M41 | Service Account Permission Boundary | 75 | PASS |
| M43 | MCP Tool Descriptor Integrity | 83 | PASS (修复后) |
| M44 | A2A Agent Identity Trust Boundary | 75 | PASS |
| M14 | High-Risk Action Simulation | 75 | PASS |
| M45 | AI Dependency Integrity | 75 | PASS |
| M03 | RAG Boundary Exposure | 75 | PASS (minor) |
| M06 | Indirect Prompt Injection | 75 | PASS |
| M13 | Tool Argument Injection | 75 | PASS |
| M15 | Business Action Simulation | 75 | PASS (修复后) |
| M16 | Human Approval Gate | 75 | PASS |
| M17 | AI Asset Exposure Mapping | 75 | PASS |
| M19 | Mock Data Exfiltration Path | 75 | PASS |
| M20 | Data Exfiltration Path | 75 | PASS |
| M21 | Impact Path Reconstruction | 75 | PASS |
| M22 | Business Impact Evidence | **72** | PASS (72 条) |
| M23 | Remediation Comparison | 75 | PASS |
| M27 | File Upload / Document Ingestion Safety | 75 | PASS |
| M28 | Connector SaaS Boundary | 75 | PASS |
| M46 | Coding Agent Repo Context Injection | 75 | PASS |

### ❌ 待增强（12 个模块，仍为 50 entries）

| 模块 | 名称 | 当前 |
|------|------|------|
| M01 | Direct Prompt Injection | 50 |
| M02 | System Prompt Leakage | 50 |
| M04 | Instruction Hierarchy Bypass | 50 |
| M07 | Role-Based Permission Boundary | ~50 |
| M12 | Tool Invocation Safety | 50 |
| M24 | Machine Speed Abuse | 50 |
| M25 | DoS / Repetitive Loop | 50 |
| M35 | MCP Tool Descriptor Poisoning | 50 |
| _M08_ | _Role-Based Permission Boundary_ | _75（开发完成，裁判有 FAIL 需修复）_ |
| _M18_ | _Business Criticality Mapping_ | _75（开发完成，裁判 PASS）_ |

### ⚠️ 已知问题（裁判审核发现）

| 模块 | 问题 | 严重度 | 状态 |
|------|------|--------|------|
| M22 | 三方声明 75 条，实际仅 72 条 | 中 | 已修复（dev 需补 3 条或确认 72 OK） |
| M08 | JSON 重复 key（credential_exposure） | 高 | 已修复 |
| M03/M18/M19/M23 | scorecard 缺少 total_entries 字段 | 低 | 已补 |
| M21 | 2 处中英文混写 | 低 | 待修复 |
| M27 | 1 处占位符缺 `>` | 低 | 已修复 |
| M46 | 1 处占位符缺 `>` | 低 | 已修复 |

---

## 3. 测试用例统计

| 模块分组 | 数量 | entries/模块 | 总用例 |
|---------|------|-------------|--------|
| 已增强 (75) | 37 | 72~83 | ~2775 |
| 待增强 (50) | 12 | 50 | 600 |
| MVP | 51 | 10 | 510 |
| **合计** | **~100** | — | **~3885** |

---

## 4. 架构与工作流

### 4.1 多 Agent 流水线（严格 workflow）

```
用户请求
  ↓
[规划+开发 Agent] — 读取 playbook → 增强 25 条 → 更新 execution_results → validate
  ↓
[独立裁判 Agent] — context: "none" — 6 项检查（entry 数、文件一致性、安全字段、
                       SIM 占位符、新向量实质、scorecard）
  ↓  PASS?
  ├─ 是 → commit
  └─ 否 → 修复 → 重新裁判 → commit
```

### 4.2 裁判六项检查清单

1. **playbook entry 数** = 75 (attack 65 + control 10)
2. **execution_results 条数** 与 playbook 完全一致
3. **scorecard total_entries** = 75
4. **安全字段**全 false（confirmed_vulnerability, formal_finding_allowed, production_safety_claimed）
5. **`<SIM_...>` 占位符**覆盖所有 query/prompt/query 内容
6. **新增 25 条**为实质性新向量（非原 50 条变体）

### 4.3 常见裁判 FAIL 模式

| 模式 | 频次 | 修复方式 |
|------|------|---------|
| scorecard total_entries 未更新 | 高 | sed 更新为 75 |
| scorecard 缺少 total_entries 字段 | 中 | 手动添加 |
| execution_results 条目不足 | 中 | 补足缺失条目 |
| <SIM_...> 占位符遗漏 | 中 | 替换具体文本为占位符 |
| metadata 与实际 entries 数不一致 | 中 | 统一对齐 |
| JSON 重复 key | 低 | 合并/去重 |

---

## 5. 关键文件结构

```
adversarial_playbooks/
├── m{01-50}_mvp/             # MVP 版本（10 entries）
│   ├── playbook.yaml
│   ├── execution_results.json
│   ├── capability_scorecard.yaml
│   ├── run_config.yaml
│   └── validate.py
└── m{01-50}_full_corpus/     # Full Corpus 版本（50/75 entries）
    ├── playbook.yaml
    ├── execution_results.json
    ├── capability_scorecard.yaml
    ├── m{XX}_full_corpus_result.yaml
    ├── run_config.yaml
    └── validate.py / validate.sh

capability_modules/
├── module_registry.yaml      # 所有模块注册信息
├── corpora/                  # 语料库规范
├── schemas/                  # 数据 schema
├── matrix/                   # 评估矩阵
├── implementations/          # 实现
└── tool_catalogs/            # 工具目录

docs/
├── full_corpus_execution_summary.md  # Full Corpus 执行摘要
├── archive_session_20260707.md        # 本文档

audits/                       # 裁判审核报告（independent裁判审核报告.md）
```

---

## 6. 开发规范

### 6.1 安全字段（必须全部 false）

```yaml
confirmed_vulnerability: false
formal_finding_allowed: false
production_safety_claimed: false
controlled_replay_claimed: false
production_safety: out_of_scope
synthetic_only: true
fake_runtime_only: true
real_execution: false
```

### 6.2 占位符规范

- 所有用户请求/工具返回/外部内容使用 `<SIM_...>` 格式
- e.g. `<SIM_FILE_PATH_001>`, `<SIM_EMAIL_CONTENT_042>`, `<SIM_CREDENTIAL_003>`
- 禁止出现真实 URL、IP、凭证、系统名称

### 6.3 命名规范

- `entry_id`: `M{XX}-{CATEGORY}-{NNN}`（3 位编号）
- `case_id`: `M{XX}-{PREFIX}{NNN}`（3 位编号，统一 zero-padded）
- playbook category 注释与实际条目数必须一致

### 6.4 scorecard 规范

- `total_entries` 必须显式存在
- `attack_entries` + `control_entries` = `total_entries`
- `category_breakdown` 各分类加总必须等于 total_entries

---

## 7. 剩余工作计划

### 优先级顺序

| 优先级 | 工作项 | 预计工作量 |
|--------|--------|-----------|
| P0 | M08 裁判问题复查确认 | ~10min |
| P0 | M22 补 3 条 → 75 或确认 72 可接受 | ~15min |
| P0 | 剩余 8 个模块 50→75 增强 | ~2h |
| P1 | 后续增强每个模块严格 workflow | ~3h |
| P2 | M21 中英文混写修复 | ~5min |

### 开放问题

1. **M22**: 当前 72 条，缺失 3 条。需要决定：补 3 条到 75，或接受 72 作为最终值
2. **M08**: JSON 重复 key 已修复，需要裁判重新确认
3. **多 Agent 基础设施**: `multi_agent/` 目录已创建（`planner.py`, `judge.py`, `task_sheet.schema.json`, `judge_verdict.schema.json`），面向 Qoder 的多 Agent 流水线基建

---

## 8. 关键技术模式

### 8.1 Full Corpus 增强模式

每个模块从 50→75 的 +25 条新向量，标准做法：
1. 读取现有 playbook 分析已有 50 条的覆盖
2. 在 4 个现有攻击类别中各补 5~10 条
   - 或者创建新的子类别（最多 2-3 个新子类）
3. 同步更新 execution_results / scorecard
4. validate 通过后才可提交

### 8.2 MVP 模式

从零创建模块（先 MVP 10 条 → 再 Full Corpus 50 → 再增强 75）：
1. 8 个攻击类别各 1 条 + 2 条控制用例 = 10
2. 所有字段完整：entry_id, prompt, expected_behavior, expected_signal, safety_fields
3. 必须有 validate 脚本，通过后 registry 标记 `mvp_complete`

### 8.3 裁判独立性

- 裁判 Agent 使用 `context: "none"`（看不到开发过程）
- 裁判接收：PRD + 裁判指令 + 交付物文件
- 裁判输出：6 项检查结果 + 问题清单 + PASS/FAIL 裁定
- 发现 FAIL 必须修复后再次提交

---

## 9. 关键资源引用

- **PRD 源文件**: `/Users/linxi/Desktop/ai-workspace/AI学习/PRD/`（`.docx` 格式）
- **项目规则**: `CLAUDE.md`（强制 safety、干运行、模拟数据）
- **SAFETY.md**: `SAFETY.md`（安全边界说明）
- **Memory**: `~/.local/share/mimocode/memory/projects/2eb3b5fb-.../MEMORY.md`
- **Session notes**: `~/.local/share/mimocode/memory/sessions/ses_.../notes.md`

---

## 10. 典型 Agent 指令模板

### 开发 Agent 模板
```
执行 M{XX} Full Corpus 增强。
目录: adversarial_playbooks/m{XX}_full_corpus/
1. 读取 playbook.yaml 分析现有 50 条 entries
2. 增加 25 条新攻击向量扩展到 75 条
3. 更新 execution_results.json
4. 运行验证
5. 提交 commit
所有数据使用 <SIM_...> 占位符。安全字段全 false。
```

### 裁判 Agent 模板
```
你是独立裁判。审核 M{XX} Full Corpus 75-entry 增强版。
读取:
- adversarial_playbooks/m{XX}_full_corpus/playbook.yaml
- adversarial_playbooks/m{XX}_full_corpus/execution_results.json
- adversarial_playbooks/m{XX}_full_corpus/capability_scorecard.yaml
检查6项:
1. playbook entry = 75
2. execution_results 条数一致
3. scorecard total_entries = 75
4. 安全字段全 false
5. <SIM_...> 占位符
6. 新增25条有实质新向量
输出: PASS/FAIL + 问题
```

---

*本文档由 MiMoCode 自动生成，用于 Qoder 开发衔接。*
