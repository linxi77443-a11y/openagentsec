"""Phase 21.7: Evidence Completeness & Provenance Audit.

Audits Phase 21.6 experiment artifacts to confirm that every evaluation conclusion
is strictly supported by verified EvidenceItems, tool execution logs, and runtime traces.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List
import pytest

ATTACK_ARTIFACT_DIR = "artifacts/live_validation/deepseek_attack"


def test_evidence_completeness_across_attack_cases() -> None:
    """Audits the 4 primary attack experiment artifacts for full evidence provenance."""
    case_files = [
        "indirect_injection_case.json",
        "memory_poisoning_case.json",
        "subagent_delegation_case.json",
        "adaptive_discovery_case.json",
    ]

    for fname in case_files:
        fpath = os.path.join(ATTACK_ARTIFACT_DIR, fname)
        assert os.path.exists(fpath), f"Artifact missing: {fpath}"

        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1. Attack Stimulus completeness
        assert "attack" in data
        assert "prompt" in data["attack"]
        assert len(data["attack"]["prompt"]) > 0

        # 2. Runtime Telemetry completeness
        assert "runtime" in data
        assert data["runtime"]["name"] == "DeepSeek Harness"
        assert data["runtime"]["endpoint"] == "http://127.0.0.1:3080"
        assert data["runtime"]["sessionId"].startswith("session-")

        # 3. Response & Event Stream completeness
        assert "response" in data
        assert "event_count" in data["response"]
        assert data["response"]["event_count"] >= 1
        assert "tool_calls" in data["response"]

        # 4. Evidence Items completeness
        assert "evidence" in data
        assert len(data["evidence"]) >= 4
        ev_types = [e["type"] for e in data["evidence"]]
        assert "state_transition_trace" in ev_types
        assert "tool_execution_log" in ev_types
        assert "runtime_observation" in ev_types
        assert "memory_persistence_receipt" in ev_types

        for e in data["evidence"]:
            assert e["verified"] is True
            assert e["source"].startswith("deepseek_harness.")
            assert len(e["id"]) > 0

        # 5. Oracle Result completeness
        assert "oracle_result" in data
        assert data["oracle_result"]["decision"] in ("NO_CONFIRMED_DEVIATION", "CONFIRMED_DEVIATION")


def test_reproduction_summary_artifact_integrity() -> None:
    """Audits the 5-run statutory reproduction summary artifact."""
    summary_file = os.path.join(ATTACK_ARTIFACT_DIR, "attack_reproduction_summary.json")
    assert os.path.exists(summary_file)

    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["target_id"] == "TARGET-LIVE-DEEPSEEK-HARNESS"
    assert summary["requested_runs"] == 5
    assert summary["completed_runs"] == 5
    assert len(summary["runs"]) == 5
    assert summary["reproduction_status"] == "REPRODUCED"
    assert summary["variance_detected"] is False

    for run in summary["runs"]:
        assert run["valid"] is True
        assert run["reset_verified_before"] is True
        assert run["reset_verified_after"] is True
        assert len(run["evidence_refs"]) >= 4
