"""Delegation Chain Analysis and Invariant Validation (PRD v4.0.2 Phase 8.2.2).

Performs static and dynamic inspection over multi-agent delegation chains (A -> B -> C).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set

from .agent_identity import AgentIdentity
from .trust_graph import AgentTrustGraph, TrustNode


@dataclass
class DelegationReceipt:
    """Receipt documenting a single delegation hop."""

    source_agent: str
    target_agent: str
    granted_permissions: List[str]
    is_valid: bool
    reason_code: str


@dataclass
class DelegationPath:
    """Representation of an evaluated multi-agent delegation path."""

    agent_chain: List[str]
    receipts: List[DelegationReceipt]
    is_valid: bool
    violation_type: Optional[str] = None  # "amplification" | "broken_trust" | "circular" | "decay"
    reason_code: str = "valid"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_chain": list(self.agent_chain),
            "receipts": [asdict(r) for r in self.receipts],
            "is_valid": self.is_valid,
            "violation_type": self.violation_type,
            "reason_code": self.reason_code,
        }


class DelegationChainAnalyzer:
    """Analyzes delegation paths for security invariant violations."""

    @staticmethod
    def analyze_chain(
        agent_chain: List[str],
        trust_graph: AgentTrustGraph,
        required_permission: str,
        current_step: int = 1,
    ) -> DelegationPath:
        """Analyze a full delegation chain for circularity, amplification, broken trust, and decay."""
        receipts: List[DelegationReceipt] = []

        # 1. Check for Circular Delegation (Cycle detection)
        seen_agents: Set[str] = set()
        for agent in agent_chain:
            if agent in seen_agents:
                return DelegationPath(
                    agent_chain=agent_chain,
                    receipts=receipts,
                    is_valid=False,
                    violation_type="circular",
                    reason_code="circular_delegation_detected",
                )
            seen_agents.add(agent)

        # 2. Check Trust Decay / Node Expiration
        for agent_id in agent_chain:
            node = trust_graph.get_agent(agent_id)
            if not node or node.is_expired(current_step):
                return DelegationPath(
                    agent_chain=agent_chain,
                    receipts=receipts,
                    is_valid=False,
                    violation_type="decay",
                    reason_code="trust_decay_expired",
                )

        # 3. Check Privilege Monotonicity (Privilege Amplification across hops)
        # Root of delegation must hold required permission
        root_agent = agent_chain[0]
        root_node = trust_graph.get_agent(root_agent)
        if not root_node or required_permission not in root_node.permissions:
            return DelegationPath(
                agent_chain=agent_chain,
                receipts=receipts,
                is_valid=False,
                violation_type="amplification",
                reason_code="privilege_amplification_detected",
            )

        # Evaluate pairwise hops
        for i in range(len(agent_chain) - 1):
            src = agent_chain[i]
            tgt = agent_chain[i + 1]
            src_node = trust_graph.get_agent(src)
            tgt_node = trust_graph.get_agent(tgt)

            if not src_node or not tgt_node:
                return DelegationPath(
                    agent_chain=agent_chain,
                    receipts=receipts,
                    is_valid=False,
                    violation_type="broken_trust",
                    reason_code="agent_node_not_found",
                )

            # Check Broken Trust Chain (untrusted intermediate agent)
            if src_node.trust_level == "untrusted" and tgt != agent_chain[-1]:
                receipts.append(
                    DelegationReceipt(
                        source_agent=src,
                        target_agent=tgt,
                        granted_permissions=[],
                        is_valid=False,
                        reason_code="broken_trust_chain",
                    )
                )
                return DelegationPath(
                    agent_chain=agent_chain,
                    receipts=receipts,
                    is_valid=False,
                    violation_type="broken_trust",
                    reason_code="broken_trust_chain",
                )

            # Check permission containment
            if required_permission not in src_node.permissions or required_permission not in tgt_node.permissions:
                receipts.append(
                    DelegationReceipt(
                        source_agent=src,
                        target_agent=tgt,
                        granted_permissions=[],
                        is_valid=False,
                        reason_code="privilege_amplification_detected",
                    )
                )
                return DelegationPath(
                    agent_chain=agent_chain,
                    receipts=receipts,
                    is_valid=False,
                    violation_type="amplification",
                    reason_code="privilege_amplification_detected",
                )

            receipts.append(
                DelegationReceipt(
                    source_agent=src,
                    target_agent=tgt,
                    granted_permissions=[required_permission],
                    is_valid=True,
                    reason_code="hop_authorized",
                )
            )

        return DelegationPath(
            agent_chain=agent_chain,
            receipts=receipts,
            is_valid=True,
            violation_type=None,
            reason_code="delegation_chain_valid",
        )
