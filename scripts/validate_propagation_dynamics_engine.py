#!/usr/bin/env python3
"""
Standalone Validation Script for Cross-Module Propagation Dynamics Engine.
Path: scripts/validate_propagation_dynamics_engine.py

Validates:
1. Engine Architecture & Package Exports.
2. 4 Security Layers & Module Mapping.
3. 7 Edge Types & Conductivity Weights.
4. Decay / Attenuation Models.
5. Amplification Models (Sequential, Cross-Layer, Feedback).
6. Markov 5-State Transition Matrix Row Sum = 1.0 (Static & Dynamic).
7. Edge Propagation Pressure Equation (P_edge) Calculations & Boundary Conditions.
8. Node Defense Evolution Equation (D_node) & Clamping.
9. Path-Level Defense Degradation (G_path) & Trajectory Classifications.
10. Multi-Step Full Graph Propagation Simulation Pipeline.
11. Complete Compliance with Safety Boundaries (confirmed_vulnerability=False, synthetic_only=True, etc.).

Usage:
    python3 scripts/validate_propagation_dynamics_engine.py
"""

import sys
import math
import logging
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

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

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("PropagationDynamicsValidator")


def validate_propagation_dynamics_engine() -> bool:
    logger.info("======================================================================")
    logger.info("Phase 97A — Cross-Module Propagation Dynamics Engine Validator")
    logger.info("Task: Phase-97A-PROPAGATION-001")
    logger.info("======================================================================")

    passed_checks = 0
    total_checks = 0

    # ------------------------------------------------------------------
    # Step 1: Validate Engine Instantiation & Packaging
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 1] Validating Engine Instantiation & Module Structure...")
    engine = PropagationDynamicsEngine()
    assert isinstance(engine, PropagationDynamicsEngine), "Engine instance creation failed"
    passed_checks += 1
    logger.info("  ✓ Engine initialized successfully.")

    # ------------------------------------------------------------------
    # Step 2: Validate 4 Security Layers
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 2] Validating 4 Security Layers Specification...")
    layers = engine.get_supported_layers()
    assert len(layers) == 4, f"Expected 4 security layers, found {len(layers)}"
    assert "supply_chain" in layers and layers["supply_chain"]["order"] == 1
    assert "development_environment" in layers and layers["development_environment"]["order"] == 2
    assert "rag_data" in layers and layers["rag_data"]["order"] == 3
    assert "runtime_sandbox" in layers and layers["runtime_sandbox"]["order"] == 4
    
    # Check module mapping completeness
    all_assigned_modules = []
    for l_data in layers.values():
        all_assigned_modules.extend(l_data["modules"])
    for m in ["M43", "M46", "M47", "M48", "M49", "M50"]:
        assert m in all_assigned_modules, f"Module {m} missing from layers mapping"
    passed_checks += 1
    logger.info("  ✓ 4 Security Layers topology and module mappings verified.")

    # ------------------------------------------------------------------
    # Step 3: Validate 7 Edge Types & Conductivity Weights
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 3] Validating 7 Edge Types & Conductivity Weights...")
    edge_types = engine.get_supported_edge_types()
    assert len(edge_types) == 7, f"Expected 7 edge types, got {len(edge_types)}"
    expected_types = [
        "context_influence",
        "trust_boundary_transfer",
        "permission_dependency",
        "evidence_dependency",
        "audit_dependency",
        "runtime_dependency",
        "tool_call_chain",
    ]
    for et in expected_types:
        assert et in edge_types, f"Edge type {et} missing"
        w = edge_types[et]["weight"]
        assert 0.0 <= w <= 1.0, f"Edge weight {w} out of range [0, 1]"
    passed_checks += 1
    logger.info("  ✓ 7 Edge types and conductivity weights verified.")

    # ------------------------------------------------------------------
    # Step 4: Validate Attenuation / Decay Model
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 4] Validating Attenuation / Decay Model...")
    atten_rules = ["ATTEN-HRG-001", "ATTEN-BND-001", "ATTEN-RED-001", "ATTEN-AUD-001", "ATTEN-RPL-001"]
    for ar in atten_rules:
        assert ar in ATTENUATION_RULES, f"Missing attenuation rule {ar}"
    
    # Distance decay
    sig0 = 0.90
    sig1 = engine.compute_signal_decay(initial_signal=sig0, hops=1, decay_rate=0.15)
    sig2 = engine.compute_signal_decay(initial_signal=sig0, hops=2, decay_rate=0.15)
    assert sig0 > sig1 > sig2, "Decay model must strictly attenuate signals over hops"
    passed_checks += 1
    logger.info("  ✓ Attenuation / Decay model equations verified.")

    # ------------------------------------------------------------------
    # Step 5: Validate Amplification Model
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 5] Validating Amplification Model...")
    # Sequential amplification
    assert engine.compute_sequential_amplification(0) == 0.00
    assert engine.compute_sequential_amplification(1) == 0.10
    assert engine.compute_sequential_amplification(2) == 0.25
    assert engine.compute_sequential_amplification(3) == 0.50

    # Cross-layer amplification
    assert math.isclose(engine.compute_cross_layer_amplification("supply_chain", "runtime_sandbox"), 0.60)
    assert math.isclose(engine.compute_cross_layer_amplification("development_environment", "rag_data"), 0.20)

    # Feedback loop presets
    assert engine.resolve_feedback_factor("runtime_control_active") == -0.20
    assert engine.resolve_feedback_factor("permission_leakage_triggered") == 0.30
    passed_checks += 1
    logger.info("  ✓ Amplification model equations verified.")

    # ------------------------------------------------------------------
    # Step 6: Validate Markov 5-State Transition Matrix Row Sums = 1.0
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 6] Validating Markov 5-State Transition Matrix Row Sums = 1.0...")
    states = engine.get_markov_states()
    assert len(states) == 5, f"Expected 5 Markov states, got {len(states)}"
    
    # Static matrix
    engine.validate_markov_matrix()

    # Dynamic matrix tests across 10 varied parameter sets
    test_params = [
        (0.0, 0.0, 0.0), (0.1, 0.1, 0.0), (0.3, 0.2, 0.1), (0.5, 0.3, 0.2),
        (0.7, 0.0, 0.0), (0.9, 0.4, 0.3), (1.0, 0.0, 0.0), (0.0, 1.0, 0.5),
        (0.8, 0.8, 0.4), (0.4, 0.5, 0.2),
    ]
    for p, r, h in test_params:
        dyn_mat = engine.compute_dynamic_transition_matrix(pressure_in=p, control_recovery=r, human_review=h)
        for s in states:
            row_sum = sum(dyn_mat[s].values())
            assert math.isclose(row_sum, 1.0, rel_tol=1e-6, abs_tol=1e-6), (
                f"Dynamic row sum for state '{s}' under p={p}, r={r}, h={h} was {row_sum}"
            )

    passed_checks += 1
    logger.info("  ✓ Markov transition matrix row sum = 1.0 strictly verified across all scenarios.")

    # ------------------------------------------------------------------
    # Step 7: Validate Edge Propagation Pressure Equation (P_edge)
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 7] Validating Edge Propagation Pressure Equation (P_edge)...")
    # P_edge = S_source * W_edge * A_pattern * (1 + F_feedback) * (1 - D_target)
    # Case: M48 -> M49 (permission_dependency, W=0.8), S=0.5, A=1.2, F=0.0, D_target=0.7 (openness=0.3)
    p_edge = engine.calculate_p_edge(
        source_signal=0.5,
        edge_type="permission_dependency",
        target_defense=0.7,
        pattern_factor=1.2,
        feedback=0.0,
    )
    expected_p = 0.5 * 0.8 * 1.2 * 1.0 * 0.3 # 0.144
    assert math.isclose(p_edge, expected_p, rel_tol=1e-4), f"Expected P_edge {expected_p}, got {p_edge}"

    # Boundary tests
    assert engine.calculate_p_edge(0.0, "context_influence", 0.5) == 0.0
    assert engine.calculate_p_edge(1.0, "context_influence", 1.0) == 0.0
    passed_checks += 1
    logger.info(f"  ✓ Edge Propagation Pressure Equation (P_edge) verified (benchmark={p_edge:.4f}).")

    # ------------------------------------------------------------------
    # Step 8: Validate Node Defense Evolution Equation (D_node)
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 8] Validating Node Defense Evolution Equation (D_node)...")
    # D_node(t+1) = clamp(D_node(t) + R_control - P_in * V_node + H_review, 0.0, 1.0)
    d_step = engine.step_node_defense(
        current_defense=0.7,
        incoming_pressure=0.3,
        node_vulnerability=0.7,
        control_recovery=0.0,
        human_review=0.0,
    )
    assert math.isclose(d_step, 0.49, rel_tol=1e-4), f"Expected 0.49, got {d_step}"
    assert engine.map_defense_to_state(d_step) == "degraded"
    passed_checks += 1
    logger.info(f"  ✓ Node Defense Evolution Equation (D_node) verified (D_t+1={d_step:.4f}).")

    # ------------------------------------------------------------------
    # Step 9: Validate Path Degradation (G_path) & Trajectory
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 9] Validating Path Degradation (G_path) & Trajectory...")
    g_val = engine.calculate_g_path(
        edge_pressures=[0.1, 0.1],
        sequential_amplification=0.10,
        active_attenuation_rules=["ATTEN-HRG-001", "ATTEN-BND-001", "ATTEN-RED-001", "ATTEN-AUD-001", "ATTEN-RPL-001", "ATTEN-HRG-001", "ATTEN-HRG-001", "ATTEN-BND-001"],
        active_amplification_rules=[0.20],
        active_blocking_rules=["BLOCK-CMD-001", "BLOCK-SB-001", "BLOCK-RPL-001"],
    )
    assert math.isclose(g_val, -3.68, rel_tol=1e-3), f"Expected G_path -3.68, got {g_val}"
    assert engine.map_g_path_to_trajectory(g_val) == "stable_or_pressured"
    passed_checks += 1
    logger.info(f"  ✓ Path Degradation (G_path) verified (G_path={g_val:.4f}).")

    # ------------------------------------------------------------------
    # Step 10: Validate Multi-Step Cross-Module Simulation Pipeline
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 10] Validating Full Graph Simulation Pipeline...")
    nodes = [
        {"id": "M43", "layer": "supply_chain", "initial_defense": 0.8},
        {"id": "M46", "layer": "development_environment", "initial_defense": 0.9},
        {"id": "M48", "layer": "rag_data", "initial_defense": 0.95},
        {"id": "M50", "layer": "runtime_sandbox", "initial_defense": 1.0},
    ]
    edges = [
        {"from": "M43", "to": "M46", "type": "context_influence", "pattern_factor": 1.1},
        {"from": "M46", "to": "M48", "type": "context_influence", "pattern_factor": 1.0},
        {"from": "M48", "to": "M50", "type": "runtime_dependency", "feedback": "runtime_control_active"},
    ]
    sim_res = engine.simulate_cross_module_propagation(
        nodes=nodes, edges=edges, time_steps=5, entry_signals={"M43": 0.7}
    )
    assert sim_res["simulation_id"] == "<SIM_PROPAGATION_RUN_001>"
    assert len(sim_res["simulation_history"]) == 5
    assert "final_node_states" in sim_res
    passed_checks += 1
    logger.info("  ✓ Full graph multi-step propagation simulation executed successfully.")

    # ------------------------------------------------------------------
    # Step 11: Validate Safety Boundary Declarations
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 11] Validating Safety Boundary Assertions...")
    sb = engine.get_safety_boundaries()
    expected_flags = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "synthetic_only": True,
        "red_team_engine_not_executable": True,
        "propagation_equation_is_not_exploit_chain": True,
        "theory_model_is_not_detection_rule": True,
    }
    for k, v in expected_flags.items():
        assert sb.get(k) == v, f"Safety flag mismatch: {k}={sb.get(k)}, expected {v}"
    passed_checks += 1
    logger.info("  ✓ Safety Boundary Assertions 100% compliant.")

    # ------------------------------------------------------------------
    # Summary Output
    # ------------------------------------------------------------------
    logger.info("======================================================================")
    logger.info(f"Phase 97A Propagation Dynamics Engine Validation: PASS ({passed_checks}/{total_checks} checks passed)")
    logger.info("======================================================================")
    return True


if __name__ == "__main__":
    try:
        success = validate_propagation_dynamics_engine()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}", exc_info=True)
        sys.exit(1)
