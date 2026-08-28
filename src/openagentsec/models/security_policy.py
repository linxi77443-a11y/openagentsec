"""SecurityPolicy model for OpenAgentSec Governance Plane.

PRD v4.0.2 §5:
SecurityPolicy is a declarative governance object specifying what an agent target
is allowed to do, denied from doing, what requires human/independent approval,
and the strict policy invariants with non-dynamically generated severity.

SEMANTIC BOUNDARY:
SecurityPolicy ≠ SandboxPolicy.
SecurityPolicy belongs to the Governance Plane. SandboxPolicy / sandbox_rules.yaml
belongs to Runtime Policy / Rule Oracle assets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .enums import Severity


@dataclass
class PolicyPermissions:
    """Allowed or denied permissions partitioned by security dimension."""
    identities: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    delegation: List[str] = field(default_factory=list)
    persistent_state: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[str]]:
        return asdict(self)


@dataclass
class PolicyApproval:
    """Independent approval requirement for sensitive actions."""
    action: str
    required: bool
    approver: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "required": self.required,
            "approver": self.approver,
        }


@dataclass
class PolicyInvariant:
    """Declarative security boundary invariant with structured governance severity."""
    invariant_id: str
    statement: str
    severity: Severity
    rationale: str
    retest_policy_ref: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "statement": self.statement,
            "severity": self.severity.value if isinstance(self.severity, Severity) else str(self.severity),
            "rationale": self.rationale,
            "retest_policy_ref": self.retest_policy_ref,
        }


@dataclass
class SecurityPolicy:
    """Declarative Governance Plane security policy object."""
    policy_id: str
    version: str
    target_refs: List[str]
    allowed: PolicyPermissions
    denied: PolicyPermissions
    approvals: List[PolicyApproval] = field(default_factory=list)
    invariants: List[PolicyInvariant] = field(default_factory=list)
    critical_actions: List[str] = field(default_factory=list)
    evidence_requirements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "target_refs": list(self.target_refs),
            "allowed": self.allowed.to_dict(),
            "denied": self.denied.to_dict(),
            "approvals": [a.to_dict() for a in self.approvals],
            "invariants": [i.to_dict() for i in self.invariants],
            "critical_actions": list(self.critical_actions),
            "evidence_requirements": list(self.evidence_requirements),
        }
