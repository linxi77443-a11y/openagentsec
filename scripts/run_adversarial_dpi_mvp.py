#!/usr/bin/env python3
"""Phase 62B — Direct Prompt Injection MVP Execution Script.

Simulates adversarial_validation evaluation for DPI playbook entries.
No real API calls. SIM_ placeholder data only.
"""
import json, sys, yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/direct_prompt_injection_mvp/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase62b_dpi_mvp"

# Entry IDs that simulate a breakthrough (defense partially fails)
SIMULATE_BREAKTHROUGH_IDS = {"DPI-006", "DPI-008"}


def load_playbook(path):
    with open(path) as f:
        return yaml.safe_load(f)


def simulate_defense(entry):
    """Simulate defense evaluation for a single playbook entry.

    Returns evaluation result dict.
    """
    eid = entry["entry_id"]
    is_control = entry.get("control_case", False)
    expected = entry.get("expected_behavior", "refuse")

    # Control cases: no threat detected
    if is_control:
        return {
            "defensive_action": "normal_response",
            "breakthrough_detected": False,
            "requires_human_review": False,
            "signal_detected": None,
            "defensive_check_passed": True,
            "evidence_trace": [],
            "exploit_chain_candidate": [],
            "evaluation_summary": "control_case — no adversarial signal detected",
        }

    # Breakthrough simulation
    if eid in SIMULATE_BREAKTHROUGH_IDS:
        return {
            "defensive_action": "partial_bypass",
            "breakthrough_detected": True,
            "requires_human_review": True,
            "signal_detected": f"incomplete_{expected}_signal",
            "defensive_check_passed": False,
            "evidence_trace": [
                {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "prompt", "content": entry["prompt"][:80], "signal_type": "adversarial_prompt_detected"},
                {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "evaluation", "content": "Defense attempted {expected} but partial content leaked", "signal_type": "breakthrough_observed"},
            ],
            "exploit_chain_candidate": [
                {"step": 1, "observation": "Adversarial prompt submitted", "signal": "direct_injection_attempt"},
                {"step": 2, "observation": "Defense triggered but incomplete — partial output returned", "signal": "boundary_erosion"},
            ],
            "evaluation_summary": f"breakthrough — defense triggered ({expected}) but partial content leakage detected",
        }

    # Standard defense: attack blocked
    return {
        "defensive_action": expected,
        "breakthrough_detected": False,
        "requires_human_review": False,
        "signal_detected": entry.get("expected_signal", "refusal_signal"),
        "defensive_check_passed": True,
        "evidence_trace": [
            {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "prompt", "content": entry["prompt"][:80], "signal_type": "adversarial_prompt_detected"},
            {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "evaluation", "content": f"Defense applied: {expected}", "signal_type": "defensive_action_applied"},
        ],
        "exploit_chain_candidate": [],
        "evaluation_summary": f"blocked — defense applied ({expected}), no breakthrough",
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
            "adversarial_playbook_type": meta.get("adversarial_playbook_type", "direct_prompt_injection"),
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


def generate_scorecard(results, meta, output_dir):
    """Generate capability_scorecard.yaml for adversarial_validation mode."""
    total = len(results)
    breakthrough = sum(1 for r in results if r["breakthrough_detected"])
    blocked = sum(1 for r in results if not r["breakthrough_detected"] and not r["control_case"])
    control_ok = sum(1 for r in results if r["control_case"] and not r["breakthrough_detected"])
    human_review = sum(1 for r in results if r["requires_human_review"])
    inconclusive = sum(1 for r in results if r.get("defensive_action") == "inconclusive")

    # Per-behavior counts
    behavior_counts = {}
    for r in results:
        b = r.get("defensive_action", "unknown")
        behavior_counts[b] = behavior_counts.get(b, 0) + 1

    scorecard = {
        "scorecard_metadata": {
            "phase": "phase62b",
            "run_id": "phase62b-dpi-mvp",
            "assessment_mode": "adversarial_validation",
            "adversarial_playbook_type": "direct_prompt_injection",
            "actor": meta.get("actor", "simulated_adversary"),
            "attacker_profile": meta.get("attacker_profile", "remote_unauthenticated"),
            "attacker_type": meta.get("attacker_type", "direct_prompt_injection"),
            "attack_objective": meta.get("attack_objective", "data_exposure"),
            "target": "SIM_ simulated defense (no real API)",
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
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
        },
        "category_coverage": list(dict.fromkeys(r["category"] for r in results if not r["control_case"])),
    }

    path = output_dir / "capability_scorecard.yaml"
    with open(path, "w") as f:
        yaml.dump(scorecard, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")
    return scorecard


def generate_adversarial_result(results, output_dir):
    """Generate adversarial_result.yaml with per-entry breakdown."""
    entries_out = []
    for r in results:
        entries_out.append({
            "entry_id": r["entry_id"],
            "category": r["category"],
            "scenario": r["scenario"],
            "control_case": r["control_case"],
            "expected_behavior": r["expected_behavior"],
            "defensive_action": r["defensive_action"],
            "breakthrough_detected": r["breakthrough_detected"],
            "requires_human_review": r["requires_human_review"],
            "signal_detected": r["signal_detected"],
            "defensive_check_passed": r["defensive_check_passed"],
            "evaluation_summary": r["evaluation_summary"],
        })

    result_yaml = {
        "adversarial_result_metadata": {
            "run_id": "phase62b-dpi-mvp",
            "assessment_mode": "adversarial_validation",
            "adversarial_playbook_type": "direct_prompt_injection",
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
        },
        "per_entry_results": entries_out,
    }

    path = output_dir / "adversarial_result.yaml"
    with open(path, "w") as f:
        yaml.dump(result_yaml, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def main():
    print("=" * 60)
    print("Phase 62B — Direct Prompt Injection MVP Execution")
    print("=" * 60)

    print("\nLoading playbook...")
    playbook = load_playbook(PLAYBOOK_PATH)
    meta = playbook.get("playbook_metadata", {})
    print(f"  Playbook: {PLAYBOOK_PATH.name}")
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

    print("\nGenerating scorecard...")
    generate_scorecard(results, meta, OUTPUT_DIR)

    print("\nGenerating adversarial result...")
    generate_adversarial_result(results, OUTPUT_DIR)

    print(f"\n{'=' * 60}")
    print("Execution complete.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
