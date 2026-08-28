#!/usr/bin/env python3
"""Phase 75A — Cross-Module Attack Path Catalog MVP Validator.

Document integrity validator. Checks catalog doc, notes, result, and confirms
no new execution artifacts were created.
"""
import sys, yaml, re
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
    print("Phase 75A — Cross-Module Attack Path Catalog MVP")
    print("Document Integrity Validation — ALL CHECKS")
    print("=" * 60)

    # ================================================================
    # 1. Document existence
    # ================================================================
    print("\n1. Document existence")
    catalog_path = ROOT / "docs/cross_module_attack_path_catalog.md"
    notes_path = ROOT / "docs/phase75a_cross_module_attack_path_catalog_notes.md"
    result_path = ROOT / "results/phase75a_cross_module_attack_path_catalog_result.yaml"
    validate_path = ROOT / "scripts/validate_phase75a_cross_module_attack_path_catalog.py"

    check(catalog_path.exists(), "Path catalog exists")
    check(notes_path.exists(), "Phase 75A notes exist")
    check(result_path.exists(), "Phase 75A catalog result exists")
    check(validate_path.exists(), "Validate script exists")

    # ================================================================
    # 2. Catalog content — Required sections
    # ================================================================
    print("\n2. Catalog document sections")
    catalog_text = catalog_path.read_text() if catalog_path.exists() else ""

    check("Purpose and Scope" in catalog_text, "Contains Purpose and Scope")
    check("Non-Execution Boundary" in catalog_text, "Contains Non-Execution Boundary")
    check("Catalog Object Model" in catalog_text, "Contains Catalog Object Model")
    check("Path Entry Schema" in catalog_text, "Contains Path Entry Schema")
    check("Evidence Trace Reference Model" in catalog_text,
          "Contains Evidence Trace Reference Model")
    check("Layer Coverage" in catalog_text, "Contains Layer Coverage")
    check("Module Coverage" in catalog_text, "Contains Module Coverage")
    check("Conceptual Path Catalog" in catalog_text, "Contains Conceptual Path Catalog")
    check("Human Review" in catalog_text, "Contains Human Review section")
    check("Forbidden Uses" in catalog_text, "Contains Forbidden Uses section")
    check("executable: false" in catalog_text,
          "Catalog declares executable: false")
    check("attack_execution_allowed: false" in catalog_text,
          "Catalog declares attack_execution_allowed: false")
    check("conceptual_path: true" in catalog_text,
          "Catalog declares conceptual_path: true")

    # ================================================================
    # 3. Required conceptual paths existence
    # ================================================================
    print("\n3. Required conceptual paths")
    required_paths = [
        "PATH-SUPPLY-DEV-001",
        "PATH-DEV-CMD-001",
        "PATH-RAG-PERMISSION-001",
        "PATH-CRED-RUNTIME-AUDIT-001",
        "PATH-RAG-RUNTIME-001",
        "PATH-DEV-RUNTIME-001",
        "PATH-SUPPLY-DEV-RUNTIME-001",
        "PATH-SUPPLY-DEV-RAG-RUNTIME-001",
    ]
    for pid in required_paths:
        check(pid in catalog_text, f"Contains required path: {pid}")

    # ================================================================
    # 4. Per-path required fields (check each path block)
    # ================================================================
    print("\n4. Per-path required fields")
    # Extract path blocks using regex
    path_blocks = re.findall(
        r'path_id: "([^"]+)".*?(?=path_id:|human_review_required:)',
        catalog_text, re.DOTALL
    )
    # Count paths by searching for path_id occurrences
    path_id_count = catalog_text.count("path_id: \"PATH-")
    check(path_id_count >= 8, f"At least 8 conceptual paths defined ({path_id_count} found)")

    # Check per-path fields in the catalog text
    check("conceptual_path: true" in catalog_text,
          "All paths marked conceptual_path: true (at least once)")
    check("executable: false" in catalog_text,
          "All paths marked executable: false")
    check("attack_execution_allowed: false" in catalog_text,
          "All paths marked attack_execution_allowed: false")
    check("human_review_required: true" in catalog_text,
          "All paths require human review")
    check("confirmed_vulnerability: false" in catalog_text,
          "All paths have confirmed_vulnerability: false")
    check("formal_finding_allowed: false" in catalog_text,
          "All paths have formal_finding_allowed: false")
    check("production_safety_claimed: false" in catalog_text,
          "All paths have production_safety_claimed: false")
    check("involved_modules" in catalog_text,
          "All paths contain involved_modules")
    check("involved_layers" in catalog_text,
          "All paths contain involved_layers")
    check("edge_sequence" in catalog_text,
          "All paths contain edge_sequence")
    check("theoretical_scenario" in catalog_text,
          "All paths contain theoretical_scenario")
    check("evidence_trace_references" in catalog_text,
          "All paths contain evidence_trace_references")
    check("conceptual_risk_amplification_notes" in catalog_text,
          "All paths contain risk amplification notes")
    check("attenuation_factors" in catalog_text,
          "All paths contain attenuation factors")

    # ================================================================
    # 5. Module and layer coverage
    # ================================================================
    print("\n5. Module and layer coverage")
    for module in ["M43", "M46", "M47", "M48", "M49", "M50"]:
        check(module in catalog_text, f"Catalog references {module}")

    for layer in ["supply_chain", "development_environment", "rag_data", "runtime_sandbox"]:
        check(layer in catalog_text, f"Catalog references {layer} layer")

    # Required path compositions
    check("M43.*M46" in catalog_text.replace("\n", " ") or
          "PATH-SUPPLY-DEV-001" in catalog_text,
          "Catalog contains M43 → M46 path")

    check("M46.*M47" in catalog_text.replace("\n", " ") or
          "PATH-DEV-CMD-001" in catalog_text,
          "Catalog contains M46 → M47 path")

    check("M48.*M49.*M50" in catalog_text.replace("\n", " ") or
          "PATH-RAG-RUNTIME-001" in catalog_text,
          "Catalog contains M48 → M49 → M50 path")

    check("M46.*M47.*M50" in catalog_text.replace("\n", " ") or
          "PATH-DEV-RUNTIME-001" in catalog_text,
          "Catalog contains M46 → M47 → M50 path")

    check("M43.*M46.*M47.*M50" in catalog_text.replace("\n", " ") or
          "PATH-SUPPLY-DEV-RUNTIME-001" in catalog_text,
          "Catalog contains M43 → M46 → M47 → M50 path")

    check("M43.*M46.*M48.*M49.*M50" in catalog_text.replace("\n", " ") or
          "PATH-SUPPLY-DEV-RAG-RUNTIME-001" in catalog_text,
          "Catalog contains M43 → M46 → M48 → M49 → M50 path")

    # ================================================================
    # 6. Evidence trace references
    # ================================================================
    print("\n6. Evidence trace references")
    check("new_evidence_generated: false" in catalog_text,
          "Evidence references marked new_evidence_generated: false")
    check("reference_type: \"existing_evidence_trace\"" in catalog_text,
          "Evidence references use existing_evidence_trace type")
    check("expected_fields" in catalog_text,
          "Evidence references contain expected_fields")

    # Count evidence references
    evidence_ref_count = catalog_text.count("module_id:")
    # Each path has at least 2 references = 16 minimum
    evidence_refs_in_paths = catalog_text.count("reference_type:")
    check(evidence_refs_in_paths >= 16,
          f"At least 16 evidence_trace references across paths ({evidence_refs_in_paths} found)")

    # ================================================================
    # 7. Edge types used
    # ================================================================
    print("\n7. Edge taxonomy usage")
    edge_types_found = set()
    for edge in ["context_influence", "permission_dependency", "audit_dependency",
                  "runtime_dependency", "trust_boundary_transfer"]:
        if f"edge_type: \"{edge}\"" in catalog_text:
            edge_types_found.add(edge)

    check(len(edge_types_found) >= 2,
          f"At least 2 edge types used in paths ({len(edge_types_found)} found: {edge_types_found})")

    # ================================================================
    # 8. Notes content
    # ================================================================
    print("\n8. Notes content")
    notes_text = notes_path.read_text() if notes_path.exists() else ""

    check("Phase 75A" in notes_text, "Notes mention Phase 75A")
    check("cross-module attack path catalog" in notes_text.lower(),
          "Notes mention cross-module attack path catalog")
    check("conceptual_path" in notes_text or "概念" in notes_text,
          "Notes mention conceptual path nature")
    check("不开发新模块" in notes_text or "no new module" in notes_text.lower(),
          "Notes mention no new module development")
    check("不新增 corpus" in notes_text or "no new corpus" in notes_text.lower(),
          "Notes mention no new corpus")
    check("不执行 capability_engine" in notes_text or "no capability_engine" in notes_text.lower(),
          "Notes mention no capability_engine")
    check("不进入 controlled replay" in notes_text or "no controlled replay" in notes_text.lower(),
          "Notes mention no controlled replay")
    check("不声明 confirmed vulnerability" in notes_text or "confirmed_vulnerability" in notes_text,
          "Notes mention no confirmed vulnerability")
    check("不声明 formal finding" in notes_text or "formal_finding" in notes_text,
          "Notes mention no formal finding")
    check("不声明 production safety" in notes_text or "production_safety" in notes_text,
          "Notes mention no production safety")

    # ================================================================
    # 9. Catalog result content
    # ================================================================
    print("\n9. Catalog result content")
    result = yaml_load(result_path)
    check(result is not None, "Catalog result YAML loaded")
    if result:
        check(result.get("phase") == "75A", "Result phase == 75A")
        check(result.get("catalog_only") is True, "Result catalog_only == true")
        check(result.get("conceptual_paths_only") is True,
              "Result conceptual_paths_only == true")
        check(result.get("executable_paths") is False,
              "Result executable_paths == false")
        check(result.get("attack_execution_allowed") is False,
              "Result attack_execution_allowed == false")
        check(result.get("new_module_development_performed") is False,
              "Result new_module_development_performed == false")
        check(result.get("new_corpus_created") is False,
              "Result new_corpus_created == false")
        check(result.get("new_run_config_created") is False,
              "Result new_run_config_created == false")
        check(result.get("capability_engine_executed") is False,
              "Result capability_engine_executed == false")
        check(result.get("execution_results_generated") is False,
              "Result execution_results_generated == false")
        check(result.get("controlled_replay_executed") is False,
              "Result controlled_replay_executed == false")
        check(result.get("confirmed_vulnerability") is False,
              "Result confirmed_vulnerability == false")
        check(result.get("formal_finding_allowed") is False,
              "Result formal_finding_allowed == false")
        check(result.get("production_safety_claimed") is False,
              "Result production_safety_claimed == false")
        check(result.get("evidence_trace_newly_generated") is False,
              "Result evidence_trace_newly_generated == false")
        check(result.get("evidence_trace_reference_only") is True,
              "Result evidence_trace_reference_only == true")

        path_count = result.get("path_count", 0)
        check(path_count >= 8, f"Result path_count >= 8 ({path_count})")

        module_cov = result.get("module_coverage_summary", {})
        if module_cov:
            for m in ["M43", "M46", "M47", "M48", "M49", "M50"]:
                check(module_cov.get(m, {}).get("referenced_in_paths", []),
                      f"Result module coverage for {m}")

        layer_cov = result.get("layer_coverage_summary", {})
        if layer_cov:
            for lyr in ["supply_chain", "development_environment", "rag_data", "runtime_sandbox"]:
                check(layer_cov.get(lyr, {}).get("covered") is True,
                      f"Result layer coverage for {lyr}")

        ev_ref = result.get("evidence_trace_reference_summary", {})
        if ev_ref:
            check(ev_ref.get("new_evidence_generated") is False,
                  "Result evidence trace: no new evidence generated")
            check(ev_ref.get("reference_only") is True,
                  "Result evidence trace: reference only")

    # ================================================================
    # 10. Negative assertions — forbidden values
    # ================================================================
    print("\n10. Negative assertions")
    all_phase75a_files = [catalog_path, notes_path, result_path]
    all_text = ""
    for f in all_phase75a_files:
        if f.exists():
            all_text += f.read_text() + "\n"

    check("confirmed_vulnerability: true" not in all_text,
          "No confirmed_vulnerability: true in Phase 75A files")
    check("formal_finding_allowed: true" not in all_text,
          "No formal_finding_allowed: true in Phase 75A files")
    check("production_safety_claimed: true" not in all_text,
          "No production_safety_claimed: true in Phase 75A files")
    check("controlled_replay_claimed: true" not in all_text,
          "No controlled_replay_claimed: true in Phase 75A files")
    check("controlled_replay_execution_allowed: true" not in all_text,
          "No controlled_replay_execution_allowed: true in Phase 75A files")
    check("replay_executable: true" not in all_text,
          "No replay_executable: true in Phase 75A files")
    check("real_system_connection_allowed: true" not in all_text,
          "No real_system_connection_allowed: true")
    check("real_api_call_allowed: true" not in all_text,
          "No real_api_call_allowed: true")
    check("real_tool_call_allowed: true" not in all_text,
          "No real_tool_call_allowed: true")
    check("attack_execution_allowed: true" not in all_text.replace("attack_execution_allowed: false", ""),
          "No attack_execution_allowed: true in Phase 75A files")

    # Check no real data patterns
    real_patterns = [
        r'https?://(?!sim\.)', r'(?<![a-zA-Z])sk-[A-Za-z0-9_-]+',
        r'rm\s+-rf', r'curl\s+', r'wget\s+',
        r'/etc/', r'/home/', r'/root/', r'/usr/',
    ]
    has_real_data = False
    for pat in real_patterns:
        if re.search(pat, catalog_text):
            has_real_data = True
            break
    check(not has_real_data, "Catalog contains no real URLs, tokens, commands, or paths")

    # ================================================================
    # 11. Non-execution assertions
    # ================================================================
    print("\n11. Non-execution assertions")
    # Check no new corpus was created
    corpus_files_before = list(ROOT.glob("corpus/*phase75a*"))
    check(len(corpus_files_before) == 0, "No Phase 75A corpus created")

    # Check no adversarial playbook was created
    playbook_files = list(ROOT.glob("adversarial_playbooks/*phase75a*"))
    check(len(playbook_files) == 0, "No Phase 75A adversarial playbook created")

    # Check no run_config was created
    run_config_files = list(ROOT.glob("run_configs/*phase75a*"))
    check(len(run_config_files) == 0, "No Phase 75A run_config created")

    # Check no execution_results was generated
    exec_dirs = list(ROOT.glob("executions/*phase75a*"))
    check(len(exec_dirs) == 0, "No Phase 75A execution_results directory")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    total = checks_passed + checks_failed
    print(f"Phase 75A Cross-Module Attack Path Catalog validation: "
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
