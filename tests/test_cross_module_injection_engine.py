"""
test_cross_module_injection_engine.py — Unit Tests for Cross-Module Injection Engine.
Path: tests/test_cross_module_injection_engine.py

Validates:
1. Engine initialization, safety invariants, and safety boundaries.
2. Playbook loading and catalog coverage across PATH-001 through PATH-008.
3. Scenario structure and schema validation for all 8 paths.
4. Step-by-step injection session lifecycle and state evolution.
5. Breakthrough detection and severity tier evaluation.
6. Exploit chain candidate and evidence trace generation.
7. Batch execution across all 8 paths.
8. Error handling and boundary edge cases.
"""

import pytest
from pathlib import Path
from engine.cross_module_injection_engine import (
    CrossModuleInjectionEngine,
    INJECTION_ENGINE_SAFETY_BOUNDARIES,
    LAYER_VULNERABILITY_FACTORS,
    EDGE_CONDUCTIVITY_WEIGHTS,
)


@pytest.fixture
def engine():
    return CrossModuleInjectionEngine()


# ============================================================================
# 1. Engine Initialization and Safety Invariants
# ============================================================================

def test_engine_initialization_and_safety_invariants(engine):
    """Verifies that all non-negotiable safety flags are strictly set and immutable."""
    assert engine.safety_boundaries["confirmed_vulnerability"] is False
    assert engine.safety_boundaries["formal_finding_allowed"] is False
    assert engine.safety_boundaries["production_safety_claimed"] is False
    assert engine.safety_boundaries["synthetic_only"] is True
    assert engine.safety_boundaries["requires_human_review"] is True
    assert engine.safety_boundaries["all_findings_are_candidate"] is True
    assert engine.safety_boundaries["red_team_engine_not_executable"] is True
    assert engine.safety_boundaries["evidence_mode"] == "synthetic_only"

    # Test safety config overrides cannot violate core invariants
    custom_engine = CrossModuleInjectionEngine(safety_config={
        "confirmed_vulnerability": True,
        "production_safety_claimed": True,
    })
    assert custom_engine.safety_boundaries["confirmed_vulnerability"] is False
    assert custom_engine.safety_boundaries["production_safety_claimed"] is False


# ============================================================================
# 2. Playbook Loading and Canonical Paths
# ============================================================================

def test_playbook_loading_and_canonical_paths(engine):
    """Verifies that all 8 scenario playbooks (PATH-001 to PATH-008) are loaded."""
    paths = engine.get_available_paths()
    assert len(paths) == 8
    expected_ids = [
        "PATH-001", "PATH-002", "PATH-003", "PATH-004",
        "PATH-005", "PATH-006", "PATH-007", "PATH-008"
    ]
    for eid in expected_ids:
        assert eid in paths
        scenario = engine.get_scenario(eid)
        assert scenario is not None
        assert scenario["path_id"] == eid


def test_scenario_lookup_aliases_and_case_insensitivity(engine):
    """Verifies scenario lookup by alias, case-insensitivity, and numeric identifier."""
    # Lookup by alias
    sc_alias = engine.get_scenario("PATH-SUPPLY-DEV-RAG-RUNTIME-001")
    assert sc_alias is not None
    assert sc_alias["path_id"] == "PATH-001"

    # Lookup by lower case
    sc_lower = engine.get_scenario("path-002")
    assert sc_lower is not None
    assert sc_lower["path_id"] == "PATH-002"

    # Lookup by number
    sc_num = engine.get_scenario("3")
    assert sc_num is not None
    assert sc_num["path_id"] == "PATH-003"


# ============================================================================
# 3. Schema Validation across all 8 paths
# ============================================================================

def test_all_8_paths_scenario_schema_validation(engine):
    """Validates schema conformance for all 8 paths."""
    for pid in engine.get_available_paths():
        scenario = engine.get_scenario(pid)
        is_valid, errors = engine.validate_scenario(scenario)
        assert is_valid is True, f"Validation failed for {pid}: {errors}"
        assert len(errors) == 0

        # Check steps completeness
        steps = scenario.get("steps", [])
        assert len(steps) >= 3, f"{pid} should have at least 3 steps"
        for step in steps:
            assert "step_number" in step
            assert "module_id" in step
            assert "layer" in step
            assert "boundary_crossed" in step
            assert "simulated_event" in step
            assert "expected_defense" in step


# ============================================================================
# 4. Step-by-Step Injection Session Lifecycle
# ============================================================================

def test_step_by_step_injection_session(engine):
    """Tests session creation and manual step injection on PATH-001."""
    session_id = engine.start_session("PATH-001")
    session = engine.get_session(session_id)
    assert session is not None
    assert session["path_id"] == "PATH-001"
    assert session["current_step_index"] == 0
    assert session["total_steps"] == 5

    # Step 1: M43
    res1 = engine.inject_step(session_id)
    assert res1["step_number"] == 1
    assert res1["module_id"] == "M43"
    assert res1["boundary_crossed"] == "tool_boundary"
    assert "descriptor_poisoning_detected" in res1["evidence_fields"]
    assert res1["synthetic_only"] is True
    assert res1["trace_id"].startswith("<SIM_TRACE_PATH-001_01_")

    # Step 2: M46
    res2 = engine.inject_step(session_id)
    assert res2["step_number"] == 2
    assert res2["module_id"] == "M46"

    # Step 3: M48
    res3 = engine.inject_step(session_id)
    assert res3["step_number"] == 3
    assert res3["module_id"] == "M48"

    # Step 4: M49
    res4 = engine.inject_step(session_id)
    assert res4["step_number"] == 4
    assert res4["module_id"] == "M49"

    # Step 5: M50
    res5 = engine.inject_step(session_id)
    assert res5["step_number"] == 5
    assert res5["module_id"] == "M50"
    assert session["status"] == "completed"
    assert len(session["step_results"]) == 5


# ============================================================================
# 5. Breakthrough Detection and Severity Tier Evaluation
# ============================================================================

def test_breakthrough_detection_on_simulated_defense_failure(engine):
    """Tests candidate breakthrough detection when defensive failure is simulated."""
    # Simulate PATH-003 where M48 and M49 fail defense
    simulated_outcomes = [
        {"defense_held": False, "evidence_fields": {"rag_poisoning_detected": False, "safe_summary_generated": False}},
        {"defense_held": False, "evidence_fields": {"permission_boundary_preserved": False, "restricted_retrieval_blocked": False}},
        {"defense_held": True, "evidence_fields": {"sandbox_boundary_preserved": True}},
    ]

    report = engine.execute_path("PATH-003", simulated_defense_outcomes=simulated_outcomes)
    assert report["status"] == "completed"
    assert report["breakthrough_detected"] is True
    assert report["severity_tier"] in ["candidate_high", "candidate_critical"]

    candidate = report["exploit_chain_candidate"]
    assert candidate["breakthrough_detected"] is True
    assert len(candidate["candidate_findings"]) > 0
    finding = candidate["candidate_findings"][0]
    assert finding["finding_status"] == "candidate"
    assert finding["confirmed_vulnerability"] is False
    assert finding["requires_human_review"] is True


def test_contained_path_simulation(engine):
    """Tests contained simulation where all defenses hold properly."""
    report = engine.execute_path("PATH-004")
    assert report["status"] == "completed"
    assert report["breakthrough_detected"] is False
    assert report["severity_tier"] == "candidate_contained"

    candidate = report["exploit_chain_candidate"]
    assert candidate["breakthrough_detected"] is False
    assert len(candidate["candidate_findings"]) == 0


# ============================================================================
# 6. Exploit Chain Candidate and Evidence Trace Structure
# ============================================================================

def test_exploit_chain_candidate_structure(engine):
    """Verifies exploit chain candidate schema conformance."""
    report = engine.execute_path("PATH-002")
    candidate = report["exploit_chain_candidate"]

    assert candidate["candidate_id"].startswith("<SIM_EXPLOIT_CHAIN_PATH-002_")
    assert candidate["path_id"] == "PATH-002"
    assert candidate["alias_id"] == "PATH-SUPPLY-A2A-DEP-RUNTIME-001"
    assert "compromised_user" in candidate["attacker_profile"]["attacker_type"]
    assert candidate["total_steps"] == 5
    assert candidate["steps_executed"] == 5
    assert len(candidate["boundary_crossings"]) == 5
    assert candidate["safety_metadata"]["confirmed_vulnerability"] is False
    assert candidate["safety_metadata"]["synthetic_only"] is True


def test_evidence_trace_consistency_and_synthetic_placeholders(engine):
    """Verifies that all generated evidence traces contain synthetic flags and placeholders."""
    report = engine.execute_path("PATH-005")
    traces = report["evidence_traces"]
    assert len(traces) == 4

    for tr in traces:
        assert tr["synthetic_only"] is True
        assert tr["trace_id"].startswith("<SIM_TRACE_PATH-005_")
        assert "evidence_fields" in tr
        assert isinstance(tr["evidence_fields"], dict)
        assert "propagation_pressure" in tr
        assert 0.0 <= tr["propagation_pressure"] <= 1.0
        assert "post_defense_state" in tr
        assert 0.0 <= tr["post_defense_state"] <= 1.0


# ============================================================================
# 7. Batch Execution Across All 8 Paths
# ============================================================================

def test_execute_all_paths_batch(engine):
    """Executes the full suite of 8 paths in batch mode."""
    batch_summary = engine.execute_all_paths()

    assert batch_summary["total_paths"] == 8
    assert len(batch_summary["paths_executed"]) == 8
    assert batch_summary["total_steps_executed"] >= 30
    assert batch_summary["total_evidence_traces_generated"] >= 30
    assert batch_summary["safety_boundaries"]["confirmed_vulnerability"] is False

    for pid in engine.get_available_paths():
        res = batch_summary["path_results"][pid]
        assert res["status"] == "completed"
        assert res["steps_executed"] == res["total_steps"]


# ============================================================================
# 8. Error Handling and Edge Cases
# ============================================================================

def test_unknown_path_id_raises_value_error(engine):
    """Verifies that unknown path IDs raise ValueError."""
    with pytest.raises(ValueError, match="Unknown scenario path_id"):
        engine.start_session("PATH-999")


def test_inject_on_completed_session_raises_runtime_error(engine):
    """Verifies that attempting to inject steps after session completion raises RuntimeError."""
    session_id = engine.start_session("PATH-003")
    engine.run_session_to_completion(session_id)

    with pytest.raises(RuntimeError, match="already completed"):
        engine.inject_step(session_id)


def test_out_of_range_step_index_raises_index_error(engine):
    """Verifies that specifying an invalid step index raises IndexError."""
    session_id = engine.start_session("PATH-003")
    with pytest.raises(IndexError):
        engine.inject_step(session_id, step_index=99)
