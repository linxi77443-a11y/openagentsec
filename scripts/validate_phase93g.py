#!/usr/bin/env python3
"""Phase-93G Batch Reconciliation Validator"""
import os, sys, yaml
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-93G ===")
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase93g_batch_reconciliation_result.yaml")))
r = yaml.safe_load(open(os.path.join(RESULTS, "phase93g_batch_reconciliation_result.yaml")))
check("assessment_execution_performed=false", r["assessment_execution_performed"] is False)
check("capability_engine_executed=false", r["capability_engine_executed"] is False)
check("coverage_credit=0", r["coverage_credit"]==0)

tsr = r["task_status_reconciliation"]
check("6 tasks reconciled (Phase-93G is self, excluded)", len(tsr)==6)
for tid, data in tsr.items():
    check(f"{tid} coverage_credit=0", data["coverage_credit"]==0)
    check(f"{tid} execution_results_modified=false", data.get("execution_results_modified", False) is False)

bs = r["batch_summary"]
check("judge_approved=6", bs["judge_approved"]==6)
check("blocked=0", bs["blocked"]==0)

s = r["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)
check("production_safety_claimed=false", s["production_safety_claimed"] is False)
check("synthetic_only=true", s["synthetic_only"] is True)
check("attack_execution_allowed=false", s["attack_execution_allowed"] is False)
check("payload_generation_allowed=false", s["payload_generation_allowed"] is False)
check("real_target_selection_allowed=false", s["real_target_selection_allowed"] is False)
check("real_system_connection_allowed=false", s["real_system_connection_allowed"] is False)
check("real_tool_execution_allowed=false", s["real_tool_execution_allowed"] is False)
check("real_data_access_allowed=false", s["real_data_access_allowed"] is False)

print(f"\n{'='*40}\nPhase-93G: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F==0 else 1)
