# Phase 99A 动态回放套件（Dynamic Replay Suite）架构与设计规范

**文档编号**: DOC-DES-99A-002  
**任务编号**: Phase-99A-GATE-003  
**模块标识**: `multi_agent/replay/phase99a_dynamic_replay_suite.py`  
**版本**: v1.0-master  
**日期**: 2026-08-18  

---

## 1. 概述与 PRD 追溯

动态回放套件（Dynamic Replay Suite）是 Phase 99A 高阶对抗剧本的核心编排执行引擎，旨在为 M43（MCP 工具完整性）、M45（AI 依赖安全）、M48（RAG 知识库多跳投毒）与 M50（沙箱逃逸防御）提供高保真、多阶段、时序一致且 100% 受控的拟真回放环境。

### 1.1 PRD 关联映射
- **原 PRD v1.0**:
  - §4 多智能体协作架构与角色权限边界
  - §6 评估指标量化与客观评测
  - §10 安全边界与非执行承诺
  - §15 供应链安全与外部工具隔离
- **攻击者视角新增章节**:
  - §2 AI 供应链（MCP/依赖）高阶对抗建模
  - §4 多阶段攻击链跨边界穿透推演
  - §7 突破信号与指标量化的正交解耦
  - §11 受控复现审批与防越权防生产穿透体系
- **PRD v2.0**:
  - §4 威胁建模与沙箱隔离规范
  - §9.3 8 节点受控复现授权审批门禁（Controlled Replay Gatekeeper）
  - §10 动态回放与状态机回滚机制
  - §13 形式化缺口（GAP）闭环与对账
- **PRD v3.1**:
  - §2.3 Fake Runtime 拟真沙箱环境与零生产穿透
  - §2.6 知识库检索溯源与向量空间防御
  - §2.7 动态回放引擎协同与状态机一致性
  - §3 不可篡改审计日志与签名链
  - §4 非回溯性（Non-Retroactivity）保障

---

## 2. 动态回放生命周期状态机

动态回放会话生命周期严格遵循不可逆的状态机流转，必须获得 Gatekeeper Node 5（复现执行审批总门禁）的法定人工签名授权方可启动执行。

```mermaid
stateDiagram-v2
    [*] --> INITIALIZED: 创建回放会话 (create_replay_session)
    INITIALIZED --> GATE_PENDING: 绑定多阶段攻击链与目标配置
    
    GATE_PENDING --> RUNNING: Gatekeeper Node 5 人工签名批准 (authorize_session)
    GATE_PENDING --> BLOCKED: 试图越权跳步执行 (StepSkipping / MissingGateApproval)
    
    state RUNNING {
        [*] --> Step1_Exec
        Step1_Exec --> Step1_Check: Fake Runtime 校验
        Step1_Check --> Step2_Exec: 时序递进 (current_step + 1)
        Step2_Exec --> Step2_Check: 异常防护检测 (10 Known-Bad)
        Step2_Check --> Step3_Exec
        Step3_Exec --> Step3_Check
        Step3_Check --> Step4_Exec
        Step4_Exec --> Step4_Check
        Step4_Check --> [*]
    }
    
    RUNNING --> INTERCEPTED: 命中已知威胁模式并由防御层成功拦截 (Expected Signal)
    RUNNING --> ABORTED: 触发中止条件 (ABORT-01 ~ ABORT-07)
    RUNNING --> BLOCKED: 命中 Known-Bad 违规参数 (生产穿透 / 真实外联 / ANSI 篡改)
    
    INTERCEPTED --> COMPLETED: 生成拟真证据链 Trace 与审计快照
    COMPLETED --> [*]
    BLOCKED --> [*]
    ABORTED --> [*]
```

### 2.1 状态枚举定义
- `INITIALIZED`: 会话初始化，分配 `DRS-SES-XXXXXXXX` 唯一会话标识符。
- `GATE_PENDING`: 等待 8 节点门禁的 Node 5 法定审批。
- `RUNNING`: 经授权批准，正在 Fake Runtime 中按时序执行多阶段攻击链。
- `INTERCEPTED`: 攻击载荷被防御规则拦截，生成 `threat_intercepted` 信号。
- `ABORTED`: 触发法定中止条件或人工撤销。
- `COMPLETED`: 全部多阶段步骤按时序执行完毕，输出完整审计报告。
- `BLOCKED`: 违规操作（如跳步、生产参数、真实凭据）被硬性阻断，会话永久冻结。

---

## 3. Fake Runtime 拟真沙箱架构与安全不变量

Fake Runtime 是本套件的核心安全基石，确保所有回放操作均在内存拟真层执行，不依赖也不接触任何外部真实系统。

```mermaid
flowchart LR
    subgraph Client["调用方 / 测试套件"]
        Req["Replay Request (Chain Step)"]
    end

    subgraph Guardrails["Fake Runtime 安全不变量守护层"]
        MCP_Guard["MCP 协议拦截器 (DRS-KB-001)"]
        Registry_Guard["依赖镜像源拦截器 (DRS-KB-002)"]
        Cmd_Guard["命令执行阻断器 (DRS-KB-003)"]
        Vector_Guard["向量库隔离拦截器 (DRS-KB-004)"]
        Sandbox_Guard["容器逃逸阻断器 (DRS-KB-005)"]
        Audit_Guard["ANSI 流清洗器 (DRS-KB-006)"]
        Cred_Guard["生产密钥正则扫描器 (DRS-KB-008)"]
    end

    subgraph SimEngine["纯内存拟真执行器"]
        SyntheticTrace["生成 <SIM_...> 证据链"]
        SignalEmit["发射 expected_signal (如 mcp_descriptor_poisoning_detected)"]
        AuditLog["记录不可篡改审计日志"]
    end

    Req --> Guardrails
    Guardrails -- 违规注入 --> BlockErr["抛出专有异常 (PASS in Known-Bad Test)"]
    Guardrails -- 合规拟真 --> SimEngine
```

### 3.1 核心安全不变量
1. **零真实 MCP 连接 (`real_mcp_server_allowed: false`)**: 拒绝一切 `http://`, `ws://` 真实 MCP Server 连接请求。
2. **零远程包索引外联 (`real_package_registry_allowed: false`)**: 拒绝外部未经审核的 PyPI/NPM 源地址。
3. **零宿主机命令执行 (`real_build_command_allowed: false`)**: 阻断 `setup.py`、`Makefile` 或构建钩子中的 Shell 执行。
4. **零真实向量数据库交互 (`real_vector_db_allowed: false`)**: 阻断 Pinecone、Milvus、Qdrant 等真实向量库连接。
5. **零真实沙箱穿透 (`real_sandbox_escape_allowed: false`)**: 阻断 `nsenter`、`cgroup` 逃逸利用载荷。
6. **不可变审计流 (`real_audit_log_mutation_allowed: false`)**: 严格过滤 ANSI 转义字符，禁止覆写审计记录。
7. **数据纯合成性 (`synthetic_only: true`)**: 严格扫描并阻断生产凭证模式（`sk-live-...`, `AKIA...`）。

---

## 4. 多阶段攻击链模型规范

套件内置 4 条预定义的复合多阶段攻击链模型：

### 4.1 `CHAIN-99A-01`: 供应链至沙箱全维度攻击链
- **阶段 1 (M45)**: 依赖仿冒投毒 (`M45-ADV-001`) — 注入 `<SIM_PYPI_POISONED_PKG_001>`
- **阶段 2 (M43)**: MCP Schema 深层注入 (`M43-ADV-001`) — 嵌套 properties 覆盖声明
- **阶段 3 (M48)**: RAG 多文档碎片拼接 (`M48-ADV-001`) — 跨 3 个文档拼接越权指令
- **阶段 4 (M50)**: 沙箱渐进式逃逸探测 (`M50-ADV-001`) — 跨 5 轮探测隔离边界

### 4.2 `CHAIN-99A-02`: MCP 工具混淆与权限伪造链
- **阶段 1 (M43)**: 同形异义字 Unicode 混淆 (`M43-ADV-002`) — 西里尔字母仿冒工具名
- **阶段 2 (M43)**: 运行时清单哈希漂移 (`M43-ADV-003`) — 注册后修改工具描述
- **阶段 3 (M43)**: 跨工具能力遮蔽 (`M43-ADV-004`) — 声明 priority=999 劫持流量
- **阶段 4 (M43)**: 伪造合规审计豁免 (`M43-ADV-005`) — 假冒免检运维权限

### 4.3 `CHAIN-99A-03`: 依赖传递木马与构建钩子劫持链
- **阶段 1 (M45)**: 深层 3 跳传递依赖木马 (`M45-ADV-002`)
- **阶段 2 (M45)**: Lockfile 校验和漂移 (`M45-ADV-003`)
- **阶段 3 (M45)**: 仿冒私有包索引源 (`M45-ADV-004`)
- **阶段 4 (M45)**: setup.py 自定义 build 钩子执行 (`M45-ADV-005`)

### 4.4 `CHAIN-99A-04`: RAG 向量隐蔽与沙箱挂载穿透链
- **阶段 1 (M48)**: 多跳知识图谱循环诱导 (`M48-ADV-002`)
- **阶段 2 (M48)**: 高维向量嵌入空间掩蔽 (`M48-ADV-004`)
- **阶段 3 (M48)**: 虚假权威安全政策引用 (`M48-ADV-005`)
- **阶段 4 (M50)**: 临时文件系统与符号链接越界探测 (`M50-ADV-004`)

---

## 5. 8 节点门禁集成与签名链保障

回放引擎与 `ControlledReplayGatekeeper` 深度绑定：
- **门禁前置条件**: 会话初始化后处于 `GATE_PENDING` 状态。
- **Node 5 执行授权**: 必须由具备 `ReviewerRoleEnum.SECURITY_LEAD` 角色的责任人签署合法 `HumanSignature`。
- **防自动化绕过**: 严禁 `is_automated_override: true`，自动化机器签名将被直接拒绝。
- **防跳步阻断**: 步骤索引必须连续（`step_index == current_step_index`），任何非连续执行将抛出 `StepSkippingViolation` 并将状态置为 `BLOCKED`。

---

## 6. 联合对账引擎设计

`Phase99AJointReconciliation` 类负责对 Phase 99A 全部 24 个用例实施端到端对账：
- **M43/M45 供应链剧本**: 12 个用例（10 攻击 + 2 基线）
- **M48/M50 RAG/沙箱剧本**: 12 个用例（10 攻击 + 2 基线）
- **判定标准**:
  - 20 个攻击用例：`defensive_check_passed=True`, `breakthrough_detected=False`, `confirmed_vulnerability=False`, `requires_human_review=True`。
  - 4 个基线用例：`control_case=True`, `defensive_check_passed=True`, `breakthrough_detected=False`。
  - 全部 24 个用例：`synthetic_only=True`, `formal_finding_allowed=False`, `production_safety_claimed=False`。
