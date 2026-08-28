"""
Unit Test Suite for Cross-Module Propagation Dynamics Engine.
Path: tests/test_propagation_dynamics_engine.py

Verifies:
1. Engine Safety Boundaries and Contract Integrity.
2. 4 Security Layers and 7 Edge Types structure and weights.
3. Attenuation (Decay) model and exponential graph decay.
4. Amplification model (Sequential, Cross-Layer, Feedback loops).
5. Markov 5-state transition matrix row-sum = 1.0 and dynamic adjustment.
6. Edge Propagation Pressure equation (P_edge) and boundary conditions.
7. Node Defense State Evolution equation (D_node) and clamping.
8. Path Degradation calculation (G_path) and trajectory mapping.
9. Full graph multi-step cross-module propagation simulation.
"""

import math
import pytest
from engine.propagation_dynamics_engine import (
    PropagationDynamicsEngine,
    ENGINE_SAFETY_BOUNDARIES,
    SECURITY_LAYERS,
    EDGE_TYPES,
    DEFAULT_EDGE_WEIGHTS,
    MARKOV_STATES,
    MARKOV_STATE_INDICES,
    DEFAULT_MARKOV_TRANSITION_MATRIX,
    ATTENUATION_RULES,
    MODULE_ATTENUATION_WEIGHTS,
    MODULE_DEFAULT_VULNERABILITY,
    BLOCKING_RULES,
    FEEDBACK_PRESETS,
    clamp,
    normalize_distribution,
)


@pytest.fixture
def engine():
    return PropagationDynamicsEngine()


# ============================================================================
# Test 1: Safety Boundaries Compliance
# ============================================================================

def test_engine_safety_boundaries(engine):
    """Test that safety boundary declarations are strictly defensive and non-executable."""
    sb = engine.get_safety_boundaries()
    assert sb["confirmed_vulnerability"] is False
    assert sb["formal_finding_allowed"] is False
    assert sb["production_safety_claimed"] is False
    assert sb["synthetic_only"] is True
    assert sb["red_team_engine_not_executable"] is True
    assert sb["propagation_equation_is_not_exploit_chain"] is True
    assert sb["theory_model_is_not_detection_rule"] is True


# ============================================================================
# Test 2: 4 Security Layers Introspection
# ============================================================================

def test_four_security_layers(engine):
    """Verify that all 4 security layers are correctly configured."""
    layers = engine.get_supported_layers()
    expected_layers = ["supply_chain", "development_environment", "rag_data", "runtime_sandbox"]

    assert set(layers.keys()) == set(expected_layers)
    assert layers["supply_chain"]["order"] == 1
    assert layers["development_environment"]["order"] == 2
    assert layers["rag_data"]["order"] == 3
    assert layers["runtime_sandbox"]["order"] == 4

    assert "M43" in layers["supply_chain"]["modules"]
    assert "M46" in layers["development_environment"]["modules"]
    assert "M47" in layers["development_environment"]["modules"]
    assert "M48" in layers["rag_data"]["modules"]
    assert "M49" in layers["rag_data"]["modules"]
    assert "M50" in layers["runtime_sandbox"]["modules"]


# ============================================================================
# Test 3: 7 Edge Types and Conductivity Weights
# ============================================================================

def test_seven_edge_types(engine):
    """Verify all 7 edge types and default conductivity weights."""
    edge_types = engine.get_supported_edge_types()
    expected_edge_types = [
        "context_influence",
        "trust_boundary_transfer",
        "permission_dependency",
        "evidence_dependency",
        "audit_dependency",
        "runtime_dependency",
        "tool_call_chain",
    ]

    assert len(edge_types) == 7
    assert set(edge_types.keys()) == set(expected_edge_types)

    assert edge_types["context_influence"]["weight"] == 0.60
    assert edge_types["trust_boundary_transfer"]["weight"] == 0.50
    assert edge_types["permission_dependency"]["weight"] == 0.80
    assert edge_types["evidence_dependency"]["weight"] == 0.30
    assert edge_types["audit_dependency"]["weight"] == 0.40
    assert edge_types["runtime_dependency"]["weight"] == 0.60
    assert edge_types["tool_call_chain"]["weight"] == 0.70


# ============================================================================
# Test 4: Markov 5-State Transition Matrix Row Sum Equals 1.0
# ============================================================================

def test_markov_matrix_row_sum_strictly_one(engine):
    """Verify that every row in the Markov transition matrix sums to exactly 1.0."""
    states = engine.get_markov_states()
    assert states == ["stable", "pressured", "degraded", "blocked", "failed"]

    for state in states:
        row = engine.markov_matrix[state]
        row_sum = sum(row.values())
        assert math.isclose(row_sum, 1.0, rel_tol=1e-6, abs_tol=1e-6), (
            f"Row sum for state '{state}' is {row_sum}, expected 1.0"
        )


def test_dynamic_markov_matrix_row_sum(engine):
    """Verify dynamic transition matrix calculation maintains strict row sum = 1.0 under diverse conditions."""
    test_conditions = [
        {"pressure_in": 0.0, "control_recovery": 0.0, "human_review": 0.0},
        {"pressure_in": 0.5, "control_recovery": 0.2, "human_review": 0.1},
        {"pressure_in": 1.0, "control_recovery": 0.0, "human_review": 0.0},
        {"pressure_in": 0.0, "control_recovery": 0.8, "human_review": 0.3},
        {"pressure_in": 0.75, "control_recovery": 0.4, "human_review": 0.2},
    ]

    for cond in test_conditions:
        dyn_matrix = engine.compute_dynamic_transition_matrix(**cond)
        for state in MARKOV_STATES:
            row_sum = sum(dyn_matrix[state].values())
            assert math.isclose(row_sum, 1.0, rel_tol=1e-6, abs_tol=1e-6), (
                f"Dynamic row sum for state '{state}' under {cond} is {row_sum}, expected 1.0"
            )


def test_markov_trajectory_simulation(engine):
    """Verify Markov trajectory multi-step state distribution progression."""
    traj = engine.simulate_markov_trajectory(
        initial_state="stable",
        steps=5,
        pressure_series=[0.2, 0.4, 0.6, 0.8, 1.0],
        recovery_series=[0.0, 0.1, 0.1, 0.2, 0.2],
    )
    assert len(traj) == 6  # initial + 5 steps
    for step_dist in traj:
        assert math.isclose(sum(step_dist.values()), 1.0, rel_tol=1e-6, abs_tol=1e-6)
        assert step_dist["stable"] >= 0.0
        assert step_dist["failed"] >= 0.0


# ============================================================================
# Test 5: Decay (Attenuation) Model
# ============================================================================

def test_decay_attenuation_calculations(engine):
    """Verify decay rule aggregation and distance-based signal attenuation."""
    # 1. Rule sum test
    hrg_atten = engine.compute_attenuation(active_rules=["ATTEN-HRG-001"])
    assert math.isclose(hrg_atten, 0.30)

    m50_atten = engine.compute_attenuation(module_id="M50")
    assert math.isclose(m50_atten, 1.50)

    # 2. Distance decay test
    sig_h0 = engine.compute_signal_decay(initial_signal=1.0, hops=0)
    assert math.isclose(sig_h0, 1.0)

    sig_h1 = engine.compute_signal_decay(initial_signal=1.0, hops=1, decay_rate=0.15)
    sig_h3 = engine.compute_signal_decay(initial_signal=1.0, hops=3, decay_rate=0.15)
    assert sig_h1 > sig_h3, "Signal should attenuate with greater distance (hops)"


# ============================================================================
# Test 6: Amplification Model
# ============================================================================

def test_amplification_calculations(engine):
    """Verify sequential weak boundary, cross-layer, and feedback amplification."""
    # 1. Sequential amplification
    assert engine.compute_sequential_amplification(0) == pytest.approx(0.00)
    assert engine.compute_sequential_amplification(1) == pytest.approx(0.10)
    assert engine.compute_sequential_amplification(2) == pytest.approx(0.25)
    assert engine.compute_sequential_amplification(3) == pytest.approx(0.50)
    assert engine.compute_sequential_amplification(5) == pytest.approx(0.50)

    # 2. Cross-layer amplification
    assert engine.compute_cross_layer_amplification("supply_chain", "supply_chain") == pytest.approx(0.00)
    assert engine.compute_cross_layer_amplification("supply_chain", "development_environment") == pytest.approx(0.20)
    assert engine.compute_cross_layer_amplification("supply_chain", "runtime_sandbox") == pytest.approx(0.60)

    # 3. Feedback loop factors
    assert engine.resolve_feedback_factor("runtime_control_active") == -0.20
    assert engine.resolve_feedback_factor("permission_leakage_triggered") == 0.30
    assert engine.resolve_feedback_factor(0.15) == 0.15


# ============================================================================
# Test 7: Edge Propagation Pressure Equation (P_edge)
# ============================================================================

def test_calculate_p_edge_core_and_boundaries(engine):
    """Verify P_edge calculation and boundary conditions."""
    # Boundary 1: Source signal = 0 -> P_edge = 0
    p0 = engine.calculate_p_edge(source_signal=0.0, edge_type="context_influence", target_defense=0.5)
    assert p0 == 0.0

    # Boundary 2: Target defense = 1.0 -> P_edge = 0 (1 - 1.0 = 0)
    p_solid = engine.calculate_p_edge(source_signal=1.0, edge_type="context_influence", target_defense=1.0)
    assert p_solid == 0.0

    # Boundary 3: Pattern factor = 0 -> P_edge = 0
    p_nopatt = engine.calculate_p_edge(source_signal=1.0, edge_type="context_influence", target_defense=0.5, pattern_factor=0.0)
    assert p_nopatt == 0.0

    # Example 1: M48 -> M49 (permission_dependency) at t=2
    # S_source=0.5, W_edge=0.8, A_pattern=1.2, F_feedback=0.0, D_target=0.7 (target openness=0.3)
    # Expected: 0.5 * 0.8 * 1.2 * 1.0 * 0.3 = 0.144
    p_calc = engine.calculate_p_edge(
        source_signal=0.5,
        edge_type="permission_dependency",
        target_defense=0.7,
        pattern_factor=1.2,
        feedback=0.0,
    )
    assert math.isclose(p_calc, 0.144, rel_tol=1e-4)


# ============================================================================
# Test 8: Node Defense State Evolution Equation (D_node)
# ============================================================================

def test_node_defense_evolution(engine):
    """Verify node defense state step computation and boundary clamping."""
    # Example: D_curr=0.7, P_in=0.3, V_node=0.7, R_ctrl=0.0, H_rev=0.0
    # Expected: clamp(0.7 - 0.3 * 0.7) = 0.7 - 0.21 = 0.49
    d_next = engine.step_node_defense(
        current_defense=0.7,
        incoming_pressure=0.3,
        node_vulnerability=0.7,
        control_recovery=0.0,
        human_review=0.0,
    )
    assert math.isclose(d_next, 0.49, rel_tol=1e-4)
    assert engine.map_defense_to_state(d_next) == "degraded"

    # Clamping upper bound: D_curr=0.9, R_ctrl=0.3 -> clamp(1.2) = 1.0
    d_clamped_high = engine.step_node_defense(
        current_defense=0.9,
        incoming_pressure=0.0,
        control_recovery=0.3,
    )
    assert d_clamped_high == 1.0
    assert engine.map_defense_to_state(d_clamped_high) == "stable"

    # Clamping lower bound: D_curr=0.1, P_in=1.0, V=0.9 -> clamp(0.1 - 0.9) = 0.0
    d_clamped_low = engine.step_node_defense(
        current_defense=0.1,
        incoming_pressure=1.0,
        node_vulnerability=0.9,
    )
    assert d_clamped_low == 0.0
    assert engine.map_defense_to_state(d_clamped_low) == "failed"


# ============================================================================
# Test 9: Path Degradation Assessment (G_path)
# ============================================================================

def test_path_degradation_and_trajectory(engine):
    """Verify path-level degradation equation and trajectory classifications."""
    # Test case: PATH-DEV-CRED-RUNTIME-001 benchmark
    # sum(P_edge) = 0.2, A_seq = 0.1, sum(A_atten) = 2.7, sum(A_ampl) = 0.2, sum(B_block) = 1.4
    # G_path = 0.2 * (1 + 0.1) - 2.7 + 0.2 - 1.4 = 0.22 - 2.7 + 0.2 - 1.4 = -3.68
    g_path = engine.calculate_g_path(
        edge_pressures=[0.1, 0.1],
        sequential_amplification=0.10,
        active_attenuation_rules=["ATTEN-HRG-001", "ATTEN-BND-001", "ATTEN-RED-001", "ATTEN-AUD-001", "ATTEN-RPL-001", "ATTEN-HRG-001", "ATTEN-HRG-001", "ATTEN-BND-001"], # total = 2.7
        active_amplification_rules=[0.20],
        active_blocking_rules=["BLOCK-CMD-001", "BLOCK-SB-001", "BLOCK-RPL-001"], # 0.4 + 0.5 + 0.5 = 1.4
    )
    assert math.isclose(g_path, -3.68, rel_tol=1e-3)
    assert engine.map_g_path_to_trajectory(g_path) == "stable_or_pressured"

    # Trajectory mappings
    assert engine.map_g_path_to_trajectory(-1.0) == "stable_or_pressured"
    assert engine.map_g_path_to_trajectory(0.2) == "partial_pressure"
    assert engine.map_g_path_to_trajectory(0.7) == "partial_degradation"
    assert engine.map_g_path_to_trajectory(1.5) == "significant_degradation"
    assert engine.map_g_path_to_trajectory(2.5) == "critical_degradation"


# ============================================================================
# Test 10: Full Cross-Module Graph Simulation
# ============================================================================

def test_full_cross_module_propagation_simulation(engine):
    """Verify end-to-end multi-step graph simulation across all 4 layers."""
    nodes = [
        {"id": "M43", "layer": "supply_chain", "initial_defense": 0.8},
        {"id": "M46", "layer": "development_environment", "initial_defense": 0.9},
        {"id": "M48", "layer": "rag_data", "initial_defense": 0.95},
        {"id": "M50", "layer": "runtime_sandbox", "initial_defense": 1.0},
    ]

    edges = [
        {"from": "M43", "to": "M46", "type": "context_influence", "pattern_factor": 1.1},
        {"from": "M46", "to": "M48", "type": "context_influence", "pattern_factor": 1.0},
        {"from": "M48", "to": "M50", "type": "runtime_dependency", "feedback": "runtime_control_active", "recovery": 0.3},
    ]

    entry_signals = {"M43": 0.6}

    result = engine.simulate_cross_module_propagation(
        nodes=nodes,
        edges=edges,
        time_steps=4,
        entry_signals=entry_signals,
    )

    assert result["simulation_id"] == "<SIM_PROPAGATION_RUN_001>"
    assert result["total_steps"] == 4
    assert result["total_nodes"] == 4
    assert result["total_edges"] == 3
    assert "final_node_states" in result
    assert "M50" in result["final_node_states"]
    assert len(result["simulation_history"]) == 4

    sb = result["safety_boundaries"]
    assert sb["confirmed_vulnerability"] is False
    assert sb["synthetic_only"] is True
