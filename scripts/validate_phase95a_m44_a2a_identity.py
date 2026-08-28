#!/usr/bin/env python3
"""Phase 95A — M44 A2A Agent Identity Trust Boundary Validator.

Comprehensive checks for playbook, run config, execution results, result YAML,
scorecard, candidate triplet, notes, and safety fields.
"""
import json
import re
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
checks_passed = 0
checks_failed = 0
errors = []


def check(condition, msg):
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  ✓ {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  ✗ {msg}")


def yaml_load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load: {path} — {e}")
        return None


def json_load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load: {path} — {e}")
        return None


def check_security_fields(obj, prefix, obj_desc):
    fields = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
    }
    for field, expected in fields.items():
        actual = obj.get(field) if isinstance(obj, dict) else getattr(obj, field, None)
        check(actual == expected,
              f"{prefix}: {obj_desc} {field} == {actual} (expected {expected})")


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 95A — M44 A2A Agent Identity Trust Boundary Validation")
    print("=" * 60)

    # ================================================================
    # 1. Playbook
    # ================================================================
    print("\n1. Playbook")
    playbook_paths = [
        ROOT / "adversarial_playbooks/m44_a2a_agent_identity_trust_boundary_mvp/m44_adversarial_playbook.yaml",
        ROOT / "adversarial_playbooks/m44_a2a_agent_identity_trust_boundary_mvp/playbook.yaml",
    ]

    for pb_path in playbook_paths:
        playbook = yaml_load(pb_path)
        check(playbook is not None, f"Playbook loaded at {pb_path.name}")
        if playbook:
            entries = playbook.get("entries", [])
            meta = playbook.get("playbook_metadata", {})
            check(len(entries) >= 14, f"{pb_path.name} has >= 14 entries ({len(entries)})")

            attack_cases = [e for e in entries if not e.get("control_case")]
            control_cases = [e for e in entries if e.get("control_case")]
            check(len(attack_cases) >= 10, f"{pb_path.name} has >= 10 attack cases ({len(attack_cases)})")
            check(len(control_cases) >= 4, f"{pb_path.name} has >= 4 control cases ({len(control_cases)})")

            # Check placeholders
            all_text = yaml.dump(entries)
            sim_pattern = re.findall(r'<SIM_AGENT_ID[\w_]*>', all_text)
            check(len(sim_pattern) >= len(entries),
                  f"{pb_path.name} entries contain <SIM_AGENT_ID...> placeholders ({len(sim_pattern)} found)")

            # Check metadata
            check(meta.get("module_id") == "M44", f"{pb_path.name} metadata module_id == M44")
            check(meta.get("assessment_mode") == "adversarial_validation",
                  f"{pb_path.name} metadata assessment_mode == adversarial_validation")
            check(meta.get("attacker_type") == "indirect_prompt_source",
                  f"{pb_path.name} metadata attacker_type == indirect_prompt_source")
            check(meta.get("attack_objective") == "service_account_abuse",
                  f"{pb_path.name} metadata attack_objective == service_account_abuse")
            check(meta.get("synthetic_only") is True, f"{pb_path.name} metadata synthetic_only == true")
            check(meta.get("requires_human_review") is True, f"{pb_path.name} metadata requires_human_review == true")
            check_security_fields(meta, "M44", f"{pb_path.name} metadata")

    # ================================================================
    # 2. Run Config
    # ================================================================
    print("\n2. Run Config")
    rc_path = ROOT / "run_configs/phase95a_m44_a2a_identity_run_config.yaml"
    rc = yaml_load(rc_path)
    check(rc is not None, "Run config loaded")
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase95a", "Run config phase == phase95a")
        check(rcfg.get("module_id") == "M44", "Run config module_id == M44")
        check(rcfg.get("assessment_mode") == "adversarial_validation", "Run config assessment_mode == adversarial_validation")
        check(rcfg.get("attacker_type") == "indirect_prompt_source", "Run config attacker_type == indirect_prompt_source")
        check(rcfg.get("attack_objective") == "service_account_abuse", "Run config attack_objective == service_account_abuse")
        check(rcfg.get("synthetic_only") is True, "Run config synthetic_only == true")
        check(rcfg.get("requires_human_review") is True, "Run config requires_human_review == true")
        check_security_fields(rcfg, "M44", "Run config")

    # ================================================================
    # 3. Execution Results
    # ================================================================
    print("\n3. Execution Results")
    exec_dirs = [
        ROOT / "adversarial_playbooks/m44_a2a_agent_identity_trust_boundary_mvp",
        ROOT / "executions/phase95a_m44_a2a_identity",
    ]

    for edir in exec_dirs:
        epath = edir / "execution_results.json"
        eres = json_load(epath)
        check(eres is not None, f"execution_results.json loaded at {edir.name}")
        if eres:
            check(len(eres) >= 14, f"{edir.name}/execution_results has >= 14 entries ({len(eres)})")
            for r in eres:
                eid = r.get("entry_id", "UNKNOWN")
                check(r.get("real_a2a_endpoint_accessed") is False, f"{eid} real_a2a_endpoint_accessed == false")
                check(r.get("real_agent_credential_read") is False, f"{eid} real_agent_credential_read == false")
                check(r.get("confirmed_vulnerability") is False, f"{eid} confirmed_vulnerability == false")
                check(r.get("formal_finding_allowed") is False, f"{eid} formal_finding_allowed == false")

    # ================================================================
    # 4. Result YAML
    # ================================================================
    print("\n4. Result YAML")
    for edir in exec_dirs:
        for rfile in ["m44_result.yaml", "result.yaml"]:
            rpath = edir / rfile
            if not rpath.exists():
                continue
            ryaml = yaml_load(rpath)
            check(ryaml is not None, f"{rfile} loaded at {edir.name}")
            if ryaml:
                check(ryaml.get("module_id") == "M44", f"{edir.name}/{rfile} module_id == M44")
                check(ryaml.get("assessment_mode") == "adversarial_validation", f"{edir.name}/{rfile} assessment_mode == adversarial_validation")
                check(ryaml.get("attacker_type") == "indirect_prompt_source", f"{edir.name}/{rfile} attacker_type == indirect_prompt_source")
                check(ryaml.get("attack_objective") == "service_account_abuse", f"{edir.name}/{rfile} attack_objective == service_account_abuse")
                rs = ryaml.get("results_summary", {})
                check(rs.get("breakthrough_detected") == 0, f"{edir.name}/{rfile} results_summary.breakthrough_detected == 0")
                check(ryaml.get("breakthrough_detected_count", 0) == 0, f"{edir.name}/{rfile} breakthrough_detected_count == 0")
                check("evidence_trace" in ryaml, f"{edir.name}/{rfile} contains evidence_trace")
                check_security_fields(ryaml, "M44", f"{edir.name}/{rfile}")

    # ================================================================
    # 5. Scorecard
    # ================================================================
    print("\n5. Capability Scorecard")
    for edir in exec_dirs:
        scpath = edir / "capability_scorecard.yaml"
        sc = yaml_load(scpath)
        check(sc is not None, f"capability_scorecard.yaml loaded at {edir.name}")
        if sc:
            sm = sc.get("scorecard_metadata", {})
            check(sm.get("module_id") == "M44", f"{edir.name}/scorecard module_id == M44")
            check(sm.get("simulated_signal_only") is True, f"{edir.name}/scorecard simulated_signal_only == true")
            check(sm.get("requires_human_review") is True, f"{edir.name}/scorecard requires_human_review == true")
            check(sc.get("capability_value") == "high", f"{edir.name}/scorecard capability_value == high")
            check(sc.get("risk_level") == "low", f"{edir.name}/scorecard risk_level == low")
            check_security_fields(sm, "M44", f"{edir.name}/scorecard metadata")

    # ================================================================
    # 6. Candidate Triplet Files
    # ================================================================
    print("\n6. Candidate Triplet Files")
    for edir in exec_dirs:
        # Red Team Evidence Candidates
        red_path = edir / "red_team_evidence_candidates.yaml"
        red = yaml_load(red_path)
        check(red is not None, f"red_team_evidence_candidates.yaml exists at {edir.name}")
        if red:
            evs = red.get("evidence_candidates", [])
            check(len(evs) >= 10, f"{edir.name}/red candidates has >= 10 evidence items ({len(evs)})")
            check(red.get("all_findings_are_candidate_level") is True, f"{edir.name}/red all_findings_are_candidate_level == true")
            check(red.get("confirmed_vulnerability") is False, f"{edir.name}/red confirmed_vulnerability == false")
            check(red.get("requires_human_review") is True, f"{edir.name}/red requires_human_review == true")

        # Blue Control Candidates
        blue_path = edir / "blue_control_candidates.yaml"
        blue = yaml_load(blue_path)
        check(blue is not None, f"blue_control_candidates.yaml exists at {edir.name}")
        if blue:
            ctrls = blue.get("control_candidates", [])
            check(len(ctrls) >= 5, f"{edir.name}/blue candidates has >= 5 control items ({len(ctrls)})")

        # Purple Retest Candidates
        purple_path = edir / "purple_retest_candidates.yaml"
        purple = yaml_load(purple_path)
        check(purple is not None, f"purple_retest_candidates.yaml exists at {edir.name}")
        if purple:
            retests = purple.get("retest_candidates", [])
            check(len(retests) >= 5, f"{edir.name}/purple candidates has >= 5 retest items ({len(retests)})")

    # ================================================================
    # 7. Documentation
    # ================================================================
    print("\n7. Documentation")
    doc_path = ROOT / "docs/phase95a_m44_a2a_identity_notes.md"
    check(doc_path.exists(), f"Notes document exists at {doc_path}")
    if doc_path.exists():
        doc_text = doc_path.read_text(encoding="utf-8")
        check("indirect_prompt_source" in doc_text, "Notes document mentions indirect_prompt_source")
        check("service_account_abuse" in doc_text, "Notes document mentions service_account_abuse")
        check("confirmed_vulnerability" in doc_text, "Notes document mentions confirmed_vulnerability")
        check("formal_finding_allowed" in doc_text, "Notes document mentions formal_finding_allowed")
        check("requires_human_review" in doc_text, "Notes document mentions requires_human_review")
        check("production_safety_claimed" in doc_text, "Notes document mentions production_safety_claimed")
        check("<SIM_AGENT_ID" in doc_text, "Notes document contains <SIM_AGENT_ID placeholders")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    total = checks_passed + checks_failed
    print(f"RESULTS: {checks_passed}/{total} passed, {checks_failed} failed")
    if checks_failed > 0:
        print("\nFAILURES:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("Phase 95A — M44 A2A Agent Identity Trust Boundary: ALL CHECKS PASSED")
    print("=" * 60)
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
