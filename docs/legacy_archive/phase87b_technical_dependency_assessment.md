# Phase 87B — AI安全评估可视化实施准备评估
# 技术依赖评估

## 范围

本评估列出可视化开发阶段可能需要的技术依赖类型和候选方案。
**本任务不选择具体方案**，仅评估各候选类型的适用条件。

---

## 1. 前端框架候选

### 需求
- 支持多 Tab 仪表盘布局
- 支持交互式数据表格和网格渲染
- 支持 SVG/Canvas 辅助渲染（非必须 — 图表库处理）
- 支持响应式布局
- 权限控制（viewer/analyst/operator/admin）

### 候选类型
| 类型 | 适合场景 | 注意事项 |
|------|---------|---------|
| 纯静态 HTML + CSS + JS | 最小依赖, 快速原型 | 无状态管理, 不适合复杂交互 |
| 轻量 SPA 框架 | 中等复杂度仪表盘 | 需构建工具, 学习成本可控 |
| 全功能前端框架 | 大规模仪表盘 | 构建复杂, 维护成本高 |

### 评估结论
四类视图均在同一 dashboard 内以 Tab 切换，视图间有 cross_filter 联动需求。建议候选为轻量或中型框架，不支持重型框架。

---

## 2. 图表库候选

### 需求
- 热力图渲染（coverage_heatmap — 矩阵 × 着色）
- 有向图渲染（attack_chain_propagation — 节点 + 边布局）
- 水平堆积条/状态时间线（defense_degradation_timeline）
- 表单+按钮+信息面板（red_team_engine — 面板式, 非图表）
- 所有着色依据 7 级覆盖色图 + 5 态防御色图

### 候选类型
| 类型 | 适合视图 | 注意事项 |
|------|---------|---------|
| 通用统计图表库 | 热力图、时间线 | 需要确认是否支持自定义着色和矩阵布局 |
| 专用可视化库 | 有向图（DAG 布局） | 攻击链传播需要合理的自动布局算法 |
| 轻量 SVG 渲染 | 自定义视图 | 开发量大, 灵活度最高 |

### 评估结论
- 热力图：通用图表库即可
- 攻击链传播：需要支持 DAG/有向图自动布局
- 防御降级轨迹：水平状态条通用图表库支持
- 红队引擎面板：不需要图表库，基于表单+卡片组件即可

---

## 3. YAML/JSON 数据解析层

### 需求
- 读取本地 YAML 文件（模块注册表、scorecard、result、schema 文件）
- JSON 序列化/反序列化
- 字段映射和类型转换

### 候选
| 类型 | 说明 |
|------|------|
| Python PyYAML | 项目已有, 用于前端数据预处理 |
| JavaScript js-yaml | 前端浏览器端解析 YAML（可选） |
| 内置 JSON API | 前端 fetch + JSON.parse |

### 评估结论
数据加载方式取决于前端架构。如果采用纯静态方式，建议通过 Python 脚本预处理 YAML → JSON 静态文件；如果采用 SPA 方式，建议前端直接请求 YAML 或通过转换后的 JSON API。

---

## 4. Schema Validation 层

### 需求
- 验证 dashboard 数据是否符合 Phase 87A 数据契约
- 验证字段类型、枚举值范围
- 验证 security boundary 字段一致性

### 候选
| 类型 | 说明 |
|------|------|
| Python jsonschema 库 | 后端预处理时验证 |
| 自定义 YAML 结构检查 | 轻量方案, 类似现有 validate 脚本模式 |
| TypeScript 类型定义 | 前端编译时检查 |

### 评估结论
建议复用 Phase 87A validate 脚本的检查逻辑（16 类别 169 checks），增加数据契约层验证。

---

## 5. 静态资产加载方式

### 需求
- 加载 YAML schema 定义（颜色语义、权限角色、筛选规则）
- 加载模块数据（registry、scorecard、result）
- 无需数据库连接、无 API 服务

### 候选
| 方式 | 说明 |
|------|------|
| Python 预处理 → JSON 静态文件 | 构建时生成静态数据 |
| 前端直接 fetch YAML | 运行时解析 |
| 嵌入式数据 + 构建脚本 | 混合模式 |

### 评估结论
推荐 Python 预处理方式，因为 YAML 解析在 Python 端已有成熟工具链（PyYAML），且项目已有大量 validate/build 脚本可作为预处理模板。

---

## 6. 权限与安全口径展示约束

### 必须满足的口径
- `capability_value` 与 `risk_level` 显示分离，不合并为单一分数
- `breakthrough_detected` 旁标注 "simulated capability signal only"
- `defense_state=breached` 旁标注 "simulated signal, not confirmed vulnerability"
- hot 颜色（红色/橙色）旁附带颜色语义说明
- 不允许显示 `confirmed_vulnerability=true`、`formal_finding`
- 不允许声明 `production_safety`、`controlled_replay_safety`
- `result_semantics=needs_human_review` 的模块需要标注人工复核标记

### 实现方式
- 所有视图必须包含安全口径注释区域
- 颜色图例必须包含语义说明（不仅是颜色名）
- 导出快照必须保留所有安全口径文本
