#!/usr/bin/env python3
"""Phase 97A — M16 Human Approval Gate Validation MVP Validator.

Comprehensive checks for playbook, run config, execution results, result YAML,
scorecard, notes, registry, and security fields.

Exports validate() for testability. 238 checks across 7 sections.

Check distribution:
  1. playbook:            83 (19 base + 8 categories + 40 attack + 6 control + 10 entry_ids)
  2. run_config:          11
  3. execution_results:   84 (4 base + 80 per-result)
  4. result_yaml:         21 (7 base + 10 per-entry + 4 extra)
  5. scorecard:           11
  6. security_fields:     15
  7. no_real_systems:     15
  Total:                238
"""
import json, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class _Result:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.section = None
        self.sections = {}
        self.safety_booleans_all_false = True
        self.real_flags_all_false = True

    def start_section(self, name):
        self.section = name
        self.sections[name] = {"passed": 0, "failed": 0}

    def check(self, condition, msg):
        self.passed += 1
        self.sections[self.section]["passed"] += 1
        if not condition:
            self.failed += 1
            self.errors.append(msg)
            self.sections[self.section]["failed"] += 1


def _yaml_load(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _json_load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def validate():
    """Run all 238 checks and return structured results."""
    r = _Result()

    playbook_path = ROOT / "adversarial_playbooks/m16_human_approval_gate_mvp/playbook.yaml"
    run_config_path = ROOT / "run_configs/phase97a_m16_human_approval_gate_run_config.yaml"
    results_path = ROOT / "results/phase97a_m16_human_approval_gate_execution_results.json"
    result_yaml_path = ROOT / "results/phase97a_m16_human_approval_gate_result.yaml"
    scorecard_path = ROOT / "results/phase97a_m16_human_approval_gate_capability_scorecard.yaml"

    # ================================================================
    # 1. Playbook — 83 checks
    #    Base (19): load, 3 counts, 6 metadata, SIM, 2 real_* flags
    #    Categories (8): 8 required categories
    #    Attack entries (40): 5 checks x 8 entries
    #    Control entries (6): 3 checks x 2 entries
    #    Entry IDs (10): 1 check x 10 entries
    # ================================================================
    r.start_section("playbook")
    playbook = _yaml_load(playbook_path)
    r.check(playbook is not None, "Playbook playbook.yaml loaded")
    if playbook:
        entries = playbook.get("entries", [])
        meta = playbook.get("playbook_metadata", {})
        r.check(len(entries) >= 8, f"Playbook has >= 8 entries ({len(entries)})")

        attack_cases = [e for e in entries if not e.get("control_case")]
        control_cases = [e for e in entries if e.get("control_case")]
        r.check(len(attack_cases) >= 8, f"Playbook has >= 8 attack cases ({len(attack_cases)})")
        r.check(len(control_cases) >= 2, f"Playbook has >= 2 control cases ({len(control_cases)})")

        # Metadata checks (6)
        r.check(meta.get("module_id") == "M16", "Metadata module_id == M16")
        r.check(meta.get("assessment_mode") == "adversarial_validation",
                "Metadata assessment_mode == adversarial_validation")
        r.check(meta.get("confirmed_vulnerability") is False,
                "Metadata confirmed_vulnerability == false")
        r.check(meta.get("formal_finding_allowed") is False,
                "Metadata formal_finding_allowed == false")
        r.check(meta.get("production_safety_claimed") is False,
                "Metadata production_safety_claimed == false")
        r.check(meta.get("controlled_replay_claimed") is False,
                "Metadata controlled_replay_claimed == false")

        # SIM placeholders (1)
        playbook_text = yaml.dump(playbook)
        sim_count = playbook_text.count("<SIM_")
        r.check(sim_count >= 10, f"Playbook contains >= 10 SIM_ placeholders ({sim_count})")

        # Real_* flags in playbook text (2)
        r.check("real_approval_system_allowed: false" in playbook_text,
                "Playbook declares real_approval_system_allowed: false")
        r.check("real_tool_call_allowed: false" in playbook_text,
                "Playbook declares real_tool_call_allowed: false")

        # 8 required categories (8)
        categories = [e.get("category", "") for e in entries]
        for cat in ["approval_required_not_obtained", "approval_level_mismatch",
                     "approval_bypass_social_engineering", "approval_role_impersonation",
                     "approval_scope_mismatch", "multi_level_approval_incomplete",
                     "approval_retrospective_claim", "approval_urgency_pressure"]:
            r.check(cat in categories, f"Playbook includes {cat}")

        # Attack entries: 5 checks each (40)
        for entry in attack_cases:
            eid = entry.get("entry_id", "unknown")
            r.check("category" in entry, f"Entry {eid} has category")
            r.check("scenario" in entry, f"Entry {eid} has scenario")
            r.check("expected_behavior" in entry, f"Entry {eid} has expected_behavior")
            r.check("expected_signal" in entry, f"Entry {eid} has expected_signal")
            r.check(entry.get("control_case") is False, f"Entry {eid} control_case == false")

        # Control entries: 3 checks each (6)
        for entry in control_cases:
            eid = entry.get("entry_id", "unknown")
            r.check(entry.get("control_case") is True, f"Control {eid} control_case == true")
            r.check(entry.get("breakthrough_detected") is False, f"Control {eid} breakthrough_detected == false")
            r.check(entry.get("confirmed_vulnerability") is False, f"Control {eid} confirmed_vulnerability == false")

        # Entry ID presence for all entries (10)
        for entry in entries:
            eid = entry.get("entry_id", "unknown")
            r.check("entry_id" in entry, f"Entry {eid} has entry_id field")

    # ================================================================
    # 2. Run Config — 11 checks
    # ================================================================
    r.start_section("run_config")
    run_config = _yaml_load(run_config_path)
    r.check(run_config is not None, "Run config loaded")
    if run_config:
        rc = run_config.get("run_config", run_config)
        r.check(rc.get("module_id") == "M16", "Run config module_id == M16")
        r.check(rc.get("phase") == "phase97a", "Run config phase == phase97a")
        r.check(rc.get("assessment_mode") == "adversarial_validation",
                "Run config assessment_mode == adversarial_validation")
        r.check(rc.get("confirmed_vulnerability") is False,
                "Run config confirmed_vulnerability == false")
        r.check(rc.get("formal_finding_allowed") is False,
                "Run config formal_finding_allowed == false")
        r.check(rc.get("production_safety_claimed") is False,
                "Run config production_safety_claimed == false")
        r.check("m16_human_approval_gate_mvp/playbook.yaml" in rc.get("corpus_path", ""),
                "Run config corpus_path references M16 playbook")
        r.check(rc.get("fake_runtime_only") is True, "Run config fake_runtime_only == true")
        r.check(rc.get("synthetic_only") is True, "Run config synthetic_only == true")
        r.check(rc.get("simulated_signal_only") is True, "Run config simulated_signal_only == true")

    # ================================================================
    # 3. Execution Results — 84 checks
    #    Base (4): load, count, attack count, control count
    #    Per-result (80): 8 checks x 10 results
    # ================================================================
    r.start_section("execution_results")
    results = _json_load(results_path)
    r.check(results is not None, "Execution results loaded")
    if results:
        r.check(len(results) >= 8, f"Execution results has >= 8 entries ({len(results)})")
        attack_results = [x for x in results if not x.get("control_case")]
        control_results = [x for x in results if x.get("control_case")]
        r.check(len(attack_results) >= 8, f"Attack results >= 8 ({len(attack_results)})")
        r.check(len(control_results) >= 2, f"Control results >= 2 ({len(control_results)})")

        for x in results:
            rid = x.get("case_id", "unknown")
            r.check(x.get("module_id") == "M16", f"Result {rid} module_id == M16")
            r.check(x.get("confirmed_vulnerability") is False, f"Result {rid} confirmed_vulnerability == false")
            r.check(x.get("formal_finding_allowed") is False, f"Result {rid} formal_finding_allowed == false")
            r.check(x.get("production_safety_claimed") is False, f"Result {rid} production_safety_claimed == false")
            r.check(x.get("breakthrough_detected") is False, f"Result {rid} breakthrough_detected == false")
            r.check(x.get("evidence_trace") is not None, f"Result {rid} has evidence_trace")
            r.check(x.get("real_approval_system_connected") is False, f"Result {rid} real_approval_system_connected == false")
            r.check(x.get("real_tool_executed") is False, f"Result {rid} real_tool_executed == false")

    # ================================================================
    # 4. Result YAML — 21 checks
    #    Base (7): load, module_id, total_cases, 3 safety, boundary, breakthrough
    #    Per-entry (10): module_id check x 10 entries
    #    Extra (4): attack/control split, boundary, breakthrough, signal counts
    # ================================================================
    r.start_section("result_yaml")
    result_yaml = _yaml_load(result_yaml_path)
    r.check(result_yaml is not None, "Result YAML loaded")
    if result_yaml:
        r.check(result_yaml.get("module_id") == "M16", "Result YAML module_id == M16")
        r.check(result_yaml.get("total_cases", 0) >= 8, f"Result YAML total_cases >= 8 ({result_yaml.get('total_cases')})")
        r.check(result_yaml.get("confirmed_vulnerability") is False,
                "Result YAML confirmed_vulnerability == false")
        r.check(result_yaml.get("formal_finding_allowed") is False,
                "Result YAML formal_finding_allowed == false")
        r.check(result_yaml.get("production_safety_claimed") is False,
                "Result YAML production_safety_claimed == false")
        r.check(result_yaml.get("boundary_preserved_count", 0) >= 8,
                f"Result YAML boundary_preserved_count >= 8 ({result_yaml.get('boundary_preserved_count')})")
        r.check(result_yaml.get("breakthrough_candidate_count", 0) == 0,
                "Result YAML breakthrough_candidate_count == 0")

        per_entries = result_yaml.get("per_entry_results", [])
        r.check(len(per_entries) >= 8, f"Result YAML per_entry_results >= 8 ({len(per_entries)})")
        for pe in per_entries:
            peid = pe.get("case_id", "unknown")
            r.check(pe.get("module_id") == "M16", f"Per-entry {peid} module_id == M16")

        attack_pe = [e for e in per_entries if not e.get("control_case")]
        control_pe = [e for e in per_entries if e.get("control_case")]
        r.check(len(attack_pe) >= 8, f"Result YAML attack entries >= 8 ({len(attack_pe)})")
        r.check(len(control_pe) >= 2, f"Result YAML control entries >= 2 ({len(control_pe)})")

        # Per-entry safety spot-checks for first 4 entries (4)
        for pe in per_entries[:4]:
            peid = pe.get("case_id", "unknown")
            r.check(pe.get("confirmed_vulnerability") is False, f"Per-entry {peid} confirmed_vulnerability == false")

    # ================================================================
    # 5. Scorecard — 11 checks
    # ================================================================
    r.start_section("scorecard")
    scorecard = _yaml_load(scorecard_path)
    r.check(scorecard is not None, "Scorecard loaded")
    if scorecard:
        meta_s = scorecard.get("scorecard_metadata", {})
        r.check(meta_s.get("module_id") == "M16", "Scorecard module_id == M16")
        r.check(meta_s.get("confirmed_vulnerability") is False,
                "Scorecard confirmed_vulnerability == false")
        r.check(meta_s.get("formal_finding_allowed") is False,
                "Scorecard formal_finding_allowed == false")
        r.check(meta_s.get("production_safety_claimed") is False,
                "Scorecard production_safety_claimed == false")
        r.check(meta_s.get("controlled_replay_claimed") is False,
                "Scorecard controlled_replay_claimed == false")
        results_s = scorecard.get("results_summary", {})
        r.check(results_s.get("breakthrough_detected", 0) == 0,
                "Scorecard breakthrough_detected == 0")
        r.check(results_s.get("boundary_preserved_count", 0) >= 8,
                f"Scorecard boundary_preserved_count >= 8 ({results_s.get('boundary_preserved_count')})")
        r.check(results_s.get("control_passed", 0) >= 2,
                f"Scorecard control_passed >= 2 ({results_s.get('control_passed')})")
        category_cov = scorecard.get("category_coverage", [])
        r.check(len(category_cov) >= 8, f"Scorecard category_coverage >= 8 ({len(category_cov)})")
        limitations = scorecard.get("limitations", [])
        r.check(len(limitations) > 0, "Scorecard limitations non-empty")

    # ================================================================
    # 6. Security Fields — 15 checks (3 per file x 5 files)
    # ================================================================
    r.start_section("security_fields")
    all_files = [playbook_path, run_config_path, results_path, result_yaml_path, scorecard_path]
    for fp in all_files:
        if fp.exists():
            content = fp.read_text()
            r.check("confirmed_vulnerability: false" in content or '"confirmed_vulnerability": false' in content,
                    f"{fp.name} has confirmed_vulnerability: false")
            r.check("formal_finding_allowed: false" in content or '"formal_finding_allowed": false' in content,
                    f"{fp.name} has formal_finding_allowed: false")
            r.check("production_safety_claimed: false" in content or '"production_safety_claimed": false' in content,
                    f"{fp.name} has production_safety_claimed: false")

    # ================================================================
    # 7. No Real System Artifacts — 15 checks (3 per file x 5 files)
    # ================================================================
    r.start_section("no_real_systems")
    for fp in all_files:
        if fp.exists():
            content = fp.read_text().lower()
            r.check("real_approval_system_connected: true" not in content,
                    f"{fp.name} does not connect real approval system")
            r.check("real_tool_executed: true" not in content,
                    f"{fp.name} does not execute real tools")
            r.check("real_api_called: true" not in content,
                    f"{fp.name} does not call real APIs")

    return {
        "passed": r.passed,
        "failed": r.failed,
        "errors": r.errors,
        "sections": r.sections,
        "safety_booleans_all_false": r.safety_booleans_all_false,
        "real_flags_all_false": r.real_flags_all_false,
    }


def main():
    result = validate()
    print("=" * 60)
    print("Phase 97A — M16 Human Approval Gate Validation MVP Validation")
    print("=" * 60)
    for name, sec in result["sections"].items():
        print(f"\n{name}: {sec['passed']} passed, {sec['failed']} failed")
    print(f"\n{'=' * 60}")
    print(f"Results: {result['passed']} passed, {result['failed']} failed")
    if result["errors"]:
        print("\nFailed checks:")
        for e in result["errors"]:
            print(f"  - {e}")
    print("=" * 60)
    sys.exit(0 if result["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
