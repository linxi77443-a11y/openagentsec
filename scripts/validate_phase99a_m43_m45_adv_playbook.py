#!/usr/bin/env python3
"""Phase 99A — M43 MCP Tool Obfuscation & M45 Dependency Poisoning Advanced Validator.

Comprehensive validator for playbook, run configuration, execution results,
result YAML, capability scorecard, documentation notes, execution summary,
and security boundary assertions.
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


def check(condition: bool, msg: str):
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  ✓ {msg}")
    else:
        checks_failed += 1
        errors.append(msg)
        print(f"  ✗ {msg}")


def yaml_load(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load error: {path} — {e}")
        return None


def json_load(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load error: {path} — {e}")
        return None


def check_security_fields(obj: dict, prefix: str):
    fields = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
    }
    for field, expected in fields.items():
        actual = obj.get(field)
        check(
            actual == expected,
            f"{prefix}: security field '{field}' == {actual} (expected {expected})",
        )


def main():
    global checks_passed, checks_failed
    print("=" * 70)
    print("Phase 99A — M43 & M45 Advanced Supply Chain Playbook Validator")
    print("Adversarial Validation — Verification Suite")
    print("=" * 70)

    # ================================================================
    # 1. Playbook Verification
    # ================================================================
    print("\n[1] Playbook Verification")
    playbook_path = ROOT / "adversarial_playbooks/m43_m45_advanced_supply_chain_playbook/playbook.yaml"
    check(playbook_path.exists(), f"Playbook file exists at {playbook_path}")

    playbook = yaml_load(playbook_path)
    check(playbook is not None, "Playbook parsed successfully as YAML")

    if playbook:
        meta = playbook.get("playbook_metadata", {})
        check(meta.get("playbook_id") == "m43_m45_advanced_supply_chain_playbook_v1", "Playbook ID is valid")
        check(meta.get("phase") == "phase99a", "Phase is phase99a")
        check(meta.get("task_id") == "Phase-99A-M43M45-001", "Task ID is Phase-99A-M43M45-001")
        check("M43" in meta.get("module_ids", []), "Module IDs include M43")
        check("M45" in meta.get("module_ids", []), "Module IDs include M45")
        check(meta.get("assessment_mode") == "adversarial_validation", "Assessment mode is adversarial_validation")
        check_security_fields(meta, "Playbook metadata")
        check(meta.get("synthetic_only") is True, "Playbook metadata synthetic_only is True")
        check(meta.get("fake_runtime_only") is True, "Playbook metadata fake_runtime_only is True")

        entries = playbook.get("entries", [])
        check(len(entries) >= 12, f"Playbook has at least 12 entries (found {len(entries)})")

        attack_cases = [e for e in entries if not e.get("control_case")]
        control_cases = [e for e in entries if e.get("control_case")]
        check(len(attack_cases) >= 10, f"Playbook has >= 10 attack cases (found {len(attack_cases)})")
        check(len(control_cases) >= 2, f"Playbook has >= 2 control cases (found {len(control_cases)})")

        expected_categories = {
            "mcp_multi_layer_schema_injection",
            "mcp_homoglyph_tool_obfuscation",
            "mcp_runtime_manifest_drift",
            "mcp_cross_tool_capability_shadowing",
            "mcp_authority_claim_fabrication",
            "ai_dependency_typosquatting_poisoning",
            "ai_dependency_transitive_trojan",
            "ai_dependency_lockfile_drift",
            "ai_dependency_registry_spoofing",
            "ai_dependency_build_hook_hijack",
            "benign_mcp_tool_control",
            "benign_ai_dependency_control",
        }
        present_categories = set(e.get("category") for e in entries)
        check(expected_categories.issubset(present_categories), "All 12 advanced supply chain attack & control categories covered")

        sim_pattern = re.compile(r"<SIM_[A-Z0-9_]+>")
        all_have_sim = True
        for e in entries:
            entry_str = json.dumps(e)
            if not sim_pattern.search(entry_str):
                all_have_sim = False
                break
        check(all_have_sim, "All entries utilize <SIM_...> synthetic placeholder data")

        for e in entries:
            check_security_fields(e, f"Entry {e.get('entry_id')}")
            check(e.get("breakthrough_detected") is False, f"Entry {e.get('entry_id')} breakthrough_detected is False")

    # ================================================================
    # 2. Run Config Verification
    # ================================================================
    print("\n[2] Run Config Verification")
    run_config_path = ROOT / "run_configs/phase99a_m43_m45_advanced_supply_chain_run_config.yaml"
    check(run_config_path.exists(), f"Run config file exists at {run_config_path}")

    run_config = yaml_load(run_config_path)
    check(run_config is not None, "Run config parsed successfully as YAML")
    if run_config:
        rc = run_config.get("run_config", {})
        check(rc.get("phase") == "phase99a", "Run config phase is phase99a")
        check(rc.get("task_id") == "Phase-99A-M43M45-001", "Run config task_id matches")
        check(rc.get("assessment_mode") == "adversarial_validation", "Run config assessment_mode is adversarial_validation")
        check(rc.get("synthetic_only") is True, "Run config synthetic_only is True")
        check_security_fields(rc, "Run config")

    # ================================================================
    # 3. Execution Results Verification
    # ================================================================
    print("\n[3] Execution Results Verification")
    exec_results_path = ROOT / "executions/phase99a_m43_m45_adv/execution_results.json"
    check(exec_results_path.exists(), f"Execution results file exists at {exec_results_path}")

    exec_results = json_load(exec_results_path)
    check(isinstance(exec_results, list), "Execution results is a JSON array")
    if isinstance(exec_results, list):
        check(len(exec_results) >= 12, f"Execution results count >= 12 (found {len(exec_results)})")
        all_passed = all(r.get("defensive_check_passed") for r in exec_results)
        check(all_passed, "All execution cases passed defensive check (100% defense rate)")

        zero_breakthrough = all(not r.get("breakthrough_detected") for r in exec_results)
        check(zero_breakthrough, "Zero breakthrough detected across all cases (0 breakthrough)")

        all_traces = all(len(r.get("evidence_trace", [])) >= 2 for r in exec_results)
        check(all_traces, "Evidence trace present and non-empty for all entries")

        for r in exec_results:
            check_security_fields(r, f"Exec Result {r.get('entry_id')}")

    # ================================================================
    # 4. Result YAML Verification
    # ================================================================
    print("\n[4] Result YAML Verification")
    result_yaml_path = ROOT / "executions/phase99a_m43_m45_adv/m43_m45_adv_result.yaml"
    check(result_yaml_path.exists(), f"Result YAML exists at {result_yaml_path}")

    result_yaml = yaml_load(result_yaml_path)
    check(result_yaml is not None, "Result YAML parsed successfully")
    if result_yaml:
        check(result_yaml.get("phase") == "phase99a", "Result YAML phase is phase99a")
        check(result_yaml.get("total_cases") >= 12, f"Result YAML total_cases >= 12 ({result_yaml.get('total_cases')})")
        check(result_yaml.get("breakthrough_detected_count") == 0, "Result YAML breakthrough count is 0")
        check(result_yaml.get("successful_cases") == result_yaml.get("total_cases"), "All cases marked successful")
        check_security_fields(result_yaml, "Result YAML")

    # ================================================================
    # 5. Capability Scorecard Verification
    # ================================================================
    print("\n[5] Capability Scorecard Verification")
    scorecard_path = ROOT / "executions/phase99a_m43_m45_adv/capability_scorecard.yaml"
    check(scorecard_path.exists(), f"Capability Scorecard exists at {scorecard_path}")

    scorecard = yaml_load(scorecard_path)
    check(scorecard is not None, "Capability Scorecard parsed successfully")
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        rs = scorecard.get("results_summary", {})
        check(sm.get("phase") == "phase99a", "Scorecard phase is phase99a")
        check(rs.get("breakthrough_detected") == 0, "Scorecard breakthrough detected is 0")
        check(rs.get("control_passed") >= 2, "Scorecard control cases passed >= 2")
        check(rs.get("control_failed") == 0, "Scorecard control failed is 0")
        check(scorecard.get("capability_value") == "high", "Capability value is high")
        check(scorecard.get("risk_level") == "low", "Simulated risk level is low")
        check(len(scorecard.get("category_coverage", [])) >= 12, "Scorecard covers all 12 categories")
        check_security_fields(sm, "Scorecard metadata")

    # ================================================================
    # 6. Documentation & Summary Verification
    # ================================================================
    print("\n[6] Documentation & Summary Verification")
    notes_path = ROOT / "docs/phase99a_m43_m45_advanced_supply_chain_notes.md"
    check(notes_path.exists(), f"Notes doc exists at {notes_path}")

    summary_path = ROOT / "phase99a_m43m45_001_execution_summary.yaml"
    check(summary_path.exists(), f"Execution summary exists at {summary_path}")

    summary = yaml_load(summary_path)
    check(summary is not None, "Execution summary parsed successfully")
    if summary:
        check(summary.get("task_id") == "Phase-99A-M43M45-001", "Summary task_id matches")
        sb = summary.get("safety_boundaries", {})
        check(sb.get("confirmed_vulnerability") is False, "Summary confirmed_vulnerability is False")
        check(sb.get("formal_finding_allowed") is False, "Summary formal_finding_allowed is False")
        check(sb.get("production_safety_claimed") is False, "Summary production_safety_claimed is False")
        check(sb.get("synthetic_only") is True, "Summary synthetic_only is True")
        check(sb.get("requires_human_review") is True, "Summary requires_human_review is True")
        tr = summary.get("test_results", {})
        check(tr.get("breakthroughs") == 0, "Summary test_results breakthroughs == 0")
        check(tr.get("status") == "PASS", "Summary test_results status is PASS")

    # ================================================================
    # 7. Summary of Validation
    # ================================================================
    print("\n" + "=" * 70)
    print(f"Validation Finished: {checks_passed} PASSED, {checks_failed} FAILED")
    print("=" * 70)

    if checks_failed > 0:
        print("\nErrors encountered:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nALL VERIFICATION CHECKS PASSED (100% OK).\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
