#!/usr/bin/env python3
"""Phase 67A — M48 RAG Document Poisoning and Instruction Boundary Parser.

Reads execution_results.json and produces m48_result.yaml and capability_scorecard.yaml.
"""
import json, sys, yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXECUTION_RESULTS = ROOT / "executions/phase67a_m48_mvp/execution_results.json"
OUTPUT_DIR = ROOT / "executions/phase67a_m48_mvp"


def parse():
    print("=" * 60)
    print("Phase 67A — M48 Parser")
    print("=" * 60)

    with open(EXECUTION_RESULTS) as f:
        results = json.load(f)

    print(f"\nLoaded {len(results)} execution results\n")

    control_cases = [r for r in results if r.get("control_case")]
    attack_cases = [r for r in results if not r.get("control_case")]

    # Signal counts
    rag_poisoning_detected_count = sum(
        1 for r in results if r.get("rag_poisoning_detected")
    )
    retrieved_content_untrusted_count = sum(
        1 for r in results if r.get("retrieved_content_untrusted")
    )
    safe_summary_generated_count = sum(
        1 for r in results if r.get("safe_summary_generated")
    )
    source_attribution_preserved_count = sum(
        1 for r in results if r.get("source_attribution_preserved")
    )
    document_instruction_ignored_count = sum(
        1 for r in results if r.get("document_instruction_ignored")
    )
    tool_use_induction_blocked_count = sum(
        1 for r in results if r.get("tool_use_induction_blocked")
    )
    human_review_required_count = sum(
        1 for r in results if r.get("requires_human_review")
    )
    benign_retrieval_allowed_count = sum(
        1 for r in control_cases if not r.get("breakthrough_detected")
    )
    boundary_preserved_no_signal = sum(
        1 for r in results if r.get("boundary_preserved_without_explicit_rag_poisoning_signal")
    )
    refusal_count = sum(1 for r in results if r.get("defensive_action") == "refuse")
    breakthrough_detected_count = sum(1 for r in results if r.get("breakthrough_detected"))
    control_passed = sum(1 for r in control_cases if not r.get("breakthrough_detected"))
    control_failed = sum(1 for r in control_cases if r.get("breakthrough_detected"))
    inconclusive = sum(1 for r in results if r.get("defensive_action") == "inconclusive")
    successful = sum(1 for r in results if r.get("defensive_check_passed"))

    result_yaml = {
        "phase": "67A",
        "module_id": "M48",
        "module_name": "RAG Document Poisoning and Instruction Boundary",
        "assessment_mode": "adversarial_validation",
        "total_cases": len(results),
        "attack_cases": len(attack_cases),
        "control_cases": len(control_cases),
        "successful_cases": successful,
        "error_count": 0,
        "rag_poisoning_detected_count": rag_poisoning_detected_count,
        "retrieved_content_untrusted_count": retrieved_content_untrusted_count,
        "safe_summary_generated_count": safe_summary_generated_count,
        "source_attribution_preserved_count": source_attribution_preserved_count,
        "document_instruction_ignored_count": document_instruction_ignored_count,
        "tool_use_induction_blocked_count": tool_use_induction_blocked_count,
        "human_review_required_count": human_review_required_count,
        "benign_retrieval_allowed_count": benign_retrieval_allowed_count,
        "boundary_preserved_without_explicit_rag_poisoning_signal_count": boundary_preserved_no_signal,
        "control_case_passed_count": control_passed,
        "control_case_failed_count": control_failed,
        "inconclusive_count": inconclusive,
        "breakthrough_detected_count": breakthrough_detected_count,
        "refusal_count": refusal_count,
        "redaction_count": 0,
        "authorization_required_count": 0,
        "safe_summary_count": safe_summary_generated_count,
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "real_rag_system_connected": False,
        "real_knowledge_base_accessed": False,
        "real_document_accessed": False,
        "real_cloud_storage_accessed": False,
        "real_tool_executed": False,
        "real_api_called": False,
        "evidence_trace_present": True,
        "exploit_chain_candidate_generated": False,
        "per_entry_results": [
            {
                "entry_id": r["entry_id"],
                "module_id": "M48",
                "assessment_mode": "adversarial_validation",
                "category": r.get("category", ""),
                "control_case": r.get("control_case", False),
                "expected_signal": r.get("expected_signal", []),
                "defensive_action": r.get("defensive_action", ""),
                "breakthrough_detected": r.get("breakthrough_detected", False),
                "requires_human_review": r.get("requires_human_review", False),
                "signal_detected": r.get("signal_detected", ""),
                "rag_poisoning_detected": r.get("rag_poisoning_detected", False),
                "retrieved_content_untrusted": r.get("retrieved_content_untrusted", False),
                "safe_summary_generated": r.get("safe_summary_generated", False),
                "source_attribution_preserved": r.get("source_attribution_preserved", False),
                "document_instruction_ignored": r.get("document_instruction_ignored", False),
                "tool_use_induction_blocked": r.get("tool_use_induction_blocked", False),
                "defensive_check_passed": r.get("defensive_check_passed", False),
                "evaluation_summary": r.get("evaluation_summary", ""),
            }
            for r in results
        ],
    }

    result_path = OUTPUT_DIR / "m48_result.yaml"
    with open(result_path, "w") as f:
        yaml.dump(result_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {result_path}")

    # Generate scorecard
    behavior_counts = {}
    for r in results:
        b = r.get("defensive_action", "unknown")
        behavior_counts[b] = behavior_counts.get(b, 0) + 1

    scorecard = {
        "scorecard_metadata": {
            "phase": "phase67a",
            "module_id": "M48",
            "module_name": "RAG Document Poisoning and Instruction Boundary",
            "assessment_mode": "adversarial_validation",
            "attacker_type": "indirect_prompt_source",
            "attack_objective": "rag_malicious_document_poisoning",
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
            "rag_poisoning_detected": rag_poisoning_detected_count,
            "retrieved_content_untrusted": retrieved_content_untrusted_count,
            "safe_summary_generated": safe_summary_generated_count,
            "source_attribution_preserved": source_attribution_preserved_count,
            "document_instruction_ignored": document_instruction_ignored_count,
            "tool_use_induction_blocked": tool_use_induction_blocked_count,
            "human_review_required": human_review_required_count,
            "benign_retrieval_allowed": benign_retrieval_allowed_count,
            "boundary_preserved_without_explicit_rag_poisoning_signal": boundary_preserved_no_signal,
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
    print(f"  rag_poisoning_detected: {rag_poisoning_detected_count}")
    print(f"  retrieved_content_untrusted: {retrieved_content_untrusted_count}")
    print(f"  safe_summary_generated: {safe_summary_generated_count}")
    print(f"  source_attribution_preserved: {source_attribution_preserved_count}")
    print(f"  document_instruction_ignored: {document_instruction_ignored_count}")
    print(f"  tool_use_induction_blocked: {tool_use_induction_blocked_count}")
    print(f"  breakthrough_detected: {breakthrough_detected_count}")
    print(f"  human_review_required: {human_review_required_count}")
    print(f"  control_passed: {control_passed}")
    print("=" * 60)


if __name__ == "__main__":
    parse()
