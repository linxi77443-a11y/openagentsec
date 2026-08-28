#!/usr/bin/env python3
"""Phase-94C Design Gate Validator"""
import os, sys, yaml
PLANNING = os.path.join(os.path.dirname(__file__), "..", "planning")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-94C Design Gate Validator ===")

# V001: 文件完整性
for f in ["phase94c_workstream_manifest.yaml","phase94c_coverage_precheck_matrix.yaml",
          "phase94c_dependency_matrix.yaml","phase94c_assessment_mode_matrix.yaml",
          "phase94c_duplicate_claim_checklist.yaml","phase94c_validator_mapping.yaml",
          "phase94c_task_candidate_index.yaml","phase94c_safety_boundary_profile.yaml"]:
    check(f"planning/{f}", os.path.exists(os.path.join(PLANNING, f)))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase94c_design_gate_result.yaml")))

# V002: 结果文件字段
r = yaml.safe_load(open(os.path.join(RESULTS, "phase94c_design_gate_result.yaml")))
check("assessment_execution_performed=false", r["assessment_execution_performed"] is False)
check("capability_engine_executed=false", r["capability_engine_executed"] is False)
check("execution_results_generated=false", r["execution_results_generated"] is False)
check("capability_value=not_applicable", r["capability_value"] == "not_applicable")
check("risk_level=not_applicable", r["risk_level"] == "not_applicable")
check("coverage_change_claimed=false", r["coverage_change_claimed"] is False)
check("registered_module=false", r["registered_module"] is False)

# V003: 7 workstreams
manifest = yaml.safe_load(open(os.path.join(PLANNING, "phase94c_workstream_manifest.yaml")))
ws = manifest.get("planned_workstreams", [])
check("7 workstreams", len(ws) == 7)
for w in ws:
    check(f"{w['task_id']} has task_id", w.get("task_id") is not None)
    check(f"{w['task_id']} has primary_scope", w.get("primary_scope") is not None)
    check(f"{w['task_id']} has assessment_mode", w.get("assessment_mode") is not None)
    check(f"{w['task_id']} has independent_validator", w.get("independent_validator") is not None)

# V004: 一致性规则
cr = manifest.get("consistency_rules", {})
check("one_task_failure_blocks_other_tasks=false", cr.get("one_task_failure_blocks_other_tasks") is False)
check("one_task_success_cannot_cover_other_task_failure=true", cr.get("one_task_success_cannot_cover_other_task_failure") is True)
check("merged_module_mvp_allowed=false", cr.get("merged_module_mvp_allowed") is False)
check("duplicate_coverage_credit_allowed=false", cr.get("duplicate_coverage_credit_allowed") is False)
check("batch_validator_replaces_task_validator=false", cr.get("batch_validator_replaces_task_validator") is False)

# V005: Coverage precheck
precheck = yaml.safe_load(open(os.path.join(PLANNING, "phase94c_coverage_precheck_matrix.yaml")))
check("12 modules checked", precheck["summary"]["total_modules_checked"] == 12)
check("4 with gap", precheck["summary"]["with_gap"] == 4)
check("8 no gap", precheck["summary"]["no_gap"] == 8)

# V006: Duplicate claim checklist
dc = yaml.safe_load(open(os.path.join(PLANNING, "phase94c_duplicate_claim_checklist.yaml")))
check("0 duplicates detected", dc["summary"]["duplicate_detected"] == 0)

# V007: Validator mapping
vm = yaml.safe_load(open(os.path.join(PLANNING, "phase94c_validator_mapping.yaml")))
check("7 validators mapped", len(vm["validator_mapping"]) == 7)
check("batch_validator_replaces_task_validator=false", "false" in str(vm.get("rules", [])))

# V008: Safety fields
sf = yaml.safe_load(open(os.path.join(PLANNING, "phase94c_safety_boundary_profile.yaml")))
gs = sf["global_safety_boundary"]
check("confirmed_vulnerability=false", gs["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", gs["formal_finding_allowed"] is False)
check("production_safety_claimed=false", gs["production_safety_claimed"] is False)
check("attack_execution_allowed=false", gs["attack_execution_allowed"] is False)
check("synthetic_only=true", gs["synthetic_only"] is True)
check("red_team_engine_not_executable=true", gs["red_team_engine_not_executable"] is True)

# V009: Assessment mode matrix
am = yaml.safe_load(open(os.path.join(PLANNING, "phase94c_assessment_mode_matrix.yaml")))
check("M12-RT-094=defensive_evaluation", am["task_mode_mapping"]["M12-RT-094"] == "defensive_evaluation")
check("M38-XM-094=adversarial_validation", am["task_mode_mapping"]["M38-XM-094"] == "adversarial_validation")
check("Phase-94D=not_applicable", am["task_mode_mapping"]["Phase-94D"] == "not_applicable")

# V010: Task candidate index
tci = yaml.safe_load(open(os.path.join(PLANNING, "phase94c_task_candidate_index.yaml")))
check("7 candidate tasks", len(tci["candidate_tasks"]) == 7)
check("disclaimer present", tci.get("disclaimer") is not None)

# V011: No execution results
check("no execution_results.json created", not os.path.exists(os.path.join(PLANNING, "execution_results.json")))
check("no scorecard created", not os.path.exists(os.path.join(PLANNING, "capability_scorecard.yaml")))

# V012: Registry not modified
import subprocess
reg_diff = subprocess.run(["git", "diff", "HEAD", "--", "capability_modules/"], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."))
check("registry_diff=0 lines", len(reg_diff.stdout.strip().split("\n")) <= 1)

print(f"\n{'='*60}")
print(f"TOTAL: {P}/{P+F} checks passed")
print(f"{'='*60}")
sys.exit(0 if F == 0 else 1)
