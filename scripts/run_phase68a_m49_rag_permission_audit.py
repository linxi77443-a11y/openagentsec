#!/usr/bin/env python3
"""Phase 68A — M49 RAG Permission Inheritance and Retrieval Audit MVP Execution Script.

Simulates adversarial_validation evaluation for M49 permission/audit entries.
No real RAG system, no real knowledge base, no real documents, no real permission
system, no real audit logs. SIM_ placeholder data only.
"""
import json, sys, yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/m49_rag_permission_inheritance_audit_mvp/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase68a_m49_mvp"

SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path):
    with open(path) as f:
        return yaml.safe_load(f)


def simulate_defense(entry):
    """Simulate permission inheritance and retrieval audit defense for M49 entries."""
    eid = entry["entry_id"]
    is_control = entry.get("control_case", False)
    category = entry.get("category", "")
    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    evidence_trace = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_permission_check",
            "content": f"User {entry.get('synthetic_user_id')} from tenant {entry.get('synthetic_tenant_id')} requests document {entry.get('synthetic_document_id')}",
            "signal_type": "permission_evaluation",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_retrieval_context",
            "content": entry.get("retrieval_context_summary", "")[:200],
            "signal_type": "retrieval_context",
        },
    ]

    if is_control:
        return {
            "defensive_action": "normal_usage_allowed",
            "breakthrough_detected": False,
            "requires_human_review": False,
            "signal_detected": "benign_authorized_retrieval_allowed",
            "defensive_check_passed": True,
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": False,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": False,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": True,
            "permission_decision_logged": True,
            "audit_trace_complete": True,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": True,
            "same_tenant_allowed": True,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "audit_log",
                    "content": f"Permission decision logged: ALLOW — user {entry.get('synthetic_user_id')} tenant {entry.get('synthetic_tenant_id')} document {entry.get('synthetic_document_id')}",
                    "signal_type": "permission_decision_logged",
                },
            ],
            "evaluation_summary": "control_case — benign authorized retrieval allowed, audit trace complete",
        }

    if is_breakthrough:
        return {
            "defensive_action": "partial_bypass",
            "breakthrough_detected": True,
            "requires_human_review": True,
            "signal_detected": "permission_bypass_missed",
            "defensive_check_passed": False,
            "permission_boundary_preserved": False,
            "restricted_retrieval_blocked": False,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": False,
            "restricted_summary_blocked": False,
            "permission_context_preserved": False,
            "retrieval_source_attributed": False,
            "permission_decision_logged": False,
            "audit_trace_complete": False,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "evaluation",
                    "content": "Defense failed to recognize permission boundary violation",
                    "signal_type": "breakthrough",
                }
            ],
            "evaluation_summary": "breakthrough — permission boundary not preserved, restricted content may be exposed",
        }

    # Apply signals based on category
    if category == "rag_permission_inheritance_bypass":
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": True,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": True,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": False,
            "permission_decision_logged": True,
            "audit_trace_complete": False,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "blocked — permission inheritance bypass attempt detected, restricted retrieval blocked"
    elif category == "rag_low_privileged_high_priv_doc_request":
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": True,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": True,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": False,
            "permission_decision_logged": True,
            "audit_trace_complete": False,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "blocked — low-privileged user high-privilege document request denied"
    elif category == "rag_cross_tenant_retrieval_attempt":
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": False,
            "cross_tenant_retrieval_blocked": True,
            "authorization_required": True,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": False,
            "permission_decision_logged": True,
            "audit_trace_complete": False,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "blocked — cross-tenant retrieval attempt detected and blocked"
    elif category == "rag_restricted_summary_request":
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": False,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": True,
            "restricted_summary_blocked": True,
            "permission_context_preserved": True,
            "retrieval_source_attributed": False,
            "permission_decision_logged": True,
            "audit_trace_complete": False,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "blocked — restricted summary request denied, authorization required"
    elif category == "rag_permission_context_confusion":
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": True,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": False,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": False,
            "permission_decision_logged": True,
            "audit_trace_complete": False,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "blocked — permission context preserved despite ambiguous query"
    elif category == "rag_source_attribution_required":
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": False,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": False,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": True,
            "permission_decision_logged": True,
            "audit_trace_complete": True,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "ok — retrieval with source attribution, audit trace complete"
    elif category == "rag_retrieval_audit_gap":
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": False,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": False,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": False,
            "permission_decision_logged": False,
            "audit_trace_complete": False,
            "audit_gap_detected": True,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "flagged — audit gap detected, missing trace fields, human review required"
    elif category == "rag_permission_decision_logging_required":
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": False,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": False,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": False,
            "permission_decision_logged": True,
            "audit_trace_complete": False,
            "audit_gap_detected": True,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "flagged — permission decision logged but audit gap detected, human review required"
    else:
        signals = {
            "permission_boundary_preserved": True,
            "restricted_retrieval_blocked": True,
            "cross_tenant_retrieval_blocked": False,
            "authorization_required": False,
            "restricted_summary_blocked": False,
            "permission_context_preserved": True,
            "retrieval_source_attributed": False,
            "permission_decision_logged": True,
            "audit_trace_complete": False,
            "audit_gap_detected": False,
            "benign_authorized_retrieval_allowed": False,
            "same_tenant_allowed": False,
            "boundary_preserved_without_explicit_permission_signal": False,
            "audit_trace_complete_by_fields": False,
        }
        eval_summary = "blocked — permission boundary preserved"

    requires_hr = signals.get("restricted_retrieval_blocked", False) or \
                  signals.get("cross_tenant_retrieval_blocked", False) or \
                  signals.get("audit_gap_detected", False) or \
                  signals.get("authorization_required", False)

    return {
        "defensive_action": "refuse" if signals.get("restricted_retrieval_blocked") or signals.get("cross_tenant_retrieval_blocked") else "allow_with_restriction",
        "breakthrough_detected": False,
        "requires_human_review": requires_hr,
        "signal_detected": "permission_boundary_preserved",
        "defensive_check_passed": True,
        **signals,
        "evidence_trace": evidence_trace + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "defensive_check",
                "content": f"Permission/audit evaluation: {category} — {entry.get('retrieval_context_summary', '')[:150]}",
                "signal_type": "permission_audit_evaluation",
            },
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "audit_log",
                "content": f"Decision logged: user {entry.get('synthetic_user_id')} tenant {entry.get('synthetic_tenant_id')} target {entry.get('synthetic_requested_tenant_id')} doc {entry.get('synthetic_document_id')}",
                "signal_type": "permission_decision_logged",
            },
        ],
        "evaluation_summary": eval_summary,
    }


def execute_playbook(playbook):
    entries = playbook.get("entries", [])
    meta = playbook.get("playbook_metadata", {})

    results = []
    for entry in entries:
        result = {
            "entry_id": entry["entry_id"],
            "module_id": "M49",
            "assessment_mode": "adversarial_validation",
            "attacker_type": "low_privileged_operator",
            "attack_objective": entry.get("attack_objective", "rag_permission_inheritance_bypass"),
            "category": entry.get("category", ""),
            "scenario": entry.get("scenario", ""),
            "control_case": entry.get("control_case", False),
            "synthetic_user_id": entry.get("synthetic_user_id", ""),
            "synthetic_tenant_id": entry.get("synthetic_tenant_id", ""),
            "synthetic_requested_tenant_id": entry.get("synthetic_requested_tenant_id", ""),
            "synthetic_document_id": entry.get("synthetic_document_id", ""),
            "synthetic_permission_policy_id": entry.get("synthetic_permission_policy_id", ""),
            "synthetic_retrieval_query_id": entry.get("synthetic_retrieval_query_id", ""),
            "synthetic_retrieval_event_id": entry.get("synthetic_retrieval_event_id", ""),
            "synthetic_audit_log_id": entry.get("synthetic_audit_log_id", ""),
            "expected_signal": entry.get("expected_signal", []),
            "expected_behavior": entry.get("expected_behavior", []),
            "user_query": entry.get("user_query", "")[:300],
            "retrieval_context_summary": entry.get("retrieval_context_summary", ""),
            "permission_context_summary": entry.get("permission_context_summary", ""),
            "fake_runtime_only": True,
            "real_rag_system_connected": False,
            "real_knowledge_base_accessed": False,
            "real_document_accessed": False,
            "real_cloud_storage_accessed": False,
            "real_url_accessed": False,
            "real_tenant_data_accessed": False,
            "real_permission_system_used": False,
            "real_audit_log_accessed": False,
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
    perm_boundary = sum(1 for r in results if r.get("permission_boundary_preserved"))
    restricted_blocked = sum(1 for r in results if r.get("restricted_retrieval_blocked"))
    cross_tenant_blocked = sum(1 for r in results if r.get("cross_tenant_retrieval_blocked"))
    auth_required = sum(1 for r in results if r.get("authorization_required"))
    restricted_summary_blocked = sum(1 for r in results if r.get("restricted_summary_blocked"))
    perm_context = sum(1 for r in results if r.get("permission_context_preserved"))
    source_attributed = sum(1 for r in results if r.get("retrieval_source_attributed"))
    perm_logged = sum(1 for r in results if r.get("permission_decision_logged"))
    audit_complete = sum(1 for r in results if r.get("audit_trace_complete"))
    audit_gap = sum(1 for r in results if r.get("audit_gap_detected"))
    human_review = sum(1 for r in results if r["requires_human_review"])
    benign_allowed = sum(1 for r in results if r.get("benign_authorized_retrieval_allowed"))
    same_tenant = sum(1 for r in results if r.get("same_tenant_allowed"))
    boundary_no_signal = sum(1 for r in results if r.get("boundary_preserved_without_explicit_permission_signal"))
    audit_by_fields = sum(1 for r in results if r.get("audit_trace_complete_by_fields"))
    inconclusive = sum(1 for r in results if r.get("defensive_action") == "inconclusive")
    control_passed = sum(1 for r in control_cases if not r["breakthrough_detected"])
    control_failed = sum(1 for r in control_cases if r["breakthrough_detected"])

    refusal_count = sum(1 for r in results if r.get("defensive_action") == "refuse")
    redaction_count = 0
    safe_summary_count = sum(1 for r in results if r.get("permission_boundary_preserved"))

    behavior_counts = {}
    for r in results:
        b = r.get("defensive_action", "unknown")
        behavior_counts[b] = behavior_counts.get(b, 0) + 1

    scorecard = {
        "scorecard_metadata": {
            "phase": "phase68a",
            "module_id": "M49",
            "module_name": "RAG Permission Inheritance and Retrieval Audit",
            "assessment_mode": "adversarial_validation",
            "attacker_type": "low_privileged_operator",
            "attack_objective": "rag_permission_inheritance_bypass",
            "actor": meta.get("actor", "simulated_adversary"),
            "fake_runtime_only": True,
            "synthetic_only": True,
            "real_rag_system_allowed": False,
            "real_knowledge_base_allowed": False,
            "real_document_access_allowed": False,
            "real_cloud_storage_allowed": False,
            "real_tenant_data_allowed": False,
            "real_permission_system_allowed": False,
            "real_audit_log_allowed": False,
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
            "permission_boundary_preserved": perm_boundary,
            "restricted_retrieval_blocked": restricted_blocked,
            "cross_tenant_retrieval_blocked": cross_tenant_blocked,
            "authorization_required": auth_required,
            "restricted_summary_blocked": restricted_summary_blocked,
            "permission_context_preserved": perm_context,
            "retrieval_source_attributed": source_attributed,
            "permission_decision_logged": perm_logged,
            "audit_trace_complete": audit_complete,
            "audit_gap_detected": audit_gap,
            "human_review_required": human_review,
            "benign_authorized_retrieval_allowed": benign_allowed,
            "same_tenant_allowed": same_tenant,
            "boundary_preserved_without_explicit_permission_signal": boundary_no_signal,
            "audit_trace_complete_by_fields": audit_by_fields,
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


def generate_m49_result(results, meta, output_dir):
    entries_out = []
    for r in results:
        entry = {
            "entry_id": r["entry_id"],
            "module_id": "M49",
            "assessment_mode": "adversarial_validation",
            "category": r["category"],
            "control_case": r["control_case"],
            "expected_signal": r.get("expected_signal", []),
            "defensive_action": r["defensive_action"],
            "breakthrough_detected": r["breakthrough_detected"],
            "requires_human_review": r["requires_human_review"],
            "signal_detected": r["signal_detected"],
            "permission_boundary_preserved": r.get("permission_boundary_preserved", False),
            "restricted_retrieval_blocked": r.get("restricted_retrieval_blocked", False),
            "cross_tenant_retrieval_blocked": r.get("cross_tenant_retrieval_blocked", False),
            "authorization_required": r.get("authorization_required", False),
            "restricted_summary_blocked": r.get("restricted_summary_blocked", False),
            "permission_context_preserved": r.get("permission_context_preserved", False),
            "retrieval_source_attributed": r.get("retrieval_source_attributed", False),
            "permission_decision_logged": r.get("permission_decision_logged", False),
            "audit_trace_complete": r.get("audit_trace_complete", False),
            "audit_gap_detected": r.get("audit_gap_detected", False),
            "defensive_check_passed": r["defensive_check_passed"],
            "evaluation_summary": r["evaluation_summary"],
            "real_rag_system_connected": r["real_rag_system_connected"],
            "real_knowledge_base_accessed": r["real_knowledge_base_accessed"],
            "real_document_accessed": r["real_document_accessed"],
            "real_cloud_storage_accessed": r["real_cloud_storage_accessed"],
            "real_tenant_data_accessed": r["real_tenant_data_accessed"],
            "real_permission_system_used": r["real_permission_system_used"],
            "real_audit_log_accessed": r["real_audit_log_accessed"],
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
        "phase": "68A",
        "module_id": "M49",
        "module_name": "RAG Permission Inheritance and Retrieval Audit",
        "assessment_mode": "adversarial_validation",
        "total_cases": total,
        "attack_cases": len(attack_cases),
        "control_cases": len(control_cases),
        "successful_cases": sum(1 for r in results if r["defensive_check_passed"]),
        "error_count": 0,
        "permission_boundary_preserved_count": sum(1 for r in results if r.get("permission_boundary_preserved")),
        "restricted_retrieval_blocked_count": sum(1 for r in results if r.get("restricted_retrieval_blocked")),
        "cross_tenant_retrieval_blocked_count": sum(1 for r in results if r.get("cross_tenant_retrieval_blocked")),
        "authorization_required_count": sum(1 for r in results if r.get("authorization_required")),
        "restricted_summary_blocked_count": sum(1 for r in results if r.get("restricted_summary_blocked")),
        "permission_context_preserved_count": sum(1 for r in results if r.get("permission_context_preserved")),
        "retrieval_source_attributed_count": sum(1 for r in results if r.get("retrieval_source_attributed")),
        "permission_decision_logged_count": sum(1 for r in results if r.get("permission_decision_logged")),
        "audit_trace_complete_count": sum(1 for r in results if r.get("audit_trace_complete")),
        "audit_gap_detected_count": sum(1 for r in results if r.get("audit_gap_detected")),
        "human_review_required_count": sum(1 for r in results if r["requires_human_review"]),
        "benign_authorized_retrieval_allowed_count": sum(1 for r in results if r.get("benign_authorized_retrieval_allowed")),
        "same_tenant_allowed_count": sum(1 for r in results if r.get("same_tenant_allowed")),
        "boundary_preserved_without_explicit_permission_signal_count": sum(1 for r in results if r.get("boundary_preserved_without_explicit_permission_signal")),
        "audit_trace_complete_by_fields_count": sum(1 for r in results if r.get("audit_trace_complete_by_fields")),
        "control_case_passed_count": sum(1 for r in control_cases if not r["breakthrough_detected"]),
        "control_case_failed_count": sum(1 for r in control_cases if r["breakthrough_detected"]),
        "inconclusive_count": sum(1 for r in results if r.get("defensive_action") == "inconclusive"),
        "breakthrough_detected_count": sum(1 for r in results if r["breakthrough_detected"]),
        "refusal_count": sum(1 for r in results if r.get("defensive_action") == "refuse"),
        "redaction_count": 0,
        "authorization_required_count": auth_required_count if (auth_required_count := sum(1 for r in results if r.get("authorization_required"))) else 0,
        "safe_summary_count": sum(1 for r in results if r.get("permission_boundary_preserved")),
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "real_rag_system_connected": False,
        "real_knowledge_base_accessed": False,
        "real_document_accessed": False,
        "real_cloud_storage_accessed": False,
        "real_tenant_data_accessed": False,
        "real_permission_system_used": False,
        "real_audit_log_accessed": False,
        "real_tool_executed": False,
        "real_api_called": False,
        "evidence_trace_present": True,
        "exploit_chain_candidate_generated": False,
        "per_entry_results": entries_out,
    }

    path = output_dir / "m49_result.yaml"
    with open(path, "w") as f:
        yaml.dump(result_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def main():
    print("=" * 60)
    print("Phase 68A — M49 RAG Permission Inheritance and Retrieval Audit MVP Execution")
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
    print(f"  Restricted retrieval blocked: {sum(1 for r in results if r.get('restricted_retrieval_blocked'))}")
    print(f"  Cross-tenant blocked: {sum(1 for r in results if r.get('cross_tenant_retrieval_blocked'))}")

    print("\nWriting execution results...")
    write_execution_results(results, OUTPUT_DIR)

    print("\nGenerating scorecard...")
    generate_scorecard(results, meta, OUTPUT_DIR)

    print("\nGenerating M49 result...")
    generate_m49_result(results, meta, OUTPUT_DIR)

    print(f"\n{'=' * 60}")
    print("Execution complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
