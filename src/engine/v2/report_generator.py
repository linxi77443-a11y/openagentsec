import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import os
from src.engine.v2.safety_invariants import assert_safety_invariants


@dataclass
class TraceabilityLink:
    """Traceability link for report provenance."""
    engine_version: str
    task_id: str
    converter_chain: str
    dataset_version: str


@dataclass
class TechniqueIntentMatrixEntry:
    """ATLAS technique -> intent matrix entry."""
    technique_id: str
    intent: str
    status: str


@dataclass
class DualPerspective:
    """Dual-perspective presentation (static + adaptive residual risk)."""
    static_summary: str
    adaptive_residual_risk: str


@dataclass
class CalibrationAppendix:
    """Calibration appendix (M25)."""
    false_positives: int
    false_negatives: int
    benign_use_correctness: float


@dataclass
class CanaryJudgment:
    """Canary judgment result."""
    passed_through: bool
    verdict: str


@dataclass
class ReportData:
    """Aggregated report data."""
    traceability_link: TraceabilityLink
    technique_intent_matrix: List[TechniqueIntentMatrixEntry]
    dual_perspective: DualPerspective
    calibration_appendix: CalibrationAppendix
    canary_judgment: Optional[CanaryJudgment]
    findings_status: str = "candidate"
    requires_human_review: bool = True
    synthetic_only: bool = True


class ReportGenerator:
    """Generates JSON / Markdown assessment reports with enforced safety invariants."""

    def __init__(self):
        assert_safety_invariants()

    def _enforce_safety(self, data: ReportData) -> None:
        data.findings_status = "candidate"
        data.requires_human_review = True
        data.synthetic_only = True
        for entry in data.technique_intent_matrix:
            if entry.status not in ("tested", "planned", "not_covered"):
                raise ValueError(f"Invalid matrix status: {entry.status}")

    def generate_json_report(self, data: ReportData) -> str:
        assert_safety_invariants()
        self._enforce_safety(data)
        return json.dumps(asdict(data), indent=2)

    def generate_markdown_report(self, data: ReportData) -> str:
        assert_safety_invariants()
        self._enforce_safety(data)
        md = f"""# Simulation Assessment Report

> [!WARNING]
> SIMULATION DECLARATION: This report contains synthetic data only. No real infrastructure was targeted.

> [!CAUTION]
> SAFETY INVARIANTS DECLARATION:
> - confirmed_vulnerability: False
> - formal_finding_allowed: False
> - production_safety_claimed: False
> - controlled_replay_claimed: False
> - controlled_replay_execution_allowed: False
> - assessment_execution_performed: False
> - synthetic_only: True
> - fake_runtime_only: True
> - requires_human_review: True
> - all_findings_are_candidate: True

> [!NOTE]
> ADAPTIVE RESIDUAL RISK DECLARATION:
> {data.dual_perspective.adaptive_residual_risk}

## Traceability
- Engine Version: {data.traceability_link.engine_version}
- Task ID: {data.traceability_link.task_id}
- Converter Chain: {data.traceability_link.converter_chain}
- Dataset Version: {data.traceability_link.dataset_version}

## Dual-Perspective Presentation
**Static Summary:**
{data.dual_perspective.static_summary}

**Adaptive Residual Risk:**
{data.dual_perspective.adaptive_residual_risk}

## Technique Intent Matrix (ATLAS v5.4)
| Technique ID | Intent | Status |
|---|---|---|
"""
        for entry in data.technique_intent_matrix:
            md += f"| {entry.technique_id} | {entry.intent} | {entry.status} |\n"

        md += f"""
## Calibration Appendix
- False Positives: {data.calibration_appendix.false_positives}
- False Negatives: {data.calibration_appendix.false_negatives}
- Benign-Use Correctness: {data.calibration_appendix.benign_use_correctness * 100}%

## Canary Judgment
"""
        if data.canary_judgment:
            md += f"- Passed Through: {data.canary_judgment.passed_through}\n"
            md += f"- Verdict: {data.canary_judgment.verdict}\n"
        else:
            md += "None\n"

        md += f"""
## Findings Summary
Status: {data.findings_status}
Requires Human Review: {str(data.requires_human_review).lower()}
Synthetic Only: {str(data.synthetic_only).lower()}
"""
        return md

    def save_reports(self, data: ReportData, output_dir: str, base_filename: str) -> None:
        json_content = self.generate_json_report(data)
        md_content = self.generate_markdown_report(data)
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, base_filename + ".json"), "w") as f:
            f.write(json_content)
        with open(os.path.join(output_dir, base_filename + ".md"), "w") as f:
            f.write(md_content)
