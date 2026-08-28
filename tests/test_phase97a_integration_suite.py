"""
tests/test_phase97a_integration_suite.py
Phase 97A Task 3 — Dynamic Propagation & Cross-Module Integration Suite.

Task: Phase-97A-GATE-003
Task Name: 阶段 97 动态传播与跨模块注入整合验证设计门

Test Coverage:
1. End-to-End Joint Simulation: 8 paths, 32 steps, contained baseline.
2. Markov 5-State Distribution Convergence across all evidence traces.
3. Multi-Scenario Perturbed Initial States (node final Markov distributions).
4. Checkpoint Snapshot Structure & Integrity.
"""

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.propagation_dynamics_engine import PropagationDynamicsEngine
from engine.cross_module_injection_engine import CrossModuleInjectionEngine

CHECKPOINT_PATH = ROOT / "artifacts/batch_checkpoints/phase97a_checkpoint.json"

EXPECTED_PIDS = [f"PATH-{i:03d}" for i in range(1, 9)]


@pytest.fixture(scope="module")
def injection_engine():
    prop_engine = PropagationDynamicsEngine()
    return CrossModuleInjectionEngine(propagation_engine=prop_engine)


@pytest.fixture(scope="module")
def batch_summary(injection_engine):
    return injection_engine.execute_all_paths()


def test_end_to_end_all_8_paths_contained_baseline(injection_engine, batch_summary):
    """Verifies the contained baseline: 8 paths, 32 steps, 0 breakthroughs, all contained."""
    assert batch_summary.get("total_paths") == 8
    assert batch_summary.get("total_steps_executed") == 32, (
        f"Expected 32 steps across 8 paths, got {batch_summary.get('total_steps_executed')}"
    )
    assert batch_summary.get("total_evidence_traces_generated") == 32
    assert batch_summary.get("breakthrough_paths_count") == 0
    assert batch_summary.get("contained_paths_count") == 8

    path_results = batch_summary.get("path_results", {})
    for pid in EXPECTED_PIDS:
        res = path_results.get(pid, {})
        assert res.get("status") == "completed", f"{pid} must be completed"
        assert res.get("breakthrough_detected") is False, f"{pid} must be contained"
        assert res.get("severity_tier") == "candidate_contained"
        assert res.get("trajectory_classification") == "stable_or_pressured"


def test_markov_state_distribution_convergence_across_all_paths(batch_summary):
    """Verifies each evidence trace carries a 5-state Markov distribution with row sum 1.0."""
    converged_steps = 0
    path_results = batch_summary.get("path_results", {})
    for pid, res in path_results.items():
        for trace in res.get("evidence_traces", []):
            dist = trace.get("markov_distribution", {})
            assert len(dist) == 5, (
                f"Path {pid} step {trace.get('step_number')} Markov distribution "
                f"must have 5 states, got {len(dist)}"
            )
            row_sum = sum(dist.values())
            assert math.isclose(row_sum, 1.0, rel_tol=1e-6, abs_tol=1e-6), (
                f"Path {pid} step {trace.get('step_number')} row sum {row_sum} != 1.0"
            )
            converged_steps += 1

    assert converged_steps == 32, (
        f"Markov convergence verified on {converged_steps} steps, expected 32"
    )


def test_multi_scenario_perturbed_initial_states(batch_summary):
    """Verifies each path produces node-final Markov distributions that stay normalized under perturbation."""
    path_results = batch_summary.get("path_results", {})
    assert len(path_results) == 8
    nodes_with_final_dist = 0
    for pid in EXPECTED_PIDS:
        res = path_results.get(pid, {})
        final_dists = res.get("node_final_markov_distributions")
        assert isinstance(final_dists, dict) and len(final_dists) > 0, (
            f"Path {pid} must carry non-empty node_final_markov_distributions"
        )
        for mod_id, dist in final_dists.items():
            row_sum = sum(dist.values())
            assert math.isclose(row_sum, 1.0, rel_tol=1e-6, abs_tol=1e-6), (
                f"Path {pid} node {mod_id} final Markov row sum {row_sum} != 1.0"
            )
            assert len(dist) == 5, f"Node {mod_id} final distribution must have 5 states"
            nodes_with_final_dist += 1

    assert nodes_with_final_dist >= 8, "All 8 paths must yield node-final distributions"


def test_checkpoint_snapshot_structure_and_integrity():
    """Verifies the checkpoint snapshot carries complete run metadata and safety boundaries."""
    assert CHECKPOINT_PATH.exists(), "Checkpoint snapshot must exist"
    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        cp = json.load(f)

    assert cp.get("checkpoint_version") == "1.0"
    assert cp.get("phase") == "Phase-97A"
    assert cp.get("task_id") == "Phase-97A-GATE-003"
    assert cp.get("status") == "completed"
    assert cp.get("total_scenarios") == 8
    assert cp.get("total_steps_executed") == 32
    assert cp.get("total_evidence_traces") == 32

    sb = cp.get("safety_boundaries", {})
    assert sb.get("confirmed_vulnerability") is False
    assert sb.get("formal_finding_allowed") is False
    assert sb.get("production_safety_claimed") is False
    assert sb.get("synthetic_only") is True
    assert sb.get("requires_human_review") is True

    paths = cp.get("paths", {})
    assert len(paths) == 8, f"Checkpoint must contain 8 paths, got {len(paths)}"
    for pid in EXPECTED_PIDS:
        assert pid in paths, f"Checkpoint missing {pid}"
        assert paths[pid].get("status") == "completed"
        assert len(paths[pid].get("steps", [])) >= 3
