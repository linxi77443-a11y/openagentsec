"""Release Documentation Contract Tests for Phase 7.4.3 OpenAgentSec External Validation Preparation.

Validates that all public release documents, guides, templates, and checklists exist and satisfy content standards.
"""

from __future__ import annotations

from pathlib import Path
import pytest


ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
DOCS_RELEASE_DIR = ROOT_DIR / "docs" / "release"
GITHUB_DIR = ROOT_DIR / ".github" / "ISSUE_TEMPLATE"


# ==============================================================================
# Case 1: Root README.md Contract
# ==============================================================================

def test_case1_root_readme_contract() -> None:
    """Case 1: Validate root README.md contains standard public release sections."""
    readme_path = ROOT_DIR / "README.md"
    assert readme_path.exists(), "README.md must exist in root directory"

    content = readme_path.read_text(encoding="utf-8")
    assert "## 🌟 Project Overview" in content
    assert "## ❓ Why OpenAgentSec?" in content
    assert "## 🏛️ Architecture Overview" in content
    assert "## 🎯 Target & Benchmark Coverage" in content
    assert "## ⚡ Quick Example" in content
    assert "TARGET-LANGGRAPH-MVP1" in content
    assert "TARGET-COMMERCIAL-LLM-AGENT" in content
    assert "Evidence Precedence Axiom" in content


# ==============================================================================
# Case 2: Quick Start Guide Contract
# ==============================================================================

def test_case2_quick_start_guide_contract() -> None:
    """Case 2: Validate quick_start.md contains setup and extension instructions."""
    qs_path = DOCS_RELEASE_DIR / "quick_start.md"
    assert qs_path.exists(), "quick_start.md must exist"

    content = qs_path.read_text(encoding="utf-8")
    assert "## 1. Environment & Prerequisites" in content
    assert "## 2. Running Benchmark Evaluation Tests" in content
    assert "## 3. Extending the Framework" in content
    assert "pytest tests/integration/planner/ -v" in content
    assert "How to Add a New Target Adapter" in content
    assert "How to Register a New Scenario" in content
    assert "How to Register a New Metric" in content


# ==============================================================================
# Case 3: Demo Workflow Contract
# ==============================================================================

def test_case3_demo_workflow_contract() -> None:
    """Case 3: Validate demo_workflow.md contains full lifecycle walkthrough."""
    demo_path = DOCS_RELEASE_DIR / "demo_workflow.md"
    assert demo_path.exists(), "demo_workflow.md must exist"

    content = demo_path.read_text(encoding="utf-8")
    assert "## 1. Overview of the Evaluation Flow" in content
    assert "## 2. Step-by-Step Code Walkthrough" in content
    assert "sequenceDiagram" in content
    assert "DeterministicToolBoundaryOracle" in content
    assert "ReproductionAggregator" in content
    assert "REPRODUCED" in content


# ==============================================================================
# Case 4: Benchmark Results Contract
# ==============================================================================

def test_case4_benchmark_results_contract() -> None:
    """Case 4: Validate benchmark_results.md documents empirical reference outcomes."""
    results_path = DOCS_RELEASE_DIR / "benchmark_results.md"
    assert results_path.exists(), "benchmark_results.md must exist"

    content = results_path.read_text(encoding="utf-8")
    assert "## 1. Domain 1 & 2: Memory & Retrieval Security Results" in content
    assert "## 2. Retrieval Security Mitigation Boundary Results" in content
    assert "## 3. Domain 3: Authorization & Operation Scope Results" in content
    assert "## 4. Blackbox Frameworks & Commercial LLM Agent Results" in content
    assert "Trust Filtering" in content
    assert "Context Isolation" in content
    assert "parameter_violation_block_rate" in content


# ==============================================================================
# Case 5: Contribution Guide & Issue Templates Contract
# ==============================================================================

def test_case5_contribution_guide_and_templates_contract() -> None:
    """Case 5: Validate CONTRIBUTING.md, contribution_guide.md, and GitHub Issue Templates."""
    contrib_root = ROOT_DIR / "CONTRIBUTING.md"
    contrib_doc = DOCS_RELEASE_DIR / "contribution_guide.md"
    bug_template = GITHUB_DIR / "bug_report.md"
    feat_template = GITHUB_DIR / "feature_request.md"

    assert contrib_root.exists(), "Root CONTRIBUTING.md must exist"
    assert contrib_doc.exists(), "docs/release/contribution_guide.md must exist"
    assert bug_template.exists(), "bug_report.md template must exist"
    assert feat_template.exists(), "feature_request.md template must exist"

    bug_content = bug_template.read_text(encoding="utf-8")
    assert "Target Under Evaluation" in bug_content
    assert "Evidence Logs & Traces" in bug_content

    feat_content = feat_template.read_text(encoding="utf-8")
    assert "Evidence & Oracles" in feat_content


# ==============================================================================
# Case 6: Release Checklist Contract
# ==============================================================================

def test_case6_release_checklist_contract() -> None:
    """Case 6: Validate release_checklist.md exists and covers code, research, and release items."""
    checklist_path = DOCS_RELEASE_DIR / "release_checklist.md"
    assert checklist_path.exists(), "release_checklist.md must exist"

    content = checklist_path.read_text(encoding="utf-8")
    assert "## 1. Code & Framework Verification" in content
    assert "## 2. Research & Academic Documentation" in content
    assert "## 3. Release Metadata & Developer Experience" in content
    assert "[x]" in content
