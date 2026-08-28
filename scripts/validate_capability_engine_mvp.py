#!/usr/bin/env python3
"""
Phase 36A — Capability Run Engine MVP Validation
Checks engine integrity, security boundaries, and config correctness.
"""
import os, sys, yaml, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "capability_engine"

ERRORS = []
WARNINGS = []

def check(condition, msg, severity="error"):
    if not condition:
        if severity == "error":
            ERRORS.append(msg)
        else:
            WARNINGS.append(msg)

def main():
    print("=" * 55)
    print("Phase 36A — Capability Run Engine MVP Validation")
    print("=" * 55)

    # --- File existence ---
    print("\n[1/8] File existence checks...")
    required = [
        ENGINE_DIR / "schemas/capability_run.schema.yaml",
        ENGINE_DIR / "configs/phase36a_m01_m02_m03_run.yaml",
        ENGINE_DIR / "runners/run_capability_eval.py",
        ENGINE_DIR / "parsers/parse_capability_results.py",
    ]
    for p in required:
        check(p.exists(), f"Missing: {p.relative_to(ROOT)}")

    # --- Security: no secrets in config ---
    print("\n[2/8] Security: no secrets in configs...")
    for cfg_path in list((ENGINE_DIR / "configs").glob("*.yaml")) + list((ENGINE_DIR / "schemas").glob("*.yaml")):
        if not cfg_path.exists():
            continue
        text = cfg_path.read_text()
        check("openapi-" not in text,
              f"API key found in {cfg_path.name}")
        check("sk-" not in text,
              f"OpenAI-style key found in {cfg_path.name}")
        check("Authorization" not in text,
              f"Authorization header found in {cfg_path.name}")
        check("confirmed_vulnerability" not in text,
              f"confirmed_vulnerability found in {cfg_path.name}")
        check("production_impact" not in text,
              f"production_impact found in {cfg_path.name}")
        for line in text.splitlines():
            if "base_url" in line.lower() and ":" in line and not line.strip().startswith("#"):
                val = line.split(":", 1)[1].strip()
                if val.startswith("http"):
                    check(False,
                          f"Hardcoded URL in {cfg_path.name}: {val}")

    # --- Security: env var names only ---
    print("\n[3/8] Security: env var references only...")
    run_config = yaml.safe_load((ENGINE_DIR / "configs/phase36a_m01_m02_m03_run.yaml").read_text())
    api_env = run_config.get("target_api_env", {})
    check("AUTHORIZED_TEST_API_BASE_URL" == api_env.get("base_url"),
          "target_api_env.base_url should be AUTHORIZED_TEST_API_BASE_URL")
    check("AUTHORIZED_TEST_API_KEY" == api_env.get("api_key"),
          "target_api_env.api_key should be AUTHORIZED_TEST_API_KEY")

    # --- Security: formal_finding_allowed ---
    print("\n[4/8] Security: formal finding disabled...")
    result_cfg = run_config.get("result", {})
    check(result_cfg.get("formal_finding_allowed") is False,
          "formal_finding_allowed must be false")
    check(result_cfg.get("result_semantics", "") == "needs_human_review",
          "result_semantics should be needs_human_review")

    # --- Security: no production / confirmed vuln ---
    print("\n[5/8] Security: no production/confirmed-vuln claims...")
    for py_file in ENGINE_DIR.rglob("*.py"):
        text = py_file.read_text()
        if "production" in text.lower():
            WARNINGS.append(f"'production' referenced in {py_file.relative_to(ROOT)}")
        if "confirmed_vulnerability" in text.lower():
            check(False, f"confirmed_vulnerability in {py_file.relative_to(ROOT)}")
        if ".local/" in text:
            check(False, f".local/ referenced in {py_file.relative_to(ROOT)}")

    # --- Runner imports ---
    print("\n[6/8] Runner imports...")
    sys.path.insert(0, str(ROOT))
    try:
        from capability_engine.runners.run_capability_eval import run, load_config
        print("  ✓ runner imports OK")
    except Exception as e:
        check(False, f"Runner import failed: {e}")

    # --- Parser imports ---
    print("\n[7/8] Parser imports...")
    try:
        from capability_engine.parsers.parse_capability_results import parse, detect_signals
        print("  ✓ parser imports OK")
    except Exception as e:
        check(False, f"Parser import failed: {e}")

    # --- Corpus reference valid ---
    print("\n[8/8] Corpus reference check...")
    corpus_ref = run_config.get("corpus_reference", "")
    corpus_path = ROOT / corpus_ref if not os.path.isabs(corpus_ref) else Path(corpus_ref)
    check(corpus_path.exists(), f"Corpus not found: {corpus_path}")
    if corpus_path.exists():
        corpus = yaml.safe_load(corpus_path.read_text())
        for mid in run_config.get("modules", []):
            entries = corpus.get(mid, [])
            check(len(entries) > 0, f"No corpus entries for module {mid}")
            positives = [e for e in entries if e.get("positive_or_control") == "positive"]
            controls = [e for e in entries if e.get("positive_or_control") == "control"]
            check(len(positives) > 0, f"No positive entries for module {mid}")

    # --- Report ---
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
