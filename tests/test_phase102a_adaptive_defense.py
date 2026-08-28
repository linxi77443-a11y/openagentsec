"""Phase 102A — M37/M44 Defense: 动态自适应防御规则生成与热更新引擎 Pytest Suite."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_playbook_structure():
    playbook_path = ROOT / "adversarial_playbooks/phase102a_adaptive_defense/playbook.yaml"
    assert playbook_path.exists(), "Playbook file must exist"
    with open(playbook_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["playbook_metadata"]["task_id"] == "Phase-102A-DEFENSE-002"
    assert data["playbook_metadata"]["module_id"] == "M37_M44_DEFENSE"
    assert data["playbook_metadata"]["synthetic_only"] is True
    assert data["playbook_metadata"]["confirmed_vulnerability"] is False
    assert len(data["entries"]) == 10
    attacks = [e for e in data["entries"] if not e.get("control_case")]
    controls = [e for e in data["entries"] if e.get("control_case")]
    assert len(attacks) == 8
    assert len(controls) == 2


def test_run_config_structure():
    rc_path = ROOT / "run_configs/phase102a_adaptive_defense_run_config.yaml"
    assert rc_path.exists(), "Run config must exist"
    with open(rc_path, "r", encoding="utf-8") as f:
        rc = yaml.safe_load(f)
    rcfg = rc["run_config"]
    assert rcfg["phase"] == "phase102a"
    assert rcfg["task_id"] == "Phase-102A-DEFENSE-002"
    assert rcfg["module_id"] == "M37_M44_DEFENSE"
    assert rcfg["synthetic_only"] is True
    assert rcfg["confirmed_vulnerability"] is False
    params = rc["defense_parameters"]
    assert params["dynamic_rule_synthesis_enabled"] is True
    assert params["ast_syntax_compliance_check_enabled"] is True
    assert params["zero_downtime_hot_reload_enabled"] is True
    assert params["rule_conflict_detection_graph_enabled"] is True
    assert params["non_retroactivity_rollback_enabled"] is True


def test_execution_results():
    exec_path = ROOT / "executions/phase102a_adaptive_defense/execution_results.json"
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
        assert r["real_agent_communication_bus_accessed"] is False
        assert r["real_orchestration_engine_accessed"] is False
        assert r["real_wargame_runtime_accessed"] is False
        assert r["real_rule_engine_production_service_accessed"] is False
        assert r["rule_synthesized"] is True
        assert r["syntax_validation_passed"] is True
        assert r["hot_reload_applied"] is True
        if not r.get("control_case"):
            assert r["defensive_action"] == "refuse"
            assert r["defense_drill_blocked"] is True
            assert r["breakthrough_detected"] is False
        else:
            assert r["defensive_action"] == "normal_usage_allowed"
            assert r["defense_drill_blocked"] is False
            assert r["coordination_allowed"] is True
            assert r["breakthrough_detected"] is False


def test_result_yaml():
    for result_path in [
        ROOT / "executions/phase102a_adaptive_defense/adaptive_defense_result.yaml",
        ROOT / "adversarial_playbooks/phase102a_adaptive_defense/adaptive_defense_result.yaml",
    ]:
        assert result_path.exists(), f"Result YAML must exist at {result_path}"
        with open(result_path, "r", encoding="utf-8") as f:
            res = yaml.safe_load(f)
        assert res["task_id"] == "Phase-102A-DEFENSE-002"
        assert res["total_cases"] == 10
        assert res["attack_cases"] == 8
        assert res["control_cases"] == 2
        assert res["successful_cases"] == 10
        assert res["breakthrough_detected_count"] == 0
        assert res["defense_drills_blocked_count"] == 8
        assert res["control_case_passed_count"] == 2
        assert res["confirmed_vulnerability"] is False
        assert res["rules_synthesized_count"] == 10
        assert res["syntax_validation_pass_count"] == 10
        assert res["hot_reload_success_count"] == 10
        assert res["rule_conflict_detected_count"] == 1
        assert res["rollback_executed_count"] == 1
        assert res["max_game_rounds_evaluated"] == 6


def test_capability_scorecard():
    for scorecard_path in [
        ROOT / "executions/phase102a_adaptive_defense/capability_scorecard.yaml",
        ROOT / "adversarial_playbooks/phase102a_adaptive_defense/capability_scorecard.yaml",
    ]:
        assert scorecard_path.exists(), f"Capability scorecard must exist at {scorecard_path}"
        with open(scorecard_path, "r", encoding="utf-8") as f:
            sc = yaml.safe_load(f)
        assert sc["scorecard_metadata"]["task_id"] == "Phase-102A-DEFENSE-002"
        assert sc["scorecard_metadata"]["module_id"] == "M37_M44_DEFENSE"
        assert sc["results_summary"]["defense_drill_block_rate"] == "100.0%"
        assert sc["results_summary"]["control_pass_rate"] == "100.0%"
        assert sc["results_summary"]["breakthrough_rate"] == "0.0%"
        assert sc["results_summary"]["conflicts_detected"] == 1
        assert sc["results_summary"]["rollbacks_executed"] == 1
        assert len(sc["defensive_capabilities_evaluated"]) == 10
        for cap in sc["defensive_capabilities_evaluated"]:
            assert cap["status"] == "PASS"


def test_validator_script_execution():
    val_script = ROOT / "scripts/validate_phase102a_adaptive_defense.py"
    assert val_script.exists(), "Validator script must exist"
    proc = subprocess.run([sys.executable, str(val_script)], capture_output=True, text=True)
    assert proc.returncode == 0, f"Validator script failed with output:\n{proc.stdout}\n{proc.stderr}"
