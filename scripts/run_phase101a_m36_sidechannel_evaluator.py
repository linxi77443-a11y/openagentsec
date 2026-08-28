#!/usr/bin/env python3
"""Phase 101A — M36 Side-channel Timing & Resource Exhaustion Defense Evaluator Runner.

Simulates adversarial_validation evaluation for M36 side-channel timing probes and
asymmetric computational resource exhaustion entries.
No real API gateways, no real billing/quota systems, no real inference hardware access,
no real network timing probes. SIM_ placeholder data only. Fake runtime only.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/m36_sidechannel_timing_evaluator/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase101a_m36_sidechannel_evaluator"
EXECUTION_RESULTS_PATH = OUTPUT_DIR / "execution_results.json"

SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def simulate_sidechannel_defense(entry: dict) -> dict:
    """Simulate advanced defense evaluation for M36 side-channel timing & resource exhaustion."""
    eid = entry["entry_id"]
    module_id = entry.get("module_id", "M36")
    is_control = entry.get("control_case", False)
    category = entry.get("category", "")
    modality = entry.get("modality", "inference_timing_sidechannel")
    timing_tech = entry.get("timing_technique", "unknown")
    amp_factor = entry.get("simulated_amplification_factor", 1.0)
    probe_type = entry.get("simulated_probe_type", "unknown")
    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    evidence_trace = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_sidechannel_timing_monitor",
            "content": f"Inspected synthetic probe session {entry.get('synthetic_probe_id', '')} with modality {modality} and probe type {probe_type}.",
            "signal_type": "probe_session_inspection",
        },
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "synthetic_amplification_analyzer",
            "content": f"Evaluated computational amplification factor {amp_factor}x for target vector {entry.get('synthetic_target_vector', '')} with signature {entry.get('synthetic_timing_signature', '')}.",
            "signal_type": "amplification_factor_evaluation",
        },
    ]

    base_security_flags = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "controlled_replay_execution_allowed": False,
        "synthetic_only": True,
        "fake_runtime_only": True,
        "real_api_gateway_accessed": False,
        "real_billing_system_accessed": False,
        "real_model_endpoint_accessed": False,
        "real_quota_system_accessed": False,
        "real_timing_probe_network_accessed": False,
        "real_inference_hardware_accessed": False,
        "real_tool_call_executed": False,
    }

    # Initialize all specific detection flags to False
    flag_dict = {
        "timing_probe_oracle_detected": False,
        "asymmetric_cot_loop_exhaustion_detected": False,
        "rag_retrieval_fanout_exhaustion_detected": False,
        "tool_recursion_deadlock_detected": False,
        "kv_cache_eviction_probe_detected": False,
        "token_expansion_blowup_detected": False,
        "speculative_decoding_thrashing_detected": False,
        "distributed_subtask_amplification_detected": False,
        "benign_resource_usage_allowed": False,
    }

    if is_control:
        flag_dict["benign_resource_usage_allowed"] = True
        return {
            "entry_id": eid,
            "module_id": module_id,
            "category": category,
            "modality": modality,
            "timing_technique": timing_tech,
            "simulated_amplification_factor": amp_factor,
            "simulated_probe_type": probe_type,
            "control_case": True,
            "defensive_action": "normal_usage_allowed",
            "breakthrough_detected": False,
            "requires_human_review": False,
            "signal_detected": "benign_resource_usage_allowed",
            "defensive_check_passed": True,
            "resource_exhaustion_blocked": False,
            "resource_usage_allowed": True,
            **flag_dict,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "synthetic_resource_guardrail",
                    "content": f"Control case passed: {category} evaluated within baseline limits (amplification {amp_factor}x, standard latency profile).",
                    "signal_type": "benign_resource_passed",
                }
            ],
            **base_security_flags,
        }

    # Attack cases
    if is_breakthrough:
        return {
            "entry_id": eid,
            "module_id": module_id,
            "category": category,
            "modality": modality,
            "timing_technique": timing_tech,
            "simulated_amplification_factor": amp_factor,
            "simulated_probe_type": probe_type,
            "control_case": False,
            "defensive_action": "normal_usage_allowed",
            "breakthrough_detected": True,
            "requires_human_review": True,
            "signal_detected": "none",
            "defensive_check_passed": False,
            "resource_exhaustion_blocked": False,
            "resource_usage_allowed": True,
            **flag_dict,
            "evidence_trace": evidence_trace + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "synthetic_resource_guardrail",
                    "content": "Simulated breakthrough: side-channel timing probe or resource exhaustion bypassed guardrails.",
                    "signal_type": "filter_bypass_simulated",
                }
            ],
            **base_security_flags,
        }

    # Normal interception of simulated attack
    signal_name = "resource_exhaustion_detected"
    detail_reason = "Resource abuse or sidechannel probe intercepted."

    if category == "timing_probe_token_oracle":
        flag_dict["timing_probe_oracle_detected"] = True
        signal_name = "timing_probe_oracle_detected"
        detail_reason = f"High-frequency differential TTFT timing probe detected (amp {amp_factor}x). Latency jitter defense engaged."
    elif category == "asymmetric_cot_loop_exhaustion":
        flag_dict["asymmetric_cot_loop_exhaustion_detected"] = True
        signal_name = "asymmetric_cot_loop_exhaustion_detected"
        detail_reason = f"Recursive CoT reasoning depth explosion detected (amplification {amp_factor}x). Circuit breaker triggered."
    elif category == "rag_retrieval_fanout_exhaustion":
        flag_dict["rag_retrieval_fanout_exhaustion_detected"] = True
        signal_name = "rag_retrieval_fanout_exhaustion_detected"
        detail_reason = f"High-entropy RAG multi-hop query fanout overload intercepted (amplification {amp_factor}x). Vector search quota enforced."
    elif category == "tool_recursion_deadlock_amplification":
        flag_dict["tool_recursion_deadlock_detected"] = True
        signal_name = "tool_recursion_deadlock_detected"
        detail_reason = f"Cyclic tool dependency graph deadlock loop detected (amplification {amp_factor}x). Threadpool exhaustion prevented."
    elif category == "kv_cache_eviction_sidechannel_probe":
        flag_dict["kv_cache_eviction_probe_detected"] = True
        signal_name = "kv_cache_eviction_probe_detected"
        detail_reason = f"Multi-tenant KV-cache eviction latency jitter probe identified (amp {amp_factor}x). Tenant cache isolation enforced."
    elif category == "token_expansion_quadratic_blowup":
        flag_dict["token_expansion_blowup_detected"] = True
        signal_name = "token_expansion_blowup_detected"
        detail_reason = f"Recursive macro token expansion bomb detected (amplification {amp_factor}x). Output bandwidth limit enforced."
    elif category == "speculative_decoding_cache_thrashing":
        flag_dict["speculative_decoding_thrashing_detected"] = True
        signal_name = "speculative_decoding_thrashing_detected"
        detail_reason = f"Adversarial speculative decoding de-synchronization thrashing detected (amp {amp_factor}x). Deterministic fallback engaged."
    elif category == "distributed_agent_subtask_amplification":
        flag_dict["distributed_subtask_amplification_detected"] = True
        signal_name = "distributed_subtask_amplification_detected"
        detail_reason = f"Hierarchical agent swarm fork bomb expansion detected (amplification {amp_factor}x). Multi-agent budget quota enforced."

    return {
        "entry_id": eid,
        "module_id": module_id,
        "category": category,
        "modality": modality,
        "timing_technique": timing_tech,
        "simulated_amplification_factor": amp_factor,
        "simulated_probe_type": probe_type,
        "control_case": False,
        "defensive_action": "refuse",
        "breakthrough_detected": False,
        "requires_human_review": True,
        "signal_detected": signal_name,
        "defensive_check_passed": True,
        "resource_exhaustion_blocked": True,
        "resource_usage_allowed": False,
        **flag_dict,
        "evidence_trace": evidence_trace + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "synthetic_resource_guardrail",
                "content": f"Interception confirmed: {detail_reason}",
                "signal_type": signal_name,
            }
        ],
        **base_security_flags,
    }


def main():
    print("=" * 70)
    print("Phase 101A — M36 Side-channel Timing & Resource Exhaustion Evaluator Runner")
    print("Adversarial Validation Mode (Synthetic Only / Fake Runtime Only)")
    print("=" * 70)

    if not PLAYBOOK_PATH.exists():
        print(f"Error: Playbook not found at {PLAYBOOK_PATH}")
        sys.exit(1)

    playbook = load_playbook(PLAYBOOK_PATH)
    entries = playbook.get("entries", [])
    print(f"\nLoaded {len(entries)} entries from {PLAYBOOK_PATH.name}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    execution_results = []
    for entry in entries:
        eid = entry["entry_id"]
        cat = entry.get("category", "")
        amp = entry.get("simulated_amplification_factor", 1.0)
        print(f"  Evaluating {eid} [{cat}] (Amp: {amp}x)...", end=" ")
        res = simulate_sidechannel_defense(entry)
        execution_results.append(res)
        action = res["defensive_action"]
        bt = res["breakthrough_detected"]
        sig = res["signal_detected"]
        print(f"Action={action}, Breakthrough={bt}, Signal={sig}")

    with open(EXECUTION_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(execution_results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved execution results ({len(execution_results)} entries) to {EXECUTION_RESULTS_PATH}")

    # Quick summary
    attacks = [r for r in execution_results if not r.get("control_case")]
    controls = [r for r in execution_results if r.get("control_case")]
    passed = sum(1 for r in execution_results if r.get("defensive_check_passed"))
    bts = sum(1 for r in execution_results if r.get("breakthrough_detected"))

    print(f"\nExecution Summary:")
    print(f"  Total Cases:     {len(execution_results)}")
    print(f"  Attack Cases:    {len(attacks)} (Interceptions: {len(attacks) - bts})")
    print(f"  Control Cases:   {len(controls)} (Passed: {sum(1 for c in controls if not c.get('breakthrough_detected'))})")
    print(f"  Breakthroughs:   {bts}")
    print(f"  Defense Passed:  {passed}/{len(execution_results)} ({passed/len(execution_results)*100:.1f}%)")
    print("=" * 70)


if __name__ == "__main__":
    main()
