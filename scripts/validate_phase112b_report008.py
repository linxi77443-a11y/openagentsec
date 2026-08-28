import sys
import os

def check_files_exist():
    files_to_check = [
        "src/engine/v2/report_generator.py",
        "tests/test_phase112b_report008.py",
        "executions/phase112b_report008/sample_full_report.md",
        "executions/phase112b_report008/sample_full_report.json"
    ]
    
    for f in files_to_check:
        if not os.path.exists(f):
            print(f"Error: Required file missing: {f}")
            sys.exit(1)

def check_md_report_content():
    with open("executions/phase112b_report008/sample_full_report.md", "r") as f:
        content = f.read()
        
    required_strings = [
        "SIMULATION DECLARATION:",
        "SAFETY INVARIANTS DECLARATION",
        "confirmed_vulnerability: False",
        "ADAPTIVE RESIDUAL RISK DECLARATION",
        "Status: candidate",
        "Requires Human Review: true",
        "Synthetic Only: true"
    ]
    
    for s in required_strings:
        if s not in content:
            print(f"Error: Missing required string in MD report: {s}")
            sys.exit(1)

def check_json_report_content():
    import json
    with open("executions/phase112b_report008/sample_full_report.json", "r") as f:
        data = json.load(f)
        
    if data.get("findings_status") != "candidate":
        print("Error: JSON findings_status is not 'candidate'")
        sys.exit(1)
        
    if data.get("requires_human_review") is not True:
        print("Error: JSON requires_human_review is not True")
        sys.exit(1)

def main():
    check_files_exist()
    check_md_report_content()
    check_json_report_content()
    print("All validations passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()

