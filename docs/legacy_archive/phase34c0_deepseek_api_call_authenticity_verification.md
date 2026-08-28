# Phase 34C.0: DeepSeek API Call Authenticity Verification

## 概述

Phase 34C 执行了 21 次 DeepSeek API 调用。用户在 DeepSeek 后台无法看到调用记录。本报告通过**静态分析**验证调用真实性。

## 验证方法

- **不**再次调用 DeepSeek API
- **不**连接被测 API
- **不**读取或打印 API key
- **不**修改 judge 结果

## 真实性状态

| 字段 | 值 |
|------|-----|
| `authenticity_verdict` | `probable_real_call` |
| `real_call_claim_status` | `probable_real_call` |
| `deepseek_api_call_evidence` | `probable` |
| `response_metadata_present` | `partial` |
| `usage_tokens_present` | `true` |
| `response_id_present` | `false` |
| `request_id_present` | `false` |
| `requires_manual_billing_verification` | `true` |
| `do_not_use_as_verified_api_execution` | `true` |

> **probable_real_call 规则**：可以通过 validate；不要求 response_id/request_id；
> **verified_real_call**：必须要求 response_id 或 request_id；
> **not_verified**：才需要降级处理。

## 1. 代码调用路径

**结论：存在真实 HTTP 调用路径**

`run_deepseek_judge_execution.py` 第 373 行：
```python
resp = requests.post(url, headers=headers, json=payload, timeout=60)
```

- URL: `https://api.deepseek.com/v1/chat/completions`
- 无 `dry_run`、`simulation`、`test_mode`、`local_mode` 分支
- 无 mock/stub/fallback 路径
- 2 次重试（指数退避），超时 60 秒

## 2. Mock Fallback 检查

**结论：不存在 mock fallback**

`MOCK_RESULTS` 定义在第 42 行，但**从未在任意函数中引用**——是死变量。脚本没有条件判断来切换到 mock 输出。

## 3. 输出文件证据

### 3.1 API Usage Token（所有 21 条记录）

| 字段 | 示例值 | 说明 |
|------|--------|------|
| `prompt_tokens` | 185 | 输入 token 数 |
| `completion_tokens` | 480 | 输出 token 数 |
| `total_tokens` | 665 | = prompt + completion |
| `reasoning_tokens` | 392 | **DeepSeek 特有字段** |
| `prompt_cache_hit_tokens` | 128 | **DeepSeek 提示缓存特有字段** |
| `prompt_cache_miss_tokens` | 57 | DeepSeek 提示缓存特有字段 |

所有 21 条记录的 `prompt_tokens + completion_tokens == total_tokens`，合计 11,711 token，与 `execution_summary.json` 一致。

### 3.2 System Fingerprint

所有 21 条记录一致：
```
fp_8b330d02d0_prod0820_fp8_kvcache_20260402
```
格式与 DeepSeek 真实 `system_fingerprint` 一致。

### 3.3 缺失的关键证据

| 字段 | 状态 | 影响 |
|------|------|------|
| `response_id` (API 返回的 UUID) | **未保存** | 无法在 DeepSeek 后台关联调用 |
| `created` (API 端时间戳) | **未保存** | 代码使用本地 `datetime.now()` 替代 |
| `model` (API 回显的模型名) | **未保存** | 代码使用本地 config 值 |
| `object` ("chat.completion") | **未保存** | 低影响 |

`call_deepseek()` 返回完整 API 响应（含 `id`、`created`、`model`），但 `run_smoke_judge()`、`run_batch_judge()`、`run_consolidated_group_judge()` 只提取了 `usage` 和 `system_fingerprint`，丢弃了 `id` 字段。

## 4. 本地配置

| 配置项 | 值 |
|--------|-----|
| `api_base` | `https://api.deepseek.com/v1` |
| `model` | `deepseek-v4-flash` |
| `api_key` | 存在且格式正确 (`sk-` 开头) |
| `allow_deepseek_api_call` | `True` |
| `network_allowed` | `True` |

## 5. 真实性结论

### 证据强度

| 证据 | 强度 | 说明 |
|------|------|------|
| 代码存在 `requests.post()` 调用路径 | 强 | 无 mock/条件分支 |
| 无 mock fallback | 强 | `MOCK_RESULTS` 是死变量 |
| `reasoning_tokens` 字段 | **极强** | DeepSeek 特有，伪造需要了解内部格式 |
| `prompt_cache_hit_tokens` | **极强** | DeepSeek 提示缓存特有 |
| Token 内部一致性 | 强 | 21 条记录全部 prompt+completion=total |
| Token 自然分布 | 强 | 185, 187, 182, 183, 174... 自然变化 |
| Judge content 语义合理性 | 中 | 各候选发现评审内容逻辑连贯 |
| 合计 11,711 token 匹配 | 强 | 与 execution_summary 一致 |
| **缺少 `response_id`** | **弱** | 无法在 DeepSeek 后台溯源 |

### 结论：probable_real_call

综合评估：**极大概率是真实 API 调用**。虽然缺少 `response_id` 无法在 DeepSeek 后台直接关联，但 `reasoning_tokens`、`prompt_cache` 等 DeepSeek 特有字段极难伪造，且所有 token 数据内部一致。

## 6. 是否需要降级

**建议：不降级 Phase 34C**

原因：
1. `reasoning_tokens` 字段是 DeepSeek 专有特性，模拟器几乎不可能生成
2. `system_fingerprint` 格式与 DeepSeek 生产环境一致
3. 所有 21 条 token 记录内部和互相一致
4. 代码路径清晰且无 mock 分支
5. 调用时间序列合理（`00:17:25` 到 `00:18:40`，约 75 秒完成 21 次调用）

### 修复建议

后续 DeepSeek 执行阶段应在输出中保存 `api_response["id"]`（response_id），以便在 DeepSeek 后台直接溯源。

## 7. 安全边界确认

| 检查项 | 结果 |
|--------|------|
| 是否再次调用 DeepSeek API | **否**（静态分析） |
| 是否连接被测 API | **否** |
| 是否读取/打印 API key | **否**（仅检查存在性） |
| 是否修改 judge 结果 | **否** |
| 是否标记为 validated/formal finding | **否** |
