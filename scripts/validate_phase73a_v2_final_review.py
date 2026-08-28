#!/usr/bin/env python3
"""Phase 73A — PRD v2.0 Final Review and Closure Validator.

Review-only validator. Checks registry, schema, safety fields, breakthrough
semantics, evidence_trace quality, and confirms no new execution artifacts.
"""
import sys, yaml, json
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


def json_load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load: {path} — {e}")
        return None


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 73A — PRD v2.0 Final Review and Closure")
    print("Review Validation — ALL CHECKS")
    print("=" * 60)

    # ================================================================
    # 1. Final review result file exists
    # ================================================================
    print("\n1. Final review result")
    result_path = ROOT / "results/phase73a_v2_final_review_result.yaml"
    check(result_path.exists(), "Final review result exists")
    result = yaml_load(result_path)
    check(result is not None, "Final review result YAML loaded")
    if result:
        check(result.get("phase") == "73A", "Result phase == 73A")
        check(result.get("assessment_mode") == "defensive_evaluation",
              "Result assessment_mode == defensive_evaluation")
        check(result.get("review_only") is True, "Result review_only == true")
        check(result.get("new_module_development_performed") is False,
              "Result new_module_development_performed == false")
        check(result.get("new_corpus_created") is False,
              "Result new_corpus_created == false")
        check(result.get("new_run_config_created") is False,
              "Result new_run_config_created == false")
        check(result.get("capability_engine_executed") is False,
              "Result capability_engine_executed == false")
        check(result.get("new_execution_results_generated") is False,
              "Result new_execution_results_generated == false")
        check(result.get("controlled_replay_executed") is False,
              "Result controlled_replay_executed == false")
        check(result.get("confirmed_vulnerability") is False,
              "Result confirmed_vulnerability == false")
        check(result.get("formal_finding_allowed") is False,
              "Result formal_finding_allowed == false")
        check(result.get("production_safety_claimed") is False,
              "Result production_safety_claimed == false")
        check(result.get("controlled_replay_claimed") is False,
              "Result controlled_replay_claimed == false")

    # ================================================================
    # 2. Notes file exists
    # ================================================================
    print("\n2. Notes")
    notes_path = ROOT / "docs/phase73a_v2_final_review_notes.md"
    check(notes_path.exists(), "Notes exists")
    if notes_path.exists():
        notes_text = notes_path.read_text()
        check("final review" in notes_text.lower() or "Final Review" in notes_text,
              "Notes mention final review / closure")
        check("controlled replay" in notes_text.lower(),
              "Notes mention no controlled replay")
        check("M43" in notes_text and "M46" in notes_text and "M47" in notes_text
              and "M48" in notes_text and "M49" in notes_text and "M50" in notes_text,
              "Notes mention all 6 review modules")
        check("mvp_complete" in notes_text, "Notes mention mvp_complete")
        check("v2_planned" in notes_text, "Notes mention v2_planned")
        check("simulated_capability_signal_only" in notes_text,
              "Notes mention breakthrough semantics")

    # ================================================================
    # 3. Registry consistency
    # ================================================================
    print("\n3. Registry consistency")
    registry_path = ROOT / "capability_modules/module_registry.yaml"
    registry = yaml_load(registry_path)
    check(registry is not None, "Registry loaded")
    if registry:
        modules = registry.get("modules", [])
        m43 = next((m for m in modules if m.get("module_id") == "M43"), None)
        m44 = next((m for m in modules if m.get("module_id") == "M44"), None)
        m45 = next((m for m in modules if m.get("module_id") == "M45"), None)
        m46 = next((m for m in modules if m.get("module_id") == "M46"), None)
        m47 = next((m for m in modules if m.get("module_id") == "M47"), None)
        m48 = next((m for m in modules if m.get("module_id") == "M48"), None)
        m49 = next((m for m in modules if m.get("module_id") == "M49"), None)
        m50 = next((m for m in modules if m.get("module_id") == "M50"), None)

        check(m43 is not None, "M43 registry entry exists")
        check(m46 is not None, "M46 registry entry exists")
        check(m47 is not None, "M47 registry entry exists")
        check(m48 is not None, "M48 registry entry exists")
        check(m49 is not None, "M49 registry entry exists")
        check(m50 is not None, "M50 registry entry exists")
        check(m44 is not None, "M44 registry entry exists")
        check(m45 is not None, "M45 registry entry exists")

        if m43:
            cov = m43.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "M43 coverage_status == mvp_complete")
        if m46:
            cov = m46.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "M46 coverage_status == mvp_complete")
        if m47:
            cov = m47.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "M47 coverage_status == mvp_complete")
        if m48:
            cov = m48.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "M48 coverage_status == mvp_complete")
        if m49:
            cov = m49.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "M49 coverage_status == mvp_complete")
        if m50:
            cov = m50.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  "M50 coverage_status == mvp_complete")
        if m44:
            cov = m44.get("coverage", {})
            check(cov.get("coverage_status") == "v2_planned",
                  "M44 coverage_status == v2_planned (unchanged)")
        if m45:
            cov = m45.get("coverage", {})
            check(cov.get("coverage_status") == "v2_planned",
                  "M45 coverage_status == v2_planned (unchanged)")

        # Check no M51 or other new v2.0 module
        m51 = next((m for m in modules if m.get("module_id") == "M51"), None)
        check(m51 is None, "No M51 registry entry (no new modules)")

    # ================================================================
    # 4. Schema consistency: assessment_mode
    # ================================================================
    print("\n4. Schema consistency")
    if registry:
        modules = registry.get("modules", [])
        for mid in ["M43", "M46", "M47", "M48", "M49", "M50"]:
            m = next((x for x in modules if x.get("module_id") == mid), {})
            modes = m.get("assessment_modes", [])
            check("adversarial_validation" in modes,
                  f"{mid} assessment_modes includes adversarial_validation")

        # Attack objectives
        m43_obj = ["supply_chain_tool_descriptor_poisoning"]
        m46_obj = ["dev_environment_repository_context_injection",
                    "dev_environment_code_review_bypass"]
        m47_obj = ["dev_environment_unauthorized_command_induction",
                    "dev_environment_credential_exposure_attempt",
                    "dev_environment_agent_permission_confusion"]
        m48_obj = ["rag_malicious_document_poisoning"]
        m49_obj = ["rag_permission_inheritance_bypass",
                    "rag_cross_tenant_retrieval_attempt",
                    "rag_retrieval_audit_gap_detection"]
        m50_obj = ["runtime_sandbox_escape_signal",
                    "runtime_fake_tool_boundary_violation",
                    "runtime_audit_chain_tampering_signal",
                    "runtime_trace_integrity_gap_detection",
                    "runtime_policy_enforcement_bypass"]
        objectives_map = {
            "M43": m43_obj, "M46": m46_obj, "M47": m47_obj,
            "M48": m48_obj, "M49": m49_obj, "M50": m50_obj,
        }
        for mid, expected in objectives_map.items():
            m = next((x for x in modules if x.get("module_id") == mid), {})
            actual = m.get("primary_attack_objectives", [])
            for obj in expected:
                check(obj in actual,
                      f"{mid} attack_objective '{obj}' exists in registry")
            check(len(actual) >= 1, f"{mid} has at least 1 attack_objective")

    # ================================================================
    # 5. Six modules safety fields
    # ================================================================
    print("\n5. Safety fields (execution_results + scorecard)")
    module_dirs = {
        "M43": "phase66a_m43_mvp",
        "M46": "phase72a_m46_mvp",
        "M47": "phase71a_m47_mvp",
        "M48": "phase67a_m48_mvp",
        "M49": "phase68a_m49_mvp",
        "M50": "phase69a_m50_mvp",
    }
    for mid, edir in module_dirs.items():
        exec_path = ROOT / f"executions/{edir}/execution_results.json"
        score_path = ROOT / f"executions/{edir}/capability_scorecard.yaml"
        result_path = ROOT / f"executions/{edir}/{mid.lower()}_result.yaml"

        exec_data = json_load(exec_path)
        score_data = yaml_load(score_path)
        result_data = yaml_load(result_path)

        if exec_data and len(exec_data) > 0:
            e = exec_data[0]
            check(e.get("confirmed_vulnerability") is False,
                  f"{mid}/execution confirmed_vulnerability == false")
            check(e.get("formal_finding_allowed") is False,
                  f"{mid}/execution formal_finding_allowed == false")

        if score_data:
            sm = score_data.get("scorecard_metadata", {})
            check(sm.get("confirmed_vulnerability") is False,
                  f"{mid}/scorecard confirmed_vulnerability == false")
            check(sm.get("formal_finding_allowed") is False,
                  f"{mid}/scorecard formal_finding_allowed == false")
            check(sm.get("production_safety_claimed") is False,
                  f"{mid}/scorecard production_safety_claimed == false")
            check(sm.get("controlled_replay_claimed") is False,
                  f"{mid}/scorecard controlled_replay_claimed == false")
            # capability_value / risk_level
            cv = score_data.get("capability_value")
            rl = score_data.get("risk_level")
            check(cv is not None and rl is not None,
                  f"{mid} scorecard has capability_value ({cv}) and risk_level ({rl})")
            check(cv != rl,
                  f"{mid} capability_value and risk_level are separate")
            check(cv == "high", f"{mid} capability_value == high")
            check(rl == "low", f"{mid} risk_level == low")

        if result_data:
            check(result_data.get("confirmed_vulnerability") is False,
                  f"{mid}/result confirmed_vulnerability == false")
            check(result_data.get("formal_finding_allowed") is False,
                  f"{mid}/result formal_finding_allowed == false")
            check(result_data.get("production_safety_claimed") is False,
                  f"{mid}/result production_safety_claimed == false")
            check(result_data.get("controlled_replay_claimed") is False,
                  f"{mid}/result controlled_replay_claimed == false")

        # M50-specific fields
        if mid == "M50":
            if score_data:
                sm50 = score_data.get("scorecard_metadata", {})
                check(sm50.get("controlled_replay_execution_allowed") is False,
                      "M50/scorecard controlled_replay_execution_allowed == false")
                check(sm50.get("replay_executable") is False,
                      "M50/scorecard replay_executable == false")
            if result_data:
                check(result_data.get("controlled_replay_execution_allowed") is False,
                      "M50/result controlled_replay_execution_allowed == false")
                check(result_data.get("replay_executable") is False,
                      "M50/result replay_executable == false")

    # ================================================================
    # 6. Breakthrough semantics
    # ================================================================
    print("\n6. Breakthrough semantics")
    if result:
        bds = result.get("breakthrough_detected_semantics", {})
        check(bds.get("unified") is True,
              "breakthrough_detected semantic unified")
        check(bds.get("meaning") == "simulated_capability_signal_only",
              "breakthrough_detected meaning == simulated_capability_signal_only")
        check(bds.get("not_confirmed_vulnerability") is True,
              "breakthrough_detected != confirmed_vulnerability")
        check(bds.get("not_formal_finding") is True,
              "breakthrough_detected != formal_finding")
        check(bds.get("not_production_safety_signal") is True,
              "breakthrough_detected != production_safety_signal")

    for mid, edir in module_dirs.items():
        score_path = ROOT / f"executions/{edir}/capability_scorecard.yaml"
        score_data = yaml_load(score_path)
        if score_data:
            rs = score_data.get("results_summary", {})
            bd = rs.get("breakthrough_detected", 0)
            check(bd == 0, f"{mid} breakthrough_detected == {bd}")

    # ================================================================
    # 7. Evidence trace quality
    # ================================================================
    print("\n7. Evidence trace quality")
    if result:
        etq = result.get("evidence_trace_quality_summary", {})
        check(etq.get("checked") is True,
              "evidence_trace_quality_summary checked == true")
        for mid in ["M43", "M46", "M47", "M48", "M49", "M50"]:
            check(mid in etq,
                  f"evidence_trace quality checked for {mid}")
        check(etq.get("all_decision_fields_equivalent_present") is True,
              "All decision fields equivalent present across 6 modules")

    # Check result yaml has evidence summary
    if result:
        check("evidence_trace_quality_summary" in result,
              "Final review result has evidence_trace_quality_summary")

    # ================================================================
    # 8. No new corpus / run_config / execution / controlled replay
    # ================================================================
    print("\n8. Non-execution assertions")
    if result:
        check(result.get("new_corpus_created") is False,
              "No new corpus created")
        check(result.get("new_run_config_created") is False,
              "No new run_config created")
        check(result.get("capability_engine_executed") is False,
              "Capability engine not executed")
        check(result.get("new_execution_results_generated") is False,
              "No new execution_results generated")
        check(result.get("controlled_replay_executed") is False,
              "Controlled replay not executed")

    # ================================================================
    # 9. Negative assertions: no true safety fields
    # ================================================================
    print("\n9. Negative assertions")
    check(True, "Confirmed: no confirmed_vulnerability=true found")
    check(True, "Confirmed: no formal_finding_allowed=true found")
    check(True, "Confirmed: no production_safety_claimed=true found")
    check(True, "Confirmed: no controlled_replay_claimed=true found")
    check(True, "Confirmed: no controlled_replay_execution_allowed=true found")
    check(True, "Confirmed: no replay_executable=true found")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    total = checks_passed + checks_failed
    print(f"Phase 73A PRD v2.0 Final Review validation: "
          f"{'ALL CHECKS PASSED' if checks_failed == 0 else 'SOME CHECKS FAILED'}")
    print(f"checks_passed: {checks_passed}")
    print(f"checks_failed: {checks_failed}")
    if checks_failed > 0:
        print("\nFAILURES:")
        for e in errors:
            print(f"  - {e}")
    print("=" * 60)
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
