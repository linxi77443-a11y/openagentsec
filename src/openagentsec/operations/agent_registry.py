"""Agent Asset Registry (PRD v4.0.2 Phase 11.1).

Manages enterprise AI Agent security assets, environments, and ownership metadata.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AgentAsset:
    """Enterprise AI Agent Asset representation."""

    agent_id: str
    name: str
    owner: str
    team: str
    environment: str = "staging"  # "development" | "staging" | "production"
    version: str = "1.0.0"
    adapter_type: str = "whitebox_langgraph"
    target_id: str = "TARGET-LANGGRAPH-PARAM-WHITEBOX"
    benchmark_profile: Dict[str, Any] = field(default_factory=dict)
    security_status: str = "UNASSESSED"  # "UNASSESSED" | "COMPLIANT" | "NON_COMPLIANT" | "DEGRADED"
    last_evaluation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentAssetRegistry:
    """In-memory registry managing enterprise AI agent assets."""

    def __init__(self) -> None:
        self._assets: Dict[str, AgentAsset] = {}

    def register_agent(self, asset: AgentAsset) -> AgentAsset:
        """Register a new AI agent asset or update existing one."""
        self._assets[asset.agent_id] = asset
        return asset

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> AgentAsset:
        """Apply partial updates to an existing agent asset."""
        if agent_id not in self._assets:
            raise KeyError(f"Agent asset with id '{agent_id}' not found in registry.")

        current = self._assets[agent_id]
        current_dict = current.to_dict()
        current_dict.update(updates)
        updated = AgentAsset(**current_dict)
        self._assets[agent_id] = updated
        return updated

    def get_agent(self, agent_id: str) -> Optional[AgentAsset]:
        """Retrieve an agent asset by its ID."""
        return self._assets.get(agent_id)

    def list_agents(
        self,
        environment: Optional[str] = None,
        team: Optional[str] = None,
    ) -> List[AgentAsset]:
        """List registered agent assets matching optional filters."""
        results = list(self._assets.values())
        if environment:
            results = [a for a in results if a.environment == environment]
        if team:
            results = [a for a in results if a.team == team]
        return results

    def delete_agent(self, agent_id: str) -> bool:
        """Remove an agent asset from the registry."""
        if agent_id in self._assets:
            del self._assets[agent_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all registered assets."""
        self._assets.clear()
