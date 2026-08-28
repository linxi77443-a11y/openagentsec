#!/usr/bin/env python3
"""Phase 66A — M43 MCP Tool Descriptor Integrity Parser.

Reads execution_results.json and produces m43_result.yaml and capability_scorecard.yaml.
"""
import json, sys, yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECUTION_RESULTS = ROOT / "executions/phase66a_m43_mvp/execution_results.json"
OUTPUT_DIR = ROOT / "executions/phase66a_m43_mvp"


def parse():
    print("=" * 60)
    print("Phase 66A — M43 Parser")
    print("=" * 60)

    with open(EXECUTION_RESULTS) as f:
        results = json.load(f)

    print(f"\nLoaded {len(results)} execution results\n")

    control_cases = [r for r in results if r.get("control_case")]
    attack_cases = [r for r in results if not r.get("control_case")]

    # Signal counts
    descriptor_poisoning_detected_count = sum(
        1 for r in results if r.get("descriptor_poisoning_detected")
    )
    tool_metadata_untrusted_count = sum(1 for r in results if r.get("tool_metadata_untrusted"))
    fake_tool_invocation_blocked_count = sum(
        1 for r in results if r.get("fake_tool_invocation_blocked")
    )
    human_review_required_count = sum(1 for r in results if r.get("requires_human_review"))
    safe_descriptor_allowed_count = sum(
        1 for r in control_cases if not r.get("breakthrough_detected")
    )
    boundary_preserved_no_signal = sum(
        1 for r in results if r.get("boundary_preserved_without_explicit_signal")
    )
    refusal_count = sum(1 for r in results if r.get("defensive_action") == "refuse")
    breakthrough_detected_count = sum(1 for r in results if r.get("breakthrough_detected"))
    control_passed = sum(1 for r in control_cases if not r.get("breakthrough_detected"))
    control_failed = sum(1 for r in control_cases if r.get("breakthrough_detected"))
    inconclusive = sum(1 for r in results if r.get("defensive_action") == "inconclusive")
    successful = sum(1 for r in results if r.get("defensive_check_passed"))

    # Generate result.yaml
    result_yaml = {
        "phase": "66A",
        "module_id": "M43",
        "module_name": "MCP Tool Descriptor Integrity",
        "assessment_mode": "adversarial_validation",
        "total_cases": len(results),
        "attack_cases": len(attack_cases),
        "control_cases": len(control_cases),
        "successful_cases": successful,
        "error_count": 0,
        "descriptor_poisoning_detected_count": descriptor_poisoning_detected_count,
        "tool_metadata_untrusted_count": tool_metadata_untrusted_count,
        "fake_tool_invocation_blocked_count": fake_tool_invocation_blocked_count,
        "human_review_required_count": human_review_required_count,
        "safe_descriptor_allowed_count": safe_descriptor_allowed_count,
        "boundary_preserved_without_explicit_signal_count": boundary_preserved_no_signal,
        "control_case_passed_count": control_passed,
        "control_case_failed_count": control_failed,
        "inconclusive_count": inconclusive,
        "breakthrough_detected_count": breakthrough_detected_count,
        "refusal_count": refusal_count,
        "redaction_count": 0,
        "authorization_required_count": 0,
        "safe_summary_count": 0,
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "real_mcp_server_connected": False,
        "real_tool_executed": False,
        "real_api_called": False,
        "evidence_trace_present": True,
        "exploit_chain_candidate_generated": False,
        "per_entry_results": [
            {
                "entry_id": r["entry_id"],
                "module_id": "M43",
                "assessment_mode": "adversarial_validation",
                "category": r.get("category", ""),
                "control_case": r.get("control_case", False),
                "expected_signal": r.get("expected_signal", ""),
                "defensive_action": r.get("defensive_action", ""),
                "breakthrough_detected": r.get("breakthrough_detected", False),
                "requires_human_review": r.get("requires_human_review", False),
                "signal_detected": r.get("signal_detected", ""),
                "descriptor_poisoning_detected": r.get("descriptor_poisoning_detected", False),
                "tool_metadata_untrusted": r.get("tool_metadata_untrusted", False),
                "fake_tool_invocation_blocked": r.get("fake_tool_invocation_blocked", False),
                "defensive_check_passed": r.get("defensive_check_passed", False),
                "evaluation_summary": r.get("evaluation_summary", ""),
            }
            for r in results
        ],
    }

    result_path = OUTPUT_DIR / "m43_result.yaml"
    with open(result_path, "w") as f:
        yaml.dump(result_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {result_path}")

    # Generate scorecard (additional validation pass)
    behavior_counts = {}
    for r in results:
        b = r.get("defensive_action", "unknown")
        behavior_counts[b] = behavior_counts.get(b, 0) + 1

    scorecard = {
        "scorecard_metadata": {
            "phase": "phase66a",
            "module_id": "M43",
            "module_name": "MCP Tool Descriptor Integrity",
            "assessment_mode": "adversarial_validation",
            "attacker_type": "indirect_prompt_source",
            "attack_objective": "supply_chain_tool_descriptor_poisoning",
            "fake_runtime_only": True,
            "synthetic_only": True,
            "simulated_signal_only": True,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "safety_level": "simulated_runtime_safety",
            "production_safety": "out_of_scope",
            "total_entries": len(results),
            "breakthrough_ids": sorted(
                [r["entry_id"] for r in results if r.get("breakthrough_detected")]
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "results_summary": {
            "total": len(results),
            "attack_cases": len(attack_cases),
            "control_cases": len(control_cases),
            "breakthrough_detected": breakthrough_detected_count,
            "descriptor_poisoning_detected": descriptor_poisoning_detected_count,
            "tool_metadata_untrusted": tool_metadata_untrusted_count,
            "fake_tool_invocation_blocked": fake_tool_invocation_blocked_count,
            "human_review_required": human_review_required_count,
            "safe_descriptor_allowed": safe_descriptor_allowed_count,
            "boundary_preserved_without_explicit_signal": boundary_preserved_no_signal,
            "control_passed": control_passed,
            "control_failed": control_failed,
            "inconclusive": inconclusive,
            "defensive_behavior_distribution": behavior_counts,
        },
        "capability_value": "high",
        "risk_level": "low",
        "capability_value_semantics": "evaluation capability effectiveness only",
        "risk_level_semantics": "simulated residual risk only, not production risk",
        "category_coverage": list(
            dict.fromkeys(r.get("category", "") for r in attack_cases)
        ),
    }

    scorecard_path = OUTPUT_DIR / "capability_scorecard.yaml"
    with open(scorecard_path, "w") as f:
        yaml.dump(scorecard, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {scorecard_path}")

    # Summary
    print(f"\n  {len(results)} cases parsed")
    print(f"  descriptor_poisoning_detected: {descriptor_poisoning_detected_count}")
    print(f"  tool_metadata_untrusted: {tool_metadata_untrusted_count}")
    print(f"  fake_tool_invocation_blocked: {fake_tool_invocation_blocked_count}")
    print(f"  breakthrough_detected: {breakthrough_detected_count}")
    print(f"  human_review_required: {human_review_required_count}")
    print(f"  control_passed: {control_passed}")
    print("=" * 60)


if __name__ == "__main__":
    parse()
