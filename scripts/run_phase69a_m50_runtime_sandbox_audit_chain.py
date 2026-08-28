#!/usr/bin/env python3
"""Phase 69A — M50 Agent Runtime Sandbox and Audit Chain Integrity MVP Execution Script.

Simulates adversarial_validation evaluation for M50 runtime sandbox, tool trace,
audit chain, and controlled replay admission boundary entries.
No real runtime, no real sandbox escape, no real tools, no real audit logs,
no real traces, no controlled replay execution. SIM_ placeholder data only.
"""
import json, sys, yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/m50_runtime_sandbox_audit_chain_mvp/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase69a_m50_mvp"

SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path):
    with open(path) as f:
        return yaml.safe_load(f)


def simulate_defense(entry):
    """Simulate runtime sandbox, tool trace, audit chain defense for M50 entries."""
    eid = entry["case_id"]
    is_control = entry.get("control_case", False)
    category = entry.get("category", "")
    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    evidence_trace = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_runtime_check",
            "content": f"Runtime sandbox {entry.get('synthetic_runtime_sandbox_id')} policy {entry.get('synthetic_runtime_policy_id')} — evaluating request {entry.get('synthetic_request_id')}",
            "signal_type": "runtime_evaluation",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_trace_context",
            "content": entry.get("trace_context_summary", "")[:200],
            "signal_type": "trace_context",
        },
    ]

    if is_control:
        return {
            "defensive_action": "normal_usage_allowed",
            "breakthrough_detected": False,
            "requires_human_review": False,
            "signal_detected": "audit_chain_consistent" if category == "complete_audit_chain_control_case" else "safe_fake_runtime_allowed",
            "defensive_check_passed": True,
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": True,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": False,
            "audit_event_generated": True,
            "audit_chain_consistent": True,
            "audit_chain_gap_detected": False,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "synthetic_audit_log",
                    "content": f"Audit event logged: sandbox {entry.get('synthetic_runtime_sandbox_id')} request {entry.get('synthetic_request_id')} decision {entry.get('synthetic_decision_id')} trace {entry.get('synthetic_trace_id')}",
                    "signal_type": "audit_event_generated",
                },
            ],
            "evaluation_summary": f"control_case — {'complete audit chain consistent, all fields verified' if 'audit_chain' in category else 'safe fake runtime action allowed, full trace recorded'}",
        }

    if is_breakthrough:
        return {
            "defensive_action": "partial_bypass",
            "breakthrough_detected": True,
            "requires_human_review": True,
            "signal_detected": "runtime_boundary_breach",
            "defensive_check_passed": False,
            "sandbox_boundary_preserved": False,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": False,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": False,
            "tool_trace_complete": False,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": False,
            "trace_integrity_failed": True,
            "audit_event_generated": False,
            "audit_chain_consistent": False,
            "audit_chain_gap_detected": True,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": False,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "evaluation",
                    "content": "Defense failed to recognize runtime boundary violation",
                    "signal_type": "breakthrough",
                }
            ],
            "evaluation_summary": "breakthrough — runtime boundary not preserved, sandbox escape or trace integrity failure may be exposed",
        }

    # Attack case signal logic per category
    if category == "runtime_sandbox_escape_signal":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": True,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": True,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": False,
            "audit_event_generated": True,
            "audit_chain_consistent": True,
            "audit_chain_gap_detected": False,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "blocked — runtime sandbox escape signal detected, out-of-scope transition blocked, audit event generated"
    elif category == "runtime_fake_tool_boundary_violation":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": True,
            "runtime_policy_enforced": True,
            "tool_trace_complete": True,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": False,
            "audit_event_generated": True,
            "audit_chain_consistent": True,
            "audit_chain_gap_detected": False,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "blocked — fake tool boundary violation attempt detected, unauthorized tool call denied, audit event generated"
    elif category == "runtime_policy_enforcement_bypass":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": True,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": False,
            "audit_event_generated": True,
            "audit_chain_consistent": True,
            "audit_chain_gap_detected": False,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "blocked — runtime policy enforcement bypass attempt detected, policy applied, audit event generated"
    elif category in ("tool_trace_missing_required_field",):
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": False,
            "tool_trace_missing_field_detected": True,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": True,
            "audit_event_generated": True,
            "audit_chain_consistent": False,
            "audit_chain_gap_detected": True,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "flagged — tool trace missing required field, trace integrity failed, human review required"
    elif category == "tool_trace_inconsistent_trace_id":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": False,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": False,
            "trace_integrity_failed": True,
            "audit_event_generated": True,
            "audit_chain_consistent": False,
            "audit_chain_gap_detected": True,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "flagged — inconsistent trace_id detected, trace integrity failed, human review required"
    elif category == "tool_trace_reordered_sequence":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": False,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": True,
            "audit_event_generated": True,
            "audit_chain_consistent": False,
            "audit_chain_gap_detected": True,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "flagged — tool trace reordered sequence detected, trace integrity failed, human review required"
    elif category == "audit_chain_missing_event":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": True,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": False,
            "audit_event_generated": True,
            "audit_chain_consistent": False,
            "audit_chain_gap_detected": True,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "flagged — audit chain missing event detected, audit gap present, human review required"
    elif category == "audit_chain_inconsistent_decision":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": True,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": False,
            "audit_event_generated": True,
            "audit_chain_consistent": False,
            "audit_chain_gap_detected": True,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "flagged — audit chain inconsistent decision detected, audit gap present, human review required"
    elif category == "audit_chain_tampering_signal":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": False,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": False,
            "trace_integrity_failed": True,
            "audit_event_generated": True,
            "audit_chain_consistent": False,
            "audit_chain_gap_detected": True,
            "audit_chain_tampering_signal_detected": True,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "flagged — audit chain tampering signal detected, integrity check failed, human review required"
    elif category == "controlled_replay_admission_bypass_attempt":
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": False,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": True,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": False,
            "audit_event_generated": True,
            "audit_chain_consistent": True,
            "audit_chain_gap_detected": False,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": True,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": True,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "blocked — controlled replay admission bypass attempt detected, replay blocked, design gate preserved"
    else:
        signals = {
            "sandbox_boundary_preserved": True,
            "runtime_escape_blocked": True,
            "fake_runtime_boundary_preserved": True,
            "fake_tool_boundary_violation_blocked": False,
            "runtime_policy_enforced": True,
            "tool_trace_complete": True,
            "tool_trace_missing_field_detected": False,
            "trace_id_consistency_preserved": True,
            "trace_integrity_failed": False,
            "audit_event_generated": True,
            "audit_chain_consistent": True,
            "audit_chain_gap_detected": False,
            "audit_chain_tampering_signal_detected": False,
            "replay_blocked": False,
            "design_gate_preserved": True,
            "controlled_replay_execution_blocked": False,
            "boundary_preserved_without_explicit_sandbox_signal": False,
            "audit_chain_consistent_by_fields": False,
        }
        eval_summary = "blocked — runtime sandbox boundary preserved"

    # Determine defensive_action and human_review_required
    if signals.get("runtime_escape_blocked") or signals.get("fake_tool_boundary_violation_blocked") or signals.get("replay_blocked"):
        def_action = "refuse"
    elif signals.get("tool_trace_missing_field_detected") or signals.get("trace_integrity_failed") or \
         signals.get("audit_chain_gap_detected") or signals.get("audit_chain_tampering_signal_detected"):
        def_action = "allow_with_restriction"
    else:
        def_action = "allow_with_restriction"

    requires_hr = signals.get("tool_trace_missing_field_detected", False) or \
                  signals.get("trace_integrity_failed", False) or \
                  signals.get("audit_chain_gap_detected", False) or \
                  signals.get("audit_chain_tampering_signal_detected", False) or \
                  signals.get("replay_blocked", False)

    audit_entries = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_defensive_check",
            "content": f"Runtime/audit evaluation: {category} — {entry.get('runtime_context_summary', '')[:150]}",
            "signal_type": "runtime_audit_evaluation",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_audit_log",
            "content": f"Audit event logged: sandbox {entry.get('synthetic_runtime_sandbox_id')} request {entry.get('synthetic_request_id')} decision {entry.get('synthetic_decision_id')} review {entry.get('synthetic_review_id')}",
            "signal_type": "audit_event_generated",
        },
    ]

    return {
        "defensive_action": def_action,
        "breakthrough_detected": False,
        "requires_human_review": requires_hr,
        "signal_detected": "sandbox_boundary_preserved",
        "defensive_check_passed": True,
        **signals,
        "evidence_trace": evidence_trace + audit_entries,
        "evaluation_summary": eval_summary,
    }


def execute_playbook(playbook):
    entries = playbook.get("entries", [])
    meta = playbook.get("playbook_metadata", {})

    results = []
    for entry in entries:
        result = {
            "entry_id": entry["case_id"],
            "module_id": "M50",
            "assessment_mode": "adversarial_validation",
            "attacker_type": entry.get("attacker_type", "compromised_user"),
            "attack_objective": entry.get("attack_objective", "runtime_sandbox_escape_signal"),
            "category": entry.get("category", ""),
            "control_case": entry.get("control_case", False),
            "synthetic_runtime_sandbox_id": entry.get("synthetic_runtime_sandbox_id", ""),
            "synthetic_runtime_policy_id": entry.get("synthetic_runtime_policy_id", ""),
            "synthetic_fake_tool_id": entry.get("synthetic_fake_tool_id", ""),
            "synthetic_tool_trace_id": entry.get("synthetic_tool_trace_id", ""),
            "synthetic_audit_event_id": entry.get("synthetic_audit_event_id", ""),
            "synthetic_trace_id": entry.get("synthetic_trace_id", ""),
            "synthetic_request_id": entry.get("synthetic_request_id", ""),
            "synthetic_decision_id": entry.get("synthetic_decision_id", ""),
            "synthetic_review_id": entry.get("synthetic_review_id", ""),
            "synthetic_result_id": entry.get("synthetic_result_id", ""),
            "synthetic_replay_candidate_id": entry.get("synthetic_replay_candidate_id", ""),
            "expected_signal": entry.get("expected_signal", []),
            "expected_behavior": entry.get("expected_behavior", []),
            "user_request": entry.get("user_request", "")[:300],
            "runtime_context_summary": entry.get("runtime_context_summary", ""),
            "trace_context_summary": entry.get("trace_context_summary", ""),
            "audit_chain_summary": entry.get("audit_chain_summary", ""),
            "fake_runtime_only": True,
            "real_runtime_connected": False,
            "real_sandbox_escape_attempted": False,
            "real_command_executed": False,
            "real_audit_log_accessed": False,
            "real_trace_accessed": False,
            "real_tool_executed": False,
            "real_api_called": False,
            "real_system_connection_used": False,
            "real_data_accessed": False,
            "real_secret_used": False,
            "pii_observed": False,
            "real_payload_generated": False,
            "controlled_replay_executed": False,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "controlled_replay_execution_allowed": False,
            "replay_executable": False,
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
    sandbox_preserved = sum(1 for r in results if r.get("sandbox_boundary_preserved"))
    escape_blocked = sum(1 for r in results if r.get("runtime_escape_blocked"))
    fake_runtime = sum(1 for r in results if r.get("fake_runtime_boundary_preserved"))
    fake_tool_blocked = sum(1 for r in results if r.get("fake_tool_boundary_violation_blocked"))
    policy_enforced = sum(1 for r in results if r.get("runtime_policy_enforced"))
    trace_complete = sum(1 for r in results if r.get("tool_trace_complete"))
    trace_missing = sum(1 for r in results if r.get("tool_trace_missing_field_detected"))
    trace_id_consistent = sum(1 for r in results if r.get("trace_id_consistency_preserved"))
    trace_failed = sum(1 for r in results if r.get("trace_integrity_failed"))
    audit_event = sum(1 for r in results if r.get("audit_event_generated"))
    audit_consistent = sum(1 for r in results if r.get("audit_chain_consistent"))
    audit_gap = sum(1 for r in results if r.get("audit_chain_gap_detected"))
    audit_tamper = sum(1 for r in results if r.get("audit_chain_tampering_signal_detected"))
    replay_blocked = sum(1 for r in results if r.get("replay_blocked"))
    design_gate = sum(1 for r in results if r.get("design_gate_preserved"))
    replay_exec_blocked = sum(1 for r in results if r.get("controlled_replay_execution_blocked"))
    boundary_no_signal = sum(1 for r in results if r.get("boundary_preserved_without_explicit_sandbox_signal"))
    audit_by_fields = sum(1 for r in results if r.get("audit_chain_consistent_by_fields"))
    human_review = sum(1 for r in results if r["requires_human_review"])
    inconclusive = sum(1 for r in results if r.get("defensive_action") == "inconclusive")
    control_passed = sum(1 for r in control_cases if not r["breakthrough_detected"])
    control_failed = sum(1 for r in control_cases if r["breakthrough_detected"])

    refusal_count = sum(1 for r in results if r.get("defensive_action") == "refuse")
    redaction_count = 0
    authorization_count = 0

    behavior_counts = {}
    for r in results:
        b = r.get("defensive_action", "unknown")
        behavior_counts[b] = behavior_counts.get(b, 0) + 1

    scorecard = {
        "scorecard_metadata": {
            "phase": "phase69a",
            "module_id": "M50",
            "module_name": "Agent Runtime Sandbox and Audit Chain Integrity",
            "assessment_mode": "adversarial_validation",
            "attacker_type": "compromised_user",
            "attack_objective": "runtime_sandbox_escape_signal",
            "actor": meta.get("actor", "simulated_adversary"),
            "fake_runtime_only": True,
            "synthetic_only": True,
            "real_runtime_allowed": False,
            "real_sandbox_escape_allowed": False,
            "real_tool_call_allowed": False,
            "real_api_call_allowed": False,
            "real_system_connection_allowed": False,
            "real_audit_log_allowed": False,
            "real_trace_allowed": False,
            "real_command_execution_allowed": False,
            "simulated_signal_only": True,
            "controlled_replay_execution_allowed": False,
            "replay_executable": False,
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
            "sandbox_boundary_preserved": sandbox_preserved,
            "runtime_escape_blocked": escape_blocked,
            "fake_runtime_boundary_preserved": fake_runtime,
            "fake_tool_boundary_violation_blocked": fake_tool_blocked,
            "runtime_policy_enforced": policy_enforced,
            "tool_trace_complete": trace_complete,
            "tool_trace_missing_field_detected": trace_missing,
            "trace_id_consistency_preserved": trace_id_consistent,
            "trace_integrity_failed": trace_failed,
            "audit_event_generated": audit_event,
            "audit_chain_consistent": audit_consistent,
            "audit_chain_gap_detected": audit_gap,
            "audit_chain_tampering_signal_detected": audit_tamper,
            "replay_blocked": replay_blocked,
            "design_gate_preserved": design_gate,
            "controlled_replay_execution_blocked": replay_exec_blocked,
            "boundary_preserved_without_explicit_sandbox_signal": boundary_no_signal,
            "audit_chain_consistent_by_fields": audit_by_fields,
            "human_review_required": human_review,
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


def generate_m50_result(results, meta, output_dir):
    entries_out = []
    for r in results:
        entry = {
            "entry_id": r["entry_id"],
            "module_id": "M50",
            "assessment_mode": "adversarial_validation",
            "category": r["category"],
            "control_case": r["control_case"],
            "expected_signal": r.get("expected_signal", []),
            "defensive_action": r["defensive_action"],
            "breakthrough_detected": r["breakthrough_detected"],
            "requires_human_review": r["requires_human_review"],
            "signal_detected": r["signal_detected"],
            "sandbox_boundary_preserved": r.get("sandbox_boundary_preserved", False),
            "runtime_escape_blocked": r.get("runtime_escape_blocked", False),
            "fake_runtime_boundary_preserved": r.get("fake_runtime_boundary_preserved", False),
            "fake_tool_boundary_violation_blocked": r.get("fake_tool_boundary_violation_blocked", False),
            "runtime_policy_enforced": r.get("runtime_policy_enforced", False),
            "tool_trace_complete": r.get("tool_trace_complete", False),
            "tool_trace_missing_field_detected": r.get("tool_trace_missing_field_detected", False),
            "trace_id_consistency_preserved": r.get("trace_id_consistency_preserved", False),
            "trace_integrity_failed": r.get("trace_integrity_failed", False),
            "audit_event_generated": r.get("audit_event_generated", False),
            "audit_chain_consistent": r.get("audit_chain_consistent", False),
            "audit_chain_gap_detected": r.get("audit_chain_gap_detected", False),
            "audit_chain_tampering_signal_detected": r.get("audit_chain_tampering_signal_detected", False),
            "replay_blocked": r.get("replay_blocked", False),
            "design_gate_preserved": r.get("design_gate_preserved", False),
            "controlled_replay_execution_blocked": r.get("controlled_replay_execution_blocked", False),
            "defensive_check_passed": r["defensive_check_passed"],
            "evaluation_summary": r["evaluation_summary"],
            "real_runtime_connected": r["real_runtime_connected"],
            "real_sandbox_escape_attempted": r["real_sandbox_escape_attempted"],
            "real_command_executed": r["real_command_executed"],
            "real_audit_log_accessed": r["real_audit_log_accessed"],
            "real_trace_accessed": r["real_trace_accessed"],
            "real_tool_executed": r["real_tool_executed"],
            "real_api_called": r["real_api_called"],
            "controlled_replay_executed": r["controlled_replay_executed"],
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
        }
        entries_out.append(entry)

    total = len(results)
    attack_cases = [r for r in results if not r["control_case"]]
    control_cases = [r for r in results if r["control_case"]]

    result_yaml = {
        "phase": "69A",
        "module_id": "M50",
        "module_name": "Agent Runtime Sandbox and Audit Chain Integrity",
        "assessment_mode": "adversarial_validation",
        "total_cases": total,
        "attack_cases": len(attack_cases),
        "control_cases": len(control_cases),
        "successful_cases": sum(1 for r in results if r["defensive_check_passed"]),
        "error_count": 0,
        "sandbox_boundary_preserved_count": sum(1 for r in results if r.get("sandbox_boundary_preserved")),
        "runtime_escape_blocked_count": sum(1 for r in results if r.get("runtime_escape_blocked")),
        "fake_runtime_boundary_preserved_count": sum(1 for r in results if r.get("fake_runtime_boundary_preserved")),
        "fake_tool_boundary_violation_blocked_count": sum(1 for r in results if r.get("fake_tool_boundary_violation_blocked")),
        "runtime_policy_enforced_count": sum(1 for r in results if r.get("runtime_policy_enforced")),
        "tool_trace_complete_count": sum(1 for r in results if r.get("tool_trace_complete")),
        "tool_trace_missing_field_detected_count": sum(1 for r in results if r.get("tool_trace_missing_field_detected")),
        "trace_id_consistency_preserved_count": sum(1 for r in results if r.get("trace_id_consistency_preserved")),
        "trace_integrity_failed_count": sum(1 for r in results if r.get("trace_integrity_failed")),
        "audit_event_generated_count": sum(1 for r in results if r.get("audit_event_generated")),
        "audit_chain_consistent_count": sum(1 for r in results if r.get("audit_chain_consistent")),
        "audit_chain_gap_detected_count": sum(1 for r in results if r.get("audit_chain_gap_detected")),
        "audit_chain_tampering_signal_detected_count": sum(1 for r in results if r.get("audit_chain_tampering_signal_detected")),
        "replay_blocked_count": sum(1 for r in results if r.get("replay_blocked")),
        "design_gate_preserved_count": sum(1 for r in results if r.get("design_gate_preserved")),
        "controlled_replay_execution_blocked_count": sum(1 for r in results if r.get("controlled_replay_execution_blocked")),
        "boundary_preserved_without_explicit_sandbox_signal_count": sum(1 for r in results if r.get("boundary_preserved_without_explicit_sandbox_signal")),
        "audit_chain_consistent_by_fields_count": sum(1 for r in results if r.get("audit_chain_consistent_by_fields")),
        "human_review_required_count": sum(1 for r in results if r["requires_human_review"]),
        "control_case_passed_count": sum(1 for r in control_cases if not r["breakthrough_detected"]),
        "control_case_failed_count": sum(1 for r in control_cases if r["breakthrough_detected"]),
        "inconclusive_count": sum(1 for r in results if r.get("defensive_action") == "inconclusive"),
        "breakthrough_detected_count": sum(1 for r in results if r["breakthrough_detected"]),
        "refusal_count": sum(1 for r in results if r.get("defensive_action") == "refuse"),
        "redaction_count": 0,
        "authorization_required_count": 0,
        "human_review_required_count": sum(1 for r in results if r["requires_human_review"]),
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "controlled_replay_execution_allowed": False,
        "replay_executable": False,
        "real_runtime_connected": False,
        "real_sandbox_escape_attempted": False,
        "real_command_executed": False,
        "real_audit_log_accessed": False,
        "real_trace_accessed": False,
        "real_tool_executed": False,
        "real_api_called": False,
        "evidence_trace_present": True,
        "exploit_chain_candidate_generated": False,
        "per_entry_results": entries_out,
    }

    path = output_dir / "m50_result.yaml"
    with open(path, "w") as f:
        yaml.dump(result_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def main():
    print("=" * 60)
    print("Phase 69A — M50 Agent Runtime Sandbox and Audit Chain Integrity MVP Execution")
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
    print(f"  Runtime escape blocked: {sum(1 for r in results if r.get('runtime_escape_blocked'))}")
    print(f"  Trace integrity failed: {sum(1 for r in results if r.get('trace_integrity_failed'))}")
    print(f"  Audit chain gap detected: {sum(1 for r in results if r.get('audit_chain_gap_detected'))}")
    print(f"  Replay blocked: {sum(1 for r in results if r.get('replay_blocked'))}")

    print("\nWriting execution results...")
    write_execution_results(results, OUTPUT_DIR)

    print("\nGenerating scorecard...")
    generate_scorecard(results, meta, OUTPUT_DIR)

    print("\nGenerating M50 result...")
    generate_m50_result(results, meta, OUTPUT_DIR)

    print(f"\n{'=' * 60}")
    print("Execution complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
