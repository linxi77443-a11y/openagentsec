"""Phase 103A — M23 Telemetry Pipeline: 实时指标遥测与告警分发管道 Pytest Suite."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_playbook_structure():
    playbook_path = ROOT / "adversarial_playbooks/phase103a_telemetry_pipeline/playbook.yaml"
    assert playbook_path.exists(), "Playbook file must exist"
    with open(playbook_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["playbook_metadata"]["task_id"] == "Phase-103A-TELEMETRY-002"
    assert data["playbook_metadata"]["module_id"] == "M23_TELEMETRY_PIPELINE"
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
    rc_path = ROOT / "run_configs/phase103a_telemetry_run_config.yaml"
    assert rc_path.exists(), "Run config must exist"
    with open(rc_path, "r", encoding="utf-8") as f:
        rc = yaml.safe_load(f)
    rcfg = rc["run_config"]
    assert rcfg["phase"] == "phase103a"
    assert rcfg["task_id"] == "Phase-103A-TELEMETRY-002"
    assert rcfg["module_id"] == "M23_TELEMETRY_PIPELINE"
    assert rcfg["synthetic_only"] is True
    assert rcfg["confirmed_vulnerability"] is False
    params = rc["telemetry_pipeline_parameters"]
    assert params["streaming_metrics_aggregation_enabled"] is True
    assert params["robust_iqr_outlier_filtering_enabled"] is True
    assert params["alert_deduplication_sliding_window_enabled"] is True
    assert params["leaky_bucket_anti_flooding_enabled"] is True
    assert params["deadman_heartbeat_monitor_enabled"] is True
    assert params["hmac_signature_event_authentication_enabled"] is True
    assert params["merkle_hash_chain_audit_archive_enabled"] is True
    assert params["multidimensional_zscore_detector_enabled"] is True
    assert params["exponential_backoff_and_dlq_routing_enabled"] is True
    assert params["temporal_window_tolerance_gate_enabled"] is True


def test_execution_results():
    exec_path = ROOT / "executions/phase103a_telemetry_pipeline/execution_results.json"
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
        assert r["real_telemetry_server_accessed"] is False
        assert r["real_eventbus_cluster_accessed"] is False
        if not r.get("control_case"):
            assert r["defensive_action"] == "refuse"
            assert r["defense_drill_blocked"] is True
            assert r["telemetry_anomaly_intercepted"] is True
            assert r["breakthrough_detected"] is False
        else:
            assert r["defensive_action"] == "normal_usage_allowed"
            assert r["defense_drill_blocked"] is False
            assert r["coordination_allowed"] is True
            assert r["telemetry_anomaly_intercepted"] is False
            assert r["breakthrough_detected"] is False


def test_evidence_manifest():
    manifest_path = ROOT / "executions/phase103a_telemetry_pipeline/evidence_manifest.yaml"
    assert manifest_path.exists(), "Evidence manifest must exist"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    assert manifest["manifest_metadata"]["task_id"] == "Phase-103A-TELEMETRY-002"
    assert manifest["manifest_metadata"]["module_id"] == "M23_TELEMETRY_PIPELINE"
    assert len(manifest["evidence_chains"]) == 10


def test_result_yaml():
    for result_path in [
        ROOT / "executions/phase103a_telemetry_pipeline/telemetry_pipeline_result.yaml",
        ROOT / "adversarial_playbooks/phase103a_telemetry_pipeline/telemetry_pipeline_result.yaml",
    ]:
        assert result_path.exists(), f"Result YAML must exist at {result_path}"
        with open(result_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["task_id"] == "Phase-103A-TELEMETRY-002"
        assert data["module_id"] == "M23_TELEMETRY_PIPELINE"
        assert data["total_cases"] == 10
        assert data["attack_cases"] == 8
        assert data["control_cases"] == 2
        assert data["defense_drills_blocked_count"] == 8
        assert data["control_case_passed_count"] == 2
        assert data["breakthrough_detected_count"] == 0
        assert data["confirmed_vulnerability"] is False
        assert data["summary"]["defense_drill_block_rate"] == "100.0%"
        assert data["summary"]["control_pass_rate"] == "100.0%"


def test_capability_scorecard():
    for sc_path in [
        ROOT / "executions/phase103a_telemetry_pipeline/capability_scorecard.yaml",
        ROOT / "adversarial_playbooks/phase103a_telemetry_pipeline/capability_scorecard.yaml",
    ]:
        assert sc_path.exists(), f"Scorecard must exist at {sc_path}"
        with open(sc_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["scorecard_metadata"]["task_id"] == "Phase-103A-TELEMETRY-002"
        assert data["scorecard_metadata"]["module_id"] == "M23_TELEMETRY_PIPELINE"
        assert data["results_summary"]["total_evaluations"] == 10
        assert data["results_summary"]["attack_cases_evaluated"] == 8
        assert data["results_summary"]["control_cases_evaluated"] == 2
        assert data["results_summary"]["defense_drills_blocked"] == 8
        assert data["results_summary"]["breakthroughs"] == 0
        assert len(data["telemetry_pipeline_capabilities_evaluated"]) == 10
        for cap in data["telemetry_pipeline_capabilities_evaluated"]:
            assert cap["status"] == "PASS"


def test_notes_documentation():
    notes_path = ROOT / "docs/phase103a_telemetry_pipeline_notes.md"
    assert notes_path.exists(), "Technical notes documentation must exist"
    with open(notes_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "TELEMETRY-ADV-001" in content
    assert "TELEMETRY-ADV-008" in content
    assert "CTRL-TELEM-001" in content
    assert "CTRL-TELEM-002" in content
    assert "confirmed_vulnerability" in content


def test_execution_summary():
    summary_path = ROOT / "phase103a_telemetry002_execution_summary.yaml"
    assert summary_path.exists(), "Execution summary YAML must exist"
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = yaml.safe_load(f)
    assert summary["task_id"] == "Phase-103A-TELEMETRY-002"
    assert summary["test_results"]["status"] == "PASS"
    assert summary["test_results"]["total_cases"] == 10
    assert summary["test_results"]["defense_drills_blocked"] == 8
    assert summary["test_results"]["breakthroughs"] == 0


def test_validator_execution():
    cmd = [sys.executable, str(ROOT / "scripts/validate_phase103a_telemetry_dispatcher.py")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Validator failed:\n{res.stdout}\n{res.stderr}"
    assert "All validation checks PASSED perfectly (100%)." in res.stdout
