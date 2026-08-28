#!/usr/bin/env python3
"""Tests for validate_phase97a_m16_human_approval_gate.py

TDD: These tests verify the validate script produces correct output.
"""
import subprocess
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATE_SCRIPT = ROOT / "scripts" / "validate_phase97a_m16_human_approval_gate.py"

# Compact output format: section names appear as "<name>: <N> passed, <M> failed"
EXPECTED_SECTIONS = [
    "playbook",
    "run_config",
    "execution_results",
    "result_yaml",
    "scorecard",
    "security_fields",
    "no_real_systems",
]

REQUIRED_SAFETY_BOOLEANS = [
    "confirmed_vulnerability: false",
    "formal_finding_allowed: false",
    "production_safety_claimed: false",
]


def run_validate():
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    return result


def test_script_exists():
    assert VALIDATE_SCRIPT.exists(), f"Validate script not found: {VALIDATE_SCRIPT}"


def test_script_exits_zero():
    result = run_validate()
    assert result.returncode == 0, (
        f"Script exited with code {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_238_passed_0_failed():
    result = run_validate()
    match = re.search(r"Results:\s+(\d+)\s+passed,\s+(\d+)\s+failed", result.stdout)
    assert match, f"Could not find results summary in output:\n{result.stdout}"
    passed, failed = int(match.group(1)), int(match.group(2))
    assert passed == 238, f"Expected 238 passed, got {passed}"
    assert failed == 0, f"Expected 0 failed, got {failed}"


def test_all_7_sections_present():
    result = run_validate()
    for section in EXPECTED_SECTIONS:
        assert re.search(rf"^{re.escape(section)}:\s+\d+ passed", result.stdout, re.MULTILINE), (
            f"Missing section: {section}"
        )


def test_playbook_section_checks():
    result = run_validate()
    match = re.search(r"^playbook:\s+(\d+) passed,\s+(\d+) failed", result.stdout, re.MULTILINE)
    assert match, f"Missing playbook section in output:\n{result.stdout}"
    passed, failed = int(match.group(1)), int(match.group(2))
    assert passed == 77, f"Expected playbook 77 passed, got {passed}"
    assert failed == 0, f"Expected playbook 0 failed, got {failed}"


def test_run_config_section_checks():
    result = run_validate()
    match = re.search(r"^run_config:\s+(\d+) passed,\s+(\d+) failed", result.stdout, re.MULTILINE)
    assert match, f"Missing run_config section in output:\n{result.stdout}"
    passed, failed = int(match.group(1)), int(match.group(2))
    assert passed == 11, f"Expected run_config 11 passed, got {passed}"
    assert failed == 0, f"Expected run_config 0 failed, got {failed}"


def test_execution_results_section_checks():
    result = run_validate()
    match = re.search(r"^execution_results:\s+(\d+) passed,\s+(\d+) failed", result.stdout, re.MULTILINE)
    assert match, f"Missing execution_results section in output:\n{result.stdout}"
    passed, failed = int(match.group(1)), int(match.group(2))
    assert passed == 84, f"Expected execution_results 84 passed, got {passed}"
    assert failed == 0, f"Expected execution_results 0 failed, got {failed}"


def test_result_yaml_section_checks():
    result = run_validate()
    match = re.search(r"^result_yaml:\s+(\d+) passed,\s+(\d+) failed", result.stdout, re.MULTILINE)
    assert match, f"Missing result_yaml section in output:\n{result.stdout}"
    passed, failed = int(match.group(1)), int(match.group(2))
    assert passed >= 21, f"Expected result_yaml >= 21 passed, got {passed}"
    assert failed == 0, f"Expected result_yaml 0 failed, got {failed}"


def test_scorecard_section_checks():
    result = run_validate()
    match = re.search(r"^scorecard:\s+(\d+) passed,\s+(\d+) failed", result.stdout, re.MULTILINE)
    assert match, f"Missing scorecard section in output:\n{result.stdout}"
    passed, failed = int(match.group(1)), int(match.group(2))
    assert passed == 11, f"Expected scorecard 11 passed, got {passed}"
    assert failed == 0, f"Expected scorecard 0 failed, got {failed}"


def test_security_fields_section_checks():
    result = run_validate()
    match = re.search(r"^security_fields:\s+(\d+) passed,\s+(\d+) failed", result.stdout, re.MULTILINE)
    assert match, f"Missing security_fields section in output:\n{result.stdout}"
    passed, failed = int(match.group(1)), int(match.group(2))
    assert passed == 15, f"Expected security_fields 15 passed, got {passed}"
    assert failed == 0, f"Expected security_fields 0 failed, got {failed}"


def test_no_real_system_artifacts_section():
    result = run_validate()
    match = re.search(r"^no_real_systems:\s+(\d+) passed,\s+(\d+) failed", result.stdout, re.MULTILINE)
    assert match, f"Missing no_real_systems section in output:\n{result.stdout}"
    passed, failed = int(match.group(1)), int(match.group(2))
    assert passed == 15, f"Expected no_real_systems 15 passed, got {passed}"
    assert failed == 0, f"Expected no_real_systems 0 failed, got {failed}"


def test_no_failed_checks_in_output():
    result = run_validate()
    assert "\u2717" not in result.stdout, f"Found failure markers in output:\n{result.stdout}"


def test_no_error_output():
    result = run_validate()
    assert "Failed checks:" not in result.stdout, f"Found 'Failed checks:' in output"


def test_no_stderr():
    result = run_validate()
    assert result.stderr == "", f"Unexpected stderr: {result.stderr}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
