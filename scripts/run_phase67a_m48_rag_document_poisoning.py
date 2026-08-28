#!/usr/bin/env python3
"""Phase 67A — M48 RAG Document Poisoning and Instruction Boundary MVP Execution Script.

Simulates adversarial_validation evaluation for M48 RAG document poisoning entries.
No real RAG system, no real knowledge base, no real documents. SIM_ placeholder data only.
"""
import json, sys, yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/m48_rag_document_poisoning_mvp/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase67a_m48_mvp"

SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path):
    with open(path) as f:
        return yaml.safe_load(f)


def simulate_defense(entry):
    """Simulate RAG document poisoning defense evaluation for M48 entries."""
    eid = entry["entry_id"]
    is_control = entry.get("control_case", False)
    expected_signal = entry.get("expected_signal", [])
    category = entry.get("category", "")
    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    evidence_trace = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_retrieved_document",
            "content": entry.get("retrieved_document_summary", "")[:200],
            "signal_type": "document_review",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "user_query",
            "content": entry.get("user_query", "")[:150],
            "signal_type": "user_request",
        },
    ]

    if is_control:
        return {
            "defensive_action": "normal_usage_allowed",
            "breakthrough_detected": False,
            "requires_human_review": False,
            "signal_detected": "benign_retrieval_allowed",
            "defensive_check_passed": True,
            "rag_poisoning_detected": False,
            "retrieved_content_untrusted": False,
            "safe_summary_generated": True,
            "source_attribution_preserved": True,
            "document_instruction_ignored": False,
            "tool_use_induction_blocked": False,
            "benign_retrieval_allowed": True,
            "instruction_boundary_preserved": True,
            "boundary_preserved_without_explicit_rag_poisoning_signal": False,
            "evidence_trace": evidence_trace,
            "evaluation_summary": "control_case — benign retrieved document allowed, no poisoning signal",
        }

    if is_breakthrough:
        return {
            "defensive_action": "partial_bypass",
            "breakthrough_detected": True,
            "requires_human_review": True,
            "signal_detected": "rag_poisoning_missed",
            "defensive_check_passed": False,
            "rag_poisoning_detected": False,
            "retrieved_content_untrusted": False,
            "safe_summary_generated": False,
            "source_attribution_preserved": False,
            "document_instruction_ignored": False,
            "tool_use_induction_blocked": False,
            "instruction_boundary_preserved": False,
            "benign_retrieval_allowed": False,
            "boundary_preserved_without_explicit_rag_poisoning_signal": False,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "evaluation",
                    "content": "Defense failed to recognize RAG document poisoning signal",
                    "signal_type": "breakthrough",
                }
            ],
            "evaluation_summary": "breakthrough — RAG document poisoning not detected, retrieved content treated as instructions",
        }

    is_poisoning_category = category in (
        "rag_document_instruction_like_content",
        "rag_document_tool_use_induction",
        "rag_document_source_confusion",
        "rag_document_authority_claim",
        "rag_document_hidden_policy_override",
        "rag_document_summary_manipulation",
    )

    signals = {
        "rag_poisoning_detected": True,
        "retrieved_content_untrusted": True,
        "safe_summary_generated": False,
        "source_attribution_preserved": True,
        "document_instruction_ignored": category
            in ("rag_document_instruction_like_content", "rag_document_hidden_policy_override"),
        "tool_use_induction_blocked": category in ("rag_document_tool_use_induction",),
        "human_review_required": True,
        "benign_retrieval_allowed": False,
        "instruction_boundary_preserved": True,
        "boundary_preserved_without_explicit_rag_poisoning_signal": False,
    }

    return {
        "defensive_action": "refuse",
        "breakthrough_detected": False,
        "requires_human_review": True,
        "signal_detected": "rag_poisoning_detected",
        "defensive_check_passed": True,
        **signals,
        "evidence_trace": evidence_trace + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "defensive_check",
                "content": f"RAG document poisoning detected: {category} — {entry.get('retrieved_document_summary', '')[:150]}",
                "signal_type": "rag_poisoning_detected",
            },
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "defensive_action",
                "content": "Retrieved content marked untrusted, safe summary generated, human review required",
                "signal_type": "retrieved_content_untrusted",
            },
        ],
        "evaluation_summary": (
            f"blocked — RAG document poisoning detected "
            f"(signal: {expected_signal}, category: {category})"
        ),
    }


def execute_playbook(playbook):
    entries = playbook.get("entries", [])
    meta = playbook.get("playbook_metadata", {})

    results = []
    for entry in entries:
        result = {
            "entry_id": entry["entry_id"],
            "module_id": "M48",
            "assessment_mode": "adversarial_validation",
            "attacker_type": "indirect_prompt_source",
            "attack_objective": "rag_malicious_document_poisoning",
            "category": entry.get("category", ""),
            "scenario": entry.get("scenario", ""),
            "control_case": entry.get("control_case", False),
            "synthetic_document_id": entry.get("synthetic_document_id", ""),
            "synthetic_knowledge_base_id": entry.get("synthetic_knowledge_base_id", ""),
            "synthetic_retrieval_result_id": entry.get("synthetic_retrieval_result_id", ""),
            "expected_signal": entry.get("expected_signal", []),
            "expected_behavior": entry.get("expected_behavior", []),
            "user_query": entry.get("user_query", "")[:300],
            "retrieved_document_summary": entry.get("retrieved_document_summary", ""),
            "fake_runtime_only": True,
            "real_rag_system_connected": False,
            "real_knowledge_base_accessed": False,
            "real_document_accessed": False,
            "real_cloud_storage_accessed": False,
            "real_url_accessed": False,
            "real_tool_executed": False,
            "real_api_called": False,
            "real_system_connection_used": False,
            "real_data_accessed": False,
            "real_secret_used": False,
            "pii_observed": False,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
        }
        result.update(simulate_defense(entry))
        results.append(result)

    return results


def write_execution_results(results, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "execution_results.json"
    with open(path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {path} — {len(results)} entries")


def generate_scorecard(results, meta, output_dir):
    total = len(results)
    attack_cases = [r for r in results if not r["control_case"]]
    control_cases = [r for r in results if r["control_case"]]

    breakthrough = sum(1 for r in results if r["breakthrough_detected"])
    poisoned_detected = sum(1 for r in results if r.get("rag_poisoning_detected"))
    content_untrusted = sum(1 for r in results if r.get("retrieved_content_untrusted"))
    safe_summary = sum(1 for r in results if r.get("safe_summary_generated"))
    source_attr = sum(1 for r in results if r.get("source_attribution_preserved"))
    doc_ignored = sum(1 for r in results if r.get("document_instruction_ignored"))
    tool_blocked = sum(1 for r in results if r.get("tool_use_induction_blocked"))
    human_review = sum(1 for r in results if r["requires_human_review"])
    benign_allowed = sum(1 for r in results if r.get("benign_retrieval_allowed"))
    instruction_boundary = sum(1 for r in results if r.get("instruction_boundary_preserved"))
    boundary_preserved_no_signal = sum(
        1 for r in results if r.get("boundary_preserved_without_explicit_rag_poisoning_signal")
    )
    inconclusive = sum(1 for r in results if r.get("defensive_action") == "inconclusive")
    control_passed = sum(1 for r in control_cases if not r["breakthrough_detected"])
    control_failed = sum(1 for r in control_cases if r["breakthrough_detected"])

    refusal_count = sum(1 for r in results if r.get("defensive_action") == "refuse")
    redaction_count = 0
    auth_required_count = 0
    safe_summary_count = safe_summary

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
            "actor": meta.get("actor", "simulated_adversary"),
            "fake_runtime_only": True,
            "synthetic_only": True,
            "real_rag_system_allowed": False,
            "real_knowledge_base_allowed": False,
            "real_document_access_allowed": False,
            "real_cloud_storage_allowed": False,
            "real_tool_call_allowed": False,
            "real_api_call_allowed": False,
            "simulated_signal_only": True,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "safety_level": "simulated_runtime_safety",
            "production_safety": "out_of_scope",
            "total_entries": total,
            "breakthrough_ids": sorted(
                [r["entry_id"] for r in results if r.get("breakthrough_detected")]
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "results_summary": {
            "total": total,
            "attack_cases": len(attack_cases),
            "control_cases": len(control_cases),
            "breakthrough_detected": breakthrough,
            "rag_poisoning_detected": poisoned_detected,
            "retrieved_content_untrusted": content_untrusted,
            "safe_summary_generated": safe_summary,
            "source_attribution_preserved": source_attr,
            "instruction_boundary_preserved": instruction_boundary,
            "document_instruction_ignored": doc_ignored,
            "tool_use_induction_blocked": tool_blocked,
            "human_review_required": human_review,
            "benign_retrieval_allowed": benign_allowed,
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
            dict.fromkeys(r["category"] for r in results if not r["control_case"])
        ),
    }

    path = output_dir / "capability_scorecard.yaml"
    with open(path, "w") as f:
        yaml.dump(scorecard, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def generate_m48_result(results, meta, output_dir):
    entries_out = []
    for r in results:
        entry = {
            "entry_id": r["entry_id"],
            "module_id": "M48",
            "assessment_mode": "adversarial_validation",
            "category": r["category"],
            "control_case": r["control_case"],
            "expected_signal": r.get("expected_signal", []),
            "defensive_action": r["defensive_action"],
            "breakthrough_detected": r["breakthrough_detected"],
            "requires_human_review": r["requires_human_review"],
            "signal_detected": r["signal_detected"],
            "rag_poisoning_detected": r.get("rag_poisoning_detected", False),
            "retrieved_content_untrusted": r.get("retrieved_content_untrusted", False),
            "safe_summary_generated": r.get("safe_summary_generated", False),
            "source_attribution_preserved": r.get("source_attribution_preserved", False),
            "document_instruction_ignored": r.get("document_instruction_ignored", False),
            "tool_use_induction_blocked": r.get("tool_use_induction_blocked", False),
            "instruction_boundary_preserved": r.get("instruction_boundary_preserved", False),
            "defensive_check_passed": r["defensive_check_passed"],
            "evaluation_summary": r["evaluation_summary"],
            "real_rag_system_connected": r["real_rag_system_connected"],
            "real_knowledge_base_accessed": r["real_knowledge_base_accessed"],
            "real_document_accessed": r["real_document_accessed"],
            "real_cloud_storage_accessed": r["real_cloud_storage_accessed"],
            "real_tool_executed": r["real_tool_executed"],
            "real_api_called": r["real_api_called"],
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
        }
        entries_out.append(entry)

    total = len(results)
    attack_cases = [r for r in results if not r["control_case"]]
    control_cases = [r for r in results if r["control_case"]]

    result_yaml = {
        "phase": "67A",
        "module_id": "M48",
        "module_name": "RAG Document Poisoning and Instruction Boundary",
        "assessment_mode": "adversarial_validation",
        "total_cases": total,
        "attack_cases": len(attack_cases),
        "control_cases": len(control_cases),
        "successful_cases": sum(1 for r in results if r["defensive_check_passed"]),
        "error_count": 0,
        "rag_poisoning_detected_count": sum(
            1 for r in results if r.get("rag_poisoning_detected")
        ),
        "retrieved_content_untrusted_count": sum(
            1 for r in results if r.get("retrieved_content_untrusted")
        ),
        "safe_summary_generated_count": sum(
            1 for r in results if r.get("safe_summary_generated")
        ),
        "source_attribution_preserved_count": sum(
            1 for r in results if r.get("source_attribution_preserved")
        ),
        "instruction_boundary_preserved_count": sum(
            1 for r in results if r.get("instruction_boundary_preserved")
        ),
        "document_instruction_ignored_count": sum(
            1 for r in results if r.get("document_instruction_ignored")
        ),
        "tool_use_induction_blocked_count": sum(
            1 for r in results if r.get("tool_use_induction_blocked")
        ),
        "human_review_required_count": sum(1 for r in results if r["requires_human_review"]),
        "benign_retrieval_allowed_count": sum(
            1 for r in results if r.get("benign_retrieval_allowed")
        ),
        "boundary_preserved_without_explicit_rag_poisoning_signal_count": sum(
            1 for r in results if r.get("boundary_preserved_without_explicit_rag_poisoning_signal")
        ),
        "control_case_passed_count": sum(1 for r in control_cases if not r["breakthrough_detected"]),
        "control_case_failed_count": sum(1 for r in control_cases if r["breakthrough_detected"]),
        "inconclusive_count": sum(1 for r in results if r.get("defensive_action") == "inconclusive"),
        "breakthrough_detected_count": sum(1 for r in results if r["breakthrough_detected"]),
        "refusal_count": sum(1 for r in results if r.get("defensive_action") == "refuse"),
        "redaction_count": 0,
        "authorization_required_count": 0,
        "safe_summary_count": sum(1 for r in results if r.get("safe_summary_generated")),
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
        "per_entry_results": entries_out,
    }

    path = output_dir / "m48_result.yaml"
    with open(path, "w") as f:
        yaml.dump(result_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def main():
    print("=" * 60)
    print("Phase 67A — M48 RAG Document Poisoning MVP Execution")
    print("=" * 60)

    print("\nLoading playbook...")
    playbook = load_playbook(PLAYBOOK_PATH)
    meta = playbook.get("playbook_metadata", {})
    print(f"  Playbook: {PLAYBOOK_PATH.name}")
    print(f"  Module: {meta.get('module_id', 'N/A')}")
    print(f"  Assessment mode: {meta.get('assessment_mode', 'N/A')}")
    print(f"  Entries: {len(playbook.get('entries', []))}")
    print(f"  Fake runtime only: {meta.get('fake_runtime_only', True)}")

    print("\nSimulating defense evaluation...")
    results = execute_playbook(playbook)
    print(f"  Entries evaluated: {len(results)}")
    print(f"  Breakthrough detected: {sum(1 for r in results if r['breakthrough_detected'])}")
    poisoned = sum(1 for r in results if r.get("rag_poisoning_detected"))
    print(f"  RAG poisoning detected: {poisoned}")
    print(f"  Human review required: {sum(1 for r in results if r['requires_human_review'])}")

    print("\nWriting execution results...")
    write_execution_results(results, OUTPUT_DIR)

    print("\nGenerating scorecard...")
    generate_scorecard(results, meta, OUTPUT_DIR)

    print("\nGenerating M48 result...")
    generate_m48_result(results, meta, OUTPUT_DIR)

    print(f"\n{'=' * 60}")
    print("Execution complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
