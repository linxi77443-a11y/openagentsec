import pytest
import yaml
from src.engine.v2.adaptive_simulator import AdaptiveSimulator
from src.engine.v2.safety_invariants import SAFETY_INVARIANTS

def get_mock_scenarios():
    return [
        {
            "id": "adapt_001",
            "static_payload": "<SIM_PAYLOAD_STATIC_001>",
            "defense_feedback": "block",
            "adaptive_variants": [
                {"bypasses_block": True}
            ]
        },
        {
            "id": "adapt_002",
            "static_payload": "<SIM_PAYLOAD_STATIC_002>",
            "defense_feedback": "block",
            "adaptive_variants": [
                {"bypasses_block": False}
            ]
        },
        {
            "id": "adapt_003",
            "static_payload": "<SIM_PAYLOAD_STATIC_003>",
            "defense_feedback": "allow",
            "adaptive_variants": [
                {"always_success": True}
            ]
        }
    ]

def test_simulator_initialization():
    sim = AdaptiveSimulator([])
    assert sim.scenarios == []
    assert sim.results == []

def test_simulator_with_data():
    scenarios = get_mock_scenarios()
    sim = AdaptiveSimulator(scenarios)
    assert len(sim.scenarios) == 3

def test_static_success_rate():
    sim = AdaptiveSimulator(get_mock_scenarios())
    result = sim.run_adaptive_simulation()
    # 1 out of 3 is "allow" statically
    assert result["static_success_rate"] == pytest.approx(1/3)

def test_adaptive_success_rate():
    sim = AdaptiveSimulator(get_mock_scenarios())
    result = sim.run_adaptive_simulation()
    # 1 adaptively bypasses block, 1 statically allows (also adaptively allows)
    # Total adaptive success = 2 out of 3
    assert result["adaptive_success_rate"] == pytest.approx(2/3)

def test_degradation_proven():
    sim = AdaptiveSimulator(get_mock_scenarios())
    result = sim.run_adaptive_simulation()
    # Degradation: adaptive success > static success
    assert result["adaptive_success_rate"] > result["static_success_rate"]

def test_safety_invariants_asserted_in_simulation():
    # Verify synthetic only
    assert SAFETY_INVARIANTS["synthetic_only"] is True
    assert SAFETY_INVARIANTS["requires_human_review"] is True

def test_results_status():
    sim = AdaptiveSimulator(get_mock_scenarios())
    result = sim.run_adaptive_simulation()
    assert result["status"] == "candidate"
    assert result["requires_human_review"] is True

def test_individual_results_status():
    sim = AdaptiveSimulator(get_mock_scenarios())
    result = sim.run_adaptive_simulation()
    for res in result["results"]:
        assert res["status"] == "candidate"
        assert res["requires_human_review"] is True

def test_empty_scenarios():
    sim = AdaptiveSimulator([])
    result = sim.run_adaptive_simulation()
    assert result["total_scenarios"] == 0
    assert result["static_success_rate"] == 0
    assert result["adaptive_success_rate"] == 0

def test_all_blocked_statically_none_bypassed():
    scenarios = [
        {"defense_feedback": "block", "adaptive_variants": [{"bypasses_block": False}]}
    ]
    sim = AdaptiveSimulator(scenarios)
    result = sim.run_adaptive_simulation()
    assert result["static_success_rate"] == 0
    assert result["adaptive_success_rate"] == 0

def test_all_blocked_statically_all_bypassed():
    scenarios = [
        {"defense_feedback": "block", "adaptive_variants": [{"bypasses_block": True}]}
    ]
    sim = AdaptiveSimulator(scenarios)
    result = sim.run_adaptive_simulation()
    assert result["static_success_rate"] == 0
    assert result["adaptive_success_rate"] == 1.0

def test_read_playbook():
    with open("adversarial_playbooks/adaptive_residual_risk_mvp/playbook.yaml", "r") as f:
        data = yaml.safe_load(f)
    assert len(data["scenarios"]) == 10
    sim = AdaptiveSimulator(data["scenarios"])
    result = sim.run_adaptive_simulation()
    assert result["total_scenarios"] == 10
    # Expected in our playbook: 
    # Static allow: adapt_003, adapt_007 (2/10 = 0.2)
    # Adaptive success: 3, 7 + 1, 2, 4, 8, 10 (7/10 = 0.7)
    assert result["static_success_rate"] == 0.3
    assert result["adaptive_success_rate"] == 0.7
    assert result["adaptive_success_rate"] > result["static_success_rate"]
