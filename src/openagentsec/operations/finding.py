"""Security Finding Lifecycle Management (PRD v4.0.2 Phase 11.4).

Manages vulnerability findings, severities, and remediation lifecycle states.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SecurityFinding:
    """Represents a discovered security vulnerability or policy deviation on an Agent asset."""

    finding_id: str
    agent_id: str
    scenario_id: str
    title: str
    severity: str = "HIGH"  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    status: str = "OPEN"  # "OPEN" | "ACKNOWLEDGED" | "FIXED" | "SUPPRESSED"
    evidence_reference: List[str] = field(default_factory=list)
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    resolved_at: Optional[str] = None
    resolution_note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FindingManager:
    """Manages the lifecycle of security findings across agents."""

    VALID_STATUSES = ["OPEN", "ACKNOWLEDGED", "FIXED", "SUPPRESSED"]

    def __init__(self) -> None:
        self._findings: Dict[str, SecurityFinding] = {}

    def create(self, finding: SecurityFinding) -> SecurityFinding:
        """Create and store a new finding."""
        self._findings[finding.finding_id] = finding
        return finding

    def get(self, finding_id: str) -> Optional[SecurityFinding]:
        """Retrieve finding by ID."""
        return self._findings.get(finding_id)

    def list_findings(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """List findings matching optional filters."""
        res = list(self._findings.values())
        if agent_id:
            res = [f for f in res if f.agent_id == agent_id]
        if status:
            res = [f for f in res if f.status == status]
        if severity:
            res = [f for f in res if f.severity == severity]
        return res

    def update_status(
        self,
        finding_id: str,
        status: str,
        note: Optional[str] = None,
    ) -> SecurityFinding:
        """Update finding lifecycle state."""
        if finding_id not in self._findings:
            raise KeyError(f"Finding with id '{finding_id}' not found.")
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {self.VALID_STATUSES}.")

        f = self._findings[finding_id]
        f.status = status
        if note:
            f.resolution_note = note
        if status in ["FIXED", "SUPPRESSED"]:
            f.resolved_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        return f

    def resolve(self, finding_id: str, note: str = "Resolved by developer") -> SecurityFinding:
        """Mark a finding as FIXED."""
        return self.update_status(finding_id, "FIXED", note)

    def suppress(self, finding_id: str, reason: str = "Risk accepted by security team") -> SecurityFinding:
        """Mark a finding as SUPPRESSED."""
        return self.update_status(finding_id, "SUPPRESSED", reason)

    def clear(self) -> None:
        """Clear all findings."""
        self._findings.clear()
