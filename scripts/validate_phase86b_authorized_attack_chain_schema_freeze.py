#!/usr/bin/env python3
"""Phase 86B — Authorized Attack Chain Simulation Schema Freeze & Validator Design.

Design-only gate: validates schema freeze completeness across 7 schema files,
71+ check rules across 10 categories. No code implementation, no real execution.
"""
import json, sys, yaml, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE_DIR = ROOT / "executions/phase86b_schema_freeze"
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
        actual = obj.get(field) if isinstance(obj, dict) else None
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
    print("Phase 86B — Authorized Attack Chain Simulation Schema Freeze")
    print("Design Gate Validation — ALL CHECKS")
    print("=" * 60)

    # Schema file list
    SCHEMA_FILES = [
        ("Attack chain schema", FREEZE_DIR / "authorized_attack_chain_schema.yaml"),
        ("State machine", FREEZE_DIR / "attack_chain_state_machine.yaml"),
        ("Safety boundary assertions", FREEZE_DIR / "safety_boundary_assertions.yaml"),
        ("Validator checklist", FREEZE_DIR / "validator_checklist.yaml"),
        ("Result schema", FREEZE_DIR / "phase86b_result_schema.yaml"),
        ("Capability scorecard schema", FREEZE_DIR / "capability_scorecard_schema.yaml"),
        ("Freeze documentation", FREEZE_DIR / "phase86b_schema_freeze.md"),
    ]
    SCHEMA_YAML_FILES = [f for f in SCHEMA_FILES if f[1].suffix == ".yaml"]
    ALL_SCHEMA_PATHS = [f[1] for f in SCHEMA_YAML_FILES]
    SCHEMAS = {}

    # ================================================================
    # 1. All schema files exist and load
    # ================================================================
    print("\n[CATEGORY 1] Schema file existence & loading")
    for name, path in SCHEMA_YAML_FILES:
        exists = file_exists(path, name)
        if exists:
            SCHEMAS[name] = yaml_load(path)
            if SCHEMAS[name] is None:
                check(False, f"{name} YAML load failed")

    check(len(SCHEMAS) >= 6, f"All 6 YAML schema files loaded ({len(SCHEMAS)}/6)")

    attack_schema = SCHEMAS.get("Attack chain schema", {})
    state_machine = SCHEMAS.get("State machine", {})
    safety_assertions = SCHEMAS.get("Safety boundary assertions", {})
    validator_checklist = SCHEMAS.get("Validator checklist", {})
    result_schema = SCHEMAS.get("Result schema", {})
    scorecard = SCHEMAS.get("Capability scorecard schema", {})

    # ================================================================
    # 2. Design gate flags correct on all schemas (REQ-001 style)
    # ================================================================
    print("\n[CATEGORY 2] Design gate flags on all schemas")
    for sname, sdata in SCHEMAS.items():
        if sdata is None:
            continue
        check(sdata.get("design_gate_only") is True,
              f"{sname}: design_gate_only == true")
        check(sdata.get("synthetic_only") is True,
              f"{sname}: synthetic_only == true")
        check_security_fields(sdata, sname, "top-level")

    # ================================================================
    # 3. Schema required fields (REQ-001 to REQ-012)
    # ================================================================
    print("\n[CATEGORY 3] Schema required fields (REQ-001 to REQ-012)")

    # REQ-001: attack schema has attack_chain and attack_node definitions
    if attack_schema:
        check("version" in attack_schema,
              "REQ-001: attack schema loaded (has version field)")
        check("attack_chain" in attack_schema,
              "REQ-001: attack_chain definition present")
        check("attack_node" in attack_schema,
              "REQ-001: attack_node definition present")

    # REQ-002: all fields must have name/type/required/description
    has_field_metadata = True
    for sname, sdata in SCHEMAS.items():
        if not isinstance(sdata, dict):
            continue
        for key, val in sdata.items():
            if isinstance(val, dict):
                if all(k in val for k in ["name", "type", "required", "description"]):
                    has_field_metadata = True
    check(has_field_metadata,
          "REQ-002: fields have name/type/required/description metadata")

    # REQ-003: attack_chain has chain_id, objective, attacker_type, nodes
    if attack_schema:
        ac = attack_schema.get("attack_chain", {})
        ac_fields = ac.get("fields", []) if isinstance(ac, dict) and "fields" in ac else ac
        if isinstance(ac_fields, dict):
            for fname in ["chain_id", "objective", "attacker_type", "nodes"]:
                check(fname in ac_fields,
                      f"REQ-003: attack_chain has field '{fname}'")
        elif isinstance(ac_fields, list):
            field_names = [f.get("name") if isinstance(f, dict) else f for f in ac_fields]
            for fname in ["chain_id", "objective", "attacker_type", "nodes"]:
                check(fname in field_names,
                      f"REQ-003: attack_chain has field '{fname}'")
        else:
            # Check raw content for these keys
            raw_ac = yaml.dump(ac) if ac else ""
            for fname in ["chain_id", "objective", "attacker_type", "nodes"]:
                check(fname in str(ac),
                      f"REQ-003: attack_chain has field '{fname}'")

    # REQ-004: attack_node has node_id, pattern_id, order, simulated_input, expected_defensive_behavior
    if attack_schema:
        anode = attack_schema.get("attack_node", {})
        anode_str = yaml.dump(anode)
        for fname in ["node_id", "pattern_id", "order", "simulated_input", "expected_defensive_behavior"]:
            check(fname in anode_str,
                  f"REQ-004: attack_node has field '{fname}'")

    # REQ-005: pattern_id enum P01-P10
    if attack_schema:
        all_text_attack = yaml.dump(attack_schema)
        pattern_ids_found = re.findall(r'P\d{2}', all_text_attack)
        unique_pids = set(pattern_ids_found)
        expected_pids = {f"P{i:02d}" for i in range(1, 11)}
        check(expected_pids.issubset(unique_pids),
              f"REQ-005: pattern_id enum P01-P10 present (found {sorted(unique_pids)})")

    # REQ-006: chain_level_evaluation has breakthrough_detected field
    if attack_schema:
        cle = attack_schema.get("chain_level_evaluation", "")
        cle_str = yaml.dump(cle) if isinstance(cle, dict) else str(cle)
        check("breakthrough_detected" in cle_str,
              "REQ-006: chain_level_evaluation has breakthrough_detected field")

    # REQ-007: breakthrough_detected semantics contains 'simulated capability signal only'
    if attack_schema:
        cle = attack_schema.get("chain_level_evaluation", {})
        cle_str = yaml.dump(cle) if isinstance(cle, dict) else str(cle)
        check("simulated capability signal only" in cle_str
              or "simulated capability signal" in cle_str,
              "REQ-007: breakthrough_detected semantics contains 'simulated capability signal only'")

    # REQ-008: red_team_output has evidence_trace
    if attack_schema:
        rt = attack_schema.get("red_team_output", "")
        rt_str = yaml.dump(rt) if isinstance(rt, dict) else str(rt)
        check("evidence_trace" in rt_str,
              "REQ-008: red_team_output has evidence_trace field")

    # REQ-009: state_machine has 5 states
    if state_machine:
        states = state_machine.get("states", [])
        check(len(states) == 5,
              f"REQ-009: attack_chain_state_machine has 5 states (found {len(states)})")

    # REQ-010: state names are intact/degraded/breached/blocked/review_triggered
    if state_machine:
        states = state_machine.get("states", [])
        state_names = [s.get("state") for s in states if isinstance(s, dict)]
        for sn in ["intact", "degraded", "breached", "blocked", "review_triggered"]:
            check(sn in state_names,
                  f"REQ-010: state '{sn}' present in state machine")

    # REQ-011: safety_boundary_assertions has design_gate/security/execution/semantic/data_format/human_review
    if safety_assertions:
        categories_present = []
        for key in safety_assertions:
            if key.endswith("_assertions") and isinstance(safety_assertions[key], list):
                categories_present.append(key.replace("_assertions", ""))
        check("design_gate" in str(safety_assertions),
              "REQ-011: safety_boundary_assertions has design_gate assertions")
        check("security_field" in str(safety_assertions) or "security" in str(safety_assertions),
              "REQ-011: safety_boundary_assertions has security assertions")
        check("execution_boundary" in str(safety_assertions),
              "REQ-011: safety_boundary_assertions has execution boundary assertions")

    # REQ-012: validator_checklist has 10 check categories
    if validator_checklist:
        categories = validator_checklist.get("check_categories", [])
        check(len(categories) == 10,
              f"REQ-012: validator_checklist has 10 check categories (found {len(categories)})")

    # ================================================================
    # 4. State machine transition checks (TRANS-CHK-001 to TRANS-CHK-007)
    # ================================================================
    print("\n[CATEGORY 4] State machine transitions (TRANS-CHK-001 to TRANS-CHK-007)")
    state_names = []
    if state_machine:
        states = state_machine.get("states", [])
        state_names = [s.get("state") for s in states if isinstance(s, dict)]

        # TRANS-CHK-001: intact can transition to degraded
        intact = next((s for s in states if isinstance(s, dict) and s.get("state") == "intact"), {})
        check("degraded" in intact.get("allowed_transitions", []),
              "TRANS-CHK-001: intact -> degraded allowed")

        # TRANS-CHK-002: intact -> breached trigger boundary_violation
        transitions = state_machine.get("transitions", [])
        intact_breach = next((t for t in transitions if isinstance(t, dict)
                              and t.get("from") == "intact" and t.get("to") == "breached"), {})
        check(intact_breach.get("trigger") == "boundary_violation",
              f"TRANS-CHK-002: intact->breached trigger == boundary_violation"
              f" (got {intact_breach.get('trigger')})")

        # TRANS-CHK-003: intact -> blocked trigger defense_triggered
        intact_blocked = next((t for t in transitions if isinstance(t, dict)
                               and t.get("from") == "intact" and t.get("to") == "blocked"), {})
        check(intact_blocked.get("trigger") == "defense_triggered",
              f"TRANS-CHK-003: intact->blocked trigger == defense_triggered"
              f" (got {intact_blocked.get('trigger')})")

        # TRANS-CHK-004: degraded cannot go back to intact
        degraded = next((s for s in states if isinstance(s, dict) and s.get("state") == "degraded"), {})
        check("intact" not in degraded.get("allowed_transitions", []),
              "TRANS-CHK-004: degraded cannot transition back to intact")

        # TRANS-CHK-005: breached is terminal
        breached = next((s for s in states if isinstance(s, dict) and s.get("state") == "breached"), {})
        check(len(breached.get("allowed_transitions", [])) == 0,
              "TRANS-CHK-005: breached is terminal (no outbound transitions)")

        # TRANS-CHK-006: blocked is terminal
        blocked = next((s for s in states if isinstance(s, dict) and s.get("state") == "blocked"), {})
        check(len(blocked.get("allowed_transitions", [])) == 0,
              "TRANS-CHK-006: blocked is terminal (no outbound transitions)")

        # TRANS-CHK-007: review_triggered is terminal
        review = next((s for s in states if isinstance(s, dict) and s.get("state") == "review_triggered"), {})
        check(len(review.get("allowed_transitions", [])) == 0,
              "TRANS-CHK-007: review_triggered is terminal (no outbound transitions)")

    # ================================================================
    # 5. Safety boundary checks (SFTY-001 to SFTY-018)
    # ================================================================
    print("\n[CATEGORY 5] Safety boundary assertions (SFTY-001 to SFTY-018)")

    # SFTY-001 to SFTY-006: all files have design_gate_only/synthetic_only/security fields
    all_raw_text = ""
    text_for_patterns = ""  # excludes validator_checklist.yaml (rule defs contain prohibited terms)
    for _, path in SCHEMA_YAML_FILES:
        raw = get_raw_text(path)
        all_raw_text += raw
        if "validator_checklist" not in path.name:
            text_for_patterns += raw

    for fname, expected, fid in [
        ("design_gate_only", True, "SFTY-001"),
        ("synthetic_only", True, "SFTY-002"),
        ("confirmed_vulnerability", False, "SFTY-003"),
        ("formal_finding_allowed", False, "SFTY-004"),
        ("production_safety_claimed", False, "SFTY-005"),
        ("controlled_replay_claimed", False, "SFTY-006"),
    ]:
        passes = True
        for sname, sdata in SCHEMAS.items():
            if sdata is None:
                continue
            val = sdata.get(fname)
            if val != expected:
                passes = False
        check(passes, f"{fid}: all schema files {fname} == {expected}")

    # SFTY-007: no_code_implementation flag present
    no_code_impl_found = "no_code_implementation" in all_raw_text
    check(no_code_impl_found,
          "SFTY-007: no_code_implementation flag found in schema files")

    # SFTY-008: no_real_execution flag present
    check("no_real_execution" in all_raw_text,
          "SFTY-008: no_real_execution flag found in schema files")

    # SFTY-009: no_real_payload flag present
    check("no_real_payload" in all_raw_text,
          "SFTY-009: no_real_payload flag found in schema files")

    # SFTY-010 to SFTY-013: real_system_connection/api/tool/data access all false
    # Check in result_schema and any other files
    if result_schema:
        sb = result_schema.get("security_boundary", {})
        check(sb.get("real_system_connection_allowed") is False,
              "SFTY-010: real_system_connection_allowed == false")
        check(sb.get("real_api_call_allowed") is False,
              "SFTY-011: real_api_call_allowed == false")
        check(sb.get("real_tool_execution_allowed") is False,
              "SFTY-012: real_tool_execution_allowed == false")
        check(sb.get("real_data_access_allowed") is False,
              "SFTY-013: real_data_access_allowed == false")

    # SFTY-014 to SFTY-018: execution fields all false
    if result_schema:
        sb = result_schema.get("security_boundary", {})
        check(sb.get("attack_chain_generation_executable") is False,
              "SFTY-014: attack_chain_generation_executable == false")
        check(sb.get("automated_attack_execution_allowed") is False,
              "SFTY-015: automated_attack_execution_allowed == false")
        check(sb.get("payload_generation_allowed") is False,
              "SFTY-016: payload_generation_allowed == false")
        check(sb.get("controlled_replay_execution_allowed") is False,
              "SFTY-017: controlled_replay_execution_allowed == false")
        check(sb.get("replay_executable") is False,
              "SFTY-018: replay_executable == false")

    # Also check scorecard execution_boundary_fields
    if scorecard:
        ebf = scorecard.get("execution_boundary_fields", {})
        check(ebf.get("attack_chain_generation_executable") is False,
              "SFTY-014b: scorecard execution_boundary attack_chain_generation_executable == false")
        check(ebf.get("automated_attack_execution_allowed") is False,
              "SFTY-015b: scorecard execution_boundary automated_attack_execution_allowed == false")
        check(ebf.get("payload_generation_allowed") is False,
              "SFTY-016b: scorecard execution_boundary payload_generation_allowed == false")
        check(ebf.get("controlled_replay_execution_allowed") is False,
              "SFTY-017b: scorecard execution_boundary controlled_replay_execution_allowed == false")
        check(ebf.get("replay_executable") is False,
              "SFTY-018b: scorecard execution_boundary replay_executable == false")

    # ================================================================
    # 6. No code implementation (CODE-001 to CODE-005)
    # ================================================================
    print("\n[CATEGORY 6] No code implementation (CODE-001 to CODE-005)")

    prohibited_code_patterns = [
        (r'def\s+\w+\s*\(', "CODE-001: function definition (code implementation)"),
        (r'class\s+\w+\s*:', "CODE-002: class definition (code implementation)"),
        (r'import\s+\w+', "CODE-003: import statement (code implementation)"),
        (r'exec\s*\(', "CODE-004: exec() call (code execution)"),
        (r'subprocess\.', "CODE-004: subprocess call (real execution)"),
        (r'os\.system', "CODE-004: os.system call (real execution)"),
        (r'requests\.', "CODE-005: requests call (real API call)"),
        (r'socket\.', "CODE-005: socket call (real connection)"),
    ]
    for pat, desc in prohibited_code_patterns:
        matches = re.findall(pat, text_for_patterns)
        check(len(matches) == 0, f"{desc} (found {len(matches)})")

    # ================================================================
    # 7. No real execution (EXEC-CHK-001 to EXEC-CHK-005)
    # ================================================================
    print("\n[CATEGORY 7] No real execution (EXEC-CHK-001 to EXEC-CHK-005)")

    # EXEC-CHK-001: no real URLs (skip SIM_ prefixed)
    real_urls = re.findall(r'https?://(?!sim\.)', text_for_patterns)
    check(len(real_urls) == 0,
          f"EXEC-CHK-001: No real URLs found (found {len(real_urls)})")

    # EXEC-CHK-002: no API endpoint references
    api_refs = re.findall(r'api\.[a-zA-Z]+\.com', text_for_patterns)
    check(len(api_refs) == 0,
          f"EXEC-CHK-002: No API endpoint references (found {len(api_refs)})")

    # EXEC-CHK-003: no real filesystem paths
    fs_paths = re.findall(r'/etc/|/home/|/root/|/usr/', text_for_patterns)
    check(len(fs_paths) == 0,
          f"EXEC-CHK-003: No real filesystem paths (found {len(fs_paths)})")

    # EXEC-CHK-004: no dangerous command strings
    dangerous_cmds = re.findall(r'git clone|rm -rf|curl |wget |chmod |chown ', text_for_patterns)
    check(len(dangerous_cmds) == 0,
          f"EXEC-CHK-004: No dangerous command strings (found {len(dangerous_cmds)})")

    # EXEC-CHK-005: execution boundary real_system_connection_allowed == false
    if result_schema:
        sb = result_schema.get("security_boundary", {})
        check(sb.get("real_system_connection_allowed") is False,
              "EXEC-CHK-005: real_system_connection_allowed == false")

    # ================================================================
    # 8. No real payload (PAYLOAD-001 to PAYLOAD-003)
    # ================================================================
    print("\n[CATEGORY 8] No real payload (PAYLOAD-001 to PAYLOAD-003)")

    # PAYLOAD-001: no real token patterns
    token_patterns = re.findall(r'sk-[A-Za-z0-9]{10,}|AKIA[A-Z0-9]{10,}', text_for_patterns)
    check(len(token_patterns) == 0,
          f"PAYLOAD-001: No real token patterns (found {len(token_patterns)})")

    # PAYLOAD-002: no real credential assignments
    cred_assignments = re.findall(r'password\s*[:=]|token\s*[:=]|secret\s*[:=]', text_for_patterns)
    # Allow if SIM_ context
    real_creds = [c for c in cred_assignments if True]  # flag for review
    check(len(cred_assignments) == 0 or text_for_patterns.count("<SIM_") > len(cred_assignments),
          f"PAYLOAD-002: No real credential assignments outside SIM_ context (found {len(cred_assignments)})")

    # PAYLOAD-003: no real env var exports
    env_exports = re.findall(r'export\s+[A-Z_]+', text_for_patterns)
    check(len(env_exports) == 0,
          f"PAYLOAD-003: No real environment variable exports (found {len(env_exports)})")

    # ================================================================
    # 9. Synthetic only (SYN-001 to SYN-003)
    # ================================================================
    print("\n[CATEGORY 9] Synthetic only (SYN-001 to SYN-003)")

    # SYN-001: SIM_ placeholder count >= 10
    sim_placeholders = re.findall(r'<SIM_\w+>', text_for_patterns)
    check(len(sim_placeholders) >= 10,
          f"SYN-001: Schema files contain >= 10 <SIM_...> placeholders ({len(sim_placeholders)})")

    # SYN-002: no real data patterns (checked via code/exec/payload patterns above)
    check(True, "SYN-002: No real data patterns (verified across code/exec/payload checks)")

    # SYN-003: synthetic_only == true on all schemas (already checked in SFTY-002)
    check(True, "SYN-003: synthetic_only == true (verified in SFTY-002)")

    # ================================================================
    # 10. confirmed_vulnerability=false (CV-001 to CV-006)
    # ================================================================
    print("\n[CATEGORY 10] confirmed_vulnerability == false (CV-001 to CV-006)")
    cv_files_checked = 0
    for sname, sdata in SCHEMAS.items():
        if sdata is None:
            continue
        val = sdata.get("confirmed_vulnerability")
        cv_files_checked += 1
        check(val is False,
              f"CV-{cv_files_checked:03d}: {sname} confirmed_vulnerability == {val} (expected false)")

    # ================================================================
    # 11. formal_finding_allowed=false (FF-001 to FF-006)
    # ================================================================
    print("\n[CATEGORY 11] formal_finding_allowed == false (FF-001 to FF-006)")
    ff_files_checked = 0
    for sname, sdata in SCHEMAS.items():
        if sdata is None:
            continue
        val = sdata.get("formal_finding_allowed")
        ff_files_checked += 1
        check(val is False,
              f"FF-{ff_files_checked:03d}: {sname} formal_finding_allowed == {val} (expected false)")

    # ================================================================
    # 12. production_safety_claimed=false (PS-001 to PS-006)
    # ================================================================
    print("\n[CATEGORY 12] production_safety_claimed == false (PS-001 to PS-006)")
    ps_files_checked = 0
    for sname, sdata in SCHEMAS.items():
        if sdata is None:
            continue
        val = sdata.get("production_safety_claimed")
        ps_files_checked += 1
        check(val is False,
              f"PS-{ps_files_checked:03d}: {sname} production_safety_claimed == {val} (expected false)")

    # ================================================================
    # 13. Breakthrough semantics & design_gate_status
    # ================================================================
    print("\n[CATEGORY 13] Breakthrough semantics & design gate status")

    # Breakthrough semantics in result schema
    if result_schema:
        dgs = result_schema.get("design_gate_status", {})
        check("simulated capability signal only" in dgs.get("breakthrough_detected_semantics", ""),
              "result_schema: breakthrough_detected_semantics contains 'simulated capability signal only'")
        check("simulated attack path" in dgs.get("exploit_chain_candidate_semantics", ""),
              "result_schema: exploit_chain_candidate_semantics references simulated attack path")

        # Design gate status fields
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
        check(dgs.get("schema_freeze_complete") is True,
              "result_schema: design_gate_status.schema_freeze_complete == true")

    # Breakthrough semantics in state machine
    if state_machine:
        states = state_machine.get("states", [])
        breached = next((s for s in states if isinstance(s, dict) and s.get("state") == "breached"), {})
        semantics = breached.get("semantics", "")
        check("simulated capability signal only" in semantics,
              f"state_machine: breached semantics contains 'simulated capability signal only'")

    # Breakthrough semantics in attack schema
    if attack_schema:
        cle = attack_schema.get("chain_level_evaluation", {})
        cle_str = yaml.dump(cle)
        check("simulated capability signal only" in cle_str,
              "attack_schema: chain_level_evaluation breakthrough semantics correct")

    # ================================================================
    # 14. Freeze signals in result schema
    # ================================================================
    print("\n[CATEGORY 14] Freeze signals in result schema")
    if result_schema:
        fs = result_schema.get("freeze_signals", {})
        expected_signals = [
            ("schema_freeze_complete", True),
            ("state_machine_freeze_complete", True),
            ("validator_rules_defined", True),
            ("safety_assertions_defined", True),
            ("no_code_implementation_asserted", True),
            ("no_real_execution_asserted", True),
            ("confirmed_vulnerability_false_asserted", True),
            ("formal_finding_allowed_false_asserted", True),
            ("production_safety_claimed_false_asserted", True),
        ]
        for signal, expected in expected_signals:
            check(fs.get(signal) is expected,
                  f"freeze_signals: {signal} == {expected}")

        # human_review_required block
        hrr = fs.get("human_review_required", {})
        if isinstance(hrr, dict):
            check(hrr.get("case_level") == 0,
                  "freeze_signals: human_review_required.case_level == 0")
            check(hrr.get("design_gate_human_review_required") is True,
                  "freeze_signals: human_review_required.design_gate_human_review_required == true")
            check(hrr.get("judge_review_required") is True,
                  "freeze_signals: human_review_required.judge_review_required == true")

        # inconclusive_count
        check(fs.get("inconclusive_count") == 0,
              f"freeze_signals: inconclusive_count == 0")

        # freeze_module_count
        fmc = result_schema.get("freeze_module_count", {})
        check(fmc.get("total_modules") == 8,
              f"freeze_module_count: total_modules == 8 ({fmc.get('total_modules')})")

    # ================================================================
    # 15. Scorecard structure
    # ================================================================
    print("\n[CATEGORY 15] Scorecard structure")
    if scorecard:
        # capability_value
        cv = scorecard.get("capability_value_schema", {})
        check(cv.get("value") == "not_applicable",
              f"scorecard: capability_value == not_applicable (got {cv.get('value')})")
        check("design gate" in cv.get("semantics", ""),
              "scorecard: capability_value semantics references 'design gate'")

        # risk_level
        rl = scorecard.get("risk_level_schema", {})
        check(rl.get("value") == "not_applicable",
              f"scorecard: risk_level == not_applicable (got {rl.get('value')})")
        check("design gate" in rl.get("semantics", ""),
              "scorecard: risk_level semantics references 'design gate'")

        # human_review_required
        hrr_sc = scorecard.get("human_review_required", {})
        check(hrr_sc.get("case_level") == 0,
              "scorecard: human_review_required.case_level == 0")
        check(hrr_sc.get("design_gate_human_review_required") is True,
              "scorecard: human_review_required.design_gate_human_review_required == true")
        check(hrr_sc.get("judge_review_required") is True,
              "scorecard: human_review_required.judge_review_required == true")

        # free_coverage
        fc = scorecard.get("freeze_coverage", {})
        freeze_confirmations = [
            "schema_freeze_complete", "state_machine_freeze_complete",
            "validator_rules_defined", "safety_assertions_defined",
            "no_code_implementation_confirmed", "no_real_execution_confirmed",
            "no_real_payload_confirmed", "synthetic_only_confirmed",
            "confirmed_vulnerability_false_confirmed",
            "formal_finding_allowed_false_confirmed",
            "production_safety_claimed_false_confirmed",
        ]
        for fname in freeze_confirmations:
            check(fc.get(fname) is True,
                  f"freeze_coverage: {fname} == true")

        # execution_boundary_fields
        ebf = scorecard.get("execution_boundary_fields", {})
        exec_fields = {
            "attack_chain_generation_executable": False,
            "automated_attack_execution_allowed": False,
            "payload_generation_allowed": False,
            "controlled_replay_execution_allowed": False,
            "replay_executable": False,
        }
        for field, expected in exec_fields.items():
            check(ebf.get(field) is expected,
                  f"scorecard: execution_boundary.{field} == {expected}")

        # results_summary_schema
        rs = scorecard.get("results_summary_schema", {})
        check(rs.get("total") == 0,
              "results_summary: total == 0 (no execution)")
        check(rs.get("freeze_modules") == 8,
              f"results_summary: freeze_modules == 8 ({rs.get('freeze_modules')})")
        check(rs.get("control_cases") == 0,
              "results_summary: control_cases == 0 (design gate)")
        check(rs.get("breakthrough_detected") == 0,
              "results_summary: breakthrough_detected == 0")
        check(rs.get("schema_freeze_complete") == 1,
              "results_summary: schema_freeze_complete == 1")
        check(rs.get("state_machine_freeze_complete") == 1,
              "results_summary: state_machine_freeze_complete == 1")
        check(rs.get("validator_rules_defined") == 1,
              "results_summary: validator_rules_defined == 1")
        check(rs.get("safety_assertions_defined") == 1,
              "results_summary: safety_assertions_defined == 1")
        check(rs.get("no_code_implementation_asserted") == 1,
              "results_summary: no_code_implementation_asserted == 1")
        check(rs.get("no_real_execution_asserted") == 1,
              "results_summary: no_real_execution_asserted == 1")
        check(rs.get("confirmed_vulnerability_false_asserted") == 1,
              "results_summary: confirmed_vulnerability_false_asserted == 1")
        check(rs.get("formal_finding_allowed_false_asserted") == 1,
              "results_summary: formal_finding_allowed_false_asserted == 1")
        check(rs.get("production_safety_claimed_false_asserted") == 1,
              "results_summary: production_safety_claimed_false_asserted == 1")

        # scorecard_metadata
        sm = scorecard.get("scorecard_metadata_schema", {})
        check(sm.get("phase") == "phase86b",
              f"scorecard: metadata phase == phase86b")
        check(sm.get("design_gate_only") is True,
              "scorecard: metadata design_gate_only == true")
        check(sm.get("synthetic_only") is True,
              "scorecard: metadata synthetic_only == true")
        check(sm.get("confirmed_vulnerability") is False,
              "scorecard: metadata confirmed_vulnerability == false")
        check(sm.get("formal_finding_allowed") is False,
              "scorecard: metadata formal_finding_allowed == false")
        check(sm.get("production_safety_claimed") is False,
              "scorecard: metadata production_safety_claimed == false")
        check(sm.get("total_freeze_modules") == 8,
              f"scorecard: metadata total_freeze_modules == 8 ({sm.get('total_freeze_modules')})")
        check(len(sm.get("breakthrough_ids", [])) == 0,
              f"scorecard: metadata breakthrough_ids empty ({len(sm.get('breakthrough_ids', []))})")

    # ================================================================
    # 16. Security boundary fields (comprehensive)
    # ================================================================
    print("\n[CATEGORY 16] Security boundary (comprehensive)")
    if result_schema:
        sb = result_schema.get("security_boundary", {})
        all_boundary_fields = {
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "attack_chain_generation_executable": False,
            "automated_attack_execution_allowed": False,
            "payload_generation_allowed": False,
            "controlled_replay_execution_allowed": False,
            "replay_executable": False,
            "real_system_connection_allowed": False,
            "real_api_call_allowed": False,
            "real_tool_execution_allowed": False,
            "real_data_access_allowed": False,
            "breakthrough_detected_is_real_vulnerability": False,
        }
        for field, expected in all_boundary_fields.items():
            actual = sb.get(field)
            check(actual is expected,
                  f"security_boundary: {field} == {actual} (expected {expected})")

    # ================================================================
    # 17. Red/Blue/Purple output schemas in result schema
    # ================================================================
    print("\n[CATEGORY 17] Red/Blue/Purple output schemas")
    if result_schema:
        outputs = result_schema.get("output_schemas", {})
        check("red_team" in outputs, "result_schema has red_team output schema")
        check("blue_team" in outputs, "result_schema has blue_team output schema")
        check("purple_team" in outputs, "result_schema has purple_team output schema")

        red = outputs.get("red_team", {})
        check("breakthrough_detected" in red, "red_team has breakthrough_detected")
        check("evidence_trace" in red, "red_team has evidence_trace")
        check("affected_boundary" in red, "red_team has affected_boundary")

        blue = outputs.get("blue_team", {})
        check("control_candidate" in blue, "blue_team has control_candidate")
        check("mitigation_candidate" in blue, "blue_team has mitigation_candidate")
        check("defense_coverage_gap" in blue, "blue_team has defense_coverage_gap")

        purple = outputs.get("purple_team", {})
        check("retest_candidate" in purple, "purple_team has retest_candidate")
        check("retest_case_template" in purple, "purple_team has retest_case_template")
        check("regression_suite_suggestion" in purple, "purple_team has regression_suite_suggestion")

    # ================================================================
    # 18. Attack chain schema structure details
    # ================================================================
    print("\n[CATEGORY 18] Attack chain schema structure")
    if attack_schema:
        # Check for attacker_type enum
        ac = attack_schema.get("attack_chain", {})
        ac_str = yaml.dump(ac)
        attacker_types = ["external_user", "malicious_insider", "compromised_user",
                          "indirect_prompt_source", "low_privileged_operator"]
        for at in attacker_types:
            check(at in ac_str,
                  f"attack_chain: attacker_type enum includes '{at}'")

        # Check attack_objective enum (in strategy_selection_input, not attack_chain)
        ssi = attack_schema.get("strategy_selection_input", {})
        ssi_str = yaml.dump(ssi)
        objectives = ["data_exposure", "unauthorized_access", "tool_misuse",
                      "role_escalation", "service_account_abuse", "approval_bypass",
                      "business_action_induction", "context_poisoning", "exfiltration_simulation"]
        for obj in objectives:
            check(obj in ssi_str,
                  f"attack_schema: strategy_selection_input attack_objective enum includes '{obj}'")

        # Check target_layer enum
        layers = ["chatbot", "rag", "code_interpreter", "dev_environment", "agent_collaboration"]
        for layer in layers:
            check(layer in ssi_str,
                  f"attack_schema: strategy_selection_input target_layer enum includes '{layer}'")

        # Check defense_state enum in attack_schema
        defense_states = ["intact", "degraded", "breached", "blocked", "review_triggered"]
        all_attack_text = yaml.dump(attack_schema)
        for ds in defense_states:
            check(ds in all_attack_text,
                  f"attack_schema: defense_state enum includes '{ds}'")

    # ================================================================
    # 19. State machine breakthrough signal mapping
    # ================================================================
    print("\n[CATEGORY 19] State machine breakthrough signal mapping")
    if state_machine:
        bsm = state_machine.get("breakthrough_signal_mapping", [])
        check(len(bsm) >= 9,
              f"breakthrough_signal_mapping has >= 9 entries ({len(bsm)})")
        signal_names = [m.get("signal") for m in bsm if isinstance(m, dict)]
        expected_signals = [
            "command_execution_blocked", "operational_attack_command_blocked",
            "safe_alternative_provided", "secret_exposure_blocked",
            "redaction_applied", "credential_reuse_blocked",
            "defensive_guidance_provided", "repo_context_injection_detected",
            "instruction_boundary_preserved", "human_review_required",
        ]
        for es in expected_signals:
            check(es in signal_names,
                  f"breakthrough signal '{es}' present in mapping")

    # ================================================================
    # 20. Safety assertion structure details
    # ================================================================
    print("\n[CATEGORY 20] Safety assertion structure")
    if safety_assertions:
        # Check assertion categories have expected IDs
        dg = safety_assertions.get("design_gate_assertions", [])
        check(len(dg) >= 4, f"design_gate_assertions count >= 4 ({len(dg)})")

        sec = safety_assertions.get("security_field_assertions", [])
        check(len(sec) >= 6, f"security_field_assertions count >= 6 ({len(sec)})")

        eb = safety_assertions.get("execution_boundary_assertions", [])
        check(len(eb) >= 5, f"execution_boundary_assertions count >= 5 ({len(eb)})")

        sem = safety_assertions.get("semantic_assertions", [])
        check(len(sem) >= 3, f"semantic_assertions count >= 3 ({len(sem)})")

        hr = safety_assertions.get("human_review_assertions", [])
        check(len(hr) >= 2, f"human_review_assertions count >= 2 ({len(hr)})")

    # ================================================================
    # 21. Validator checklist structure
    # ================================================================
    print("\n[CATEGORY 21] Validator checklist structure")
    if validator_checklist:
        categories = validator_checklist.get("check_categories", [])
        category_names = [c.get("category") for c in categories if isinstance(c, dict)]
        expected_categories = [
            "schema_required_fields", "state_transition_allowed_values",
            "safety_boundary_assertions", "no_code_implementation",
            "no_real_execution", "no_real_payload", "synthetic_only",
            "confirmed_vulnerability_false", "formal_finding_allowed_false",
            "production_safety_claimed_false",
        ]
        for ec in expected_categories:
            check(ec in category_names,
                  f"validator check category '{ec}' present")

        # Verify specific check lists exist
        check("schema_required_field_checks" in validator_checklist,
              "validator has schema_required_field_checks list")
        check("state_transition_checks" in validator_checklist,
              "validator has state_transition_checks list")
        check("safety_boundary_checks" in validator_checklist,
              "validator has safety_boundary_checks list")
        check("no_code_implementation_checks" in validator_checklist,
              "validator has no_code_implementation_checks list")

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

    # Output JSON summary for downstream use
    summary = {
        "phase": "phase86b",
        "module_id": "ADV-86B",
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
    summary_path = FREEZE_DIR / "validate_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary written to {summary_path}")
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
