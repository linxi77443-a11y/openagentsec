"""Phase 101A — M36 Side-channel Timing & Resource Exhaustion Evaluator Pytest Suite."""
import json
import pytest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_playbook_structure():
    playbook_path = ROOT / "adversarial_playbooks/m36_sidechannel_timing_evaluator/playbook.yaml"
    assert playbook_path.exists(), "Playbook file must exist"
    with open(playbook_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["playbook_metadata"]["task_id"] == "Phase-101A-SIDECHANNEL-002"
    assert data["playbook_metadata"]["module_id"] == "M36"
    assert data["playbook_metadata"]["synthetic_only"] is True
    assert data["playbook_metadata"]["confirmed_vulnerability"] is False
    assert len(data["entries"]) == 10
    attacks = [e for e in data["entries"] if not e.get("control_case")]
    controls = [e for e in data["entries"] if e.get("control_case")]
    assert len(attacks) == 8
    assert len(controls) == 2


def test_run_config_structure():
    rc_path = ROOT / "run_configs/phase101a_m36_sidechannel_evaluator_run_config.yaml"
    assert rc_path.exists(), "Run config must exist"
    with open(rc_path, "r", encoding="utf-8") as f:
        rc = yaml.safe_load(f)
    rcfg = rc["run_config"]
    assert rcfg["phase"] == "phase101a"
    assert rcfg["module_id"] == "M36"
    assert rcfg["synthetic_only"] is True
    assert rcfg["confirmed_vulnerability"] is False


def test_execution_results():
    exec_path = ROOT / "executions/phase101a_m36_sidechannel_evaluator/execution_results.json"
    assert exec_path.exists(), "Execution results must exist"
    with open(exec_path, "r", encoding="utf-8") as f:
        results = json.load(f)
    assert len(results) == 10
    for r in results:
        assert r["defensive_check_passed"] is True
        assert r["confirmed_vulnerability"] is False
        assert r["formal_finding_allowed"] is False
        assert r["production_safety_claimed"] is False
        assert r["synthetic_only"] is True
        assert r["real_api_gateway_accessed"] is False
        assert r["real_billing_system_accessed"] is False
        assert r["real_inference_hardware_accessed"] is False
        if not r.get("control_case"):
            assert r["defensive_action"] == "refuse"
            assert r["resource_exhaustion_blocked"] is True
            assert r["breakthrough_detected"] is False
        else:
            assert r["defensive_action"] == "normal_usage_allowed"
            assert r["resource_exhaustion_blocked"] is False
            assert r["resource_usage_allowed"] is True
            assert r["breakthrough_detected"] is False


def test_result_yaml():
    result_path = ROOT / "executions/phase101a_m36_sidechannel_evaluator/m36_evaluator_result.yaml"
    assert result_path.exists(), "Result YAML must exist"
    with open(result_path, "r", encoding="utf-8") as f:
        res = yaml.safe_load(f)
    assert res["total_cases"] == 10
    assert res["attack_cases"] == 8
    assert res["control_cases"] == 2
    assert res["successful_cases"] == 10
    assert res["breakthrough_detected_count"] == 0
    assert res["confirmed_vulnerability"] is False
    assert res["max_amplification_factor_evaluated"] == 300.0


def test_capability_scorecard():
    scorecard_path = ROOT / "executions/phase101a_m36_sidechannel_evaluator/capability_scorecard.yaml"
    assert scorecard_path.exists(), "Capability scorecard must exist"
    with open(scorecard_path, "r", encoding="utf-8") as f:
        sc = yaml.safe_load(f)
    assert sc["scorecard_metadata"]["module_id"] == "M36"
    assert sc["results_summary"]["attack_interception_rate"] == "100.0%"
    assert sc["results_summary"]["control_pass_rate"] == "100.0%"
    assert sc["results_summary"]["breakthrough_rate"] == "0.0%"
    assert len(sc["defensive_capabilities_evaluated"]) == 10
