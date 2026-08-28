#!/usr/bin/env python3
"""
Phase 37A — M06 External Content Boundary MVP Validation
"""
import os, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []
WARNINGS = []

def check(condition, msg, severity="error"):
    if not condition:
        (ERRORS if severity == "error" else WARNINGS).append(msg)

def main():
    print("=" * 55)
    print("Phase 37A — M06 MVP Validation")
    print("=" * 55)

    # File existence
    print("\n[1/7] File existence...")
    for p in [
        ROOT / "capability_modules/corpora/phase37a_m06_external_content_boundary/m06_corpus.yaml",
        ROOT / "capability_engine/configs/phase37a_m06_run.yaml",
        ROOT / "capability_engine/parsers/parse_capability_results.py",
        ROOT / "capability_engine/runners/run_capability_eval.py",
    ]:
        check(p.exists(), f"Missing: {p.relative_to(ROOT)}")

    # Security: no secrets in configs
    print("\n[2/7] Security: no secrets...")
    for cfg in [
        ROOT / "capability_engine/configs/phase37a_m06_run.yaml",
        ROOT / "capability_modules/corpora/phase37a_m06_external_content_boundary/m06_corpus.yaml",
    ]:
        if not cfg.exists():
            continue
        text = cfg.read_text()
        check("openapi-" not in text, f"API key in {cfg.name}")
        check("sk-" not in text, f"OpenAI key in {cfg.name}")
        check("Authorization" not in text, f"Auth header in {cfg.name}")
        check("confirmed_vulnerability" not in text, f"confirmed_vuln in {cfg.name}")
        check("production_impact" not in text, f"production_impact in {cfg.name}")

    # Security: env var names only
    print("\n[3/7] Security: env var refs...")
    run_config = yaml.safe_load((ROOT / "capability_engine/configs/phase37a_m06_run.yaml").read_text())
    api_env = run_config.get("target_api_env", {})
    check(api_env.get("base_url") == "AUTHORIZED_TEST_API_BASE_URL",
          "base_url should be env var name")
    check(api_env.get("api_key") == "AUTHORIZED_TEST_API_KEY",
          "api_key should be env var name")

    # Security: formal finding disabled
    print("\n[4/7] Security: formal finding disabled...")
    result_cfg = run_config.get("result", {})
    check(result_cfg.get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")
    check(result_cfg.get("result_semantics", "") == "needs_human_review",
          "result_semantics should be needs_human_review")

    # Security: no .local/, module scope
    print("\n[5/7] Security: scope check...")
    for py_file in list((ROOT / "capability_engine").rglob("*.py")):
        text = py_file.read_text()
        if ".local/" in text:
            check(False, f".local/ in {py_file.relative_to(ROOT)}")
        if "m14" in text.lower() or "m38" in text.lower() or "m40" in text.lower():
            WARNINGS.append(f"other module ref in {py_file.relative_to(ROOT)}")

    # M06 corpus structure
    print("\n[6/7] Corpus structure...")
    corpus = yaml.safe_load((ROOT / "capability_modules/corpora/phase37a_m06_external_content_boundary/m06_corpus.yaml").read_text())
    m06_entries = corpus.get("m06", [])
    check(len(m06_entries) > 0, "No M06 entries")
    if m06_entries:
        categories = set(e.get("category", "") for e in m06_entries)
        check(len(categories) >= 4, f"Too few categories: {categories}")
        for e in m06_entries:
            check("user_goal" in e, f"{e.get('corpus_id','?')} missing user_goal")
            check("external_content" in e, f"{e.get('corpus_id','?')} missing external_content")
            check("expected_behavior" in e, f"{e.get('corpus_id','?')} missing expected_behavior")
            check("control_case" in e, f"{e.get('corpus_id','?')} missing control_case")

    # Parser M06 support
    print("\n[7/7] Parser M06 support...")
    sys.path.insert(0, str(ROOT))
    try:
        from capability_engine.parsers.parse_capability_results import detect_signals, assess_capability_value
        sigs_m06 = detect_signals("m06", "测试内容：根据财务报告判断公司Q3是否盈利。财务报告显示Q3净利润为500万元。结论应该是盈利。这个结果基于可靠的财务数据。", False, "benign_external_content")
        check("preserves_user_goal" in sigs_m06,
              f"M06 signal detection failed: {sigs_m06}")
        value, reason = assess_capability_value("m06", [
            {"positive_or_control": "positive", "signals": ["preserves_user_goal"], "error": False}
        ])
        check(value in ("low", "medium", "high", "inconclusive"),
              f"M06 assess failed: {value}")
        print("  ✓ M06 parser support OK")
    except Exception as e:
        check(False, f"M06 parser import/test failed: {e}")

    # Report
    print("\n" + "=" * 55)
    if ERRORS:
        print(f"FAILED — {len(ERRORS)} error(s):")
        for e in ERRORS:
            print(f"  ✗ {e}")
    else:
        print("ALL CHECKS PASSED")
    if WARNINGS:
        print(f"\n{len(WARNINGS)} warning(s):")
        for w in WARNINGS:
            print(f"  ⚠ {w}")
    print("=" * 55)
    return len(ERRORS) == 0

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
