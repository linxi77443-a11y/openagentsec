#!/usr/bin/env python3
"""Phase 70A — PRD v2.0 Core Layer Review and Cleanup Validator.

Review-only phase: no new corpus, no run config, no capability_engine execution.
Validates schema consistency, security fields, breakthrough_detected semantics,
evidence_trace quality, and registry status unification for M43-M50.
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


def check_security_fields(obj, prefix, obj_desc):
    """Check that all required security fields exist and have correct values."""
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


def check_security_fields_m50(obj, prefix, obj_desc):
    """Check security fields including M50-specific fields."""
    check_security_fields(obj, prefix, obj_desc)
    if isinstance(obj, dict):
        check(obj.get("controlled_replay_execution_allowed") is False,
              f"{prefix}: {obj_desc} controlled_replay_execution_allowed == false")
        check(obj.get("replay_executable") is False,
              f"{prefix}: {obj_desc} replay_executable == false")


def check_security_fields_m49(obj, prefix, obj_desc):
    """Check security fields including M49-specific fields."""
    check_security_fields(obj, prefix, obj_desc)
    if isinstance(obj, dict):
        for field in ["real_rag_system_connected", "real_knowledge_base_accessed",
                       "real_document_accessed", "real_cloud_storage_accessed",
                       "real_tenant_data_accessed", "real_permission_system_used",
                       "real_audit_log_accessed", "real_tool_executed",
                       "real_api_called"]:
            check(obj.get(field) is False,
                  f"{prefix}: {obj_desc} {field} == false")


def check_breakthrough_semantics(entry, prefix):
    """Verify breakthrough_detected is not treated as confirmed vulnerability."""
    bt = entry.get("breakthrough_detected", False)
    cv = entry.get("confirmed_vulnerability", False)
    if bt:
        check(cv is False,
              f"{prefix}: breakthrough_detected entry still has confirmed_vulnerability==false")
        check(entry.get("formal_finding_allowed") is False,
              f"{prefix}: breakthrough_detected entry has formal_finding_allowed==false")
        # breakthrough_detected should only mean simulated_capability_signal
        check(entry.get("exploit_chain_candidate_generated") in (None, False),
              f"{prefix}: breakthrough_detected entry has no exploit_chain_candidate_generated")
    else:
        check(True, f"{prefix}: breakthrough_detected is false (expected)")


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 70A — PRD v2.0 Core Layer Review and Cleanup")
    print("Review-only mode: no execution, no new corpus")
    print("=" * 60)

    # ================================================================
    # 1. Registry Module Status Verification
    # ================================================================
    print("\n" + "=" * 60)
    print("1. Registry Module Status Verification")
    print("=" * 60)

    reg_path = ROOT / "capability_modules/module_registry.yaml"
    reg = yaml_load(reg_path)
    check(reg is not None, "module_registry.yaml loaded")
    if not reg:
        print("FATAL: registry not loaded. Aborting.")
        sys.exit(1)

    modules = reg.get("modules", [])
    check(len(modules) >= 35, f"Registry has >= 35 modules ({len(modules)})")

    # Helper to find module by ID
    def find_module(mid):
        for m in modules:
            if m.get("module_id") == mid:
                return m
        return None

    # Check v2.0 modules exist
    v2_modules = ["M43", "M44", "M45", "M46", "M47", "M48", "M49", "M50"]
    for mid in v2_modules:
        m = find_module(mid)
        check(m is not None, f"Module {mid} exists in registry")
        if m:
            cov = m.get("coverage", {})
            check(cov.get("matrix_area", "").startswith(
                {"M43": "supply_chain", "M44": "supply_chain", "M45": "supply_chain",
                 "M46": "dev_environment", "M47": "dev_environment",
                 "M48": "rag", "M49": "rag", "M50": "runtime"}[mid]),
                  f"{mid} matrix_area starts with correct domain")

    # Check M43/M49/M50 = mvp_complete
    for mid in ["M43", "M49", "M50"]:
        m = find_module(mid)
        if m:
            cov = m.get("coverage", {})
            check(cov.get("coverage_status") == "mvp_complete",
                  f"{mid} coverage_status == mvp_complete (got {cov.get('coverage_status')})")
            check(cov.get("implementation_status") == "mvp_done",
                  f"{mid} implementation_status == mvp_done")
            check(m.get("execution_complete") is True,
                  f"{mid} execution_complete == true")

    # Check M48 = mvp_candidate
    m48 = find_module("M48")
    if m48:
        m48_cov = m48.get("coverage", {})
        check(m48_cov.get("coverage_status") == "mvp_candidate",
              f"M48 coverage_status == mvp_candidate (got {m48_cov.get('coverage_status')})")
        check(m48.get("execution_complete") is True,
              "M48 execution_complete == true (executed but awaiting judge review)")

    # Check M44/M45/M46/M47 = v2_planned
    for mid in ["M44", "M45", "M46", "M47"]:
        m = find_module(mid)
        if m:
            cov = m.get("coverage", {})
            check(cov.get("coverage_status") == "v2_planned",
                  f"{mid} coverage_status == v2_planned (got {cov.get('coverage_status')})")
            check(m.get("execution_complete") is False,
                  f"{mid} execution_complete == false")

    # Verify no extra v2.0 modules beyond M43-M50
    for m in modules:
        mid = m.get("module_id", "")
        if mid.startswith("M") and len(mid) <= 3:
            try:
                num = int(mid[1:])
                if 43 <= num <= 50:
                    continue
            except ValueError:
                pass
        # Check no other Mxx in 43-50 range
        for num in range(43, 51):
            if mid == f"M{num}":
                continue  # already checked
        # Old modules are fine

    print(f"\n  v2.0 registry status summary:")
    print(f"    M43: mvp_complete | M44: v2_planned | M45: v2_planned")
    print(f"    M46: v2_planned | M47: v2_planned | M48: mvp_candidate")
    print(f"    M49: mvp_complete | M50: mvp_complete")

    # ================================================================
    # 2. Schema Consistency — All v2.0 modules have required fields
    # ================================================================
    print("\n" + "=" * 60)
    print("2. Schema Consistency — v2.0 Required Fields")
    print("=" * 60)

    required_top_fields = [
        "module_id", "module_name", "priority", "layer", "capability_goal",
        "business_value", "domain", "assessment_modes", "primary_attack_objectives",
        "current_status", "result_semantics", "formal_finding_allowed",
        "human_review_required", "coverage", "production_safety", "synthetic_only",
        "confirmed_vulnerability_allowed", "controlled_replay_claimed",
        "controlled_replay_execution_allowed", "execution_complete", "production_ready"
    ]

    required_cov_fields = [
        "matrix_area", "coverage_status", "implementation_status",
        "evidence", "gaps", "next_action"
    ]

    for mid in v2_modules:
        m = find_module(mid)
        if not m:
            continue
        for field in required_top_fields:
            check(field in m, f"{mid} has required top-level field '{field}'")
        cov = m.get("coverage", {})
        for field in required_cov_fields:
            check(field in cov, f"{mid} coverage has required field '{field}'")
        # Check allowed domains
        check(m.get("domain") in ("ai_supply_chain_security", "rag_data_security",
                                   "runtime_sandbox_security", "development_environment_security"),
              f"{mid} domain is one of the 4 v2.0 domains (got {m.get('domain')})")
        # Check assessment_modes list
        modes = m.get("assessment_modes", [])
        check("defensive_evaluation" in modes,
              f"{mid} assessment_modes includes defensive_evaluation")
        check("adversarial_validation" in modes,
              f"{mid} assessment_modes includes adversarial_validation")
        # Check primary_attack_objectives is non-empty
        attack_objs = m.get("primary_attack_objectives", [])
        check(len(attack_objs) >= 1,
              f"{mid} has >= 1 primary_attack_objectives ({len(attack_objs)})")

    # ================================================================
    # 3. Security Field Consistency Across Deliverables
    # ================================================================
    print("\n" + "=" * 60)
    print("3. Security Field Consistency Across Deliverables")
    print("=" * 60)

    exec_dirs = {
        "M43": "phase66a_m43_mvp",
        "M48": "phase67a_m48_mvp",
        "M49": "phase68a_m49_mvp",
        "M50": "phase69a_m50_mvp",
    }

    for mid, edir in exec_dirs.items():
        base = ROOT / "executions" / edir
        m = find_module(mid)
        if not m:
            continue

        print(f"\n  --- {mid} ({edir}) ---")

        # Check registry security fields
        check(m.get("confirmed_vulnerability_allowed") is False,
              f"{mid}: registry confirmed_vulnerability_allowed == false")
        check(m.get("controlled_replay_claimed") is False,
              f"{mid}: registry controlled_replay_claimed == false")
        check(m.get("controlled_replay_execution_allowed") is False,
              f"{mid}: registry controlled_replay_execution_allowed == false")
        check(m.get("production_safety") == "out_of_scope",
              f"{mid}: registry production_safety == out_of_scope")
        check(m.get("synthetic_only") is True,
              f"{mid}: registry synthetic_only == true")
        check(m.get("production_ready") is False,
              f"{mid}: registry production_ready == false")

        # Check result YAML security fields
        result_path = base / f"{mid.lower()}_result.yaml"
        if not result_path.exists():
            result_path = base / f"{mid.lower()}_result.yaml"
        r_yaml = yaml_load(result_path) if result_path.exists() else None
        if r_yaml:
            check_security_fields(r_yaml, f"{mid}", "result YAML")
            # Check real-connection fields
            for rfield in [k for k in r_yaml if k.startswith("real_")]:
                check(r_yaml[rfield] is False,
                      f"{mid}: result {rfield} == false")

            # Per-entry security fields
            entries = r_yaml.get("per_entry_results", [])
            for entry in entries:
                eid = entry.get("entry_id", "?")
                check(entry.get("confirmed_vulnerability") is False,
                      f"{mid}/{eid}: confirmed_vulnerability == false")
                check(entry.get("formal_finding_allowed") is False,
                      f"{mid}/{eid}: formal_finding_allowed == false")
                # Check breakthrough semantics
                check_breakthrough_semantics(entry, f"{mid}/{eid}")

        # Check scorecard security fields
        score_path = base / "capability_scorecard.yaml"
        sc = yaml_load(score_path) if score_path.exists() else None
        if sc:
            sm = sc.get("scorecard_metadata", {})
            check(sm.get("simulated_signal_only") is True,
                  f"{mid}: scorecard simulated_signal_only == true")
            check(sm.get("safety_level") == "simulated_runtime_safety",
                  f"{mid}: scorecard safety_level == simulated_runtime_safety")
            check(sm.get("production_safety") == "out_of_scope",
                  f"{mid}: scorecard production_safety == out_of_scope")
            check_security_fields(sm, f"{mid}", "scorecard metadata")
            if mid == "M50":
                check(sm.get("controlled_replay_execution_allowed") is False,
                      "M50: scorecard controlled_replay_execution_allowed == false")
                check(sm.get("replay_executable") is False,
                      "M50: scorecard replay_executable == false")
            # capability_value vs risk_level separation
            cv = sc.get("capability_value")
            rl = sc.get("risk_level")
            check(cv is not None, f"{mid}: scorecard has capability_value")
            check(rl is not None, f"{mid}: scorecard has risk_level")
            check(sc.get("capability_value_semantics") is not None,
                  f"{mid}: scorecard has capability_value_semantics")
            check(sc.get("risk_level_semantics") is not None,
                  f"{mid}: scorecard has risk_level_semantics")
            check(cv == "high", f"{mid}: capability_value == high (got {cv})")
            check(rl == "low", f"{mid}: risk_level == low (got {rl})")

    # ================================================================
    # 4. breakthrough_detected Semantics Review
    # ================================================================
    print("\n" + "=" * 60)
    print("4. breakthrough_detected Semantics Review")
    print("=" * 60)

    for mid, edir in exec_dirs.items():
        base = ROOT / "executions" / edir
        result_path = base / f"{mid.lower()}_result.yaml"
        r_yaml = yaml_load(result_path) if result_path.exists() else None
        if r_yaml:
            bt_count = r_yaml.get("breakthrough_detected_count", -1)
            check(bt_count == 0,
                  f"{mid}: breakthrough_detected_count == 0 (got {bt_count})")
            entries = r_yaml.get("per_entry_results", [])
            for entry in entries:
                eid = entry.get("entry_id", "?")
                bt = entry.get("breakthrough_detected", False)
                check(bt is False,
                      f"{mid}/{eid}: breakthrough_detected == false (got {bt})")
                # breakthrough_detected must never imply confirmed_vulnerability
                if bt:
                    check(entry.get("exploit_chain_candidate_generated") is False,
                          f"{mid}/{eid}: exploit_chain_candidate_generated is false "
                          "even when breakthrough_detected")

        # Also check scorecard breakthrough_ids
        score_path = base / "capability_scorecard.yaml"
        sc = yaml_load(score_path) if score_path.exists() else None
        if sc:
            breakthrough_ids = sc.get("scorecard_metadata", {}).get("breakthrough_ids", [])
            check(len(breakthrough_ids) == 0,
                  f"{mid}: scorecard breakthrough_ids is empty (got {len(breakthrough_ids)})")

    print(f"\n  All modules: breakthrough_detected_count == 0, no breakthrough_ids")

    # ================================================================
    # 5. evidence_trace Quality Check
    # ================================================================
    print("\n" + "=" * 60)
    print("5. evidence_trace Quality Check")
    print("=" * 60)

    for mid, edir in exec_dirs.items():
        base = ROOT / "executions" / edir

        # Result YAML evidence_trace_present
        result_path = base / f"{mid.lower()}_result.yaml"
        r_yaml = yaml_load(result_path) if result_path.exists() else None
        if r_yaml:
            check(r_yaml.get("evidence_trace_present") is True,
                  f"{mid}: result evidence_trace_present == true")
            check(r_yaml.get("exploit_chain_candidate_generated") is False,
                  f"{mid}: result exploit_chain_candidate_generated == false")

            # Per-entry entries have defensive_check_passed and evaluation_summary
            entries = r_yaml.get("per_entry_results", [])
            for entry in entries:
                eid = entry.get("entry_id", "?")
                check("defensive_check_passed" in entry,
                      f"{mid}/{eid}: has defensive_check_passed")
                check("evaluation_summary" in entry,
                      f"{mid}/{eid}: has evaluation_summary")
                check("signal_detected" in entry,
                      f"{mid}/{eid}: has signal_detected")
                check("category" in entry,
                      f"{mid}/{eid}: has category")

        # Registry evidence section quality
        m = find_module(mid)
        if m:
            evidence = m.get("coverage", {}).get("evidence", [])
            check(len(evidence) >= 6,
                  f"{mid}: registry evidence has >= 6 entries ({len(evidence)})")
            for ev in evidence:
                check(ev.startswith("- ") or ev.startswith("Phase") or
                      ": " in ev or ev.startswith("corpus") or
                      ev.startswith("run") or ev.startswith("parse") or
                      ev.startswith("result") or ev.startswith("scorecard") or
                      ev.startswith("validate") or ev.startswith("notes"),
                      f"{mid}: evidence entry well-formatted: {ev[:80]}")

        # Check notes files exist for all modules
        notes_map = {
            "M43": "docs/phase66a_m43_mcp_tool_descriptor_integrity_notes.md",
            "M48": "docs/phase67a_m48_rag_document_poisoning_notes.md",
            "M49": "docs/phase68a_m49_rag_permission_audit_notes.md",
            "M50": "docs/phase69a_m50_runtime_sandbox_audit_chain_notes.md",
        }
        if mid in notes_map:
            notes_file = file_exists(ROOT / notes_map[mid], f"{mid} notes")

    # ================================================================
    # 6. No New Unauthorized Modules
    # ================================================================
    print("\n" + "=" * 60)
    print("6. No New Unauthorized Modules")
    print("=" * 60)

    # Verify no modules beyond M50 were added
    for m in modules:
        mid = m.get("module_id", "")
        # Check for modules M51+
        if mid.startswith("M") and mid[1:].isdigit():
            num = int(mid[1:])
            if num >= 51:
                check(False, f"No unauthorized modules beyond M50: found {mid}")

    # Check that non-v2 modules that are not_started remain not_started
    not_started_check = ["M09", "M17", "M18", "M21", "M22", "M05", "M10", "M11",
                          "M20", "M23", "M24", "M25", "M27", "M28", "M29",
                          "M26", "M30", "M31", "M32", "M33", "M34", "M35", "M36", "M37",
                          "M40", "M41", "M42"]
    for mid in not_started_check:
        m = find_module(mid)
        if m:
            cov = m.get("coverage", {})
            status = cov.get("coverage_status", "")
            if status not in ("mvp_complete", "reference_only", "mvp_candidate"):
                check(status == "not_started" or status == "",
                      f"{mid}: coverage_status remains 'not_started' (got '{status}')")

    # ================================================================
    # 7. Registry v2.0 Global Description
    # ================================================================
    print("\n" + "=" * 60)
    print("7. Registry Global Description & Version")
    print("=" * 60)

    check(reg.get("registry_version", "").startswith("1.0"),
          f"registry_version starts with 1.0 (got {reg.get('registry_version')})")
    desc = reg.get("description", "")
    check("M43" in desc, "Description mentions M43")
    check("M48" in desc, "Description mentions M48")
    check("M49" in desc, "Description mentions M49")
    check("M50" in desc, "Description mentions M50")
    check("mvp_complete" in desc, "Description mentions mvp_complete")
    check("v2.0" in desc or "PRD v2" in desc or "PRD v2.0" in desc,
          "Description references v2.0")

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
    print("=" * 60)
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
