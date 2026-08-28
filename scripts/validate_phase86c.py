#!/usr/bin/env python3
"""validate_phase86c.py — Phase 86C Mock Attack Chain Candidate Composer PoC Validator.

Validates:
  1. All PoC module files exist
  2. Phase 88A fixture loads correctly
  3. Seed selector produces deterministic results + registry_info checks
  4. State machine executor validates transitions correctly
  5. Defense simulator produces valid state transitions
  6. Mock candidate composer produces valid attack paths
  7. Report generator produces candidate report (NOT execution_results)
  8. Output files exist, use correct naming, and contain expected fields
  9. Code-level safety constraints are maintained
  10. PRD compliance: no execution_results, no capability_value/risk_level,
      no coverage_status modification, no executable generator marking
"""
import json
import sys
import yaml
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

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


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 86C — Mock Attack Chain Candidate Composer PoC")
    print("Validation — ALL CHECKS")
    print("red_team_engine_not_executable: true (PRD v3.1 §4)")
    print("=" * 60)

    POC_DIR = ROOT / "attack_chain_poc"
    FIXTURE_DIR = ROOT / "mock_fixtures" / "phase88a"
    OUTPUT_DIR = ROOT / "executions" / "phase86c_attack_chain_poc"

    # ================================================================
    # 1. All PoC module files exist
    # ================================================================
    print("\n1. PoC module file existence")
    required_poc_files = [
        "attack_chain_poc.py",
        "attack_chain_engine.py",
        "seed_selector.py",
        "state_machine_executor.py",
        "defense_degradation_simulator.py",
        "report_generator.py",
        "phase88a_fixture_loader.py",
        "run_config.yaml",
    ]
    for f in required_poc_files:
        path = POC_DIR / f
        exists = path.exists()
        check(exists, f"PoC file '{f}' exists")
        if exists:
            check(path.stat().st_size > 0, f"PoC file '{f}' is non-empty")

    # ================================================================
    # 2. Run config loaded — verify all safety declarations
    # ================================================================
    print("\n2. Run config validation")
    config_path = POC_DIR / "run_config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        rc = config.get("run_config", {})
        check(rc.get("phase") == "phase86c", "run_config: phase == phase86c")
        check(rc.get("assessment_mode") == "adversarial_validation",
              "run_config: assessment_mode == adversarial_validation")
        # Component type — must NOT be an executable engine
        check(rc.get("component_type") == "mock_candidate_composer",
              "run_config: component_type == mock_candidate_composer (not executable engine)")
        check("executable" not in rc.get("engine", "").lower(),
              "run_config: engine does not contain 'executable'")
        # PRD v3.1 §4: red_team_engine_not_executable
        check(rc.get("red_team_engine_not_executable") is True,
              "run_config: red_team_engine_not_executable == true")
        # PRD §4: attack_execution_allowed
        check(rc.get("attack_execution_allowed") is False,
              "run_config: attack_execution_allowed == false")
        # PRD §12: payload_generation_allowed
        check(rc.get("payload_generation_allowed") is False,
              "run_config: payload_generation_allowed == false")
        # PRD v3.1 §4: real_target_selection_allowed
        check(rc.get("real_target_selection_allowed") is False,
              "run_config: real_target_selection_allowed == false")
        # PRD §16: confirmed_vulnerability
        check(rc.get("confirmed_vulnerability") is False,
              "run_config: confirmed_vulnerability == false")
        # PRD §3/§11: formal_finding_allowed
        check(rc.get("formal_finding_allowed") is False,
              "run_config: formal_finding_allowed == false")
        # PRD v3.1 §4: production_safety_claimed
        check(rc.get("production_safety_claimed") is False,
              "run_config: production_safety_claimed == false")
        # PRD v2.0 §4: synthetic_only
        check(rc.get("synthetic_only") is True,
              "run_config: synthetic_only == true")
        # PRD v2.0 §13: no_execution_results_generated
        check(rc.get("no_execution_results_generated") is True,
              "run_config: no_execution_results_generated == true")
        check(rc.get("no_real_execution") is True,
              "run_config: no_real_execution == true")
        check(rc.get("no_real_payload") is True,
              "run_config: no_real_payload == true")
        check(rc.get("no_external_io_beyond_local_files") is True,
              "run_config: no_external_io_beyond_local_files == true")
        check(rc.get("no_real_tool_simulation_beyond_fake_runtime") is True,
              "run_config: no_real_tool_simulation_beyond_fake_runtime == true")
        # PRD §4: no_external_network
        check(rc.get("no_external_network") is True,
              "run_config: no_external_network == true")
        check(rc.get("real_system_connection_allowed") is False,
              "run_config: real_system_connection_allowed == false")
        check(rc.get("real_api_call_allowed") is False,
              "run_config: real_api_call_allowed == false")
        check(rc.get("real_tool_execution_allowed") is False,
              "run_config: real_tool_execution_allowed == false")

    # ================================================================
    # 3. Phase 88A fixture loading
    # ================================================================
    print("\n3. Fixture loading test")
    fixture = None
    try:
        from attack_chain_poc.phase88a_fixture_loader import load_fixture
        fixture = load_fixture(FIXTURE_DIR)
        check(fixture is not None, "Fixture loaded successfully")
        chains = fixture.get("attack_chains", [])
        nodes = fixture.get("attack_nodes", [])
        transitions = fixture.get("state_machine_transitions", [])
        check(len(chains) >= 10, f"Fixture contains >= 10 attack chains ({len(chains)})")
        check(len(nodes) >= 14, f"Fixture contains >= 14 attack nodes ({len(nodes)})")
        check(len(transitions) >= 10, f"Fixture contains >= 10 transitions ({len(transitions)})")
        meta = fixture.get("fixture_metadata", {})
        check(meta.get("synthetic_only") is True,
              "Fixture metadata: synthetic_only == true")
        check(meta.get("confirmed_vulnerability") is False,
              "Fixture metadata: confirmed_vulnerability == false")
        check(meta.get("formal_finding_allowed") is False,
              "Fixture metadata: formal_finding_allowed == false")
    except Exception as e:
        check(False, f"Fixture loading: {e}")

    # ================================================================
    # 4. Seed selector test — with registry_info checks
    # ================================================================
    print("\n4. Seed selector test (mock_seed_selector)")
    try:
        from attack_chain_poc.seed_selector import (
            load_registry_scores, select_seeds
        )
        registry_path = ROOT / "capability_modules" / "module_registry.yaml"
        scores = load_registry_scores(registry_path)
        check(len(scores) >= 8, f"Loaded scores for >= 8 modules ({len(scores)})")

        seeds = select_seeds(scores, count=4, strategy="diverse",
                             registry_path=registry_path)
        check(len(seeds) == 4, f"Selected 4 seeds (got {len(seeds)})")
        check(len(seeds) == len({s["seed_module_id"] for s in seeds}),
              "All seeds have unique module IDs")
        for s in seeds:
            check("seed_module_id" in s, f"Seed has seed_module_id")
            check("score" in s, f"Seed has score")
            check("layer" in s, f"Seed has layer")
            check("selection_reason" in s, f"Seed has selection_reason")
            check("registry_info" in s, f"Seed has registry_info")
            ri = s.get("registry_info", {})
            check("registered" in ri, f"Seed registry_info has 'registered'")
            check("legacy_reference_only" in ri,
                  f"Seed registry_info has 'legacy_reference_only'")
            check("counts_toward_registered_module_coverage" in ri,
                  f"Seed registry_info has 'counts_toward_registered_module_coverage'")
            check("no_registry_credit" in ri,
                  f"Seed registry_info has 'no_registry_credit'")
            check(isinstance(s["score"], (int, float)),
                  f"Seed score is numeric ({s['score']})")
            # PRD v2.0 §10.2: M01 (and M0x) must be legacy_reference_only
            if s["seed_module_id"] == "M01":
                check(ri.get("legacy_reference_only") is True,
                      "M01: legacy_reference_only == true (PRD v2.0 §10.2)")
                check(ri.get("no_registry_credit") is True,
                      "M01: no_registry_credit == true (PRD v2.0 §10.2)")
                check(ri.get("counts_toward_registered_module_coverage") is False,
                      "M01: counts_toward_registered_module_coverage == false")
    except Exception as e:
        check(False, f"Seed selector: {e}")

    # ================================================================
    # 5. State machine executor test
    # ================================================================
    print("\n5. State machine executor test")
    try:
        from attack_chain_poc.state_machine_executor import (
            execute_transition, is_valid_transition, get_valid_targets
        )

        # Valid transitions
        result = execute_transition("idle", "entry_selected")
        check(result["success"], "Valid transition: idle -> entry_selected")

        result = execute_transition("defense_pressured", "defense_degraded")
        check(result["success"], "Valid transition: defense_pressured -> defense_degraded")

        result = execute_transition("runtime_blocked", "human_review_required")
        check(result["success"], "Valid transition: runtime_blocked -> human_review_required")

        # Invalid transitions
        result = execute_transition("chain_closed", "node_entered")
        check(not result["success"], "Invalid transition: chain_closed -> node_entered (terminal)")
        check("TERMINAL_STATE_REENTRY" in result.get("error", ""),
              "Terminal re-entry error message is descriptive")

        result = execute_transition("entry_selected", "runtime_blocked")
        check(not result["success"], "Invalid transition: entry_selected -> runtime_blocked (skip)")
        check("MISSING_INTERMEDIATE_STATE" in result.get("error", ""),
              "Skip-path error message is descriptive")

        # is_valid_transition
        check(is_valid_transition("idle", "entry_selected"),
              "is_valid_transition: idle -> entry_selected")
        check(not is_valid_transition("chain_closed", "node_entered"),
              "is_valid_transition: chain_closed -> node_entered is invalid")

        # get_valid_targets
        targets = get_valid_targets("defense_pressured")
        check("defense_degraded" in targets,
              "get_valid_targets: defense_pressured includes defense_degraded")
        check("runtime_blocked" in targets,
              "get_valid_targets: defense_pressured includes runtime_blocked")
        targets_idle = get_valid_targets("chain_closed")
        check(len(targets_idle) == 0,
              "get_valid_targets: chain_closed returns empty list (terminal)")

    except Exception as e:
        check(False, f"State machine executor: {e}")

    # ================================================================
    # 6. Defense degradation simulator test
    # ================================================================
    print("\n6. Defense degradation simulator test")
    try:
        from attack_chain_poc.defense_degradation_simulator import (
            simulate_step, compute_fake_runtime_decision
        )

        # Simulate from stable
        result = simulate_step("stable", pressure_level=2, seed=42)
        check(result["defense_state_before"] == "stable",
              "Simulator: before state is stable")
        check(result["defense_state_after"] in (
            "stable", "pressured", "degraded", "blocked"
        ), f"Simulator: after state is valid ({result['defense_state_after']})")
        check("signal_generated" in result, "Simulator: has signal_generated")
        check("defensive_action" in result, "Simulator: has defensive_action")
        check("human_review_required" in result, "Simulator: has human_review_required")
        check("boundary_type" in result, "Simulator: has boundary_type")
        check("pressure_level" in result, "Simulator: has pressure_level")

        # Simulate from blocked
        result = simulate_step("blocked", pressure_level=3, seed=99)
        check(result["defense_state_before"] == "blocked",
              "Simulator: before state is blocked")
        check(result["defense_state_after"] in (
            "blocked", "requires_human_review"
        ), f"Simulator: blocked transitions valid ({result['defense_state_after']})")

        # Fake runtime decision
        decision = compute_fake_runtime_decision("blocked")
        check(decision["fake_runtime_decision"] == "block",
              "Fake runtime: blocked state -> block decision")
        check(decision["sandbox_boundary_preserved"] is True,
              "Fake runtime: blocked -> boundary preserved")

        decision = compute_fake_runtime_decision("stable")
        check(decision["fake_runtime_decision"] == "allow",
              "Fake runtime: stable state -> allow decision")

        decision = compute_fake_runtime_decision("inconclusive")
        check(decision["sandbox_boundary_preserved"] is False,
              "Fake runtime: inconclusive -> boundary NOT preserved")

    except Exception as e:
        check(False, f"Defense degradation simulator: {e}")

    # ================================================================
    # 7. Mock candidate composer test (NOT attack chain engine)
    # ================================================================
    print("\n7. Mock candidate composer test")
    try:
        from attack_chain_poc.attack_chain_engine import (
            generate_attack_path,
            generate_defense_degradation,
            generate_red_blue_purple_output,
        )

        # Generate test path
        seed = {"seed_module_id": "M50", "score": 90, "layer": "runtime"}
        path = generate_attack_path(
            seed=seed,
            fixture_nodes=fixture.get("attack_nodes", []) if fixture else [],
            fixture_chains=fixture.get("attack_chains", []) if fixture else [],
            max_depth=3,
        )
        check(path["chain_id"].startswith("<SIM_"),
              f"Chain ID uses SIM_ prefix ({path['chain_id']})")
        check("path" in path, "Attack path has 'path' key")
        check("valid_path" in path, "Attack path has 'valid_path' key")
        check("path_depth" in path, "Attack path has 'path_depth' key")
        check(path["path_depth"] >= 1,
              f"Attack path depth >= 1 ({path['path_depth']})")
        check(path.get("objective") == "simulated_attack_chain_propagation",
              "Attack path objective is simulated")

        # Defense degradation
        deg = generate_defense_degradation(path, seed=42)
        check(deg["chain_id"] == path["chain_id"],
              "Defense degradation chain_id matches attack path")
        check(len(deg["steps"]) >= 1, "Defense degradation has >= 1 steps")
        check(deg["overall_breakthrough_detected"] is False,
              "Defense degradation: breakthrough_detected == false")
        check(deg["confirmed_vulnerability"] is False,
              "Defense degradation: confirmed_vulnerability == false")

        # Red/Blue/Purple output
        output = generate_red_blue_purple_output(path, deg)
        check("red_team" in output, "Output has red_team")
        check("blue_team" in output, "Output has blue_team")
        check("purple_team" in output, "Output has purple_team")
        check(output["red_team"]["breakthrough_detected"] is False,
              "Red team: breakthrough_detected == false")
        check(len(output["red_team"]["evidence_trace"]) >= 1,
              "Red team: evidence_trace non-empty")
        check(len(output["blue_team"]["control_candidate"]) >= 1,
              "Blue team: control_candidate non-empty")
        check(len(output["purple_team"]["retest_candidate"]) >= 1,
              "Purple team: retest_candidate non-empty")

    except Exception as e:
        check(False, f"Mock candidate composer: {e}")

    # ================================================================
    # 8. Report generator test — candidate report, NOT execution_results
    # ================================================================
    print("\n8. Report generator test (candidate report, NOT execution_results)")
    try:
        from attack_chain_poc.report_generator import (
            generate_candidate_report,
            write_report,
        )

        report = generate_candidate_report(
            degradation_results=[deg] if 'deg' in dir() else [],
            attack_paths=[path] if 'path' in dir() else [],
            red_blue_purple_outputs=[output] if 'output' in dir() else [],
        )
        check("report_metadata" in report, "Report has report_metadata")
        check("candidate_summary" in report,
              "Report has candidate_summary (NOT results_summary)")
        check("results_summary" not in report,
              "Report does NOT contain old 'results_summary' key")
        check("candidate_attack_chains" in report,
              "Report has candidate_attack_chains")
        check("attack_chains" not in report,
              "Report does NOT contain old 'attack_chains' key")
        check("candidate_defense_degradation_trajectories" in report,
              "Report has candidate_defense_degradation_trajectories")
        check("defense_degradation_trajectories" not in report,
              "Report does NOT contain old 'defense_degradation_trajectories' key")
        check("candidate_red_blue_purple_outputs" in report,
              "Report has candidate_red_blue_purple_outputs")
        check("red_blue_purple_outputs" not in report,
              "Report does NOT contain old 'red_blue_purple_outputs' key")
        check("safety_assertions" in report, "Report has safety_assertions")

        cs = report["candidate_summary"]
        check("total_candidate_paths" in cs,
              "Summary has total_candidate_paths (NOT total_attack_paths_generated)")
        check("total_attack_paths_generated" not in cs,
              "Summary does NOT contain old 'total_attack_paths_generated'")
        check("valid_candidate_paths" in cs, "Summary has valid_candidate_paths")
        check("invalid_candidate_paths" in cs, "Summary has invalid_candidate_paths")
        # PRD v2.0 §13: must NOT declare capability_value or risk_level
        check("capability_value" not in cs,
              "Summary does NOT declare capability_value (PRD v2.0 §13)")
        check("risk_level" not in cs,
              "Summary does NOT declare risk_level (PRD v2.0 §13)")
        check("mock_control_case_performance" in cs,
              "Summary has mock_control_case_performance")
        check("mock_state_distribution" in cs,
              "Summary has mock_state_distribution")
        check("inconclusive_count" in cs, "Summary has inconclusive_count")
        check("human_review_required_count" in cs,
              "Summary has human_review_required_count")
        check(cs["confirmed_vulnerability"] is False,
              "Summary: confirmed_vulnerability == false")
        check(cs["formal_finding_allowed"] is False,
              "Summary: formal_finding_allowed == false")
        check(cs["production_safety_claimed"] is False,
              "Summary: production_safety_claimed == false")
        check(cs["red_team_engine_not_executable"] is True,
              "Summary: red_team_engine_not_executable == true (PRD v3.1 §4)")
        check(cs["attack_execution_allowed"] is False,
              "Summary: attack_execution_allowed == false")
        check(cs["payload_generation_allowed"] is False,
              "Summary: payload_generation_allowed == false")
        check(cs["real_target_selection_allowed"] is False,
              "Summary: real_target_selection_allowed == false (PRD v3.1 §4)")
        check(cs["no_execution_results_generated"] is True,
              "Summary: no_execution_results_generated == true (PRD v2.0 §13)")
        check(cs["no_external_network"] is True,
              "Summary: no_external_network == true (PRD §4)")

        rm = report["report_metadata"]
        check(rm["synthetic_only"] is True,
              "Metadata: synthetic_only == true")
        check(rm["confirmed_vulnerability"] is False,
              "Metadata: confirmed_vulnerability == false")
        check(rm["formal_finding_allowed"] is False,
              "Metadata: formal_finding_allowed == false")
        check(rm["red_team_engine_not_executable"] is True,
              "Metadata: red_team_engine_not_executable == true")
        check(rm["no_execution_results_generated"] is True,
              "Metadata: no_execution_results_generated == true")

        sa = report["safety_assertions"]
        check(sa["red_team_engine_not_executable"] is True,
              "Safety: red_team_engine_not_executable == true")
        check(sa["attack_execution_allowed"] is False,
              "Safety: attack_execution_allowed == false")
        check(sa["payload_generation_allowed"] is False,
              "Safety: payload_generation_allowed == false")
        check(sa["real_target_selection_allowed"] is False,
              "Safety: real_target_selection_allowed == false")
        check(sa["confirmed_vulnerability"] is False,
              "Safety: confirmed_vulnerability == false")
        check(sa["formal_finding_allowed"] is False,
              "Safety: formal_finding_allowed == false")
        check(sa["production_safety_claimed"] is False,
              "Safety: production_safety_claimed == false")
        check(sa["synthetic_only"] is True,
              "Safety: synthetic_only == true")
        check(sa["no_real_execution"] is True,
              "Safety: no_real_execution == true")
        check(sa["no_external_network"] is True,
              "Safety: no_external_network == true")
        check(sa["no_execution_results_generated"] is True,
              "Safety: no_execution_results_generated == true")
        check(sa["no_external_io_beyond_local_files"] is True,
              "Safety: no_external_io_beyond_local_files == true")
        check(sa["no_real_tool_simulation_beyond_fake_runtime"] is True,
              "Safety: no_real_tool_simulation_beyond_fake_runtime == true")

        # PRD v3.1 §6: generator must NOT be marked as executable
        check(rm.get("report_type") == "mock_candidate_trajectory",
              "Metadata: report_type == mock_candidate_trajectory (not execution_results)")

    except Exception as e:
        check(False, f"Report generator: {e}")

    # ================================================================
    # 9. Output file existence — uses candidate naming, NOT execution_results
    # ================================================================
    print("\n9. Output file existence (candidate naming, not execution_results)")
    # PRD v2.0 §13: must NOT generate execution_results
    output_json_candidate = OUTPUT_DIR / "candidate_trajectory_results.json"
    output_json_old = OUTPUT_DIR / "execution_results.json"
    output_yaml = OUTPUT_DIR / "defense_degradation_trajectory.yaml"

    # PRD v2.0 §13: verify no execution_results.json exists
    check(not output_json_old.exists(),
          "execution_results.json does NOT exist (PRD v2.0 §13)")

    if output_json_candidate.exists():
        check(output_json_candidate.stat().st_size > 0,
              "candidate_trajectory_results.json is non-empty")
        with open(output_json_candidate) as f:
            json_data = json.load(f)
        check(json_data.get("report_metadata", {}).get("phase") == "phase86c",
              "Output JSON: phase == phase86c")
        check(json_data.get("report_metadata", {}).get("synthetic_only") is True,
              "Output JSON: synthetic_only == true")
        check(json_data.get("report_metadata", {}).get("confirmed_vulnerability") is False,
              "Output JSON: confirmed_vulnerability == false")
        check(json_data.get("report_metadata", {}).get("no_execution_results_generated") is True,
              "Output JSON: no_execution_results_generated == true")
        # Verify no capability_value or risk_level in output
        cs = json_data.get("candidate_summary", {})
        check("capability_value" not in cs,
              "Output JSON: no capability_value declared")
        check("risk_level" not in cs,
              "Output JSON: no risk_level declared")
    else:
        check(False, "candidate_trajectory_results.json exists (run PoC first)")

    if output_yaml.exists():
        check(output_yaml.stat().st_size > 0,
              "defense_degradation_trajectory.yaml is non-empty")
        with open(output_yaml) as f:
            yaml_data = yaml.safe_load(f)
        check(yaml_data.get("report_metadata", {}).get("phase") == "phase86c",
              "Output YAML: phase == phase86c")
    else:
        check(False, "defense_degradation_trajectory.yaml exists (run PoC first)")

    # ================================================================
    # 10. Code-level safety checks
    # ================================================================
    print("\n10. Code-level safety checks")
    all_poc_code = ""
    for f in required_poc_files:
        path = POC_DIR / f
        if path.exists():
            all_poc_code += path.read_text()

    prohibited = [
        (r'import\s+(socket|requests|subprocess|os\.system)', "network/system calls"),
        (r'exec\s*\(', "exec() calls"),
        (r'eval\s*\(', "eval() calls"),
        (r'__import__\s*\(', "dynamic imports"),
        (r'open\s*\([^)]*["\']/[^)]*["\']', "absolute path file opens (should use Path)"),
    ]
    for pattern, desc in prohibited:
        matches = re.findall(pattern, all_poc_code)
        check(len(matches) == 0, f"No {desc} in PoC code (found {len(matches)})")

    # Check for SIM_ placeholder usage across source, fixture, and output
    sim_check_text = all_poc_code
    for fname in ["mock_attack_chains.yaml", "mock_attack_nodes.json",
                  "mock_state_machine_transitions.yaml", "mock_defense_state_events.json",
                  "mock_safety_boundary_assertions.yaml", "mock_red_blue_purple_mapping.yaml",
                  "mock_evidence_traces.json"]:
        fpath = FIXTURE_DIR / fname
        if fpath.exists():
            sim_check_text += fpath.read_text()
    if output_json_candidate.exists():
        sim_check_text += output_json_candidate.read_text()
    if output_yaml.exists():
        sim_check_text += output_yaml.read_text()
    sim_count = len(re.findall(r'<SIM_\w+>', sim_check_text))
    check(sim_count >= 30,
          f"Combined source + fixture + output contains >= 30 <SIM_...> placeholders ({sim_count})")

    # Check no real URLs
    real_urls = re.findall(r'https?://(?!sim\.)', all_poc_code)
    check(len(real_urls) == 0, f"No real URLs in PoC code (found {len(real_urls)})")

    # ================================================================
    # 11. SIM_ prefix in output files
    # ================================================================
    print("\n11. SIM_ prefix in output files")
    if output_json_candidate.exists():
        json_text = output_json_candidate.read_text()
        sim_count_json = len(re.findall(r'<SIM_\w+>', json_text))
        check(sim_count_json >= 10,
              f"Output JSON contains >= 10 <SIM_...> placeholders ({sim_count_json})")
    if output_yaml.exists():
        yaml_text = output_yaml.read_text()
        sim_count_yaml = len(re.findall(r'<SIM_\w+>', yaml_text))
        check(sim_count_yaml >= 10,
              f"Output YAML contains >= 10 <SIM_...> placeholders ({sim_count_yaml})")

    # ================================================================
    # 12. PRD v3.1 §6/§7: generator not marked as executable
    # ================================================================
    print("\n12. PRD compliance: no executable generator marking")
    # Check all PoC source files for prohibited terminology
    for f in required_poc_files:
        path = POC_DIR / f
        if path.exists():
            text = path.read_text().lower()
            if "attack chain generation engine" in text:
                check(False, f"{f}: contains 'attack chain generation engine' (PRD v3.1 §6/§7)")
                break
            if "attack start selector" in text:
                check(False, f"{f}: contains 'attack start selector' (PRD v3.1 §4)")
                break
    else:
        check(True, "No 'attack chain generation engine' or 'attack start selector' in any PoC file")

    # Verify run_config engine field does not suggest executability
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        rc = config.get("run_config", {})
        engine_val = rc.get("engine", "")
        if "executable" in engine_val.lower() or "engine" == engine_val.lower():
            check(False, "run_config engine field suggests executability")
        else:
            check(True, f"run_config engine field is safe: '{engine_val}'")

    # Check no coverage_status modification (M43/M46/M50)
    print("\n13. PRD compliance: no coverage_status modification")
    coverage_mod_patterns = [
        r'M43.*coverage_status',
        r'M46.*coverage_status',
        r'M50.*coverage_status',
        r'coverage_status.*M43',
        r'coverage_status.*M46',
        r'coverage_status.*M50',
    ]
    for pattern in coverage_mod_patterns:
        matches = re.findall(pattern, all_poc_code)
        check(len(matches) == 0,
              f"No coverage_status modification for M43/M46/M50 (found {len(matches)})")

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
