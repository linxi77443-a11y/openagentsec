"""
Unit and Integration Tests for Phase-96B BatchRunner & Checkpoint Resume Engine.
Path: tests/test_phase96b_batch_runner.py
"""

import os
import json
import pytest
from pathlib import Path
from typing import Dict, List, Any

from core.batch_runner import (
    BatchRunner,
    BatchRunConfig,
    CheckpointManager,
    BatchInterruptedException,
    SAFE_BOUNDARIES
)
from core.full_corpus_loader import FullCorpusLoader

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def temp_checkpoint_file(tmp_path):
    return tmp_path / "test_checkpoint.json"


def test_batch_runner_initialization(temp_checkpoint_file):
    config = BatchRunConfig(
        phase="Phase-96B",
        modules=["M31"],
        checkpoint_file=str(temp_checkpoint_file)
    )
    runner = BatchRunner(config=config, workspace_root=WORKSPACE_ROOT)
    assert runner.config.phase == "Phase-96B"
    assert runner.config.modules == ["M31"]
    assert runner.config.checkpoint_file == str(temp_checkpoint_file)


def test_discover_and_filter_tasks(temp_checkpoint_file):
    config = BatchRunConfig(
        phase="Phase-96B",
        modules=["M31", "M32"],
        tags=["control_case"],
        checkpoint_file=str(temp_checkpoint_file)
    )
    runner = BatchRunner(config=config, workspace_root=WORKSPACE_ROOT)
    tasks = runner.discover_and_filter_tasks()

    assert len(tasks) > 0
    assert all(t.module_id in ["M31", "M32"] for t in tasks)
    assert all(t.control_case is True for t in tasks)


def test_checkpoint_atomic_save_and_load(temp_checkpoint_file):
    mgr = CheckpointManager(temp_checkpoint_file)
    assert mgr.load_checkpoint() is None

    test_data = {
        "session_id": "test_sess_001",
        "total_tasks": 10,
        "completed_count": 0,
        "tasks": {}
    }
    assert mgr.save_checkpoint(test_data) is True
    assert temp_checkpoint_file.exists()

    loaded = mgr.load_checkpoint()
    assert loaded is not None
    assert loaded["session_id"] == "test_sess_001"
    assert loaded["safety_boundaries"]["synthetic_only"] is True


def test_batch_run_with_interruption_and_resume(temp_checkpoint_file):
    config = BatchRunConfig(
        session_id="test_interruption_sess",
        phase="Phase-96B",
        modules=["M31"],  # 75 entries
        checkpoint_file=str(temp_checkpoint_file),
        auto_resume=True
    )
    runner = BatchRunner(config=config, workspace_root=WORKSPACE_ROOT)

    executed_ids_pass1 = []

    def mock_handler_pass1(entry):
        executed_ids_pass1.append(entry.id)
        return {"entry_id": entry.id, "status": "ok"}

    # Run with interruption after 30 tasks
    with pytest.raises(BatchInterruptedException) as exc_info:
        runner.run_batch(task_handler=mock_handler_pass1, interrupt_after=30)

    assert exc_info.value.completed_count == 30
    assert len(executed_ids_pass1) == 30

    ckpt_summary = runner.get_checkpoint_summary()
    assert ckpt_summary["status"] == "interrupted"
    assert ckpt_summary["completed_count"] == 30
    assert ckpt_summary["total_tasks"] == 75

    # Resume execution
    executed_ids_pass2 = []

    def mock_handler_pass2(entry):
        executed_ids_pass2.append(entry.id)
        return {"entry_id": entry.id, "status": "ok"}

    summary = runner.resume_batch(task_handler=mock_handler_pass2)

    assert len(executed_ids_pass2) == 45
    assert summary["completed_total"] == 75
    assert summary["resumed_skipped_count"] == 30
    assert summary["executed_in_this_run"] == 45
    assert summary["status"] == "completed"

    # Verify zero duplicate executions
    set1 = set(executed_ids_pass1)
    set2 = set(executed_ids_pass2)
    assert set1.intersection(set2) == set()


def test_safety_boundaries_compliance(temp_checkpoint_file):
    config = BatchRunConfig(
        phase="Phase-96B",
        modules=["M31"],
        checkpoint_file=str(temp_checkpoint_file)
    )
    runner = BatchRunner(config=config, workspace_root=WORKSPACE_ROOT)
    summary = runner.run_batch()

    sb = summary["safety_summary"]
    assert sb["confirmed_vulnerability"] is False
    assert sb["formal_finding_allowed"] is False
    assert sb["production_safety_claimed"] is False
    assert sb["synthetic_only"] is True
