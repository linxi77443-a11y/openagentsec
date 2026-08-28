# Phase 86A — Authorized Attack Chain Simulation Design Gate 设计文档

## 1. 概述

Phase 86A 是 **Authorized Attack Chain Simulation Design Gate**，以纯设计方式将已闭环的四个上游 Phase 的输出整合为一个可自动化的攻击链生成、模拟执行、实时评估、证据归档与复测候选输出引擎蓝图。capability_value 和 risk_level 均为 not_applicable，设计门不声明能力值。

### 1.1 设计目标

- 攻击链自动生成：基于攻击者档案和攻击目标，自动选择合适的攻击模式并组装为攻击链
- 模拟执行：在 simulated runtime 边界内执行攻击链，所有操作使用 `<SIM_...>` 占位符
- 实时评估：基于节点防御状态演化模型，在攻击链执行过程中动态评估防御降级、边界保持、阻断和人工复核
- 证据归档：为每个攻击节点记录 evidence_trace，形成完整的模拟证据链
- 复测候选输出：基于突破信号和控制候选自动生成复测用例候选

### 1.2 上游输入

| Phase | 内容 | 本引擎使用方式 |
|-------|------|--------------|
| Phase 75A | 攻击路径目录 | 攻击链组装的路径库 |
| Phase 76A | 自动化探索器设计 | 攻击链生成策略的理论基础 |
| Phase 77A | 动态模拟层设计 | simulated runtime 的执行环境设计 |
| Phase 81A | 攻击模式库（8 种模式） | 策略选择模型的模式来源 |

### 1.3 设计约束

- design_gate_only：仅产出设计文档、schema 草案、流程图文本、状态机定义和非执行伪接口说明
- 不产生可运行代码、不产生真实攻击链、不产生真实 payload
- 所有数据使用 `<SIM_...>` 合成占位符
- `confirmed_vulnerability=false`、`formal_finding_allowed=false`、`production_safety_claimed=false`
- `breakthrough_detected` 仅表示 simulated capability signal

---

## 2. 系统架构

### 2.1 架构层次

```
┌─────────────────────────────────────────────────────────┐
│                   攻击链自动化引擎                         │
├─────────────────────────────────────────────────────────┤
│  1. Strategy Selection Engine     (策略选择引擎)          │
│     - 加载攻击者档案和攻击目标                             │
│     - 从模式库选择最优攻击模式                             │
│     - 确定模式执行顺序                                     │
├─────────────────────────────────────────────────────────┤
│  2. Attack Chain Generator       (攻击链生成器)           │
│     - 根据策略组装攻击链                                    │
│     - 验证攻击前提条件                                      │
│     - 初始化每个攻击节点的状态                               │
├─────────────────────────────────────────────────────────┤
│  3. Simulated Runtime Layer      (模拟运行时层)            │
│     - 执行攻击节点（模拟模式）                              │
│     - 生成 simulated tool trace                            │
│     - 维护模拟运行时状态                                     │
├─────────────────────────────────────────────────────────┤
│  4. Dynamic Defense Evaluator    (动态防御评估器)          │
│     - 评估每个节点的防御状态                                  │
│     - 检测边界保持/阻断/降级                                  │
│     - 生成突破信号                                          │
├─────────────────────────────────────────────────────────┤
│  5. Evidence Archiver           (证据归档器)               │
│     - 记录每个节点的 evidence_trace                          │
│     - 聚合链级别的完整证据链                                  │
│     - 标记 breakthrough_type                                 │
├─────────────────────────────────────────────────────────┤
│  6. Output Mapper               (输出映射器)               │
│     - Red: 突破信号 / exploit_chain_candidate               │
│     - Blue: 控制候选 / mitigation_candidate                 │
│     - Purple: 复测候选 / retest_case                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心流程

```
[攻击目标 + 攻击者档案]
        │
        ▼
┌───────────────────┐
│ Strategy Selection │ ←── 模式库 (8 patterns, Phase 81A)
│ Engine             │
└─────────┬─────────┘
          │ selected_patterns
          ▼
┌───────────────────┐
│ Attack Chain       │ ←── 路径库 (Phase 75A)
│ Generator          │
└─────────┬─────────┘
          │ attack_chain (ordered nodes)
          ▼
┌───────────────────┐
│ Simulated Runtime  │ ←── 动态模拟层 (Phase 77A)
│ Layer              │
└─────────┬─────────┘
          │ node_execution_trace
          ▼
┌───────────────────┐
│ Dynamic Defense    │
│ Evaluator          │
└─────────┬─────────┘
          │ defense_assessment (per node)
          ▼
┌───────────────────┐
│ Evidence Archiver  │
└─────────┬─────────┘
          │ evidence_trace (aggregated)
          ▼
┌───────────────────┐
│ Output Mapper      │
└─────────┬─────────┘
          │
     ┌────┴────┬────┬────┐
     ▼         ▼    ▼    ▼
   Red       Blue Purple Schema
  Signal    Control Retest  Output
```

---

## 3. 攻击链自动生成 (Attack Chain Generator)

### 3.1 生成流程

1. **输入解析**: 解析攻击者档案（attacker_type、attack_objective）和目标系统层（layer）
2. **策略匹配**: Strategy Selection Engine 从 8 个模式中选择最优策略组合
3. **链组装**: 按依赖顺序组装攻击节点
   - 同一模式可输出多个节点（如 multi-turn boundary erosion 按轮次扩展）
   - 节点间通过 prerequisite 和 postrequisite 连接
4. **前提验证**: 验证每个节点的前提条件是否满足
5. **节点初始化**: 为每个节点分配初始防御状态（intact）、模拟输入、预期行为

### 3.2 节点结构

每个攻击节点包含：
- `node_id`: 链内唯一标识
- `pattern_id`: 所属模式
- `attacker_type`: 攻击者类型
- `attack_objective`: 攻击目标
- `prerequisites`: 前置条件列表
- `simulated_input`: 模拟输入内容
- `expected_defensive_behavior`: 预期防御行为
- `initial_defense_state`: 初始防御状态
- `breakthrough_indicators`: 突破判定指标

---

## 4. 策略选择模型 (Strategy Selection Engine)

### 4.1 模式库映射

| 模式 | 适用 attacker_type | 适用 attack_objective | 优先级 |
|------|-------------------|----------------------|--------|
| Direct Prompt Injection | external_user | data_exposure, unauthorized_access | 高 |
| Indirect Prompt Injection | indirect_prompt_source | context_poisoning | 高 |
| Multi-turn Boundary Erosion | malicious_insider | role_escalation, approval_bypass | 中 |
| Tool Invocation Abuse | low_privileged_operator | tool_misuse | 高 |
| Tool Argument Pollution | external_user | tool_misuse, unauthorized_access | 中 |
| Role Boundary Bypass | malicious_insider | role_escalation | 高 |
| Service Account Abuse | compromised_user | service_account_abuse | 中 |
| Approval Bypass | malicious_insider | approval_bypass | 中 |
| Business Action Induction | external_user | business_action_induction | 低 |
| Simulated Exfiltration Attempt | compromised_user | exfiltration_simulation | 低 |

### 4.2 选择逻辑

1. 过滤：仅保留与当前 attacker_type 和 attack_objective 匹配的模式
2. 排序：按优先级降序排列
3. 依赖解析：检查模式间的前置依赖关系
4. 序列化：输出有序的模式列表
5. 去重：同一模式重复出现时合并参数

### 4.3 策略变体

- **单链策略**: 仅选择优先级最高的单个模式
- **组合链策略**: 选择多个模式按顺序执行（默认）
- **并行链策略**: 多个独立链同时执行，各链互不依赖

---

## 5. 动态防御评估 (Dynamic Defense Evaluator)

### 5.1 节点防御状态模型

每个攻击节点在执行过程中维护一个防御状态：

| 状态 | 说明 | 含义 |
|------|------|------|
| `intact` | 防御完整 | 未检测到突破信号 |
| `degraded` | 防御降级 | 部分防御被绕过但仍在可控范围内 |
| `breached` | 边界突破 | 检测到明确的边界违反信号 |
| `blocked` | 阻断 | 防御机制成功阻断攻击 |
| `review_triggered` | 人工复核触发 | 系统标记需要人工审查 |

### 5.2 状态转换

```
         ┌─────────────────────────────────────┐
         │                                     │
         ▼                                     │
    ┌────────┐    detected_weakness    ┌───────────┐
    │ intact │ ──────────────────────→ │ degraded  │
    └────┬───┘                        └─────┬─────┘
         │                                  │
         │ boundary_violation               │ boundary_violation
         ▼                                  ▼
    ┌──────────┐                      ┌──────────┐
    │ breached │                      │ breached │
    └──────────┘                      └──────────┘

    ┌────────┐    defense_triggered   ┌──────────┐
    │ intact │ ─────────────────────→ │ blocked  │
    └────────┘                        └──────────┘

    ┌────────┐    ambiguous_signal    ┌──────────────────┐
    │ intact │ ─────────────────────→ │ review_triggered │
    └────────┘                        └──────────────────┘
```

### 5.3 评估规则

- **边界保持**: 未检测到任何突破信号 → intact
- **部分降级**: 检测到尝试绕过但未成功 → degraded
- **突破确认**: 检测到明确的边界违反 → breached
- **阻断**: 防御机制明确拒绝/拦截 → blocked
- **需复核**: 信号模糊或高风险 → review_triggered

### 5.4 链级别评估

链级评估基于所有节点的评估结果：
- 链内存在任何 `breached` 节点 → `chain_breach_detected`
- 链内存在 `blocked` 节点 → `chain_blocked_at_nth_node`
- 链级 `breakthrough_detected` = any(breached) AND `confirmed_vulnerability` = false

---

## 6. 证据归档 (Evidence Archiver)

### 6.1 证据条目结构

```yaml
evidence_trace:
  - timestamp: "<SIM_TIMESTAMP>"
    source: "synthetic_runtime/simulated_defense"
    signal_type: "defense_assessment"
    content: "Simulated defense evaluation at node <SIM_NODE_ID>..."
    node_id: "<SIM_NODE_ID>"
    pattern_id: "<SIM_PATTERN_ID>"
    defense_state: "intact|degraded|breached|blocked|review_triggered"
```

### 6.2 链级证据聚合

- 所有节点的 evidence_trace 聚合为链级 evidence_chain
- 链级包含 breakthrough_ids 列表
- 链级包含 defended_until_node（最后一个被成功防御的节点）
- 链级包含 first_breach_at_node（第一个突破节点）

---

## 7. 输出映射 (Output Mapper)

### 7.1 Red Team 输出

| 字段 | 来源 |
|------|------|
| breakthrough_detected | 链级别 any breached |
| breakthrough_type | breached 节点的 pattern + category |
| exploit_chain_candidate | 从 breached 节点按顺序组装 |
| evidence_trace | 聚合 evidence_chain |
| affected_boundary | breached 节点的 boundary |

### 7.2 Blue Team 输出

| 字段 | 来源 |
|------|------|
| control_candidate | blocked / review_triggered 节点的防御机制 |
| mitigation_candidate | 基于 detected 的 weakness 生成建议 |
| defense_coverage_gap | degraded / breached 节点的未防御面 |

### 7.3 Purple Team 输出

| 字段 | 来源 |
|------|------|
| retest_candidate | 基于 breakthrough signal 生成 |
| retest_case_template | 攻击链的简化版本 |
| regression_suite_suggestion | 影响的其他边界 |

---

## 8. 安全边界声明

```yaml
confirmed_vulnerability: false
formal_finding_allowed: false
production_safety_claimed: false
controlled_replay_claimed: false
result_is_candidate_level: true
simulated_execution_boundary: true
synthetic_only: true
real_system_connection_allowed: false
real_api_call_allowed: false
real_tool_execution_allowed: false
real_data_access_allowed: false
breakthrough_detected_semantics: "simulated capability signal only"
exploit_chain_candidate_semantics: "simulated attack path, not real exploit"
```

## 9. 设计门完成标准

- [x] 攻击链生成流程已设计（attack_chain_generation_flow_defined）
- [x] 策略选择逻辑已设计（strategy_selection_logic_defined）
- [x] 动态防御评估已设计（dynamic_state_evaluation_defined）
- [x] 防御降级评估已设计（defense_degradation_assessment_defined）
- [x] 模拟执行边界已定义（simulated_execution_boundary_defined）
- [x] 证据链 schema 已设计（evidence_trace_schema_defined）
- [x] 红/蓝/紫输出映射已设计（red_blue_purple_output_mapping_defined）
- [x] 不包含代码实现
- [x] 不包含真实执行入口
- [x] 不生成真实 payload

## 10. 非目标

- 不实现可运行代码
- 不实现自动化执行器
- 不生成真实攻击链
- 不执行真实扫描或利用
- 不连接真实 SIEM / CI/CD / RAG / MCP / A2A
- 不接入真实云资源
- 不产生 confirmed_vulnerability
- 不声明 production_safety
- 不进入 controlled replay execution
