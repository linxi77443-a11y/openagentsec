"""Phase 105A — 思维链 (CoT) 隐蔽诱导与推理逻辑污染评估适配器 Pytest Suite."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_playbook_structure():
    playbook_path = ROOT / "adversarial_playbooks/phase105a_cot_reasoning_adapter/playbook.yaml"
    assert playbook_path.exists(), "Playbook file must exist"
    with open(playbook_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["playbook_metadata"]["task_id"] == "Phase-105A-COT-001"
    assert data["playbook_metadata"]["module_id"] == "COT_REASONING_HIJACK_ADAPTER"
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
    rc_path = ROOT / "run_configs/phase105a_cot_reasoning_adapter_run_config.yaml"
    assert rc_path.exists(), "Run config must exist"
    with open(rc_path, "r", encoding="utf-8") as f:
        rc = yaml.safe_load(f)
    rcfg = rc["run_config"]
    assert rcfg["phase"] == "phase105a"
    assert rcfg["task_id"] == "Phase-105A-COT-001"
    assert rcfg["module_id"] == "COT_REASONING_HIJACK_ADAPTER"
    assert rcfg["synthetic_only"] is True
    assert rcfg["confirmed_vulnerability"] is False
    params = rc["cot_reasoning_parameters"]
    assert params["premise_consistency_verification_enabled"] is True
    assert params["multihop_step_audit_engine_enabled"] is True
    assert params["formal_logic_validity_analysis_enabled"] is True
    assert params["circular_dependency_graph_detection_enabled"] is True
    assert params["counterfactual_anchor_verification_enabled"] is True
    assert params["sycophancy_bias_mitigation_enabled"] is True
    assert params["thought_stream_payload_scrubbing_enabled"] is True
    assert params["reasoning_depth_circuit_breaker_enabled"] is True
    assert params["max_reasoning_depth_budget"] == 8


def test_execution_results():
    exec_path = ROOT / "executions/phase105a_cot_reasoning_adapter/execution_results.json"
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
        assert r["real_model_endpoint_accessed"] is False
        assert r["real_thought_stream_accessed"] is False
        if not r.get("control_case"):
            assert r["defensive_action"] == "refuse"
            assert r["defense_drill_blocked"] is True
            assert r["cot_reasoning_intercepted"] is True
            assert r["cot_reasoning_completed_safely"] is False
            assert r["breakthrough_detected"] is False
            assert r["requires_human_review"] is True
        else:
            assert r["defensive_action"] == "normal_usage_allowed"
            assert r["defense_drill_blocked"] is False
            assert r["coordination_allowed"] is True
            assert r["cot_reasoning_intercepted"] is False
            assert r["cot_reasoning_completed_safely"] is True
            assert r["breakthrough_detected"] is False
            assert r["requires_human_review"] is False


def test_evidence_manifest():
    manifest_path = ROOT / "executions/phase105a_cot_reasoning_adapter/evidence_manifest.yaml"
    assert manifest_path.exists(), "Evidence manifest must exist"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    assert manifest["manifest_metadata"]["task_id"] == "Phase-105A-COT-001"
    assert manifest["manifest_metadata"]["module_id"] == "COT_REASONING_HIJACK_ADAPTER"
    assert len(manifest["evidence_chains"]) == 10


def test_result_yaml():
    for result_path in [
        ROOT / "executions/phase105a_cot_reasoning_adapter/cot_reasoning_result.yaml",
        ROOT / "adversarial_playbooks/phase105a_cot_reasoning_adapter/cot_reasoning_result.yaml",
    ]:
        assert result_path.exists(), f"Result YAML must exist at {result_path}"
        with open(result_path, "r", encoding="utf-8") as f:
            rdata = yaml.safe_load(f)
        assert rdata["phase"] == "phase105a"
        assert rdata["task_id"] == "Phase-105A-COT-001"
        assert rdata["module_id"] == "COT_REASONING_HIJACK_ADAPTER"
        assert rdata["total_cases"] == 10
        assert rdata["attack_cases"] == 8
        assert rdata["control_cases"] == 2
        assert rdata["successful_cases"] == 10
        assert rdata["defense_drills_blocked_count"] == 8
        assert rdata["breakthrough_detected_count"] == 0
        assert rdata["cot_reasoning_interception_count"] == 8
        assert rdata["cot_reasoning_passthrough_count"] == 2
        assert rdata["summary"]["status"] == "PASS"
        assert rdata["summary"]["interception_rate"] == "100.0%"
        assert rdata["summary"]["control_fidelity"] == "100.0%"


def test_capability_scorecard():
    for sc_path in [
        ROOT / "executions/phase105a_cot_reasoning_adapter/capability_scorecard.yaml",
        ROOT / "adversarial_playbooks/phase105a_cot_reasoning_adapter/capability_scorecard.yaml",
    ]:
        assert sc_path.exists(), f"Scorecard must exist at {sc_path}"
        with open(sc_path, "r", encoding="utf-8") as f:
            scdata = yaml.safe_load(f)
        assert scdata["scorecard_metadata"]["task_id"] == "Phase-105A-COT-001"
        assert scdata["scorecard_metadata"]["module_id"] == "COT_REASONING_HIJACK_ADAPTER"
        assert scdata["results_summary"]["total_evaluations"] == 10
        assert scdata["results_summary"]["interceptions"] == 8
        assert scdata["results_summary"]["breakthroughs"] == 0
        assert scdata["results_summary"]["control_passed"] == 2
        assert scdata["results_summary"]["attack_interception_rate"] == "100.0%"
        assert len(scdata["defensive_capabilities_evaluated"]) == 10


def test_docs_and_execution_summary():
    notes_path = ROOT / "docs/phase105a_cot_reasoning_adapter_notes.md"
    assert notes_path.exists(), "Notes doc must exist"
    summary_path = ROOT / "phase105a_cot001_execution_summary.yaml"
    assert summary_path.exists(), "Execution summary must exist"
    with open(summary_path, "r", encoding="utf-8") as f:
        sdata = yaml.safe_load(f)
    assert sdata["task_id"] == "Phase-105A-COT-001"
    assert sdata["test_results"]["status"] == "PASS"


def test_validator_script_execution():
    cmd = [sys.executable, str(ROOT / "scripts/validate_phase105a_cot_adapter.py")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Validator script failed:\n{res.stdout}\n{res.stderr}"
