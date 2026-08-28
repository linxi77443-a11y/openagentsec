import os
import sys
import glob
import subprocess
import datetime
import re

def run_gate():
    report = {}
    report['execution_date'] = datetime.datetime.now().isoformat()
    
    print("Running pytest...")
    # Using .venv interpreter as requested
    pytest_cmd = [".venv/bin/python", "-m", "pytest", "tests/", "-q"]
    proc = subprocess.run(pytest_cmd, capture_output=True, text=True)
    
    output = proc.stdout + "\n" + proc.stderr
    
    failed_count = 0
    skipped_count = 0
    passed_count = 0
    
    fail_match = re.search(r'(\d+)\s+failed', output)
    if fail_match: failed_count += int(fail_match.group(1))
    
    error_match = re.search(r'(\d+)\s+errors', output)
    if error_match: failed_count += int(error_match.group(1))
    
    skip_match = re.search(r'(\d+)\s+skipped', output)
    if skip_match: skipped_count = int(skip_match.group(1))
    
    pass_match = re.search(r'(\d+)\s+passed', output)
    if pass_match: passed_count = int(pass_match.group(1))
    
    # [Phase-113C gate-recovery 2026-08-20] Strict pytest evaluation
    pytest_pass = (failed_count == 0 and proc.returncode == 0)
    
    report['pytest_results'] = {
        'passed': pytest_pass,
        'failed_count': failed_count,
        'skipped_count': skipped_count,
        'passed_count': passed_count,
        'returncode': proc.returncode
    }
    
    print(f"Pytest result: PASS={pytest_pass}, FAILED={failed_count}")
    
    validators = glob.glob("scripts/validate_*.py")
    # exclude self
    validators = [v for v in validators if os.path.basename(v) != "validate_full_regression_gate.py"]
    
    val_total = len(validators)
    val_passed = 0
    val_failed = 0
    
    third_party = ["yaml", "pytest", "requests", "pydantic", "jsonschema"]
    
    for val in validators:
        needs_venv = False
        try:
            with open(val, "r", encoding="utf-8") as f:
                content = f.read()
                for pkg in third_party:
                    if re.search(rf'^(?:import|from)\s+{pkg}\b', content, re.MULTILINE):
                        needs_venv = True
                        break
        except Exception:
            pass
            
        py_bin = ".venv/bin/python" if needs_venv else "python3"
        print(f"Running {val} with {py_bin}...")
        v_proc = subprocess.run([py_bin, val], capture_output=True)
        if v_proc.returncode == 0:
            val_passed += 1
        else:
            val_failed += 1
            print(f"FAILED: {val}")
            
    report['validators_results'] = {
        'total': val_total,
        'passed': val_passed,
        'failed': val_failed
    }
    
    overall = "PASS" if (pytest_pass and val_failed == 0) else "FAIL"
    report['overall_status'] = overall
    
    yaml_content = f"""execution_date: '{report['execution_date']}'
overall_status: '{overall}'
pytest_results:
  passed: {'true' if pytest_pass else 'false'}
  failed_count: {failed_count}
  skipped_count: {skipped_count}
  passed_count: {passed_count}
validators_results:
  total: {val_total}
  passed: {val_passed}
  failed: {val_failed}
"""
    os.makedirs("executions/phase113b_regress015", exist_ok=True)
    with open("executions/phase113b_regress015/regression_gate_report.yaml", "w", encoding="utf-8") as f:
        f.write(yaml_content)
        
    print(f"Gate evaluation finished. Overall status: {overall}")
    if overall == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_gate()
