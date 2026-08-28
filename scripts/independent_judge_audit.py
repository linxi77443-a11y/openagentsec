#!/usr/bin/env python3
"""
Independent Judge Agent — 8 modules × 6 checks
Reads delivery artifacts with context: "none" (no development context).
"""
import yaml, json, os, sys
from collections import Counter

BASE = "/Users/linxi/Desktop/ai-workspace/AI学习/AI安全评估探索/adversarial_playbooks"
MODULES = ["m01", "m02", "m04", "m07", "m12", "m24", "m25", "m35"]

# Safety fields
MUST_BE_FALSE = {
    "confirmed_vulnerability", "real_system_connection_allowed",
    "real_api_call_allowed", "production_safety_claimed",
    "formal_finding_allowed", "attack_execution_allowed",
}
MUST_BE_TRUE = {
    "synthetic_only", "red_team_engine_not_executable",
    "dashboard_not_execution_interface", "requires_human_review",
}

def get_entries(pb):
    """Extract entries from playbook regardless of structure."""
    if "entries" in pb:
        return pb["entries"]
    for key in pb:
        if isinstance(pb[key], list) and len(pb[key]) > 0 and isinstance(pb[key][0], dict):
            return pb[key]
    return []

def get_entry_id(e):
    return e.get("entry_id", e.get("case_id", e.get("corpus_id", "")))

def get_attack_entries(entries):
    """Filter attack (non-control) entries."""
    result = []
    for e in entries:
        cat = e.get("category", "")
        poc = e.get("positive_or_control", "")
        if cat == "control" or poc == "control":
            continue
        result.append(e)
    return result

def get_prompt(e):
    """Get prompt text from entry regardless of field name."""
    return e.get("prompt", e.get("prompt_text", e.get("user_goal", "")))

# ═══════════════════════════════════════════════════════════
# CHECK 1: Entry count = 75
# ═══════════════════════════════════════════════════════════
def check1_entry_count(pb, entries):
    count = len(entries)
    declared = pb.get("total_entries", count)
    passed = count == 75
    return passed, f"entries={count}, declared_total={declared}"

# ═══════════════════════════════════════════════════════════
# CHECK 2: File consistency
# ═══════════════════════════════════════════════════════════
def check2_file_consistency(mod_dir, entries, pb):
    issues = []
    pb_count = len(entries)

    # Check execution_results.json
    er_path = os.path.join(mod_dir, "execution_results.json")
    if os.path.exists(er_path):
        with open(er_path) as f:
            er = json.load(f)
        er_total = er.get("total_entries", er.get("execution_summary", {}).get("total_entries", None))
        per_entry = er.get("per_entry_results", [])

        if er_total is not None and er_total != pb_count:
            issues.append(f"execution_results total={er_total} != playbook={pb_count}")
        if len(per_entry) != pb_count:
            issues.append(f"per_entry_results count={len(per_entry)} != playbook={pb_count}")

        # Check entry_ids match
        pb_ids = {get_entry_id(e) for e in entries if get_entry_id(e)}
        er_ids = {r.get("entry_id", "") for r in per_entry if r.get("entry_id")}
        if pb_ids and er_ids:
            missing = pb_ids - er_ids
            extra = er_ids - pb_ids
            if missing:
                issues.append(f"per_entry missing {len(missing)} IDs: {list(missing)[:3]}")
            if extra:
                issues.append(f"per_entry has {len(extra)} extra IDs")
    else:
        issues.append("execution_results.json MISSING")

    # Check capability_scorecard.yaml
    sc_path = os.path.join(mod_dir, "capability_scorecard.yaml")
    if os.path.exists(sc_path):
        with open(sc_path) as f:
            sc = yaml.safe_load(f)
        # Check various locations for total
        sc_total = None
        for path in [
            sc.get("results_summary", {}).get("total_entries"),
            sc.get("assessment_metadata", {}).get("total_entries"),
            sc.get("total_entries"),
        ]:
            if path is not None:
                sc_total = path
                break
        if sc_total is not None and sc_total != pb_count:
            issues.append(f"scorecard total={sc_total} != playbook={pb_count}")
    else:
        issues.append("capability_scorecard.yaml MISSING")

    passed = len(issues) == 0
    return passed, "; ".join(issues) if issues else "all files consistent"

# ═══════════════════════════════════════════════════════════
# CHECK 3: Safety fields
# ═══════════════════════════════════════════════════════════
def check3_safety_fields(pb, entries):
    issues = []

    # Check top-level safety flags in playbook
    safety_flags = pb.get("safety_flags", {})
    for field in MUST_BE_FALSE:
        val = safety_flags.get(field)
        if val is not None and val != False:
            issues.append(f"safety_flags.{field}={val} (should be false)")

    # Check individual entries
    for e in entries:
        eid = get_entry_id(e)
        for field in MUST_BE_FALSE:
            val = e.get(field)
            if val is not None and val != False:
                issues.append(f"{eid}.{field}={val}")

    passed = len(issues) == 0
    return passed, "; ".join(issues[:5]) if issues else "all safety fields clean"

# ═══════════════════════════════════════════════════════════
# CHECK 4: SIM placeholders in attack entries
# ═══════════════════════════════════════════════════════════
def check4_sim_placeholders(entries):
    attacks = get_attack_entries(entries)
    missing = []
    for i, e in enumerate(attacks):
        prompt = get_prompt(e)
        # Check all text fields for SIM placeholders
        has_sim = False
        for k, v in e.items():
            if isinstance(v, str) and "<SIM_" in v:
                has_sim = True
                break
        if not has_sim:
            missing.append(get_entry_id(e) or f"index_{i}")

    passed = len(missing) == 0
    detail = f"{len(attacks)} attack entries, {len(missing)} without <SIM_...>"
    if missing:
        detail += f" (first 5: {missing[:5]})"
    return passed, detail

# ═══════════════════════════════════════════════════════════
# CHECK 5: New vectors have substance (no duplicates)
# ═══════════════════════════════════════════════════════════
def check5_new_vectors_substance(entries):
    attacks = get_attack_entries(entries)
    ids = [get_entry_id(e) for e in attacks]
    prompts = [get_prompt(e) for e in attacks]

    issues = []

    # Check duplicate IDs
    id_counts = Counter(ids)
    dupes = {k: v for k, v in id_counts.items() if v > 1}
    if dupes:
        issues.append(f"Duplicate IDs: {list(dupes.keys())[:5]}")

    # Check duplicate prompts (exact match)
    prompt_counts = Counter(prompts)
    prompt_dupes = {k: v for k, v in prompt_counts.items() if v > 1 and k}
    if prompt_dupes:
        issues.append(f"Duplicate prompts: {len(prompt_dupes)} groups")

    # Check empty prompts
    empty = [i for i, p in enumerate(prompts) if not p.strip()]
    if empty:
        issues.append(f"Empty prompts at {empty[:5]}")

    # Check entry_id uniqueness
    empty_ids = [i for i, eid in enumerate(ids) if not eid.strip()]
    if empty_ids:
        issues.append(f"Empty IDs at {len(empty_ids)} entries")

    passed = len(issues) == 0
    return passed, "; ".join(issues) if issues else f"{len(attacks)} unique attack vectors, no duplicates"

# ═══════════════════════════════════════════════════════════
# CHECK 6: Scorecard consistency
# ═══════════════════════════════════════════════════════════
def check6_scorecard_consistency(mod_dir, entries):
    sc_path = os.path.join(mod_dir, "capability_scorecard.yaml")
    if not os.path.exists(sc_path):
        return True, "no scorecard file (skipped)"

    with open(sc_path) as f:
        sc = yaml.safe_load(f)

    attacks = get_attack_entries(entries)
    controls = [e for e in entries if e.get("category") == "control" or e.get("positive_or_control") == "control"]

    issues = []

    # Check category counts match
    pb_cats = Counter(e.get("category", "unknown") for e in entries)

    # Check if scorecard has category breakdown
    for key in ["category_breakdown", "categories", "results_by_category"]:
        if key in sc:
            sc_cats = sc[key]
            if isinstance(sc_cats, dict):
                for cat, count in pb_cats.items():
                    sc_count = sc_cats.get(cat, {})
                    if isinstance(sc_count, dict):
                        sc_count = sc_count.get("count", 0)
                    if isinstance(sc_count, int) and sc_count != count:
                        issues.append(f"category {cat}: playbook={count} scorecard={sc_count}")
            break

    passed = len(issues) == 0
    return passed, "; ".join(issues) if issues else "scorecard consistent with playbook"


# ═══════════════════════════════════════════════════════════
# MAIN: Run all checks
# ═══════════════════════════════════════════════════════════
def run_judge():
    print("=" * 70)
    print("  INDEPENDENT JUDGE AGENT — 8 MODULE AUDIT")
    print("  Context: NONE (no development context loaded)")
    print("=" * 70)
    print()

    results = {}
    all_pass = True

    for mod in MODULES:
        mod_dir = os.path.join(BASE, f"{mod}_full_corpus")
        pb_path = os.path.join(mod_dir, "playbook.yaml")

        if not os.path.exists(pb_path):
            print(f"  [{mod}] SKIP — playbook.yaml not found")
            continue

        with open(pb_path) as f:
            pb = yaml.safe_load(f)
        entries = get_entries(pb)

        print(f"  ┌─── {mod.upper()} ─── ({len(entries)} entries)")

        checks = [
            ("1. Entry Count",        check1_entry_count(pb, entries)),
            ("2. File Consistency",   check2_file_consistency(mod_dir, entries, pb)),
            ("3. Safety Fields",      check3_safety_fields(pb, entries)),
            ("4. SIM Placeholders",   check4_sim_placeholders(entries)),
            ("5. Vector Substance",   check5_new_vectors_substance(entries)),
            ("6. Scorecard Match",    check6_scorecard_consistency(mod_dir, entries)),
        ]

        mod_pass = True
        for name, (passed, detail) in checks:
            icon = "✅" if passed else "❌"
            print(f"  │  {icon} {name}: {detail}")
            if not passed:
                mod_pass = False
                all_pass = False

        results[mod] = mod_pass
        status = "PASS" if mod_pass else "FAIL"
        print(f"  └── {status}")
        print()

    # Summary
    print("=" * 70)
    passed_count = sum(1 for v in results.values() if v)
    failed_count = sum(1 for v in results.values() if not v)
    print(f"  SUMMARY: {passed_count} PASS / {failed_count} FAIL / {len(results)} total")

    if all_pass:
        print("  🟢 ALL MODULES PASS INDEPENDENT JUDGE REVIEW")
    else:
        failed = [m for m, v in results.items() if not v]
        print(f"  🔴 FAILED modules: {failed}")
        print("  → Correction instructions generated below")

    print("=" * 70)
    return all_pass


if __name__ == "__main__":
    success = run_judge()
    sys.exit(0 if success else 1)
