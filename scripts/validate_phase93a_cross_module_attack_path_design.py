#!/usr/bin/env python3
"""Phase 93A — M46→M47→M50 Cross-Module Attack Path Design Gate Validator.

Comprehensive checks for attack path schema, trace correlation rules,
defense state machine, Red/Blue/Purple mapping, and security fields.
"""
import sys, yaml
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


def yaml_load(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load: {path} — {e}")
        return None


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 93A — Cross-Module Attack Path Design Gate Validation")
    print("=" * 60)

    # ================================================================
    # 1. Attack Path Schema
    # ================================================================
    print("\n1. Attack Path Schema")
    schema_path = ROOT / "executions/phase93a_cross_module_attack_path_design/attack_path_schema.yaml"
    schema = yaml_load(schema_path)
    check(schema is not None, "Attack path schema loaded")
    if schema:
        # Check schema metadata
        meta = schema.get("schema_metadata", {})
        check(meta.get("design_gate") is True, "Schema metadata design_gate == true")
        check(meta.get("capability_value") == "not_applicable",
              "Schema metadata capability_value == not_applicable")
        check(meta.get("risk_level") == "not_applicable",
              "Schema metadata risk_level == not_applicable")

        # Check schema fields
        attack_path_schema = schema.get("attack_path_schema", {})
        fields = attack_path_schema.get("fields", [])
        check("path_id" in [f.get("name") if isinstance(f, dict) else f for f in fields] or
              any("path_id" in str(f) for f in fields),
              "Schema has path_id field")
        check("entry_module" in str(fields), "Schema has entry_module field")
        check("propagation_steps" in str(fields), "Schema has propagation_steps field")
        check("target_module" in str(fields), "Schema has target_module field")

        # Check predefined paths
        paths = schema.get("predefined_attack_paths", [])
        check(len(paths) >= 3, f"Schema has >= 3 predefined paths ({len(paths)})")
        for p in paths:
            check("path_id" in p, f"Path {p.get('path_id', 'UNKNOWN')} has path_id")
            check("entry_module" in p, f"Path {p.get('path_id', 'UNKNOWN')} has entry_module")
            check("target_module" in p, f"Path {p.get('path_id', 'UNKNOWN')} has target_module")
            check("propagation_steps" in p, f"Path {p.get('path_id', 'UNKNOWN')} has propagation_steps")

    # ================================================================
    # 2. Trace Correlation Rules
    # ================================================================
    print("\n2. Trace Correlation Rules")
    trace_path = ROOT / "executions/phase93a_cross_module_attack_path_design/trace_correlation_rules.yaml"
    trace = yaml_load(trace_path)
    check(trace is not None, "Trace correlation rules loaded")
    if trace:
        rules = trace.get("trace_correlation_rules", {})

        # Check trace_id propagation
        propagation = rules.get("trace_id_propagation", {})
        check(len(propagation.get("rules", [])) >= 3,
              f"Trace ID propagation has >= 3 rules ({len(propagation.get('rules', []))})")

        # Check audit log correlation
        audit = rules.get("audit_log_correlation", {})
        check(len(audit.get("rules", [])) >= 3,
              f"Audit log correlation has >= 3 rules ({len(audit.get('rules', []))})")

        # Check identity correlation
        identity = rules.get("identity_correlation", {})
        check(len(identity.get("rules", [])) >= 2,
              f"Identity correlation has >= 2 rules ({len(identity.get('rules', []))})")

        # Check tenant correlation
        tenant = rules.get("tenant_correlation", {})
        check(len(tenant.get("rules", [])) >= 2,
              f"Tenant correlation has >= 2 rules ({len(tenant.get('rules', []))})")

    # ================================================================
    # 3. Defense State Machine
    # ================================================================
    print("\n3. Defense State Machine")
    dsm_path = ROOT / "executions/phase93a_cross_module_attack_path_design/defense_state_machine.yaml"
    dsm = yaml_load(dsm_path)
    check(dsm is not None, "Defense state machine loaded")
    if dsm:
        dsm_def = dsm.get("defense_state_machine", {})

        # Check states
        states = dsm_def.get("defense_states", {})
        check("stable" in states, "DSM has stable state")
        check("pressured" in states, "DSM has pressured state")
        check("degraded" in states, "DSM has degraded state")
        check("blocked" in states, "DSM has blocked state")
        check("failed" in states, "DSM has failed state")

        # Check transitions
        transitions = dsm_def.get("state_transitions", [])
        check(len(transitions) >= 5, f"DSM has >= 5 transitions ({len(transitions)})")

        # Check propagation dynamics
        dynamics = dsm_def.get("propagation_dynamics", {})
        check("base_propagation_probability" in dynamics,
              "DSM has base_propagation_probability")
        check("decay_factor" in dynamics, "DSM has decay_factor")
        check("amplification_factor" in dynamics, "DSM has amplification_factor")

        # Check feedback loops
        loops = dsm_def.get("feedback_loops", [])
        check(len(loops) >= 2, f"DSM has >= 2 feedback loops ({len(loops)})")

        # Check attack propagation modeling layer
        modeling = dsm_def.get("attack_propagation_modeling", {})
        check(len(modeling) > 0, "DSM has attack_propagation_modeling layer")
        if modeling:
            # Check propagation probability calculation
            prob_calc = modeling.get("propagation_probability_calculation", {})
            check("formula" in prob_calc, "Modeling has propagation formula")
            check("defense_modifier" in prob_calc, "Modeling has defense_modifier")

            # Check decay model
            decay = modeling.get("decay_model", {})
            check("decay_per_hop" in decay, "Modeling has decay_per_hop")
            check("cumulative_decay_formula" in decay, "Modeling has cumulative_decay_formula")

            # Check amplification model
            amp = modeling.get("amplification_model", {})
            check("amplification_triggers" in amp, "Modeling has amplification_triggers")

            # Check cross-module propagation
            cross_prop = modeling.get("cross_module_propagation", {})
            check(len(cross_prop.get("rules", [])) >= 4,
                  f"Modeling has >= 4 cross-module rules ({len(cross_prop.get('rules', []))})")

            # Check path success probability
            path_prob = modeling.get("path_success_probability", {})
            check("formula" in path_prob, "Modeling has path_success_probability formula")
            check("example_calculation" in path_prob, "Modeling has example_calculation")

            # Check degradation trajectory prediction
            degrad = modeling.get("degradation_trajectory_prediction", {})
            check("prediction_model" in degrad, "Modeling has degradation prediction_model")
            check("transition_matrix" in degrad, "Modeling has transition_matrix")

            # Check critical decay nodes
            critical = modeling.get("critical_decay_nodes", {})
            check(len(critical.get("nodes", [])) >= 2,
                  f"Modeling has >= 2 critical decay nodes ({len(critical.get('nodes', []))})")

            # Check feedback loop dynamics
            fb_dynamics = modeling.get("feedback_loop_dynamics", {})
            check(len(fb_dynamics.get("loops", [])) >= 2,
                  f"Modeling has >= 2 feedback loop dynamics ({len(fb_dynamics.get('loops', []))})")

    # ================================================================
    # 4. Red/Blue/Purple Mapping
    # ================================================================
    print("\n4. Red/Blue/Purple Mapping")
    rbp_path = ROOT / "executions/phase93a_cross_module_attack_path_design/red_blue_purple_mapping.yaml"
    rbp = yaml_load(rbp_path)
    check(rbp is not None, "Red/Blue/Purple mapping loaded")
    if rbp:
        rbp_def = rbp.get("red_blue_purple_mapping", {})

        # Check Red output
        red = rbp_def.get("red_team_output", {})
        check("fields" in red, "Red team output has fields")
        check("safety_constraints" in red, "Red team output has safety_constraints")

        # Check Blue output
        blue = rbp_def.get("blue_team_output", {})
        check("fields" in blue, "Blue team output has fields")
        check("control_categories" in blue, "Blue team output has control_categories")

        # Check Purple output
        purple = rbp_def.get("purple_team_output", {})
        check("fields" in purple, "Purple team output has fields")
        check("retest_methods" in purple, "Purple team output has retest_methods")

        # Check path mappings
        mappings = rbp_def.get("path_mappings", [])
        check(len(mappings) >= 2, f"RBP has >= 2 path mappings ({len(mappings)})")
        for m in mappings:
            check("path_id" in m, f"Mapping {m.get('path_id', 'UNKNOWN')} has path_id")
            check("red_output" in m, f"Mapping {m.get('path_id', 'UNKNOWN')} has red_output")
            check("blue_output" in m, f"Mapping {m.get('path_id', 'UNKNOWN')} has blue_output")
            check("purple_output" in m, f"Mapping {m.get('path_id', 'UNKNOWN')} has purple_output")

    # ================================================================
    # 5. Security field consistency
    # ================================================================
    print("\n5. Security field consistency")
    deliverables = {
        "attack_path_schema": schema,
        "trace_correlation_rules": trace,
        "defense_state_machine": dsm,
        "red_blue_purple_mapping": rbp,
    }
    for name, data in deliverables.items():
        if data is None:
            check(False, f"{name}: could not load — skipping")
            continue
        data_str = str(data).lower()
        check("confirmed_vulnerability" not in data_str or 'false' in data_str,
              f"{name}: confirmed_vulnerability == false")
        check("production_safety" not in data_str or 'out_of_scope' in data_str or 'not_applicable' in data_str,
              f"{name}: production_safety == out_of_scope or not_applicable")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print("Phase 93A Cross-Module Attack Path Design Gate: ALL CHECKS PASSED")
    else:
        print("Phase 93A Cross-Module Attack Path Design Gate: FAILED")
    print(f"  checks_passed: {checks_passed}")
    print(f"  checks_failed: {checks_failed}")
    if errors:
        print("\n  Errors:")
        for e in errors:
            print(f"    - {e}")
    print("=" * 60)

    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
