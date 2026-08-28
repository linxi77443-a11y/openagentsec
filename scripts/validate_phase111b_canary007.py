import os
import sys
import yaml

def validate():
    required_files = [
        "src/engine/v2/canary.py",
        "adversarial_playbooks/canary_judgment_mvp/playbook.yaml",
        "executions/phase111b_canary007/execution_summary.yaml",
        "tests/test_phase111b_canary007.py"
    ]
    for file in required_files:
        if not os.path.exists(file):
            print(f"Missing file: {file}")
            sys.exit(1)
            
    # Check playbook
    with open("adversarial_playbooks/canary_judgment_mvp/playbook.yaml") as f:
        data = yaml.safe_load(f)
        scenarios = data.get("scenarios", [])
        if len(scenarios) < 10:
            print("Playbook needs at least 10 scenarios")
            sys.exit(1)
            
    print("Validation passed!")
    sys.exit(0)

if __name__ == "__main__":
    validate()
