"""Agent Identity and Delegation Security Model (PRD v4.0.2 Phase 8.1.2).

Defines cryptographically verifiable AgentIdentity independent of natural language prompt content.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
from typing import Any, Dict, List, Optional


@dataclass
class AgentIdentity:
    """Cryptographically verifiable Agent Identity independent of prompt text."""

    agent_id: str
    role: str  # "coordinator" | "executor" | "admin" | "guest"
    permissions: List[str] = field(default_factory=list)
    delegated_from: Optional[str] = None
    trust_level: str = "untrusted"  # "trusted" | "semi_trusted" | "untrusted"
    signature: Optional[str] = None

    def compute_signature(self, secret_key: str = "openagentsec_multiagent_secret_2026") -> str:
        """Compute SHA256 signature binding identity attributes."""
        canonical_permissions = ",".join(sorted(self.permissions))
        delegator = self.delegated_from or "root"
        payload = f"{self.agent_id}|{self.role}|{canonical_permissions}|{delegator}|{self.trust_level}|{secret_key}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def sign(self, secret_key: str = "openagentsec_multiagent_secret_2026") -> AgentIdentity:
        """Sign this identity in place."""
        self.signature = self.compute_signature(secret_key)
        return self

    def verify_integrity(self, secret_key: str = "openagentsec_multiagent_secret_2026") -> bool:
        """Verify whether signature matches identity attributes."""
        if not self.signature:
            return False
        return self.signature == self.compute_signature(secret_key)

    def has_permission(self, required_permission: str) -> bool:
        """Check whether this identity explicitly holds required permission."""
        return required_permission in self.permissions

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DelegationValidator:
    """Validates delegation authority across multi-agent call chains."""

    @staticmethod
    def validate_delegation(
        delegator_identity: AgentIdentity,
        delegatee_identity: AgentIdentity,
        requested_tool: str,
        required_permission: str,
        secret_key: str = "openagentsec_multiagent_secret_2026",
    ) -> Dict[str, Any]:
        """Verify transitive authority: delegator must possess permission to delegate it."""
        # 1. Verify signatures
        if not delegator_identity.verify_integrity(secret_key):
            return {
                "authorized": False,
                "reason_code": "delegator_signature_invalid",
                "message": f"Delegator {delegator_identity.agent_id} signature verification failed.",
            }

        if not delegatee_identity.verify_integrity(secret_key):
            return {
                "authorized": False,
                "reason_code": "delegatee_signature_invalid",
                "message": f"Delegatee {delegatee_identity.agent_id} signature verification failed.",
            }

        # 2. Check delegator permission (Delegator cannot grant what it doesn't possess)
        if not delegator_identity.has_permission(required_permission):
            return {
                "authorized": False,
                "reason_code": "delegator_insufficient_permissions",
                "message": (
                    f"Delegator {delegator_identity.agent_id} lacks '{required_permission}' "
                    f"to delegate tool '{requested_tool}'."
                ),
            }

        # 3. Check delegatee permission
        if not delegatee_identity.has_permission(required_permission):
            return {
                "authorized": False,
                "reason_code": "delegatee_insufficient_permissions",
                "message": (
                    f"Delegatee {delegatee_identity.agent_id} lacks '{required_permission}' "
                    f"for tool '{requested_tool}'."
                ),
            }

        return {
            "authorized": True,
            "reason_code": "delegation_authorized",
            "message": f"Delegation of '{requested_tool}' authorized from {delegator_identity.agent_id} to {delegatee_identity.agent_id}.",
        }
