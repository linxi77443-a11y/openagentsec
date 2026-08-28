#!/usr/bin/env python3
"""
M39 Full Corpus Validator
Validates the expanded M39 Agent Runtime State Corruption corpus (50 entries).

Usage:
    python3 scripts/validate_m39_full_corpus.py
"""

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CORPUS_PATH = BASE / "adversarial_playbooks" / "m39_full_corpus" / "playbook.yaml"
RESULTS_PATH = BASE / "executions" / "m39-full-corpus" / "execution_results.json"
RESULT_YAML_PATH = BASE / "executions" / "m39-full-corpus" / "m39_full_corpus_result.yaml"
SCORECARD_PATH = BASE / "executions" / "m39-full-corpus" / "capability_scorecard.yaml"
CONFIG_PATH = BASE / "capability_engine" / "configs" / "m39_full_corpus_run.yaml"


def load_corpus():
    """Load corpus YAML by splitting on '- corpus_id:' boundaries."""
    text = CORPUS_PATH.read_text(encoding="utf-8")
    # Split on the pattern that starts each entry
    # After split, parts[0] is header, parts[1..50] start with ' "M39-XX-NNN"'
    parts = re.split(r'\n  - corpus_id:', text)
    entries = []
    for raw in parts[1:]:  # skip header
        entry = {}
        # corpus_id is at the start of raw (consumed by split)
        m = re.match(r'\s*"([^"]+)"', raw)
        if m:
            entry["corpus_id"] = m.group(1)
        # module_id
        m = re.search(r'module_id:\s*"([^"]+)"', raw)
        if m:
            entry["module_id"] = m.group(1)
        # category
        m = re.search(r'category:\s*"([^"]+)"', raw)
        if m:
            entry["category"] = m.group(1)
        # subcategory
        m = re.search(r'subcategory:\s*"([^"]+)"', raw)
        if m:
            entry["subcategory"] = m.group(1)
        # technique_tag
        m = re.search(r'technique_tag:\s*"([^"]+)"', raw)
        if m:
            entry["technique_tag"] = m.group(1)
        # positive_or_control
        m = re.search(r'positive_or_control:\s*"([^"]+)"', raw)
        if m:
            entry["positive_or_control"] = m.group(1)
        # control_case
        m = re.search(r'control_case:\s*(true|false)', raw)
        if m:
            entry["control_case"] = m.group(1) == "true"
        # confirmed_vulnerability
        m = re.search(r'confirmed_vulnerability:\s*(true|false)', raw)
        if m:
            entry["confirmed_vulnerability"] = m.group(1) == "true"
        # formal_finding_allowed
        m = re.search(r'formal_finding_allowed:\s*(true|false)', raw)
        if m:
            entry["formal_finding_allowed"] = m.group(1) == "true"
        # production_safety_claimed
        m = re.search(r'production_safety_claimed:\s*(true|false)', raw)
        if m:
            entry["production_safety_claimed"] = m.group(1) == "true"
        # user_goal
        m = re.search(r'user_goal:\s*"([^"]*)"', raw)
        if m:
            entry["user_goal"] = m.group(1)
        # trusted_context
        m = re.search(r'trusted_context:\s*"([^"]*)"', raw)
        if m:
            entry["trusted_context"] = m.group(1)
        # embedded_payload
        m = re.search(r'embedded_payload:\s*"([^"]*)"', raw)
        if m:
            entry["embedded_payload"] = m.group(1)
        # expected_behavior
        m = re.search(r'expected_behavior:\s*"([^"]+)"', raw)
        if m:
            entry["expected_behavior"] = m.group(1)
        # expected_result_semantics
        m = re.search(r'expected_result_semantics:\s*"([^"]+)"', raw)
        if m:
            entry["expected_result_semantics"] = m.group(1)
        # boundary_signal
        m = re.search(r'boundary_signal:\s*"([^"]+)"', raw)
        if m:
            entry["boundary_signal"] = m.group(1)
        # execution_priority
        m = re.search(r'execution_priority:\s*(\d+)', raw)
        if m:
            entry["execution_priority"] = int(m.group(1))
        # prompt_text — multi-line string after "prompt_text: "
        pt_idx = raw.find('prompt_text:')
        if pt_idx >= 0:
            rest = raw[pt_idx + len('prompt_text:'):].strip()
            if rest.startswith('"'):
                # find closing quote
                end = rest.find('"', 1)
                while end > 0 and rest[end - 1] == '\\':
                    end = rest.find('"', end + 1)
                if end > 0:
                    entry["prompt_text"] = rest[1:end]
                else:
                    entry["prompt_text"] = rest[1:]
            else:
                entry["prompt_text"] = rest.split('\n')[0]

        if entry.get("corpus_id"):
            entries.append(entry)
    return entries


def load_results():
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))


def parse_simple_yaml(path):
    text = path.read_text(encoding="utf-8")
    data = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = re.match(r'^(\w[\w_]*)\s*:\s*(.+)$', stripped)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            else:
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        if val.lower() == "true":
                            val = True
                        elif val.lower() == "false":
                            val = False
            data[key] = val
    return data


REQUIRED_FIELDS = [
    "corpus_id", "module_id", "category", "subcategory", "technique_tag",
    "positive_or_control", "control_case", "user_goal", "trusted_context",
    "embedded_payload", "expected_behavior", "expected_result_semantics",
    "boundary_signal", "prompt_text", "execution_priority",
    "confirmed_vulnerability", "formal_finding_allowed", "production_safety_claimed",
]

CATEGORY_COUNTS = {
    "state_contamination": 15,
    "state_tampering": 15,
    "state_recovery": 10,
    "control_case": 10,
}

SAFETY_FLAGS = ["confirmed_vulnerability", "formal_finding_allowed", "production_safety_claimed"]


def validate():
    errors = []

    # 1. Files exist
    for label, path in [("Corpus", CORPUS_PATH), ("Results JSON", RESULTS_PATH),
                         ("Result YAML", RESULT_YAML_PATH), ("Scorecard", SCORECARD_PATH),
                         ("Run config", CONFIG_PATH)]:
        if not path.exists():
            errors.append(f"{label} not found: {path}")
    if errors:
        for e in errors:
            print(f"  FAIL: {e}")
        return False

    # 2. Load corpus
    entries = load_corpus()
    print(f"  [1] Corpus entries loaded: {len(entries)}")
    if len(entries) != 50:
        errors.append(f"Expected 50 corpus entries, got {len(entries)}")
    else:
        print("       PASS: entry count = 50")

    # 3. Category distribution
    cat_counts = {}
    for e in entries:
        cat = e.get("category", "unknown")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, expected in CATEGORY_COUNTS.items():
        actual = cat_counts.get(cat, 0)
        status = "PASS" if actual == expected else "FAIL"
        print(f"  [2] {cat}: {actual}/{expected} — {status}")
        if actual != expected:
            errors.append(f"Category {cat}: expected {expected}, got {actual}")

    # 4. Required fields
    missing_fields = []
    for i, e in enumerate(entries):
        for field in REQUIRED_FIELDS:
            if field not in e:
                missing_fields.append((i, e.get("corpus_id", "?"), field))
    if missing_fields:
        shown = missing_fields[:10]
        for idx, cid, f in shown:
            errors.append(f"Entry {idx} ({cid}) missing field: {f}")
        if len(missing_fields) > 10:
            errors.append(f"  ... and {len(missing_fields) - 10} more")
    else:
        print("  [3] PASS: all required fields present")

    # 5. No duplicate corpus_ids
    ids = [e.get("corpus_id", "") for e in entries]
    dupes = [x for x in ids if ids.count(x) > 1]
    if dupes:
        errors.append(f"Duplicate corpus_ids: {set(dupes)}")
    else:
        print("  [4] PASS: no duplicate corpus_ids")

    # 6. Safety flags
    bad_safety = []
    for e in entries:
        for flag in SAFETY_FLAGS:
            val = e.get(flag)
            if val is not False and val is not None:
                bad_safety.append((e.get("corpus_id"), flag, val))
    if bad_safety:
        for cid, flag, val in bad_safety[:5]:
            errors.append(f"{cid}: {flag} = {val} (expected false)")
    else:
        print("  [5] PASS: all safety flags are false")

    # 7. Results match corpus
    results = load_results()
    print(f"  [6] Execution results entries: {len(results)}")
    if len(results) != len(entries):
        errors.append(f"Results count ({len(results)}) != corpus count ({len(entries)})")
    else:
        print("       PASS: results count matches corpus")

    result_ids = {r["corpus_id"] for r in results}
    corpus_ids = {e["corpus_id"] for e in entries}
    if result_ids != corpus_ids:
        missing = corpus_ids - result_ids
        extra = result_ids - corpus_ids
        if missing:
            errors.append(f"Results missing corpus_ids: {missing}")
        if extra:
            errors.append(f"Results has extra corpus_ids: {extra}")
    else:
        print("       PASS: result corpus_ids match corpus")

    # 8. Result YAML
    result_yaml = parse_simple_yaml(RESULT_YAML_PATH)
    print(f"  [7] Result YAML total_entries: {result_yaml.get('total_entries', 'N/A')}")
    if result_yaml.get("total_entries") != 50:
        errors.append(f"Result YAML total_entries != 50")

    # 9. Scorecard
    scorecard_yaml = parse_simple_yaml(SCORECARD_PATH)
    print(f"  [8] Scorecard total_api_calls: {scorecard_yaml.get('total_api_calls', 'N/A')}")
    if scorecard_yaml.get("total_api_calls") != 50:
        errors.append(f"Scorecard total_api_calls != 50")

    # 10. Config
    config_yaml = parse_simple_yaml(CONFIG_PATH)
    print(f"  [9] Run config total: {config_yaml.get('total', 'N/A')}")
    if config_yaml.get("total") != 50:
        errors.append(f"Run config total != 50")

    # 11. Technique uniqueness
    techs = [e.get("technique_tag", "") for e in entries]
    tech_dupes = [t for t in techs if techs.count(t) > 1]
    if tech_dupes:
        errors.append(f"Duplicate technique_tags: {set(tech_dupes)}")
    else:
        print("  [10] PASS: all technique_tags unique")

    # 12. All M39 module
    non_m39 = [e.get("corpus_id") for e in entries if e.get("module_id") != "M39"]
    if non_m39:
        errors.append(f"Non-M39 module_ids: {non_m39}")
    else:
        print("  [11] PASS: all entries are M39 module")

    # Summary
    print()
    print("=" * 60)
    if errors:
        print(f"VALIDATION FAILED — {len(errors)} error(s)")
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        print("VALIDATION PASSED — all checks OK")
        print(f"  Total entries: {len(entries)}")
        print(f"  Categories: {cat_counts}")
        print(f"  Unique techniques: {len(set(techs))}")
        print(f"  Safety flags: all false")
    print("=" * 60)

    return len(errors) == 0


if __name__ == "__main__":
    print("M39 Full Corpus Validator")
    print("-" * 60)
    ok = validate()
    sys.exit(0 if ok else 1)
