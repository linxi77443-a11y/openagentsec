"""
Pytest Unit Test Suite for Phase 96C Assessment Dashboard Data API
Path: tests/test_phase96c_dashboard_api.py

Tests AssessmentDashboardAPI and DashboardDataAdapter across 4 Views, Filters,
Safety Boundary Assertions, and JSON Exports.
"""

import os
import json
import pytest
from pathlib import Path

from core.dashboard_api import (
    AssessmentDashboardAPI,
    DashboardDataAdapter,
    SAFE_BOUNDARIES,
    STATUS_COLOR_MAP,
    DEFENSE_STATE_COLOR_MAP
)

ROOT_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def dashboard_api():
    """Fixture providing initialized AssessmentDashboardAPI instance."""
    return AssessmentDashboardAPI(root_dir=ROOT_DIR)


def test_dashboard_api_initialization(dashboard_api):
    """Test API initialization and basic summary data."""
    assert dashboard_api is not None
    assert dashboard_api.adapter is not None
    assert len(dashboard_api.adapter.modules_data) > 0

    summary = dashboard_api.get_summary()
    assert summary["api_version"] == "96C-1.0"
    assert summary["read_only"] is True
    assert summary["platform_metrics"]["total_modules"] > 0
    assert summary["platform_metrics"]["confirmed_vulnerabilities"] == 0


def test_safety_boundary_assertions(dashboard_api):
    """Test safety boundary assertions across all API view responses."""
    views_bundle = dashboard_api.get_all_views()
    sb = views_bundle.get("safety_boundaries", {})

    assert sb["synthetic_only"] is True
    assert sb["confirmed_vulnerability"] is False
    assert sb["formal_finding_allowed"] is False
    assert sb["production_safety_claimed"] is False
    assert sb["dashboard_not_execution_interface"] is True


def test_coverage_heatmap_view(dashboard_api):
    """Test View 1: Coverage Heatmap payload structure and filters."""
    heatmap = dashboard_api.get_coverage_heatmap()

    assert heatmap["view_id"] == "coverage_heatmap"
    assert heatmap["read_only"] is True
    assert "items" in heatmap
    assert "matrix_anchors" in heatmap
    assert "layers" in heatmap
    assert heatmap["status_color_map"] == STATUS_COLOR_MAP

    items = heatmap["items"]
    assert len(items) > 0

    first_item = items[0]
    assert "module_id" in first_item
    assert "module_name" in first_item
    assert "priority" in first_item
    assert "layer" in first_item
    assert "matrix_anchor" in first_item
    assert "coverage_status" in first_item
    assert "capability_value" in first_item
    assert "risk_level" in first_item
    assert "color" in first_item

    # Test filtering by priority P0
    p0_heatmap = dashboard_api.get_coverage_heatmap(priority="P0")
    for item in p0_heatmap["items"]:
        assert item["priority"] == "P0"

    # Test filtering by layer chatbot
    chatbot_heatmap = dashboard_api.get_coverage_heatmap(layer="chatbot")
    for item in chatbot_heatmap["items"]:
        assert item["layer"] == "chatbot"

    # Test filtering by coverage status mvp_complete
    mvp_heatmap = dashboard_api.get_coverage_heatmap(coverage_status="mvp_complete")
    for item in mvp_heatmap["items"]:
        assert item["coverage_status"] == "mvp_complete"


def test_attack_chain_propagation_view(dashboard_api):
    """Test View 2: Attack Chain Propagation payload structure and filters."""
    chain_view = dashboard_api.get_attack_chain_propagation()

    assert chain_view["view_id"] == "attack_chain_propagation"
    assert chain_view["read_only"] is True
    assert "chains" in chain_view
    assert "summary" in chain_view
    assert chain_view["defense_state_color_map"] == DEFENSE_STATE_COLOR_MAP

    chains = chain_view["chains"]
    assert len(chains) > 0

    first_chain = chains[0]
    assert "chain_id" in first_chain
    assert "chain_name" in first_chain
    assert "attacker_type" in first_chain
    assert "attack_objective" in first_chain
    assert "nodes" in first_chain
    assert "chain_level_evaluation" in first_chain

    eval_info = first_chain["chain_level_evaluation"]
    assert "simulated capability signal only" in eval_info["breakthrough_semantics"]

    # Test filtering by chain_id if chain exists
    c_id = first_chain["chain_id"]
    filtered_chain = dashboard_api.get_attack_chain_propagation(chain_id=c_id)
    assert len(filtered_chain["chains"]) == 1
    assert filtered_chain["chains"][0]["chain_id"] == c_id


def test_defense_degradation_timeline_view(dashboard_api):
    """Test View 3: Defense Degradation Timeline payload structure and filters."""
    timeline_view = dashboard_api.get_defense_degradation_timeline()

    assert timeline_view["view_id"] == "defense_degradation_timeline"
    assert timeline_view["read_only"] is True
    assert "timeline_nodes" in timeline_view
    assert "summary" in timeline_view
    assert timeline_view["state_color_map"] == DEFENSE_STATE_COLOR_MAP

    nodes = timeline_view["timeline_nodes"]
    assert len(nodes) > 0

    first_node = nodes[0]
    assert "node_id" in first_node
    assert "pattern_id" in first_node
    assert "module_id" in first_node
    assert "state_sequence" in first_node
    assert "final_state" in first_node
    assert "final_state_color" in first_node

    # Test filtering by final_state
    f_state = first_node["final_state"]
    filtered_tl = dashboard_api.get_defense_degradation_timeline(final_state=f_state)
    for node in filtered_tl["timeline_nodes"]:
        assert node["final_state"] == f_state


def test_red_team_panel_summary_view(dashboard_api):
    """Test View 4: Red Team Panel Summary payload structure and filters."""
    red_view = dashboard_api.get_red_team_panel_summary()

    assert red_view["view_id"] == "red_team_panel_summary"
    assert red_view["read_only"] is True
    assert "available_attack_profiles" in red_view
    assert "available_modules" in red_view
    assert "simulation_controls" in red_view
    assert "evidence_viewer" in red_view
    assert "summary" in red_view

    profiles = red_view["available_attack_profiles"]
    assert len(profiles) >= 5

    controls = red_view["simulation_controls"]
    assert controls["read_only_simulation"] is True

    # Test filtering by attacker_type
    filtered_red = dashboard_api.get_red_team_panel_summary(attacker_type="malicious_insider")
    assert len(filtered_red["available_attack_profiles"]) == 1
    assert filtered_red["available_attack_profiles"][0]["attacker_type"] == "malicious_insider"


def test_export_dashboard_json(dashboard_api, tmp_path):
    """Test dashboard JSON snapshot export functionality."""
    export_file = tmp_path / "dashboard_export.json"
    actual_path = dashboard_api.export_dashboard_json(output_path=export_file)

    assert Path(actual_path).exists()

    with open(actual_path, "r", encoding="utf-8") as f:
        exported_data = json.load(f)

    assert "views" in exported_data
    assert "coverage_heatmap" in exported_data["views"]
    assert "attack_chain_propagation" in exported_data["views"]
    assert "defense_degradation_timeline" in exported_data["views"]
    assert "red_team_panel_summary" in exported_data["views"]
