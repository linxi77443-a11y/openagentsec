#!/usr/bin/env python3
"""FIXT-093A Validator"""
import os, sys, yaml
DIR = os.path.join(os.path.dirname(__file__), "..", "mock_fixtures", "phase93a")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== FIXT-093A ===")
check("fixture exists", os.path.exists(os.path.join(DIR, "red018_path_fixtures.yaml")))
f = yaml.safe_load(open(os.path.join(DIR, "red018_path_fixtures.yaml")))
check("5 nodes", len(f["nodes"])==5)
node_ids = [n["node_id"] for n in f["nodes"]]
check("M43 present", "M43" in node_ids)
check("M46 present", "M46" in node_ids)
check("M48 present", "M48" in node_ids)
check("M49 present", "M49" in node_ids)
check("M50 present", "M50" in node_ids)
check("4 edges", len(f["edges"])==4)
check("synthetic_only=true", f["synthetic_only"] is True)
check("assessment_execution_performed=false", f["assessment_execution_performed"] is False)
check("capability_engine_executed=false", f["capability_engine_executed"] is False)
check("coverage_credit=0", f["coverage_credit"]==0)
check("capability_value=not_applicable", f["capability_value"]=="not_applicable")

print(f"\n{'='*40}\nFIXT-093A: {P}/{P+F} passed\n{'='*40}")
sys.exit(0 if F==0 else 1)
