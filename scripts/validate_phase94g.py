#!/usr/bin/env python3
"""Phase-94G Task Package Generation Validator"""
import os, sys, yaml
PLANNING = os.path.join(os.path.dirname(__file__), "..", "planning")
PACKAGES = os.path.join(os.path.dirname(__file__), "..", "task_packages")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-94G Validator ===")

# V001: 公共资产
for f in ["phase94g_input_evidence_index.yaml","phase94g_shared_safety_profile.yaml",
          "phase94g_shared_delivery_contract.yaml","phase94g_dependency_order.yaml",
          "phase94g_task_package_manifest.yaml","phase94g_coverage_claim_reconciliation.yaml"]:
    check(f"planning/{f}", os.path.exists(os.path.join(PLANNING, f)))

# V002: 7 个任务包
for pkg in ["M12-RT-094.md","M15-RT-094.md","M38-XM-094.md","M08-MT-094.md",
            "Phase-94D.md","Phase-94E.md","Phase-94F.md"]:
    check(f"task_packages/{pkg}", os.path.exists(os.path.join(PACKAGES, pkg)))

# V003: 结果文件
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase94g_design_gate_result.yaml")))

# V004: 结果文件字段
r = yaml.safe_load(open(os.path.join(RESULTS, "phase94g_design_gate_result.yaml")))
check("assessment_execution_performed=false", r["assessment_execution_performed"] is False)
check("capability_engine_executed=false", r["capability_engine_executed"] is False)
check("execution_results_generated=false", r["execution_results_generated"] is False)
check("capability_value=not_applicable", r["capability_value"] == "not_applicable")
check("risk_level=not_applicable", r["risk_level"] == "not_applicable")
check("registered_module=false", r["registered_module"] is False)
check("coverage_change_claimed=false", r["coverage_change_claimed"] is False)
check("coverage_credit_requested=0", r["coverage_credit_requested"] == 0)
s = r["safety"]
check("confirmed_vulnerability=false", s["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", s["formal_finding_allowed"] is False)
check("production_safety_claimed=false", s["production_safety_claimed"] is False)

# V005: Task package manifest
manifest = yaml.safe_load(open(os.path.join(PLANNING, "phase94g_task_package_manifest.yaml")))
check("7 packages", manifest["total_packages"] == 7)
for tp in manifest["task_packages"]:
    check(f"{tp['task_id']} has independent_validator", tp.get("independent_validator") is not None)
    check(f"{tp['task_id']} independent_commit=true", tp.get("independent_commit") is True)

# V006: Coverage claim reconciliation
ccr = yaml.safe_load(open(os.path.join(PLANNING, "phase94g_coverage_claim_reconciliation.yaml")))
check("0 duplicate claims", ccr["summary"]["duplicate_claims"] == 0)
check("coverage_credit_granted_by_phase94g=0", ccr["summary"]["coverage_credit_granted_by_phase94g"] == 0)

# V007: Dependency order
dep = yaml.safe_load(open(os.path.join(PLANNING, "phase94g_dependency_order.yaml")))
check("dependency_graph present", dep.get("dependency_graph") is not None)

# V008: No execution results created
check("no execution_results.json", not os.path.exists(os.path.join(PACKAGES, "execution_results.json")))
check("no scorecard.yaml", not os.path.exists(os.path.join(PACKAGES, "capability_scorecard.yaml")))

# V009: Registry not modified
import subprocess
reg = subprocess.run(["git", "diff", "HEAD", "--", "capability_modules/"], capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."))
check("registry_diff=0", len(reg.stdout.strip().split("\n")) <= 1)

print(f"\n{'='*60}")
print(f"TOTAL: {P}/{P+F} checks passed")
print(f"{'='*60}")
sys.exit(0 if F == 0 else 1)
