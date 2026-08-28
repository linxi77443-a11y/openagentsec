#!/usr/bin/env python3
"""
Phase 95A — M07 Unauthorized Data Access Core Regression Validator

Validates corpus, run config, execution results, result YAML, capability scorecard,
documentation, and safety flags for Task M07.
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
    print("Phase 95A — M07 Unauthorized Data Access Core Regression Validation")
    print("=" * 65)

    # 1. File existence
    print("\n1. Checking file existence...")
    required_files = [
        ROOT / "capability_modules/corpora/phase45a_m07_unauthorized_access/m07_corpus.yaml",
        ROOT / "capability_modules/corpora/phase45a_m07_unauthorized_access/m07_mvp_corpus.yaml",
        ROOT / "adversarial_playbooks/m07_full_corpus/playbook.yaml",
        ROOT / "run_configs/phase95a_m07_core_regression_run_config.yaml",
        ROOT / "executions/phase95a_m07_core_regression/execution_results.json",
        ROOT / "executions/phase95a_m07_core_regression/m07_result.yaml",
        ROOT / "executions/phase95a_m07_core_regression/capability_scorecard.yaml",
        ROOT / "docs/phase95a_m07_core_regression_notes.md",
    ]
    for p in required_files:
        check(p.exists(), f"File exists: {p.relative_to(ROOT)}")

    # 2. Security Flags & Boundaries
    print("\n2. Checking security flags & boundaries...")
    for p in required_files:
        if p.suffix in [".yaml", ".yml", ".json", ".md"]:
            text = p.read_text(encoding="utf-8").lower()
            check("sk-" not in text and "openapi-" not in text, f"No secrets in {p.name}")

    # 3. Check Corpus Placeholder Standardization (<SIM_...>)
    print("\n3. Checking corpus placeholders (<SIM_...>)...")
    m07_corpus_path = ROOT / "capability_modules/corpora/phase45a_m07_unauthorized_access/m07_corpus.yaml"
    corpus_data = yaml_load(m07_corpus_path)
    if corpus_data:
        entries = corpus_data.get("m07", [])
        check(len(entries) >= 16, f"M07 corpus has >= 16 entries (got {len(entries)})")

        forbidden_names = [
            "张三", "李四", "王五", "赵六", "陈七", "孙八", "周九", "吴十",
            "郑一", "冯二", "褚三", "卫四", "蒋五", "沈六", "韩七", "黄八", "曹九", "杨十",
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

        # Verify <SIM_...> presence
        sim_tokens = re.findall(r"<SIM_\w+>", corpus_str)
        check(len(sim_tokens) >= 30, f"Found {len(sim_tokens)} <SIM_...> placeholders in corpus")

    # 4. Run config validation
    print("\n4. Checking run config...")
    rc_path = ROOT / "run_configs/phase95a_m07_core_regression_run_config.yaml"
    rc = yaml_load(rc_path)
    if rc:
        rcfg = rc.get("run_config", {})
        check(rcfg.get("phase") == "phase95a", "run_config phase == phase95a")
        check(rcfg.get("module_id") == "M07", "run_config module_id == M07")
        check(rcfg.get("confirmed_vulnerability") is False, "run_config confirmed_vulnerability == false")
        check(rcfg.get("formal_finding_allowed") is False, "run_config formal_finding_allowed == false")
        check(rcfg.get("production_safety_claimed") is False, "run_config production_safety_claimed == false")
        check(rcfg.get("synthetic_only") is True, "run_config synthetic_only == true")

    # 5. Execution results validation
    print("\n5. Checking execution results...")
    exec_path = ROOT / "executions/phase95a_m07_core_regression/execution_results.json"
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
    print("\n6. Checking m07_result.yaml...")
    res_path = ROOT / "executions/phase95a_m07_core_regression/m07_result.yaml"
    res_yaml = yaml_load(res_path)
    if res_yaml:
        check(res_yaml.get("module_id") == "m07" or res_yaml.get("module_id") == "M07", "result module_id == M07/m07")
        check(res_yaml.get("confirmed_vulnerability") is False, "result confirmed_vulnerability == false")
        check(res_yaml.get("formal_finding_allowed") is False, "result formal_finding_allowed == false")
        check(res_yaml.get("production_safety_claimed") is False, "result production_safety_claimed == false")
        check(res_yaml.get("capability_value") in ["high", "medium", "low"], f"capability_value valid ({res_yaml.get('capability_value')})")
        check(res_yaml.get("unauthorized_access_risk_level") in ["high", "medium", "low"], f"risk_level valid ({res_yaml.get('unauthorized_access_risk_level')})")
        check(res_yaml.get("breakthrough_detected", 0) == 0, "breakthrough_detected == 0")

    # 7. Scorecard validation
    print("\n7. Checking capability_scorecard.yaml...")
    sc_path = ROOT / "executions/phase95a_m07_core_regression/capability_scorecard.yaml"
    scorecard = yaml_load(sc_path)
    if scorecard:
        sm = scorecard.get("scorecard_metadata", {})
        check(sm.get("module_id") == "M07", "scorecard module_id == M07")
        check(sm.get("confirmed_vulnerability") is False, "scorecard confirmed_vulnerability == false")
        check(sm.get("formal_finding_allowed") is False, "scorecard formal_finding_allowed == false")
        check(sm.get("production_safety_claimed") is False, "scorecard production_safety_claimed == false")
        check(scorecard.get("capability_value") == "high", "scorecard capability_value == high")
        check(scorecard.get("risk_level") == "low", "scorecard risk_level == low")

    # 8. Documentation validation
    print("\n8. Checking docs/phase95a_m07_core_regression_notes.md...")
    doc_path = ROOT / "docs/phase95a_m07_core_regression_notes.md"
    if doc_path.exists():
        doc_text = doc_path.read_text(encoding="utf-8")
        check("<SIM_...>" in doc_text or "<SIM_" in doc_text, "Doc mentions <SIM_...> placeholders")
        check("confirmed_vulnerability" in doc_text and "false" in doc_text.lower(), "Doc specifies confirmed_vulnerability: false")
        check("formal_finding_allowed" in doc_text and "false" in doc_text.lower(), "Doc specifies formal_finding_allowed: false")

    # Summary
    print("\n" + "=" * 65)
    if checks_failed == 0:
        print("Phase 95A — M07 Core Regression: ALL CHECKS PASSED")
    else:
        print(f"Phase 95A — M07 Core Regression: FAILED ({checks_failed} errors)")
        for err in errors:
            print(f"  - {err}")
    print(f"Passed: {checks_passed}, Failed: {checks_failed}")
    print("=" * 65)

    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
