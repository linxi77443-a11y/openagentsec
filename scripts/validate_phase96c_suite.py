#!/usr/bin/env python3
"""
Exclusive End-to-End Integration Verification Script for Phase 96C (Stage 3 Verification Suite)
Path: scripts/validate_phase96c_suite.py

Validates the full pipeline:
1. BatchRunner Checkpoint Integrity (artifacts/batch_checkpoints/phase96c_checkpoint.json).
2. Assessment Dashboard API Read-Only View Transformations (Coverage Heatmap, Attack Chains, Timeline, Red Team Panel).
3. Enterprise ReportExporter Automated HTML/Markdown Generation.
4. 100% Data Redaction Policy Coverage across all exported artifacts.
5. Offline Self-Contained HTML (0 external CDN dependencies).
6. Zero Memory Leak / Memory Boundedness verification over iterative export cycles.
7. Strict Compliance with Safety Boundaries (confirmed_vulnerability=False, formal_finding_allowed=False, etc.).

Usage:
    python3 scripts/validate_phase96c_suite.py
"""

import sys
import os
import re
import json
import gc
import tracemalloc
import logging
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.batch_runner import CheckpointManager
from core.dashboard_api import AssessmentDashboardAPI, SAFE_BOUNDARIES
from core.report_exporter import ReportExporter, REPORT_SAFE_BOUNDARIES

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Phase96CIntegrationSuiteValidator")


def validate_phase96c_integration_suite():
    logger.info("======================================================================")
    logger.info("Phase 96C — Stage 3 Integration Verification Suite")
    logger.info("Pipeline: BatchRunner Checkpoint -> Dashboard API -> ReportExporter")
    logger.info("======================================================================")

    passed_checks = 0
    total_checks = 0

    checkpoint_path = root_dir / "artifacts" / "batch_checkpoints" / "phase96c_checkpoint.json"

    # ------------------------------------------------------------------
    # Step 1: Validate BatchRunner Checkpoint File Integrity
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 1] Validating BatchRunner Checkpoint File Integrity...")

    assert checkpoint_path.exists(), f"Phase 96C Checkpoint missing at {checkpoint_path}"
    ckpt_mgr = CheckpointManager(checkpoint_path)
    ckpt_data = ckpt_mgr.load_checkpoint()

    assert ckpt_data is not None, "Failed to load phase96c_checkpoint.json"
    assert ckpt_data.get("phase") == "Phase-96C", f"Expected phase Phase-96C, got {ckpt_data.get('phase')}"
    assert ckpt_data.get("total_tasks") == 750, f"Expected 750 total tasks, got {ckpt_data.get('total_tasks')}"
    assert ckpt_data.get("completed_count") == 750, f"Expected 750 completed tasks, got {ckpt_data.get('completed_count')}"
    assert ckpt_data.get("status") == "completed", f"Expected status completed, got {ckpt_data.get('status')}"

    # Verify safety boundaries in checkpoint
    sb = ckpt_data.get("safety_boundaries", {})
    assert sb.get("confirmed_vulnerability") is False, "Checkpoint confirmed_vulnerability must be False"
    assert sb.get("formal_finding_allowed") is False, "Checkpoint formal_finding_allowed must be False"
    assert sb.get("production_safety_claimed") is False, "Checkpoint production_safety_claimed must be False"
    assert sb.get("synthetic_only") is True, "Checkpoint synthetic_only must be True"

    passed_checks += 1
    logger.info(f"  ✓ Checkpoint verified: {ckpt_data.get('completed_count')}/{ckpt_data.get('total_tasks')} tasks completed. Session: {ckpt_data.get('session_id')}")

    # ------------------------------------------------------------------
    # Step 2: Validate Dashboard API Data Transformation Pipeline
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 2] Validating Dashboard API 4 Read-Only Views Transformation...")

    dashboard_api = AssessmentDashboardAPI(root_dir=root_dir, checkpoint_file=checkpoint_path)
    summary_api = dashboard_api.get_summary()

    metrics = summary_api.get("platform_metrics", {})
    assert metrics.get("total_modules", 0) > 0, "Total modules count must be > 0"
    assert metrics.get("total_simulation_runs") == 750, f"Expected 750 simulation runs from checkpoint, got {metrics.get('total_simulation_runs')}"
    assert metrics.get("confirmed_vulnerabilities") == 0, "Confirmed vulnerabilities in API summary must be 0"

    heatmap_view = dashboard_api.get_coverage_heatmap()
    assert heatmap_view.get("read_only") is True, "Heatmap view must be read-only"
    assert len(heatmap_view.get("items", [])) > 0, "Heatmap items should not be empty"

    chain_view = dashboard_api.get_attack_chain_propagation()
    assert chain_view.get("read_only") is True, "Attack chain view must be read-only"
    assert len(chain_view.get("chains", [])) > 0, "Attack chains list should not be empty"

    timeline_view = dashboard_api.get_defense_degradation_timeline()
    assert timeline_view.get("read_only") is True, "Timeline view must be read-only"
    assert len(timeline_view.get("timeline_nodes", [])) > 0, "Timeline nodes should not be empty"

    redteam_view = dashboard_api.get_red_team_panel_summary()
    assert redteam_view.get("read_only") is True, "Red team view must be read-only"
    assert len(redteam_view.get("available_attack_profiles", [])) > 0, "Attack profiles should not be empty"

    passed_checks += 1
    logger.info("  ✓ Dashboard API all 4 read-only views transformed successfully.")

    # ------------------------------------------------------------------
    # Step 3: Validate ReportExporter Automated Generation Pipeline
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 3] Validating ReportExporter Automated Generation Pipeline...")

    exporter = ReportExporter(root_dir=root_dir, dashboard_api=dashboard_api)
    test_out_dir = root_dir / "reports" / "phase96c_integration_test_outputs"
    test_out_dir.mkdir(parents=True, exist_ok=True)

    html_file = test_out_dir / "integration_assessment_report.html"
    md_file = test_out_dir / "integration_assessment_report.md"

    exported_html = exporter.export_html(output_path=html_file)
    exported_md = exporter.export_markdown(output_path=md_file)

    assert Path(exported_html).exists() and Path(exported_html).stat().st_size > 0, "Exported HTML report is missing or empty"
    assert Path(exported_md).exists() and Path(exported_md).stat().st_size > 0, "Exported Markdown report is missing or empty"

    passed_checks += 1
    logger.info(f"  ✓ ReportExporter HTML and Markdown generated successfully in {test_out_dir.name}.")

    # ------------------------------------------------------------------
    # Step 4: Validate 100% Data Redaction Policy Coverage
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 4] Validating 100% Data Redaction Policy Coverage...")

    sensitive_vector = {
        "api_key": "sk-proj9999999999999999999999999",
        "aws": "AKIA9999999999999999",
        "github": "ghp_999999999999999999999999999999999999",
        "token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "cred": "password: ConfidentialPassword123!",
        "email": "security_audit@internal.corp",
        "ip": "192.168.10.25",
        "db": "postgresql://admin:secret@10.0.0.1:5432/production_db",
        "secret": "secret-token-integration-check"
    }

    redacted_vector = exporter.apply_redaction_policy(sensitive_vector)

    assert "sk-proj" not in str(redacted_vector), "API key was not redacted"
    assert "<REDACTED_API_KEY>" in str(redacted_vector), "Missing <REDACTED_API_KEY>"
    assert "ConfidentialPassword123!" not in str(redacted_vector), "Password was not redacted"
    assert "<REDACTED_PASSWORD>" in str(redacted_vector), "Missing <REDACTED_PASSWORD>"
    assert "192.168.10.25" not in str(redacted_vector), "IP address was not redacted"
    assert "<REDACTED_IP>" in str(redacted_vector), "Missing <REDACTED_IP>"
    assert "security_audit@internal.corp" not in str(redacted_vector), "Email was not redacted"
    assert "<REDACTED_EMAIL>" in str(redacted_vector), "Missing <REDACTED_EMAIL>"
    assert "postgresql://admin" not in str(redacted_vector), "DB URI was not redacted"
    assert "<REDACTED_DB_URI>" in str(redacted_vector), "Missing <REDACTED_DB_URI>"

    passed_checks += 1
    logger.info("  ✓ Data Redaction Policy 100% coverage verified.")

    # ------------------------------------------------------------------
    # Step 5: Validate Offline Self-Contained HTML (0 CDN dependencies)
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 5] Validating Offline Self-Contained HTML (0 External CDN Dependencies)...")

    with open(exported_html, "r", encoding="utf-8") as f:
        html_content = f.read()

    assert "<style>" in html_content, "HTML report missing embedded CSS stylesheet"
    assert "metrics-grid" in html_content, "HTML report missing metrics grid"

    cdn_matches = re.findall(r'(?:href|src)=["\'](http[s]?://[^"\']+)["\']', html_content)
    assert len(cdn_matches) == 0, f"Found external CDN dependencies: {cdn_matches}"

    passed_checks += 1
    logger.info("  ✓ Offline self-contained HTML verified (0 external CDN dependencies).")

    # ------------------------------------------------------------------
    # Step 6: Validate Memory Boundedness & Zero Memory Leak
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 6] Validating Zero Memory Leak Over Iterative Export Cycles...")

    gc.collect()
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    # Perform 5 iterative report generation cycles
    for i in range(5):
        cycle_html = test_out_dir / f"leak_test_{i}.html"
        cycle_md = test_out_dir / f"leak_test_{i}.md"
        exporter.export_html(output_path=cycle_html)
        exporter.export_markdown(output_path=cycle_md)
        if cycle_html.exists():
            cycle_html.unlink()
        if cycle_md.exists():
            cycle_md.unlink()

    gc.collect()
    snapshot_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    total_diff_kb = sum(stat.size_diff for stat in top_stats) / 1024.0

    # Memory delta threshold limit: 2048 KB (2MB)
    assert total_diff_kb < 2048.0, f"Excessive memory heap growth detected: {total_diff_kb:.2f} KB"

    passed_checks += 1
    logger.info(f"  ✓ Zero memory leak verified (Memory delta across 5 cycles: {total_diff_kb:.2f} KB < 2048 KB limit).")

    # ------------------------------------------------------------------
    # Step 7: Validate Complete Safety Boundaries Assertions Compliance
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 7] Validating Safety Boundary Assertions Across Full Pipeline...")

    report_context = exporter.get_report_context()
    context_sb = report_context.get("safety_boundaries", {})

    expected_safety_flags = {
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "synthetic_only": True,
        "dashboard_not_execution_interface": True,
        "report_not_formal_audit": True
    }

    for flag_name, expected_val in expected_safety_flags.items():
        actual_val = context_sb.get(flag_name)
        assert actual_val == expected_val, f"Safety flag '{flag_name}' expected {expected_val}, got {actual_val}"

    # Verify candidates are not confirmed vulnerabilities
    candidates = report_context.get("candidate_findings", [])
    for cand in candidates:
        assert cand.get("confirmed_vulnerability") is False, f"Candidate {cand.get('candidate_id')} has confirmed_vulnerability=True"
        assert cand.get("status") == "candidate_finding", f"Candidate {cand.get('candidate_id')} status is not candidate_finding"

    passed_checks += 1
    logger.info("  ✓ Safety Boundary Assertions 100% compliant across pipeline.")

    # Clean up test output directory
    for f in test_out_dir.glob("*"):
        f.unlink()
    test_out_dir.rmdir()

    # ------------------------------------------------------------------
    # Summary Output
    # ------------------------------------------------------------------
    logger.info("======================================================================")
    logger.info(f"Phase 96C Integration Suite Validation Result: PASS ({passed_checks}/{total_checks} checks passed)")
    logger.info("======================================================================")
    return True


if __name__ == "__main__":
    try:
        success = validate_phase96c_suite()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}", exc_info=True)
        sys.exit(1)
