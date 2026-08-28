# OpenAgentSec Research Claim Calibration & Audit Register

> **Phase 24.1:** Current allowed/forbidden claims: [claim_boundaries.md](claim_boundaries.md).

---

## 1. Audit Methodology & Scope

In accordance with strict academic research standards, this document conducts a systematic audit of all claims made across OpenAgentSec documentation (`README.md`, `docs/research/`, `docs/governance/`, `docs/operations/`). 

The audit evaluates each claim against two mandatory criteria:
1. **Code Evidence**: Does the claim correspond to a concrete, tested implementation in `src/openagentsec/`?
2. **Empirical Evidence**: Has the claim been verified through reproduction runs without over-extrapolating from sandbox tests to general production safety?

---

## 2. Research Claim Audit & Calibration Matrix

| 原始声明 / 术语 | 声明类型 | 代码与实验依据 | 潜在学术风险 / 歧义 | 校准后的严谨学术表达 (Calibrated Expression) |
|---|---|---|---|---|
| **“首创 Agent 安全评估体系”** | 独创性声明 | `src/openagentsec/oracle/` (Deterministic Oracle) | 忽略学术界已有提示词测试基准的背景。 | **“提出了一种基于物理运行时回执的确定性 Agent 安全评估方法”** (Proposes a deterministic evidence-driven evaluation methodology for autonomous agents). |
| **“完全解决 Agent 安全问题”** | 范围声明 | 无 (理论上无法完全消除所有安全风险) | 过度承诺，混淆了“评估机制”与“系统绝对安全”。 | **“为 Stateful 与 Tool-Using Agent 提供了形式化安全边界检验机制”** (Provides a formal boundary evaluation mechanism for stateful and tool-using agents). |
| **“零误报 / 绝对确定”** | 可靠性声明 | `ReproductionAggregator` (5-run zero variance) | 仅在受控离散测试配置下成立，未覆盖随机温度下的连续概率分布。 | **“在受控实验配置下实现 5 轮法定零方差可复现判定 ($\text{Variance} = 0.0000$)”** (Enforces 5-run zero-variance consensus under clean session resets in controlled environments). |
| **“不可篡改的铁证”** | 密码学声明 | `EvidenceItem` (Hash Signer & Provenance) | 物理宿主环境遭到 Root 提权时，进程级签名无法完全防范物理篡改。 | **“基于策略执行点 (PEP) 与反向代理捕获的可验证运行时回执 (`EvidenceItem`)”** (Verifiable runtime telemetry captured at Policy Enforcement Points). |
| **“世界一流 / 顶级标准”** | 评价性声明 | 无量化对照基准 | 带有营销宣传色彩，不符合学术论文客观中立原则。 | **“严格对齐形式化验证与可复现基准规范”** (Strictly aligned with formal invariant verification and statutory reproduction benchmarks). |
| **“证明所有 Agent 安全”** | 归纳声明 | `tests/integration/empirical/` (14 实验用例) | 以有限测试用例推导全称命题，存在以偏概全风险。 | **“在覆盖的 15 个典型场景与 9 类目标架构中完成了实验验证”** (Empirically verified across 15 canonical scenarios and 9 target architectural profiles). |
| **“自主红队全自动渗透”** | 能力声明 | `AttackMutationEngine` (4-D 启发式变异) | 现阶段为规则与模板驱动的自适应变异，并非具备完全自主通用推理的攻防 Agent。 | **“具备 4 维自适应对抗变异与攻击路径发现能力”** (Equipped with a 4-dimensional attack mutation and automated scenario discovery engine). |

---

## 3. General Scientific Principles Adopted

1. **Separation of Evaluation from Guarantee (评估机制与安全保证分离)**:
   - *Prohibited*: "OpenAgentSec guarantees the target agent is 100% secure."
   - *Mandatory*: "OpenAgentSec verifies whether the target agent satisfies declared Policy Invariants under specified adversarial scenarios."
2. **Empirical Grounding (以实测证据为唯一真理依据)**:
   - All evaluation statements must cite concrete physical receipts (`tool_execution_log`, `authorization_parameter_check_receipt`).
3. **Fail-Closed Reporting (不确定性必须显式声明)**:
   - When telemetry is unobservable or degraded, verdicts are strictly reported as `INCONCLUSIVE` rather than guessing a Pass or Fail.
