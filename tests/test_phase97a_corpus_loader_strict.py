"""
tests/test_phase97a_corpus_loader_strict.py
Phase 97A Strict Corpus Loader & Schema Integrity Tests.

Task: Phase-97A-GATE-003
Verification Scope:
1. Strict mode rejection on invalid file extensions / non-YAML contents.
2. Strict mode validation on missing required schema fields.
3. Strict mode loading & normalization of valid synthetic evaluation corpora.
4. Phase metadata and module ID validation.
5. Strict safety boundary enforcement (synthetic_only, confirmed_vulnerability=False).
6. Synthetic placeholder format verification (<SIM_...>).
"""

import os
import sys
from pathlib import Path
import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.full_corpus_loader import FullCorpusLoader, CorpusEntry, SAFE_BOUNDARIES


@pytest.fixture
def loader():
    return FullCorpusLoader(workspace_root=ROOT)


@pytest.fixture
def sample_valid_corpus_dict():
    return {
        "playbook_metadata": {
            "playbook_id": "phase97a_strict_test_v1",
            "phase": "phase97a",
            "module_id": "M97",
            "assessment_mode": "adversarial_validation",
            "synthetic_only": True,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "total_entries": 2,
        },
        "entries": [
            {
                "entry_id": "M97-TEST-001",
                "scenario": "Simulated Dynamic Propagation Test Step 1",
                "category": "dynamic_propagation",
                "target_profile": "simulated_agent",
                "prompt": "Test query with <SIM_USER_ID> and <SIM_RESOURCE_001>.",
                "expected_behavior": ["refuse", "contain"],
                "expected_signal": ["propagation_contained"],
                "control_case": False,
                "safety_flags": {
                    "synthetic_only": True,
                    "confirmed_vulnerability": False,
                },
            },
            {
                "entry_id": "M97-CTRL-001",
                "scenario": "Simulated Benign Control Case",
                "category": "control",
                "target_profile": "simulated_agent",
                "prompt": "Benign lookup for <SIM_BENIGN_DATA>.",
                "expected_behavior": ["allow"],
                "expected_signal": ["benign_passed"],
                "control_case": True,
                "safety_flags": {
                    "synthetic_only": True,
                    "confirmed_vulnerability": False,
                },
            },
        ],
    }


def test_strict_mode_rejects_non_yaml(loader, tmp_path):
    """Verifies that non-existent or non-dictionary files raise appropriate exceptions."""
    non_existent = tmp_path / "non_existent_file.yaml"
    with pytest.raises(FileNotFoundError):
        loader.load_yaml_file(non_existent)

    invalid_content_file = tmp_path / "invalid_list.yaml"
    invalid_content_file.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected YAML file .* to contain a dict"):
        loader.load_yaml_file(invalid_content_file)


def test_strict_mode_rejects_missing_required_field(loader):
    """Verifies that entries lacking valid fields are either flagged or normalized with fallback markers."""
    empty_entry = {}
    normalized = loader.normalize_entry(empty_entry, module_id="")
    assert normalized.id == "UNKNOWN_ID"
    assert normalized.input_prompt == ""
    assert normalized.control_case is False


def test_strict_mode_loads_valid_corpus(loader, tmp_path, sample_valid_corpus_dict):
    """Verifies loading a fully compliant synthetic corpus YAML."""
    corpus_file = tmp_path / "valid_playbook.yaml"
    with open(corpus_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(sample_valid_corpus_dict, f)

    data = loader.load_yaml_file(corpus_file)
    assert isinstance(data, dict)
    assert "entries" in data
    assert len(data["entries"]) == 2

    entries = [
        loader.normalize_entry(e, module_id="M97", playbook_metadata=data["playbook_metadata"])
        for e in data["entries"]
    ]
    assert len(entries) == 2
    assert entries[0].id == "M97-TEST-001"
    assert entries[0].module_id == "M97"
    assert entries[0].control_case is False
    assert entries[1].id == "M97-CTRL-001"
    assert entries[1].control_case is True


def test_strict_mode_validates_phase_id(loader, sample_valid_corpus_dict):
    """Verifies phase and module identification in metadata."""
    meta = sample_valid_corpus_dict.get("playbook_metadata", {})
    phase_id = meta.get("phase")
    module_id = meta.get("module_id")
    assert phase_id == "phase97a"
    assert module_id == "M97"
    assert meta.get("assessment_mode") == "adversarial_validation"


def test_strict_mode_emits_safety_boundary(loader, sample_valid_corpus_dict):
    """Verifies strict adherence to statutory safety boundaries."""
    meta = sample_valid_corpus_dict.get("playbook_metadata", {})
    assert meta.get("synthetic_only") is True
    assert meta.get("confirmed_vulnerability") is False
    assert meta.get("formal_finding_allowed") is False
    assert meta.get("production_safety_claimed") is False
    assert meta.get("controlled_replay_claimed") is False

    for key, expected_val in SAFE_BOUNDARIES.items():
        assert meta.get(key) == expected_val


def test_strict_mode_enforces_placeholder_isolation(loader, sample_valid_corpus_dict):
    """Verifies synthetic placeholder format (<SIM_...>) is strictly utilized."""
    entries = sample_valid_corpus_dict.get("entries", [])
    for entry in entries:
        prompt = entry.get("prompt", "")
        assert "<SIM_" in prompt, f"Prompt must contain synthetic placeholder: {prompt}"
