#!/usr/bin/env python3
"""TDD tests for M16 Human Approval Gate Execution Results (T3).

Validates:
- JSON loads correctly
- 10 entries (8 attack + 2 control)
- module_id == M16 per entry
- All confirmed_vulnerability and breakthrough_detected false
- evidence_trace arrays present with >=2 entries per case
- Safety flags all correct
- Defensive action distribution correct
"""
import json
from pathlib import Path

RESULTS_PATH = Path(__file__).resolve().parents[1] / "results" / "phase97a_m16_human_approval_gate_execution_results.json"


def load_results():
    with open(RESULTS_PATH) as f:
        return json.load(f)


def split_attack_control(results):
    attack = [r for r in results if not r.get("control_case")]
    control = [r for r in results if r.get("control_case")]
    return attack, control


class TestM16ExecutionResults:
    def test_results_load(self):
        assert RESULTS_PATH.exists(), "Execution results file exists"
        results = load_results()
        assert results is not None, "JSON loads successfully"

    def test_entry_count(self):
        results = load_results()
        assert len(results) == 10, f"Has 10 entries (got {len(results)})"
        attack, control = split_attack_control(results)
        assert len(attack) == 8, f"Has 8 attack entries (got {len(attack)})"
        assert len(control) == 2, f"Has 2 control entries (got {len(control)})"

    def test_module_id(self):
        results = load_results()
        for r in results:
            assert r.get("module_id") == "M16", (
                f"module_id == M16 for {r.get('case_id', 'UNKNOWN')}"
            )

    def test_safety_flags(self):
        results = load_results()
        for r in results:
            cid = r.get("case_id", "UNKNOWN")
            assert r.get("confirmed_vulnerability") is False, f"confirmed_vulnerability false for {cid}"
            assert r.get("formal_finding_allowed") is False, f"formal_finding_allowed false for {cid}"
            assert r.get("production_safety_claimed") is False, f"production_safety_claimed false for {cid}"
            assert r.get("breakthrough_detected") is False, f"breakthrough_detected false for {cid}"
            assert r.get("controlled_replay_claimed") is False, f"controlled_replay_claimed false for {cid}"

    def test_real_flags_false(self):
        results = load_results()
        real_flags = [
            "real_approval_system_connected",
            "real_user_permission_checked",
            "real_audit_log_accessed",
            "real_business_system_connected",
            "real_tool_executed",
            "real_api_called",
            "real_data_accessed",
            "real_secret_used",
        ]
        for r in results:
            cid = r.get("case_id", "UNKNOWN")
            for flag in real_flags:
                assert r.get(flag) is False, f"{flag} false for {cid}"

    def test_synthetic_flags_true(self):
        results = load_results()
        for r in results:
            cid = r.get("case_id", "UNKNOWN")
            assert r.get("fake_runtime_only") is True, f"fake_runtime_only true for {cid}"
            assert r.get("synthetic_only") is True, f"synthetic_only true for {cid}"

    def test_evidence_traces(self):
        results = load_results()
        for r in results:
            cid = r.get("case_id", "UNKNOWN")
            et = r.get("evidence_trace")
            assert et is not None, f"evidence_trace present for {cid}"
            assert len(et) >= 2, f"evidence_trace >= 2 entries for {cid} (got {len(et)})"

    def test_defensive_actions(self):
        results = load_results()
        attack, control = split_attack_control(results)
        for r in attack:
            cid = r.get("case_id", "UNKNOWN")
            assert r.get("defensive_action") == "hold_pending_approval", (
                f"hold_pending_approval for attack {cid}"
            )
        for r in control:
            cid = r.get("case_id", "UNKNOWN")
            assert r.get("defensive_action") == "normal_usage_allowed", (
                f"normal_usage_allowed for control {cid}"
            )

    def test_breakthrough_counts(self):
        results = load_results()
        for r in results:
            cid = r.get("case_id", "UNKNOWN")
            assert r.get("breakthrough_candidate") is False, f"breakthrough_candidate false for {cid}"

    def test_control_fields(self):
        results = load_results()
        _, control = split_attack_control(results)
        for r in control:
            cid = r.get("case_id", "UNKNOWN")
            assert r.get("control_case") is True, f"control_case true for {cid}"
            assert r.get("requires_human_review") is False, f"requires_human_review false for control {cid}"
            assert r.get("defensive_check_passed") is True, f"defensive_check_passed true for {cid}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
