"""TargetProfile model for OpenAgentSec Target Modeling.

PRD v4.0.2 §7:
TargetProfile describes an Agent target's security attributes, boundaries, and
observable capabilities.

SEMANTIC BOUNDARY:
TargetProfile ≠ TargetAdapter Config.
TargetProfile describes architectural security properties and explicit observability.
It MUST NOT contain API tokens, credentials, connection secrets, or live endpoint URLs.

OBSERVABILITY REQUIREMENT:
Observability dimensions must explicitly declare their state:
- observable
- unobservable
- partially_observable
Missing/undeclared states must never be auto-filled or guessed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .enums import EnvironmentType, ObservabilityState


@dataclass
class TargetProfile:
    """Target profile describing security attributes and observable capabilities."""
    target_id: str
    target_type: str
    target_version: str
    environment: EnvironmentType
    identities: List[str] = field(default_factory=list)
    tenants: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    rag_sources: List[str] = field(default_factory=list)
    memory_stores: List[str] = field(default_factory=list)
    approval_points: List[str] = field(default_factory=list)
    connectors: List[str] = field(default_factory=list)
    runtime_capabilities: List[str] = field(default_factory=list)
    output_channels: List[str] = field(default_factory=list)
    observability: Dict[str, ObservabilityState] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_type": self.target_type,
            "target_version": self.target_version,
            "environment": (
                self.environment.value
                if isinstance(self.environment, EnvironmentType)
                else str(self.environment)
            ),
            "identities": list(self.identities),
            "tenants": list(self.tenants),
            "roles": list(self.roles),
            "tools": list(self.tools),
            "resources": list(self.resources),
            "rag_sources": list(self.rag_sources),
            "memory_stores": list(self.memory_stores),
            "approval_points": list(self.approval_points),
            "connectors": list(self.connectors),
            "runtime_capabilities": list(self.runtime_capabilities),
            "output_channels": list(self.output_channels),
            "observability": {
                k: (v.value if isinstance(v, ObservabilityState) else str(v))
                for k, v in self.observability.items()
            },
        }
