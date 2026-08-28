#!/usr/bin/env python3
"""
Phase 96B CorpusLoader Validation & Regression Verification Script
Path: scripts/validate_phase96b_corpus_loader.py

Verification Objectives:
1. Auto-discover all 10 75-entry full corpus suites in adversarial_playbooks/.
2. Load and dynamically normalize 750 entries into CorpusEntry objects.
3. Validate 100% format reconciliation (格式对账) and safety boundary compliance.
4. Verify dynamic context/payload rendering across target adapters (OpenAI, REST, MCP, Generic).
5. Verify entry querying, filtering, and slicing capabilities.

Safety Controls:
- synthetic_only: True
- confirmed_vulnerability: False
- formal_finding_allowed: False
- production_safety_claimed: False
"""

import sys
import logging
from pathlib import Path

# Add project root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.full_corpus_loader import FullCorpusLoader, CorpusEntry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ValidateCorpusLoader")


def run_validation() -> bool:
    logger.info("=== Phase-96B-CORPUS-001 Validation & Regression Test Suite ===")

    loader = FullCorpusLoader(workspace_root=REPO_ROOT)

    # 1. Discover 75-entry playbooks
    logger.info("Step 1: Auto-discovering 75-entry corpus suites...")
    discovered = loader.discover_75_entry_playbooks()
    logger.info(f"Discovered {len(discovered)} 75-entry playbooks.")

    expected_modules = {"M31", "M32", "M33", "M35", "M37", "M40", "M41", "M44", "M45", "M46"}
    found_modules = {item["module_id"] for item in discovered}

    assert len(discovered) == 10, f"Expected 10 75-entry playbooks, found {len(discovered)}"
    assert found_modules == expected_modules, f"Module mismatch! Expected {expected_modules}, got {found_modules}"

    for item in discovered:
        assert item["total_entries"] == 75, f"Playbook {item['path']} does not have 75 entries!"
        logger.info(f"  [OK] Module {item['module_id']} -> {item['path']} (75 entries)")

    # 2. Load all 75-entry corpora
    logger.info("\nStep 2: Loading & dynamically transforming entries across all suites...")
    all_corpora = loader.load_all_75_entry_corpora()
    assert len(all_corpora) == 10, f"Expected 10 loaded corpora dict, got {len(all_corpora)}"

    total_loaded_entries = sum(len(entries) for entries in all_corpora.values())
    logger.info(f"Successfully loaded {total_loaded_entries} entries across 10 modules.")
    assert total_loaded_entries == 750, f"Expected 750 total entries, got {total_loaded_entries}"

    # 3. Format Reconciliation & Safety Boundary Checks
    logger.info("\nStep 3: Performing format reconciliation (格式对账) & safety audit...")
    all_entries = [e for entries in all_corpora.values() for e in entries]

    reconcile = loader.reconcile_format(all_entries)
    logger.info(f"Reconciliation Status: {reconcile['reconciliation_status']}")
    logger.info(f"Compliance Rate: {reconcile['compliance_rate']:.2f}% ({reconcile['valid_entries']}/{reconcile['total_entries_checked']})")
    logger.info(f"Control Cases Count: {reconcile['control_cases_count']}")
    logger.info(f"Category Distribution: {reconcile['category_distribution']}")

    assert reconcile["reconciliation_status"] == "PASS", "Format reconciliation failed!"
    assert reconcile["compliance_rate"] == 100.0, f"Compliance rate is {reconcile['compliance_rate']}%, expected 100.0%"
    assert reconcile["invalid_entries"] == 0, f"Found {reconcile['invalid_entries']} invalid entries"
    assert reconcile["safety_boundary_violations"] == 0, f"Found {reconcile['safety_boundary_violations']} safety boundary violations"

    # Deep safety boundary assertion per entry
    for entry in all_entries:
        assert entry.safety_flags["confirmed_vulnerability"] is False
        assert entry.safety_flags["formal_finding_allowed"] is False
        assert entry.safety_flags["production_safety_claimed"] is False
        assert entry.safety_flags["synthetic_only"] is True
        assert len(entry.input_prompt) > 0, f"Entry {entry.id} has empty prompt"

    logger.info("  [OK] Safety boundaries 100% verified across all 750 entries.")

    # 4. Dynamic Context & Payload Rendering Verification
    logger.info("\nStep 4: Verifying dynamic context/payload rendering for target adapters...")
    sample_entry = all_corpora["M35"][0]  # MCP module entry
    sample_multimodal = all_corpora["M33"][0]  # Multimodal entry

    # Test OpenAI rendering
    openai_rendered = loader.render_context_and_payload(sample_entry, target_adapter="openai")
    assert openai_rendered["adapter"] == "openai"
    assert len(openai_rendered["messages"]) >= 1
    logger.info("  [OK] OpenAI target adapter payload rendered successfully.")

    # Test REST rendering
    rest_rendered = loader.render_context_and_payload(sample_entry, target_adapter="rest")
    assert rest_rendered["adapter"] == "rest"
    assert "payload" in rest_rendered
    logger.info("  [OK] REST target adapter payload rendered successfully.")

    # Test MCP rendering
    mcp_rendered = loader.render_context_and_payload(sample_entry, target_adapter="mcp")
    assert mcp_rendered["adapter"] == "mcp"
    assert mcp_rendered["method"] == "tools/call"
    logger.info("  [OK] MCP target adapter payload rendered successfully.")

    # Test Generic rendering
    generic_rendered = loader.render_context_and_payload(sample_multimodal, target_adapter="generic")
    assert generic_rendered["adapter"] == "generic"
    assert generic_rendered["entry_id"] == sample_multimodal.id
    logger.info("  [OK] Generic target adapter payload rendered successfully.")

    # 5. Filtering & Query Slicing Verification
    logger.info("\nStep 5: Verifying entry filtering, slicing & query capabilities...")
    m31_entries = loader.filter_entries(all_entries, module_id="M31")
    assert len(m31_entries) == 75, f"Expected 75 M31 entries, got {len(m31_entries)}"

    control_entries = loader.filter_entries(all_entries, control_case=True)
    logger.info(f"Found {len(control_entries)} control case entries.")

    sliced = loader.filter_entries(all_entries, limit=10, offset=5)
    assert len(sliced) == 10, f"Expected sliced length 10, got {len(sliced)}"
    logger.info("  [OK] Filtering and pagination verified.")

    logger.info("\n===========================================================")
    logger.info("ALL VALIDATION & REGRESSION CHECKS PASSED (100% PASS)!")
    logger.info("===========================================================")
    return True


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
