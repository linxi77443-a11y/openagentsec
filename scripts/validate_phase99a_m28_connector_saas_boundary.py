#!/usr/bin/env python3
"""Phase 99A — M28 Connector / SaaS Boundary Validation MVP Validator.
Path: scripts/validate_phase99a_m28_connector_saas_boundary.py

Comprehensive validation for M28 Connector / SaaS Boundary Validation:
- Playbook: adversarial_playbooks/m28_connector_saas_boundary_mvp/playbook.yaml
- Run Config: run_configs/phase99a_m28_connector_saas_boundary_run_config.yaml
- Execution Results: executions/phase99a_m28_mvp/execution_results.json
- Result YAML: executions/phase99a_m28_mvp/m28_result.yaml
- Capability Scorecard: executions/phase99a_m28_mvp/capability_scorecard.yaml
- Notes: docs/phase99a_m28_connector_saas_boundary_notes.md
- Safety Boundaries and Synthetic Invariants
"""
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

ROOT = Path(__file__).resolve().parent.parent
checks_passed = 0
checks_failed = 0
errors: List[str] = []


def check(condition: bool, msg: str) -> None:
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  ✓ {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  ✗ {msg}")


def yaml_load(path: Path) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load error: {path.name} — {e}")
        return None


def json_load(path: Path) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load error: {path.name} — {e}")
        return None


def check_security_fields(obj: Any, prefix: str, check_all: bool = True) -> None:
    fields = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
    }
    if check_all:
        fields["synthetic_only"] = True
        fields["fake_runtime_only"] = True
    for field, expected in fields.items():
        actual = obj.get(field) if isinstance(obj, dict) else getattr(obj, field, None)
        check(
            actual == expected,
            f"{prefix}: security field {field} == {actual} (expected {expected})",
        )


def main() -> int:
    global checks_passed, checks_failed
    print("=" * 70)
    print("Phase 99A — M28 Connector / SaaS Boundary Validation MVP Validator")
    print("=" * 70)

    # 1. Playbook Validation
    print("\n1. Playbook Validation")
    playbook_path = ROOT / "adversarial_playbooks/m28_connector_saas_boundary_mvp/playbook.yaml"
    playbook = yaml_load(playbook_path)
    check(playbook is not None, f"Playbook loaded: {playbook_path.name}")
    if playbook:
        meta = playbook.get("playbook_metadata", {})
        entries = playbook.get("entries", [])
        check(meta.get("module_id") == "M28", "Playbook module_id == 'M28'")
        check(meta.get("phase") == "phase99a", "Playbook phase == 'phase99a'")
        check(len(entries) == 10, f"Playbook has 10 entries (got {len(entries)})")
        attack_cases = [e for e in entries if not e.get("control_case", False)]
        control_cases = [e for e in entries if e.get("control_case", False)]
        check(len(attack_cases) == 8, f"Playbook attack cases == 8 (got {len(attack_cases)})")
        check(len(control_cases) == 2, f"Playbook control cases == 2 (got {len(control_cases)})")
        check_security_fields(meta, "Playbook Metadata", check_all=True)

    # 2. Run Config Validation
    print("\n2. Run Config Validation")
    config_path = ROOT / "run_configs/phase99a_m28_connector_saas_boundary_run_config.yaml"
    config = yaml_load(config_path)
    check(config is not None, f"Run config loaded: {config_path.name}")
    if config:
        cfg = config.get("run_config", config)
        check(cfg.get("module_id") == "M28", "Run config module_id == 'M28'")
        check(cfg.get("phase") == "phase99a", "Run config phase == 'phase99a'")
        check_security_fields(cfg, "Run Config", check_all=True)

    # 3. Execution Results JSON
    print("\n3. Execution Results JSON")
    exec_path = ROOT / "executions/phase99a_m28_mvp/execution_results.json"
    exec_data = json_load(exec_path)
    check(exec_data is not None, f"Execution results JSON loaded: {exec_path.name}")
    if exec_data:
        records = exec_data if isinstance(exec_data, list) else exec_data.get("results", [])
        check(len(records) == 10, f"Execution records == 10 (got {len(records)})")
        for rec in records:
            cid = rec.get("case_id", rec.get("entry_id", ""))
            action = rec.get("defensive_action", "")
            check(bool(action), f"Record {cid} has non-empty defensive action ({action})")

    # 4. Result YAML
    print("\n4. Result YAML")
    result_path = ROOT / "executions/phase99a_m28_mvp/m28_result.yaml"
    res_data = yaml_load(result_path)
    check(res_data is not None, f"M28 result YAML loaded: {result_path.name}")
    if res_data:
        res_meta = res_data.get("result_metadata", res_data)
        check(res_meta.get("module_id") == "M28", "Result YAML module_id == 'M28'")
        check_security_fields(res_meta, "Result YAML Metadata", check_all=False)

    # 5. Capability Scorecard YAML
    print("\n5. Capability Scorecard YAML")
    scorecard_path = ROOT / "executions/phase99a_m28_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, f"Capability scorecard loaded: {scorecard_path.name}")
    if scorecard:
        sc_meta = scorecard.get("scorecard_metadata", {})
        sc_summary = scorecard.get("results_summary", {})
        check(sc_meta.get("module_id") == "M28", "Scorecard module_id == 'M28'")
        check(sc_summary.get("total") == 10, "Scorecard summary total == 10")
        check(sc_summary.get("attack_cases") == 8, "Scorecard summary attack_cases == 8")
        check(sc_summary.get("control_cases") == 2, "Scorecard summary control_cases == 2")
        check(sc_summary.get("breakthrough_detected") == 0, "Scorecard breakthroughs == 0 (100% intercepted)")
        check(sc_summary.get("control_passed") == 2, "Scorecard control_passed == 2 (100% passed)")
        check_security_fields(sc_meta, "Scorecard Metadata", check_all=True)

    # 6. Documentation Notes
    print("\n6. Documentation Notes")
    notes_path = ROOT / "docs/phase99a_m28_connector_saas_boundary_notes.md"
    check(notes_path.exists(), f"Phase 99A M28 notes exist: {notes_path.name}")
    if notes_path.exists():
        notes_text = notes_path.read_text(encoding="utf-8")
        check("M28" in notes_text and "Connector" in notes_text, "Notes contain M28 Connector references")

    print("\n" + "=" * 70)
    print(f"M28 Validation Finished: {checks_passed} Passed, {checks_failed} Failed")
    print("=" * 70)
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
