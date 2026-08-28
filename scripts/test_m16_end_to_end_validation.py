#!/usr/bin/env python3
"""TDD test for M16 Human Approval Gate Validation — end-to-end validation.

This test verifies the acceptance criteria for T8:
1. validate script passes 238/238
2. All 7 deliverable files exist
3. No real system references across deliverables
"""
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# All 7 deliverable files that must exist
DELIVERABLE_FILES = [
    ROOT / "adversarial_playbooks/m16_human_approval_gate_mvp/playbook.yaml",
    ROOT / "run_configs/phase97a_m16_human_approval_gate_run_config.yaml",
    ROOT / "results/phase97a_m16_human_approval_gate_execution_results.json",
    ROOT / "results/phase97a_m16_human_approval_gate_result.yaml",
    ROOT / "results/phase97a_m16_human_approval_gate_capability_scorecard.yaml",
    ROOT / "scripts/validate_phase97a_m16_human_approval_gate.py",
    ROOT / "docs/phase97a_m16_human_approval_gate_mvp_notes.md",
]

# Strings that must NOT appear as "true" in any deliverable
REAL_SYSTEM_FALSE_MARKERS = [
    "real_approval_system_connected: true",
    "real_tool_executed: true",
    "real_api_called: true",
]

# JSON false patterns
REAL_SYSTEM_FALSE_JSON = [
    '"real_approval_system_connected": true',
    '"real_tool_executed": true',
    '"real_api_called": true',
]


def test_all_deliverable_files_exist():
    """Verify all 7 deliverable files exist on disk."""
    missing = []
    for f in DELIVERABLE_FILES:
        if not f.exists():
            missing.append(str(f))
    assert not missing, f"Missing deliverable files: {missing}"


def test_validate_script_passes_238():
    """Run the validate script and verify 238/238 checks pass."""
    script = ROOT / "scripts/validate_phase97a_m16_human_approval_gate.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    output = result.stdout + result.stderr
    # Check exit code
    assert result.returncode == 0, (
        f"Validate script failed with exit code {result.returncode}.\n"
        f"Output:\n{output}"
    )
    # Check for "238 passed" in output
    assert "238 passed" in output, (
        f"Expected '238 passed' in validate output.\n"
        f"Output:\n{output}"
    )
    # Check no failures
    assert "0 failed" in output, (
        f"Expected '0 failed' in validate output.\n"
        f"Output:\n{output}"
    )


def test_no_real_system_references():
    """Verify no deliverable data file contains real system references as true.

    Excludes the validate script itself — it contains these strings as part
    of its negative assertion checks (verifying they are NOT present).
    """
    # Only check data deliverables, not the validator script
    data_deliverables = [f for f in DELIVERABLE_FILES
                         if "validate" not in f.name]
    violations = []
    for f in data_deliverables:
        if not f.exists():
            continue
        content = f.read_text()
        for marker in REAL_SYSTEM_FALSE_MARKERS:
            if marker in content:
                violations.append(f"{f.name}: {marker}")
        for marker in REAL_SYSTEM_FALSE_JSON:
            if marker in content:
                violations.append(f"{f.name}: {marker}")
    assert not violations, (
        f"Real system references found as 'true':\n" +
        "\n".join(f"  - {v}" for v in violations)
    )


def test_registry_m16_mvp_complete():
    """Verify M16 registry entry shows mvp_complete status."""
    import yaml
    registry_path = ROOT / "capability_modules/module_registry.yaml"
    assert registry_path.exists(), "module_registry.yaml not found"
    with open(registry_path) as f:
        reg = yaml.safe_load(f)
    m16_entries = [m for m in reg["modules"] if m["module_id"] == "M16"]
    assert len(m16_entries) == 1, f"Expected 1 M16 entry, got {len(m16_entries)}"
    m16 = m16_entries[0]
    assert m16["current_status"] == "mvp_complete", (
        f"M16 current_status is '{m16['current_status']}', expected 'mvp_complete'"
    )
    assert m16["coverage"]["coverage_status"] == "mvp_complete", (
        f"M16 coverage_status is '{m16['coverage']['coverage_status']}', expected 'mvp_complete'"
    )
    assert m16["coverage"]["implementation_status"] == "mvp_done", (
        f"M16 implementation_status is '{m16['coverage']['implementation_status']}', expected 'mvp_done'"
    )
    assert len(m16["coverage"]["evidence"]) >= 7, (
        f"M16 evidence has {len(m16['coverage']['evidence'])} items, expected >= 7"
    )


if __name__ == "__main__":
    passed = 0
    failed = 0
    errors = []

    tests = [
        ("All 7 deliverable files exist", test_all_deliverable_files_exist),
        ("Validate script passes 238/238", test_validate_script_passes_238),
        ("No real system references in deliverables", test_no_real_system_references),
        ("M16 registry entry is mvp_complete", test_registry_m16_mvp_complete),
    ]

    for name, test_fn in tests:
        print(f"\nTest: {name}")
        try:
            test_fn()
            print(f"  PASS")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
            errors.append(f"{name}: {e}")
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
            errors.append(f"{name}: {e}")

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    if errors:
        print("\nFailed:")
        for e in errors:
            print(f"  - {e}")
    print(f"{'=' * 60}")
    sys.exit(0 if failed == 0 else 1)
