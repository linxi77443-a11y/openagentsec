"""Integration tests for Phase 9 Benchmark Validation & Comparative Study.

Validates:
- Case 1: Text Deception Resistance (Exp 1: LLM Judge FP vs OpenAgentSec Precision).
- Case 2: Multi-Run Reproduction Stability (Exp 2: Single-Run Variance vs 5-Run Consensus).
- Case 3: Adapter Portability across 4 Target Tiers (Exp 3: Portability & Scenario Reuse).
- Case 4: Memory False Positive Reduction (Exp 4: Accumulated Trace vs Delta Evaluation).
- Case 5: Metric Registry Conformance for Phase 9 Comparative Metrics.
"""

from __future__ import annotations

from typing import Any, Dict, List
import pytest

from src.openagentsec.benchmark import MetricRegistry
from src.openagentsec.validation import (
    BenchmarkComparativeStudy,
    ComparisonResult,
    EvaluationComparisonRunner,
    JudgeDecision,
    TraditionalJudgeBaseline,
)
from tests.integration.planner.test_state_memory_security import _load_fixtures


# ==============================================================================
# Case 1: Text Deception Resistance (Exp 1)
# ==============================================================================

def test_case1_text_deception_resistance() -> None:
    """Case 1: Validate that OpenAgentSec eliminates LLM Judge text hallucination false positives."""
    policy, objective, _ = _load_fixtures()
    study = BenchmarkComparativeStudy()

    exp1_res = study.run_experiment_1_text_deception_resistance(policy, objective)

    assert exp1_res["total_cases"] == 10
    # LLM Judge was fooled by text claims -> high false positive rate
    assert exp1_res["judge_false_positives"] >= 5
    assert exp1_res["judge_false_positive_rate"] >= 0.50

    # OpenAgentSec checked runtime sandbox execution -> zero false positives
    assert exp1_res["openagentsec_false_positives"] == 0
    assert exp1_res["openagentsec_false_positive_rate"] == 0.0
    assert exp1_res["false_positive_reduction"] == 1.0


# ==============================================================================
# Case 2: Multi-Run Reproduction Stability (Exp 2)
# ==============================================================================

def test_case2_reproduction_variance_detection() -> None:
    """Case 2: Validate that 5-run statutory zero-variance reproduction catches stochastic drift."""
    study = BenchmarkComparativeStudy()

    # Scenario A: Stochastic noisy runs
    noisy_runs = ["CONFIRMED_DEVIATION", "NO_CONFIRMED_DEVIATION", "NO_CONFIRMED_DEVIATION", "NO_CONFIRMED_DEVIATION", "NO_CONFIRMED_DEVIATION"]
    exp2_noisy = study.run_experiment_2_reproduction_stability(noisy_runs)

    assert exp2_noisy["variance_detected"] is True
    assert exp2_noisy["reproduction_status"] == "INCONCLUSIVE"  # Fail-closed, no majority voting

    # Scenario B: Deterministic 5 clean runs
    clean_runs = ["NO_CONFIRMED_DEVIATION"] * 5
    exp2_clean = study.run_experiment_2_reproduction_stability(clean_runs)

    assert exp2_clean["variance_detected"] is False
    assert exp2_clean["reproduction_rate"] == 1.0
    assert exp2_clean["reproduction_status"] == "REPRODUCED"


# ==============================================================================
# Case 3: Adapter Portability across 4 Target Tiers (Exp 3)
# ==============================================================================

def test_case3_adapter_portability_across_tiers() -> None:
    """Case 3: Validate that evaluation scenarios execute losslessly across 4 target tiers."""
    study = BenchmarkComparativeStudy()

    exp3_res = study.run_experiment_3_adapter_portability()

    assert exp3_res["tier_count"] == 4
    assert exp3_res["adapter_portability_score"] == 1.0
    assert exp3_res["scenario_reuse_rate"] == 1.0
    for tier in exp3_res["evaluated_tiers"]:
        assert tier["success_rate"] == 1.0


# ==============================================================================
# Case 4: Memory False Positive Reduction (Exp 4)
# ==============================================================================

def test_case4_memory_false_positive_delta_evaluation() -> None:
    """Case 4: Validate that Delta State Evaluation eliminates accumulated historical false confirms."""
    study = BenchmarkComparativeStudy()

    exp4_res = study.run_experiment_4_delta_evaluation_advantage()

    assert exp4_res["subsequent_clean_steps"] == 4
    # Accumulated trace method false-confirmed all 4 subsequent clean turns
    assert exp4_res["accumulated_false_confirms"] == 4
    # Delta state evaluation correctly identified zero deviations in clean turns
    assert exp4_res["delta_false_confirms"] == 0
    assert exp4_res["false_confirm_reduction_rate"] == 1.0


# ==============================================================================
# Case 5: Phase 9 Metric Registration and Calculation
# ==============================================================================

def test_case5_comparative_metrics_registration() -> None:
    """Case 5: Validate that all 4 Phase 9 comparative validation metrics are registered in MetricRegistry."""
    req_metrics = [
        "judge_false_positive_rate",
        "evaluation_variance_rate",
        "adapter_portability_score",
        "false_confirm_reduction_rate",
    ]

    for m_id in req_metrics:
        metric = MetricRegistry.get(m_id)
        assert metric is not None, f"Metric '{m_id}' must be registered in MetricRegistry"
        assert metric.formula != ""
        assert metric.unit == "ratio"
        d = metric.to_dict()
        assert d["metric_id"] == m_id
