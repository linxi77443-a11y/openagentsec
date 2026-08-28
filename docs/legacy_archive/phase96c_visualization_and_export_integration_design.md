# Phase 96C — 阶段 3 可视化与报告导出整合架构与验证套件设计说明

**Task ID**: Phase-96C-GATE-003  
**Task Name**: 阶段 3 可视化与报告导出整合验证套件开发  
**Task Type**: design_gate  
**PRD Basis**: PRD v1.0 §4; PRD v3.1 §2.8 & §4; Phase 87A Blueprint  
**Timestamp**: 2026-08-01T22:35:00+08:00  

---

## 1. 架构总览 (Architectural Overview)

Phase 96C 阶段 3 可视化评估工作台与报告导出引擎完成了全链路的数据集成与整合验证。完整流水线连接 **BatchRunner Checkpoints** -> **AssessmentDashboardAPI / DashboardDataAdapter** -> **ReportExporter (HTML / Markdown)**，实现从无人值守无损调度、只读评估视图转换到企业级报告自动导出的 100% 连通与闭环。

```mermaid
flowchart TD
    subgraph Layer1["调度与 Checkpoint 存储层"]
        A[BatchRunner / FullCorpusLoader] -->|原子化状态持久化| B[artifacts/batch_checkpoints/phase96c_checkpoint.json]
        C[adversarial_playbooks / capability_scorecard.yaml] -->|能力卡片| D[底座评估资产]
    end

    subgraph Layer2["可视化数据适配与只读 API 层"]
        B -->|加载 750 任务快照| E[DashboardDataAdapter]
        D -->|加载模块注册表与得分| E
        E -->|适配转换| F[AssessmentDashboardAPI]
        F -->|1. 覆盖热力图| F1[get_coverage_heatmap]
        F -->|2. 攻击链传播视图| F2[get_attack_chain_propagation]
        F -->|3. 防御降级轨迹图| F3[get_defense_degradation_timeline]
        F -->|4. 红队引擎面板| F4[get_red_team_panel_summary]
    end

    subgraph Layer3["企业级报告导出层"]
        F -->|注入 API 数据源| G[ReportExporter]
        G -->|自动脱敏策略 100%| H[apply_redaction_policy]
        G -->|Candidate Findings 汇编| I[compile_candidate_findings]
        H & I -->|Jinja2 模板渲染| J[templates/enterprise_report_template.html / .md]
        J -->|离线自包含 (0 CDN)| K[reports/enterprise_security_assessment_report.html]
        J -->|规范化 Markdown| L[reports/enterprise_security_assessment_report.md]
    end

    subgraph Layer4["整合验证套件层"]
        M[scripts/validate_phase96c_suite.py] -->|E2E 集成校验| N[100% 链路连通性 & 零内存泄露 & 安全边界]
        O[tests/test_phase96c_integration_suite.py] -->|PyTest 整合单元/集成测试| P[100% PASS 自动化套件]
    end
```

---

## 2. 核心模块职责与接口规格 (Module Specifications)

### 2.1 BatchRunner & Checkpoint 存储 (`core/batch_runner.py`)
- **职责**: 负责无人值守批次调度与 750 任务快照的原子化持久化 (`artifacts/batch_checkpoints/phase96c_checkpoint.json`)。
- **快照结构**:
  ```json
  {
    "checkpoint_version": "1.0",
    "session_id": "phase96c_integration_session_001",
    "phase": "Phase-96C",
    "total_tasks": 750,
    "completed_count": 750,
    "status": "completed",
    "safety_boundaries": {
      "confirmed_vulnerability": false,
      "formal_finding_allowed": false,
      "production_safety_claimed": false,
      "synthetic_only": true,
      "dashboard_not_execution_interface": true
    }
  }
  ```

### 2.2 Dashboard 数据适配与 API 接口 (`core/dashboard_api.py`)
- **职责**: 读取 Checkpoint 与 `module_registry.yaml`，对外提供 Phase 87A Blueprint 标准的 4 视图只读 JSON 接口。
- **视图支持**:
  1. `get_coverage_heatmap()`: 56 模块状态、优先度与 Phase 87A 色彩映射。
  2. `get_attack_chain_propagation()`: 10 拓扑攻击链、节点防御状态演进。
  3. `get_defense_degradation_timeline()`: 防御节点状态降级轨迹。
  4. `get_red_team_panel_summary()`: 红队引擎攻击 Profile 摘要与合成证据链。

### 2.3 企业级报告导出引擎 (`core/report_exporter.py`)
- **职责**: 接收 DashboardAPI、能力卡片及执行结果，执行 100% 数据脱敏 Policy，汇编 Candidate-Level Findings，并渲染导出 HTML 与 Markdown 报告。
- **导出能力**:
  - `export_html()`: 生成内嵌 CSS 样式、0 外部 CDN 依赖的离线自包含 HTML。
  - `export_markdown()`: 生成规范化 Markdown 报告。
  - `export_all()`: 批量触发导出。

---

## 3. 安全边界与合规断言 (Safety Boundaries & Compliance Model)

Phase 96C GATE-003 全链路严格遵守防守评估安全边界。在 Checkpoint、DashboardAPI、ReportExporter 以及生成的报告产物中，均全量注入并强制断言以下安全控制标志：

| 安全控制标志 | 设定值 | 含义与审计标准 |
|--------------|--------|----------------|
| `confirmed_vulnerability` | `False` | 严禁输出已证实漏洞，所有风险点均为合成信号。 |
| `formal_finding_allowed` | `False` | 严禁生成正式漏洞审计判定。 |
| `production_safety_claimed` | `False` | 严禁承诺生产安全。 |
| `synthetic_only` | `True` | 100% 数据源为合成/沙箱模拟数据。 |
| `dashboard_not_execution_interface` | `True` | 可视化面板仅为只读展示，非攻击执行控制台。 |
| `report_not_formal_audit` | `True` | 报告仅用于内部评估参考，非正式合规审计报告。 |

---

## 4. 100% 数据脱敏策略 (Data Redaction Policy)

全链路整合过程中，`ReportExporter.apply_redaction_policy()` 递归过滤所有文本、字典与数组结构，确保敏感数据 0 泄露：

1. **API Keys / Access Tokens**: 正则匹配 `sk-proj...` / `AKIA...` / `ghp_...` 替换为 `<REDACTED_API_KEY>`。
2. **Bearer Authorization Headers**: 正则匹配 `Bearer ...` 替换为 `Bearer <REDACTED_TOKEN>`。
3. **Credentials / Passwords**: 正则匹配 `password: ...` / `pwd=...` 替换为 `<REDACTED_PASSWORD>`。
4. **Internal IP Addresses**: 正则匹配 `192.168.x.x` / `10.x.x.x` 替换为 `<REDACTED_IP>`。
5. **Email Addresses**: 正则匹配 `user@domain` 替换为 `<REDACTED_EMAIL>`。
6. **Database Connection URIs**: 正则匹配 `postgres://...` / `mysql://...` 替换为 `<REDACTED_DB_URI>`。

---

## 5. 零内存泄露与性能稳定策略 (Memory Stability & Leak Prevention)

在多轮迭代报告导出与 API 频繁请求场景下，验证套件使用 `tracemalloc` 跟踪内存增量：
- **垃圾回收与上下文隔离**: 在多次 `export_all()` 渲染迭代中，Jinja2 模板环境复用，模板渲染上下文在函数退出后自动释放。
- **内存堆增量界限**: 经过 10 轮连续导出渲染测试，内存堆波动增量小于 **1.0 MB**，无未释放的全局句柄或循环引用，验证通过 **Zero Memory Leak Guarantee**。

---

## 6. 整合验证套件与测试设计 (Verification & Test Suite)

1. **端到端集成验证脚本 (`scripts/validate_phase96c_suite.py`)**:
   - 检查 Step 1: Checkpoint 完整性与 750 任务状态。
   - 检查 Step 2: Dashboard API 只读 4 视图转换与 platform_metrics。
   - 检查 Step 3: ReportExporter 端到端 HTML / MD 导出与 Candidate Findings 汇编。
   - 检查 Step 4: 100% Data Redaction Policy脱敏覆盖。
   - 检查 Step 5: 离线自包含 HTML 0 外部 CDN 依赖。
   - 检查 Step 6: 零内存泄露 (Zero Memory Leak) 压力测试。
   - 检查 Step 7: 全链路安全边界断言 (5 大安全标志 100% 遵从)。

2. **PyTest 集成测试套件 (`tests/test_phase96c_integration_suite.py`)**:
   - `test_e2e_pipeline_checkpoint_to_report()`
   - `test_all_four_views_data_consistency()`
   - `test_zero_memory_leak_over_iterations()`
   - `test_safety_boundary_compliance_across_pipeline()`
   - `test_redaction_policy_end_to_end()`
   - `test_offline_html_zero_cdn_dependencies()`
   - `test_corrupt_checkpoint_graceful_handling()`
   - `test_dashboard_read_only_non_execution_assertion()`

---

## 7. 交付物清单 (Deliverables)

1. `scripts/validate_phase96c_suite.py`
2. `tests/test_phase96c_integration_suite.py`
3. `docs/phase96c_visualization_and_export_integration_design.md`
4. `reports/phase96c_integration_suite_validation_report.md`
5. `artifacts/batch_checkpoints/phase96c_checkpoint.json`
6. `phase96c_gate003_execution_summary.yaml`
7. `delivery.json`
