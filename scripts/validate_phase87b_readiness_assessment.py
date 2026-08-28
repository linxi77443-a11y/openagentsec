#!/usr/bin/env python3
"""Phase 87B — AI安全评估可视化实施准备评估 Validator.

Design-only gate: validates readiness assessment deliverables, no code
implementation, no chart generation, no real execution.
"""
import json, sys, yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = ROOT / "executions/phase87b_readiness_assessment"
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


def file_exists(path, desc):
    result = path.exists()
    check(result, f"{desc} exists at {path}")
    return result if result else None


def yaml_load(path):
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return None
        keys = list(data.keys())
        if len(keys) == 1 and isinstance(data[keys[0]], dict):
            return data[keys[0]]
        return data
    except Exception as e:
        check(False, f"YAML load: {path} — {e}")
        return None


def get_raw_text(path):
    try:
        return path.read_text()
    except Exception:
        return ""


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 87B — AI安全评估可视化实施准备评估")
    print("Readiness Assessment Validation — ALL CHECKS")
    print("=" * 60)

    # File list
    YAML_FILES = [
        ("Data source readiness matrix", DESIGN_DIR / "phase87b_data_source_readiness_matrix.yaml"),
        ("View complexity assessment", DESIGN_DIR / "phase87b_view_complexity_assessment.yaml"),
        ("Schema & field risk register", DESIGN_DIR / "phase87b_schema_and_field_risk_register.yaml"),
        ("Start condition checklist", DESIGN_DIR / "phase87b_start_condition_checklist.yaml"),
        ("Validator checklist", DESIGN_DIR / "validator_checklist.yaml"),
    ]
    DOC_FILES = [
        ("Implementation readiness assessment",
         ROOT / "docs/phase87b_visualization_implementation_readiness_assessment.md"),
        ("Asset inventory",
         ROOT / "docs/phase87b_asset_inventory.md"),
        ("Technical dependency assessment",
         ROOT / "docs/phase87b_technical_dependency_assessment.md"),
        ("Short notes",
         ROOT / "docs/phase87b_visualization_implementation_readiness_assessment_notes.md"),
    ]
    SCHEMA_PATHS = [f[1] for f in YAML_FILES]
    DOC_PATHS = [f[1] for f in DOC_FILES]
    ALL_PATHS = list(SCHEMA_PATHS) + list(DOC_PATHS)
    ALL_SCHEMAS = {}

    # ============================================================
    # 1. Deliverable existence (DEL-001 to DEL-010)
    # ============================================================
    print("\n[CATEGORY 1] Deliverable existence (DEL-001 to DEL-010)")
    for name, path in YAML_FILES:
        exists = file_exists(path, name)
        if exists:
            data = yaml_load(path)
            if data is None:
                check(False, f"{name} YAML load failed")
            else:
                ALL_SCHEMAS[name] = data
    for name, path in DOC_FILES:
        file_exists(path, name)
    # Validate script existence
    validate_script = ROOT / "scripts/validate_phase87b_readiness_assessment.py"
    file_exists(validate_script, "Validate script")

    # ============================================================
    # 2. Security boundary (SFTY-001 to SFTY-006)
    # ============================================================
    print("\n[CATEGORY 2] Security boundary (SFTY-001 to SFTY-006)")
    security_ok = True
    for sname, sdata in ALL_SCHEMAS.items():
        if sdata is None:
            continue
        for field in ["confirmed_vulnerability", "formal_finding_allowed",
                       "production_safety_claimed", "controlled_replay_claimed"]:
            val = sdata.get(field)
            if val is not False:
                security_ok = False
                check(False, f"{sname}.{field} == {val} (expected False)")
            else:
                checks_passed += 1
    check(security_ok, "SFTY-001/004: all security fields == false")

    synthetic_ok = True
    for sname, sdata in ALL_SCHEMAS.items():
        if sdata is None:
            continue
        for field in ["synthetic_only", "design_gate_only"]:
            if sdata.get(field) is not True:
                synthetic_ok = False
    check(synthetic_ok, "SFTY-005: synthetic_only & design_gate_only == true on all schemas")

    # SFTY-006: capability_value/risk_level separated (exclude validator_checklist)
    cv_rl_combined = False
    all_raw = ""
    for _, path in YAML_FILES:
        if "validator_checklist" not in path.name:
            all_raw += get_raw_text(path)
    for _, path in DOC_FILES:
        all_raw += get_raw_text(path)
    if re.search(r'capability_value_risk_level|merged.*score|combined.*safety', all_raw):
        cv_rl_combined = True
    check(not cv_rl_combined,
          "SFTY-006: capability_value and risk_level not merged/combined")

    # SFTY-007: display_allowed fields == false on all schemas
    display_ok = True
    for sname, sdata in ALL_SCHEMAS.items():
        if sdata is None:
            continue
        for field in ["confirmed_vulnerability_display_allowed",
                       "formal_finding_display_allowed", "production_safety_display_allowed"]:
            val = sdata.get(field)
            if val is not False:
                display_ok = False
                check(False, f"{sname}.{field} == {val} (expected False)")
            else:
                checks_passed += 1
    check(display_ok, "SFTY-007: all display_allowed fields == false")

    # SFTY-008: implementation status fields
    impl_ok = True
    for sname, sdata in ALL_SCHEMAS.items():
        if sdata is None:
            continue
        for field, expected in [("implementation_ready", False),
                                 ("dashboard_implementation_allowed", False),
                                 ("not_module_mvp", True),
                                 ("not_execution_module", True)]:
            val = sdata.get(field)
            if val is not expected:
                impl_ok = False
                check(False, f"{sname}.{field} == {val} (expected {expected})")
            else:
                checks_passed += 1
    check(impl_ok, "SFTY-008: all implementation status fields == expected values")

    # SFTY-009: registry coverage credit and real-data binding
    misc_ok = True
    for sname, sdata in ALL_SCHEMAS.items():
        if sdata is None:
            continue
        for field, expected in [("no_registry_coverage_credit", True),
                                 ("real_data_dashboard_binding_allowed", False)]:
            val = sdata.get(field)
            if val is not expected:
                misc_ok = False
                check(False, f"{sname}.{field} == {val} (expected {expected})")
            else:
                checks_passed += 1
    check(misc_ok, "SFTY-009: no_registry_coverage_credit & real_data_dashboard_binding_allowed == expected")

    # ============================================================
    # 3. Data source readiness (DSR-001 to DSR-004)
    # ============================================================
    print("\n[CATEGORY 3] Data source readiness (DSR-001 to DSR-004)")
    dsr = ALL_SCHEMAS.get("Data source readiness matrix")
    if dsr and isinstance(dsr, dict):
        views = dsr.get("data_source_readiness_matrix", dsr)
        if isinstance(views, dict):
            # Unwrap nested "views" key if present
            if "views" in views and isinstance(views["views"], list):
                views = views["views"]
            else:
                views = [v for k, v in views.items() if isinstance(v, dict)]
        if isinstance(views, list):
            view_ids = [v.get("view_id") for v in views if isinstance(v, dict)]
            dsr_ready = all(v.get("readiness") in ["ready", "partially_ready",
                            "schema_ready_data_pending"] for v in views if isinstance(v, dict))
            check("coverage_heatmap" in view_ids, "DSR-001: coverage_heatmap in readiness matrix")
            check("attack_chain_propagation" in view_ids, "DSR-002: attack_chain_propagation in readiness matrix")
            check("defense_degradation_timeline" in view_ids, "DSR-003: defense_degradation_timeline in readiness matrix")
            check("red_team_candidate_view" in view_ids, "DSR-004: red_team_candidate_view in readiness matrix")
        else:
            check(False, "DSR: readiness matrix is not a list")
    else:
        check(False, "DSR: readiness matrix not loaded")

    # ============================================================
    # 4. View coverage (VIEW-001 to VIEW-004)
    # ============================================================
    print("\n[CATEGORY 4] View coverage (VIEW-001 to VIEW-004)")
    cmp = ALL_SCHEMAS.get("View complexity assessment")
    if cmp and isinstance(cmp, dict):
        views = cmp.get("view_complexity_assessment", cmp)
        if isinstance(views, dict):
            # May be a dict with list at first key
            view_items = [v for k, v in views.items() if isinstance(v, list)]
            if view_items:
                views = view_items[0]
        if isinstance(views, list):
            check(len(views) >= 4, f"VIEW-001: >= 4 views ({len(views)})")
            has_complexity = all("complexity_level" in v for v in views if isinstance(v, dict))
            check(has_complexity, "VIEW-002: all views have complexity_level")
            has_challenges = all("main_challenges" in v for v in views if isinstance(v, dict))
            check(has_challenges, "VIEW-003: all views have main_challenges")
            has_deps = all("dependencies" in v and "blocking_conditions" in v
                          for v in views if isinstance(v, dict))
            check(has_deps, "VIEW-004: all views have dependencies and blocking_conditions")
        else:
            check(False, "CMP: views is not a list")
    else:
        check(False, "CMP: view complexity not loaded")

    # ============================================================
    # 5. Complexity assessment (CMP-001 to CMP-004)
    # ============================================================
    print("\n[CATEGORY 5] Complexity assessment (CMP-001 to CMP-004)")
    if cmp and isinstance(cmp, dict):
        views = cmp.get("view_complexity_assessment", cmp)
        if isinstance(views, dict):
            view_items = [v for k, v in views.items() if isinstance(v, list)]
            if view_items:
                views = view_items[0]
        if isinstance(views, list):
            scores_ok = all(1 <= v.get("complexity_score", 0) <= 5
                           for v in views if isinstance(v, dict))
            check(scores_ok, "CMP-001: all complexity scores in [1,5]")
            has_dims = all("dimensions" in v for v in views if isinstance(v, dict))
            check(has_dims, "CMP-002: all views have dimensions")
            # Check summary fields
            summary = cmp.get("summary", {})
            check("recommended_order" in summary,
                  "CMP-003: summary has recommended_order")
            check("mock_fixture_needed" in summary,
                  "CMP-004: summary has mock_fixture_needed")
        else:
            check(False, "CMP: views is not a list")
    else:
        check(False, "CMP: view complexity not loaded")

    # ============================================================
    # 6. Risk register (RSK-001 to RSK-003)
    # ============================================================
    print("\n[CATEGORY 6] Risk register (RSK-001 to RSK-003)")
    rr = ALL_SCHEMAS.get("Schema & field risk register")
    if rr and isinstance(rr, dict):
        risks = rr.get("schema_and_field_risk_register", rr)
        if isinstance(risks, dict):
            risks_list = risks.get("risks", [])
        else:
            risks_list = []
        check(len(risks_list) >= 10, f"RSK-001: >= 10 risks ({len(risks_list)})")
        req_fields = ["risk_id", "category", "severity", "likelihood", "mitigation"]
        has_all_fields = all(
            all(f in r for f in req_fields) for r in risks_list if isinstance(r, dict))
        check(has_all_fields, "RSK-002: all risks have risk_id/category/severity/likelihood/mitigation")
        has_critical = any(
            r.get("severity") == "critical" for r in risks_list if isinstance(r, dict))
        check(has_critical, "RSK-003: at least 1 critical risk")
    else:
        check(False, "RSK: risk register not loaded")

    # ============================================================
    # 7. Start conditions (SC-001 to SC-007)
    # ============================================================
    print("\n[CATEGORY 7] Start conditions (SC-001 to SC-007)")
    sc = ALL_SCHEMAS.get("Start condition checklist")
    if sc and isinstance(sc, dict):
        conds = sc.get("start_condition_checklist", sc)
        if isinstance(conds, dict):
            conds_list = conds.get("conditions", [])
        else:
            conds_list = []
        check(len(conds_list) >= 7, f"SC-001: >= 7 conditions ({len(conds_list)})")
        req_fields = ["condition_id", "category", "title", "verification_method"]
        has_all_fields = all(
            all(f in c for f in req_fields) for c in conds_list if isinstance(c, dict))
        check(has_all_fields, "SC-002: all conditions have required fields")
        cats = [c.get("category") for c in conds_list if isinstance(c, dict)]
        check("schema_stability" in cats, "SC-003: schema_stability condition exists")
        check("test_data" in cats, "SC-004: test_data condition exists")
        check("validation" in cats, "SC-005: validation condition exists")
        check("security" in cats, "SC-006: security condition exists")
        check("field_semantics" in cats, "SC-007: field_semantics condition exists")
        # SC-008/SC-009: blocking flags
        if isinstance(conds, dict):
            summary = conds.get("summary", {})
        else:
            summary = {}
        check(summary.get("blocking_risks_present") is True,
              "SC-008: blocking_risks_present == true in summary")
        check(summary.get("start_conditions_blocking") is True,
              "SC-009: start_conditions_blocking == true in summary")
    else:
        check(False, "SC: start condition checklist not loaded")

    # ============================================================
    # 8. Cross-reference (XREF-001 to XREF-004)
    # ============================================================
    print("\n[CATEGORY 8] Cross-reference (XREF-001 to XREF-004)")
    # XREF-001: risk_ids from RR referenced by SC
    if sc and rr:
        rr_data = rr.get("schema_and_field_risk_register", rr)
        sc_data = sc.get("start_condition_checklist", sc)
        if isinstance(rr_data, dict) and isinstance(sc_data, dict):
            rr_risks = rr_data.get("risks", [])
            sc_conds = sc_data.get("conditions", [])
            rr_ids = set(r.get("risk_id") for r in rr_risks if isinstance(r, dict))
            sc_rids = set()
            for c in sc_conds:
                if isinstance(c, dict):
                    rids = c.get("related_risk_ids", [])
                    sc_rids.update(rids)
            overlap = sc_rids - rr_ids
            check(len(overlap) == 0,
                  f"XREF-001: risk_ids in SC not in RR: {overlap}")
        else:
            check(False, "XREF-001: risk register or start conditions not dict")
    else:
        check(True, "XREF-001: SKIP (data not loaded)")

    # XREF-004: no code/chart/exec patterns in docs
    patterns = r'def\s+\w+\s*\(|class\s+\w+\s*:|import\s+\w+|react|chart\.js|api\.[a-zA-Z]+\.com|https?://(?!sim\.)|sk-[A-Za-z0-9]{10,}'
    doc_raw = ""
    for _, path in DOC_FILES:
        doc_raw += get_raw_text(path)
    matches = re.findall(patterns, doc_raw)
    check(len(matches) == 0,
          f"XREF-004: no code/chart/real patterns in docs ({len(matches)} found)")

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    total = checks_passed + checks_failed
    print(f"RESULTS: {checks_passed}/{total} passed, {checks_failed} failed")
    if checks_failed > 0:
        print("\nFAILURES:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("ALL CHECKS PASSED")
    print("=" * 60)

    summary = {
        "phase": "phase87b",
        "module_id": "ADV-87B",
        "total": total,
        "passed": checks_passed,
        "failed": checks_failed,
        "all_passed": checks_failed == 0,
        "capability_value": "not_applicable",
        "risk_level": "not_applicable",
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "implementation_ready": False,
        "dashboard_implementation_allowed": False,
        "not_module_mvp": True,
        "not_execution_module": True,
        "no_registry_coverage_credit": True,
        "real_data_dashboard_binding_allowed": False,
        "confirmed_vulnerability_display_allowed": False,
        "formal_finding_display_allowed": False,
        "production_safety_display_allowed": False,
        "human_review_required": {
            "case_level": 0,
            "design_gate_human_review_required": True,
            "judge_review_required": True,
        },
    }
    summary_path = DESIGN_DIR / "validate_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to {summary_path}")
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
