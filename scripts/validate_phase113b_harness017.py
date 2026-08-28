import os
import yaml
import sys

def main():
    checks = [
        "benchmarks/deepseek_suite/tasks_bilingual.yaml",
        "benchmarks/deepseek_suite/suite_manifest.yaml",
        "src/engine/v2/task_suite.py",
        "scripts/run_phase113b_suite_demo.py",
        "executions/phase113b_harness017/suite_report.yaml"
    ]
    
    for f in checks:
        if not os.path.exists(f):
            print(f"Missing {f}")
            sys.exit(1)
            
    with open("benchmarks/deepseek_suite/tasks_bilingual.yaml", "r", encoding="utf-8") as f:
        ds = yaml.safe_load(f)
        if len(ds.get("tasks", [])) < 40:
            print("tasks_bilingual.yaml must have >=40 entries")
            sys.exit(1)
            
    sys.exit(0)

if __name__ == "__main__":
    main()
