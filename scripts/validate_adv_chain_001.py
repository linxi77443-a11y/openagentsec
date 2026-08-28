#!/usr/bin/env python3
"""ADV-CHAIN-001 — Validate Attack Chain Deep Exploitation Design Blueprint.

Checks:
- All 8 deliverable files exist
- Security fields consistent across all YAML files
- Design gate only constraints (no execution, no corpus, no payload)
- Blueprint content structure (3 stages, 9 playbook outlines)
- Blueprint mapping completeness (ADV + RED + module references)
- Design gate result completeness
- Reused baseline index completeness
- Candidate signal schema (9 signals, breakthrough semantics)
- Human review gate (9 playbook review requirements)
- No real data patterns
- No prohibited declarations
"""
import sys, os, re, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

checks = []
findings = []

def check(name: str, ok: bool, detail: str = ""):
    checks.append({"name": name, "pass": ok, "detail": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

def finding(cat: str, item: str, field: str, detail: str):
    findings.append({"category": cat, "item": item, "field": field, "detail": detail})
    print(f"  [FINDING] {cat}: {item} / {field}: {detail}")

def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_text(path):
    return path.read_text(encoding="utf-8")

# ── File paths ──
CHAIN_DIR = ROOT / "red_team" / "adv_chain_001"
DESIGN_BLUEPRINT = CHAIN_DIR / "adv_chain_001_design_blueprint.md"
BLUEPRINT_MAPPING = CHAIN_DIR / "blueprint_mapping.yaml"
DESIGN_GATE_RESULT = CHAIN_DIR / "design_gate_result.yaml"
REUSED_BASELINE_INDEX = CHAIN_DIR / "reused_baseline_index.yaml"
CANDIDATE_SIGNAL_SCHEMA = CHAIN_DIR / "candidate_signal_schema.yaml"
HUMAN_REVIEW_GATE = CHAIN_DIR / "human_review_gate.yaml"
SHORT_NOTES = CHAIN_DIR / "short_notes.md"
VALIDATE_SCRIPT = ROOT / "scripts" / "validate_adv_chain_001.py"

REQUIRED_FILES = [
    DESIGN_BLUEPRINT,
    BLUEPRINT_MAPPING,
    DESIGN_GATE_RESULT,
    REUSED_BASELINE_INDEX,
    CANDIDATE_SIGNAL_SCHEMA,
    HUMAN_REVIEW_GATE,
    SHORT_NOTES,
    VALIDATE_SCRIPT,
]

YAML_FILES = [
    BLUEPRINT_MAPPING,
    DESIGN_GATE_RESULT,
    REUSED_BASELINE_INDEX,
    CANDIDATE_SIGNAL_SCHEMA,
    HUMAN_REVIEW_GATE,
]

REQUIRED_STAGE_IDS = ["chain_recon_01", "chain_recon_02", "chain_recon_03",
                       "chain_exfil_01", "chain_exfil_02", "chain_exfil_03",
                       "chain_persist_01", "chain_persist_02", "chain_persist_03"]

REQUIRED_PLAYBOOK_IDS = ["CHAIN-RECON-01", "CHAIN-RECON-02", "CHAIN-RECON-03",
                          "CHAIN-EXFIL-01", "CHAIN-EXFIL-02", "CHAIN-EXFIL-03",
                          "CHAIN-PERSIST-01", "CHAIN-PERSIST-02", "CHAIN-PERSIST-03"]

REQUIRED_ADV_PLAYBOOKS = ["ADV-ROLE-001", "ADV-ENCODE-001", "ADV-OPPO-001", "ADV-MULTILANG-001"]
REQUIRED_RED_REPORTS = [f"RED-{i:03d}" for i in range(1, 12)]
REQUIRED_MODULES = ["M04", "M07", "M08", "M12", "M13", "M14", "M15", "M19",
                     "M38", "M39", "M41", "M46", "M47", "M48", "M49", "M50"]

REAL_DATA_PATTERNS = [
    r'@[a-zA-Z0-9]+\.[a-zA-Z]{2,}\b',
]

SECURITY_FIELDS_FALSE = [
    "confirmed_vulnerability",
    "formal_finding_allowed",
    "production_safety_claimed",
    "controlled_replay_claimed",
    "attack_execution_allowed",
    "payload_generation_allowed",
    "controlled_replay_execution_allowed",
    "replay_executable",
    "capability_engine_execution_allowed",
    "execution_results_generation_allowed",
    "new_corpus_created",
    "capability_value_declared",
    "risk_level_declared",
    "new_score_calculation_performed",
    "real_system_connection_allowed",
    "real_api_call_allowed",
    "real_tool_execution_allowed",
    "real_data_access_allowed",
    "real_target_selection_allowed",
    "red_team_action_report",
    "attack_chain_execution_allowed",
    "exploit_execution_allowed",
    "asset_theft_execution_allowed",
    "persistence_execution_allowed",
]
SECURITY_FIELDS_TRUE = [
    "all_findings_are_candidate_level",
    "requires_human_review",
    "design_gate_only",
    "synthetic_only",
    "red_team_engine_not_executable",
    "dashboard_not_execution_interface",
    "not_attack_platform",
    "not_vulnerability_discovery_tool",
    "all_chain_steps_are_design_candidates_only",
    "not_red_team_action_report",
    "baseline_reference_only",
]

def check_all_yaml_security_fields(data, source_file):
    """Recursively check security fields in YAML structure."""
    if not isinstance(data, dict):
        return
    for key, val in data.items():
        if key in SECURITY_FIELDS_FALSE and val is not False:
            finding("security_field", source_file, key, f"expected false, got {val}")
        elif key in SECURITY_FIELDS_TRUE and val is not True:
            finding("security_field", source_file, key, f"expected true, got {val}")
        else:
            check_all_yaml_security_fields(val, source_file)

def main():
    print("=" * 60)
    print("ADV-CHAIN-001 — Attack Chain Deep Exploitation Design Blueprint Validation")
    print("=" * 60)

    # ── A. File existence (8 checks) ──
    print("\n--- A. File Existence ---")
    all_files_exist = True
    for f in REQUIRED_FILES:
        exists = f.exists()
        if not exists:
            all_files_exist = False
            finding("missing_file", str(f), "exists", "file not found")
        check(f"File exists: {f.name}", exists)
    if not all_files_exist:
        print("\n[FAIL] Required files missing. Aborting.")
        sys.exit(1)

    # ── B. Security field recursive scan ──
    print("\n--- B. Security Field Recursive Scan ---")
    for yf in YAML_FILES:
        data = load_yaml(yf)
        check_all_yaml_security_fields(data, yf.name)

    # ── C. Design gate only constraints ──
    print("\n--- C. Design Gate Only Constraints ---")
    dg_data = load_yaml(DESIGN_GATE_RESULT)
    check("design_gate_only=true", dg_data.get("design_gate_only") is True)
    check("design_blueprint_only=true", dg_data.get("design_blueprint_only") is True)
    check("attack_execution_allowed=false", dg_data.get("attack_execution_allowed") is False)
    check("payload_generation_allowed=false", dg_data.get("payload_generation_allowed") is False)
    check("controlled_replay_execution_allowed=false", dg_data.get("controlled_replay_execution_allowed") is False)
    check("replay_executable=false", dg_data.get("replay_executable") is False)
    check("capability_engine_executed=false", dg_data.get("capability_engine_executed") is False)
    check("execution_results_generated=false", dg_data.get("execution_results_generated") is False)
    check("new_corpus_created=false", dg_data.get("new_corpus_created") is False)
    check("adversarial_playbook_created=false", dg_data.get("adversarial_playbook_created") is False)

    # ── D. Blueprint content structure ──
    print("\n--- D. Blueprint Content Structure ---")
    bp_text = read_text(DESIGN_BLUEPRINT)
    for pid in REQUIRED_PLAYBOOK_IDS:
        check(f"Playbook outline present: {pid}", pid in bp_text)
    for sid in REQUIRED_STAGE_IDS:
        check(f"Stage ID present: {sid}", sid in bp_text)
    # Check required sections
    for section in ["非执行边界声明", "人工审核门", "Phase 86B Schema 引用",
                    "跨阶段依赖关系", "后续拆分建议"]:
        check(f"Required section: {section}", section in bp_text)
    # Check required fields per playbook outline
    for field in ["attack_objective", "attacker_type", "candidate_only",
                  "requires_human_review", "预期防御行为", "预期候选信号",
                  "非执行边界"]:
        check(f"Playbook field present: {field}", field in bp_text)

    # ── E. Blueprint mapping completeness ──
    print("\n--- E. Blueprint Mapping Completeness ---")
    map_data = load_yaml(BLUEPRINT_MAPPING)
    mappings = map_data.get("mappings", [])
    check("Mappings list present", len(mappings) > 0, f"{len(mappings)} entries")
    # Check required fields in each mapping
    required_map_fields = ["mapping_id", "source_playbook", "source_red_report",
                           "source_module", "source_corpus_ref", "source_evidence_trace_ref",
                           "target_stage", "target_candidate_signal"]
    for m in mappings:
        mid = m.get("mapping_id", "UNKNOWN")
        for rf in required_map_fields:
            if rf not in m:
                finding("mapping_field_missing", mid, rf, "field not found")
    # Check ADV playbooks referenced
    source_playbooks = set()
    for m in mappings:
        sp = m.get("source_playbook", "N/A")
        if sp != "N/A":
            source_playbooks.add(sp)
    for ap in REQUIRED_ADV_PLAYBOOKS:
        check(f"ADV playbook mapped: {ap}", ap in source_playbooks)

    # ── F. Design gate result completeness ──
    print("\n--- F. Design Gate Result Completeness ---")
    check("non_execution_summary exists", "non_execution_summary" in dg_data)
    if "non_execution_summary" in dg_data:
        nes = dg_data["non_execution_summary"]
        for field in ["confirmed_vulnerability", "formal_finding_allowed",
                       "production_safety_claimed", "controlled_replay_claimed",
                       "replay_executable", "controlled_replay_execution_allowed",
                       "real_system_connection_used", "real_api_called",
                       "real_tool_executed", "real_secret_used"]:
            if field in nes:
                check(f"non_execution_summary.{field}=false", nes[field] is False)
    check("design_gate_deliverables lists 8 files",
          len(dg_data.get("design_gate_deliverables", [])) == 8)
    check("stage_summaries covers 3 stages",
          len(dg_data.get("stage_summaries", [])) == 3)
    # Reuse summary
    rs = dg_data.get("reuse_summary", {})
    check("reuse_summary.source_playbooks_referenced has 4 ADV",
          len(rs.get("source_playbooks_referenced", [])) == 4)
    check("reuse_summary.source_red_reports_referenced has 11",
          len(rs.get("source_red_reports_referenced", [])) == 11)
    check("reuse_summary.source_modules_referenced has 16",
          len(rs.get("source_modules_referenced", [])) == 16)
    check("reuse_summary.schema_freeze_referenced",
          rs.get("schema_freeze_referenced") is True)
    check("reuse_summary.baseline_reference_only",
          rs.get("baseline_reference_only") is True)

    # ── G. Reused baseline index ──
    print("\n--- G. Reused Baseline Index ---")
    bi_data = load_yaml(REUSED_BASELINE_INDEX)
    check("reused_playbooks section", "reused_playbooks" in bi_data)
    if "reused_playbooks" in bi_data:
        pb_ids = [p["playbook_id"] for p in bi_data["reused_playbooks"] if "playbook_id" in p]
        for ap in REQUIRED_ADV_PLAYBOOKS:
            check(f"Reused playbook: {ap}", ap in pb_ids)
    check("reused_red_reports section", "reused_red_reports" in bi_data)
    if "reused_red_reports" in bi_data:
        rr_ids = [r["report_id"] for r in bi_data["reused_red_reports"] if "report_id" in r]
        for rr in REQUIRED_RED_REPORTS:
            check(f"Reused RED report: {rr}", rr in rr_ids)
    check("reused_modules section", "reused_modules" in bi_data)
    if "reused_modules" in bi_data:
        mod_ids = [m["module_id"] for m in bi_data["reused_modules"] if "module_id" in m]
        for rm in REQUIRED_MODULES:
            check(f"Reused module: {rm}", rm in mod_ids)
    check("reused_schema section", "reused_schema" in bi_data)
    check("capability_value_risk_level noted as reused baseline only",
          bi_data.get("no_new_capability_score_calculated") is True)

    # ── H. Candidate signal schema ──
    print("\n--- H. Candidate Signal Schema ---")
    cs_data = load_yaml(CANDIDATE_SIGNAL_SCHEMA)
    signals = cs_data.get("signal_definitions", [])
    check("9 signal definitions", len(signals) == 9, f"got {len(signals)}")
    for sig in signals:
        sid = sig.get("signal_id", "UNKNOWN")
        check(f"Signal {sid}: playbook_outline_id present", "playbook_outline_id" in sig)
        check(f"Signal {sid}: signal_name present", "signal_name" in sig)
        check(f"Signal {sid}: candidate_only=true", sig.get("candidate_only") is True)
        check(f"Signal {sid}: confirmed_vulnerability=false", sig.get("confirmed_vulnerability") is False)
        check(f"Signal {sid}: source_evidence_trace_refs list", len(sig.get("source_evidence_trace_refs", [])) > 0)
    check("signal_aggregation section", "signal_aggregation" in cs_data)
    check("breakthrough_signal_semantics section", "breakthrough_signal_semantics" in cs_data)
    if "breakthrough_signal_semantics" in cs_data:
        bss = cs_data["breakthrough_signal_semantics"]
        check("breakthrough is candidate-only design signal",
              bss.get("breakthrough_detected_is_candidate_only_design_signal") is True)
        check("breakthrough != confirmed vulnerability",
              bss.get("does_not_equal_confirmed_vulnerability") is True)

    # ── I. Human review gate ──
    print("\n--- I. Human Review Gate ---")
    hrg_data = load_yaml(HUMAN_REVIEW_GATE)
    hrg = hrg_data.get("human_review_gate", {})
    check("human_review_gate.human_review_required=true",
          hrg.get("human_review_required") is True)
    check("human_review_gate.formal_finding_requires_manual_review=true",
          hrg.get("formal_finding_requires_manual_review") is True)
    check("human_review_gate.controlled_replay_requires_separate_approval=true",
          hrg.get("controlled_replay_requires_separate_approval") is True)
    check("human_review_gate.all_findings_are_candidate_level=true",
          hrg.get("all_findings_are_candidate_level") is True)
    playbook_reqs = hrg_data.get("playbook_outline_review_requirements", [])
    check("9 playbook outline review requirements", len(playbook_reqs) == 9,
          f"got {len(playbook_reqs)}")
    for pr in playbook_reqs:
        pid = pr.get("playbook_outline_id", "UNKNOWN")
        check(f"Playbook {pid}: requires_human_review_for_execution=true",
              pr.get("requires_human_review_for_execution") is True)
        check(f"Playbook {pid}: review_gate_criteria list",
              len(pr.get("review_gate_criteria", [])) > 0)
    check("candidate_counts section", "candidate_counts" in hrg_data)
    cc = hrg_data.get("candidate_counts", {})
    check("candidate_counts.candidate_signals_defined=9",
          cc.get("candidate_signals_defined") == 9)
    check("candidate_counts.playbook_outlines=9",
          cc.get("playbook_outlines") == 9)
    check("candidate_counts.stages=3",
          cc.get("stages") == 3)
    check("candidate_status section", "candidate_status" in hrg_data)
    cs_status = hrg_data.get("candidate_status", {})
    check("candidate_status.candidate_upgraded_to_finding=false",
          cs_status.get("candidate_upgraded_to_finding") is False)
    check("review_notes section", "review_notes" in hrg_data)

    # ── J. No real data check ──
    print("\n--- J. No Real Data Check ---")
    for yf in YAML_FILES:
        raw = read_text(yf)
        for pattern in REAL_DATA_PATTERNS:
            matches = re.findall(pattern, raw)
            for m in matches:
                # Filter out SIM_ placeholders and markdown headers
                if "SIM_" not in m and not m.startswith("#"):
                    finding("real_data_pattern", yf.name, pattern, f"potential real data: {m}")
    # Check all evidence_trace and source_evidence_trace_ref values use SIM_ format
    for yf in YAML_FILES:
        data = load_yaml(yf)
        def scan_evidence_refs(d, path=""):
            if not isinstance(d, dict):
                return
            for k, v in d.items():
                fp = f"{path}.{k}" if path else k
                if k in ("evidence_trace", "source_evidence_trace_ref", "evidence_trace_refs"):
                    if isinstance(v, str) and v and not v.startswith("<SIM_") and v != "N/A":
                        finding("non_sim_evidence_trace", yf.name, fp,
                                f"expected <SIM_...> or N/A, got: {v}")
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, str) and not item.startswith("<SIM_") and item != "N/A":
                                finding("non_sim_evidence_trace", yf.name, fp,
                                        f"expected <SIM_...> or N/A, got: {item}")
                scan_evidence_refs(v, fp)
        scan_evidence_refs(data)

    # ── K. No prohibited declarations ──
    print("\n--- K. No Prohibited Declarations ---")
    for yf in YAML_FILES:
        data = load_yaml(yf)
        def scan_prohibited(d, path=""):
            if not isinstance(d, dict):
                return
            for k, v in d.items():
                fp = f"{path}.{k}" if path else k
                # Skip semantic description fields that use "true" to describe the prohibition
                if k.startswith("does_not_") or k.startswith("no_") or k.endswith("_semantics"):
                    scan_prohibited(v, fp)
                    continue
                if k in ("confirmed_vulnerability", "formal_finding_allowed",
                         "production_safety_claimed", "attack_execution_allowed",
                         "payload_generation_allowed", "controlled_replay_execution_allowed",
                         "replay_executable") and v is True:
                    finding("prohibited_declaration", yf.name, fp,
                            "should not be true")
                # Design gate must not declare capability_value or risk_level directly
                if k in ("capability_value", "risk_level") and isinstance(v, str):
                    finding("prohibited_capability_risk_declaration", yf.name, fp,
                            "design gate must not declare capability_value/risk_level directly; use baseline_*_reference fields instead")
                scan_prohibited(v, fp)
        scan_prohibited(data)

    # ── L. v3.1 §4 — 模拟红队专项安全字段 —─
    print("\n--- L. v3.1 §4 — 模拟红队专项安全字段 ---")
    v31_fields = [
        "synthetic_only", "real_system_connection_allowed", "real_api_call_allowed",
        "real_tool_execution_allowed", "real_data_access_allowed", "real_target_selection_allowed",
        "red_team_engine_not_executable", "dashboard_not_execution_interface",
        "not_attack_platform", "not_vulnerability_discovery_tool",
    ]
    semantic_freeze_fields = [
        "attack_chain_execution_allowed", "exploit_execution_allowed",
        "asset_theft_execution_allowed", "persistence_execution_allowed",
        "all_chain_steps_are_design_candidates_only",
        "red_team_action_report", "not_red_team_action_report",
    ]
    baseline_ref_fields = [
        "capability_value_declared", "risk_level_declared",
        "baseline_capability_value_reference", "baseline_risk_level_reference",
        "baseline_reference_only", "new_score_calculation_performed",
    ]
    for yf in YAML_FILES:
        data = load_yaml(yf)
        def scan_v31_fields(d, path=""):
            if not isinstance(d, dict):
                return
            for k, v in d.items():
                fp = f"{path}.{k}" if path else k
                if k in v31_fields:
                    if k.endswith("_allowed") and v is not False:
                        finding("v31_field_violation", yf.name, fp,
                                f"expected false, got {v}")
                    elif k in ("synthetic_only", "red_team_engine_not_executable",
                               "dashboard_not_execution_interface", "not_attack_platform",
                               "not_vulnerability_discovery_tool") and v is not True:
                        finding("v31_field_violation", yf.name, fp,
                                f"expected true, got {v}")
                if k in semantic_freeze_fields:
                    if k.endswith("_allowed") and v is not False:
                        finding("semantic_freeze_violation", yf.name, fp,
                                f"expected false, got {v}")
                    elif k in ("all_chain_steps_are_design_candidates_only",
                               "not_red_team_action_report") and v is not True:
                        finding("semantic_freeze_violation", yf.name, fp,
                                f"expected true, got {v}")
                    elif k == "red_team_action_report" and v is not False:
                        finding("semantic_freeze_violation", yf.name, fp,
                                "red_team_action_report must be false for design gate")
                if k in baseline_ref_fields:
                    if k in ("capability_value_declared", "risk_level_declared",
                             "new_score_calculation_performed") and v is not False:
                        finding("baseline_ref_violation", yf.name, fp,
                                f"expected false, got {v}")
                    elif k == "baseline_reference_only" and v is not True:
                        finding("baseline_ref_violation", yf.name, fp,
                                f"expected true, got {v}")
                scan_v31_fields(v, fp)
        scan_v31_fields(data)

    # Check all 9 candidate signals have required security fields
    print("\n--- M. 候选信号安全字段验证 ---")
    cs_data = load_yaml(CANDIDATE_SIGNAL_SCHEMA)
    signals = cs_data.get("signal_definitions", [])
    required_signal_fields = {
        "candidate_only": True,
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
    }
    for sig in signals:
        sid = sig.get("signal_id", "UNKNOWN")
        for field, expected in required_signal_fields.items():
            actual = sig.get(field)
            if actual is expected:
                check(f"Signal {sid}: {field}={expected}", True)
            else:
                check(f"Signal {sid}: {field}={expected}", False,
                      f"got {actual}")
    # Also check human_review_gate for each signal (requires_human_review_for_execution)
    hrg_data = load_yaml(HUMAN_REVIEW_GATE)
    playbook_reqs = hrg_data.get("playbook_outline_review_requirements", [])
    for pr in playbook_reqs:
        pid = pr.get("playbook_outline_id", "UNKNOWN")
        check(f"Playbook {pid}: requires_human_review_for_execution=true",
              pr.get("requires_human_review_for_execution") is True)

    # Verify no YAML file directly declares capability_value or risk_level as top-level key
    print("\n--- N. 禁止直接声明 capability_value/risk_level ---")
    for yf in YAML_FILES:
        data = load_yaml(yf)
        raw = read_text(yf)
        # Check for lines like "capability_value:" or "risk_level:" not followed by _declared/_reference
        for line in raw.split("\n"):
            stripped = line.strip()
            if stripped.startswith("capability_value:") and "baseline_" not in stripped and "_declared" not in stripped:
                # Only flag if the value is a string (not a boolean or reference field)
                val = stripped.split(":", 1)[1].strip()
                if val and val not in ("false", "true", "''", '""'):
                    finding("direct_capability_risk_declaration", yf.name,
                            "capability_value",
                            f"direct declaration found: '{stripped}' — use baseline_capability_value_reference instead")
            if stripped.startswith("risk_level:") and "baseline_" not in stripped and "_declared" not in stripped:
                val = stripped.split(":", 1)[1].strip()
                if val and val not in ("false", "true", "''", '""'):
                    finding("direct_capability_risk_declaration", yf.name,
                            "risk_level",
                            f"direct declaration found: '{stripped}' — use baseline_risk_level_reference instead")

    # ── Summary ──
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    total = len(checks)

    print(f"\n{'=' * 60}")
    print("Validation Summary")
    print(f"{'=' * 60}")
    print(f"  Total checks:  {total}")
    print(f"  Passed:        {passed}")
    print(f"  Failed:        {failed}")
    print(f"  Findings:      {len(findings)}")

    if findings:
        print(f"\n--- Findings ({len(findings)}) ---")
        cat_order = ["missing_file", "security_field", "mapping_field_missing",
                     "real_data_pattern", "non_sim_evidence_trace", "prohibited_declaration"]
        for cat in cat_order:
            items = [f for f in findings if f["category"] == cat]
            if items:
                for fi in items:
                    print(f"  [{fi['category']}] {fi['item']} / {fi['field']}: {fi['detail']}")

    print(f"\n{'=' * 60}")
    if failed == 0 and len(findings) == 0:
        print(f"ALL {total} CHECKS PASSED — No findings. ADV-CHAIN-001 design gate is consistent.")
        sys.exit(0)
    else:
        print(f"{failed} check(s) FAILED. {len(findings)} findings.")
        sys.exit(1 if failed > 0 else 0)

if __name__ == "__main__":
    main()
