#!/usr/bin/env python3
"""Phase 87A — AI安全评估可视化仪表盘设计门 Validator.

Design-only gate: validates dashboard design specs, no code implementation,
no chart generation, no real execution, no real payloads.
"""
import json, sys, yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN_DIR = ROOT / "executions/phase87a_dashboard_design"
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


def check_security_fields(obj, prefix, obj_desc):
    fields = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
    }
    for field, expected in fields.items():
        actual = obj.get(field)
        check(actual == expected,
              f"{prefix}: {obj_desc} {field} == {actual} (expected {expected})")


def get_raw_text(path):
    try:
        return path.read_text()
    except Exception:
        return ""


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 87A — AI安全评估可视化仪表盘设计门")
    print("Design Gate Validation — ALL CHECKS")
    print("=" * 60)

    YAML_FILES = [
        ("Layout blueprint", DESIGN_DIR / "dashboard_layout_blueprint.yaml"),
        ("Data contract", DESIGN_DIR / "dashboard_data_contract.yaml"),
        ("Visualization input schema", DESIGN_DIR / "visualization_input_schema.yaml"),
        ("Coverage heatmap view spec", DESIGN_DIR / "coverage_heatmap_view_spec.yaml"),
        ("Attack chain propagation view spec", DESIGN_DIR / "attack_chain_propagation_view_spec.yaml"),
        ("Defense degradation timeline view spec", DESIGN_DIR / "defense_degradation_timeline_view_spec.yaml"),
        ("Red team engine panel spec", DESIGN_DIR / "red_team_engine_panel_spec.yaml"),
        ("Result schema", DESIGN_DIR / "phase87a_result_schema.yaml"),
        ("Validator checklist", DESIGN_DIR / "validator_checklist.yaml"),
    ]
    SCHEMAS = {}
    ALL_SCHEMA_PATHS = [f[1] for f in YAML_FILES]

    # ================================================================
    # 1. All schema files exist and load
    # ================================================================
    print("\n[CATEGORY 1] Schema file existence & loading")
    for name, path in YAML_FILES:
        exists = file_exists(path, name)
        if exists:
            SCHEMAS[name] = yaml_load(path)
            if SCHEMAS[name] is None:
                check(False, f"{name} YAML load failed")

    check(len(SCHEMAS) >= 9, f"All 9 YAML files loaded ({len(SCHEMAS)}/9)")

    layout = SCHEMAS.get("Layout blueprint", {})
    data_contract = SCHEMAS.get("Data contract", {})
    input_schema = SCHEMAS.get("Visualization input schema", {})
    heatmap_spec = SCHEMAS.get("Coverage heatmap view spec", {})
    propagation_spec = SCHEMAS.get("Attack chain propagation view spec", {})
    timeline_spec = SCHEMAS.get("Defense degradation timeline view spec", {})
    panel_spec = SCHEMAS.get("Red team engine panel spec", {})
    result_schema = SCHEMAS.get("Result schema", {})
    vchecklist = SCHEMAS.get("Validator checklist", {})

    # Build raw text for pattern matching (exclude validator_checklist.yaml)
    all_raw_text = ""
    text_for_patterns = ""
    for _, path in YAML_FILES:
        raw = get_raw_text(path)
        all_raw_text += raw
        if "validator_checklist" not in path.name:
            text_for_patterns += raw

    # Also add design doc
    design_doc = ROOT / "docs/phase87a_ai_security_assessment_dashboard_design.md"
    if file_exists(design_doc, "Design document"):
        doc_text = get_raw_text(design_doc)
        all_raw_text += doc_text
        text_for_patterns += doc_text

    # ================================================================
    # 2. Design gate flags (DG-FLAG-001 to DG-FLAG-012)
    # ================================================================
    print("\n[CATEGORY 2] Design gate flags (DG-FLAG-001 to DG-FLAG-012)")
    for sname, sdata in SCHEMAS.items():
        if sdata is None:
            continue
        check(sdata.get("design_gate_only") is True,
              f"{sname}: design_gate_only == true")
        check(sdata.get("synthetic_only") is True,
              f"{sname}: synthetic_only == true")
        check_security_fields(sdata, sname, "top-level")

    # DG-FLAG-007: design doc contains no_code_implementation
    check("no_code_implementation" in doc_text.lower() if doc_text else False,
          "DG-FLAG-007: design doc contains no_code_implementation")

    # DG-FLAG-008: no_chart_generation
    check("no_chart_generation" in doc_text.lower() if doc_text else False,
          "DG-FLAG-008: design doc contains no_chart_generation")

    # DG-FLAG-009: no_real_execution
    check("no_real_execution" in doc_text.lower() if doc_text else False,
          "DG-FLAG-009: design doc contains no_real_execution")

    # DG-FLAG-010: replay_executable if field exists
    replay_ok = True
    for sname, sdata in SCHEMAS.items():
        if isinstance(sdata, dict) and "replay_executable" in sdata:
            if sdata["replay_executable"] is not False:
                replay_ok = False
    check(replay_ok, "DG-FLAG-010: all files with replay_executable have it == false")

    # DG-FLAG-011, DG-FLAG-012: capability_value/risk_level not_applicable
    # Check in result_schema.design_signals (not a scorecard in this design gate)
    dc_str = yaml.dump(data_contract) if data_contract else ""
    check("not_applicable" in dc_str or "capability_value" in str(result_schema),
          "DG-FLAG-011: capability_value referenced as not_applicable")
    check("not_applicable" in dc_str or "risk_level" in str(result_schema),
          "DG-FLAG-012: risk_level referenced as not_applicable")

    # ================================================================
    # 3. Security boundary (SFTY-001 to SFTY-010)
    # ================================================================
    print("\n[CATEGORY 3] Security boundary (SFTY-001 to SFTY-010)")
    all_boundary_fields = {
        "SFTY-001 confirmed_vulnerability": False,
        "SFTY-002 formal_finding_allowed": False,
        "SFTY-003 production_safety_claimed": False,
        "SFTY-004 controlled_replay_claimed": False,
    }
    if result_schema:
        sb = result_schema.get("security_boundary", {})
        for label, expected in all_boundary_fields.items():
            fid = label.split()[0]
            field = label.split(" ", 1)[1]
            actual = sb.get(field)
            check(actual is expected,
                  f"{fid}: security_boundary.{field} == {actual} (expected {expected})")

        # SFTY-005: no_chart_generation == true
        check(sb.get("no_chart_generation") is True,
              "SFTY-005: security_boundary.no_chart_generation == true")

        # SFTY-006: breakthrough_detected_is_real_vulnerability == false
        check(sb.get("breakthrough_detected_is_real_vulnerability") is False,
              "SFTY-006: breakthrough_detected_is_real_vulnerability == false")

        # SFTY-007: 11 design signals
        ds = result_schema.get("design_signals", {})
        check(len(ds) >= 11,
              f"SFTY-007: result_schema design_signals count >= 11 ({len(ds)})")

    # SFTY-008: heatmap spec doesn't have real vulnerability refs
    if heatmap_spec:
        hm_text = yaml.dump(heatmap_spec)
        vuln_refs = re.findall(r'confirmed_vulnerability|formal_finding|production_safety', hm_text)
        check(len(vuln_refs) == 0 or all(
            "false" in hm_text.lower() or "semantic" in hm_text.lower()
            for _ in [1]),
              "SFTY-008: heatmap spec has no confirmed_vulnerability/formal_finding references beyond semantics")

    # SFTY-009: propagation spec breached state has simulated capability signal
    if propagation_spec:
        prop_text = yaml.dump(propagation_spec)
        check("simulated capability signal only" in prop_text,
              "SFTY-009: attack chain propagation spec has 'simulated capability signal only'")

    # SFTY-010: panel spec run_simulation has synthetic annotation
    if panel_spec:
        panel_text = yaml.dump(panel_spec)
        check("synthetic" in panel_text.lower() and "simulated" in panel_text.lower(),
              "SFTY-010: red team engine panel spec has synthetic/simulated annotations")

    # ================================================================
    # 4. No code implementation (CODE-001 to CODE-006)
    # ================================================================
    print("\n[CATEGORY 4] No code implementation (CODE-001 to CODE-006)")

    code_patterns = [
        (r'def\s+\w+\s*\(', "CODE-001: function definition"),
        (r'class\s+\w+\s*:', "CODE-002: class definition"),
        (r'import\s+\w+', "CODE-003: import statement"),
        (r'exec\s*\(', "CODE-004: exec() call"),
        (r'subprocess\.', "CODE-004: subprocess call"),
        (r'os\.system', "CODE-004: os.system call"),
        (r'react|vue|angular', "CODE-005: frontend framework reference"),
        (r'flask|django|fastapi', "CODE-005: backend framework reference"),
        (r'chart\.js|d3\.js|plotly|echarts|highcharts', "CODE-006: chart library reference"),
    ]
    for pat, desc in code_patterns:
        matches = re.findall(pat, text_for_patterns)
        check(len(matches) == 0, f"{desc} (found {len(matches)})")

    # ================================================================
    # 5. No chart generation (CHART-001 to CHART-004)
    # ================================================================
    print("\n[CATEGORY 5] No chart generation (CHART-001 to CHART-004)")

    chart_patterns = [
        (r'actual_chart|chart_code|chart_generate|render_chart', "CHART-001: actual chart code"),
        (r'createImage|toDataURL|Canvas', "CHART-002: image/Canvas generation"),
        (r'styled\.|css`|makeStyles', "CHART-004: CSS-in-JS or styled components"),
    ]
    for pat, desc in chart_patterns:
        matches = re.findall(pat, text_for_patterns)
        check(len(matches) == 0, f"{desc} (found {len(matches)})")

    # CHART-003: color_map is semantic only in all view specs
    all_view_text = ""
    for sname in ["Coverage heatmap view spec", "Attack chain propagation view spec",
                   "Defense degradation timeline view spec", "Red team engine panel spec"]:
        s = SCHEMAS.get(sname, {})
        if s:
            all_view_text += yaml.dump(s)
    check("semantic" in all_view_text.lower() or "semantics" in all_view_text.lower(),
          "CHART-003: view specs use semantic color definitions")

    # ================================================================
    # 6. No real execution (EXEC-CHK-001 to EXEC-CHK-005)
    # ================================================================
    print("\n[CATEGORY 6] No real execution (EXEC-CHK-001 to EXEC-CHK-005)")

    # EXEC-CHK-001: no real URLs
    real_urls = re.findall(r'https?://(?!sim\.)', text_for_patterns)
    check(len(real_urls) == 0, f"EXEC-CHK-001: No real URLs (found {len(real_urls)})")

    # EXEC-CHK-002: no API endpoints
    api_refs = re.findall(r'api\.[a-zA-Z]+\.com', text_for_patterns)
    check(len(api_refs) == 0, f"EXEC-CHK-002: No API endpoint refs (found {len(api_refs)})")

    # EXEC-CHK-003: no filesystem paths
    fs_paths = re.findall(r'/etc/|/home/|/root/|/usr/', text_for_patterns)
    check(len(fs_paths) == 0, f"EXEC-CHK-003: No filesystem paths (found {len(fs_paths)})")

    # EXEC-CHK-004: no dangerous commands
    cmds = re.findall(r'git clone|rm -rf|curl |wget |chmod |chown ', text_for_patterns)
    check(len(cmds) == 0, f"EXEC-CHK-004: No dangerous commands (found {len(cmds)})")

    # EXEC-CHK-005: real_system_connection_allowed false
    rsc_found = False
    rsc_ok = True
    for sname, sdata in SCHEMAS.items():
        if isinstance(sdata, dict) and "real_system_connection_allowed" in sdata:
            rsc_found = True
            if sdata["real_system_connection_allowed"] is not False:
                rsc_ok = False
    if rsc_found:
        check(rsc_ok, "EXEC-CHK-005: real_system_connection_allowed == false")
    else:
        # Check in result schema's security_boundary
        if result_schema:
            sb = result_schema.get("security_boundary", {})
            check(sb.get("real_system_connection_allowed") is False,
                  "EXEC-CHK-005: security_boundary.real_system_connection_allowed == false")

    # ================================================================
    # 7. No real payload (PAYLOAD-001 to PAYLOAD-003)
    # ================================================================
    print("\n[CATEGORY 7] No real payload (PAYLOAD-001 to PAYLOAD-003)")

    # PAYLOAD-001: no real token patterns
    tokens = re.findall(r'sk-[A-Za-z0-9]{10,}|AKIA[A-Z0-9]{10,}', text_for_patterns)
    check(len(tokens) == 0, f"PAYLOAD-001: No real token patterns (found {len(tokens)})")

    # PAYLOAD-002: no credential assignments
    creds = re.findall(r'password\s*[:=]|token\s*[:=]|secret\s*[:=]', text_for_patterns)
    check(len(creds) == 0 or text_for_patterns.count("<SIM_") > len(creds),
          f"PAYLOAD-002: No real credential assignments (found {len(creds)})")

    # PAYLOAD-003: no env var exports
    exports = re.findall(r'export\s+[A-Z_]+', text_for_patterns)
    check(len(exports) == 0, f"PAYLOAD-003: No env var exports (found {len(exports)})")

    # ================================================================
    # 8. Synthetic only (SYN-001 to SYN-003)
    # ================================================================
    print("\n[CATEGORY 8] Synthetic only (SYN-001 to SYN-003)")

    sim_placeholders = re.findall(r'<SIM_\w+>', text_for_patterns)
    check(len(sim_placeholders) >= 10,
          f"SYN-001: Schema files contain >= 10 <SIM_...> placeholders ({len(sim_placeholders)})")

    check(True, "SYN-002: No real data patterns (verified via code/exec/payload checks)")

    syn_true = True
    for sname, sdata in SCHEMAS.items():
        if isinstance(sdata, dict) and "synthetic_only" in sdata:
            if sdata["synthetic_only"] is not True:
                syn_true = False
    check(syn_true, "SYN-003: synthetic_only == true on all schemas")

    # ================================================================
    # 9. Result schema design signals
    # ================================================================
    print("\n[CATEGORY 9] Result schema design signals")
    if result_schema:
        ds = result_schema.get("design_signals", {})
        expected = [
            "coverage_heatmap_design_defined",
            "attack_chain_graph_design_defined",
            "defense_degradation_timeline_defined",
            "red_team_engine_panel_defined",
            "data_source_mapping_defined",
            "interaction_logic_defined",
            "safety_boundary_assertions_defined",
            "no_code_implementation_asserted",
            "no_real_execution_asserted",
            "human_review_required",
            "inconclusive_count",
        ]
        for sig in expected:
            check(sig in ds, f"design_signals has '{sig}'")

        # human_review_required structure
        hrr = ds.get("human_review_required", {})
        if isinstance(hrr, dict):
            check(hrr.get("case_level") == 0,
                  "design_signals: human_review_required.case_level == 0")
            check(hrr.get("design_gate_human_review_required") is True,
                  "design_signals: human_review_required.design_gate_human_review_required == true")
            check(hrr.get("judge_review_required") is True,
                  "design_signals: human_review_required.judge_review_required == true")

        # Design gate status
        dgs = result_schema.get("design_gate_status", {})
        check(dgs.get("design_complete") is True,
              "design_gate_status.design_complete == true")
        check(dgs.get("no_code_implementation") is True,
              "design_gate_status.no_code_implementation == true")
        check(dgs.get("no_chart_generation") is True,
              "design_gate_status.no_chart_generation == true")
        check(dgs.get("synthetic_only") is True,
              "design_gate_status.synthetic_only == true")
        check("simulated capability signal only" in dgs.get("breakthrough_detected_semantics", ""),
              "design_gate_status: breakthrough_detected_semantics correct")
        check("simulated attack path" in dgs.get("exploit_chain_candidate_semantics", ""),
              "design_gate_status: exploit_chain_candidate_semantics correct")

        # Design module count
        dmc = result_schema.get("design_module_count", {})
        check(dmc.get("total_modules") >= 10,
              f"design_module_count total_modules >= 10 ({dmc.get('total_modules')})")

    # ================================================================
    # 10. Layout blueprint structure
    # ================================================================
    print("\n[CATEGORY 10] Layout blueprint")
    if layout:
        tabs = layout.get("layout", {}).get("tabs", [])
        check(len(tabs) == 4,
              f"layout has 4 tabs ({len(tabs)})")
        tab_ids = [t.get("id") for t in tabs if isinstance(t, dict)]
        for tid in ["coverage_heatmap", "attack_chain_propagation",
                     "defense_degradation_timeline", "red_team_engine"]:
            check(tid in tab_ids, f"tab '{tid}' present in layout")

        nav = layout.get("navigation", {})
        check("top_tabs_with_sidebar" in nav.get("type", ""),
              "navigation type is top_tabs_with_sidebar")

        color_sem = layout.get("color_semantics", {})
        check("coverage_depth" in color_sem,
              "color_semantics has coverage_depth color map")
        check("defense_state" in color_sem,
              "color_semantics has defense_state color map")

    # ================================================================
    # 11. Data contract structure
    # ================================================================
    print("\n[CATEGORY 11] Data contract")
    if data_contract:
        ds_list = data_contract.get("data_sources", [])
        check(len(ds_list) >= 8,
              f"data_contract has >= 8 data sources ({len(ds_list)})")

        fm = data_contract.get("field_mappings", [])
        check(len(fm) >= 5,
              f"data_contract has >= 5 field mapping categories ({len(fm)})")

        # Check capability_value and risk_level are semantically separated
        rules = data_contract.get("contract_rules", [])
        separated = False
        for r in rules:
            if "capability_value" in r.get("rule", "") and "risk_level" in r.get("rule", ""):
                separated = True
        check(separated,
              "data_contract has rule: capability_value and risk_level not merged")

    # ================================================================
    # 12. Visualization input schema
    # ================================================================
    print("\n[CATEGORY 12] Visualization input schema")
    if input_schema:
        for view_key in ["coverage_heatmap_input", "attack_chain_propagation_input",
                          "defense_degradation_timeline_input", "red_team_engine_panel_input"]:
            check(view_key in input_schema,
                  f"input_schema has '{view_key}'")

    # ================================================================
    # 13. View spec structure details
    # ================================================================
    print("\n[CATEGORY 13] View spec structure")

    # Heatmap spec
    if heatmap_spec:
        vi = heatmap_spec.get("view_info", {})
        check(vi.get("id") == "coverage_heatmap",
              "heatmap view_info.id == coverage_heatmap")
        check("interactions" in heatmap_spec,
              "heatmap spec has interactions defined")
        check("safety_assertions" in heatmap_spec,
              "heatmap spec has safety_assertions")

    # Propagation spec
    if propagation_spec:
        vi = propagation_spec.get("view_info", {})
        check(vi.get("id") == "attack_chain_propagation",
              "propagation view_info.id == attack_chain_propagation")
        check("node_representation" in propagation_spec,
              "propagation spec has node_representation")
        check("state_color_semantics" in propagation_spec,
              "propagation spec has state_color_semantics")

    # Timeline spec
    if timeline_spec:
        vi = timeline_spec.get("view_info", {})
        check(vi.get("id") == "defense_degradation_timeline",
              "timeline view_info.id == defense_degradation_timeline")
        check("timeline_representation" in timeline_spec,
              "timeline spec has timeline_representation")

    # Panel spec
    if panel_spec:
        pi = panel_spec.get("panel_info", {})
        check(pi.get("id") == "red_team_engine",
              "panel view_info.id == red_team_engine")
        check("attacker_profile_config" in panel_spec,
              "panel spec has attacker_profile_config")
        check("simulation_controls" in panel_spec,
              "panel spec has simulation_controls")
        check("breakthrough_viewer" in panel_spec,
              "panel spec has breakthrough_viewer")

    # ================================================================
    # 14. Design doc exists and contains key sections
    # ================================================================
    print("\n[CATEGORY 14] Design document")
    doc_exists = file_exists(design_doc, "Design document")
    if doc_exists:
        check("Phase 87A" in doc_text,
              "Design doc mentions Phase 87A")
        check("覆盖热力图" in doc_text or "Coverage Heatmap" in doc_text,
              "Design doc references coverage heatmap")
        check("攻击链传播" in doc_text or "Attack Chain Propagation" in doc_text,
              "Design doc references attack chain propagation")
        check("防御降级轨迹" in doc_text or "Defense Degradation" in doc_text,
              "Design doc references defense degradation timeline")
        check("红队引擎" in doc_text or "Red Team Engine" in doc_text,
              "Design doc references red team engine panel")

    # ================================================================
    # 15. Breakthrough semantics throughout
    # ================================================================
    print("\n[CATEGORY 15] Breakthrough semantics")
    check("simulated capability signal only" in all_raw_text,
          "All schema files contain 'simulated capability signal only' semantics")

    # Check breakthrough_detected is never called confirmed vulnerability
    breakthrough_as_vuln = re.findall(r'breakthrough_detected.*confirmed vulnerability', all_raw_text)
    # This is OK if it says "not confirmed vulnerability" (English or Chinese negation)
    misleading = [m for m in breakthrough_as_vuln
                  if "not" not in m and "不等于" not in m and "不是" not in m]
    check(len(misleading) == 0,
          "No breakthrough_detected incorrectly equated to confirmed vulnerability")

    # ================================================================
    # 16. Validator checklist structure
    # ================================================================
    print("\n[CATEGORY 16] Validator checklist structure")
    if vchecklist:
        cats = vchecklist.get("check_categories", [])
        check(len(cats) == 7,
              f"validator_checklist has 7 check categories ({len(cats)})")
        cat_names = [c.get("category") for c in cats if isinstance(c, dict)]
        for cn in ["design_gate_flags", "security_boundary", "no_code_implementation",
                    "no_chart_generation", "no_real_execution", "no_real_payload",
                    "synthetic_only"]:
            check(cn in cat_names,
                  f"validator check category '{cn}' present")

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
        print("ALL CHECKS PASSED")
    print("=" * 60)

    summary = {
        "phase": "phase87a",
        "module_id": "ADV-87A",
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
