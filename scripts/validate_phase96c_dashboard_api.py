#!/usr/bin/env python3
"""
Exclusive Validation Script for Phase 96C Visualization Assessment Dashboard Data API
Path: scripts/validate_phase96c_dashboard_api.py

Validates 4 Dashboard View Contracts (Coverage Heatmap, Attack Chain Propagation,
Defense Degradation Timeline, Red Team Panel Summary), Safety Boundaries, Filter Functionality,
and JSON Export.

Usage:
  python3 scripts/validate_phase96c_dashboard_api.py
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.dashboard_api import (
    AssessmentDashboardAPI,
    DashboardDataAdapter,
    SAFE_BOUNDARIES,
    STATUS_COLOR_MAP,
    DEFENSE_STATE_COLOR_MAP
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Phase96CValidator")


def validate_dashboard_api():
    logger.info("======================================================================")
    logger.info("Phase 96C — Assessment Dashboard Data API Exclusive Validator")
    logger.info("======================================================================")

    passed_checks = 0
    total_checks = 0

    api = AssessmentDashboardAPI(root_dir=root_dir)

    # ------------------------------------------------------------------
    # Step 1: Initial API Initialization & Overview Summary
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 1] Initializing API and checking summary platform metrics...")
    summary = api.get_summary()
    assert summary.get("api_version") == "96C-1.0", "API version mismatch"
    assert summary.get("read_only") is True, "API must be read-only"

    metrics = summary.get("platform_metrics", {})
    assert metrics.get("total_modules", 0) > 0, "Total modules count should be > 0"
    assert metrics.get("confirmed_vulnerabilities") == 0, "Confirmed vulnerabilities must be 0"
    passed_checks += 1
    logger.info(f"  ✓ Summary metrics validated. Total modules: {metrics.get('total_modules')}")

    # ------------------------------------------------------------------
    # Step 2: Validate Safety Boundaries on All API Endpoints
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 2] Validating Safety Boundary Assertions across all views...")
    all_views_bundle = api.get_all_views()
    sb = all_views_bundle.get("safety_boundaries", {})

    for key, expected_val in SAFE_BOUNDARIES.items():
        assert sb.get(key) == expected_val, f"Safety boundary {key} expected {expected_val}, got {sb.get(key)}"

    passed_checks += 1
    logger.info("  ✓ Safety boundaries validated (100% compliant with Phase 87A / Phase 96C rules).")

    # ------------------------------------------------------------------
    # Step 3: Validate View 1 — Coverage Heatmap
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 3] Validating View 1 — Coverage Heatmap Data Contract...")
    heatmap = api.get_coverage_heatmap()
    assert heatmap.get("view_id") == "coverage_heatmap"
    assert "items" in heatmap
    assert "matrix_anchors" in heatmap
    assert "layers" in heatmap
    assert "status_color_map" in heatmap

    # Check item schema
    items = heatmap.get("items", [])
    assert len(items) > 0, "Heatmap items should not be empty"
    first_item = items[0]
    for req_field in ["module_id", "module_name", "priority", "layer", "matrix_anchor", "coverage_status", "capability_value", "risk_level", "color"]:
        assert req_field in first_item, f"Heatmap item missing field {req_field}"

    # Test Heatmap Filters (priority=P0)
    p0_heatmap = api.get_coverage_heatmap(priority="P0")
    for p_item in p0_heatmap.get("items", []):
        assert p_item["priority"] == "P0", "Filter priority=P0 failed"

    passed_checks += 1
    logger.info(f"  ✓ Coverage Heatmap contract & filtering validated. Items count: {len(items)}")

    # ------------------------------------------------------------------
    # Step 4: Validate View 2 — Attack Chain Propagation View
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 4] Validating View 2 — Attack Chain Propagation View Data Contract...")
    chain_view = api.get_attack_chain_propagation()
    assert chain_view.get("view_id") == "attack_chain_propagation"
    chains = chain_view.get("chains", [])
    assert len(chains) > 0, "Attack chains should not be empty"

    first_chain = chains[0]
    for c_field in ["chain_id", "chain_name", "attacker_type", "attack_objective", "nodes", "chain_level_evaluation"]:
        assert c_field in first_chain, f"Chain missing field {c_field}"

    # Check breakthrough detected semantics assertion
    eval_info = first_chain.get("chain_level_evaluation", {})
    assert "breakthrough_semantics" in eval_info, "Breakthrough semantics explanation required"
    assert "simulated capability signal only" in eval_info["breakthrough_semantics"]

    passed_checks += 1
    logger.info(f"  ✓ Attack Chain Propagation contract validated. Chains count: {len(chains)}")

    # ------------------------------------------------------------------
    # Step 5: Validate View 3 — Defense Degradation Timeline View
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 5] Validating View 3 — Defense Degradation Timeline Data Contract...")
    timeline_view = api.get_defense_degradation_timeline()
    assert timeline_view.get("view_id") == "defense_degradation_timeline"
    nodes = timeline_view.get("timeline_nodes", [])
    assert len(nodes) > 0, "Timeline nodes should not be empty"

    first_node = nodes[0]
    for t_field in ["node_id", "pattern_id", "module_id", "state_sequence", "final_state", "final_state_color"]:
        assert t_field in first_node, f"Timeline node missing field {t_field}"

    assert len(first_node["state_sequence"]) > 0, "State sequence should contain steps"

    passed_checks += 1
    logger.info(f"  ✓ Defense Degradation Timeline contract validated. Nodes count: {len(nodes)}")

    # ------------------------------------------------------------------
    # Step 6: Validate View 4 — Red Team Panel Summary View
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 6] Validating View 4 — Red Team Panel Summary Data Contract...")
    red_view = api.get_red_team_panel_summary()
    assert red_view.get("view_id") == "red_team_panel_summary"

    profiles = red_view.get("available_attack_profiles", [])
    assert len(profiles) >= 5, "Should provide 5 standardized attacker profiles"

    ev = red_view.get("evidence_viewer", {})
    assert "breakthrough_signals" in ev
    assert "semantics" in ev

    controls = red_view.get("simulation_controls", {})
    assert controls.get("read_only_simulation") is True, "Simulation controls must be read-only"

    passed_checks += 1
    logger.info(f"  ✓ Red Team Panel Summary contract validated. Profiles count: {len(profiles)}")

    # ------------------------------------------------------------------
    # Step 7: Export JSON Snapshot & Verify Output File
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 7] Validating JSON Snapshot Export...")
    export_path = root_dir / "dashboard" / "dashboard_data.json"
    actual_path = api.export_dashboard_json(output_path=export_path)
    assert Path(actual_path).exists(), f"Export file not found at {actual_path}"

    with open(actual_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "views" in data
    assert "coverage_heatmap" in data["views"]
    assert "attack_chain_propagation" in data["views"]
    assert "defense_degradation_timeline" in data["views"]
    assert "red_team_panel_summary" in data["views"]

    passed_checks += 1
    logger.info(f"  ✓ Dashboard JSON snapshot successfully exported to {actual_path}")

    # ------------------------------------------------------------------
    # Summary Output
    # ------------------------------------------------------------------
    logger.info("======================================================================")
    logger.info(f"Validation Result: PASS ({passed_checks}/{total_checks} checks passed)")
    logger.info("======================================================================")
    return True


if __name__ == "__main__":
    try:
        success = validate_dashboard_api()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}", exc_info=True)
        sys.exit(1)
