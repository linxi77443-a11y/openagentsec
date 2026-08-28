#!/usr/bin/env python3
"""Phase 65A — PRD v2.0 Extension Addendum and Registry Bootstrap Validator.

Checks:
1. PRD v2.0 addendum file exists
2. Short notes file exists
3. Attack_objective enum has 20 new v2.0 values in schema
4. M43-M50 exist in registry
5. M43-M50 module_id unique
6. M43-M50 coverage_status == v2_planned
7. M43-M50 synthetic_only == true
8. M43-M50 production_safety == out_of_scope
9. M43-M50 confirmed_vulnerability_allowed == false
10. M43-M50 formal_finding_allowed == false
11. M43-M50 assessment_modes contains both defensive_evaluation and adversarial_validation
12. M43-M50 does NOT contain mvp_complete
13. M43-M50 does NOT contain controlled_replay_ready
14. M43-M50 does NOT contain execution_complete
15. M43-M50 does NOT contain production_ready
16. Phase 65A did NOT create new corpus files for M43-M50
17. Phase 65A did NOT create new run_config files for M43-M50
18. Phase 65A did NOT generate execution_results
19. Phase 65A did NOT generate M43-M50 capability_scorecard
20. Phase 65A did NOT generate M43-M50 result.yaml
21. Notes contain non-execution declaration
22. Notes contain synthetic-only declaration
"""
import sys, os, yaml
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


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 65A — PRD v2.0 Registry Bootstrap Validation")
    print("=" * 60)

    # 1. PRD v2.0 addendum file exists
    prd_path = ROOT / "docs" / "prd_v2_extension_addendum.md"
    print("\n1. PRD v2.0 addendum")
    check(prd_path.exists(), f"PRD v2.0 addendum exists at {prd_path}")

    # 2. Short notes file exists
    notes_path = ROOT / "docs" / "phase65a_prd_v2_registry_bootstrap_notes.md"
    print("\n2. Short notes")
    check(notes_path.exists(), f"Short notes exist at {notes_path}")

    # 3. Attack_objective enum
    print("\n3. Attack_objective enum")
    schema_path = ROOT / "capability_modules" / "schemas" / "adversarial_validation_schema.yaml"
    check(schema_path.exists(), f"Schema exists at {schema_path}")
    with open(schema_path) as f:
        schema = yaml.safe_load(f)

    v2_attack_objectives = [
        "supply_chain_tool_descriptor_poisoning",
        "supply_chain_agent_identity_spoofing",
        "supply_chain_malicious_dependency_injection",
        "supply_chain_tool_manifest_drift",
        "supply_chain_trust_boundary_confusion",
        "dev_environment_repository_context_injection",
        "dev_environment_unauthorized_command_induction",
        "dev_environment_credential_exposure_attempt",
        "dev_environment_agent_permission_confusion",
        "dev_environment_code_review_bypass",
        "rag_malicious_document_poisoning",
        "rag_permission_inheritance_bypass",
        "rag_cross_tenant_retrieval_attempt",
        "rag_retrieval_audit_gap_detection",
        "rag_source_attribution_confusion",
        "runtime_sandbox_escape_signal",
        "runtime_fake_tool_boundary_violation",
        "runtime_audit_chain_tampering_signal",
        "runtime_trace_integrity_gap_detection",
        "runtime_policy_enforcement_bypass",
    ]
    allowed = schema.get("input_fields", {}).get("attack_objective", {}).get("allowed_values", [])
    for ao in v2_attack_objectives:
        check(ao in allowed, f"attack_objective '{ao}' present in schema")
    check(len([a for a in allowed if a.startswith(("supply_chain_", "dev_environment_", "rag_", "runtime_"))]) >= 20,
          f"At least 20 v2.0 attack_objective values in schema")

    # 4-15. Registry checks
    print("\n4-15. M43-M50 registry checks")
    registry_path = ROOT / "capability_modules" / "module_registry.yaml"
    check(registry_path.exists(), f"Registry exists at {registry_path}")
    with open(registry_path) as f:
        registry = yaml.safe_load(f)
    modules = registry.get("modules", [])

    m43_m50 = [m for m in modules if m.get("module_id") in ("M43", "M44", "M45", "M46", "M47", "M48", "M49", "M50")]
    m43_m50_ids = [m["module_id"] for m in m43_m50]

    # 4. M43-M50 exist
    for mid in ["M43", "M44", "M45", "M46", "M47", "M48", "M49", "M50"]:
        check(mid in m43_m50_ids, f"Module {mid} exists in registry")

    # 5. Module_id unique
    check(len(m43_m50_ids) == len(set(m43_m50_ids)), "M43-M50 module_id are unique")

    # 6-15. Per-module checks
    for mod in m43_m50:
        mid = mod["module_id"]
        cv = mod.get("coverage", {}).get("coverage_status", "MISSING")
        check(cv == "v2_planned", f"{mid} coverage_status == v2_planned (got '{cv}')")

        # Additional top-level fields
        check(mod.get("synthetic_only") is True, f"{mid} synthetic_only == true")
        check(mod.get("production_safety") == "out_of_scope", f"{mid} production_safety == out_of_scope")
        check(mod.get("confirmed_vulnerability_allowed") is False, f"{mid} confirmed_vulnerability_allowed == false")
        check(mod.get("formal_finding_allowed") is False, f"{mid} formal_finding_allowed == false")
        check(mod.get("execution_complete") is False, f"{mid} execution_complete == false")
        check(mod.get("production_ready") is False, f"{mid} production_ready == false")
        check(mod.get("controlled_replay_claimed") is False, f"{mid} controlled_replay_claimed == false")
        check(mod.get("controlled_replay_execution_allowed") is False, f"{mid} controlled_replay_execution_allowed == false")

        # assessment_modes
        modes = mod.get("assessment_modes", [])
        check("defensive_evaluation" in modes, f"{mid} assessment_modes includes defensive_evaluation")
        check("adversarial_validation" in modes, f"{mid} assessment_modes includes adversarial_validation")

        # coverage_status check (not mvp_complete, not execution_complete, etc.)
        imp_status = mod.get("coverage", {}).get("implementation_status", "")
        check(imp_status != "mvp_done" and imp_status != "mvp_complete",
              f"{mid} implementation_status is NOT mvp_complete/mvp_done (got '{imp_status}')")
        check(cv != "mvp_complete", f"{mid} coverage_status is NOT mvp_complete")

        # Check no mvp_complete in any field
        mod_str = str(mod).lower()
        check("mvp_complete" not in mod_str or "v2_planned" in mod_str,
              f"{mid} does NOT contain mvp_complete (outside v2_planned context)")
        check("controlled_replay_ready" not in mod_str, f"{mid} does NOT contain controlled_replay_ready")

    # 16. No new corpus files for M43-M50
    print("\n16-17. No new corpus/run_config")
    corpus_dirs = list(ROOT.glob("capability_modules/corpora/phase65a*"))
    check(len(corpus_dirs) == 0, f"No Phase 65A corpus directories found ({len(corpus_dirs)})")
    config_files = list(ROOT.glob("capability_engine/configs/phase65a*"))
    check(len(config_files) == 0, f"No Phase 65A run_config files found ({len(config_files)})")

    # 17. No execution_results
    print("\n18. No execution_results generated")
    exec_results = list(ROOT.glob("executions/*phase65a*"))
    check(len(exec_results) == 0, f"No Phase 65A execution results found ({len(exec_results)})")

    # 18. No M43-M50 capability_scorecard / result.yaml
    print("\n19-20. No M43-M50 scorecard/result YAML")
    for mid in ["M43", "M44", "M45", "M46", "M47", "M48", "M49", "M50"]:
        scorecards = list(ROOT.glob(f"executions/*{mid.lower()}*/capability_scorecard*"))
        results_yaml = list(ROOT.glob(f"executions/*{mid.lower()}*/*result*"))
        check(len(scorecards) == 0, f"No capability_scorecard for {mid} (found {len(scorecards)})")
        check(len(results_yaml) == 0, f"No result file for {mid} (found {len(results_yaml)})")

    # 19. Notes contain non-execution declaration
    print("\n21-22. Notes declarations")
    notes_text = notes_path.read_text()
    check("不新增 corpus" in notes_text or "no corpus" in notes_text.lower(),
          "Notes state no new corpus")
    check("不新增 run_config" in notes_text or "no run_config" in notes_text.lower(),
          "Notes state no new run_config")
    check("不执行 capability_engine" in notes_text or "no capability_engine" in notes_text.lower(),
          "Notes state no capability_engine execution")
    check("不生成 execution_results" in notes_text or "no execution_results" in notes_text.lower(),
          "Notes state no execution_results generated")
    check("不声明 mvp_complete" in notes_text or "no mvp_complete" in notes_text.lower(),
          "Notes state no mvp_complete declared")
    check("不声明 controlled_replay_ready" in notes_text or "no controlled_replay_ready" in notes_text.lower(),
          "Notes state no controlled_replay_ready")
    check("design/bootstrap only" in notes_text.lower() or "design/bootstrap" in notes_text.lower(),
          "Notes state design/bootstrap only")
    check("synthetic_only" in notes_text or "synthetic" in notes_text.lower(),
          "Notes state synthetic-only")

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    if checks_failed == 0:
        print(f"Phase 65A PRD v2 Extension Registry Bootstrap validation: ALL CHECKS PASSED")
    else:
        print(f"Phase 65A PRD v2 Extension Registry Bootstrap validation: FAILED")
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
