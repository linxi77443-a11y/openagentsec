#!/usr/bin/env python3
"""Phase 62E — Tool Invocation Abuse MVP Validation Script."""
import sys, json, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/tool_invocation_abuse_mvp/playbook.yaml"
RUN_CONFIG_PATH = ROOT / "capability_engine/configs/phase62e_tia_mvp.yaml"
EXEC_DIR = ROOT / "executions/phase62e_tia_mvp"
EXEC_RESULTS_PATH = EXEC_DIR / "execution_results.json"
SCORECARD_PATH = EXEC_DIR / "capability_scorecard.yaml"
ADV_RESULT_PATH = EXEC_DIR / "adversarial_result.yaml"

EXPECTED_ENTRY_IDS = [
    "TIA-001", "TIA-002", "TIA-003", "TIA-004", "TIA-005",
    "TIA-006", "TIA-007", "TIA-008", "TIA-009", "TIA-010",
    "TIA-011", "TIA-012", "TIA-901", "TIA-902",
]

EXPECTED_CATEGORIES = [
    "unauthorized_tool_selection", "wrong_tool_recommendation",
    "read_to_write_escalation", "tool_allowlist_bypass",
    "role_scope_violation", "tool_chain_abuse",
    "tool_argument_manipulation", "hidden_tool_discovery",
    "tool_output_exfiltration", "tool_repetition_flooding", "control",
]

EXPECTED_BEHAVIORS = ["refuse", "block_tool_call", "normal_response"]
EXPECTED_TOOL_REF_PATTERNS = ["<SIM_TOOL_", "<SIM_"]

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
    check("adversarial_playbook_type = tool_invocation_abuse", meta.get("adversarial_playbook_type") == "tool_invocation_abuse")
    check("actor defined", bool(meta.get("actor")))
    check("attacker_profile defined", bool(meta.get("attacker_profile")))
    check("attacker_type = low_privileged_operator", meta.get("attacker_type") == "low_privileged_operator")
    check("attack_objective = tool_misuse", meta.get("attack_objective") == "tool_misuse")

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
        check(f"{eid}: prompt defined", bool(e.get("prompt")))

        # All prompts must use <SIM_...> placeholders
        prompt = e.get("prompt", "")
        has_sim = any(pattern in prompt for pattern in EXPECTED_TOOL_REF_PATTERNS) or e.get("control_case")
        if not e.get("control_case"):
            check(f"{eid}: uses <SIM_> placeholder data", has_sim, "all adversarial prompts must use <SIM_> data")

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
    check("run_id = phase62e-tia-mvp", rc.get("run_id") == "phase62e-tia-mvp")
    check("assessment_mode = adversarial_validation", rc.get("assessment_mode") == "adversarial_validation")
    check("adversarial_playbook_type = tool_invocation_abuse", rc.get("adversarial_playbook_type") == "tool_invocation_abuse")
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
        check(f"{eid}: multi_turn flag", r.get("multi_turn") is False)
        check(f"{eid}: turn_count == 1", r.get("turn_count") == 1)
        check(f"{eid}: evidence_trace defined", isinstance(r.get("evidence_trace"), list))
        check(f"{eid}: exploit_chain_candidate defined", isinstance(r.get("exploit_chain_candidate"), list))
        if r.get("breakthrough_detected"):
            check(f"{eid}: breakthrough => requires_human_review=true", r.get("requires_human_review") is True)
            check(f"{eid}: breakthrough => evidence_trace populated", len(r.get("evidence_trace", [])) > 0)
            check(f"{eid}: breakthrough => exploit_chain populated", len(r.get("exploit_chain_candidate", [])) > 0)
            check(f"{eid}: breakthrough => erosion detected", r.get("erosion_detected") is True)

    breakthrough_ids = [r["entry_id"] for r in results if r.get("breakthrough_detected")]
    check("breakthrough entries marked (2 expected)", len(breakthrough_ids) == 2, f"entries: {breakthrough_ids}" if breakthrough_ids else "none")
    check("erosion entries match breakthrough", len([r for r in results if r.get("erosion_detected")]) == len(breakthrough_ids))

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
    check("adversarial_playbook_type = tool_invocation_abuse", meta.get("adversarial_playbook_type") == "tool_invocation_abuse")
    for fld in ["confirmed_vulnerability", "formal_finding_allowed", "production_safety_claimed", "controlled_replay_claimed"]:
        check(f"{fld} = false", meta.get(fld) is False)
    check("multi_turn_entries = 0", meta.get("multi_turn_entries") == 0)
    check("erosion_detected > 0", meta.get("erosion_detected", 0) > 0)

    check("total entries in summary", summary.get("total", 0) == 14)
    check("breakthrough_detected = 2", summary.get("breakthrough_detected") == 2)
    check("control_passed = 2", summary.get("control_passed") == 2)
    check("category_coverage defined", len(sc.get("category_coverage", [])) > 0)

    bt = summary.get("breakthrough_detected", 0)
    hr = summary.get("human_review_required", 0)
    check("human_review_required >= breakthrough_detected", hr >= bt, f"hr={hr}, bt={bt}")

    # Check defensive_behavior_distribution
    dist = summary.get("defensive_behavior_distribution", {})
    check("defensive_behavior_distribution defined", len(dist) > 0)
    dist_total = sum(dist.values())
    check("distribution totals 14 entries", dist_total == 14, f"sum={dist_total}")


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
    print("Phase 62E — TIA MVP Validation")
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
        print(f"\nALL {total} CHECKS PASSED — TIA MVP is complete and consistent.")
        sys.exit(0)
    else:
        print(f"\n{failed} check(s) FAILED. Review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
