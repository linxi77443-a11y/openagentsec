#!/usr/bin/env python3
"""Phase 74A — Cross-Module Attack Graph & Propagation Model Design Gate Validator.

Review-only validator. Checks design docs, notes, safety fields, and confirms
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


def main():
    global checks_passed, checks_failed
    print("=" * 60)
    print("Phase 74A — Cross-Module Attack Graph Design Gate")
    print("Review Validation — ALL CHECKS")
    print("=" * 60)

    # ================================================================
    # 1. Design documents existence
    # ================================================================
    print("\n1. Design document existence")
    schema_path = ROOT / "docs/cross_module_attack_graph_schema.md"
    prop_path = ROOT / "docs/risk_propagation_model.md"
    result_path = ROOT / "results/phase74a_cross_module_attack_graph_design_gate_result.yaml"
    notes_path = ROOT / "docs/phase74a_cross_module_attack_graph_design_gate_notes.md"

    check(schema_path.exists(), "Attack graph schema exists")
    check(prop_path.exists(), "Risk propagation model exists")
    check(result_path.exists(), "Design gate result exists")
    check(notes_path.exists(), "Design gate notes exists")

    # ================================================================
    # 2. Attack graph schema content check
    # ================================================================
    print("\n2. Attack graph schema content")
    schema_text = schema_path.read_text() if schema_path.exists() else ""

    check("node_types" in schema_text, "Schema contains node_types")
    check("edge_types" in schema_text, "Schema contains edge_types")
    check("path_schema" in schema_text or "Path Representation" in schema_text,
          "Schema contains path representation")
    check("M43" in schema_text and "M46" in schema_text and "M47" in schema_text,
          "Schema references M43, M46, M47")
    check("M48" in schema_text and "M49" in schema_text and "M50" in schema_text,
          "Schema references M48, M49, M50")
    check("executable: false" in schema_text,
          "Schema contains executable: false declaration")
    check("supply_chain" in schema_text and "development_environment" in schema_text,
          "Schema contains supply_chain layer")
    check("rag_data" in schema_text and "runtime_sandbox" in schema_text,
          "Schema contains rag_data and runtime_sandbox layers")
    check("conceptual_paths" in schema_text or "Attack Path Schema" in schema_text,
          "Schema contains conceptual path definitions")
    check("Forbidden Uses" in schema_text, "Schema contains Forbidden Uses section")
    check("simulated_capability_signal_only" in schema_text,
          "Schema preserves breakthrough semantics")

    # Check no real data in schema
    real_patterns = [
        r'https?://(?!sim\.)', r'(?<![a-zA-Z])sk-[A-Za-z0-9_-]+',
        r'api[a-zA-Z]*\.[a-zA-Z]+\.com',
        r'git\s+clone', r'rm\s+-rf', r'curl\s+', r'wget\s+',
        r'/etc/', r'/home/', r'/root/', r'/usr/',
    ]
    schema_no_real = True
    for pat in real_patterns:
        if re.search(pat, schema_text):
            schema_no_real = False
            break
    check(schema_no_real, "Schema contains no real URLs, tokens, commands, or paths")

    # ================================================================
    # 3. Risk propagation model content check
    # ================================================================
    print("\n3. Risk propagation model content")
    prop_text = prop_path.read_text() if prop_path.exists() else ""

    check("propagation_layers" in prop_text, "Model contains propagation_layers")
    check("propagation_rule_types" in prop_text, "Model contains propagation_rule_types")
    check("risk_amplification_factor" in prop_text,
          "Model contains risk_amplification_factor")
    check("not_production_risk" in prop_text,
          "Model contains not_production_risk disclaimer")
    check("not_vulnerability_severity" in prop_text,
          "Model contains not_vulnerability_severity disclaimer")
    check("risk_attenuation_factors" in prop_text or "Risk Attenuation" in prop_text,
          "Model contains attenuation factor concept")
    check("boundary_preservation_rules" in prop_text or "Boundary Preservation" in prop_text,
          "Model contains boundary preservation rules")
    check("evidence_trace_dependency" in prop_text or "Evidence Trace" in prop_text,
          "Model contains evidence trace dependency")
    check("human_review_gate" in prop_text or "Human Review" in prop_text,
          "Model contains human review gate concept")
    check("Forbidden Uses" in prop_text, "Model contains Forbidden Uses section")
    check("conceptual_only" in prop_text, "Model declares conceptual_only")
    check("not_exploitability_score" in prop_text or "not_cvss" in prop_text,
          "Model declares not exploitability score")
    check("M43" in prop_text and "M46" in prop_text and "M47" in prop_text,
          "Model references M43, M46, M47")
    check("M48" in prop_text and "M49" in prop_text and "M50" in prop_text,
          "Model references M48, M49, M50")

    # Check no real data in propagation model
    prop_no_real = True
    for pat in real_patterns:
        if re.search(pat, prop_text):
            prop_no_real = False
            break
    check(prop_no_real, "Propagation model contains no real URLs, tokens, or commands")

    # ================================================================
    # 4. Design gate notes content check
    # ================================================================
    print("\n4. Design gate notes content")
    notes_text = notes_path.read_text() if notes_path.exists() else ""

    check("design_gate" in notes_text.lower() or "Design Gate" in notes_text,
          "Notes mention design gate")
    check("理论模型" in notes_text or "theory" in notes_text.lower(),
          "Notes mention theory model")
    check("不开发新模块" in notes_text or "no new module" in notes_text.lower(),
          "Notes mention no new module development")
    check("不新增 corpus" in notes_text or "no corpus" in notes_text.lower(),
          "Notes mention no corpus")
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
    # 5. Design gate result content check
    # ================================================================
    print("\n5. Design gate result content")
    result = yaml_load(result_path)
    check(result is not None, "Design gate result YAML loaded")
    if result:
        check(result.get("phase") == "74A", "Result phase == 74A")
        check(result.get("design_gate_only") is True,
              "Result design_gate_only == true")
        check(result.get("theory_model_only") is True,
              "Result theory_model_only == true")
        check(result.get("schema_definition_only") is True,
              "Result schema_definition_only == true")
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
        check(result.get("breakthrough_detected_generated") is False,
              "Result breakthrough_detected_generated == false")

    # ================================================================
    # 6. Non-execution assertions
    # ================================================================
    print("\n6. Non-execution assertions")

    # Check no corpus directories were created
    corpus_dirs = list((ROOT / "adversarial_playbooks").glob("*phase74a*"))
    check(len(corpus_dirs) == 0, "No Phase 74A adversarial playbook created")

    # Check no run_config (we don't have a run_configs dir, so skip this specific check)
    # Check no execution_results was generated
    exec_dirs = list((ROOT / "executions").glob("*phase74a*"))
    check(len(exec_dirs) == 0, "No Phase 74A execution_results directory")

    # ================================================================
    # 7. Negative assertions
    # ================================================================
    print("\n7. Negative assertions")

    # Check for forbidden true values in all Phase 74A files
    phase74a_files = [
        schema_path, prop_path, notes_path, result_path,
    ]
    all_text = ""
    for f in phase74a_files:
        if f.exists():
            all_text += f.read_text() + "\n"

    check("confirmed_vulnerability: true" not in all_text,
          "No confirmed_vulnerability: true in Phase 74A files")
    check("formal_finding_allowed: true" not in all_text,
          "No formal_finding_allowed: true in Phase 74A files")
    check("production_safety_claimed: true" not in all_text,
          "No production_safety_claimed: true in Phase 74A files")
    check("controlled_replay_claimed: true" not in all_text,
          "No controlled_replay_claimed: true in Phase 74A files")
    check("controlled_replay_execution_allowed: true" not in all_text,
          "No controlled_replay_execution_allowed: true in Phase 74A files")
    check("replay_executable: true" not in all_text,
          "No replay_executable: true in Phase 74A files")

    # Check no real system connections
    check("real_system_connection_allowed: true" not in all_text,
          "No real_system_connection_allowed: true")
    check("real_tool_call_allowed: true" not in all_text,
          "No real_tool_call_allowed: true")
    check("real_api_call_allowed: true" not in all_text,
          "No real_api_call_allowed: true")

    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "=" * 60)
    total = checks_passed + checks_failed
    print(f"Phase 74A Cross-Module Attack Graph Design Gate validation: "
          f"{'ALL CHECKS PASSED' if checks_failed == 0 else 'SOME CHECKS FAILED'}")
    print(f"checks_passed: {checks_passed}")
    print(f"checks_failed: {checks_failed}")
    if checks_failed > 0:
        print("\nFAILURES:")
        for e in errors:
            print(f"  - {e}")
    print("=" * 60)
    return 0 if checks_failed == 0 else 1


def yaml_load(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load: {path} — {e}")
        return None


if __name__ == "__main__":
    sys.exit(main())
