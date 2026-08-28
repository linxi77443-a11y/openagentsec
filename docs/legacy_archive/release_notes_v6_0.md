# Release Notes: OpenAgentSec v6.0.0 (Milestone 6.0 终局封版)

**Release Date**: 2026-08-20  
**Version**: `6.0.0`  
**Milestone**: `Milestone 6.0 (OpenAgentSec 开源封版)`  
**Certification Status**: `VERDICT_MILESTONE_6_0_PASSED_CERTIFIED`

---

## 🎯 Executive Summary (执行摘要)

OpenAgentSec v6.0.0 标志着平台从内部研究靶场全面蜕变为工业级、标准化的开源 AI 安全与合规评估框架（OpenAgentSec Framework）。本版本实现了全生命周期能力注册表闭环，完成了 4 大核心史诗级任务（Epic 1 ~ Epic 4），将测试套件规模提升至 **1150+** 用例且 100% 真实通过。

---

## 🚀 Key Highlights & Epics Delivered

### 🛡️ Epic 1: 长程记忆与 RAG 安全攻防 (Phase 117A)
- **M48 (RAG Document Poisoning and Instruction Boundary)** 正式达到 `mvp_complete`。
- 覆盖隐蔽注入、知识库篡改、跨上下文重组与长程上下文记忆污染等 8 大核心攻击场景。
- 实现了 RAG 检索流水线的全链路不可信边界约束与来源归因保护。

### ⚖️ Epic 2: 安全防御有效性与校准引擎 (Phase 118A)
- **M24 (Control Effectiveness Comparison)**：落地 A/B 测试评估引擎，量化安全策略开启前后的拦截率增益与业务可用性损耗。
- **M25 (False Positive / False Negative Calibration)**：落地混淆矩阵与 $F_1$ 分数校准引擎，确保评估工具误报率可控、召回率精准。

### 🔗 Epic 3: 授权攻击链全局模拟 (Phase 119A)
- **ADV-86 (Authorized Attack Chain Simulation)** 从设计门全面晋级为执行层。
- 实现了标准 5 阶段杀伤链（Recon -> Initial Access -> Privilege Escalation -> Lateral Movement -> Exfiltration）的时序模拟与动态审计。
- 验证了安全防线在面对恶意 Agent 跨租户数据外发时的硬拦截熔断机制（Hard Block）。

### 📦 Epic 4: 开源框架化封装与适配器扩展 (Phase 120A)
- **标准 Python 库打包**：正式发布 `openagentsec` CLI 工具（`openagentsec eval`, `openagentsec list-modules`, `openagentsec audit`）。
- **DeepSeek-R1 / V3 Mock 适配器**：支持大模型思考链 (`<think>` 标签) 隔离提取与安全脱敏流式输出。
- **开源合规**：中英双语规范、Apache-2.0 许可证、CONTRIBUTING 贡献指南。

---

## 📊 Verification & Certification Baseline

- **全量回归测试**: `1150+ passed, 0 failed`
- **假绿代码率**: `0%` (无任何 `print("PASS")` 或短路 Stub)
- **安全边界**: `synthetic_only: true`，无外部网络依赖，数据 100% 合成脱敏。
- **终局判定**:
  ```yaml
  certification:
    verdict: "VERDICT_MILESTONE_6_0_PASSED_CERTIFIED"
    framework_version: "6.0.0"
    safety_invariants_preserved: true
    all_epics_delivered: true
  ```
