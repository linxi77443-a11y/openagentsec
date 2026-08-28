import os
import sys
import yaml

def check_file_exists(filepath):
    if not os.path.exists(filepath):
        print(f"Missing file: {filepath}")
        return False
    return True

def validate():
    success = True
    files = [
        "src/engine/v2/control_comparison.py",
        "adversarial_playbooks/m24_control_effectiveness_mvp/playbook.yaml",
        "executions/phase111b_m24_mvp/capability_scorecard.yaml",
        "executions/phase111b_m24_mvp/execution_summary.yaml",
        "docs/phase111b_m24_control_comparison_notes.md",
        "tests/test_phase111b_ctrl005.py"
    ]
    
    for f in files:
        if not check_file_exists(f):
            success = False

    # Check playbook
    try:
        with open("adversarial_playbooks/m24_control_effectiveness_mvp/playbook.yaml", "r") as f:
            pb = yaml.safe_load(f)
            if not pb.get('groups') or len(pb['groups']) < 3:
                print("Playbook does not have at least 3 groups")
                success = False
            yaml_str = yaml.dump(pb)
            if "<SIM_API_ENDPOINT>" not in yaml_str and "<SIM_STRICT_WAF>" not in yaml_str:
                print("Playbook missing SIM placeholders")
                success = False
    except Exception as e:
        print(f"Failed to parse playbook: {e}")
        success = False

    # Check scorecard
    try:
        with open("executions/phase111b_m24_mvp/capability_scorecard.yaml", "r") as f:
            sc = yaml.safe_load(f)
            if not sc.get('requires_human_review'):
                print("Scorecard missing requires_human_review")
                success = False
            if not sc.get('all_findings_are_candidate'):
                print("Scorecard missing all_findings_are_candidate")
                success = False
    except Exception as e:
        print(f"Failed to parse scorecard: {e}")
        success = False

    # Check registry update
    try:
        with open("capability_modules/module_registry.yaml", "r") as f:
            registry = f.read()
            if "module_id: M24" not in registry or "current_status: mvp_complete" not in registry:
                print("Registry not updated correctly for M24")
                success = False
    except Exception as e:
        print(f"Failed to parse registry: {e}")
        success = False

    if success:
        print("Validation Passed")
        sys.exit(0)
    else:
        print("Validation Failed")
        sys.exit(1)

if __name__ == "__main__":
    validate()

