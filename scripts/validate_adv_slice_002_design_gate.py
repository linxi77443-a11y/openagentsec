#!/usr/bin/env python3
"""
ADV-SLICE-002 设计门验证脚本
验证语法库草案符合 design_gate_only 约束

运行: python3 scripts/validate_adv_slice_002_design_gate.py
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
    "capability_modules/adversarial/problem_slicing/adv_slice_002_problem_slicing_corpus_draft.yaml",
    "docs/adv_slice_002_corpus_draft_notes.md",
    "scripts/validate_adv_slice_002_design_gate.py",
]
for d in deliverables:
    check(file_exists(d), f"交付物存在: {d}", f"DLV-{deliverables.index(d)+1:03d}")

# ═══════════════════════════════════════════
# CHECKS GROUP 2: corpus_draft_gate_only 约束
# ═══════════════════════════════════════════
print("\n═══ Group 2: corpus_draft_gate_only 约束 ═══")

corpus = load_yaml(
    "capability_modules/adversarial/problem_slicing/adv_slice_002_problem_slicing_corpus_draft.yaml"
)
meta = corpus.get("corpus_draft_metadata", {})

check(
    meta.get("corpus_draft_gate_only") is True,
    "corpus_draft_metadata: corpus_draft_gate_only=true",
    "DG-001",
)
check(
    meta.get("run_config_created") is False,
    "corpus_draft_metadata: run_config_created=false",
    "DG-002",
)
check(
    meta.get("capability_engine_executed") is False,
    "corpus_draft_metadata: capability_engine_executed=false",
    "DG-003",
)
check(
    meta.get("execution_results_generated") is False,
    "corpus_draft_metadata: execution_results_generated=false",
    "DG-004",
)

# v3.1 §4 模拟红队专项安全字段
check(
    meta.get("real_target_selection_allowed") is False,
    "v3.1 §4: real_target_selection_allowed=false",
    "DG-005",
)
check(
    meta.get("red_team_engine_not_executable") is True,
    "v3.1 §4: red_team_engine_not_executable=true",
    "DG-006",
)
check(
    meta.get("dashboard_not_execution_interface") is True,
    "v3.1 §4: dashboard_not_execution_interface=true",
    "DG-007",
)
check(
    meta.get("not_attack_platform") is True,
    "v3.1 §4: not_attack_platform=true",
    "DG-008",
)
check(
    meta.get("not_vulnerability_discovery_tool") is True,
    "v3.1 §4: not_vulnerability_discovery_tool=true",
    "DG-009",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 3: Schema 引用
# ═══════════════════════════════════════════
print("\n═══ Group 3: Schema 引用 ═══")

refs = meta.get("schema_references", [])
ref_paths = [r.get("path") for r in refs]
check(
    "schemas/adversarial/problem_slicing_schema_addendum.yaml" in ref_paths,
    "引用 ADV-SLICE-001 problem_slicing_schema_addendum.yaml",
    "SCH-001",
)
check(
    "schemas/adversarial/multiturn_engine_minimum_requirements.yaml" in ref_paths,
    "引用 ADV-SLICE-001 multiturn_engine_minimum_requirements.yaml",
    "SCH-002",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 4: 仅绑定两个 playbook
# ═══════════════════════════════════════════
print("\n═══ Group 4: 仅绑定两个 playbook ═══")

bound = meta.get("bound_playbooks", [])
bound_ids = [b.get("playbook_id") for b in bound]
check(
    "ADV-SLICE-DIST-001" in bound_ids,
    "绑定 playbook: ADV-SLICE-DIST-001",
    "PB-001",
)
check(
    "ADV-SLICE-CROSS-001" in bound_ids,
    "绑定 playbook: ADV-SLICE-CROSS-001",
    "PB-002",
)
check(
    len(bound_ids) == 2,
    f"仅绑定 2 个 playbook (实际 {len(bound_ids)})",
    "PB-003",
)
check(
    "playbook_metadata_dist" in corpus,
    "playbook_metadata_dist 定义存在",
    "PB-004",
)
check(
    "playbook_metadata_cross" in corpus,
    "playbook_metadata_cross 定义存在",
    "PB-005",
)
check(
    "dist_001_entries" in corpus,
    "dist_001_entries 条目组存在",
    "PB-006",
)
check(
    "cross_001_entries" in corpus,
    "cross_001_entries 条目组存在",
    "PB-007",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 5: 条目结构完整性
# ═══════════════════════════════════════════
print("\n═══ Group 5: 条目结构完整性 ═══")

required_entry_fields = [
    "case_id", "playbook_id", "category", "scenario",
    "synthetic_objects", "turn_sequence_outline",
    "expected_behavior", "expected_signal",
]

all_entries = corpus.get("dist_001_entries", []) + corpus.get("cross_001_entries", [])
check(
    len(all_entries) == 8,
    f"条目总数: 8 (实际 {len(all_entries)})",
    "ENT-001",
)

for entry in all_entries:
    for field in required_entry_fields:
        check(
            field in entry,
            f"条目 {entry.get('case_id', '?')} 包含必填字段: {field}",
            f"ENT-{entry.get('case_id', '?')}-{field}",
        )

# 检查 SYNTHETIC 类型
for entry in all_entries:
    for sobj in entry.get("synthetic_objects", []):
        stype = sobj.get("synthetic_type", "")
        valid_types = [
            "SIM_SECRET_FRAGMENT",
            "SIM_CUSTOMER_FIELD",
            "SIM_BUSINESS_RECORD_PART",
            "SIM_POLICY_FRAGMENT",
            "SIM_RAG_SNIPPET",
            "SIM_BUSINESS_CONTEXT",
        ]
        check(
            stype in valid_types,
            f"条目 {entry.get('case_id', '?')} synthetic_type 有效: {stype}",
            f"SYN-{entry.get('case_id', '?')}-{stype}",
        )

# ═══════════════════════════════════════════
# CHECKS GROUP 6: expected_signal ONLY (无 observed_signal)
# ═══════════════════════════════════════════
print("\n═══ Group 6: expected_signal ONLY ═══")

for entry in all_entries:
    check(
        "observed_signal" not in entry,
        f"条目 {entry.get('case_id', '?')} 不包含 observed_signal",
        f"OBS-{entry.get('case_id', '?')}",
    )
    check(
        "observed_model_behavior" not in entry,
        f"条目 {entry.get('case_id', '?')} 不包含 observed_model_behavior",
        f"OBS-{entry.get('case_id', '?')}-b",
    )
    check(
        "parser_signal" not in entry,
        f"条目 {entry.get('case_id', '?')} 不包含 parser_signal",
        f"OBS-{entry.get('case_id', '?')}-c",
    )
    check(
        "execution_result" not in entry,
        f"条目 {entry.get('case_id', '?')} 不包含 execution_result",
        f"OBS-{entry.get('case_id', '?')}-d",
    )
    check(
        "breakthrough_observed" not in entry,
        f"条目 {entry.get('case_id', '?')} 不包含 breakthrough_observed",
        f"OBS-{entry.get('case_id', '?')}-e",
    )

# ═══════════════════════════════════════════
# CHECKS GROUP 7: DIST-001 expected_signal 覆盖
# ═══════════════════════════════════════════
print("\n═══ Group 7: DIST-001 expected_signal 覆盖 ═══")

dist_attack_entries = [e for e in corpus.get("dist_001_entries", [])
                       if e.get("category") != "control_case"]
dist_signals = set()
for e in dist_attack_entries:
    dist_signals.update(e.get("expected_signal", []))

req_dist_signals = [
    "slicing_pattern_detected",
    "cumulative_disclosure_blocked",
    "safe_summary_generated",
    "authorization_required",
    "human_review_required",
]
for s in req_dist_signals:
    check(
        s in dist_signals,
        f"DIST-001 expected_signal 包含: {s}",
        f"DIST-SIG-{req_dist_signals.index(s)+1:03d}",
    )

# ═══════════════════════════════════════════
# CHECKS GROUP 8: CROSS-001 expected_signal 覆盖
# ═══════════════════════════════════════════
print("\n═══ Group 8: CROSS-001 expected_signal 覆盖 ═══")

cross_attack_entries = [e for e in corpus.get("cross_001_entries", [])
                        if e.get("category") != "control_case"]
cross_signals = set()
for e in cross_attack_entries:
    cross_signals.update(e.get("expected_signal", []))

req_cross_signals = [
    "cross_context_composition_blocked",
    "context_boundary_preserved",
    "source_priority_enforced",
    "permission_check_required",
    "human_review_required",
]
for s in req_cross_signals:
    check(
        s in cross_signals,
        f"CROSS-001 expected_signal 包含: {s}",
        f"CROSS-SIG-{req_cross_signals.index(s)+1:03d}",
    )

# ═══════════════════════════════════════════
# CHECKS GROUP 9: Control case 验证
# ═══════════════════════════════════════════
print("\n═══ Group 9: Control case 验证 ═══")

all_entries_flat = corpus.get("dist_001_entries", []) + corpus.get("cross_001_entries", [])
control_entries = [e for e in all_entries_flat if e.get("control_case") is True]
check(
    len(control_entries) == 2,
    f"control cases 数量: 2 (实际 {len(control_entries)})",
    "CTRL-001",
)
for ce in control_entries:
    check(
        ce.get("control_case") is True,
        f"Control case {ce.get('case_id', '?')} 标记 control_case=true",
        f"CTRL-{ce.get('case_id', '?')}-flag",
    )
    signals = ce.get("expected_signal", [])
    check(
        "normal_response" in signals,
        f"Control case {ce.get('case_id', '?')} expected_signal 包含 normal_response",
        f"CTRL-{ce.get('case_id', '?')}-sig",
    )

# ═══════════════════════════════════════════
# CHECKS GROUP 10: 安全默认值
# ═══════════════════════════════════════════
print("\n═══ Group 10: 安全默认值 ═══")

check(
    meta.get("confirmed_vulnerability") is False,
    "confirmed_vulnerability=false",
    "SAFE-001",
)
check(
    meta.get("formal_finding_allowed") is False,
    "formal_finding_allowed=false",
    "SAFE-002",
)
check(
    meta.get("production_safety_claimed") is False,
    "production_safety_claimed=false",
    "SAFE-003",
)
check(
    meta.get("controlled_replay_claimed") is False,
    "controlled_replay_claimed=false",
    "SAFE-004",
)
check(
    meta.get("attack_execution_allowed") is False,
    "attack_execution_allowed=false",
    "SAFE-005",
)
check(
    meta.get("payload_generation_allowed") is False,
    "payload_generation_allowed=false",
    "SAFE-006",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 11: 禁止项检查
# ═══════════════════════════════════════════
print("\n═══ Group 11: 禁止项检查 ═══")

# 检查所有文件不包含危险内容
all_deliverable_paths = [
    os.path.join(PROJECT_ROOT, d) for d in deliverables
]
dangerous_patterns = [
    "rm -rf",
    "DROP TABLE",
    "sudo ",
    "chmod 777",
    "confirmed_vulnerability: true",
    "formal_finding_allowed: true",
    "production_safety_claimed: true",
    "attack_execution_allowed: true",
    "payload_generation_allowed: true",
    "real_target_selection_allowed: true",
]
for dp in all_deliverable_paths:
    if not os.path.isfile(dp):
        continue
    if dp.endswith("validate_adv_slice_002_design_gate.py"):
        continue
    with open(dp, "r", encoding="utf-8") as f:
        content = f.read()
    for pattern in dangerous_patterns:
        check(
            pattern not in content,
            f"文件 {os.path.basename(dp)} 不包含危险模式: {pattern}",
            f"DLG-{hash(pattern) % 10000:04d}",
        )

# ═══════════════════════════════════════════
# CHECKS GROUP 12: 无 run_config / 无执行证据文件
# ═══════════════════════════════════════════
print("\n═══ Group 12: 无执行入口 / 执行结果 ═══")

# 检查没有新增 adv_slice run_config
runner_dir = os.path.join(PROJECT_ROOT, "runners")
if os.path.isdir(runner_dir):
    for fname in os.listdir(runner_dir):
        check(
            "adv_slice" not in fname,
            f"runner 目录不包含 adv_slice run config: {fname}",
            f"NRC-{fname}",
        )

# 检查没有新增 adv_slice execution_results
for dp, dn, filenames in os.walk(PROJECT_ROOT):
    for f in filenames:
        if "execution_results" in f.lower() and "adv_slice" in f.lower():
            check(False, f"未生成 execution_results: {f}", "NEX-001")

# ═══════════════════════════════════════════
# CHECKS GROUP 13: exploit_chain_candidate / evidence_trace 不在条目中
# ═══════════════════════════════════════════
print("\n═══ Group 13: 禁止字段检查 ═══")

for entry in all_entries_flat:
    check(
        "exploit_chain_candidate" not in entry,
        f"条目 {entry.get('case_id', '?')} 不包含 exploit_chain_candidate",
        f"PRO-{entry.get('case_id', '?')}-a",
    )
    check(
        "evidence_trace" not in entry,
        f"条目 {entry.get('case_id', '?')} 不包含 evidence_trace",
        f"PRO-{entry.get('case_id', '?')}-b",
    )
    # 确认有 pre_execution_note 占位
    check(
        "pre_execution_note" in entry,
        f"条目 {entry.get('case_id', '?')} 包含 pre_execution_note 占位",
        f"PRO-{entry.get('case_id', '?')}-note",
    )

# ═══════════════════════════════════════════
# CHECKS GROUP 14: Metadata 完整性
# ═══════════════════════════════════════════
print("\n═══ Group 14: Metadata 完整性 ═══")

check(
    meta.get("corpus_draft_id") == "ADV-SLICE-002",
    "corpus_draft_id 正确",
    "META-001",
)
check(
    meta.get("corpus_draft_status") == "corpus_draft_gate_planned",
    "corpus_draft_status 为 corpus_draft_gate_planned",
    "META-002",
)
check(
    meta.get("total_entries") == 8,
    "total_entries == 8",
    "META-003",
)
check(
    meta.get("capabilities_scored") == "not_scored_corpus_draft_gate_only",
    "capabilities_scored 为 not_scored_corpus_draft_gate_only",
    "META-004",
)
check(
    meta.get("risk_level_scored") == "not_scored_corpus_draft_gate_only",
    "risk_level_scored 为 not_scored_corpus_draft_gate_only",
    "META-005",
)

# corpus_draft_status 更新
check(
    meta.get("corpus_draft_status") == "corpus_draft_gate_planned",
    "corpus_draft_status 为 corpus_draft_gate_planned",
    "META-006",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 15: SIM_ 格式检查
# ═══════════════════════════════════════════
print("\n═══ Group 15: SIM_ 格式检查 ═══")

corpus_text = yaml.dump(corpus).lower()
check(
    "<sim_" in corpus_text or "sim_" in corpus_text,
    "corpus 草案使用 SIM_ 格式模拟数据",
    "SIM-001",
)

with open(os.path.join(PROJECT_ROOT, "docs/adv_slice_002_corpus_draft_notes.md"),
          "r", encoding="utf-8") as f:
    notes_text = f.read()
check(
    "expected_signal" in notes_text,
    "notes 文档使用 expected_signal 术语",
    "SIM-002",
)
check(
    "由后续" in notes_text,
    "notes 文档说明 exploit_chain_candidate/evidence_trace 由后续阶段产生",
    "SIM-003",
)
check(
    "不创建 run_config" in notes_text,
    "notes 文档声明未创建 run_config",
    "SIM-004",
)
check(
    "不执行 capability_engine" in notes_text,
    "notes 文档声明未执行 capability_engine",
    "SIM-005",
)
check(
    "不生成 execution_results" in notes_text,
    "notes 文档声明未生成 execution_results",
    "SIM-006",
)
check(
    "human_review_required 在本阶段仅作为 expected_signal" in notes_text,
    "notes 文档明确 human_review_required 为 expected_signal 非实际计数",
    "SIM-007",
)

# ═══════════════════════════════════════════
# CHECKS GROUP 16: playbook 元数据字段完整性
# ═══════════════════════════════════════════
print("\n═══ Group 16: Playbook 元数据字段完整性 ═══")

required_pb_fields = [
    "playbook_id", "playbook_name", "assessment_mode",
    "attacker_type", "attack_objective", "target_boundaries",
    "description", "synthetic_only",
]

for pb_key, pb_name in [("playbook_metadata_dist", "DIST-001"),
                         ("playbook_metadata_cross", "CROSS-001")]:
    pb = corpus.get(pb_key, {})
    for field in required_pb_fields:
        check(
            field in pb,
            f"{pb_name} playbook_metadata 包含: {field}",
            f"PB-META-{hash(pb_name+field) % 10000:04d}",
        )

# ═══════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════
print(f"\n{'='*60}")
print(f"  校验完成: {passed} 通过, {failed} 失败")
print(f"{'='*60}")

if failed > 0:
    print("  ❌ 部分检查未通过，请修复后重新运行")
    sys.exit(1)
else:
    print("  ALL CHECKS PASSED — ADV-SLICE-002 design_gate 验收通过")
    sys.exit(0)
