#!/usr/bin/env python3
"""Phase-92C Batch Review Submission Validator"""
import os, sys, yaml
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
BATCH = os.path.join(os.path.dirname(__file__), "..", "batch_runtime")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

# V001: 交付物存在
print("\n=== V001: 交付物 ===")
for f in ["phase92c_batch_child_task_manifest.yaml","phase92c_batch_review_evidence_matrix.yaml",
          "phase92c_batch_commit_file_map.yaml","phase92c_batch_coverage_claim_reconciliation.yaml",
          "phase92c_batch_safety_assertion_matrix.yaml","phase92c_batch_review_submission.md"]:
    check(f, os.path.exists(os.path.join(DOCS, f)))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase92c_batch_review_submission_result.yaml")))

# V002: Manifest 子任务完整性
print("\n=== V002: Manifest ===")
manifest = yaml.safe_load(open(os.path.join(DOCS, "phase92c_batch_child_task_manifest.yaml")))
tasks = manifest.get("child_tasks", [])
check("8 child tasks", len(tasks) == 8)
for t in tasks:
    check(f"{t['task_id']} has task_id", t.get("task_id") is not None)
    check(f"{t['task_id']} has module_or_path", t.get("module_or_path") is not None)
    check(f"{t['task_id']} has assessment_mode", t.get("assessment_mode") is not None)
    check(f"{t['task_id']} has prd_reference", t.get("prd_reference") is not None)
    check(f"{t['task_id']} execution_allowed=false", t.get("execution_allowed") is False)
    check(f"{t['task_id']} judge_status=pending_review", t.get("judge_status") == "pending_review")

# V003: 禁止项
print("\n=== V003: 禁止项 ===")
manifest_str = yaml.dump(manifest)
check("no merged_module_mvp", "merged_module_mvp" not in manifest_str)
check("no batch_auto_approval", "batch_auto_approval" not in manifest_str)
check("no commit_only_acceptance", "commit_only_acceptance" not in manifest_str)
check("batch_orchestration_only=true", manifest.get("batch_orchestration_only") is True)
check("coverage_credit_granted=false", manifest.get("coverage_credit_granted") is False)
check("registered_module=false", manifest.get("registered_module") is False)

# V004: 安全字段（完整）
print("\n=== V004: 安全字段 ===")
safety = yaml.safe_load(open(os.path.join(DOCS, "phase92c_batch_safety_assertion_matrix.yaml")))
ss = safety.get("batch_safety_snapshot", {})
safety_fields = [
    ("confirmed_vulnerability", False), ("formal_finding_allowed", False),
    ("production_safety_claimed", False), ("controlled_replay_execution_allowed", False),
    ("controlled_replay_claimed", False), ("attack_execution_allowed", False),
    ("payload_generation_allowed", False), ("real_target_selection_allowed", False),
    ("real_system_connection_allowed", False), ("real_api_call_allowed", False),
    ("real_tool_execution_allowed", False), ("real_data_access_allowed", False),
    ("synthetic_only", True), ("red_team_engine_not_executable", True),
    ("dashboard_not_execution_interface", True),
]
for field, expected in safety_fields:
    actual = ss.get(field)
    check(f"safety.{field}={expected}", actual is expected or actual == expected)

# V005: Coverage reconciliation
print("\n=== V005: Coverage ===")
cr = yaml.safe_load(open(os.path.join(DOCS, "phase92c_batch_coverage_claim_reconciliation.yaml")))
check("batch_coverage_credit_granted=false", cr.get("batch_coverage_credit_granted") is False)
check("batch_registered_as_module=false", cr.get("batch_registered_as_module") is False)
for c in cr.get("coverage_claims", []):
    check(f"{c['task_id']} credit_granted=false", c.get("coverage_credit_granted") is False)
    if c.get("task_id") == "M-BATCH-WS-M19":
        check("M19 previously_judge_approved=true", c.get("previously_judge_approved") is True)
        check("M19 duplicate_coverage_credit_allowed=false", c.get("duplicate_coverage_credit_allowed") is False)

# V006: Result yaml
print("\n=== V006: Result ===")
result = yaml.safe_load(open(os.path.join(RESULTS, "phase92c_batch_review_submission_result.yaml")))
check("total child tasks=8", result.get("child_task_summary", {}).get("total") == 8)
check("coverage_credit_granted=0", result.get("coverage_credit_granted") == 0)
check("judge_approved=0", result.get("judge_approved") == 0)
check("pending_review=7", result.get("pending_review") == 7)
check("blocked_for_review=1", result.get("blocked_for_review") == 1)

# V007: No-execution fields
print("\n=== V007: No-execution ===")
check("task_type=batch_review_submission", result.get("task_type") == "batch_review_submission")
check("assessment_execution_performed=false", result.get("assessment_execution_performed") is False)
check("capability_engine_executed=false", result.get("capability_engine_executed") is False)
check("execution_results_generated_by_phase=false", result.get("execution_results_generated_by_phase") is False)

# V008: SHARED PRD mapping
print("\n=== V008: SHARED PRD mapping ===")
shared_task = [t for t in tasks if t.get("task_id") == "M-BATCH-WS-SHARED"]
if shared_task:
    prd = shared_task[0].get("prd_reference", "")
    check("SHARED has PRD §10", "§10" in prd)
    check("SHARED has PRD §11", "§11" in prd)
    check("SHARED has v3.1 §9", "§9" in prd or "v3.1" in prd)

print(f"\n{'='*60}")
print(f"TOTAL: {P}/{P+F} checks passed")
print(f"{'='*60}")
sys.exit(0 if F==0 else 1)
