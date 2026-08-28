"""Integration tests for Finding Lifecycle Management (Phase 11.4)."""

from __future__ import annotations

from typing import Any, Dict
import pytest

from src.openagentsec.operations import FindingManager, SecurityFinding


def test_case1_finding_lifecycle_and_resolution() -> None:
    """Case 1: Validate finding creation, acknowledgment, and resolution lifecycle."""
    manager = FindingManager()

    finding = SecurityFinding(
        finding_id="FIND-AGENT-01-AUTH-001",
        agent_id="AGENT-01",
        scenario_id="AUTH-IDENTITY-SPOOF-001",
        title="Identity Spoofing Vulnerability",
        severity="CRITICAL",
        status="OPEN",
        evidence_reference=["EV-AUTH-001"],
        description="Agent accepted unverified caller identity.",
    )

    # 1. Create
    manager.create(finding)
    assert manager.get("FIND-AGENT-01-AUTH-001") is not None
    assert len(manager.list_findings(agent_id="AGENT-01", status="OPEN")) == 1

    # 2. Acknowledge
    manager.update_status("FIND-AGENT-01-AUTH-001", "ACKNOWLEDGED", "Investigating root cause")
    f_ack = manager.get("FIND-AGENT-01-AUTH-001")
    assert f_ack.status == "ACKNOWLEDGED"
    assert f_ack.resolution_note == "Investigating root cause"

    # 3. Resolve / Fix
    manager.resolve("FIND-AGENT-01-AUTH-001", "Fixed by enforcing HMAC session signature")
    f_fixed = manager.get("FIND-AGENT-01-AUTH-001")
    assert f_fixed.status == "FIXED"
    assert f_fixed.resolved_at is not None
    assert "HMAC" in f_fixed.resolution_note


def test_case2_finding_suppression() -> None:
    """Case 2: Validate finding suppression with security exception note."""
    manager = FindingManager()

    finding = SecurityFinding(
        finding_id="FIND-AGENT-02-SCOPE-001",
        agent_id="AGENT-02",
        scenario_id="AUTH-PARAMETER-SCOPE-001",
        title="Broad Parameter Scope Warning",
        severity="LOW",
        status="OPEN",
    )
    manager.create(finding)

    # Suppress
    manager.suppress("FIND-AGENT-02-SCOPE-001", "Approved business exception for read-only query")
    f_supp = manager.get("FIND-AGENT-02-SCOPE-001")
    assert f_supp.status == "SUPPRESSED"
    assert f_supp.resolved_at is not None
    assert len(manager.list_findings(status="SUPPRESSED")) == 1
