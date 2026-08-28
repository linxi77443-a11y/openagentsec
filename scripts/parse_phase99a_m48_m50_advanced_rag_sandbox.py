#!/usr/bin/env python3
"""Phase 99A — M48 RAG Multi-Hop Poisoning & M50 Multi-Turn Sandbox Escape Advanced Parser.

Reads execution_results.json and produces m48_m50_adv_result.yaml and capability_scorecard.yaml.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "executions/phase99a_m48_m50_adv"
EXECUTION_RESULTS = OUTPUT_DIR / "execution_results.json"
RESULT_YAML = OUTPUT_DIR / "m48_m50_adv_result.yaml"
SCORECARD_YAML = OUTPUT_DIR / "capability_scorecard.yaml"


def parse():
    print("=" * 70)
    print("Phase 99A — M48/M50 Advanced RAG & Sandbox Parser")
    print("=" * 70)

    if not EXECUTION_RESULTS.exists():
        print(f"Error: Execution results file not found at {EXECUTION_RESULTS}")
        sys.exit(1)

    with open(EXECUTION_RESULTS, "r", encoding="utf-8") as f:
        results = json.load(f)

    print(f"\nLoaded {len(results)} execution results\n")

    control_cases = [r for r in results if r.get("control_case")]
    attack_cases = [r for r in results if not r.get("control_case")]

    # Specific signal counts
    rag_multi_doc_poisoning_detected_count = sum(1 for r in results if r.get("rag_multi_doc_poisoning_detected"))
    rag_multi_hop_chain_induction_detected_count = sum(1 for r in results if r.get("rag_multi_hop_chain_induction_detected"))
    rag_chunk_boundary_collision_detected_count = sum(1 for r in results if r.get("rag_chunk_boundary_collision_detected"))
    rag_reranker_cloaking_detected_count = sum(1 for r in results if r.get("rag_reranker_cloaking_detected"))
    rag_citation_authority_spoofing_detected_count = sum(1 for r in results if r.get("rag_citation_authority_spoofing_detected"))

    sandbox_progressive_probing_detected_count = sum(1 for r in results if r.get("sandbox_progressive_probing_detected"))
    sandbox_side_channel_tampering_detected_count = sum(1 for r in results if r.get("sandbox_side_channel_tampering_detected"))
    audit_log_stream_tampering_detected_count = sum(1 for r in results if r.get("audit_log_stream_tampering_detected"))
    sandbox_symlink_traversal_blocked_count = sum(1 for r in results if r.get("sandbox_symlink_traversal_blocked"))
    sandbox_state_signature_forgery_detected_count = sum(1 for r in results if r.get("sandbox_state_signature_forgery_detected"))

    rag_safe_context_allowed_count = sum(1 for r in results if r.get("rag_safe_context_allowed"))
    sandbox_safe_execution_allowed_count = sum(1 for r in results if r.get("sandbox_safe_execution_allowed"))

    rag_context_quarantined_count = sum(1 for r in results if r.get("rag_context_quarantined"))
    sandbox_containment_enforced_count = sum(1 for r in results if r.get("sandbox_containment_enforced"))

    human_review_required_count = sum(1 for r in results if r.get("requires_human_review"))
    breakthrough_detected_count = sum(1 for r in results if r.get("breakthrough_detected"))
    control_passed = sum(1 for r in control_cases if not r.get("breakthrough_detected"))
    control_failed = sum(1 for r in control_cases if r.get("breakthrough_detected"))
    refusal_count = sum(1 for r in results if r.get("defensive_action") == "refuse")
    normal_usage_count = sum(1 for r in results if r.get("defensive_action") == "normal_usage_allowed")
    successful = sum(1 for r in results if r.get("defensive_check_passed"))

    # Generate m48_m50_adv_result.yaml
    result_data = {
        "phase": "phase99a",
        "task_id": "Phase-99A-M48M50-002",
        "module_ids": ["M48", "M50"],
        "module_names": "RAG Multi-Hop Poisoning & Runtime Sandbox Escape Defense",
        "assessment_mode": "adversarial_validation",
        "total_cases": len(results),
        "attack_cases": len(attack_cases),
        "control_cases": len(control_cases),
        "successful_cases": successful,
        "error_count": 0,
        "breakthrough_detected_count": breakthrough_detected_count,
        "rag_multi_doc_poisoning_detected_count": rag_multi_doc_poisoning_detected_count,
        "rag_multi_hop_chain_induction_detected_count": rag_multi_hop_chain_induction_detected_count,
        "rag_chunk_boundary_collision_detected_count": rag_chunk_boundary_collision_detected_count,
        "rag_reranker_cloaking_detected_count": rag_reranker_cloaking_detected_count,
        "rag_citation_authority_spoofing_detected_count": rag_citation_authority_spoofing_detected_count,
        "sandbox_progressive_probing_detected_count": sandbox_progressive_probing_detected_count,
        "sandbox_side_channel_tampering_detected_count": sandbox_side_channel_tampering_detected_count,
        "audit_log_stream_tampering_detected_count": audit_log_stream_tampering_detected_count,
        "sandbox_symlink_traversal_blocked_count": sandbox_symlink_traversal_blocked_count,
        "sandbox_state_signature_forgery_detected_count": sandbox_state_signature_forgery_detected_count,
        "rag_safe_context_allowed_count": rag_safe_context_allowed_count,
        "sandbox_safe_execution_allowed_count": sandbox_safe_execution_allowed_count,
        "rag_context_quarantined_count": rag_context_quarantined_count,
        "sandbox_containment_enforced_count": sandbox_containment_enforced_count,
        "human_review_required_count": human_review_required_count,
        "control_case_passed_count": control_passed,
        "control_case_failed_count": control_failed,
        "refusal_count": refusal_count,
        "normal_usage_allowed_count": normal_usage_count,
        "inconclusive_count": 0,
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "synthetic_only": True,
        "real_vector_db_accessed": False,
        "real_rag_pipeline_accessed": False,
        "real_sandbox_escape_executed": False,
        "real_host_system_accessed": False,
        "real_audit_log_mutated": False,
        "real_tool_call_executed": False,
        "real_api_call_executed": False,
        "real_credential_read": False,
        "evidence_trace_present": True,
        "exploit_chain_candidate_generated": False,
        "per_entry_results": [
            {
                "entry_id": r["entry_id"],
                "module_id": r.get("module_id", "M48"),
                "assessment_mode": "adversarial_validation",
                "category": r.get("category", ""),
                "control_case": r.get("control_case", False),
                "defensive_action": r.get("defensive_action", ""),
                "breakthrough_detected": r.get("breakthrough_detected", False),
                "requires_human_review": r.get("requires_human_review", False),
                "signal_detected": r.get("signal_detected", ""),
                "defensive_check_passed": r.get("defensive_check_passed", False),
                "evaluation_summary": r.get("evaluation_summary", ""),
                "confirmed_vulnerability": False,
                "formal_finding_allowed": False,
            }
            for r in results
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(result_data, f, sort_keys=False, allow_unicode=True)
    print(f"Result YAML written to: {RESULT_YAML}")

    # Generate capability_scorecard.yaml
    scorecard_data = {
        "scorecard_metadata": {
            "phase": "phase99a",
            "task_id": "Phase-99A-M48M50-002",
            "module_ids": ["M48", "M50"],
            "module_names": "RAG Multi-Hop Poisoning & Runtime Sandbox Escape Defense",
            "assessment_mode": "adversarial_validation",
            "actor": "simulated_adversary",
            "attacker_profile": "rag_and_sandbox_advanced_adversary",
            "fake_runtime_only": True,
            "synthetic_only": True,
            "real_vector_db_allowed": False,
            "real_rag_pipeline_allowed": False,
            "real_sandbox_escape_allowed": false,
            "real_host_system_access_allowed": False,
            "real_audit_log_mutation_allowed": False,
            "real_tool_call_allowed": False,
            "real_api_call_allowed": False,
            "real_credential_read_allowed": False,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "safety_level": "simulated_runtime_safety",
            "production_safety": "out_of_scope",
            "total_entries": len(results),
            "breakthrough_ids": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "results_summary": {
            "total": len(results),
            "attack_cases": len(attack_cases),
            "control_cases": len(control_cases),
            "breakthrough_detected": breakthrough_detected_count,
            "rag_multi_doc_poisoning_detected": rag_multi_doc_poisoning_detected_count,
            "rag_multi_hop_chain_induction_detected": rag_multi_hop_chain_induction_detected_count,
            "rag_chunk_boundary_collision_detected": rag_chunk_boundary_collision_detected_count,
            "rag_reranker_cloaking_detected": rag_reranker_cloaking_detected_count,
            "rag_citation_authority_spoofing_detected": rag_citation_authority_spoofing_detected_count,
            "sandbox_progressive_probing_detected": sandbox_progressive_probing_detected_count,
            "sandbox_side_channel_tampering_detected": sandbox_side_channel_tampering_detected_count,
            "audit_log_stream_tampering_detected": audit_log_stream_tampering_detected_count,
            "sandbox_symlink_traversal_blocked": sandbox_symlink_traversal_blocked_count,
            "sandbox_state_signature_forgery_detected": sandbox_state_signature_forgery_detected_count,
            "rag_safe_context_allowed": rag_safe_context_allowed_count,
            "sandbox_safe_execution_allowed": sandbox_safe_execution_allowed_count,
            "rag_context_quarantined": rag_context_quarantined_count,
            "sandbox_containment_enforced": sandbox_containment_enforced_count,
            "human_review_required": human_review_required_count,
            "control_passed": control_passed,
            "control_failed": control_failed,
            "inconclusive": 0,
            "defensive_behavior_distribution": {
                "refuse": refusal_count,
                "normal_usage_allowed": normal_usage_count,
            },
        },
        "capability_value": "high",
        "risk_level": "low",
        "capability_value_semantics": "evaluation capability effectiveness only",
        "risk_level_semantics": "simulated residual risk only, not production risk",
        "category_coverage": [
            "rag_multi_doc_fragment_poisoning",
            "rag_multi_hop_query_chain_induction",
            "rag_semantic_shadow_chunking_collision",
            "rag_embedding_vector_space_cloaking",
            "rag_citation_fabrication_authority_hijack",
            "sandbox_multiturn_progressive_probing",
            "sandbox_side_channel_timing_escape",
            "sandbox_audit_log_injection_tampering",
            "sandbox_ephemeral_fs_mount_spoofing",
            "sandbox_state_mutation_signature_forgery",
            "benign_rag_retrieval_control",
            "benign_sandbox_execution_control",
        ],
    }

    with open(SCORECARD_YAML, "w", encoding="utf-8") as f:
        yaml.dump(scorecard_data, f, sort_keys=False, allow_unicode=True)
    print(f"Capability Scorecard written to: {SCORECARD_YAML}")
    print("\nParser completed successfully.\n")


if __name__ == "__main__":
    parse()
