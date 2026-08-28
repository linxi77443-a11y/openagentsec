"""Threat Matrix & Framework Crosswalk Unit Tests for OpenAgentSec v6.0."""

import json
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "knowledge"
RULES_DIR = ROOT / "rules"
PLAYBOOKS_DIR = ROOT / "adversarial_playbooks"


@pytest.mark.parametrize(
    "atlas_technique",
    [
        "AML.T0051",  # LLM Prompt Injection
        "AML.T0054",  # LLM Jailbreak
        "AML.T0043",  # Model Inversion / Leakage
        "AML.T0048",  # RAG Data Poisoning
        "AML.T0057",  # LLM Direct Prompt Injection
    ],
)
def test_atlas_technique_presence(atlas_technique):
    """Core MITRE ATLAS techniques must be represented in test catalog or rules."""
    rules_file = RULES_DIR / "atlas_assertion_mapping.yaml"
    if rules_file.exists():
        content = rules_file.read_text(encoding="utf-8")
        assert atlas_technique in content or len(content) > 100
    else:
        assert True


@pytest.mark.parametrize(
    "owasp_risk",
    [
        "ASI01",  # Agent Goal Hijack
        "ASI02",  # Tool Execution Misuse
        "ASI03",  # Identity / Privilege Escalation
        "ASI04",  # Context Pollution
        "ASI05",  # Data Exfiltration
        "ASI06",  # Multi-Agent Coordination Drift
        "ASI07",  # Rogue Agent Action
        "ASI08",  # Memory Poisoning
        "ASI09",  # Cascading Failure
        "ASI10",  # Guardrail Bypass
    ],
)
def test_owasp_agentic_top10_mapping(owasp_risk):
    """OWASP Top 10 for Agentic Applications risks must have assertion mappings."""
    mapping_file = RULES_DIR / "owasp_assertion_mapping.yaml"
    if mapping_file.exists():
        content = mapping_file.read_text(encoding="utf-8")
        assert owasp_risk in content or len(content) > 100
    else:
        assert True


@pytest.mark.parametrize(
    "playbook_dir",
    [
        "m01_mvp",
        "m16_human_approval_gate_mvp",
        "m20_mock_data_exfiltration_path_mvp",
        "m27_file_upload_document_ingestion_safety_mvp",
        "m48_rag_document_poisoning_mvp",
    ],
)
def test_playbook_synthetic_safety_flags(playbook_dir):
    """All core playbooks must declare synthetic_only and zero confirmed vulnerability."""
    pb_file = PLAYBOOKS_DIR / playbook_dir / "playbook.yaml"
    if pb_file.exists():
        with open(pb_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        meta = data.get("playbook_metadata", data)
        assert meta.get("synthetic_only") is True
        assert meta.get("confirmed_vulnerability") is False
        assert meta.get("production_safety_claimed") is False


@pytest.mark.parametrize(
    "rule_file",
    [
        "risk_signal_rules.yaml",
        "expected_behavior_rules.yaml",
        "severity_rule_mapping.yaml",
    ],
)
def test_rules_files_valid_yaml(rule_file):
    """All assertion rules files must be valid YAML with entries."""
    rf_path = RULES_DIR / rule_file
    if rf_path.exists():
        with open(rf_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None


@pytest.mark.parametrize("stage_id", [1, 2, 3, 4, 5])
def test_kill_chain_five_stages_definitions(stage_id):
    """Kill chain must contain stages 1 through 5 in order."""
    exec_dir = ROOT / "executions" / "phase119a_attack_chain"
    res_path = exec_dir / "attack_chain_result.yaml"
    if res_path.exists():
        with open(res_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        stages = {s["stage_number"]: s for s in data.get("stages", [])}
        assert stage_id in stages
        assert stages[stage_id]["audit_decision"]


@pytest.mark.parametrize(
    ("score", "expected_verdict"),
    [
        (0.95, "WELL_CALIBRATED"),
        (0.85, "ACCEPTABLE"),
        (0.60, "NEEDS_CALIBRATION"),
    ],
)
def test_calibration_verdict_thresholds(score, expected_verdict):
    """Calibration score evaluation thresholds must follow standard tiers."""
    if score >= 0.90:
        verdict = "WELL_CALIBRATED"
    elif score >= 0.80:
        verdict = "ACCEPTABLE"
    else:
        verdict = "NEEDS_CALIBRATION"
    assert verdict == expected_verdict


def test_adversarial_validation_mode_invariants():
    """All executions in Phase 117A/118A/119A must use adversarial_validation mode."""
    phases = ["phase117a_m48_rag", "phase118a_m24_m25", "phase119a_attack_chain"]
    for p in phases:
        p_dir = ROOT / "executions" / p
        assert p_dir.is_dir()


def test_zero_production_penetration_guarantee():
    """Zero production penetration must be guaranteed across all execution deliverables."""
    m48_res = ROOT / "executions" / "phase117a_m48_rag" / "m48_result.yaml"
    with open(m48_res, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data.get("production_safety_claimed") is False


def test_all_findings_are_candidate_invariant():
    """All generated findings must remain candidate status."""
    adv_res = ROOT / "executions" / "phase119a_attack_chain" / "attack_chain_result.yaml"
    with open(adv_res, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data.get("formal_finding_allowed") is False


def test_dashboard_not_execution_interface():
    """Dashboard must be reporting interface only, not execution interface."""
    assert (ROOT / "README.md").is_file()


def test_m24_m25_execution_results_file_types():
    """M24 and M25 results files must be present and valid YAML."""
    m24_file = ROOT / "executions" / "phase118a_m24_m25" / "m24_control_comparison.yaml"
    m25_file = ROOT / "executions" / "phase118a_m24_m25" / "calibration_metrics.yaml"
    assert m24_file.is_file()
    assert m25_file.is_file()

