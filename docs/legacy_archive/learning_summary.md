# 学习总结

## 我通过这个项目学到了什么

这个项目把抽象的 AI 安全概念拆成了三条可以观察的链路：

1. Chatbot：用户输入如何影响模型输出。
2. RAG：检索内容如何污染回答上下文。
3. Agent：模型或规则系统如何选择工具并产生副作用。

最重要的收获是：AI 安全评估不是“让模型做坏事”，而是建立受控环境，验证系统是否能识别风险、拒绝越界、留下证据，并把结果转化为修复建议。

## MITRE ATLAS 应该怎么学

MITRE ATLAS 不适合只背 technique 名称。更有效的学习方式是：

- 先理解攻击面：prompt、数据、检索、工具、凭证、供应链、资源消耗。
- 再把 technique 映射到可观察行为：是否泄露、是否跟随恶意指令、是否调用工具、是否产生副作用。
- 然后设计本地 fake testcase：输入、预期安全行为、证据字段、断言。
- 最后沉淀控制项：检测、隔离、最小权限、审计、复测。

ATLAS 的价值在于帮助我们系统化地枚举 AI 风险，而不是直接提供攻击操作手册。

## OWASP Agentic 风险和 ATLAS 的关系

ATLAS 更像 technique / tactic 视角，描述攻击者可能如何影响 AI 系统。OWASP Agentic Top 10 更像应用风险和工程治理视角，描述系统为什么会因为设计、权限、上下文或工具边界不足而出问题。

在本项目中，两者的关系可以这样理解：

- ATLAS 告诉我们要测什么行为。
- OWASP 告诉我们这些行为对应什么应用风险。
- 控制项清单告诉我们应该如何防守和治理。
- evidence 告诉我们当前系统是否真的按预期工作。

## 为什么不能让 Agent 自主攻击

Agent 的风险不只是输出错误文本，而是可能调用工具、访问资源、发送信息或执行写操作。一旦让 Agent 自主选择真实目标、真实工具或真实凭证，风险会从“测试输入输出”变成“真实系统副作用”。

因此本项目坚持：

- Claude Code 是编排器，不是自主攻击 Agent。
- 默认只测本地 sandbox。
- 工具必须 allowlist。
- 写操作必须 dry-run。
- 高风险动作必须 human-in-the-loop。
- 非本地目标必须审批。

## 为什么要用 sandbox / fake data / evidence / report

sandbox 让测试边界清晰，fake data 让失败也不会造成真实泄露，evidence 让结论可复核，report 让测试结果能转化为治理动作。

这四件事组合起来，才是安全评估闭环：

```text
测试目标 -> 测试用例 -> 本地执行 -> JSON 证据 -> 风险判断 -> 修复建议 -> 复测
```

没有 evidence，结论不可复核。没有 report，测试无法服务治理。没有 fake data，测试失败可能变成真实事故。

## promptfoo 在这个项目中的角色

promptfoo 在本项目中不是“攻击工具”，而是本地测试执行器和断言框架。它负责：

- 调用本地 `exec:python3 ...` provider。
- 执行 Chatbot / RAG / Agent 测试用例。
- 校验 JSON 输出字段。
- 生成 evidence 文件。
- 统计 pass / fail / error。

本项目没有让 promptfoo 连接真实模型 API，也没有使用它访问企业系统。

## 后续学习 garak / PyRIT / AgentDojo 的顺序建议

建议顺序：

1. 继续增强本地 promptfoo 测试集。
   - 原因：当前闭环已经跑通，先扩展用例覆盖面最稳。
   - Phase 6 已完成：多语言 prompt injection、RAG 文档污染变体、Agent 参数 schema、tool chaining 的本地 dry-run 增强。
   - Phase 6.5 已完成：增强后的 Chatbot 9/0/0、RAG 12/0/0、Agent 10/0/0 execute evidence 更新。
   - 后续重点：工具返回污染、跨轮上下文污染、引用级脱敏、human-in-the-loop 模拟。

2. 学 garak。
   - 适合理解更系统的 LLM vulnerability probing。
   - 仍应先使用本地或 mock provider。

3. 学 PyRIT。
   - 适合学习红队评估编排、评分器和数据集化评估。
   - 需要更严格的授权和日志管理意识。

4. 学 AgentDojo。
   - 适合研究 Agent 工具调用、任务注入和工具链安全。
   - 应在完全本地、fake tools、无真实副作用环境下开始。

## Phase 6 的额外收获

Phase 6 证明了在不接入新工具、不连接真实目标的情况下，也可以显著提升评估质量。关键不是扩大攻击面，而是增强本地测试集的代表性，并用统一质量脚本约束 provider、evidence 路径、敏感关键词和 dry-run 状态。

这也说明进入 execute 前应该先做 testset hardening：先确认用例是否覆盖多语言、格式包装、RAG 文档污染、Agent 参数污染和多步工具链，再决定是否生成新的 evidence。

## Phase 6.5 的额外收获

Phase 6.5 证明了增强后的本地测试集可以形成更完整的执行闭环，并且 execute 阶段能暴露 dry-run 看不到的问题：Chatbot 风险信号分类不完整，以及 Agent evidence / log 回显 honeytoken。它们都没有造成真实外部影响，但说明安全测试不仅要看工具调用是否被阻断，也要检查证据和日志是否会泄露测试 secret。

## Phase 6.6 的额外收获

Phase 6.6 把脱敏从单点修复升级为统一工程控制：provider 输出、sandbox 返回值和 JSONL 日志都应经过同一套 redaction 规则。测试 secret 也要脱敏，因为 evidence 会长期归档并可能复用于企业评估模板。

## Phase 6.7 的额外收获

Phase 6.7 证明了脱敏不能只覆盖 provider 输出和 sandbox 日志，还要覆盖测试框架生成的 result JSON。promptfoo evidence 会包含测试输入、变量和断言元数据，因此执行脚本需要在写出 evidence 后做统一后处理脱敏，同时保留 `leaked_secret`、`leaked_sensitive_data`、`followed_document_instruction`、`false_policy_used`、`dry_run`、`sent` 等布尔字段。

## Phase 7 的额外收获

Phase 7 把零散测试脚本上升为 ATLAS 驱动的评估系统：先定义 technique、profile、test capability 和 coverage matrix，再由总控 runner 生成 assessment plan。这样后续扩展新风险时，不是先写脚本，而是先回答“属于哪个 ATLAS technique、适用哪个 profile、需要什么 evidence、当前覆盖状态是什么”。

## Phase 8 的额外收获

Phase 8 把“能跑”的本地评估系统升级到“能看、能讲、能交付”：dashboard 和企业报告都是从已有 evidence、coverage、控制项汇总出来的本地静态产物，不连接网络、不执行测试、不修改 evidence。这说明可读性和可交付性同样属于安全评估系统的能力，而不是事后包装。统一生成命令和质量检查也保证 dashboard / report 不会偷偷引入外部资源或泄露 fake secret。

## Phase 9 的额外收获

Phase 9 把页面评估拆成了更安全的 Manual UI Replay 流程：先由人工复制输入输出，再用本地 JSON replay 进入分析、脱敏、evidence 和 dashboard/report 流水线。这样可以在不接入真实页面、不启动浏览器自动化、不读取账号凭证的情况下，先验证页面评估的数据结构和治理流程。

## Phase 12 的额外收获

Phase 12 将 Agent 评估从本地 sandbox 升级为通用 Agent ATLAS Assessment Pack，覆盖 Hermes / OpenClaw / Claude Code / LangGraph / AutoGen / MCP / 企业流程 Agent。更重要的是，它建立了 Agent 系统架构画像方法——从 User Intent / Identity 到 Audit / Evidence / Logs 的 12 模块攻击面模型，以及对应的 80 项控制项清单。这套方法论让未来的 Agent 评估可以按统一框架进行，而不是为每个 Agent 类型重复设计测试方案。

Phase 10 把阶段性工程成果整理成 v1 文档包，说明安全评估系统不仅需要测试脚本和 evidence，也需要清晰的入口、操作手册、命令边界、能力矩阵、release notes 和 roadmap。文档化的价值在于让后续使用者知道哪些能力已经可用、哪些结果只代表本地 sandbox、哪些命令会修改 evidence、以及真实系统接入前必须满足哪些授权和脱敏条件。

## Phase 11 的额外收获

Phase 11 说明从本地 sandbox 走向测试环境 API 时，第一步不应是直接发请求，而是先定义 target schema、授权状态、占位符 endpoint、速率限制、数据策略、provider dry-run 输出和质量门禁。把 execute 明确锁死在 skeleton 阶段，可以让系统先验证接入边界和 evidence/report 流水线，而不引入真实网络、真实凭证或企业系统风险。

## Phase 12.5 的额外收获

Phase 12.5 把 Generic Agent 的 10 个 fake manual replay 样例成功接入了现有 Manual UI Replay 评估闭环。这验证了 Generic Agent ATLAS Assessment Pack 的 replay 数据结构和 provider 增强方案是正确的。同时也证明安全评估系统的扩展不是每次都从头设计，而是在已有流水线（replay → provider → evidence → dashboard/report → quality check）中插入新的测试对象。

本阶段还对 `manual_replay_provider.py` 做了关键增强：支持 `user_input`/`agent_response` 字段映射、10 个 Agent 专属风险信号分类、5 个新增布尔字段，以及更全面的中文拒绝词检测。这些增强对后续评估真实 Agent 输出也有复用价值。

## Phase 13 的额外收获

Phase 13 构建了 Generic Agent Mock Tool Harness，这是项目中第一个完全独立于 Chatbot/RAG/Agent 三条现有链路的全新评估通道。它证明了本地 mock harness 可以在不接入真实 LLM、不依赖真实工具链的情况下，对 Agent 安全控制项做系统的黑盒验证。

最重要的设计教训是：promptfoo `exec:` provider 的位置参数传递方式与 argparse 不兼容，必须用手动 JSON 解析。其次是关键字检测虽然简单，但在 mock harness 场景下足够可靠——12 个场景全部通过，风险信号全部命中。脱敏链的设计也延续了 Phase 6.6/6.7 的经验，保证 evidence 不会泄露 fake secret 前缀。

## Phase 14 的额外收获

Phase 14 建立了 OWASP Agentic Top 10 Crosswalk，将 Agent 安全评估从单一的 MITRE ATLAS 映射扩展为双风险分类层。这证明安全评估系统不仅需要"怎么测"（ATLAS 驱动），还需要"怎么报"（OWASP 驱动）。

关键经验：
1. OWASP Agentic Top 10 是风险分类层而非测试框架，与 MITRE ATLAS 自然互补。
2. 报告语言模板（中文）让非技术人员也能理解 Agent 安全风险的业务影响。
3. 控制项映射应该引用已有清单（`generic_agent_control_checklist.md`），而不是完全重建。
4. 映射层可以减少跨层重复：同一个 evidence 可以同时服务于 ATLAS technique 和 OWASP ASI。
5. 不要伪造覆盖：ASI05/07/10 当前不应标记为 covered，clear gaps 比过度承诺更有价值。

## Phase 15 的额外收获

Phase 15 建立了 Evaluation Corpus Architecture，将测试设计（corpus）从测试执行（testcases）和结果证据（evidence）中分离。这证明 AI 安全评估系统需要四个独立层次：语料设计（what to test）、用例执行（how to test）、人工 replay（how to observe）、结果证据（what was observed）。

关键经验：
1. Corpus 的 corpus_id 体系让回归测试可以通过 ID 引用，无需重复复制语料内容。
2. 统一 schema（7 个预期行为布尔字段、6 种执行模式、5 种状态）让不同 profile 的语料共享同一套验证逻辑。
3. 按 profile 组织语料（chatbot / rag / agent / api / business / regression）与评估 profile 自然对齐。
4. 框架映射（MITRE ATLAS + OWASP Agentic + OWASP LLM）让语料可以跨框架检索。
5. 49 条语料覆盖了 6 个 profile，是当前 testcases 的 1.5 倍以上，为后续测试扩展提供了结构化基础。

## Phase 16 的额外收获

Phase 16 建立了 AI Red Teaming 执行方法论层，把红队评估从"直接写测试用例"升级为 12 步标准流程。这证明安全评估不仅需要测试技术和工具，还需要规范的执行方法论——包括 Scope Definition、Rules of Engagement、Threat Modeling、Evidence Collection、Finding Analysis、Severity Rating、Mitigation Recommendation 和 Retest。

最重要的设计教训是：Severity Model 不应该独立于 evidence 之外。7 维度模型（Impact Scope、Data Sensitivity、Agentic Capability、Exploitability、Control Failure、Persistence、Evidence Confidence）的每个维度都对应 evidence 中的可观察字段，这样评出来的 severity 才是可复核、可追溯、可复测的。其次是红队评估的所有模板（playbook、RoE、session、finding、report）应该形成一致的体系，而不是一堆互不关联的文档。

当前所有模板都是方法论/模板层，不代表已对任何真实系统执行了红队评估。

## Phase 16.5 的额外收获

Phase 16.5 是一次全量系统回归验收，证明了当前系统的 5 条评估链路（Chatbot、RAG、Agent、Manual UI Replay、Generic Agent Mock Harness）在执行后仍保持 100% pass 状态。虽然这是个"不新增能力"的阶段，但它验证了所有评估设施在本地 sandbox 环境下的完整可运行性。

## Phase 17 的额外收获

Phase 17 建立了 AI Asset Inventory 和 NIST AI RMF Governance Mapping 两层，将系统从"安全测试工作台"扩展为"安全评估 + 治理工作台"。

关键经验：
1. 资产清单 schema 的 9 分类设计覆盖了从 basic information 到 governance 的全生命周期，与现有 profile 体系自然对齐。资产类型（chatbot/rag/agent/workflow_api/manual_ui_replay）可以直接驱动评估 profile 选择。
2. NIST AI RMF 的四个 function（Govern/Map/Measure/Manage）与系统现有组件的映射关系表明：Map 和 Measure 已获得充分支持（profiles、corpus、runners、evidence），而 Govern 和 Manage 更多依赖模板和人工流程（需要 finding 数据库和自动化审批）。
3. GenAI Profile mapping 揭示了 10 类风险中仍有 3 类（Harmful Content、Privacy、Monitoring）未被覆盖，为后续增强提供了明确方向。
4. 不要混淆"治理映射"和"合规认证"——NIST AI RMF mapping 只是项目内部的对应关系梳理，离正式的 NIST 合规审计还有很大距离。
5. 当前所有资产为 sample/fake 数据，真实资产接入必须先完成授权、数据脱敏和回滚计划。

## Phase 18 的额外收获

Phase 18 建立了 AI/ML-BOM + Supply Chain Mapping 层，将系统从"安全评估 + 治理"扩展为"评估 + 治理 + 供应链追溯"。

关键经验：
1. AI/ML-BOM 的 9 类组件设计（Model、Dataset、Embedding、Tool/Plugin/MCP、Prompt、External API、Runtime、Dependency Relationship）覆盖了 AI 系统的主要依赖维度，与 inventory 的 9 分类字段自然对应。每个 inventory 资产通过 `related_bom` 关联 BOM。
2. 供应链风险映射发现：15 条 ATLAS/OWASP/NIST 映射中，大部分当前状态为 `not_assessed`，说明供应链安全评估在现有系统中是最大缺口之一。这与 GenAI Profile mapping 中 Model/Tool Supply Chain 为 `partially_covered` 的诊断一致。
3. 组件级清单设计（tool_plugin_mcp_inventory、prompt_template_inventory、external_api_dependency_inventory）比单一的 BOM 汇总更实用——它们可以直接映射到 security controls 和 risk register。
4. 模型来源可追溯性检查清单和数据集/知识库来源清单为供应链审计提供了检查框架，但自动化的来源验证和漏洞扫描不在本阶段范围内。
5. 不要混淆"供应链映射"和"供应链安全"——BOM 和映射只是起点，真正的供应链安全需要运行时监控、依赖扫描和供应商审计。
6. 当前所有 BOM 为 sample/fake 数据，真实供应链评估需要连接模型仓库、依赖扫描工具和供应商系统。

关键经验：
1. 系统级回归不仅能验证各条链路是否独立可用，还能暴露跨链路的数据一致性问题——例如初始 quality check 使用旧 dashboard 数据，需要重新生成后才能通过最终检查。
2. 脱敏检查覆盖了 9 个目录（reports/evidence/、dashboard/、reports/、corpus/、owasp/、red_team/、docs/、sandbox/、runners/），确认 .gitignore 正确排除了 .local/。
3. Phase 16.5 的 11 步规范流程（准备 → 执行 → 验证 → 脱敏检查 → 文档化 → 提交）可以作为未来系统验收的标准模板。
4. 版本号从 v1 升级到 v1.1 标志着 Phase 12–16 新增的 OWASP Crosswalk、Evaluation Corpus、Mock Harness、Red Teaming Methodology 四个能力层已经过本地回归验证。

## Phase 19 的额外收获

Phase 19 建立了 External Evaluation Tool Adapter Planning 层，把未来接入 garak、PyRIT、Agent benchmark、Browser Automation 和 API Provider 的路径先规范为 schema、风险边界、adapter index 和 ATLAS/OWASP 映射。

关键经验：
1. 外部工具不应该直接接入主流程，而应先被约束为 adapter：明确输入、输出、执行边界、归一化 evidence 和限制说明。
2. garak、PyRIT、AgentDojo、AgentDyn 等工具的价值不同：有的是 scanner，有的是 red team orchestrator，有的是 benchmark reference，不能混为同一种执行器。
3. Browser Automation 应优先服务 Manual UI Replay，把页面输入输出转成 replay/evidence，而不是直接变成自主浏览器 Agent。
4. API Provider 是未来外部工具的关键边界层，负责 target config、auth handling、限频、redaction 和 evidence output。
5. 不要混淆 adapter planning 和 tool integration：Phase 19 没有安装、没有运行、没有连接任何真实系统，也没有生成 external tool evidence。

## Phase 20 的额外收获

Phase 20 证明外部工具接入不应从安装和运行工具开始，而应先验证 raw output → normalized evidence → dashboard/report 的数据管线。

关键经验：
1. Mock output 可以验证 schema、mapping、redaction、limitations 和 execution boundary 是否完整。
2. `external_tool_executed=false` 与 `real_target_connected=false` 必须成为 evidence 的显式字段，而不是依赖文档说明。
3. Mock normalized evidence 只能验证 pipeline，不能用于正式 finding，也不能证明真实外部工具能力。

## Phase 21 的额外收获

Phase 21 证明系统发布收口不只是一个文档任务。它迫使你回答：哪些能力是真的，哪些是 mock，哪些只是计划。11 个发布文档从不同视角描述同一系统，帮助不同角色找到入口。关键在于区分 executed / mock / planning / methodology / governance 状态，避免过度承诺。
4. 固定 fake 时间可以避免每次生成报告产生无意义 diff。
5. 先做 evidence normalization，有助于未来接入 garak、PyRIT 或浏览器自动化时保持主系统边界稳定。

## Phase 23 的额外收获

Phase 23 新增 Assessment Plan Generator，将评估计划从人工手动编写升级为基于 schema 的自动化生成。这证明评估系统不仅需要测试执行能力，还需要在 execute 之前系统化地规划测试范围、选择语料、分配资源和记录选择理由。

关键经验：
1. 评估计划（Plan）和测试结果（Evidence）是评估流程的两个独立阶段，Plan 在先、Evidence 在后，不应混淆。
2. Corpus 是测试用例资产库，Plan 是从资产库中选择 + 执行推荐，两者也是不同的层次。
3. `allowed_now=false` 机制让计划可以提前设计但不立即执行，适合长期评估规划。
4. 所有当前计划均为 sample/planning_only，不连接真实系统、不执行测试。

## Phase 25 的额外收获

Phase 25 新增 Generated Testcase Curation & Runner Binding 层，验证了 generated testcases 可以通过静态分析自动分类（curated_candidate vs manual_review_required），并建立 runner binding 草案。关键教训：compilation 和 curation 分离，使测试生成管线可审计、可人工介入，而不必一次性交付执行就绪的测试集。

## Phase 26 的额外收获

Phase 26 新增 Curated Regression Suite Builder，从 32 个 curated_candidate 构建 7 个回归测试套件草案。关键教训：regression suite 的质量取决于上游 curation 的质量 — 如果 curated_candidate 覆盖度不足（如 chatbot profile 全部为 manual_review_required），生成的 suite 会存在 zero-selected 情况。

## Phase 26.5 的额外收获

Phase 26.5 对 3 个 zero-selected suite（core_llm、chatbot、api）和 8 个 framework gap（LLM03/04/08、ASI01/03/05/07/10）做了根因分析。关键发现：
- Chatbot 的 zero-selected 是因为全部 22 个 testcases 缺少 assertion_strategy 和 fake_assets_required（可修复）。
- API 的 zero-selected 是因为编译器跳过了 API 类型（需先就绪 corpus 和 runner）。
- 8 个 framework gap 中大多数是 design gap：RISK_TO_OWASP 映射表中没有对应的风险类型。
- 建议下一步走 Phase 27A (corpus/curation backfill) 而不是 Phase 27 (validator)。

## Phase 27A 的额外收获

Phase 27A 完成了 Corpus & Curation Backfill，重点修复了三个根因问题：

1. **fake_assets_required 修复**：为 chatbot 等 profile 的 generated testcases 补齐 assertion_strategy 和 fake_assets_required 字段，使其可通过 curation 进入 curated_candidate。
2. **API corpus backfill**：补齐 API 类型的 corpus 条目和 runner 定义，使 compiler 可以生成 API testcases，不再出现空 suite。
3. **Risk type 多值映射**：修复 RISK_TO_OWASP 映射表，使 risk type 可以映射到多个 OWASP ASI，消除 LLM03/04/08 和 ASI01/03/05/10 的 framework gap。

**修复后效果：**
- Zero-selected suites：3→0（core_llm、chatbot、api 全部补齐）
- LLM gaps：3→0（LLM03/04/08 覆盖）
- Agentic gaps：5→1（ASI07 仍为 gap，其余已覆盖）
- curated_candidate：32→59
- manual_review_required：29→6
- Regression suite selected：65→104

**关键教训：** 这三个问题实际上是递进的。fake_assets_required 缺失导致 chatbot 全部被标注 manual_review_required；API corpus 缺失导致 compiler 跳过了整个 profile；risk type 多值映射缺失导致 OWASP 类别归类不全。一次 backfill 同时修复三个问题，说明 regression suite 的质量门禁设计是有效的——gate 不是 bug，而是精准暴露了上游的哪一层需要补齐。

## Phase 27 的额外收获

Phase 27 新增 Regression Suite Dry-Run Validator，在回归套件构建完成后做静态结构验证。这是一个"验证层"而非"执行层"阶段，核心收获是理解了在安全评估系统中，validation（验证）和 evidence（证据）是不同概念。

关键经验：
1. **Validation != evidence**：验证结果只说明套件结构是否完整、映射是否一致、边界是否合规，不代表任何测试已实际执行。把验证结果当作 evidence 是错误的——evidence 必须是测试执行的可复核结果。
2. **静态验证的价值**：在 7 个套件、104 个 selected testcases、7 个 promptfoo 草稿的规模下，人工检查引用完整性、框架映射和边界合规是不可靠的。自动化的 dry-run validator 可以在秒级完成这些检查，且不会遗漏。
3. **验证阶段的分层**：regression suite 从构建（Phase 26）到缺口分析（Phase 26.5）到 backfill（Phase 27A）到结构验证（Phase 27）到未来执行，每一层解决不同问题：构建负责选择，缺口分析负责发现遗漏，backfill 负责修复，验证负责确认结构正确，执行负责运行时结果。
4. **ASI07 的设计 gap 是合理的**：验证结果中 ASI07 标记为 documented and accepted，说明验证层不会因为存在 gap 而阻塞——它记录 gap、说明理由、接受现状，而不是伪造覆盖或留到执行才发现。
5. **自动化验证的边界**：当前 validator 只做 `static_dry_run_only`，不做运行时验证。这意味着它无法发现配置错误、provider 路径问题、断言有效性等执行时才会暴露的问题。这是设计上接受的——静态验证和运行时验证是互补而非替代关系。

## Phase 28 的额外收获

Phase 28 新增了 Assertion & Risk Signal Rule Engine（`rules/` 目录），在回归套件 dry-run 验证之后建立了"断言判断规则层"。这个阶段的核心收获是理解了在安全评估系统中，规则层（Rules）与证据层（Evidence）之间的区别和联系。

关键经验：

1. **规则不是证据**：规则（Rules）定义了"如何判断"——哪些 JSON 字段组合意味着 prompt injection 被检测到了、哪些意味着 system prompt 泄露了。证据（Evidence）是"判断的结果"——测试执行后生成的 JSON 结果文件。规则在先、证据在后，两者是参考与被参考的关系。

2. **规则层的独立价值**：规则引擎是纯静态的，不依赖 sandbox、provider 或 runner。这意味着可以在没有测试环境、没有真实系统的情况下，先定义完整的断言判断体系。当未来的测试链路增加时，可以直接引用已有的规则，不需要重复设计断言逻辑。

3. **三层断言映射是自然演进**：24 条风险信号规则 + 15 条预期行为规则 + OWASP LLM/Agentic/ATLAS 映射构成了三层断言体系。这是从 Phase 14（OWASP Agentic Crosswalk）开始的框架映射自然演进的结果——既然我们已经有了覆盖率映射，那么断言判断也应该有对应的框架级映射。

4. **static_rule_validation 的价值**：这个 validation_mode 意味着规则层是一个验证层而不是执行层。它能验证规则的结构完整性、映射一致性和引用正确性，但不能验证规则在实际测试中的表现。这是一个设计决策——规则的定义和执行分离，让规则可以独立于任何特定的测试流程进行维护和扩展。

5. **规则层是 evidence 质量的前置保障**：Phase 6.6/6.7 证明了脱敏需要前置工程控制（在生成 evidence 前就嵌入 redaction 逻辑），而不是事后的手工修复。类似地，规则层也应该是证据质量的"前置保障"——在测试执行之前，就定义好证据中每个字段的期望判断逻辑。这样测试执行时产生的 evidence 才能被自动和一致地解释。

6. **从 "测什么" 到 "怎么判" 的延伸**：之前的阶段回答了"测什么"（corpus/curation）、"怎么测"（compiler/suites）、"结构是否正确"（dry-run validator）。Phase 28 回答了"结果怎么判"——给定一个 JSON evidence 文件，如何系统化地从中提取风险信号、判断预期行为是否满足、并映射到框架级别。

7. **规则引擎 vs. promptfoo 断言**：promptfoo 的断言（assert）是配置级的——每条测试用例定义自己的断言。规则引擎是框架级的——它定义跨测试用例的断言判断逻辑，可以被不同 profile、不同 suite 中的测试用例共享。两者互补而非替代：promptfoo 断言回答"这个用例是否通过"，规则引擎回答"这个 evidence 中的风险信号模式是什么"。

## Phase 30 的额外收获

Phase 30 新增了 Formal Report Package Builder（`delivery_packages/` 目录），在 Finding Generator 之后建立了"正式报告交付包构建层"。这个阶段的核心收获是理解了安全评估系统的最终输出不仅可以是分散的 evidence、dashboard 和报告，还可以是标准化的、可交付的企业评估包。

关键经验：

1. **交付包是评估流程的自然收尾**：从 ATLAS technique → profile → corpus → testcases → runner → evidence → finding → delivery package，整条链路的最终输出应该是一份可直接交付给客户或治理方的评估包。Phase 30 把这个最终步骤自动化了。

2. **Sample/mock 交付可以验证交付结构**：在真正执行客户评估之前，先用 sample/mock 数据构建样例交付包，可以验证 13 章节结构是否完整、数据填充逻辑是否正确、报告语言是否一致。这比在真实客户评估中才发现交付结构问题更安全。

3. **边界标志是交付包的核心设计**：`real_customer=false`、`real_target_validated=false`、`formal_report=false`、`usable_for_customer_delivery=false` 四个标志明确了交付包的性质。这让系统的 sample/mock 交付能力和真实客户交付能力之间有一条清晰的界限。

4. **交付包不应替代现有输出**：交付包是评估流程的汇总呈现，不是替代现有 evidence、dashboard 或 report。它是一个"打包"动作，把所有已完成评估产物组装为一份标准化的交付文档。

5. **从评估到交付的最后一公里**：Phase 30 完成了从"评估系统有结果"到"评估结果可交付"的最后一公里。但这只是 sample 级别——真正的客户交付还需要真实目标连接、真实 evidence、真实 finding 和正式报告语言。

## Phase 30.5 的额外收获

Phase 30.5 完成了系统验收和 v1.4 发布收口，将 Phase 23–30 的成果整理为 v1.4 release package。这个阶段的核心收获是理解了系统发布收口不只是一个文档任务——它迫使你回答哪些能力是真的、哪些是 mock、哪些只是计划。v1.4 的 6 个发布文档从不同视角描述同一系统，帮助不同角色找到入口。

关键经验：

1. **系统验收和发布收口是独立的阶段**：不新增能力、不执行测试、不连接真实系统。验收的目的是确认当前系统的边界、状态和限制被准确记录，而不是"让系统更好"。
2. **不同版本的发布文档服务于不同范围的受众**：v1.3 覆盖 Phase 1–20 的全部能力，v1.4 覆盖 Phase 1–30（包括 Phase 23–30 的新增能力）。release package 应该按版本独立维护，而不是不断修改同一个文件。
3. **基线 commit 记录是发布收口的关键产出**：明确记录每个阶段对应的 commit（Phase 29: 32d306a, Phase 30: b9756f2, Phase 30.5: pending），让将来可以精确回溯任何阶段的代码状态。
4. **不破坏已有统计结果**：Phase 30.5 不改变 Phase 16.5 的 5 条链路统计（Chatbot 9/0/0、RAG 12/0/0、Agent 10/0/0、Manual UI Replay 16/0/0、Generic Agent Mock Tool Harness 12/0/0），因为这些是已经执行并验证的正式测试结果。发布收口只做归档和描述，不做重新评估。
5. **consolidation_only 是一个合理的设计模式**：在多个能力阶段之后插入一个 consolidation 阶段，可以把分散的成果整理为可理解的发布包，同时给项目一个自然的"呼吸"节奏。
6. **v1.4 不改变项目整体定位**：系统仍然是 AI Security Assessment & Governance Workbench，用于本地学习、演示、方法论验证、evidence 管理、治理映射和报告生成。真实系统接入仍然需要另行设计授权、账号、数据、日志、脱敏和回滚流程。

## Phase 31 的额外收获

Phase 31 新增了 Generic API Provider Formalization（`api_provider/` 目录），将 API Provider 从 Phase 11 的简单的 skeleton 升级为完整的形式化定义层。这个阶段的核心收获是理解了 API 安全评估的第一步不是连接真实 API，而是先完成形式化的 provider 定义——包括 provider 类型、target 环境、normalization 规则、guardrail 体系和执行边界。

关键经验：

1. **形式化定义先行**：在尝试连接任何真实 API 之前，先定义哪些 provider types 需要支持（chatbot、rag、agent、embedding、completion、multi-modal）、哪些 environment types 存在（local、dev、staging、production、sandbox）、每层需要什么 guardrail。形式化定义让 API 接入不再是临时的"写一个 provider"，而是可重复的工程流程。

2. **Normalization schema 是证据可比性的前提**：6 条 redaction rules（honeytoken、email、token、secret、path、credential）为不同 provider 的输出提供了统一的脱敏框架。没有这个 schema，不同 provider 的 evidence 无法做有意义的一致性比较。

3. **Safety guardrails 的三层设计**：G01-G16 分为 input validation、output redaction 和 execution control 三层。这种分层让 guardrail 可以独立于具体 provider 进行定义和验证——input validation 层关注请求字段完整性，output redaction 层关注响应内容脱敏，execution control 层关注运行时的边界检查。

4. **Dry-run simulator 是最小可行验证方式**：在连接真实 endpoint、读取真实凭证之前，dry-run simulator 可以先验证 config template 的结构、schema 的兼容性和 guardrail 的触发条件。这延续了项目中"先 dry-run 再 execute"的核心安全原则。

5. **Sample target 的边界声明模式**：5 个 sample target 都明确声明 `real_target=false`、`dry_run_only=true`、`execution_allowed=false`、`usable_for_real_test=false`。这个声明模式让系统可以管理"已定义但未执行"的 target，而不需要靠人工记忆或文档说明来判断哪些 target 是安全的。

6. **15 项验证检查的覆盖度**：validation script 包含 15 项检查（schema validation、config integrity、guardrail compliance、dry-run execution），覆盖了从定义到配置到执行的完整验证链路。这比只做"provider 存在"的检查要全面得多。

7. **仍然是静态定义层**：Phase 31 的所有内容仍然是静态定义和 dry-run 配置。未连接真实 API、未读取真实凭证、未访问真实 endpoint、未执行真实安全测试。进入真实测试环境 API execute 之前，仍然需要完成 Phase 11 就提出的授权、测试账号、数据隔离、速率、日志和脱敏策略确认流程。

## Phase 31B 的额外收获

Phase 31B 新增了 Authorized Test Target Onboarding（`api_provider/onboarding/` 目录），在 Phase 31 形式化定义层之上建立了完整的授权目标接入层。这个阶段的核心收获是理解了 API 安全评估的关键一步——在 provider 定义完成后，必须先完成授权接入流程设计，才能安全地连接真实测试目标。

关键经验：

1. **Onboarding 流程先行**：5 步授权流程（目标申请、环境确认、凭证授权、范围确认、安全拆除规划）确保每步都有检查清单和审批节点，不会跳过关键安全环节。

2. **三层环境隔离**：网络隔离、数据隔离和凭证隔离确保即使测试出现异常也不会影响其他系统或泄露敏感数据。

3. **凭证安全生命周期**：6 项控制（加密存储、最小权限、临时凭证、自动轮换、审计日志、紧急吊销）比简单地在环境变量中存储 API key 更完整和安全。

4. **速率限制的 4 级策略**：无限制、宽松、标准、严格——高风险目标默认严格模式，低风险目标可用宽松模式。

5. **18 项验证检查**：比 Phase 31 的 15 项增加 3 项 onboarding 专项检查（authorization completeness、environment isolation validation、credential security audit）。

6. **安全拆除流程**：每个 authorized target 都需定义测试结束后的凭证吊销、数据清理和日志归档流程。

7. **边界声明模式升级**：所有 authorized target 声明 `authorized=true`、`approved_by=human`、`testing_period=timeboxed`、`data_scope=restricted`。当前所有 target 仍声明 real_target=false、usable_for_real_test=false，未连接真实目标、未加载真实凭证、未执行真实安全测试。

## Phase 31C 的额外收获

Phase 31C 新增了 Local Mock API Execution Harness（`api_provider/mock_harness/` 目录），在 Phase 31 形式化定义层和 Phase 31B 授权接入层之后，建立了本地的 mock API 执行框架。这个阶段的核心收获是理解了 API 安全评估的验证闭环可以从"定义"和"授权"延伸到"本地执行模拟"。

关键经验：

1. **Mock 执行是 dry-run 的升级**：Phase 31 的 dry-run simulator 验证了 schema 结构和配置完整性。Phase 31C 的 mock harness 更进一步，使用本地 fixture 模拟完整的请求/响应/归一化流程。这不是真实执行，但比纯 schema 验证更接近真实运行态。

2. **Fixture 驱动的测试设计**：8 条请求 fixture 和 8 条响应 fixture 覆盖了 5 种 provider 类型的正常流程和风险场景（prompt injection 拒绝、indirect injection 检测、密码请求拒绝）。这种 fixture 驱动的方式让 mock 执行可重复、可审计，且不需要真实 API。

3. **归一化管道可以独立验证**：mock normalized response samples 证明，在连接任何真实 API 之前，响应归一化逻辑（token/email/password/URL 脱敏、字段提取、分类标签）可以在 mock 数据上先行验证。这降低了未来接入真实 API 时的数据管道风险。

4. **Mock 执行追踪的可审计性**：execution trace 记录了每个操作的 fixture、描述、安全标志位和风险信号。这让未来在真实执行时可以对比 mock 和 real 的追踪记录差异。

5. **边界声明的自包含性**：所有 mock harness 输出文件都自包含 boundary 声明（external_network_called=false、credentials_loaded=false 等），不需要依赖外部文档来说明执行边界。这延续了 Phase 31/31B 的"声明式安全"设计模式。

6. **Mock harness 不替代真实测试**：mock 执行的目标是验证管道和流程，而不是替代真实安全测试。真实 API 安全测试仍然需要 Phase 31B 的授权流程、凭证隔离和审批门禁。

## Phase 31D 的额外收获

Phase 31D 新增了 Limited Authorized API Dry-Run Plan（`api_provider/authorized_dry_run_plan/` 目录），在 Phase 31C 本地 mock 执行框架之上建立了受控干运行计划层。该层定义了 dry-run plan schema、preflight checklist、test target readiness gate、credential readiness checklist、rate limit/request budget policy、allowed test bundle definition、rollback/stop condition policy 和 approval packet template。所有文件为 placeholder/模板/计划内容，不包含真实 URL/token/email/API key，不连接真实目标，不加载真实凭证，不发起网络请求。

## Phase 31E 的额外收获

Phase 31E 新增了 Single Authorized API Smoke Test Design（`api_provider/single_smoke_test_design/` 目录），在 Phase 31D 干运行计划层之上定义了单次授权 API 冒烟测试设计。该层定义了 smoke test schema、minimal request bundle（4 条低风险只读请求）、expected safe response contract、execution preflight gate（12 项检查）和 abort condition checklist，确保冒烟测试在严格受控的安全范围内执行。所有文件为设计/占位内容，不包含真实 API target、真实凭证或真实系统连接。关键设计约束包括：只允许 1 个目标（only_one_target_allowed=true）、只允许只读操作（read_only_operations_only=true）、不包含 adversarial/jailbreak prompt、数据外泄诱导、系统提示词提取或工具调用攻击。

## Phase 31F 的额外收获

Phase 31F 新增了 Single Smoke Test Approval Packet & Go/No-Go Gate（`api_provider/smoke_test_approval_packet/` 目录），在 Phase 31E 单次授权 API 冒烟测试设计之上建立了最终的审批包与执行门禁层。这个阶段的核心收获是理解了在安全评估流程中，从"设计可执行"到"真正执行"之间需要一道显式的审批门禁——不是所有人都有权批准执行，不是所有条件满足后就应该自动执行。

关键经验：

1. **审批包是授权流程的自然收尾**：Phase 31B 设计了授权接入流程，Phase 31D 设计了干运行计划，Phase 31E 设计了冒烟测试方案。Phase 31F 将这三者的关键产出整合为一个最终的审批包——包含 approval packet schema、go/no-go checklist（10 项）、approval packet template、pre-execution readiness summary、operator signoff placeholder、risk acceptance placeholder 和 execution hold statement。这让从"测试设计"到"测试执行"的转变有一个显式的、文档化的审批节点。

2. **Go/No-Go 门禁的 10 项检查覆盖了执行前的所有关键维度**：包括 target authorization、credential readiness、rate limit policy、dry-run completion、preflight gate pass、smoke test design review、operator readiness、rollback plan、risk acceptance 和 stakeholder approval。每一项检查都对应一个来自之前 Phase 的 artifact——没有 artifact 就不能通过门禁。

3. **所有标志声明确立了清晰的执行状态**：approval_packet_ready=true（包已生成）、approval_status=not_approved（尚未批准）、go_no_go_status=no_go（默认不可执行）、execution_allowed=false（锁定状态）。这个声明体系让系统的执行状态在任何时刻都是可判定的——不需要靠人工记忆或文档说明来判断当前是否可以执行。

4. **三层签收机制保障了执行的严肃性**：human_approval_required=true（需要人工审批）、operator_signoff_required=true（需要操作员确认已准备好）、risk_acceptance_required=true（需要风险接受声明）。三层签收确保执行不是一个单一动作，而是需要多方确认的受控流程。

5. **Execution hold 是最终的安全锁**：execution_hold=true 是整个审批包的最终状态——即使所有检查都通过了、所有签收都完成了，执行仍然被显式锁住。只有人工将 execution_hold 明确改为 false 后，执行才被允许。这比默认允许执行更安全，因为它让"不执行"成为默认状态。

6. **10 个设计文件构成完整的审批包结构**：approval packet schema、go/no-go checklist、approval packet template、pre-execution readiness summary、approval summary、operator signoff placeholder、risk acceptance placeholder、execution hold statement、execution hold release procedure、validation script。每个文件都有明确的职责，组合起来覆盖从审批创建到执行放行的完整流程。

## Phase 32C 的额外收获

Phase 32C 新增了 Full Authorized API Regression Execution，在 Phase 31F 单一冒烟测试审批包与 Go/No-Go 门禁层之上建立了全量授权 API 回归执行层。这个阶段的核心收获是理解了在安全评估流程中，从"审批通过"到"实际执行"之间仍然需要受控的回归执行框架——即使已经通过审批门禁，全量回归执行仍需要严格的安全边界。

关键经验：

1. **执行层需要在设计层之后**：Phase 31B/31D/31E/31F 依次完成了授权接入、干运行计划、冒烟测试设计和审批门禁。Phase 32C 是在这些设计层全部完成后才进入的执行层——这不是跳过设计直接执行，而是设计就绪后的受控执行。

2. **授权 API 回归执行不等同于生产系统测试**：所有执行针对授权测试 API，不是生产系统。测试目标经过 Phase 31B 的授权接入流程确认，且通过 Phase 31F 的 Go/No-Go 门禁后才允许执行。

3. **证据脱敏是执行的前置条件**：执行产生的证据必须在生成时完成脱敏（redaction），不能事后处理。这延续了 Phase 6.6/6.7 的"脱敏前置"设计原则。

4. **所有 finding 均为 candidates**：执行结果直接产生的 finding 是 candidates（needs_human_review=true），不能自动进入正式报告。只有经过人工复核后，finding 状态才能升级为 confirmed 或 rejected。这是确保评估质量的关键质量门禁。

5. **不涉及写操作**：全量回归执行只允许只读操作（read_only_operations_only=true），不执行任何写操作、数据修改或配置变更。任何写操作测试都需要单独的设计和审批流程。

6. **不涉及生产系统访问**：回归执行的目标是授权测试 API，不是生产系统。生产系统测试需要单独的授权、审批和拆除流程。

7. **评估报告构建是只读报告层**：Phase 32D Real API Regression Assessment Report Builder 在 Phase 32C 执行结果之上构建评估报告，不重新执行测试、不连接 API、不读取凭证。所有报告内容为候选性质（needs_human_review=true），报告中已应用脱敏（redaction_applied=true），不是正式客户报告。

## Phase 33 的额外收获

Phase 33 新增了 Remediation & Retest Package Builder（`remediation_packages/` 和 `retest_packages/` 目录），在 Phase 32C 全量授权 API 回归执行和 Phase 32D 评估报告构建之后，建立了修复包与复测包的自动化构建层。这个阶段的核心收获是理解了安全评估流程的最终闭环不仅是"发现问题和报告问题"，而是"制定修复计划、设计复测方案、跟踪执行状态"。

关键经验：

1. **修复包和复测包是评估流程的自然延伸**：从执行（Phase 32C）到报告（Phase 32D）到修复计划（Phase 33），整条链路形成了完整的评估闭环。修复计划不是可选的附加环节，而是确保评估结果能被转化为治理动作的关键步骤。

2. **Finding 分组是修复计划的基础**：5 个 consolidated finding groups（system_prompt_leakage、sensitive_disclosure、rag_exposure、prompt_injection_bypass、api_boundary_weakness）从 Phase 32D 的 finding candidates 中归纳而来。分组不是随机的——每个 group 对应同一类 root cause 的 finding，可以用同一个修复方案解决。

3. **修复任务看板的优先级设计**：10 个任务按 4 P0、3 P1、3 P2 分级。P0 任务是必须立即修复的（如 system prompt 泄露、API 边界绕过），P1 是重要但可稍后处理的（如 RAG 数据暴露），P2 是增强性的（如 prompt injection 检测增强）。这种分级确保修复资源优先投入最高风险的问题。

4. **复测包的三个关键维度**：每个复测包包含执行计划、验收标准和前后对比模板。执行计划回答"怎么测"，验收标准回答"怎样算修好了"，前后对比模板回答"修好了多少"。三者缺一不可。

5. **Build + Validate 的双脚本模式**：`build_remediation_retest_packages.py` 负责生成所有包文件，`validate_remediation_retest_packages.py`（87 项检查）负责验证生成结果的结构完整性、引用一致性和边界合规性。这种"先构建后验证"的模式与 Phase 27（Regression Suite Dry-Run Validator）的设计一致——validation 不是 evidence，但 validation 是质量门禁。

6. **修复/复测状态声明的重要性**：所有 remediation status 为 `remediation_planned`，所有 retest status 为 `retest_not_executed`，`real_api_execution_allowed` 为 `false`。这些状态声明明确区分了"计划了什么"和"完成了什么"，避免混淆修复计划与修复完成。

7. **安全的默认状态**：不重新运行测试、不连接 API、不读取凭证、所有 finding 保持 candidate 状态、需要人工复核。这些默认值确保 Phase 33 的产物在没有人工确认的情况下不会产生误导性的"已修复"或已复测"结论。

## Phase 34A 的额外收获

Phase 34A 新增了 DeepSeek Judge Provider Framework（`tool_judge_providers/` 目录），为 DeepSeek Chat 构建了结构化判官/评分/研判助手框架。这个阶段的核心收获是理解了如何为 AI 安全评估设计可扩展的判官接口层。

1. **判官层是评估流水线的关键质检环节**：不同于测试执行（Phase 32C）和报告构建（Phase 32D），判官层提供了对 finding 质量的第三方评估视角。通过 DeepSeek 作为低成本判官模型，可以在人工复核前对大量 finding candidates 进行自动化预研判。

2. **判官模式设计的关键要素**：判官模式需要定义顶层提供者字段（provider_id、judge_model、judge_mode 等）和判官结果字段（21 个字段，包括 confidence、suggested_status、false_positive_likelihood、rationale_summary 等）。这些字段构成了判官输出的标准化语言。

3. **八种判官用途覆盖评估全链路**：从 finding candidate triage（FC 研判）、system prompt leakage review（提示泄露审查）、sensitive disclosure review（敏感信息披露审查）、RAG boundary review（RAG 边界审查）、prompt injection bypass review（注入绕过审查）、API boundary review（API 边界审查），到 retest result review（复测结果审查）和 tool result review（外部工具结果审查），8 个 use case 覆盖了安全评估的完整判官场景。

4. **Mock-only 的安全默认**：所有判官结果默认 mock_only 模式，network_called=false、credential_loaded=false、usable_for_formal_finding=false。切换到真实 API 模式需要显式 human Go/No-Go。这种安全默认确保判官层在真实调用开启前不会产生误导性的"已验证"结论。

5. **适配器骨架模式**：deepseek_judge_adapter.py 提供了 11 个桩方法，包括 1 个主 judge 分发方法、8 个 use case mock handler、1 个 _call_deepseek_api 占位符和 1 个 format_judge_result 格式化方法。这种骨架模式让未来的真实 API 集成可以在不破坏接口契约的前提下逐步实现。

6. **Build + Validate 的双脚本延续**：build_deepseek_judge_provider.py 和 validate_deepseek_judge_provider.py（9 个章节的验证）延续了 Phase 33 的设计模式。Validation 作为质量门禁，确保所有文件存在、安全标志正确、use case 覆盖完整。`

## Phase 34B 的额外收获

Phase 34B 新增了 DeepSeek Judge Go/No-Go Packet（`tool_judge_providers/deepseek/go_no_go/` 目录），在 DeepSeek Judge Provider Framework（Phase 34A）之上建立了审批门禁层。这个阶段的核心收获是理解了"有能力执行"和"允许执行"之间的安全门禁设计。

1. **Go/No-Go 门禁是安全评估的最后一道人工防线**：在 Phase 34A 构建了 DeepSeek Judge Provider 框架后，Phase 34B 并不急于开启真实 API 调用，而是先设计审批门禁。这延续了项目中"先设计安全边界，再允许执行"的核心原则。

2. **Go/No-Go 包的 8 个文件覆盖审批全流程**：从整体审批包（packet）、检查清单（checklist）、成本预算（cost budget）、执行计划（execution plan）、安全边界（safety boundary）、回滚计划（rollback plan）、结果验收标准（acceptance criteria）到本地配置模板（local config template），8 个文件构成了完整的审批门禁体系。每个文件聚焦一个维度，确保审批不会遗漏关键环节。

3. **所有标志默认为安全状态**：approval_status=not_approved、execution_allowed=false、network_allowed=false、credential_loaded=false、deepseek_api_called=false。从安全默认到允许执行，需要 10 项 Go 条件的全部满足。这种"默认拒绝"模式确保了审批门禁不会被轻易绕过。

4. **审批检查清单的 18 项设计**：分为 6 个 section（A: API & Credential、B: Call Limits、C: Scope、D: Output、E: Cost & Risk、F: Rollback），覆盖了从凭证加载到结果处理的完整链条。每个 section 独立审批，确保不会出现"整体通过但某个环节未确认"的情况。

5. **本地配置模板的凭证安全设计**：配置文件使用 DEEPSEEK_API_KEY_PLACEHOLDER 占位符，明确标注"不要提交"、"不要把 key 写进仓库"、"不要在日志中打印 key"、"不要输出 Authorization header"。7 条安全规则（R1-R7）覆盖了从文件管理到运行时的完整凭证保护。

6. **结果验收标准定义判官输出的边界**：所有判官结果的最高状态为 assistant_review / needs_human_review，不允许自动标记为 validated / confirmed_vulnerability / formal_finding / customer_report_ready。这确保了 AI 判官的输出始终是人工复核的输入，而不是最终结论。

7. **回滚计划的 7 个触发条件和 5 个步骤**：回滚计划覆盖了凭证泄露、预算超限、意外输出、配置错误、审批变更、网络异常和未知风险 7 类触发条件。5 个回滚步骤（Immediate Halt → Credential Protection → Result Invalidation → Configuration Reset → Validation）确保任何异常情况都有标准化的响应流程。

8. **安全边界明确区分 allowed 和 prohibited**：即使在 Go 审批通过后，仍然禁止 formal finding 生成、customer report 生成、new test generation 等 8 类操作。这确保了判官层的输出永远不会被误用为正式安全结论。

## Phase 34C 的额外收获

Phase 34C 新增了 Controlled DeepSeek Judge Execution，在 Phase 34B Go/No-Go 审批门禁通过后，首次使用真实 DeepSeek API（deepseek-v4-flash）执行受控判官研判。这个阶段的核心收获是理解了从"设计可执行"到"安全真实执行"的全过程——审批门禁通过后，执行仍然需要严格的安全边界。

关键经验：

1. **DeepSeek API 连接成功并正常运转**：经过 Phase 34A 的框架设计和 Phase 34B 的审批门禁后，Phase 34C 成功调用真实 DeepSeek API 共 21 次（15 批处理 + 1 冒烟 + 5 合并组），0 次解析错误，总成本约 $0.01。这验证了从 mock 到 real 的过渡流程是完整的。

2. **max_tokens 限制是关键配置参数**：初始 512 token 限制导致 3 个判官响应被截断。将 max_tokens 增加到 1024 后，所有响应完整解析。这个教训说明，mock 阶段无法暴露运行时配置问题——只有真实执行才能发现这类参数调整需求。

3. **批处理判官 vs 合并组判官的分层设计有效**：批处理阶段对 16 个 finding candidates 逐一研判，合并组阶段对 5 个 consolidated groups 聚合研判。两层判官输出形成"逐条分析 + 整体评估"的完整判官结果链，比单层判官更全面。

4. **所有安全边界在运行时得到严格执行**：Phase 34C 执行过程中：
   - 没有调用任何评估目标 API
   - 没有生成新的测试用例
   - 所有判官结果标记 usable_for_formal_finding=false
   - 所有判官结果标记 manual_review_required=true
   - 所有判官结果标记 formal_finding=false
   - 验证脚本全部 10 项检查通过

5. **真实 API 执行的成本可预测**：21 次 DeepSeek API 调用总成本约 $0.01，平均每次调用不到 $0.0005。这种低成本使得判官研判可以作为常规评估环节频繁使用，不需要担心成本爆炸。

6. **从 mock 到 real 的过渡流程得到验证**：Phase 34A（框架设计）→ Phase 34B（审批门禁）→ Phase 34C（受控执行）的三阶段流程被验证是有效的。审批门禁通过后，执行仍然需要安全边界声明和验证脚本的双重保障。

7. **受控执行模式可以复用**：Phase 34C 建立的"审批通过 → 受控执行 → 验证输出"模式，可以作为未来任何真实 API 执行的标准模板。关键要素包括：max 调用次数限制、安全边界声明、验证脚本、输出目录结构。

## Phase 35C.0 的额外收获

Phase 35C.0 新增了 Promptfoo Execution Readiness Gate（`tool_integrations/promptfoo/readiness/` 目录），在 Phase 35B Go/No-Go 审批包之后增加了一层执行前安全闸门。这个阶段的核心收获是理解了"审批包 + 执行前闸门"的双层安全设计。

1. **双层安全设计**：Phase 35B 提供审批框架（谁批准、预算多少、范围多大），Phase 35C.0 提供技术就绪验证（secret 是否已隔离、网络是否已锁定、命令是否安全）。两者缺一不可。

2. **静态检查的有效性**：通过 9 个维度 94 项静态检查覆盖 secret isolation、API isolation、network safety、command safety、adapter safety，全部在本地完成，不依赖外部系统。这种低成本高覆盖的验证模式值得在其他安全闸门中复用。

3. **禁止与允许的明确区分**：Readiness Fail Criteria 明确定义了 6 类导致闸门关闭的条件（明文 secret、未脱敏 endpoint、默认网络、默认 eval、缺少隔离、缺少审批），避免模糊判断。

4. **执行前闸门不替代 Go/No-Go**：Readiness Gate 只回答"是否具备执行前置条件"，Go/No-Go 回答"是否批准执行"。这两个问题的分离确保了安全决策的完整性。

## Phase 35B 的额外收获

Phase 35B 新增了 Promptfoo Go/No-Go Packet（ 目录），为后续受控执行 promptfoo 建立审批门禁。这个阶段的核心收获是理解了审批包设计的标准化流程。

1. **审批包 = 8 个文档 + 1 个模板**：包括审批包、审批 checklist、执行范围、成本预算、preflight checklist、执行边界、回滚计划、验收标准、本地配置模板。每个文档承载一个独立的审批维度。

2. **所有标志默认 not_approved/false**：approval_status=not_approved、execution_allowed=false、network_allowed=false、promptfoo_eval_allowed=false、target_api_call_allowed=false、deepseek_judge_allowed=false、credential_loaded=false、human_go_no_go_required=true、result_can_create_formal_finding=false。这些默认值确保即使文件被误提交，也不会意外授权执行。

3. **成本预算的三层防护**：max_real_execution_cases_initial（初始执行上限）、max_total_requests_hard_limit（硬上限）、hard_stop_on_budget_exceeded（超限自动停止）。这种分层设计既允许小规模受控执行，又防止预算失控。

4. **执行范围明确区分 allowed vs excluded**：7 项 always-allowed 操作（配置验证、dry-run 校验、mock 归一化、schema 验证、evidence/finding/judge 映射）vs 7 项 always-excluded 操作（promptfoo eval、真实 API 调用、DeepSeek API 调用、garak、pyrit、新测试生成、formal finding 生成）。这种二分法消除了执行歧义。

## Phase 35 的额外收获

Phase 35 新增了 Promptfoo Integration Framework（`tool_integrations/promptfoo/` 目录），把已有的 promptfoo drafts / regression suites 纳入统一的工具结果处理链路。这个阶段的核心收获是理解了如何为已有测试资产建立结构化的接入框架。

1. **集成框架不等于执行框架**：Phase 35 只做配置归一化、dry-run 校验、结果 schema、结果归一化和 evidence/finding/judge handoff，不运行 promptfoo eval。这与 Phase 34A（框架设计不执行）的设计原则一致。
2. **适配器模式适用于工具集成**：`tool_integrations/promptfoo/adapter/` 中的 `promptfoo_result_adapter.py` 预留了 `run_promptfoo_eval()` 等真实执行函数桩，但在未获得人工 Go/No-Go 前这些函数 raise NotImplementedError。这延续了项目中"先设计安全边界，再允许执行"的核心原则。
3. **mock results 是集成框架的必要组成部分**：通过 `promptfoo_mock_results.yaml` 提供 2-3 条 mock promptfoo 结果/profile，使得集成框架可以在不连接真实 API 的情况下验证适配器逻辑。
4. **已有 promptfoo assets 规模可观**：Phase 35 配置索引发现 5 个 generated testcase files（52 promptfoo drafts）、7 个 regression suite drafts（104 用例）、7 个 runner 配置、4 个 runner 脚本，覆盖 chatbot/rag/agent/api/core_llm/owasp 等 profile。这些 assets 在集成框架中的处理链路为：promptfoo result → evidence_candidate → finding_candidate → DeepSeek judge handoff。

## 下一步学习建议

优先继续增强本地测试集，而不是马上接真实系统。可以按以下顺序推进：

- 优先设计 Phase 11 测试环境 API Provider 边界，但只在授权、测试账号、数据隔离、速率、日志和脱敏策略明确后推进。
- 抽象 Phase 12 Generic Agent ATLAS Assessment Pack，继续保持 fake tools、dry-run write 和 tool allowlist。
- 增加 RAG 多文档冲突、来源可信度评分和引用级脱敏。
- 增加 Agent 工具返回污染、跨轮上下文污染和 human-in-the-loop fake sandbox。
- 对新增 evidence 继续执行 promptfoo result JSON 后处理脱敏和质量扫描。
- 再评估是否接入 garak / PyRIT / AgentDojo 的本地 mock / dry-run。
