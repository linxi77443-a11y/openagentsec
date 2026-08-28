#!/usr/bin/env python3
"""
Phase-96B BatchRunner & Checkpoint Resume Validation Script
Path: scripts/validate_phase96b_batch_runner.py

Verifies:
1. Multi-criteria task discovery & filtering (Phase, Module, Tag).
2. Full 75-entry / 750-entry batch run & atomic Checkpoint persistence.
3. Simulated Interruption, Checkpoint state persistence & Resume (100% zero duplicate task executions).
4. Target Adapter payload rendering (OpenAI, REST, MCP, Generic).
5. Safety boundary compliance (synthetic_only=True, confirmed_vulnerability=False, etc.).

Task ID: Phase-96B-RUNNER-002
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from core.batch_runner import (
    BatchRunner,
    BatchRunConfig,
    CheckpointManager,
    BatchInterruptedException,
    SAFE_BOUNDARIES
)
from core.full_corpus_loader import FullCorpusLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("Phase96BRunnerValidation")


def test_1_multi_criteria_filtering():
    """Test 1: Multi-criteria Task Filtering (Phase, Module, Tag)."""
    logger.info("--- Running Test 1: Multi-criteria Task Filtering ---")
    config = BatchRunConfig(
        phase="Phase-96B",
        modules=["M31", "M35"],
        tags=["control_case"],
        checkpoint_file="artifacts/batch_checkpoints/test_filter_checkpoint.json"
    )
    runner = BatchRunner(config=config, workspace_root=WORKSPACE_ROOT)
    tasks = runner.discover_and_filter_tasks()

    # M31 has control cases, M35 has control cases
    assert len(tasks) > 0, "Expected non-empty tasks for filtered criteria"
    assert all(e.module_id in ["M31", "M35"] for e in tasks), "Module filter failed"
    assert all(e.control_case is True for e in tasks), "Tag filter ('control_case') failed"

    logger.info(f"PASS Test 1: Filtered {len(tasks)} tasks matching modules=['M31', 'M35'] and tag='control_case'")


def test_2_full_batch_checkpoint_persistence():
    """Test 2: Full 750-Entry Batch Execution & Atomic Checkpoint Persistence."""
    logger.info("--- Running Test 2: Full 750-Entry Batch Run & Checkpoint Persistence ---")
    ckpt_file = WORKSPACE_ROOT / "artifacts/batch_checkpoints/test_full_run_checkpoint.json"
    if ckpt_file.exists():
        ckpt_file.unlink()

    config = BatchRunConfig(
        session_id="test_full_session_001",
        phase="Phase-96B",
        checkpoint_file=str(ckpt_file),
        auto_resume=False
    )
    runner = BatchRunner(config=config, workspace_root=WORKSPACE_ROOT)

    summary = runner.run_batch()

    assert summary["total_tasks"] == 750, f"Expected 750 tasks, got {summary['total_tasks']}"
    assert summary["completed_total"] == 750, f"Expected 750 completed, got {summary['completed_total']}"
    assert summary["status"] == "completed", f"Expected status 'completed', got {summary['status']}"
    assert summary["failed_total"] == 0, f"Expected 0 failures, got {summary['failed_total']}"
    assert ckpt_file.exists(), "Checkpoint file was not persisted to disk"

    # Verify JSON content of checkpoint file
    with open(ckpt_file, "r", encoding="utf-8") as f:
        ckpt_json = json.load(f)

    assert ckpt_json["total_tasks"] == 750
    assert ckpt_json["completed_count"] == 750
    assert ckpt_json["status"] == "completed"
    assert len(ckpt_json["tasks"]) == 750

    logger.info("PASS Test 2: 750-entry batch executed and checkpoint persisted successfully.")


def test_3_interruption_and_resume_zero_duplicate():
    """Test 3: Simulated Interruption & Resume (100% Zero-Duplicate Executions)."""
    logger.info("--- Running Test 3: Simulated Interruption & Resume Zero-Duplicate Check ---")
    ckpt_file = WORKSPACE_ROOT / "artifacts/batch_checkpoints/phase96b_checkpoint.json"
    if ckpt_file.exists():
        ckpt_file.unlink()

    config = BatchRunConfig(
        session_id="phase96b_resume_session_001",
        phase="Phase-96B",
        checkpoint_file=str(ckpt_file),
        auto_resume=True
    )
    runner = BatchRunner(config=config, workspace_root=WORKSPACE_ROOT)

    handler_calls: List[str] = []

    def tracking_handler(entry):
        handler_calls.append(entry.id)
        return {
            "entry_id": entry.id,
            "module_id": entry.module_id,
            "status": "success",
            "eval_signal": entry.expected_signal[0] if entry.expected_signal else "refuse"
        }

    # Step A: Run batch with interruption after 300 tasks
    interrupted_caught = False
    try:
        runner.run_batch(task_handler=tracking_handler, interrupt_after=300)
    except BatchInterruptedException as e:
        interrupted_caught = True
        logger.info(f"Caught expected interruption exception after {e.completed_count} tasks.")

    assert interrupted_caught, "Expected BatchInterruptedException was not raised!"
    assert len(handler_calls) == 300, f"Expected 300 handler calls before interruption, got {len(handler_calls)}"

    # Inspect checkpoint after interruption
    ckpt_summary = runner.get_checkpoint_summary()
    assert ckpt_summary["status"] == "interrupted", f"Expected checkpoint status 'interrupted', got {ckpt_summary['status']}"
    assert ckpt_summary["completed_count"] == 300
    assert ckpt_summary["total_tasks"] == 750

    logger.info("Step A PASS: Batch run successfully interrupted at 300 tasks, state saved.")

    # Step B: Resume batch run on the same checkpoint
    handler_calls_during_resume: List[str] = []

    def resume_tracking_handler(entry):
        handler_calls_during_resume.append(entry.id)
        return {
            "entry_id": entry.id,
            "module_id": entry.module_id,
            "status": "success",
            "eval_signal": entry.expected_signal[0] if entry.expected_signal else "refuse"
        }

    resume_summary = runner.resume_batch(task_handler=resume_tracking_handler)

    logger.info(f"Resume summary: {resume_summary}")

    # STRICT ASSERTION: Handler should ONLY be called for the remaining 450 tasks!
    assert len(handler_calls_during_resume) == 450, f"Expected exactly 450 handler calls during resume, got {len(handler_calls_during_resume)}"
    assert resume_summary["completed_total"] == 750, f"Expected 750 total completed after resume, got {resume_summary['completed_total']}"
    assert resume_summary["resumed_skipped_count"] == 300, f"Expected 300 resumed skipped, got {resume_summary['resumed_skipped_count']}"
    assert resume_summary["executed_in_this_run"] == 450, f"Expected 450 executed in resume run, got {resume_summary['executed_in_this_run']}"
    assert resume_summary["status"] == "completed"

    # Verify final checkpoint file state
    final_summary = runner.get_checkpoint_summary()
    assert final_summary["status"] == "completed"
    assert final_summary["completed_count"] == 750
    assert final_summary["failed_count"] == 0

    logger.info("PASS Test 3: Interruption & Resume verified with 100% zero duplicate handler calls!")


def test_4_target_adapter_payload_rendering():
    """Test 4: Target Adapter Payload Rendering across batch entries."""
    logger.info("--- Running Test 4: Target Adapter Payload Rendering ---")

    for adapter_name in ["openai", "rest", "mcp", "generic"]:
        ckpt_file = WORKSPACE_ROOT / f"artifacts/batch_checkpoints/test_adapter_{adapter_name}.json"
        if ckpt_file.exists():
            ckpt_file.unlink()

        config = BatchRunConfig(
            session_id=f"test_adapter_{adapter_name}",
            phase="Phase-96B",
            modules=["M35", "M46"],  # Sample modules for speed
            target_adapter=adapter_name,
            checkpoint_file=str(ckpt_file),
            auto_resume=False
        )
        runner = BatchRunner(config=config, workspace_root=WORKSPACE_ROOT)
        summary = runner.run_batch()

        assert summary["completed_total"] == 150, f"Adapter {adapter_name}: expected 150 tasks"
        assert summary["status"] == "completed"
        logger.info(f"Adapter '{adapter_name}' verified PASS (150 tasks rendered).")

    logger.info("PASS Test 4: All target adapters (openai, rest, mcp, generic) rendered successfully.")


def test_5_safety_boundary_compliance():
    """Test 5: Verify safety boundary flags across checkpoints and batch outputs."""
    logger.info("--- Running Test 5: Safety Boundary Compliance ---")
    ckpt_file = WORKSPACE_ROOT / "artifacts/batch_checkpoints/phase96b_checkpoint.json"
    assert ckpt_file.exists(), "Primary checkpoint file phase96b_checkpoint.json should exist"

    with open(ckpt_file, "r", encoding="utf-8") as f:
        ckpt_data = json.load(f)

    sb = ckpt_data.get("safety_boundaries", {})
    assert sb.get("confirmed_vulnerability") is False, "confirmed_vulnerability must be False"
    assert sb.get("formal_finding_allowed") is False, "formal_finding_allowed must be False"
    assert sb.get("production_safety_claimed") is False, "production_safety_claimed must be False"
    assert sb.get("synthetic_only") is True, "synthetic_only must be True"

    logger.info("PASS Test 5: Safety boundaries strictly compliant.")


def main():
    logger.info("============================================================")
    logger.info("Starting Phase-96B-RUNNER-002 Validation & Regression Tests")
    logger.info("============================================================")

    try:
        test_1_multi_criteria_filtering()
        test_2_full_batch_checkpoint_persistence()
        test_3_interruption_and_resume_zero_duplicate()
        test_4_target_adapter_payload_rendering()
        test_5_safety_boundary_compliance()

        logger.info("============================================================")
        logger.info("ALL TESTS PASSED 100%! BatchRunner & Checkpoint Resume Verified.")
        logger.info("============================================================")
        sys.exit(0)
    except AssertionError as e:
        logger.error(f"Validation assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
