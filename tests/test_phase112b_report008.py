import pytest
import json
import os
from src.engine.v2.report_generator import (
    ReportGenerator, ReportData, TraceabilityLink,
    TechniqueIntentMatrixEntry, DualPerspective, CalibrationAppendix, CanaryJudgment
)
from src.engine.v2.safety_invariants import SAFETY_INVARIANTS

@pytest.fixture
def sample_data():
    return ReportData(
        traceability_link=TraceabilityLink("v2.1", "TASK-123", "chain-A", "1.0.0"),
        technique_intent_matrix=[
            TechniqueIntentMatrixEntry("AML.T0000", "Evasion", "tested")
        ],
        dual_perspective=DualPerspective("Static overview", "Residual risk is low"),
        calibration_appendix=CalibrationAppendix(5, 2, 0.98),
        canary_judgment=CanaryJudgment(True, "expected verdict")
    )

def test_init_asserts_safety():
    gen = ReportGenerator()
    assert gen is not None

def test_generate_json_asserts_safety(sample_data):
    gen = ReportGenerator()
    result = gen.generate_json_report(sample_data)
    assert result

def test_generate_md_asserts_safety(sample_data):
    gen = ReportGenerator()
    result = gen.generate_markdown_report(sample_data)
    assert result

def test_trace_integrity_json(sample_data):
    gen = ReportGenerator()
    result = json.loads(gen.generate_json_report(sample_data))
    assert result["traceability_link"]["engine_version"] == "v2.1"
    assert result["traceability_link"]["task_id"] == "TASK-123"

def test_trace_integrity_md(sample_data):
    gen = ReportGenerator()
    result = gen.generate_markdown_report(sample_data)
    assert "Engine Version: v2.1" in result
    assert "Task ID: TASK-123" in result

def test_matrix_no_false_claims_invalid_status(sample_data):
    sample_data.technique_intent_matrix[0].status = "hacked"
    gen = ReportGenerator()
    with pytest.raises(ValueError, match="Invalid matrix status"):
        gen.generate_json_report(sample_data)

def test_matrix_output_correct(sample_data):
    gen = ReportGenerator()
    result = gen.generate_markdown_report(sample_data)
    assert "| AML.T0000 | Evasion | tested |" in result

def test_dual_perspective_coexistence_json(sample_data):
    gen = ReportGenerator()
    result = json.loads(gen.generate_json_report(sample_data))
    assert result["dual_perspective"]["static_summary"] == "Static overview"
    assert result["dual_perspective"]["adaptive_residual_risk"] == "Residual risk is low"

def test_dual_perspective_coexistence_md(sample_data):
    gen = ReportGenerator()
    result = gen.generate_markdown_report(sample_data)
    assert "Static overview" in result
    assert "Residual risk is low" in result

def test_canary_judgment_passthrough(sample_data):
    gen = ReportGenerator()
    result = gen.generate_markdown_report(sample_data)
    assert "Passed Through: True" in result
    assert "Verdict: expected verdict" in result

def test_candidate_enforcement_json(sample_data):
    # Attempt to smuggle a confirmed finding; must be forced back to candidate
    sample_data.findings_status = "CONFIRMED"
    gen = ReportGenerator()
    result = json.loads(gen.generate_json_report(sample_data))
    assert result["findings_status"] == "candidate"
    assert result["requires_human_review"] is True
    assert result["synthetic_only"] is True

def test_candidate_enforcement_md(sample_data):
    sample_data.findings_status = "CONFIRMED"
    gen = ReportGenerator()
    result = gen.generate_markdown_report(sample_data)
    assert "Status: candidate" in result
    assert "Requires Human Review: true" in result
    assert "Synthetic Only: true" in result
