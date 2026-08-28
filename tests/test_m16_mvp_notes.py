"""TDD test: M16 Human Approval Gate MVP Notes validation."""

from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTES_PATH = ROOT / "docs" / "phase97a_m16_human_approval_gate_mvp_notes.md"


def _read_notes() -> str:
    assert NOTES_PATH.exists(), f"Notes file not found: {NOTES_PATH}"
    return NOTES_PATH.read_text(encoding="utf-8")


def test_notes_file_exists():
    """The MVP notes file must exist and be non-empty."""
    assert NOTES_PATH.is_file(), f"Notes file not found: {NOTES_PATH}"
    assert NOTES_PATH.stat().st_size > 0, "Notes file must not be empty"


def test_notes_title_and_metadata():
    """Notes must declare Phase 97A and M16 Human Approval Gate."""
    content = _read_notes()
    assert "Phase 97A" in content
    assert "M16" in content
    assert "Human Approval Gate" in content


def test_notes_assessment_mode():
    """Notes must specify adversarial_validation mode."""
    content = _read_notes()
    assert "adversarial_validation" in content


def test_notes_all_eight_attack_categories():
    """Notes must cover all 8 attack scenarios."""
    content = _read_notes()
    required_categories = [
        "approval_required_not_obtained",
        "approval_level_mismatch",
        "approval_bypass_social_engineering",
        "approval_role_impersonation",
        "approval_scope_mismatch",
        "multi_level_approval_incomplete",
        "approval_retrospective_claim",
        "approval_urgency_pressure",
    ]
    for cat in required_categories:
        assert cat in content, f"Scenario category '{cat}' missing from notes"


def test_notes_control_cases():
    """Notes must list both control baseline cases."""
    content = _read_notes()
    assert "control_approval_correctly_obtained" in content
    assert "control_no_approval_needed" in content


def test_notes_safety_boundaries():
    """Notes must document safety invariants and boolean flags."""
    content = _read_notes()
    assert "confirmed_vulnerability: false" in content
    assert "formal_finding_allowed: false" in content
    assert "production_safety_claimed: false" in content
    assert "controlled_replay_claimed: false" in content
    assert "<SIM_" in content or "SIM_" in content


def test_notes_results_metrics():
    """Notes must state key evaluation metrics."""
    content = _read_notes()
    assert "capability_value: high" in content
    assert "risk_level: low" in content
    assert "breakthrough_detected: 0" in content


def test_notes_module_relations():
    """Notes must define boundaries with M14, M15, M40, M41."""
    content = _read_notes()
    assert "M14" in content
    assert "M15" in content
    assert "M40" in content
    assert "M41" in content
    assert "M16" in content


def test_notes_non_goals():
    """Notes must state non-goals and candidate-only status."""
    content = _read_notes()
    assert "production safety" in content
    assert "candidate" in content

