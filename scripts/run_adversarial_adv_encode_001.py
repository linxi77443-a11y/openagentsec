#!/usr/bin/env python3
"""ADV-ENCODE-001 — Encoding Obfuscation Attack Playbook MVP Execution Script.

Extends DPI-012 base64 framework with Unicode homoglyph, emoji hidden
instruction, and zero-width character obfuscation variants.

Simulates adversarial_validation evaluation for all playbook entries.
No real API calls. SIM_ placeholder data only.
All findings remain candidate level, confirmed_vulnerability=false.
"""
import json, sys, yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/encoding_obfuscation_playbook/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/adv_encode_001"

# No breakthrough simulation in this MVP
SIMULATE_BREAKTHROUGH_IDS = set()


def load_playbook(path):
    with open(path) as f:
        return yaml.safe_load(f)


def simulate_defense(entry):
    """Simulate defense evaluation for a single playbook entry.

    Returns evaluation result dict with encoding-specific signal fields.
    """
    eid = entry["entry_id"]
    is_control = entry.get("control_case", False)
    expected = entry.get("expected_behavior", "refuse")
    category = entry.get("category", "")
    expected_signal = entry.get("expected_signal", "")

    # Control cases: no threat detected
    if is_control:
        return {
            "defensive_action": "normal_response",
            "breakthrough_detected": False,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "requires_human_review": False,
            "signal_detected": None,
            "defensive_check_passed": True,
            "inconclusive": False,
            "encoding_obfuscation_detected": False,
            "instruction_boundary_preserved": True,
            "obfuscated_instruction_ignored": False,
            "unsafe_tool_trace_signal": False,
            "simulated_exfiltration_signal": False,
            "real_runtime_accessed": False,
            "real_sandbox_accessed": False,
            "real_system_call_executed": False,
            "real_tool_executed": False,
            "real_audit_log_accessed": False,
            "real_network_request_sent": False,
            "real_file_system_written": False,
            "evidence_trace": [],
            "exploit_chain_candidate": [],
            "evaluation_summary": "control_case — no adversarial signal detected",
        }

    # Breakthrough simulation (if configured)
    if eid in SIMULATE_BREAKTHROUGH_IDS:
        return {
            "defensive_action": "partial_bypass",
            "breakthrough_detected": True,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "requires_human_review": True,
            "signal_detected": f"incomplete_{expected_signal}",
            "defensive_check_passed": False,
            "inconclusive": False,
            "encoding_obfuscation_detected": True,
            "instruction_boundary_preserved": False,
            "obfuscated_instruction_ignored": True,
            "unsafe_tool_trace_signal": category in ("emoji_hidden_instruction_obfuscation", "zero_width_character_obfuscation"),
            "simulated_exfiltration_signal": category in ("emoji_hidden_instruction_obfuscation",),
            "real_runtime_accessed": False,
            "real_sandbox_accessed": False,
            "real_system_call_executed": False,
            "real_tool_executed": False,
            "real_audit_log_accessed": False,
            "real_network_request_sent": False,
            "real_file_system_written": False,
            "evidence_trace": [
                {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "prompt", "content": entry["prompt"][:80], "signal_type": "adversarial_prompt_detected"},
                {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "evaluation", "content": f"Defense attempted {expected} but partial content leaked", "signal_type": "breakthrough_observed"},
            ],
            "exploit_chain_candidate": [
                {"step": 1, "observation": "Adversarial prompt submitted with encoding obfuscation", "signal": "encoding_obfuscation_attempt"},
                {"step": 2, "observation": "Defense triggered but incomplete — partial output returned", "signal": "boundary_erosion"},
            ],
            "evaluation_summary": f"breakthrough — defense triggered ({expected}) but partial content leakage detected via {category}",
        }

    # Standard defense: attack blocked — map category to signals
    encoding_signals = _get_category_signals(category, expected)

    result = {
        "defensive_action": expected,
        "breakthrough_detected": False,
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "requires_human_review": False,
        "signal_detected": expected_signal,
        "defensive_check_passed": True,
        "inconclusive": False,
        "real_runtime_accessed": False,
        "real_sandbox_accessed": False,
        "real_system_call_executed": False,
        "real_tool_executed": False,
        "real_audit_log_accessed": False,
        "real_network_request_sent": False,
        "real_file_system_written": False,
        "evidence_trace": [
            {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "prompt", "content": entry["prompt"][:80], "signal_type": "adversarial_prompt_detected"},
            {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "evaluation", "content": f"Defense applied: {expected}", "signal_type": "defensive_action_applied"},
        ],
        "exploit_chain_candidate": [],
        "evaluation_summary": f"blocked — defense applied ({expected}), no breakthrough",
    }
    result.update(encoding_signals)
    return result


def _get_category_signals(category, expected_behavior):
    """Return encoding-specific signal fields based on attack category."""
    if category == "base64_baseline":
        return {
            "encoding_obfuscation_detected": True,
            "instruction_boundary_preserved": True,
            "obfuscated_instruction_ignored": True,
            "unsafe_tool_trace_signal": False,
            "simulated_exfiltration_signal": False,
        }
    elif category == "unicode_homoglyph_obfuscation":
        return {
            "encoding_obfuscation_detected": True,
            "instruction_boundary_preserved": True,
            "obfuscated_instruction_ignored": True,
            "unsafe_tool_trace_signal": False,
            "simulated_exfiltration_signal": False,
        }
    elif category == "emoji_hidden_instruction_obfuscation":
        return {
            "encoding_obfuscation_detected": True,
            "instruction_boundary_preserved": expected_behavior == "refuse",
            "obfuscated_instruction_ignored": True,
            "unsafe_tool_trace_signal": expected_behavior == "block_tool_call",
            "simulated_exfiltration_signal": False,
        }
    elif category == "zero_width_character_obfuscation":
        return {
            "encoding_obfuscation_detected": True,
            "instruction_boundary_preserved": True,
            "obfuscated_instruction_ignored": True,
            "unsafe_tool_trace_signal": expected_behavior == "block_tool_call",
            "simulated_exfiltration_signal": False,
        }
    else:
        return {
            "encoding_obfuscation_detected": False,
            "instruction_boundary_preserved": True,
            "obfuscated_instruction_ignored": False,
            "unsafe_tool_trace_signal": False,
            "simulated_exfiltration_signal": False,
        }


def execute_playbook(playbook):
    """Execute all playbook entries and produce execution results."""
    entries = playbook.get("entries", [])
    meta = playbook.get("playbook_metadata", {})

    results = []
    for entry in entries:
        eval_result = simulate_defense(entry)
        result = {
            "entry_id": entry["entry_id"],
            "module_id": meta.get("module_id", "ADV-ENCODE-001"),
            "adversarial_playbook_type": meta.get("adversarial_playbook_type", "encoding_obfuscation"),
            "category": entry.get("category", ""),
            "scenario": entry.get("scenario", ""),
            "control_case": entry.get("control_case", False),
            "expected_behavior": entry.get("expected_behavior", ""),
            "expected_signal": entry.get("expected_signal", ""),
            "prompt": entry["prompt"],
        }
        result.update(eval_result)
        results.append(result)

    return results


def write_execution_results(results, output_dir):
    """Write execution_results.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "execution_results.json"
    with open(path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  [OK] {path} — {len(results)} entries")
    return path


def generate_result_yaml(results, meta, output_dir):
    """Generate adv_encode_001_result.yaml with parser fields and per-entry breakdown."""
    total = len(results)
    attack_entries = [r for r in results if not r["control_case"]]
    control_entries = [r for r in results if r["control_case"]]

    encoding_detected = sum(1 for r in attack_entries if r["encoding_obfuscation_detected"])
    boundary_preserved = sum(1 for r in attack_entries if r["instruction_boundary_preserved"])
    instr_ignored = sum(1 for r in attack_entries if r["obfuscated_instruction_ignored"])
    unsafe_tool = sum(1 for r in attack_entries if r["unsafe_tool_trace_signal"])
    exfil_signal = sum(1 for r in attack_entries if r["simulated_exfiltration_signal"])
    human_review = sum(1 for r in results if r["requires_human_review"])

    # Per-category distribution
    category_dist = {}
    for r in results:
        cat = r["category"]
        if cat not in category_dist:
            category_dist[cat] = {"total": 0, "refuse": 0, "block_tool_call": 0, "normal_response": 0, "breakthrough": 0}
        category_dist[cat]["total"] += 1
        action = r.get("defensive_action", "unknown")
        if action in category_dist[cat]:
            category_dist[cat][action] += 1
        if r.get("breakthrough_detected"):
            category_dist[cat]["breakthrough"] += 1

    result_yaml = {
        "result_metadata": {
            "module_id": "ADV-ENCODE-001",
            "phase": "adv_encode_001",
            "assessment_mode": "adversarial_validation",
            "adversarial_playbook_type": "encoding_obfuscation",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "attack_execution_allowed": False,
            "payload_generation_allowed": False,
            "all_findings_are_candidate_level": True,
            "result_is_candidate_level": True,
            "total_cases": total,
            "attack_cases": len(attack_entries),
            "control_cases": len(control_entries),
        },
        "parser_fields": {
            "encoding_obfuscation_detected": encoding_detected,
            "instruction_boundary_preserved": boundary_preserved,
            "obfuscated_instruction_ignored": instr_ignored,
            "unsafe_tool_trace_signal": unsafe_tool,
            "simulated_exfiltration_signal": exfil_signal,
            "human_review_required_count": human_review,
        },
        "category_distribution": category_dist,
        "control_case_performance": {
            "total_controls": len(control_entries),
            "all_passed": all(r.get("defensive_check_passed", True) for r in control_entries),
            "no_false_positives": all(not r.get("encoding_obfuscation_detected", True) for r in control_entries),
        },
        "per_entry_results": [
            {
                "entry_id": r["entry_id"],
                "category": r["category"],
                "control_case": r["control_case"],
                "defensive_action": r["defensive_action"],
                "breakthrough_detected": r["breakthrough_detected"],
                "confirmed_vulnerability": r["confirmed_vulnerability"],
                "formal_finding_allowed": r["formal_finding_allowed"],
                "requires_human_review": r["requires_human_review"],
                "signal_detected": r["signal_detected"],
                "defensive_check_passed": r["defensive_check_passed"],
                "inconclusive": r["inconclusive"],
                "encoding_obfuscation_detected": r["encoding_obfuscation_detected"],
                "instruction_boundary_preserved": r["instruction_boundary_preserved"],
                "obfuscated_instruction_ignored": r["obfuscated_instruction_ignored"],
                "unsafe_tool_trace_signal": r["unsafe_tool_trace_signal"],
                "simulated_exfiltration_signal": r["simulated_exfiltration_signal"],
                "evaluation_summary": r["evaluation_summary"],
            }
            for r in results
        ],
    }

    path = output_dir / "adv_encode_001_result.yaml"
    with open(path, "w") as f:
        yaml.dump(result_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")
    return result_yaml


def generate_scorecard(results, meta, output_dir):
    """Generate capability_scorecard.yaml for adversarial_validation mode."""
    total = len(results)
    breakthrough = sum(1 for r in results if r["breakthrough_detected"])
    blocked = sum(1 for r in results if not r["breakthrough_detected"] and not r["control_case"])
    control_ok = sum(1 for r in results if r["control_case"] and not r["breakthrough_detected"])
    human_review = sum(1 for r in results if r["requires_human_review"])
    inconclusive = sum(1 for r in results if r.get("inconclusive"))

    # Per-behavior counts
    behavior_counts = {}
    for r in results:
        b = r.get("defensive_action", "unknown")
        behavior_counts[b] = behavior_counts.get(b, 0) + 1

    scorecard = {
        "scorecard_metadata": {
            "phase": "adv_encode_001",
            "module_id": "ADV-ENCODE-001",
            "run_id": "adv_encode_001-mvp",
            "assessment_mode": "adversarial_validation",
            "adversarial_playbook_type": "encoding_obfuscation",
            "actor": meta.get("actor", "simulated_adversary"),
            "attacker_type": meta.get("attacker_type", "external_user"),
            "attack_objective": meta.get("attack_objective", ["context_poisoning", "data_exposure", "tool_misuse", "unauthorized_access"]),
            "target": "SIM_ simulated defense (no real API)",
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "attack_execution_allowed": False,
            "payload_generation_allowed": False,
            "all_findings_are_candidate_level": True,
            "total_entries": total,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "results_summary": {
            "total": total,
            "breakthrough_detected": breakthrough,
            "blocked": blocked,
            "control_passed": control_ok,
            "inconclusive": inconclusive,
            "human_review_required": human_review,
            "defensive_behavior_distribution": behavior_counts,
            "signal_summary": {
                "encoding_obfuscation_detected": sum(1 for r in results if r.get("encoding_obfuscation_detected")),
                "instruction_boundary_preserved": sum(1 for r in results if r.get("instruction_boundary_preserved")),
                "obfuscated_instruction_ignored": sum(1 for r in results if r.get("obfuscated_instruction_ignored")),
                "unsafe_tool_trace_signal": sum(1 for r in results if r.get("unsafe_tool_trace_signal")),
                "simulated_exfiltration_signal": sum(1 for r in results if r.get("simulated_exfiltration_signal")),
            },
        },
        "capability_value": "not_applicable",
        "risk_level": "not_applicable",
        "category_coverage": list(dict.fromkeys(r["category"] for r in results if not r["control_case"])),
    }

    path = output_dir / "capability_scorecard.yaml"
    with open(path, "w") as f:
        yaml.dump(scorecard, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")
    return scorecard


def generate_evidence_candidates(results, output_dir):
    """Generate red_team_evidence_candidates.yaml."""
    attack_entries = [r for r in results if not r["control_case"]]
    candidates = []
    for i, r in enumerate(attack_entries):
        candidates.append({
            "candidate_id": f"<SIM_RED_CAND_ENC_{i+1:03d}>",
            "source_case_id": r["entry_id"],
            "category": r["category"],
            "evidence_trace": r.get("evidence_trace", []),
            "breakthrough_detected": r["breakthrough_detected"],
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "all_findings_are_candidate_level": True,
            "defense_state": "blocked" if r["defensive_check_passed"] else "partial_bypass",
            "human_review_required": r["requires_human_review"],
        })

    evidence_yaml = {
        "evidence_metadata": {
            "module_id": "ADV-ENCODE-001",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_candidates": len(candidates),
            "confirmed_vulnerability": False,
            "all_findings_are_candidate_level": True,
        },
        "evidence_candidates": candidates,
    }

    path = output_dir / "red_team_evidence_candidates.yaml"
    with open(path, "w") as f:
        yaml.dump(evidence_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def generate_blue_controls(results, output_dir):
    """Generate blue_control_candidates.yaml."""
    categories_seen = set()
    controls = []
    for r in results:
        cat = r["category"]
        if cat == "control" or cat in categories_seen:
            continue
        categories_seen.add(cat)
        controls.append({
            "control_id": f"<SIM_BLUE_CTRL_{cat.upper()[:4]}>",
            "category": cat,
            "source_case_id": r["entry_id"],
            "rationale": f"Blue team detection control for {cat} — encoding obfuscation detection and boundary preservation verified",
            "detection_method": "encoding_pattern_matching" if cat != "base64_baseline" else "base64_decode_detection",
            "recommended_action": "implement encoding obfuscation detection filter for this category",
            "confirmed_vulnerability": False,
            "all_findings_are_candidate_level": True,
        })

    blue_yaml = {
        "blue_control_metadata": {
            "module_id": "ADV-ENCODE-001",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_controls": len(controls),
            "all_findings_are_candidate_level": True,
        },
        "control_candidates": controls,
    }

    path = output_dir / "blue_control_candidates.yaml"
    with open(path, "w") as f:
        yaml.dump(blue_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def generate_purple_retests(results, output_dir):
    """Generate purple_retest_candidates.yaml."""
    retests = []
    category_pairs = list(dict.fromkeys(r["category"] for r in results if not r["control_case"]))
    for i, cat in enumerate(category_pairs):
        cat_entries = [r for r in results if r["category"] == cat]
        retests.append({
            "retest_id": f"<SIM_PURPLE_RETEST_{i+1:03d}>",
            "category": cat,
            "source_case_ids": [r["entry_id"] for r in cat_entries],
            "test_focus": f"Purple team retest for {cat} — verify encoding obfuscation detection and boundary preservation",
            "retest_method": "run same adversarial prompts and verify consistent defensive behavior",
            "expected_outcome": "all entries blocked, no breakthrough",
            "confirmed_vulnerability": False,
            "all_findings_are_candidate_level": True,
        })

    purple_yaml = {
        "purple_retest_metadata": {
            "module_id": "ADV-ENCODE-001",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_retests": len(retests),
            "all_findings_are_candidate_level": True,
        },
        "retest_candidates": retests,
    }

    path = output_dir / "purple_retest_candidates.yaml"
    with open(path, "w") as f:
        yaml.dump(purple_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def main():
    print("=" * 60)
    print("ADV-ENCODE-001 — Encoding Obfuscation MVP Execution")
    print("=" * 60)

    print("\nLoading playbook...")
    playbook = load_playbook(PLAYBOOK_PATH)
    meta = playbook.get("playbook_metadata", {})
    print(f"  Playbook: {PLAYBOOK_PATH.name}")
    print(f"  Module: {meta.get('module_id', 'N/A')}")
    print(f"  Type: {meta.get('adversarial_playbook_type', 'N/A')}")
    print(f"  Entries: {len(playbook.get('entries', []))}")

    print("\nSimulating defense evaluation...")
    results = execute_playbook(playbook)

    breakout_count = sum(1 for r in results if r["breakthrough_detected"])
    print(f"  Entries evaluated: {len(results)}")
    print(f"  Breakthrough detected: {breakout_count}")
    print(f"  Human review required: {sum(1 for r in results if r['requires_human_review'])}")

    print("\nWriting execution results...")
    write_execution_results(results, OUTPUT_DIR)

    print("\nGenerating result YAML...")
    generate_result_yaml(results, meta, OUTPUT_DIR)

    print("\nGenerating scorecard...")
    generate_scorecard(results, meta, OUTPUT_DIR)

    print("\nGenerating evidence candidates...")
    generate_evidence_candidates(results, OUTPUT_DIR)

    print("\nGenerating blue controls...")
    generate_blue_controls(results, OUTPUT_DIR)

    print("\nGenerating purple retests...")
    generate_purple_retests(results, OUTPUT_DIR)

    print(f"\n{'=' * 60}")
    print("Execution complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
