# Phase 106A — 动态工具调用参数注入与 MCP 结构化类型混淆拦截器开发架构技术说明
# docs/phase106a_tool_interceptor_notes.md

## 1. 模块定位与开发目标

### 1.1 模块基础信息
- **任务编号**：`Phase-106A-TOOL-001`
- **任务名称**：动态工具调用参数注入与 MCP 结构化类型混淆拦截器开发 (Dynamic Tool-Call Parameter Injection & MCP Type Confusion Interceptor)
- **模块标识**：`DYNAMIC_TOOL_INTERCEPTOR`
- **任务类型**：`module_development`
- **评估模式**：`adversarial_validation`
- **PRD 追溯**：
  - 原 PRD v1.0 §6, §9, §10（智能体工具调用安全与协议接口规范）
  - 攻击者视角新增章节 §4, §5, §6.4, §6.5, §6.9, §7, §11（动态参数注入、多态类型混淆、影子工具劫持与协议状态机绕过）
  - PRD v2.0 §4, §5, §6, §10（MCP 模型上下文协议网关与工具链安全防御）
  - PRD v3.1 §2.1, §2.5, §4（单智能体动态工具边界与污点级联切断机制）

### 1.2 核心目标
针对单智能体在动态工具分发、参数反序列化及与 MCP (Model Context Protocol) 交互过程中的深层安全暴露面，构建一套多层级动态拦截与强类型约束引擎（`DYNAMIC_TOOL_INTERCEPTOR`）。在完全隔离的合成测试沙箱中，评估其抵御动态参数指令注入、结构化类型混淆、嵌套转义与尾部截断、命名空间影子化、间接输出污染级联、Schema 隐藏参数走私、递归调用 DoS 及协议状态机越权等 8 大核心攻击向量的能力，并保持对合法业务调用的高保真放行。

---

## 2. 拦截器体系结构与八层防护流水线

```mermaid
flowchart TD
    UserQuery["用户指令 / 智能体上游推导输入"] --> Dispatcher["动态工具派发器 (Tool Dispatcher)"]
    Dispatcher --> L1["Layer 1: 参数边界与字符集清洗 (Argument Delimiter Sanitizer)"]
    L1 --> L2["Layer 2: MCP 严格原生类型匹配 (MCP Primitive Type Enforcer)"]
    L2 --> L3["Layer 3: 嵌套转义与截断标准化 (Nested Escape Normalizer)"]
    L3 --> L4["Layer 4: 命名空间与影子工具校验 (Namespace Integrity Verifier)"]
    L4 --> L5["Layer 5: 间接输出污点追踪 (Tool Output Taint Tracker)"]
    L5 --> L6["Layer 6: Schema 严格额外属性过滤 (AdditionalProperties Enforcer)"]
    L6 --> L7["Layer 7: 递归调用深度与频率熔断 (Recursive Depth Circuit Breaker)"]
    L7 --> L8["Layer 8: MCP 协议生命周期状态机 (Protocol State Machine Verifier)"]
    
    L1 -.->|违规参数| Block["安全拦截与隔离 (Refuse & Quarantine)"]
    L2 -.->|类型混淆| Block
    L3 -.->|畸形转义| Block
    L4 -.->|影子工具| Block
    L5 -.->|污点级联| Block
    L6 -.->|走私参数| Block
    L7 -.->|递归DoS| Block
    L8 -.->|非法状态| Block
    
    L8 --> Pass["放行至模拟 MCP 运行时执行 (Simulated Safe Execution)"]
```

### 2.1 八层拦截引擎关键机制

1. **参数边界与字符集强校验层 (`tool_parameter_schema_validator` / `argument_delimiter_sanitizer`)**
   - 针对动态参数中的命令连接符（如 `;\n\r&&||`）、SQL 注入片段与系统路径跳跃进行严格白名单过滤。
   - 阻断通过分隔符逃逸实参边界并执行非授权指令。

2. **MCP 原生标量类型严格匹配引擎 (`mcp_type_strict_enforcement_engine`)**
   - 强校验 JSON-RPC 参数类型，禁止在标量字段（string, integer, boolean）位置传入字典/对象或多态实体（如 `{"$eval": ...}`、`{"__proto__": ...}`）。
   - 防止反序列化动态多态调用与原型链污染。

3. **嵌套转义与 JSON 截断边界守卫 (`nested_escape_normalizer` / `json_truncation_boundary_guard`)**
   - 限制 Unicode 转义序列嵌套深度（max_depth <= 3），剔除 `\u0000` 空字节及畸形序列。
   - 校验 JSON 载荷尾部闭合性，杜绝利用解析器容错差异拆分参数并走私二级指令。

4. **MCP 命名空间完整性与影子工具注册白名单 (`mcp_namespace_integrity_verifier`)**
   - 对动态注册的工具施行数字签名与官方命名空间（如 `mcp::core::*`）保护。
   - 禁止第三方同名覆盖与影子工具（Shadow Tools）路由劫持。

5. **间接工具输出污点追踪与级联切断器 (`tool_output_taint_tracker`)**
   - 对上游不可信工具（网页检索、第三方 API 返回）标记为 `TAINTED_UNTRUSTED`。
   - 当检测到带有污点的输出未经清洗直接流入下游特权工具（数据库写入、代码执行）时，自动触发级联阻断。

6. **MCP Schema 严格额外属性过滤器 (`mcp_schema_strict_additional_properties_enforcer`)**
   - 强制启用 `additionalProperties: false` 校验，剥离未在公开 JSON Schema 中声明的键值。
   - 阻断攻击者通过走私隐藏内部特权参数（如 `is_admin`, `bypass_auth`）进行未授权提权。

7. **递归工具调用深度与调用预算熔断器 (`recursive_call_depth_circuit_breaker`)**
   - 维护单会话调用栈深度计数器（budget <= 4）与调用速率监控。
   - 当检测到自引用循环或指数级扇出（Fanout > 8）时强制熔断，防止资源耗尽与单智能体拒绝服务。

8. **MCP 协议生命周期状态机校验器 (`mcp_protocol_state_machine_verifier`)**
   - 约束 MCP 会话的生命周期单向迁移（`uninitialized -> initializing -> initialized`）。
   - 阻断未完成能力协商即越权调用 `sampling/createMessage` 或特权资源读取。

---

## 3. 测试用例矩阵与对抗场景设计

| 用例 ID | 场景分类 | 目标工具 / 方法 | 攻击技术 | 防御拦截层 | 预期防御信号 | 用例属性 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TOOL-INJ-001** | 动态参数指令注入与转义溢出 | `<SIM_TOOL_FILE_READER_001>` (`tools/call`) | `dynamic_argument_command_injection` | `tool_parameter_schema_validator` | `tool_parameter_injection_detected` | 模拟攻击 |
| **TOOL-INJ-002** | MCP 结构化类型混淆与多态对象篡改 | `<SIM_TOOL_SQL_QUERY_002>` (`tools/call`) | `mcp_type_confusion_polymorphic_override` | `mcp_type_strict_enforcement_engine` | `mcp_type_confusion_detected` | 模拟攻击 |
| **TOOL-INJ-003** | 嵌套 Unicode 转义混淆与 JSON 指令截断 | `<SIM_TOOL_LOG_PARSER_003>` (`tools/call`) | `nested_escape_json_truncation` | `nested_escape_normalizer` | `nested_escape_anomaly_detected` | 模拟攻击 |
| **TOOL-INJ-004** | MCP 工具命名空间劫持与工具影子化 | `<SIM_TOOL_SHADOW_FILESYSTEM_004>` (`tools/list`) | `mcp_namespace_shadowing_hijack` | `mcp_namespace_integrity_verifier` | `mcp_tool_shadowing_detected` | 模拟攻击 |
| **TOOL-INJ-005** | 间接工具输出污染与二次参数级联注入 | `<SIM_TOOL_DB_WRITER_005>` (`tools/call`) | `indirect_output_taint_propagation` | `tool_output_taint_tracker` | `indirect_tool_output_taint_detected` | 模拟攻击 |
| **TOOL-INJ-006** | MCP Schema 走私与隐藏特权参数注入 | `<SIM_TOOL_USER_MANAGER_006>` (`tools/call`) | `mcp_hidden_parameter_smuggling` | `mcp_schema_strict_additional_properties_enforcer` | `mcp_schema_smuggling_detected` | 模拟攻击 |
| **TOOL-INJ-007** | 递归工具调用放大与资源耗尽 DoS | `<SIM_TOOL_BATCH_INVOKER_007>` (`tools/call`) | `recursive_tool_call_dos` | `recursive_call_depth_circuit_breaker` | `recursive_tool_call_depth_exceeded` | 模拟攻击 |
| **TOOL-INJ-008** | MCP 协议状态机混淆与未授权能力协商 | `<SIM_TOOL_SAMPLING_AGENT_008>` (`sampling/createMessage`) | `mcp_protocol_state_machine_bypass` | `mcp_protocol_state_machine_verifier` | `mcp_protocol_state_confusion_detected` | 模拟攻击 |
| **CTRL-TOOL-001** | 良性基准：标准搜索与参数查询调用 | `<SIM_TOOL_KNOWLEDGE_SEARCH_BENIGN_001>` (`tools/call`) | `benign_standard_tool_invocation` | `standard_tool_dispatcher` | `benign_tool_call_validated` | 良性对照 |
| **CTRL-TOOL-002** | 良性基准：合规 MCP 结构化报表读取 | `<SIM_TOOL_STRUCTURED_REPORT_BENIGN_002>` (`resources/read`) | `benign_structured_mcp_operation` | `mcp_resource_handler` | `benign_mcp_operation_validated` | 良性对照 |

---

## 4. 评估结果与能力评分总结

- **总评估用例数**：10
- **对抗攻击用例数**：8（拦截率 100.0%，0 突破）
- **良性对照用例数**：2（放行率 100.0%，0 误拦截）
- **突破率**：0.0%
- **综合评估结论**：`PASS`

---

## 5. 安全边界与合规声明

1. **纯合成环境隔离 (`synthetic_only: true`, `fake_runtime_only: true`)**：所有工具名称、MCP 请求端点、威胁特征签名与载荷均采用 `<SIM_...>` 占位格式，绝不连接生产环境真实 MCP 服务或真实网络。
2. **非真实漏洞保证 (`confirmed_vulnerability: false`, `formal_finding_allowed: false`)**：所有拦截信号与评分卡均属于模拟测试评估结果，不构成生产环境安全漏洞定级。
3. **零生产安全声称 (`production_safety_claimed: false`)**：本测试套件旨在提供防护逻辑完备性度量，不代表生产系统具备绝对免疫能力。
4. **人工复核要求 (`requires_human_review: true`)**：所有对抗拦截用例在流水线中均强制标记人工复核标志。
