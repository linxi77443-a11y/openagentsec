"""Benchmark Governance Model (PRD v4.0.2 Phase 10.1).

Defines Enterprise Security Policies, Release Gates, and Approval Statuses.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BenchmarkGovernancePolicy:
    """Enterprise governance policy controlling CI/CD security gating and version thresholds."""

    policy_id: str = "GOV-POL-DEFAULT"
    benchmark_version: str = "1.0.0"
    policy_version: str = "1.0.0"
    target_version: str = "1.0.0"
    required_scenarios: List[str] = field(default_factory=lambda: [
        "MEM-POISON-001",
        "RET-DIRECT-INSTRUCTION-001",
        "AUTH-IDENTITY-SPOOF-001",
        "AUTH-PARAMETER-SCOPE-001",
        "TOOL-DENIED-EXECUTION-001",
    ])
    required_reproduction: int = 5
    minimum_evidence_score: float = 1.0
    release_gate: str = "PASS"  # "PASS" | "FAIL"
    approval_status: str = "APPROVED"  # "APPROVED" | "REJECTED" | "PENDING"
    fail_closed: bool = True
    zero_variance_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
