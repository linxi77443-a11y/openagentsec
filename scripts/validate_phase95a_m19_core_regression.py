#!/usr/bin/env python3
"""
Phase 95A — M19 Business Data Exposure Core Regression Validator

Validates corpus, run config, execution results, result YAML, capability scorecard,
documentation, and safety flags for Task M19.
Enforces strictly <SIM_FINANCIAL_...> and <SIM_STRATEGY_...> placeholders.
"""
import json
import sys
import yaml
import re
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
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        check(False, f"YAML load failed for {path}: {e}")
        return None


def json_load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        check(False, f"JSON load failed for {path}: {e}")
        return None


def main():
    global checks_passed, checks_failed
    print("=" * 65)
    print("Phase 95A — M19 Business Data Exposure Core Regression Validation")
    print("=" * 65)

    # 1. File existence
    print("\n1. Checking file existence...")
    required_files = [
        ROOT / "capability_modules/corpora/phase47a_m19_business_data_exposure/m19_corpus.yaml",
        ROOT / "capability_modules/corpora/phase47a_m19_business_data_exposure/m19_mvp_corpus.yaml",
        ROOT / "run_configs/phase95a_m19_core_regression_run_config.yaml",
        ROOT / "executions/phase95a_m19_core_regression/execution_results.json",
        ROOT / "executions/phase95a_m19_core_regression/m19_result.yaml",
        ROOT / "executions/phase95a_m19_core_regression/result.yaml",
        ROOT / "executions/phase95a_m19_core_regression/capability_scorecard.yaml",
        ROOT / "docs/phase95a_m19_core_regression_notes.md",
    ]
    for p in required_files:
        check(p.exists(), f"File exists: {p.relative_to(ROOT)}")

    # 2. Security Flags & Boundaries
    print("\n2. Checking security flags & boundaries...")
    for p in required_files:
        if p.suffix in [".yaml", ".yml", ".json", ".md"]:
            text = p.read_text(encoding="utf-8").lower()
            # Verify no real secrets (non-simulated sk- tokens)
            sk_real = re.findall(r'sk-(?!<sim)', text)
            check(len(sk_real) == 0, f"No real secret tokens in {p.name}")

    # 3. Check Corpus Placeholder Standardization (<SIM_FINANCIAL_...> & <SIM_STRATEGY_...>)
    print("\n3. Checking corpus placeholders (<SIM_FINANCIAL_...> & <SIM_STRATEGY_...>)...")
    m19_corpus_path = ROOT / "capability_modules/corpora/phase47a_m19_business_data_exposure/m19_corpus.yaml"
    corpus_data = yaml_load(m19_corpus_path)
    if corpus_data:
        entries = corpus_data.get("m19", [])
        check(len(entries) >= 16, f"M19 corpus has >= 16 entries (got {len(entries)})")

        forbidden_names = [
            "张三", "李四", "王五", "赵六", "陈七", "孙八", "周九", "吴十",
            "A公司", "B公司", "X集团", "Y科技", "EMP001", "EMP002"
        ]
        has_forbidden = False
        corpus_str = str(corpus_data)
        for fname in forbidden_names:
            if fname in corpus_str:
                has_forbidden = True
                check(False, f"Corpus contains un-sanitized name: {fname}")
        if not has_forbidden:
            check(True, "All corpus entries are free of hardcoded real-world entity names")

        # Verify <SIM_FINANCIAL_...> and <SIM_STRATEGY_...> presence
        sim_financial_tokens = re.findall(r"<SIM_FINANCIAL_\w+>", corpus_str)
        sim_strategy_tokens = re.findall(r"<SIM_STRATEGY_\w+>", corpus_str)
        check(len(sim_financial_tokens) >= 5, f"Found {len(sim_financial_tokens)} <SIM_FINANCIAL_...> placeholders in corpus")
        check(len(sim_strategy_tokens) >= 5, f"Found {len(sim_strategy_tokens)} <SIM_STRATEGY_...> placeholders in corpus")

        # Ensure all placeholders match strictly SIM_FINANCIAL_ or SIM_STRATEGY_
        all_sim_tokens = re.findall(r"<SIM_\w+>", corpus_str)
        non_standard_sim = [t for t in all_sim_tokens if not (t.startswith("<SIM_FINANCIAL_") or t.startswith("<SIM_STRATEGY_"))]
        check(len(non_standard_sim) == 0, f"All <SIM_...> placeholders follow <SIM_FINANCIAL_...> or <SIM_STRATEGY_...> format (non-standard: {non_standard_sim})")

    # 4. Run config validation
    print("\n4. Checking run config...")
    rc_path = ROOT / "run_configs/phase95a_m19_core_regression_run_config.yaml"
    rc = yaml_load(rc_path)
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase95a", "run_config phase == phase95a")
        check(rcfg.get("module_id") == "M19", "run_config module_id == M19")
        check(rcfg.get("confirmed_vulnerability") is False, "run_config confirmed_vulnerability == false")
        check(rcfg.get("formal_finding_allowed") is False, "run_config formal_finding_allowed == false")
        check(rcfg.get("production_safety_claimed") is False, "run_config production_safety_claimed == false")
        check(rcfg.get("synthetic_only") is True, "run_config synthetic_only == true")

    # 5. Execution results validation
    print("\n5. Checking execution results...")
    exec_path = ROOT / "executions/phase95a_m19_core_regression/execution_results.json"
    exec_results = json_load(exec_path)
    if exec_results:
        check(len(exec_results) >= 16, f"execution_results has {len(exec_results)} items (>=16)")
        for r in exec_results:
            cid = r.get("case_id", "?")
            check(r.get("confirmed_vulnerability") is False, f"{cid} confirmed_vulnerability == false")
            check(r.get("formal_finding_allowed") is False, f"{cid} formal_finding_allowed == false")
            check(r.get("real_user_system_accessed") is False, f"{cid} real_user_system_accessed == false")
            check(r.get("real_tenant_database_accessed") is False, f"{cid} real_tenant_database_accessed == false")

    # 6. Result YAML validation
    print("\n6. Checking m19_result.yaml and result.yaml...")
    for res_name in ["m19_result.yaml", "result.yaml"]:
        res_path = ROOT / "executions/phase95a_m19_core_regression" / res_name
        res_yaml = yaml_load(res_path)
        if res_yaml:
            check(res_yaml.get("module_id") in ["m19", "M19"], f"{res_name} module_id == M19/m19")
            check(res_yaml.get("confirmed_vulnerability") is False, f"{res_name} confirmed_vulnerability == false")
            check(res_yaml.get("formal_finding_allowed") is False, f"{res_name} formal_finding_allowed == false")
            check(res_yaml.get("production_safety_claimed") is False, f"{res_name} production_safety_claimed == false")
            check(res_yaml.get("capability_value") in ["high", "medium", "low"], f"{res_name} capability_value valid ({res_yaml.get('capability_value')})")
            check(res_yaml.get("business_data_exposure_risk_level", res_yaml.get("risk_level")) in ["high", "medium", "low"], f"{res_name} risk_level valid")
            check(res_yaml.get("breakthrough_detected", 0) == 0, f"{res_name} breakthrough_detected == 0")

    # 7. Scorecard validation
    print("\n7. Checking capability_scorecard.yaml...")
    sc_path = ROOT / "executions/phase95a_m19_core_regression/capability_scorecard.yaml"
    scorecard = yaml_load(sc_path)
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        check(sm.get("module_id") == "M19", "scorecard module_id == M19")
        check(sm.get("confirmed_vulnerability") is False, "scorecard confirmed_vulnerability == false")
        check(sm.get("formal_finding_allowed") is False, "scorecard formal_finding_allowed == false")
        check(sm.get("production_safety_claimed") is False, "scorecard production_safety_claimed == false")
        check(scorecard.get("capability_value") in ["high", "medium", "low"], "scorecard capability_value valid")
        check(scorecard.get("risk_level") in ["high", "medium", "low"], "scorecard risk_level valid")

    # 8. Documentation validation
    print("\n8. Checking documentation...")
    doc_path = ROOT / "docs/phase95a_m19_core_regression_notes.md"
    if doc_path.exists():
        doc_text = doc_path.read_text(encoding="utf-8")
        check("<SIM_FINANCIAL_" in doc_text, "Doc mentions <SIM_FINANCIAL_...")
        check("<SIM_STRATEGY_" in doc_text, "Doc mentions <SIM_STRATEGY_...")
        check("confirmed_vulnerability" in doc_text, "Doc contains confirmed_vulnerability assertion")
        check("formal_finding_allowed" in doc_text, "Doc contains formal_finding_allowed assertion")

    # Summary
    print("\n" + "=" * 65)
    print(f"Validation Summary: {checks_passed} PASSED, {checks_failed} FAILED")
    print("=" * 65)

    if checks_failed > 0:
        print("\nFailures:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nALL CHECKS PASSED SUCCESSFULLY!")
        sys.exit(0)


if __name__ == "__main__":
    main()
