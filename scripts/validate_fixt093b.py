#!/usr/bin/env python3
"""FIXT-093B Validator"""
import os, sys, yaml
DIR = os.path.join(os.path.dirname(__file__), "..", "mock_fixtures", "phase93b")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== FIXT-093B ===")
check("fixture exists", os.path.exists(os.path.join(DIR, "defense_state_fixtures.yaml")))
f = yaml.safe_load(open(os.path.join(DIR, "defense_state_fixtures.yaml")))
check("5 branches", len(f["state_branches"])==5)
branch_ids = [b["branch_id"] for b in f["state_branches"]]
check("normal_block present", "normal_block" in branch_ids)
check("gradual_degradation present", "gradual_degradation" in branch_ids)
check("evidence_insufficient present", "evidence_insufficient" in branch_ids)
check("audit_chain_break present", "audit_chain_break" in branch_ids)
check("recovery_to_blocked present", "recovery_to_blocked" in branch_ids)
check("synthetic_only=true", f["synthetic_only"] is True)
check("assessment_execution_performed=false", f["assessment_execution_performed"] is False)
check("capability_engine_executed=false", f["capability_engine_executed"] is False)
check("coverage_credit=0", f["coverage_credit"]==0)
check("capability_value=not_applicable", f["capability_value"]=="not_applicable")
sa = f["safety_assertions"]
check("confirmed_vulnerability=false", sa["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", sa["formal_finding_allowed"] is False)

print(f"\n{'='*40}\nFIXT-093B: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F==0 else 1)
