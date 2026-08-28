#!/usr/bin/env python3
"""Phase 86A — Authorized Attack Chain Simulation Design Gate Validator.

Design-only gate: checks schema definitions, no code implementation,
no real execution, no real payloads. All checks on YAML schema files.
"""
import json, sys, yaml, re
from pathlib import Path

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
        # Schema files have nested structure: root_key: {content}
        # Unwrap: if a single key maps to a dict, return the inner dict
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
        actual = obj.get(field) if isinstance(obj, dict) else getattr(obj, field, None)
        check(actual == expected,
              f"{prefix}: {obj_desc} {field} == {actual} (expected {expected})")


def get_raw_text(path):
    """Return raw text of a file, for pattern matching."""
    try:
        return path.read_text()
    except Exception:
        return ""


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 86A — Authorized Attack Chain Simulation Design Gate")
    print("Design Gate Validation — ALL CHECKS")
    print("=" * 60)

    DESIGN_DIR = ROOT / "executions/phase86a_attack_chain_design"
    SCHEMA_FILES = [
        ("Attack chain flow spec", DESIGN_DIR / "phase86a_attack_chain_flow_spec.yaml"),
        ("Strategy selection model", DESIGN_DIR / "phase86a_strategy_selection_model.yaml"),
        ("Dynamic defense evaluation schema", DESIGN_DIR / "phase86a_dynamic_defense_evaluation_schema.yaml"),
        ("Result schema", DESIGN_DIR / "phase86a_result_schema.yaml"),
        ("Capability scorecard schema", DESIGN_DIR / "capability_scorecard_schema.yaml"),
    ]
    SCHEMAS = {}

    # ================================================================
    # 1. All schema files exist and load
    # ================================================================
    print("\n1. Schema file existence")
    for name, path in SCHEMA_FILES:
        exists = file_exists(path, name)
        if exists:
            SCHEMAS[name] = yaml_load(path)
            if SCHEMAS[name] is None:
                check(False, f"{name} YAML load failed")

    check(len(SCHEMAS) >= 5, f"All 5 schema files loaded ({len(SCHEMAS)}/5)")

    # ================================================================
    # 2. Design gate flags correct on all schemas
    # ================================================================
    print("\n2. Design gate flags")
    for sname, sdata in SCHEMAS.items():
        if sdata is None:
            continue
        check(sdata.get("design_gate_only") is True,
              f"{sname}: design_gate_only == true")
        check(sdata.get("synthetic_only") is True,
              f"{sname}: synthetic_only == true")
        check_security_fields(sdata, sname, "top-level")

    # ================================================================
    # 3. No code implementation, no real execution, no real payload
    # ================================================================
    print("\n3. Code/execution/payload restrictions")

    all_design_text = ""
    for sname, sdata in SCHEMAS.items():
        if sdata:
            all_design_text += yaml.dump(sdata)

    # Also check raw files for any embedded code patterns
    for _, path in SCHEMA_FILES:
        all_design_text += get_raw_text(path)

    prohibited_patterns = [
        (r'def\s+\w+\s*\(', "function definition (code implementation)"),
        (r'class\s+\w+\s*:', "class definition (code implementation)"),
        (r'import\s+\w+', "import statement (code implementation)"),
        (r'exec\s*\(', "exec() call (code execution)"),
        (r'subprocess\.', "subprocess call (real execution)"),
        (r'os\.system', "os.system call (real execution)"),
        (r'requests\.', "requests call (real API call)"),
        (r'socket\.', "socket call (real connection)"),
    ]
    for pat, desc in prohibited_patterns:
        matches = re.findall(pat, all_design_text, re.IGNORECASE)
        check(len(matches) == 0, f"No {desc} in schema files (found {len(matches)})")

    # Check for real URLs — skip SIM_ prefixed
    real_urls = re.findall(r'https?://(?!sim\.)', all_design_text, re.IGNORECASE)
    check(len(real_urls) == 0, f"No real URLs found (found {len(real_urls)})")

    # Check scorecard design coverage
    scorecard = SCHEMAS.get("Capability scorecard schema", {})
    if scorecard:
        dc = scorecard.get("design_coverage", {})
        check(dc.get("no_code_implementation_confirmed") is True,
              "scorecard: no_code_implementation_confirmed == true")
        check(dc.get("no_real_execution_confirmed") is True,
              "scorecard: no_real_execution_confirmed == true")
        check(dc.get("no_real_payload_confirmed") is True,
              "scorecard: no_real_payload_confirmed == true")
        check(dc.get("synthetic_only_confirmed") is True,
              "scorecard: synthetic_only_confirmed == true")

    flow_spec = SCHEMAS.get("Attack chain flow spec", {})
    if flow_spec:
        eb = flow_spec.get("execution_boundary", {})
        if eb:
            check(eb.get("design_gate_only") is True,
                  "flow_spec: execution_boundary.design_gate_only == true")
            check(eb.get("real_system_connection_allowed") is False,
                  "flow_spec: real_system_connection_allowed == false")
            check(eb.get("real_api_call_allowed") is False,
                  "flow_spec: real_api_call_allowed == false")
            check(eb.get("real_tool_execution_allowed") is False,
                  "flow_spec: real_tool_execution_allowed == false")
            check(eb.get("real_data_access_allowed") is False,
                  "flow_spec: real_data_access_allowed == false")
            check(eb.get("synthetic_only") is True,
                  "flow_spec: execution_boundary.synthetic_only == true")
            check(eb.get("simulated_execution_only") is True,
                  "flow_spec: execution_boundary.simulated_execution_only == true")
            check(eb.get("no_code_generation") is True,
                  "flow_spec: execution_boundary.no_code_generation == true")
            check(eb.get("no_real_payload_generation") is True,
                  "flow_spec: no_real_payload_generation == true")
            check(eb.get("no_real_attack_chain_execution") is True,
                  "flow_spec: no_real_attack_chain_execution == true")

    # ================================================================
    # 4. Design signals present in result schema
    # ================================================================
    print("\n4. Design signals")
    result_schema = SCHEMAS.get("Result schema", {})
    if result_schema:
        ds = result_schema.get("design_signals", {})
        expected_signals = [
            "attack_chain_generation_flow_defined",
            "strategy_selection_logic_defined",
            "dynamic_state_evaluation_defined",
            "defense_degradation_assessment_defined",
            "simulated_execution_boundary_defined",
            "evidence_trace_schema_defined",
            "red_blue_purple_output_mapping_defined",
            "human_review_required",
            "inconclusive_count",
        ]
        for signal in expected_signals:
            check(signal in ds, f"result_schema design_signals has '{signal}'")
        check(len(ds) >= 9, f"result_schema has >= 9 design signals ({len(ds)})")

        dmc = result_schema.get("design_module_count", {})
        check(dmc.get("total_modules", 0) >= 7,
              f"result_schema total_modules >= 7 ({dmc.get('total_modules')})")

        dgs = result_schema.get("design_gate_status", {})
        check(dgs.get("design_complete") is True,
              "result_schema: design_gate_status.design_complete == true")
        check(dgs.get("no_code_implementation") is True,
              "result_schema: design_gate_status.no_code_implementation == true")
        check(dgs.get("no_real_execution") is True,
              "result_schema: design_gate_status.no_real_execution == true")
        check(dgs.get("no_real_payload") is True,
              "result_schema: design_gate_status.no_real_payload == true")
        check(dgs.get("synthetic_only") is True,
              "result_schema: design_gate_status.synthetic_only == true")

    # ================================================================
    # 5. Breakthrough semantics
    # ================================================================
    print("\n5. Breakthrough semantics")
    if result_schema:
        dgs = result_schema.get("design_gate_status", {})
        check("simulated capability signal only" in dgs.get("breakthrough_detected_semantics", ""),
              "result_schema: breakthrough_detected_semantics contains 'simulated capability signal only'")
        check("simulated attack path" in dgs.get("exploit_chain_candidate_semantics", ""),
              "result_schema: exploit_chain_candidate_semantics references simulated attack path")

    # Check human_review_required structure
    if result_schema:
        ds = result_schema.get("design_signals", {})
        hrr = ds.get("human_review_required", {})
        if isinstance(hrr, dict):
            check(hrr.get("case_level") == 0,
                  "result_schema: human_review_required.case_level == 0")
            check(hrr.get("design_gate_human_review_required") is True,
                  "result_schema: human_review_required.design_gate_human_review_required == true")
            check(hrr.get("judge_review_required") is True,
                  "result_schema: human_review_required.judge_review_required == true")

    defense_schema = SCHEMAS.get("Dynamic defense evaluation schema", {})
    if defense_schema:
        cle = defense_schema.get("chain_level_evaluation", {})
        if cle:
            rules = cle.get("evaluation_rules", [])
            for rule in rules:
                if rule.get("name") == "breakthrough_detected":
                    check("simulated capability signal" in rule.get("semantics", ""),
                          "defense_schema: breakthrough_detected rule semantics references simulated capability signal")
                if rule.get("name") == "confirmed_vulnerability":
                    check(rule.get("rule") == "false",
                          "defense_schema: confirmed_vulnerability rule == false")

    if scorecard:
        sm = scorecard.get("scorecard_metadata_schema", {})
        check(len(sm.get("breakthrough_ids", [])) == 0,
              f"scorecard: breakthrough_ids empty ({len(sm.get('breakthrough_ids', []))})")

    # ================================================================
    # 6. Capability value / risk level separation
    # ================================================================
    print("\n6. Capability value & risk level separation")
    if scorecard:
        cv = scorecard.get("capability_value_schema", {})
        rl = scorecard.get("risk_level_schema", {})
        check(cv.get("value") == "not_applicable",
              f"scorecard: capability_value == not_applicable (got {cv.get('value')})")
        check("design gate" in cv.get("semantics", ""),
              "scorecard: capability_value semantics references 'design gate'")
        check(rl.get("value") == "not_applicable",
              f"scorecard: risk_level == not_applicable (got {rl.get('value')})")
        check("design gate" in rl.get("semantics", ""),
              "scorecard: risk_level semantics references 'design gate'")
        check(cv.get("value") != rl.get("value") or cv.get("value") == "not_applicable",
              "capability_value and risk_level are semantically separate (both not_applicable for design gate)")

    # ================================================================
    # 7. <SIM_...> placeholder usage
    # ================================================================
    print("\n7. SIM_ placeholder usage")
    all_text = ""
    for sname, sdata in SCHEMAS.items():
        if sdata:
            all_text += yaml.dump(sdata)

    sim_placeholders = re.findall(r'<SIM_\w+>', all_text)
    check(len(sim_placeholders) >= 20,
          f"Schema files contain >= 20 <SIM_...> placeholders ({len(sim_placeholders)})")

    # ================================================================
    # 8. Output schemas (Red/Blue/Purple)
    # ================================================================
    print("\n8. Red/Blue/Purple output mapping schemas")
    if result_schema:
        outputs = result_schema.get("output_schemas", {})
        check("red_team" in outputs, "result_schema has red_team output schema")
        check("blue_team" in outputs, "result_schema has blue_team output schema")
        check("purple_team" in outputs, "result_schema has purple_team output schema")

        red = outputs.get("red_team", {})
        check("breakthrough_detected" in red, "red_team has breakthrough_detected field")
        check("evidence_trace" in red, "red_team has evidence_trace field")
        check("affected_boundary" in red, "red_team has affected_boundary field")

        blue = outputs.get("blue_team", {})
        check("control_candidate" in blue, "blue_team has control_candidate field")
        check("mitigation_candidate" in blue, "blue_team has mitigation_candidate field")
        check("defense_coverage_gap" in blue, "blue_team has defense_coverage_gap field")

        purple = outputs.get("purple_team", {})
        check("retest_candidate" in purple, "purple_team has retest_candidate field")
        check("retest_case_template" in purple, "purple_team has retest_case_template field")
        check("regression_suite_suggestion" in purple, "purple_team has regression_suite_suggestion field")

    # ================================================================
    # 9. Security boundary fields
    # ================================================================
    print("\n9. Security boundary")
    if result_schema:
        sb = result_schema.get("security_boundary", {})
        check(sb.get("confirmed_vulnerability") is False,
              "security_boundary: confirmed_vulnerability == false")
        check(sb.get("formal_finding_allowed") is False,
              "security_boundary: formal_finding_allowed == false")
        check(sb.get("production_safety_claimed") is False,
              "security_boundary: production_safety_claimed == false")
        check(sb.get("controlled_replay_claimed") is False,
              "security_boundary: controlled_replay_claimed == false")
        check(sb.get("attack_chain_generation_executable") is False,
              "security_boundary: attack_chain_generation_executable == false")
        check(sb.get("automated_attack_execution_allowed") is False,
              "security_boundary: automated_attack_execution_allowed == false")
        check(sb.get("payload_generation_allowed") is False,
              "security_boundary: payload_generation_allowed == false")
        check(sb.get("controlled_replay_execution_allowed") is False,
              "security_boundary: controlled_replay_execution_allowed == false")
        check(sb.get("replay_executable") is False,
              "security_boundary: replay_executable == false")
        check(sb.get("real_system_connection_allowed") is False,
              "security_boundary: real_system_connection_allowed == false")
        check(sb.get("real_api_call_allowed") is False,
              "security_boundary: real_api_call_allowed == false")
        check(sb.get("real_tool_execution_allowed") is False,
              "security_boundary: real_tool_execution_allowed == false")
        check(sb.get("real_data_access_allowed") is False,
              "security_boundary: real_data_access_allowed == false")
        check(sb.get("breakthrough_detected_is_real_vulnerability") is False,
              "security_boundary: breakthrough_detected_is_real_vulnerability == false")

    # ================================================================
    # 10. Design coverage checklist
    # ================================================================
    print("\n10. Design coverage checklist")
    if scorecard:
        dc = scorecard.get("design_coverage", {})
        design_signals = [
            "attack_chain_generation_flow_defined",
            "strategy_selection_logic_defined",
            "dynamic_state_evaluation_defined",
            "defense_degradation_assessment_defined",
            "simulated_execution_boundary_defined",
            "evidence_trace_schema_defined",
            "red_blue_purple_output_mapping_defined",
        ]
        for s in design_signals:
            check(dc.get(s) is True, f"design_coverage: {s} == true")

        # Check human_review_required in scorecard
        hrr_sc = scorecard.get("human_review_required", {})
        check(hrr_sc.get("case_level") == 0,
              "scorecard: human_review_required.case_level == 0")
        check(hrr_sc.get("design_gate_human_review_required") is True,
              "scorecard: human_review_required.design_gate_human_review_required == true")
        check(hrr_sc.get("judge_review_required") is True,
              "scorecard: human_review_required.judge_review_required == true")

        # Check execution boundary fields
        ebf = scorecard.get("execution_boundary_fields", {})
        check(ebf.get("attack_chain_generation_executable") is False,
              "scorecard: execution_boundary.attack_chain_generation_executable == false")
        check(ebf.get("automated_attack_execution_allowed") is False,
              "scorecard: execution_boundary.automated_attack_execution_allowed == false")
        check(ebf.get("payload_generation_allowed") is False,
              "scorecard: execution_boundary.payload_generation_allowed == false")
        check(ebf.get("controlled_replay_execution_allowed") is False,
              "scorecard: execution_boundary.controlled_replay_execution_allowed == false")
        check(ebf.get("replay_executable") is False,
              "scorecard: execution_boundary.replay_executable == false")

    # ================================================================
    # 11. Scorecard results summary counts
    # ================================================================
    print("\n11. Scorecard results summary")
    if scorecard:
        rs = scorecard.get("results_summary_schema", {})
        check(rs.get("design_modules", 0) >= 7,
              f"results_summary: design_modules >= 7 ({rs.get('design_modules')})")
        check(rs.get("total", 0) == 0,
              "results_summary: total == 0 (no real execution)")
        check(rs.get("control_cases", 0) == 0,
              "results_summary: control_cases == 0 (design gate only)")
        check(rs.get("breakthrough_detected", 0) == 0,
              "results_summary: breakthrough_detected == 0")

        design_signal_keys = [
            "attack_chain_generation_flow_defined",
            "strategy_selection_logic_defined",
            "dynamic_state_evaluation_defined",
            "defense_degradation_assessment_defined",
            "simulated_execution_boundary_defined",
            "evidence_trace_schema_defined",
            "red_blue_purple_output_mapping_defined",
        ]
        for key in design_signal_keys:
            check(rs.get(key, 0) >= 1,
                  f"results_summary: {key} >= 1 ({rs.get(key)})")

    # ================================================================
    # 12. Strategy selection model structure
    # ================================================================
    print("\n12. Strategy selection model")
    strategy = SCHEMAS.get("Strategy selection model", {})
    if strategy:
        patterns = strategy.get("pattern_library", [])
        check(len(patterns) >= 8,
              f"strategy: >= 8 patterns ({len(patterns)})")
        pattern_ids = [p.get("pattern_id") for p in patterns]
        for pid in ["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P10"]:
            check(pid in pattern_ids, f"strategy: pattern {pid} present")

        sl = strategy.get("selection_logic", {})
        steps = sl.get("steps", [])
        step_names = [s.get("name") for s in steps]
        for sn in ["attacker_type_filter", "objective_filter", "layer_filter", "priority_sort",
                    "dependency_resolution", "chain_strategy_dispatch"]:
            check(sn in step_names, f"strategy: selection step '{sn}' present")

        variants = strategy.get("strategy_variants", [])
        var_names = [v.get("variant") for v in variants]
        for vn in ["single_chain", "composite_chain", "parallel_chain"]:
            check(vn in var_names, f"strategy: variant '{vn}' present")

    # ================================================================
    # 13. Defense evaluation schema structure
    # ================================================================
    print("\n13. Defense evaluation schema")
    if defense_schema:
        states = defense_schema.get("node_defense_states", [])
        state_names = [s.get("state") for s in states]
        for sn in ["intact", "degraded", "breached", "blocked", "review_triggered"]:
            check(sn in state_names, f"defense: state '{sn}' present")

        signals = defense_schema.get("breakthrough_signals", [])
        signal_names = [s.get("signal") for s in signals]
        expected_signals = [
            "command_execution_blocked", "operational_attack_command_blocked",
            "safe_alternative_provided", "secret_exposure_blocked",
            "redaction_applied", "credential_reuse_blocked",
            "defensive_guidance_provided", "repo_context_injection_detected",
            "instruction_boundary_preserved", "human_review_required",
        ]
        for es in expected_signals:
            check(es in signal_names, f"defense: breakthrough signal '{es}' present")

        cle = defense_schema.get("chain_level_evaluation", {})
        check("chain_breach_detected" in cle.get("structure", {}),
              "defense: chain_level_evaluation has chain_breach_detected")
        check("breakthrough_detected" in cle.get("structure", {}),
              "defense: chain_level_evaluation has breakthrough_detected")

    # ================================================================
    # 14. Design doc exists
    # ================================================================
    print("\n14. Design document")
    design_doc = ROOT / "docs/phase86a_ai_red_team_attack_chain_engine_design.md"
    file_exists(design_doc, "Design document")
    if design_doc.exists():
        doc_text = design_doc.read_text()
        check("Phase 86A" in doc_text, "Design doc mentions Phase 86A")
        check("design_gate_only" in doc_text.lower() or "design gate" in doc_text.lower(),
              "Design doc references design gate constraints")

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
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
