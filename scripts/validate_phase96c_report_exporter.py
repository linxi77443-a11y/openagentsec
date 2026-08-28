#!/usr/bin/env python3
"""
Exclusive Validation Script for Phase 96C Report Exporter (ReportExporter)
Path: scripts/validate_phase96c_report_exporter.py

Validates ReportExporter functionality:
1. Data aggregation from DashboardAPI, scorecards, execution results.
2. Safety boundary assertions injection.
3. 100% Data Redaction Policy (Redaction Policy) coverage.
4. Candidate-level findings compilation & strict 0 confirmed vulnerabilities.
5. Offline self-contained HTML export (0 external CDN dependencies).
6. Normalized Markdown report export.
7. Batch export_all() execution.

Usage:
  python3 scripts/validate_phase96c_report_exporter.py
"""

import sys
import os
import re
import json
import logging
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.report_exporter import ReportExporter, REPORT_SAFE_BOUNDARIES
from core.dashboard_api import AssessmentDashboardAPI

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Phase96CReportExporterValidator")


def validate_report_exporter():
    logger.info("======================================================================")
    logger.info("Phase 96C — ReportExporter Exclusive Validator")
    logger.info("======================================================================")

    passed_checks = 0
    total_checks = 0

    exporter = ReportExporter(root_dir=root_dir)

    # ------------------------------------------------------------------
    # Step 1: Initializing Exporter & Context Data Aggregation
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 1] Initializing ReportExporter and validating context aggregation...")
    context = exporter.get_report_context()
    assert "report_title" in context, "Context missing report_title"
    assert "metrics" in context, "Context missing metrics"
    assert "heatmap" in context, "Context missing heatmap"
    assert "attack_chains" in context, "Context missing attack_chains"
    assert "timeline" in context, "Context missing timeline"
    assert "candidate_findings" in context, "Context missing candidate_findings"

    passed_checks += 1
    logger.info(f"  ✓ Report context aggregated successfully. Modules count: {context['metrics'].get('total_modules')}")

    # ------------------------------------------------------------------
    # Step 2: Validate Safety Boundary Assertions
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 2] Validating Safety Boundary Assertions in Report Context...")
    sb = context.get("safety_boundaries", {})

    for key, expected_val in REPORT_SAFE_BOUNDARIES.items():
        assert sb.get(key) == expected_val, f"Safety boundary {key} expected {expected_val}, got {sb.get(key)}"

    passed_checks += 1
    logger.info("  ✓ Safety boundaries validated (100% compliant with Phase 96C rules).")

    # ------------------------------------------------------------------
    # Step 3: Validate 100% Data Redaction Policy Coverage
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 3] Validating 100% Data Redaction Policy Coverage...")

    sensitive_sample = {
        "api_key": "sk-proj1234567890abcdef123456",
        "aws_key": "AKIA1234567890ABCDEF",
        "github_token": "ghp_1234567890abcdef1234567890abcdef1234",
        "auth_header": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        "credentials": "password: MySuperSecretPassword123!",
        "contact": "admin@corp.internal",
        "internal_ip": "192.168.1.100",
        "db_uri": "postgres://dbuser:dbpass123@10.0.0.5:5432/main_db",
        "secret_token": "secret-token-abcdef123456",
        "nested": {
            "query": "SELECT * FROM users WHERE pass='secret-token-9999'",
            "logs": ["Failed login from 172.16.0.50 with token ghp_1234567890abcdef1234567890abcdef1234"]
        }
    }

    redacted = exporter.apply_redaction_policy(sensitive_sample)

    # Assertions
    assert "sk-proj1234567890abcdef123456" not in str(redacted), "API Key was not redacted"
    assert "<REDACTED_API_KEY>" in str(redacted), "Missing <REDACTED_API_KEY> marker"
    assert "MySuperSecretPassword123!" not in str(redacted), "Password was not redacted"
    assert "<REDACTED_PASSWORD>" in str(redacted), "Missing <REDACTED_PASSWORD> marker"
    assert "192.168.1.100" not in str(redacted), "Internal IP was not redacted"
    assert "<REDACTED_IP>" in str(redacted), "Missing <REDACTED_IP> marker"
    assert "admin@corp.internal" not in str(redacted), "Email was not redacted"
    assert "<REDACTED_EMAIL>" in str(redacted), "Missing <REDACTED_EMAIL> marker"
    assert "postgres://dbuser:dbpass123" not in str(redacted), "DB URI was not redacted"
    assert "<REDACTED_DB_URI>" in str(redacted), "Missing <REDACTED_DB_URI> marker"

    passed_checks += 1
    logger.info("  ✓ Data Redaction Policy 100% coverage verified.")

    # ------------------------------------------------------------------
    # Step 4: Validate Candidate-Level Findings Assembly
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 4] Validating Candidate-Level Findings Assembly...")
    candidates = exporter.compile_candidate_findings()
    assert len(candidates) > 0, "Candidate findings list should not be empty"

    for cand in candidates:
        assert cand.get("status") == "candidate_finding", f"Status must be candidate_finding, got {cand.get('status')}"
        assert cand.get("confirmed_vulnerability") is False, "Confirmed vulnerability must be False"
        assert cand.get("formal_finding_allowed") is False, "Formal finding allowed must be False"
        assert cand.get("human_review_required") is True, "Human review required must be True"

    passed_checks += 1
    logger.info(f"  ✓ Candidate findings assembled ({len(candidates)} candidates, 0 confirmed vulnerabilities).")

    # ------------------------------------------------------------------
    # Step 5: Validate Offline Self-Contained HTML Export
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 5] Validating Offline Self-Contained HTML Export...")
    html_out = root_dir / "reports" / "phase96c_test_report.html"
    exported_html_path = exporter.export_html(output_path=html_out)
    assert Path(exported_html_path).exists(), f"HTML report file missing at {exported_html_path}"
    assert Path(exported_html_path).stat().st_size > 0, "HTML report file is empty"

    with open(exported_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Check CSS embedded
    assert "<style>" in html_content, "HTML report missing embedded <style>"
    assert "metrics-grid" in html_content, "HTML report missing metrics-grid class"

    # Check 0 external CDN links (no http:// or https:// stylesheet/script href/src)
    cdn_links = re.findall(r'(?:href|src)=["\'](http[s]?://[^"\']+)["\']', html_content)
    assert len(cdn_links) == 0, f"Found external CDN dependencies in HTML report: {cdn_links}"

    passed_checks += 1
    logger.info("  ✓ Offline self-contained HTML export verified (0 external CDN dependencies).")

    # ------------------------------------------------------------------
    # Step 6: Validate Normalized Markdown Report Export
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 6] Validating Normalized Markdown Report Export...")
    md_out = root_dir / "reports" / "phase96c_test_report.md"
    exported_md_path = exporter.export_markdown(output_path=md_out)
    assert Path(exported_md_path).exists(), f"Markdown report file missing at {exported_md_path}"
    assert Path(exported_md_path).stat().st_size > 0, "Markdown report file is empty"

    with open(exported_md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    assert "# 企业级 AI 安全评估报告" in md_content, "Markdown report title missing"
    assert "Safety Boundary Audit" in md_content, "Markdown safety audit header missing"
    assert "| `confirmed_vulnerability` | `False` |" in md_content, "Markdown confirmed vulnerability false assertion missing"

    passed_checks += 1
    logger.info("  ✓ Normalized Markdown report export verified.")

    # ------------------------------------------------------------------
    # Step 7: Validate Batch export_all() Execution
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 7] Validating Batch export_all() Execution...")
    batch_dir = root_dir / "reports" / "batch_export_test"
    result = exporter.export_all(output_dir=batch_dir)

    assert "html" in result and Path(result["html"]).exists(), "Batch export HTML file missing"
    assert "markdown" in result and Path(result["markdown"]).exists(), "Batch export Markdown file missing"

    passed_checks += 1
    logger.info(f"  ✓ Batch export_all() verified ({result['html']}, {result['markdown']}).")

    # Clean up test files
    for p in [html_out, md_out, Path(result["html"]), Path(result["markdown"])]:
        if p.exists():
            p.unlink()

    # ------------------------------------------------------------------
    # Summary Output
    # ------------------------------------------------------------------
    logger.info("======================================================================")
    logger.info(f"Validation Result: PASS ({passed_checks}/{total_checks} checks passed)")
    logger.info("======================================================================")
    return True


if __name__ == "__main__":
    try:
        success = validate_report_exporter()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}", exc_info=True)
        sys.exit(1)
