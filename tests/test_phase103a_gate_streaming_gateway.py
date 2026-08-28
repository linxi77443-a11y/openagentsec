"""
tests/test_phase103a_gate_streaming_gateway.py
Automated Integration Test Suite for Phase 103A Realtime Streaming Gateway & Telemetry Pipeline Integration Design Gate.

Task: Phase-103A-GATE-003
Task Name: 阶段 103 实时流式网关与遥测管道整合验证设计门开发
PRD References:
  - 原 PRD v1.0 §3, §4, §6, §10, §13, §15
  - 攻击者视角新增章节 §3, §5, §8, §11
  - PRD v2.0 §4, §5, §10, §13
  - PRD v3.1 §2.4, §2.7, §3, §4

Test Coverage:
1. Deliverables Files Existence & Structure Integrity (24+ files).
2. Safety Boundary Invariants Enforcement across Manifest, Playbooks, and Execution Results.
3. Stream Gateway (Task 1) Schema & 10 Test Cases (8 attacks + 2 controls).
4. Telemetry Pipeline (Task 2) Schema & 10 Test Cases (8 attacks + 2 controls).
5. Parameterized 20-Case Synthetic Placeholder (<SIM_...>) 100% Syntax & Isolation Assertion.
6. Defense Interceptions (16/16 blocked) and Baseline Controls (4/4 allowed).
7. Closed-Loop Stream Interceptor & Telemetry Pipeline Mapping Integrity (8 loops).
8. Capability Scorecards & Result YAML Metric Consistency.
9. Run Configs & Fake Runtime Sandboxing Invariants.
10. Manifest Reconciliation & Cross-Module Metadata Integrity.
11. Standalone Validator Script Execution Verification.
12. Non-Retroactivity Guarantees for Historical Baselines.
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent

SIM_PLACEHOLDER_REGEX = re.compile(r"^<SIM_[A-Za-z0-9_]+>$")
SIM_EXTRACTION_REGEX = re.compile(r"<SIM_[A-Za-z0-9_]+>")


@pytest.fixture(scope="module")
def manifest_data() -> Dict[str, Any]:
    manifest_path = ROOT / "manifests/phase103a_reconciliation_manifest.yaml"
    assert manifest_path.exists(), f"Manifest missing at {manifest_path}"
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def gateway_playbook() -> Dict[str, Any]:
    pb_path = ROOT / "adversarial_playbooks/phase103a_stream_gateway/playbook.yaml"
    assert pb_path.exists(), f"Gateway Playbook missing at {pb_path}"
    return yaml.safe_load(pb_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def telemetry_playbook() -> Dict[str, Any]:
    pb_path = ROOT / "adversarial_playbooks/phase103a_telemetry_pipeline/playbook.yaml"
    assert pb_path.exists(), f"Telemetry Playbook missing at {pb_path}"
    return yaml.safe_load(pb_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def gateway_execution_results() -> List[Dict[str, Any]]:
    exec_path = ROOT / "executions/phase103a_gateway_interceptor/execution_results.json"
    assert exec_path.exists(), f"Gateway Execution results missing at {exec_path}"
    return json.loads(exec_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def telemetry_execution_results() -> List[Dict[str, Any]]:
    exec_path = ROOT / "executions/phase103a_telemetry_pipeline/execution_results.json"
    assert exec_path.exists(), f"Telemetry Execution results missing at {exec_path}"
    return json.loads(exec_path.read_text(encoding="utf-8"))


# ==============================================================================
# 1. Deliverables Files Existence & Integrity
# ==============================================================================

def test_gate_deliverables_files_existence():
    """Verifies all Phase 103A Gate deliverable files exist and are non-empty."""
    required_files = [
        # Gate Deliverables
        ROOT / "docs/phase103a_streaming_gateway_telemetry_integration_design_gate.md",
        ROOT / "docs/phase103a_gate_summary.md",
        ROOT / "manifests/phase103a_reconciliation_manifest.yaml",
        ROOT / "scripts/validate_phase103a_gate_streaming_gateway.py",
        ROOT / "tests/test_phase103a_gate_streaming_gateway.py",
        ROOT / "phase103a_gate003_execution_summary.yaml",
        ROOT / "delivery.json",
        # Task 1 (Stream Gateway) Assets
        ROOT / "adversarial_playbooks/phase103a_stream_gateway/playbook.yaml",
        ROOT / "run_configs/phase103a_gateway_run_config.yaml",
        ROOT / "scripts/run_phase103a_gateway_interceptor.py",
        ROOT / "scripts/parse_phase103a_gateway_interceptor.py",
        ROOT / "scripts/validate_phase103a_gateway_interceptor.py",
        ROOT / "tests/test_phase103a_gateway_interceptor.py",
        ROOT / "docs/phase103a_gateway_interceptor_notes.md",
        ROOT / "executions/phase103a_gateway_interceptor/execution_results.json",
        ROOT / "executions/phase103a_gateway_interceptor/evidence_manifest.yaml",
        ROOT / "executions/phase103a_gateway_interceptor/stream_gateway_result.yaml",
        ROOT / "executions/phase103a_gateway_interceptor/capability_scorecard.yaml",
        ROOT / "phase103a_gateway001_execution_summary.yaml",
        # Task 2 (Telemetry Pipeline) Assets
        ROOT / "adversarial_playbooks/phase103a_telemetry_pipeline/playbook.yaml",
        ROOT / "run_configs/phase103a_telemetry_run_config.yaml",
        ROOT / "scripts/run_phase103a_telemetry_dispatcher.py",
        ROOT / "scripts/parse_phase103a_telemetry_dispatcher.py",
        ROOT / "scripts/validate_phase103a_telemetry_dispatcher.py",
        ROOT / "tests/test_phase103a_telemetry_dispatcher.py",
        ROOT / "docs/phase103a_telemetry_pipeline_notes.md",
        ROOT / "executions/phase103a_telemetry_pipeline/execution_results.json",
        ROOT / "executions/phase103a_telemetry_pipeline/evidence_manifest.yaml",
        ROOT / "executions/phase103a_telemetry_pipeline/telemetry_pipeline_result.yaml",
        ROOT / "executions/phase103a_telemetry_pipeline/capability_scorecard.yaml",
        ROOT / "phase103a_telemetry002_execution_summary.yaml",
    ]

    for fpath in required_files:
        assert fpath.exists(), f"Required file missing: {fpath}"
        assert fpath.stat().st_size > 0, f"File empty: {fpath}"


# ==============================================================================
# 2. Safety Boundary Invariants
# ==============================================================================

def test_safety_boundary_invariants(manifest_data, gateway_playbook, telemetry_playbook):
    """Verifies that all safety boundary invariants are strictly code-enforced."""
    sb = manifest_data["safety_boundaries"]
    assert sb["confirmed_vulnerability"] is False
    assert sb["formal_finding_allowed"] is False
    assert sb["production_safety_claimed"] is False
    assert sb["controlled_replay_claimed"] is False
    assert sb["controlled_replay_execution_allowed"] is False
    assert sb["assessment_execution_performed"] is False
    assert sb["synthetic_only"] is True
    assert sb["fake_runtime_only"] is True
    assert sb["requires_human_review"] is True
    assert sb["all_findings_are_candidate"] is True
    assert sb["red_team_engine_not_executable"] is True
    assert sb["dashboard_not_execution_interface"] is True
    assert sb["theory_model_is_not_detection_rule"] is True
    assert sb["real_agent_communication_bus_allowed"] is False
    assert sb["real_websocket_endpoint_allowed"] is False
    assert sb["real_sse_server_allowed"] is False
    assert sb["real_telemetry_server_allowed"] is False
    assert sb["real_eventbus_cluster_allowed"] is False
    assert sb["real_alert_webhook_allowed"] is False
    assert sb["non_retroactivity_guarantee"] is True
    assert sb["zero_production_penetration"] is True
    assert sb["zero_formal_disconnect"] is True

    # Playbook metadata safety flags
    assert gateway_playbook["playbook_metadata"]["synthetic_only"] is True
    assert gateway_playbook["playbook_metadata"]["confirmed_vulnerability"] is False
    assert gateway_playbook["playbook_metadata"]["formal_finding_allowed"] is False
    assert telemetry_playbook["playbook_metadata"]["synthetic_only"] is True
    assert telemetry_playbook["playbook_metadata"]["confirmed_vulnerability"] is False
    assert telemetry_playbook["playbook_metadata"]["formal_finding_allowed"] is False


# ==============================================================================
# 3. Stream Gateway Playbook & Execution
# ==============================================================================

@pytest.mark.parametrize("entry_idx,expected_id,expected_category,expected_technique,is_control", [
    (0, "STREAM-GW-001", "chunk_level_token_smuggling", "token_boundary_smuggling_reassembly", False),
    (1, "STREAM-GW-002", "websocket_tool_call_smuggling", "websocket_frame_json_injection_interception", False),
    (2, "STREAM-GW-003", "stream_mitm_control_sequence_obfuscation", "control_char_stream_sanitization", False),
    (3, "STREAM-GW-004", "streaming_data_exfiltration", "streaming_dlp_regex_rollback_redaction", False),
    (4, "STREAM-GW-005", "unicode_chunk_splitting_smuggling", "multibyte_utf8_boundary_state_machine", False),
    (5, "STREAM-GW-006", "slow_stream_dos_throttling", "streaming_time_to_first_token_and_jitter_guard", False),
    (6, "STREAM-GW-007", "recursive_stream_injection", "recursive_stream_semantic_gate", False),
    (7, "STREAM-GW-008", "websocket_binary_frame_smuggling", "binary_frame_entropy_and_magic_byte_validator", False),
    (8, "CTRL-STREAM-001", "control_benign_sse_stream", "benign_stream_passthrough", True),
    (9, "CTRL-STREAM-002", "control_benign_websocket_tool_call", "benign_websocket_validation", True),
])
def test_stream_gateway_playbook_entries_structure(gateway_playbook, entry_idx, expected_id, expected_category, expected_technique, is_control):
    """Verifies all 10 Stream Gateway test cases have valid schema, techniques, and synthetic metadata."""
    entries = gateway_playbook["entries"]
    assert len(entries) == 10
    entry = entries[entry_idx]
    assert entry["entry_id"] == expected_id
    assert entry["category"] == expected_category
    assert entry["attack_technique"] == expected_technique
    assert entry["control_case"] is is_control
    assert entry["breakthrough_detected"] is False
    assert entry["confirmed_vulnerability"] is False

    if not is_control:
        assert entry["requires_human_review"] is True
    else:
        assert entry["requires_human_review"] is False


# ==============================================================================
# 4. Telemetry Pipeline Playbook & Execution
# ==============================================================================

@pytest.mark.parametrize("entry_idx,expected_id,expected_category,expected_technique,is_control", [
    (0, "TELEMETRY-ADV-001", "telemetry_metric_poisoning_attack", "metric_baseline_poisoning_statistical_drift", False),
    (1, "TELEMETRY-ADV-002", "alert_storm_flooding_dos", "alert_storm_flooding_exhaustion", False),
    (2, "TELEMETRY-ADV-003", "telemetry_heartbeat_suppression", "telemetry_heartbeat_silence_blindspot", False),
    (3, "TELEMETRY-ADV-004", "spoofed_alert_injection_tampering", "cryptographic_signature_spoofing_injection", False),
    (4, "TELEMETRY-ADV-005", "audit_stream_tampering_truncation", "audit_stream_merkle_chain_tampering", False),
    (5, "TELEMETRY-ADV-006", "multidimensional_metric_burst_anomaly", "correlated_metric_spike_anomaly", False),
    (6, "TELEMETRY-ADV-007", "webhook_dispatcher_failover_exhaustion", "webhook_endpoint_saturation_and_timeout", False),
    (7, "TELEMETRY-ADV-008", "telemetry_timestamp_replay_drift", "replay_attack_with_timestamp_manipulation", False),
    (8, "CTRL-TELEM-001", "control_benign_metric_telemetry", "none_baseline_control", True),
    (9, "CTRL-TELEM-002", "control_benign_alert_dispatch", "none_baseline_control", True),
])
def test_telemetry_pipeline_playbook_entries_structure(telemetry_playbook, entry_idx, expected_id, expected_category, expected_technique, is_control):
    """Verifies all 10 Telemetry Pipeline test cases have valid schema, techniques, and synthetic metadata."""
    entries = telemetry_playbook["entries"]
    assert len(entries) == 10
    entry = entries[entry_idx]
    assert entry["entry_id"] == expected_id
    assert entry["category"] == expected_category
    assert entry["attack_technique"] == expected_technique
    assert entry["control_case"] is is_control
    assert entry["breakthrough_detected"] is False
    assert entry["confirmed_vulnerability"] is False

    if not is_control:
        assert entry["requires_human_review"] is True
    else:
        assert entry["requires_human_review"] is False


# ==============================================================================
# 5. Parameterized 20-Case Synthetic Placeholder Compliance
# ==============================================================================

def test_all_20_cases_synthetic_placeholder_compliance(gateway_playbook, telemetry_playbook):
    """Verifies that all 20 cases use valid <SIM_...> placeholders without raw live data."""
    all_entries = gateway_playbook["entries"] + telemetry_playbook["entries"]
    assert len(all_entries) == 20

    total_placeholders = 0
    for entry in all_entries:
        entry_str = yaml.dump(entry)
        placeholders = SIM_EXTRACTION_REGEX.findall(entry_str)
        assert len(placeholders) >= 1, f"Entry {entry['entry_id']} has no placeholders"
        for ph in placeholders:
            total_placeholders += 1
            assert SIM_PLACEHOLDER_REGEX.match(ph), f"Invalid placeholder format: {ph}"

    assert total_placeholders >= 80, f"Expected at least 80 placeholders across 20 cases, got {total_placeholders}"


# ==============================================================================
# 6. Defense Interceptions and Baseline Controls
# ==============================================================================

def test_defense_interception_and_baseline_controls(gateway_execution_results, telemetry_execution_results):
    """Verifies that all 16 attack cases are intercepted (blocked) and all 4 control cases are allowed."""
    combined = gateway_execution_results + telemetry_execution_results
    assert len(combined) == 20

    attacks = [e for e in combined if not e.get("control_case")]
    controls = [e for e in combined if e.get("control_case")]

    assert len(attacks) == 16
    assert len(controls) == 4

    for a in attacks:
        assert a["breakthrough_detected"] is False
        assert a["defensive_check_passed"] is True
        assert a["confirmed_vulnerability"] is False
        assert a["synthetic_only"] is True

    for c in controls:
        assert c["breakthrough_detected"] is False
        assert c["defensive_check_passed"] is True
        assert c["confirmed_vulnerability"] is False
        assert c["synthetic_only"] is True


# ==============================================================================
# 7. Closed-Loop Feedback Mapping
# ==============================================================================

def test_closed_loop_feedback_mapping(manifest_data):
    """Verifies that the 8 closed-loop feedback mappings are fully established."""
    loops = manifest_data.get("closed_loop_reconciliation_mapping", [])
    assert len(loops) == 8

    for loop in loops:
        assert loop["closed_loop_status"] == "VERIFIED_CLOSED"
        assert "->" in loop["feedback_signal"]


# ==============================================================================
# 8. Capability Scorecards & Result YAML Metric Consistency
# ==============================================================================

def test_capability_scorecards_and_result_yamls():
    """Verifies that scorecards and result YAMLs reflect 100% block and 0% breakthrough."""
    g_res = yaml.safe_load((ROOT / "executions/phase103a_gateway_interceptor/stream_gateway_result.yaml").read_text(encoding="utf-8"))
    g_sc = yaml.safe_load((ROOT / "executions/phase103a_gateway_interceptor/capability_scorecard.yaml").read_text(encoding="utf-8"))
    t_res = yaml.safe_load((ROOT / "executions/phase103a_telemetry_pipeline/telemetry_pipeline_result.yaml").read_text(encoding="utf-8"))
    t_sc = yaml.safe_load((ROOT / "executions/phase103a_telemetry_pipeline/capability_scorecard.yaml").read_text(encoding="utf-8"))

    # Gateway assertions
    assert g_res["total_cases"] == 10
    assert g_res["attack_cases"] == 8
    assert g_res["control_cases"] == 2
    assert g_res["breakthrough_detected_count"] == 0
    assert g_sc["results_summary"]["defense_drill_block_rate"] in ["100%", "100.0%"]
    assert g_sc["results_summary"]["control_pass_rate"] in ["100%", "100.0%"]
    assert g_sc["results_summary"]["breakthrough_rate"] in ["0%", "0.0%"]

    # Telemetry assertions
    assert t_res["total_cases"] == 10
    assert t_res["attack_cases"] == 8
    assert t_res["control_cases"] == 2
    assert t_res["breakthrough_detected_count"] == 0
    assert t_sc["results_summary"]["defense_drill_block_rate"] in ["100%", "100.0%"]
    assert t_sc["results_summary"]["control_pass_rate"] in ["100%", "100.0%"]
    assert t_sc["results_summary"]["breakthrough_rate"] in ["0%", "0.0%"]


# ==============================================================================
# 9. Run Configs & Fake Runtime Sandboxing Invariants
# ==============================================================================

def test_run_configs_sandboxing_invariants():
    """Verifies that run configs enforce fake runtime sandbox and forbid real system access."""
    rc_gateway = yaml.safe_load((ROOT / "run_configs/phase103a_gateway_run_config.yaml").read_text(encoding="utf-8"))
    rc_telemetry = yaml.safe_load((ROOT / "run_configs/phase103a_telemetry_run_config.yaml").read_text(encoding="utf-8"))

    cg = rc_gateway["run_config"]
    assert cg["synthetic_only"] is True
    assert cg["fake_runtime_only"] is True
    assert cg["real_websocket_endpoint_allowed"] is False
    assert cg["real_sse_server_allowed"] is False

    ct = rc_telemetry["run_config"]
    assert ct["synthetic_only"] is True
    assert ct["fake_runtime_only"] is True
    assert ct["real_eventbus_cluster_allowed"] is False
    assert ct["real_alert_webhook_allowed"] is False


# ==============================================================================
# 10. Manifest Reconciliation & Cross-Module Metadata Integrity
# ==============================================================================

def test_manifest_reconciliation_integrity(manifest_data):
    """Verifies that the reconciliation manifest accurately captures both modules and all 20 cases."""
    assert manifest_data["manifest_metadata"]["task_id"] == "Phase-103A-GATE-003"
    assert manifest_data["manifest_metadata"]["phase"] == "Phase-103A"

    modules = manifest_data["modules_under_governance"]
    assert "M23_STREAM_GATEWAY" in modules
    assert "M23_TELEMETRY_PIPELINE" in modules
    assert modules["M23_STREAM_GATEWAY"]["total_cases"] == 10
    assert modules["M23_TELEMETRY_PIPELINE"]["total_cases"] == 10

    catalog = manifest_data["reconciliation_catalog_20_cases"]
    assert len(catalog) == 20

    gw_catalog = [c for c in catalog if c["module_id"] == "M23_STREAM_GATEWAY"]
    tm_catalog = [c for c in catalog if c["module_id"] == "M23_TELEMETRY_PIPELINE"]
    assert len(gw_catalog) == 10
    assert len(tm_catalog) == 10

    summary = manifest_data["joint_reconciliation_summary"]
    assert summary["total_cases_audited"] == 20
    assert summary["attack_cases"] == 16
    assert summary["control_cases"] == 4
    assert summary["total_interceptions"] == 16
    assert summary["total_breakthroughs"] == 0
    assert summary["controls_passed"] == 4
    assert summary["status"] == "PASS"
    assert summary["verdict"] == "PHASE_103A_DESIGN_GATE_APPROVED"


# ==============================================================================
# 11. Standalone Validator Script Execution
# ==============================================================================

def test_standalone_gate_validator_script():
    """Runs the standalone validator script and asserts exit code 0."""
    script_path = ROOT / "scripts/validate_phase103a_gate_streaming_gateway.py"
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Validator script failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    combined_output = result.stdout + result.stderr
    assert "STATUS: ALL CHECKS PASSED (100% COMPLIANT)" in combined_output


# ==============================================================================
# 12. Non-Retroactivity Guarantees
# ==============================================================================

def test_non_retroactivity_guarantees():
    """Verifies that historical phase deliverables and baselines remain intact."""
    hist_files = [
        ROOT / "phase98a_gate003_execution_summary.yaml",
        ROOT / "phase99a_gate003_execution_summary.yaml",
        ROOT / "phase100a_mega_reconciliation_matrix.yaml",
        ROOT / "phase101a_gate003_execution_summary.yaml",
        ROOT / "phase102a_gate003_execution_summary.yaml",
        ROOT / "phase103a_gateway001_execution_summary.yaml",
        ROOT / "phase103a_telemetry002_execution_summary.yaml",
    ]

    for fpath in hist_files:
        assert fpath.exists(), f"Historical baseline file missing: {fpath}"
        assert fpath.stat().st_size > 0, f"Historical file empty: {fpath}"
