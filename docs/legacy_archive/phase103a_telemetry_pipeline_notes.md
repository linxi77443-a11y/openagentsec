# Phase 103A — M23 Telemetry Pipeline: 实时指标遥测与告警分发管道技术设计与架构说明

## 1. 任务概述与设计背景
在企业级 Agentic AI 与大规模大模型推理系统中，实时指标遥测（Streaming Telemetry）与动态告警分发（Alert Dispatcher）是维系整套系统安全与高可用的“中枢神经”。随着大模型应用向多智能体协作、高并发实时流交互演进，传统静态日志收集与定时巡检监控面临严峻挑战：
1. **指标投毒与基线污染 (Metric Poisoning & Baseline Drift)**：对抗攻击者通过向遥测流注入高频微幅伪造指标，恶意拉高动态基线均值并改变方差，掩盖后续真实的越狱与高危注入攻击。
2. **告警风暴与分发阻塞 (Alert Storm & Dispatch Starvation)**：突发海量低危或重复异常事件可能耗尽告警分发队列与下游 Webhook 连接池，造成关键 P0/P1 熔断告警被丢弃或严重延迟。
3. **遥测抑制与静默盲区 (Telemetry Suppression & Silent Blindspots)**：受控节点通过阻断心跳上报制造“无告警即安全”的伪象，要求系统具备毫秒级死信看门狗（Deadman Switch）探测。
4. **审计篡改与事件回放 (Audit Tampering & Replay Drift)**：对安全日志进行时间戳回溯或哈希链篡改，企图抹除渗透痕迹，必须建立具备不可篡改哈希链（Forward Hash Chaining）与时间窗口容差检验的审计归档引擎。

Phase-103A-TELEMETRY-002 构建并验证高吞吐、低延迟的**实时遥测管道与动态告警分发引擎 (Telemetry Pipeline & Alert Dispatcher)**，实现流式指标实时聚合、滑动窗口多维异常检测、告警降噪与反洪泛限流、多通道 Webhook/EventBus 仿真分发与不可篡改审计流归档。

---

## 2. 核心威胁模型与管道处理场景

| 用例编号 | 威胁/处理分类 | 协议/通道 | 攻击手法与特征 | 防御与分发机制 | 关键信号与指标 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TELEMETRY-ADV-001` | 指标投毒与基线漂移 | gRPC Streaming | 注入 500 条篡改均值/方差的虚假 Token/s 指标 | 鲁棒 IQR 四分位距与截断均值过滤 | `metric_poisoning_filtered_and_baseline_protected` |
| `TELEMETRY-ADV-002` | 告警风暴与分发阻塞 | HTTPS Batch | 突发 1200 条重复低优先级告警洪水 | 漏桶反洪泛限流器与指纹滑动窗口去重 (去重率>95%) | `alert_storm_throttled_and_deduplicated` |
| `TELEMETRY-ADV-003` | 遥测心跳抑制攻击 | gRPC Streaming | 关键节点突发静默中断心跳上报超过 3000ms | 节点租约管理与死信看门狗 (Deadman Switch) | `telemetry_heartbeat_timeout_detected` |
| `TELEMETRY-ADV-004` | 伪造 P0 告警反向注入 | EventStream | 未签名伪造 P0 熔断事件试图诱发业务震荡 | HMAC-SHA256 签名鉴权与非受信事件丢弃 | `spoofed_alert_signature_rejected` |
| `TELEMETRY-ADV-005` | 审计流哈希链篡改 | Kafka Sim | 篡改历史审计记录父哈希指针与非单调时间戳 | SHA-256 前向 Merkle 哈希链检验与异常流隔离 | `audit_stream_tamper_detected_and_quarantined` |
| `TELEMETRY-ADV-006` | 多维指标协同突增异常 | gRPC Streaming | Token 消耗激增 12x 且威胁置信度瞬时攀升至 0.98 | 多元协方差马氏距离检测与 P0 动态升级 | `multidim_metric_burst_detected_and_escalated` |
| `TELEMETRY-ADV-007` | Webhook 端点故障与重试耗尽 | HTTPS Batch | 模拟主 SIEM Webhook 504 网关超时 | 3次指数退避重试与死信队列 (DLQ) 无损保全 | `dispatcher_failover_to_dlq_success` |
| `TELEMETRY-ADV-008` | 遥测时间戳回放与时钟漂移 | EventStream | 注入 1800s 严重时钟漂移的历史旧遥测帧 | ±5000ms 滑动时间窗口容差门与 Nonce 防重放 | `timestamp_replay_drift_rejected` |
| `CTRL-TELEM-001` | 良性指标常态流式上报 | gRPC Streaming | 1000 条常规负载业务指标流 | 滑动窗口均值平稳聚合与零误报告警 | `benign_telemetry_aggregated_smoothly` |
| `CTRL-TELEM-002` | 良性常规运维告警分发 | HTTPS Batch | 50 条合法 P3 信息级运维通知 | 基于策略的多通道精准路由与审计持久化 | `benign_alert_dispatched_successfully` |

---

## 3. 架构设计与遥测告警管道

```
  [ Ingestion Gateways & Agents ]
                 │
   ( gRPC / HTTPS / EventStream )
                 ▼
┌─────────────────────────────────────────────────────────┐
│        Telemetry Pipeline & Alert Dispatcher Engine     │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 1. Time-Window & Nonce Gate (±5000ms Replay Guard)│  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 2. Sliding Window Aggregator & Robust IQR Filter  │  │
│  │    - Token/s, Latency, Error Density, Confidence  │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 3. Multi-Dimensional Anomaly Detector & Deadman   │  │
│  │    - Multivariate Z-Score & Heartbeat Lease Guard │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 4. Alert De-noiser & Leaky-Bucket Rate Limiter    │  │
│  │    - Fingerprint Dedup (>95%) & Priority Bypass   │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 5. Cryptographic Event Authenticator (HMAC-SHA256)│  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 6. Dynamic Dispatch Router (Webhook / EventBus)   │  │
│  │    - P0/P1 High-Priority / P2/P3 Standard Ops     │  │
│  │    - Exponential Backoff & Dead Letter Queue(DLQ) │  │
│  └─────────────────────────┬─────────────────────────┘  │
│                            │                            │
│  ┌─────────────────────────▼─────────────────────────┐  │
│  │ 7. Tamper-Evident Merkle Hash Chain Audit Archive │  │
│  └───────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────────────┬─────────┘
             │                                  │
             ▼                                  ▼
      [ SIEM / PagerDuty ]             [ Audit Storage / DLQ ]
```

### 3.1 关键子系统与算法
1. **时间容差与重放防范门 (Temporal Window & Nonce Gate)**：
   - 维持全局高精度单调时钟，拒绝超出 `±5000ms` 容差窗口的重放帧或伪造时间戳数据，校验 Nonce 唯一性。
2. **滑动窗口鲁棒聚合器 (Sliding Window Robust Aggregator)**：
   - 维护 1000ms/3000ms 滑动窗口，计算截断均值（Trimmed Mean）与四分位距（IQR），隔离偏离 3-Sigma 的投毒指标，防止动态基线被恶意污染。
3. **多维异常检测与死信看门狗 (Multivariate Anomaly & Deadman Switch)**：
   - 融合 Token 突发消耗、请求延迟与威胁分类置信度特征向量；同时跟踪 Agent 心跳租约，在租约超期时自动触发节点失联告警。
4. **告警降噪与反洪泛限流器 (Alert De-noiser & Anti-flood Limiter)**：
   - 依据事件摘要指纹在滑动时间窗口内自动聚合去重；漏桶限流平滑普通告警，同时为 P0/P1 熔断告警提供零延迟绕过优先通道。
5. **HMAC-SHA256 签名鉴权器 (Cryptographic Event Authenticator)**：
   - 强制对所有接入分发管道的告警事件进行签名校验，直接丢弃未签名或伪造签名的 P0 震荡攻击事件。
6. **多通道分发路由与死信队列 (Dispatcher & Dead Letter Queue)**：
   - 支持 Webhook、EventBus、SIEM 多路动态分发；对不可达端点执行 3 次指数退避重试，重试耗尽后安全落盘至死信队列 (DLQ)，实现 100% 告警无损。
7. **不可篡改前向哈希链审计归档 (Tamper-Evident Merkle Hash Chaining)**：
   - 所有事件归档均计算 `SHA256(PrevHash || EventPayload || MonotonicTimestamp)`，形成链式不可逆记录，任何历史篡改即刻触发完整性告警。

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
- 所有数据、渠道名与载荷均为 `<SIM_...>` 纯合成占位符。
- 绝不连接真实监控服务端、真实告警 Webhook、生产 EventBus 或真实生产网络。
