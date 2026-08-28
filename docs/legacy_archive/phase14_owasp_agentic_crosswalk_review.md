# Phase 14：OWASP Agentic Top 10 Crosswalk 复盘

## 本阶段做了什么

Phase 14 将 OWASP Agentic Top 10 风险分类框架融入现有 Generic Agent 评估体系，形成风险分类与报告映射层。本阶段是纯映射和文档层，不连接真实 Agent，不执行任何测试，不修改任何 evidence。

### 新增文件（`owasp/` 目录）

| 文件 | 用途 |
|---|---|
| `README.md` | OWASP 目录说明和 ASI 覆盖状态总览 |
| `agentic_top10_2026.yaml` | ASI01-ASI10 风险定义，包含描述、ATLAS 映射、证据、控制项、覆盖状态 |
| `agentic_to_atlas_crosswalk.yaml` | OWASP → ATLAS technique / test case / evidence / gaps 映射 |
| `agentic_to_generic_agent_capabilities.yaml` | 18 个 Generic Agent capability → OWASP / ATLAS / control / report 映射 |
| `agentic_control_mapping.yaml` | 每个 ASI 的预防/检测/响应控制项映射（引用 `generic_agent_control_checklist.md`） |
| `agentic_report_language.md` | ASI01-ASI10 中文报告语言模板 |

### 更新文件

- `docs/generic_agent_assessment_methodology.md` — 新增 Risk Classification 说明
- `docs/generic_agent_attack_surface.md` — 新增 OWASP 映射说明
- `docs/generic_agent_control_checklist.md` — 新增 OWASP Agentic Top 10 映射表
- `reports/generic_agent_assessment_template.md` — 新增 OWASP Agentic Top 10 覆盖映射表
- `docs/atlas_assessment_system_guide.md` — 新增 Phase 14 说明
- `docs/capability_matrix_v1.md` — 新增 OWASP Crosswalk 行
- `docs/release_notes_v1.md` — 新增 Phase 14 条目、Phase 13 commit
- `docs/roadmap.md` — 新增 Phase 14 完成说明
- `docs/learning_summary.md` — 新增 Phase 14 收获
- `reports/evidence_index.md` — 新增 OWASP crosswalk 行
- `dashboard/README.md` — 新增 OWASP 说明
- `README.md` — 新增 OWASP 文件引用
- `scripts/generate_atlas_dashboard.py` — 新增 OWASP 覆盖区块
- `scripts/generate_enterprise_report.py` — 新增 OWASP 章节
- `runners/run_quality_check.sh` — 新增 Phase 14 检查

## ASI01-ASI10 覆盖状态

| ASI | 名称 | 状态 | 说明 |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | covered_by_local_harness | Mock harness tool_return_injection_detected + goal_hijacking 场景 |
| ASI02 | Tool Misuse and Exploitation | covered_by_local_harness | 多个 mock harness + sandbox 场景覆盖 |
| ASI03 | Identity and Privilege Abuse | covered_by_local_harness | Secret access blocked + identity spoofing 检测 |
| ASI04 | Agentic Supply Chain Vulnerabilities | partially_covered | Skill poisoning 已覆盖，Plugin/MCP planned |
| ASI05 | Unexpected Code Execution | not_supported_for_now | 需要真实代码执行环境 |
| ASI06 | Memory & Context Poisoning | covered_by_local_harness | Memory poisoning blocked + context poisoning 检测 |
| ASI07 | Insecure Inter-Agent Communication | planned | 需要多 Agent 模拟 |
| ASI08 | Cascading Failures | covered_by_local_harness | Resource loop abuse 场景 |
| ASI09 | Human-Agent Trust Exploitation | covered_by_local_harness | Human confirmation bypass + write action dry-run 场景 |
| ASI10 | Rogue Agents | planned | 需要自主 Agent 漂移模拟 |

## 与 MITRE ATLAS 的关系

- **MITRE ATLAS** 提供攻击技术和战术分类，是威胁建模和测试用例设计的基座。
- **OWASP Agentic Top 10** 提供风险等级和业务影响视角，是报告和治理的基座。
- 两者不冲突，互补使用：ATLAS 用于"怎么测"，OWASP 用于"怎么报"。
- Dashboard 同时展示 ATLAS technique 覆盖和 OWASP ASI 覆盖。

## 关键设计决策

1. **映射层而非测试层**：OWASP Agentic Top 10 Crosswalk 是风险分类和报告映射层，不新增测试能力，不替代 MITRE ATLAS。
2. **不伪造覆盖**：ASI05/07/10 标记为 `not_supported_for_now` 或 `planned`，不声称已覆盖。清楚标注 gaps 比过度承诺更有价值。
3. **控制项引用而非重建**：`agentic_control_mapping.yaml` 引用 `generic_agent_control_checklist.md` 中的现有控制项，不创建重复清单。
4. **报告语言模板中文化**：`agentic_report_language.md` 提供 ASI01-ASI10 的中文风险描述、业务影响和技术发现表达，降低非技术读者的理解门槛。

## 质量检查

- Phase 14 检查通过（文件完整性、forbidden pattern、ASI05/07/10 未标记 covered、evidence 引用检查）
- 报告生成通过
- 未运行任何 `--execute`
- 未连接任何真实 Agent
- 未访问任何真实 API

## 限制

- OWASP Agentic Top 10 Crosswalk 是映射和文档层，不代表真实 Agent 已评估或已通过。
- ASI05（Code Execution）、ASI07（Inter-Agent Communication）、ASI10（Rogue Agents）当前未实现本地测试能力。
- ASI04（Agentic Supply Chain）的 Plugin 和 MCP 部分暂未覆盖。

## 后续方向

- 在新增 Plugin/MCP mock harness 后更新 ASI04 覆盖状态
- 在新增多 Agent 模拟后覆盖 ASI07
- 在新增目标偏离检测后覆盖 ASI10
- 考虑 ASI05 的 mock 代码执行场景设计
