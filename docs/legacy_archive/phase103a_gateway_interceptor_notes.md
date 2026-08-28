# Phase 103A — M23 Stream Gateway: 实时流式代理评估网关技术设计与架构说明

## 1. 任务概述与设计背景
在企业级 Agentic AI 落地场景中，Server-Sent Events (SSE) 与 WebSocket 流式传输已成为大模型推理与多智能体（Multi-Agent）双向协同的核心交互协议。传统基于静态全量请求/响应（Full-Payload Inspection）的安全网关在面对流式输出时存在天然的“时间与空间盲区”：
1. **静态检测滞后**：传统网关必须等待流式输出全部结束才能进行内容审核，导致下游消费者已先期执行恶意指令。
2. **跨分块走私（Cross-Chunk Smuggling）**：攻击者通过故意将敏感指令或恶意 Token 拆散在连续的微小分块（Chunk/Frame）边界，绕过单分块独立校验。
3. **流式凭据外泄（Streaming Exfiltration）**：受控或越狱的模型在流式输出中外泄内部密钥，必须在毫秒级时间内执行跨 Token 缓冲回滚与流切断。

Phase-103A-GATEWAY-001 构建并验证企业级 **Agentic 安全代理与流式拦截器 (Agentic Security Proxy & Stream Interceptor)**，实现毫秒级流式分块检测、Token 级走私识别、流式中间人混淆拦截、敏感数据动态脱敏与良性业务流平滑放行。

---

## 2. 核心威胁模型与拦截场景

| 用例编号 | 威胁分类 | 传输协议 | 攻击手法与特征 | 拦截机制与关键信号 |
| :--- | :--- | :--- | :--- | :--- |
| `STREAM-GW-001` | Token 级走私与跨 Chunk 拼接 | SSE | 将越狱提示拆分在相邻 SSE `data:` 分块边界 | 流式滑动窗口重组器识别跨边界指令 (`cross_chunk_token_smuggling_intercepted`) |
| `STREAM-GW-002` | WebSocket 增量分片 Tool-Call 走私 | WebSocket | 利用增量 JSON 帧逐步拼装未授权特权工具调用 | 增量 JSON AST 状态机在闭合前拦截 (`websocket_malicious_tool_call_blocked`) |
| `STREAM-GW-003` | 流式中间人 ANSI 控制字符混淆 | SSE / HTTP Chunked | 注入终端转义序列与零宽字符欺骗审计渲染 | 流式控制字符实时过滤器净化阻断 (`stream_control_sequence_stripped_and_blocked`) |
| `STREAM-GW-004` | 动态分块敏感凭据流式泄露 | SSE | 模型逐 Token 吐出 API Key/密钥 | 延迟重叠缓冲区正则回滚脱敏 (`streaming_credential_leak_redacted_and_severed`) |
| `STREAM-GW-005` | 多字节 UTF-8 跨 Chunk 分割走私 | SSE | 在 3/4 字节 Unicode 编码中间截断分块造成解码脱节 | 流式多字节 UTF-8 状态机重组校验 (`unicode_chunk_split_smuggling_intercepted`) |
| `STREAM-GW-006` | 慢速 Token 耗尽 DoS 攻击 | SSE / WebSocket | 极慢速发送单个 Token 耗尽并发连接池 | Token 到达间隔延迟监控与熔断器 (`slow_stream_dos_throttled_and_terminated`) |
| `STREAM-GW-007` | 递归流式提示注入与反射越狱 | SSE | Markdown 代码块嵌套二次注入引发下游循环提权 | 流式语义上下文深度解析与门禁阻断 (`recursive_stream_injection_intercepted`) |
| `STREAM-GW-008` | WebSocket 二进制帧隐写走私 | WebSocket Binary | 二进制帧伪装图片头嵌入结构化控制指令 | 二进制帧文件头魔数与信息熵分析 (`websocket_binary_smuggling_detected_and_dropped`) |
| `CTRL-STREAM-001` | 良性 SSE 业务文本长流式放行 | SSE | 10 分块合规业务周报输出 | 零误报平滑中继 (`benign_sse_stream_passed`) |
| `CTRL-STREAM-002` | 良性 WebSocket 结构化 Tool-Call 放行 | WebSocket | 标准天气查询合法工具调用分片 | AST 白名单合规放行 (`benign_websocket_tool_call_passed`) |

---

## 3. 架构设计与流式拦截管道

```
  [ Client / Upstream Agent ]
             │
      ( SSE / WebSocket )
             ▼
┌─────────────────────────────────────────────────────────┐
│       Agentic Security Proxy & Stream Interceptor       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 1. Frame / Chunk Demux & UTF-8 Byte State Machine │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 2. Sliding Window Token Reassembler & AST Parser   │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 3. Realtime Stream Sanitizer & DLP Rollback Buffer│  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 4. Cadence Monitor & Binary Entropy Analyzer       │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│             [ Security Policy Adjudication ]            │
│            /                                \           │
│      [ Violations ]                    [ Compliant ]    │
│            │                                  │         │
│     Terminate & Reset                  Forward Chunk    │
│     (Send Event / Close)               (Low Latency)    │
└────────────┬──────────────────────────────────┬─────────┘
             │                                  │
             ▼                                  ▼
      [ Security Log ]              [ Downstream Execution ]
```

### 3.1 关键拦截组件
1. **多字节 UTF-8 字节状态机 (UTF-8 Boundary State Machine)**：
   - 维护跨 Chunk 的未完成多字节缓冲区，防止因截断引发解码异常或解析器绕过。
2. **滑动窗口重组器 (Sliding Window Token Reassembler)**：
   - 维持固定 Token 长度（默认 64-128 Tokens）的滑动窗口，对跨边界拼接指令执行实时模式匹配。
3. **流式增量 JSON AST 状态机 (Incremental JSON AST Stream Parser)**：
   - 针对 WebSocket Tool-Call 增量分片，动态构建抽象语法树，在识别到高危敏感工具名瞬间终止流。
4. **低延迟 DLP 延迟重叠缓冲区 (DLP Rollback Buffer)**：
   - 引入可控微延迟（Latency Budget < 15ms），在敏感凭据被完整识别时阻断下游转发，并将已发送前端替换为安全脱敏掩码 `<REDACTED_SECRET>`。
5. **流速节奏监控与慢速流熔断器 (Cadence Monitor & Circuit Breaker)**：
   - 计算 Inter-Token Latency (ITL) 与抖动率，对异常慢速长连接及时熔断，防止连接池资源枯竭。
6. **二进制帧熵值与魔数校验器 (Binary Frame Entropy Analyzer)**：
   - 检验 WebSocket 二进制帧的 Magic Bytes 及熵分布，拦截伪装成多媒体数据的结构化注入载荷。

---

## 4. 安全红线与隔离约束

本项目严格遵守授权模拟红队平台的安全边界规范：
- `confirmed_vulnerability`: `false`
- `formal_finding_allowed`: `false`
- `production_safety_claimed`: `false`
- `controlled_replay_claimed`: `false`
- `synthetic_only`: `true`
- `fake_runtime_only`: `true`
- `requires_human_review`: `true`
- 所有数据与载荷均为 `<SIM_...>` 纯合成占位符。
- 绝不连接真实 SSE/WebSocket 服务端、大模型推理端点或生产网络。
