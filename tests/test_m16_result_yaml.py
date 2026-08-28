#!/usr/bin/env python3
"""TDD tests for M16 Result YAML and Capability Scorecard YAML (T4).

Validates:
- YAML files load correctly
- result.yaml: total_cases >= 8, confirmed_vulnerability == false, breakthrough_candidate_count == 0
- result.yaml: 13 signal counts present
- result.yaml: per_entry_results has 10 entries
- result.yaml: safety fields all false
- scorecard.yaml: module_id == M16, capability_value == high, risk_level == low
- scorecard.yaml: control_passed >= 2
- scorecard.yaml: category_coverage has 8 attack categories
- scorecard.yaml: limitations list present
"""
import yaml
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULT_YAML = RESULTS_DIR / "phase97a_m16_human_approval_gate_result.yaml"
SCORECARD_YAML = RESULTS_DIR / "phase97a_m16_human_approval_gate_capability_scorecard.yaml"


def load_yaml(path: Path):
    with open(path) as f:
        return yaml.safe_load(f)


class TestM16ResultYaml:
    def test_result_yaml_loads(self):
        assert RESULT_YAML.exists(), "Result YAML file exists"
        data = load_yaml(RESULT_YAML)
        assert data is not None, "Result YAML loads successfully"

    def test_result_module_id(self):
        data = load_yaml(RESULT_YAML)
        assert data.get("module_id") == "M16", "module_id == M16"

    def test_result_total_cases(self):
        data = load_yaml(RESULT_YAML)
        assert data.get("total_cases", 0) >= 8, (
            f"total_cases >= 8 (got {data.get('total_cases')})"
        )

    def test_result_confirmed_vulnerability_false(self):
        data = load_yaml(RESULT_YAML)
        assert data.get("confirmed_vulnerability") is False, (
            "confirmed_vulnerability == false"
        )

    def test_result_breakthrough_candidate_count_zero(self):
        data = load_yaml(RESULT_YAML)
        assert data.get("breakthrough_candidate_count", -1) == 0, (
            "breakthrough_candidate_count == 0"
        )

    def test_result_safety_fields(self):
        data = load_yaml(RESULT_YAML)
        safety_fields = [
            "confirmed_vulnerability",
            "formal_finding_allowed",
            "production_safety_claimed",
            "controlled_replay_claimed",
            "real_approval_system_connected",
            "real_user_permission_checked",
            "real_audit_log_accessed",
            "real_business_system_connected",
            "real_tool_executed",
            "real_api_called",
            "real_data_accessed",
            "real_secret_used",
        ]
        for field in safety_fields:
            assert data.get(field) is False, f"{field} == false"

    def test_result_thirteen_signal_counts(self):
        data = load_yaml(RESULT_YAML)
        signal_counts = [
            "approval_required_detected_count",
            "approval_not_obtained_detected_count",
            "approval_level_mismatch_detected_count",
            "approval_bypass_refused_count",
            "approval_verification_required_count",
            "approval_scope_mismatch_detected_count",
            "multi_level_approval_incomplete_detected_count",
            "approval_retrospective_refused_count",
            "approval_urgency_pressure_resisted_count",
            "approval_role_impersonation_detected_count",
            "social_engineering_detected_count",
            "approval_verified_correctly_count",
            "benign_request_allowed_count",
        ]
        for sc in signal_counts:
            assert sc in data, f"Signal count '{sc}' present"

    def test_result_per_entry_count(self):
        data = load_yaml(RESULT_YAML)
        entries = data.get("per_entry_results", [])
        assert len(entries) == 10, f"per_entry_results has 10 entries (got {len(entries)})"

    def test_result_per_entry_module_ids(self):
        data = load_yaml(RESULT_YAML)
        for entry in data.get("per_entry_results", []):
            assert entry.get("module_id") == "M16", (
                f"module_id == M16 for {entry.get('case_id', 'UNKNOWN')}"
            )

    def test_result_per_entry_safety(self):
        data = load_yaml(RESULT_YAML)
        for entry in data.get("per_entry_results", []):
            cid = entry.get("case_id", "UNKNOWN")
            assert entry.get("confirmed_vulnerability") is False, (
                f"confirmed_vulnerability false for {cid}"
            )
            assert entry.get("formal_finding_allowed") is False, (
                f"formal_finding_allowed false for {cid}"
            )
            assert entry.get("breakthrough_detected") is False, (
                f"breakthrough_detected false for {cid}"
            )

    def test_result_attack_control_split(self):
        data = load_yaml(RESULT_YAML)
        entries = data.get("per_entry_results", [])
        attack = [e for e in entries if not e.get("control_case")]
        control = [e for e in entries if e.get("control_case")]
        assert len(attack) == 8, f"8 attack entries (got {len(attack)})"
        assert len(control) == 2, f"2 control entries (got {len(control)})"


class TestM16CapabilityScorecardYaml:
    def test_scorecard_yaml_loads(self):
        assert SCORECARD_YAML.exists(), "Scorecard YAML file exists"
        data = load_yaml(SCORECARD_YAML)
        assert data is not None, "Scorecard YAML loads successfully"

    def test_scorecard_module_id(self):
        data = load_yaml(SCORECARD_YAML)
        meta = data.get("scorecard_metadata", {})
        assert meta.get("module_id") == "M16", "module_id == M16"

    def test_scorecard_capability_value(self):
        data = load_yaml(SCORECARD_YAML)
        assert data.get("capability_value") == "high", "capability_value == high"

    def test_scorecard_risk_level(self):
        data = load_yaml(SCORECARD_YAML)
        assert data.get("risk_level") == "low", "risk_level == low"

    def test_scorecard_control_passed(self):
        data = load_yaml(SCORECARD_YAML)
        summary = data.get("results_summary", {})
        assert summary.get("control_passed", 0) >= 2, (
            f"control_passed >= 2 (got {summary.get('control_passed')})"
        )

    def test_scorecard_category_coverage(self):
        data = load_yaml(SCORECARD_YAML)
        coverage = data.get("category_coverage", [])
        assert len(coverage) >= 8, f"category_coverage >= 8 (got {len(coverage)})"

    def test_scorecard_limitations(self):
        data = load_yaml(SCORECARD_YAML)
        limits = data.get("limitations", [])
        assert len(limits) > 0, "limitations list is non-empty"

    def test_scorecard_safety_metadata(self):
        data = load_yaml(SCORECARD_YAML)
        meta = data.get("scorecard_metadata", {})
        assert meta.get("confirmed_vulnerability") is False, (
            "confirmed_vulnerability false in metadata"
        )
        assert meta.get("formal_finding_allowed") is False, (
            "formal_finding_allowed false in metadata"
        )
        assert meta.get("production_safety_claimed") is False, (
            "production_safety_claimed false in metadata"
        )

    def test_scorecard_results_summary_breakthrough(self):
        data = load_yaml(SCORECARD_YAML)
        summary = data.get("results_summary", {})
        assert summary.get("breakthrough_detected", -1) == 0, (
            "breakthrough_detected == 0"
        )
        assert summary.get("breakthrough_candidate_count", -1) == 0, (
            "breakthrough_candidate_count == 0"
        )

    def test_scorecard_boundary_preserved(self):
        data = load_yaml(SCORECARD_YAML)
        summary = data.get("results_summary", {})
        assert summary.get("boundary_preserved_count", 0) >= 8, (
            "boundary_preserved_count >= 8"
        )
        assert summary.get("boundary_failed_count", -1) == 0, (
            "boundary_failed_count == 0"
        )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
