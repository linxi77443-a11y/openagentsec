# 归档：全量模拟执行闭环 — 49 模块 execution_results 生成

**日期**: 2026-07-07  
**会话类型**: 7 小时功能开发计划  
**核心成果**: 将平台从"有 playbook 无执行结果"推进到"49 模块全管道闭环"

---

## 起始状态

```
Playbook (攻击定义)    ████████████████████ 49/49 ✅  全部 75 条
Execution Results      ░░░░░░░░░░░░░░░░░░░░  1/49    (仅 M08)
Capability Scorecard   ░░░░░░░░░░░░░░░░░░░░  1/49    (仅 M08)
```

## 终止状态

```
Playbook (攻击定义)    ████████████████████ 49/49 ✅  全部 75 条
Execution Results      ████████████████████ 49/49 ✅  全部生成
Capability Scorecard   ████████████████████ 49/49 ✅  全部生成
Result YAML            ████████████████████ 49/49 ✅  全部生成
回归测试覆盖           ████████████████████ 8 模块   (M01/M02/M04/M07/M12/M24/M25/M35)
攻击链                 ████████████████████ 49+8     (49 单模块 + 8 跨模块)
```

---

## Phase 1: 全量 execution_results 生成

### Task 1.1: synthetic_result_generator.py
- **文件**: `scripts/synthetic_result_generator.py`
- **功能**: 基于 playbook entry 的 control_case/expected_signal 确定性生成执行结果
- **输出**: 每模块 3 文件 → execution_results.json + capability_scorecard.yaml + {mod}_result.yaml
- **兼容**: 处理多种 playbook 格式（entries/m07/m13_full_corpus/m39_full_corpus key）
- **结果**: 49/49 模块成功，147 文件生成

### Task 1.2: Parser 信号检测扩展
- **文件**: `capability_engine/parsers/parse_capability_results.py`
- **变更**:
  - M01/M02/M03 添加 generic fallback（特定关键词不匹配时的后备逻辑）
  - M06 添加 attack/control 区分逻辑
  - 新增通用后备 detect_signals（覆盖 M05/M09-M11/M16-M37/M40/M42-M50）
  - 新增通用后备 assess_capability_value（覆盖所有未明确处理的模块）
- **验证**: 49/49 模块 attack/control 信号区分度 PASS

### Task 1.3: 批量生成
- 49 模块 × 3 文件 = 147 文件全部生成

### Task 1.4: 全量裁判审核
- **文件**: `scripts/full_corpus_judge_audit.py`
- **六项检查**: 文件完整性 + 数据一致性 + 安全字段 + 突破率 + 信号覆盖率 + 人审率
- **结果**: 49/49 PASS

---

## Phase 2: 回归测试补齐

### Task 2.1: M12/M24/M25/M35 回归用例
- **输出**: `regression_suites/generated/m{12,24,25,35}_regression_suite.yaml`
- **覆盖**: 每模块按 subcategory 选取 1 attack + 1 control

### Task 2.2: M01/M02/M04/M07 回归覆盖增强
- **输出**: `regression_suites/generated/m{01,02,04,07}_regression_suite.yaml`
- **覆盖率**: M01=30.7%, M02=48%, M04=100%, M07=46.7%

### Task 2.3: 回归套件验证
- 8 个新 suite 全部通过格式验证

---

## Phase 3: 攻击链端到端验证

### Task 3.1: 49 模块攻击链生成
- 使用 seed_selector + attack_chain_engine 为 49 模块各生成 1 条攻击链
- 全部 valid_path=True，chain_id 唯一，SIM 占位符正确

### Task 3.2: 跨模块攻击路径扩展
- **文件**: `docs/cross_module_path_catalog_update.yaml`
- **新增 5 条路径**:
  1. PATH-CHATBOT-AGENT-001: M01→M38 (提示注入→Agent 输入污染)
  2. PATH-AGENT-SUPPLY-CHAIN-001: M38→M43→M44 (Agent→MCP 工具操控)
  3. PATH-RAG-DATA-EXFIL-001: M06→M34→M20 (间接注入→数据外泄)
  4. PATH-IDENTITY-PERMISSION-001: M10→M11→M08→M41 (身份伪造→权限绕过)
  5. PATH-MULTI-AGENT-IMPACT-001: M37→M21→M22 (多 Agent 失调→业务影响)

### Task 3.3: 攻击链裁判审核
- 49 单模块链 + 5 新跨模块链 + 3 已有跨模块链 = 57 条全部合法

---

## Phase 4: 收尾与修复

### Task 4.1: 修复已知问题
| 问题 | 修复 |
|------|------|
| M02 缺 run_config.yaml | ✅ 基于 M01 模板创建 |
| M10 缺 run_config.yaml | ✅ 基于 M01 模板创建 |
| M39 缺 run_config.yaml | ✅ 基于 M01 模板创建 |
| M04/M07/M13 缺 result.yaml | ✅ 由 synthetic_result_generator 生成 |
| M43 playbook 83 条 | ✅ 确认声明=实际=83，内部一致 |
| M22 声明 75 实际 72 | ✅ 实际为 75，无误 |

### Task 4.3: module_registry 状态同步
- 49/49 模块已是 `full_corpus_complete`，无需更新

---

## 新增/修改文件清单

### 新增文件
| 文件 | 说明 |
|------|------|
| `scripts/synthetic_result_generator.py` | 全量执行结果确定性生成器 |
| `scripts/full_corpus_judge_audit.py` | 49 模块 × 6 项裁判审核脚本 |
| `docs/cross_module_path_catalog_update.yaml` | 5 条新增跨模块攻击路径 |
| `regression_suites/generated/m01_regression_suite.yaml` | M01 回归套件 |
| `regression_suites/generated/m02_regression_suite.yaml` | M02 回归套件 |
| `regression_suites/generated/m04_regression_suite.yaml` | M04 回归套件 |
| `regression_suites/generated/m07_regression_suite.yaml` | M07 回归套件 |
| `regression_suites/generated/m12_regression_suite.yaml` | M12 回归套件 |
| `regression_suites/generated/m24_regression_suite.yaml` | M24 回归套件 |
| `regression_suites/generated/m25_regression_suite.yaml` | M25 回归套件 |
| `regression_suites/generated/m35_regression_suite.yaml` | M35 回归套件 |
| `adversarial_playbooks/m02_full_corpus/run_config.yaml` | M02 运行配置 |
| `adversarial_playbooks/m10_full_corpus/run_config.yaml` | M10 运行配置 |
| `adversarial_playbooks/m39_full_corpus/run_config.yaml` | M39 运行配置 |

### 修改文件
| 文件 | 说明 |
|------|------|
| `capability_engine/parsers/parse_capability_results.py` | 添加 34 模块通用信号检测后备 |
| `adversarial_playbooks/m{01-50}_full_corpus/execution_results.json` | 49 模块执行结果（生成/覆盖） |
| `adversarial_playbooks/m{01-50}_full_corpus/capability_scorecard.yaml` | 49 模块评分卡（生成/覆盖） |
| `adversarial_playbooks/m{01-50}_full_corpus/*_result.yaml` | 49 模块结果摘要（生成/覆盖） |

---

## 剩余待办

| 优先级 | 项目 | 说明 |
|--------|------|------|
| P1 | 仪表盘更新 | dashboard_data.json 停留在 Phase 35B，未反映 49/49 状态 |
| P2 | ADV 模块推进 | ADV-86A/86B/87A design gates → 执行 |
| P2 | v2 模块开发 | M05 v2, M10 v2, AI Safety Decision Graph |
| P3 | 真实 API 对接 | 当前全部为 synthetic_only，需逐步对接真实 API |
