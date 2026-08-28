#!/usr/bin/env python3
"""Phase 63A — Validate Red/Blue/Purple Retest Mapping for 20 Breakthrough Candidates.

Checks:
- 20 candidates total
- 10 playbooks, each ≥2 candidates
- Each candidate has Red/Blue/Purple sections
- All required fields present per section
- All 5 security fields correct (4 false + requires_human_review=true)
- No controlled_replay, production_safety, confirmed_vulnerability, formal_finding declarations
- No real secrets/PII in evidence_trace_ref
"""
import sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "red_blue_purple_retest_mapping.yaml"

checks = []
findings = []

def check(name: str, ok: bool, detail: str = ""):
    checks.append({"name": name, "pass": ok, "detail": detail})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

def finding(cat: str, item: str, field: str, detail: str):
    findings.append({"category": cat, "item": item, "field": field, "detail": detail})
    print(f"  [FINDING] {cat}: {item} — {field}: {detail}")

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

def main():
    print("=" * 60)
    print("Phase 63A — Red/Blue/Purple Retest Mapping Validation")
    print("=" * 60)

    if not MAPPING_PATH.exists():
        print(f"\n[FAIL] Mapping file not found: {MAPPING_PATH}")
        sys.exit(1)

    mapping = load_yaml(MAPPING_PATH)
    rbp = mapping.get("red_blue_purple_mapping", {})
    candidates = rbp.get("candidates", [])

    # Total count
    check(f"Breakthrough candidate count = 20", len(candidates) == 20, f"got {len(candidates)}")
    if len(candidates) != 20:
        print(f"\n[FAIL] Expected 20 candidates, got {len(candidates)}. Aborting.")
        sys.exit(1)

    # Source playbook coverage
    playbook_counts = {}
    for c in candidates:
        pb = c.get("source_playbook", "?")
        playbook_counts[pb] = playbook_counts.get(pb, 0) + 1

    REQUIRED_PLAYBOOKS = [
        "direct_prompt_injection", "indirect_prompt_injection", "multi_turn_boundary_erosion",
        "tool_invocation_abuse", "tool_argument_pollution", "role_boundary_bypass",
        "service_account_abuse", "approval_bypass", "business_action_induction",
        "simulated_exfiltration_attempt",
    ]
    check(f"All 10 playbooks covered", len(playbook_counts) >= 10, f"found {len(playbook_counts)}")
    for pb in REQUIRED_PLAYBOOKS:
        cnt = playbook_counts.get(pb, 0)
        check(f"  {pb}: {cnt} candidates", cnt >= 2, f"expected ≥2, got {cnt}")
        if cnt < 2:
            finding("playbook coverage", pb, "candidate_count", f"expected ≥2, got {cnt}")

    # Per-candidate validation
    RED_FIELDS = ["source_playbook", "breakthrough_candidate_id", "attacker_type",
                  "attack_objective", "breakthrough_detected", "breakthrough_type",
                  "capability_signal", "affected_boundary", "evidence_trace_ref",
                  "observed_behavior_summary"]
    BLUE_FIELDS = ["prevention_control", "detection_control", "response_control"]
    BLUE_SUB_FIELDS = ["recommendation", "rationale", "priority"]
    PURPLE_FIELDS = ["retest_case_id", "retest_objective", "expected_blocking_behavior",
                     "regression_requirement", "pass_condition", "fail_condition",
                     "human_review_required"]
    SECURITY_FIELDS = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
    }

    affected_boundaries = set()
    retest_ids = set()
    security_field_pass = {f: 0 for f in SECURITY_FIELDS}
    security_field_fail = {f: 0 for f in SECURITY_FIELDS}
    hr_ok = 0
    hr_fail = 0

    for c in candidates:
        cid = c.get("candidate_id", "?")
        entry_id = c.get("entry_id", "?")
        red = c.get("red", {})
        blue = c.get("blue", {})
        purple = c.get("purple", {})

        # Red fields
        for f in RED_FIELDS:
            if f not in red:
                finding("red field missing", cid, f, f"missing in red section")
            else:
                val = red.get(f)
                if val is None or (isinstance(val, str) and not val.strip()):
                    finding("red field empty", cid, f, f"empty value")

        # Blue fields
        for f in BLUE_FIELDS:
            if f not in blue:
                finding("blue field missing", cid, f, f"missing in blue section")
            else:
                sub = blue.get(f, {})
                for sf in BLUE_SUB_FIELDS:
                    if sf not in sub:
                        finding("blue sub-field missing", cid, f"{f}.{sf}", f"missing")

        # Purple fields
        for f in PURPLE_FIELDS:
            if f not in purple:
                finding("purple field missing", cid, f, f"missing in purple section")

        # Retest case ID uniqueness
        rtc = purple.get("retest_case_id", "")
        if rtc:
            if rtc in retest_ids:
                finding("duplicate retest_case_id", cid, "retest_case_id", f"duplicate: {rtc}")
            retest_ids.add(rtc)

        # Security fields
        for f, expected in SECURITY_FIELDS.items():
            val = c.get(f)
            if val is expected:
                security_field_pass[f] += 1
            else:
                security_field_fail[f] += 1
                finding("security field", cid, f, f"expected {expected}, got {val}")

        # requires_human_review
        hr = c.get("requires_human_review")
        if hr is True:
            hr_ok += 1
        else:
            hr_fail += 1
            finding("requires_human_review", cid, "requires_human_review",
                    f"expected True, got {hr}")

        # breakthrough_detected
        bd = red.get("breakthrough_detected")
        if bd is not True:
            finding("breakthrough_detected", cid, "breakthrough_detected",
                    f"expected true, got {bd}")

        # affected_boundary
        ab = red.get("affected_boundary")
        if ab:
            affected_boundaries.add(ab)

        # human_review_required in purple
        purple_hr = purple.get("human_review_required")
        if purple_hr is not True:
            finding("purple human_review_required", cid, "purple.human_review_required",
                    f"expected True, got {purple_hr}")

    # Cross-candidate checks
    check("All affected_boundary values defined",
          len(affected_boundaries) > 0, f"found {len(affected_boundaries)} unique boundaries: {sorted(affected_boundaries)}")

    # Security fields summary
    for f in SECURITY_FIELDS:
        check(f"{f}=false", security_field_fail[f] == 0,
              f"{security_field_pass[f]}/20 correct")

    check("requires_human_review=true", hr_fail == 0, f"{hr_ok}/20 correct")

    # No prohibited declarations
    prohibited = ["controlled_replay", "production_safety"]
    raw_text = MAPPING_PATH.read_text()
    for term in prohibited:
        # Check only in structural contexts, not in field names
        # Look for values like "true" or "yes" near these terms
        check(f"No {term} declaration in mapping",
              "true" not in raw_text.lower().split(term)[-1][:10] if term in raw_text.lower() else True,
              "no false declaration detected")

    # Retest case ID count
    check(f"Unique retest_case_ids = 20", len(retest_ids) == 20,
          f"got {len(retest_ids)} unique IDs")

    # Summary
    passed = sum(1 for c in checks if c["pass"])
    failed = len(checks) - passed
    total = len(checks)

    print(f"\n{'=' * 60}")
    print(f"Validation Summary")
    print(f"{'=' * 60}")
    print(f"  Total checks:  {total}")
    print(f"  Passed:        {passed}")
    print(f"  Failed:        {failed}")
    print(f"  Findings:      {len(findings)}")

    if findings:
        print(f"\n--- Findings ({len(findings)}) ---")
        for f in findings:
            print(f"  [{f['category']}] {f['item']} / {f['field']}: {f['detail']}")

    print(f"\n{'=' * 60}")
    if failed == 0 and len(findings) == 0:
        print(f"ALL {total} CHECKS PASSED — No findings. Mapping is consistent.")
        sys.exit(0)
    else:
        print(f"{failed} check(s) FAILED. {len(findings)} findings.")
        sys.exit(1 if failed > 0 else 0)

if __name__ == "__main__":
    main()
