"""Phase 103A — M23 Stream Gateway: 实时流式代理评估网关 Pytest Suite."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_playbook_structure():
    playbook_path = ROOT / "adversarial_playbooks/phase103a_stream_gateway/playbook.yaml"
    assert playbook_path.exists(), "Playbook file must exist"
    with open(playbook_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["playbook_metadata"]["task_id"] == "Phase-103A-GATEWAY-001"
    assert data["playbook_metadata"]["module_id"] == "M23_STREAM_GATEWAY"
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
    rc_path = ROOT / "run_configs/phase103a_gateway_run_config.yaml"
    assert rc_path.exists(), "Run config must exist"
    with open(rc_path, "r", encoding="utf-8") as f:
        rc = yaml.safe_load(f)
    rcfg = rc["run_config"]
    assert rcfg["phase"] == "phase103a"
    assert rcfg["task_id"] == "Phase-103A-GATEWAY-001"
    assert rcfg["module_id"] == "M23_STREAM_GATEWAY"
    assert rcfg["synthetic_only"] is True
    assert rcfg["confirmed_vulnerability"] is False
    params = rc["stream_gateway_parameters"]
    assert params["sse_chunk_interception_enabled"] is True
    assert params["websocket_frame_inspection_enabled"] is True
    assert params["sliding_window_token_assembly_enabled"] is True
    assert params["streaming_dlp_rollback_buffer_enabled"] is True
    assert params["control_character_stream_sanitization_enabled"] is True
    assert params["multibyte_utf8_boundary_state_machine_enabled"] is True
    assert params["slow_stream_cadence_monitoring_enabled"] is True
    assert params["recursive_stream_semantic_gate_enabled"] is True
    assert params["websocket_binary_entropy_analyzer_enabled"] is True


def test_execution_results():
    exec_path = ROOT / "executions/phase103a_gateway_interceptor/execution_results.json"
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
        assert r["real_orchestration_engine_accessed"] is False
        assert r["real_wargame_runtime_accessed"] is False
        assert r["real_websocket_endpoint_accessed"] is False
        assert r["real_sse_server_accessed"] is False
        if not r.get("control_case"):
            assert r["defensive_action"] == "refuse"
            assert r["defense_drill_blocked"] is True
            assert r["stream_intercepted"] is True
            assert r["stream_forwarded_safely"] is False
            assert r["breakthrough_detected"] is False
        else:
            assert r["defensive_action"] == "normal_usage_allowed"
            assert r["defense_drill_blocked"] is False
            assert r["coordination_allowed"] is True
            assert r["stream_intercepted"] is False
            assert r["stream_forwarded_safely"] is True
            assert r["breakthrough_detected"] is False


def test_evidence_manifest():
    manifest_path = ROOT / "executions/phase103a_gateway_interceptor/evidence_manifest.yaml"
    assert manifest_path.exists(), "Evidence manifest must exist"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    assert manifest["manifest_metadata"]["task_id"] == "Phase-103A-GATEWAY-001"
    assert manifest["manifest_metadata"]["module_id"] == "M23_STREAM_GATEWAY"
    assert len(manifest["evidence_chains"]) == 10


def test_result_yaml():
    for result_path in [
        ROOT / "executions/phase103a_gateway_interceptor/stream_gateway_result.yaml",
        ROOT / "adversarial_playbooks/phase103a_stream_gateway/stream_gateway_result.yaml",
    ]:
        assert result_path.exists(), f"Result YAML must exist at {result_path}"
        with open(result_path, "r", encoding="utf-8") as f:
            res = yaml.safe_load(f)
        assert res["task_id"] == "Phase-103A-GATEWAY-001"
        assert res["total_cases"] == 10
        assert res["attack_cases"] == 8
        assert res["control_cases"] == 2
        assert res["successful_cases"] == 10
        assert res["breakthrough_detected_count"] == 0
        assert res["defense_drills_blocked_count"] == 8
        assert res["stream_interception_count"] == 8
        assert res["stream_passthrough_count"] == 2
        assert res["control_case_passed_count"] == 2
        assert res["confirmed_vulnerability"] is False
        assert res["summary"]["defense_drill_block_rate"] == "100.0%"
        assert res["summary"]["control_pass_rate"] == "100.0%"


def test_capability_scorecard():
    for sc_path in [
        ROOT / "executions/phase103a_gateway_interceptor/capability_scorecard.yaml",
        ROOT / "adversarial_playbooks/phase103a_stream_gateway/capability_scorecard.yaml",
    ]:
        assert sc_path.exists(), f"Capability scorecard must exist at {sc_path}"
        with open(sc_path, "r", encoding="utf-8") as f:
            sc = yaml.safe_load(f)
        assert sc["scorecard_metadata"]["task_id"] == "Phase-103A-GATEWAY-001"
        assert sc["scorecard_metadata"]["module_id"] == "M23_STREAM_GATEWAY"
        assert sc["results_summary"]["total_evaluations"] == 10
        assert sc["results_summary"]["defense_drills_blocked"] == 8
        assert sc["results_summary"]["breakthroughs"] == 0
        assert sc["results_summary"]["control_passed"] == 2
        caps = sc["streaming_interception_capabilities_evaluated"]
        assert len(caps) == 10
        for c in caps:
            assert c["status"] == "PASS"


def test_notes_doc():
    notes_path = ROOT / "docs/phase103a_gateway_interceptor_notes.md"
    assert notes_path.exists(), "Notes document must exist"
    content = notes_path.read_text(encoding="utf-8")
    assert "Phase 103A" in content or "Phase-103A" in content
    assert "Stream Gateway" in content or "SSE" in content


def test_execution_summary():
    summary_path = ROOT / "phase103a_gateway001_execution_summary.yaml"
    assert summary_path.exists(), "Execution summary must exist"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = yaml.safe_load(f)
    assert summary["task_id"] == "Phase-103A-GATEWAY-001"
    assert summary["test_results"]["status"] == "PASS"
    assert summary["test_results"]["total_cases"] == 10
    assert summary["test_results"]["defense_drills_blocked"] == 8


def test_validator_script_execution():
    val_script = ROOT / "scripts/validate_phase103a_gateway_interceptor.py"
    proc = subprocess.run(
        [sys.executable, str(val_script)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"Validator script failed with output:\n{proc.stdout}\n{proc.stderr}"
    assert "ALL PHASE-103A-GATEWAY-001 VALIDATION CHECKS PASSED" in proc.stdout
