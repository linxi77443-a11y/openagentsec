#!/usr/bin/env python3
"""Phase-91A RED-015 Review Cleanup Validator"""

import os
import sys
import yaml
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RED015_DIR = os.path.join(PROJECT_ROOT, "red_team", "red_015")
INDEX_FILE = os.path.join(PROJECT_ROOT, "red_team_report_index.yaml")

checks = []
passed = 0
failed = 0


def check(desc, cond):
    global passed, failed
    checks.append((desc, cond))
    if cond:
        passed += 1
        print(f"  ✅ {desc}")
    else:
        failed += 1
        print(f"  ❌ {desc}")


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


# === V001: RED-015 文件完整性 ===
print("\n=== V001: RED-015 文件完整性 ===")
required_files = [
    "adversarial_playbook.yaml", "run_config.yaml", "execution_results.json",
    "red_015_result.yaml", "capability_scorecard.yaml",
    "red_team_evidence_candidates.yaml", "blue_control_candidates.yaml",
    "purple_retest_candidates.yaml", "reused_baseline_index.yaml", "short_notes.md"
]
for fname in required_files:
    check(f"{fname} 存在", os.path.exists(os.path.join(RED015_DIR, fname)))

# === V002: 索引存在性 ===
print("\n=== V002: 索引存在性 ===")
check("red_team_report_index.yaml 存在", os.path.exists(INDEX_FILE))
index = load_yaml(INDEX_FILE)
reports = index.get("reports", [])
red015_entries = [r for r in reports if r.get("report_id") == "RED-015"]
check("RED-015 在索引中", len(red015_entries) == 1)

# === V003: 索引唯一性 ===
print("\n=== V003: 索引唯一性 ===")
all_ids = [r.get("report_id") for r in reports]
check("无重复 report_id", len(all_ids) == len(set(all_ids)))
check("RED-015 唯一", all_ids.count("RED-015") == 1)

# === V004: RED-015 索引字段完整性 ===
print("\n=== V004: RED-015 索引字段 ===")
if red015_entries:
    r = red015_entries[0]
    check("report_id=RED-015", r.get("report_id") == "RED-015")
    check("status=closed/judge_approved", r.get("status") == "closed/judge_approved")
    check("path_id 为 null（链级评估）", r.get("path_id") is None)
    check("chain_id=ADV-CHAIN-001", r.get("chain_id") == "ADV-CHAIN-001")
    check("breakthrough=0", r.get("breakthrough") == 0)
    check("boundary_preservation_rate=100", r.get("boundary_preservation_rate") in [100, "100%"])
    check("total_entries=47", r.get("total_entries") == 47)
    check("total_attack=29", r.get("total_attack") == 29)
    check("total_control=18", r.get("total_control") == 18)
    check("v3_1_s5_sections 存在", r.get("v3_1_s5_sections") is not None)

# === V005: RED-015 统计一致性 ===
print("\n=== V005: RED-015 统计一致性 ===")
result = load_yaml(os.path.join(RED015_DIR, "red_015_result.yaml"))
es = result.get("execution_summary", {})
check("result total_entries=47", es.get("total_entries") == 47)
check("result attack_entries=29", es.get("attack_entries") == 29)
check("result control_entries=18", es.get("control_entries") == 18)
check("result breakthroughs=0", es.get("breakthroughs") == 0)
check("result confirmed_vulnerability=false", es.get("confirmed_vulnerability") is False)
check("result formal_finding_allowed=false", es.get("formal_finding_allowed") is False)
check("result all_findings_are_candidate_level=true", es.get("all_findings_are_candidate_level") is True)

# === V006: Scorecard 一致性 ===
print("\n=== V006: Scorecard 一致性 ===")
sc = load_yaml(os.path.join(RED015_DIR, "capability_scorecard.yaml"))
cl = sc.get("chain_level", {})
check("scorecard total_entries=47", cl.get("total_entries") == 47)
check("scorecard blocked=29", cl.get("blocked") == 29)
check("scorecard allowed=18", cl.get("allowed") == 18)
check("scorecard breakthroughs=0", cl.get("breakthroughs") == 0)
check("scorecard confirmed_vulnerability=false", cl.get("confirmed_vulnerability") is False)

# === V007: execution_results 安全字段 ===
print("\n=== V007: execution_results 安全字段 ===")
with open(os.path.join(RED015_DIR, "execution_results.json")) as f:
    er = json.load(f)
check("er confirmed_vulnerability=false", er.get("confirmed_vulnerability") is False)
check("er formal_finding_allowed=false", er.get("formal_finding_allowed") is False)
check("er all_findings_are_candidate_level=true", er.get("all_findings_are_candidate_level") is True)
check("er production_safety_claimed=false", er.get("production_safety_claimed") is False)
check("er attack_execution_allowed=false", er.get("attack_execution_allowed") is False)
check("er payload_generation_allowed=false", er.get("payload_generation_allowed") is False)
er_summary = er.get("summary", {})
check("er summary total_entries=47", er_summary.get("total_entries") == 47)
check("er summary breakthrough_count=0", er_summary.get("breakthrough_count") == 0)

# === V008: Evidence/Controls/Retest 存在 ===
print("\n=== V008: Evidence/Controls/Retest ===")
ev = load_yaml(os.path.join(RED015_DIR, "red_team_evidence_candidates.yaml"))
check("evidence candidates 存在", len(ev.get("evidence_candidates", [])) > 0)
bc = load_yaml(os.path.join(RED015_DIR, "blue_control_candidates.yaml"))
check("blue control candidates 存在", len(bc.get("control_candidates", [])) > 0)
pr = load_yaml(os.path.join(RED015_DIR, "purple_retest_candidates.yaml"))
check("purple retest candidates 存在", len(pr.get("retest_candidates", [])) > 0)

# === V009: 索引不干扰其他报告 ===
print("\n=== V009: 其他报告完整性 ===")
red016 = [r for r in reports if r.get("report_id") == "RED-016"]
red017 = [r for r in reports if r.get("report_id") == "RED-017"]
check("RED-016 仍在索引中", len(red016) == 1)
check("RED-016 status=closed/judge_approved", red016[0].get("status") == "closed/judge_approved" if red016 else False)
check("RED-017 仍在索引中", len(red017) == 1)
check("RED-017 status=closed/judge_approved", red017[0].get("status") == "closed/judge_approved" if red017 else False)

# === V010: 模拟数据合规性 ===
print("\n=== V010: 模拟数据合规性 ===")
suspicious = ["api_key=", "password=", "real_siem", "real_database", "production_url"]
for fname in os.listdir(RED015_DIR):
    if fname.endswith((".yaml", ".md")):
        with open(os.path.join(RED015_DIR, fname)) as f:
            content = f.read().lower()
        for pat in suspicious:
            if pat in content:
                check(f"{fname} 含可疑模式: {pat}", False)

# === V011: Cleanup result 存在 ===
print("\n=== V011: Cleanup Result ===")
cleanup_result = os.path.join(PROJECT_ROOT, "results", "phase91a_red015_review_cleanup_result.yaml")
check("cleanup result 存在", os.path.exists(cleanup_result))
if os.path.exists(cleanup_result):
    cr = load_yaml(cleanup_result)
    check("cleanup result entries_added=1", cr.get("index_cleanup", {}).get("entries_added") == 1)
    check("cleanup result no_execution=true", cr.get("no_execution") is True)
    # PRD v2.0 §13 执行状态
    check("task_type=registry_review_cleanup", cr.get("task_type") == "registry_review_cleanup")
    check("assessment_execution_performed=false", cr.get("assessment_execution_performed") is False)
    check("capability_engine_executed=false", cr.get("capability_engine_executed") is False)
    check("execution_results_generated=false", cr.get("execution_results_generated") is False)
    check("corpus_added=false", cr.get("corpus_added") is False)
    check("run_config_added=false", cr.get("run_config_added") is False)
    # 来源报告原始值
    check("source_report_capability_value_raw=very_strong", cr.get("source_report_capability_value_raw") == "very_strong")
    check("source_report_risk_level_raw=low", cr.get("source_report_risk_level_raw") == "low")
    check("source_report_breakthrough_detected=false", cr.get("source_report_breakthrough_detected") is False)
    check("source_report_results_unchanged=true", cr.get("source_report_results_unchanged") is True)
    check("capability_value_declared_by_phase=false", cr.get("capability_value_declared_by_phase") is False)
    check("risk_level_declared_by_phase=false", cr.get("risk_level_declared_by_phase") is False)
    check("normalization_performed=false", cr.get("normalization_performed") is False)
    # 模拟红队安全字段
    srsf = cr.get("simulated_red_team_safety_fields", {})
    check("attack_execution_allowed=false", srsf.get("attack_execution_allowed") is False)
    check("payload_generation_allowed=false", srsf.get("payload_generation_allowed") is False)
    check("real_target_selection_allowed=false", srsf.get("real_target_selection_allowed") is False)
    check("red_team_engine_not_executable=true", srsf.get("red_team_engine_not_executable") is True)
    check("dashboard_not_execution_interface=true", srsf.get("dashboard_not_execution_interface") is True)
    check("confirmed_vulnerability=false", srsf.get("confirmed_vulnerability") is False)
    check("formal_finding_allowed=false", srsf.get("formal_finding_allowed") is False)
    check("production_safety_claimed=false", srsf.get("production_safety_claimed") is False)
    check("controlled_replay_execution_allowed=false", srsf.get("controlled_replay_execution_allowed") is False)

# === V012: 索引 RED-015 额外字段 ===
print("\n=== V012: 索引 RED-015 额外字段 ===")
if red015_entries:
    r = red015_entries[0]
    check("index_repair_only=true", r.get("index_repair_only") is True)
    check("source_report_ref 存在", r.get("source_report_ref") is not None)
    check("source_chain_ref=ADV-CHAIN-001", r.get("source_chain_ref") == "ADV-CHAIN-001")
    check("source_results_unchanged=true", r.get("source_results_unchanged") is True)

# === 汇总 ===
print(f"\n{'='*60}")
print(f"总检查项: {len(checks)}")
print(f"通过: {passed}")
print(f"失败: {failed}")
print(f"结果: {'ALL CHECKS PASSED' if failed == 0 else 'SOME CHECKS FAILED'}")
print(f"{'='*60}")
sys.exit(0 if failed == 0 else 1)
