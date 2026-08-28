#!/usr/bin/env python3
"""Tests for M16 registry entry in module_registry.yaml.

TDD: These tests verify the M16 entry has been updated to mvp_complete
with correct status fields and evidence list.
"""
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "capability_modules" / "module_registry.yaml"


def load_registry():
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


def find_m16(registry):
    for mod in registry.get("modules", []):
        if mod.get("module_id") == "M16":
            return mod
    return None


class TestM16RegistryEntry:
    def test_registry_loads(self):
        registry = load_registry()
        assert registry is not None, "Registry should load"

    def test_m16_exists(self):
        registry = load_registry()
        m16 = find_m16(registry)
        assert m16 is not None, "M16 module should exist in registry"

    def test_m16_current_status_mvp_complete(self):
        m16 = find_m16(load_registry())
        assert m16["current_status"] in ["mvp_complete", "full_corpus_complete"], (
            f"Expected current_status in ['mvp_complete', 'full_corpus_complete'], got {m16.get('current_status')}"
        )

    def test_m16_coverage_status_mvp_complete(self):
        m16 = find_m16(load_registry())
        coverage = m16.get("coverage", {})
        assert coverage.get("coverage_status") == "mvp_complete", (
            f"Expected coverage_status=mvp_complete, got {coverage.get('coverage_status')}"
        )

    def test_m16_implementation_status_mvp_done(self):
        m16 = find_m16(load_registry())
        coverage = m16.get("coverage", {})
        assert coverage.get("implementation_status") == "mvp_done", (
            f"Expected implementation_status=mvp_done, got {coverage.get('implementation_status')}"
        )

    def test_m16_evidence_has_at_least_7_entries(self):
        m16 = find_m16(load_registry())
        coverage = m16.get("coverage", {})
        evidence = coverage.get("evidence", [])
        assert len(evidence) >= 7, (
            f"Expected >= 7 evidence entries, got {len(evidence)}"
        )

    def test_m16_evidence_contains_playbook(self):
        m16 = find_m16(load_registry())
        evidence = m16["coverage"]["evidence"]
        assert any("playbook" in e for e in evidence), (
            "Evidence should contain playbook path"
        )

    def test_m16_evidence_contains_run_config(self):
        m16 = find_m16(load_registry())
        evidence = m16["coverage"]["evidence"]
        assert any("run_config" in e or "run config" in e for e in evidence), (
            "Evidence should contain run config path"
        )

    def test_m16_evidence_contains_result(self):
        m16 = find_m16(load_registry())
        evidence = m16["coverage"]["evidence"]
        assert any("result" in e for e in evidence), (
            "Evidence should contain result path"
        )

    def test_m16_evidence_contains_scorecard(self):
        m16 = find_m16(load_registry())
        evidence = m16["coverage"]["evidence"]
        assert any("scorecard" in e for e in evidence), (
            "Evidence should contain scorecard path"
        )

    def test_m16_evidence_contains_validate(self):
        m16 = find_m16(load_registry())
        evidence = m16["coverage"]["evidence"]
        assert any("validate" in e for e in evidence), (
            "Evidence should contain validate script path"
        )

    def test_m16_result_semantics_is_needs_human_review(self):
        m16 = find_m16(load_registry())
        assert m16.get("result_semantics") == "needs_human_review", (
            f"Expected result_semantics=needs_human_review, got {m16.get('result_semantics')}"
        )

    def test_m16_formal_finding_allowed_false(self):
        m16 = find_m16(load_registry())
        assert m16.get("formal_finding_allowed") is False, (
            "formal_finding_allowed should be false"
        )

    def test_m16_gaps_describes_mvp(self):
        m16 = find_m16(load_registry())
        gaps = m16["coverage"].get("gaps", [])
        assert len(gaps) > 0, "M16 should have gaps describing MVP scope"
        gaps_text = " ".join(gaps).lower()
        assert "mvp" in gaps_text or "10 entries" in gaps_text or "synthetic" in gaps_text, (
            "Gaps should describe MVP scope"
        )
