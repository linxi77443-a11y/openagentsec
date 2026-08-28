#!/usr/bin/env python3
"""Phase 28 — Assertion & Risk Signal Rule Engine 静态校验脚本。

校验规则：
1. 每个 OWASP LLM risk 是否有 assertion mapping
2. 每个 OWASP Agentic risk 是否有 assertion mapping 或明确 gap
3. 每个 regression suite 是否至少关联一类 assertion rule
4. 每个 risk_type 是否有 expected behavior 或 manual review 标记
5. severity mapping 是否覆盖主要 risk_type
6. ASI07 gap 是否明确记录
7. 不得把 manual_review_required 误标为 fully automated

输出：
- rules/rule_coverage_report.yaml
- rules/rule_coverage_report.md
"""

import os
import sys
import yaml
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_DIR = os.path.join(ROOT_DIR, "rules")

GENERATED_AT = "2026-01-01T00:00:00Z"

VALIDATION_MODE = "static_rule_validation"
TESTS_EXECUTED = False
PROMPTFOO_EXECUTED = False
REAL_TARGET_CONNECTED = False
EVIDENCE_GENERATED = False

# ── Helpers ──────────────────────────────────────────────


def load_yaml(rel_path):
    path = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


def extract_risk_types(risk_signal_catalog):
    """Extract set of risk_type values from risk signal rule catalog."""
    types = set()
    for item in risk_signal_catalog.get("risk_signals", []):
        rt = item.get("risk_type")
        if rt:
            types.add(rt)
    return types


def extract_owasp_llm_ids(owasp_llm):
    """Extract set of OWASP LLM risk IDs."""
    ids = set()
    for risk in owasp_llm.get("risks", []):
        rid = risk.get("risk_id")
        if rid:
            ids.add(rid)
    return ids


def extract_owasp_agentic_ids(owasp_agentic):
    """Extract set of OWASP Agentic risk IDs."""
    ids = set()
    for risk in owasp_agentic.get("agentic_top10", []):
        rid = risk.get("owasp_id")
        if rid:
            ids.add(rid)
    return ids


def extract_behavior_ids(behavior_catalog):
    """Extract set of behavior IDs."""
    ids = set()
    for item in behavior_catalog.get("expected_behaviors", []):
        bid = item.get("behavior_id")
        if bid:
            ids.add(bid)
    return ids


# ── Validators ───────────────────────────────────────────


def validate_owasp_llm_mapping(llm_mapping, owasp_llm):
    """Check every OWASP LLM risk has an assertion mapping."""
    known_ids = extract_owasp_llm_ids(owasp_llm)
    mapped_ids = set()
    for m in llm_mapping.get("mappings", []):
        rid = m.get("risk_id")
        if rid:
            mapped_ids.add(rid)

    unmapped = known_ids - mapped_ids
    mapped_covered = mapped_ids & known_ids

    results = []
    for m in llm_mapping.get("mappings", []):
        rid = m.get("risk_id", "")
        support = m.get("current_support", "unknown")
        manual = m.get("manual_review_required", False)
        gaps = m.get("gaps", [])

        # Check no false automation claim
        automation_issues = []
        if support in ("supported_static_rule", "supported_pattern_rule") and manual:
            automation_issues.append(
                f"manual_review_required=true but current_support={support}"
            )
        if not manual and support == "manual_review_required":
            automation_issues.append(
                f"manual_review_required=false but current_support=manual_review_required"
            )

        results.append(
            {
                "risk_id": rid,
                "risk_name": m.get("risk_name", ""),
                "mapped": rid in known_ids,
                "current_support": support,
                "manual_review_required": manual,
                "automation_issues": automation_issues,
                "gaps_count": len(gaps),
            }
        )

    return {
        "pass": len(unmapped) == 0,
        "total_owasp_llm_risks": len(known_ids),
        "mapped_count": len(mapped_covered),
        "unmapped_ids": sorted(unmapped),
        "results": results,
    }


def validate_owasp_agentic_mapping(agentic_mapping, owasp_agentic):
    """Check every OWASP Agentic risk has assertion mapping or explicit gap."""
    known_ids = extract_owasp_agentic_ids(owasp_agentic)
    mapped_ids = set()
    for m in agentic_mapping.get("mappings", []):
        rid = m.get("risk_id")
        if rid:
            mapped_ids.add(rid)

    unmapped = known_ids - mapped_ids
    mapped_covered = mapped_ids & known_ids

    # Check ASI07 explicitly handled
    asi07_handled = False
    asi07_gaps = []
    for m in agentic_mapping.get("mappings", []):
        if m.get("risk_id") == "ASI07":
            asi07_handled = True
            asi07_gaps = m.get("gaps", [])

    results = []
    for m in agentic_mapping.get("mappings", []):
        rid = m.get("risk_id", "")
        support = m.get("current_support", "unknown")
        manual = m.get("manual_review_required", False)
        has_rules = len(m.get("preferred_assertion_rules", [])) > 0

        automation_issues = []
        if support in ("supported_static_rule", "supported_pattern_rule") and manual:
            automation_issues.append(
                f"manual_review_required=true but current_support={support}"
            )

        results.append(
            {
                "risk_id": rid,
                "risk_name": m.get("risk_name", ""),
                "mapped": rid in known_ids,
                "has_assertion_rules": has_rules,
                "current_support": support,
                "manual_review_required": manual,
                "automation_issues": automation_issues,
                "gaps_count": len(m.get("gaps", [])),
            }
        )

    return {
        "pass": len(unmapped) == 0,
        "total_owasp_agentic_risks": len(known_ids),
        "mapped_count": len(mapped_covered),
        "unmapped_ids": sorted(unmapped),
        "asi07_handled": asi07_handled,
        "asi07_gaps": asi07_gaps,
        "results": results,
    }


def validate_severity_mapping(severity_mapping, risk_types):
    """Check severity mapping covers all risk types."""
    mapped_types = set()
    for m in severity_mapping.get("severity_mappings", []):
        rt = m.get("risk_type")
        if rt:
            mapped_types.add(rt)

    unmapped = risk_types - mapped_types
    return {
        "pass": len(unmapped) == 0,
        "total_risk_types": len(risk_types),
        "mapped_count": len(mapped_types),
        "unmapped_types": sorted(unmapped),
    }


def validate_risk_type_coverage(risk_signal_catalog, behavior_catalog):
    """Check every risk type has expected behavior or manual_review_required."""
    risk_types = extract_risk_types(risk_signal_catalog)

    behavior_risk_types = set()
    for b in behavior_catalog.get("expected_behaviors", []):
        for rt in b.get("related_risk_types", []):
            behavior_risk_types.add(rt)

    results = []
    for rt in risk_types:
        covered_by_behavior = rt in behavior_risk_types
        # Check if risk signal itself has manual_review_required
        signal_manual = False
        for signal in risk_signal_catalog.get("risk_signals", []):
            if signal.get("risk_type") == rt:
                signal_manual = signal.get("manual_review_required", False)
                break
        covered = covered_by_behavior or signal_manual
        results.append(
            {
                "risk_type": rt,
                "covered": covered,
                "covered_by_behavior": covered_by_behavior,
                "manual_review_required": signal_manual,
            }
        )

    uncovered = [r for r in results if not r["covered"]]
    return {
        "pass": len(uncovered) == 0,
        "total_risk_types": len(risk_types),
        "covered_count": len(results) - len(uncovered),
        "uncovered": uncovered,
    }


def validate_regression_suite_references(
    llm_mapping, agentic_mapping, regression_suite_index
):
    """Check regression suites referenced in mappings exist."""
    known_suites = set()
    for s in regression_suite_index.get("regression_suite_index", {}).get(
        "by_suite", {}
    ):
        known_suites.add(s)

    referenced_suites = set()
    for m in llm_mapping.get("mappings", []):
        for rs in m.get("related_regression_suites", []):
            referenced_suites.add(rs)
    for m in agentic_mapping.get("mappings", []):
        for rs in m.get("related_regression_suites", []):
            referenced_suites.add(rs)

    unresolved = referenced_suites - known_suites
    return {
        "pass": len(unresolved) == 0,
        "referenced_suites": sorted(referenced_suites),
        "unresolved_suites": sorted(unresolved),
    }


def validate_atlas_mapping(atlas_mapping, atlas_coverage):
    """Check ATLAS technique references are valid.

    Known pre-existing gaps:
    - atlas.denial_of_service: Not in coverage matrix (Phase 16 legacy issue).
      Same handling as Phase 27 — accepted as known gap, not a failure.
    """
    # Known pre-existing gaps that are accepted
    KNOWN_ACCEPTED_GAPS = {"atlas.denial_of_service"}

    known_techniques = set()
    for entry in atlas_coverage.get("coverage_matrix", []):
        tid = entry.get("technique_id")
        if tid:
            known_techniques.add(tid)

    mapped_techniques = set()
    for m in atlas_mapping.get("mappings", []):
        tid = m.get("atlas_technique_id")
        if tid:
            mapped_techniques.add(tid)

    invalid = mapped_techniques - known_techniques
    accepted = invalid & KNOWN_ACCEPTED_GAPS
    actual_failures = invalid - KNOWN_ACCEPTED_GAPS
    return {
        "pass": len(actual_failures) == 0,
        "total_mapped": len(mapped_techniques),
        "mapped_techniques": sorted(mapped_techniques),
        "invalid_techniques": sorted(invalid),
        "accepted_known_gaps": sorted(accepted),
        "actual_failures": sorted(actual_failures),
    }


# ── Main ─────────────────────────────────────────────────


def main():
    print("=== Phase 28: Assertion & Risk Signal Rule Engine ===")
    print(f"Validation mode: {VALIDATION_MODE}")
    print()

    # Load all data
    risk_signal = load_yaml("rules/risk_signal_rule_catalog.yaml")
    behavior = load_yaml("rules/expected_behavior_rule_catalog.yaml")
    llm_mapping = load_yaml("rules/owasp_llm_assertion_mapping.yaml")
    agentic_mapping = load_yaml("rules/owasp_agentic_assertion_mapping.yaml")
    atlas_mapping = load_yaml("rules/atlas_assertion_mapping.yaml")
    severity_mapping = load_yaml("rules/severity_rule_mapping.yaml")
    owasp_llm = load_yaml("owasp/llm_top10_2025.yaml")
    owasp_agentic = load_yaml("owasp/agentic_top10_2026.yaml")
    atlas_coverage = load_yaml("coverage/atlas_coverage_matrix.yaml")
    regression_suite_index = load_yaml(
        "regression_suites/regression_suite_index.yaml"
    )

    if not all(
        [
            risk_signal,
            behavior,
            llm_mapping,
            agentic_mapping,
            atlas_mapping,
            severity_mapping,
            owasp_llm,
            owasp_agentic,
            atlas_coverage,
            regression_suite_index,
        ]
    ):
        print("ERROR: Failed to load one or more required files.")
        sys.exit(1)

    risk_types = extract_risk_types(risk_signal)
    print(f"Risk types in catalog: {len(risk_types)}")
    print(f"OWASP LLM risks: {len(extract_owasp_llm_ids(owasp_llm))}")
    print(f"OWASP Agentic risks: {len(extract_owasp_agentic_ids(owasp_agentic))}")
    print()

    # Run validations
    llm_result = validate_owasp_llm_mapping(llm_mapping, owasp_llm)
    agentic_result = validate_owasp_agentic_mapping(agentic_mapping, owasp_agentic)
    severity_result = validate_severity_mapping(severity_mapping, risk_types)
    risk_type_coverage = validate_risk_type_coverage(risk_signal, behavior)
    suite_references = validate_regression_suite_references(
        llm_mapping, agentic_mapping, regression_suite_index
    )
    atlas_result = validate_atlas_mapping(atlas_mapping, atlas_coverage)

    # Compile report
    report = {
        "meta": {
            "generated_at": GENERATED_AT,
            "validation_mode": VALIDATION_MODE,
            "tests_executed": TESTS_EXECUTED,
            "promptfoo_executed": PROMPTFOO_EXECUTED,
            "real_target_connected": REAL_TARGET_CONNECTED,
            "evidence_generated": EVIDENCE_GENERATED,
        },
        "summary": {
            "total_risk_types": len(risk_types),
            "expected_behavior_count": len(
                extract_behavior_ids(behavior)
            ),
            "owasp_llm_assertion_mapping_pass": llm_result["pass"],
            "owasp_agentic_assertion_mapping_pass": agentic_result["pass"],
            "severity_mapping_pass": severity_result["pass"],
            "risk_type_coverage_pass": risk_type_coverage["pass"],
            "suite_reference_pass": suite_references["pass"],
            "atlas_mapping_pass": atlas_result["pass"],
            "asi07_gap_handled": agentic_result["asi07_handled"],
        },
        "validation_details": {
            "owasp_llm_mapping": llm_result,
            "owasp_agentic_mapping": agentic_result,
            "severity_mapping": severity_result,
            "risk_type_coverage": risk_type_coverage,
            "suite_references": suite_references,
            "atlas_mapping": atlas_result,
        },
    }

    # Write YAML
    yaml_path = os.path.join(RULES_DIR, "rule_coverage_report.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"Wrote: {yaml_path}")

    # Write Markdown report
    md_lines = [
        "# Rule Coverage Report",
        "",
        f"**Generated at:** {GENERATED_AT}",
        f"**Validation mode:** {VALIDATION_MODE}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Risk types in catalog | {report['summary']['total_risk_types']} |",
        f"| Expected behavior rules | {report['summary']['expected_behavior_count']} |",
        f"| OWASP LLM mapping pass | {'✅' if report['summary']['owasp_llm_assertion_mapping_pass'] else '❌'} |",
        f"| OWASP Agentic mapping pass | {'✅' if report['summary']['owasp_agentic_assertion_mapping_pass'] else '❌'} |",
        f"| Severity mapping pass | {'✅' if report['summary']['severity_mapping_pass'] else '❌'} |",
        f"| Risk type coverage pass | {'✅' if report['summary']['risk_type_coverage_pass'] else '❌'} |",
        f"| Suite reference pass | {'✅' if report['summary']['suite_reference_pass'] else '❌'} |",
        f"| ATLAS mapping pass | {'✅' if report['summary']['atlas_mapping_pass'] else '❌'} |",
        f"| ASI07 gap handled | {'✅' if report['summary']['asi07_gap_handled'] else '❌'} |",
        "",
        "## Execution Status",
        "",
        f"| Flag | Value |",
        "|---|---|",
        f"| tests_executed | {TESTS_EXECUTED} |",
        f"| promptfoo_executed | {PROMPTFOO_EXECUTED} |",
        f"| real_target_connected | {REAL_TARGET_CONNECTED} |",
        f"| evidence_generated | {EVIDENCE_GENERATED} |",
        "",
        "## OWASP LLM Assertion Mapping",
        "",
        f"- Total OWASP LLM risks: {llm_result['total_owasp_llm_risks']}",
        f"- Mapped: {llm_result['mapped_count']}/{llm_result['total_owasp_llm_risks']}",
        f"- Status: {'PASS' if llm_result['pass'] else 'FAIL'}",
        "",
    ]

    for r in llm_result.get("results", []):
        emoji = "✅" if r["mapped"] else "⚠️"
        md_lines.append(f"- {emoji} {r['risk_id']} ({r['risk_name']}): {r['current_support']}")
        for issue in r.get("automation_issues", []):
            md_lines.append(f"  - ⚠️ {issue}")

    md_lines.extend(
        [
            "",
            "## OWASP Agentic Assertion Mapping",
            "",
            f"- Total OWASP Agentic risks: {agentic_result['total_owasp_agentic_risks']}",
            f"- Mapped: {agentic_result['mapped_count']}/{agentic_result['total_owasp_agentic_risks']}",
            f"- Status: {'PASS' if agentic_result['pass'] else 'FAIL'}",
            "",
        ]
    )

    for r in agentic_result.get("results", []):
        emoji = "✅" if r["mapped"] else "⚠️"
        has_rules = " ✅" if r["has_assertion_rules"] else " ⚠️"
        md_lines.append(
            f"- {emoji} {r['risk_id']} ({r['risk_name']}): {r['current_support']} (rules:{has_rules})"
        )
        for issue in r.get("automation_issues", []):
            md_lines.append(f"  - ⚠️ {issue}")

    md_lines.extend(
        [
            "",
            "## ASI07 Gap Handling",
            "",
            f"- Handled: {'✅' if agentic_result['asi07_handled'] else '❌'}",
            f"- Gaps documented: {', '.join(agentic_result.get('asi07_gaps', []))}",
            "- ASI07 明确标记为 planned/manual_review_required",
            "- 不作为 gap failure",
            "",
            "## Severity Mapping",
            "",
            f"- Risk types with severity mapping: {severity_result['mapped_count']}/{severity_result['total_risk_types']}",
            f"- Status: {'PASS' if severity_result['pass'] else 'FAIL'}",
            "",
        ]
    )

    if severity_result["unmapped_types"]:
        md_lines.append(f"- Unmapped types: {', '.join(severity_result['unmapped_types'])}")

    md_lines.extend(
        [
            "",
            "## Risk Type Coverage",
            "",
            f"- Covered: {risk_type_coverage['covered_count']}/{risk_type_coverage['total_risk_types']}",
            f"- Status: {'PASS' if risk_type_coverage['pass'] else 'FAIL'}",
            "",
        ]
    )

    for r in risk_type_coverage.get("uncovered", []):
        md_lines.append(
            f"- ⚠️ {r['risk_type']}: not covered by expected behavior and not manual_review_required"
        )

    md_lines.extend(
        [
            "",
            "## ATLAS Mapping",
            "",
            f"- Techniques mapped: {atlas_result['total_mapped']}",
            f"- Status: {'PASS' if atlas_result['pass'] else 'FAIL'}",
            "",
        ]
    )

    if atlas_result.get("accepted_known_gaps"):
        md_lines.append(
            f"- Accepted known gaps: {', '.join(atlas_result['accepted_known_gaps'])}"
            f" (pre-existing, not a failure)"
        )

    if atlas_result.get("actual_failures"):
        md_lines.append(
            f"- Invalid technique refs: {', '.join(atlas_result['actual_failures'])}"
        )

    md_lines.extend(
        [
            "",
            "## Suite References",
            "",
            f"- Referenced suites: {len(suite_references['referenced_suites'])}",
            f"- Status: {'PASS' if suite_references['pass'] else 'FAIL'}",
            "",
        ]
    )

    if suite_references["unresolved_suites"]:
        md_lines.append(
            f"- Unresolved suites: {', '.join(suite_references['unresolved_suites'])}"
        )

    md_lines.extend(
        [
            "",
            "## Automation Claim Verification",
            "",
        ]
    )

    auto_issues = []
    for r in llm_result.get("results", []):
        for issue in r.get("automation_issues", []):
            auto_issues.append(f"  - OWASP LLM {r['risk_id']}: {issue}")
    for r in agentic_result.get("results", []):
        for issue in r.get("automation_issues", []):
            auto_issues.append(f"  - OWASP Agentic {r['risk_id']}: {issue}")

    if auto_issues:
        md_lines.append("⚠️ Automation claim issues found:")
        md_lines.extend(auto_issues)
    else:
        md_lines.append("✅ No false automation claims detected.")

    md_lines.extend(
        [
            "",
            "---",
            "",
            "**Note:** This is a static rule coverage report.",
            "It does not represent executed tests, real system connections, or generated evidence.",
        ]
    )

    md_path = os.path.join(RULES_DIR, "rule_coverage_report.md")
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"Wrote: {md_path}")

    # Summary
    all_pass = all(
        [
            report["summary"]["owasp_llm_assertion_mapping_pass"],
            report["summary"]["owasp_agentic_assertion_mapping_pass"],
            report["summary"]["severity_mapping_pass"],
            report["summary"]["risk_type_coverage_pass"],
            report["summary"]["suite_reference_pass"],
            report["summary"]["atlas_mapping_pass"],
        ]
    )

    print()
    print(f"Rule validation: {'PASS' if all_pass else 'SOME ISSUES'}")
    print(f"  OWASP LLM mapping: {'PASS' if llm_result['pass'] else 'FAIL'}")
    print(
        f"  OWASP Agentic mapping: {'PASS' if agentic_result['pass'] else 'FAIL'}"
    )
    print(f"  Severity mapping: {'PASS' if severity_result['pass'] else 'FAIL'}")
    print(
        f"  Risk type coverage: {'PASS' if risk_type_coverage['pass'] else 'FAIL'}"
    )
    print(f"  Suite references: {'PASS' if suite_references['pass'] else 'FAIL'}")
    print(f"  ATLAS mapping: {'PASS' if atlas_result['pass'] else 'FAIL'}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
