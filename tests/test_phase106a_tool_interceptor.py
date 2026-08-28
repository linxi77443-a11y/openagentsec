"""Phase 106A — 动态工具调用参数注入与 MCP 结构化类型混淆拦截器 Pytest Suite."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_playbook_structure():
    playbook_path = ROOT / "adversarial_playbooks/phase106a_dynamic_tool_interceptor/playbook.yaml"
    assert playbook_path.exists(), "Playbook file must exist"
    with open(playbook_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["playbook_metadata"]["task_id"] == "Phase-106A-TOOL-001"
    assert data["playbook_metadata"]["module_id"] == "DYNAMIC_TOOL_INTERCEPTOR"
    assert data["playbook_metadata"]["assessment_mode"] == "adversarial_validation"
    assert data["playbook_metadata"]["synthetic_only"] is True
    assert data["playbook_metadata"]["fake_runtime_only"] is True
    assert data["playbook_metadata"]["confirmed_vulnerability"] is False
    assert len(data["entries"]) == 10
    attacks = [e for e in data["entries"] if not e.get("control_case")]
    controls = [e for e in data["entries"] if e.get("control_case")]
    assert len(attacks) == 8
    assert len(controls) == 2


def test_run_config_structure():
    rc_path = ROOT / "run_configs/phase106a_dynamic_tool_interceptor_run_config.yaml"
    assert rc_path.exists(), "Run config must exist"
    with open(rc_path, "r", encoding="utf-8") as f:
        rc = yaml.safe_load(f)
    rcfg = rc["run_config"]
    assert rcfg["phase"] == "phase106a"
    assert rcfg["task_id"] == "Phase-106A-TOOL-001"
    assert rcfg["module_id"] == "DYNAMIC_TOOL_INTERCEPTOR"
    assert rcfg["synthetic_only"] is True
    assert rcfg["confirmed_vulnerability"] is False
    params = rc["dynamic_tool_interceptor_parameters"]
    assert params["schema_strict_validation_enabled"] is True
    assert params["mcp_type_enforcement_enabled"] is True
    assert params["nested_escape_normalizer_enabled"] is True
    assert params["namespace_integrity_guard_enabled"] is True
    assert params["indirect_output_taint_tracking_enabled"] is True
    assert params["additional_properties_strict_rejection_enabled"] is True
    assert params["recursive_call_depth_circuit_breaker_enabled"] is True
    assert params["mcp_protocol_state_machine_verifier_enabled"] is True
    assert params["max_tool_call_depth_budget"] == 4


def test_execution_results():
    exec_path = ROOT / "executions/phase106a_dynamic_tool_interceptor/execution_results.json"
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
        assert r["fake_runtime_only"] is True
        assert r["real_agent_communication_bus_accessed"] is False
        assert r["real_mcp_server_accessed"] is False
        assert r["real_tool_call_executed"] is False
        if not r.get("control_case"):
            assert r["defensive_action"] == "refuse"
            assert r["defense_drill_blocked"] is True
            assert r["tool_call_intercepted"] is True
            assert r["tool_call_completed_safely"] is False
            assert r["breakthrough_detected"] is False
            assert r["requires_human_review"] is True
        else:
            assert r["defensive_action"] == "normal_usage_allowed"
            assert r["defense_drill_blocked"] is False
            assert r["coordination_allowed"] is True
            assert r["tool_call_intercepted"] is False
            assert r["tool_call_completed_safely"] is True
            assert r["breakthrough_detected"] is False
            assert r["requires_human_review"] is False


def test_evidence_manifest():
    manifest_path = ROOT / "executions/phase106a_dynamic_tool_interceptor/evidence_manifest.yaml"
    assert manifest_path.exists(), "Evidence manifest must exist"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    assert manifest["manifest_metadata"]["task_id"] == "Phase-106A-TOOL-001"
    assert manifest["manifest_metadata"]["module_id"] == "DYNAMIC_TOOL_INTERCEPTOR"
    assert len(manifest["evidence_chains"]) == 10


def test_result_yaml():
    for result_path in [
        ROOT / "executions/phase106a_dynamic_tool_interceptor/result.yaml",
        ROOT / "adversarial_playbooks/phase106a_dynamic_tool_interceptor/result.yaml",
    ]:
        assert result_path.exists(), f"Result file {result_path} must exist"
        with open(result_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["task_id"] == "Phase-106A-TOOL-001"
        assert data["module_id"] == "DYNAMIC_TOOL_INTERCEPTOR"
        assert data["status"] == "PASS"
        assert data["total_cases"] == 10
        assert data["attack_cases"] == 8
        assert data["control_cases"] == 2
        assert data["defense_drills_blocked_count"] == 8
        assert data["breakthrough_detected_count"] == 0
        assert data["confirmed_vulnerability"] is False


def test_capability_scorecard():
    for scorecard_path in [
        ROOT / "executions/phase106a_dynamic_tool_interceptor/capability_scorecard.yaml",
        ROOT / "adversarial_playbooks/phase106a_dynamic_tool_interceptor/capability_scorecard.yaml",
    ]:
        assert scorecard_path.exists(), f"Scorecard file {scorecard_path} must exist"
        with open(scorecard_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["scorecard_metadata"]["task_id"] == "Phase-106A-TOOL-001"
        assert data["scorecard_metadata"]["module_id"] == "DYNAMIC_TOOL_INTERCEPTOR"
        assert data["results_summary"]["interceptions"] == 8
        assert data["results_summary"]["breakthroughs"] == 0
        assert data["results_summary"]["control_passed"] == 2
        assert len(data["defensive_capabilities_evaluated"]) == 10
        for cap in data["defensive_capabilities_evaluated"]:
            assert cap["status"] == "PASS"


def test_validator_script():
    validator_path = ROOT / "scripts/validate_phase106a_tool_interceptor.py"
    assert validator_path.exists(), "Validator script must exist"
    res = subprocess.run([sys.executable, str(validator_path)], capture_output=True, text=True)
    assert res.returncode == 0, f"Validator exited with error: {res.stderr}\nOutput: {res.stdout}"


def test_notes_doc():
    notes_path = ROOT / "docs/phase106a_tool_interceptor_notes.md"
    assert notes_path.exists(), "Notes document must exist"
    content = notes_path.read_text(encoding="utf-8")
    assert "DYNAMIC_TOOL_INTERCEPTOR" in content
    assert "Phase-106A-TOOL-001" in content
