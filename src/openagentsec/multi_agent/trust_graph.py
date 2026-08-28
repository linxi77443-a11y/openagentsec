"""Multi-Agent Trust Graph Model (PRD v4.0.2 Phase 8.2.1).

Defines directed trust topology, permission path resolution, and privilege inheritance detection.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class TrustNode:
    """Node representing an Agent in the Trust Network."""

    agent_id: str
    trust_level: str  # "trusted" | "semi_trusted" | "untrusted" | "expired"
    permissions: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    expires_at_step: Optional[int] = None

    def is_expired(self, current_step: int) -> bool:
        if self.trust_level == "expired":
            return True
        if self.expires_at_step is not None and current_step >= self.expires_at_step:
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TrustEdge:
    """Directed edge representing trust or delegation relationship between agents."""

    source_agent: str
    target_agent: str
    relationship: str  # "delegates_to" | "supervises" | "peers_with"
    delegation_scope: List[str] = field(default_factory=list)
    created_by: str = "system"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentTrustGraph:
    """Graph model managing agents, directed trust relationships, and path resolution."""

    def __init__(self) -> None:
        self.nodes: Dict[str, TrustNode] = {}
        self.edges: List[TrustEdge] = []

    def add_agent(self, node: TrustNode) -> None:
        self.nodes[node.agent_id] = node

    def add_trust_edge(self, edge: TrustEdge) -> None:
        self.edges.append(edge)

    def get_agent(self, agent_id: str) -> Optional[TrustNode]:
        return self.nodes.get(agent_id)

    def find_all_paths(
        self,
        source_id: str,
        target_id: str,
        visited: Optional[List[str]] = None,
    ) -> List[List[str]]:
        """Find all acyclic delegation paths between source and target agents."""
        if visited is None:
            visited = []

        visited = visited + [source_id]

        if source_id == target_id:
            return [visited]

        paths: List[List[str]] = []
        for edge in self.edges:
            if edge.source_agent == source_id:
                next_agent = edge.target_agent
                if next_agent not in visited:
                    sub_paths = self.find_all_paths(next_agent, target_id, visited)
                    for p in sub_paths:
                        paths.append(p)

        return paths

    def resolve_permission_path(
        self,
        source_agent: str,
        target_agent: str,
        tool_permission: str,
        current_step: int = 1,
    ) -> Dict[str, Any]:
        """Resolve if source can delegate tool_permission to target along an active trust path."""
        paths = self.find_all_paths(source_agent, target_agent)
        if not paths:
            return {
                "authorized": False,
                "reason_code": "no_trust_path_found",
                "path": [],
                "message": f"No delegation path found from {source_agent} to {target_agent}.",
            }

        # Check shortest path
        primary_path = paths[0]

        # 1. Check trust expiration on any node
        for agent_id in primary_path:
            node = self.get_agent(agent_id)
            if not node or node.is_expired(current_step):
                return {
                    "authorized": False,
                    "reason_code": "trust_decay_expired",
                    "path": primary_path,
                    "expired_agent": agent_id,
                    "message": f"Agent {agent_id} trust level is expired at step {current_step}.",
                }

        # 2. Check monotonic permission constraint (source must possess tool_permission)
        source_node = self.get_agent(source_agent)
        if not source_node or tool_permission not in source_node.permissions:
            return {
                "authorized": False,
                "reason_code": "privilege_amplification_detected",
                "path": primary_path,
                "message": f"Source agent {source_agent} lacks '{tool_permission}'. Cannot delegate.",
            }

        # 3. Check target agent permission
        target_node = self.get_agent(target_agent)
        if not target_node or tool_permission not in target_node.permissions:
            return {
                "authorized": False,
                "reason_code": "target_agent_lacks_permission",
                "path": primary_path,
                "message": f"Target agent {target_agent} lacks '{tool_permission}'.",
            }

        # 4. Check trust boundary (no untrusted node in intermediate hops)
        for agent_id in primary_path[:-1]:
            node = self.get_agent(agent_id)
            if node and node.trust_level == "untrusted":
                return {
                    "authorized": False,
                    "reason_code": "untrusted_boundary_violation",
                    "path": primary_path,
                    "message": f"Delegation through untrusted agent {agent_id} violates trust boundary.",
                }

        return {
            "authorized": True,
            "reason_code": "trust_path_authorized",
            "path": primary_path,
            "message": f"Delegation path {primary_path} successfully authorized for '{tool_permission}'.",
        }

    def detect_privilege_inheritance(self, path: List[str]) -> Dict[str, Any]:
        """Detect whether permissions expand across hops along the path."""
        cumulative_permissions: Set[str] = set()
        amplifications: List[Dict[str, Any]] = []

        for idx, agent_id in enumerate(path):
            node = self.get_agent(agent_id)
            if not node:
                continue

            node_perms = set(node.permissions)
            if idx > 0:
                # Disallowed: child node has permissions not present in parent node
                parent_node = self.get_agent(path[idx - 1])
                parent_perms = set(parent_node.permissions) if parent_node else set()
                excess = node_perms - parent_perms
                if excess:
                    amplifications.append({
                        "from_agent": path[idx - 1],
                        "to_agent": agent_id,
                        "amplified_permissions": list(excess),
                    })

            cumulative_permissions.update(node_perms)

        return {
            "amplification_detected": len(amplifications) > 0,
            "amplifications": amplifications,
        }
