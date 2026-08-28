#!/usr/bin/env python3
"""TDD tests for M16 Human Approval Gate Validate Script.

RED phase: These tests define what the validate script MUST satisfy.
Run them first — they should FAIL if the script is missing or malformed.

The validate script must export a validate() function returning:
{
  "passed": int,
  "failed": int,
  "errors": list[str],
  "sections": {
    "playbook": {"passed": int, "failed": int},
    "run_config": {"passed": int, "failed": int},
    "execution_results": {"passed": int, "failed": int},
    "result_yaml": {"passed": int, "failed": int},
    "scorecard": {"passed": int, "failed": int},
    "security_fields": {"passed": int, "failed": int},
    "no_real_systems": {"passed": int, "failed": int},
  },
  "safety_booleans_all_false": bool,
  "real_flags_all_false": bool,
}
"""
import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_phase97a_m16_human_approval_gate.py"

SECTION_NAMES = [
    "playbook",
    "run_config",
    "execution_results",
    "result_yaml",
    "scorecard",
    "security_fields",
    "no_real_systems",
]


def _load_validate():
    """Dynamically import the validate script as a module."""
    spec = importlib.util.spec_from_file_location("validate_m16", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["validate_m16"] = mod
    spec.loader.exec_module(mod)
    return mod.validate()


class TestM16ValidateScript:
    def test_script_exists(self):
        assert SCRIPT_PATH.exists(), (
            f"Validate script exists at {SCRIPT_PATH}"
        )

    def test_validate_returns_dict(self):
        result = _load_validate()
        assert isinstance(result, dict), "validate() returns a dict"

    def test_validate_has_required_keys(self):
        result = _load_validate()
        required_keys = [
            "passed", "failed", "errors", "sections",
            "safety_booleans_all_false", "real_flags_all_false",
        ]
        for key in required_keys:
            assert key in result, f"Result has key '{key}'"

    def test_total_passed_is_238(self):
        result = _load_validate()
        assert result["passed"] == 238, (
            f"Total passed == 238 (got {result['passed']})"
        )

    def test_total_failed_is_0(self):
        result = _load_validate()
        assert result["failed"] == 0, (
            f"Total failed == 0 (got {result['failed']})"
        )

    def test_errors_list_empty(self):
        result = _load_validate()
        assert result["errors"] == [], (
            f"Errors list is empty (got {result['errors']})"
        )

    def test_has_all_7_sections(self):
        result = _load_validate()
        sections = result["sections"]
        assert isinstance(sections, dict), "sections is a dict"
        for name in SECTION_NAMES:
            assert name in sections, f"Section '{name}' present"

    def test_section_count_is_7(self):
        result = _load_validate()
        assert len(result["sections"]) == 7, (
            f"7 sections (got {len(result['sections'])})"
        )

    def test_each_section_has_passed_and_failed(self):
        result = _load_validate()
        for name, section in result["sections"].items():
            assert "passed" in section, f"Section '{name}' has 'passed'"
            assert "failed" in section, f"Section '{name}' has 'failed'"
            assert isinstance(section["passed"], int), (
                f"Section '{name}' passed is int"
            )
            assert isinstance(section["failed"], int), (
                f"Section '{name}' failed is int"
            )

    def test_section_passed_plus_failed_sums_to_total(self):
        result = _load_validate()
        section_sum = sum(
            s["passed"] + s["failed"]
            for s in result["sections"].values()
        )
        assert section_sum == result["passed"] + result["failed"], (
            f"Section sums ({section_sum}) == total ({result['passed'] + result['failed']})"
        )

    def test_safety_booleans_all_false(self):
        result = _load_validate()
        assert result["safety_booleans_all_false"] is True, (
            "safety_booleans_all_false == true"
        )

    def test_real_flags_all_false(self):
        result = _load_validate()
        assert result["real_flags_all_false"] is True, (
            "real_flags_all_false == true"
        )

    def test_playbook_section_has_checks(self):
        result = _load_validate()
        pb = result["sections"]["playbook"]
        assert pb["passed"] > 0, f"Playbook has > 0 passed checks"

    def test_no_real_systems_section_has_checks(self):
        result = _load_validate()
        nrs = result["sections"]["no_real_systems"]
        assert nrs["passed"] > 0, f"No_real_systems has > 0 passed checks"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
