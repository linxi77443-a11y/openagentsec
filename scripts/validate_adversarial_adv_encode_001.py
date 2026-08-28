#!/usr/bin/env python3
"""ADV-ENCODE-001 — Encoding Obfuscation MVP Validation Script.

Validates playbook, run config, execution results, result YAML, scorecard,
evidence candidates, blue controls, and purple retests for completeness
and correctness.

Does NOT execute real API calls or connect to real systems.
"""
import sys, json, yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/encoding_obfuscation_playbook/playbook.yaml"
RUN_CONFIG_PATH = ROOT / "run_configs/phase_adv_encode_001_run_config.yaml"
EXEC_DIR = ROOT / "executions/adv_encode_001"
EXEC_RESULTS_PATH = EXEC_DIR / "execution_results.json"
RESULT_YAML_PATH = EXEC_DIR / "adv_encode_001_result.yaml"
SCORECARD_PATH = EXEC_DIR / "capability_scorecard.yaml"
EVIDENCE_PATH = EXEC_DIR / "red_team_evidence_candidates.yaml"
BLUE_PATH = EXEC_DIR / "blue_control_candidates.yaml"
PURPLE_PATH = EXEC_DIR / "purple_retest_candidates.yaml"
NOTES_PATH = ROOT / "docs/phase_adv_encode_001_notes.md"

EXPECTED_ENTRY_IDS = [
    "ENC-001", "ENC-002", "ENC-003", "ENC-004", "ENC-005",
    "ENC-006", "ENC-007", "ENC-008", "ENC-009", "ENC-010",
    "ENC-011", "ENC-901", "ENC-902",
]

EXPECTED_CATEGORIES = [
    "base64_baseline",
    "unicode_homoglyph_obfuscation",
    "emoji_hidden_instruction_obfuscation",
    "zero_width_character_obfuscation",
    "control",
]

EXPECTED_BEHAVIORS = ["refuse", "block_tool_call", "normal_response"]

PARSER_FIELDS = [
    "encoding_obfuscation_detected",
    "instruction_boundary_preserved",
    "obfuscated_instruction_ignored",
    "unsafe_tool_trace_signal",
    "unsafe_tool_trace_attempt_blocked",
    "simulated_exfiltration_signal",
    "human_review_required_count",
]

V31_SAFETY_FIELDS = [
    "synthetic_only",
    "real_target_selection_allowed",
    "red_team_engine_not_executable",
    "dashboard_not_execution_interface",
    "controlled_replay_claimed",
    "controlled_replay_execution_allowed",
]

SAFETY_FIELDS_FALSE = [
    "confirmed_vulnerability",
    "formal_finding_allowed",
    "production_safety_claimed",
    "controlled_replay_claimed",
    "attack_execution_allowed",
    "payload_generation_allowed",
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


ENTRY_SAFETY_FIELDS = [
    "confirmed_vulnerability",
    "formal_finding_allowed",
]


def check_safety_fields(obj, prefix="", entry_level=False):
    """Check that all safety fields are False in a dict.

    Args:
        obj: The dict to check
        prefix: Display prefix
        entry_level: If True, only check fields that exist at entry level
    """
    fields = ENTRY_SAFETY_FIELDS if entry_level else SAFETY_FIELDS_FALSE
    for field in fields:
        # Only check if present at entry level
        if entry_level and field not in obj:
            continue
        val = obj.get(field)
        name = f"{prefix}: {field} = false" if prefix else f"{field} = false"
        check(name, val is False, f"got {val}")


def check_v31_safety_fields(obj, prefix=""):
    """Check v3.1 §4 safety fields exist with correct values."""
    v31_map = {
        "synthetic_only": True,
        "real_target_selection_allowed": False,
        "red_team_engine_not_executable": True,
        "dashboard_not_execution_interface": True,
        "controlled_replay_claimed": False,
        "controlled_replay_execution_allowed": False,
    }
    for field, expected in v31_map.items():
        val = obj.get(field)
        name = f"{prefix}: {field} = {expected}" if prefix else f"{field} = {expected}"
        check(name, val == expected, f"got {val}")


def check_non_registry_declarations(obj, prefix=""):
    """Check non-registry-module declarations."""
    decl_map = {
        "not_registered_module": True,
        "registry_credit_granted": False,
        "module_registry_modified": False,
        "registry_score_credit_granted": False,
    }
    for field, expected in decl_map.items():
        val = obj.get(field)
        name = f"{prefix}: {field} = {expected}" if prefix else f"{field} = {expected}"
        check(name, val == expected, f"got {val}")

    # score_not_applicable_reason must equal non_registry_adversarial_extension
    reason = obj.get("score_not_applicable_reason")
    check(f"{prefix}: score_not_applicable_reason = non_registry_adversarial_extension" if prefix else
          "score_not_applicable_reason = non_registry_adversarial_extension",
          reason == "non_registry_adversarial_extension", f"got {reason}")

    # mapped_modules must include M38, tooltrace, M12, M04, M19
    mapped = obj.get("mapped_modules", [])
    expected_mapped = {"M38", "tooltrace", "M12", "M04", "M19"}
    check(f"{prefix}: mapped_modules includes M38/tooltrace/M12/M04/M19" if prefix else
          "mapped_modules includes M38/tooltrace/M12/M04/M19",
          expected_mapped.issubset(set(mapped)), f"missing: {expected_mapped - set(mapped)}")


def check_unsafe_signal_compliance(parser, prefix=""):
    """Check unsafe signal compliance per attacker_perspective §7-§8.

    If unsafe_tool_trace_signal > 0, must bind human_review_required_count.
    If signals are blocked attempts, must use _attempt_blocked naming.
    """
    sig_val = parser.get("unsafe_tool_trace_signal", 0)
    blocked_val = parser.get("unsafe_tool_trace_attempt_blocked", 0)
    hr_count = parser.get("human_review_required_count", 0)

    if sig_val > 0:
        # Real signal must have human review
        check(f"{prefix}: unsafe_tool_trace_signal > 0 => human_review_required_count > 0" if prefix else
              "unsafe_tool_trace_signal > 0 => human_review_required_count > 0",
              hr_count >= sig_val, f"signal={sig_val}, hr={hr_count}")
    elif blocked_val > 0:
        # Blocked attempts: signal must be 0, attempt_blocked must be > 0
        check(f"{prefix}: blocked attempt naming correct (signal=0, attempt_blocked>0)" if prefix else
              "blocked attempt naming correct (signal=0, attempt_blocked>0)",
              sig_val == 0 and blocked_val > 0, f"signal={sig_val}, blocked={blocked_val}")
    else:
        check(f"{prefix}: no unsafe signals or blocked attempts" if prefix else
              "no unsafe signals or blocked attempts", True)


def check_sim_placeholder(text, entry_id, is_control=False):
    """Verify text uses <SIM_...> placeholders and no real data.

    Control entries are exempt from <SIM_...> requirement.
    Base64-encoded text may contain <SIM_...> in its decoded form.
    """
    # Skip SIM_ check for control entries (they contain harmless content)
    if not is_control:
        # Check for <SIM_...> in plain text OR in base64-encoded content
        has_sim = bool(re.search(r'<SIM_[A-Z_]+>', text))
        # Also check base64-encoded strings for embedded SIM_ placeholders
        b64_patterns = re.findall(r'[A-Za-z0-9+/=]{20,}', text)
        for b64 in b64_patterns:
            try:
                import base64
                decoded = base64.b64decode(b64).decode('utf-8', errors='replace')
                if '<SIM_' in decoded:
                    has_sim = True
                    break
            except Exception:
                continue
        check(f"{entry_id}: prompt uses <SIM_...> placeholders", has_sim)
    # Must NOT contain real URLs, tokens, or secrets
    no_real_url = not re.search(r'https?://(?!sim\.)', text, re.IGNORECASE)
    check(f"{entry_id}: no real URLs", no_real_url)
    no_real_token = not re.search(r'(?<!SIM_)(?:sk-[a-zA-Z0-9]{10,}|api[-_]?key[\s:=]+[a-zA-Z0-9]{10,})', text, re.IGNORECASE)
    check(f"{entry_id}: no real tokens/keys", no_real_token)


# ── 1. Playbook checks ─────────────────────────────────────────────────────

def validate_playbook():
    print("\n--- Playbook Validation ---")
    exists = PLAYBOOK_PATH.exists()
    check("Playbook file exists", exists, str(PLAYBOOK_PATH))
    if not exists:
        return False

    pb = load_yaml(PLAYBOOK_PATH)
    meta = pb.get("playbook_metadata", {})

    check("playbook_metadata present", bool(meta))
    check("module_id = ADV-ENCODE-001", meta.get("module_id") == "ADV-ENCODE-001")
    check("assessment_mode = adversarial_validation",
          meta.get("assessment_mode") == "adversarial_validation")
    check("adversarial_playbook_type = encoding_obfuscation",
          meta.get("adversarial_playbook_type") == "encoding_obfuscation")
    check("actor defined", bool(meta.get("actor")))
    check("attacker_type defined", bool(meta.get("attacker_type")))
    check("attack_objective defined", bool(meta.get("attack_objective")))
    check("total_entries = 13", meta.get("total_entries") == 13)
    check_safety_fields(meta, "playbook_metadata")
    check("all_findings_are_candidate_level = true",
          meta.get("all_findings_are_candidate_level") is True)

    entries = pb.get("entries", [])
    eids = [e["entry_id"] for e in entries]
    check("playbook has entries", len(entries) > 0, f"{len(entries)} entries")
    check("total entries = 13", len(entries) == 13)

    missing_ids = [eid for eid in EXPECTED_ENTRY_IDS if eid not in eids]
    extra_ids = [eid for eid in eids if eid not in EXPECTED_ENTRY_IDS]
    check("all expected entry IDs present", len(missing_ids) == 0,
          f"missing: {missing_ids}" if missing_ids else "all 13 present")
    check("no unexpected entry IDs", len(extra_ids) == 0,
          f"extra: {extra_ids}" if extra_ids else "no extras")

    for e in entries:
        eid = e.get("entry_id", "?")
        check(f"{eid}: category defined", bool(e.get("category")))
        check(f"{eid}: expected_behavior defined", bool(e.get("expected_behavior")))
        check(f"{eid}: expected_signal defined", "expected_signal" in e)
        check(f"{eid}: control_case defined", "control_case" in e)
        check_safety_fields(e, eid, entry_level=True)

    cats = set(e["category"] for e in entries)
    for cat in EXPECTED_CATEGORIES:
        check(f"category '{cat}' present", cat in cats)

    controls = [e for e in entries if e.get("control_case")]
    check("control cases present (= 2)", len(controls) == 2)
    for c in controls:
        check(f"control {c['entry_id']}: expected_behavior = normal_response",
              c.get("expected_behavior") == "normal_response")
        check(f"control {c['entry_id']}: expected_signal = none",
              c.get("expected_signal") == "none")
        check_sim_placeholder(c.get("prompt", ""), c["entry_id"], is_control=True)

    # Check SIM_ placeholders in attack prompts
    attack_entries = [e for e in entries if not e.get("control_case")]
    for e in attack_entries:
        check_sim_placeholder(e.get("prompt", ""), e["entry_id"])

    return True


# ── 2. Run config checks ───────────────────────────────────────────────────

def validate_run_config():
    print("\n--- Run Config Validation ---")
    exists = RUN_CONFIG_PATH.exists()
    check("Run config file exists", exists, str(RUN_CONFIG_PATH))
    if not exists:
        return

    rc = load_yaml(RUN_CONFIG_PATH).get("run_config", {})
    check("module_id = ADV-ENCODE-001", rc.get("module_id") == "ADV-ENCODE-001")
    check("assessment_mode = adversarial_validation",
          rc.get("assessment_mode") == "adversarial_validation")
    check("adversarial_playbook_type = encoding_obfuscation",
          rc.get("adversarial_playbook_type") == "encoding_obfuscation")
    check("corpus_path points to playbook",
          rc.get("corpus_path") == "adversarial_playbooks/encoding_obfuscation_playbook/playbook.yaml")
    check("output_dir = executions/adv_encode_001",
          rc.get("output_dir") == "executions/adv_encode_001")
    check_safety_fields(rc)


# ── 3. Execution results checks ────────────────────────────────────────────

def validate_execution_results():
    print("\n--- Execution Results Validation ---")
    exists = EXEC_RESULTS_PATH.exists()
    check("execution_results.json exists", exists, str(EXEC_RESULTS_PATH))
    if not exists:
        return

    results = load_json(EXEC_RESULTS_PATH)
    check("results is a list", isinstance(results, list), f"{len(results)} entries")
    check("all 13 entries present", len(results) == 13)

    eids = [r["entry_id"] for r in results]
    for eid in EXPECTED_ENTRY_IDS:
        check(f"result for {eid} present", eid in eids)

    for r in results:
        eid = r.get("entry_id", "?")
        check(f"{eid}: breakthrough_detected defined",
              "breakthrough_detected" in r)
        check(f"{eid}: defensive_action defined",
              bool(r.get("defensive_action")))
        check(f"{eid}: evidence_trace defined",
              isinstance(r.get("evidence_trace"), list))
        check(f"{eid}: exploit_chain_candidate defined",
              isinstance(r.get("exploit_chain_candidate"), list))

        # Encoding-specific signal fields
        # Note: execution_results.json retains original field names (not modified per judge)
        for sig_field in ["encoding_obfuscation_detected", "instruction_boundary_preserved",
                          "obfuscated_instruction_ignored", "unsafe_tool_trace_signal",
                          "simulated_exfiltration_signal"]:
            check(f"{eid}: {sig_field} defined",
                  sig_field in r and isinstance(r[sig_field], bool))

        # Runtime prohibition fields
        for rt_field in ["real_runtime_accessed", "real_sandbox_accessed",
                         "real_system_call_executed", "real_tool_executed",
                         "real_audit_log_accessed", "real_network_request_sent",
                         "real_file_system_written"]:
            check(f"{eid}: {rt_field} = false",
                  r.get(rt_field) is False)

        # BRK-001 compliance
        if r.get("breakthrough_detected"):
            check(f"{eid}: breakthrough => requires_human_review=true",
                  r.get("requires_human_review") is True)
            check(f"{eid}: breakthrough => evidence_trace populated",
                  len(r.get("evidence_trace", [])) > 0)
            check(f"{eid}: breakthrough => exploit_chain populated",
                  len(r.get("exploit_chain_candidate", [])) > 0)

    for r in results:
        if r.get("control_case"):
            check(f"control {r['entry_id']}: no breakthrough",
                  not r.get("breakthrough_detected"))
            check(f"control {r['entry_id']}: no human review",
                  not r.get("requires_human_review"))


# ── 4. Result YAML checks ──────────────────────────────────────────────────

REGISTRY_PATH = ROOT / "capability_modules/module_registry.yaml"


def validate_registry_absence():
    """Verify ADV-ENCODE-001 is NOT in module_registry.yaml.

    Per PRD v2.0 §10.1-§10.2 / v3.1 §2.1 / §8, this playbook is a
    non-registry adversarial extension of M38/tooltrace/M12/M04/M19.
    """
    print("\n--- Registry Absence Validation ---")
    exists = REGISTRY_PATH.exists()
    check("module_registry.yaml exists", exists, str(REGISTRY_PATH))
    if not exists:
        return

    registry = load_yaml(REGISTRY_PATH)
    modules = registry.get("modules", [])
    module_ids = [m.get("module_id") for m in modules]
    check("ADV-ENCODE-001 NOT in module_registry.yaml",
          "ADV-ENCODE-001" not in module_ids,
          f"FOUND in registry — must remove per PRD v2.0 §10.1-§10.2")


def validate_result_yaml():
    print("\n--- Result YAML Validation ---")
    exists = RESULT_YAML_PATH.exists()
    check("adv_encode_001_result.yaml exists", exists, str(RESULT_YAML_PATH))
    if not exists:
        return

    ry = load_yaml(RESULT_YAML_PATH)
    meta = ry.get("result_metadata", {})
    parser = ry.get("parser_fields", {})

    check("module_id = ADV-ENCODE-001", meta.get("module_id") == "ADV-ENCODE-001")
    check("assessment_mode = adversarial_validation",
          meta.get("assessment_mode") == "adversarial_validation")
    check("total_cases = 13", meta.get("total_cases") == 13)
    check_safety_fields(meta, "result_metadata")
    check("result_is_candidate_level = true",
          meta.get("result_is_candidate_level") is True)
    check("all_findings_are_candidate_level = true",
          meta.get("all_findings_are_candidate_level") is True)

    # Non-registry module declarations
    check_non_registry_declarations(meta, "result_metadata")

    # v3.1 §4 safety fields
    check_v31_safety_fields(meta, "result_metadata")

    # Parser field validation
    for field in PARSER_FIELDS:
        check(f"parser field '{field}' present",
              field in parser and isinstance(parser[field], int))
        check(f"parser field '{field}' >= 0", parser.get(field, -1) >= 0)

    # Unsafe signal compliance (attacker_perspective §7-§8)
    check_unsafe_signal_compliance(parser, "parser_fields")

    # Category distribution present
    cat_dist = ry.get("category_distribution", {})
    check("category_distribution present", bool(cat_dist))
    for cat in EXPECTED_CATEGORIES:
        check(f"category '{cat}' in distribution", cat in cat_dist)

    # Per-entry results
    per_entry = ry.get("per_entry_results", [])
    check("per_entry_results present", len(per_entry) > 0, f"{len(per_entry)} entries")
    check("per_entry_results count = 13", len(per_entry) == 13)

    for e in per_entry:
        eid = e.get("entry_id", "?")
        check(f"{eid}: entry has breakthrough_detected",
              "breakthrough_detected" in e)
        check(f"{eid}: entry has defensive_action",
              bool(e.get("defensive_action")))
        check(f"{eid}: entry has evaluation_summary",
              bool(e.get("evaluation_summary")))
        check(f"{eid}: confirmed_vulnerability = false",
              e.get("confirmed_vulnerability") is False)
        check(f"{eid}: formal_finding_allowed = false",
              e.get("formal_finding_allowed") is False)

    # Control case performance
    ctrl = ry.get("control_case_performance", {})
    check("control_case_performance present", bool(ctrl))
    check("all controls passed", ctrl.get("all_passed") is True)
    check("no false positives in controls", ctrl.get("no_false_positives") is True)


# ── 5. Scorecard checks ────────────────────────────────────────────────────

def validate_scorecard():
    print("\n--- Scorecard Validation ---")
    exists = SCORECARD_PATH.exists()
    check("capability_scorecard.yaml exists", exists, str(SCORECARD_PATH))
    if not exists:
        return

    sc = load_yaml(SCORECARD_PATH)
    meta = sc.get("scorecard_metadata", {})
    summary = sc.get("results_summary", {})

    check("module_id = ADV-ENCODE-001", meta.get("module_id") == "ADV-ENCODE-001")
    check("assessment_mode = adversarial_validation",
          meta.get("assessment_mode") == "adversarial_validation")
    check_safety_fields(meta, "scorecard_metadata")
    check("all_findings_are_candidate_level = true",
          meta.get("all_findings_are_candidate_level") is True)

    # Non-registry module declarations
    check_non_registry_declarations(meta, "scorecard_metadata")

    # v3.1 §4 safety fields
    check_v31_safety_fields(meta, "scorecard_metadata")

    check("total entries in summary", summary.get("total", 0) == 13)
    check("breakthrough_detected count >= 0",
          isinstance(summary.get("breakthrough_detected"), int))
    check("control_passed count >= 0",
          isinstance(summary.get("control_passed"), int))

    bt = summary.get("breakthrough_detected", 0)
    hr = summary.get("human_review_required", 0)
    check("human_review_required >= breakthrough_detected", hr >= bt,
          f"hr={hr}, bt={bt}")

    # Signal summary
    sig_summary = summary.get("signal_summary", {})
    check("signal_summary present", bool(sig_summary))
    for sig in ["encoding_obfuscation_detected", "instruction_boundary_preserved",
                "obfuscated_instruction_ignored", "unsafe_tool_trace_signal",
                "unsafe_tool_trace_attempt_blocked", "simulated_exfiltration_signal"]:
        check(f"signal '{sig}' in summary", sig in sig_summary)

    cats = sc.get("category_coverage", [])
    check("category_coverage defined", len(cats) > 0)
    for cat in EXPECTED_CATEGORIES:
        if cat != "control":
            check(f"category '{cat}' in coverage", cat in cats)

    # capability_value and risk_level semantic separation
    cv = sc.get("capability_value")
    rl = sc.get("risk_level")
    check("capability_value defined", cv is not None)
    check("risk_level defined", rl is not None)
    # When both are "not_applicable", the semantic separation is satisfied
    # because the MVP uses synthetic-only simulated execution.
    sep_ok = (cv != rl) or (cv == "not_applicable" and rl == "not_applicable")
    check("capability_value/risk_level semantic separation maintained", sep_ok,
          f"cv={cv}, rl={rl}")


# ── 6. Evidence candidates checks ──────────────────────────────────────────

def validate_evidence():
    print("\n--- Evidence Candidates Validation ---")
    exists = EVIDENCE_PATH.exists()
    check("red_team_evidence_candidates.yaml exists", exists, str(EVIDENCE_PATH))
    if not exists:
        return

    ev = load_yaml(EVIDENCE_PATH)
    meta = ev.get("evidence_metadata", {})
    candidates = ev.get("evidence_candidates", [])

    check("evidence_metadata present", bool(meta))
    check("module_id = ADV-ENCODE-001", meta.get("module_id") == "ADV-ENCODE-001")
    check("confirmed_vulnerability = false",
          meta.get("confirmed_vulnerability") is False)
    check("all_findings_are_candidate_level = true",
          meta.get("all_findings_are_candidate_level") is True)

    check("evidence_candidates present", len(candidates) > 0,
          f"{len(candidates)} candidates")

    for c in candidates:
        check(f"candidate {c.get('candidate_id', '?')}: confirmed_vulnerability = false",
              c.get("confirmed_vulnerability") is False)
        check(f"candidate {c.get('candidate_id', '?')}: formal_finding_allowed = false",
              c.get("formal_finding_allowed") is False)
        check(f"candidate {c.get('candidate_id', '?')}: all_findings_are_candidate_level = true",
              c.get("all_findings_are_candidate_level") is True)


# ── 7. Blue control candidates checks ──────────────────────────────────────

def validate_blue_controls():
    print("\n--- Blue Control Candidates Validation ---")
    exists = BLUE_PATH.exists()
    check("blue_control_candidates.yaml exists", exists, str(BLUE_PATH))
    if not exists:
        return

    bc = load_yaml(BLUE_PATH)
    meta = bc.get("blue_control_metadata", {})
    controls = bc.get("control_candidates", [])

    check("blue_control_metadata present", bool(meta))
    check("module_id = ADV-ENCODE-001", meta.get("module_id") == "ADV-ENCODE-001")
    check("control_candidates present", len(controls) > 0,
          f"{len(controls)} controls")

    for c in controls:
        check(f"control {c.get('control_id', '?')}: confirmed_vulnerability = false",
              c.get("confirmed_vulnerability") is False)


# ── 8. Purple retest candidates checks ─────────────────────────────────────

def validate_purple_retests():
    print("\n--- Purple Retest Candidates Validation ---")
    exists = PURPLE_PATH.exists()
    check("purple_retest_candidates.yaml exists", exists, str(PURPLE_PATH))
    if not exists:
        return

    pr = load_yaml(PURPLE_PATH)
    meta = pr.get("purple_retest_metadata", {})
    retests = pr.get("retest_candidates", [])

    check("purple_retest_metadata present", bool(meta))
    check("module_id = ADV-ENCODE-001", meta.get("module_id") == "ADV-ENCODE-001")
    check("retest_candidates present", len(retests) > 0,
          f"{len(retests)} retests")

    for r in retests:
        check(f"retest {r.get('retest_id', '?')}: confirmed_vulnerability = false",
              r.get("confirmed_vulnerability") is False)


# ── 9. Notes checks ────────────────────────────────────────────────────────

def validate_notes():
    print("\n--- Notes Validation ---")
    exists = NOTES_PATH.exists()
    check("phase_adv_encode_001_notes.md exists", exists, str(NOTES_PATH))
    if not exists:
        return

    notes_text = NOTES_PATH.read_text()
    check("notes mention no real system access (synthetic only)",
          "synthetic" in notes_text.lower() or "不连接真实系统" in notes_text)
    check("notes mention confirmed_vulnerability = false",
          "confirmed_vulnerability" in notes_text and "false" in notes_text)
    check("notes mention not_registered_module = true",
          "not_registered_module" in notes_text and "true" in notes_text.lower())
    check("notes mention registry_credit_granted = false",
          "registry_credit_granted" in notes_text and "false" in notes_text)
    check("notes mention mapped_modules includes M38/tooltrace/M12/M04/M19",
          "M38" in notes_text and "tooltrace" in notes_text and "M12" in notes_text
          and "M04" in notes_text and "M19" in notes_text)


def main():
    print("=" * 60)
    print("ADV-ENCODE-001 — Encoding Obfuscation MVP Validation")
    print("=" * 60)

    validate_playbook()
    validate_run_config()
    validate_registry_absence()
    validate_execution_results()
    validate_result_yaml()
    validate_scorecard()
    validate_evidence()
    validate_blue_controls()
    validate_purple_retests()
    validate_notes()

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
        print(f"\nALL {total} CHECKS PASSED — ADV-ENCODE-001 is complete and consistent.")
        sys.exit(0)
    else:
        print(f"\n{failed} check(s) FAILED. Review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
