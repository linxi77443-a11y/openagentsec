import os
import sys
import py_compile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def validate_imports():
    print("Validating imports...")
    try:
        from src.engine.v2 import ENGINE_VERSION
        from src.engine.v2.safety_invariants import assert_safety_invariants
        from src.engine.v2.converter import Base64Converter
        from src.engine.v2.orchestrator import SingleTurnStrategy
        from src.engine.v2.scorer import BooleanScorer
        from src.engine.v2.memory import JsonlMemory
        from src.engine.v2.task_metadata import load_task_metadata
        from src.engine.v2.run_spec import parse_run_spec
        print("Imports validated.")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False

def validate_safety_invariants():
    print("Validating safety invariants assertion...")
    try:
        from src.engine.v2.safety_invariants import assert_safety_invariants, SAFETY_INVARIANTS
        assert_safety_invariants()
        print("Safety invariants assertion validated.")
        return True
    except Exception as e:
        print(f"Safety invariant assertion failed: {e}")
        return False

def validate_trace_tuple():
    print("Validating trace tuple...")
    import json
    trace_path = os.path.join(os.path.dirname(__file__), '..', 'executions', 'phase110b_engine003', 'trace.jsonl')
    if not os.path.exists(trace_path):
        print(f"Trace file not found at {trace_path}")
        return False
    
    with open(trace_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            required_keys = ["engine_version", "task_id", "atlas_technique_id", "intent"]
            for k in required_keys:
                if k not in record or not record[k]:
                    print(f"Missing required key in trace record: {k}")
                    return False
    print("Trace tuple validated.")
    return True

def validate_py_compile():
    print("Validating py_compile...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    files_to_compile = [
        "src/engine/v2/__init__.py",
        "src/engine/v2/safety_invariants.py",
        "src/engine/v2/converter.py",
        "src/engine/v2/orchestrator.py",
        "src/engine/v2/scorer.py",
        "src/engine/v2/memory.py",
        "src/engine/v2/task_metadata.py",
        "src/engine/v2/run_spec.py",
        "scripts/run_phase110b_engine003_demo.py",
        "tests/test_phase110b_engine_v2.py"
    ]
    
    for f in files_to_compile:
        full_path = os.path.join(base_dir, f)
        try:
            py_compile.compile(full_path, doraise=True)
            print(f"Compiled {f}")
        except Exception as e:
            print(f"Failed to compile {f}: {e}")
            return False
    print("py_compile validated.")
    return True

def main():
    if not validate_imports():
        sys.exit(1)
    if not validate_safety_invariants():
        sys.exit(1)
    if not validate_trace_tuple():
        sys.exit(1)
    if not validate_py_compile():
        sys.exit(1)
    
    print("All validations passed.")

if __name__ == "__main__":
    main()
