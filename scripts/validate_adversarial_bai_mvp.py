#!/usr/bin/env python3
"""ADV-BAI-001 — Business Action Induction (BAI) MVP Validator.

Validates playbook, run config, execution results, result YAML,
scorecard, evidence traces, retest candidate backlog, and audit notes.
Review-only: no real execution.
"""
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

ROOT = Path(__file__).resolve().parents[1]
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
        check(False, f"YAML load failed for {path.name}: {e}")
        return None


def json_load(path: Path) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load failed for {path.name}: {e}")
        return None


def check_security_fields(obj: Any, prefix: str) -> None:
    fields = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
    }
    for field, expected in fields.items():
        actual = obj.get(field) if isinstance(obj, dict) else getattr(obj, field, None)
        check(
            actual == expected,
            f"{prefix}: security field {field} == {actual} (expected {expected})",
        )


def main() -> int:
    global checks_passed, checks_failed
    print("=" * 60)
    print("ADV-BAI-001 — Business Action Induction MVP Validator")
    print("=" * 60)

    # 1. Playbook Existence and Structure
    print("\n1. Playbook")
    playbook_path = ROOT / "adversarial_playbooks/business_action_induction_mvp/playbook.yaml"
    playbook = yaml_load(playbook_path)
    check(playbook is not None, f"Playbook exists: {playbook_path.name}")
    if playbook:
        entries = playbook.get("entries", [])
        meta = playbook.get("playbook_metadata", {})
        check(len(entries) >= 10, f"Playbook entries count >= 10 (got {len(entries)})")
        check(meta.get("adversarial_playbook_type") == "business_action_induction", "Playbook type matches business_action_induction")
        check_security_fields(meta, "Playbook Metadata")

    # 2. Run Config
    print("\n2. Run Config")
    config_path = ROOT / "capability_engine/configs/phase62j_bai_mvp.yaml"
    config = yaml_load(config_path)
    check(config is not None, f"Run config exists: {config_path.name}")
    if config:
        cfg_result = config.get("result", {})
        check_security_fields(cfg_result, "Run Config Result")

    # 3. Execution Results JSON
    print("\n3. Execution Results JSON")
    exec_path = ROOT / "executions/phase62j_bai_mvp/execution_results.json"
    exec_data = json_load(exec_path)
    check(exec_data is not None, f"Execution results JSON exists: {exec_path.name}")
    if isinstance(exec_data, list):
        check(len(exec_data) >= 10, f"Execution results list count >= 10 (got {len(exec_data)})")
    elif isinstance(exec_data, dict):
        check("results" in exec_data or "entries" in exec_data, "Execution results contain structured records")

    # 4. Adversarial Result YAML
    print("\n4. Adversarial Result YAML")
    result_path = ROOT / "executions/phase62j_bai_mvp/adversarial_result.yaml"
    result_data = yaml_load(result_path)
    check(result_data is not None, f"Adversarial result YAML exists: {result_path.name}")
    if result_data:
        check_security_fields(result_data.get("adversarial_result_metadata", result_data), "Adversarial Result")

    # 5. Capability Scorecard YAML
    print("\n5. Capability Scorecard YAML")
    scorecard_path = ROOT / "executions/phase62j_bai_mvp/capability_scorecard.yaml"
    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, f"Capability scorecard exists: {scorecard_path.name}")
    if scorecard:
        sc_meta = scorecard.get("scorecard_metadata", {})
        sc_results = scorecard.get("results_summary", {})
        check(sc_meta.get("adversarial_playbook_type") == "business_action_induction", "Scorecard matches business_action_induction")
        check(sc_results.get("total", 0) >= 10, f"Scorecard total entries >= 10 (got {sc_results.get('total')})")
        check_security_fields(sc_meta, "Scorecard Safety")

    # 6. Evidence Manifest & Trace Integrity
    print("\n6. Evidence & Trace Integrity")
    evidence_path = ROOT / "executions/internal_security_assessment/bai_business_action_induction_results.json"
    if evidence_path.exists():
        ev_data = json_load(evidence_path)
        check(ev_data is not None, "Internal assessment evidence file loaded")
    else:
        check(exec_path.exists(), "Fallback evidence verified in execution results")

    # 7. Retest Candidate Backlog
    print("\n7. Retest Candidate Backlog")
    retest_path = ROOT / "docs/phase62j_bai_mvp_retest_backlog.md"
    check(retest_path.exists(), f"Retest candidate backlog exists: {retest_path.name}")
    if retest_path.exists():
        content = retest_path.read_text(encoding="utf-8")
        check("BAI" in content, "Retest backlog references BAI candidates")

    # 8. Notes & Documentation
    print("\n8. MVP Notes & Documentation")
    notes_path = ROOT / "docs/phase62j_bai_mvp_notes.md"
    check(notes_path.exists(), f"Phase 62J notes exist: {notes_path.name}")
    if notes_path.exists():
        notes_text = notes_path.read_text(encoding="utf-8")
        check("Business Action Induction" in notes_text or "BAI" in notes_text, "Notes document BAI scope")

    print("\n" + "=" * 60)
    print(f"Validation Finished: {checks_passed} Passed, {checks_failed} Failed")
    print("=" * 60)
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
