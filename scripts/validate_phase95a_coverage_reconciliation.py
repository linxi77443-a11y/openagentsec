#!/usr/bin/env python3
"""
Phase-95A Full System Coverage & Compliance Consistency Reconciliation Gate Validator
Validates read-only compliance, mandatory declarations, safety invariants, and reconciliation deliverables.
"""
import os
import sys
import yaml
import subprocess

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

checks = []
P = 0
F = 0

def check(description, condition):
    global P, F
    checks.append((description, condition))
    if condition:
        P += 1
        print(f"  ✅ {description}")
    else:
        F += 1
        print(f"  ❌ {description}")

print("\n=== Phase-95A Coverage & Compliance Reconciliation Validator ===")

# ------------------------------------------------------------
# Check 1: Deliverable Files Existence
# ------------------------------------------------------------
required_docs = [
    "phase95a_registry_coverage_reconciliation.yaml",
    "phase95a_open_gap_classification.yaml",
    "phase95a_system_compliance_reconciliation_notes.md",
    "phase95a_short_notes.md"
]

for doc_file in required_docs:
    full_path = os.path.join(DOCS_DIR, doc_file)
    check(f"Doc file existence: docs/{doc_file}", os.path.exists(full_path))

result_yaml_path = os.path.join(RESULTS_DIR, "phase95a_design_gate_result.yaml")
check("Result file existence: results/phase95a_design_gate_result.yaml", os.path.exists(result_yaml_path))

# ------------------------------------------------------------
# Check 2: Mandatory Declarations in phase95a_registry_coverage_reconciliation.yaml
# ------------------------------------------------------------
reconcil_path = os.path.join(DOCS_DIR, "phase95a_registry_coverage_reconciliation.yaml")
if os.path.exists(reconcil_path):
    with open(reconcil_path, "r", encoding="utf-8") as f:
        rec_data = yaml.safe_load(f)
    
    check("reconcil: assessment_execution_performed == false", rec_data.get("assessment_execution_performed") is False)
    check("reconcil: capability_engine_executed == false", rec_data.get("capability_engine_executed") is False)
    check("reconcil: execution_results_generated == false", rec_data.get("execution_results_generated") is False)
    check("reconcil: capability_value == not_applicable", rec_data.get("capability_value") == "not_applicable")
    check("reconcil: risk_level == not_applicable", rec_data.get("risk_level") == "not_applicable")
    check("reconcil: coverage_change_claimed == false", rec_data.get("coverage_change_claimed") is False)
    
    sf = rec_data.get("safety_fields", {})
    check("reconcil: confirmed_vulnerability == false", sf.get("confirmed_vulnerability") is False)
    check("reconcil: formal_finding_allowed == false", sf.get("formal_finding_allowed") is False)
    check("reconcil: production_safety_claimed == false", sf.get("production_safety_claimed") is False)
    check("reconcil: synthetic_only == true", sf.get("synthetic_only") is True)
    
    mod_rec = rec_data.get("module_reconciliation", {})
    check("reconcil: total_modules == 50", mod_rec.get("total_modules") == 50)
    check("reconcil: all_modules_mvp_complete == true", mod_rec.get("all_modules_mvp_complete") is True)
    
    rt_rec = rec_data.get("red_team_reconciliation", {})
    check("reconcil: total_reports_reconciled == 15", rt_rec.get("total_reports_reconciled") == 15)
    check("reconcil: total_breakthrough == 0", rt_rec.get("total_breakthrough") == 0)

# ------------------------------------------------------------
# Check 3: Mandatory Declarations in phase95a_open_gap_classification.yaml
# ------------------------------------------------------------
gap_path = os.path.join(DOCS_DIR, "phase95a_open_gap_classification.yaml")
if os.path.exists(gap_path):
    with open(gap_path, "r", encoding="utf-8") as f:
        gap_data = yaml.safe_load(f)
        
    check("gap_class: assessment_execution_performed == false", gap_data.get("assessment_execution_performed") is False)
    check("gap_class: capability_engine_executed == false", gap_data.get("capability_engine_executed") is False)
    check("gap_class: execution_results_generated == false", gap_data.get("execution_results_generated") is False)
    check("gap_class: capability_value == not_applicable", gap_data.get("capability_value") == "not_applicable")
    check("gap_class: risk_level == not_applicable", gap_data.get("risk_level") == "not_applicable")
    check("gap_class: coverage_change_claimed == false", gap_data.get("coverage_change_claimed") is False)
    
    gap_sf = gap_data.get("safety_fields", {})
    check("gap_class: confirmed_vulnerability == false", gap_sf.get("confirmed_vulnerability") is False)
    check("gap_class: formal_finding_allowed == false", gap_sf.get("formal_finding_allowed") is False)
    check("gap_class: production_safety_claimed == false", gap_sf.get("production_safety_claimed") is False)
    check("gap_class: synthetic_only == true", gap_sf.get("synthetic_only") is True)
    
    gap_sum = gap_data.get("gap_summary", {})
    check("gap_class: total_blocking == 0", gap_sum.get("total_blocking") == 0)

# ------------------------------------------------------------
# Check 4: Text Content Assertions in markdown files
# ------------------------------------------------------------
notes_path = os.path.join(DOCS_DIR, "phase95a_system_compliance_reconciliation_notes.md")
if os.path.exists(notes_path):
    with open(notes_path, "r", encoding="utf-8") as f:
        notes_content = f.read()
    
    check("notes.md: contains PRD v1.0 §6 reference", "PRD v1.0 §6" in notes_content)
    check("notes.md: contains PRD v1.0 §7 reference", "PRD v1.0 §7" in notes_content)
    check("notes.md: contains PRD v2.0 §4 reference", "PRD v2.0 §4" in notes_content)
    check("notes.md: contains PRD v3.1 §4 reference", "PRD v3.1 §4" in notes_content)
    check("notes.md: contains assessment_execution_performed: false", "assessment_execution_performed: false" in notes_content)
    check("notes.md: contains capability_engine_executed: false", "capability_engine_executed: false" in notes_content)
    check("notes.md: contains execution_results_generated: false", "execution_results_generated: false" in notes_content)
    check("notes.md: contains capability_value: not_applicable", "capability_value: not_applicable" in notes_content)
    check("notes.md: contains risk_level: not_applicable", "risk_level: not_applicable" in notes_content)
    check("notes.md: contains coverage_change_claimed: false", "coverage_change_claimed: false" in notes_content)
    check("notes.md: contains confirmed_vulnerability = false", "confirmed_vulnerability = false" in notes_content)
    check("notes.md: contains formal_finding_allowed = false", "formal_finding_allowed = false" in notes_content)
    check("notes.md: contains production_safety_claimed = false", "production_safety_claimed = false" in notes_content)
    check("notes.md: contains synthetic_only = true", "synthetic_only = true" in notes_content)
    check("notes.md: references M01至M50/M01-M50", "M01" in notes_content and "M50" in notes_content)
    check("notes.md: references RED-001至RED-015/RED-001 至 RED-015", "RED-001" in notes_content and "RED-015" in notes_content)

short_notes_path = os.path.join(DOCS_DIR, "phase95a_short_notes.md")
if os.path.exists(short_notes_path):
    with open(short_notes_path, "r", encoding="utf-8") as f:
        short_content = f.read()
    check("short_notes.md: contains assessment_execution_performed: false", "assessment_execution_performed: false" in short_content)
    check("short_notes.md: contains confirmed_vulnerability: false", "confirmed_vulnerability: false" in short_content)
    check("short_notes.md: contains synthetic_only: true", "synthetic_only: true" in short_content)

# ------------------------------------------------------------
# Check 5: Results YAML Fields Validation
# ------------------------------------------------------------
if os.path.exists(result_yaml_path):
    with open(result_yaml_path, "r", encoding="utf-8") as f:
        res_data = yaml.safe_load(f)
    
    check("result.yaml: assessment_execution_performed == false", res_data.get("assessment_execution_performed") is False)
    check("result.yaml: capability_engine_executed == false", res_data.get("capability_engine_executed") is False)
    check("result.yaml: execution_results_generated == false", res_data.get("execution_results_generated") is False)
    check("result.yaml: capability_value == not_applicable", res_data.get("capability_value") == "not_applicable")
    check("result.yaml: risk_level == not_applicable", res_data.get("risk_level") == "not_applicable")
    check("result.yaml: coverage_change_claimed == false", res_data.get("coverage_change_claimed") is False)
    
    s = res_data.get("safety", {})
    check("result.yaml: confirmed_vulnerability == false", s.get("confirmed_vulnerability") is False)
    check("result.yaml: formal_finding_allowed == false", s.get("formal_finding_allowed") is False)
    check("result.yaml: production_safety_claimed == false", s.get("production_safety_claimed") is False)
    check("result.yaml: synthetic_only == true", s.get("synthetic_only") is True)

# ------------------------------------------------------------
# Check 6: Read-only Integrity & Execution Protection
# ------------------------------------------------------------
check("No execution_results.json created in docs/", not os.path.exists(os.path.join(DOCS_DIR, "execution_results.json")))
check("No capability_scorecard.yaml created in docs/", not os.path.exists(os.path.join(DOCS_DIR, "capability_scorecard.yaml")))

# Check registry clean diff
reg_diff = subprocess.run(["git", "diff", "HEAD", "--", "capability_modules/module_registry.yaml"], capture_output=True, text=True, cwd=ROOT_DIR)
check("capability_modules/module_registry.yaml unmodified", len(reg_diff.stdout.strip()) == 0)

# Summary Output
print(f"\n{'='*65}")
print(f"Phase-95A Gate Validation Summary: {P}/{P+F} CHECKS PASSED")
print(f"{'='*65}")

sys.exit(0 if F == 0 else 1)
