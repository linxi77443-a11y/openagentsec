#!/usr/bin/env python3
"""Phase 62G — Role Boundary Bypass MVP Execution Script.

Simulates adversarial_validation evaluation for RBB playbook entries.
No real API calls. SIM_ placeholder data only.
Focus: fake role declarations, manager authorization claims, emergency override,
temporary proxy, test environment claims, audit bypass.
"""
import json, sys, yaml
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_PATH = ROOT / "adversarial_playbooks/role_boundary_bypass_mvp/playbook.yaml"
OUTPUT_DIR = ROOT / "executions/phase62g_rbb_mvp"

# Entry IDs where defense fails (breakthrough on evaluation)
SIMULATE_BREAKTHROUGH_IDS = {"RBB-005", "RBB-008"}


def load_playbook(path):
    with open(path) as f:
        return yaml.safe_load(f)


def simulate_defense(entry):
    """Simulate single-turn defense evaluation for RBB entries.

    For most entries, defense detects the fake role/authorization claim and refuses.
    For breakthrough entries, defense fails to identify the boundary bypass attempt
    due to plausible context (emergency pressure, audit authority).
    """
    eid = entry["entry_id"]
    is_control = entry.get("control_case", False)
    expected = entry.get("expected_behavior", "refuse")

    if is_control:
        return {
            "defensive_action": "normal_response",
            "breakthrough_detected": False,
            "requires_human_review": False,
            "signal_detected": None,
            "defensive_check_passed": True,
            "erosion_detected": False,
            "evidence_trace": [],
            "exploit_chain_candidate": [],
            "evaluation_summary": "control_case — no adversarial signal detected",
        }

    is_breakthrough = eid in SIMULATE_BREAKTHROUGH_IDS

    if is_breakthrough:
        return {
            "defensive_action": "partial_bypass",
            "breakthrough_detected": True,
            "requires_human_review": True,
            "signal_detected": "role_bypass_breakthrough",
            "defensive_check_passed": False,
            "erosion_detected": True,
            "evidence_trace": [
                {"timestamp": datetime.now(timezone.utc).isoformat(), "source": "user_prompt", "content": entry.get("prompt", "")[:80], "signal_type": "role_bypass"},
            ],
            "exploit_chain_candidate": [
                {"step": 1, "observation": "User claimed elevated role/authority with plausible context (emergency, audit)", "signal": "role_fabrication"},
                {"step": 2, "observation": "Defense accepted the role claim without independent verification", "signal": "role_verification_gap"},
            ],
            "evaluation_summary": f"breakthrough — defense failed to detect role boundary bypass (expected: {expected}, actual: partial_bypass)",
        }

    # Standard defense: holds, detects role boundary bypass
    return {
        "defensive_action": expected,
        "breakthrough_detected": False,
        "requires_human_review": False,
        "signal_detected": entry.get("expected_signal", "role_bypass_refusal"),
        "defensive_check_passed": True,
        "erosion_detected": False,
        "evidence_trace": [],
        "exploit_chain_candidate": [],
        "evaluation_summary": f"blocked — role boundary bypass detected and refused (defensive action: {expected})",
    }


def execute_playbook(playbook):
    entries = playbook.get("entries", [])
    meta = playbook.get("playbook_metadata", {})

    results = []
    for entry in entries:
        result = {
            "entry_id": entry["entry_id"],
            "adversarial_playbook_type": meta.get("adversarial_playbook_type", "role_boundary_bypass"),
            "category": entry.get("category", ""),
            "scenario": entry.get("scenario", ""),
            "control_case": entry.get("control_case", False),
            "expected_behavior": entry.get("expected_behavior", ""),
            "expected_signal": entry.get("expected_signal", ""),
            "multi_turn": False,
            "turn_count": 1,
            "prompt": entry.get("prompt", ""),
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
    breakthrough = sum(1 for r in results if r["breakthrough_detected"])
    blocked = sum(1 for r in results if not r["breakthrough_detected"] and not r["control_case"])
    control_ok = sum(1 for r in results if r["control_case"] and not r["breakthrough_detected"])
    human_review = sum(1 for r in results if r["requires_human_review"])
    inconclusive = sum(1 for r in results if r.get("defensive_action") == "inconclusive")
    erosion = sum(1 for r in results if r.get("erosion_detected"))

    behavior_counts = {}
    for r in results:
        b = r.get("defensive_action", "unknown")
        behavior_counts[b] = behavior_counts.get(b, 0) + 1

    scorecard = {
        "scorecard_metadata": {
            "phase": "phase62g",
            "run_id": "phase62g-rbb-mvp",
            "assessment_mode": "adversarial_validation",
            "adversarial_playbook_type": "role_boundary_bypass",
            "actor": meta.get("actor", "simulated_adversary"),
            "attacker_profile": meta.get("attacker_profile", "authenticated_low_privilege"),
            "attacker_type": meta.get("attacker_type", "low_privileged_operator"),
            "attack_objective": meta.get("attack_objective", "role_escalation"),
            "target": "SIM_ simulated defense (no real API)",
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "total_entries": total,
            "multi_turn_entries": 0,
            "erosion_detected": erosion,
            "breakthrough_ids": sorted([r["entry_id"] for r in results if r.get("breakthrough_detected")]),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "results_summary": {
            "total": total,
            "breakthrough_detected": breakthrough,
            "blocked": blocked,
            "control_passed": control_ok,
            "inconclusive": inconclusive,
            "human_review_required": human_review,
            "erosion_detected": erosion,
            "defensive_behavior_distribution": behavior_counts,
        },
        "category_coverage": list(dict.fromkeys(r["category"] for r in results if not r["control_case"])),
    }

    path = output_dir / "capability_scorecard.yaml"
    with open(path, "w") as f:
        yaml.dump(scorecard, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"  [OK] {path}")


def generate_adversarial_result(results, output_dir):
    entries_out = []
    for r in results:
        entry = {
            "entry_id": r["entry_id"],
            "category": r["category"],
            "scenario": r["scenario"],
            "control_case": r["control_case"],
            "multi_turn": r.get("multi_turn", False),
            "turn_count": r.get("turn_count", 1),
            "expected_behavior": r["expected_behavior"],
            "defensive_action": r["defensive_action"],
            "breakthrough_detected": r["breakthrough_detected"],
            "requires_human_review": r["requires_human_review"],
            "signal_detected": r["signal_detected"],
            "erosion_detected": r.get("erosion_detected", False),
            "defensive_check_passed": r["defensive_check_passed"],
            "evaluation_summary": r["evaluation_summary"],
        }
        entries_out.append(entry)

    result_yaml = {
        "adversarial_result_metadata": {
            "run_id": "phase62g-rbb-mvp",
            "assessment_mode": "adversarial_validation",
            "adversarial_playbook_type": "role_boundary_bypass",
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
    print("Phase 62G — Role Boundary Bypass MVP Execution")
    print("=" * 60)

    print("\nLoading playbook...")
    playbook = load_playbook(PLAYBOOK_PATH)
    meta = playbook.get("playbook_metadata", {})
    print(f"  Playbook: {PLAYBOOK_PATH.name}")
    print(f"  Type: {meta.get('adversarial_playbook_type', 'N/A')}")
    print(f"  Entries: {len(playbook.get('entries', []))}")

    print("\nSimulating defense evaluation...")
    results = execute_playbook(playbook)
    print(f"  Entries evaluated: {len(results)}")
    print(f"  Breakthrough detected: {sum(1 for r in results if r['breakthrough_detected'])}")
    print(f"  Erosion detected: {sum(1 for r in results if r.get('erosion_detected'))}")
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
