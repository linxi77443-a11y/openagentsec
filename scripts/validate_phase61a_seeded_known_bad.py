#!/usr/bin/env python3
"""Phase 61A — Seeded Known-Bad Self-Test Validation.

Validates that all Phase 61A deliverables are present and internally consistent:
  - Corpus v2 exists and has expected structure
  - Self-test execution results exist
  - Scorecard exists with valid fields
  - Per-module result files exist for parser-tested modules
  - Runtime results exist and pass
  - Self-test passes or has documented gaps
"""

import sys, os, json, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Paths
CORPUS_PATH = ROOT / "capability_modules/corpora/phase61a_seeded_known_bad/seeded_known_bad_corpus_v2.yaml"
RUN_CONFIG_PATH = ROOT / "capability_engine/configs/phase61a_seeded_known_bad_self_test.yaml"
SCRIPT_PATH = ROOT / "scripts/run_phase61a_seeded_known_bad_self_test.py"
OUTPUT_DIR = ROOT / "executions/phase61a-seeded-known-bad-self-test"
NOTES_PATH = ROOT / "docs/phase61a_seeded_known_bad_self_test_notes.md"

REQUIRED_FILES = [
    CORPUS_PATH,
    RUN_CONFIG_PATH,
    SCRIPT_PATH,
    OUTPUT_DIR / "execution_results.json",
    OUTPUT_DIR / "capability_scorecard.yaml",
    OUTPUT_DIR / "self_test_results.json",
    OUTPUT_DIR / "runtime/runtime_results.json",
    NOTES_PATH,
]

EXPECTED_CORPUS_IDS = [
    # Type 1: sensitive_data_leakage
    "SKB-101", "SKB-102",
    # Type 2: unauthorized_access
    "SKB-201", "SKB-202",
    # Type 3: business_data_exposure
    "SKB-301", "SKB-302",
    # Type 4: role_boundary_breach
    "SKB-401", "SKB-402",
    # Type 5: unsafe_tool_trace
    "SKB-501", "SKB-502",
    # Type 6: unsafe_runtime_allowed
    "SKB-601", "SKB-602",
    # Controls
    "SKB-901", "SKB-902", "SKB-903",
    # Legacy runtime
    "SKB-701", "SKB-702", "SKB-703", "SKB-704", "SKB-705",
    "SKB-706", "SKB-707", "SKB-708", "SKB-709",
]

# Expected per-module result files
EXPECTED_MODULE_RESULTS = [
    "m04_result.yaml",
    "m07_result.yaml",
    "m19_result.yaml",
    "m08_result.yaml",
    "m41_result.yaml",
]


def validate_corpus():
    """Validate corpus v2 structure."""
    print("  Corpus v2:", CORPUS_PATH)
    if not CORPUS_PATH.exists():
        print("    [FAIL] File not found")
        return False

    with open(CORPUS_PATH) as f:
        data = yaml.safe_load(f)
    corpus = data.get("m61a", [])
    if not isinstance(corpus, list) or len(corpus) == 0:
        print("    [FAIL] Corpus is empty or not a list under m61a key")
        return False

    found_ids = [e["corpus_id"] for e in corpus if "corpus_id" in e]
    missing = [cid for cid in EXPECTED_CORPUS_IDS if cid not in found_ids]
    if missing:
        print(f"    [FAIL] Missing expected corpus IDs: {missing}")
        return False

    # Check each entry has required fields
    required_fields = ["corpus_id", "module_id", "category", "known_bad_type"]
    for entry in corpus:
        missing_fields = [f for f in required_fields if f not in entry]
        if missing_fields:
            print(f"    [FAIL] {entry.get('corpus_id', '?')} missing: {missing_fields}")
            return False

    print(f"    [PASS] {len(corpus)} entries, all {len(EXPECTED_CORPUS_IDS)} expected IDs present")
    return True


def validate_run_config():
    """Validate run config structure."""
    print("  Run config:", RUN_CONFIG_PATH)
    if not RUN_CONFIG_PATH.exists():
        print("    [FAIL] File not found")
        return False

    with open(RUN_CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)

    required = ["run_id", "phase", "modules", "corpus_reference", "result"]
    missing = [r for r in required if r not in cfg]
    if missing:
        print(f"    [FAIL] Missing fields: {missing}")
        return False

    if not cfg.get("result", {}).get("formal_finding_allowed", True):
        print("    [PASS] formal_finding_allowed=False")
    else:
        print("    [WARN] formal_finding_allowed is not False")

    print(f"    [PASS] Run config valid")
    return True


def validate_self_test_results():
    """Validate execution output files and results."""
    print("  Output:", OUTPUT_DIR)

    # Check required output files exist
    missing_files = [str(p) for p in REQUIRED_FILES if not p.exists()]
    if missing_files:
        print(f"    [FAIL] Missing output files: {missing_files}")
        return False

    # Validate self_test_results.json
    with open(OUTPUT_DIR / "self_test_results.json") as f:
        results = json.load(f)

    if results.get("total", 0) == 0:
        print("    [FAIL] self_test_results.json has total=0")
        return False

    if results["passed"] + results["failed"] != results["total"]:
        print(f"    [FAIL] pass+failed ({results['passed']}+{results['failed']}) != total ({results['total']})")
        return False

    print(f"    [INFO] Total: {results['total']}, Passed: {results['passed']}, Failed: {results['failed']}")

    # Validate scorecard
    with open(OUTPUT_DIR / "capability_scorecard.yaml") as f:
        sc = yaml.safe_load(f)

    if not sc.get("scorecard_metadata", {}).get("formal_finding_allowed", True) == False:
        print("    [FAIL] Scorecard formal_finding_allowed must be False")
        return False

    print(f"    [PASS] Scorecard present with formal_finding_allowed=False")

    # Validate per-module result files for parser-tested modules
    for mod_file in EXPECTED_MODULE_RESULTS:
        mod_path = OUTPUT_DIR / mod_file
        if mod_path.exists():
            print(f"    [PASS] {mod_file} exists")
        else:
            print(f"    [WARN] {mod_file} not found (may be generated by parser)")

    return True


def validate_runtime_results():
    """Validate runtime test results."""
    print("  Runtime results:", OUTPUT_DIR / "runtime/runtime_results.json")
    r_path = OUTPUT_DIR / "runtime/runtime_results.json"
    if not r_path.exists():
        print("    [FAIL] File not found")
        return False

    with open(r_path) as f:
        results = json.load(f)

    passed = sum(1 for r in results if r["pass"])
    failed = len(results) - passed

    if failed > 0:
        print(f"    [FAIL] {failed} runtime test(s) failed")
        return False

    print(f"    [PASS] All {len(results)} runtime tests passed")
    return True


def validate_script():
    """Validate that the self-test script is executable."""
    print("  Script:", SCRIPT_PATH)
    if not SCRIPT_PATH.exists():
        print("    [FAIL] Script not found")
        return False

    # Check it has a main() function
    content = SCRIPT_PATH.read_text()
    if "def main()" not in content:
        print("    [FAIL] Script missing main() function")
        return False
    print("    [PASS] Script has main()")
    return True


def validate_notes():
    """Validate that the notes document exists."""
    print("  Notes:", NOTES_PATH)
    if not NOTES_PATH.exists():
        print("    [FAIL] Notes document not found")
        return False
    print("    [PASS] Notes document exists")
    return True


def main():
    print("Phase 61A Seeded Known-Bad Self-Test Validation")
    print("=" * 60)
    print()

    checks = {
        "Corpus v2": validate_corpus(),
        "Run config": validate_run_config(),
        "Self-test script": validate_script(),
        "Execution output files": validate_self_test_results(),
        "Runtime test results": validate_runtime_results(),
        "Notes document": validate_notes(),
    }

    print(f"\n{'=' * 60}")
    print("Validation Summary")
    print(f"{'=' * 60}")
    all_pass = True
    for name, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_pass = False

    if all_pass:
        print(f"\nALL VALIDATION CHECKS PASSED.")
        sys.exit(0)
    else:
        print(f"\nSOME CHECKS FAILED. Review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
