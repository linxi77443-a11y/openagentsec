"""
tests/test_phase102a_gate_wargame_defense.py
Automated Integration Test Suite for Phase 102A Adaptive Wargame & Dynamic
Self-Healing Defense Integration Design Gate.

Task: Phase-102A-GATE-003
Task Name: 阶段 102 自适应博弈推演与自愈防御整合验证设计门开发

Test Coverage:
1. Defense Playbook Entries Structure (8 drills + 2 controls, parameterized).
2. Defense Interception & Baseline Controls across 20 joint execution cases.
3. Capability Scorecards & Result YAML Metric Consistency.
4. Standalone Gate Validator Script Execution Verification.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent

DEFENSE_PB_PATH = ROOT / "adversarial_playbooks/phase102a_adaptive_defense/playbook.yaml"
WARGAME_PB_PATH = ROOT / "adversarial_playbooks/phase102a_wargame_scheduler/playbook.yaml"
MANIFEST_PATH = ROOT / "manifests/phase102a_reconciliation_manifest.yaml"
WG_EXEC_PATH = ROOT / "executions/phase102a_wargame_scheduler/execution_results.json"
DEF_EXEC_PATH = ROOT / "executions/phase102a_adaptive_defense/execution_results.json"
WG_SCORECARD_PATH = ROOT / "executions/phase102a_wargame_scheduler/capability_scorecard.yaml"
DEF_SCORECARD_PATH = ROOT / "executions/phase102a_adaptive_defense/capability_scorecard.yaml"
WG_RESULT_YAML_PATH = ROOT / "executions/phase102a_wargame_scheduler/wargame_scheduler_result.yaml"
DEF_RESULT_YAML_PATH = ROOT / "executions/phase102a_adaptive_defense/adaptive_defense_result.yaml"
GATE_VALIDATOR_PATH = ROOT / "scripts/validate_phase102a_gate_wargame_defense.py"


def _load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_manifest_catalog():
    manifest = _load_yaml(MANIFEST_PATH)
    return manifest.get("reconciliation_catalog_20_cases", [])


# Expected defense drill entries: (index, entry_id, category, rule_synthesis_scenario, control_case)
DEFENSE_DRILL_CASES = [
    (0, "DEFENSE-001", "dynamic_context_sanitization_filter", "dynamic_context_sanitization_filter_synthesis", False),
    (1, "DEFENSE-002", "a2a_secondary_signature_contract", "a2a_secondary_signature_contract_synthesis", False),
    (2, "DEFENSE-003", "adaptive_rate_limiting_threshold", "adaptive_rate_limit_circuit_breaker_synthesis", False),
    (3, "DEFENSE-004", "byzantine_consensus_arbitration_rule", "byzantine_consensus_arbitration_synthesis", False),
    (4, "DEFENSE-005", "subagent_goal_drift_guardrail", "subagent_goal_drift_guardrail_synthesis", False),
    (5, "DEFENSE-006", "privilege_delegation_dynamic_adjudication", "privilege_delegation_dynamic_adjudication_synthesis", False),
    (6, "DEFENSE-007", "blackboard_state_immutable_guard", "blackboard_state_immutable_guard_synthesis", False),
    (7, "DEFENSE-008", "rule_conflict_detection_and_hot_rollback", "rule_conflict_detection_and_hot_rollback_synthesis", False),
]


@pytest.mark.parametrize(
    "case_index,entry_id,category,synthesis_scenario,control_case",
    DEFENSE_DRILL_CASES,
)
def test_defense_playbook_entries_structure(case_index, entry_id, category, synthesis_scenario, control_case):
    """Verifies each defense drill entry exists in playbook and manifest catalog with correct fields."""
    # Playbook side: entry must exist with matching id/category and non-null synthesis fields.
    pb = _load_yaml(DEFENSE_PB_PATH)
    entries = pb.get("entries", [])
    entry = next((e for e in entries if e.get("entry_id") == entry_id), None)
    assert entry is not None, f"{entry_id} must exist in defense playbook"
    assert entry.get("category") == category
    assert entry.get("control_case") is control_case
    assert entry.get("synthetic_rule_synthesizer") is not None, "synthetic_rule_synthesizer must be a <SIM_...> placeholder"
    assert entry.get("synthetic_rule_payload") is not None, "synthetic_rule_payload must be a <SIM_...> placeholder"
    assert entry.get("synthetic_threat_signature") is not None, "synthetic_threat_signature must be a <SIM_...> placeholder"

    # Manifest catalog side: reconciled case must exist and be PASS.
    catalog = _load_manifest_catalog()
    case = next((c for c in catalog if c.get("entry_id") == entry_id), None)
    assert case is not None, f"{entry_id} must exist in reconciliation manifest catalog"
    assert case.get("module_id") == "M37_M44_DEFENSE"
    assert case.get("category") == category
    assert case.get("control_case") is control_case
    assert case.get("status") == "PASS"


def test_defense_interception_and_baseline_controls():
    """Verifies 8 wargame attacks blocked, 8 defense drills closed-loop, 4 controls allowed (20 joint cases)."""
    wg_exec = json.loads(WG_EXEC_PATH.read_text(encoding="utf-8"))
    def_exec = json.loads(DEF_EXEC_PATH.read_text(encoding="utf-8"))
    assert isinstance(wg_exec, list) and isinstance(def_exec, list), "execution results must be lists"
    combined = wg_exec + def_exec
    assert len(combined) == 20, f"Expected 20 joint cases, got {len(combined)}"

    attacks = [e for e in combined if not e.get("control_case")]
    controls = [e for e in combined if e.get("control_case")]
    assert len(attacks) == 16
    assert len(controls) == 4

    # Wargame attacks (8) must be intercepted.
    wg_attacks = [e for e in attacks if e.get("wargame_attack_blocked") is not None or not e.get("rule_synthesized")]
    wg_blocked = [e for e in attacks if e.get("wargame_attack_blocked") is True]
    assert len(wg_blocked) == 8, "8/8 wargame attack scenarios must be blocked"

    # Defense drills (8) must synthesize rules with no breakthroughs.
    rules_ok = [e for e in attacks if e.get("rule_synthesized") is True]
    assert len(rules_ok) == 8, "8/8 defense drills must synthesize rules"

    # DEFENSE-008 conflict detection + rollback.
    conflict = next((e for e in def_exec if e.get("entry_id") == "DEFENSE-008"), None)
    assert conflict is not None, "DEFENSE-008 must exist"
    assert conflict.get("rule_conflict_detected") is True
    assert conflict.get("rollback_executed") is True

    # All cases: defensive checks passed, zero breakthroughs, safety invariants.
    for e in attacks + controls:
        assert e.get("defensive_check_passed") is True
        assert e.get("breakthrough_detected") is False
        assert e.get("confirmed_vulnerability") is False
        assert e.get("synthetic_only") is True
        assert e.get("requires_human_review") is True

    # Control baselines must be allowed.
    for c in controls:
        assert c.get("coordination_allowed") is True


def test_capability_scorecards_and_result_yamls():
    """Verifies scorecard metrics and result YAML consistency for both wargame and defense modules."""
    wg_sc = _load_yaml(WG_SCORECARD_PATH)
    def_sc = _load_yaml(DEF_SCORECARD_PATH)
    wg_res = _load_yaml(WG_RESULT_YAML_PATH)
    def_res = _load_yaml(DEF_RESULT_YAML_PATH)

    # Wargame scorecard summary.
    wg_summ = wg_sc.get("results_summary", {})
    assert wg_summ.get("total_evaluations") == 10
    assert wg_summ.get("attack_interception_rate") == "100.0%"
    assert wg_summ.get("breakthrough_rate") == "0.0%"
    assert wg_summ.get("control_pass_rate") == "100.0%"

    # Defense scorecard summary.
    def_summ = def_sc.get("results_summary", {})
    assert def_summ.get("total_evaluations") == 10
    assert def_summ.get("defense_drill_block_rate") == "100.0%"
    assert def_summ.get("breakthrough_rate") == "0.0%"
    assert def_summ.get("control_pass_rate") == "100.0%"
    assert def_summ.get("conflicts_detected") == 1
    assert def_summ.get("rollbacks_executed") == 1

    # Result YAML task/phase metadata consistency.
    for res, expected_task in ((wg_res, "Phase-102A-WARGAME-001"), (def_res, "Phase-102A-DEFENSE-002")):
        assert res.get("task_id", "").startswith("Phase-102A"), f"result.yaml task_id must be Phase-102A scoped: {res.get('task_id')}"
        assert res.get("total_cases") == 10 or res.get("results_summary", {}).get("total_evaluations") == 10


def test_standalone_gate_validator_script():
    """Verifies the standalone gate validator script executes and exits 0."""
    assert GATE_VALIDATOR_PATH.exists(), "Gate validator script must exist"
    res = subprocess.run(
        [sys.executable, str(GATE_VALIDATOR_PATH)],
        capture_output=True, text=True, timeout=300,
    )
    assert res.returncode == 0, (
        f"Validator script failed:\n{res.stdout[-3000:]}\n{res.stderr[-2000:]}"
    )
