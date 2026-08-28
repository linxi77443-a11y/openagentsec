#!/usr/bin/env python3
import os
import sys
import yaml
import subprocess

def check_file_exists(path):
    if not os.path.exists(path):
        print(f"ERROR: Missing file {path}")
        sys.exit(1)

def run_tests():
    print("Running tests...")
    result = subprocess.run(["pytest", "tests/test_phase111b_adapt006.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR: Tests failed.")
        print(result.stdout)
        sys.exit(1)
    print("Tests passed.")

def check_pass_rate_threshold():
    # Load playbook and execution summary to ensure rates are documented
    with open("executions/phase111b_adapt006/execution_summary.yaml", "r") as f:
        summary = yaml.safe_load(f)
    
    static_rate = summary["simulation_results"]["static_success_rate"]
    adaptive_rate = summary["simulation_results"]["adaptive_success_rate"]
    
    if adaptive_rate <= static_rate:
        print(f"ERROR: Adaptive success rate ({adaptive_rate}) should be > static success rate ({static_rate}).")
        sys.exit(1)
    
    print(f"Pass rate threshold verified. Static: {static_rate}, Adaptive: {adaptive_rate}")

def main():
    check_file_exists("src/engine/v2/adaptive_simulator.py")
    check_file_exists("adversarial_playbooks/adaptive_residual_risk_mvp/playbook.yaml")
    check_file_exists("executions/phase111b_adapt006/execution_summary.yaml")
    check_file_exists("docs/phase111b_adaptive_risk_schema.md")
    check_file_exists("tests/test_phase111b_adapt006.py")
    
    run_tests()
    check_pass_rate_threshold()
    
    print("Validation passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
