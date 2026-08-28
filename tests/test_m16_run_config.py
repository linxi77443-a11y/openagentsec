#!/usr/bin/env python3
"""TDD Test: M16 Human Approval Gate Run Config Structure.

RED phase: This test defines what the run_config MUST satisfy.
Run it first — it should FAIL if the run_config is missing or malformed.
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
RUN_CONFIG_PATH = ROOT / "run_configs/phase97a_m16_human_approval_gate_run_config.yaml"

checks_passed = 0
checks_failed = 0
errors = []


def check(condition, msg):
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  \u2713 {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  \u2717 {msg}")


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("TDD Test: M16 Run Config Structure")
    print("=" * 60)

    # --- File existence ---
    check(RUN_CONFIG_PATH.exists(), f"run_config.yaml exists at {RUN_CONFIG_PATH}")

    if not RUN_CONFIG_PATH.exists():
        print("\nFAILED: run_config.yaml not found — test correctly fails (RED)")
        sys.exit(1)

    # --- Load ---
    with open(RUN_CONFIG_PATH) as f:
        rc = yaml.safe_load(f)

    check(rc is not None, "run_config.yaml loads successfully")
    check("run_config" in rc, "Top-level 'run_config' key present")

    cfg = rc.get("run_config", {})

    # --- Core fields ---
    check(cfg.get("phase") == "phase97a", f"phase == 'phase97a' (got '{cfg.get('phase')}')")
    check(cfg.get("module_id") == "M16", f"module_id == 'M16' (got '{cfg.get('module_id')}')")
    check(cfg.get("assessment_mode") == "adversarial_validation",
          f"assessment_mode == 'adversarial_validation' (got '{cfg.get('assessment_mode')}')")

    # --- Corpus path references M16 playbook ---
    corpus = cfg.get("corpus_path", "")
    check("m16" in corpus.lower(), f"corpus_path references M16 playbook (got '{corpus}')")

    # --- Safety booleans ---
    check(cfg.get("confirmed_vulnerability") is False,
          "confirmed_vulnerability == false")
    check(cfg.get("formal_finding_allowed") is False,
          "formal_finding_allowed == false")
    check(cfg.get("production_safety_claimed") is False,
          "production_safety_claimed == false")

    # --- Synthetic / fake runtime flags ---
    check(cfg.get("fake_runtime_only") is True, "fake_runtime_only == true")
    check(cfg.get("synthetic_only") is True, "synthetic_only == true")
    check(cfg.get("simulated_signal_only") is True, "simulated_signal_only == true")

    # --- Output paths reference results/ directory ---
    output_dir = cfg.get("output_dir", "")
    result_path = cfg.get("result_path", "")
    scorecard_path = cfg.get("scorecard_path", "")
    exec_results_path = cfg.get("execution_results_path", "")
    check(output_dir.startswith("results"), f"output_dir starts with 'results' (got '{output_dir}')")
    check(result_path.startswith("results"), f"result_path starts with 'results' (got '{result_path}')")
    check(scorecard_path.startswith("results"), f"scorecard_path starts with 'results' (got '{scorecard_path}')")
    check(exec_results_path.startswith("results"), f"execution_results_path starts with 'results' (got '{exec_results_path}')")

    # --- Summary ---
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Run config structure verified")
    else:
        print(f"FAILED: {checks_failed} check(s) failed")
        for e in errors:
            print(f"  - {e}")
    print(f"Results: {checks_passed} passed, {checks_failed} failed")
    print("=" * 60)
    sys.exit(0 if checks_failed == 0 else 1)


if __name__ == "__main__":
    main()
