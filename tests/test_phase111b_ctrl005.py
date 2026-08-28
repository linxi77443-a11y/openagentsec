import pytest
from src.engine.v2.control_comparison import ControlMetrics, ControlComparisonEngine

def test_metrics_initialization():
    metrics = ControlMetrics(0.8, 0.9, 0.05)
    assert metrics.interception_rate == 0.8
    assert metrics.benign_usability == 0.9
    assert metrics.false_positive_rate == 0.05

def test_engine_initialization():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    assert engine.baseline == baseline
    assert len(engine.groups) == 0

def test_add_group():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("test1", ControlMetrics(0.6, 0.9, 0.1))
    assert "test1" in engine.groups

def test_compare_interception_increment():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("test1", ControlMetrics(0.6, 0.9, 0.1))
    results = engine.compare()
    assert pytest.approx(results["test1"]["interception_rate_increment"]) == 0.1

def test_compare_usability_loss():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("test1", ControlMetrics(0.6, 0.9, 0.1))
    results = engine.compare()
    assert pytest.approx(results["test1"]["benign_usability_loss"]) == 0.1

def test_compare_false_positive_increment():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("test1", ControlMetrics(0.6, 0.9, 0.1))
    results = engine.compare()
    assert pytest.approx(results["test1"]["false_positive_increment"]) == 0.1

def test_get_best_group_empty():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    assert engine.get_best_group() == ""

def test_get_best_group_interception():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("low", ControlMetrics(0.6, 0.9, 0.1))
    engine.add_group("high", ControlMetrics(0.9, 0.5, 0.2))
    assert engine.get_best_group("interception") == "high"

def test_get_best_group_usability():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("low", ControlMetrics(0.6, 0.9, 0.1))
    engine.add_group("high", ControlMetrics(0.9, 0.5, 0.2))
    assert engine.get_best_group("usability") == "low"

def test_compare_multiple_groups():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("g1", ControlMetrics(0.6, 0.9, 0.1))
    engine.add_group("g2", ControlMetrics(0.7, 0.8, 0.2))
    results = engine.compare()
    assert len(results) == 2
    assert "g1" in results and "g2" in results

def test_negative_increment_handling():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("worse", ControlMetrics(0.4, 0.9, 0.1))
    results = engine.compare()
    assert results["worse"]["interception_rate_increment"] < 0

def test_zero_increment_handling():
    baseline = ControlMetrics(0.5, 1.0, 0.0)
    engine = ControlComparisonEngine(baseline)
    engine.add_group("same", ControlMetrics(0.5, 1.0, 0.0))
    results = engine.compare()
    assert results["same"]["interception_rate_increment"] == 0
    assert results["same"]["benign_usability_loss"] == 0
    assert results["same"]["false_positive_increment"] == 0
