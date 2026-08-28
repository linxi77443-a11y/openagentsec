#!/usr/bin/env python3
"""
Phase 1 — Mock Fixture Generator for Full Corpus Modules
Generates per-module mock_fixtures.yaml with:
  - attack_chains (from playbook entries)
  - safety_boundary_assertions
  - state_machine_transitions
All data is synthetic. No real systems or credentials.
"""
import yaml, json, os, sys
from datetime import datetime

BASE = "/Users/linxi/Desktop/ai-workspace/AI学习/AI安全评估探索/adversarial_playbooks"

def get_entries(pb):
    if 'entries' in pb:
        return pb['entries']
    for key in pb:
        if isinstance(pb[key], list) and len(pb[key]) > 0 and isinstance(pb[key][0], dict):
            return pb[key]
    return []

def get_entry_id(e):
    return e.get('entry_id', e.get('case_id', e.get('corpus_id', '')))

def get_prompt(e):
    return e.get('prompt', e.get('prompt_text', e.get('user_goal', '')))

def is_control(e):
    cat = e.get('category', '')
    poc = e.get('positive_or_control', '')
    return cat == 'control' or poc == 'control'

def generate_fixture(mod_name, playbook_path):
    """Generate mock fixture for a single module."""
    with open(playbook_path) as f:
        pb = yaml.safe_load(f)
    
    entries = get_entries(pb)
    attacks = [e for e in entries if not is_control(e)]
    controls = [e for e in entries if is_control(e)]
    
    # Get categories
    categories = {}
    for e in attacks:
        cat = e.get('category', 'unknown')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(e)
    
    mod_upper = mod_name.upper()
    
    # ── 1. Generate attack chains ──
    attack_chains = []
    chain_idx = 0
    for cat, cat_entries in categories.items():
        # Pick up to 5 representative entries per category for chains
        sample = cat_entries[:5]
        for entry in sample:
            chain_idx += 1
            eid = get_entry_id(entry)
            prompt = get_prompt(entry)
            
            chain = {
                "chain_id": f"<SIM_{mod_upper}_CHAIN_{chain_idx:03d}>",
                "chain_name": f"{mod_upper} {cat} - {entry.get('subcategory', 'unknown')}",
                "attacker_type": "synthetic_adversary",
                "attack_objective": cat,
                "source_entry_id": eid,
                "lifecycle": [
                    {
                        "stage": "chain_created",
                        "timestamp": f"<SIM_TS_{mod_upper}_{chain_idx:03d}_01>",
                        "trigger": entry.get('scenario', f'Synthetic {cat} attack'),
                        "entry_id": eid,
                        "module_id": mod_upper,
                        "initial_state": "idle"
                    },
                    {
                        "stage": "entry_selected",
                        "timestamp": f"<SIM_TS_{mod_upper}_{chain_idx:03d}_02>",
                        "corpus_entry": eid,
                        "attack_vector": entry.get('subcategory', entry.get('technique_tag', cat))
                    },
                    {
                        "stage": "path_generated",
                        "timestamp": f"<SIM_TS_{mod_upper}_{chain_idx:03d}_03>",
                        "attack_path": [
                            {"node": f"initial_{cat}_attempt"},
                            {"node": f"boundary_probe_{entry.get('subcategory', 'unknown')}"},
                            {"node": f"defense_pressure_{cat}"},
                            {"node": f"final_{entry.get('expected_behavior', 'blocked')}"}
                        ]
                    },
                    {
                        "stage": "defense_pressured",
                        "timestamp": f"<SIM_TS_{mod_upper}_{chain_idx:03d}_04>",
                        "defense_state_before": "stable",
                        "defense_state_after": "pressured",
                        "pressed_boundary": f"{cat}_boundary",
                        "signal_generated": entry.get('expected_signal', f'{cat}_detected')
                    },
                    {
                        "stage": "runtime_blocked",
                        "timestamp": f"<SIM_TS_{mod_upper}_{chain_idx:03d}_05>",
                        "blocking_mechanism": f"{cat}_defense_policy",
                        "blocked_boundary": f"{cat}_boundary",
                        "defensive_action": entry.get('expected_behavior', 'refuse')
                    },
                    {
                        "stage": "chain_terminated",
                        "timestamp": f"<SIM_TS_{mod_upper}_{chain_idx:03d}_06>",
                        "final_state": "blocked",
                        "breakthrough_detected": False,
                        "confirmed_vulnerability": False
                    }
                ]
            }
            attack_chains.append(chain)
    
    # ── 2. Generate safety boundary assertions ──
    safety_assertions = []
    for idx, entry in enumerate(attacks[:20], 1):  # Top 20 attack entries
        eid = get_entry_id(entry)
        cat = entry.get('category', 'unknown')
        
        assertion = {
            "assertion_id": f"<SIM_{mod_upper}_SBA_{idx:03d}>",
            "boundary_type": f"{cat}_boundary",
            "description": entry.get('scenario', f'Synthetic {cat} safety check'),
            "mock_chain_id": f"<SIM_{mod_upper}_CHAIN_{min(idx, len(attack_chains)):03d}>",
            "mock_node_id": f"<SIM_{mod_upper}_NODE_{idx:03d}>",
            "expected_behavior": str(entry.get('expected_behavior', 'refuse')),
            "observed_outcome": f"synthetic_{cat}_blocked",
            "signal_generated": entry.get('expected_signal', f'{cat}_detected'),
            "boundary_preserved": True,
            "breakthrough_detected": False,
            "confirmed_vulnerability": False,
            "synthetic_input": f"<SIM_{mod_upper}_INPUT_{idx:03d}>"
        }
        safety_assertions.append(assertion)
    
    # ── 3. Generate state machine transitions ──
    transitions = []
    states = ["idle", "entry_selected", "path_generated", "defense_pressured", "blocked", "terminated"]
    for idx in range(min(len(attacks), 15)):
        entry = attacks[idx]
        cat = entry.get('category', 'unknown')
        eid = get_entry_id(entry)
        
        for s_idx in range(len(states) - 1):
            trans = {
                "transition_id": f"<SIM_{mod_upper}_TR_{idx:03d}_{s_idx:02d}>",
                "source_entry_id": eid,
                "module_id": mod_upper,
                "from_state": states[s_idx],
                "to_state": states[s_idx + 1],
                "trigger_type": f"{cat}_{states[s_idx]}_to_{states[s_idx+1]}",
                "trigger_description": f"Synthetic {cat} attack progresses from {states[s_idx]} to {states[s_idx+1]}",
                "boundary_affected": f"{cat}_boundary",
                "signal_generated": entry.get('expected_signal', f'{cat}_detected'),
                "defense_response": entry.get('expected_behavior', 'refuse'),
                "breakthrough_detected": False,
                "synthetic_only": True
            }
            transitions.append(trans)
    
    # ── Assemble fixture ──
    fixture = {
        "fixture_metadata": {
            "module_id": mod_upper,
            "phase": "full_corpus_fixture",
            "assessment_mode": "adversarial_validation",
            "synthetic_only": True,
            "no_code_implementation": True,
            "no_attack_execution": True,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "requires_human_review": True,
            "total_entries": len(entries),
            "attack_entries": len(attacks),
            "control_entries": len(controls),
            "categories": list(categories.keys()),
            "generated_at": datetime.now().isoformat()
        },
        "attack_chains": attack_chains,
        "safety_boundary_assertions": safety_assertions,
        "state_machine_transitions": transitions,
        "control_baseline": [
            {
                "control_id": f"<SIM_{mod_upper}_CTL_{idx:03d}>",
                "source_entry_id": get_entry_id(e),
                "category": e.get('category', 'control'),
                "expected_behavior": "normal_operation",
                "observed_outcome": "control_baseline_normal",
                "false_positive": False
            }
            for idx, e in enumerate(controls[:10], 1)
        ]
    }
    
    return fixture


def main():
    modules = sys.argv[1:] if len(sys.argv) > 1 else [
        'm01', 'm02', 'm04', 'm07', 'm12', 'm24', 'm25', 'm35'
    ]
    
    for mod in modules:
        mod_dir = os.path.join(BASE, f"{mod}_full_corpus")
        pb_path = os.path.join(mod_dir, "playbook.yaml")
        
        if not os.path.exists(pb_path):
            print(f"  {mod}: SKIP (no playbook)")
            continue
        
        try:
            fixture = generate_fixture(mod, pb_path)
        except Exception as e:
            print(f"  {mod}: ERROR - {e}")
            continue
        
        # Write fixture
        fixture_path = os.path.join(mod_dir, "mock_fixtures.yaml")
        with open(fixture_path, "w") as f:
            yaml.dump(fixture, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        meta = fixture["fixture_metadata"]
        chains = len(fixture["attack_chains"])
        assertions = len(fixture["safety_boundary_assertions"])
        transitions = len(fixture["state_machine_transitions"])
        
        print(f"  {mod}: {meta['total_entries']} entries → {chains} chains, {assertions} assertions, {transitions} transitions ✓")
    
    print(f"\nDone! Generated fixtures for {len(modules)} modules.")


if __name__ == "__main__":
    main()
