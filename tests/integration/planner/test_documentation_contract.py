"""Documentation Contract Tests for Phase 7.4.2 OpenAgentSec Technical Report & Documentation.

Validates that research technical reports, threat models, methodology, and specifications
exist, cover mandatory sections, and align precisely with code registries.
"""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from src.openagentsec.benchmark import (
    EvidenceContractMatrix,
    MetricRegistry,
    ScenarioRegistry,
    TargetCatalog,
)


DOCS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "research"


# ==============================================================================
# Case 1: Technical Report Structure & Content
# ==============================================================================

def test_case1_technical_report_contract() -> None:
    """Case 1: Validate openagentsec_technical_report.md exists and contains required sections."""
    report_path = DOCS_DIR / "openagentsec_technical_report.md"
    assert report_path.exists(), f"Missing technical report at {report_path}"

    content = report_path.read_text(encoding="utf-8")
    assert "OpenAgentSec: A Deterministic Evidence-driven Security Benchmark" in content
    assert "## Abstract" in content
    assert "## 1. Problem Formulation" in content
    assert "## 2. Scientific Contributions" in content
    assert "## 3. Experimental Evaluation Synthesis" in content
    assert "## 4. Conclusion" in content

    # Key concepts present
    assert "Evidence Precedence Axiom" in content
    assert "Zero-Variance" in content
    assert "Fail-Closed" in content


# ==============================================================================
# Case 2: Threat Model Completeness
# ==============================================================================

def test_case2_threat_model_contract() -> None:
    """Case 2: Validate threat_model.md exists and covers all 4 threat domains."""
    threat_path = DOCS_DIR / "threat_model.md"
    assert threat_path.exists(), f"Missing threat model at {threat_path}"

    content = threat_path.read_text(encoding="utf-8")
    assert "## 2. Threat Domain 1: Memory Threats" in content
    assert "## 3. Threat Domain 2: Retrieval Threats" in content
    assert "## 4. Threat Domain 3: Authorization Threats" in content
    assert "## 5. Threat Domain 4: Tool Execution Threats" in content
    assert "## 6. Threat Mitigation & Security Boundary Matrix" in content


# ==============================================================================
# Case 3: Evaluation Methodology Pipeline & Axioms
# ==============================================================================

def test_case3_evaluation_methodology_contract() -> None:
    """Case 3: Validate evaluation_methodology.md covers 7-stage pipeline and formal axioms."""
    method_path = DOCS_DIR / "evaluation_methodology.md"
    assert method_path.exists(), f"Missing evaluation methodology at {method_path}"

    content = method_path.read_text(encoding="utf-8")
    assert "## 1. The 7-Stage Universal Evaluation Pipeline" in content
    assert "## 2. Core Epistemological Axioms" in content
    assert "Axiom 1: Evidence Precedence Hierarchy" in content
    assert "Axiom 2: Strict Fail-Closed Principle" in content
    assert "Axiom 3: Statutory Zero-Variance Reproduction Rule" in content
    assert "Axiom 4: Delta State Evaluation Principle" in content
    assert "## 3. Evidence Matrix and Sufficiency Contract" in content


# ==============================================================================
# Case 4: Benchmark Specification Alignment
# ==============================================================================

def test_case4_benchmark_specification_contract() -> None:
    """Case 4: Validate benchmark_specification.md matches registries for targets, scenarios, and metrics."""
    spec_path = DOCS_DIR / "benchmark_specification.md"
    assert spec_path.exists(), f"Missing benchmark specification at {spec_path}"

    content = spec_path.read_text(encoding="utf-8")
    assert "OpenAgentSec-Agent-Security-Benchmark" in content
    assert "Specification Version: `1.0.0`" in content

    # All 7 target IDs present
    for target in TargetCatalog.list_all():
        assert target.target_id in content

    # All 8 scenario IDs present
    for scenario in ScenarioRegistry.list_all():
        assert scenario.scenario_id in content

    # All 9 metric IDs present
    for metric in MetricRegistry.list_all():
        assert metric.metric_id in content

    # All 7 evidence types present
    for ev_type in EvidenceContractMatrix.get_all_requirements():
        assert ev_type in content


# ==============================================================================
# Case 5: Limitations and Future Roadmap
# ==============================================================================

def test_case5_limitations_and_future_roadmap_contract() -> None:
    """Case 5: Validate limitations_and_future_work.md contains honest boundaries and phase roadmap."""
    lim_path = DOCS_DIR / "limitations_and_future_work.md"
    assert lim_path.exists(), f"Missing limitations document at {lim_path}"

    content = lim_path.read_text(encoding="utf-8")
    assert "## 1. Boundary & Limitations" in content
    assert "Multi-Agent Delegation & Cascading Authority" in content
    assert "Stochastic Temperature & Behavioral Drift" in content
    assert "Multimodal Side-Channels" in content
    assert "Hidden Internal Model Reasoning" in content
    assert "## 2. Future Roadmap" in content
    assert "Phase 8" in content
    assert "Phase 9" in content
    assert "Phase 10" in content
