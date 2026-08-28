# Phase 110B ~ 112B 能力迭代规划（Capability Iteration Roadmap）

**Document Title**: Platform Capability Iteration Plan — Absorbing PyRIT / OpenAI Evals / promptfoo / garak Patterns
**Target Executor**: antigravity（或其他 AI 开发智能体）+ 人工复核
**Created**: 2026-08-19
**Baseline**: Milestone 5.0 Golden Baseline（Phase 109A 认证，健康度 100.0/100.0）
**Scope**: 平台自身能力迭代。**本阶段不开发 DeepSeek Harness 插件**（原 Phase 110-112 插件路线暂缓，后续重启时编号顺延）。

---

## 0. 给执行智能体的强制阅读项（Non-Negotiable）

1. **先读** `SAFETY.md` 与 `CLAUDE.md`，再读本文档。
2. **10 大安全不变式**（见 §1）在所有新代码与测试中强制断言，严禁削弱。
3. 所有新能力在 **fake_runtime / simulated 层**实现：合成数据一律用 `<SIM_...>` 占位符，不连接真实模型端点、不发起真实网络请求、不执行真实工具。
4. 每个任务包完成必须产出四件套：**实现代码 + validator 脚本（scripts/）+ pytest 套件（tests/）+ 执行摘要（YAML）**，并登记进 `delivery.json`。
5. 安装任何新依赖前必须请求人工确认（当前仅允许 dev 依赖 `pytest`）。
6. 不修改、不回退任何既有 50 模块的 `coverage_status`；新增能力只做**增量登记**。
7. 遇到与既有资产冲突的编号（如历史 `phase110
<truncated 18537 bytes>

2. `multi_agent/replay/phase112b_integration_gate.py`（沿用 phase109a 对账门模式）
3. `tests/test_phase112b_integration_gate.py`（≥15 用例）
4. `docs/phase112b_gate_summary.md`：九支柱结论 + 更新后的平台健康度记分卡
5. `delivery.json` 最终登记 + `docs/release_notes_v5_1.md`（v5.1 能力迭代版发布说明，中英摘要）
6. 更新 `docs/project_handover_and_roadmap_for_teamwork.md`：把本次迭代成果与"插件路线重启条件"写入交接状态

**验收标准**：
- 全部 9 任务包 validator 100% PASS
- 全量 pytest（含新增 ≥110 用例）零失败
- 既有 50 模块 registry 状态除 M24/M25 升级外零变更（非回溯性保证）

---

## 5. 执行顺序与依赖

```
ENG-001 ──┬──> ATLAS-002 ──> ENGINE-003 ──┬──> CAL-004 ──> CTRL-005
          │                              ├──> ADAPT-006 ──> CANARY-007
          │                              └──────┴──────────────> REPORT-008 ──> GATE-009
```

- **ENG-001 必须第一个完成**（后续所有 pytest 验收依赖可运行环境）
- ENGINE-003 是 CAL/ADAPT/CANARY/REPORT 的公共基座
- ATLAS-002 与 ENGINE-003 可并行（数据层 vs 代码层无冲突）
- 人工确认点：① ENG-001 安装 pytest；② 若 CI workflow 需要真实 Git 仓库远端；③ 任何偏离本规划的变更

## 6. 完成定义（DoD，阶段整体）

1. §2 八项短板全部消灭并有 validator 证据
2. 新增 pytest ≥110 用例，全量测试通过率 100%
3. `delivery.json` 新增 9 条登记，证据链完整可回溯
4. 10 大安全不变式在全部新模块强制断言并有负面测试证明
5. 平台在干净环境（仅 Python 3.10+）可运行全部验证

The above content shows the entire, complete file contents of the requested file.
