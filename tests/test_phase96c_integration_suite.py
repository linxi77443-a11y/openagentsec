"""
PyTest Unit & Integration Test Suite for Phase 96C (Stage 3 Integration Suite)
Path: tests/test_phase96c_integration_suite.py

Verifies end-to-end integration across:
BatchRunner Checkpoint -> AssessmentDashboardAPI -> ReportExporter HTML/Markdown Export
with zero memory leak and strict safety boundary enforcement.
"""

import re
import gc
import json
import tracemalloc
import pytest
from pathlib import Path

from core.batch_runner import CheckpointManager
from core.dashboard_api import AssessmentDashboardAPI, SAFE_BOUNDARIES
from core.report_exporter import ReportExporter, REPORT_SAFE_BOUNDARIES


@pytest.fixture
def root_dir():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def checkpoint_path(root_dir):
    return root_dir / "artifacts" / "batch_checkpoints" / "phase96c_checkpoint.json"


@pytest.fixture
def dashboard_api(root_dir, checkpoint_path):
    return AssessmentDashboardAPI(root_dir=root_dir, checkpoint_file=checkpoint_path)


@pytest.fixture
def report_exporter(root_dir, dashboard_api):
    return ReportExporter(root_dir=root_dir, dashboard_api=dashboard_api)


def test_batch_checkpoint_loading_and_integrity(checkpoint_path):
    """Test loading and integrity of Phase 96C Checkpoint file."""
    assert checkpoint_path.exists(), "phase96c_checkpoint.json must exist"

    ckpt_mgr = CheckpointManager(checkpoint_path)
    data = ckpt_mgr.load_checkpoint()

    assert data is not None
    assert data.get("phase") == "Phase-96C"
    assert data.get("total_tasks") == 750
    assert data.get("completed_count") == 750
    assert data.get("status") == "completed"

    sb = data.get("safety_boundaries", {})
    assert sb.get("confirmed_vulnerability") is False
    assert sb.get("formal_finding_allowed") is False
    assert sb.get("production_safety_claimed") is False
    assert sb.get("synthetic_only") is True
    assert sb.get("dashboard_not_execution_interface") is True


def test_e2e_pipeline_checkpoint_to_dashboard_to_exporter(dashboard_api, report_exporter, tmp_path):
    """Test full end-to-end flow from Checkpoint to Dashboard API to Report Exporter."""
    # 1. API check
    summary = dashboard_api.get_summary()
    assert summary["platform_metrics"]["total_simulation_runs"] == 750

    # 2. Exporter check
    out_html = tmp_path / "e2e_report.html"
    out_md = tmp_path / "e2e_report.md"

    exported_html = report_exporter.export_html(output_path=out_html)
    exported_md = report_exporter.export_markdown(output_path=out_md)

    assert Path(exported_html).exists() and Path(exported_html).stat().st_size > 0
    assert Path(exported_md).exists() and Path(exported_md).stat().st_size > 0


def test_all_four_views_consistency(dashboard_api):
    """Test consistency and schema compliance across all 4 visual dashboard API views."""
    heatmap = dashboard_api.get_coverage_heatmap()
    chains = dashboard_api.get_attack_chain_propagation()
    timeline = dashboard_api.get_defense_degradation_timeline()
    redteam = dashboard_api.get_red_team_panel_summary()

    assert heatmap["view_id"] == "coverage_heatmap"
    assert len(heatmap["items"]) > 0
    assert heatmap["read_only"] is True

    assert chains["view_id"] == "attack_chain_propagation"
    assert len(chains["chains"]) > 0
    assert chains["read_only"] is True

    assert timeline["view_id"] == "defense_degradation_timeline"
    assert len(timeline["timeline_nodes"]) > 0
    assert timeline["read_only"] is True

    assert redteam["view_id"] == "red_team_panel_summary"
    assert len(redteam["available_attack_profiles"]) > 0
    assert redteam["read_only"] is True


def test_zero_memory_leak_over_iterations(report_exporter, tmp_path):
    """Test zero memory leak / memory boundedness over multiple report generation cycles."""
    gc.collect()
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()

    for i in range(5):
        h = tmp_path / f"test_{i}.html"
        m = tmp_path / f"test_{i}.md"
        report_exporter.export_html(output_path=h)
        report_exporter.export_markdown(output_path=m)
        if h.exists():
            h.unlink()
        if m.exists():
            m.unlink()

    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    diff_kb = sum(stat.size_diff for stat in top_stats) / 1024.0

    assert diff_kb < 2048.0, f"Memory heap growth {diff_kb:.2f} KB exceeded 2048 KB limit"


def test_safety_boundary_compliance_across_pipeline(dashboard_api, report_exporter):
    """Test that safety boundary assertions are 100% compliant across checkpoint, API, and exporter context."""
    # API context
    api_summary = dashboard_api.get_summary()
    api_sb = api_summary["safety_boundaries"]
    assert api_sb["confirmed_vulnerability"] is False
    assert api_sb["formal_finding_allowed"] is False
    assert api_sb["production_safety_claimed"] is False
    assert api_sb["synthetic_only"] is True
    assert api_sb["dashboard_not_execution_interface"] is True

    # Exporter context
    report_ctx = report_exporter.get_report_context()
    exporter_sb = report_ctx["safety_boundaries"]
    assert exporter_sb["confirmed_vulnerability"] is False
    assert exporter_sb["formal_finding_allowed"] is False
    assert exporter_sb["production_safety_claimed"] is False
    assert exporter_sb["synthetic_only"] is True
    assert exporter_sb["report_not_formal_audit"] is True

    # Candidate findings safety check
    candidates = report_ctx["candidate_findings"]
    for c in candidates:
        assert c["confirmed_vulnerability"] is False
        assert c["status"] == "candidate_finding"


def test_redaction_policy_end_to_end(report_exporter):
    """Test Data Redaction Policy against sensitive test vectors."""
    payload = {
        "api_key": "sk-proj1234567890abcdef123456",
        "auth": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "pwd": "password: TopSecretKey!2026",
        "ip": "10.0.0.15",
        "mail": "admin@subdomain.internal",
        "db": "mysql://user:pass@192.168.1.1:3306/db"
    }

    redacted = report_exporter.apply_redaction_policy(payload)

    assert "sk-proj" not in str(redacted)
    assert "<REDACTED_API_KEY>" in str(redacted)
    assert "TopSecretKey!2026" not in str(redacted)
    assert "<REDACTED_PASSWORD>" in str(redacted)
    assert "10.0.0.15" not in str(redacted)
    assert "<REDACTED_IP>" in str(redacted)
    assert "admin@subdomain.internal" not in str(redacted)
    assert "<REDACTED_EMAIL>" in str(redacted)
    assert "mysql://user:pass" not in str(redacted)
    assert "<REDACTED_DB_URI>" in str(redacted)


def test_offline_html_zero_cdn_dependencies(report_exporter, tmp_path):
    """Test that generated HTML report is offline self-contained with 0 external CDN links."""
    out_html = tmp_path / "offline_report.html"
    exported_path = report_exporter.export_html(output_path=out_html)

    content = Path(exported_path).read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert "<style>" in content
    assert "metrics-grid" in content

    cdn_links = re.findall(r'(?:href|src)=["\'](http[s]?://[^"\']+)["\']', content)
    assert len(cdn_links) == 0, f"Found external CDN dependencies: {cdn_links}"


def test_dashboard_read_only_non_execution_assertion(dashboard_api):
    """Test that dashboard API views strictly assert read_only=True and non-execution interface."""
    views = [
        dashboard_api.get_coverage_heatmap(),
        dashboard_api.get_attack_chain_propagation(),
        dashboard_api.get_defense_degradation_timeline(),
        dashboard_api.get_red_team_panel_summary()
    ]

    for v in views:
        assert v.get("read_only") is True
        sb = v.get("safety_boundaries", {})
        assert sb.get("dashboard_not_execution_interface") is True
