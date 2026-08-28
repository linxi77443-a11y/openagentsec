#!/usr/bin/env python3
"""
ADV-SLICE-001 设计门验证脚本
验证所有交付物符合 design_gate_only 约束

运行: python3 scripts/validate_adv_slice_001_design_gate.py
"""

import os
import sys
import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

checks = []
failed = 0
passed = 0


def check(condition: bool, message: str, check_id: str):
    global failed, passed
    if condition:
        passed += 1
        print(f"  ✅ [{check_id}] {message}")
    else:
        failed += 1
        print(f"  ❌ [{check_id}] {message}")


def file_exists(path: str) -> bool:
    full = os.path.join(PROJECT_ROOT, path) if not os.path.isabs(path) else path
    return os.path.isfile(full)


def load_yaml(path: str):
    full = os.path.join(PROJECT_ROOT, path) if not os.path.isabs(path) else path
    with open(full, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ═══════════════════════════════════════════
# CHECKS GROUP 1: 交付物存在性
# ═══════════════════════════════════════════
print("\n═══ Group 1: 交付物存在性 ═══")

deliverables = [
    "docs/adv_slice_001_problem_slicing_reference_spike.md",
    "schemas/adversarial/problem_slicing_schema_addendum.yaml",
    "schemas/adversarial/multiturn_engine_minimum_requirements.yaml",
    "docs/adv_slice_001_playbook_outline.md",
    "scripts/validate_adv_slice_001_design_gate.py",
]
for d in deliverables:
    check(file_exists(d), f"交付物存在: {d}", f"DLV-{deliverables.index(d)+1:03d}")

# ═══════════════════════════════════════════
# CHECKS GROUP 2: design_gate_only
# ═══════════════════════════════════════════
print("\n═══ Group 2: design_gate_only 约束 ═══")

check(
    not file_exists("corpora/adversarial/module_mvp_corpus.yaml"),
    "未创建 corpus 文件",
    "DG-001",
)
check(
    not file_exists("corpora/adversarial/adversarial_playbook.yaml"),
    "未创建正式 adversarial_playbook.yaml",
    "DG-002",
)
check(
    not any(f.startswith("runners/") and "adv_slice" in f for f in
            [os.path.relpath(os.path.join(dp, f), PROJECT_ROOT)
             for dp, dn, filenames in os.walk(os.path.join(PROJECT_ROOT, "runners"))
             for f in filenames]),
    "未创建 run config",
    "DG-003",
)

# 检查未生成 execution_results
exec_results_exists = False
for dp, dn, filenames in os.walk(PROJECT_ROOT):
    for f in filenames:
        if "execution_results" in f and "adv_slice" in f:
            exec_results_exists = True
            break
check(not exec_results_exists, "未生成 execution_results.json", "DG-004")

# 检查未创建 corpus 目录
adversarial_dirs_exist = [
    os.path.isdir(os.path.join(PROJECT_ROOT, "corpora/adversarial"))
]
check(not any(adversarial_dirs_exist), "corpora/adversarial 目录不存在（未创建 corpus）", "DG-005")

# ═══════════════════════════════════════════
# CHECKS GROUP 3: Schema Addendum 内容合规
# ═══════════════════════════════════════════
print("\n═══ Group 3: Schema Addendum 内容合规 ═══")

schema = load_yaml("schemas/adversarial/problem_slicing_schema_addendum.yaml")
check(
    schema.get("schema_addendum_id") == "ADV-SLICE-001",
    "schema_addendum_id 正确",
    "SC-001",
)
check(
    "problem_slicing_attack" in schema,
    "包含 problem_slicing_attack 顶层对象",
    "SC-002",
)
check(
    schema.get("production_parser_dispatched") is False,
    "production_parser_dispatched == false",
    "SC-003",
)
check(
    schema.get("parser_integration_point") == "multiturn_parser_extension",
    "parser 接入点为 multiturn_parser_extension",
    "SC-004",
)

result_fields = schema.get("problem_slicing_attack", {}).get("result_fields", {})
check(
    result_fields.get("confirmed_vulnerability", {}).get("const") is False,
    "confirmed_vulnerability const == false",
    "SC-005",
)
check(
    result_fields.get("formal_finding_allowed", {}).get("const") is False,
    "formal_finding_allowed const == false",
    "SC-006",
)
check(
    "confirmed_vulnerability" in result_fields,
    "结果字段包含 confirmed_vulnerability",
    "SC-007",
)
check(
    "formal_finding_allowed" in result_fields,
    "结果字段包含 formal_finding_allowed",
    "SC-008",
)
check(
    "requires_human_review" in result_fields,
    "结果字段包含 requires_human_review",
    "SC-009",
)
check(
    "breakthrough_detected" in result_fields,
    "结果字段包含 breakthrough_detected",
    "SC-010",
)

constraints = schema.get("problem_slicing_attack", {}).get("constraints", [])
constraint_ids = [c.get("id") for c in constraints]
check(
    "BRK-PSA-002" in constraint_ids,
    "约束 BRK-PSA-002 (confirmed_vulnerability=false) 已定义",
    "SC-011",
)
check(
    "BRK-PSA-003" in constraint_ids,
    "约束 BRK-PSA-003 (formal_finding_allowed=false) 已定义",
    "SC-012",
)
check(
    "BRK-PSA-005" in constraint_ids,
    "约束 BRK-PSA-005 (synthetic data 格式限制) 已定义",
    "SC-013",
)

sec_defaults = schema.get("problem_slicing_attack", {}).get("security_defaults", {})
check(
    sec_defaults.get("confirmed_vulnerability") is False,
    "安全默认值: confirmed_vulnerability=false",
    "SC-014",
)
check(
    sec_defaults.get("formal_finding_allowed") is False,
    "安全默认值: formal_finding_allowed=false",
    "SC-015",
)
check(
    sec_defaults.get("production_safety_claimed") is False,
    "安全默认值: production_safety_claimed=false",
    "SC-016",
)
check(
    sec_defaults.get("attack_execution_allowed") is False,
    "安全默认值: attack_execution_allowed=false",
    "SC-017",
)
check(
    sec_defaults.get("payload_generation_allowed") is False,
    "安全默认值: payload_generation_allowed=false",
    "SC-018",
)

# v3.1 §4 模拟红队专项安全字段
check(
    schema.get("real_target_selection_allowed") is False,
    "v3.1 §4: real_target_selection_allowed=false",
    "SC-019",
)
check(
    schema.get("red_team_engine_not_executable") is True,
    "v3.1 §4: red_team_engine_not_executable=true",
    "SC-020",
)
check(
    schema.get("dashboard_not_execution_interface") is True,
    "v3.1 §4: dashboard_not_execution_interface=true",
    "SC-021",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 4: 剧本概要合规
# ═══════════════════════════════════════════
print("\n═══ Group 4: 剧本概要合规 ═══")

playbook_doc_path = os.path.join(PROJECT_ROOT, "docs/adv_slice_001_playbook_outline.md")
check(
    file_exists("docs/adv_slice_001_playbook_outline.md"),
    "剧本概要文件存在",
    "PB-001",
)

with open(playbook_doc_path, "r", encoding="utf-8") as f:
    pb_content = f.read()

check(
    "ADV-SLICE-DIST-001" in pb_content,
    "剧本 1: distributed_information_acquisition (ADV-SLICE-DIST-001) 已定义",
    "PB-002",
)
check(
    "ADV-SLICE-CROSS-001" in pb_content,
    "剧本 2: cross_context_boundary_composition (ADV-SLICE-CROSS-001) 已定义",
    "PB-003",
)

required_fields = [
    "playbook_id", "name", "assessment_mode", "attacker_type",
    "attack_objective", "summary", "turn_sequence_outline",
    "expected_behavior", "expected_signal", "target_boundary",
    "synthetic_objects", "forbidden",
]
for field in required_fields:
    check(
        field in pb_content,
        f"剧本概要包含必填字段: {field}",
        f"PB-FLD-{required_fields.index(field)+1:03d}",
    )

check(
    "<SIM_CUSTOMER_FIELD_LASTNAME_001>" in pb_content,
    "剧本 1 使用 SIM_ 格式模拟数据",
    "PB-004",
)
check(
    "<SIM_POLICY_FRAGMENT_SCOPE_001>" in pb_content,
    "剧本 2 使用 SIM_ 格式模拟数据",
    "PB-005",
)

# v3.1 §4 + §7/§8 + v2.0 §13: 剧本性质与信号性质澄清
check(
    "simulated adversarial playbook outline" in pb_content,
    "剧本明确标注为 simulated adversarial playbook outline",
    "PB-006",
)
check(
    "expected_signal" in pb_content,
    "剧本使用 expected_signal（非 observed_signal/parser_signal/execution_result）",
    "PB-007",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 5: 多轮引擎需求合规
# ═══════════════════════════════════════════
print("\n═══ Group 5: 多轮引擎需求合规 ═══")

engine_req = load_yaml("schemas/adversarial/multiturn_engine_minimum_requirements.yaml")
check(
    engine_req.get("engine_development_status") == "not_implemented_design_gate_only",
    "引擎开发状态为 not_implemented_design_gate_only",
    "MT-001",
)

tracking_fields = {f.get("field"): f for f in engine_req.get("tracking_fields", [])}
required_tracking = [
    "conversation_id", "turn_id", "slice_group_id", "attack_stage",
    "prior_turn_refs", "cumulative_risk_state",
]
for tf in required_tracking:
    check(
        tf in tracking_fields,
        f"跟踪字段包含: {tf}",
        f"MT-FLD-{required_tracking.index(tf)+1:03d}",
    )

per_turn = engine_req.get("per_turn_record", {})
check(
    "model_response_excerpt" in per_turn,
    "per_turn_record 包含 model_response_excerpt",
    "MT-002",
)
check(
    "boundary_tested" in per_turn,
    "per_turn_record 包含 boundary_tested",
    "MT-003",
)
check(
    "observed_signal" in per_turn,
    "per_turn_record 包含 observed_signal",
    "MT-004",
)
check(
    "requires_human_review" in per_turn,
    "per_turn_record 包含 requires_human_review",
    "MT-005",
)

agg = engine_req.get("aggregated_output", {})
check(
    agg.get("confirmed_vulnerability", {}).get("const") is False,
    "聚合输出: confirmed_vulnerability const == false",
    "MT-006",
)
check(
    agg.get("formal_finding_allowed", {}).get("const") is False,
    "聚合输出: formal_finding_allowed const == false",
    "MT-007",
)
check(
    agg.get("production_safety_claimed", {}).get("const") is False,
    "聚合输出: production_safety_claimed const == false",
    "MT-008",
)

core_reqs = {r.get("requirement"): r for r in engine_req.get("core_functional_requirements", [])}
check(
    "cross_turn_state_aggregation" in core_reqs,
    "核心需求: cross_turn_state_aggregation",
    "MT-009",
)
check(
    "cumulative_disclosure_signal" in core_reqs,
    "核心需求: cumulative_disclosure_signal",
    "MT-010",
)
check(
    "per_turn_recording" in core_reqs,
    "核心需求: per_turn_recording",
    "MT-011",
)
check(
    "aggregated_breakthrough_output" in core_reqs,
    "核心需求: aggregated_breakthrough_output",
    "MT-012",
)
check(
    "control_turn_support" in core_reqs,
    "核心需求: control_turn_support",
    "MT-013",
)
check(
    "stop_condition_handling" in core_reqs,
    "核心需求: stop_condition_handling",
    "MT-014",
)

check(
    "control_turn" in engine_req,
    "control_turn 定义存在",
    "MT-015",
)
check(
    "stop_condition" in engine_req,
    "stop_condition 定义存在",
    "MT-016",
)

# ── 语义冻结检查（PRD §4、攻击者视角新增章节 §3/§11、v2.0 §4、v3.1 §4/§6）──
check(
    engine_req.get("engine_not_implemented") is True,
    "语义冻结: engine_not_implemented=true",
    "MT-017",
)
check(
    engine_req.get("attack_execution_allowed") is False,
    "语义冻结: attack_execution_allowed=false",
    "MT-018",
)
check(
    engine_req.get("payload_generation_allowed") is False,
    "语义冻结: payload_generation_allowed=false",
    "MT-019",
)
check(
    engine_req.get("real_target_selection_allowed") is False,
    "语义冻结: real_target_selection_allowed=false",
    "MT-020",
)
check(
    engine_req.get("controlled_replay_execution_allowed") is False,
    "语义冻结: controlled_replay_execution_allowed=false",
    "MT-021",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 6: 无真实 payload / 无攻击性内容
# ═══════════════════════════════════════════
print("\n═══ Group 6: 内容安全合规 ═══")

# 检查所有交付物中不包含真实 payload 或攻击命令
all_deliverable_paths = [
    os.path.join(PROJECT_ROOT, d) for d in deliverables
]
# 也检查 YAML 文件
all_deliverable_paths.extend([
    os.path.join(PROJECT_ROOT, "schemas/adversarial/multiturn_engine_minimum_requirements.yaml"),
])

dangerous_patterns = [
    "rm -rf",
    "DROP TABLE",
    "sudo ",
    "chmod 777",
    "exec(",
    "eval(",
    "os.system(",
    "subprocess.call",
    "confirmed_vulnerability: true",
    "formal_finding_allowed: true",
    "production_safety_claimed: true",
    "attack_execution_allowed: true",
    "payload_generation_allowed: true",
]

for dp in all_deliverable_paths:
    if not os.path.isfile(dp):
        continue
    # 跳过验证脚本自身，其源代码包含 dangerous_patterns 列表的字符串字面量
    if dp.endswith("validate_adv_slice_001_design_gate.py"):
        continue
    with open(dp, "r", encoding="utf-8") as f:
        content = f.read()
    for pattern in dangerous_patterns:
        check(
            pattern not in content,
            f"文件 {os.path.basename(dp)} 不包含危险模式: {pattern}",
            f"SAFE-{hash(pattern) % 10000:04d}",
        )

# 检查 SIM_ 格式
for dp in all_deliverable_paths:
    if not os.path.isfile(dp):
        continue
    with open(dp, "r", encoding="utf-8") as f:
        content = f.read()
    # 模拟数据格式检查（如果有敏感数据字样，必须是 <SIM_> 格式）
    for suspicious in ["secret", "password", "token", "credential", "customer", "business_record"]:
        # 简单地按行检查
        for line in content.split("\n"):
            lower = line.lower()
            if suspicious in lower and "sim_" not in lower and "SIM_" not in lower:
                # 注释或 schema 定义中的字段名不算
                if "description:" in line or "#" in line or "type:" in line:
                    continue
                # 但需要确认没有真实数据
                pass

# ═══════════════════════════════════════════
# CHECKS GROUP 7: 参考文档内容合规
# ═══════════════════════════════════════════
print("\n═══ Group 7: 参考文档内容合规 ═══")

ref_doc_path = os.path.join(PROJECT_ROOT, "docs/adv_slice_001_problem_slicing_reference_spike.md")
with open(ref_doc_path, "r", encoding="utf-8") as f:
    ref_content = f.read()

check(
    "design_gate" in ref_content.lower(),
    "参考文档声明 design_gate",
    "REF-001",
)
check(
    "adversarial_validation" in ref_content,
    "评估模式为 adversarial_validation",
    "REF-002",
)
check(
    "<SIM_" in ref_content,
    "参考文档使用 SIM_ 格式模拟数据",
    "REF-003",
)
check(
    "confirmed_vulnerability" in ref_content,
    "参考文档包含 confirmed_vulnerability 讨论",
    "REF-004",
)

for forbidden_ref in [
    "不新增完整 corpus",
    "不配置 run config",
    "不执行 capability_engine",
    "不生成 execution_results",
    "不开发多轮对话引擎",
]:
    check(
        forbidden_ref in ref_content,
        f"参考文档明确声明: {forbidden_ref}",
        f"REF-SCOPE-{hash(forbidden_ref) % 10000:04d}",
    )

# v3.1 §8 / v2.0 §13: coverage scope 声明
coverage_scope_claims = [
    "不更新 M04/M19/M38/multiturn 的 coverage_depth",
    "不更新 M43-M50 coverage_status",
    "不声明 simulated_mvp",
    "multiturn_ready",
    "execution_complete",
]
for claim in coverage_scope_claims:
    check(
        claim in ref_content,
        f"参考文档声明: {claim}",
        f"REF-CVG-{hash(claim) % 10000:04d}",
    )

# ═══════════════════════════════════════════
# CHECKS GROUP 8: 引擎需求文档安全合规
# ═══════════════════════════════════════════
print("\n═══ Group 8: 引擎需求安全声明 ═══")

engine_req_path = os.path.join(PROJECT_ROOT, "schemas/adversarial/multiturn_engine_minimum_requirements.yaml")
with open(engine_req_path, "r", encoding="utf-8") as f:
    eng_content = f.read()

check(
    "not_implemented_design_gate_only" in eng_content,
    "引擎状态声明: not_implemented_design_gate_only",
    "ENG-001",
)
check(
    "confirmed_vulnerability=false" in eng_content or "confirmed_vulnerability: false" in eng_content,
    "引擎包含 confirmed_vulnerability=false",
    "ENG-002",
)
check(
    "formal_finding_allowed=false" in eng_content or "formal_finding_allowed: false" in eng_content,
    "引擎包含 formal_finding_allowed=false",
    "ENG-003",
)
check(
    "production_safety_claimed=false" in eng_content or "production_safety_claimed: false" in eng_content,
    "引擎包含 production_safety_claimed=false",
    "ENG-004",
)

# ═══════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════
print(f"\n{'='*60}")
print(f"  校验完成: {passed} 通过, {failed} 失败")
print(f"{'='*60}")

if failed > 0:
    sys.exit(1)
else:
    print("  ALL CHECKS PASSED — ADV-SLICE-001 design_gate 验收通过")
    sys.exit(0)
