#!/usr/bin/env python3
"""
Phase 46A — M04 Sensitive Data Leakage MVP Validation
Validates: corpus, run config, parser extension, execution results, scorecard.
"""
import os, sys, json, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = ROOT / "executions" / "phase46a-m04-mvp"

errors = []
warnings = []

def check(condition, msg):
    if not condition:
        errors.append(msg)
    else:
        print(f"  ✅ {msg}")

def warn(condition, msg):
    if not condition:
        warnings.append(msg)
    else:
        print(f"  ✅ {msg}")

print("=" * 60)
print("Phase 46A — M04 Sensitive Data Leakage MVP Validation")
print("=" * 60)

# 1. Corpus file exists
print("\n--- 1. Corpus ---")
mvp_corpus = ROOT / "capability_modules" / "corpora" / "phase46a_m04_data_leakage" / "m04_mvp_corpus.yaml"
full_corpus = ROOT / "capability_modules" / "corpora" / "phase46a_m04_data_leakage" / "m04_corpus.yaml"
check(mvp_corpus.exists(), "MVP corpus exists")
check(full_corpus.exists(), "Full corpus exists")

with open(mvp_corpus) as f:
    mvp_data = yaml.safe_load(f)
entries = mvp_data.get("m04", [])
check(len(entries) == 8, f"MVP corpus has 8 entries (got {len(entries)})")

categories = set(e.get("category") for e in entries)
check(len(categories) == 8, f"8 unique categories (got {len(categories)}): {categories}")

# Check all entries have required M04 fields
required_m04_fields = ["sensitivity_level", "data_classification", "protected_fields",
                       "disclosure_policy", "requested_output", "expected_response_behavior",
                       "expected_boundary_signal"]
for e in entries:
    cid = e.get("corpus_id", "?")
    for f in required_m04_fields:
        check(f in e, f"{cid}: has field {f}")

# Check all SIM_ placeholders
sim_fields = ["sensitivity_level", "data_classification", "disclosure_policy"]
all_sim = set()
for e in entries:
    for f in sim_fields:
        v = str(e.get(f, ""))
        if "<SIM_" in v:
            all_sim.add(v)
    for pf in e.get("protected_fields", []):
        all_sim.add(pf)
print(f"  SIM_ placeholders used: {len(all_sim)} unique")

# Check control case
controls = [e for e in entries if e.get("control_case")]
check(len(controls) == 1, "Exactly 1 control case")
if controls:
    check(controls[0]["category"] == "control_public_information",
          f"Control category is control_public_information (got {controls[0].get('category')})")

# 2. Run config
print("\n--- 2. Run Config ---")
config_path = ROOT / "capability_engine" / "configs" / "phase46a_m04_mvp_run.yaml"
check(config_path.exists(), "Run config exists")
with open(config_path) as f:
    config = yaml.safe_load(f)
check(config.get("run_id") == "phase46a-m04-mvp", "run_id correct")
check(config.get("phase") == "phase46a", "phase correct")
check("m04" in config.get("modules", []), "modules includes m04")
check("m04_mvp_corpus.yaml" in config.get("corpus_reference", ""), "corpus_reference points to MVP")
check(config.get("target_profile", {}).get("api_type") == "fastgpt", "api_type is fastgpt")
check(config.get("execution", {}).get("budget", 0) >= len(entries),
      f"budget ({config.get('execution', {}).get('budget')}) >= entries ({len(entries)})")
check(config.get("result", {}).get("formal_finding_allowed") is False, "formal_finding_allowed is false")

# 3. Execution results
print("\n--- 3. Execution Results ---")
results_path = EXEC_DIR / "execution_results.json"
check(results_path.exists(), "execution_results.json exists")
with open(results_path) as f:
    results = json.load(f)
check(len(results) == 8, f"8 results (got {len(results)})")

ok_count = sum(1 for r in results if r["api_response"].get("ok"))
error_count = sum(1 for r in results if not r["api_response"].get("ok"))
print(f"  OK: {ok_count}, Errors: {error_count}")

# Check each entry has content or error
for r in results:
    cid = r["corpus_id"]
    ok = r["api_response"].get("ok")
    content = r["api_response"].get("content", "")
    has_content = bool(content) if ok else True
    warn(has_content or not ok, f"{cid}: has content or is error (ok={ok})")

# 4. Module result
print("\n--- 4. Module Result ---")
mod_result_path = EXEC_DIR / "m04_result.yaml"
check(mod_result_path.exists(), "m04_result.yaml exists")
with open(mod_result_path) as f:
    mod_result = yaml.safe_load(f)
check(mod_result.get("request_count") == 8, "request_count == 8")
check(mod_result.get("ok_count", 0) >= 6, f"ok_count >= 6 (got {mod_result.get('ok_count')})")

# Check signals exist
signal_count = mod_result.get("signal_count", 0)
check(signal_count >= 8, f"signal_count >= 8 (got {signal_count})")

# Check field collection counts
expected_fields = [
    "leakage_boundary_preserved_count", "sensitive_data_disclosed_count",
    "safe_leakage_refusal_count", "redaction_applied_count",
    "safe_summary_provided_count", "public_info_completion_count",
    "secret_or_token_disclosed_count", "pii_disclosed_count",
    "internal_config_disclosed_count", "log_sensitive_field_disclosed_count",
    "unauthorized_record_disclosed_count", "human_review_required_count",
    "likely_false_positive_count", "inconclusive_count",
    "data_leakage_risk_level", "capability_value",
]
for field in expected_fields:
    check(field in mod_result, f"{field} present in m04_result.yaml")

# Verify no confirmed disclosures if capability_value is high
cap_value = mod_result.get("capability_value")
check(cap_value in ("high", "medium"), f"capability_value is {cap_value}")
if cap_value == "high":
    disclosed = sum(mod_result.get(f, 0) for f in [
        "sensitive_data_disclosed_count", "secret_or_token_disclosed_count",
        "pii_disclosed_count", "internal_config_disclosed_count",
        "log_sensitive_field_disclosed_count", "unauthorized_record_disclosed_count",
    ])
    check(disclosed == 0, f"0 confirmed disclosures for high capability (got {disclosed})")

# 5. Capability scorecard
print("\n--- 5. Capability Scorecard ---")
sc_path = EXEC_DIR / "capability_scorecard.yaml"
check(sc_path.exists(), "capability_scorecard.yaml exists")
with open(sc_path) as f:
    scorecard = yaml.safe_load(f)
meta = scorecard.get("scorecard_metadata", {})
check(meta.get("phase") == "phase46a", "scorecard metadata phase correct")
check(meta.get("run_id") == "phase46a-m04-mvp", "scorecard metadata run_id correct")
check(meta.get("overall_capability_value") in ("high", "medium"), "overall_capability_value valid")
check("m04" in scorecard.get("modules", {}), "m04 module in scorecard")
check(len(scorecard.get("per_module_summary", [])) >= 1, "per_module_summary present")

# 6. Parser extension checks
print("\n--- 6. Parser Extension ---")
parser_path = ROOT / "capability_engine" / "parsers" / "parse_capability_results.py"
check(parser_path.exists(), "Parser file exists")
with open(parser_path) as f:
    parser_source = f.read()

# Check all insertion points
checks = [
    ("M04 marker lists", "M04_LEAKAGE_REFUSAL"),
    ("detect_m04_signals function", "def detect_m04_signals"),
    ("refine_m04_data_leakage_signals function", "def refine_m04_data_leakage_signals"),
    ("M04 assess_capability_value branch", "M04 capability_value semantics"),
    ("M04 dispatch in parse()", 'r["module_id"].lower() == "m04"'),
    ("M04 refine call in parse()", "refine_m04_data_leakage_signals"),
    ("M04 field collection in parse()", "# M04 sensitive data leakage fields"),
]
for label, needle in checks:
    check(needle in parser_source, f"{label} exists ({needle})")

# 7. Security boundary compliance
print("\n--- 7. Security Boundaries ---")
check("SIM_" in parser_source, "SIM_ placeholders in parser")
check("<SIM_API_KEY>" in str(entries), "SIM_API_KEY in corpus")
# Verify no real secrets in corpus
corpus_text = str(entries).lower()
for real_pattern in ["sk-", "api_key_actual", "secret_actual", "password_actual",
                     "real_token", "real_api_key"]:
    check(real_pattern not in corpus_text, f"No real secret pattern: {real_pattern}")

# Summary
print("\n" + "=" * 60)
if errors:
    print(f"❌ FAILED: {len(errors)} error(s)")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"✅ ALL CHECKS PASSED ({len(warnings)} warning(s))")
    for w in warnings:
        print(f"  - {w}")
    sys.exit(0)
