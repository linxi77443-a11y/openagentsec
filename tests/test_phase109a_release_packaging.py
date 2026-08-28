#!/usr/bin/env python3
"""
tests/test_phase109a_release_packaging.py — Automated Pytest Suite for Phase-109A-RELEASE-002 (v5.0 Master).
Path: tests/test_phase109a_release_packaging.py

Task: Phase-109A-RELEASE-002
Task Name: 企业级 AI 安全评估平台 v5.0 Master 最终发布包封版、架构白皮书与规范归档
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.validate_phase109a_release_package import compute_sha256


class TestReleasePackageDeliverables:
    """Test release package files existence, non-emptiness, and key headers."""

    def test_all_deliverables_exist(self):
        deliverables = [
            ROOT / "docs/release_notes_v5_0.md",
            ROOT / "docs/enterprise_ai_security_platform_v5_0_architecture.md",
            ROOT / "docs/milestone_5_0_safety_and_compliance_charter.md",
            ROOT / "release_v5_0_manifest.yaml",
            ROOT / "checksums_v5_0.sha256",
            ROOT / "scripts/validate_phase109a_release_package.py",
            ROOT / "tests/test_phase109a_release_packaging.py",
            ROOT / "phase109a_release002_execution_summary.yaml",
            ROOT / "delivery.json",
        ]
        for f in deliverables:
            assert f.exists(), f"Deliverable missing: {f.name}"
            assert f.stat().st_size > 0, f"Deliverable is empty: {f.name}"

    def test_release_notes_v50_content(self):
        rn = ROOT / "docs/release_notes_v5_0.md"
        content = rn.read_text(encoding="utf-8")
        assert "企业级 AI 安全评估平台 v5.0 Master 终局发布说明" in content
        assert "八大核心架构支柱终局交付" in content
        assert "全系统 50 模块最终清单索引" in content
        assert "20 份红队行动报告全量审计收口清单" in content
        assert "终局安全边界声明" in content
        assert "v5.0-FINAL" in content

    def test_architecture_whitepaper_content(self):
        arch = ROOT / "docs/enterprise_ai_security_platform_v5_0_architecture.md"
        content = arch.read_text(encoding="utf-8")
        assert "全景系统架构说明与技术白皮书" in content
        assert "8 层全景架构蓝图" in content
        assert "多智能体协作编排层" in content
        assert "50 模块威胁能力引擎层" in content
        assert "前沿多模态与流式安全层" in content
        assert "单智能体全景纵深防御体系深度解析" in content
        assert "随机攻击传播动力学推演层" in content
        assert "8-Node 法定受控重放门禁层" in content
        assert "异常防御拦截子系统" in content

    def test_safety_charter_content(self):
        charter = ROOT / "docs/milestone_5_0_safety_and_compliance_charter.md"
        content = charter.read_text(encoding="utf-8")
        assert "终局安全边界与合规公约" in content
        assert "十大终局法定不可逾越公理" in content
        assert "安全边界标志位法定定义" in content
        assert "违规行为硬性拦截与异常处理协议" in content
        assert "CHARTER-v5.0-FINAL" in content


class TestReleaseManifest:
    """Test release manifest schema, pillars, and catalogs."""

    @pytest.fixture
    def manifest_data(self) -> Dict:
        path = ROOT / "release_v5_0_manifest.yaml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_manifest_metadata(self, manifest_data):
        meta = manifest_data.get("release_metadata", {})
        assert meta.get("release_id") == "REL-5.0-20260819"
        assert meta.get("release_version") == "v5.0"
        assert meta.get("release_status") == "RELEASE_SEALED"
        assert meta.get("task_id") == "Phase-109A-RELEASE-002"

    def test_manifest_pillars_all_pass(self, manifest_data):
        pillars = manifest_data.get("architectural_pillars", {})
        assert pillars["pillar_1_50_modules"]["status"] == "PASS"
        assert pillars["pillar_1_50_modules"]["total_modules"] == 50
        assert pillars["pillar_2_red_team_reports"]["status"] == "PASS"
        assert pillars["pillar_2_red_team_reports"]["total_reports_audited"] == 20
        assert pillars["pillar_3_60_extended_scenarios"]["status"] == "PASS"
        assert pillars["pillar_3_60_extended_scenarios"]["total_scenarios"] == 60
        assert pillars["pillar_3_60_extended_scenarios"]["breakthroughs"] == 0
        assert pillars["pillar_4_80_single_agent_scenarios"]["status"] == "PASS"
        assert pillars["pillar_4_80_single_agent_scenarios"]["total_scenarios"] == 80
        assert pillars["pillar_4_80_single_agent_scenarios"]["breakthroughs"] == 0
        assert pillars["pillar_4_1_unified_140_scenarios"]["status"] == "PASS"
        assert pillars["pillar_4_1_unified_140_scenarios"]["total_scenarios"] == 140
        assert pillars["pillar_5_propagation_dynamics"]["status"] == "PASS"
        assert pillars["pillar_6_gatekeeper_8node"]["status"] == "PASS"
        assert pillars["pillar_7_dashboard_and_reports"]["status"] == "PASS"
        assert pillars["pillar_8_known_bad_defenses"]["status"] == "PASS"
        assert pillars["pillar_8_known_bad_defenses"]["interception_rate"] == 1.0

    def test_manifest_50_modules_catalog(self, manifest_data):
        modules = manifest_data.get("modules_catalog", {})
        assert len(modules) == 50
        for i in range(1, 51):
            mod_id = f"M{i:02d}"
            assert mod_id in modules
            assert modules[mod_id]["status"] == "PASS"

    def test_manifest_20_reports_catalog(self, manifest_data):
        reports = manifest_data.get("red_team_reports_catalog", {})
        assert len(reports) == 20
        for i in range(1, 21):
            rep_id = f"RED-{i:03d}"
            assert rep_id in reports
            assert reports[rep_id]["status"] == "closed/judge_approved"
            assert reports[rep_id]["breakthroughs"] == 0

    def test_manifest_extended_scenarios_catalog(self, manifest_data):
        ext = manifest_data.get("extended_scenarios_catalog", {})
        assert "phase101_multimodal_sidechannel" in ext
        assert "phase102_wargame_adaptive_defense" in ext
        assert "phase103_stream_gateway_telemetry" in ext
        assert "phase105_cot_reasoning_reflection" in ext
        assert "phase106_tool_interpreter_sandbox" in ext
        assert "phase107_os_world_browser_guardrail" in ext
        assert "phase108_memory_semantic_fuzzing_dlp" in ext
        assert ext["phase101_multimodal_sidechannel"]["total_cases"] == 20
        assert ext["phase102_wargame_adaptive_defense"]["total_cases"] == 20
        assert ext["phase103_stream_gateway_telemetry"]["total_cases"] == 20
        assert ext["phase105_cot_reasoning_reflection"]["total_cases"] == 20
        assert ext["phase106_tool_interpreter_sandbox"]["total_cases"] == 20
        assert ext["phase107_os_world_browser_guardrail"]["total_cases"] == 20
        assert ext["phase108_memory_semantic_fuzzing_dlp"]["total_cases"] == 20


class TestSafetyBoundariesAndAssertions:
    """Test mandatory safety assertions and credential sanitization."""

    def test_negative_assertions_strictly_false(self):
        manifest_path = ROOT / "release_v5_0_manifest.yaml"
        with open(manifest_path, "r", encoding="utf-8") as f:
            m = yaml.safe_load(f)
        b = m.get("safety_declarations", {})
        assert b.get("confirmed_vulnerability") is False
        assert b.get("formal_finding_allowed") is False
        assert b.get("production_safety_claimed") is False
        assert b.get("controlled_replay_claimed") is False
        assert b.get("controlled_replay_execution_allowed") is False
        assert b.get("assessment_execution_performed") is False

    def test_positive_assertions_strictly_true(self):
        manifest_path = ROOT / "release_v5_0_manifest.yaml"
        with open(manifest_path, "r", encoding="utf-8") as f:
            m = yaml.safe_load(f)
        b = m.get("safety_declarations", {})
        assert b.get("synthetic_only") is True
        assert b.get("fake_runtime_only") is True
        assert b.get("requires_human_review") is True
        assert b.get("all_findings_are_candidate") is True
        assert b.get("red_team_engine_not_executable") is True
        assert b.get("dashboard_not_execution_interface") is True
        assert b.get("theory_model_is_not_detection_rule") is True
        assert b.get("non_retroactivity_guarantee") is True
        assert b.get("zero_production_penetration") is True
        assert b.get("zero_formal_disconnect") is True

    def test_zero_real_credentials_in_core_assets(self):
        test_files = [
            ROOT / "docs/release_notes_v5_0.md",
            ROOT / "docs/enterprise_ai_security_platform_v5_0_architecture.md",
            ROOT / "docs/milestone_5_0_safety_and_compliance_charter.md",
            ROOT / "release_v5_0_manifest.yaml",
        ]
        for f in test_files:
            content = f.read_text(encoding="utf-8")
            assert "sk-proj-" not in content
            assert "AKIA" not in content
            assert "-----BEGIN RSA PRIVATE KEY-----" not in content


class TestChecksumsIntegrity:
    """Test SHA-256 integrity against checksums_v5_0.sha256."""

    def test_all_checksums_match(self):
        checksums_file = ROOT / "checksums_v5_0.sha256"
        assert checksums_file.exists()
        with open(checksums_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith("#")]

        assert len(lines) >= 10
        for line in lines:
            parts = re.split(r"\s+", line, maxsplit=1)
            assert len(parts) == 2
            expected_hash, rel_path = parts[0], parts[1]
            target_path = ROOT / rel_path
            assert target_path.exists(), f"File in checksums does not exist: {rel_path}"
            actual_hash = compute_sha256(target_path)
            assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}"


class TestReleaseValidatorExecution:
    """Test that the standalone validator script passes with returncode 0."""

    def test_validator_script_executes_pass(self):
        from scripts.validate_phase109a_release_package import main as validator_main
        ret = validator_main()
        assert ret == 0
