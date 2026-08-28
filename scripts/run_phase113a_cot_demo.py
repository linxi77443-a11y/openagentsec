import yaml
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from src.engine.v2.cot_analyzer import analyze_cot

def run_demo():
    samples_file = "adversarial_playbooks/cot_reasoning_abnormality_mvp/cot_samples.yaml"
    with open(samples_file, "r") as f:
        data = yaml.safe_load(f)
        
    results = []
    
    for sample in data.get("samples", []):
        sample_id = sample.get("sample_id")
        raw_output = sample.get("raw_output")
        expected_findings = sample.get("expected_findings", [])
        
        analysis = analyze_cot(raw_output)
        actual_findings = [f.category for f in analysis["findings"]]
        
        # very naive evaluation
        precision = 1.0 if actual_findings == expected_findings or (not expected_findings and not actual_findings) else 0.0
        recall = 1.0 if all(cat in actual_findings for cat in expected_findings) else 0.0
        
        results.append({
            "sample_id": sample_id,
            "expected_findings": expected_findings,
            "actual_findings": actual_findings,
            "precision": precision,
            "recall": recall
        })
        
    report = {
        "summary": {
            "total_samples": len(results),
            "avg_precision": sum(r["precision"] for r in results) / max(1, len(results)),
            "avg_recall": sum(r["recall"] for r in results) / max(1, len(results))
        },
        "results": results
    }
    
    os.makedirs("executions/phase113a_cot012", exist_ok=True)
    with open("executions/phase113a_cot012/analysis_report.yaml", "w") as f:
        yaml.dump(report, f, default_flow_style=False)
        
if __name__ == "__main__":
    run_demo()
