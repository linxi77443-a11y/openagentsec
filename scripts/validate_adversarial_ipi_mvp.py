#!/usr/bin/env python3
"""Phase 62C — Indirect Prompt Injection MVP Validation Script."""
import sys, json, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/indirect_prompt_injection_mvp/playbook.yaml"
RUN_CONFIG_PATH = ROOT / "capability_engine/configs/phase62c_ipi_mvp.yaml"
EXEC_DIR = ROOT / "executions/phase62c_ipi_mvp"
EXEC_RESULTS_PATH = EXEC_DIR / "execution_results.json"
SCORECARD_PATH = EXEC_DIR / "capability_scorecard.yaml"
ADV_RESULT_PATH = EXEC_DIR / "adversarial_result.yaml"

EXPECTED_ENTRY_IDS = [
    "IPI-001", "IPI-002", "IPI-003", "IPI-004", "IPI-005",
    "IPI-006", "IPI-007", "IPI-008", "IPI-009", "IPI-010",
    "IPI-011", "IPI-012", "IPI-901", "IPI-902",
]

EXPECTED_CATEGORIES = [
    "rag_poisoning", "tool_output_poisoning", "pasted_content_injection",
    "email_content_injection", "document_metadata_injection",
    "code_repository_poisoning", "control",
]

checks = []


def check(name: str, condition: bool, detail: str = ""):
    checks.append({"name": name, "pass": condition, "detail": detail})
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def validate_playbook():
    print("\n--- Playbook Validation ---")
    exists = PLAYBOOK_PATH.exists()
    check("Playbook file exists", exists, str(PLAYBOOK_PATH))
    if not exists:
        return False

    pb = load_yaml(PLAYBOOK_PATH)
    meta = pb.get("playbook_metadata", {})

    check("playbook_metadata present", bool(meta))
    check("assessment_mode = adversarial_validation", meta.get("assessment_mode") == "adversarial_validation")
    check("adversarial_playbook_type = indirect_prompt_injection", meta.get("adversarial_playbook_type") == "indirect_prompt_injection")
    check("actor defined", bool(meta.get("actor")))
    check("attacker_profile defined", bool(meta.get("attacker_profile")))
    check("attacker_type defined", bool(meta.get("attacker_type")))
    check("attack_objective = context_poisoning", meta.get("attack_objective") == "context_poisoning")

    entries = pb.get("entries", [])
    eids = [e["entry_id"] for e in entries]
    check("playbook has entries", len(entries) > 0, f"{len(entries)} entries")

    missing_ids = [eid for eid in EXPECTED_ENTRY_IDS if eid not in eids]
    extra_ids = [eid for eid in eids if eid not in EXPECTED_ENTRY_IDS]
    check("all expected entry IDs present", len(missing_ids) == 0, f"missing: {missing_ids}" if missing_ids else "all 14 present")
    check("no unexpected entry IDs", len(extra_ids) == 0, f"extra: {extra_ids}" if extra_ids else "no extras")

    for e in entries:
        eid = e.get("entry_id", "?")
        check(f"{eid}: category defined", bool(e.get("category")))
        check(f"{eid}: expected_behavior defined", bool(e.get("expected_behavior")))
        check(f"{eid}: expected_signal defined", bool(e.get("expected_signal")) or e.get("control_case"))
        check(f"{eid}: control_case defined", "control_case" in e)

    cats = set(e["category"] for e in entries)
    for cat in EXPECTED_CATEGORIES:
        check(f"category '{cat}' present", cat in cats)

    controls = [e for e in entries if e.get("control_case")]
    check("control cases present (>= 2)", len(controls) >= 2)
    for c in controls:
        check(f"control {c['entry_id']}: expected_behavior = normal_response", c.get("expected_behavior") == "normal_response")
        check(f"control {c['entry_id']}: expected_signal = none", c.get("expected_signal") == "none")

    return True


def validate_run_config():
    print("\n--- Run Config Validation ---")
    exists = RUN_CONFIG_PATH.exists()
    check("Run config file exists", exists, str(RUN_CONFIG_PATH))
    if not exists:
        return
    rc = load_yaml(RUN_CONFIG_PATH)
    check("run_id = phase62c-ipi-mvp", rc.get("run_id") == "phase62c-ipi-mvp")
    check("assessment_mode = adversarial_validation", rc.get("assessment_mode") == "adversarial_validation")
    check("adversarial_playbook_type = indirect_prompt_injection", rc.get("adversarial_playbook_type") == "indirect_prompt_injection")
    for fld in ["confirmed_vulnerability", "formal_finding_allowed", "production_safety_claimed", "controlled_replay_claimed"]:
        check(f"{fld} = false", rc.get("result", {}).get(fld) is False)


def validate_execution_results():
    print("\n--- Execution Results Validation ---")
    exists = EXEC_RESULTS_PATH.exists()
    check("execution_results.json exists", exists, str(EXEC_RESULTS_PATH))
    if not exists:
        return
    results = load_json(EXEC_RESULTS_PATH)
    check("results is a list", isinstance(results, list), f"{len(results)} entries")
    check("all 14 entries present", len(results) == 14)

    eids = [r["entry_id"] for r in results]
    for eid in EXPECTED_ENTRY_IDS:
        check(f"result for {eid} present", eid in eids)

    for r in results:
        eid = r.get("entry_id", "?")
        check(f"{eid}: breakthrough_detected defined", "breakthrough_detected" in r)
        check(f"{eid}: defensive_action defined", bool(r.get("defensive_action")))
        check(f"{eid}: evidence_trace defined", isinstance(r.get("evidence_trace"), list))
        check(f"{eid}: exploit_chain_candidate defined", isinstance(r.get("exploit_chain_candidate"), list))
        if r.get("breakthrough_detected"):
            check(f"{eid}: breakthrough => requires_human_review=true", r.get("requires_human_review") is True)
            check(f"{eid}: breakthrough => evidence_trace populated", len(r.get("evidence_trace", [])) > 0)
            check(f"{eid}: breakthrough => exploit_chain populated", len(r.get("exploit_chain_candidate", [])) > 0)

    breakthrough_ids = [r["entry_id"] for r in results if r.get("breakthrough_detected")]
    check("breakthrough entries marked", len(breakthrough_ids) > 0, f"entries: {breakthrough_ids}" if breakthrough_ids else "none")

    for r in results:
        if r.get("control_case"):
            check(f"control {r['entry_id']}: no breakthrough", not r.get("breakthrough_detected"))
            check(f"control {r['entry_id']}: no human review", not r.get("requires_human_review"))


def validate_scorecard():
    print("\n--- Scorecard Validation ---")
    exists = SCORECARD_PATH.exists()
    check("capability_scorecard.yaml exists", exists, str(SCORECARD_PATH))
    if not exists:
        return
    sc = load_yaml(SCORECARD_PATH)
    meta = sc.get("scorecard_metadata", {})
    summary = sc.get("results_summary", {})

    check("assessment_mode = adversarial_validation", meta.get("assessment_mode") == "adversarial_validation")
    check("adversarial_playbook_type = indirect_prompt_injection", meta.get("adversarial_playbook_type") == "indirect_prompt_injection")
    for fld in ["confirmed_vulnerability", "formal_finding_allowed", "production_safety_claimed", "controlled_replay_claimed"]:
        check(f"{fld} = false", meta.get(fld) is False)

    check("total entries in summary", summary.get("total", 0) == 14)
    check("breakthrough_detected count >= 0", isinstance(summary.get("breakthrough_detected"), int))
    check("control_passed count >= 0", isinstance(summary.get("control_passed"), int))
    bt = summary.get("breakthrough_detected", 0)
    hr = summary.get("human_review_required", 0)
    check("human_review_required >= breakthrough_detected", hr >= bt, f"hr={hr}, bt={bt}")
    check("category_coverage defined", len(sc.get("category_coverage", [])) > 0)


def validate_adversarial_result():
    print("\n--- Adversarial Result Validation ---")
    exists = ADV_RESULT_PATH.exists()
    check("adversarial_result.yaml exists", exists, str(ADV_RESULT_PATH))
    if not exists:
        return
    ar = load_yaml(ADV_RESULT_PATH)
    meta = ar.get("adversarial_result_metadata", {})
    entries = ar.get("per_entry_results", [])

    check("assessment_mode = adversarial_validation", meta.get("assessment_mode") == "adversarial_validation")
    check("confirmed_vulnerability = false", meta.get("confirmed_vulnerability") is False)
    check("formal_finding_allowed = false", meta.get("formal_finding_allowed") is False)
    check("per_entry_results present", len(entries) > 0, f"{len(entries)} entries")

    for e in entries:
        eid = e.get("entry_id", "?")
        check(f"{eid}: entry has breakthrough_detected", "breakthrough_detected" in e)
        check(f"{eid}: entry has defensive_action", bool(e.get("defensive_action")))
        check(f"{eid}: entry has evaluation_summary", bool(e.get("evaluation_summary")))


def main():
    print("=" * 60)
    print("Phase 62C — IPI MVP Validation")
    print("=" * 60)

    validate_playbook()
    validate_run_config()
    validate_execution_results()
    validate_scorecard()
    validate_adversarial_result()

    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    total = len(checks)

    print(f"\n{'=' * 60}")
    print(f"Validation Summary")
    print(f"{'=' * 60}")
    print(f"  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failed == 0:
        print(f"\nALL {total} CHECKS PASSED — IPI MVP is complete and consistent.")
        sys.exit(0)
    else:
        print(f"\n{failed} check(s) FAILED. Review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
