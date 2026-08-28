"""Phase 60 — Parser Gold Set Regression Validator.

Ensures that the tool trace extraction logic remains stable across code changes.
Asserts that extracted signals match the predefined gold labels.
"""
import yaml, json
from pathlib import Path
from capability_engine.fake_runtime.tool_trace_extractor import parse_model_response, extract_tool_trace

ROOT = Path(__file__).resolve().parents[1]
GOLD_SET_PATH = ROOT / "capability_engine/parsers/gold_set_regression.yaml"

def run_parser_regression():
    print("Starting Parser Gold Set Regression Validation...")
    
    with open(GOLD_SET_PATH) as f:
        gold_set = yaml.safe_load(f)
        
    passed = 0
    failed = 0
    results = []
    
    for sample in gold_set:
        sid = sample["sample_id"]
        raw = sample["raw_content"]
        expected_signals = sample["expected_signals"]
        
        # 1. Parse JSON
        parsed_json = parse_model_response(raw)
        
        # 2. Extract signals
        # If parse failed but expected no_trace_refusal (like timeout), we mock a failed parse
        if parsed_json is None:
            extraction = {"extraction_status": "no_trace_refusal"}
        else:
            extraction = extract_tool_trace(parsed_json, {})
            
        actual_signals = []
        if extraction["extraction_status"] == "no_trace_refusal":
            actual_signals.append("no_trace_refusal")
            # Heuristic for rejected based on tool_trace_extractor logic
            if extraction.get("rationale_type") == "rejected" or extraction.get("model_decision") == "reject":
                actual_signals.append("rejected")
        elif extraction["extraction_status"] == "trace_extracted":
            actual_signals.append("trace_extracted")
            if extraction.get("model_allowed"):
                actual_signals.append("model_allowed")
        
        # Match check
        is_match = all(sig in actual_signals for sig in expected_signals)
        
        if is_match:
            print(f"[PASS] {sid}: Signals match {expected_signals}")
            passed += 1
        else:
            print(f"[FAIL] {sid}: Expected {expected_signals}, Actual {actual_signals}")
            failed += 1
            
        results.append({
            "sample_id": sid,
            "expected": expected_signals,
            "actual": actual_signals,
            "pass": is_match
        })
        
    print("\n--- Regression Summary ---")
    print(f"Total: {len(gold_set)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\nPARSER REGRESSION VALIDATION PASSED.")
        return True
    else:
        print("\nCRITICAL: Parser logic has REGRESSED on gold samples!")
        return False

if __name__ == "__main__":
    success = run_parser_regression()
    exit(0 if success else 1)
