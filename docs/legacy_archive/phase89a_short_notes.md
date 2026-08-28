# Phase 89A — AI 安全评估仪表盘 (dashboard_quarantined_prototype) 开发笔记

## 概述

Phase 89A 构建了 AI 安全评估仪表盘 quarantined prototype，作为 M43-M50 模块覆盖矩阵、攻击链传播静态视图、防御降级轨迹追踪和候选研判面板的可视化展示。

**重要**：本阶段为 quarantined prototype，not_module_mvp=true, no_registry_coverage_credit=true, dashboard_implementation_allowed=false。不支持攻击链执行或受控回放。不链接 release baseline。

## 回滚修正内容（裁判审核反馈）

1. **命名修正**：从"Phase 89A MVP"改为"dashboard_quarantined_prototype"
2. **engine-panel.js → candidate-review-panel.js**：重命名并重写为静态候选研判面板，移除所有"红队引擎/攻击配置/模拟执行"表述
3. **D3.js CDN**：标注 external_network_required=true
4. **新增声明字段**：not_module_mvp, no_registry_coverage_credit, not_execution_module, no_attack_chain_execution, no_controlled_replay_execution, dashboard_implementation_allowed
5. **release baseline 解链**：footer 标注不链接 release baseline
6. **CDN 隔离**：D3.js 从 CDN 下载至 `dashboard/js/lib/d3.min.js`，改为本地加载；external_network_required=false；新增 external_network_allowed=false；静态检查确认无外部 URL 依赖

## 架构设计

- **纯前端**：HTML + CSS + JS，无后端依赖
- **本地数据**：所有数据来自本地静态 JSON 文件（`dashboard/data/` + `mock_fixtures/phase88a/`）
- **可视化引擎**：D3.js v7（本地加载 `dashboard/js/lib/d3.min.js`，external_network_required=false, external_network_allowed=false）
- **数据安全**：所有数据标记 synthetic_only=true，confirmed_vulnerability=false

## 交付物清单

| 文件路径 | 状态 |
|----------|------|
| `dashboard/index.html` | ✅ 回滚修正完成 |
| `dashboard/css/style.css` | ✅ 无变动 |
| `dashboard/js/data-loader.js` | ✅ 无变动 |
| `dashboard/js/app.js` | ✅ engine → candidate_review 路由修正 |
| `dashboard/js/heatmap-view.js` | ✅ 无变动 |
| `dashboard/js/propagation-view.js` | ✅ 无变动 |
| `dashboard/js/timeline-view.js` | ✅ 无变动 |
| `dashboard/js/candidate-review-panel.js` | ✅ 新建（替代 engine-panel.js） |
| `dashboard/data/*.json` | ✅ data_config.json 标签修正，其余不变 |
| `dashboard/README.md` | ✅ 回滚修正完成 |
| `dashboard/validator_checklist.yaml` | ✅ 回滚修正完成 |
| `dashboard/validate_results.md` | ✅ 回滚修正完成 |
| `dashboard/js/lib/d3.min.js` | ✅ 新增（本地 D3.js v7，替代 CDN 引用） |
| `dashboard/dashboard_isolation_validation_result.md` | ✅ 新增（CDN 隔离验证结果） |
| `docs/phase89a_short_notes.md` | ✅ 回滚修正 + CDN 隔离完成 |

## 结果摘要

### 声明字段

| 字段 | 值 |
|------|-----|
| not_module_mvp | true |
| no_registry_coverage_credit | true |
| not_execution_module | true |
| no_attack_chain_execution | true |
| no_controlled_replay_execution | true |
| dashboard_implementation_allowed | false |
| external_network_required | false |
| external_network_allowed | false |
| synthetic_only | true |
| confirmed_vulnerability | false |
| formal_finding_allowed | false |
| production_safety_claimed | false |

### 视图功能

| 视图 | 核心功能 | 数据源 |
|------|----------|--------|
| 攻击面覆盖热力图 | 模块 × 攻击阶段覆盖矩阵、统计卡片、模块详情 | module_registry_snapshot.json |
| 攻击链传播视图 | D3.js 力导向图、路径筛选、悬浮 tooltip（静态展示） | attack_path_catalog.json |
| 防御降级轨迹图 | 状态机路径、D3 时间线图表、防御事件日志 | state_machine.json, mock_defense_state_events.json |
| 候选研判面板 | 安全边界断言、红蓝紫映射、模块安全元数据（静态展示） | safety_boundary_assertions.json, red_blue_purple_mapping.json |

## 使用方式

```bash
cd dashboard
python3 -m http.server 8766
# 浏览器打开 http://localhost:8766
```
