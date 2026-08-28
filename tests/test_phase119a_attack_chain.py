"""Phase 119A — ADV-86 Authorized Attack Chain Simulation Tests."""

import json
from pathlib import Path
import jsonschema
import pytest
import yaml

from scripts.validate_phase119a_attack_chain import validate

ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = ROOT / "executions" / "phase119a_attack_chain"


def test_kill_chain_schema_validity():
    """kill_chain_schema.yaml must exist and define proper draft schema."""
    schema_path = EXEC_DIR / "kill_chain_schema.yaml"
    assert schema_path.is_file()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    assert schema["$schema"]
    assert "chain_id" in schema["required"]
    assert "stages" in schema["required"]


def test_multi_turn_trace_execution_sequence():
    """trace.jsonl must contain exactly 5 sequential kill chain stages."""
    trace_path = EXEC_DIR / "trace.jsonl"
    assert trace_path.is_file()

    records = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(records) == 5

    stages = [r["stage"] for r in records]
    assert stages == [
        "reconnaissance",
        "initial_access",
        "privilege_escalation",
        "lateral_movement",
        "exfiltration",
    ]


def test_exfiltration_hard_halt_enforcement():
    """The final exfiltration step must be intercepted with hard_intercept_halted."""
    trace_path = EXEC_DIR / "trace.jsonl"
    records = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    final_step = records[-1]
    assert final_step["stage"] == "exfiltration"
    assert final_step["audit_intercepted"] is True
    assert final_step["audit_decision"] == "hard_intercept_halted"
    assert "HARD_BLOCK" in final_step["engine_halt_reason"]


def test_attack_chain_result_against_schema():
    """attack_chain_result.yaml must strictly conform to kill_chain_schema.yaml."""
    schema_path = EXEC_DIR / "kill_chain_schema.yaml"
    result_path = EXEC_DIR / "attack_chain_result.yaml"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    with open(result_path, "r", encoding="utf-8") as f:
        res = yaml.safe_load(f)

    jsonschema.validate(instance=res, schema=schema)
    assert res["chain_id"] == "ADV-86-SIM-001"
    assert res["halted_at_stage"] == 5
    assert res["data_exfiltration_prevented"] is True
    assert res["breakthrough_detected"] is False
    assert res["synthetic_only"] is True


def test_defense_audit_summary_metrics():
    """defense_audit_summary.yaml must reflect complete coverage and effective defense."""
    summary_path = EXEC_DIR / "defense_audit_summary.yaml"
    assert summary_path.is_file()

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = yaml.safe_load(f)

    assert summary["synthetic_only"] is True
    assert summary["kill_chain_monitoring"]["halt_event_triggered"] is True
    assert summary["defense_assessment"]["exfiltration_hard_block"] == "effective"


def test_phase119a_validator_script():
    """Phase 119A validator script must pass all checks with zero failures."""
    result = validate()
    assert result["failed"] == 0
    assert result["passed"] >= 8
    assert result["safety_booleans_all_false"] is True
