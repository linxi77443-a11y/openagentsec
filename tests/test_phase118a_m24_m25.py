"""Phase 118A — M24 Control Comparison & M25 Calibration Unit Tests."""

from pathlib import Path
import pytest
import yaml

from scripts.validate_phase118a_m24_m25 import validate
from src.engine.v2.calibration import ConfusionMatrix, compute_calibration
from src.engine.v2.control_comparison import ControlComparisonEngine, ControlMetrics

ROOT = Path(__file__).resolve().parents[1]
EXEC_DIR = ROOT / "executions" / "phase118a_m24_m25"


def test_control_comparison_engine_computation():
    """ControlComparisonEngine must calculate delta increments and usability loss accurately."""
    baseline = ControlMetrics(interception_rate=0.2, benign_usability=0.99, false_positive_rate=0.01)
    engine = ControlComparisonEngine(baseline)

    group_a = ControlMetrics(interception_rate=0.8, benign_usability=0.90, false_positive_rate=0.10)
    engine.add_group("GroupA", group_a)

    results = engine.compare()
    assert "GroupA" in results
    assert abs(results["GroupA"]["interception_rate_increment"] - 0.6) < 1e-4
    assert abs(results["GroupA"]["benign_usability_loss"] - 0.09) < 1e-4
    assert abs(results["GroupA"]["false_positive_increment"] - 0.09) < 1e-4

    best = engine.get_best_group(priority="interception")
    assert best == "GroupA"


def test_calibration_confusion_matrix_and_metrics():
    """ConfusionMatrix dataclass must compute precision, recall, and F1 correctly."""
    cm = ConfusionMatrix(tp=30, fp=5, tn=60, fn=5)
    assert abs(cm.precision - (30 / 35)) < 1e-4
    assert abs(cm.recall - (30 / 35)) < 1e-4
    assert abs(cm.f1 - (30 / 35)) < 1e-4
    assert abs(cm.false_positive_rate - (5 / 65)) < 1e-4


def test_compute_calibration_from_traces():
    """compute_calibration must process trace records and generate a CalibrationReport."""
    traces = [
        {"intent": "attack_simulation", "scorer_result": True, "is_refusal": True},
        {"intent": "attack_simulation", "scorer_result": True, "is_refusal": True},
        {"intent": "attack_simulation", "scorer_result": False, "is_refusal": False},
        {"intent": "benign_baseline", "scorer_result": False, "is_refusal": False},
        {"intent": "benign_baseline", "scorer_result": True, "is_refusal": True},
    ]
    report = compute_calibration(traces)
    assert report.confusion_matrix.tp == 2
    assert report.confusion_matrix.fn == 1
    assert report.confusion_matrix.tn == 1
    assert report.confusion_matrix.fp == 1
    assert report.precision == 2 / 3
    assert report.recall == 2 / 3
    assert report.f1 == 2 / 3


def test_m24_yaml_fixtures():
    """m24_control_comparison.yaml fixture must exist and contain valid results."""
    m24_path = EXEC_DIR / "m24_control_comparison.yaml"
    assert m24_path.is_file()

    with open(m24_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["module_id"] == "M24"
    assert data["synthetic_only"] is True
    assert data["confirmed_vulnerability"] is False
    assert "baseline_group" in data
    assert "comparison_groups" in data
    assert len(data["comparison_groups"]) >= 2


def test_m25_yaml_fixtures():
    """calibration_metrics.yaml fixture must exist and contain valid confusion matrix."""
    m25_path = EXEC_DIR / "calibration_metrics.yaml"
    assert m25_path.is_file()

    with open(m25_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data["module_id"] == "M25"
    assert data["synthetic_only"] is True
    assert data["confirmed_vulnerability"] is False
    assert data["metrics"]["f1_score"] > 0.90
    assert data["calibration_verdict"] == "WELL_CALIBRATED"


def test_phase118a_validator():
    """Phase 118A validator script must pass all checks."""
    result = validate()
    assert result["failed"] == 0
    assert result["passed"] >= 10
    assert result["safety_booleans_all_false"] is True
