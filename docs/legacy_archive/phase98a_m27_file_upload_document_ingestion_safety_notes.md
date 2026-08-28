# Phase 98A — M27 File Upload / Document Ingestion Safety MVP Notes

## 范围
实现 M27 的最小可执行模拟评估能力，验证文件上传/文档摄入安全在攻击场景下的安全行为。

## 评估模式
adversarial_validation

## 场景覆盖
- malicious_file_upload: 恶意文件上传 — 伪装为PDF的可执行文件
- document_injection: 文档注入 — 隐藏提示注入指令
- file_type_confusion: 文件类型混淆 — 扩展名与实际内容不匹配
- path_traversal: 路径穿越 — 文件名中的路径遍历字符
- metadata_tampering: 元数据篡改 — 伪造作者和创建时间
- permission_bypass: 权限绕过 — 通过上传绕过文档分类权限
- content_poisoning: 内容投毒 — 上传虚假/恶意内容污染知识库
- batch_upload_attack: 批量上传攻击 — 短时间大量上传
- control_normal_file_upload: 正常文件上传（控制用例）
- control_standard_document_retrieval: 标准文档检索（控制用例）

## 安全边界
- 不连接真实文件系统
- 不使用真实上传服务
- 不访问真实存储后端
- 不使用真实文档解析引擎
- 所有数据使用 `<SIM_...>` 合成占位符

## 安全字段
- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety_claimed: false
- controlled_replay_claimed: false
- attack_execution_allowed: false
- payload_generation_allowed: false
- real_target_selection_allowed: false
- red_team_engine_not_executable: true
- dashboard_not_execution_interface: true

## 结果
- capability_value: high
- risk_level: low
- breakthrough_detected: 0

## 与 M48/M49/M03/M19 的关系
- M48: RAG Document Poisoning and Instruction Boundary
- M49: RAG Permission Inheritance and Retrieval Audit
- M03: RAG Boundary Exposure
- M19: Business Data Exposure Validation
- M27: 文件上传/文档摄入安全（本模块）

## 非目标
- 不是漏洞发现工具
- 不声称 production safety
- 不进入 controlled replay
- 所有发现为 candidate 级别
