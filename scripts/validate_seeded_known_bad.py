"""Phase 60 — Seeded Known-bad Runtime Validator.

Verifies that the Fake Tool Runtime correctly blocks malicious tool traces.
All SKB (Seeded Known-bad) entries must result in the expected_runtime_decision.
"""
import yaml, json
from pathlib import Path
from capability_engine.fake_runtime.fake_tool_runtime import evaluate_trace

ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "capability_modules/corpora/phase60_seeded_known_bad/seeded_known_bad_corpus.yaml"

def run_skb_validation():
    print("Starting Phase 60 Seeded Known-bad Validation...")
    
    with open(CORPUS_PATH) as f:
        corpus = yaml.safe_load(f)
    
    results = []
    passed = 0
    failed = 0
    
    for entry in corpus:
        cid = entry["corpus_id"]
        expected = entry["expected_runtime_decision"]
        
        # Prepare trace input
        trace = {
            "tool_name": entry.get("requested_tool_action", ""),
            "requested_resource": entry.get("requested_resource", ""),
        }
        
        # Execute runtime check
        decision_result = evaluate_trace(
            trace_id=cid,
            current_user_role=entry.get("current_user_role", ""),
            current_tenant=entry.get("current_tenant", ""),
            current_department=entry.get("current_department", ""),
            service_account=entry.get("service_account", ""),
            service_account_scope=entry.get("service_account_scope", ""),
            trusted_context=entry.get("trusted_context", ""),
            untrusted_context=entry.get("untrusted_context", ""),
            simulated_tool_trace=trace
        )
        
        actual = decision_result["runtime_decision"]
        
        if actual == expected:
            print(f"[PASS] {cid}: Expected {expected}, Actual {actual}")
            passed += 1
        else:
            print(f"[FAIL] {cid}: Expected {expected}, Actual {actual}")
            failed += 1
            
        results.append({
            "corpus_id": cid,
            "expected": expected,
            "actual": actual,
            "pass": actual == expected
        })
        
    print("\n--- Validation Summary ---")
    print(f"Total: {len(corpus)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    # Save results
    output_dir = ROOT / "executions/phase60-seeded-known-bad-validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if failed == 0:
        print("\nALL SEEDED KNOWN-BAD CASES BLOCKED SUCCESSFULLY.")
        return True
    else:
        print("\nCRITICAL: Some malicious traces were NOT correctly blocked!")
        return False

if __name__ == "__main__":
    success = run_skb_validation()
    exit(0 if success else 1)
