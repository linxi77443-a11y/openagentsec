# Phase 83A — 统一攻击智能理论模型复核检查清单

## 范围

本阶段为 Phase 82A 统一攻击智能理论模型创建结构化复核检查清单，覆盖四个复核维度：

1. **方程一致性复核** — 3 个核心概念方程的变量完整性、来源映射、图结构/动力学/tabletop/模式库对齐
2. **权重因子语义复核** — 6 个权重因子的源模式映射、方向/范围合理性、校准来源可追溯性
3. **校准方法复核** — 6 个校准目标的 tabletop 数据对齐、轨迹字段覆盖、验证问题充分性
4. **安全语义复核** — 所有方程/权重/目标的 conceptual_only、not_production_risk、not_vulnerability_severity 声明确认

**只做 tabletop 复核检查清单** — 不生成可执行逻辑，不进行自动验证。

## 交付物

| 文件 | 内容 |
|------|------|
| `docs/phase83a_unified_theory_review_checklist.md` | 统一复核检查清单主文档（12 节，4 维度概览） |
| `docs/phase83a_equation_consistency_review_checklist.md` | 方程一致性复核子清单（3 方程 × 8 维度 + 5 项交叉方程检查） |
| `docs/phase83a_weight_factor_semantic_review_checklist.md` | 权重因子语义复核子清单（6 权重 × 9 维度 + 5 项交叉权重检查） |
| `docs/phase83a_calibration_method_review_checklist.md` | 校准方法复核子清单（6 目标 × 8 维度 + 5 项交叉目标检查） |
| `docs/phase83a_safety_semantics_review_checklist.md` | 安全语义复核子清单（3 方程 + 6 权重 + 6 目标 + 全局声明 + 禁止误解清单） |
| `docs/phase83a_unified_theory_review_checklist_notes.md` | 本说明文件 |
| `results/phase83a_unified_theory_review_checklist_result.yaml` | 复核检查清单结果 |

## 复核维度摘要

### 方程一致性（3 方程）

| 方程 | 变量数 | 来源阶段 | 核心对齐维度 |
|------|--------|----------|------------|
| P_edge(t) = S_source × W_edge × A_pattern × F_feedback × (1 - D_target) | 5 | 74A/77A/81A | 边类型映射、传播概率顺序 |
| D_node(t+1) = clamp(D_node + R_control - P_in × V_node + H_review) | 5+1 | 74A/77A/81A | 8 态模型映射、入口模块降级顺序 |
| G_path = Σ P_edge × (1 + A_seq) - Σ A_attenuation + Σ A_amplification - Σ B_blocking | 5 | 74A/77A/81A | 三路径 G_path 值、partial_degradation 分类 |

### 权重因子语义（6 权重）

| 权重 ID | 方向 | 范围 | 默认值 | 模式生命周期 |
|---------|------|------|--------|------------|
| W-ENTRY-VULN-001 | amplification | 0.0-1.0 | M43=0.9/M46=0.7/M48=0.5 | confirmed_across_3_paths |
| W-M50-AUDIT-DAMP-001 | attenuation | 0.5-1.0 | 0.8 | confirmed_across_3_paths |
| W-M50-SB-BLOCK-001 | blocking | 0.0-1.0 | 0.9 | confirmed_across_3_paths |
| W-CRED-ATTEN-001 | attenuation | 0.0-1.0 | 0.85 | observed_in_2_paths |
| W-PERM-AMPL-001 | amplification | 0.0-2.0 | 1.3 | observed_in_2_paths |
| W-HRG-BREAK-001 | review_gate | 0.0-0.5 | 0.3 | confirmed_across_3_paths |

### 校准方法（6 目标）

| 目标 ID | 核心验证问题 | 主来源阶段 |
|---------|------------|-----------|
| CAL-PROPAGATION-001 | P_edge 相对顺序是否匹配观察？ | 79A |
| CAL-ATTENUATION-001 | 衰减排名：M50 > M47 > M49 > M48 > M46 > M43？ | 80A |
| CAL-M50-DAMPING-001 | M50 D_node ≥ 0.7 在三路径中？ | 79A/80A |
| CAL-ENTRY-DEGRADATION-001 | 降级顺序：M43 < M46 < M48？ | 79A |
| CAL-FEEDBACK-001 | F_feedback 符号与实际反馈一致？ | 77A/79A/80A |
| CAL-CROSS-PATH-001 | DEV-CRED vs RAG G_path 可区分？ | 80A |

### 安全语义（全面扫描）

- 3 个方程：conceptual_only + not_executable + not_production_risk + not_vulnerability_severity + not_exploitability_score + requires_human_review ✓
- 6 个权重：conceptual_only + not_production_risk + not_vulnerability_severity + human_review_required ✓
- 6 个目标：tabletop_consistency_review_only + not_statistical_validation + not_production_risk_calibration + human_review_required ✓
- 12 项全局声明 + 10 项禁止误解确认

## 来源阶段引用

| 阶段 | 内容 | 在复核清单中的角色 |
|------|------|-------------------|
| Phase 74A | 攻击图结构 | 方程变量来源映射、图结构对齐 |
| Phase 77A | 动力学模型 | 方程动力学对齐、衰减/放大/阻断规则验证 |
| Phase 79A | 首次 tabletop | 校准目标观察对齐、轨迹字段覆盖 |
| Phase 80A | 多路径 tabletop | 交叉路径验证、M47 vs M49 衰减对比 |
| Phase 81A | 模式库 | 权重因子源模式映射、模式生命周期一致性 |
| Phase 82A | 统一理论模型 | 被复核的对象（所有交付物内容） |

## 确认项

| 确认项 | 状态 |
|--------|------|
| tabletop_review_checklist_only | 通过 |
| conceptual_only | 通过 |
| executable=false | 通过 |
| 方程一致性子清单已创建（3 方程） | 通过 |
| 权重因子语义子清单已创建（6 权重） | 通过 |
| 校准方法子清单已创建（6 目标） | 通过 |
| 安全语义子清单已创建（3+6+6+全局+禁止误解） | 通过 |
| 所有复核项标记 pending | 通过 |
| 所有复核项要求 human review | 通过 |
| 未生成可执行代码 | 通过 |
| 未声明 confirmed_vulnerability | 通过 |
| 未声明 formal_finding | 通过 |
| 未声明 production_safety | 通过 |

## 非目标

- 不生成任何可执行代码
- 不进行自动验证
- 不生成测试用例
- 不生成正式发现
- 不评估生产风险
- 不评估漏洞严重性
- 不计算可利用性分数
- 不连接真实系统
- 不执行 capability_engine
- 不进入 controlled replay

---

*Phase 83A 统一攻击智能理论模型复核检查清单说明文件末端。*
