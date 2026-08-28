"""
PyTest Unit Test Suite for Phase 96C Report Exporter (ReportExporter)
Path: tests/test_phase96c_report_exporter.py
"""

import re
import pytest
from pathlib import Path

from core.report_exporter import ReportExporter, REPORT_SAFE_BOUNDARIES
from core.dashboard_api import AssessmentDashboardAPI


@pytest.fixture
def exporter(tmp_path):
    root_dir = Path(__file__).resolve().parent.parent
    return ReportExporter(root_dir=root_dir)


def test_report_exporter_initialization(exporter):
    """Test clean initialization of ReportExporter."""
    assert exporter is not None
    assert exporter.dashboard_api is not None
    assert exporter.templates_dir.exists()


def test_safety_boundary_assertions(exporter):
    """Test that safety boundary assertions are properly injected in report context."""
    context = exporter.get_report_context()
    sb = context.get("safety_boundaries", {})

    assert sb.get("confirmed_vulnerability") is False
    assert sb.get("formal_finding_allowed") is False
    assert sb.get("production_safety_claimed") is False
    assert sb.get("synthetic_only") is True
    assert sb.get("report_not_formal_audit") is True


def test_redaction_policy_100_percent_coverage(exporter):
    """Test Data Redaction Policy against sensitive test vectors."""
    sample_payload = {
        "key": "sk-proj1234567890abcdef12345678",
        "bearer": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "secret": "password: TopSecret123!",
        "ip": "10.0.0.1",
        "email": "user@example.org",
        "db": "mysql://root:pass123@192.168.1.50:3306/db",
        "token": "secret-token-test12345"
    }

    redacted = exporter.apply_redaction_policy(sample_payload)

    assert "sk-proj" not in str(redacted)
    assert "<REDACTED_API_KEY>" in str(redacted)
    assert "TopSecret123!" not in str(redacted)
    assert "<REDACTED_PASSWORD>" in str(redacted)
    assert "10.0.0.1" not in str(redacted)
    assert "<REDACTED_IP>" in str(redacted)
    assert "user@example.org" not in str(redacted)
    assert "<REDACTED_EMAIL>" in str(redacted)
    assert "mysql://root:pass123" not in str(redacted)
    assert "<REDACTED_DB_URI>" in str(redacted)


def test_candidate_findings_compilation(exporter):
    """Test candidate findings assembly logic."""
    candidates = exporter.compile_candidate_findings()
    assert len(candidates) > 0

    for cand in candidates:
        assert cand["status"] == "candidate_finding"
        assert cand["confirmed_vulnerability"] is False
        assert cand["formal_finding_allowed"] is False
        assert cand["human_review_required"] is True


def test_export_html_self_contained(exporter, tmp_path):
    """Test offline HTML export without external CDN dependencies."""
    out_html = tmp_path / "test_report.html"
    exported_path = exporter.export_html(output_path=out_html)

    assert Path(exported_path).exists()
    content = Path(exported_path).read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert "<style>" in content
    assert "Safety Boundary Audit" in content

    # Assert 0 external http/https CDN links
    cdn_links = re.findall(r'(?:href|src)=["\'](http[s]?://[^"\']+)["\']', content)
    assert len(cdn_links) == 0


def test_export_markdown(exporter, tmp_path):
    """Test normalized Markdown report export."""
    out_md = tmp_path / "test_report.md"
    exported_path = exporter.export_markdown(output_path=out_md)

    assert Path(exported_path).exists()
    content = Path(exported_path).read_text(encoding="utf-8")

    assert "# 企业级 AI 安全评估报告" in content
    assert "Safety Boundary Audit" in content
    assert "`confirmed_vulnerability`" in content


def test_export_all_and_file_creation(exporter, tmp_path):
    """Test batch export_all function."""
    out_dir = tmp_path / "batch_out"
    res = exporter.export_all(output_dir=out_dir)

    assert "html" in res and Path(res["html"]).exists()
    assert "markdown" in res and Path(res["markdown"]).exists()
